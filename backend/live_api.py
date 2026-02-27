"""Live Star Citizen Wiki API integration with automatic fallback to mock data."""

import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

SC_API_BASE = "https://api.star-citizen.wiki/api"
API_KEY = os.environ.get("STAR_CITIZEN_API_KEY", "")
MAX_PER_PAGE = 200

# Caches
_vehicles_cache: list = []
_weapons_cache: list = []
_components_cache: list = []
_api_available: Optional[bool] = None


def _headers():
    h = {"Accept": "application/json"}
    if API_KEY:
        h["Authorization"] = f"Bearer {API_KEY}"
    return h


async def _fetch_paginated(endpoint: str, params: dict = None) -> list:
    """Fetch all pages from a paginated API endpoint."""
    if params is None:
        params = {}
    params["limit"] = MAX_PER_PAGE
    all_data = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        page = 1
        while True:
            params["page"] = page
            resp = await client.get(f"{SC_API_BASE}/{endpoint}", params=params, headers=_headers(), follow_redirects=True)
            resp.raise_for_status()
            body = resp.json()
            data = body.get("data", [])
            all_data.extend(data)
            meta = body.get("meta", {})
            if page >= meta.get("last_page", 1):
                break
            page += 1
    return all_data


def _normalize_vehicle(v: dict) -> dict:
    """Transform API vehicle data to our app format."""
    sizes = v.get("sizes") or {}
    dimension = v.get("dimension") or {}
    crew = v.get("crew") or {}
    speed = v.get("speed") or {}

    length = sizes.get("length") or dimension.get("length") or 0
    beam = sizes.get("beam") or dimension.get("width") or 0
    height = sizes.get("height") or dimension.get("height") or 0

    # Determine size class from length
    if length <= 15:
        size_class = "Snub"
    elif length <= 30:
        size_class = "Small"
    elif length <= 60:
        size_class = "Medium"
    elif length <= 150:
        size_class = "Large"
    else:
        size_class = "Capital"

    # Determine if ground vehicle
    is_ground = v.get("class_name", "").startswith("TMBL") or \
                v.get("class_name", "").startswith("RSI_Ursa") or \
                "Ground" in (v.get("classification") or "") or \
                speed.get("scm", 0) == 0

    manufacturer_name = ""
    if v.get("manufacturer"):
        if isinstance(v["manufacturer"], dict):
            manufacturer_name = v["manufacturer"].get("name", "")
        else:
            manufacturer_name = str(v["manufacturer"])

    # Estimate price from size
    price_map = {"Snub": 50000, "Small": 100000, "Medium": 500000, "Large": 2000000, "Capital": 10000000}

    return {
        "id": v.get("slug", v.get("uuid", "")),
        "name": v.get("name", ""),
        "manufacturer": manufacturer_name,
        "size": size_class,
        "length": round(length, 1),
        "beam": round(beam, 1),
        "height": round(height, 1),
        "mass": v.get("mass") or v.get("mass_hull") or 0,
        "crew_min": crew.get("min", 1),
        "crew_max": crew.get("max", 1),
        "cargo": v.get("cargo_capacity", 0),
        "max_speed": speed.get("scm", 0),
        "max_speed_boost": speed.get("boost_forward", 0),
        "health": v.get("health", 0),
        "shield_hp": v.get("shield_hp", 0),
        "price": price_map.get(size_class, 100000),
        "role": "Multi-role",
        "armor": "Medium" if size_class in ["Medium", "Large"] else "Light",
        "description": (v.get("description", {}).get("en_EN", "") if isinstance(v.get("description"), dict) else "") or f"The {v.get('name', '')} is a versatile vessel.",
        "is_ground_vehicle": is_ground,
        "image": "",
    }


def _extract_best_price(item: dict) -> dict:
    """Extract best (lowest) buy price and location from uex_prices."""
    uex = item.get("uex_prices", [])
    best_price = None
    best_location = ""
    for p in uex:
        buy = p.get("price_buy", 0)
        if buy and buy > 0:
            if best_price is None or buy < best_price:
                best_price = buy
                best_location = p.get("terminal_name", "").strip()
    return {"cost_auec": best_price or 0, "location": best_location or "Unknown"}


def _normalize_weapon(item: dict) -> dict:
    """Transform API weapon item to our app format."""
    vw = item.get("vehicle_weapon") or {}
    mfg = item.get("manufacturer") or {}

    weapon_type = "Energy"
    vw_type = (vw.get("type") or "").lower()
    if "ballistic" in vw_type:
        weapon_type = "Ballistic"
    elif "missile" in vw_type or "torpedo" in vw_type:
        weapon_type = "Missile"

    price_info = _extract_best_price(item)

    return {
        "id": item.get("uuid", ""),
        "name": item.get("name", ""),
        "type": weapon_type,
        "manufacturer": mfg.get("name", "") if isinstance(mfg, dict) else str(mfg),
        "size": str(item.get("size", 1)),
        "damage": round(vw.get("damage_per_shot", 0), 1),
        "rate": vw.get("rpm", 0),
        "ammo_per_mag": vw.get("capacity", 0) if weapon_type == "Ballistic" else None,
        "location": price_info["location"],
        "cost_auec": price_info["cost_auec"],
    }


