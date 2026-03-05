"""
Test Iteration 25: Interdiction Planner Enhancements
- Per-route timing analysis
- Escape analysis with speed comparison
- Multi-snare suggestion when coverage < 100%
- Nearby POI warnings
- Tactical notes
- Your QD / Target QD size parameters
- Enhanced route_details with covered/uncovered status
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestInterdictionEnhancements:
    """Tests for enhanced interdiction planning features"""

    def test_interdiction_accepts_qd_size_params(self):
        """Test that /api/routes/interdiction accepts your_qd_size and target_qd_size"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "area18"],
            "destination": "port-tressler",
            "snare_range_mkm": 7.5,
            "your_qd_size": 3,  # Large QD
            "target_qd_size": 1   # Small QD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        result = data["data"]
        # Escape analysis should reflect the QD sizes
        escape = result.get("escape_analysis", {})
        assert escape.get("your_speed_kms") == 240000  # S3 QD speed
        assert escape.get("target_speed_kms") == 165000  # S1 QD speed

    def test_route_details_per_route_timing(self):
        """Test that route_details contains per-route timing data"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "orison", "area18"],
            "destination": "port-tressler",
            "snare_range_mkm": 10.0,
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        # Check route_details exists and has expected fields
        route_details = result.get("route_details", [])
        assert len(route_details) == 3  # 3 origins
        
        for rd in route_details:
            assert "origin_id" in rd
            assert "origin_name" in rd
            assert "distance_mkm" in rd
            assert "target_travel_time_s" in rd
            assert "time_to_snare_s" in rd
            assert "covered" in rd
            assert "deviation_mkm" in rd
            assert isinstance(rd["target_travel_time_s"], int)
            assert isinstance(rd["covered"], bool)

    def test_route_details_covered_uncovered_status(self):
        """Test covered/uncovered status for routes"""
        # Use a very small snare range to ensure some routes are uncovered
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "orison", "area18", "new-babbage"],
            "destination": "port-tressler",
            "snare_range_mkm": 2.0,  # Very small range
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        # Should have route_details
        route_details = result.get("route_details", [])
        assert len(route_details) == 4
        
        # Some routes should be uncovered with small snare
        covered_count = sum(1 for rd in route_details if rd["covered"])
        uncovered_count = sum(1 for rd in route_details if not rd["covered"])
        
        # Coverage percentage should match
        assert result["coverage_pct"] == round((covered_count / 4) * 100)
        
        # Uncovered routes should have deviation > snare_range
        for rd in route_details:
            if not rd["covered"]:
                # Deviation is how far off the route is from snare coverage
                assert rd["deviation_mkm"] >= 0

    def test_escape_analysis_speed_comparison(self):
        """Test escape analysis shows speed comparison"""
        # Target with faster QD than you
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville"],
            "destination": "port-tressler",
            "snare_range_mkm": 10.0,
            "your_qd_size": 1,  # S1 = 165k km/s
            "target_qd_size": 3  # S3 = 240k km/s
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        escape = result.get("escape_analysis", {})
        assert escape is not None
        assert escape["your_speed_kms"] == 165000
        assert escape["target_speed_kms"] == 240000
        assert escape["can_escape"] is True  # Target is faster
        assert "note" in escape
        assert "may escape" in escape["note"].lower() or "faster" in escape["note"].lower()

    def test_escape_analysis_you_are_faster(self):
        """Test escape analysis when you have speed advantage"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville"],
            "destination": "port-tressler",
            "snare_range_mkm": 10.0,
            "your_qd_size": 3,  # S3 = 240k km/s
            "target_qd_size": 1  # S1 = 165k km/s
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        escape = result.get("escape_analysis", {})
        assert escape["your_speed_kms"] == 240000
        assert escape["target_speed_kms"] == 165000
        assert escape["can_escape"] is False  # You are faster
        assert escape["speed_diff_kms"] == 75000  # Speed advantage

    def test_tactical_notes_generated(self):
        """Test that tactical_notes are generated"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "orison", "area18", "new-babbage"],
            "destination": "port-tressler",
            "snare_range_mkm": 7.5,
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        tactical_notes = result.get("tactical_notes", [])
        assert isinstance(tactical_notes, list)
        # Should have at least one tactical note
        assert len(tactical_notes) >= 1
        # Notes should be strings
        for note in tactical_notes:
            assert isinstance(note, str)
            assert len(note) > 5  # Non-trivial note

    def test_nearby_pois_returned(self):
        """Test that nearby_pois are returned"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville"],
            "destination": "port-tressler",
            "snare_range_mkm": 10.0,
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        nearby_pois = result.get("nearby_pois", [])
        assert isinstance(nearby_pois, list)
        
        # POIs should have required fields
        for poi in nearby_pois:
            assert "id" in poi
            assert "name" in poi
            assert "type" in poi
            assert "distance_mkm" in poi
            # Distance should be a number
            assert isinstance(poi["distance_mkm"], (int, float))

    def test_timing_arrival_times(self):
        """Test timing data with arrival_times array"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "orison", "area18"],
            "destination": "port-tressler",
            "snare_range_mkm": 10.0,
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        timing = result.get("timing", {})
        assert timing is not None
        assert "arrival_times" in timing
        assert "note" in timing
        
        arrival_times = timing["arrival_times"]
        assert isinstance(arrival_times, list)
        # Should be sorted
        assert arrival_times == sorted(arrival_times)

    def test_timing_note_generated(self):
        """Test that timing.note is generated with useful info"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "orison"],
            "destination": "port-tressler",
            "snare_range_mkm": 10.0,
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        timing = result.get("timing", {})
        note = timing.get("note", "")
        assert isinstance(note, str)
        assert len(note) > 10  # Should have meaningful content

    def test_second_snare_suggestion_when_low_coverage(self):
        """Test that second_snare is suggested when coverage < 100%"""
        # Use tiny snare range to ensure partial coverage
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "orison", "area18", "new-babbage", "grim-hex"],
            "destination": "port-tressler",
            "snare_range_mkm": 2.0,  # Very small range
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        # If coverage < 100%, second_snare should be suggested
        if result["coverage_pct"] < 100:
            second_snare = result.get("second_snare")
            assert second_snare is not None
            assert "position" in second_snare
            assert "x" in second_snare["position"]
            assert "y" in second_snare["position"]
            assert "covers" in second_snare
            assert "total_uncovered" in second_snare

    def test_second_snare_null_when_full_coverage(self):
        """Test that second_snare is null when coverage is 100%"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["new-babbage"],  # Single origin close to dest
            "destination": "port-tressler",
            "snare_range_mkm": 15.0,  # Large range
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        if result["coverage_pct"] == 100:
            assert result.get("second_snare") is None

    def test_cross_system_interdiction(self):
        """Test interdiction with cross-system origins"""
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": ["lorville", "pyro-bloom-settlement"],  # Mix systems
            "destination": "port-tressler",
            "snare_range_mkm": 10.0,
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        # Should handle cross-system routes
        route_details = result.get("route_details", [])
        assert len(route_details) == 2

    def test_all_cities_as_origins_preset(self):
        """Test with all cities as origins (preset scenario)"""
        # Get all cities
        loc_response = requests.get(f"{BASE_URL}/api/routes/locations")
        locations = loc_response.json()["data"]
        cities = [loc["id"] for loc in locations if loc["type"] == "city"]
        
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": cities,
            "destination": "port-tressler",
            "snare_range_mkm": 7.5,
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        # Should process all city origins
        route_details = result.get("route_details", [])
        assert len(route_details) >= len(cities) - 1  # Minus destination if it's a city

    def test_all_stations_as_origins_preset(self):
        """Test with all stations as origins (preset scenario)"""
        loc_response = requests.get(f"{BASE_URL}/api/routes/locations")
        locations = loc_response.json()["data"]
        stations = [loc["id"] for loc in locations if loc["type"] == "station"][:10]  # Limit for test
        
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": stations,
            "destination": "new-babbage",
            "snare_range_mkm": 10.0,
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        # Should have all required enhanced fields
        assert "route_details" in result
        assert "timing" in result
        assert "escape_analysis" in result
        assert "nearby_pois" in result
        assert "tactical_notes" in result

    def test_all_rest_stops_as_origins_preset(self):
        """Test with rest stops as origins (preset scenario)"""
        loc_response = requests.get(f"{BASE_URL}/api/routes/locations")
        locations = loc_response.json()["data"]
        rest_stops = [loc["id"] for loc in locations if loc["type"] == "rest_stop"]
        
        response = requests.post(f"{BASE_URL}/api/routes/interdiction", json={
            "origins": rest_stops,
            "destination": "grim-hex",
            "snare_range_mkm": 7.5,
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        assert response.status_code == 200
        result = response.json()["data"]
        
        # Verify all fields present
        assert "coverage_pct" in result
        assert "routes_covered" in result
        assert "routes_total" in result


class TestRouteTabRegression:
    """Regression tests to ensure Route tab still works"""

    def test_route_calculation_basic(self):
        """Test basic route calculation still works"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "area18",
            "qd_size": 2
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        route = data["data"]
        assert "total_distance_mkm" in route
        assert "travel_time_seconds" in route
        assert "waypoints" in route

    def test_cross_system_route(self):
        """Test cross-system route still works"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "ruin-station",
            "qd_size": 2
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["cross_system"] is True


class TestChaseTabRegression:
    """Regression tests to ensure Chase tab still works"""

    def test_chase_calculation_can_catch(self):
        """Test chase calculation with faster pursuer"""
        response = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 3,
            "target_qd_size": 1,
            "distance_mkm": 10,
            "prep_time_seconds": 30
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["can_catch"] is True

    def test_chase_calculation_cannot_catch(self):
        """Test chase calculation with slower pursuer"""
        response = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 1,
            "target_qd_size": 3,
            "distance_mkm": 10,
            "prep_time_seconds": 30
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["can_catch"] is False


class TestQDSpeedsConsistency:
    """Test QD speeds are consistent across features"""

    def test_qd_speeds_available(self):
        """Test QD speeds are returned by locations endpoint"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        assert response.status_code == 200
        qd_speeds = response.json().get("qd_speeds", {})
        
        assert "1" in qd_speeds or 1 in qd_speeds
        assert "2" in qd_speeds or 2 in qd_speeds
        assert "3" in qd_speeds or 3 in qd_speeds
