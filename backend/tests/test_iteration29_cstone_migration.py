"""
Test CStone Data Migration - Iteration 29
Verifies P0 Ship & Vehicle Data Migration from CStone (finder.cstone.space) as primary source.
Tests ship data with CStone fields: cstone_id, cstone_image, sold_in_game, rentable, role, purchase_details.
Tests Wiki API specs: max_speed, crew_min, crew_max, health, shield_hp, hardpoints, quantum.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fleet-forge-1.preview.emergentagent.com')


class TestAuth:
    """Authentication - Register and Login tests"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Create authenticated session for tests"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Try to register a new user
        reg_response = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": "cstone_test_pilot_29",
            "password": "password123"
        })
        
        # If user exists, login instead
        if reg_response.status_code == 400:
            login_response = session.post(f"{BASE_URL}/api/auth/login", json={
                "username": "cstone_test_pilot_29",
                "password": "password123"
            })
            assert login_response.status_code == 200, f"Login failed: {login_response.text}"
            token = login_response.json().get("access_token")
        else:
            assert reg_response.status_code == 200, f"Register failed: {reg_response.text}"
            token = reg_response.json().get("access_token")
        
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session

    def test_register_user(self):
        """Test user registration endpoint"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": "cstone_test_reg_29",
            "password": "password123"
        })
        # 200 if new user, 400 if already exists
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"

    def test_login_user(self):
        """Test user login endpoint - uses username NOT email"""
        session = requests.Session()
        # First ensure user exists
        session.post(f"{BASE_URL}/api/auth/register", json={
            "username": "cstone_test_login_29",
            "password": "password123"
        })
        # Now login
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "username": "cstone_test_login_29",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


class TestShipsEndpoint:
    """Test /api/ships endpoint with CStone data"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        reg_response = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": "cstone_ships_test_29",
            "password": "password123"
        })
        if reg_response.status_code == 400:
            login_response = session.post(f"{BASE_URL}/api/auth/login", json={
                "username": "cstone_ships_test_29",
                "password": "password123"
            })
            token = login_response.json().get("access_token")
        else:
            token = reg_response.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session

    def test_ships_endpoint_returns_cstone_live_source(self, auth_session):
        """Verify /api/ships returns data with 'cstone+live' source"""
        response = auth_session.get(f"{BASE_URL}/api/ships")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["source"] == "cstone+live", f"Expected 'cstone+live', got '{data['source']}'"
        assert len(data["data"]) > 100, f"Expected >100 ships, got {len(data['data'])}"

    def test_ships_have_cstone_fields(self, auth_session):
        """Verify ships have CStone data fields: cstone_id, cstone_image, sold_in_game, rentable, role"""
        response = auth_session.get(f"{BASE_URL}/api/ships")
        assert response.status_code == 200
        ships = response.json()["data"]
        
        # Find a ship with CStone data (Avenger Titan is commonly sold in-game)
        ship_with_cstone = None
        for ship in ships:
            if ship.get("cstone_id") and ship.get("sold_in_game"):
                ship_with_cstone = ship
                break
        
        assert ship_with_cstone is not None, "No ship found with CStone data"
        
        # Verify CStone fields
        assert "cstone_id" in ship_with_cstone, "Missing cstone_id field"
        assert "cstone_image" in ship_with_cstone, "Missing cstone_image field"
        assert "sold_in_game" in ship_with_cstone, "Missing sold_in_game field"
        assert "rentable" in ship_with_cstone, "Missing rentable field"
        assert "role" in ship_with_cstone, "Missing role field"
        
        # Validate CStone image URL format
        if ship_with_cstone["cstone_image"]:
            assert ship_with_cstone["cstone_image"].startswith("https://cstone.space/uifimages/"), \
                f"Invalid CStone image URL: {ship_with_cstone['cstone_image']}"

    def test_ships_have_purchase_details(self, auth_session):
        """Verify ships have purchase_details with per-location prices from CStone"""
        response = auth_session.get(f"{BASE_URL}/api/ships")
        assert response.status_code == 200
        ships = response.json()["data"]
        
        # Find a ship with purchase_details (not all sold_in_game ships have locations cached)
        sold_ship = None
        for ship in ships:
            purchase_details = ship.get("purchase_details")
            if purchase_details and len(purchase_details) > 0:
                sold_ship = ship
                break
        
        assert sold_ship is not None, "No ship found with purchase_details"
        assert "purchase_details" in sold_ship
        assert isinstance(sold_ship["purchase_details"], list)
        
        if len(sold_ship["purchase_details"]) > 0:
            detail = sold_ship["purchase_details"][0]
            assert "location" in detail, "purchase_details missing 'location'"
            assert "price" in detail, "purchase_details missing 'price'"
            assert isinstance(detail["price"], int), f"price should be int, got {type(detail['price'])}"

    def test_ships_have_wiki_api_specs(self, auth_session):
        """Verify ships have Wiki API specs: max_speed, crew_min, crew_max, health, shield_hp, hardpoints, quantum"""
        response = auth_session.get(f"{BASE_URL}/api/ships")
        assert response.status_code == 200
        ships = response.json()["data"]
        
        # Check first ship has spec fields
        ship = ships[0]
        
        # Wiki API spec fields
        assert "max_speed" in ship, "Missing max_speed field"
        assert "crew_min" in ship, "Missing crew_min field"
        assert "crew_max" in ship, "Missing crew_max field"
        assert "health" in ship, "Missing health field"
        assert "shield_hp" in ship, "Missing shield_hp field"
        assert "hardpoints" in ship, "Missing hardpoints field"
        assert "quantum" in ship, "Missing quantum field"
        
        # Validate hardpoints structure
        hardpoints = ship["hardpoints"]
        assert "weapons" in hardpoints or "shield" in hardpoints, "hardpoints missing weapon or shield data"

    def test_avenger_titan_cstone_data(self, auth_session):
        """Verify Avenger Titan (commonly sold) has correct CStone data"""
        response = auth_session.get(f"{BASE_URL}/api/ships")
        assert response.status_code == 200
        ships = response.json()["data"]
        
        titan = next((s for s in ships if s["name"] == "Avenger Titan"), None)
        assert titan is not None, "Avenger Titan not found"
        
        # Should be sold in-game and have CStone data
        assert titan.get("sold_in_game") == True, "Avenger Titan should be sold_in_game"
        assert titan.get("cstone_id"), "Avenger Titan missing cstone_id"
        assert titan.get("price_auec", 0) > 0, "Avenger Titan should have a price_auec"
        assert len(titan.get("purchase_locations", [])) > 0, "Avenger Titan should have purchase_locations"


