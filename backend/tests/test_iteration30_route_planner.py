"""
Test iteration 30: Route Planner Feature Validation
Comprehensive tests for Route, Interdiction, and Chase (Pursuit Planner) tabs
Features tested:
- GET /api/routes/locations - returns locations, systems, qd_speeds
- GET /api/routes/calculate - route calculation with distance, time, waypoints, fuel
- GET /api/routes/calculate with cross-system route (stanton to pyro)
- POST /api/routes/interdiction - interdiction analysis with coverage, snare position
- POST /api/routes/chase/advanced - chase analysis with escape destinations, intercept %, tactical notes
- POST /api/routes/chase - simple chase calculator
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TOKEN = None

# QD Speeds reference
QD_SPEEDS = {
    1: 165_000,   # Small
    2: 190_000,   # Medium  
    3: 240_000,   # Large
}


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for API requests"""
    global TOKEN
    if TOKEN:
        return TOKEN
    
    # Try login with test credentials from request
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "chasetest",
        "password": "Test123!"
    })
    if resp.status_code == 200:
        TOKEN = resp.json().get("access_token")
        return TOKEN
    
    # Try alternate credentials
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "testpilot",
        "password": "password123"
    })
    if resp.status_code == 200:
        TOKEN = resp.json().get("access_token")
        return TOKEN
    
    # Register if needed
    requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": "route_test_30",
        "password": "Test123!"
    })
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "route_test_30",
        "password": "Test123!"
    })
    if resp.status_code == 200:
        TOKEN = resp.json().get("access_token")
    return TOKEN


class TestLocationsEndpoint:
    """Tests for GET /api/routes/locations endpoint"""
    
    def test_locations_returns_success(self):
        """Test locations endpoint returns success"""
        resp = requests.get(f"{BASE_URL}/api/routes/locations")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True
        
    def test_locations_returns_location_data(self):
        """Test locations endpoint returns at least 50 locations"""
        resp = requests.get(f"{BASE_URL}/api/routes/locations")
        data = resp.json()
        locations = data.get("data", [])
        assert len(locations) > 50  # Should have 80+ locations
        
    def test_locations_have_required_fields(self):
        """Test that locations have required fields for map rendering"""
        resp = requests.get(f"{BASE_URL}/api/routes/locations")
        data = resp.json()
        locations = data.get("data", [])
        
        # Check first location has required fields
        assert len(locations) > 0
        loc = locations[0]
        required_fields = ["id", "name", "system", "type", "map_x", "map_y"]
        for field in required_fields:
            assert field in loc, f"Location missing field: {field}"
            
    def test_locations_returns_systems(self):
        """Test locations endpoint returns system definitions for Stanton, Pyro, Nyx"""
        resp = requests.get(f"{BASE_URL}/api/routes/locations")
        data = resp.json()
        systems = data.get("systems", {})
        assert "stanton" in systems
        assert "pyro" in systems
        assert "nyx" in systems
        
    def test_systems_have_star_coordinates(self):
        """Test that each system has star coordinates for visualization"""
        resp = requests.get(f"{BASE_URL}/api/routes/locations")
        data = resp.json()
        systems = data.get("systems", {})
        
        for sys_id, sys_data in systems.items():
            assert "star" in sys_data, f"System {sys_id} missing star data"
            assert "x" in sys_data["star"], f"System {sys_id} star missing x coordinate"
            assert "y" in sys_data["star"], f"System {sys_id} star missing y coordinate"
            
    def test_locations_returns_qd_speeds(self):
        """Test locations endpoint returns QD speeds by size"""
        resp = requests.get(f"{BASE_URL}/api/routes/locations")
        data = resp.json()
        qd_speeds = data.get("qd_speeds", {})
        
        # Check QD speeds match expected values
        assert int(qd_speeds.get(1, qd_speeds.get("1", 0))) == 165000  # Size 1
        assert int(qd_speeds.get(2, qd_speeds.get("2", 0))) == 190000  # Size 2
        assert int(qd_speeds.get(3, qd_speeds.get("3", 0))) == 240000  # Size 3


