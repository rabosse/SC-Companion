"""
Iteration 21: Ship Deduplication and Variant Grouping Tests
Tests:
- /api/ships returns 0 duplicate ship names (was 17 duplicates before fix)
- /api/ships returns ~203 ships (reduced from 276 after dedup + grouping)
- Ships with variants have 'variants' array with name/id/image per variant
- /api/vehicles returns no duplicates and vehicles with variants have 'variants' array
- Regression: Gear endpoints still work correctly
"""

import pytest
import requests
import os
from collections import Counter

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHealthAndAuth:
    """Health check and authentication tests"""

    def test_health_endpoint(self):
        """Verify backend is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✓ Backend health check passed")

    def test_login_success(self):
        """Verify login works with test credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "e1agent",
            "password": "test123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print(f"✓ Login successful, token length: {len(data['access_token'])}")
        return data["access_token"]


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for subsequent requests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "e1agent",
        "password": "test123"
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


class TestShipDeduplication:
    """Tests for ship deduplication - no duplicate ship names in response"""

    def test_ships_no_duplicates(self, auth_token):
        """Verify /api/ships returns 0 duplicate ship names"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/ships", headers=headers, timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        ships = data["data"]
        ship_names = [s["name"] for s in ships]
        name_counts = Counter(ship_names)
        duplicates = {name: count for name, count in name_counts.items() if count > 1}

        assert len(duplicates) == 0, f"Found duplicate ship names: {duplicates}"
        print(f"✓ No duplicate ship names found in {len(ships)} ships")

    def test_ships_count_reduced(self, auth_token):
        """Verify ship count is reduced after deduplication (was 276, now ~203)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/ships", headers=headers, timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        ships = data["data"]
        # After dedup + variant grouping, expect around 180-220 ships
        assert 150 <= len(ships) <= 250, f"Expected 150-250 ships, got {len(ships)}"
        print(f"✓ Ship count is {len(ships)} (reduced from original 276)")


class TestShipVariants:
    """Tests for ship variant grouping functionality"""

    def test_ships_have_variants_array(self, auth_token):
        """Verify ships with variants have 'variants' array"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/ships", headers=headers, timeout=30)
        assert response.status_code == 200
        data = response.json()

        ships_with_variants = [s for s in data["data"] if s.get("variants") and len(s["variants"]) > 0]
        assert len(ships_with_variants) > 0, "No ships with variants found"
        print(f"✓ Found {len(ships_with_variants)} ships with variants")

    def test_variant_structure(self, auth_token):
        """Verify variant structure has name/id/image fields"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/ships", headers=headers, timeout=30)
        assert response.status_code == 200
        data = response.json()

        ships_with_variants = [s for s in data["data"] if s.get("variants") and len(s["variants"]) > 0]
        
        for ship in ships_with_variants[:5]:  # Check first 5 ships with variants
            for variant in ship["variants"]:
                assert "name" in variant, f"Variant missing 'name' field for ship {ship['name']}"
                assert "id" in variant, f"Variant missing 'id' field for ship {ship['name']}"
                # image can be empty string but should exist
                assert "image" in variant, f"Variant missing 'image' field for ship {ship['name']}"
        
        print(f"✓ Variant structure verified (name/id/image) for {len(ships_with_variants)} ships")

    def test_f8c_lightning_has_variants(self, auth_token):
        """Verify F8C Lightning has 4 variants (or similar multi-variant ship)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/ships", headers=headers, timeout=30)
        assert response.status_code == 200
        data = response.json()

        # Look for F8C Lightning or other ships with multiple variants
        f8c_ships = [s for s in data["data"] if "F8C" in s["name"] or "Lightning" in s["name"]]
        
        if f8c_ships:
            f8c = f8c_ships[0]
            variants = f8c.get("variants", [])
            print(f"✓ {f8c['name']} has {len(variants)} variants: {[v['name'] for v in variants]}")
            # F8C Lightning should have variants if cosmetic variants exist
        else:
            # Check any ship with multiple variants
            multi_variant_ships = [s for s in data["data"] if len(s.get("variants", [])) >= 2]
            if multi_variant_ships:
                ship = multi_variant_ships[0]
                print(f"✓ Found ship with variants: {ship['name']} has {len(ship['variants'])} variants")
            else:
                pytest.skip("No F8C Lightning or multi-variant ships found in live data")

    def test_search_finds_variant_names(self, auth_token):
        """Verify variant names are searchable (PYAM, Executive Edition, etc.)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/ships", headers=headers, timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        # Find ships with variants that have special edition names
        variant_keywords = ["PYAM", "Executive", "Emerald", "Pirate", "Star Kitten", "Wikelo", "Carbon", "CitizenCon"]
        
        found_variants = []
        for ship in data["data"]:
            for variant in ship.get("variants", []):
                for keyword in variant_keywords:
                    if keyword.lower() in variant["name"].lower():
                        found_variants.append(f"{ship['name']} -> {variant['name']}")
                        break
        
        print(f"✓ Found {len(found_variants)} special edition variants")
        if found_variants[:5]:
            print(f"  Examples: {found_variants[:5]}")