class TestVehiclesEndpoint:
    """Test /api/vehicles endpoint with CStone data"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        reg_response = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": "cstone_vehicles_test_29",
            "password": "password123"
        })
        if reg_response.status_code == 400:
            login_response = session.post(f"{BASE_URL}/api/auth/login", json={
                "username": "cstone_vehicles_test_29",
                "password": "password123"
            })
            token = login_response.json().get("access_token")
        else:
            token = reg_response.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session

    def test_vehicles_endpoint_returns_cstone_live(self, auth_session):
        """Verify /api/vehicles returns ground vehicles with CStone data"""
        response = auth_session.get(f"{BASE_URL}/api/vehicles")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["source"] == "cstone+live", f"Expected 'cstone+live', got '{data['source']}'"
        assert len(data["data"]) > 0, "Expected at least 1 ground vehicle"

    def test_vehicles_have_cstone_fields(self, auth_session):
        """Verify vehicles have CStone data fields"""
        response = auth_session.get(f"{BASE_URL}/api/vehicles")
        assert response.status_code == 200
        vehicles = response.json()["data"]
        
        # Check if any vehicle has CStone data
        vehicle_with_cstone = None
        for v in vehicles:
            if v.get("cstone_id"):
                vehicle_with_cstone = v
                break
        
        if vehicle_with_cstone:
            assert "cstone_id" in vehicle_with_cstone
            assert "sold_in_game" in vehicle_with_cstone or "rentable" in vehicle_with_cstone


class TestItemLocations:
    """Test /api/item-locations/{item_id} endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        reg_response = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": "cstone_itemloc_test_29",
            "password": "password123"
        })
        if reg_response.status_code == 400:
            login_response = session.post(f"{BASE_URL}/api/auth/login", json={
                "username": "cstone_itemloc_test_29",
                "password": "password123"
            })
            token = login_response.json().get("access_token")
        else:
            token = reg_response.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session

    def test_item_locations_endpoint(self, auth_session):
        """Verify /api/item-locations/{item_id} returns CStone purchase locations"""
        # First get a valid cstone_id from ships
        ships_response = auth_session.get(f"{BASE_URL}/api/ships")
        assert ships_response.status_code == 200
        ships = ships_response.json()["data"]
        
        # Find a ship with cstone_id and sold_in_game
        ship_with_id = None
        for ship in ships:
            if ship.get("cstone_id") and ship.get("sold_in_game"):
                ship_with_id = ship
                break
        
        if ship_with_id:
            item_id = ship_with_id["cstone_id"]
            response = auth_session.get(f"{BASE_URL}/api/item-locations/{item_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert isinstance(data["data"], list)
            
            # If locations exist, verify structure
            if len(data["data"]) > 0:
                loc = data["data"][0]
                assert "location" in loc
                assert "price" in loc


class TestComponentsEndpoint:
    """Test /api/components endpoint still works with CStone data"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        reg_response = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": "cstone_comps_test_29",
            "password": "password123"
        })
        if reg_response.status_code == 400:
            login_response = session.post(f"{BASE_URL}/api/auth/login", json={
                "username": "cstone_comps_test_29",
                "password": "password123"
            })
            token = login_response.json().get("access_token")
        else:
            token = reg_response.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session

    def test_components_endpoint_cstone_source(self, auth_session):
        """Verify /api/components returns CStone data"""
        response = auth_session.get(f"{BASE_URL}/api/components")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["source"] == "cstone", f"Expected 'cstone', got '{data['source']}'"
        assert len(data["data"]) > 50, f"Expected >50 components, got {len(data['data'])}"


class TestWeaponsEndpoint:
    """Test /api/weapons endpoint still works with CStone data"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        reg_response = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": "cstone_weapons_test_29",
            "password": "password123"
        })
        if reg_response.status_code == 400:
            login_response = session.post(f"{BASE_URL}/api/auth/login", json={
                "username": "cstone_weapons_test_29",
                "password": "password123"
            })
            token = login_response.json().get("access_token")
        else:
            token = reg_response.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session

    def test_weapons_endpoint_cstone_source(self, auth_session):
        """Verify /api/weapons returns CStone data"""
        response = auth_session.get(f"{BASE_URL}/api/weapons")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["source"] == "cstone", f"Expected 'cstone', got '{data['source']}'"
        assert len(data["data"]) > 50, f"Expected >50 weapons, got {len(data['data'])}"


class TestMissilesEndpoint:
    """Test /api/missiles endpoint still works with CStone data"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        reg_response = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": "cstone_missiles_test_29",
            "password": "password123"
        })
        if reg_response.status_code == 400:
            login_response = session.post(f"{BASE_URL}/api/auth/login", json={
                "username": "cstone_missiles_test_29",
                "password": "password123"
            })
            token = login_response.json().get("access_token")
        else:
            token = reg_response.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session

    def test_missiles_endpoint_cstone_source(self, auth_session):
        """Verify /api/missiles returns CStone data"""
        response = auth_session.get(f"{BASE_URL}/api/missiles")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["source"] == "cstone", f"Expected 'cstone', got '{data['source']}'"
        assert len(data["data"]) > 20, f"Expected >20 missiles, got {len(data['data'])}"