class TestRouteCalculation:
    """Tests for GET /api/routes/calculate endpoint"""
    
    def test_basic_route_lorville_to_area18(self):
        """Test basic route calculation from Lorville to Area18"""
        resp = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "area18",
            "qd_size": 2
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True
        
        route = data.get("data", {})
        # Check origin and destination
        assert route["origin"]["name"] == "Lorville"
        assert route["destination"]["name"] == "Area 18"
        
    def test_route_returns_distance(self):
        """Test route calculation returns total distance in Mkm"""
        resp = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "area18",
            "qd_size": 2
        })
        data = resp.json().get("data", {})
        
        assert "total_distance_mkm" in data
        assert data["total_distance_mkm"] > 0
        
    def test_route_returns_travel_time(self):
        """Test route calculation returns travel time in seconds"""
        resp = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "area18",
            "qd_size": 2
        })
        data = resp.json().get("data", {})
        
        assert "travel_time_seconds" in data
        assert data["travel_time_seconds"] > 0
        
    def test_route_returns_waypoints(self):
        """Test route calculation returns waypoints array"""
        resp = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "area18",
            "qd_size": 2
        })
        data = resp.json().get("data", {})
        
        assert "waypoints" in data
        assert len(data["waypoints"]) > 0
        
        # Check waypoint structure
        wp = data["waypoints"][0]
        assert "from" in wp
        assert "to" in wp
        assert "distance_mkm" in wp
        assert "type" in wp
        
    def test_route_returns_fuel_info(self):
        """Test route calculation returns fuel information"""
        resp = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "area18",
            "qd_size": 2
        })
        data = resp.json().get("data", {})
        
        assert "fuel_remaining_pct" in data
        assert "fuel_stops" in data
        
    def test_cross_system_route_stanton_to_pyro(self):
        """Test cross-system route from Stanton to Pyro includes jump waypoints"""
        resp = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "pyro-bloom-settlement",
            "qd_size": 2
        })
        assert resp.status_code == 200
        data = resp.json().get("data", {})
        
        # Should be marked as cross-system
        assert data["cross_system"] == True
        
        # Should have jump waypoint(s)
        jump_waypoints = [w for w in data["waypoints"] if w["type"] == "jump"]
        assert len(jump_waypoints) > 0
        
    def test_route_qd_speed_matches_size(self):
        """Test that route uses correct QD speed for size"""
        for qd_size in [1, 2, 3]:
            resp = requests.get(f"{BASE_URL}/api/routes/calculate", params={
                "origin": "lorville",
                "destination": "area18",
                "qd_size": qd_size
            })
            data = resp.json().get("data", {})
            assert data["qd_speed_kms"] == QD_SPEEDS[qd_size]


class TestInterdictionEndpoint:
    """Tests for POST /api/routes/interdiction endpoint"""
    
    def test_interdiction_basic_request(self):
        """Test basic interdiction analysis request"""
        resp = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville"],
            "destination": "area18",
            "snare_range_mkm": 7.5
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True
        
    def test_interdiction_returns_snare_position(self):
        """Test interdiction returns snare position coordinates"""
        resp = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "orison"],
            "destination": "area18",
            "snare_range_mkm": 7.5
        })
        data = resp.json().get("data", {})
        
        assert "snare_position" in data
        assert "x" in data["snare_position"]
        assert "y" in data["snare_position"]
        
    def test_interdiction_returns_coverage(self):
        """Test interdiction returns coverage percentage"""
        resp = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville"],
            "destination": "area18",
            "snare_range_mkm": 7.5
        })
        data = resp.json().get("data", {})
        
        assert "coverage_pct" in data
        assert 0 <= data["coverage_pct"] <= 100
        
    def test_interdiction_returns_route_details(self):
        """Test interdiction returns detailed route analysis"""
        resp = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "orison", "new-babbage"],
            "destination": "area18",
            "snare_range_mkm": 7.5,
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        data = resp.json().get("data", {})
        
        assert "route_details" in data
        assert len(data["route_details"]) >= 1
        
        # Check route detail structure
        if len(data["route_details"]) > 0:
            rd = data["route_details"][0]
            assert "origin_name" in rd
            assert "distance_mkm" in rd
            assert "covered" in rd
            
    def test_interdiction_with_qd_sizes(self):
        """Test interdiction includes QD size analysis for timing"""
        resp = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville"],
            "destination": "area18",
            "snare_range_mkm": 7.5,
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        data = resp.json().get("data", {})
        
        # Should have escape analysis with speed info
        assert "escape_analysis" in data or "your_speed_kms" in data.get("escape_analysis", {})
        
    def test_interdiction_single_origin_100_coverage(self):
        """Test single origin achieves 100% coverage"""
        resp = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville"],
            "destination": "area18",
            "snare_range_mkm": 7.5
        })
        data = resp.json().get("data", {})
        
        assert data["coverage_pct"] == 100
        assert data["routes_covered"] == 1
        assert data["routes_total"] == 1


