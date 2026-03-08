"""
CStone Finder Integration Tests - Iteration 29
Tests all CStone data endpoints for Star Citizen Fleet Manager.

Features tested:
- GET /api/components - Vehicle components from CStone (coolers, power, quantum, shields)
- GET /api/weapons - Ship weapons from CStone
- GET /api/missiles - Missiles from CStone
- GET /api/item-locations/{item_id} - Purchase locations from CStone detail pages
- GET /api/gear/weapons - FPS weapons with CStone stats merged
- GET /api/gear/armor - Armor sets
- GET /api/gear/equipment - Equipment items
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestAuthentication:
    """Test authentication for CStone endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        # First try login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "cstonetest29",
            "password": "test123"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        
        # If login fails, register and login again
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": "cstonetest29",
            "password": "test123"
        })
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "cstonetest29",
            "password": "test123"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    def test_login_works(self, auth_token):
        """Verify authentication works"""
        assert auth_token is not None
        assert len(auth_token) > 0
        print(f"Auth token obtained successfully")


class TestCStoneComponents:
    """Test /api/components endpoint - Vehicle components from CStone"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "cstonetest29",
            "password": "test123"
        })
        if response.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "username": "cstonetest29",
                "password": "test123"
            })
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "cstonetest29",
                "password": "test123"
            })
        return response.json().get("access_token")
    
    def test_components_returns_cstone_data(self, auth_token):
        """GET /api/components returns data from CStone (source=cstone) with 270+ items"""
        response = requests.get(
            f"{BASE_URL}/api/components",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["source"] == "cstone", f"Expected source=cstone, got {data.get('source')}"
        assert len(data["data"]) >= 270, f"Expected 270+ components, got {len(data['data'])}"
        print(f"Components count: {len(data['data'])} (source: {data['source']})")
    
    def test_components_have_item_class_field(self, auth_token):
        """Components should have item_class field populated"""
        response = requests.get(
            f"{BASE_URL}/api/components",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check item_class values
        item_classes = set()
        for comp in data["data"]:
            if comp.get("item_class"):
                item_classes.add(comp["item_class"])
        
        # Should have Military, Civilian, Industrial, Stealth, Competition
        expected_classes = {"Military", "Civilian", "Industrial", "Stealth", "Competition"}
        found_classes = item_classes & expected_classes
        assert len(found_classes) >= 3, f"Expected at least 3 class types, found: {found_classes}"
        print(f"Found item classes: {item_classes}")
    
    def test_components_have_required_fields(self, auth_token):
        """Components should have all required fields from CStone"""
        response = requests.get(
            f"{BASE_URL}/api/components",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["id", "name", "type", "manufacturer", "size", "grade"]
        sample = data["data"][0]
        for field in required_fields:
            assert field in sample, f"Missing required field: {field}"
        print(f"Sample component: {sample.get('name')}, type={sample.get('type')}, grade={sample.get('grade')}")


class TestCStoneShipWeapons:
    """Test /api/weapons endpoint - Ship weapons from CStone"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "cstonetest29",
            "password": "test123"
        })
        if response.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "username": "cstonetest29",
                "password": "test123"
            })
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "cstonetest29",
                "password": "test123"
            })
        return response.json().get("access_token")
    
    def test_weapons_returns_cstone_data(self, auth_token):
        """GET /api/weapons returns ship weapons from CStone (source=cstone) with 140+ items"""
        response = requests.get(
            f"{BASE_URL}/api/weapons",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["source"] == "cstone", f"Expected source=cstone, got {data.get('source')}"
        assert len(data["data"]) >= 140, f"Expected 140+ weapons, got {len(data['data'])}"
        print(f"Ship weapons count: {len(data['data'])} (source: {data['source']})")
    
    def test_weapons_have_damage_rate_dps_fields(self, auth_token):
        """Ship weapons should have damage, fire_rate, and dps fields populated"""
        response = requests.get(
            f"{BASE_URL}/api/weapons",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check that at least some weapons have stats (handle None values)
        weapons_with_damage = [w for w in data["data"] if (w.get("damage") or 0) > 0]
        weapons_with_dps = [w for w in data["data"] if (w.get("dps") or 0) > 0]
        weapons_with_rate = [w for w in data["data"] if (w.get("fire_rate") or 0) > 0]
        
        assert len(weapons_with_damage) > 50, f"Expected 50+ weapons with damage, got {len(weapons_with_damage)}"
        assert len(weapons_with_dps) > 50, f"Expected 50+ weapons with dps, got {len(weapons_with_dps)}"
        assert len(weapons_with_rate) > 50, f"Expected 50+ weapons with fire_rate, got {len(weapons_with_rate)}"
        
        sample = data["data"][0]
        print(f"Sample weapon: {sample.get('name')}, damage={sample.get('damage')}, dps={sample.get('dps')}, rate={sample.get('fire_rate')}")


class TestCStoneMissiles:
    """Test /api/missiles endpoint - Missiles from CStone"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "cstonetest29",
            "password": "test123"
        })
        if response.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "username": "cstonetest29",
                "password": "test123"
            })
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "cstonetest29",
                "password": "test123"
            })
        return response.json().get("access_token")
    
    def test_missiles_returns_cstone_data(self, auth_token):
        """GET /api/missiles returns missiles from CStone with damage and speed data"""
        response = requests.get(
            f"{BASE_URL}/api/missiles",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["source"] == "cstone", f"Expected source=cstone, got {data.get('source')}"
        assert len(data["data"]) >= 30, f"Expected 30+ missiles, got {len(data['data'])}"
        print(f"Missiles count: {len(data['data'])} (source: {data['source']})")
    
    def test_missiles_have_damage_and_speed(self, auth_token):
        """Missiles should have damage and linear_speed fields populated"""
        response = requests.get(
            f"{BASE_URL}/api/missiles",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        missiles_with_damage = [m for m in data["data"] if m.get("damage", 0) > 0]
        missiles_with_speed = [m for m in data["data"] if m.get("linear_speed", 0) > 0]
        
        assert len(missiles_with_damage) > 20, f"Expected 20+ missiles with damage, got {len(missiles_with_damage)}"
        assert len(missiles_with_speed) > 20, f"Expected 20+ missiles with speed, got {len(missiles_with_speed)}"
        
        sample = data["data"][0]
        print(f"Sample missile: {sample.get('name')}, damage={sample.get('damage')}, speed={sample.get('linear_speed')}")


class TestItemLocations:
    """Test /api/item-locations/{item_id} endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "cstonetest29",
            "password": "test123"
        })
        if response.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "username": "cstonetest29",
                "password": "test123"
            })
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "cstonetest29",
                "password": "test123"
            })
        return response.json().get("access_token")
    
    def test_item_locations_endpoint_works(self, auth_token):
        """GET /api/item-locations/{item_id} returns purchase locations from CStone"""
        # First get a component ID
        response = requests.get(
            f"{BASE_URL}/api/components",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        components = response.json()["data"]
        
        # Find a component that's sold (has locations)
        sold_component = next((c for c in components if c.get("sold")), components[0])
        item_id = sold_component["id"]
        
        # Test the item locations endpoint
        response = requests.get(
            f"{BASE_URL}/api/item-locations/{item_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        print(f"Item locations for {sold_component.get('name')}: {len(data.get('data', []))} locations found")


class TestGearEndpoints:
    """Test /api/gear/* endpoints - FPS Weapons, Armor, Equipment"""
    
    def test_gear_weapons_returns_fps_weapons(self):
        """GET /api/gear/weapons returns FPS weapons with CStone stats merged"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["data"]) >= 20, f"Expected 20+ FPS weapons, got {len(data['data'])}"
        
        # Check CStone stats are merged (damage, ammo)
        weapons_with_damage = [w for w in data["data"] if w.get("damage", 0) > 0]
        weapons_with_ammo = [w for w in data["data"] if w.get("ammo", 0) > 0]
        
        assert len(weapons_with_damage) > 10, f"Expected 10+ weapons with damage, got {len(weapons_with_damage)}"
        assert len(weapons_with_ammo) > 10, f"Expected 10+ weapons with ammo, got {len(weapons_with_ammo)}"
        
        sample = data["data"][0]
        print(f"FPS weapons count: {len(data['data'])}, sample: {sample.get('name')}, damage={sample.get('damage')}, ammo={sample.get('ammo')}")
    
    def test_gear_armor_returns_armor_sets(self):
        """GET /api/gear/armor returns armor sets"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["data"]) >= 20, f"Expected 20+ armor sets, got {len(data['data'])}"
        
        sample = data["data"][0]
        print(f"Armor sets count: {len(data['data'])}, sample: {sample.get('name')}")
    
    def test_gear_equipment_returns_equipment(self):
        """GET /api/gear/equipment returns equipment"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["data"]) >= 10, f"Expected 10+ equipment items, got {len(data['data'])}"
        
        sample = data["data"][0]
        print(f"Equipment count: {len(data['data'])}, sample: {sample.get('name')}")


class TestComponentDataQuality:
    """Test data quality of CStone components"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "cstonetest29",
            "password": "test123"
        })
        if response.status_code != 200:
            requests.post(f"{BASE_URL}/api/auth/register", json={
                "username": "cstonetest29",
                "password": "test123"
            })
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "cstonetest29",
                "password": "test123"
            })
        return response.json().get("access_token")
    
    def test_component_types_present(self, auth_token):
        """Verify all component types are present (Cooler, Power, Quantum, Shield)"""
        response = requests.get(
            f"{BASE_URL}/api/components",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        types = set(c.get("type") for c in data["data"])
        expected_types = {"Cooler", "Power", "Quantum", "Shield"}
        
        for expected in expected_types:
            assert expected in types, f"Missing component type: {expected}"
        print(f"Component types found: {types}")
    
    def test_shield_components_have_output(self, auth_token):
        """Shield components should have output (max shield HP) field"""
        response = requests.get(
            f"{BASE_URL}/api/components",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        shields = [c for c in data["data"] if c.get("type") == "Shield"]
        shields_with_output = [s for s in shields if s.get("output", 0) > 0]
        
        assert len(shields) >= 30, f"Expected 30+ shields, got {len(shields)}"
        assert len(shields_with_output) >= 20, f"Expected 20+ shields with output, got {len(shields_with_output)}"
        
        sample = shields[0]
        print(f"Shields count: {len(shields)}, sample: {sample.get('name')}, output={sample.get('output')}")
    
    def test_power_plants_have_output(self, auth_token):
        """Power plant components should have output (power gen) field"""
        response = requests.get(
            f"{BASE_URL}/api/components",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        power = [c for c in data["data"] if c.get("type") == "Power"]
        power_with_output = [p for p in power if p.get("output", 0) > 0]
        
        assert len(power) >= 30, f"Expected 30+ power plants, got {len(power)}"
        assert len(power_with_output) >= 20, f"Expected 20+ power plants with output, got {len(power_with_output)}"
        
        sample = power[0]
        print(f"Power plants count: {len(power)}, sample: {sample.get('name')}, output={sample.get('output')}")
    
    def test_quantum_drives_have_speed(self, auth_token):
        """Quantum drive components should have speed field"""
        response = requests.get(
            f"{BASE_URL}/api/components",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        quantum = [c for c in data["data"] if c.get("type") == "Quantum"]
        quantum_with_speed = [q for q in quantum if q.get("speed", 0) > 0]
        
        assert len(quantum) >= 30, f"Expected 30+ quantum drives, got {len(quantum)}"
        assert len(quantum_with_speed) >= 20, f"Expected 20+ quantum drives with speed, got {len(quantum_with_speed)}"
        
        sample = quantum[0]
        print(f"Quantum drives count: {len(quantum)}, sample: {sample.get('name')}, speed={sample.get('speed')}")
    
    def test_coolers_have_rate(self, auth_token):
        """Cooler components should have rate (cooling rate) field"""
        response = requests.get(
            f"{BASE_URL}/api/components",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        coolers = [c for c in data["data"] if c.get("type") == "Cooler"]
        coolers_with_rate = [c for c in coolers if c.get("rate", 0) > 0]
        
        assert len(coolers) >= 30, f"Expected 30+ coolers, got {len(coolers)}"
        assert len(coolers_with_rate) >= 20, f"Expected 20+ coolers with rate, got {len(coolers_with_rate)}"
        
        sample = coolers[0]
        print(f"Coolers count: {len(coolers)}, sample: {sample.get('name')}, rate={sample.get('rate')}")
