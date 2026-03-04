"""
Test gear modal and armor variant expansion features - iteration 16
Tests: armor variants expanded to 4-5 per set, weapon modal data structure, health regression
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestArmorVariantsExpansion:
    """Test armor variants expanded to 4-5 per set"""
    
    def test_armor_api_returns_success(self):
        """GET /api/gear/armor returns 200 with success=true"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
    def test_armor_count(self):
        """GET /api/gear/armor returns 21 armor sets"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        assert len(data.get('data', [])) == 21
        
    def test_armor_variants_expanded_4_to_5(self):
        """Each armor set should have 4-5 variants (expanded from 2-3)"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        for armor in data.get('data', []):
            variants = armor.get('variants', [])
            variant_count = len(variants)
            # Each armor should have 4 or 5 variants
            assert variant_count >= 4, f"{armor['name']} has only {variant_count} variants (expected 4-5)"
            assert variant_count <= 5, f"{armor['name']} has {variant_count} variants (expected max 5)"
            
    def test_armor_heavy_variants(self):
        """Heavy armor sets should have 4-5 variants"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        heavy_armors = [a for a in data.get('data', []) if a.get('type') == 'Heavy']
        assert len(heavy_armors) >= 8, f"Expected at least 8 heavy armor sets, got {len(heavy_armors)}"
        
        for armor in heavy_armors:
            variant_count = len(armor.get('variants', []))
            assert variant_count >= 4, f"Heavy armor {armor['name']} has only {variant_count} variants"
            
    def test_armor_medium_variants(self):
        """Medium armor sets should have 4 variants"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        medium_armors = [a for a in data.get('data', []) if a.get('type') == 'Medium']
        assert len(medium_armors) >= 5, f"Expected at least 5 medium armor sets"
        
        for armor in medium_armors:
            variant_count = len(armor.get('variants', []))
            assert variant_count >= 4, f"Medium armor {armor['name']} has only {variant_count} variants"
            
    def test_armor_light_variants(self):
        """Light armor sets should have 4 variants"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        light_armors = [a for a in data.get('data', []) if a.get('type') == 'Light']
        assert len(light_armors) >= 5, f"Expected at least 5 light armor sets"
        
        for armor in light_armors:
            variant_count = len(armor.get('variants', []))
            assert variant_count >= 4, f"Light armor {armor['name']} has only {variant_count} variants"


class TestWeaponModalData:
    """Test weapons have all required fields for detail modal display"""
    
    def test_weapons_api_returns_success(self):
        """GET /api/gear/weapons returns 200 with success=true"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        
    def test_weapons_have_modal_fields(self):
        """All weapons should have fields required for modal: name, type, size, manufacturer, description, damage, ammo, fire_rate, effective_range, locations, variants"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        
        required_fields = ['id', 'name', 'type', 'size', 'manufacturer', 'description', 
                          'damage', 'ammo', 'fire_rate', 'effective_range', 'locations']
        
        for weapon in data.get('data', []):
            for field in required_fields:
                assert field in weapon, f"Weapon {weapon.get('name', 'unknown')} missing field: {field}"
                
    def test_weapons_have_image_field(self):
        """All weapons should have 'image' field (may be empty string)"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        
        for weapon in data.get('data', []):
            assert 'image' in weapon, f"Weapon {weapon['name']} missing 'image' field"


class TestArmorModalData:
    """Test armors have all required fields for detail modal display"""
    
    def test_armors_have_modal_fields(self):
        """All armors should have fields for modal: name, type, manufacturer, description, temp_max, temp_min, radiation, locations, variants"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        required_fields = ['id', 'name', 'type', 'manufacturer', 'description',
                          'temp_max', 'temp_min', 'radiation', 'locations', 'variants']
        
        for armor in data.get('data', []):
            for field in required_fields:
                assert field in armor, f"Armor {armor.get('name', 'unknown')} missing field: {field}"
                
    def test_armors_have_image_field(self):
        """All armors should have 'image' field"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        for armor in data.get('data', []):
            assert 'image' in armor, f"Armor {armor['name']} missing 'image' field"
            
    def test_armors_have_loot_locations(self):
        """Armors should have 'loot_locations' field for modal display"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        for armor in data.get('data', []):
            # loot_locations is optional but should be present as key
            assert 'loot_locations' in armor, f"Armor {armor['name']} missing 'loot_locations' field"


class TestRegressionTests:
    """Regression tests for existing functionality"""
    
    def test_health_endpoint(self):
        """GET /api/health returns ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
    def test_equipment_endpoint(self):
        """GET /api/gear/equipment returns equipment list"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') == True
        assert len(data.get('data', [])) == 30  # 30 equipment items
        
    def test_weapons_count(self):
        """GET /api/gear/weapons returns 38 weapons"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        assert len(data.get('data', [])) == 38


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
