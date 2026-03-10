"""CStone Finder API integration - Primary data source for Star Citizen items.

Fetches data from finder.cstone.space JSON endpoints and caches it in-memory.
Provides normalized data for vehicle components, ship weapons, FPS weapons, armor,
and vehicle purchase information.
"""

import time
import httpx
import logging
from typing import Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

CSTONE_BASE = "https://finder.cstone.space"
CSTONE_IMG_BASE = "https://cstone.space/uifimages"
CACHE_TTL = 3600  # 1 hour
_last_fetch: float = 0

# In-memory caches
_coolers: list = []
_power_plants: list = []
_quantum_drives: list = []
_shields: list = []
_ship_weapons: list = []
_missiles: list = []
_missile_racks: list = []
_turrets: list = []
_fps_weapons: list = []
_fps_melee: list = []
_fps_attachments: list = []
_armor_helmets: list = []
_armor_torsos: list = []
_armor_arms: list = []
_armor_legs: list = []
_armor_backpacks: list = []
_armor_undersuits: list = []
_ship_shops: list = []
_flight_blades: list = []
_life_support: list = []
_jump_drives: list = []

# Location cache: ItemId -> list of {location, price, verified}
_location_cache: dict = {}


def _cache_stale() -> bool:
    return (time.time() - _last_fetch) > CACHE_TTL


async def _fetch_json(endpoint: str) -> list:
    """Fetch JSON data from a CStone endpoint."""
    url = f"{CSTONE_BASE}{endpoint}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"CStone fetch failed for {endpoint}: {e}")
        return []


async def _fetch_item_locations(item_id: str) -> list:
    """Fetch purchase locations for a specific item from its detail page."""
    if item_id in _location_cache:
        return _location_cache[item_id]
    url = f"{CSTONE_BASE}/Search/{item_id}"
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            tables = soup.find_all("table")
            for t in tables:
                    headers = [th.text.strip() for th in t.find_all("th")]
                    if any("LOCATION" in h.upper() for h in headers):
                        locations = []
                        for row in t.find_all("tr"):
                            cells = [td.text.strip() for td in row.find_all("td")]
                            if len(cells) >= 2 and cells[0] and "Not Sold" not in cells[0]:
                                price_str = cells[1].replace("\xa0", "").replace(" ", "").strip()
                                try:
                                    price = int(price_str)
                                except (ValueError, TypeError):
                                    price = 0
                                locations.append({
                                    "location": cells[0],
                                    "price": price,
                                    "verified": cells[2] if len(cells) > 2 else "",
                                })
                        _location_cache[item_id] = locations
                        return locations
    except Exception as e:
        logger.debug(f"Failed to fetch locations for {item_id}: {e}")
    _location_cache[item_id] = []
    return []


def _norm_component(item: dict, comp_type: str) -> dict:
    """Normalize a CStone component item to our app format."""
    item_class = (item.get("ItemClass", "") or "").strip()
    grade = (item.get("Grade", "") or "").strip()

    base = {
        "id": item.get("ItemId", ""),
        "name": item.get("Name", ""),
        "type": comp_type,
        "manufacturer": item.get("Manu", ""),
        "size": str(item.get("Size", "")),
        "grade": grade,
        "item_class": item_class,
        "description": item.get("Desc", ""),
        "sold": item.get("Sold", 0) == 1,
        "durability": item.get("Durability", 0),
        "power_draw": item.get("Powerdraw", 0),
        "volume": item.get("Volume", 0),
    }

    if comp_type == "Cooler":
        base["output"] = item.get("CoolingRate", 0)
        base["rate"] = item.get("CoolingRate", 0)
    elif comp_type == "Power":
        base["output"] = item.get("Powergen", 0)
        base["coolant_draw"] = item.get("Coolantdraw", 0)
    elif comp_type == "Shield":
        base["output"] = item.get("Maxshield", 0)
        base["rate"] = item.get("ShieldRegen", 0)
        base["damage_delay"] = item.get("DmgDelay", 0)
        base["downed_delay"] = item.get("DownedDelay", 0)
    elif comp_type == "Quantum":
        base["speed"] = item.get("DriveSpeed", 0)
        base["fuel_requirement"] = item.get("QuantumFuelRequirement", 0)
        base["spool_time"] = item.get("SpoolUpTime", 0)
        base["stage1_accel"] = item.get("StageOneAccelRate", 0)
        base["stage2_accel"] = item.get("StageTwoAccelRate", 0)
        base["calibration_rate"] = item.get("CalibrationRate", 0)
        base["cooldown_time"] = item.get("CooldownTime", 0)

    return base


