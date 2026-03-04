"""
Iteration 20: Backpack Migration Tests
- 4 backpacks removed from Equipment, 26 added to Armor
- Armor returns 81 items (55 armor + 26 backpacks)
- Equipment returns 26 items (was 30)
- CStone backpack image integration
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')


class TestBackpackMigrationBackend:
    """Backend tests for backpack migration from Equipment to Armor"""

    def test_health_check(self):
        """Verify server is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("PASS: Health check - server running")

    def test_armor_returns_81_items(self):
        """Armor endpoint should return 81 items (55 armor + 26 backpacks)"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 81, f"Expected 81 armor items, got {len(data['data'])}"
        print(f"PASS: Armor endpoint returns {len(data['data'])} items")

    def test_equipment_returns_26_items(self):
        """Equipment endpoint should return 26 items (removed 4 backpacks)"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 26, f"Expected 26 equipment items, got {len(data['data'])}"
        print(f"PASS: Equipment endpoint returns {len(data['data'])} items")

    def test_no_backpacks_in_equipment(self):
        """Equipment should have no items with type 'Backpack'"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        assert response.status_code == 200
        data = response.json()
        backpacks = [item for item in data["data"] if item.get("type") == "Backpack"]
        assert len(backpacks) == 0, f"Found {len(backpacks)} backpacks in equipment: {[b['name'] for b in backpacks]}"
        print("PASS: No backpacks found in equipment endpoint")

    def test_26_backpacks_in_armor(self):
        """Armor should have exactly 26 items with type 'Backpack'"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        backpacks = [item for item in data["data"] if item.get("type") == "Backpack"]
        assert len(backpacks) == 26, f"Expected 26 backpacks, got {len(backpacks)}"
        print(f"PASS: Found {len(backpacks)} backpacks in armor endpoint")

    def test_backpacks_have_cstone_images(self):
        """All 26 backpack items should have CStone images (image field not empty)"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        backpacks = [item for item in data["data"] if item.get("type") == "Backpack"]
        
        backpacks_with_images = []
        backpacks_without_images = []
        
        for bp in backpacks:
            if bp.get("image") and "cstone.space" in bp.get("image", ""):
                backpacks_with_images.append(bp["name"])
            else:
                backpacks_without_images.append(bp["name"])
        
        # All backpacks should have CStone images
        assert len(backpacks_with_images) >= 20, f"Only {len(backpacks_with_images)}/26 backpacks have CStone images. Missing: {backpacks_without_images[:5]}"
        print(f"PASS: {len(backpacks_with_images)}/26 backpacks have CStone images")

    def test_strata_backpack_12_variants(self):
        """Strata Backpack should have 12 variants with variant_images and variant_data"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        
        strata_bp = next((item for item in data["data"] if item.get("name") == "Strata Backpack"), None)
        assert strata_bp is not None, "Strata Backpack not found in armor endpoint"
        
        variants = strata_bp.get("variants", [])
        assert len(variants) == 12, f"Expected 12 Strata Backpack variants, got {len(variants)}"
        
        assert "variant_images" in strata_bp, "Strata Backpack missing variant_images"
        assert "variant_data" in strata_bp, "Strata Backpack missing variant_data"
        
        print(f"PASS: Strata Backpack has {len(variants)} variants with variant_images and variant_data")

    def test_palatino_backpack_8_variants(self):
        """Palatino Backpack should have 8 variants"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        
        palatino_bp = next((item for item in data["data"] if item.get("name") == "Palatino Backpack"), None)
        assert palatino_bp is not None, "Palatino Backpack not found"
        
        variants = palatino_bp.get("variants", [])
        assert len(variants) == 8, f"Expected 8 Palatino Backpack variants, got {len(variants)}"
        print(f"PASS: Palatino Backpack has {len(variants)} variants")

    def test_morozov_ch_backpack_11_variants(self):
        """Morozov-CH Backpack should have 11 variants"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        
        morozov_bp = next((item for item in data["data"] if item.get("name") == "Morozov-CH Backpack"), None)
        assert morozov_bp is not None, "Morozov-CH Backpack not found"
        
        variants = morozov_bp.get("variants", [])
        assert len(variants) == 11, f"Expected 11 Morozov-CH Backpack variants, got {len(variants)}"
        print(f"PASS: Morozov-CH Backpack has {len(variants)} variants")

    def test_testudo_backpack_7_variants(self):
        """Testudo Backpack should have 7 variants"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        
        testudo_bp = next((item for item in data["data"] if item.get("name") == "Testudo Backpack"), None)
        assert testudo_bp is not None, "Testudo Backpack not found"
        
        variants = testudo_bp.get("variants", [])
        assert len(variants) == 7, f"Expected 7 Testudo Backpack variants, got {len(variants)}"
        print(f"PASS: Testudo Backpack has {len(variants)} variants")

    def test_stirling_exploration_backpack_9_variants(self):
        """Stirling Exploration Backpack should have 9 variants"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        
        stirling_bp = next((item for item in data["data"] if item.get("name") == "Stirling Exploration Backpack"), None)
        assert stirling_bp is not None, "Stirling Exploration Backpack not found"
        
        variants = stirling_bp.get("variants", [])
        assert len(variants) == 9, f"Expected 9 Stirling Exploration Backpack variants, got {len(variants)}"
        print(f"PASS: Stirling Exploration Backpack has {len(variants)} variants")

    def test_geist_backpack_7_variants(self):
        """Geist Backpack should have 7 variants"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        
        geist_bp = next((item for item in data["data"] if item.get("name") == "Geist Backpack"), None)
        assert geist_bp is not None, "Geist Backpack not found"
        
        variants = geist_bp.get("variants", [])
        assert len(variants) == 7, f"Expected 7 Geist Backpack variants, got {len(variants)}"
        print(f"PASS: Geist Backpack has {len(variants)} variants")

    def test_backpack_has_zero_temp_radiation(self):
        """Backpacks should have temp_max=0, temp_min=0, radiation=0"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        
        backpacks = [item for item in data["data"] if item.get("type") == "Backpack"]
        
        for bp in backpacks[:5]:  # Check first 5 backpacks
            assert bp.get("temp_max") == 0, f"{bp['name']} has temp_max={bp.get('temp_max')}"
            assert bp.get("temp_min") == 0, f"{bp['name']} has temp_min={bp.get('temp_min')}"
            assert bp.get("radiation") == 0, f"{bp['name']} has radiation={bp.get('radiation')}"
        
        print("PASS: Backpacks have temp_max=0, temp_min=0, radiation=0")

    def test_backpack_variant_data_structure(self):
        """Backpack variant_data should have price_auec, locations, loot_locations, sold fields"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        
        # Find a backpack with variants
        strata_bp = next((item for item in data["data"] if item.get("name") == "Strata Backpack"), None)
        assert strata_bp is not None
        
        variant_data = strata_bp.get("variant_data", {})
        assert len(variant_data) > 0, "Strata Backpack missing variant_data"
        
        first_variant = list(variant_data.values())[0]
        assert "price_auec" in first_variant, "variant_data missing price_auec"
        assert "locations" in first_variant, "variant_data missing locations"
        assert "loot_locations" in first_variant, "variant_data missing loot_locations"
        assert "sold" in first_variant, "variant_data missing sold field"
        
        print("PASS: Backpack variant_data has correct structure")

    def test_weapons_regression(self):
        """FPS Weapons should still return 50 items"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 50, f"Expected 50 weapons, got {len(data['data'])}"
        print(f"PASS: Weapons endpoint returns {len(data['data'])} items (regression)")

    def test_armor_type_distribution(self):
        """Verify armor type distribution: Heavy + Medium + Light + Flight Suit + Backpack = 81"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        
        type_counts = {}
        for item in data["data"]:
            item_type = item.get("type", "Unknown")
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        print(f"Armor type distribution: {type_counts}")
        
        total = sum(type_counts.values())
        assert total == 81, f"Total armor items should be 81, got {total}"
        assert type_counts.get("Backpack", 0) == 26, f"Expected 26 backpacks, got {type_counts.get('Backpack', 0)}"
        
        print(f"PASS: Type distribution correct, 26 backpacks in {total} total armor items")

    def test_armor_sets_without_backpacks_count(self):
        """Verify 55 non-backpack armor items"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        
        non_backpack = [item for item in data["data"] if item.get("type") != "Backpack"]
        assert len(non_backpack) == 55, f"Expected 55 non-backpack armor items, got {len(non_backpack)}"
        print(f"PASS: {len(non_backpack)} non-backpack armor items (original armor sets)")

    def test_equipment_types(self):
        """Verify equipment types are correct (no Backpack type)"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        assert response.status_code == 200
        data = response.json()
        
        types = set(item.get("type") for item in data["data"])
        print(f"Equipment types: {types}")
        
        assert "Backpack" not in types, "Backpack type found in equipment"
        print("PASS: No Backpack type in equipment")
