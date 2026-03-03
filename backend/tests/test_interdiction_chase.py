"""
Interdiction and Chase API Tests - Iteration 9
Tests for POST /api/routes/interdiction and POST /api/routes/chase endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# QD Speeds reference from star_systems.py
QD_SPEEDS = {
    0: 100_000,   # Snub / no QD
    1: 165_000,   # Small
    2: 190_000,   # Medium  
    3: 240_000,   # Large
}


class TestInterdictionAPI:
    """Tests for POST /api/routes/interdiction endpoint - QED Snare Planning"""

    def test_interdiction_single_origin_full_coverage(self):
        """Single origin to destination should give 100% coverage"""
        response = requests.post(
            f"{BASE_URL}/api/routes/interdiction",
            json={
                "origins": ["hurston"],
                "destination": "microtech",
                "snare_range_mkm": 7.5
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        result = data["data"]
        
        # Validate response structure
        assert "snare_position" in result
        assert "x" in result["snare_position"]
        assert "y" in result["snare_position"]
        assert "coverage_pct" in result
        assert "routes_covered" in result
        assert "routes_total" in result
        assert "route_lines" in result
        assert "destination" in result
        
        # Single origin should have 100% coverage
        assert result["coverage_pct"] == 100
        assert result["routes_covered"] == 1
        assert result["routes_total"] == 1

    def test_interdiction_multiple_origins_full_coverage(self):
        """Multiple origins converging on destination with good snare range"""
        response = requests.post(
            f"{BASE_URL}/api/routes/interdiction",
            json={
                "origins": ["hurston", "arccorp", "crusader"],
                "destination": "microtech",
                "snare_range_mkm": 10.0  # Larger range for better coverage
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        result = data["data"]
        
        # Should have 3 routes
        assert result["routes_total"] == 3
        
        # Validate route lines
        assert len(result["route_lines"]) == 3
        for route_line in result["route_lines"]:
            assert "from" in route_line
            assert "from_id" in route_line
            assert "sx" in route_line
            assert "sy" in route_line
            assert "ex" in route_line
            assert "ey" in route_line

    def test_interdiction_snare_range_affects_coverage(self):
        """Smaller snare range may result in partial coverage"""
        # Test with small range
        response_small = requests.post(
            f"{BASE_URL}/api/routes/interdiction",
            json={
                "origins": ["hurston", "arccorp", "crusader"],
                "destination": "microtech",
                "snare_range_mkm": 2.0  # Very small range
            }
        )
        assert response_small.status_code == 200
        result_small = response_small.json()["data"]
        
        # Test with large range
        response_large = requests.post(
            f"{BASE_URL}/api/routes/interdiction",
            json={
                "origins": ["hurston", "arccorp", "crusader"],
                "destination": "microtech",
                "snare_range_mkm": 15.0  # Large range
            }
        )
        assert response_large.status_code == 200
        result_large = response_large.json()["data"]
        
        # Larger range should have equal or better coverage
        assert result_large["coverage_pct"] >= result_small["coverage_pct"]

    def test_interdiction_invalid_destination(self):
        """Error when destination doesn't exist"""
        response = requests.post(
            f"{BASE_URL}/api/routes/interdiction",
            json={
                "origins": ["hurston"],
                "destination": "invalid-location",
                "snare_range_mkm": 7.5
            }
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_interdiction_no_valid_origins(self):
        """Error when no valid origins provided"""
        response = requests.post(
            f"{BASE_URL}/api/routes/interdiction",
            json={
                "origins": ["invalid-origin1", "invalid-origin2"],
                "destination": "microtech",
                "snare_range_mkm": 7.5
            }
        )
        assert response.status_code == 400
        assert "origin" in response.json()["detail"].lower()

    def test_interdiction_empty_origins(self):
        """Error when origins list is empty"""
        response = requests.post(
            f"{BASE_URL}/api/routes/interdiction",
            json={
                "origins": [],
                "destination": "microtech",
                "snare_range_mkm": 7.5
            }
        )
        assert response.status_code == 400

    def test_interdiction_returns_snare_position_info(self):
        """Snare position includes distance to destination on full coverage"""
        response = requests.post(
            f"{BASE_URL}/api/routes/interdiction",
            json={
                "origins": ["hurston"],
                "destination": "microtech",
                "snare_range_mkm": 7.5
            }
        )
        assert response.status_code == 200
        result = response.json()["data"]
        
        if result.get("success", True) and result["coverage_pct"] == 100:
            assert "distance_to_dest_mkm" in result
            assert result["distance_to_dest_mkm"] > 0

    def test_interdiction_cross_system_routes(self):
        """Interdiction with cross-system origin uses gateway entry point"""
        response = requests.post(
            f"{BASE_URL}/api/routes/interdiction",
            json={
                "origins": ["pyro-iii"],  # Pyro system
                "destination": "microtech",  # Stanton system
                "snare_range_mkm": 10.0
            }
        )
        assert response.status_code == 200
        result = response.json()["data"]
        
        # Cross-system route should use gateway as entry point
        # The route line should show the gateway entry in destination system
        assert result["routes_total"] >= 1


class TestChaseAPI:
    """Tests for POST /api/routes/chase endpoint - QD Chase Calculator"""

    def test_chase_faster_ship_can_catch(self):
        """S2 QD chasing S1 QD can catch target"""
        response = requests.post(
            f"{BASE_URL}/api/routes/chase",
            json={
                "your_qd_size": 2,
                "target_qd_size": 1,
                "distance_mkm": 10,
                "prep_time_seconds": 30
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        result = data["data"]
        
        # Validate response structure
        assert "can_catch" in result
        assert "your_speed_kms" in result
        assert "target_speed_kms" in result
        assert "speed_advantage_kms" in result
        assert "verdict" in result
        
        # S2 (190k) vs S1 (165k) - can catch
        assert result["can_catch"] is True
        assert result["your_speed_kms"] == 190_000
        assert result["target_speed_kms"] == 165_000
        assert result["speed_advantage_kms"] == 25_000  # 190k - 165k
        
        # Should have closing time info
        assert "closing_time_seconds" in result
        assert result["closing_time_seconds"] > 0
        assert "total_time_seconds" in result
        assert result["total_time_seconds"] > 0

    def test_chase_slower_ship_cannot_catch(self):
        """S1 QD chasing S2 QD cannot catch target"""
        response = requests.post(
            f"{BASE_URL}/api/routes/chase",
            json={
                "your_qd_size": 1,
                "target_qd_size": 2,
                "distance_mkm": 10,
                "prep_time_seconds": 30
            }
        )
        assert response.status_code == 200
        
        result = response.json()["data"]
        
        # S1 (165k) vs S2 (190k) - cannot catch
        assert result["can_catch"] is False
        assert result["your_speed_kms"] == 165_000
        assert result["target_speed_kms"] == 190_000
        assert result["speed_advantage_kms"] == -25_000  # Negative = disadvantage
        
        # Verdict should mention cannot catch
        assert "cannot" in result["verdict"].lower() or "can't" in result["verdict"].lower()

    def test_chase_same_speed_cannot_catch(self):
        """Same QD size cannot close the gap"""
        response = requests.post(
            f"{BASE_URL}/api/routes/chase",
            json={
                "your_qd_size": 2,
                "target_qd_size": 2,
                "distance_mkm": 10,
                "prep_time_seconds": 30
            }
        )
        assert response.status_code == 200
        
        result = response.json()["data"]
        
        # Same speed - cannot catch
        assert result["can_catch"] is False
        assert result["your_speed_kms"] == result["target_speed_kms"]
        assert result["speed_advantage_kms"] == 0
        
        # Verdict should mention same speed
        assert "same" in result["verdict"].lower()

    def test_chase_s3_vs_s1_fastest_catch(self):
        """S3 QD chasing S1 QD - maximum speed advantage"""
        response = requests.post(
            f"{BASE_URL}/api/routes/chase",
            json={
                "your_qd_size": 3,
                "target_qd_size": 1,
                "distance_mkm": 10,
                "prep_time_seconds": 30
            }
        )
        assert response.status_code == 200
        
        result = response.json()["data"]
        
        # S3 (240k) vs S1 (165k) - can catch
        assert result["can_catch"] is True
        assert result["your_speed_kms"] == 240_000
        assert result["target_speed_kms"] == 165_000
        assert result["speed_advantage_kms"] == 75_000  # 240k - 165k

    def test_chase_prep_time_affects_total_time(self):
        """Different prep times affect total catch time"""
        # Short prep time
        response_short = requests.post(
            f"{BASE_URL}/api/routes/chase",
            json={
                "your_qd_size": 2,
                "target_qd_size": 1,
                "distance_mkm": 10,
                "prep_time_seconds": 10
            }
        )
        assert response_short.status_code == 200
        result_short = response_short.json()["data"]
        
        # Long prep time
        response_long = requests.post(
            f"{BASE_URL}/api/routes/chase",
            json={
                "your_qd_size": 2,
                "target_qd_size": 1,
                "distance_mkm": 10,
                "prep_time_seconds": 60
            }
        )
        assert response_long.status_code == 200
        result_long = response_long.json()["data"]
        
        # Both can catch, but longer prep = more total time
        assert result_short["can_catch"] is True
        assert result_long["can_catch"] is True
        assert result_long["total_time_seconds"] > result_short["total_time_seconds"]

    def test_chase_distance_affects_time(self):
        """Larger distance takes longer to close"""
        # Short distance
        response_short = requests.post(
            f"{BASE_URL}/api/routes/chase",
            json={
                "your_qd_size": 2,
                "target_qd_size": 1,
                "distance_mkm": 5,
                "prep_time_seconds": 30
            }
        )
        assert response_short.status_code == 200
        result_short = response_short.json()["data"]
        
        # Long distance
        response_long = requests.post(
            f"{BASE_URL}/api/routes/chase",
            json={
                "your_qd_size": 2,
                "target_qd_size": 1,
                "distance_mkm": 50,
                "prep_time_seconds": 30
            }
        )
        assert response_long.status_code == 200
        result_long = response_long.json()["data"]
        
        # Both can catch, but longer distance = more time
        assert result_short["can_catch"] is True
        assert result_long["can_catch"] is True
        assert result_long["closing_time_seconds"] > result_short["closing_time_seconds"]

    def test_chase_verdict_text_content(self):
        """Verdict text contains useful information"""
        # Catchable scenario
        response = requests.post(
            f"{BASE_URL}/api/routes/chase",
            json={
                "your_qd_size": 2,
                "target_qd_size": 1,
                "distance_mkm": 10,
                "prep_time_seconds": 30
            }
        )
        result = response.json()["data"]
        
        # Verdict should mention time and speed advantage
        verdict = result["verdict"]
        assert "catch" in verdict.lower()
        assert "km/s" in verdict.lower() or "faster" in verdict.lower()

    def test_chase_all_qd_sizes_valid(self):
        """All QD sizes (1, 2, 3) work correctly"""
        for qd_size in [1, 2, 3]:
            response = requests.post(
                f"{BASE_URL}/api/routes/chase",
                json={
                    "your_qd_size": qd_size,
                    "target_qd_size": 1,
                    "distance_mkm": 10,
                    "prep_time_seconds": 30
                }
            )
            assert response.status_code == 200
            result = response.json()["data"]
            assert result["your_speed_kms"] == QD_SPEEDS[qd_size]
