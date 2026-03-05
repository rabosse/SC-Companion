"""
Iteration 24: Starmap/Route Planner Visual Overhaul Tests
Tests the complete visual overhaul of the starmap with animated canvas,
route calculation, interdiction, and chase functionality.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRouteLocationsAPI:
    """Test /api/routes/locations endpoint - returns map data"""
    
    def test_locations_returns_success(self):
        """Verify locations endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("PASS: /api/routes/locations returns success")
    
    def test_locations_returns_data_array(self):
        """Verify locations endpoint returns data array with locations"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        data = response.json()
        locations = data.get("data", [])
        assert isinstance(locations, list)
        assert len(locations) > 80  # Should have 80+ locations
        print(f"PASS: Returns {len(locations)} locations")
    
    def test_locations_returns_systems(self):
        """Verify systems data (stanton, pyro, nyx) is returned"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        data = response.json()
        systems = data.get("systems", {})
        assert "stanton" in systems
        assert "pyro" in systems
        assert "nyx" in systems
        assert systems["stanton"]["name"] == "Stanton"
        print("PASS: Returns 3 systems (stanton, pyro, nyx)")
    
    def test_locations_returns_qd_speeds(self):
        """Verify QD speeds by size are returned"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        data = response.json()
        qd_speeds = data.get("qd_speeds", {})
        assert len(qd_speeds) >= 3
        # Size 1, 2, 3 should exist
        assert qd_speeds.get(1) or qd_speeds.get("1")
        print("PASS: Returns QD speeds by size")
    
    def test_location_has_map_coordinates(self):
        """Verify locations have map_x and map_y for canvas rendering"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        locations = response.json().get("data", [])
        for loc in locations[:10]:  # Check first 10
            assert "map_x" in loc, f"Location {loc.get('id')} missing map_x"
            assert "map_y" in loc, f"Location {loc.get('id')} missing map_y"
        print("PASS: All locations have map coordinates for canvas rendering")
    
    def test_location_types_exist(self):
        """Verify various location types exist (star, planet, moon, gateway, city, etc.)"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        locations = response.json().get("data", [])
        types = set(loc.get("type") for loc in locations)
        expected_types = {"star", "planet", "moon", "gateway", "city", "station"}
        assert expected_types.issubset(types), f"Missing types: {expected_types - types}"
        print(f"PASS: Location types present: {types}")


class TestRouteCalculationAPI:
    """Test /api/routes/calculate endpoint - calculates quantum routes"""
    
    def test_basic_route_calculation(self):
        """Test basic route between two locations"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "new-babbage",
            "qd_size": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        route = data.get("data", {})
        assert route.get("origin", {}).get("id") == "lorville"
        assert route.get("destination", {}).get("id") == "new-babbage"
        print("PASS: Basic route calculation works")
    
    def test_route_includes_fuel_tracking(self):
        """Verify route includes fuel tracking fields"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "new-babbage",
            "qd_size": 1
        })
        route = response.json().get("data", {})
        assert "fuel_remaining_pct" in route
        assert "fuel_stops" in route
        assert "qd_range_mkm" in route
        print(f"PASS: Route includes fuel tracking (remaining: {route.get('fuel_remaining_pct')}%)")
    
    def test_route_includes_travel_time(self):
        """Verify route includes travel time calculation"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "new-babbage",
            "qd_size": 1
        })
        route = response.json().get("data", {})
        assert "travel_time_seconds" in route
        assert route.get("travel_time_seconds") > 0
        assert "qd_speed_kms" in route
        print(f"PASS: Route includes travel time ({route.get('travel_time_seconds')}s)")
    
    def test_route_includes_waypoints(self):
        """Verify route includes waypoints array"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "new-babbage",
            "qd_size": 1
        })
        route = response.json().get("data", {})
        waypoints = route.get("waypoints", [])
        assert isinstance(waypoints, list)
        assert len(waypoints) >= 1
        wp = waypoints[0]
        assert "from" in wp
        assert "to" in wp
        assert "distance_mkm" in wp
        print(f"PASS: Route includes {len(waypoints)} waypoint(s)")
    
    def test_cross_system_route_has_jump_waypoints(self):
        """Verify cross-system routes include jump waypoints through gateways"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "pyro-iii",
            "qd_size": 1
        })
        route = response.json().get("data", {})
        assert route.get("cross_system") == True
        waypoints = route.get("waypoints", [])
        jump_waypoints = [wp for wp in waypoints if wp.get("type") == "jump"]
        assert len(jump_waypoints) >= 1, "Cross-system route should have jump waypoint"
        print(f"PASS: Cross-system route has {len(jump_waypoints)} jump waypoint(s)")
    
    def test_custom_qd_speed_override(self):
        """Verify custom QD speed override works"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "area18",
            "qd_size": 1,
            "qd_speed": 200000
        })
        route = response.json().get("data", {})
        assert route.get("qd_speed_kms") == 200000
        print("PASS: Custom QD speed override works")
    
    def test_invalid_location_returns_error(self):
        """Verify invalid location returns error"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "invalid-location",
            "destination": "new-babbage",
            "qd_size": 1
        })
        assert response.status_code == 400
        print("PASS: Invalid location returns 400 error")


