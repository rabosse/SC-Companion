"""
Tests for Personal Gear API endpoints - FPS Weapons and Armor Sets
/api/gear/weapons and /api/gear/armor are PUBLIC endpoints (no auth required)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGearWeaponsAPI:
    """Test the /api/gear/weapons endpoint - PUBLIC, no auth"""
    
    def test_gear_weapons_returns_success(self):
        """Weapons endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    def test_gear_weapons_returns_28_items(self):
        """Weapons endpoint returns expected 28 weapons"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        assert len(data["data"]) == 28
    
    def test_gear_weapons_has_required_fields(self):
        """Each weapon has required fields: id, name, type, manufacturer, damage, ammo"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        required_fields = ["id", "name", "type", "manufacturer", "damage", "ammo", 
                          "fire_rate", "effective_range", "description", "locations"]
        
        for weapon in data["data"][:5]:  # Check first 5 weapons
            for field in required_fields:
                assert field in weapon, f"Weapon {weapon.get('name', 'unknown')} missing field: {field}"
    
    def test_gear_weapons_includes_pistols(self):
        """Weapons include pistol type"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        pistols = [w for w in data["data"] if w["type"] == "Pistol"]
        assert len(pistols) >= 4, "Should have at least 4 pistols"
    
    def test_gear_weapons_includes_smgs(self):
        """Weapons include SMG type"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        smgs = [w for w in data["data"] if w["type"] == "SMG"]
        assert len(smgs) >= 3, "Should have at least 3 SMGs"
    
    def test_gear_weapons_includes_assault_rifles(self):
        """Weapons include Assault Rifle type"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        ars = [w for w in data["data"] if w["type"] == "Assault Rifle"]
        assert len(ars) >= 4, "Should have at least 4 assault rifles"
    
    def test_gear_weapons_includes_sniper_rifles(self):
        """Weapons include Sniper Rifle type"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        snipers = [w for w in data["data"] if w["type"] == "Sniper Rifle"]
        assert len(snipers) >= 2, "Should have at least 2 sniper rifles"
    
    def test_gear_weapons_includes_shotguns(self):
        """Weapons include Shotgun type"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        shotguns = [w for w in data["data"] if w["type"] == "Shotgun"]
        assert len(shotguns) >= 2, "Should have at least 2 shotguns"
    
    def test_gear_weapons_includes_lmgs(self):
        """Weapons include LMG type"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        lmgs = [w for w in data["data"] if w["type"] == "LMG"]
        assert len(lmgs) >= 2, "Should have at least 2 LMGs"
    
    def test_gear_weapons_have_variants(self):
        """Some weapons have variants"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        weapons_with_variants = [w for w in data["data"] if w.get("variants") and len(w["variants"]) > 0]
        assert len(weapons_with_variants) >= 10, "Should have at least 10 weapons with variants"
    
    def test_gear_weapons_arclight_exists(self):
        """Arclight pistol exists with correct data"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        arclight = next((w for w in data["data"] if "arclight" in w["id"].lower()), None)
        assert arclight is not None
        assert arclight["type"] == "Pistol"
        assert arclight["manufacturer"] == "Klaus & Werner"
    
    def test_gear_weapons_p8_smg_exists(self):
        """P8-SMG exists with correct data"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        data = response.json()
        p8 = next((w for w in data["data"] if "p8" in w["id"].lower()), None)
        assert p8 is not None
        assert p8["type"] == "SMG"
        assert p8["manufacturer"] == "Behring"


class TestGearArmorAPI:
    """Test the /api/gear/armor endpoint - PUBLIC, no auth"""
    
    def test_gear_armor_returns_success(self):
        """Armor endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    def test_gear_armor_returns_21_items(self):
        """Armor endpoint returns expected 21 armor sets"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        assert len(data["data"]) == 21
    
    def test_gear_armor_has_required_fields(self):
        """Each armor has required fields: id, name, type, manufacturer, temp_max, temp_min"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        required_fields = ["id", "name", "type", "manufacturer", "temp_max", "temp_min", 
                          "radiation", "description", "locations"]
        
        for armor in data["data"][:5]:  # Check first 5 armor sets
            for field in required_fields:
                assert field in armor, f"Armor {armor.get('name', 'unknown')} missing field: {field}"
    
    def test_gear_armor_includes_heavy_type(self):
        """Armor includes Heavy type"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        heavy = [a for a in data["data"] if a["type"] == "Heavy"]
        assert len(heavy) >= 6, "Should have at least 6 heavy armor sets"
    
    def test_gear_armor_includes_medium_type(self):
        """Armor includes Medium type"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        medium = [a for a in data["data"] if a["type"] == "Medium"]
        assert len(medium) >= 4, "Should have at least 4 medium armor sets"
    
    def test_gear_armor_includes_light_type(self):
        """Armor includes Light type"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        light = [a for a in data["data"] if a["type"] == "Light"]
        assert len(light) >= 4, "Should have at least 4 light armor sets"
    
    def test_gear_armor_includes_flight_suits(self):
        """Armor includes Flight Suit type"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        flight = [a for a in data["data"] if a["type"] == "Flight Suit"]
        assert len(flight) >= 2, "Should have at least 2 flight suits"
    
    def test_gear_armor_have_variants(self):
        """Some armor have variants"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        armor_with_variants = [a for a in data["data"] if a.get("variants") and len(a["variants"]) > 0]
        assert len(armor_with_variants) >= 10, "Should have at least 10 armor with variants"
    
    def test_gear_armor_have_loot_locations(self):
        """Some armor have loot locations"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        armor_with_loot = [a for a in data["data"] if a.get("loot_locations") and len(a["loot_locations"]) > 0]
        assert len(armor_with_loot) >= 10, "Should have at least 10 armor with loot locations"
    
    def test_gear_armor_antium_exists(self):
        """Antium heavy armor exists with correct data"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        antium = next((a for a in data["data"] if "antium" in a["id"].lower()), None)
        assert antium is not None
        assert antium["type"] == "Heavy"
        assert antium["temp_max"] == 120  # Best environmental resistance
        assert antium["temp_min"] == -95
    
    def test_gear_armor_novikov_exists(self):
        """Novikov medium armor exists with good cold protection"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        data = response.json()
        novikov = next((a for a in data["data"] if "novikov" in a["id"].lower()), None)
        assert novikov is not None
        assert novikov["type"] == "Medium"
        assert novikov["temp_min"] <= -60  # Good cold protection


class TestGearAPINoAuth:
    """Test that gear endpoints don't require authentication"""
    
    def test_weapons_accessible_without_auth(self):
        """Weapons endpoint works without auth header"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", 
                               headers={"Content-Type": "application/json"})
        assert response.status_code == 200
        assert response.json()["success"] == True
    
    def test_armor_accessible_without_auth(self):
        """Armor endpoint works without auth header"""
        response = requests.get(f"{BASE_URL}/api/gear/armor", 
                               headers={"Content-Type": "application/json"})
        assert response.status_code == 200
        assert response.json()["success"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
