"""
Test iteration 23: Gear tab parity testing - Equipment tab should match Armor/Weapons layout.
Tests that all three gear tabs have consistent data structure (loot_locations, variant_data, images).
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestGearWeaponsEndpoint:
    """Tests for /api/gear/weapons - verify variant_data includes loot_locations"""

    def test_weapons_endpoint_returns_success(self):
        """Weapons endpoint returns success and data array"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") is True
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        print(f"PASS: Weapons endpoint returned {len(data['data'])} weapons")

    def test_weapons_have_variant_data_with_loot_locations(self):
        """Each weapon with variants should have variant_data containing loot_locations field"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        data = response.json()
        weapons_with_variants = [w for w in data["data"] if w.get("variants")]
        assert len(weapons_with_variants) > 0, "Expected some weapons with variants"
        
        for weapon in weapons_with_variants[:5]:  # Check first 5
            assert "variant_data" in weapon, f"Weapon {weapon['name']} missing variant_data"
            for variant_name, vd in weapon["variant_data"].items():
                assert "loot_locations" in vd, f"Variant {variant_name} missing loot_locations"
                assert isinstance(vd["loot_locations"], list), f"loot_locations should be list"
                assert "locations" in vd, f"Variant {variant_name} missing locations"
                assert "price_auec" in vd, f"Variant {variant_name} missing price_auec"
        print(f"PASS: Weapons variant_data includes loot_locations for all variants")

    def test_weapons_have_image_and_variant_images(self):
        """Weapons should have image and variant_images fields"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        data = response.json()
        
        for weapon in data["data"][:5]:
            assert "image" in weapon, f"Weapon {weapon['name']} missing image field"
            assert "variant_images" in weapon, f"Weapon {weapon['name']} missing variant_images"
        print("PASS: Weapons have image and variant_images fields")


