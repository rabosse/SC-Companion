"""
Test Suite for Weapon Card Redesign + Equipment Categories Expansion
Tests iteration 15 features:
1. FPS Weapons with wiki images (24/38 expected)
2. Equipment expanded to 30 items with Salvage Tools (3), Scanners (2), Hacking Tools (2)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestWeaponImages:
    """Tests for FPS Weapons with wiki images"""

    def test_weapons_endpoint_returns_200(self):
        """GET /api/gear/weapons returns 200 with success=true"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") is True, "Expected success=true"
        print("PASS: GET /api/gear/weapons returns 200 with success=true")

    def test_weapons_returns_38_items(self):
        """Weapons endpoint returns 38 items"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
        data = response.json()
        weapons = data.get("data", [])
        assert len(weapons) == 38, f"Expected 38 weapons, got {len(weapons)}"
        print(f"PASS: GET /api/gear/weapons returns {len(weapons)} items")

    def test_all_weapons_have_image_field(self):
        """All weapons have 'image' field (may be empty string)"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        weapons = data.get("data", [])
        
        for weapon in weapons:
            assert "image" in weapon, f"Weapon {weapon.get('name')} missing 'image' field"
        print(f"PASS: All {len(weapons)} weapons have 'image' field")

    def test_at_least_24_weapons_have_wiki_images(self):
        """At least 24 out of 38 weapons have non-empty wiki image URLs"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        weapons = data.get("data", [])
        
        weapons_with_images = [w for w in weapons if w.get("image")]
        count = len(weapons_with_images)
        
        print(f"Weapons with images: {count}/38")
        for w in weapons_with_images:
            print(f"  - {w['name']}: {w['image'][:80]}...")
        
        assert count >= 24, f"Expected at least 24 weapons with images, got {count}"
        print(f"PASS: {count}/38 weapons have wiki image URLs (expected >=24)")

    def test_wiki_image_urls_valid(self):
        """Wiki image URLs are from starcitizen.tools"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        weapons = data.get("data", [])
        
        weapons_with_images = [w for w in weapons if w.get("image")]
        
        for w in weapons_with_images:
            url = w["image"]
            assert "starcitizen.tools" in url, f"Invalid wiki URL for {w['name']}: {url}"
        
        print(f"PASS: All {len(weapons_with_images)} weapon wiki URLs are from starcitizen.tools")

    def test_weapons_have_required_fields(self):
        """All weapons have required fields for card display"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        weapons = data.get("data", [])
        
        required_fields = ["id", "name", "type", "size", "manufacturer", "damage", "ammo", "fire_rate", "effective_range", "description", "locations"]
        
        for weapon in weapons:
            for field in required_fields:
                assert field in weapon, f"Weapon {weapon.get('name')} missing '{field}' field"
        
        print(f"PASS: All {len(weapons)} weapons have required fields")

    def test_weapon_types_distribution(self):
        """Weapons have correct type distribution for filter buttons"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        weapons = data.get("data", [])
        
        type_counts = {}
        for w in weapons:
            t = w.get("type")
            type_counts[t] = type_counts.get(t, 0) + 1
        
        print("Weapon type distribution:")
        for t, c in sorted(type_counts.items()):
            print(f"  {t}: {c}")
        
        # Expected types
        assert "Pistol" in type_counts
        assert "SMG" in type_counts
        assert "Assault Rifle" in type_counts
        assert "Sniper Rifle" in type_counts
        
        print("PASS: Weapons have expected type distribution")


class TestEquipmentExpansion:
    """Tests for Equipment category expansion"""

    def test_equipment_endpoint_returns_200(self):
        """GET /api/gear/equipment returns 200 with success=true"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("success") is True, "Expected success=true"
        print("PASS: GET /api/gear/equipment returns 200 with success=true")

    def test_equipment_returns_30_items(self):
        """Equipment endpoint returns 30 items (was 23, now expanded)"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        assert response.status_code == 200
        data = response.json()
        equipment = data.get("data", [])
        
        print(f"Equipment count: {len(equipment)}")
        assert len(equipment) == 30, f"Expected 30 equipment items, got {len(equipment)}"
        print(f"PASS: GET /api/gear/equipment returns {len(equipment)} items (expanded from 23)")

    def test_equipment_has_salvage_tools(self):
        """Equipment includes 3 Salvage Tool items"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = response.json()
        equipment = data.get("data", [])
        
        salvage_tools = [e for e in equipment if e.get("type") == "Salvage Tool"]
        
        print(f"Salvage Tools found: {len(salvage_tools)}")
        for s in salvage_tools:
            print(f"  - {s['name']}")
        
        assert len(salvage_tools) == 3, f"Expected 3 Salvage Tools, got {len(salvage_tools)}"
        print("PASS: Equipment includes 3 Salvage Tool items")

    def test_equipment_has_scanners(self):
        """Equipment includes 2 Scanner items"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = response.json()
        equipment = data.get("data", [])
        
        scanners = [e for e in equipment if e.get("type") == "Scanner"]
        
        print(f"Scanners found: {len(scanners)}")
        for s in scanners:
            print(f"  - {s['name']}")
        
        assert len(scanners) == 2, f"Expected 2 Scanners, got {len(scanners)}"
        print("PASS: Equipment includes 2 Scanner items")

    def test_equipment_has_hacking_tools(self):
        """Equipment includes 2 Hacking Tool items"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = response.json()
        equipment = data.get("data", [])
        
        hacking_tools = [e for e in equipment if e.get("type") == "Hacking Tool"]
        
        print(f"Hacking Tools found: {len(hacking_tools)}")
        for h in hacking_tools:
            print(f"  - {h['name']}")
        
        assert len(hacking_tools) == 2, f"Expected 2 Hacking Tools, got {len(hacking_tools)}"
        print("PASS: Equipment includes 2 Hacking Tool items")

    def test_equipment_type_distribution(self):
        """Equipment has correct type distribution including new types"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        data = response.json()
        equipment = data.get("data", [])
        
        type_counts = {}
        for e in equipment:
            t = e.get("type")
            type_counts[t] = type_counts.get(t, 0) + 1
        
        print("Equipment type distribution:")
        for t, c in sorted(type_counts.items()):
            print(f"  {t}: {c}")
        
        # Verify new types exist
        assert "Salvage Tool" in type_counts, "Missing 'Salvage Tool' type"
        assert "Scanner" in type_counts, "Missing 'Scanner' type"
        assert "Hacking Tool" in type_counts, "Missing 'Hacking Tool' type"
        
        print("PASS: Equipment has all expected types including new categories")


class TestRegressionChecks:
    """Regression tests for existing functionality"""

    def test_health_endpoint(self):
        """Health endpoint returns ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS: /api/health returns ok")

    def test_armor_endpoint_21_items(self):
        """Armor endpoint still returns 21 items"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        armor = data.get("data", [])
        assert len(armor) == 21, f"Expected 21 armor sets, got {len(armor)}"
        print(f"PASS: GET /api/gear/armor returns {len(armor)} items (regression)")

    def test_armor_has_images(self):
        """Armor items still have wiki images"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        armor = data.get("data", [])
        
        armor_with_images = [a for a in armor if a.get("image")]
        count = len(armor_with_images)
        
        assert count >= 18, f"Expected at least 18 armor items with images, got {count}"
        print(f"PASS: {count}/21 armor items have wiki images (regression)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
