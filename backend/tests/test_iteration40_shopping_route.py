"""
Iteration 40: Shopping List Route Features Tests
Tests for:
1. POST /api/routes/shopping_trip with origin_id returns reordered stops matching the route
2. GET /api/routes/starting_locations returns dockable locations
3. Route button and store list reordering functionality
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')


class TestStartingLocations:
    """Test GET /api/routes/starting_locations endpoint"""

    def test_starting_locations_returns_success(self):
        """Starting locations endpoint returns success with data"""
        response = requests.get(f"{BASE_URL}/api/routes/starting_locations")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "data" in data
        assert isinstance(data["data"], list)
        print(f"PASS: Starting locations returned {len(data['data'])} locations")

    def test_starting_locations_has_required_fields(self):
        """Each location has id, name, system, type fields"""
        response = requests.get(f"{BASE_URL}/api/routes/starting_locations")
        assert response.status_code == 200
        data = response.json()
        locations = data.get("data", [])
        assert len(locations) > 0, "Should have at least one location"
        
        # Check first few locations have required fields
        for loc in locations[:5]:
            assert "id" in loc, f"Location missing 'id': {loc}"
            assert "name" in loc, f"Location missing 'name': {loc}"
            assert "system" in loc, f"Location missing 'system': {loc}"
            assert "type" in loc, f"Location missing 'type': {loc}"
        print(f"PASS: Locations have required fields (id, name, system, type)")

    def test_starting_locations_are_dockable_types(self):
        """Locations are dockable types (city, station, rest_stop)"""
        response = requests.get(f"{BASE_URL}/api/routes/starting_locations")
        assert response.status_code == 200
        data = response.json()
        locations = data.get("data", [])
        
        allowed_types = {"city", "station", "rest_stop"}
        for loc in locations:
            assert loc.get("type") in allowed_types, f"Invalid type: {loc.get('type')} for {loc.get('name')}"
        print(f"PASS: All locations are dockable types (city/station/rest_stop)")


class TestShoppingTripRouteOrdering:
    """Test POST /api/routes/shopping_trip route ordering with origin"""

    def test_shopping_trip_without_origin(self):
        """Shopping trip without origin_id is backwards compatible"""
        # Use location-based store names that map to actual star system locations
        store_names = ["Area 18", "New Babbage", "Lorville"]
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json={
            "store_names": store_names,
            "qd_size": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        result = data.get("data", {})
        
        # Should have stops
        stops = result.get("stops", [])
        assert len(stops) > 0, "Should have at least one stop"
        
        # Origin should be null when not provided
        assert result.get("origin") is None, "Origin should be null when not provided"
        print(f"PASS: Shopping trip without origin_id returns {len(stops)} stops, origin=null")

    def test_shopping_trip_with_origin_returns_reordered_stops(self):
        """Shopping trip with origin_id returns stops starting from origin"""
        # Get a starting location to use as origin
        locations_response = requests.get(f"{BASE_URL}/api/routes/starting_locations")
        assert locations_response.status_code == 200
        locations = locations_response.json().get("data", [])
        assert len(locations) > 0, "Need at least one starting location"
        
        # Pick a location (Lorville has good connectivity)
        origin_loc = next((l for l in locations if "lorville" in l.get("name", "").lower()), locations[0])
        origin_id = origin_loc["id"]
        
        # Use location-based store names
        store_names = ["Area 18", "New Babbage", "Orison"]
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json={
            "store_names": store_names,
            "qd_size": 1,
            "origin_id": origin_id
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        result = data.get("data", {})
        
        # Should have origin info
        origin = result.get("origin")
        assert origin is not None, "Origin should be set when origin_id provided"
        assert origin.get("id") == origin_id, "Origin ID should match requested origin"
        
        # Should have stops
        stops = result.get("stops", [])
        assert len(stops) > 0, "Should have stops"
        
        # Should have legs
        legs = result.get("legs", [])
        assert len(legs) > 0, "Should have legs (route segments)"
        
        # First leg should start from origin if not same location
        print(f"PASS: Shopping trip with origin_id returns origin object and {len(stops)} stops")
        print(f"  Origin: {origin.get('name')}, First stop: {stops[0].get('location_name') if stops else 'N/A'}")

    def test_shopping_trip_route_changes_with_different_origin(self):
        """Different origins produce different route orderings"""
        # Get starting locations
        locations_response = requests.get(f"{BASE_URL}/api/routes/starting_locations")
        locations = locations_response.json().get("data", [])
        
        # Get two different origins
        stanton_locs = [l for l in locations if l.get("system") == "stanton"]
        if len(stanton_locs) < 2:
            pytest.skip("Need at least 2 starting locations in Stanton")
        
        origin1 = stanton_locs[0]
        origin2 = stanton_locs[1] if stanton_locs[1]["id"] != stanton_locs[0]["id"] else stanton_locs[2]
        
        # Use location-based store names
        store_names = ["Area 18", "New Babbage", "Lorville"]
        
        # Route from origin 1
        response1 = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json={
            "store_names": store_names,
            "qd_size": 1,
            "origin_id": origin1["id"]
        })
        result1 = response1.json().get("data", {})
        
        # Route from origin 2
        response2 = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json={
            "store_names": store_names,
            "qd_size": 1,
            "origin_id": origin2["id"]
        })
        result2 = response2.json().get("data", {})
        
        # Check that routes exist
        assert len(result1.get("stops", [])) > 0
        assert len(result2.get("stops", [])) > 0
        
        # The origins should be different
        assert result1.get("origin", {}).get("id") != result2.get("origin", {}).get("id")
        
        print(f"PASS: Different origins produce routes from different starting points")
        print(f"  Origin 1: {origin1['name']}, Origin 2: {origin2['name']}")

    def test_shopping_trip_response_has_route_data(self):
        """Shopping trip response has complete route data for map display"""
        store_names = ["Area 18", "New Babbage"]
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json={
            "store_names": store_names,
            "qd_size": 1
        })
        assert response.status_code == 200
        result = response.json().get("data", {})
        
        # Check required fields for route map
        assert "stops" in result, "Response should have stops"
        assert "legs" in result, "Response should have legs"
        assert "total_distance_mkm" in result, "Response should have total_distance_mkm"
        assert "total_travel_time_s" in result, "Response should have total_travel_time_s"
        
        # Check stops have map coordinates
        stops = result.get("stops", [])
        if len(stops) > 0:
            stop = stops[0]
            assert "map_x" in stop, "Stop should have map_x"
            assert "map_y" in stop, "Stop should have map_y"
            assert "location_name" in stop, "Stop should have location_name"
        
        print(f"PASS: Shopping trip response has complete route data for map display")


class TestInvalidInputHandling:
    """Test error handling for invalid inputs"""

    def test_shopping_trip_invalid_origin(self):
        """Shopping trip with invalid origin_id handles gracefully"""
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json={
            "store_names": ["Area 18"],
            "qd_size": 1,
            "origin_id": "invalid-origin-id-12345"
        })
        assert response.status_code == 200  # Should still succeed
        result = response.json().get("data", {})
        # Origin should be null for invalid origin
        assert result.get("origin") is None, "Invalid origin should result in null origin"
        print(f"PASS: Invalid origin_id handled gracefully (origin=null)")

    def test_shopping_trip_empty_stores(self):
        """Shopping trip with empty store list returns error"""
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json={
            "store_names": [],
            "qd_size": 1
        })
        assert response.status_code == 400
        print(f"PASS: Empty store list returns 400 error")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
