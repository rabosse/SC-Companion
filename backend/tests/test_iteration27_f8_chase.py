"""
Iteration 27: F8 Lightning Hardpoints Fix & Chase Planner Enhancement Tests

Tests:
1. F8C Lightning has weapons=[3,3,3,3,2,2,2,2] (8 weapons), shield_size=2, shield_count=2, power_size=2
2. F8A Lightning has weapons=[4,4,3,3,3,3,3,3] (8 weapons), shield_size=2, shield_count=2, power_size=2
3. POST /api/routes/chase/advanced - location-aware pursuit planner with escape route analysis
4. POST /api/routes/chase (legacy) - still works correctly
"""

import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestF8LightningHardpoints:
    """Test F8 Lightning variants have correct hardpoint configurations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for ships API"""
        # Register/login to get token
        register_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": "f8test27",
            "password": "password123"
        })
        if register_resp.status_code == 400:  # Already exists
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "f8test27",
                "password": "password123"
            })
            self.token = login_resp.json().get("access_token")
        else:
            self.token = register_resp.json().get("access_token")
        
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_f8c_lightning_has_8_weapons(self):
        """F8C Lightning should have 8 weapon hardpoints: [3,3,3,3,2,2,2,2]"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=self.headers)
        assert response.status_code == 200
        
        ships = response.json().get("data", [])
        f8c_ships = [s for s in ships if "f8c lightning" in s.get("name", "").lower() 
                     and "executive" not in s.get("name", "").lower()]
        
        assert len(f8c_ships) > 0, "F8C Lightning not found in ships list"
        
        f8c = f8c_ships[0]
        hardpoints = f8c.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        
        # Verify 8 weapon slots
        assert len(weapons) == 8, f"F8C should have 8 weapons, got {len(weapons)}"
        
        # Verify weapon sizes: [3,3,3,3,2,2,2,2]
        expected_weapons = [3, 3, 3, 3, 2, 2, 2, 2]
        assert sorted(weapons) == sorted(expected_weapons), f"F8C weapons should be {expected_weapons}, got {weapons}"
        
        # Verify shield configuration
        shield = hardpoints.get("shield", {})
        assert shield.get("size") == 2, f"F8C shield size should be 2, got {shield.get('size')}"
        assert shield.get("count") == 2, f"F8C shield count should be 2, got {shield.get('count')}"
        
        # Verify power plant
        power = hardpoints.get("power_plant", {})
        assert power.get("size") == 2, f"F8C power size should be 2, got {power.get('size')}"
        
        print(f"F8C Lightning verified: {len(weapons)} weapons, shield S{shield.get('size')}x{shield.get('count')}")

    def test_f8a_lightning_has_8_weapons(self):
        """F8A Lightning should have 8 weapon hardpoints: [4,4,3,3,3,3,3,3]"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=self.headers)
        assert response.status_code == 200
        
        ships = response.json().get("data", [])
        f8a_ships = [s for s in ships if "f8a lightning" in s.get("name", "").lower()]
        
        assert len(f8a_ships) > 0, "F8A Lightning not found in ships list"
        
        f8a = f8a_ships[0]
        hardpoints = f8a.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        
        # Verify 8 weapon slots
        assert len(weapons) == 8, f"F8A should have 8 weapons, got {len(weapons)}"
        
        # Verify weapon sizes: [4,4,3,3,3,3,3,3]
        expected_weapons = [4, 4, 3, 3, 3, 3, 3, 3]
        assert sorted(weapons) == sorted(expected_weapons), f"F8A weapons should be {expected_weapons}, got {weapons}"
        
        # Verify shield configuration
        shield = hardpoints.get("shield", {})
        assert shield.get("size") == 2, f"F8A shield size should be 2, got {shield.get('size')}"
        assert shield.get("count") == 2, f"F8A shield count should be 2, got {shield.get('count')}"
        
        # Verify power plant
        power = hardpoints.get("power_plant", {})
        assert power.get("size") == 2, f"F8A power size should be 2, got {power.get('size')}"
        
        print(f"F8A Lightning verified: {len(weapons)} weapons, shield S{shield.get('size')}x{shield.get('count')}")

    def test_f8_base_lightning_has_8_weapons(self):
        """F8 Lightning (base) should have 8 weapon hardpoints: [4,4,3,3,3,3,3,3]"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=self.headers)
        assert response.status_code == 200
        
        ships = response.json().get("data", [])
        # Find base F8 Lightning (not F8A or F8C)
        f8_ships = [s for s in ships if s.get("name", "").lower() == "f8 lightning"]
        
        if len(f8_ships) == 0:
            pytest.skip("Base F8 Lightning not found in API - may not exist in wiki data")
        
        f8 = f8_ships[0]
        hardpoints = f8.get("hardpoints", {})
        weapons = hardpoints.get("weapons", [])
        
        assert len(weapons) == 8, f"F8 should have 8 weapons, got {len(weapons)}"
        print(f"F8 Lightning (base) verified: {len(weapons)} weapons")


class TestChaseAdvancedEndpoint:
    """Test the new /api/routes/chase/advanced endpoint"""
    
    def test_chase_advanced_grim_hex_to_orison(self):
        """Chase from Grim HEX to target at Orison"""
        response = requests.post(f"{BASE_URL}/api/routes/chase/advanced", json={
            "your_position": "grim-hex",
            "target_position": "orison",
            "your_qd_size": 2,
            "target_qd_size": 1,
            "prep_time_seconds": 30
        })
        
        assert response.status_code == 200, f"Chase advanced failed: {response.text}"
        data = response.json().get("data", {})
        
        # Verify response structure
        assert "escape_destinations" in data, "Missing escape_destinations"
        assert "threat_level" in data, "Missing threat_level"
        assert "intercept_pct" in data, "Missing intercept_pct"
        assert "best_pursuit" in data, "Missing best_pursuit"
        assert "tactical_notes" in data, "Missing tactical_notes"
        assert "chase_lines" in data, "Missing chase_lines"
        
        # Verify position info
        assert data.get("your_position", {}).get("id") == "grim-hex"
        assert data.get("target_position", {}).get("id") == "orison"
        
        # Verify speeds
        assert data.get("your_speed_kms") > 0
        assert data.get("target_speed_kms") > 0
        assert data.get("speed_diff_kms") > 0  # S2 is faster than S1
        
        # Verify escape destinations list
        escape_dests = data.get("escape_destinations", [])
        assert len(escape_dests) > 0, "Should have escape destinations"
        for dest in escape_dests:
            assert "id" in dest
            assert "name" in dest
            assert "can_intercept" in dest
            assert "target_distance_mkm" in dest
            assert "your_distance_mkm" in dest
            assert "time_margin_s" in dest
        
        print(f"Chase advanced result: threat={data.get('threat_level')}, intercept={data.get('intercept_pct')}%")
        print(f"Escape destinations: {len(escape_dests)}")
        if data.get("best_pursuit"):
            print(f"Best pursuit: {data['best_pursuit'].get('name')}")

    def test_chase_advanced_inverted_qd_advantage(self):
        """Test chase where target has faster QD (S3 vs S1) - should show higher threat"""
        response = requests.post(f"{BASE_URL}/api/routes/chase/advanced", json={
            "your_position": "grim-hex",
            "target_position": "orison",
            "your_qd_size": 1,  # Your slow QD
            "target_qd_size": 3,  # Target fast QD
            "prep_time_seconds": 30
        })
        
        assert response.status_code == 200, f"Chase advanced failed: {response.text}"
        data = response.json().get("data", {})
        
        # When target is faster, threat should be higher
        threat_level = data.get("threat_level", "")
        assert threat_level in ["high", "critical"], f"Expected high/critical threat when target is faster, got {threat_level}"
        
        # Speed diff should be negative (you're slower)
        speed_diff = data.get("speed_diff_kms", 0)
        assert speed_diff < 0, f"Speed diff should be negative when target is faster, got {speed_diff}"
        
        # Intercept percentage should be lower
        intercept_pct = data.get("intercept_pct", 100)
        assert intercept_pct < 100, f"Should not have 100% intercept when target is faster, got {intercept_pct}%"
        
        print(f"Inverted QD test: threat={threat_level}, intercept={intercept_pct}%, speed_diff={speed_diff}")

    def test_chase_advanced_invalid_position_returns_400(self):
        """Invalid position should return 400 error"""
        response = requests.post(f"{BASE_URL}/api/routes/chase/advanced", json={
            "your_position": "invalid-location-xyz",
            "target_position": "orison",
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        
        assert response.status_code == 400, f"Expected 400 for invalid position, got {response.status_code}"
        print("Invalid position correctly returns 400")

    def test_chase_advanced_invalid_target_returns_400(self):
        """Invalid target position should return 400 error"""
        response = requests.post(f"{BASE_URL}/api/routes/chase/advanced", json={
            "your_position": "grim-hex",
            "target_position": "fake-location-abc",
            "your_qd_size": 2,
            "target_qd_size": 1
        })
        
        assert response.status_code == 400, f"Expected 400 for invalid target, got {response.status_code}"
        print("Invalid target correctly returns 400")


class TestChaseLegacyEndpoint:
    """Test the legacy /api/routes/chase endpoint still works"""
    
    def test_legacy_chase_faster_qd_catches_target(self):
        """Legacy chase: faster QD should catch target"""
        response = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 3,
            "target_qd_size": 1,
            "distance_mkm": 10.0,
            "prep_time_seconds": 30
        })
        
        assert response.status_code == 200, f"Legacy chase failed: {response.text}"
        data = response.json().get("data", {})
        
        assert data.get("can_catch") is True, "Should be able to catch with faster QD"
        assert data.get("speed_advantage_kms", 0) > 0
        print(f"Legacy chase (faster): can_catch={data.get('can_catch')}, time={data.get('total_time_seconds')}s")

    def test_legacy_chase_slower_qd_cannot_catch(self):
        """Legacy chase: slower QD cannot catch target"""
        response = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 1,
            "target_qd_size": 3,
            "distance_mkm": 10.0,
            "prep_time_seconds": 30
        })
        
        assert response.status_code == 200, f"Legacy chase failed: {response.text}"
        data = response.json().get("data", {})
        
        assert data.get("can_catch") is False, "Should not catch with slower QD"
        assert data.get("speed_advantage_kms", 0) < 0
        print(f"Legacy chase (slower): can_catch={data.get('can_catch')}")

    def test_legacy_chase_same_speed_cannot_catch(self):
        """Legacy chase: same speed cannot catch target"""
        response = requests.post(f"{BASE_URL}/api/routes/chase", json={
            "your_qd_size": 2,
            "target_qd_size": 2,
            "distance_mkm": 10.0,
            "prep_time_seconds": 30
        })
        
        assert response.status_code == 200, f"Legacy chase failed: {response.text}"
        data = response.json().get("data", {})
        
        assert data.get("can_catch") is False, "Should not catch with same QD speed"
        assert data.get("speed_advantage_kms") == 0
        print(f"Legacy chase (same): can_catch={data.get('can_catch')}")


class TestRoutesLocationsEndpoint:
    """Verify routes/locations endpoint still works"""
    
    def test_locations_returns_data(self):
        """GET /api/routes/locations returns locations and QD data"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        assert len(data.get("data", [])) > 0
        assert "systems" in data
        assert "qd_speeds" in data
        assert "qd_fuel" in data
        
        # Verify grim-hex and orison exist for chase tests
        locations = data.get("data", [])
        loc_ids = [l.get("id") for l in locations]
        assert "grim-hex" in loc_ids, "grim-hex location not found"
        assert "orison" in loc_ids, "orison location not found"
        
        print(f"Locations endpoint: {len(locations)} locations, systems: {list(data.get('systems', {}).keys())}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
