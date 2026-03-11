"""
Iteration 33: Wikelo Section Tests
Tests for the new Wikelo NPC trader section with collection contracts.

Features tested:
- GET /api/wikelo/info - Wikelo info (name, description, locations, image)
- GET /api/wikelo/contracts - All contracts with categories breakdown
- GET /api/wikelo/contracts?category=X - Filter by category
- GET /api/wikelo/contracts?active_only=true - Filter active contracts only
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

class TestWikeloInfo:
    """Tests for GET /api/wikelo/info endpoint"""
    
    def test_wikelo_info_returns_success(self):
        """Verify the info endpoint returns success status"""
        response = requests.get(f"{BASE_URL}/api/wikelo/info")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data

    def test_wikelo_info_has_required_fields(self):
        """Verify Wikelo info contains all required fields"""
        response = requests.get(f"{BASE_URL}/api/wikelo/info")
        data = response.json()["data"]
        
        # Check required fields exist
        assert "name" in data
        assert "description" in data
        assert "locations" in data
        assert "image" in data
        
        # Verify specific values
        assert data["name"] == "Wikelo"
        assert "Banu trader" in data["description"]
        assert isinstance(data["locations"], list)
        assert len(data["locations"]) == 3  # 3 emporium locations
    
    def test_wikelo_info_locations_structure(self):
        """Verify location data structure"""
        response = requests.get(f"{BASE_URL}/api/wikelo/info")
        data = response.json()["data"]
        
        for location in data["locations"]:
            assert "name" in location
            assert "near" in location
            assert "Wikelo Emporium" in location["name"]


class TestWikeloContracts:
    """Tests for GET /api/wikelo/contracts endpoint"""
    
    def test_contracts_returns_success(self):
        """Verify contracts endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        assert "total" in data
        assert "categories" in data
    
    def test_contracts_returns_70_contracts(self):
        """Verify we get all 70 contracts"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts")
        data = response.json()
        
        assert data["total"] == 70
        assert len(data["data"]) == 70
    
    def test_contracts_have_required_fields(self):
        """Verify each contract has required fields"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts")
        contracts = response.json()["data"]
        
        for contract in contracts[:10]:  # Check first 10 for speed
            assert "id" in contract
            assert "name" in contract
            assert "category" in contract
            assert "active" in contract
            assert "items_needed" in contract
            assert "reward" in contract
            assert isinstance(contract["items_needed"], list)
            assert isinstance(contract["reward"], list)
    
    def test_contracts_categories_breakdown(self):
        """Verify categories breakdown is correct"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts")
        categories = response.json()["categories"]
        
        # Verify all 5 categories exist
        assert "Vehicles" in categories
        assert "Weapons" in categories
        assert "Armor" in categories
        assert "Currencies" in categories
        assert "Utility" in categories
        
        # Verify structure
        for cat, data in categories.items():
            assert "total" in data
            assert "active" in data
            assert data["total"] >= data["active"]
    
    def test_contracts_category_counts(self):
        """Verify category counts match expected values"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts")
        categories = response.json()["categories"]
        
        # Expected: 34 Vehicles (all active), 17 Weapons (7 active), 
        # 13 Armor (7 active), 5 Currencies (all active), 1 Utility (inactive)
        assert categories["Vehicles"]["total"] == 34
        assert categories["Vehicles"]["active"] == 34
        
        assert categories["Weapons"]["total"] == 17
        assert categories["Weapons"]["active"] == 7
        
        assert categories["Armor"]["total"] == 13
        assert categories["Armor"]["active"] == 7
        
        assert categories["Currencies"]["total"] == 5
        assert categories["Currencies"]["active"] == 5
        
        assert categories["Utility"]["total"] == 1
        assert categories["Utility"]["active"] == 0


