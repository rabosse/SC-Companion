"""
Test Community & Loadout Sharing Features
- Community Loadouts page (GET /api/community/loadouts) - PUBLIC
- Shared Loadout view (GET /api/community/loadouts/{share_code}) - PUBLIC
- Loadout saving with share_code (POST /api/loadouts/save) - AUTH required
- Clone loadout (POST /api/loadouts/clone/{share_code}) - AUTH required
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USERNAME = "testpilot2"
TEST_PASSWORD = "password"
KNOWN_SHARE_CODE = "yckbp4gd"


class TestPublicCommunityEndpoints:
    """Public endpoints - no auth required"""
    
    def test_community_loadouts_endpoint_public(self):
        """Verify /api/community/loadouts works without auth"""
        response = requests.get(f"{BASE_URL}/api/community/loadouts")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["success"] == True, "Expected success=True"
        assert "data" in data, "Expected data field"
        assert "total" in data, "Expected total field"
        assert "page" in data, "Expected page field"
        print(f"SUCCESS: Community loadouts endpoint returned {len(data['data'])} loadouts, total: {data['total']}")
    
    def test_community_loadouts_search_by_ship(self):
        """Test search functionality by ship_name"""
        response = requests.get(f"{BASE_URL}/api/community/loadouts", params={"ship_name": "Arrow"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        # All returned loadouts should contain Arrow in ship_name
        for loadout in data["data"]:
            assert "arrow" in loadout["ship_name"].lower(), f"Expected Arrow ship, got {loadout['ship_name']}"
        print(f"SUCCESS: Search by ship_name='Arrow' returned {len(data['data'])} loadouts")
    
    def test_community_loadouts_pagination(self):
        """Test pagination works"""
        response = requests.get(f"{BASE_URL}/api/community/loadouts", params={"page": 1, "limit": 5})
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert len(data["data"]) <= 5, "Should not return more than limit"
        print(f"SUCCESS: Pagination works - page 1, limit 5, got {len(data['data'])} items")
    
    def test_shared_loadout_by_code_public(self):
        """Verify /api/community/loadouts/{share_code} works without auth"""
        response = requests.get(f"{BASE_URL}/api/community/loadouts/{KNOWN_SHARE_CODE}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        
        loadout = data["data"]
        assert loadout["share_code"] == KNOWN_SHARE_CODE
        assert "ship_name" in loadout
        assert "loadout_name" in loadout
        assert "slots" in loadout
        assert "username" in loadout
        print(f"SUCCESS: Shared loadout '{loadout['loadout_name']}' for {loadout['ship_name']} by {loadout['username']}")
    
    def test_shared_loadout_invalid_code_returns_404(self):
        """Test invalid share code returns 404"""
        response = requests.get(f"{BASE_URL}/api/community/loadouts/invalid_code_xyz")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("SUCCESS: Invalid share code returns 404")


class TestAuthenticatedLoadoutEndpoints:
    """Authenticated endpoints - require login"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        print(f"SUCCESS: Logged in as {TEST_USERNAME}")
    
    def test_save_loadout_returns_share_code(self):
        """Test saving a loadout returns a share_code"""
        unique_name = f"TEST_Loadout_{uuid.uuid4().hex[:6]}"
        payload = {
            "ship_id": "arrow",
            "ship_name": "Arrow",
            "loadout_name": unique_name,
            "slots": {
                "shield_0": {"name": "AllStop", "type": "Shield", "size": "1", "manufacturer": "Mirage", "cost_auec": 12400}
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/loadouts/save", json=payload, headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "share_code" in data, "Expected share_code in response"
        assert len(data["share_code"]) > 0, "share_code should not be empty"
        print(f"SUCCESS: Saved loadout '{unique_name}' with share_code: {data['share_code']}")
        
        # Store for cleanup
        self.created_loadout_id = data.get("id")
        self.created_share_code = data["share_code"]
        
        # Verify the share_code works in community endpoint
        verify_response = requests.get(f"{BASE_URL}/api/community/loadouts/{data['share_code']}")
        assert verify_response.status_code == 200, "Newly created loadout should be accessible via share_code"
        print(f"SUCCESS: Verified loadout accessible at /api/community/loadouts/{data['share_code']}")
    
    def test_clone_loadout_creates_copy(self):
        """Test cloning a shared loadout"""
        # Clone the known loadout
        response = requests.post(
            f"{BASE_URL}/api/loadouts/clone/{KNOWN_SHARE_CODE}", 
            json={},
            headers=self.headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "id" in data, "Expected id of cloned loadout"
        print(f"SUCCESS: Cloned loadout, new id: {data['id']}")
    
    def test_clone_loadout_without_auth_fails(self):
        """Test cloning without auth returns 401/403"""
        response = requests.post(f"{BASE_URL}/api/loadouts/clone/{KNOWN_SHARE_CODE}", json={})
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("SUCCESS: Clone without auth returns 401/403")
    
    def test_get_my_loadouts(self):
        """Test getting user's saved loadouts"""
        response = requests.get(f"{BASE_URL}/api/loadouts/my/all", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        print(f"SUCCESS: Retrieved {len(data['data'])} user loadouts")
    
    def test_get_loadouts_for_ship(self):
        """Test getting loadouts for a specific ship"""
        response = requests.get(f"{BASE_URL}/api/loadouts/arrow", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        print(f"SUCCESS: Retrieved {len(data['data'])} loadouts for Arrow")


class TestLoadoutDataStructure:
    """Test the data structure of loadouts"""
    
    def test_community_loadout_has_required_fields(self):
        """Verify community loadout has all required fields"""
        response = requests.get(f"{BASE_URL}/api/community/loadouts/{KNOWN_SHARE_CODE}")
        assert response.status_code == 200
        
        loadout = response.json()["data"]
        
        required_fields = ["id", "user_id", "username", "ship_id", "ship_name", "loadout_name", "slots", "share_code", "updated_at"]
        for field in required_fields:
            assert field in loadout, f"Missing required field: {field}"
        
        print(f"SUCCESS: Loadout has all required fields: {required_fields}")
    
    def test_loadout_slots_have_proper_structure(self):
        """Verify slots have proper structure with equipment data"""
        response = requests.get(f"{BASE_URL}/api/community/loadouts/{KNOWN_SHARE_CODE}")
        assert response.status_code == 200
        
        loadout = response.json()["data"]
        slots = loadout["slots"]
        
        assert len(slots) > 0, "Loadout should have at least one slot"
        
        for slot_key, slot_item in slots.items():
            assert "name" in slot_item, f"Slot {slot_key} missing 'name'"
            print(f"  - Slot '{slot_key}': {slot_item['name']}")
        
        print(f"SUCCESS: Loadout has {len(slots)} properly structured slots")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
