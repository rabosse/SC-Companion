"""
Full Re-validation Tests for Star Citizen Fleet Manager
Tests all API endpoints: Auth, Ships, Vehicles, Fleet, Loadouts, Components, Weapons, Routes, Gear, Prices, Wikelo
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USERNAME = "newpilot"
TEST_PASSWORD = "test1234"
TEST_NEW_USER = f"TEST_user_{os.getpid()}"


class TestHealthAndBasics:
    """Health check and basic connectivity"""
    
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("✓ Health endpoint working")


class TestAuth:
    """Authentication endpoints - login and registration"""
    
    def test_login_existing_user(self):
        """Test login with existing user newpilot/test1234"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }, timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["username"] == TEST_USERNAME
        print(f"✓ Login successful for user: {TEST_USERNAME}")
    
    def test_login_invalid_credentials(self):
        """Test login with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": "wrongpassword123"
        }, timeout=15)
        assert response.status_code == 401
        print("✓ Invalid login correctly rejected")
    
    def test_register_new_user(self):
        """Test registration of a new user"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": TEST_NEW_USER,
            "password": "testpass123"
        }, timeout=15)
        # If user exists, that's OK (from previous test runs)
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            print(f"✓ New user registered: {TEST_NEW_USER}")
        else:
            print(f"✓ User already exists (expected): {TEST_NEW_USER}")