def _normalize_component(item: dict, comp_type: str) -> dict:
    """Transform API component item to our app format."""
    mfg = item.get("manufacturer") or {}
    price_info = _extract_best_price(item)

    # Get type-specific stats
    power = 0
    output = 0
    rate = 0
    speed_val = 0
    range_val = 0

    if comp_type == "Shield":
        shield = item.get("shield") or {}
        output = shield.get("max_health", 0)
        rate = shield.get("regen_rate", 0)
    elif comp_type == "PowerPlant":
        pp = item.get("power_plant") or {}
        output = pp.get("power_output", 0)
    elif comp_type == "Cooler":
        cool = item.get("cooler") or {}
        output = cool.get("cooling_rate", 0)
    elif comp_type == "QuantumDrive":
        qd = item.get("quantum_drive") or {}
        speed_val = qd.get("quantum_speed", 0)
        range_val = qd.get("range", 0)
    elif comp_type == "Radar":
        radar = item.get("radar") or {}
        range_val = radar.get("range", 0)

    # Map type name for UI
    type_map = {
        "Shield": "Shield",
        "PowerPlant": "Power",
        "Cooler": "Cooler",
        "QuantumDrive": "Quantum",
        "Radar": "Radar",
    }

    return {
        "id": item.get("uuid", ""),
        "name": item.get("name", ""),
        "type": type_map.get(comp_type, comp_type),
        "manufacturer": mfg.get("name", "") if isinstance(mfg, dict) else str(mfg),
        "size": str(item.get("size", 1)),
        "grade": item.get("grade", "C"),
        "power": power,
        "output": output,
        "rate": rate,
        "speed": speed_val,
        "range": range_val,
        "location": price_info["location"],
        "cost_auec": price_info["cost_auec"],
    }


async def fetch_live_vehicles() -> list:
    """Fetch all vehicles/ships from the live API."""
    global _vehicles_cache, _api_available
    if _vehicles_cache:
        return _vehicles_cache

    try:
        logger.info("Fetching live vehicle data from Star Citizen Wiki API...")
        raw = await _fetch_paginated("vehicles")
        vehicles = [_normalize_vehicle(v) for v in raw]
        _vehicles_cache = vehicles
        _api_available = True
        logger.info(f"Live API: fetched {len(vehicles)} vehicles")
        return vehicles
    except Exception as e:
        logger.error(f"Live API vehicles fetch failed: {e}")
        _api_available = False
        return []


async def fetch_live_weapons() -> list:
    """Fetch all weapon items from the live API."""
    global _weapons_cache
    if _weapons_cache:
        return _weapons_cache

    try:
        logger.info("Fetching live weapon data from Star Citizen Wiki API...")
        raw = await _fetch_paginated("items", {"filter[type]": "WeaponGun"})
        weapons = [_normalize_weapon(w) for w in raw]
        # Filter out items with no useful data
        weapons = [w for w in weapons if w["name"] and w["damage"] > 0]
        _weapons_cache = weapons
        logger.info(f"Live API: fetched {len(weapons)} weapons")
        return weapons
    except Exception as e:
        logger.error(f"Live API weapons fetch failed: {e}")
        return []


async def fetch_live_components() -> list:
    """Fetch all component items from the live API."""
    global _components_cache
    if _components_cache:
        return _components_cache

    try:
        logger.info("Fetching live component data from Star Citizen Wiki API...")
        all_components = []
        for comp_type in ["Shield", "PowerPlant", "Cooler", "QuantumDrive", "Radar"]:
            raw = await _fetch_paginated("items", {"filter[type]": comp_type})
            normalized = [_normalize_component(item, comp_type) for item in raw]
            all_components.extend(normalized)

        # Filter out items with no name
        all_components = [c for c in all_components if c["name"]]
        _components_cache = all_components
        logger.info(f"Live API: fetched {len(all_components)} components")
        return all_components
    except Exception as e:
        logger.error(f"Live API components fetch failed: {e}")
        return []


async def prefetch_all():
    """Prefetch all data on startup."""
    await fetch_live_vehicles()
    await fetch_live_weapons()
    await fetch_live_components()


def is_api_available() -> bool:
    """Check if the live API was reachable."""
    return _api_available is True
