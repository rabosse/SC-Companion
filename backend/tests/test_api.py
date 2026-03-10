"""
Star Citizen Fleet Manager API Tests
Tests: Authentication, Ships, Vehicles, Components, Weapons, Fleet management
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fleet-manager-394.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "test@test.com"
TEST_TOKEN = "testtoken123"


class TestAuthentication:
    """Authentication endpoint tests"""
    
    def test_login_success(self):
        """Test successful login with demo credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "star_citizen_token": TEST_TOKEN
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL
        })
        assert response.status_code == 422  # Validation error


@pytest.fixture
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "star_citizen_token": TEST_TOKEN
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed")


@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestShipsAPI:
    """Ships endpoint tests - verify LIVE API with images from wiki"""
    
    def test_get_ships_requires_auth(self):
        """Test ships endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ships")
        assert response.status_code in [401, 403]
    
    def test_get_ships_with_auth(self, auth_headers):
        """Test get all ships with authentication"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) > 0
        # Verify ship structure
        ship = data["data"][0]
        assert "id" in ship
        assert "name" in ship
        assert "manufacturer" in ship
    
    def test_ships_have_live_source(self, auth_headers):
        """Test that ships are from LIVE API (source=live)"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Verify source field is 'live'
        assert "source" in data, "Missing 'source' field in response"
        assert data["source"] == "live", f"Expected source='live', got '{data.get('source')}'"
    
    def test_ships_have_crew_min_max_format(self, auth_headers):
        """Test ships from LIVE API have crew_min and crew_max fields"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        ships = data["data"]
        
        # Check first 10 ships have crew_min and crew_max
        ships_with_crew_format = 0
        for ship in ships[:20]:
            if ship.get("crew_min") is not None and ship.get("crew_max") is not None:
                ships_with_crew_format += 1
        
        assert ships_with_crew_format >= 15, f"Expected 15+ ships with crew_min/crew_max, got {ships_with_crew_format}"
    
    def test_ships_have_live_data_fields(self, auth_headers):
        """Test ships have LIVE API specific fields: speed, shield_hp, etc"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        ships = data["data"]
        
        # Check ships have live API fields
        live_fields = ["max_speed", "shield_hp", "cargo", "length", "beam", "height"]
        ship = ships[0]
        for field in live_fields:
            assert field in ship, f"Ship missing LIVE field: {field}"
    
    def test_ships_have_wiki_images(self, auth_headers):
        """Test that ships have images from starcitizen.tools wiki"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        ships = data["data"]
        
        # Check that some ships have images
        ships_with_images = [s for s in ships if s.get("image") and s["image"].strip()]
        # With 289 ships from live API, expect at least 50 to have wiki images
        assert len(ships_with_images) >= 50, f"Expected 50+ ships to have images, got {len(ships_with_images)}/{len(ships)}"
        
        # Verify images are from starcitizen.tools
        for ship in ships_with_images[:10]:  # Check first 10
            if ship.get("image"):
                assert "starcitizen.tools" in ship["image"], f"Ship {ship['name']} image not from wiki: {ship['image']}"


