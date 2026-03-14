"""
Iteration 41 Tests:
1. Shopping Route location resolution for hierarchical CStone format
2. Ship hardpoint verification (cross-referenced with Fleetyards/SCTools data)
3. Starting locations endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestShoppingRouteLocationResolution:
    """Test that shopping route resolves hierarchical CStone location strings"""

    def test_resolve_pyro_hierarchical_format(self):
        """Pyro > Pyro V > Ignis > Ashland > shop_terminal -> Bloom Settlement"""
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json={
            "store_names": ["Pyro > Pyro V > Ignis > Ashland > shop_terminal"],
            "qd_size": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        
        route_data = data.get("data", {})
        stops = route_data.get("stops", [])
        assert len(stops) >= 1, "Should resolve at least one store"
        
        # The Ashland/Ignis/Bloom store should resolve to Bloom Settlement
        first_stop = stops[0]
        location_name = first_stop.get("location_name", "").lower()
        # Check for bloom, settlement, or pyro-related location
        assert any(kw in location_name for kw in ["bloom", "settlement", "pyro"]), \
            f"Expected Bloom Settlement, got: {first_stop.get('location_name')}"

    def test_resolve_stanton_arccorp_format(self):
        """Stanton > ArcCorp > Area 18 > TDD > shop_terminal -> Area 18"""
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json={
            "store_names": ["Stanton > ArcCorp > Area 18 > TDD > shop_terminal"],
            "qd_size": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        
        route_data = data.get("data", {})
        stops = route_data.get("stops", [])
        assert len(stops) >= 1, "Should resolve at least one store"
        
        first_stop = stops[0]
        location_name = first_stop.get("location_name", "").lower()
        assert any(kw in location_name for kw in ["area", "18", "arccorp"]), \
            f"Expected Area 18, got: {first_stop.get('location_name')}"

    def test_resolve_with_origin_id(self):
        """Shopping trip with origin_id returns optimized route from that origin"""
        # Multiple stores to test route ordering
        store_names = [
            "Centermass @ Area 18",
            "Dumper's Depot @ Port Olisar",
            "Cubby Blast @ New Babbage"
        ]
        
        # Without origin
        response_no_origin = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json={
            "store_names": store_names,
            "qd_size": 1
        })
        assert response_no_origin.status_code == 200
        
        # With origin (Levski - Nyx system)
        response_with_origin = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json={
            "store_names": store_names,
            "qd_size": 1,
            "origin_id": "levski-city"
        })
        assert response_with_origin.status_code == 200
        data = response_with_origin.json()
        assert data.get("success") is True
        
        route_data = data.get("data", {})
        assert route_data.get("origin") is not None, "Origin should be set when origin_id provided"
        origin = route_data.get("origin", {})
        assert "levski" in origin.get("name", "").lower()

    def test_starting_locations_returns_dockable(self):
        """GET /api/routes/starting_locations returns dockable locations"""
        response = requests.get(f"{BASE_URL}/api/routes/starting_locations")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        
        locations = data.get("data", [])
        assert len(locations) >= 30, f"Expected 30+ locations, got {len(locations)}"
        
        # Check that all are dockable types
        valid_types = {"city", "station", "rest_stop"}
        for loc in locations:
            assert "id" in loc
            assert "name" in loc
            assert "system" in loc
            assert "type" in loc
            assert loc["type"] in valid_types, f"Type {loc['type']} not dockable"


class TestShipHardpoints:
    """Test ship hardpoint accuracy against Fleetyards/SCTools data"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Register and get auth token"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        username = f"hardptest_{unique_id}"
        
        # Try register
        register_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": "password123"
        })
        
        if register_res.status_code == 200:
            return register_res.json().get("access_token")
        
        # If failed, try login
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": f"{username}@test.com",
            "password": "password123"
        })
        if login_res.status_code == 200:
            return login_res.json().get("access_token")
        
        pytest.skip("Could not authenticate")

    def _get_ship_by_name(self, token, ship_name):
        """Helper to find ship by name (case-insensitive)"""
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/ships", headers=headers)
        if response.status_code != 200:
            return None
        
        ships = response.json().get("data", [])
        ship_name_lower = ship_name.lower()
        for ship in ships:
            if ship.get("name", "").lower() == ship_name_lower:
                return ship
        return None

    def test_gladius_hardpoints(self, auth_token):
        """Gladius should have 3 S3 weapon hardpoints [3,3,3]"""
        ship = self._get_ship_by_name(auth_token, "Gladius")
        assert ship is not None, "Gladius not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [3, 3, 3], f"Gladius weapons: expected [3,3,3], got {weapons}"

    def test_arrow_hardpoints(self, auth_token):
        """Arrow should have 3 S3 weapon hardpoints [3,3,3]"""
        ship = self._get_ship_by_name(auth_token, "Arrow")
        assert ship is not None, "Arrow not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [3, 3, 3], f"Arrow weapons: expected [3,3,3], got {weapons}"

    def test_cutlass_black_hardpoints(self, auth_token):
        """Cutlass Black should have 6 S3 weapon hardpoints [3,3,3,3,3,3]"""
        ship = self._get_ship_by_name(auth_token, "Cutlass Black")
        assert ship is not None, "Cutlass Black not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [3, 3, 3, 3, 3, 3], f"Cutlass Black weapons: expected [3,3,3,3,3,3], got {weapons}"

    def test_constellation_andromeda_hardpoints(self, auth_token):
        """Constellation Andromeda should have [5,5,5,5,2,2,2,2] weapons"""
        ship = self._get_ship_by_name(auth_token, "Constellation Andromeda")
        assert ship is not None, "Constellation Andromeda not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [5, 5, 5, 5, 2, 2, 2, 2], f"Constellation Andromeda weapons: expected [5,5,5,5,2,2,2,2], got {weapons}"

    def test_vanguard_warden_hardpoints(self, auth_token):
        """Vanguard Warden should have [5,2,2,2,2,2,2] weapons"""
        ship = self._get_ship_by_name(auth_token, "Vanguard Warden")
        assert ship is not None, "Vanguard Warden not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [5, 2, 2, 2, 2, 2, 2], f"Vanguard Warden weapons: expected [5,2,2,2,2,2,2], got {weapons}"

    def test_eclipse_hardpoints(self, auth_token):
        """Eclipse should have [2,2] weapons (NOT 3xS9 torpedoes as weapons)"""
        ship = self._get_ship_by_name(auth_token, "Eclipse")
        assert ship is not None, "Eclipse not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [2, 2], f"Eclipse weapons: expected [2,2], got {weapons}"

    def test_freelancer_hardpoints(self, auth_token):
        """Freelancer should have [5,5,3,3] weapons"""
        ship = self._get_ship_by_name(auth_token, "Freelancer")
        assert ship is not None, "Freelancer not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [5, 5, 3, 3], f"Freelancer weapons: expected [5,5,3,3], got {weapons}"

    def test_sabre_hardpoints(self, auth_token):
        """Sabre should have [3,3,3,3] weapons"""
        ship = self._get_ship_by_name(auth_token, "Sabre")
        assert ship is not None, "Sabre not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [3, 3, 3, 3], f"Sabre weapons: expected [3,3,3,3], got {weapons}"

    def test_redeemer_hardpoints(self, auth_token):
        """Redeemer should have [4,4,4,4,2,2,2,2] weapons"""
        ship = self._get_ship_by_name(auth_token, "Redeemer")
        assert ship is not None, "Redeemer not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [4, 4, 4, 4, 2, 2, 2, 2], f"Redeemer weapons: expected [4,4,4,4,2,2,2,2], got {weapons}"

    def test_hurricane_hardpoints(self, auth_token):
        """Hurricane should have [4,4,4,4] weapons"""
        ship = self._get_ship_by_name(auth_token, "Hurricane")
        assert ship is not None, "Hurricane not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [4, 4, 4, 4], f"Hurricane weapons: expected [4,4,4,4], got {weapons}"

    def test_corsair_hardpoints(self, auth_token):
        """Corsair should have [5,5,5,5,4,4,3,3,3,3,3,3] weapons"""
        ship = self._get_ship_by_name(auth_token, "Corsair")
        assert ship is not None, "Corsair not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [5, 5, 5, 5, 4, 4, 3, 3, 3, 3, 3, 3], f"Corsair weapons: expected [5,5,5,5,4,4,3,3,3,3,3,3], got {weapons}"

    def test_aurora_mr_hardpoints(self, auth_token):
        """Aurora MR should have [1,1,1,1] weapons"""
        ship = self._get_ship_by_name(auth_token, "Aurora MR")
        assert ship is not None, "Aurora MR not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [1, 1, 1, 1], f"Aurora MR weapons: expected [1,1,1,1], got {weapons}"

    def test_mustang_alpha_hardpoints(self, auth_token):
        """Mustang Alpha should have [3] weapons"""
        ship = self._get_ship_by_name(auth_token, "Mustang Alpha")
        assert ship is not None, "Mustang Alpha not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [3], f"Mustang Alpha weapons: expected [3], got {weapons}"

    def test_talon_hardpoints(self, auth_token):
        """Talon should have [4,4] weapons"""
        ship = self._get_ship_by_name(auth_token, "Talon")
        assert ship is not None, "Talon not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [4, 4], f"Talon weapons: expected [4,4], got {weapons}"

    def test_talon_shrike_hardpoints(self, auth_token):
        """Talon Shrike should have [2,2] weapons"""
        ship = self._get_ship_by_name(auth_token, "Talon Shrike")
        assert ship is not None, "Talon Shrike not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [2, 2], f"Talon Shrike weapons: expected [2,2], got {weapons}"

    def test_nomad_hardpoints(self, auth_token):
        """Nomad should have [3,3,3,3] weapons"""
        ship = self._get_ship_by_name(auth_token, "Nomad")
        assert ship is not None, "Nomad not found"
        
        hardpoints = ship.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        assert weapons == [3, 3, 3, 3], f"Nomad weapons: expected [3,3,3,3], got {weapons}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
