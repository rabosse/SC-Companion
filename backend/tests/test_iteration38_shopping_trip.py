"""
Iteration 38: Shopping Trip Route Planner Backend Tests
Tests the POST /api/routes/shopping_trip endpoint for loadout shopping list feature
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestShoppingTripEndpoint:
    """Tests for POST /api/routes/shopping_trip endpoint"""
    
    def test_shopping_trip_multiple_stores(self):
        """Test multi-stop route calculation with known store locations"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Centermass @ Area 18", "Dumpers Depot @ New Babbage", "Tammany and Sons @ Lorville"],
                "qd_size": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        result = data["data"]
        
        # Verify stops structure
        assert "stops" in result
        assert len(result["stops"]) == 3
        
        # Verify first stop
        stop1 = result["stops"][0]
        assert stop1["order"] == 1
        assert stop1["location_name"] == "Area 18"
        assert stop1["location_id"] == "area18"
        assert stop1["system"] == "stanton"
        assert "map_x" in stop1
        assert "map_y" in stop1
        
        # Verify legs between stops
        assert "legs" in result
        assert len(result["legs"]) == 2  # 3 stops = 2 legs
        
        leg1 = result["legs"][0]
        assert "from_name" in leg1
        assert "to_name" in leg1
        assert "distance_mkm" in leg1
        assert leg1["distance_mkm"] > 0
        assert "travel_time_s" in leg1
        assert leg1["travel_time_s"] > 0
        assert "from_x" in leg1
        assert "from_y" in leg1
        assert "to_x" in leg1
        assert "to_y" in leg1
        
        # Verify totals
        assert result["total_distance_mkm"] > 0
        assert result["total_travel_time_s"] > 0
        
        # Verify QD info
        assert result["qd_size"] == 1
        assert result["qd_speed_kms"] == 165000
        
        # Verify no unresolved stores
        assert result["unresolved_stores"] == []
        
        # Verify systems and context_locations for map rendering
        assert "systems" in result
        assert "stanton" in result["systems"]
        assert "context_locations" in result
        assert len(result["context_locations"]) > 0
    
    def test_shopping_trip_single_stop(self):
        """Test single store handling (no route legs needed)"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={"store_names": ["Area 18"], "qd_size": 1}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        result = data["data"]
        assert len(result["stops"]) == 1
        assert result["stops"][0]["location_name"] == "Area 18"
        assert result["legs"] == []  # No legs for single stop
        assert result["total_distance_mkm"] == 0
        assert result["total_travel_time_s"] == 0
    
    def test_shopping_trip_unresolvable_store(self):
        """Test error handling for stores that can't be mapped to locations"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={"store_names": ["Random Unknown Store XYZ"], "qd_size": 1}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "resolve" in data["detail"].lower() or "location" in data["detail"].lower()
    
    def test_shopping_trip_mixed_resolvable_unresolvable(self):
        """Test handling mix of resolvable and unresolvable stores"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Area 18", "Unknown Store 123", "New Babbage"],
                "qd_size": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        result = data["data"]
        # Should have 2 resolvable stops
        assert len(result["stops"]) == 2
        # Should report the unresolved store
        assert "Unknown Store 123" in result["unresolved_stores"]
    
    def test_shopping_trip_fuzzy_store_name_resolution(self):
        """Test fuzzy matching of store names to locations"""
        # Test various formats that should resolve to Area 18
        test_cases = [
            "Centermass @ Area 18",
            "Centermass @ Area18",
            "Area 18",
            "area 18",
        ]
        
        for store_name in test_cases:
            response = requests.post(
                f"{BASE_URL}/api/routes/shopping_trip",
                json={"store_names": [store_name], "qd_size": 1}
            )
            assert response.status_code == 200, f"Failed for: {store_name}"
            data = response.json()
            assert data["success"] is True
            assert data["data"]["stops"][0]["location_id"] == "area18", f"Wrong location for: {store_name}"
    
    def test_shopping_trip_different_qd_sizes(self):
        """Test route calculation with different QD sizes affects travel time"""
        # Test with small QD (size 1)
        response1 = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Area 18", "New Babbage"],
                "qd_size": 1
            }
        )
        assert response1.status_code == 200
        result1 = response1.json()["data"]
        
        # Test with large QD (size 3)
        response3 = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Area 18", "New Babbage"],
                "qd_size": 3
            }
        )
        assert response3.status_code == 200
        result3 = response3.json()["data"]
        
        # Larger QD should have faster travel time (same distance)
        assert result1["total_distance_mkm"] == result3["total_distance_mkm"]
        assert result3["qd_speed_kms"] > result1["qd_speed_kms"]
        # Travel time should be shorter with faster QD
        assert result3["total_travel_time_s"] < result1["total_travel_time_s"]
    
    def test_shopping_trip_empty_store_names(self):
        """Test error handling for empty store_names list"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={"store_names": [], "qd_size": 1}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_shopping_trip_deduplication(self):
        """Test that duplicate store locations are deduplicated"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": [
                    "Centermass @ Area 18",
                    "Cubby Blast @ Area 18",  # Same location
                    "New Babbage"
                ],
                "qd_size": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        result = data["data"]
        # Should have only 2 stops (Area 18 deduplicated)
        location_ids = [s["location_id"] for s in result["stops"]]
        assert len(set(location_ids)) == len(location_ids), "Duplicate locations should be deduplicated"
    
    def test_shopping_trip_location_coordinates_for_svg(self):
        """Test that all necessary SVG rendering data is present"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={
                "store_names": ["Area 18", "New Babbage", "Lorville"],
                "qd_size": 1
            }
        )
        assert response.status_code == 200
        result = response.json()["data"]
        
        # Check stops have SVG coordinates
        for stop in result["stops"]:
            assert "map_x" in stop
            assert "map_y" in stop
            assert isinstance(stop["map_x"], (int, float))
            assert isinstance(stop["map_y"], (int, float))
        
        # Check legs have SVG coordinates
        for leg in result["legs"]:
            assert "from_x" in leg
            assert "from_y" in leg
            assert "to_x" in leg
            assert "to_y" in leg
        
        # Check context locations for background rendering
        for ctx in result["context_locations"]:
            assert "map_x" in ctx
            assert "map_y" in ctx
            assert "name" in ctx
            assert "type" in ctx


