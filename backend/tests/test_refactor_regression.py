"""
Comprehensive regression test for Star Citizen Fleet Manager API after refactoring.
Tests all endpoints from the refactored router modules:
- auth.py: /api/auth/register, /api/auth/login
- ships.py: /api/ships, /api/vehicles, /api/components, /api/weapons, /api/upgrades
- fleet.py: /api/fleet/add, /api/fleet/my, /api/fleet/{id}, /api/fleet/bulk-add
- loadouts.py: /api/loadouts/*, /api/community/loadouts/*
- starmap.py: /api/routes/locations, /api/routes/calculate, /api/routes/interdiction, /api/routes/chase
- gear.py: /api/gear/weapons, /api/gear/armor
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHealthEndpoint:
    """Health check endpoint - server.py"""
    
    def test_health_returns_ok(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestAuthRoutes:
    """Authentication endpoints - routes/auth.py"""
    
    def test_login_existing_user(self):
        """Login with existing test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "geartest",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "geartest"
    
    def test_register_new_user(self):
        """Register a new user"""
        unique_username = f"TEST_refactor_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": unique_username,
            "password": "testpass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == unique_username
    
    def test_register_duplicate_username_fails(self):
        """Cannot register with existing username"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": "geartest",
            "password": "anything"
        })
        assert response.status_code == 400
        assert "already taken" in response.json().get("detail", "").lower()
    
    def test_login_wrong_password_fails(self):
        """Login with wrong password fails"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "geartest",
            "password": "wrongpassword"
        })
        assert response.status_code == 401


class TestShipsRoutes:
    """Ship data endpoints - routes/ships.py (require auth)"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "geartest",
            "password": "password123"
        })
        return response.json()["access_token"]
    
    def test_get_ships_returns_data(self, auth_token):
        """GET /api/ships returns ship data"""
        response = requests.get(f"{BASE_URL}/api/ships",
                                headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert len(data["data"]) > 0
        # Check first ship has required fields
        ship = data["data"][0]
        assert "name" in ship
        assert "manufacturer" in ship
    
    def test_get_vehicles_returns_data(self, auth_token):
        """GET /api/vehicles returns vehicle data"""
        response = requests.get(f"{BASE_URL}/api/vehicles",
                                headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_get_components_returns_data(self, auth_token):
        """GET /api/components returns component data"""
        response = requests.get(f"{BASE_URL}/api/components",
                                headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert len(data["data"]) > 0
    
    def test_get_weapons_returns_data(self, auth_token):
        """GET /api/weapons returns ship weapon data"""
        response = requests.get(f"{BASE_URL}/api/weapons",
                                headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert len(data["data"]) > 0
    
    def test_ships_without_auth_fails(self):
        """Ship endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/ships")
        assert response.status_code in [401, 403]


