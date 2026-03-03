"""
Test armor card redesign with wiki images feature (iteration_14)
Tests:
- GET /api/gear/armor returns armor sets with 'image' field
- At least 18 out of 21 armor sets have non-empty image URLs
- Armor types (Heavy, Medium, Light, Flight Suit) are properly categorized
- Required fields: id, name, type, manufacturer, temp_max, temp_min, radiation, variants
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestArmorWikiImages:
    """Tests for armor wiki images feature"""

    def test_armor_endpoint_returns_success(self):
        """GET /api/gear/armor returns 200 with success=true"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        print("PASS: GET /api/gear/armor returns 200 with success=true")

    def test_armor_returns_21_items(self):
        """GET /api/gear/armor returns exactly 21 armor sets"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        items = data.get("data", [])
        assert len(items) == 21, f"Expected 21 armor sets, got {len(items)}"
        print(f"PASS: GET /api/gear/armor returns 21 armor sets")

    def test_armor_has_image_field(self):
        """All armor items have 'image' field (can be empty string for missing)"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        items = data.get("data", [])
        
        for item in items:
            assert "image" in item, f"Armor '{item.get('name')}' missing 'image' field"
        print("PASS: All armor items have 'image' field")

    def test_at_least_18_have_wiki_images(self):
        """At least 18 out of 21 armor sets have non-empty wiki image URLs"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        items = data.get("data", [])
        
        with_images = [a for a in items if a.get("image")]
        without_images = [a.get("name") for a in items if not a.get("image")]
        
        assert len(with_images) >= 18, f"Expected at least 18 images, got {len(with_images)}"
        print(f"PASS: {len(with_images)}/21 armor sets have wiki images")
        print(f"      Missing images: {without_images}")

    def test_image_urls_are_valid_wiki_urls(self):
        """Wiki image URLs start with https://media.starcitizen.tools/"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        items = data.get("data", [])
        
        for item in items:
            img = item.get("image", "")
            if img:  # Only check non-empty URLs
                assert img.startswith("https://media.starcitizen.tools/"), \
                    f"Image URL for '{item.get('name')}' is not from starcitizen.tools wiki: {img}"
        print("PASS: All wiki image URLs are from starcitizen.tools")

    def test_armor_types_correct(self):
        """Armor types are Heavy, Medium, Light, or Flight Suit"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        items = data.get("data", [])
        
        valid_types = {"Heavy", "Medium", "Light", "Flight Suit"}
        type_counts = {}
        
        for item in items:
            armor_type = item.get("type")
            assert armor_type in valid_types, f"Invalid type '{armor_type}' for '{item.get('name')}'"
            type_counts[armor_type] = type_counts.get(armor_type, 0) + 1
        
        assert type_counts.get("Heavy", 0) == 9, f"Expected 9 Heavy, got {type_counts.get('Heavy', 0)}"
        assert type_counts.get("Medium", 0) == 5, f"Expected 5 Medium, got {type_counts.get('Medium', 0)}"
        assert type_counts.get("Light", 0) == 5, f"Expected 5 Light, got {type_counts.get('Light', 0)}"
        assert type_counts.get("Flight Suit", 0) == 2, f"Expected 2 Flight Suit, got {type_counts.get('Flight Suit', 0)}"
        print(f"PASS: Armor types correct - Heavy: 9, Medium: 5, Light: 5, Flight Suit: 2")

    def test_armor_required_fields(self):
        """Each armor item has required fields for card display"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        items = data.get("data", [])
        
        required_fields = ["id", "name", "type", "manufacturer", "temp_max", "temp_min", "radiation", "description"]
        
        for item in items:
            for field in required_fields:
                assert field in item, f"Armor '{item.get('name')}' missing required field '{field}'"
        print("PASS: All armor items have required fields for card display")

    def test_armor_has_variants_field(self):
        """Armor items have 'variants' field (can be empty list)"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        items = data.get("data", [])
        
        items_with_variants = 0
        for item in items:
            assert "variants" in item, f"Armor '{item.get('name')}' missing 'variants' field"
            if item.get("variants"):
                items_with_variants += 1
        
        print(f"PASS: All armor items have 'variants' field ({items_with_variants} have variants)")

    def test_armor_temp_stats_numeric(self):
        """Temperature and radiation stats are numeric"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        items = data.get("data", [])
        
        for item in items:
            name = item.get("name")
            assert isinstance(item.get("temp_max"), (int, float)), f"{name} temp_max not numeric"
            assert isinstance(item.get("temp_min"), (int, float)), f"{name} temp_min not numeric"
            assert isinstance(item.get("radiation"), (int, float)), f"{name} radiation not numeric"
        print("PASS: All temp/radiation stats are numeric")


class TestRegressionGearEndpoints:
    """Regression tests for other gear endpoints"""

    def test_fps_weapons_endpoint(self):
        """GET /api/gear/weapons still returns 38 items"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        items = data.get("data", [])
        assert len(items) == 38, f"Expected 38 weapons, got {len(items)}"
        print("PASS: FPS Weapons endpoint returns 38 items")

    def test_equipment_endpoint(self):
        """GET /api/gear/equipment still returns 23 items"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        items = data.get("data", [])
        assert len(items) == 23, f"Expected 23 equipment, got {len(items)}"
        print("PASS: Equipment endpoint returns 23 items")

    def test_health_endpoint(self):
        """Health endpoint returns ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS: Health endpoint returns ok")