class TestInterdictionAPI:
    """Test /api/routes/interdiction endpoint - calculates QED snare position"""
    
    def test_interdiction_basic_calculation(self):
        """Test basic interdiction calculation"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "area18"],
            "destination": "new-babbage",
            "snare_range_mkm": 7.5
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        result = data.get("data", {})
        assert "snare_position" in result
        assert "coverage_pct" in result
        print("PASS: Basic interdiction calculation works")
    
    def test_interdiction_returns_snare_position(self):
        """Verify snare position has x and y coordinates"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "area18"],
            "destination": "new-babbage",
            "snare_range_mkm": 7.5
        })
        result = response.json().get("data", {})
        snare = result.get("snare_position", {})
        assert "x" in snare
        assert "y" in snare
        print(f"PASS: Snare position: ({snare.get('x')}, {snare.get('y')})")
    
    def test_interdiction_returns_coverage(self):
        """Verify coverage percentage and route counts"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "area18"],
            "destination": "new-babbage",
            "snare_range_mkm": 7.5
        })
        result = response.json().get("data", {})
        assert "coverage_pct" in result
        assert "routes_covered" in result
        assert "routes_total" in result
        assert result.get("routes_total") == 2
        print(f"PASS: Coverage {result.get('coverage_pct')}%, {result.get('routes_covered')}/{result.get('routes_total')} routes")
    
    def test_interdiction_returns_route_lines(self):
        """Verify route lines for canvas visualization"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "area18"],
            "destination": "new-babbage",
            "snare_range_mkm": 7.5
        })
        result = response.json().get("data", {})
        route_lines = result.get("route_lines", [])
        assert len(route_lines) == 2
        for rl in route_lines:
            assert "sx" in rl and "sy" in rl  # Start coordinates
            assert "ex" in rl and "ey" in rl  # End coordinates
        print("PASS: Route lines returned for canvas visualization")


class TestChaseAPI:
    """Test /api/routes/chase endpoint - calculates quantum chase scenarios"""
    
    def test_chase_faster_can_catch(self):
        """Test chase where pursuer is faster (should catch)"""
        response = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 2,
            "target_qd_size": 1,
            "distance_mkm": 10,
            "prep_time_seconds": 30
        })
        assert response.status_code == 200
        result = response.json().get("data", {})
        assert result.get("can_catch") == True
        assert result.get("your_speed_kms") > result.get("target_speed_kms")
        print("PASS: Faster QD can catch target")
    
    def test_chase_slower_cannot_catch(self):
        """Test chase where pursuer is slower (should not catch)"""
        response = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 1,
            "target_qd_size": 3,
            "distance_mkm": 10,
            "prep_time_seconds": 30
        })
        result = response.json().get("data", {})
        assert result.get("can_catch") == False
        assert result.get("your_speed_kms") < result.get("target_speed_kms")
        print("PASS: Slower QD cannot catch target")
    
    def test_chase_returns_timing_data(self):
        """Verify chase returns timing data when catchable"""
        response = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 2,
            "target_qd_size": 1,
            "distance_mkm": 10,
            "prep_time_seconds": 30
        })
        result = response.json().get("data", {})
        assert "closing_time_seconds" in result
        assert "total_time_seconds" in result
        assert result.get("total_time_seconds") > result.get("closing_time_seconds")
        print(f"PASS: Chase timing - closing: {result.get('closing_time_seconds')}s, total: {result.get('total_time_seconds')}s")
    
    def test_chase_returns_verdict(self):
        """Verify chase returns human-readable verdict"""
        response = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 2,
            "target_qd_size": 1,
            "distance_mkm": 10,
            "prep_time_seconds": 30
        })
        result = response.json().get("data", {})
        assert "verdict" in result
        assert len(result.get("verdict", "")) > 10
        print(f"PASS: Verdict returned: {result.get('verdict')[:60]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
