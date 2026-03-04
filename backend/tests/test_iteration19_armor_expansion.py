"""
Iteration 19: Testing 27 new armor sets added from CStone.
Tests: Total count (55), CStone images, variant data, loot-only sets, purchasable sets.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestArmorExpansion:
    """Test 27 new armor sets added from CStone."""
    
    # All 27 new armor set names
    NEW_ARMOR_SETS = [
        'Ana', 'Bokto', 'Citadel-SE', 'DCP Armor', 'Dust Devil', 'Dust Devil Armor',
        'Morozov-SH-I', 'Wrecker', 'Aves Shrike', 'Aves Starchaser', 'Aves Talon',
        'Carrion', 'Clash', 'DustUp', 'GCD-Army', 'Stitcher', 'Strata', 'Testudo',
        'Aztalan Galena', 'Aztalan Tamarack', 'Carnifex', 'Carnifex Armor', 'Chiron',
        'Field Recon Suit', 'Geist Armor', 'Microid Battle Suit', 'Piecemeal Armor'
    ]
    
    # Sets with multiple variants (name: expected_count)
    MULTI_VARIANT_SETS = {
        'Strata': 12, 'Testudo': 7, 'Geist Armor': 8, 'DCP Armor': 6,
        'Microid Battle Suit': 5, 'Carrion': 4, 'DustUp': 4, 'Morozov-SH-I': 4,
        'Citadel-SE': 3, 'Carnifex Armor': 3, 'Ana': 2, 'Wrecker': 2,
        'Piecemeal Armor': 2, 'Chiron': 2
    }
    
    # Loot-only sets (price_auec should be 0)
    LOOT_ONLY_SETS = [
        'Ana', 'Bokto', 'DCP Armor', 'Geist Armor', 'Dust Devil', 'Dust Devil Armor',
        'Morozov-SH-I', 'Wrecker', 'Aves Shrike', 'Aves Starchaser', 'Aves Talon',
        'Carrion', 'Clash', 'GCD-Army', 'Testudo', 'Aztalan Galena', 'Aztalan Tamarack',
        'Carnifex', 'Carnifex Armor', 'Chiron', 'Piecemeal Armor'
    ]
    
    # Purchasable sets (price_auec should be > 0)
    PURCHASABLE_SETS = ['DustUp', 'Strata', 'Microid Battle Suit', 'Field Recon Suit', 'Stitcher']
    
    @pytest.fixture(scope="class")
    def armor_data(self):
        """Fetch armor data once for all tests."""
        resp = requests.get(f"{BASE_URL}/api/gear/armor", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get('success') is True
        return data['data']
    
    def test_total_armor_count_is_55(self, armor_data):
        """Verify total armor sets is now 55 (was 28, added 27 new)."""
        assert len(armor_data) == 55, f"Expected 55 armor sets, got {len(armor_data)}"
    
    def test_all_27_new_sets_present(self, armor_data):
        """Verify all 27 new armor sets are in response."""
        armor_names = [a['name'] for a in armor_data]
        missing = [s for s in self.NEW_ARMOR_SETS if s not in armor_names]
        assert len(missing) == 0, f"Missing new armor sets: {missing}"
    
    def test_type_distribution(self, armor_data):
        """Verify armor type distribution (Heavy: 17, Medium: 19, Light: 17, Flight Suit: 2)."""
        types = {'Heavy': 0, 'Medium': 0, 'Light': 0, 'Flight Suit': 0}
        for a in armor_data:
            t = a.get('type', '')
            if t in types:
                types[t] += 1
        assert types['Heavy'] == 17, f"Expected 17 Heavy, got {types['Heavy']}"
        assert types['Medium'] == 19, f"Expected 19 Medium, got {types['Medium']}"
        assert types['Light'] == 17, f"Expected 17 Light, got {types['Light']}"
        assert types['Flight Suit'] == 2, f"Expected 2 Flight Suit, got {types['Flight Suit']}"
    
    def test_cstone_images_for_52_sets(self, armor_data):
        """Verify at least 52 sets have CStone images (3 without: Novikov, Sterling, Odyssey II)."""
        cstone_count = sum(1 for a in armor_data if 'cstone.space' in a.get('image', ''))
        assert cstone_count >= 52, f"Expected at least 52 CStone images, got {cstone_count}"
    
    def test_new_sets_have_cstone_images(self, armor_data):
        """Verify all 27 new sets have CStone images."""
        for a in armor_data:
            if a['name'] in self.NEW_ARMOR_SETS:
                img = a.get('image', '')
                assert 'cstone.space' in img, f"{a['name']} missing CStone image: {img}"
    
    def test_strata_has_12_variants(self, armor_data):
        """Verify Strata has 12 variants with CStone images and variant_data."""
        strata = next((a for a in armor_data if a['name'] == 'Strata'), None)
        assert strata is not None, "Strata not found"
        assert len(strata.get('variants', [])) == 12, f"Strata: expected 12 variants, got {len(strata.get('variants', []))}"
        
        # Check variant_images
        variant_images = strata.get('variant_images', {})
        cstone_count = sum(1 for v in variant_images.values() if 'cstone.space' in v)
        assert cstone_count == 12, f"Strata: expected 12 CStone variant images, got {cstone_count}"
        
        # Check variant_data
        variant_data = strata.get('variant_data', {})
        assert len(variant_data) == 12, f"Strata: expected 12 variant_data entries, got {len(variant_data)}"
    
    def test_testudo_has_7_variants(self, armor_data):
        """Verify Testudo has 7 variants with CStone images."""
        testudo = next((a for a in armor_data if a['name'] == 'Testudo'), None)
        assert testudo is not None, "Testudo not found"
        assert len(testudo.get('variants', [])) == 7, f"Testudo: expected 7 variants, got {len(testudo.get('variants', []))}"
        
        variant_images = testudo.get('variant_images', {})
        cstone_count = sum(1 for v in variant_images.values() if 'cstone.space' in v)
        assert cstone_count == 7, f"Testudo: expected 7 CStone variant images, got {cstone_count}"
    
    def test_geist_armor_has_8_variants(self, armor_data):
        """Verify Geist Armor has 8 variants with CStone images."""
        geist = next((a for a in armor_data if a['name'] == 'Geist Armor'), None)
        assert geist is not None, "Geist Armor not found"
        assert len(geist.get('variants', [])) == 8, f"Geist Armor: expected 8 variants, got {len(geist.get('variants', []))}"
        
        variant_images = geist.get('variant_images', {})
        cstone_count = sum(1 for v in variant_images.values() if 'cstone.space' in v)
        assert cstone_count == 8, f"Geist Armor: expected 8 CStone variant images, got {cstone_count}"
    
    def test_dcp_armor_has_6_variants(self, armor_data):
        """Verify DCP Armor has 6 variants with CStone images."""
        dcp = next((a for a in armor_data if a['name'] == 'DCP Armor'), None)
        assert dcp is not None, "DCP Armor not found"
        assert len(dcp.get('variants', [])) == 6, f"DCP Armor: expected 6 variants, got {len(dcp.get('variants', []))}"
    
    def test_microid_battle_suit_has_5_variants(self, armor_data):
        """Verify Microid Battle Suit has 5 variants."""
        microid = next((a for a in armor_data if a['name'] == 'Microid Battle Suit'), None)
        assert microid is not None, "Microid Battle Suit not found"
        assert len(microid.get('variants', [])) == 5, f"Microid Battle Suit: expected 5 variants, got {len(microid.get('variants', []))}"
    
    def test_loot_only_sets_have_price_zero(self, armor_data):
        """Verify loot-only sets have price_auec = 0."""
        for a in armor_data:
            if a['name'] in self.LOOT_ONLY_SETS:
                price = a.get('price_auec', -1)
                assert price == 0, f"{a['name']}: expected price_auec=0, got {price}"
    
    def test_loot_only_sets_have_sold_false_in_variant_data(self, armor_data):
        """Verify loot-only sets with variants have sold=false in variant_data."""
        # These sets have variants AND sold=false entries in CStone
        sets_with_sold_false = ['Ana', 'DCP Armor', 'Dust Devil', 'Morozov-SH-I', 'Wrecker',
                                'Carrion', 'Testudo', 'Carnifex', 'Carnifex Armor', 'Chiron',
                                'Geist Armor', 'Piecemeal Armor']
        for a in armor_data:
            if a['name'] in sets_with_sold_false:
                variant_data = a.get('variant_data', {})
                if variant_data:
                    has_sold_false = any(v.get('sold') is False for v in variant_data.values())
                    assert has_sold_false, f"{a['name']}: expected at least one variant with sold=false"
    
    def test_purchasable_sets_have_price(self, armor_data):
        """Verify purchasable sets have price_auec > 0."""
        for a in armor_data:
            if a['name'] in self.PURCHASABLE_SETS:
                price = a.get('price_auec', 0)
                assert price > 0, f"{a['name']}: expected price_auec > 0, got {price}"
    
    def test_purchasable_sets_have_locations(self, armor_data):
        """Verify purchasable sets have locations array with entries."""
        for a in armor_data:
            if a['name'] in self.PURCHASABLE_SETS:
                locations = a.get('locations', [])
                assert len(locations) > 0, f"{a['name']}: expected locations, got {len(locations)}"
    
    def test_variant_data_structure(self, armor_data):
        """Verify variant_data has correct structure (price_auec, locations, loot_locations, sold)."""
        strata = next((a for a in armor_data if a['name'] == 'Strata'), None)
        assert strata is not None
        variant_data = strata.get('variant_data', {})
        
        for variant_name, data in variant_data.items():
            assert 'price_auec' in data, f"{variant_name}: missing price_auec"
            assert 'locations' in data, f"{variant_name}: missing locations"
            assert 'loot_locations' in data, f"{variant_name}: missing loot_locations"
            assert 'sold' in data, f"{variant_name}: missing sold"


class TestArmorRegressionCheck:
    """Regression tests for existing armor functionality."""
    
    @pytest.fixture(scope="class")
    def armor_data(self):
        """Fetch armor data once for all tests."""
        resp = requests.get(f"{BASE_URL}/api/gear/armor", timeout=30)
        assert resp.status_code == 200
        return resp.json()['data']
    
    def test_original_adp_armor_still_works(self, armor_data):
        """Verify original ADP armor still has correct data."""
        adp = next((a for a in armor_data if a['name'] == 'ADP'), None)
        assert adp is not None, "ADP not found"
        assert adp['type'] == 'Heavy'
        assert 'cstone.space' in adp.get('image', '')
        assert len(adp.get('variants', [])) == 8
    
    def test_original_citadel_armor_still_works(self, armor_data):
        """Verify original Citadel armor still has correct data."""
        citadel = next((a for a in armor_data if a['name'] == 'Citadel'), None)
        assert citadel is not None, "Citadel not found"
        assert citadel['type'] == 'Heavy'
        assert len(citadel.get('variants', [])) == 7
    
    def test_all_armor_have_required_fields(self, armor_data):
        """Verify all armor sets have required fields."""
        required_fields = ['id', 'name', 'type', 'manufacturer', 'description']
        for a in armor_data:
            for field in required_fields:
                assert field in a, f"{a['name']}: missing required field '{field}'"


class TestWeaponsRegression:
    """Regression test for FPS Weapons endpoint."""
    
    def test_weapons_endpoint_returns_50_items(self):
        """Verify weapons endpoint still returns 50 items."""
        resp = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get('success') is True
        assert len(data['data']) == 50


class TestEquipmentRegression:
    """Regression test for Equipment endpoint."""
    
    def test_equipment_endpoint_returns_30_items(self):
        """Verify equipment endpoint still returns 30 items."""
        resp = requests.get(f"{BASE_URL}/api/gear/equipment", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get('success') is True
        assert len(data['data']) == 30
