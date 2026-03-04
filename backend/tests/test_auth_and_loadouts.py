"""
Star Citizen Fleet Manager API Tests - Updated Auth + Loadouts + Purchase Data
Tests: Username/Password Authentication, Ships/Vehicles with purchase data, Loadout CRUD
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fleet-companion.preview.emergentagent.com')

# New test credentials (username + password)
TEST_USERNAME = "testpilot"
TEST_PASSWORD = "password123"


class TestUsernamePasswordAuth:
    """Authentication endpoint tests - NEW username/password system"""
    
    def test_login_success_username_password(self):
        """Test successful login with username + password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["username"] == TEST_USERNAME
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": "wrongpassword"
        })
        assert response.status_code == 401  # Invalid password
    
    def test_login_auto_register_new_user(self):
        """Test auto-registration for new users on login"""
        new_username = f"newuser_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": new_username,
            "password": "newpassword123"
        })
        assert response.status_code == 200, f"Auto-register failed: {response.text}"
        data = response.json()
        assert data["user"]["username"] == new_username
    
    def test_register_endpoint(self):
        """Test explicit register endpoint"""
        new_username = f"reguser_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": new_username,
            "password": "password123"
        })
        assert response.status_code == 200, f"Register failed: {response.text}"
        data = response.json()
        assert data["user"]["username"] == new_username
    
    def test_register_duplicate_username(self):
        """Test register with duplicate username fails"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": TEST_USERNAME,  # Already exists
            "password": "anypassword"
        })
        assert response.status_code == 400  # Username already taken
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": TEST_USERNAME
        })
        assert response.status_code == 422  # Validation error


@pytest.fixture
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed")


@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestShipsWithPurchaseData:
    """Ships endpoint tests - verify purchase data (aUEC, dealers, USD, pledge URL)"""
    
    def test_get_ships_with_auth(self, auth_headers):
        """Test get all ships with authentication"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) > 0
    
    def test_avenger_titan_purchase_info(self, auth_headers):
        """Test Avenger Titan has in-game purchase data"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        avenger = next((s for s in ships if s["name"] == "Avenger Titan"), None)
        assert avenger is not None, "Avenger Titan not found in ships list"
        
        # Verify aUEC price
        assert "price_auec" in avenger, "Avenger Titan missing price_auec"
        assert avenger["price_auec"] > 0, "Avenger Titan should have positive aUEC price"
        assert avenger["price_auec"] == 1358280, f"Expected 1358280 aUEC, got {avenger['price_auec']}"
        
        # Verify dealers list
        assert "purchase_locations" in avenger, "Avenger Titan missing purchase_locations"
        assert isinstance(avenger["purchase_locations"], list)
        assert len(avenger["purchase_locations"]) >= 1, "Avenger Titan should have at least 1 dealer"
        assert "New Deal (Lorville)" in avenger["purchase_locations"]
    
    def test_ships_have_rsi_pledge_info(self, auth_headers):
        """Test ships have RSI pledge store info (msrp and pledge_url)"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        # Find a ship with known pledge info (Avenger Titan has msrp=60)
        avenger = next((s for s in ships if s["name"] == "Avenger Titan"), None)
        assert avenger is not None
        
        # Check msrp (USD price)
        assert "price_usd" in avenger or "msrp" in avenger, "Ship missing USD price field"
        usd_price = avenger.get("price_usd") or avenger.get("msrp")
        assert usd_price > 0, "Avenger Titan should have USD price > 0"
        
        # Check pledge URL
        assert "pledge_url" in avenger, "Ship missing pledge_url field"
        assert avenger["pledge_url"], "Avenger Titan should have pledge_url"
        assert "robertsspaceindustries.com" in avenger["pledge_url"]
    
    def test_multiple_dealers_for_arrow(self, auth_headers):
        """Test Arrow is sold at multiple dealers"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        arrow = next((s for s in ships if s["name"] == "Arrow"), None)
        assert arrow is not None, "Arrow not found"
        
        assert len(arrow["purchase_locations"]) >= 2, f"Arrow should have 2+ dealers, got {arrow['purchase_locations']}"
        assert "Astro Armada (Area18)" in arrow["purchase_locations"]


class TestVehiclesWithPurchaseData:
    """Vehicles endpoint tests - verify purchase data on ground vehicles"""
    
    def test_get_vehicles_with_auth(self, auth_headers):
        """Test get all vehicles with authentication"""
        response = requests.get(f"{BASE_URL}/api/vehicles", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) > 0
    
    def test_vehicles_have_purchase_data(self, auth_headers):
        """Test vehicles have price_auec and purchase_locations"""
        response = requests.get(f"{BASE_URL}/api/vehicles", headers=auth_headers)
        assert response.status_code == 200
        vehicles = response.json()["data"]
        
        # Find vehicles with purchase data
        vehicles_with_price = [v for v in vehicles if v.get("price_auec", 0) > 0]
        assert len(vehicles_with_price) >= 1, "Should have at least 1 vehicle with aUEC price"
        
        # Check structure
        vehicle = vehicles_with_price[0]
        assert "purchase_locations" in vehicle
        assert isinstance(vehicle["purchase_locations"], list)


class TestLoadoutCRUD:
    """Loadout save/load/delete endpoint tests - NEW FEATURE"""
    
    def test_save_loadout(self, auth_headers):
        """Test saving a custom loadout"""
        loadout_data = {
            "ship_id": "test-ship-crud",
            "ship_name": "Test Ship CRUD",
            "loadout_name": f"Test Loadout {uuid.uuid4().hex[:8]}",
            "slots": {
                "weapon_0": {"name": "Test Laser", "id": "laser-1"},
                "shield_0": {"name": "Test Shield", "id": "shield-1"}
            }
        }
        response = requests.post(f"{BASE_URL}/api/loadouts/save", json=loadout_data, headers=auth_headers)
        assert response.status_code == 200, f"Save failed: {response.text}"
        data = response.json()
        assert data["success"] == True
        assert "id" in data
    
    def test_get_loadouts_for_ship(self, auth_headers):
        """Test getting saved loadouts for a ship"""
        # First save a loadout
        ship_id = f"test-get-{uuid.uuid4().hex[:8]}"
        loadout_data = {
            "ship_id": ship_id,
            "ship_name": "Test Ship Get",
            "loadout_name": "Get Test Loadout",
            "slots": {"weapon_0": {"name": "Weapon", "id": "w1"}}
        }
        save_response = requests.post(f"{BASE_URL}/api/loadouts/save", json=loadout_data, headers=auth_headers)
        assert save_response.status_code == 200
        
        # Now get loadouts
        response = requests.get(f"{BASE_URL}/api/loadouts/{ship_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        assert len(data["data"]) >= 1
        
        # Verify loadout structure
        loadout = data["data"][0]
        assert loadout["loadout_name"] == "Get Test Loadout"
        assert loadout["ship_id"] == ship_id
        assert "slots" in loadout
    
    def test_delete_loadout(self, auth_headers):
        """Test deleting a saved loadout"""
        # First save a loadout
        ship_id = f"test-delete-{uuid.uuid4().hex[:8]}"
        loadout_data = {
            "ship_id": ship_id,
            "ship_name": "Test Ship Delete",
            "loadout_name": "Delete Test Loadout",
            "slots": {}
        }
        save_response = requests.post(f"{BASE_URL}/api/loadouts/save", json=loadout_data, headers=auth_headers)
        assert save_response.status_code == 200
        loadout_id = save_response.json()["id"]
        
        # Now delete it
        delete_response = requests.delete(f"{BASE_URL}/api/loadouts/{loadout_id}", headers=auth_headers)
        assert delete_response.status_code == 200
        assert delete_response.json()["success"] == True
        
        # Verify it's gone
        get_response = requests.get(f"{BASE_URL}/api/loadouts/{ship_id}", headers=auth_headers)
        loadouts = get_response.json()["data"]
        assert not any(l["id"] == loadout_id for l in loadouts), "Loadout should be deleted"
    
    def test_loadout_upsert_same_name(self, auth_headers):
        """Test saving loadout with same name updates existing"""
        ship_id = "test-upsert-ship"
        loadout_name = "Upsert Test"
        
        # Save first version
        loadout1 = {
            "ship_id": ship_id,
            "ship_name": "Upsert Ship",
            "loadout_name": loadout_name,
            "slots": {"weapon_0": {"name": "Original Weapon"}}
        }
        requests.post(f"{BASE_URL}/api/loadouts/save", json=loadout1, headers=auth_headers)
        
        # Save updated version with same name
        loadout2 = {
            "ship_id": ship_id,
            "ship_name": "Upsert Ship",
            "loadout_name": loadout_name,
            "slots": {"weapon_0": {"name": "Updated Weapon"}}
        }
        requests.post(f"{BASE_URL}/api/loadouts/save", json=loadout2, headers=auth_headers)
        
        # Verify only one loadout with that name exists
        response = requests.get(f"{BASE_URL}/api/loadouts/{ship_id}", headers=auth_headers)
        loadouts = response.json()["data"]
        matching = [l for l in loadouts if l["loadout_name"] == loadout_name]
        assert len(matching) == 1, f"Should have 1 loadout, got {len(matching)}"
        assert matching[0]["slots"]["weapon_0"]["name"] == "Updated Weapon"


class TestFleetPersistence:
    """Fleet persistence tests - verify ships stay after adding"""
    
    def test_add_ship_to_fleet_persists(self, auth_headers):
        """Test adding a ship to fleet and verifying persistence"""
        ship_data = {
            "id": f"persist-test-{uuid.uuid4().hex[:8]}",
            "name": "Persist Test Ship",
            "manufacturer": "Test Corp"
        }
        
        # Add ship
        add_response = requests.post(f"{BASE_URL}/api/fleet/add", json=ship_data, headers=auth_headers)
        assert add_response.status_code == 200
        
        # Verify it persists (fetch fleet)
        fleet_response = requests.get(f"{BASE_URL}/api/fleet/my", headers=auth_headers)
        assert fleet_response.status_code == 200
        fleet = fleet_response.json()["data"]
        
        found = [s for s in fleet if s["ship_name"] == "Persist Test Ship"]
        assert len(found) >= 1, "Ship should persist in fleet"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
