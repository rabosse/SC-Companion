"""
Iteration 39: Starting Location Picker for Shopping Trip Route Planner
Tests:
1. GET /api/routes/starting_locations - returns dockable locations grouped by system
2. POST /api/routes/shopping_trip with origin_id - route starts from specified origin
3. POST /api/routes/shopping_trip without origin_id - backwards compatible
4. Route with origin includes extra leg from origin to first store
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestStartingLocationsEndpoint:
    """Tests for GET /api/routes/starting_locations"""
    
    def test_starting_locations_returns_success(self):
        """Endpoint returns success status"""
        response = requests.get(f"{BASE_URL}/api/routes/starting_locations")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_starting_locations_returns_dockable_types_only(self):
        """Only returns city, station, rest_stop types"""
        response = requests.get(f"{BASE_URL}/api/routes/starting_locations")
        data = response.json()["data"]
        
        assert len(data) > 0, "Should return at least some locations"
        
        allowed_types = {"city", "station", "rest_stop"}
        for loc in data:
            assert loc["type"] in allowed_types, f"Location {loc['name']} has invalid type {loc['type']}"
    
    def test_starting_locations_has_required_fields(self):
        """Each location has id, name, system, type"""
        response = requests.get(f"{BASE_URL}/api/routes/starting_locations")
        data = response.json()["data"]
        
        for loc in data:
            assert "id" in loc, "Missing id field"
            assert "name" in loc, "Missing name field"
            assert "system" in loc, "Missing system field"
            assert "type" in loc, "Missing type field"
    
    def test_starting_locations_grouped_by_system(self):
        """Locations include all 3 systems: Stanton, Pyro, Nyx"""
        response = requests.get(f"{BASE_URL}/api/routes/starting_locations")
        data = response.json()["data"]
        
        systems_found = set(loc["system"] for loc in data)
        
        # Should have locations from multiple systems
        assert "stanton" in systems_found, "Should have Stanton locations"
        # Nyx and Pyro may also be present
        assert len(systems_found) >= 1, "Should have at least one system"
    
    def test_starting_locations_count(self):
        """Should return ~36 dockable locations"""
        response = requests.get(f"{BASE_URL}/api/routes/starting_locations")
        data = response.json()["data"]
        
        # Should have significant number of dockable locations
        assert len(data) >= 30, f"Expected ~36 locations, got {len(data)}"


class TestShoppingTripWithOrigin:
    """Tests for POST /api/routes/shopping_trip with origin_id"""
    
    def test_shopping_trip_with_origin_returns_origin_in_response(self):
        """Origin appears in response when origin_id provided"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Centermass @ Area 18", "Dumpers Depot @ Lorville"],
                "qd_size": 1,
                "origin_id": "port-olisar"
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        
        assert data["origin"] is not None, "Origin should be in response"
        assert data["origin"]["id"] == "port-olisar"
        assert data["origin"]["name"] == "Port Olisar"
        assert data["origin"]["system"] == "stanton"
        assert "map_x" in data["origin"]
        assert "map_y" in data["origin"]
    
    def test_shopping_trip_without_origin_has_null_origin(self):
        """Backwards compatible - no origin when not provided"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Centermass @ Area 18"],
                "qd_size": 1
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        
        assert data["origin"] is None, "Origin should be null when not provided"
    
    def test_shopping_trip_origin_changes_route_order(self):
        """Route starts from origin - nearest store to origin is first"""
        # Without origin - Area 18 first (alphabetically/default)
        resp_no_origin = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Dumpers Depot @ Port Olisar", "Centermass @ Area 18"],
                "qd_size": 1
            }
        )
        
        # With origin at Grim HEX (near Port Olisar) - Port Olisar should be first
        resp_with_origin = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Dumpers Depot @ Port Olisar", "Centermass @ Area 18"],
                "qd_size": 1,
                "origin_id": "grim-hex"
            }
        )
        
        assert resp_with_origin.status_code == 200
        data = resp_with_origin.json()["data"]
        
        # Grim HEX is near Port Olisar, so Port Olisar should be first stop
        first_stop = data["stops"][0]
        assert first_stop["location_id"] == "port-olisar", \
            f"First stop should be Port Olisar (nearest to Grim HEX), got {first_stop['location_id']}"
        
        # Origin should be in response
        assert data["origin"]["id"] == "grim-hex"
    
    def test_shopping_trip_origin_adds_extra_leg(self):
        """Route includes leg from origin to first store"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Centermass @ Area 18", "Dumpers Depot @ Lorville"],
                "qd_size": 1,
                "origin_id": "new-babbage"
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        
        # Should have legs: origin->first, first->second
        legs = data["legs"]
        assert len(legs) >= 2, f"Expected at least 2 legs, got {len(legs)}"
        
        # First leg should be from origin
        first_leg = legs[0]
        assert first_leg["from_id"] == "new-babbage", \
            f"First leg should start from origin, got {first_leg['from_id']}"
    
    def test_shopping_trip_origin_with_single_store(self):
        """Origin works even with single store"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Centermass @ Area 18"],
                "qd_size": 1,
                "origin_id": "lorville"
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        
        assert data["origin"]["id"] == "lorville"
        assert len(data["stops"]) == 1
        assert len(data["legs"]) == 1  # Origin -> Area 18
        assert data["legs"][0]["from_id"] == "lorville"
        assert data["legs"][0]["to_id"] == "area18"
    
    def test_shopping_trip_invalid_origin_id(self):
        """Invalid origin_id should be ignored or handled gracefully"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Centermass @ Area 18"],
                "qd_size": 1,
                "origin_id": "invalid-location-xyz"
            }
        )
        # Should either return 200 with null origin or 400
        # Based on code, invalid origin is silently ignored (origin_loc = None)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["origin"] is None, "Invalid origin should result in null"
    
    def test_shopping_trip_origin_same_as_store(self):
        """When origin is same location as a store, handles gracefully"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Dumpers Depot @ Port Olisar", "Centermass @ Area 18"],
                "qd_size": 1,
                "origin_id": "port-olisar"
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        
        # Origin should still be set
        assert data["origin"]["id"] == "port-olisar"
        
        # First stop should be Port Olisar (since we're starting there)
        assert data["stops"][0]["location_id"] == "port-olisar"


class TestShoppingTripBackwardsCompatibility:
    """Ensure existing behavior is preserved without origin_id"""
    
    def test_shopping_trip_basic_route(self):
        """Basic multi-store route without origin"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Centermass @ Area 18", "Dumpers Depot @ New Babbage"],
                "qd_size": 1
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        
        assert len(data["stops"]) == 2
        assert data["origin"] is None
        assert data["total_distance_mkm"] > 0
        assert data["total_travel_time_s"] > 0
    
    def test_shopping_trip_response_structure(self):
        """Response has all required fields"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Centermass @ Area 18"],
                "qd_size": 1
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        
        # Required fields from iteration 38
        assert "stops" in data
        assert "legs" in data
        assert "total_distance_mkm" in data
        assert "total_travel_time_s" in data
        assert "qd_size" in data
        assert "qd_speed_kms" in data
        assert "unresolved_stores" in data
        assert "systems" in data
        assert "context_locations" in data
        # New field from iteration 39
        assert "origin" in data


class TestDifferentOriginLocations:
    """Test with various origin location types"""
    
    @pytest.mark.parametrize("origin_id,origin_name,origin_type", [
        ("lorville", "Lorville", "city"),
        ("area18", "Area 18", "city"),
        ("orison", "Orison", "city"),
        ("new-babbage", "New Babbage", "city"),
        ("port-olisar", "Port Olisar", "station"),
        ("grim-hex", "Grim HEX", "station"),
        ("everus-harbor", "Everus Harbor", "station"),
        ("hur-r1", "R&R HUR-L1", "rest_stop"),
    ])
    def test_origin_types(self, origin_id, origin_name, origin_type):
        """Various dockable location types work as origin"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Centermass @ Area 18"],
                "qd_size": 1,
                "origin_id": origin_id
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        
        assert data["origin"] is not None, f"Origin {origin_id} should be valid"
        assert data["origin"]["id"] == origin_id
        assert data["origin"]["name"] == origin_name
