"""
Iteration 31: Price Tracker Feature Tests
Tests for:
1. GET /api/prices/summary - returns all items with no duplicates, no 50-item cap
2. GET /api/prices/snapshot - creates new snapshot with deduplicated entries
3. GET /api/prices/changes - detects price differences between snapshots
4. GET /api/prices/history/{item_name} - returns price history for specific item
"""
import pytest
import requests
import os
from collections import Counter

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPriceSummary:
    """Test /api/prices/summary endpoint"""
    
    def test_summary_returns_success(self):
        """Summary endpoint returns success status"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
    def test_summary_contains_all_categories(self):
        """Summary contains ships, weapons, and components"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        assert response.status_code == 200
        data = response.json()
        assert "ships" in data["data"]
        assert "weapons" in data["data"]
        assert "components" in data["data"]
        
    def test_summary_no_50_item_cap(self):
        """Summary returns all items, not capped at 50 per category"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        assert response.status_code == 200
        data = response.json()
        
        ships = data["data"]["ships"]
        weapons = data["data"]["weapons"]
        components = data["data"]["components"]
        
        # Should have more than 50 ships (we know there are ~239)
        assert len(ships) > 50, f"Ships count {len(ships)} should be > 50"
        # Should have more than 50 weapons (we know there are ~82)
        assert len(weapons) > 50, f"Weapons count {len(weapons)} should be > 50"
        # Should have more than 50 components (we know there are ~175)
        assert len(components) > 50, f"Components count {len(components)} should be > 50"
        
        total = len(ships) + len(weapons) + len(components)
        print(f"Total items: {total} (ships: {len(ships)}, weapons: {len(weapons)}, components: {len(components)})")
        
    def test_summary_no_duplicate_items(self):
        """Summary returns no duplicate items within categories"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        assert response.status_code == 200
        data = response.json()
        
        # Check ships for duplicates
        ship_names = [s["item_name"] for s in data["data"]["ships"]]
        ship_duplicates = [name for name, count in Counter(ship_names).items() if count > 1]
        assert len(ship_duplicates) == 0, f"Duplicate ships found: {ship_duplicates}"
        
        # Check weapons for duplicates
        weapon_names = [w["item_name"] for w in data["data"]["weapons"]]
        weapon_duplicates = [name for name, count in Counter(weapon_names).items() if count > 1]
        assert len(weapon_duplicates) == 0, f"Duplicate weapons found: {weapon_duplicates}"
        
        # Check components for duplicates
        component_names = [c["item_name"] for c in data["data"]["components"]]
        component_duplicates = [name for name, count in Counter(component_names).items() if count > 1]
        assert len(component_duplicates) == 0, f"Duplicate components found: {component_duplicates}"
        
    def test_summary_item_structure(self):
        """Summary items have correct structure with all required fields"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        assert response.status_code == 200
        data = response.json()
        
        # Check first ship has required fields
        if data["data"]["ships"]:
            ship = data["data"]["ships"][0]
            assert "item_name" in ship
            assert "item_type" in ship
            assert "price_auec" in ship
            assert "price_usd" in ship
            assert "dealers" in ship
            assert "timestamp" in ship
            assert ship["item_type"] == "ship"
            
        # Check first weapon has required fields
        if data["data"]["weapons"]:
            weapon = data["data"]["weapons"][0]
            assert "item_name" in weapon
            assert "item_type" in weapon
            assert "price_auec" in weapon
            assert weapon["item_type"] == "weapon"
            
        # Check first component has required fields
        if data["data"]["components"]:
            component = data["data"]["components"][0]
            assert "item_name" in component
            assert "item_type" in component
            assert "price_auec" in component
            assert component["item_type"] == "component"
            
    def test_summary_snapshot_count(self):
        """Summary includes snapshot count"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        assert response.status_code == 200
        data = response.json()
        assert "snapshot_count" in data
        assert isinstance(data["snapshot_count"], int)
        assert data["snapshot_count"] > 0  # Should have at least one snapshot
        
    def test_summary_latest_snapshot_timestamp(self):
        """Summary includes latest snapshot timestamp"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        assert response.status_code == 200
        data = response.json()
        assert "latest_snapshot" in data
        assert data["latest_snapshot"] is not None


class TestPriceSnapshot:
    """Test /api/prices/snapshot endpoint - creates new snapshot"""
    
    def test_snapshot_creation_success(self):
        """Taking a snapshot returns success"""
        response = requests.get(f"{BASE_URL}/api/prices/snapshot")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        print(f"Snapshot result: {data['message']}")
        
    def test_snapshot_captures_entries(self):
        """Snapshot captures price entries"""
        response = requests.get(f"{BASE_URL}/api/prices/snapshot")
        assert response.status_code == 200
        data = response.json()
        # Message should indicate number of captured entries
        assert "Captured" in data["message"]
        # Extract number from message like "Captured 496 price entries"
        parts = data["message"].split()
        if len(parts) >= 2:
            count = int(parts[1])
            # Should capture more than 50 items (verifying no cap in snapshot)
            assert count > 50, f"Snapshot only captured {count} items, should be > 50"
            print(f"Snapshot captured {count} entries")


class TestPriceChanges:
    """Test /api/prices/changes endpoint"""
    
    def test_changes_returns_success(self):
        """Changes endpoint returns success status"""
        response = requests.get(f"{BASE_URL}/api/prices/changes")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
    def test_changes_includes_snapshot_info(self):
        """Changes response includes snapshot timestamps"""
        response = requests.get(f"{BASE_URL}/api/prices/changes")
        assert response.status_code == 200
        data = response.json()
        assert "latest_snapshot" in data
        assert "previous_snapshot" in data
        
    def test_changes_data_structure(self):
        """Changes data has correct structure"""
        response = requests.get(f"{BASE_URL}/api/prices/changes")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        
        # If there are changes, check structure
        if data["data"]:
            change = data["data"][0]
            assert "item_name" in change
            assert "item_type" in change
            assert "old_price" in change
            assert "new_price" in change
            assert "change" in change
            assert "change_pct" in change
            assert "direction" in change
            
    def test_changes_filter_by_type(self):
        """Changes can be filtered by item type"""
        # Test ship filter
        response = requests.get(f"{BASE_URL}/api/prices/changes?item_type=ship")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # If there are results, they should all be ships
        for change in data["data"]:
            assert change["item_type"] == "ship"


class TestPriceHistory:
    """Test /api/prices/history/{item_name} endpoint"""
    
    def test_history_returns_success(self):
        """History endpoint returns success for known item"""
        response = requests.get(f"{BASE_URL}/api/prices/history/Gladius")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
    def test_history_contains_data(self):
        """History returns price data for known item"""
        response = requests.get(f"{BASE_URL}/api/prices/history/Gladius")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        # Gladius should have history entries
        assert len(data["data"]) > 0, "Gladius should have price history"
        
    def test_history_item_structure(self):
        """History items have correct structure"""
        response = requests.get(f"{BASE_URL}/api/prices/history/Gladius")
        assert response.status_code == 200
        data = response.json()
        
        if data["data"]:
            entry = data["data"][0]
            assert "item_name" in entry
            assert "item_type" in entry
            assert "price_auec" in entry
            assert "timestamp" in entry
            
    def test_history_partial_match(self):
        """History supports partial name matching (case-insensitive)"""
        # Should find items containing 'aurora'
        response = requests.get(f"{BASE_URL}/api/prices/history/aurora")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should return multiple Aurora variants
        if data["data"]:
            names = set(entry["item_name"] for entry in data["data"])
            # Aurora LN, Aurora MR, Aurora ES, etc.
            print(f"Found Aurora variants: {names}")
            
    def test_history_unknown_item_empty(self):
        """History returns empty list for unknown item"""
        response = requests.get(f"{BASE_URL}/api/prices/history/NonExistentShipXYZ123")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 0


class TestDataIntegrity:
    """Test data integrity and consistency"""
    
    def test_ships_have_valid_prices(self):
        """Ships in summary have valid price data"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        assert response.status_code == 200
        data = response.json()
        
        ships_with_auec = [s for s in data["data"]["ships"] if s["price_auec"] > 0]
        # Most ships should have aUEC prices
        assert len(ships_with_auec) > 100, f"Only {len(ships_with_auec)} ships have aUEC prices"
        
    def test_ships_have_dealers(self):
        """Ships with prices should have dealer information"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        assert response.status_code == 200
        data = response.json()
        
        ships_with_dealers = [s for s in data["data"]["ships"] if s.get("dealers") and len(s["dealers"]) > 0]
        # Ships with aUEC prices should have dealers
        ships_with_prices = [s for s in data["data"]["ships"] if s["price_auec"] > 0]
        print(f"Ships with prices: {len(ships_with_prices)}, ships with dealers: {len(ships_with_dealers)}")
        # At least half of priced ships should have dealers
        assert len(ships_with_dealers) >= len(ships_with_prices) // 2
        
    def test_weapons_have_locations(self):
        """Weapons should have location information"""
        response = requests.get(f"{BASE_URL}/api/prices/summary")
        assert response.status_code == 200
        data = response.json()
        
        weapons_with_location = [w for w in data["data"]["weapons"] if w.get("location")]
        print(f"Weapons with locations: {len(weapons_with_location)} / {len(data['data']['weapons'])}")
        # Most weapons should have locations
        assert len(weapons_with_location) > len(data["data"]["weapons"]) // 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
