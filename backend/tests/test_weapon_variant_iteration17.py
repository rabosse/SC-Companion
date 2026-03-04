"""
Test Iteration 17: Weapon tab variant functionality matching Armor tab
- CStone images per variant
- Dynamic pricing with LOOT ONLY variants
- Buy/Loot location sections
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestWeaponVariantImages:
    """Test weapon variant images from CStone API"""
    
    def test_weapons_endpoint_returns_success(self):
        """GET /api/gear/weapons returns success"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        print("PASS: Weapons endpoint returns success")
    
    def test_weapons_have_variant_images_field(self):
        """All weapons have variant_images field"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        weapons = response.json().get("data", [])
        
        for w in weapons:
            assert "variant_images" in w, f"Weapon {w['name']} missing variant_images field"
        
        print(f"PASS: All {len(weapons)} weapons have variant_images field")
    
    def test_weapons_have_variant_data_field(self):
        """All weapons have variant_data field"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        weapons = response.json().get("data", [])
        
        for w in weapons:
            assert "variant_data" in w, f"Weapon {w['name']} missing variant_data field"
        
        print(f"PASS: All {len(weapons)} weapons have variant_data field")
    
    def test_arclight_pistol_has_variants(self):
        """Arclight Pistol has multiple variants with CStone images"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        weapons = response.json().get("data", [])
        
        arclight = next((w for w in weapons if w["name"] == "Arclight Pistol"), None)
        assert arclight is not None, "Arclight Pistol not found"
        
        variants = arclight.get("variants", [])
        assert len(variants) >= 5, f"Expected 5+ variants, got {len(variants)}"
        
        variant_images = arclight.get("variant_images", {})
        cstone_images = [v for v in variant_images.values() if "cstone.space" in v]
        assert len(cstone_images) >= 5, f"Expected 5+ CStone variant images, got {len(cstone_images)}"
        
        print(f"PASS: Arclight Pistol has {len(variants)} variants with {len(cstone_images)} CStone images")
    
    def test_variant_data_has_required_fields(self):
        """Variant data includes price_auec, locations, loot_locations, sold"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        weapons = response.json().get("data", [])
        
        weapons_with_variants = [w for w in weapons if w.get("variants")]
        assert len(weapons_with_variants) > 0, "No weapons with variants found"
        
        for w in weapons_with_variants[:3]:
            variant_data = w.get("variant_data", {})
            for variant_name, vd in variant_data.items():
                assert "price_auec" in vd, f"{variant_name} missing price_auec"
                assert "locations" in vd, f"{variant_name} missing locations"
                assert "loot_locations" in vd, f"{variant_name} missing loot_locations"
                assert "sold" in vd, f"{variant_name} missing sold field"
        
        print(f"PASS: Variant data has all required fields")
    
    def test_loot_only_variants_exist(self):
        """Some weapon variants are loot-only (sold=false)"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        weapons = response.json().get("data", [])
        
        loot_only_count = 0
        for w in weapons:
            variant_data = w.get("variant_data", {})
            for vd in variant_data.values():
                if not vd.get("sold"):
                    loot_only_count += 1
        
        assert loot_only_count > 0, "No loot-only weapon variants found"
        print(f"PASS: Found {loot_only_count} loot-only weapon variants")
    
    def test_loot_only_variants_have_loot_locations(self):
        """Loot-only variants have loot_locations populated"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        weapons = response.json().get("data", [])
        
        for w in weapons:
            variant_data = w.get("variant_data", {})
            for variant_name, vd in variant_data.items():
                if not vd.get("sold"):
                    loot_locs = vd.get("loot_locations", [])
                    assert len(loot_locs) > 0, f"Loot-only variant {variant_name} has no loot_locations"
        
        print("PASS: All loot-only variants have loot_locations")


class TestArmorVariantRegression:
    """Regression tests for armor variants"""
    
    def test_armor_endpoint_returns_success(self):
        """GET /api/gear/armor returns success"""
        response = requests.get(f"{BASE_URL}/api/gear/armor", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        print("PASS: Armor endpoint returns success")
    
    def test_armor_has_variant_images_and_data(self):
        """Armor sets have variant_images and variant_data fields"""
        response = requests.get(f"{BASE_URL}/api/gear/armor", timeout=30)
        armor_sets = response.json().get("data", [])
        
        for a in armor_sets:
            assert "variant_images" in a, f"Armor {a['name']} missing variant_images"
            assert "variant_data" in a, f"Armor {a['name']} missing variant_data"
        
        print(f"PASS: All {len(armor_sets)} armor sets have variant fields")
    
    def test_adp_armor_has_cstone_images(self):
        """ADP armor has CStone images for variants"""
        response = requests.get(f"{BASE_URL}/api/gear/armor", timeout=30)
        armor_sets = response.json().get("data", [])
        
        adp = next((a for a in armor_sets if a["name"] == "ADP"), None)
        assert adp is not None, "ADP armor not found"
        
        variant_images = adp.get("variant_images", {})
        cstone_images = [v for v in variant_images.values() if "cstone.space" in v]
        assert len(cstone_images) >= 5, f"Expected 5+ CStone images, got {len(cstone_images)}"
        
        print(f"PASS: ADP armor has {len(cstone_images)} CStone variant images")


class TestEquipmentModal:
    """Test equipment modal functionality"""
    
    def test_equipment_endpoint_returns_success(self):
        """GET /api/gear/equipment returns success"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        print("PASS: Equipment endpoint returns success")
    
    def test_equipment_has_required_fields(self):
        """Equipment items have required fields for modal display"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment", timeout=30)
        equipment = response.json().get("data", [])
        
        required_fields = ["id", "name", "type", "manufacturer", "description", "locations"]
        for item in equipment:
            for field in required_fields:
                assert field in item, f"Equipment {item.get('name', 'unknown')} missing {field}"
        
        print(f"PASS: All {len(equipment)} equipment items have required fields")
    
    def test_equipment_has_stats_for_modal(self):
        """Equipment items have stats field for modal display"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment", timeout=30)
        equipment = response.json().get("data", [])
        
        items_with_stats = [e for e in equipment if e.get("stats")]
        assert len(items_with_stats) > 0, "No equipment items have stats"
        
        print(f"PASS: {len(items_with_stats)} equipment items have stats")


class TestWeaponBaseImage:
    """Test weapon base images from CStone"""
    
    def test_weapons_have_base_image(self):
        """All weapons have a base image field"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        weapons = response.json().get("data", [])
        
        for w in weapons:
            assert "image" in w, f"Weapon {w['name']} missing image field"
        
        print(f"PASS: All {len(weapons)} weapons have image field")
    
    def test_majority_weapons_have_cstone_images(self):
        """Majority of weapons have CStone images"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        weapons = response.json().get("data", [])
        
        cstone_count = sum(1 for w in weapons if "cstone.space" in w.get("image", ""))
        total = len(weapons)
        pct = (cstone_count / total) * 100 if total > 0 else 0
        
        assert cstone_count >= 15, f"Expected 15+ weapons with CStone images, got {cstone_count}"
        print(f"PASS: {cstone_count}/{total} weapons ({pct:.0f}%) have CStone images")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