class TestChaseAdvancedEndpoint:
    """Tests for POST /api/routes/chase/advanced endpoint (Pursuit Planner)"""
    
    def test_chase_advanced_basic_request(self):
        """Test basic chase advanced analysis request"""
        resp = requests.post(f"{BASE_URL}/api/routes/chase/advanced", json={
            "your_position": "lorville",
            "target_position": "area18",
            "your_qd_size": 2,
            "target_qd_size": 1,
            "prep_time_seconds": 30
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True
        
    def test_chase_advanced_returns_positions(self):
        """Test chase returns your and target position info"""
        resp = requests.post(f"{BASE_URL}/api/routes/chase/advanced", json={
            "your_position": "lorville",
            "target_position": "area18",
            "your_qd_size": 2,
            "target_qd_size": 1,
            "prep_time_seconds": 30
        })
        data = resp.json().get("data", {})
        
        assert "your_position" in data
        assert "target_position" in data
        assert data["your_position"]["name"] == "Lorville"
        assert data["target_position"]["name"] == "Area 18"
        
    def test_chase_advanced_returns_escape_destinations(self):
        """Test chase returns escape destinations analysis"""
        resp = requests.post(f"{BASE_URL}/api/routes/chase/advanced", json={
            "your_position": "lorville",
            "target_position": "orison",
            "your_qd_size": 2,
            "target_qd_size": 1,
            "prep_time_seconds": 30
        })
        data = resp.json().get("data", {})
        
        assert "escape_destinations" in data
        assert len(data["escape_destinations"]) > 0
        
        # Check escape destination structure
        dest = data["escape_destinations"][0]
        assert "name" in dest
        assert "type" in dest
        assert "can_intercept" in dest
        
    def test_chase_advanced_returns_intercept_percentage(self):
        """Test chase returns intercept percentage"""
        resp = requests.post(f"{BASE_URL}/api/routes/chase/advanced", json={
            "your_position": "lorville",
            "target_position": "orison",
            "your_qd_size": 2,
            "target_qd_size": 1,
            "prep_time_seconds": 30
        })
        data = resp.json().get("data", {})
        
        assert "intercept_pct" in data
        assert 0 <= data["intercept_pct"] <= 100
        
    def test_chase_advanced_returns_tactical_notes(self):
        """Test chase returns tactical notes"""
        resp = requests.post(f"{BASE_URL}/api/routes/chase/advanced", json={
            "your_position": "lorville",
            "target_position": "orison",
            "your_qd_size": 2,
            "target_qd_size": 1,
            "prep_time_seconds": 30
        })
        data = resp.json().get("data", {})
        
        assert "tactical_notes" in data
        assert len(data["tactical_notes"]) > 0
        
    def test_chase_advanced_returns_threat_level(self):
        """Test chase returns threat level assessment"""
        resp = requests.post(f"{BASE_URL}/api/routes/chase/advanced", json={
            "your_position": "lorville",
            "target_position": "orison",
            "your_qd_size": 2,
            "target_qd_size": 1,
            "prep_time_seconds": 30
        })
        data = resp.json().get("data", {})
        
        assert "threat_level" in data
        assert data["threat_level"] in ["low", "medium", "high", "critical"]
        
    def test_chase_advanced_faster_qd_better_intercept(self):
        """Test that faster QD gives better intercept rate"""
        # Your QD is faster
        resp_fast = requests.post(f"{BASE_URL}/api/routes/chase/advanced", json={
            "your_position": "lorville",
            "target_position": "orison",
            "your_qd_size": 3,
            "target_qd_size": 1,
            "prep_time_seconds": 30
        })
        data_fast = resp_fast.json().get("data", {})
        
        # Your QD is slower  
        resp_slow = requests.post(f"{BASE_URL}/api/routes/chase/advanced", json={
            "your_position": "lorville",
            "target_position": "orison",
            "your_qd_size": 1,
            "target_qd_size": 3,
            "prep_time_seconds": 30
        })
        data_slow = resp_slow.json().get("data", {})
        
        # Faster QD should have higher or equal intercept percentage
        assert data_fast["intercept_pct"] >= data_slow["intercept_pct"]


class TestSimpleChaseEndpoint:
    """Tests for POST /api/routes/chase endpoint (simple calculator)"""
    
    def test_chase_simple_basic_request(self):
        """Test basic simple chase calculation"""
        resp = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 2,
            "target_qd_size": 1,
            "distance_mkm": 10,
            "prep_time_seconds": 30
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True
        
    def test_chase_simple_faster_can_catch(self):
        """Test faster ship can catch slower target"""
        resp = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 3,
            "target_qd_size": 1,
            "distance_mkm": 10,
            "prep_time_seconds": 30
        })
        data = resp.json().get("data", {})
        
        assert data["can_catch"] == True
        assert data["your_speed_kms"] > data["target_speed_kms"]
        
    def test_chase_simple_slower_cannot_catch(self):
        """Test slower ship cannot catch faster target"""
        resp = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 1,
            "target_qd_size": 3,
            "distance_mkm": 10,
            "prep_time_seconds": 30
        })
        data = resp.json().get("data", {})
        
        assert data["can_catch"] == False
        assert data["your_speed_kms"] < data["target_speed_kms"]
        
    def test_chase_simple_returns_verdict(self):
        """Test chase returns verdict text"""
        resp = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 2,
            "target_qd_size": 1,
            "distance_mkm": 10,
            "prep_time_seconds": 30
        })
        data = resp.json().get("data", {})
        
        assert "verdict" in data
        assert len(data["verdict"]) > 0


