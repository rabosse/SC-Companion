"""
Iteration 43: Test shopping route planner improvements
- Gate jumps are avoided unless necessary (GATE_JUMP_PENALTY = 200 Mkm)
- Same-system stores are visited first before jumping to another system
- Legs include 'type' field ('quantum' or 'jump')
- Cross-system routes broken into quantum→jump→quantum sub-legs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test store names (as specified in review request)
STANTON_STORES = [
    'Stanton - Hurston - Lorville - Workers District - Tammany And Sons',
    'Stanton - ArcCorp - Area18 - Plaza - Centermass',
    'Stanton - microTech - New Babbage - The Commons - Plaza - Centermass'
]
PYRO_STORE = 'Pyro - Ruin Station - Marketplace - Guns'


class TestShoppingRouteGateJumpPenalty:
    """
    Tests that shopping route planner avoids gate jumps unless necessary.
    Gate jumps should only occur after all same-system stops are exhausted.
    """
    
    def test_stanton_origin_visits_stanton_stores_first(self):
        """
        BACKEND: POST /api/routes/shopping_trip with stores in Stanton + Pyro 
        and origin in Stanton — verify all Stanton stores are visited before jumping to Pyro
        """
        # All 3 Stanton stores + 1 Pyro store, origin in Lorville (Stanton)
        payload = {
            "store_names": STANTON_STORES + [PYRO_STORE],
            "qd_size": 1,
            "origin_id": "lorville"  # Stanton system
        }
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success"), f"Expected success=True: {data}"
        
        route = data.get("data", {})
        legs = route.get("legs", [])
        stops = route.get("stops", [])
        
        # Verify we have legs and stops
        assert len(legs) > 0, "Expected route to have legs"
        assert len(stops) > 0, "Expected route to have stops"
        
        # Find the index of the first jump leg (gate jump to Pyro)
        first_jump_idx = None
        for i, leg in enumerate(legs):
            if leg.get("type") == "jump":
                first_jump_idx = i
                break
        
        # If there's a jump, all Stanton stops should be visited before it
        if first_jump_idx is not None:
            # Get location IDs of stops before the jump
            stanton_stop_count = 0
            for stop in stops:
                if stop.get("system") == "stanton":
                    stanton_stop_count += 1
            
            # Count quantum legs before the jump - these should cover Stanton stores
            quantum_legs_before_jump = sum(1 for leg in legs[:first_jump_idx] if leg.get("type") == "quantum")
            
            print(f"Stanton stops: {stanton_stop_count}")
            print(f"Quantum legs before first jump: {quantum_legs_before_jump}")
            print(f"First jump at leg index: {first_jump_idx}")
            
            # Verify all 3 Stanton stores are visited before the jump
            assert quantum_legs_before_jump >= stanton_stop_count - 1, \
                f"Expected to visit all Stanton stores before jumping. Got {quantum_legs_before_jump} quantum legs before jump"
    
    def test_pyro_origin_visits_pyro_stores_first(self):
        """
        BACKEND: POST /api/routes/shopping_trip with origin in Pyro and stores 
        in both systems — verify Pyro stores visited first
        """
        payload = {
            "store_names": STANTON_STORES[:2] + [PYRO_STORE],  # 2 Stanton + 1 Pyro
            "qd_size": 1,
            "origin_id": "ruin-station"  # Pyro system
        }
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success"), f"Expected success=True: {data}"
        
        route = data.get("data", {})
        stops = route.get("stops", [])
        legs = route.get("legs", [])
        origin = route.get("origin", {})
        
        # Origin should be in Pyro
        assert origin.get("system") == "pyro", f"Expected origin in pyro, got {origin.get('system')}"
        
        # First stop(s) should be Pyro stores before jumping to Stanton
        # Find the first jump leg
        first_jump_idx = None
        for i, leg in enumerate(legs):
            if leg.get("type") == "jump":
                first_jump_idx = i
                break
        
        if first_jump_idx is not None:
            # Count Pyro stops - they should all come before the jump
            pyro_stops = [s for s in stops if s.get("system") == "pyro"]
            
            # The algorithm should visit Pyro store (Ruin Station) before jumping
            print(f"Pyro stops: {len(pyro_stops)}")
            print(f"First jump index: {first_jump_idx}")
            
            # With origin at Ruin Station and Pyro store at Ruin Station,
            # the Pyro store should be the first stop
            if len(pyro_stops) > 0:
                first_stop = stops[0]
                print(f"First stop: {first_stop.get('location_name')} in {first_stop.get('system')}")
                # First stop should be in Pyro if there's a Pyro store
                assert first_stop.get("system") == "pyro", \
                    f"Expected first stop in Pyro when origin is Pyro. Got {first_stop.get('system')}"
    
    def test_same_system_no_gate_jumps(self):
        """
        BACKEND: POST /api/routes/shopping_trip with all stores in same system 
        — verify no gate jumps in legs
        """
        payload = {
            "store_names": STANTON_STORES,  # All 3 Stanton stores
            "qd_size": 1,
            "origin_id": "lorville"  # Also in Stanton
        }
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success"), f"Expected success=True: {data}"
        
        route = data.get("data", {})
        legs = route.get("legs", [])
        
        # No legs should have type='jump' for same-system route
        jump_legs = [leg for leg in legs if leg.get("type") == "jump"]
        assert len(jump_legs) == 0, \
            f"Expected no jump legs for same-system route, found {len(jump_legs)}: {jump_legs}"
        
        # All legs should be quantum
        for leg in legs:
            assert leg.get("type") == "quantum", \
                f"Expected all legs to be 'quantum' for same-system route, found: {leg.get('type')}"
    
    def test_legs_have_type_field(self):
        """
        BACKEND: Verify legs now include a 'type' field ('quantum' or 'jump') 
        and gate jump legs show type='jump'
        """
        # Cross-system route to force a gate jump
        payload = {
            "store_names": [STANTON_STORES[0], PYRO_STORE],
            "qd_size": 1,
            "origin_id": "lorville"
        }
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success")
        
        route = data.get("data", {})
        legs = route.get("legs", [])
        
        # Verify all legs have 'type' field
        for i, leg in enumerate(legs):
            assert "type" in leg, f"Leg {i} missing 'type' field: {leg}"
            assert leg["type"] in ["quantum", "jump"], \
                f"Leg {i} has invalid type '{leg['type']}', expected 'quantum' or 'jump'"
        
        # For cross-system, there should be at least one jump leg
        jump_legs = [leg for leg in legs if leg.get("type") == "jump"]
        assert len(jump_legs) >= 1, \
            f"Cross-system route should have at least one 'jump' leg, found {len(jump_legs)}"
        
        # Verify jump legs have gateway locations
        for jump_leg in jump_legs:
            from_name = jump_leg.get("from_name", "").lower()
            to_name = jump_leg.get("to_name", "").lower()
            assert "gateway" in from_name or "gateway" in to_name or "gw" in from_name or "gw" in to_name, \
                f"Jump leg should be between gateways: {from_name} -> {to_name}"
    
    def test_cross_system_broken_into_sub_legs(self):
        """
        BACKEND: Verify cross-system legs are broken into quantum→jump→quantum sub-legs
        """
        payload = {
            "store_names": [STANTON_STORES[0], PYRO_STORE],
            "qd_size": 1,
            "origin_id": "lorville"
        }
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        route = data.get("data", {})
        legs = route.get("legs", [])
        
        # Count leg types
        leg_types = [leg.get("type") for leg in legs]
        print(f"Leg sequence: {leg_types}")
        
        # Should have quantum legs before and after the jump
        quantum_count = leg_types.count("quantum")
        jump_count = leg_types.count("jump")
        
        assert quantum_count >= 2, f"Expected at least 2 quantum legs, got {quantum_count}"
        assert jump_count >= 1, f"Expected at least 1 jump leg, got {jump_count}"
    
    def test_default_nearest_neighbor_without_origin(self):
        """
        BACKEND: POST /api/routes/shopping_trip without origin_id 
        — verify default nearest-neighbor still works
        """
        payload = {
            "store_names": STANTON_STORES,
            "qd_size": 1
            # No origin_id
        }
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success"), f"Expected success=True: {data}"
        
        route = data.get("data", {})
        stops = route.get("stops", [])
        
        # Should have stops even without origin
        assert len(stops) >= 1, "Expected at least 1 stop"
        
        # Origin should be null/None
        assert route.get("origin") is None, \
            f"Expected no origin when origin_id not provided, got: {route.get('origin')}"


class TestShoppingRouteWithDifferentOrigins:
    """
    Additional tests for shopping route with different starting locations
    """
    
    def test_area18_origin_stanton_stores(self):
        """Test route from Area 18 to other Stanton stores"""
        payload = {
            "store_names": STANTON_STORES,
            "qd_size": 1,
            "origin_id": "area18"
        }
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        route = data.get("data", {})
        origin = route.get("origin", {})
        
        assert origin.get("id") == "area18"
        assert origin.get("system") == "stanton"
        
        # No jumps for Stanton-only route
        legs = route.get("legs", [])
        jump_count = sum(1 for leg in legs if leg.get("type") == "jump")
        assert jump_count == 0, f"Expected no jumps for Stanton route, got {jump_count}"
    
    def test_new_babbage_origin_cross_system(self):
        """Test route from New Babbage to Stanton + Pyro stores"""
        payload = {
            "store_names": STANTON_STORES[:1] + [PYRO_STORE],
            "qd_size": 1,
            "origin_id": "new-babbage"
        }
        response = requests.post(f"{BASE_URL}/api/routes/shopping_trip", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        route = data.get("data", {})
        origin = route.get("origin", {})
        legs = route.get("legs", [])
        
        assert origin.get("id") == "new-babbage"
        
        # Should have jump leg(s) for cross-system
        jump_count = sum(1 for leg in legs if leg.get("type") == "jump")
        assert jump_count >= 1, f"Expected at least 1 jump for cross-system route"


class TestStartingLocationsEndpoint:
    """Test the starting locations endpoint"""
    
    def test_get_starting_locations(self):
        """Verify /api/routes/starting_locations returns dockable locations"""
        response = requests.get(f"{BASE_URL}/api/routes/starting_locations")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success")
        
        locations = data.get("data", [])
        assert len(locations) > 0, "Expected at least some starting locations"
        
        # Verify structure
        for loc in locations[:5]:  # Check first 5
            assert "id" in loc
            assert "name" in loc
            assert "system" in loc
            assert "type" in loc
            assert loc["type"] in ["city", "station", "rest_stop"], \
                f"Expected dockable type, got {loc['type']}"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
