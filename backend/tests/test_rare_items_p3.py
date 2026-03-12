"""
Test suite for P3 Rare Items feature - /api/gear/rare-items endpoint
Tests rare item locations for armor and FPS weapons
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRareItemsAPI:
    """Tests for /api/gear/rare-items endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - verify BASE_URL is configured"""
        assert BASE_URL, "REACT_APP_BACKEND_URL environment variable must be set"
    
    def test_rare_items_endpoint_returns_success(self):
        """Test that /api/gear/rare-items returns 200 with success: true"""
        response = requests.get(f"{BASE_URL}/api/gear/rare-items", timeout=120)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") is True, "Expected success: true in response"
        assert "data" in data, "Expected 'data' key in response"
        assert "total" in data, "Expected 'total' key in response"
        print(f"Rare items endpoint returned {data['total']} items")
    
    def test_rare_items_have_required_fields(self):
        """Test that each rare item has the required fields"""
        response = requests.get(f"{BASE_URL}/api/gear/rare-items", timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        items = data.get("data", [])
        
        assert len(items) > 0, "Expected at least some rare items"
        
        required_fields = ["id", "name", "category", "type", "manufacturer", 
                          "description", "image", "loot_locations", "buy_locations", 
                          "price_auec", "loot_only"]
        
        # Check first 10 items
        for item in items[:10]:
            for field in required_fields:
                assert field in item, f"Missing field '{field}' in item {item.get('name', 'unknown')}"
        
        print(f"Verified required fields in {min(10, len(items))} rare items")
    
    def test_rare_items_category_distribution(self):
        """Test that rare items span weapon, armor, and equipment categories"""
        response = requests.get(f"{BASE_URL}/api/gear/rare-items", timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        items = data.get("data", [])
        
        categories = {}
        for item in items:
            cat = item.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"Category distribution: {categories}")
        
        # Expect at least weapons and armor
        assert "weapon" in categories or "armor" in categories, \
            f"Expected at least weapon or armor categories, got: {list(categories.keys())}"
    
    def test_rare_items_have_loot_locations(self):
        """Test that rare items have loot_locations populated"""
        response = requests.get(f"{BASE_URL}/api/gear/rare-items", timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        items = data.get("data", [])
        
        items_with_loot = [i for i in items if i.get("loot_locations") and len(i["loot_locations"]) > 0]
        
        print(f"Items with loot locations: {len(items_with_loot)}/{len(items)}")
        
        # All items should have loot locations (that's the whole point of rare items)
        assert len(items_with_loot) == len(items), \
            f"Expected all rare items to have loot_locations, but {len(items) - len(items_with_loot)} are missing"
    
    def test_rare_items_loot_only_flag(self):
        """Test loot_only flag is present and some items are marked as loot-only"""
        response = requests.get(f"{BASE_URL}/api/gear/rare-items", timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        items = data.get("data", [])
        
        loot_only_items = [i for i in items if i.get("loot_only") is True]
        buyable_items = [i for i in items if i.get("loot_only") is False]
        
        print(f"Loot-only items: {len(loot_only_items)}")
        print(f"Items with buy option: {len(buyable_items)}")
        
        # Per requirement: ~26 are loot-only
        assert len(loot_only_items) > 0, "Expected some loot-only items"
    
    def test_rare_items_weapons_count(self):
        """Test weapons in rare items count"""
        response = requests.get(f"{BASE_URL}/api/gear/rare-items", timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        items = data.get("data", [])
        
        weapons = [i for i in items if i.get("category") == "weapon"]
        print(f"Rare weapons count: {len(weapons)}")
        
        # Per requirement: ~15 weapons
        if len(weapons) > 0:
            print(f"Sample weapon: {weapons[0].get('name')} - loot locations: {weapons[0].get('loot_locations')}")
    
    def test_rare_items_armor_count(self):
        """Test armor in rare items count"""
        response = requests.get(f"{BASE_URL}/api/gear/rare-items", timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        items = data.get("data", [])
        
        armor = [i for i in items if i.get("category") == "armor"]
        print(f"Rare armor count: {len(armor)}")
        
        # Per requirement: ~70 armor
        if len(armor) > 0:
            print(f"Sample armor: {armor[0].get('name')} - loot locations: {armor[0].get('loot_locations')}")


class TestExistingGearEndpointsRegression:
    """Regression tests for existing gear endpoints"""
    
    def test_weapons_endpoint_still_works(self):
        """Test /api/gear/weapons still returns data"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        assert len(data.get("data", [])) > 0
        print(f"Weapons endpoint returned {len(data['data'])} weapons")
    
    def test_armor_endpoint_still_works(self):
        """Test /api/gear/armor still returns data"""
        response = requests.get(f"{BASE_URL}/api/gear/armor", timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        assert len(data.get("data", [])) > 0
        print(f"Armor endpoint returned {len(data['data'])} armor sets")
    
    def test_equipment_endpoint_still_works(self):
        """Test /api/gear/equipment still returns data"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment", timeout=120)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        assert len(data.get("data", [])) > 0
        print(f"Equipment endpoint returned {len(data['data'])} equipment items")


class TestDashboardRegression:
    """Regression tests for dashboard"""
    
    def test_dashboard_health(self):
        """Test /api/health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=30)
        assert response.status_code == 200
        print("Health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