def _norm_ship_weapon(item: dict) -> dict:
    """Normalize a CStone ship weapon."""
    return {
        "id": item.get("ItemId", ""),
        "name": item.get("Name", ""),
        "type": item.get("Shipweapontype", item.get("Type", "Weapon")),
        "manufacturer": item.get("Manu", ""),
        "size": str(item.get("Size", "")),
        "grade": item.get("Grade", ""),
        "alpha_damage": item.get("Alphadmg", 0),
        "dps": item.get("Dps", 0),
        "fire_rate": item.get("Firerate", 0),
        "rate": item.get("Firerate", 0),
        "range": item.get("Firerange", 0),
        "ammo_speed": item.get("Ammospeed", 0),
        "max_ammo": item.get("Maxammoshipgunammo", 0),
        "power_draw": item.get("Powerdraw", 0),
        "damage": item.get("Alphadmg", 0),
        "sold": item.get("Sold", 0) == 1,
        "volume": item.get("Volume", 0),
        "description": item.get("Desc", ""),
    }


def _norm_fps_weapon(item: dict) -> dict:
    """Normalize a CStone FPS weapon."""
    item_id = item.get("ItemId", "")
    return {
        "id": item_id,
        "name": item.get("Name", ""),
        "type": item.get("Type", item.get("ItemClass", "Unknown")),
        "manufacturer": item.get("Manu", ""),
        "magazine_capacity": item.get("Magcapacity", 0),
        "bullet_speed": item.get("Bulletspeed", 0),
        "alpha_damage": item.get("Personalalphadmg", 0),
        "max_fire_rate": item.get("Fpsmaxfirerate", 0),
        "max_dps": item.get("Fpsmaxdps", 0),
        "single_fire_rate": item.get("Fpssfirerate", 0),
        "single_dps": item.get("Fpssdps", 0),
        "burst_fire_rate": item.get("Fpsbfirerate", 0),
        "burst_dps": item.get("Fpsbdps", 0),
        "rapid_fire_rate": item.get("Fpsrfirerate", 0),
        "rapid_dps": item.get("Fpsrdps", 0),
        "optics_attach": item.get("OpticsAttach", False),
        "barrel_attach": item.get("BarrelAttach", False),
        "underbarrel_attach": item.get("UnderbarrelAttach", False),
        "sold": item.get("Sold", 0) == 1,
        "volume": item.get("Volume", 0),
        "description": item.get("Desc", ""),
        "image": f"{CSTONE_IMG_BASE}/{item_id}.png" if item_id else "",
    }


def _norm_armor(item: dict, slot: str) -> dict:
    """Normalize a CStone armor piece."""
    item_id = item.get("ItemId", "")
    return {
        "id": item_id,
        "name": item.get("Name", ""),
        "slot": slot,
        "type": item.get("Atype", item.get("Type", "")),
        "manufacturer": item.get("Manu", ""),
        "damage_reduction": item.get("Dmgred", ""),
        "physical_resistance": item.get("ArmordmgreductionPhysicalResistance", ""),
        "energy_resistance": item.get("ArmordmgreductionEnergyResistance", ""),
        "distortion_resistance": item.get("ArmordmgreductionDistortionResistance", ""),
        "thermal_resistance": item.get("ArmordmgreductionThermalResistance", ""),
        "biochemical_resistance": item.get("ArmordmgreductionBiochemicalResistance", ""),
        "stun_resistance": item.get("ArmordmgreductionStunResistance", ""),
        "min_temp": item.get("Wearmintemp", 0),
        "max_temp": item.get("Wearmaxtemp", 0),
        "radiation_resistance": item.get("Radresistance", 0),
        "radiation_scrub_rate": item.get("Radscrubrate", 0),
        "cargo": item.get("Acargo", 0),
        "sold": item.get("Sold", 0) == 1,
        "volume": item.get("Volume", 0),
        "description": item.get("Desc", ""),
        "image": f"{CSTONE_IMG_BASE}/{item_id}.png" if item_id else "",
    }


