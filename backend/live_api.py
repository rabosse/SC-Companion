"""Live Star Citizen Wiki API integration with automatic fallback to mock data."""

import os
import time
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

SC_API_BASE = "https://api.star-citizen.wiki/api"
API_KEY = os.environ.get("STAR_CITIZEN_API_KEY", "")
MAX_PER_PAGE = 200
CACHE_TTL = 3600  # Refresh data every hour

# Caches
_vehicles_cache: list = []
_weapons_cache: list = []
_components_cache: list = []
_api_available: Optional[bool] = None
_last_fetch_time: float = 0


def _headers():
    h = {"Accept": "application/json"}
    if API_KEY:
        h["Authorization"] = f"Bearer {API_KEY}"
    return h


# Curated per-ship weapon hardpoint data (verified against in-game data)
# Format: ship_name_lowercase -> list of weapon sizes
_CURATED_HARDPOINTS = {
    # === Aegis Dynamics ===
    "gladius": [3, 3, 3],
    "gladius valiant": [3, 3, 3],
    "gladius dunlevy": [3, 3, 3],
    "sabre": [3, 3, 3, 3],
    "sabre comet": [3, 3, 3, 3],
    "sabre firebird": [3, 3, 3, 3],
    "sabre peregrine": [3, 3, 3, 3],
    "sabre raven": [3, 3, 3, 3],
    "avenger titan": [4, 3, 3],
    "avenger titan renegade": [4, 3, 3],
    "avenger stalker": [4, 3, 3],
    "avenger warlock": [4, 3, 3],
    "eclipse": [],
    "vanguard warden": [5, 2, 2, 2, 2],
    "vanguard sentinel": [5, 2, 2, 2, 2],
    "vanguard harbinger": [5, 2, 2, 2, 2],
    "vanguard hoplite": [5, 2, 2, 2, 2],
    "retaliator": [2, 2],
    "retaliator bomber": [2, 2],
    "redeemer": [4, 4, 3, 3],
    "hammerhead": [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    "reclaimer": [],
    "idris-p": [5, 5, 5, 5, 5, 5],
    "idris-m": [7, 5, 5, 5, 5, 5, 5],
    "javelin": [6, 6, 6, 6, 5, 5, 5, 5, 5, 5, 5, 5],
    # === Anvil Aerospace ===
    "arrow": [3, 3, 3, 3],
    "hawk": [3, 3, 2, 2],
    "f7c hornet": [4, 3, 3, 3],
    "f7c hornet mk i": [4, 3, 3, 3],
    "f7c hornet mk ii": [4, 3, 3, 3],
    "f7c hornet wildfire mk i": [4, 3, 3, 3],
    "f7c-m super hornet": [4, 4, 3, 3],
    "f7c-m super hornet mk i": [4, 4, 3, 3],
    "f7c-m super hornet mk ii": [4, 4, 3, 3],
    "f7c-m hornet heartseeker mk i": [4, 4, 3, 3],
    "f7c-m hornet heartseeker mk ii": [4, 4, 3, 3],
    "f7c-s hornet ghost": [4, 3, 3, 3],
    "f7c-s hornet ghost mk i": [4, 3, 3, 3],
    "f7c-s hornet ghost mk ii": [4, 3, 3, 3],
    "f7c-r hornet tracker mk i": [4, 3, 3, 3],
    "f7c-r hornet tracker mk ii": [4, 3, 3, 3],
    "f7a hornet": [4, 4, 3, 3, 3],
    "f7a hornet mk i": [4, 4, 3, 3, 3],
    "f7a hornet mk ii": [4, 4, 3, 3, 3],
    "f7a hornet (military)": [4, 4, 3, 3, 3],
    "hornet f7a mk ii pyam exec": [4, 4, 3, 3, 3],
    "f7 hornet mk wikelo": [4, 3, 3, 3],
    "hurricane": [4, 4, 3, 3],
    "f8 lightning": [4, 4, 3, 3, 3, 3, 3, 3],
    "f8a lightning": [4, 4, 3, 3, 3, 3, 3, 3],
    "f8c lightning": [3, 3, 3, 3, 2, 2, 2, 2],
    "f8c lightning executive edition": [3, 3, 3, 3, 2, 2, 2, 2],
    "gladiator": [3, 3, 3, 3],
    "terrapin": [],
    "terrapin medic": [],
    "valkyrie": [4, 4, 2, 2, 2, 2],
    "carrack": [4, 4, 4, 4],
    "carrack expedition": [4, 4, 4, 4],
    "liberator": [],
    "ballista": [4, 4, 4, 4, 2, 2],
    "centurion": [4, 4, 4, 4, 3],
    "spartan": [2, 2],
    # === Roberts Space Industries ===
    "aurora mr": [3],
    "aurora ln": [3, 3],
    "aurora cl": [3],
    "aurora lx": [3],
    "aurora es": [3],
    "mantis": [3, 3],
    "scorpius": [4, 4, 3, 3],
    "scorpius antares": [4, 4, 3, 3],
    "constellation andromeda": [5, 5, 4, 4],
    "constellation aquila": [5, 5, 4, 4],
    "constellation taurus": [5, 5, 4, 4],
    "constellation phoenix": [5, 5, 4, 4],
    "perseus": [7, 7, 5, 5],
    "polaris": [4, 4, 4, 4],
    "galaxy": [4, 4],
    "meteor": [5, 5, 3, 3, 3, 3],
    "paladin": [5, 5, 4, 4],
    "lynx": [1, 1],
    "zeus mk ii cl": [4, 4, 3, 3],
    "zeus mk ii es": [4, 4, 3, 3],
    # === Crusader Industries ===
    "ares ion": [7],
    "ares inferno": [7],
    "ares star fighter ion": [7],
    "ares star fighter inferno": [7],
    "spirit a1": [3, 3],
    "a1 spirit": [3, 3],
    "spirit c1": [],
    "c1 spirit": [],
    "spirit e1": [],
    "mercury star runner": [3, 3, 2, 2],
    "c2 hercules": [4, 4],
    "c2 hercules starlifter": [4, 4],
    "m2 hercules": [5, 5, 4, 4],
    "m2 hercules starlifter": [5, 5, 4, 4],
    "a2 hercules": [5, 5, 4, 4],
    "a2 hercules starlifter": [5, 5, 4, 4],
    "odyssey": [5, 5, 4, 4],
    "intrepid": [4],
    "starlancer max": [4, 4, 4, 4, 4, 4, 4, 4],
    "starlancer tac": [5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4],
    "hermes": [4, 4],
    # === MISC ===
    "prospector": [],
    "razor": [3, 3],
    "razor ex": [3, 3],
    "razor lx": [3, 3],
    "reliant kore": [3, 3],
    "reliant tana": [3, 3, 3, 3],
    "reliant sen": [3, 3],
    "reliant mako": [3, 3],
    "freelancer": [4, 4, 3, 3],
    "freelancer dur": [4, 4, 3, 3],
    "freelancer max": [4, 4, 3, 3],
    "freelancer mis": [4, 4, 3, 3],
    "hull a": [],
    "hull b": [],
    "hull c": [],
    "starfarer": [4, 4, 3, 3],
    "starfarer gemini": [5, 5, 4, 4, 3, 3],
    "fortune": [],
    # === Drake Interplanetary ===
    "buccaneer": [4, 3, 3, 2, 2],
    "herald": [2, 2],
    "cutlass black": [4, 4, 3, 3],
    "cutlass black pyam exec": [4, 4, 3, 3],
    "cutlass red": [4, 4, 3, 3],
    "cutlass blue": [4, 4, 3, 3],
    "cutlass steel": [4, 4, 3, 3],
    "corsair": [5, 5, 4, 4, 3, 3],
    "corsair pyam exec": [5, 5, 4, 4, 3, 3],
    "caterpillar": [4, 4, 2, 2],
    "vulture": [],
    "clipper": [3, 3, 3, 3],
    "cutter": [2, 2],
    "cutter rambler": [2, 2],
    "cutter scout": [2, 2],
    "shiv": [4, 4, 3, 3, 3, 3],
    # === Consolidated Outland ===
    "mustang alpha": [2, 2],
    "mustang beta": [2, 2],
    "mustang gamma": [3, 3, 2, 2],
    "mustang delta": [3, 3, 2, 2],
    "mustang omega": [3, 3],
    "mustang citizencon 2948 edition": [3, 3],
    "nomad": [3, 3, 3],
    # === Esperia ===
    "blade": [3, 3, 3, 3],
    "glaive": [5, 5],
    "prowler": [4, 4, 3, 3],
    "prowler utility": [4, 4, 3, 3],
    "talon": [3, 3],
    "talon shrike": [],
    "esperia stinger": [5],
    # === Aopoa / Alien ===
    "nox": [],
    "nox kue": [],
    "khartu-al": [3, 3],
    "san'tok.yāi": [4, 4, 3, 3],
    "vanduul scythe": [5, 5],
    "syulen": [3, 3],
    # === Banu ===
    "defender": [3, 3, 2, 2],
    "merchantman": [5, 5, 4, 4, 3, 3, 3, 3],
    # === Argo ===
    "raft": [],
    "mole": [],
    "csv-sm": [],
    "moth": [],
    "srv": [],
    "mpuv cargo": [],
    "mpuv personnel": [],
    "mpuv tractor": [],
    # === Origin ===
    "85x": [2, 2],
    "85x limited": [2, 2],
    "100i": [3, 3],
    "125a": [3, 3],
    "135c": [3, 3],
    "300i": [3, 3],
    "315p": [3, 3],
    "325a": [4, 3, 3],
    "350r": [3, 3],
    "400i": [4, 4, 3, 3],
    "600i explorer": [5, 5, 3, 3],
    "600i touring": [5, 5, 3, 3],
    "600i 2951 bis": [5, 5, 3, 3],
    "890 jump": [5, 5, 4, 4, 3, 3],
    "m50 interceptor": [2, 2],
    # === Kruger ===
    "p-52 merlin": [2, 1, 1],
    "p-72 archimedes": [1, 1, 1, 1],
    "l-21 wolf": [4, 4],
    "l-22 alpha wolf": [4, 4],
    # === Anvil (Pisces) ===
    "c8 pisces": [1, 1],
    "c8r pisces rescue": [1, 1],
    "c8x pisces expedition": [1, 1, 1, 1],
    # === Mirai ===
    "guardian": [5, 5],
    "guardian mx": [4, 4, 4, 4],
    "guardian qi": [5, 5],
    "fury": [2, 2, 2, 2],
    "fury lx": [2, 2, 2, 2],
    "fury mx": [2, 2, 2, 2],
    "pulse": [1, 1],
    "pulse lx": [1, 1],
    # === Drake / Ground ===
    "dragonfly": [2],
    "dragonfly yellowjacket": [2],
    # === Greycat ===
    "mule": [],
    "ptv": [],
    "stv": [],
    "mtc": [2, 2],
    "mdc": [],
    # === RSI / Ground ===
    "roc": [],
    "roc-ds": [],
    "hoverquad": [],
    # === Origin / Ground ===
    "x1": [],
    "x1 force": [],
    "x1 velocity": [],
    # === Misc / Starter ===
    "golem": [],
    "golem ox": [],
    "salvation": [1, 1],
    # === ATLS ===
    "atls": [],
    "atls cool metal color": [],
    "atls geo": [],
    "atls geo ikti": [],
    "atls ikti": [],
    "atls ikti rad": [],
    "atls orange line": [],
    "atls snowland color": [],
    # === Power Suit ===
    "power suit": [],
    # === Anvil / Other ===
    "apollo medivac": [4, 4, 3, 3],
    "apollo triage": [4, 4, 3, 3],
    "asgard": [4, 4],
}


def _get_curated_weapons(ship_name_lower: str, fallback: list) -> list:
    """Get curated weapon hardpoints for a ship, or use the fallback."""
    if ship_name_lower in _CURATED_HARDPOINTS:
        return _CURATED_HARDPOINTS[ship_name_lower]
    # Try partial match
    for key, weapons in _CURATED_HARDPOINTS.items():
        if key in ship_name_lower or ship_name_lower in key:
            return weapons
    return fallback


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

    raw_size_class = v.get("size_class", 0)

    # Derive component slot sizes from size_class
    SLOT_MAP = {
        0: {"shield_size": 1, "power_size": 1, "cooler_size": 1, "qd_size": 1, "shield_count": 1, "power_count": 1, "cooler_count": 1, "qd_count": 1, "weapon_slots": []},
        1: {"shield_size": 0, "power_size": 0, "cooler_size": 0, "qd_size": 0, "shield_count": 0, "power_count": 0, "cooler_count": 0, "qd_count": 0, "weapon_slots": [1, 1]},
        2: {"shield_size": 1, "power_size": 1, "cooler_size": 1, "qd_size": 1, "shield_count": 1, "power_count": 1, "cooler_count": 1, "qd_count": 1, "weapon_slots": [3, 3]},
        3: {"shield_size": 2, "power_size": 2, "cooler_size": 2, "qd_size": 2, "shield_count": 1, "power_count": 1, "cooler_count": 2, "qd_count": 1, "weapon_slots": [4, 4, 3, 3]},
        4: {"shield_size": 2, "power_size": 2, "cooler_size": 2, "qd_size": 2, "shield_count": 2, "power_count": 1, "cooler_count": 2, "qd_count": 1, "weapon_slots": [5, 5, 4, 4]},
        5: {"shield_size": 3, "power_size": 3, "cooler_size": 3, "qd_size": 3, "shield_count": 2, "power_count": 1, "cooler_count": 2, "qd_count": 1, "weapon_slots": [6, 6, 5, 5, 4, 4]},
    }
    slots = SLOT_MAP.get(raw_size_class, SLOT_MAP[0])

    # Use curated per-ship hardpoint data when available, else use SLOT_MAP
    ship_name_lower = (v.get("name", "") or "").lower().strip()
    weapon_slots = _get_curated_weapons(ship_name_lower, slots["weapon_slots"])

    # Per-ship component overrides (verified via starcitizen.tools / RSI)
    _COMPONENT_OVERRIDES = {
        # F8 Lightning series
        "f8c lightning": {"shield_size": 2, "shield_count": 2, "power_size": 2, "power_count": 1, "cooler_size": 1, "cooler_count": 2, "qd_size": 1, "qd_count": 1},
        "f8c lightning executive edition": {"shield_size": 2, "shield_count": 2, "power_size": 2, "power_count": 1, "cooler_size": 1, "cooler_count": 2, "qd_size": 1, "qd_count": 1},
        "f8a lightning": {"shield_size": 2, "shield_count": 2, "power_size": 2, "power_count": 1, "cooler_size": 1, "cooler_count": 2, "qd_size": 1, "qd_count": 1},
        "f8 lightning": {"shield_size": 2, "shield_count": 2, "power_size": 2, "power_count": 1, "cooler_size": 1, "cooler_count": 2, "qd_size": 1, "qd_count": 1},
        # 890 Jump (Capital luxury — size_class wrong in API)
        "890 jump": {"shield_size": 3, "shield_count": 2, "power_size": 3, "power_count": 1, "cooler_size": 3, "cooler_count": 2, "qd_size": 3, "qd_count": 1},
        # Capital ships
        "idris-p": {"shield_size": 3, "shield_count": 2, "power_size": 3, "power_count": 1, "cooler_size": 3, "cooler_count": 2, "qd_size": 3, "qd_count": 1},
        "idris-m": {"shield_size": 3, "shield_count": 2, "power_size": 3, "power_count": 1, "cooler_size": 3, "cooler_count": 2, "qd_size": 3, "qd_count": 1},
        "javelin": {"shield_size": 3, "shield_count": 2, "power_size": 3, "power_count": 1, "cooler_size": 3, "cooler_count": 2, "qd_size": 3, "qd_count": 1},
        "polaris": {"shield_size": 3, "shield_count": 2, "power_size": 3, "power_count": 1, "cooler_size": 3, "cooler_count": 2, "qd_size": 3, "qd_count": 1},
        # Ares (heavy fighters with medium components)
        "ares star fighter ion": {"shield_size": 2, "shield_count": 3, "power_size": 2, "power_count": 2, "cooler_size": 2, "cooler_count": 3, "qd_size": 2, "qd_count": 1},
        "ares star fighter inferno": {"shield_size": 2, "shield_count": 2, "power_size": 2, "power_count": 1, "cooler_size": 2, "cooler_count": 2, "qd_size": 2, "qd_count": 1},
        # Apollo (large hull, medium systems)
        "apollo medivac": {"shield_size": 2, "shield_count": 2, "power_size": 2, "power_count": 1, "cooler_size": 2, "cooler_count": 2, "qd_size": 2, "qd_count": 1},
        "apollo triage": {"shield_size": 2, "shield_count": 2, "power_size": 2, "power_count": 1, "cooler_size": 2, "cooler_count": 2, "qd_size": 2, "qd_count": 1},
        # Starlancer (large multi-crew)
        "starlancer max": {"shield_size": 2, "shield_count": 2, "power_size": 2, "power_count": 1, "cooler_size": 2, "cooler_count": 2, "qd_size": 2, "qd_count": 1},
        "starlancer tac": {"shield_size": 2, "shield_count": 3, "power_size": 2, "power_count": 1, "cooler_size": 2, "cooler_count": 2, "qd_size": 2, "qd_count": 1},
        # Hermes (large cargo)
        "hermes": {"shield_size": 2, "shield_count": 2, "power_size": 2, "power_count": 1, "cooler_size": 2, "cooler_count": 2, "qd_size": 2, "qd_count": 1},
        # Meteor (medium fighter)
        "meteor": {"shield_size": 1, "shield_count": 2, "power_size": 1, "power_count": 1, "cooler_size": 1, "cooler_count": 2, "qd_size": 1, "qd_count": 1},
        # Guardian (medium fighter)
        "guardian": {"shield_size": 1, "shield_count": 2, "power_size": 1, "power_count": 1, "cooler_size": 1, "cooler_count": 1, "qd_size": 1, "qd_count": 1},
        "guardian mx": {"shield_size": 1, "shield_count": 2, "power_size": 1, "power_count": 1, "cooler_size": 1, "cooler_count": 1, "qd_size": 1, "qd_count": 1},
        "guardian qi": {"shield_size": 1, "shield_count": 2, "power_size": 1, "power_count": 1, "cooler_size": 1, "cooler_count": 1, "qd_size": 1, "qd_count": 1},
        # 600i BIS (large ship, not capital)
        "600i 2951 bis": {"shield_size": 3, "shield_count": 2, "power_size": 3, "power_count": 1, "cooler_size": 3, "cooler_count": 2, "qd_size": 3, "qd_count": 1},
    }
    comp_override = _COMPONENT_OVERRIDES.get(ship_name_lower, {})

    # Extract quantum drive data from API
    quantum = v.get("quantum") or {}
    qd_speed_raw = quantum.get("quantum_speed", 0)  # m/s
    qd_fuel_cap = quantum.get("quantum_fuel_capacity", 0)
    qd_range_raw = quantum.get("quantum_range", 0)  # metres
    qd_speed_kms = round(qd_speed_raw / 1000) if qd_speed_raw else 0
    qd_range_mkm = round(qd_range_raw / 1_000_000_000, 1) if qd_range_raw else 0

    return {
        "id": v.get("slug", v.get("uuid", "")),
        "name": v.get("name", "").replace("\\n", "").strip(),
        "manufacturer": manufacturer_name,
        "size": size_class,
        "size_class": raw_size_class,
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
        "role": v.get("role", "Multi-role") or "Multi-role",
        "armor": "Medium" if size_class in ["Medium", "Large"] else "Light",
        "description": (v.get("description", {}).get("en_EN", "") if isinstance(v.get("description"), dict) else "") or f"The {v.get('name', '')} is a versatile vessel.",
        "is_ground_vehicle": is_ground,
        "image": "",
        "msrp": v.get("msrp", 0),
        "pledge_url": v.get("pledge_url", ""),
        # Quantum drive data from API
        "quantum": {
            "speed_kms": qd_speed_kms,
            "fuel_capacity": qd_fuel_cap,
            "range_mkm": qd_range_mkm,
            "spool_time": quantum.get("quantum_spool_time", 4),
        },
        # Hardpoint data for loadout builder
        "hardpoints": {
            "shield": {"size": comp_override.get("shield_size", slots["shield_size"]), "count": comp_override.get("shield_count", slots["shield_count"])},
            "power_plant": {"size": comp_override.get("power_size", slots["power_size"]), "count": comp_override.get("power_count", slots["power_count"])},
            "cooler": {"size": comp_override.get("cooler_size", slots["cooler_size"]), "count": comp_override.get("cooler_count", slots["cooler_count"])},
            "quantum_drive": {"size": comp_override.get("qd_size", slots["qd_size"]), "count": comp_override.get("qd_count", slots["qd_count"])},
            "weapons": weapon_slots,
        },
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


def _cache_stale() -> bool:
    """Check if cache needs refresh."""
    return (time.time() - _last_fetch_time) > CACHE_TTL


async def fetch_live_vehicles() -> list:
    """Fetch all vehicles/ships from the live API."""
    global _vehicles_cache, _api_available, _last_fetch_time
    if _vehicles_cache and not _cache_stale():
        return _vehicles_cache

    try:
        logger.info("Fetching live vehicle data from Star Citizen Wiki API...")
        raw = await _fetch_paginated("vehicles")
        vehicles = [_normalize_vehicle(v) for v in raw]
        _vehicles_cache = vehicles
        _api_available = True
        _last_fetch_time = time.time()
        logger.info(f"Live API: fetched {len(vehicles)} vehicles")
        return vehicles
    except Exception as e:
        logger.error(f"Live API vehicles fetch failed: {e}")
        _api_available = False
        return _vehicles_cache or []


async def fetch_live_weapons() -> list:
    """Fetch all weapon items from the live API."""
    global _weapons_cache
    if _weapons_cache and not _cache_stale():
        return _weapons_cache

    try:
        logger.info("Fetching live weapon data from Star Citizen Wiki API...")
        raw = await _fetch_paginated("items", {"filter[type]": "WeaponGun"})
        weapons = [_normalize_weapon(w) for w in raw]
        weapons = [w for w in weapons if w["name"] and w["damage"] > 0]
        _weapons_cache = weapons
        logger.info(f"Live API: fetched {len(weapons)} weapons")
        return weapons
    except Exception as e:
        logger.error(f"Live API weapons fetch failed: {e}")
        return _weapons_cache or []


async def fetch_live_components() -> list:
    """Fetch all component items from the live API."""
    global _components_cache
    if _components_cache and not _cache_stale():
        return _components_cache

    try:
        logger.info("Fetching live component data from Star Citizen Wiki API...")
        all_components = []
        for comp_type in ["Shield", "PowerPlant", "Cooler", "QuantumDrive", "Radar"]:
            raw = await _fetch_paginated("items", {"filter[type]": comp_type})
            normalized = [_normalize_component(item, comp_type) for item in raw]
            all_components.extend(normalized)

        all_components = [c for c in all_components if c["name"]]
        _components_cache = all_components
        logger.info(f"Live API: fetched {len(all_components)} components")
        return all_components
    except Exception as e:
        logger.error(f"Live API components fetch failed: {e}")
        return _components_cache or []


async def prefetch_all():
    """Prefetch all data on startup."""
    global _last_fetch_time
    await fetch_live_vehicles()
    await fetch_live_weapons()
    await fetch_live_components()
    _last_fetch_time = time.time()


def is_api_available() -> bool:
    """Check if the live API was reachable."""
    return _api_available is True
