"""
Iteration 18 Backend Tests: CStone Equipment Integration + Module Refactor

Tests:
1. Equipment endpoint returns 30 items with proper fields
2. MedPen Mk II and Hemozal have CStone images  
3. Weapons endpoint regression (50 items, variant data)
4. Armor endpoint regression (28 items, variant data)
5. Health endpoint works (server starts with new imports)
6. Equipment items with variants have variant_data and variant_images
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHealthEndpoint:
    """Server health check - validates new module imports work"""
    
    def test_health_returns_ok(self):
        """Server starts correctly with refactored module imports"""
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "ok"


class TestEquipmentCStoneIntegration:
    """Equipment endpoint with CStone image integration tests"""
    
    def test_equipment_returns_30_items(self):
        """Equipment endpoint returns expected 30 items"""
        resp = requests.get(f"{BASE_URL}/api/gear/equipment")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        items = data.get("data", [])
        assert len(items) == 30, f"Expected 30 equipment items, got {len(items)}"
    
    def test_equipment_items_have_required_fields(self):
        """All equipment items have image, variant_images, variant_data fields"""
        resp = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = resp.json()
        items = data.get("data", [])
        
        for item in items:
            assert "image" in item, f"Missing image field in {item.get('name')}"
            assert "variant_images" in item, f"Missing variant_images in {item.get('name')}"
            assert "variant_data" in item, f"Missing variant_data in {item.get('name')}"
    
    def test_medpen_mk2_has_cstone_image(self):
        """MedPen Mk II should have CStone image from GetGadgets API"""
        resp = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = resp.json()
        items = data.get("data", [])
        
        medpen = next((i for i in items if i.get("name") == "MedPen Mk II"), None)
        assert medpen is not None, "MedPen Mk II not found in equipment"
        assert medpen.get("image"), "MedPen Mk II should have CStone image"
        assert "cstone.space" in medpen.get("image", ""), "Image should be from CStone"
    
    def test_hemozal_has_cstone_image(self):
        """Hemozal should have CStone image from GetGadgets API"""
        resp = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = resp.json()
        items = data.get("data", [])
        
        hemozal = next((i for i in items if i.get("name") == "Hemozal"), None)
        assert hemozal is not None, "Hemozal not found in equipment"
        assert hemozal.get("image"), "Hemozal should have CStone image"
        assert "cstone.space" in hemozal.get("image", ""), "Image should be from CStone"
    
    def test_equipment_items_have_stats(self):
        """Equipment items should have stats for modal display"""
        resp = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = resp.json()
        items = data.get("data", [])
        
        items_with_stats = [i for i in items if i.get("stats")]
        assert len(items_with_stats) > 20, f"Expected >20 items with stats, got {len(items_with_stats)}"


class TestEquipmentVariants:
    """Equipment items with variants tests"""
    
    def test_pembroke_backpack_has_variants(self):
        """Pembroke Backpack should have 2 color variants"""
        resp = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = resp.json()
        items = data.get("data", [])
        
        pembroke = next((i for i in items if i.get("name") == "Pembroke Backpack"), None)
        assert pembroke is not None, "Pembroke Backpack not found"
        variants = pembroke.get("variants", [])
        assert len(variants) >= 2, f"Expected 2 variants, got {len(variants)}"
        assert "Pembroke Red" in variants or "Pembroke Gold" in variants
    
    def test_pembroke_backpack_variant_data(self):
        """Pembroke Backpack variant_data should have price and locations"""
        resp = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = resp.json()
        items = data.get("data", [])
        
        pembroke = next((i for i in items if i.get("name") == "Pembroke Backpack"), None)
        assert pembroke is not None
        
        variant_data = pembroke.get("variant_data", {})
        for variant_name, vd in variant_data.items():
            assert "price_auec" in vd, f"Missing price_auec in {variant_name}"
            assert "locations" in vd, f"Missing locations in {variant_name}"
            assert "sold" in vd, f"Missing sold in {variant_name}"
    
    def test_alantin_undersuit_has_variants(self):
        """Alantin Undersuit should have White and Black variants"""
        resp = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = resp.json()
        items = data.get("data", [])
        
        alantin = next((i for i in items if i.get("name") == "Alantin Undersuit"), None)
        assert alantin is not None, "Alantin Undersuit not found"
        variants = alantin.get("variants", [])
        assert len(variants) >= 2, f"Expected 2 variants, got {len(variants)}"
    
    def test_venture_undersuit_has_variant(self):
        """Venture Undersuit should have Pathfinder variant"""
        resp = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = resp.json()
        items = data.get("data", [])
        
        venture = next((i for i in items if i.get("name") == "Venture Undersuit"), None)
        assert venture is not None, "Venture Undersuit not found"
        variants = venture.get("variants", [])
        assert len(variants) >= 1, f"Expected 1+ variants, got {len(variants)}"
        assert "Venture Pathfinder" in variants
    
    def test_arden_undersuit_has_variants(self):
        """Arden Undersuit should have Black and Navy variants"""
        resp = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = resp.json()
        items = data.get("data", [])
        
        arden = next((i for i in items if i.get("name") == "Arden Undersuit"), None)
        assert arden is not None, "Arden Undersuit not found"
        variants = arden.get("variants", [])
        assert len(variants) >= 2, f"Expected 2 variants, got {len(variants)}"


class TestWeaponsRegression:
    """Weapons endpoint regression tests after refactor"""
    
    def test_weapons_returns_50_items(self):
        """Weapons endpoint still returns 50 items after refactor"""
        resp = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        items = data.get("data", [])
        assert len(items) == 50, f"Expected 50 weapons, got {len(items)}"
    
    def test_weapons_have_variant_images(self):
        """All weapons should still have variant_images field"""
        resp = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = resp.json()
        items = data.get("data", [])
        
        for item in items:
            assert "variant_images" in item, f"Missing variant_images in {item.get('name')}"
    
    def test_weapons_have_variant_data(self):
        """All weapons should still have variant_data field"""
        resp = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = resp.json()
        items = data.get("data", [])
        
        for item in items:
            assert "variant_data" in item, f"Missing variant_data in {item.get('name')}"
    
    def test_arclight_pistol_has_cstone_images(self):
        """Arclight Pistol should still have CStone variant images"""
        resp = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = resp.json()
        items = data.get("data", [])
        
        arclight = next((i for i in items if i.get("name") == "Arclight Pistol"), None)
        assert arclight is not None
        
        variant_images = arclight.get("variant_images", {})
        images_with_cstone = [v for v in variant_images.values() if "cstone.space" in str(v)]
        assert len(images_with_cstone) > 3, f"Expected >3 CStone variant images, got {len(images_with_cstone)}"


class TestArmorRegression:
    """Armor endpoint regression tests after refactor"""
    
    def test_armor_returns_28_items(self):
        """Armor endpoint still returns 28 items after refactor"""
        resp = requests.get(f"{BASE_URL}/api/gear/armor")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        items = data.get("data", [])
        assert len(items) == 28, f"Expected 28 armor sets, got {len(items)}"
    
    def test_armor_have_variant_images(self):
        """All armor should still have variant_images field"""
        resp = requests.get(f"{BASE_URL}/api/gear/armor")
        data = resp.json()
        items = data.get("data", [])
        
        for item in items:
            assert "variant_images" in item, f"Missing variant_images in {item.get('name')}"
    
    def test_armor_have_variant_data(self):
        """All armor should still have variant_data field"""
        resp = requests.get(f"{BASE_URL}/api/gear/armor")
        data = resp.json()
        items = data.get("data", [])
        
        for item in items:
            assert "variant_data" in item, f"Missing variant_data in {item.get('name')}"
    
    def test_adp_armor_has_cstone_images(self):
        """ADP armor should still have CStone variant images"""
        resp = requests.get(f"{BASE_URL}/api/gear/armor")
        data = resp.json()
        items = data.get("data", [])
        
        adp = next((i for i in items if i.get("name") == "ADP"), None)
        assert adp is not None
        
        variant_images = adp.get("variant_images", {})
        images_with_cstone = [v for v in variant_images.values() if "cstone.space" in str(v)]
        assert len(images_with_cstone) > 0, "ADP should have CStone variant images"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
