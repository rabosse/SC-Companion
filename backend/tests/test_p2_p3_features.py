"""
Test P2 (Expanded Gear) and P3 (Price Tracking) Features for Star Citizen Fleet Manager.

P2: Expanded gear data with grenades and utilities
P3: Real-time price tracking using Star Citizen Wiki API with MongoDB snapshots
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestP2GearExpansion:
    """P2 Feature: Expanded gear data with grenades and utilities"""

    def test_gear_weapons_returns_38_items(self):
        """GET /api/gear/weapons should return 38 items (was 28)"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 38, f"Expected 38 weapons, got {len(data['data'])}"

    def test_gear_weapons_has_grenade_type(self):
        """GET /api/gear/weapons should include Grenade type"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
        data = response.json()
        grenade_items = [w for w in data["data"] if w["type"] == "Grenade"]
        assert len(grenade_items) == 4, f"Expected 4 grenades, got {len(grenade_items)}"
        
        # Verify specific grenade names
        grenade_names = [g["name"] for g in grenade_items]
        assert "Frag Grenade" in grenade_names
        assert "Flash Grenade" in grenade_names
        assert "Smoke Grenade" in grenade_names
        assert "EMP Grenade" in grenade_names

    def test_gear_weapons_has_utility_type(self):
        """GET /api/gear/weapons should include Utility type"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
        data = response.json()
        utility_items = [w for w in data["data"] if w["type"] == "Utility"]
        assert len(utility_items) == 6, f"Expected 6 utilities, got {len(utility_items)}"
        
        # Verify specific utility names
        utility_names = [u["name"] for u in utility_items]
        assert "MedPen" in utility_names
        assert "OxyPen" in utility_names
        assert "AdrenaPen" in utility_names
        assert "Tractor Beam (Multi-Tool)" in utility_names
        assert "Cutting Tool (Multi-Tool)" in utility_names
        assert "Repair Tool (Multi-Tool)" in utility_names

    def test_grenade_item_structure(self):
        """Verify grenade item has correct structure"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        frag = next((w for w in data["data"] if w["name"] == "Frag Grenade"), None)
        
        assert frag is not None
        assert frag["type"] == "Grenade"
        assert frag["manufacturer"] == "Behring"
        assert frag["damage"] == 200
        assert frag["size"] == 0
        assert "locations" in frag
        assert len(frag["locations"]) > 0

    def test_utility_item_structure(self):
        """Verify utility item has correct structure"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        medpen = next((w for w in data["data"] if w["name"] == "MedPen"), None)
        
        assert medpen is not None
        assert medpen["type"] == "Utility"
        assert medpen["manufacturer"] == "CureLife"
        assert medpen["damage"] == 0
        assert medpen["size"] == 0
        assert "locations" in medpen
        assert len(medpen["locations"]) > 0


class TestP3PriceTracking:
    """P3 Feature: Real-time price tracking with MongoDB snapshots"""

    def test_prices_summary_returns_tracked_items(self):
        """GET /api/prices/summary returns tracked items with snapshot_count"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "ships" in data["data"]
        assert "weapons" in data["data"]
        assert "components" in data["data"]
        assert "snapshot_count" in data
        assert data["snapshot_count"] >= 1, "Should have at least 1 snapshot"

    def test_prices_summary_has_items_with_prices(self):
        """Price summary should contain items with price data"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        data = response.json()
        
        # Verify ships have price data
        if len(data["data"]["ships"]) > 0:
            ship = data["data"]["ships"][0]
            assert "item_name" in ship
            assert "item_type" in ship
            assert ship["item_type"] == "ship"
            assert "price_auec" in ship or "price_usd" in ship
            assert "timestamp" in ship

    def test_prices_changes_returns_comparison(self):
        """GET /api/prices/changes returns price changes between snapshots"""
        response = requests.get(f"{BASE_URL}/api/prices/changes")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        
        # If we have 2+ snapshots, should have snapshot timestamps
        if data.get("total_changes", 0) > 0 or len(data.get("data", [])) == 0:
            assert "latest_snapshot" in data or "message" in data

    def test_prices_changes_with_type_filter(self):
        """GET /api/prices/changes supports item_type filter"""
        response = requests.get(f"{BASE_URL}/api/prices/changes?item_type=ship")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # All changes should be for ships
        for change in data.get("data", []):
            if "item_type" in change:
                assert change["item_type"] == "ship"

    def test_prices_snapshot_triggers_capture(self):
        """GET /api/prices/snapshot triggers a new price capture"""
        response = requests.get(f"{BASE_URL}/api/prices/snapshot")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
        assert "Captured" in data["message"]

    def test_prices_history_returns_item_history(self):
        """GET /api/prices/history/{item_name} returns price history"""
        response = requests.get(f"{BASE_URL}/api/prices/history/Aurora")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        # Should have history entries if Aurora has been tracked
        if len(data["data"]) > 0:
            entry = data["data"][0]
            assert "item_name" in entry
            assert "price_auec" in entry or "price_usd" in entry
            assert "timestamp" in entry

    def test_prices_history_case_insensitive(self):
        """Price history search should be case-insensitive"""
        response1 = requests.get(f"{BASE_URL}/api/prices/history/aurora")
        response2 = requests.get(f"{BASE_URL}/api/prices/history/AURORA")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Both should return similar results (case-insensitive regex)
        assert len(data1["data"]) == len(data2["data"])


class TestRegressionDashboardAndGear:
    """Regression tests for existing functionality"""

    def test_health_endpoint(self):
        """GET /api/health still works"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_gear_armor_still_works(self):
        """GET /api/gear/armor still returns armor sets"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 21, "Should have at least 21 armor sets"

    def test_login_flow(self):
        """POST /api/auth/login still works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "geartest",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data

    def test_ships_endpoint_with_auth(self):
        """GET /api/ships still works with auth"""
        # Login first
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "geartest",
            "password": "password123"
        })
        token = login_resp.json()["access_token"]
        
        # Get ships
        response = requests.get(
            f"{BASE_URL}/api/ships",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
