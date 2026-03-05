"""
Test iteration 22: Route Planner overhaul with fuel model, fleet integration, and weapon hardpoints
Features tested:
- Route planner /api/routes/locations returns locations, systems, qd_speeds, qd_fuel
- Route planner /api/routes/calculate returns fuel_stops, fuel_remaining_pct, waypoints
- Cross-system routes include jump waypoints with type='jump'
- Low qd_range triggers fuel stops
- Ships endpoint returns quantum data (speed_kms, range_mkm, fuel_capacity)
- Ships have curated weapon hardpoints from _CURATED_HARDPOINTS
- Interdiction and chase calculators work
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TOKEN = None


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for API requests"""
    global TOKEN
    if TOKEN:
        return TOKEN
    
    # Login
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "testpilot",
        "password": "password123"
    })
    if resp.status_code == 200:
        TOKEN = resp.json().get("access_token")
        return TOKEN
    
    # Register if needed
    requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": "testpilot",
        "password": "password123"
    })
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "testpilot",
        "password": "password123"
    })
    TOKEN = resp.json().get("access_token")
    return TOKEN


class TestRouteLocations:
    """Tests for /api/routes/locations endpoint"""
    
    def test_locations_returns_data(self):
        """Test that locations endpoint returns location data"""
        resp = requests.get(f"{BASE_URL}/api/routes/locations")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True
        assert len(data.get("data", [])) > 50  # Should have 80+ locations
        
    def test_locations_returns_systems(self):
        """Test that locations endpoint returns system definitions"""
        resp = requests.get(f"{BASE_URL}/api/routes/locations")
        data = resp.json()
        systems = data.get("systems", {})
        assert "stanton" in systems
        assert "pyro" in systems
        assert "nyx" in systems
        
    def test_locations_returns_qd_speeds(self):
        """Test that locations endpoint returns QD speeds by size"""
        resp = requests.get(f"{BASE_URL}/api/routes/locations")
        data = resp.json()
        qd_speeds = data.get("qd_speeds", {})
        # Check QD speeds by size
        assert int(qd_speeds.get("1", 0)) == 165000  # Size 1
        assert int(qd_speeds.get("2", 0)) == 190000  # Size 2
        assert int(qd_speeds.get("3", 0)) == 240000  # Size 3
        
    def test_locations_returns_qd_fuel(self):
        """Test that locations endpoint returns QD fuel defaults"""
        resp = requests.get(f"{BASE_URL}/api/routes/locations")
        data = resp.json()
        qd_fuel = data.get("qd_fuel", {})
        assert qd_fuel.get("1", {}).get("range_mkm") == 120  # Size 1 range
        assert qd_fuel.get("2", {}).get("range_mkm") == 180  # Size 2 range


class TestRouteCalculation:
    """Tests for /api/routes/calculate endpoint"""
    
    def test_basic_route_calculation(self):
        """Test basic route calculation within Stanton"""
        resp = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "new-babbage",
            "qd_size": 1
        })
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        
        # Check route structure
        assert data["origin"]["name"] == "Lorville"
        assert data["destination"]["name"] == "New Babbage"
        assert data["qd_size"] == 1
        assert data["qd_speed_kms"] == 165000
        
        # Check fuel tracking
        assert "fuel_remaining_pct" in data
        assert "fuel_stops" in data
        assert data["fuel_remaining_pct"] > 0
        
        # Check waypoints
        assert len(data["waypoints"]) > 0
        assert data["waypoints"][0]["type"] == "quantum"
        
    def test_cross_system_route(self):
        """Test cross-system route includes jump waypoints"""
        resp = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "pyro-bloom-settlement",
            "qd_size": 2
        })
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        
        # Should be cross-system
        assert data["cross_system"] == True
        
        # Should have jump waypoint
        jump_waypoints = [w for w in data["waypoints"] if w["type"] == "jump"]
        assert len(jump_waypoints) > 0
        assert "Gateway" in jump_waypoints[0]["from"] or "Gateway" in jump_waypoints[0]["to"]
        
    def test_low_qd_range_triggers_fuel_stops(self):
        """Test that low qd_range triggers fuel stops on long routes"""
        resp = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "new-babbage",
            "qd_size": 1,
            "qd_range": 30  # Very low range
        })
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        
        # Should have fuel stops
        assert data["fuel_stops"] >= 1
        
        # Should have refuel waypoint
        refuel_waypoints = [w for w in data["waypoints"] if w["type"] == "refuel"]
        assert len(refuel_waypoints) >= 1
        
    def test_custom_qd_speed(self):
        """Test route calculation with custom QD speed"""
        resp = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "new-babbage",
            "qd_size": 1,
            "qd_speed": 200000  # Custom speed
        })
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        assert data["qd_speed_kms"] == 200000