class TestWikeloContractFiltering:
    """Tests for contract filtering functionality"""
    
    def test_filter_by_category_vehicles(self):
        """Test filtering by Vehicles category"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts?category=Vehicles")
        data = response.json()
        
        assert response.status_code == 200
        assert data["total"] == 34
        # Verify all returned contracts are Vehicles
        for contract in data["data"]:
            assert contract["category"] == "Vehicles"
    
    def test_filter_by_category_weapons(self):
        """Test filtering by Weapons category"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts?category=Weapons")
        data = response.json()
        
        assert response.status_code == 200
        assert data["total"] == 17
        for contract in data["data"]:
            assert contract["category"] == "Weapons"
    
    def test_filter_by_category_armor(self):
        """Test filtering by Armor category"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts?category=Armor")
        data = response.json()
        
        assert response.status_code == 200
        assert data["total"] == 13
        for contract in data["data"]:
            assert contract["category"] == "Armor"
    
    def test_filter_by_category_currencies(self):
        """Test filtering by Currencies category"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts?category=Currencies")
        data = response.json()
        
        assert response.status_code == 200
        assert data["total"] == 5
        for contract in data["data"]:
            assert contract["category"] == "Currencies"
    
    def test_filter_by_category_utility(self):
        """Test filtering by Utility category"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts?category=Utility")
        data = response.json()
        
        assert response.status_code == 200
        assert data["total"] == 1
        for contract in data["data"]:
            assert contract["category"] == "Utility"
    
    def test_filter_active_only(self):
        """Test active_only=true filter"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts?active_only=true")
        data = response.json()
        
        assert response.status_code == 200
        # 34 Vehicles + 7 Weapons + 7 Armor + 5 Currencies + 0 Utility = 53 active
        assert data["total"] == 53
        
        # Verify all returned contracts are active
        for contract in data["data"]:
            assert contract["active"] == True
    
    def test_filter_combined_category_and_active(self):
        """Test combining category and active_only filters"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts?category=Weapons&active_only=true")
        data = response.json()
        
        assert response.status_code == 200
        assert data["total"] == 7  # 7 active weapons
        
        for contract in data["data"]:
            assert contract["category"] == "Weapons"
            assert contract["active"] == True
    
    def test_filter_case_insensitive(self):
        """Test category filter is case insensitive"""
        response_lower = requests.get(f"{BASE_URL}/api/wikelo/contracts?category=weapons")
        response_upper = requests.get(f"{BASE_URL}/api/wikelo/contracts?category=WEAPONS")
        response_mixed = requests.get(f"{BASE_URL}/api/wikelo/contracts?category=Weapons")
        
        assert response_lower.json()["total"] == response_upper.json()["total"] == response_mixed.json()["total"]


class TestWikeloContractData:
    """Tests for specific contract data quality"""
    
    def test_reputation_rank_contracts_exist(self):
        """Verify contracts with reputation rank requirements exist"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts")
        contracts = response.json()["data"]
        
        contracts_with_rank = [c for c in contracts if "req_rank" in c]
        assert len(contracts_with_rank) >= 2  # At least 2 contracts require rank
        
        # Check specific contract
        most_special_wolf = next((c for c in contracts if c["id"] == "most-special-wolf"), None)
        assert most_special_wolf is not None
        assert most_special_wolf["req_rank"] == "Very Good Customer"
    
    def test_contracts_with_images(self):
        """Verify some contracts have images"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts?category=Weapons")
        contracts = response.json()["data"]
        
        contracts_with_images = [c for c in contracts if c.get("image")]
        assert len(contracts_with_images) > 0  # At least some weapons have images
    
    def test_contract_items_needed_not_empty(self):
        """Verify all contracts have items needed"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts")
        contracts = response.json()["data"]
        
        for contract in contracts:
            assert len(contract["items_needed"]) > 0, f"Contract {contract['name']} has no items needed"
    
    def test_contract_rewards_not_empty(self):
        """Verify all contracts have rewards"""
        response = requests.get(f"{BASE_URL}/api/wikelo/contracts")
        contracts = response.json()["data"]
        
        for contract in contracts:
            assert len(contract["reward"]) > 0, f"Contract {contract['name']} has no reward"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
