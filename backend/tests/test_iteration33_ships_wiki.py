"""
Star Citizen Fleet Manager API Tests - Iteration 33
Tests: Ships page with wiki ships, ground vehicle filtering, flight_ready flag, Avenger variants, filters
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cargo-pilot.preview.emergentagent.com')

# Test credentials
TEST_USERNAME = "wikitest"
TEST_PASSWORD = "test123"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token using username/password"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip(f"Authentication failed: {response.text}")


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


# List of known ground vehicles that should NOT appear in /api/ships
GROUND_VEHICLE_NAMES = {
    "ballista", "ballista dunestalker", "ballista snowblind",
    "nox", "nox kue",
    "dragonfly", "dragonfly black", "dragonfly yellowjacket",
    "cyclone", "cyclone aa", "cyclone mt", "cyclone rc", "cyclone rn", "cyclone tr",
    "ursa", "ursa rover", "ursa fortuna", "ursa medivac",
    "nova", "nova tank",
    "centurion", "spartan", "srv", "hoverquad", "roc", "roc-ds", "mule",
    "x1", "x1 force", "x1 velocity", "lynx", "golem", "golem ox",
    "ptv", "stv", "storm", "storm aa"
}

# Non-flight-ready ships added from starcitizen.tools wiki
WIKI_NON_FLIGHT_READY_SHIPS = [
    "Arrastra", "Crucible", "E1 Spirit", "Endeavor", "Expanse", "Genesis Starliner",
    "Hull B", "Hull D", "Hull E", "Ironclad", "Ironclad Assault", "Kraken", 
    "Kraken Privateer", "Legionnaire", "Liberator", "Merchantman", "Nautilus",
    "Odyssey", "Orion", "Pioneer", "Railen", "Zeus Mk II MR"
]


class TestShipsNoGroundVehicles:
    """Test that GET /api/ships returns NO ground vehicles"""
    
    def test_no_ground_vehicles_in_ships(self, auth_headers):
        """Verify ground vehicles are excluded from ships endpoint"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        ships = data["data"]
        
        # Check each ship name against ground vehicle list
        found_ground_vehicles = []
        for ship in ships:
            ship_name = ship.get("name", "").lower().strip()
            if ship_name in GROUND_VEHICLE_NAMES:
                found_ground_vehicles.append(ship["name"])
        
        assert len(found_ground_vehicles) == 0, \
            f"Ground vehicles found in /api/ships: {found_ground_vehicles}"
    
    def test_no_ballista_in_ships(self, auth_headers):
        """Specifically check Ballista is not in ships"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        ballista_ships = [s for s in ships if "ballista" in s.get("name", "").lower()]
        assert len(ballista_ships) == 0, f"Ballista found in ships: {[s['name'] for s in ballista_ships]}"
    
    def test_no_nox_in_ships(self, auth_headers):
        """Specifically check Nox hoverbikes are not in ships"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        # Check if name is exactly 'Nox' or 'Nox Kue' (not part of another name like 'Phoenix')
        nox_ships = [s for s in ships if s.get("name", "").lower() in ["nox", "nox kue"]]
        assert len(nox_ships) == 0, f"Nox found in ships: {[s['name'] for s in nox_ships]}"
    
    def test_no_cyclone_in_ships(self, auth_headers):
        """Specifically check Cyclone variants are not in ships"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        cyclone_ships = [s for s in ships if s.get("name", "").lower().startswith("cyclone")]
        assert len(cyclone_ships) == 0, f"Cyclone found in ships: {[s['name'] for s in cyclone_ships]}"
    
    def test_no_ursa_in_ships(self, auth_headers):
        """Specifically check Ursa rovers are not in ships"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        ursa_ships = [s for s in ships if s.get("name", "").lower().startswith("ursa")]
        assert len(ursa_ships) == 0, f"Ursa found in ships: {[s['name'] for s in ursa_ships]}"
    
    def test_no_dragonfly_in_ships(self, auth_headers):
        """Specifically check Dragonfly hoverbikes are not in ships"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        dragonfly_ships = [s for s in ships if s.get("name", "").lower().startswith("dragonfly")]
        assert len(dragonfly_ships) == 0, f"Dragonfly found in ships: {[s['name'] for s in dragonfly_ships]}"


class TestAvengerVariants:
    """Test Avenger variants grouped under Avenger Titan base card"""
    
    def test_avenger_titan_is_base_ship(self, auth_headers):
        """Verify Avenger Titan appears as a base ship"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        avenger_titan = next((s for s in ships if s.get("name") == "Avenger Titan"), None)
        assert avenger_titan is not None, "Avenger Titan not found as base ship"
    
    def test_avenger_titan_has_variants(self, auth_headers):
        """Verify Avenger Titan has variants array with Stalker, Warlock, Renegade"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        avenger_titan = next((s for s in ships if s.get("name") == "Avenger Titan"), None)
        assert avenger_titan is not None, "Avenger Titan not found"
        
        variants = avenger_titan.get("variants", [])
        variant_names = [v.get("name") for v in variants]
        
        # Check expected variants are present
        expected_variants = ["Avenger Stalker", "Avenger Warlock"]
        for expected in expected_variants:
            assert expected in variant_names, f"{expected} not in Avenger Titan variants: {variant_names}"
    
    def test_avenger_stalker_not_standalone(self, auth_headers):
        """Verify Avenger Stalker is NOT a standalone base ship (should be variant)"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        # Get top-level ship names
        base_ship_names = [s.get("name") for s in ships]
        
        # Avenger Stalker should NOT be at top level
        assert "Avenger Stalker" not in base_ship_names, \
            "Avenger Stalker should be a variant under Avenger Titan, not a standalone ship"
    
    def test_avenger_warlock_not_standalone(self, auth_headers):
        """Verify Avenger Warlock is NOT a standalone base ship (should be variant)"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        base_ship_names = [s.get("name") for s in ships]
        assert "Avenger Warlock" not in base_ship_names, \
            "Avenger Warlock should be a variant under Avenger Titan, not a standalone ship"


class TestFlightReadyFlag:
    """Test flight_ready flag on ships"""
    
    def test_live_api_ships_are_flight_ready(self, auth_headers):
        """Verify ships from live API have flight_ready=True"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        # Common flight-ready ships that should have flight_ready=True
        flight_ready_ships = ["Aurora MR", "Avenger Titan", "Cutlass Black", "Freelancer", "Carrack"]
        
        for ship_name in flight_ready_ships:
            ship = next((s for s in ships if s.get("name") == ship_name), None)
            if ship:
                assert ship.get("flight_ready") == True, \
                    f"{ship_name} should have flight_ready=True"
    
    def test_wiki_ships_not_flight_ready(self, auth_headers):
        """Verify non-flight-ready ships from wiki have flight_ready=False"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        # Check a few known non-flight-ready ships
        non_ready_to_check = ["Endeavor", "Kraken", "Merchantman", "Orion"]
        
        for ship_name in non_ready_to_check:
            ship = next((s for s in ships if s.get("name") == ship_name), None)
            if ship:
                assert ship.get("flight_ready") == False, \
                    f"{ship_name} should have flight_ready=False (is non-flight-ready wiki ship)"
    
    def test_all_ships_have_flight_ready_field(self, auth_headers):
        """Verify all ships have the flight_ready field"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        ships_without_field = [s["name"] for s in ships if "flight_ready" not in s]
        assert len(ships_without_field) == 0, \
            f"Ships missing flight_ready field: {ships_without_field[:10]}"


