#!/usr/bin/env python3

import requests
import sys
from datetime import datetime
import json

class StarCitizenAPITester:
    def __init__(self, base_url="https://citizen-fleet.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log_test(self, name, status, details=""):
        """Log test results"""
        self.tests_run += 1
        if status:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
            self.failed_tests.append({"test": name, "error": details})

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    self.log_test(name, True)
                    return True, response_data
                except:
                    self.log_test(name, True)
                    return True, {}
            else:
                try:
                    error_data = response.json()
                    self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}. Response: {error_data}")
                except:
                    self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}. Text: {response.text[:200]}")
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_login(self):
        """Test login with demo credentials"""
        print("\n🚀 Testing Authentication...")
        test_email = f"test_user_{datetime.now().strftime('%H%M%S')}@example.com"
        test_token = "demo_token_12345"
        
        success, response = self.run_test(
            "Login (Demo Mode)",
            "POST",
            "auth/login",
            200,
            data={"email": test_email, "star_citizen_token": test_token}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response.get('user', {}).get('id')
            print(f"   Token received: {self.token[:20]}...")
            return True
        return False

    def test_ships_endpoint(self):
        """Test ships endpoint"""
        print("\n🚢 Testing Ships Endpoint...")
        success, response = self.run_test(
            "Get Ships",
            "GET",
            "ships",
            200
        )
        
        if success:
            ships = response.get('data', [])
            print(f"   Ships count: {len(ships)}")
            if ships:
                print(f"   Sample ship: {ships[0]['name']} by {ships[0]['manufacturer']}")
            return len(ships) > 0
        return False

    def test_vehicles_endpoint(self):
        """Test vehicles endpoint"""
        print("\n🚗 Testing Vehicles Endpoint...")
        success, response = self.run_test(
            "Get Vehicles", 
            "GET",
            "vehicles",
            200
        )
        
        if success:
            vehicles = response.get('data', [])
            print(f"   Vehicles count: {len(vehicles)}")
            if vehicles:
                print(f"   Sample vehicle: {vehicles[0]['name']} by {vehicles[0]['manufacturer']}")
            return len(vehicles) > 0
        return False

    def test_components_endpoint(self):
        """Test components endpoint"""
        print("\n🔧 Testing Components Endpoint...")
        success, response = self.run_test(
            "Get Components",
            "GET", 
            "components",
            200
        )
        
        if success:
            components = response.get('data', [])
            print(f"   Components count: {len(components)}")
            if components:
                print(f"   Sample component: {components[0]['name']} ({components[0]['type']})")
            return len(components) > 0
        return False

    def test_weapons_endpoint(self):
        """Test weapons endpoint"""
        print("\n⚔️ Testing Weapons Endpoint...")
        success, response = self.run_test(
            "Get Weapons",
            "GET",
            "weapons", 
            200
        )
        
        if success:
            weapons = response.get('data', [])
            print(f"   Weapons count: {len(weapons)}")
            if weapons:
                print(f"   Sample weapon: {weapons[0]['name']} ({weapons[0]['type']})")
            return len(weapons) > 0
        return False

    def test_upgrades_endpoint(self):
        """Test ship upgrades endpoint"""
        print("\n⬆️ Testing Ship Upgrades Endpoint...")
        success, response = self.run_test(
            "Get Ship Upgrades",
            "GET",
            "upgrades/600i",
            200
        )
        
        if success:
            upgrades = response.get('data', {})
            print(f"   Upgrade categories: {list(upgrades.keys())}")
            return len(upgrades) > 0
        return False

    def test_fleet_operations(self):
        """Test fleet add/get/remove operations"""
        print("\n🏭 Testing Fleet Operations...")
        
        # Add ship to fleet
        ship_data = {
            "id": "600i",
            "name": "600i",
            "manufacturer": "Origin Jumpworks"
        }
        
        add_success, _ = self.run_test(
            "Add Ship to Fleet",
            "POST",
            "fleet/add",
            200,
            data=ship_data
        )
        
        # Get fleet
        get_success, response = self.run_test(
            "Get My Fleet",
            "GET", 
            "fleet/my",
            200
        )
        
        fleet_items = []
        if get_success:
            fleet_items = response.get('data', [])
            print(f"   Fleet size: {len(fleet_items)}")
        
        return add_success and get_success

    def test_unauthorized_access(self):
        """Test API access without token"""
        print("\n🔒 Testing Unauthorized Access...")
        old_token = self.token
        self.token = None  # Remove token temporarily
        
        success, _ = self.run_test(
            "Unauthorized Ships Access",
            "GET",
            "ships", 
            401  # Should get unauthorized
        )
        
        self.token = old_token  # Restore token
        return success

def main():
    print("=" * 60)
    print("🚀 Star Citizen Fleet Manager API Test Suite")
    print("=" * 60)
    
    tester = StarCitizenAPITester()
    
    # Test authentication first
    if not tester.test_login():
        print("\n❌ Login failed - cannot proceed with other tests")
        return 1
    
    # Test all endpoints
    tests = [
        tester.test_ships_endpoint,
        tester.test_vehicles_endpoint,
        tester.test_components_endpoint,
        tester.test_weapons_endpoint,
        tester.test_upgrades_endpoint,
        tester.test_fleet_operations,
        tester.test_unauthorized_access,
    ]
    
    for test in tests:
        test()
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {len(tester.failed_tests)}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.failed_tests:
        print("\n❌ Failed Tests:")
        for failure in tester.failed_tests:
            print(f"  - {failure['test']}: {failure['error']}")
    
    print("\n🎯 Mock API Status: All endpoints using mock data (Star Citizen API key not provided)")
    
    return 0 if len(tester.failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())