class TestVehiclesAPI:
    """Vehicles endpoint tests - verify images"""
    
    def test_get_vehicles_requires_auth(self):
        """Test vehicles endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/vehicles")
        assert response.status_code in [401, 403]
    
    def test_get_vehicles_with_auth(self, auth_headers):
        """Test get all vehicles with authentication"""
        response = requests.get(f"{BASE_URL}/api/vehicles", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) > 0
        # Verify vehicle structure (live API may not have 'type' field)
        vehicle = data["data"][0]
        assert "id" in vehicle
        assert "name" in vehicle
        assert "manufacturer" in vehicle
        # LIVE API has is_ground_vehicle flag instead of 'type' string
        assert vehicle.get("is_ground_vehicle") == True or "is_ground_vehicle" in vehicle
    
    def test_vehicles_have_wiki_images(self, auth_headers):
        """Test that vehicles have images from starcitizen.tools wiki"""
        response = requests.get(f"{BASE_URL}/api/vehicles", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        vehicles = data["data"]
        
        # Check vehicles have images
        vehicles_with_images = [v for v in vehicles if v.get("image") and v["image"].strip()]
        assert len(vehicles_with_images) > 0, "No vehicles have images"
        
        # Verify images are from starcitizen.tools
        for vehicle in vehicles_with_images:
            assert "starcitizen.tools" in vehicle["image"], f"Vehicle {vehicle['name']} image not from wiki"


class TestComponentsAPI:
    """Components endpoint tests - verify LIVE API, size filter, location, price"""
    
    def test_get_components_requires_auth(self):
        """Test components endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/components")
        assert response.status_code in [401, 403]
    
    def test_get_components_with_auth(self, auth_headers):
        """Test get all components with authentication"""
        response = requests.get(f"{BASE_URL}/api/components", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) > 0
    
    def test_components_have_live_source(self, auth_headers):
        """Test components are from LIVE API (source=live)"""
        response = requests.get(f"{BASE_URL}/api/components", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "source" in data, "Missing 'source' field in response"
        assert data["source"] == "live", f"Expected source='live', got '{data.get('source')}'"
    
    def test_components_have_multiple_types(self, auth_headers):
        """Test components have multiple types: Shield, Power, Cooler, Quantum, Radar"""
        response = requests.get(f"{BASE_URL}/api/components", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        components = data["data"]
        
        types = set(c.get("type") for c in components if c.get("type"))
        expected_types = {"Shield", "Power", "Cooler", "Quantum", "Radar"}
        for t in expected_types:
            assert t in types, f"Missing component type: {t}. Found: {types}"
    
    def test_components_have_size_field(self, auth_headers):
        """Test all components have size field for filtering"""
        response = requests.get(f"{BASE_URL}/api/components", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        components = data["data"]
        
        for component in components:
            assert "size" in component, f"Component {component.get('name')} missing size field"
            assert component["size"] is not None, f"Component {component.get('name')} has null size"
    
    def test_components_have_location(self, auth_headers):
        """Test all components have location field"""
        response = requests.get(f"{BASE_URL}/api/components", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        components = data["data"]
        
        components_with_location = [c for c in components if c.get("location")]
        assert len(components_with_location) == len(components), \
            f"Expected all components to have location, got {len(components_with_location)}/{len(components)}"
    
    def test_components_have_price(self, auth_headers):
        """Test all components have cost_auec field"""
        response = requests.get(f"{BASE_URL}/api/components", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        components = data["data"]
        
        components_with_price = [c for c in components if c.get("cost_auec") is not None]
        assert len(components_with_price) == len(components), \
            f"Expected all components to have cost_auec, got {len(components_with_price)}/{len(components)}"
    
    def test_components_multiple_sizes(self, auth_headers):
        """Test components have multiple sizes for filtering"""
        response = requests.get(f"{BASE_URL}/api/components", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        components = data["data"]
        
        sizes = set(c["size"] for c in components if c.get("size"))
        assert len(sizes) >= 2, f"Expected multiple sizes for filtering, got {sizes}"


class TestWeaponsAPI:
    """Weapons endpoint tests - verify LIVE API, size filter, location, price"""
    
    def test_get_weapons_requires_auth(self):
        """Test weapons endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/weapons")
        assert response.status_code in [401, 403]
    
    def test_get_weapons_with_auth(self, auth_headers):
        """Test get all weapons with authentication"""
        response = requests.get(f"{BASE_URL}/api/weapons", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) > 0
    
    def test_weapons_have_live_source(self, auth_headers):
        """Test weapons are from LIVE API (source=live)"""
        response = requests.get(f"{BASE_URL}/api/weapons", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "source" in data, "Missing 'source' field in response"
        assert data["source"] == "live", f"Expected source='live', got '{data.get('source')}'"
    
    def test_weapons_have_size_field(self, auth_headers):
        """Test all weapons have size field for filtering"""
        response = requests.get(f"{BASE_URL}/api/weapons", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        weapons = data["data"]
        
        for weapon in weapons:
            assert "size" in weapon, f"Weapon {weapon.get('name')} missing size field"
            assert weapon["size"] is not None, f"Weapon {weapon.get('name')} has null size"
    
    def test_weapons_have_location(self, auth_headers):
        """Test all weapons have location field"""
        response = requests.get(f"{BASE_URL}/api/weapons", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        weapons = data["data"]
        
        weapons_with_location = [w for w in weapons if w.get("location")]
        assert len(weapons_with_location) == len(weapons), \
            f"Expected all weapons to have location, got {len(weapons_with_location)}/{len(weapons)}"
    
    def test_weapons_have_price(self, auth_headers):
        """Test all weapons have cost_auec field"""
        response = requests.get(f"{BASE_URL}/api/weapons", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        weapons = data["data"]
        
        weapons_with_price = [w for w in weapons if w.get("cost_auec") is not None]
        assert len(weapons_with_price) == len(weapons), \
            f"Expected all weapons to have cost_auec, got {len(weapons_with_price)}/{len(weapons)}"
    
    def test_weapons_multiple_sizes(self, auth_headers):
        """Test weapons have multiple sizes for filtering"""
        response = requests.get(f"{BASE_URL}/api/weapons", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        weapons = data["data"]
        
        sizes = set(w["size"] for w in weapons if w.get("size"))
        assert len(sizes) >= 2, f"Expected multiple sizes for filtering, got {sizes}"
    
    def test_weapons_have_type_field(self, auth_headers):
        """Test all weapons have type field for filtering"""
        response = requests.get(f"{BASE_URL}/api/weapons", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        weapons = data["data"]
        
        types = set(w["type"] for w in weapons if w.get("type"))
        assert len(types) >= 2, f"Expected multiple weapon types, got {types}"


class TestFleetAPI:
    """Fleet management tests"""
    
    def test_get_fleet_requires_auth(self):
        """Test fleet endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/fleet/my")
        assert response.status_code in [401, 403]
    
    def test_get_empty_fleet(self, auth_headers):
        """Test getting fleet (may be empty or have items)"""
        response = requests.get(f"{BASE_URL}/api/fleet/my", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_add_ship_to_fleet(self, auth_headers):
        """Test adding a ship to fleet"""
        ship_data = {
            "id": "test-ship-pytest",
            "name": "TEST Pytest Ship",
            "manufacturer": "Test Manufacturer"
        }
        response = requests.post(f"{BASE_URL}/api/fleet/add", 
                                 json=ship_data, 
                                 headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "message" in data
    
    def test_add_and_verify_fleet(self, auth_headers):
        """Test add ship then verify it appears in fleet"""
        # Add ship
        ship_data = {
            "id": "test-verify-ship",
            "name": "TEST Verify Ship",
            "manufacturer": "Test Manufacturer"
        }
        add_response = requests.post(f"{BASE_URL}/api/fleet/add",
                                     json=ship_data,
                                     headers=auth_headers)
        assert add_response.status_code == 200
        
        # Get fleet and verify
        fleet_response = requests.get(f"{BASE_URL}/api/fleet/my", headers=auth_headers)
        assert fleet_response.status_code == 200
        fleet = fleet_response.json()["data"]
        
        # Find the ship we just added
        added_ships = [s for s in fleet if s.get("ship_name") == "TEST Verify Ship"]
        assert len(added_ships) >= 1, "Added ship not found in fleet"
    
    def test_remove_from_fleet(self, auth_headers):
        """Test removing a ship from fleet"""
        # First add a ship
        ship_data = {
            "id": "test-remove-ship",
            "name": "TEST Remove Ship",
            "manufacturer": "Test Manufacturer"
        }
        add_response = requests.post(f"{BASE_URL}/api/fleet/add",
                                     json=ship_data,
                                     headers=auth_headers)
        assert add_response.status_code == 200
        
        # Get fleet to find the ID
        fleet_response = requests.get(f"{BASE_URL}/api/fleet/my", headers=auth_headers)
        fleet = fleet_response.json()["data"]
        
        # Find the ship we added
        ships_to_remove = [s for s in fleet if s.get("ship_name") == "TEST Remove Ship"]
        if ships_to_remove:
            fleet_id = ships_to_remove[0]["id"]
            
            # Remove it
            delete_response = requests.delete(f"{BASE_URL}/api/fleet/{fleet_id}",
                                              headers=auth_headers)
            assert delete_response.status_code == 200


class TestUpgradesAPI:
    """Ship upgrades endpoint tests"""
    
    def test_get_upgrades_for_ship(self, auth_headers):
        """Test getting upgrade recommendations for a ship"""
        response = requests.get(f"{BASE_URL}/api/upgrades/arrow", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        upgrades = data["data"]
        
        # Verify upgrade categories exist
        expected_categories = ["shields", "power", "weapons", "quantum"]
        for category in expected_categories:
            assert category in upgrades, f"Missing upgrade category: {category}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
