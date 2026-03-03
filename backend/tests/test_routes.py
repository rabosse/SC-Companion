"""
Route Planner API Tests - Iteration 8
Tests for /api/routes/locations and /api/routes/calculate endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRoutesPlannerAPI:
    """Tests for Route Planner endpoints - PUBLIC (no auth required)"""

    def test_get_locations_success(self):
        """GET /api/routes/locations returns all navigable locations"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "systems" in data
        assert "qd_speeds" in data
        
        # Validate location count (should be 61)
        locations = data["data"]
        assert len(locations) == 61, f"Expected 61 locations, got {len(locations)}"
        
        # Validate systems
        systems = data["systems"]
        assert "stanton" in systems
        assert "pyro" in systems
        assert "nyx" in systems
        
        # Validate QD speeds
        qd_speeds = data["qd_speeds"]
        assert "1" in qd_speeds or 1 in qd_speeds  # JSON may stringify keys
        
    def test_locations_have_required_fields(self):
        """Each location has required fields: id, name, system, type, map_x, map_y"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        assert response.status_code == 200
        
        locations = response.json()["data"]
        required_fields = ["id", "name", "system", "type", "map_x", "map_y"]
        
        for loc in locations:
            for field in required_fields:
                assert field in loc, f"Location {loc.get('id', 'unknown')} missing {field}"
    
    def test_locations_grouped_by_system(self):
        """Locations exist in all 3 systems: stanton, pyro, nyx"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        assert response.status_code == 200
        
        locations = response.json()["data"]
        systems_present = set(loc["system"] for loc in locations)
        
        assert "stanton" in systems_present
        assert "pyro" in systems_present
        assert "nyx" in systems_present
        
        # Count by system
        stanton_count = len([l for l in locations if l["system"] == "stanton"])
        pyro_count = len([l for l in locations if l["system"] == "pyro"])
        nyx_count = len([l for l in locations if l["system"] == "nyx"])
        
        assert stanton_count > 30, f"Stanton should have 30+ locations, got {stanton_count}"
        assert pyro_count >= 8, f"Pyro should have 8+ locations, got {pyro_count}"
        assert nyx_count >= 8, f"Nyx should have 8+ locations, got {nyx_count}"

    def test_calculate_same_system_route(self):
        """Calculate route within same system: Hurston to microTech"""
        response = requests.get(
            f"{BASE_URL}/api/routes/calculate",
            params={"origin": "hurston", "destination": "microtech", "qd_size": 2}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        route = data["data"]
        
        # Validate route structure
        assert route["origin"]["id"] == "hurston"
        assert route["origin"]["name"] == "Hurston"
        assert route["destination"]["id"] == "microtech"
        assert route["destination"]["name"] == "microTech"
        assert route["qd_size"] == 2
        assert route["qd_speed_kms"] == 190000
        assert route["cross_system"] is False
        
        # Validate distance/time
        assert route["total_distance_mkm"] > 0
        assert route["travel_time_seconds"] > 0
        
        # Same-system route should have 1 quantum waypoint
        assert len(route["waypoints"]) == 1
        assert route["waypoints"][0]["type"] == "quantum"

    def test_calculate_cross_system_route(self):
        """Calculate cross-system route: Hurston to Pyro III via gateway"""
        response = requests.get(
            f"{BASE_URL}/api/routes/calculate",
            params={"origin": "hurston", "destination": "pyro-iii", "qd_size": 2}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        route = data["data"]
        
        # Validate cross-system flag
        assert route["cross_system"] is True
        
        # Cross-system route should have 3 waypoints: quantum -> jump -> quantum
        waypoints = route["waypoints"]
        assert len(waypoints) == 3
        assert waypoints[0]["type"] == "quantum"  # To gateway
        assert waypoints[1]["type"] == "jump"     # Jump tunnel
        assert waypoints[2]["type"] == "quantum"  # From gateway to dest
        
        # Validate gateway names in waypoints
        assert "Gateway" in waypoints[0]["to"]
        assert "Gateway" in waypoints[1]["from"]
        assert "Gateway" in waypoints[1]["to"]
        assert "Gateway" in waypoints[2]["from"]

    def test_qd_size_affects_travel_time(self):
        """Different QD sizes produce different travel times"""
        times = {}
        for qd_size in [1, 2, 3]:
            response = requests.get(
                f"{BASE_URL}/api/routes/calculate",
                params={"origin": "hurston", "destination": "microtech", "qd_size": qd_size}
            )
            assert response.status_code == 200
            times[qd_size] = response.json()["data"]["travel_time_seconds"]
        
        # Larger QD should be faster (smaller travel time)
        assert times[1] > times[2] > times[3], f"Expected S1 > S2 > S3 times, got {times}"

    def test_calculate_route_same_origin_destination_error(self):
        """Error when origin equals destination"""
        response = requests.get(
            f"{BASE_URL}/api/routes/calculate",
            params={"origin": "hurston", "destination": "hurston", "qd_size": 1}
        )
        assert response.status_code == 400
        assert "same" in response.json()["detail"].lower()

    def test_calculate_route_invalid_location_error(self):
        """Error when location doesn't exist"""
        response = requests.get(
            f"{BASE_URL}/api/routes/calculate",
            params={"origin": "invalid-planet", "destination": "hurston", "qd_size": 1}
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_location_types_present(self):
        """All location types exist: star, planet, moon, station, gateway"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        locations = response.json()["data"]
        
        types_present = set(loc["type"] for loc in locations)
        assert "star" in types_present
        assert "planet" in types_present
        assert "moon" in types_present
        assert "station" in types_present
        assert "gateway" in types_present

    def test_cross_system_nyx_route(self):
        """Cross-system route to Nyx: Hurston to Delamar"""
        response = requests.get(
            f"{BASE_URL}/api/routes/calculate",
            params={"origin": "hurston", "destination": "delamar", "qd_size": 1}
        )
        assert response.status_code == 200
        
        route = response.json()["data"]
        assert route["cross_system"] is True
        assert route["destination"]["system"] == "nyx"
        
        # Should have jump waypoint
        jump_waypoints = [w for w in route["waypoints"] if w["type"] == "jump"]
        assert len(jump_waypoints) >= 1