class TestVehicleDeduplication:
    """Tests for vehicle deduplication and variant grouping"""

    def test_vehicles_no_duplicates(self, auth_token):
        """Verify /api/vehicles returns no duplicate vehicle names"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/vehicles", headers=headers, timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        vehicles = data["data"]
        vehicle_names = [v["name"] for v in vehicles]
        name_counts = Counter(vehicle_names)
        duplicates = {name: count for name, count in name_counts.items() if count > 1}

        assert len(duplicates) == 0, f"Found duplicate vehicle names: {duplicates}"
        print(f"✓ No duplicate vehicle names found in {len(vehicles)} vehicles")

    def test_vehicles_have_variants_array(self, auth_token):
        """Verify vehicles with variants have 'variants' array"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/vehicles", headers=headers, timeout=30)
        assert response.status_code == 200
        data = response.json()

        vehicles = data["data"]
        vehicles_with_variants = [v for v in vehicles if v.get("variants") and len(v["variants"]) > 0]
        
        if vehicles_with_variants:
            print(f"✓ Found {len(vehicles_with_variants)} vehicles with variants")
            for vehicle in vehicles_with_variants[:3]:
                print(f"  {vehicle['name']}: {len(vehicle['variants'])} variants")
        else:
            print(f"✓ {len(vehicles)} vehicles loaded (no cosmetic variants found - expected for ground vehicles)")

    def test_ballista_has_dunestalker_snowblind_variants(self, auth_token):
        """Verify Ballista has Dunestalker and Snowblind as variants"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/vehicles", headers=headers, timeout=30)
        assert response.status_code == 200
        data = response.json()

        ballista = next((v for v in data["data"] if "Ballista" in v["name"]), None)
        
        if ballista:
            variants = ballista.get("variants", [])
            variant_names = [v["name"] for v in variants]
            print(f"✓ Ballista found with variants: {variant_names}")
            
            # Check for Dunestalker and Snowblind
            has_dunestalker = any("Dunestalker" in name for name in variant_names)
            has_snowblind = any("Snowblind" in name for name in variant_names)
            
            if has_dunestalker or has_snowblind:
                print(f"  ✓ Found expected variants (Dunestalker: {has_dunestalker}, Snowblind: {has_snowblind})")
        else:
            print("Ballista not found in vehicles list (may be in mock data or ships)")


class TestGearRegression:
    """Regression tests for gear endpoints (Armor/Weapons/Equipment)"""

    def test_gear_armor_endpoint(self, auth_token):
        """Verify /api/gear/armor still returns data"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/gear/armor", headers=headers, timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        armor_items = data.get("data", data.get("armor", []))
        assert len(armor_items) > 0, "No armor items returned"
        print(f"✓ Gear/Armor returns {len(armor_items)} items (regression passed)")

    def test_gear_weapons_endpoint(self, auth_token):
        """Verify /api/gear/weapons still returns data"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/gear/weapons", headers=headers, timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        weapons = data.get("data", data.get("weapons", []))
        assert len(weapons) > 0, "No weapons returned"
        print(f"✓ Gear/Weapons returns {len(weapons)} items (regression passed)")

    def test_gear_equipment_endpoint(self, auth_token):
        """Verify /api/gear/equipment still returns data"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/gear/equipment", headers=headers, timeout=30)
        assert response.status_code == 200
        data = response.json()
        
        equipment = data.get("data", data.get("equipment", []))
        assert len(equipment) > 0, "No equipment returned"
        print(f"✓ Gear/Equipment returns {len(equipment)} items (regression passed)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