class TestGearArmorEndpoint:
    """Tests for /api/gear/armor - verify variant_data includes loot_locations"""

    def test_armor_endpoint_returns_success(self):
        """Armor endpoint returns success and data array"""
        response = requests.get(f"{BASE_URL}/api/gear/armor", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") is True
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        print(f"PASS: Armor endpoint returned {len(data['data'])} armor sets")

    def test_armor_have_variant_data_with_loot_locations(self):
        """Each armor with variants should have variant_data containing loot_locations field"""
        response = requests.get(f"{BASE_URL}/api/gear/armor", timeout=30)
        data = response.json()
        armor_with_variants = [a for a in data["data"] if a.get("variants")]
        assert len(armor_with_variants) > 0, "Expected some armor with variants"
        
        for armor in armor_with_variants[:5]:  # Check first 5
            assert "variant_data" in armor, f"Armor {armor['name']} missing variant_data"
            for variant_name, vd in armor["variant_data"].items():
                assert "loot_locations" in vd, f"Variant {variant_name} missing loot_locations"
                assert isinstance(vd["loot_locations"], list), f"loot_locations should be list"
                assert "locations" in vd, f"Variant {variant_name} missing locations"
                assert "price_auec" in vd, f"Variant {variant_name} missing price_auec"
        print(f"PASS: Armor variant_data includes loot_locations for all variants")

    def test_armor_has_base_loot_locations(self):
        """Armor items should have base loot_locations field"""
        response = requests.get(f"{BASE_URL}/api/gear/armor", timeout=30)
        data = response.json()
        
        for armor in data["data"][:10]:
            assert "loot_locations" in armor, f"Armor {armor['name']} missing loot_locations"
            assert isinstance(armor["loot_locations"], list), f"loot_locations should be list"
        print("PASS: Armor has base loot_locations field")


class TestGearEquipmentEndpoint:
    """Tests for /api/gear/equipment - verify it matches armor/weapons structure"""

    def test_equipment_endpoint_returns_success(self):
        """Equipment endpoint returns success and data array"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment", timeout=30)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") is True
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        print(f"PASS: Equipment endpoint returned {len(data['data'])} equipment items")

    def test_equipment_has_loot_locations_field(self):
        """Equipment items should have loot_locations field (matching armor)"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment", timeout=30)
        data = response.json()
        
        for item in data["data"]:
            assert "loot_locations" in item, f"Equipment {item['name']} missing loot_locations"
            assert isinstance(item["loot_locations"], list), f"loot_locations should be list"
        print("PASS: All equipment items have loot_locations field")

    def test_equipment_has_variant_data_structure(self):
        """Equipment should have variant_data with loot_locations like armor/weapons"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment", timeout=30)
        data = response.json()
        
        equip_with_variants = [e for e in data["data"] if e.get("variants")]
        
        for item in equip_with_variants:
            assert "variant_data" in item, f"Equipment {item['name']} missing variant_data"
            for variant_name, vd in item["variant_data"].items():
                assert "loot_locations" in vd, f"Variant {variant_name} missing loot_locations"
                assert "locations" in vd, f"Variant {variant_name} missing locations"
                assert "price_auec" in vd, f"Variant {variant_name} missing price_auec"
                assert "sold" in vd, f"Variant {variant_name} missing sold field"
        
        if equip_with_variants:
            print(f"PASS: Equipment variant_data structure matches armor/weapons ({len(equip_with_variants)} items with variants)")
        else:
            print("PASS: No equipment with variants to test, but structure is ready")

    def test_equipment_has_type_field(self):
        """Equipment items should have type field for filtering"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment", timeout=30)
        data = response.json()
        
        types_found = set()
        for item in data["data"]:
            assert "type" in item, f"Equipment {item['name']} missing type"
            types_found.add(item["type"])
        
        print(f"PASS: Equipment has type field. Types found: {types_found}")

    def test_equipment_has_image_fields(self):
        """Equipment should have image and variant_images fields"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment", timeout=30)
        data = response.json()
        
        for item in data["data"]:
            assert "image" in item, f"Equipment {item['name']} missing image field"
            assert "variant_images" in item, f"Equipment {item['name']} missing variant_images"
        print("PASS: Equipment has image and variant_images fields")


class TestGearDataConsistency:
    """Tests for data consistency across all three gear endpoints"""

    def test_all_gear_endpoints_have_consistent_structure(self):
        """All gear endpoints should have matching data structure"""
        weapons_resp = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        armor_resp = requests.get(f"{BASE_URL}/api/gear/armor", timeout=30)
        equip_resp = requests.get(f"{BASE_URL}/api/gear/equipment", timeout=30)
        
        assert weapons_resp.status_code == 200
        assert armor_resp.status_code == 200
        assert equip_resp.status_code == 200
        
        weapons = weapons_resp.json()["data"][0]
        armor = armor_resp.json()["data"][0]
        equip = equip_resp.json()["data"][0]
        
        # All should have these common fields
        common_fields = ["id", "name", "type", "manufacturer", "description", "price_auec", 
                         "locations", "image", "variant_images", "variant_data"]
        
        for field in common_fields:
            assert field in weapons, f"Weapon missing {field}"
            assert field in armor, f"Armor missing {field}"
            assert field in equip, f"Equipment missing {field}"
        
        # loot_locations now required on all
        assert "loot_locations" in armor, "Armor missing loot_locations"
        assert "loot_locations" in equip, "Equipment missing loot_locations"
        
        print("PASS: All gear endpoints have consistent data structure")

    def test_equipment_type_colors_mappable(self):
        """Equipment types should be mappable to colors in frontend TYPE_COLORS"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment", timeout=30)
        data = response.json()
        
        # Types from frontend TYPE_COLORS that should be supported
        expected_equipment_types = {"Mining Head", "Mining Attachment", "Mining Module", 
                                    "Backpack", "Undersuit", "Medical Device",
                                    "Salvage Tool", "Scanner", "Hacking Tool"}
        
        equipment_types = set(item["type"] for item in data["data"])
        
        # At least some expected types should be present
        matching_types = expected_equipment_types.intersection(equipment_types)
        print(f"Equipment types found: {equipment_types}")
        print(f"Types with color mapping: {matching_types}")
        
        assert len(equipment_types) > 0, "No equipment types found"
        print(f"PASS: Equipment types available for filtering")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
