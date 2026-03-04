"""
Test iteration 16: New map locations (cities, rest stops, outposts) + aUEC prices on weapons/armor
Tests:
1. GET /api/routes/locations returns 81 locations (was 61)
2. Locations include type 'city' with Lorville, Orison, Area 18, New Babbage, Levski
3. Locations include type 'rest_stop' with R&R HUR-L1, CRU-L1, ARC-L1, MIC-L1
4. Locations include type 'outpost' with Kudre Ore, HDMS-Lathan, Shubin Mining SAL-5, Bountiful Harvest
5. Route calculation works with new location types (e.g. origin=lorville, destination=area18)
6. GET /api/gear/weapons returns 38 items all with price_auec > 0
7. GET /api/gear/armor returns 21 items all with price_auec > 0
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestNewLocations:
    """Tests for new map location types: cities, rest stops, outposts"""
    
    def test_locations_count_81(self):
        """GET /api/routes/locations should return 81 locations (was 61)"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        locations = data.get("data", [])
        assert len(locations) == 81, f"Expected 81 locations, got {len(locations)}"
        print(f"PASS: GET /api/routes/locations returns {len(locations)} locations")
    
    def test_locations_include_cities(self):
        """Locations should include type 'city' with major cities"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        assert response.status_code == 200
        data = response.json()
        locations = data.get("data", [])
        
        # Filter for cities
        cities = [loc for loc in locations if loc.get("type") == "city"]
        city_names = [c.get("name") for c in cities]
        city_ids = [c.get("id") for c in cities]
        
        # Expected cities
        expected_cities = ["Lorville", "Orison", "Area 18", "New Babbage", "Levski"]
        expected_ids = ["lorville", "orison", "area18", "new-babbage", "levski-city"]
        
        for city_name in expected_cities:
            assert city_name in city_names, f"City '{city_name}' not found in locations"
        
        for city_id in expected_ids:
            assert city_id in city_ids, f"City ID '{city_id}' not found in locations"
        
        print(f"PASS: Found {len(cities)} cities: {city_names}")
    
    def test_locations_include_rest_stops(self):
        """Locations should include type 'rest_stop' with R&R stations"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        assert response.status_code == 200
        data = response.json()
        locations = data.get("data", [])
        
        # Filter for rest stops
        rest_stops = [loc for loc in locations if loc.get("type") == "rest_stop"]
        rest_stop_names = [r.get("name") for r in rest_stops]
        rest_stop_ids = [r.get("id") for r in rest_stops]
        
        # Expected rest stops
        expected_rest_stops = ["R&R HUR-L1", "R&R CRU-L1", "R&R ARC-L1", "R&R MIC-L1"]
        expected_ids = ["hur-r1", "cru-r1", "arc-r1", "mic-r1"]
        
        for rs_name in expected_rest_stops:
            assert rs_name in rest_stop_names, f"Rest stop '{rs_name}' not found in locations"
        
        for rs_id in expected_ids:
            assert rs_id in rest_stop_ids, f"Rest stop ID '{rs_id}' not found in locations"
        
        print(f"PASS: Found {len(rest_stops)} rest stops: {rest_stop_names}")
    
    def test_locations_include_outposts(self):
        """Locations should include type 'outpost' with mining/research outposts"""
        response = requests.get(f"{BASE_URL}/api/routes/locations")
        assert response.status_code == 200
        data = response.json()
        locations = data.get("data", [])
        
        # Filter for outposts
        outposts = [loc for loc in locations if loc.get("type") == "outpost"]
        outpost_names = [o.get("name") for o in outposts]
        outpost_ids = [o.get("id") for o in outposts]
        
        # Expected outposts (sample)
        expected_outposts = ["Kudre Ore", "HDMS-Lathan", "Shubin Mining SAL-5", "Bountiful Harvest"]
        expected_ids = ["kudre-ore", "lathan", "shubin-sal5", "bountiful-harvest"]
        
        for op_name in expected_outposts:
            assert op_name in outpost_names, f"Outpost '{op_name}' not found in locations"
        
        for op_id in expected_ids:
            assert op_id in outpost_ids, f"Outpost ID '{op_id}' not found in locations"
        
        print(f"PASS: Found {len(outposts)} outposts including: {expected_outposts}")
    
    def test_route_calculation_city_to_city(self):
        """Route calculation should work with new city location types"""
        # Test route from Lorville to Area 18
        response = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "lorville",
            "destination": "area18",
            "qd_size": 1
        })
        assert response.status_code == 200, f"Route calc failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        
        route = data.get("data", {})
        assert route.get("origin", {}).get("id") == "lorville"
        assert route.get("destination", {}).get("id") == "area18"
        assert route.get("total_distance_mkm", 0) > 0
        assert route.get("travel_time_seconds", 0) > 0
        assert len(route.get("waypoints", [])) >= 1
        
        print(f"PASS: Route Lorville→Area 18: {route.get('total_distance_mkm')} Mkm, {route.get('travel_time_seconds')}s")
    
    def test_route_calculation_city_to_rest_stop(self):
        """Route calculation should work from city to rest stop"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "new-babbage",
            "destination": "mic-r1",
            "qd_size": 2
        })
        assert response.status_code == 200, f"Route calc failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        
        route = data.get("data", {})
        assert route.get("origin", {}).get("id") == "new-babbage"
        assert route.get("destination", {}).get("id") == "mic-r1"
        
        print(f"PASS: Route New Babbage→R&R MIC-L1: {route.get('total_distance_mkm')} Mkm")
    
    def test_route_calculation_outpost_to_city(self):
        """Route calculation should work from outpost to city"""
        response = requests.get(f"{BASE_URL}/api/routes/calculate", params={
            "origin": "kudre-ore",
            "destination": "lorville",
            "qd_size": 1
        })
        assert response.status_code == 200, f"Route calc failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        
        route = data.get("data", {})
        assert route.get("origin", {}).get("id") == "kudre-ore"
        assert route.get("destination", {}).get("id") == "lorville"
        
        print(f"PASS: Route Kudre Ore→Lorville: {route.get('total_distance_mkm')} Mkm")


class TestGearPrices:
    """Tests for aUEC prices on weapons and armor"""
    
    def test_weapons_count_38(self):
        """GET /api/gear/weapons should return 38 items"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        weapons = data.get("data", [])
        assert len(weapons) == 38, f"Expected 38 weapons, got {len(weapons)}"
        print(f"PASS: GET /api/gear/weapons returns {len(weapons)} weapons")
    
    def test_all_weapons_have_price_auec(self):
        """All 38 weapons should have price_auec field > 0"""
        response = requests.get(f"{BASE_URL}/api/gear/weapons")
        assert response.status_code == 200
        data = response.json()
        weapons = data.get("data", [])
        
        weapons_without_price = []
        weapons_with_zero_price = []
        
        for weapon in weapons:
            if "price_auec" not in weapon:
                weapons_without_price.append(weapon.get("name"))
            elif weapon.get("price_auec", 0) <= 0:
                weapons_with_zero_price.append(weapon.get("name"))
        
        assert len(weapons_without_price) == 0, f"Weapons missing price_auec: {weapons_without_price}"
        assert len(weapons_with_zero_price) == 0, f"Weapons with zero/negative price: {weapons_with_zero_price}"
        
        # Verify some sample prices
        weapon_prices = {w.get("name"): w.get("price_auec") for w in weapons}
        assert weapon_prices.get("Arclight Pistol", 0) > 0
        assert weapon_prices.get("P4-AR Assault Rifle", 0) > 0
        assert weapon_prices.get("F55 LMG", 0) > 0
        
        print(f"PASS: All {len(weapons)} weapons have price_auec > 0")
        print(f"  Sample prices: Arclight={weapon_prices.get('Arclight Pistol')}, P4-AR={weapon_prices.get('P4-AR Assault Rifle')}, F55={weapon_prices.get('F55 LMG')}")
    
    def test_armor_count_21(self):
        """GET /api/gear/armor should return 21 items"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        armor = data.get("data", [])
        assert len(armor) == 21, f"Expected 21 armor sets, got {len(armor)}"
        print(f"PASS: GET /api/gear/armor returns {len(armor)} armor sets")
    
    def test_all_armor_have_price_auec(self):
        """All 21 armor sets should have price_auec field > 0"""
        response = requests.get(f"{BASE_URL}/api/gear/armor")
        assert response.status_code == 200
        data = response.json()
        armor = data.get("data", [])
        
        armor_without_price = []
        armor_with_zero_price = []
        
        for item in armor:
            if "price_auec" not in item:
                armor_without_price.append(item.get("name"))
            elif item.get("price_auec", 0) <= 0:
                armor_with_zero_price.append(item.get("name"))
        
        assert len(armor_without_price) == 0, f"Armor missing price_auec: {armor_without_price}"
        assert len(armor_with_zero_price) == 0, f"Armor with zero/negative price: {armor_with_zero_price}"
        
        # Verify some sample prices
        armor_prices = {a.get("name"): a.get("price_auec") for a in armor}
        
        print(f"PASS: All {len(armor)} armor sets have price_auec > 0")
        sample_armor = list(armor_prices.keys())[:3]
        for name in sample_armor:
            print(f"  {name}: {armor_prices.get(name)} aUEC")


class TestRegressionEndpoints:
    """Regression tests for existing functionality"""
    
    def test_health_endpoint(self):
        """GET /api/health should return ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS: GET /api/health returns ok")
    
    def test_equipment_endpoint(self):
        """GET /api/gear/equipment should return equipment"""
        response = requests.get(f"{BASE_URL}/api/gear/equipment")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        equipment = data.get("data", [])
        assert len(equipment) >= 30, f"Expected at least 30 equipment, got {len(equipment)}"
        print(f"PASS: GET /api/gear/equipment returns {len(equipment)} items")
    
    def test_prices_endpoint(self):
        """GET /api/prices/summary endpoint should work"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        print(f"PASS: GET /api/prices/summary endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