class TestShipCount:
    """Test total ship count is reasonable (no duplicates)"""
    
    def test_ship_count_reasonable(self, auth_headers):
        """Verify ship count is approximately 180 (live + wiki ships, no dupes)"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        ship_count = len(ships)
        # With wiki ships added and ground vehicles removed, expect 150-220 ships
        assert 150 <= ship_count <= 220, \
            f"Ship count {ship_count} outside expected range 150-220"
    
    def test_no_duplicate_ship_names(self, auth_headers):
        """Verify no duplicate ship names at base level"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        ship_names = [s.get("name") for s in ships]
        unique_names = set(ship_names)
        
        if len(ship_names) != len(unique_names):
            # Find duplicates
            from collections import Counter
            counts = Counter(ship_names)
            dupes = [name for name, count in counts.items() if count > 1]
            assert False, f"Duplicate ships found: {dupes}"
    
    def test_wiki_ships_present(self, auth_headers):
        """Verify at least some wiki ships are added"""
        response = requests.get(f"{BASE_URL}/api/ships", headers=auth_headers)
        assert response.status_code == 200
        ships = response.json()["data"]
        
        ship_names = [s.get("name") for s in ships]
        
        # Check for some expected wiki ships
        wiki_ships_found = [name for name in WIKI_NON_FLIGHT_READY_SHIPS if name in ship_names]
        
        assert len(wiki_ships_found) >= 10, \
            f"Expected at least 10 wiki ships, found {len(wiki_ships_found)}: {wiki_ships_found}"


class TestGroundVehiclesEndpoint:
    """Test that ground vehicles ARE in /api/vehicles endpoint"""
    
    def test_vehicles_endpoint_has_ground_vehicles(self, auth_headers):
        """Verify /api/vehicles returns ground vehicles"""
        response = requests.get(f"{BASE_URL}/api/vehicles", headers=auth_headers)
        assert response.status_code == 200
        vehicles = response.json()["data"]
        
        # Check some ground vehicles are present
        vehicle_names = [v.get("name", "").lower() for v in vehicles]
        
        found_ground = []
        for gv in ["cyclone", "ursa", "nox"]:
            if any(gv in name for name in vehicle_names):
                found_ground.append(gv)
        
        assert len(found_ground) > 0, \
            f"No ground vehicles found in /api/vehicles. Names: {vehicle_names[:10]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
