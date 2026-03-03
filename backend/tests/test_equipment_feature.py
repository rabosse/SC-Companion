"""
Test suite for Equipment Feature (P4) - Mining Equipment, Medical Supplies, Backpacks, Undersuits
Tests the new /api/gear/equipment endpoint and verifies item structure
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestEquipmentAPI:
    """Tests for GET /api/gear/equipment endpoint"""
    
    def test_equipment_endpoint_returns_success(self):
        """Verify endpoint returns success status"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "data" in data
        print(f"PASS: Equipment endpoint returns success with {len(data['data'])} items")
    
    def test_equipment_returns_23_items(self):
        """Verify 23 equipment items are returned"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 23, f"Expected 23 items, got {len(data['data'])}"
        print("PASS: Equipment endpoint returns exactly 23 items")
    
    def test_equipment_type_counts(self):
        """Verify correct number of items per type"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = response.json()["data"]
        
        type_counts = {}
        for item in data:
            t = item["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        
        expected = {
            "Mining Head": 5,
            "Mining Module": 4,
            "Mining Attachment": 1,
            "Medical Device": 4,
            "Backpack": 4,
            "Undersuit": 5
        }
        
        for expected_type, expected_count in expected.items():
            actual_count = type_counts.get(expected_type, 0)
            assert actual_count == expected_count, f"{expected_type}: expected {expected_count}, got {actual_count}"
            print(f"PASS: {expected_type} has {expected_count} items")
    
    def test_mining_head_structure(self):
        """Verify Mining Head items have correct structure"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = response.json()["data"]
        
        mining_heads = [i for i in data if i["type"] == "Mining Head"]
        assert len(mining_heads) == 5
        
        for mh in mining_heads:
            # Required fields
            assert "id" in mh
            assert "name" in mh
            assert "type" in mh and mh["type"] == "Mining Head"
            assert "subtype" in mh  # Ship or Hand
            assert "manufacturer" in mh
            assert "stats" in mh and isinstance(mh["stats"], dict)
            assert "description" in mh
            assert "locations" in mh and isinstance(mh["locations"], list)
            assert "price_auec" in mh and isinstance(mh["price_auec"], int)
            
            # Stats fields for mining head
            stats = mh["stats"]
            assert "power" in stats
            assert "range" in stats
            print(f"PASS: Mining Head '{mh['name']}' has correct structure")
    
    def test_backpack_structure(self):
        """Verify Backpack items have correct structure"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = response.json()["data"]
        
        backpacks = [i for i in data if i["type"] == "Backpack"]
        assert len(backpacks) == 4
        
        for bp in backpacks:
            assert "id" in bp
            assert "name" in bp
            assert "type" in bp and bp["type"] == "Backpack"
            assert "subtype" in bp  # Large, Medium, Utility
            assert "manufacturer" in bp
            assert "stats" in bp
            assert "capacity" in bp["stats"]  # Backpack-specific stat
            assert "description" in bp
            assert "locations" in bp
            assert "price_auec" in bp
            print(f"PASS: Backpack '{bp['name']}' has correct structure")
    
    def test_undersuit_structure(self):
        """Verify Undersuit items have correct structure"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = response.json()["data"]
        
        undersuits = [i for i in data if i["type"] == "Undersuit"]
        assert len(undersuits) == 5
        
        for us in undersuits:
            assert "id" in us
            assert "name" in us
            assert "type" in us and us["type"] == "Undersuit"
            assert "subtype" in us  # Standard, Exploration, Tactical, Cold Weather, Heat Resistant
            assert "manufacturer" in us
            assert "stats" in us
            assert "temp_max" in us["stats"]  # Undersuit-specific stat
            assert "temp_min" in us["stats"]
            assert "description" in us
            assert "locations" in us
            assert "price_auec" in us
            print(f"PASS: Undersuit '{us['name']}' has correct structure")
    
    def test_medical_device_structure(self):
        """Verify Medical Device items have correct structure"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = response.json()["data"]
        
        medical = [i for i in data if i["type"] == "Medical Device"]
        assert len(medical) == 4
        
        for md in medical:
            assert "id" in md
            assert "name" in md
            assert "type" in md and md["type"] == "Medical Device"
            assert "subtype" in md  # Tool, Consumable, Equipment
            assert "manufacturer" in md
            assert "stats" in md
            assert "description" in md
            assert "locations" in md
            print(f"PASS: Medical Device '{md['name']}' has correct structure")
    
    def test_mining_module_structure(self):
        """Verify Mining Module items have correct structure"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = response.json()["data"]
        
        modules = [i for i in data if i["type"] == "Mining Module"]
        assert len(modules) == 4
        
        for mod in modules:
            assert "id" in mod
            assert "name" in mod
            assert "type" in mod and mod["type"] == "Mining Module"
            assert "subtype" in mod and mod["subtype"] == "Consumable"
            assert "manufacturer" in mod
            assert "stats" in mod
            assert "effect" in mod["stats"]  # Module-specific stat
            assert "description" in mod
            assert "locations" in mod
            assert "price_auec" in mod
            print(f"PASS: Mining Module '{mod['name']}' has correct structure")
    
    def test_equipment_price_values(self):
        """Verify price_auec values are reasonable"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = response.json()["data"]
        
        for item in data:
            price = item.get("price_auec", 0)
            # Most items should have a price (except medical stretcher = 0)
            assert isinstance(price, int), f"{item['name']} price is not int"
            assert price >= 0, f"{item['name']} has negative price"
            
        # Check specific known prices
        arbor = next((i for i in data if i["id"] == "arbor-mh1"), None)
        assert arbor and arbor["price_auec"] == 13000
        
        klein = next((i for i in data if i["id"] == "klein-s1"), None)
        assert klein and klein["price_auec"] == 146000
        
        print("PASS: Equipment prices are valid integers")


class TestGearEndpointRegression:
    """Regression tests for existing gear endpoints"""
    
    def test_weapons_still_returns_38_items(self):
        """Verify FPS Weapons endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert len(data["data"]) == 38, f"Expected 38 weapons, got {len(data['data'])}"
        print("PASS: Weapons endpoint returns 38 items (no regression)")
    
    def test_armor_still_returns_21_items(self):
        """Verify Armor endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert len(data["data"]) == 21, f"Expected 21 armor sets, got {len(data['data'])}"
        print("PASS: Armor endpoint returns 21 items (no regression)")


class TestOtherRegressions:
    """Regression tests for other important endpoints"""
    
    def test_health_endpoint(self):
        """Verify health endpoint works"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        assert response.json().get("status") == "ok"
        print("PASS: Health endpoint returns ok")
    
    def test_dashboard_loads(self):
        """Verify dashboard page loads"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        print("PASS: Dashboard page loads")
    
    def test_prices_endpoint(self):
        """Verify prices endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        assert response.status_code == 200
        data = response.json()
        # Response has success=True and data containing ships, weapons, components
        assert data.get("success") == True or "ships" in data or ("data" in data and "ships" in data.get("data", {}))
        print("PASS: Prices endpoint works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
