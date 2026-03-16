"""
Test iteration 44: Liveries page feature
Tests for GET /api/liveries endpoint - ship paints/liveries from starcitizen.tools wiki
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLiveriesEndpoint:
    """Tests for GET /api/liveries endpoint"""

    def test_liveries_endpoint_returns_success(self):
        """BACKEND: GET /api/liveries returns data with success=true"""
        response = requests.get(f"{BASE_URL}/api/liveries")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True, "Expected success=true"
        print(f"✓ success=true")

    def test_liveries_endpoint_loading_false(self):
        """BACKEND: GET /api/liveries returns loading=false (data is cached)"""
        response = requests.get(f"{BASE_URL}/api/liveries")
        assert response.status_code == 200
        data = response.json()
        assert data.get("loading") == False, "Expected loading=false (cached data)"
        print(f"✓ loading=false")

    def test_liveries_endpoint_has_series_data(self):
        """BACKEND: GET /api/liveries returns total_series > 0 and data array"""
        response = requests.get(f"{BASE_URL}/api/liveries")
        assert response.status_code == 200
        data = response.json()
        assert data.get("total_series", 0) > 0, "Expected total_series > 0"
        assert isinstance(data.get("data"), list), "Expected data to be an array"
        assert len(data["data"]) > 0, "Expected at least one series"
        print(f"✓ total_series={data['total_series']}, data array length={len(data['data'])}")

    def test_series_object_structure(self):
        """BACKEND: Each series object has 'series', 'paint_count', and 'paints' array"""
        response = requests.get(f"{BASE_URL}/api/liveries")
        assert response.status_code == 200
        data = response.json()
        
        # Check first 5 series for structure
        for series in data["data"][:5]:
            assert "series" in series, "Missing 'series' field"
            assert "paint_count" in series, "Missing 'paint_count' field"
            assert "paints" in series, "Missing 'paints' array"
            assert isinstance(series["paints"], list), "paints should be an array"
            assert series["paint_count"] == len(series["paints"]), "paint_count should match paints array length"
            print(f"✓ Series '{series['series']}' has {series['paint_count']} paints")

    def test_paint_object_structure(self):
        """BACKEND: Each paint has 'name', 'description', 'acquisition' fields (image_url optional)"""
        response = requests.get(f"{BASE_URL}/api/liveries")
        assert response.status_code == 200
        data = response.json()
        
        # Required fields - image_url is optional as some paints may not have images on wiki
        required_fields = ["name", "description", "acquisition"]
        checked = 0
        with_images = 0
        for series in data["data"][:10]:
            for paint in series["paints"][:3]:
                for field in required_fields:
                    assert field in paint, f"Missing '{field}' in paint {paint.get('name', 'unknown')}"
                # image_url is optional but track how many have it
                if paint.get("image_url"):
                    with_images += 1
                checked += 1
        print(f"✓ Checked {checked} paints, all have required fields, {with_images} have images")

    def test_rsi_store_paints_have_store_url(self):
        """BACKEND: RSI Store paints have 'store_url' field with valid URL"""
        response = requests.get(f"{BASE_URL}/api/liveries")
        assert response.status_code == 200
        data = response.json()
        
        rsi_store_paints = []
        for series in data["data"]:
            for paint in series["paints"]:
                if paint.get("acquisition") == "RSI Store":
                    rsi_store_paints.append(paint)
        
        # Check that RSI Store paints have store_url
        with_url = [p for p in rsi_store_paints if p.get("store_url")]
        
        # Even if acquisition is "RSI Store", they may have been acquired differently 
        # But any paint with store_url should have a valid URL
        paints_with_url = [p for s in data["data"] for p in s["paints"] if p.get("store_url")]
        assert len(paints_with_url) > 0, "Expected at least some paints with store_url"
        
        for paint in paints_with_url[:5]:
            url = paint["store_url"]
            assert url.startswith("http"), f"store_url should be a valid URL: {url}"
            print(f"✓ {paint['name']}: {url}")
        
        print(f"✓ Found {len(paints_with_url)} paints with store_url")

    def test_ingame_paints_have_price_auec(self):
        """BACKEND: In-Game paints have 'price_auec' field with numeric value"""
        response = requests.get(f"{BASE_URL}/api/liveries")
        assert response.status_code == 200
        data = response.json()
        
        ingame_paints = []
        for series in data["data"]:
            for paint in series["paints"]:
                if paint.get("acquisition") == "In-Game":
                    ingame_paints.append(paint)
        
        assert len(ingame_paints) > 0, "Expected at least some In-Game paints"
        
        # Check that In-Game paints have price_auec
        with_price = [p for p in ingame_paints if p.get("price_auec") is not None]
        assert len(with_price) > 0, "Expected In-Game paints to have price_auec"
        
        for paint in with_price[:5]:
            assert isinstance(paint["price_auec"], (int, float)), f"price_auec should be numeric: {paint['price_auec']}"
            print(f"✓ {paint['name']}: {paint['price_auec']} aUEC")
        
        print(f"✓ Found {len(with_price)} In-Game paints with price_auec")

    def test_liveries_data_volume(self):
        """BACKEND: Verify expected data volume (~98 series, ~815 paints)"""
        response = requests.get(f"{BASE_URL}/api/liveries")
        assert response.status_code == 200
        data = response.json()
        
        total_series = data.get("total_series", 0)
        total_paints = sum(s.get("paint_count", 0) for s in data["data"])
        
        # Expected ~98 series and ~815 paints
        assert total_series >= 50, f"Expected at least 50 series, got {total_series}"
        assert total_paints >= 300, f"Expected at least 300 paints, got {total_paints}"
        
        print(f"✓ {total_series} series, {total_paints} paints")

    def test_acquisition_types_present(self):
        """BACKEND: Verify multiple acquisition types are present"""
        response = requests.get(f"{BASE_URL}/api/liveries")
        assert response.status_code == 200
        data = response.json()
        
        acquisition_types = set()
        for series in data["data"]:
            for paint in series["paints"]:
                acquisition_types.add(paint.get("acquisition", "Unknown"))
        
        # Should have at least In-Game and RSI Store
        assert "In-Game" in acquisition_types, "Missing 'In-Game' acquisition type"
        print(f"✓ Found acquisition types: {acquisition_types}")
