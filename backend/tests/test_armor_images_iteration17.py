"""
Test iteration 17: Complete armor data with images and variant-specific images.
Tests:
- 28 armor sets returned (7 new sets: ORC-mkX, ORC-mkV, MacFlex, Venture, Inquisitor, TrueDef-Pro, PAB-1)
- Each armor set has base image field (most non-empty)
- variant_images dict present with variant-specific URLs
- Variant images differ from base image for sets with unique variants
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestArmorSetsComplete:
    """Test armor sets API with complete data and images"""
    
    def test_armor_returns_28_sets(self):
        """Verify /api/gear/armor returns exactly 28 armor sets"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert len(data["data"]) == 28, f"Expected 28 armor sets, got {len(data['data'])}"
    
    def test_new_armor_sets_present(self):
        """Verify 7 new armor sets are present: ORC-mkX, ORC-mkV, MacFlex, Venture, Inquisitor, TrueDef-Pro, PAB-1"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        armor_names = [a["name"] for a in data["data"]]
        
        new_sets = ["ORC-mkX", "ORC-mkV", "MacFlex", "Venture", "Inquisitor", "TrueDef-Pro", "PAB-1"]
        for expected in new_sets:
            assert expected in armor_names, f"Missing new armor set: {expected}"
    
    def test_armor_sets_have_base_image(self):
        """Verify most armor sets have non-empty 'image' field"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        with_image = 0
        without_image = []
        for armor in data["data"]:
            if armor.get("image"):
                with_image += 1
            else:
                without_image.append(armor["name"])
        
        # At least 90% should have images (allowing for some sets without wiki images)
        assert with_image >= 25, f"Only {with_image} armor sets have images. Missing: {without_image}"
    
    def test_armor_sets_have_variant_images_dict(self):
        """Verify each armor set has variant_images dict in response"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        missing_variant_images = []
        for armor in data["data"]:
            if "variant_images" not in armor:
                missing_variant_images.append(armor["name"])
        
        assert len(missing_variant_images) == 0, f"Armor sets missing variant_images: {missing_variant_images}"
    
    def test_adp_variant_images_differ_from_base(self):
        """Verify ADP variant images are different from base image"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        adp = next((a for a in data["data"] if a["name"] == "ADP"), None)
        assert adp is not None, "ADP armor not found"
        
        base_image = adp.get("image", "")
        variant_images = adp.get("variant_images", {})
        
        # Check that at least some variants have different images
        unique_variants = [v for v, url in variant_images.items() if url != base_image]
        assert len(unique_variants) >= 4, f"Expected at least 4 unique ADP variant images, got {len(unique_variants)}"
    
    def test_orc_mkx_variant_images_differ_from_base(self):
        """Verify ORC-mkX variant images are different from base image"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        orc = next((a for a in data["data"] if a["name"] == "ORC-mkX"), None)
        assert orc is not None, "ORC-mkX armor not found"
        
        base_image = orc.get("image", "")
        variant_images = orc.get("variant_images", {})
        
        # Check that variants have images (may fall back to base)
        unique_variants = [v for v, url in variant_images.items() if url != base_image]
        assert len(unique_variants) >= 2, f"Expected at least 2 unique ORC-mkX variant images, got {len(unique_variants)}"
    
    def test_overlord_variant_images_differ_from_base(self):
        """Verify Overlord variant images are different from base image"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        overlord = next((a for a in data["data"] if a["name"] == "Overlord"), None)
        assert overlord is not None, "Overlord armor not found"
        
        base_image = overlord.get("image", "")
        variant_images = overlord.get("variant_images", {})
        
        unique_variants = [v for v, url in variant_images.items() if url != base_image]
        assert len(unique_variants) >= 2, f"Expected at least 2 unique Overlord variant images, got {len(unique_variants)}"
    
    def test_macflex_variant_images_present(self):
        """Verify MacFlex has variant_images for its variants"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        macflex = next((a for a in data["data"] if a["name"] == "MacFlex"), None)
        assert macflex is not None, "MacFlex armor not found"
        
        variants = macflex.get("variants", [])
        variant_images = macflex.get("variant_images", {})
        
        # All variants should have entries in variant_images
        for v in variants:
            assert v in variant_images, f"MacFlex variant '{v}' missing from variant_images"
    
    def test_new_sets_have_images(self):
        """Verify new armor sets (ORC-mkX, MacFlex, Venture) have images"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        new_sets_with_images = ["ORC-mkX", "MacFlex", "Venture", "Inquisitor"]
        for name in new_sets_with_images:
            armor = next((a for a in data["data"] if a["name"] == name), None)
            assert armor is not None, f"{name} armor not found"
            assert armor.get("image"), f"{name} should have a base image"
    
    def test_armor_response_structure(self):
        """Verify armor response has correct structure with all expected fields"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        
        # Check first armor set has all expected fields
        armor = data["data"][0]
        expected_fields = ["id", "name", "type", "manufacturer", "temp_max", "temp_min", 
                          "radiation", "description", "price_auec", "locations", 
                          "loot_locations", "variants", "image", "variant_images"]
        
        for field in expected_fields:
            assert field in armor, f"Missing field '{field}' in armor response"