class TestFleetRoutes:
    """Fleet management endpoints - routes/fleet.py (require auth)"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "geartest",
            "password": "password123"
        })
        return response.json()["access_token"]
    
    def test_get_my_fleet(self, auth_token):
        """GET /api/fleet/my returns user's fleet"""
        response = requests.get(f"{BASE_URL}/api/fleet/my",
                                headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_add_ship_to_fleet(self, auth_token):
        """POST /api/fleet/add adds a ship to fleet"""
        ship_data = {
            "id": f"test-ship-{uuid.uuid4().hex[:8]}",
            "name": "Test Aurora MR",
            "manufacturer": "RSI"
        }
        response = requests.post(f"{BASE_URL}/api/fleet/add",
                                 headers={"Authorization": f"Bearer {auth_token}"},
                                 json=ship_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "added" in data["message"].lower()
    
    def test_bulk_add_to_fleet(self, auth_token):
        """POST /api/fleet/bulk-add adds multiple ships"""
        ships = [
            {"id": f"bulk-test-{uuid.uuid4().hex[:8]}", "name": "Bulk Ship 1", "manufacturer": "Aegis"},
            {"id": f"bulk-test-{uuid.uuid4().hex[:8]}", "name": "Bulk Ship 2", "manufacturer": "Drake"}
        ]
        response = requests.post(f"{BASE_URL}/api/fleet/bulk-add",
                                 headers={"Authorization": f"Bearer {auth_token}"},
                                 json={"ships": ships})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "added" in data
    
    def test_delete_from_fleet_nonexistent(self, auth_token):
        """DELETE /api/fleet/{id} returns 404 for nonexistent ship"""
        response = requests.delete(f"{BASE_URL}/api/fleet/nonexistent-id-12345",
                                   headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 404


class TestLoadoutsRoutes:
    """Loadout endpoints - routes/loadouts.py"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "geartest",
            "password": "password123"
        })
        return response.json()["access_token"]
    
    def test_get_my_loadouts(self, auth_token):
        """GET /api/loadouts/my/all returns user's loadouts"""
        response = requests.get(f"{BASE_URL}/api/loadouts/my/all",
                                headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_save_loadout(self, auth_token):
        """POST /api/loadouts/save creates a new loadout"""
        loadout_data = {
            "ship_id": "arrow",
            "ship_name": "Arrow",
            "loadout_name": f"TEST_Refactor_Loadout_{uuid.uuid4().hex[:6]}",
            "slots": {
                "weapon_0": {"name": "Test Weapon", "type": "Energy"}
            }
        }
        response = requests.post(f"{BASE_URL}/api/loadouts/save",
                                 headers={"Authorization": f"Bearer {auth_token}"},
                                 json=loadout_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "share_code" in data
    
    def test_community_loadouts_public(self):
        """GET /api/community/loadouts is public (no auth)"""
        response = requests.get(f"{BASE_URL}/api/community/loadouts")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "total" in data
    
    def test_community_loadout_by_share_code_nonexistent(self):
        """GET /api/community/loadouts/{share_code} returns 404 for invalid code"""
        response = requests.get(f"{BASE_URL}/api/community/loadouts/invalid-code-xyz")
        assert response.status_code == 404


class TestStarmapRoutes:
    """Star map / route planning endpoints - routes/starmap.py (mostly public)"""
    
    def test_get_locations(self):
        """GET /api/routes/locations returns all star map locations"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert len(data["data"]) > 0
        # Check structure
        assert "systems" in data
        assert "qd_speeds" in data
        # Verify location has required fields
        loc = data["data"][0]
        assert "id" in loc
        assert "name" in loc
        assert "system" in loc
    
    def test_calculate_route_same_system(self):
        """GET /api/routes/calculate works for same-system routes"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate?origin=hurston&destination=crusader")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        route = data["data"]
        assert route["origin"]["id"] == "hurston"
        assert route["destination"]["id"] == "crusader"
        assert "total_distance_mkm" in route
        assert "travel_time_seconds" in route
        assert "waypoints" in route
    
    def test_calculate_route_cross_system(self):
        """GET /api/routes/calculate works for cross-system routes"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate?origin=hurston&destination=pyro-iii")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        route = data["data"]
        assert route["cross_system"] is True
        assert len(route["waypoints"]) > 1
    
    def test_calculate_route_invalid_location(self):
        """GET /api/routes/calculate returns 400 for invalid location"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate?origin=invalid-loc&destination=crusader")
        assert response.status_code == 400
    
    def test_interdiction_calculation(self):
        """POST /api/routes/interdiction calculates snare position"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["hurston", "arccorp"],
            "destination": "crusader",
            "snare_range_mkm": 10.0
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        result = data["data"]
        assert "snare_position" in result
        assert "coverage_pct" in result
    
    def test_chase_calculation(self):
        """POST /api/routes/chase calculates chase scenario"""
        response = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 2,
            "target_qd_size": 1,
            "distance_mkm": 10.0,
            "prep_time_seconds": 30
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        result = data["data"]
        assert "can_catch" in result
        assert "your_speed_kms" in result
        assert "target_speed_kms" in result


class TestGearRoutes:
    """Personal gear endpoints - routes/gear.py (public)"""
    
    def test_get_fps_weapons(self):
        """GET /api/gear/weapons returns FPS weapons"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        weapons = data["data"]
        assert len(weapons) == 28  # Expected 28 FPS weapons
        # Verify structure
        weapon = weapons[0]
        assert "id" in weapon
        assert "name" in weapon
        assert "type" in weapon
        assert "manufacturer" in weapon
        assert "damage" in weapon
    
    def test_get_armor_sets(self):
        """GET /api/gear/armor returns armor sets"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        armor = data["data"]
        assert len(armor) == 21  # Expected 21 armor sets
        # Verify structure
        item = armor[0]
        assert "id" in item
        assert "name" in item
        assert "type" in item
        assert "temp_max" in item
        assert "temp_min" in item


class TestAuthenticationRequired:
    """Verify auth requirement on protected endpoints"""
    
    def test_ships_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/ships")
        assert response.status_code in [401, 403]
    
    def test_vehicles_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/vehicles")
        assert response.status_code in [401, 403]
    
    def test_components_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/components")
        assert response.status_code in [401, 403]
    
    def test_weapons_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/weapons")
        assert response.status_code in [401, 403]
    
    def test_fleet_my_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/fleet/my")
        assert response.status_code in [401, 403]
    
    def test_loadouts_my_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/loadouts/my/all")
        assert response.status_code in [401, 403]


class TestPublicEndpoints:
    """Verify public endpoints work without auth"""
    
    def test_health_is_public(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
    
    def test_gear_weapons_is_public(self):
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
    
    def test_gear_armor_is_public(self):
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
    
    def test_routes_locations_is_public(self):
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        assert response.status_code == 200
    
    def test_routes_calculate_is_public(self):
        response = requests.get(f"{BASE_URL}/api/routes/calculate?origin=hurston&destination=crusader")
        assert response.status_code == 200
    
    def test_community_loadouts_is_public(self):
        response = requests.get(f"{BASE_URL}/api/community/loadouts")
        assert response.status_code == 200