def _norm_ship_shop(item: dict) -> dict:
    """Normalize a CStone vehicle shop entry."""
    desc = item.get("Desc", "")
    focus = ""
    if "Focus:" in desc:
        parts = desc.split("Focus:")
        if len(parts) > 1:
            focus = parts[1].split("\\n")[0].strip().replace("\xa0", " ")

    return {
        "id": item.get("ItemId", ""),
        "code_name": item.get("ItemCodeName", ""),
        "name": item.get("Name", ""),
        "manufacturer": item.get("Manu", ""),
        "focus": focus,
        "sold": item.get("Sold", 0) == 1,
        "rentable": item.get("Rent", 0) == 1,
        "length": item.get("Length", 0),
        "width": item.get("Width", 0),
        "volume": item.get("Volume", 0),
        "description": desc,
    }


def _norm_missile(item: dict) -> dict:
    """Normalize a CStone missile."""
    return {
        "id": item.get("ItemId", ""),
        "name": item.get("Name", ""),
        "type": item.get("Type", ""),
        "manufacturer": item.get("Manu", ""),
        "size": str(item.get("Size", "")),
        "grade": item.get("Grade", ""),
        "lock_time": item.get("LockTime", 0),
        "tracking_signal_min": item.get("TrackingSignalMin", 0),
        "tracking_signal_type": item.get("TrackingSignalType", ""),
        "linear_speed": item.get("LinearSpeed", 0),
        "damage": item.get("Misdmg", 0),
        "lock_range_min": item.get("Lockmin", 0),
        "lock_range_max": item.get("Lockmax", 0),
        "sold": item.get("Sold", 0) == 1,
        "volume": item.get("Volume", 0),
        "description": item.get("Desc", ""),
    }