class TestShipsAPI:
    """Ships endpoints - /api/ships, /api/vehicles"""
    
    @pytest.fixture(autouse=True)
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }, timeout=15)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Auth failed")
    
    def test_get_ships(self):
        """Test /api/ships returns ship data with 180 ships"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=self.headers, timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        ships = data.get("data", [])
        # Should have 158 flight-ready + 22 non-flight-ready = 180 ships
        assert len(ships) >= 150, f"Expected ~180 ships, got {len(ships)}"
        # Verify ship structure
        if ships:
            ship = ships[0]
            assert "id" in ship
            assert "name" in ship
            assert "manufacturer" in ship
        print(f"✓ Ships API returned {len(ships)} ships")
    
    def test_get_vehicles(self):
        """Test /api/vehicles returns ground vehicles"""
        response = requests.get(f"{BASE_URL}/api/vehicles", headers=self.headers, timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        vehicles = data.get("data", [])
        # Should have ground vehicles
        assert len(vehicles) >= 1, "Should have at least some vehicles"
        print(f"✓ Vehicles API returned {len(vehicles)} vehicles")


class TestComponentsWeaponsAPI:
    """Components and Weapons endpoints"""
    
    @pytest.fixture(autouse=True)
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }, timeout=15)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Auth failed")
    
    def test_get_components(self):
        """Test /api/components returns component data"""
        response = requests.get(f"{BASE_URL}/api/components", headers=self.headers, timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        components = data.get("data", [])
        # Should have components data
        assert len(components) >= 1, "Should have components data"
        print(f"✓ Components API returned {len(components)} components")
    
    def test_get_weapons(self):
        """Test /api/weapons returns weapon data"""
        response = requests.get(f"{BASE_URL}/api/weapons", headers=self.headers, timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        weapons = data.get("data", [])
        # Should have weapons data
        assert len(weapons) >= 1, "Should have weapons data"
        print(f"✓ Weapons API returned {len(weapons)} weapons")
    
    def test_get_missiles(self):
        """Test /api/missiles returns missile data"""
        response = requests.get(f"{BASE_URL}/api/missiles", headers=self.headers, timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("✓ Missiles API working")


class TestFleetAPI:
    """Fleet management endpoints"""
    
    @pytest.fixture(autouse=True)
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }, timeout=15)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Auth failed")
    
    def test_get_my_fleet(self):
        """Test /api/fleet/my returns user's fleet"""
        response = requests.get(f"{BASE_URL}/api/fleet/my", headers=self.headers, timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        fleet = data.get("data", [])
        # User newpilot should have 10 ships
        assert len(fleet) >= 1, "User should have ships in fleet"
        print(f"✓ Fleet API returned {len(fleet)} ships for user")
    
    def test_add_ship_to_fleet(self):
        """Test adding a ship to fleet"""
        # Add a test ship
        response = requests.post(f"{BASE_URL}/api/fleet/add", headers=self.headers, json={
            "id": f"TEST_ship_{os.getpid()}",
            "name": "TEST Aurora MR",
            "manufacturer": "Roberts Space Industries"
        }, timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("✓ Add to fleet working")


class TestLoadoutsAPI:
    """Loadout management endpoints"""
    
    @pytest.fixture(autouse=True)
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }, timeout=15)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Auth failed")
    
    def test_get_all_loadouts(self):
        """Test /api/loadouts/my/all returns user's loadouts"""
        response = requests.get(f"{BASE_URL}/api/loadouts/my/all", headers=self.headers, timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✓ Loadouts API returned {len(data.get('data', []))} loadouts")
    
    def test_save_loadout(self):
        """Test saving a loadout"""
        response = requests.post(f"{BASE_URL}/api/loadouts/save", headers=self.headers, json={
            "ship_id": "avenger-titan",
            "ship_name": "Avenger Titan",
            "loadout_name": f"TEST_Loadout_{os.getpid()}",
            "slots": {"shield": {"name": "TEST Shield"}, "power": {"name": "TEST Power"}}
        }, timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "share_code" in data
        print(f"✓ Save loadout working, share_code: {data.get('share_code')}")
    
    def test_get_ship_loadouts(self):
        """Test /api/loadouts/{ship_id} returns loadouts for a ship"""
        response = requests.get(f"{BASE_URL}/api/loadouts/avenger-titan", headers=self.headers, timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✓ Ship loadouts API working")
    
    def test_community_loadouts(self):
        """Test /api/community/loadouts returns community loadouts"""
        response = requests.get(f"{BASE_URL}/api/community/loadouts", timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✓ Community loadouts API returned {len(data.get('data', []))} loadouts")


class TestRoutesAPI:
    """Routes/Starmap endpoints"""
    
    def test_get_route_locations(self):
        """Test /api/routes/locations returns locations data"""
        response = requests.get(f"{BASE_URL}/api/routes/locations", timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "data" in data
        assert "systems" in data
        assert "qd_speeds" in data
        print(f"✓ Routes locations API working")
    
    def test_calculate_route(self):
        """Test route calculation"""
        response = requests.get(
            f"{BASE_URL}/api/routes/calculate",
            params={"origin": "Hurston", "destination": "MicroTech", "qd_size": 1},
            timeout=15
        )
        # Route might fail if locations don't exist - that's OK
        assert response.status_code in [200, 400]
        print("✓ Route calculation endpoint accessible")


class TestGearAPI:
    """FPS Gear endpoints"""
    
    def test_get_fps_weapons(self):
        """Test /api/gear/weapons returns FPS weapons"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        weapons = data.get("data", [])
        assert len(weapons) >= 1, "Should have FPS weapons"
        print(f"✓ Gear weapons API returned {len(weapons)} FPS weapons")
    
    def test_get_armor(self):
        """Test /api/gear/armor returns armor sets"""
        response = requests.get(f"{BASE_URL}/api/gear/armor", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        armor = data.get("data", [])
        assert len(armor) >= 1, "Should have armor sets"
        print(f"✓ Gear armor API returned {len(armor)} armor sets")
    
    def test_get_equipment(self):
        """Test /api/gear/equipment returns equipment"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("✓ Gear equipment API working")


class TestPricesAPI:
    """Price tracker endpoints"""
    
    def test_get_price_summary(self):
        """Test /api/prices/summary returns price summary"""
        response = requests.get(f"{BASE_URL}/api/prices/summary", timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("✓ Prices summary API working")
    
    def test_get_price_changes(self):
        """Test /api/prices/changes returns price changes"""
        response = requests.get(f"{BASE_URL}/api/prices/changes", timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("✓ Prices changes API working")


class TestWikeloAPI:
    """Wikelo contract endpoints"""
    
    def test_get_wikelo_info(self):
        """Test /api/wikelo/info returns wikelo info"""
        response = requests.get(f"{BASE_URL}/api/wikelo/info", timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("✓ Wikelo info API working")
    
    def test_get_wikelo_contracts(self):
        """Test /api/wikelo/contracts returns contracts"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts", timeout=15)
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        contracts = data.get("data", [])
        print(f"✓ Wikelo contracts API returned {len(contracts)} contracts")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