class TestErrorHandling:
    """Tests for error handling in route endpoints"""
    
    def test_route_invalid_origin(self):
        """Test route calculation with invalid origin returns 400"""
        resp = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "invalid-location",
            "destination": "area18",
            "qd_size": 2
        })
        assert resp.status_code == 400
        
    def test_route_invalid_destination(self):
        """Test route calculation with invalid destination returns 400"""
        resp = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "invalid-location",
            "qd_size": 2
        })
        assert resp.status_code == 400
        
    def test_interdiction_invalid_destination(self):
        """Test interdiction with invalid destination returns 400"""
        resp = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville"],
            "destination": "invalid-location",
            "snare_range_mkm": 7.5
        })
        assert resp.status_code == 400
        
    def test_interdiction_empty_origins(self):
        """Test interdiction with empty origins returns 400"""
        resp = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": [],
            "destination": "area18",
            "snare_range_mkm": 7.5
        })
        assert resp.status_code == 400
        
    def test_chase_advanced_invalid_position(self):
        """Test chase with invalid position returns 400"""
        resp = requests.post(f"{BASE_URL}/api/routes/chase/advanced", json={
            "your_position": "invalid-location",
            "target_position": "area18",
            "your_qd_size": 2,
            "target_qd_size": 1,
            "prep_time_seconds": 30
        })
        assert resp.status_code == 400