class TestShoppingTripStoreResolution:
    """Tests for store name to location resolution logic"""
    
    def test_resolve_orison(self):
        """Test Orison/Crusader resolution"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={"store_names": ["Orison"], "qd_size": 1}
        )
        assert response.status_code == 200
        assert response.json()["data"]["stops"][0]["location_id"] == "orison"
    
    def test_resolve_lorville(self):
        """Test Lorville/Hurston resolution"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={"store_names": ["Lorville"], "qd_size": 1}
        )
        assert response.status_code == 200
        assert response.json()["data"]["stops"][0]["location_id"] == "lorville"
    
    def test_resolve_grim_hex(self):
        """Test Grim HEX resolution"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={"store_names": ["Grim HEX"], "qd_size": 1}
        )
        assert response.status_code == 200
        assert response.json()["data"]["stops"][0]["location_id"] == "grim-hex"
    
    def test_resolve_port_olisar(self):
        """Test Port Olisar resolution"""
        response = requests.post(
            f"{BASE_URL}/api/routes/shopping_trip",
            json={"store_names": ["Port Olisar"], "qd_size": 1}
        )
        assert response.status_code == 200
        assert response.json()["data"]["stops"][0]["location_id"] == "port-olisar"
    
    def test_resolve_orbital_stations(self):
        """Test orbital station resolution"""
        stations = [
            ("Everus Harbor", "everus-harbor"),
            ("Baijini Point", "baijini-point"),
            ("Port Tressler", "port-tressler"),
        ]
        for store_name, expected_id in stations:
            response = requests.post(
                f"{BASE_URL}/api/routes/shopping_trip",
                json={"store_names": [store_name], "qd_size": 1}
            )
            assert response.status_code == 200, f"Failed for: {store_name}"
            assert response.json()["data"]["stops"][0]["location_id"] == expected_id


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
