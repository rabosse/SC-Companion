"""
Backend tests for Quick Import feature and bulk-add endpoint
Tests: POST /api/fleet/bulk-add, fleet stats, fleet persistence
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_USERNAME = f"TEST_bulk_import_{uuid.uuid4().hex[:8]}"
TEST_PASSWORD = "testpass123"

class TestQuickImportBackend:
    """Tests for Quick Import / bulk-add fleet functionality"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create a requests session"""
        return requests.Session()
    
    @pytest.fixture(scope="class")
    def auth_token(self, session):
        """Get authentication token for test user"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Auth failed: {response.text}"
        token = response.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return token
    
    def test_ships_endpoint_returns_data(self, session, auth_token):
        """Verify /api/ships returns ship data"""
        response = session.get(f"{BASE_URL}/api/ships")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert len(data["data"]) > 0
        # Verify ship structure
        ship = data["data"][0]
        assert "id" in ship
        assert "name" in ship
        assert "manufacturer" in ship
        print(f"Ships endpoint returned {len(data['data'])} ships")
    
    def test_bulk_add_single_ship(self, session, auth_token):
        """Test adding a single ship via bulk-add endpoint"""
        # First get a ship to add
        ships_response = session.get(f"{BASE_URL}/api/ships")
        ships = ships_response.json()["data"]
        test_ship = ships[0]
        
        response = session.post(f"{BASE_URL}/api/fleet/bulk-add", json={
            "ships": [{"id": test_ship["id"], "name": test_ship["name"], "manufacturer": test_ship["manufacturer"]}]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["added"] == 1
        assert data["skipped"] == 0
        print(f"Added ship: {test_ship['name']}")
    
    def test_bulk_add_multiple_ships(self, session, auth_token):
        """Test adding multiple ships at once via bulk-add"""
        # Get ships to add
        ships_response = session.get(f"{BASE_URL}/api/ships")
        ships = ships_response.json()["data"]
        
        # Add 3 different ships (skip first one already added)
        test_ships = ships[1:4]
        
        response = session.post(f"{BASE_URL}/api/fleet/bulk-add", json={
            "ships": [{"id": s["id"], "name": s["name"], "manufacturer": s["manufacturer"]} for s in test_ships]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["added"] >= 1  # At least one should be added
        print(f"Bulk add: {data['added']} added, {data['skipped']} skipped")
    
    def test_bulk_add_skips_duplicates(self, session, auth_token):
        """Test that bulk-add skips ships already in fleet"""
        # Get current fleet
        fleet_response = session.get(f"{BASE_URL}/api/fleet/my")
        fleet = fleet_response.json()["data"]
        
        if len(fleet) > 0:
            # Try to add an existing ship
            existing_ship = fleet[0]
            response = session.post(f"{BASE_URL}/api/fleet/bulk-add", json={
                "ships": [{"id": existing_ship["ship_id"], "name": existing_ship["ship_name"], "manufacturer": existing_ship["manufacturer"]}]
            })
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert data["skipped"] == 1
            assert data["added"] == 0
            print(f"Duplicate skip verified for: {existing_ship['ship_name']}")
    
    def test_bulk_add_mixed_new_and_existing(self, session, auth_token):
        """Test bulk-add with mix of new and existing ships"""
        # Get ships data
        ships_response = session.get(f"{BASE_URL}/api/ships")
        ships = ships_response.json()["data"]
        
        # Get current fleet
        fleet_response = session.get(f"{BASE_URL}/api/fleet/my")
        fleet = fleet_response.json()["data"]
        fleet_ship_ids = {f["ship_id"] for f in fleet}
        
        # Find one existing and one new ship
        existing_ship = None
        new_ship = None
        for ship in ships:
            if ship["id"] in fleet_ship_ids and existing_ship is None:
                existing_ship = ship
            elif ship["id"] not in fleet_ship_ids and new_ship is None:
                new_ship = ship
            if existing_ship and new_ship:
                break
        
        if existing_ship and new_ship:
            response = session.post(f"{BASE_URL}/api/fleet/bulk-add", json={
                "ships": [
                    {"id": existing_ship["id"], "name": existing_ship["name"], "manufacturer": existing_ship["manufacturer"]},
                    {"id": new_ship["id"], "name": new_ship["name"], "manufacturer": new_ship["manufacturer"]}
                ]
            })
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert data["added"] == 1
            assert data["skipped"] == 1
            print(f"Mixed add: added {new_ship['name']}, skipped {existing_ship['name']}")
    
    def test_fleet_my_returns_fleet_data(self, session, auth_token):
        """Verify /api/fleet/my returns fleet with added ships"""
        response = session.get(f"{BASE_URL}/api/fleet/my")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert len(data["data"]) > 0
        
        # Verify fleet item structure
        item = data["data"][0]
        assert "id" in item
        assert "ship_id" in item
        assert "ship_name" in item
        assert "manufacturer" in item
        assert "added_at" in item
        print(f"Fleet contains {len(data['data'])} ships")
    
    def test_fleet_remove_ship(self, session, auth_token):
        """Test removing a ship from fleet"""
        # Get current fleet
        fleet_response = session.get(f"{BASE_URL}/api/fleet/my")
        fleet = fleet_response.json()["data"]
        
        if len(fleet) > 0:
            ship_to_remove = fleet[0]
            response = session.delete(f"{BASE_URL}/api/fleet/{ship_to_remove['id']}")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            print(f"Removed ship: {ship_to_remove['ship_name']}")
            
            # Verify it's removed
            fleet_response = session.get(f"{BASE_URL}/api/fleet/my")
            updated_fleet = fleet_response.json()["data"]
            fleet_ids = {f["id"] for f in updated_fleet}
            assert ship_to_remove["id"] not in fleet_ids
    
    def test_bulk_add_empty_array(self, session, auth_token):
        """Test bulk-add with empty ships array"""
        response = session.post(f"{BASE_URL}/api/fleet/bulk-add", json={
            "ships": []
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["added"] == 0
        assert data["skipped"] == 0
        print("Empty array handled correctly")
    
    def test_cache_ttl_set(self):
        """Verify live_api.py has CACHE_TTL=3600 for auto-refresh"""
        # This is a code review test - we verify the constant is set correctly
        import sys
        sys.path.insert(0, '/app/backend')
        from live_api import CACHE_TTL
        assert CACHE_TTL == 3600, f"Expected CACHE_TTL=3600, got {CACHE_TTL}"
        print(f"CACHE_TTL correctly set to {CACHE_TTL} seconds (1 hour)")
    
    @pytest.fixture(scope="class", autouse=True)
    def cleanup(self, session, auth_token):
        """Cleanup test fleet data after all tests"""
        yield
        # Clean up all fleet items for test user
        try:
            fleet_response = session.get(f"{BASE_URL}/api/fleet/my")
            if fleet_response.status_code == 200:
                fleet = fleet_response.json().get("data", [])
                for item in fleet:
                    session.delete(f"{BASE_URL}/api/fleet/{item['id']}")
            print(f"Cleanup: Removed test fleet data")
        except Exception as e:
            print(f"Cleanup warning: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