class TestShipsQuantumAndHardpoints:
    """Tests for ships endpoint quantum data and weapon hardpoints"""
    
    def test_ships_returns_quantum_data(self, auth_token):
        """Test ships have quantum drive data"""
        resp = requests.get(f"{BASE_URL}/api/ships", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert resp.status_code == 200
        ships = resp.json().get("data", [])
        
        # Find Gladius
        gladius = next((s for s in ships if s["name"] == "Gladius"), None)
        assert gladius is not None
        
        # Check quantum data
        quantum = gladius.get("quantum", {})
        assert quantum.get("speed_kms", 0) > 0
        
    def test_gladius_has_correct_hardpoints(self, auth_token):
        """Test Gladius has [3,3,3] weapon hardpoints"""
        resp = requests.get(f"{BASE_URL}/api/ships", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        ships = resp.json().get("data", [])
        gladius = next((s for s in ships if s["name"] == "Gladius"), None)
        assert gladius is not None
        
        weapons = gladius.get("hardpoints", {}).get("weapons", [])
        assert weapons == [3, 3, 3]
        
    def test_avenger_titan_has_correct_hardpoints(self, auth_token):
        """Test Avenger Titan has [4,3,3] weapon hardpoints"""
        resp = requests.get(f"{BASE_URL}/api/ships", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        ships = resp.json().get("data", [])
        avenger = next((s for s in ships if s["name"] == "Avenger Titan"), None)
        assert avenger is not None
        
        weapons = avenger.get("hardpoints", {}).get("weapons", [])
        assert weapons == [4, 3, 3]
        
    def test_arrow_has_correct_hardpoints(self, auth_token):
        """Test Arrow has [3,3,3,3] weapon hardpoints"""
        resp = requests.get(f"{BASE_URL}/api/ships", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        ships = resp.json().get("data", [])
        arrow = next((s for s in ships if s["name"] == "Arrow"), None)
        assert arrow is not None
        
        weapons = arrow.get("hardpoints", {}).get("weapons", [])
        assert weapons == [3, 3, 3, 3]
        
    def test_cutlass_black_has_correct_hardpoints(self, auth_token):
        """Test Cutlass Black has [4,4,3,3] weapon hardpoints"""
        resp = requests.get(f"{BASE_URL}/api/ships", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        ships = resp.json().get("data", [])
        cutlass = next((s for s in ships if s["name"] == "Cutlass Black"), None)
        assert cutlass is not None
        
        weapons = cutlass.get("hardpoints", {}).get("weapons", [])
        assert weapons == [4, 4, 3, 3]
        
    def test_constellation_andromeda_has_correct_hardpoints(self, auth_token):
        """Test Constellation Andromeda has [5,5,4,4] weapon hardpoints"""
        resp = requests.get(f"{BASE_URL}/api/ships", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        ships = resp.json().get("data", [])
        connie = next((s for s in ships if s["name"] == "Constellation Andromeda"), None)
        assert connie is not None
        
        weapons = connie.get("hardpoints", {}).get("weapons", [])
        assert weapons == [5, 5, 4, 4]


class TestInterdiction:
    """Tests for interdiction calculator"""
    
    def test_interdiction_calculation(self):
        """Test interdiction calculator returns snare position"""
        resp = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "area18"],
            "destination": "new-babbage",
            "snare_range_mkm": 7.5
        })
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        
        assert "snare_position" in data
        assert "coverage_pct" in data
        assert "routes_covered" in data
        assert "routes_total" in data


class TestChase:
    """Tests for chase calculator"""
    
    def test_chase_calculation_faster_qd(self):
        """Test chase calculator when you're faster"""
        resp = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 3,
            "target_qd_size": 1,
            "distance_mkm": 10,
            "prep_time_seconds": 30
        })
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        
        assert data["can_catch"] == True
        assert data["your_speed_kms"] > data["target_speed_kms"]
        assert "verdict" in data
        
    def test_chase_calculation_slower_qd(self):
        """Test chase calculator when you're slower"""
        resp = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 1,
            "target_qd_size": 3,
            "distance_mkm": 10,
            "prep_time_seconds": 30
        })
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        
        assert data["can_catch"] == False
        assert data["your_speed_kms"] < data["target_speed_kms"]


class TestLoadoutBuilderShipData:
    """Tests for loadout builder ship data"""
    
    def test_ships_have_hardpoint_structure(self, auth_token):
        """Test ships have proper hardpoint structure for loadout builder"""
        resp = requests.get(f"{BASE_URL}/api/ships", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        ships = resp.json().get("data", [])
        
        # Sample several ships
        for ship in ships[:10]:
            hardpoints = ship.get("hardpoints", {})
            assert "shield" in hardpoints
            assert "power_plant" in hardpoints
            assert "cooler" in hardpoints
            assert "quantum_drive" in hardpoints
            assert "weapons" in hardpoints