async def prefetch_cstone_data():
    """Fetch all CStone data and populate caches."""
    global _coolers, _power_plants, _quantum_drives, _shields
    global _ship_weapons, _missiles, _missile_racks, _turrets
    global _fps_weapons, _fps_melee, _fps_attachments
    global _armor_helmets, _armor_torsos, _armor_arms, _armor_legs
    global _armor_backpacks, _armor_undersuits, _ship_shops
    global _flight_blades, _life_support, _jump_drives
    global _last_fetch

    if not _cache_stale() and _coolers:
        return

    logger.info("Fetching CStone Finder data...")

    # Fetch all component categories
    raw_coolers = await _fetch_json("/GetCoolers")
    raw_powers = await _fetch_json("/GetPowers")
    raw_drives = await _fetch_json("/GetDrives")
    raw_shields = await _fetch_json("/GetShields")
    raw_sweapons = await _fetch_json("/GetSWeapons")
    raw_missiles = await _fetch_json("/GetMissiles")
    raw_fps = await _fetch_json("/GetFPSWeapons")
    raw_melee = await _fetch_json("/GetFPSWeaponMelee")
    raw_shops = await _fetch_json("/GetSShops")

    # Armor categories
    raw_helmets = await _fetch_json("/GetArmors/Helmets")
    raw_torsos = await _fetch_json("/GetArmors/Torsos")
    raw_arms = await _fetch_json("/GetArmors/Arms")
    raw_legs = await _fetch_json("/GetArmors/Legs")
    raw_backpacks = await _fetch_json("/GetArmors/Backpacks")
    raw_undersuits = await _fetch_json("/GetArmors/Undersuits")

    # Normalize
    _coolers = [_norm_component(c, "Cooler") for c in raw_coolers]
    _power_plants = [_norm_component(p, "Power") for p in raw_powers]
    _quantum_drives = [_norm_component(q, "Quantum") for q in raw_drives]
    _shields = [_norm_component(s, "Shield") for s in raw_shields]
    _ship_weapons = [_norm_ship_weapon(w) for w in raw_sweapons]
    _missiles = [_norm_missile(m) for m in raw_missiles]
    _fps_weapons = [_norm_fps_weapon(w) for w in raw_fps]
    _fps_melee = [_norm_fps_weapon(w) for w in raw_melee]
    _ship_shops = [_norm_ship_shop(s) for s in raw_shops]

    _armor_helmets = [_norm_armor(a, "Helmet") for a in raw_helmets]
    _armor_torsos = [_norm_armor(a, "Torso") for a in raw_torsos]
    _armor_arms = [_norm_armor(a, "Arms") for a in raw_arms]
    _armor_legs = [_norm_armor(a, "Legs") for a in raw_legs]
    _armor_backpacks = [_norm_armor(a, "Backpack") for a in raw_backpacks]
    _armor_undersuits = [_norm_armor(a, "Undersuit") for a in raw_undersuits]

    _last_fetch = time.time()

    total = (len(_coolers) + len(_power_plants) + len(_quantum_drives) +
             len(_shields) + len(_ship_weapons) + len(_missiles) +
             len(_fps_weapons) + len(_fps_melee) + len(_ship_shops) +
             len(_armor_helmets) + len(_armor_torsos) + len(_armor_arms) +
             len(_armor_legs) + len(_armor_backpacks) + len(_armor_undersuits))
    logger.info(f"CStone: loaded {total} items across all categories")


# === Public accessors ===

def get_all_components() -> list:
    """Get all vehicle components (coolers, power plants, quantum drives, shields)."""
    return _coolers + _power_plants + _quantum_drives + _shields


def get_components_by_type(comp_type: str) -> list:
    type_map = {
        "cooler": _coolers,
        "power": _power_plants,
        "quantum": _quantum_drives,
        "shield": _shields,
    }
    return type_map.get(comp_type.lower(), [])


def get_ship_weapons() -> list:
    return _ship_weapons


def get_missiles_list() -> list:
    return _missiles


def get_fps_weapons() -> list:
    return _fps_weapons + _fps_melee


def get_all_armor() -> list:
    return (_armor_helmets + _armor_torsos + _armor_arms +
            _armor_legs + _armor_backpacks + _armor_undersuits)


def get_armor_by_slot(slot: str) -> list:
    slot_map = {
        "helmet": _armor_helmets,
        "torso": _armor_torsos,
        "arms": _armor_arms,
        "legs": _armor_legs,
        "backpack": _armor_backpacks,
        "undersuit": _armor_undersuits,
    }
    return slot_map.get(slot.lower(), [])


def get_ship_shops() -> list:
    return _ship_shops


async def get_item_locations(item_id: str) -> list:
    """Get purchase locations for a specific item."""
    return await _fetch_item_locations(item_id)


async def batch_fetch_locations(item_ids: list):
    """Fetch locations for multiple items concurrently with rate limiting."""
    import asyncio
    sem = asyncio.Semaphore(15)

    async def _fetch_one(item_id):
        async with sem:
            return await _fetch_item_locations(item_id)

    tasks = [_fetch_one(iid) for iid in item_ids if iid not in _location_cache]
    if tasks:
        logger.info(f"Batch fetching locations for {len(tasks)} items...")
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"Location cache size: {len(_location_cache)}")


def get_cached_locations(item_id: str) -> list:
    """Get locations from cache without fetching. Returns empty list if not cached."""
    return _location_cache.get(item_id, [])
