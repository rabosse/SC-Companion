from fastapi import APIRouter, Depends
import re

from deps import get_current_user
from ship_data_enhancer import enhance_ship_data, get_vehicle_image, get_ship_image
from live_api import fetch_live_vehicles, fetch_live_weapons, fetch_live_components
from ship_purchases import get_purchase_info
from cstone_api import (
    get_all_components as cstone_components,
    get_ship_weapons as cstone_ship_weapons,
    get_missiles_list as cstone_missiles,
    get_item_locations,
    prefetch_cstone_data,
)

router = APIRouter(prefix="/api", tags=["ships"])

# Suffixes that indicate a variant (cosmetic/edition) of a base ship
_VARIANT_SUFFIXES = [
    r"\s+PYAM Exec$",
    r"\s+Executive Edition$",
    r"\s+Emerald$",
    r"\s+Pirate$",
    r"\s+Star Kitten$",
    r"\s+Wikelo.*$",
    r"\s+Teach'?s?\s+Special$",
    r"\s+CitizenCon\s+\d+.*$",
    r"\s+2949\s+Best\s+In\s+Show.*$",
    r"\s+Carbon$",
    r"\s+Talus$",
    r"\s+Dunestalker$",
    r"\s+Snowblind$",
    r"\s+Savior\s+Special$",
    r"\s+Speedy\s+Special$",
]


def _get_variant_base(name):
    """Return the base name for variant grouping."""
    base = name
    for pattern in _VARIANT_SUFFIXES:
        base = re.sub(pattern, "", base, flags=re.IGNORECASE).strip()
    return base


def _dedupe_and_group_variants(ships):
    """Deduplicate ships by name and group variants under base ships."""
    seen_names = set()
    unique = []
    for s in ships:
        if s["name"] not in seen_names:
            seen_names.add(s["name"])
            unique.append(s)

    base_map = {}
    result = []
    for s in unique:
        base_name = _get_variant_base(s["name"])
        if base_name != s["name"] and base_name in base_map:
            idx = base_map[base_name]
            if "variants" not in result[idx]:
                result[idx]["variants"] = []
            result[idx]["variants"].append({
                "name": s["name"],
                "id": s["id"],
                "image": s.get("image", ""),
            })
        else:
            s["variants"] = s.get("variants", [])
            base_map[s["name"]] = len(result)
            if base_name != s["name"]:
                base_map[base_name] = len(result)
            result.append(s)
    return result


@router.get("/ships")
async def get_ships(user_id: str = Depends(get_current_user)):
    live_vehicles = await fetch_live_vehicles()
    if live_vehicles:
        ships = [v for v in live_vehicles if not v.get("is_ground_vehicle")]
        for s in ships:
            img = get_ship_image(s["name"])
            if img:
                s["image"] = img
            pinfo = get_purchase_info(s["name"])
            s["price_auec"] = pinfo["price_auec"]
            s["purchase_locations"] = pinfo["dealers"]
            s["price_usd"] = s.get("msrp", 0)
            s["pledge_url"] = s.get("pledge_url", "")
        ships = _dedupe_and_group_variants(ships)
        return {"success": True, "data": ships, "source": "live"}
    ships = enhance_ship_data(_get_comprehensive_ship_list())
    for s in ships:
        pinfo = get_purchase_info(s["name"])
        s["price_auec"] = pinfo["price_auec"]
        s["purchase_locations"] = pinfo["dealers"]
    return {"success": True, "data": ships, "source": "mock"}


@router.get("/vehicles")
async def get_vehicles(user_id: str = Depends(get_current_user)):
    live_vehicles = await fetch_live_vehicles()
    if live_vehicles:
        ground = [v for v in live_vehicles if v.get("is_ground_vehicle")]
        for v in ground:
            img = get_ship_image(v["name"])
            if img:
                v["image"] = img
            pinfo = get_purchase_info(v["name"])
            v["price_auec"] = pinfo["price_auec"]
            v["purchase_locations"] = pinfo["dealers"]
        if ground:
            ground = _dedupe_and_group_variants(ground)
            return {"success": True, "data": ground, "source": "live"}
    mock_vehicles = [
        {"id": "cyclone", "name": "Cyclone", "manufacturer": "Tumbril", "type": "Ground", "crew": "2", "image": get_vehicle_image("Cyclone")},
        {"id": "nox", "name": "Nox", "manufacturer": "Aopoa", "type": "Hover", "crew": "1", "image": get_vehicle_image("Nox")},
        {"id": "ursa", "name": "Ursa Rover", "manufacturer": "Roberts Space Industries", "type": "Ground", "crew": "6", "image": get_vehicle_image("Ursa")},
        {"id": "nova", "name": "Nova Tank", "manufacturer": "Roberts Space Industries", "type": "Ground", "crew": "2", "image": get_vehicle_image("Nova")},
    ]
    for v in mock_vehicles:
        pinfo = get_purchase_info(v["name"])
        v["price_auec"] = pinfo["price_auec"]
        v["purchase_locations"] = pinfo["dealers"]
    return {"success": True, "data": mock_vehicles, "source": "mock"}


@router.get("/components")
async def get_components(user_id: str = Depends(get_current_user)):
    await prefetch_cstone_data()
    data = cstone_components()
    if data:
        return {"success": True, "data": data, "source": "cstone"}
    # Fallback to old API
    live = await fetch_live_components()
    if live:
        return {"success": True, "data": live, "source": "live"}
    return {"success": True, "data": _get_comprehensive_components_list(), "source": "mock"}


@router.get("/weapons")
async def get_weapons(user_id: str = Depends(get_current_user)):
    await prefetch_cstone_data()
    data = cstone_ship_weapons()
    if data:
        return {"success": True, "data": data, "source": "cstone"}
    live = await fetch_live_weapons()
    if live:
        return {"success": True, "data": live, "source": "live"}
    return {"success": True, "data": _get_comprehensive_weapons_list(), "source": "mock"}


@router.get("/upgrades/{ship_id}")
async def get_upgrades(ship_id: str, user_id: str = Depends(get_current_user)):
    """Generate ship-specific upgrade recommendations using CStone component/weapon data."""
    ships = await fetch_live_vehicles()
    ship = next((s for s in ships if s["id"] == ship_id), None)
    if not ship:
        return {"success": True, "data": {"shields": [], "power": [], "weapons": [], "quantum": [], "coolers": []}}

    hp = ship.get("hardpoints", {})
    shield_size = str(hp.get("shield", {}).get("size", 1))
    power_size = str(hp.get("power_plant", {}).get("size", 1))
    cooler_size = str(hp.get("cooler", {}).get("size", 1))
    qd_size = str(hp.get("quantum_drive", {}).get("size", 1))
    weapon_sizes = hp.get("weapons", [])

    # Use CStone data as primary source
    await prefetch_cstone_data()
    components = cstone_components() or []
    weapons = cstone_ship_weapons() or []

    def best_components(comp_type, size, limit=3):
        matches = [c for c in components if c.get("type", "").lower() == comp_type.lower() and str(c.get("size", "")) == str(size)]
        sort_key = "output" if comp_type.lower() in ("shield", "power") else "rate" if comp_type.lower() == "cooler" else "speed"
        matches.sort(key=lambda c: c.get(sort_key, 0) or 0, reverse=True)
        results = []
        for c in matches[:limit]:
            results.append({
                "id": c.get("id", ""), "name": c.get("name", ""),
                "type": c.get("type", ""), "manufacturer": c.get("manufacturer", ""),
                "size": c.get("size", ""), "grade": c.get("grade", ""),
                "item_class": c.get("item_class", ""),
                "output": c.get("output", 0), "rate": c.get("rate", 0),
                "power_draw": c.get("power_draw", 0), "speed": c.get("speed", 0),
                "durability": c.get("durability", 0),
            })
        return results

    def best_weapons(size, limit=3):
        matches = [w for w in weapons if str(w.get("size", "")) == str(size)]
        matches.sort(key=lambda w: w.get("dps", 0) or w.get("alpha_damage", 0) or 0, reverse=True)
        results = []
        seen = set()
        for w in matches:
            if w.get("name") in seen:
                continue
            seen.add(w.get("name"))
            results.append({
                "id": w.get("id", ""), "name": w.get("name", ""),
                "type": w.get("type", "Weapon"), "manufacturer": w.get("manufacturer", ""),
                "size": w.get("size", ""), "alpha_damage": w.get("alpha_damage", 0),
                "dps": w.get("dps", 0), "fire_rate": w.get("fire_rate", 0),
                "range": w.get("range", 0), "ammo_speed": w.get("ammo_speed", 0),
            })
            if len(results) >= limit:
                break
        return results

    shields = best_components("Shield", shield_size)
    power = best_components("Power", power_size)
    coolers = best_components("Cooler", cooler_size)
    quantum = best_components("Quantum", qd_size)

    weapon_recs = []
    seen_weapons = set()
    for ws in sorted(set(weapon_sizes), reverse=True):
        for w in best_weapons(ws, limit=2):
            if w["name"] not in seen_weapons:
                seen_weapons.add(w["name"])
                weapon_recs.append(w)
    weapon_recs = weapon_recs[:6]

    return {"success": True, "data": {
        "shields": shields, "power": power, "weapons": weapon_recs,
        "quantum": quantum, "coolers": coolers,
    }}


@router.get("/item-locations/{item_id}")
async def get_item_purchase_locations(item_id: str, user_id: str = Depends(get_current_user)):
    """Get purchase locations for a specific item from CStone Finder."""
    locations = await get_item_locations(item_id)
    return {"success": True, "data": locations}


@router.get("/missiles")
async def get_missiles(user_id: str = Depends(get_current_user)):
    """Get all missile data from CStone."""
    await prefetch_cstone_data()
    data = cstone_missiles()
    return {"success": True, "data": data, "source": "cstone"}


# ---------------------------------------------------------------------------
# Static fallback data
# ---------------------------------------------------------------------------

def _get_comprehensive_ship_list():
    return [
        {"id": "85x", "name": "85X", "manufacturer": "Origin Jumpworks", "size": "Snub", "crew": "1", "cargo": 0, "length": 12.5},
        {"id": "100i", "name": "100i", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 2, "length": 20},
        {"id": "125a", "name": "125a", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 2, "length": 20},
        {"id": "135c", "name": "135c", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 6, "length": 20},
        {"id": "300i", "name": "300i", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 8, "length": 27},
        {"id": "315p", "name": "315p", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 12, "length": 27},
        {"id": "325a", "name": "325a", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 4, "length": 27},
        {"id": "350r", "name": "350r", "manufacturer": "Origin Jumpworks", "size": "Small", "crew": "1", "cargo": 0, "length": 27},
        {"id": "400i", "name": "400i", "manufacturer": "Origin Jumpworks", "size": "Medium", "crew": "3", "cargo": 42, "length": 60},
        {"id": "600i", "name": "600i Explorer", "manufacturer": "Origin Jumpworks", "size": "Large", "crew": "5", "cargo": 40, "length": 91.5},
        {"id": "600i-touring", "name": "600i Touring", "manufacturer": "Origin Jumpworks", "size": "Large", "crew": "5", "cargo": 16, "length": 91.5},
        {"id": "890jump", "name": "890 Jump", "manufacturer": "Origin Jumpworks", "size": "Capital", "crew": "8", "cargo": 0, "length": 210},
        {"id": "arrow", "name": "Arrow", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 16},
        {"id": "hawk", "name": "Hawk", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 16},
        {"id": "hornet-f7c", "name": "F7C Hornet", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 22.5},
        {"id": "hornet-f7cm", "name": "F7C-M Super Hornet", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "2", "cargo": 0, "length": 22.5},
        {"id": "hornet-f7cs", "name": "F7C-S Hornet Ghost", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 22.5},
        {"id": "hornet-f7a", "name": "F7A Hornet (Military)", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 22.5},
        {"id": "gladiator", "name": "Gladiator", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "2", "cargo": 0, "length": 24},
        {"id": "hurricane", "name": "Hurricane", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "2", "cargo": 0, "length": 22},
        {"id": "terrapin", "name": "Terrapin", "manufacturer": "Anvil Aerospace", "size": "Small", "crew": "1", "cargo": 0, "length": 20},
        {"id": "valkyrie", "name": "Valkyrie", "manufacturer": "Anvil Aerospace", "size": "Large", "crew": "5", "cargo": 30, "length": 46.5},
        {"id": "carrack", "name": "Carrack", "manufacturer": "Anvil Aerospace", "size": "Large", "crew": "6", "cargo": 456, "length": 126.5},
        {"id": "liberator", "name": "Liberator", "manufacturer": "Anvil Aerospace", "size": "Large", "crew": "6", "cargo": 400, "length": 163},
        {"id": "crucible", "name": "Crucible", "manufacturer": "Anvil Aerospace", "size": "Large", "crew": "6", "cargo": 230, "length": 95},
        {"id": "aurora-ln", "name": "Aurora LN", "manufacturer": "Roberts Space Industries", "size": "Small", "crew": "1", "cargo": 3, "length": 18.5},
        {"id": "aurora-mr", "name": "Aurora MR", "manufacturer": "Roberts Space Industries", "size": "Small", "crew": "1", "cargo": 3, "length": 18.5},
        {"id": "aurora-cl", "name": "Aurora CL", "manufacturer": "Roberts Space Industries", "size": "Small", "crew": "1", "cargo": 6, "length": 18.5},
        {"id": "aurora-lx", "name": "Aurora LX", "manufacturer": "Roberts Space Industries", "size": "Small", "crew": "1", "cargo": 3, "length": 18.5},
        {"id": "aurora-es", "name": "Aurora ES", "manufacturer": "Roberts Space Industries", "size": "Small", "crew": "1", "cargo": 3, "length": 18.5},
        {"id": "mantis", "name": "Mantis", "manufacturer": "Roberts Space Industries", "size": "Small", "crew": "1", "cargo": 0, "length": 28},
        {"id": "scorpius", "name": "Scorpius", "manufacturer": "Roberts Space Industries", "size": "Medium", "crew": "2", "cargo": 0, "length": 27},
        {"id": "constellation-andromeda", "name": "Constellation Andromeda", "manufacturer": "Roberts Space Industries", "size": "Large", "crew": "5", "cargo": 96, "length": 61},
        {"id": "constellation-aquila", "name": "Constellation Aquila", "manufacturer": "Roberts Space Industries", "size": "Large", "crew": "5", "cargo": 96, "length": 61},
        {"id": "constellation-taurus", "name": "Constellation Taurus", "manufacturer": "Roberts Space Industries", "size": "Large", "crew": "5", "cargo": 174, "length": 61},
        {"id": "constellation-phoenix", "name": "Constellation Phoenix", "manufacturer": "Roberts Space Industries", "size": "Large", "crew": "5", "cargo": 96, "length": 61},
        {"id": "perseus", "name": "Perseus", "manufacturer": "Roberts Space Industries", "size": "Large", "crew": "6", "cargo": 500, "length": 100},
        {"id": "polaris", "name": "Polaris", "manufacturer": "Roberts Space Industries", "size": "Capital", "crew": "14", "cargo": 216, "length": 155},
        {"id": "galaxy", "name": "Galaxy", "manufacturer": "Roberts Space Industries", "size": "Capital", "crew": "12", "cargo": 1088, "length": 115},
        {"id": "avenger-titan", "name": "Avenger Titan", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 8, "length": 22.5},
        {"id": "avenger-stalker", "name": "Avenger Stalker", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 0, "length": 22.5},
        {"id": "avenger-warlock", "name": "Avenger Warlock", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 0, "length": 22.5},
        {"id": "sabre", "name": "Sabre", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 0, "length": 24},
        {"id": "sabre-comet", "name": "Sabre Comet", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 0, "length": 24},
        {"id": "gladius", "name": "Gladius", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 0, "length": 20},
        {"id": "vanguard-warden", "name": "Vanguard Warden", "manufacturer": "Aegis Dynamics", "size": "Medium", "crew": "2", "cargo": 0, "length": 38},
        {"id": "vanguard-sentinel", "name": "Vanguard Sentinel", "manufacturer": "Aegis Dynamics", "size": "Medium", "crew": "2", "cargo": 0, "length": 38},
        {"id": "vanguard-harbinger", "name": "Vanguard Harbinger", "manufacturer": "Aegis Dynamics", "size": "Medium", "crew": "2", "cargo": 0, "length": 38},
        {"id": "vanguard-hoplite", "name": "Vanguard Hoplite", "manufacturer": "Aegis Dynamics", "size": "Medium", "crew": "2", "cargo": 0, "length": 38},
        {"id": "eclipse", "name": "Eclipse", "manufacturer": "Aegis Dynamics", "size": "Small", "crew": "1", "cargo": 0, "length": 30},
        {"id": "retaliator", "name": "Retaliator Bomber", "manufacturer": "Aegis Dynamics", "size": "Large", "crew": "7", "cargo": 0, "length": 70.5},
        {"id": "redeemer", "name": "Redeemer", "manufacturer": "Aegis Dynamics", "size": "Medium", "crew": "5", "cargo": 0, "length": 46},
        {"id": "hammerhead", "name": "Hammerhead", "manufacturer": "Aegis Dynamics", "size": "Large", "crew": "11", "cargo": 40, "length": 102},
        {"id": "reclaimer", "name": "Reclaimer", "manufacturer": "Aegis Dynamics", "size": "Large", "crew": "7", "cargo": 180, "length": 158},
        {"id": "nautilus", "name": "Nautilus", "manufacturer": "Aegis Dynamics", "size": "Large", "crew": "6", "cargo": 0, "length": 95},
        {"id": "idris-p", "name": "Idris-P", "manufacturer": "Aegis Dynamics", "size": "Capital", "crew": "28", "cargo": 995, "length": 242},
        {"id": "idris-m", "name": "Idris-M", "manufacturer": "Aegis Dynamics", "size": "Capital", "crew": "28", "cargo": 819, "length": 242},
        {"id": "javelin", "name": "Javelin", "manufacturer": "Aegis Dynamics", "size": "Capital", "crew": "80", "cargo": 5400, "length": 480},
        {"id": "dragonfly-black", "name": "Dragonfly Black", "manufacturer": "Drake Interplanetary", "size": "Snub", "crew": "1", "cargo": 0, "length": 6.3},
        {"id": "dragonfly-yellow", "name": "Dragonfly Yellowjacket", "manufacturer": "Drake Interplanetary", "size": "Snub", "crew": "1", "cargo": 0, "length": 6.3},
        {"id": "buccaneer", "name": "Buccaneer", "manufacturer": "Drake Interplanetary", "size": "Small", "crew": "1", "cargo": 0, "length": 24},
        {"id": "herald", "name": "Herald", "manufacturer": "Drake Interplanetary", "size": "Small", "crew": "1", "cargo": 0, "length": 24},
        {"id": "cutlass-black", "name": "Cutlass Black", "manufacturer": "Drake Interplanetary", "size": "Medium", "crew": "3", "cargo": 46, "length": 38.5},
        {"id": "cutlass-red", "name": "Cutlass Red", "manufacturer": "Drake Interplanetary", "size": "Medium", "crew": "3", "cargo": 10, "length": 38.5},
        {"id": "cutlass-blue", "name": "Cutlass Blue", "manufacturer": "Drake Interplanetary", "size": "Medium", "crew": "3", "cargo": 10, "length": 38.5},
        {"id": "corsair", "name": "Corsair", "manufacturer": "Drake Interplanetary", "size": "Large", "crew": "4", "cargo": 72, "length": 52},
        {"id": "caterpillar", "name": "Caterpillar", "manufacturer": "Drake Interplanetary", "size": "Large", "crew": "5", "cargo": 576, "length": 111},
        {"id": "vulture", "name": "Vulture", "manufacturer": "Drake Interplanetary", "size": "Medium", "crew": "1", "cargo": 12, "length": 32},
        {"id": "kraken", "name": "Kraken", "manufacturer": "Drake Interplanetary", "size": "Capital", "crew": "10", "cargo": 3792, "length": 270},
        {"id": "ares-ion", "name": "Ares Ion", "manufacturer": "Crusader Industries", "size": "Medium", "crew": "1", "cargo": 0, "length": 30},
        {"id": "ares-inferno", "name": "Ares Inferno", "manufacturer": "Crusader Industries", "size": "Medium", "crew": "1", "cargo": 0, "length": 30},
        {"id": "spirit-a1", "name": "Spirit A1", "manufacturer": "Crusader Industries", "size": "Medium", "crew": "2", "cargo": 48, "length": 42},
        {"id": "spirit-c1", "name": "Spirit C1", "manufacturer": "Crusader Industries", "size": "Medium", "crew": "2", "cargo": 96, "length": 42},
        {"id": "mercury", "name": "Mercury Star Runner", "manufacturer": "Crusader Industries", "size": "Large", "crew": "3", "cargo": 114, "length": 66},
        {"id": "starlifter-m2", "name": "M2 Hercules", "manufacturer": "Crusader Industries", "size": "Large", "crew": "4", "cargo": 468, "length": 94},
        {"id": "starlifter-c2", "name": "C2 Hercules", "manufacturer": "Crusader Industries", "size": "Large", "crew": "4", "cargo": 696, "length": 94},
        {"id": "starlifter-a2", "name": "A2 Hercules", "manufacturer": "Crusader Industries", "size": "Large", "crew": "4", "cargo": 234, "length": 94},
        {"id": "genesis", "name": "Genesis Starliner", "manufacturer": "Crusader Industries", "size": "Large", "crew": "5", "cargo": 0, "length": 85},
        {"id": "odyssey", "name": "Odyssey", "manufacturer": "Crusader Industries", "size": "Large", "crew": "6", "cargo": 252, "length": 140},
        {"id": "prospector", "name": "Prospector", "manufacturer": "MISC", "size": "Small", "crew": "1", "cargo": 32, "length": 31},
        {"id": "razor", "name": "Razor", "manufacturer": "MISC", "size": "Small", "crew": "1", "cargo": 0, "length": 13},
        {"id": "reliant-kore", "name": "Reliant Kore", "manufacturer": "MISC", "size": "Small", "crew": "2", "cargo": 6, "length": 28.5},
        {"id": "reliant-tana", "name": "Reliant Tana", "manufacturer": "MISC", "size": "Small", "crew": "2", "cargo": 0, "length": 28.5},
        {"id": "reliant-sen", "name": "Reliant Sen", "manufacturer": "MISC", "size": "Small", "crew": "2", "cargo": 2, "length": 28.5},
        {"id": "reliant-mako", "name": "Reliant Mako", "manufacturer": "MISC", "size": "Small", "crew": "2", "cargo": 0, "length": 28.5},
        {"id": "freelancer", "name": "Freelancer", "manufacturer": "MISC", "size": "Medium", "crew": "4", "cargo": 66, "length": 38},
        {"id": "freelancer-dur", "name": "Freelancer DUR", "manufacturer": "MISC", "size": "Medium", "crew": "4", "cargo": 36, "length": 38},
        {"id": "freelancer-max", "name": "Freelancer MAX", "manufacturer": "MISC", "size": "Medium", "crew": "4", "cargo": 120, "length": 38},
        {"id": "freelancer-mis", "name": "Freelancer MIS", "manufacturer": "MISC", "size": "Medium", "crew": "4", "cargo": 36, "length": 38},
        {"id": "hull-a", "name": "Hull A", "manufacturer": "MISC", "size": "Small", "crew": "1", "cargo": 48, "length": 22},
        {"id": "hull-b", "name": "Hull B", "manufacturer": "MISC", "size": "Medium", "crew": "2", "cargo": 384, "length": 49.5},
        {"id": "hull-c", "name": "Hull C", "manufacturer": "MISC", "size": "Large", "crew": "3", "cargo": 4608, "length": 132},
        {"id": "starfarer", "name": "Starfarer", "manufacturer": "MISC", "size": "Large", "crew": "6", "cargo": 291, "length": 101},
        {"id": "starfarer-gemini", "name": "Starfarer Gemini", "manufacturer": "MISC", "size": "Large", "crew": "6", "cargo": 291, "length": 101},
        {"id": "endeavor", "name": "Endeavor", "manufacturer": "MISC", "size": "Capital", "crew": "16", "cargo": 500, "length": 200},
        {"id": "nox", "name": "Nox", "manufacturer": "Aopoa", "size": "Snub", "crew": "1", "cargo": 0, "length": 7.25},
        {"id": "nox-kue", "name": "Nox Kue", "manufacturer": "Aopoa", "size": "Snub", "crew": "1", "cargo": 0, "length": 7.25},
        {"id": "khartu-al", "name": "Khartu-Al", "manufacturer": "Aopoa", "size": "Small", "crew": "1", "cargo": 0, "length": 16},
        {"id": "san-tok-yai", "name": "San'tok.yāi", "manufacturer": "Aopoa", "size": "Medium", "crew": "1", "cargo": 0, "length": 35},
        {"id": "defender", "name": "Defender", "manufacturer": "Banu", "size": "Small", "crew": "2", "cargo": 0, "length": 26},
        {"id": "merchantman", "name": "Merchantman", "manufacturer": "Banu", "size": "Large", "crew": "8", "cargo": 3584, "length": 160},
        {"id": "blade", "name": "Blade", "manufacturer": "Esperia", "size": "Small", "crew": "1", "cargo": 0, "length": 26},
        {"id": "glaive", "name": "Glaive", "manufacturer": "Esperia", "size": "Small", "crew": "1", "cargo": 0, "length": 32},
        {"id": "prowler", "name": "Prowler", "manufacturer": "Esperia", "size": "Medium", "crew": "5", "cargo": 0, "length": 34},
        {"id": "talon", "name": "Talon", "manufacturer": "Esperia", "size": "Small", "crew": "1", "cargo": 0, "length": 22},
        {"id": "talon-shrike", "name": "Talon Shrike", "manufacturer": "Esperia", "size": "Small", "crew": "1", "cargo": 0, "length": 22},
        {"id": "mpuv-cargo", "name": "MPUV Cargo", "manufacturer": "Argo Astronautics", "size": "Snub", "crew": "1", "cargo": 2, "length": 9.5},
        {"id": "mpuv-personnel", "name": "MPUV Personnel", "manufacturer": "Argo Astronautics", "size": "Snub", "crew": "1", "cargo": 0, "length": 9.5},
        {"id": "mole", "name": "MOLE", "manufacturer": "Argo Astronautics", "size": "Large", "crew": "4", "cargo": 96, "length": 55},
        {"id": "raft", "name": "RAFT", "manufacturer": "Argo Astronautics", "size": "Medium", "crew": "2", "cargo": 96, "length": 38},
        {"id": "mustang-alpha", "name": "Mustang Alpha", "manufacturer": "Consolidated Outland", "size": "Small", "crew": "1", "cargo": 6, "length": 19},
        {"id": "mustang-beta", "name": "Mustang Beta", "manufacturer": "Consolidated Outland", "size": "Small", "crew": "1", "cargo": 0, "length": 19},
        {"id": "mustang-gamma", "name": "Mustang Gamma", "manufacturer": "Consolidated Outland", "size": "Small", "crew": "1", "cargo": 0, "length": 19},
        {"id": "mustang-delta", "name": "Mustang Delta", "manufacturer": "Consolidated Outland", "size": "Small", "crew": "1", "cargo": 0, "length": 19},
        {"id": "mustang-omega", "name": "Mustang Omega", "manufacturer": "Consolidated Outland", "size": "Small", "crew": "1", "cargo": 0, "length": 19},
        {"id": "nomad", "name": "Nomad", "manufacturer": "Consolidated Outland", "size": "Small", "crew": "1", "cargo": 24, "length": 26},
        {"id": "pioneer", "name": "Pioneer", "manufacturer": "Consolidated Outland", "size": "Capital", "crew": "6", "cargo": 500, "length": 140},
    ]


def _get_comprehensive_components_list():
    return [
        {"id": "shield_allstop", "name": "AllStop", "type": "Shield", "manufacturer": "Mirage", "size": "1", "grade": "A", "power": 0.5, "location": "New Babbage", "cost_auec": 12400},
        {"id": "shield_shimmer", "name": "Shimmer", "type": "Shield", "manufacturer": "Mirage", "size": "1", "grade": "B", "power": 0.45, "location": "Port Olisar", "cost_auec": 8900},
        {"id": "shield_bulwark", "name": "Bulwark", "type": "Shield", "manufacturer": "A&R", "size": "1", "grade": "A", "power": 0.52, "location": "Area18", "cost_auec": 13200},
        {"id": "shield_vanguard", "name": "Vanguard", "type": "Shield", "manufacturer": "Gorgon Defender", "size": "1", "grade": "C", "power": 0.48, "location": "Lorville", "cost_auec": 7500},
        {"id": "shield_fr76", "name": "FR-76 Shield Generator", "type": "Shield", "manufacturer": "Gorgon Defender", "size": "2", "grade": "A", "power": 0.8, "location": "Port Olisar", "cost_auec": 24800},
        {"id": "shield_fr86", "name": "FR-86 Shield Generator", "type": "Shield", "manufacturer": "Gorgon Defender", "size": "2", "grade": "B", "power": 0.75, "location": "New Babbage", "cost_auec": 18600},
        {"id": "shield_rampart", "name": "Rampart", "type": "Shield", "manufacturer": "Mirage", "size": "2", "grade": "A", "power": 0.85, "location": "Area18", "cost_auec": 26400},
        {"id": "shield_palisade", "name": "Palisade", "type": "Shield", "manufacturer": "A&R", "size": "2", "grade": "B", "power": 0.78, "location": "Lorville", "cost_auec": 19800},
        {"id": "shield_stronghold", "name": "Stronghold", "type": "Shield", "manufacturer": "A&R", "size": "2", "grade": "C", "power": 0.72, "location": "Port Olisar", "cost_auec": 15200},
        {"id": "shield_sukoran", "name": "Sukoran Shield", "type": "Shield", "manufacturer": "A&R", "size": "3", "grade": "A", "power": 1.2, "location": "New Babbage", "cost_auec": 48600},
        {"id": "shield_guardian", "name": "Guardian", "type": "Shield", "manufacturer": "Gorgon Defender", "size": "3", "grade": "B", "power": 1.15, "location": "Area18", "cost_auec": 38400},
        {"id": "shield_citadel", "name": "Citadel", "type": "Shield", "manufacturer": "Mirage", "size": "3", "grade": "A", "power": 1.25, "location": "Lorville", "cost_auec": 52800},
        {"id": "shield_fortress", "name": "Fortress", "type": "Shield", "manufacturer": "A&R", "size": "3", "grade": "C", "power": 1.1, "location": "Port Olisar", "cost_auec": 32200},
        {"id": "power_breton", "name": "Breton", "type": "Power", "manufacturer": "Sakura Sun", "size": "1", "grade": "A", "output": 3200, "location": "New Babbage", "cost_auec": 14200},
        {"id": "power_juno", "name": "Juno Starworks", "type": "Power", "manufacturer": "Juno Starworks", "size": "1", "grade": "B", "output": 3000, "location": "Area18", "cost_auec": 10800},
        {"id": "power_lightfire", "name": "Lightfire", "type": "Power", "manufacturer": "Aegis", "size": "1", "grade": "C", "output": 2800, "location": "Port Olisar", "cost_auec": 8400},
        {"id": "power_genoa", "name": "Genoa", "type": "Power", "manufacturer": "Sakura Sun", "size": "2", "grade": "A", "output": 4200, "location": "Lorville", "cost_auec": 28400},
        {"id": "power_beacon", "name": "Beacon", "type": "Power", "manufacturer": "Tyler Design", "size": "2", "grade": "B", "output": 4000, "location": "New Babbage", "cost_auec": 22600},
        {"id": "power_slipstream", "name": "Slipstream", "type": "Power", "manufacturer": "Wen/Cassel", "size": "2", "grade": "C", "output": 3800, "location": "Area18", "cost_auec": 18200},
        {"id": "power_regulus", "name": "Regulus", "type": "Power", "manufacturer": "Aegis", "size": "3", "grade": "A", "output": 5600, "location": "Port Olisar", "cost_auec": 56800},
        {"id": "power_maelstrom", "name": "Maelstrom", "type": "Power", "manufacturer": "Lightning Power", "size": "3", "grade": "B", "output": 5400, "location": "Lorville", "cost_auec": 45200},
        {"id": "power_quadracell", "name": "Quadracell", "type": "Power", "manufacturer": "Tyler Design", "size": "3", "grade": "C", "output": 5200, "location": "New Babbage", "cost_auec": 36400},
        {"id": "cooler_frost", "name": "Frost-Star", "type": "Cooler", "manufacturer": "J-Span", "size": "1", "grade": "A", "rate": 4200, "location": "Area18", "cost_auec": 11200},
        {"id": "cooler_polar", "name": "Polar", "type": "Cooler", "manufacturer": "Seal Corp", "size": "1", "grade": "B", "rate": 4000, "location": "Port Olisar", "cost_auec": 8600},
        {"id": "cooler_thermal", "name": "ThermalCore", "type": "Cooler", "manufacturer": "ACOM", "size": "1", "grade": "C", "rate": 3800, "location": "Lorville", "cost_auec": 6800},
        {"id": "cooler_avalanche", "name": "Avalanche", "type": "Cooler", "manufacturer": "J-Span", "size": "2", "grade": "A", "rate": 6800, "location": "New Babbage", "cost_auec": 22400},
        {"id": "cooler_zero", "name": "Zero-Rush", "type": "Cooler", "manufacturer": "Seal Corp", "size": "2", "grade": "B", "rate": 6500, "location": "Area18", "cost_auec": 17200},
        {"id": "cooler_arctic", "name": "ArcticStorm", "type": "Cooler", "manufacturer": "ACOM", "size": "2", "grade": "C", "rate": 6200, "location": "Port Olisar", "cost_auec": 13600},
        {"id": "cooler_blizzard", "name": "Blizzard", "type": "Cooler", "manufacturer": "J-Span", "size": "3", "grade": "A", "rate": 8800, "location": "Lorville", "cost_auec": 44800},
        {"id": "cooler_icecream", "name": "Ice-Scream", "type": "Cooler", "manufacturer": "Seal Corp", "size": "3", "grade": "B", "rate": 8500, "location": "New Babbage", "cost_auec": 34400},
        {"id": "cooler_cryo", "name": "CryoStar", "type": "Cooler", "manufacturer": "ACOM", "size": "3", "grade": "C", "rate": 8200, "location": "Area18", "cost_auec": 27200},
        {"id": "quantum_rush", "name": "Rush", "type": "Quantum", "manufacturer": "Aspro Hangar", "size": "1", "grade": "A", "speed": 121000, "location": "Port Olisar", "cost_auec": 18400},
        {"id": "quantum_yeager", "name": "Yeager", "type": "Quantum", "manufacturer": "Wei-Tek", "size": "1", "grade": "B", "speed": 115000, "location": "New Babbage", "cost_auec": 14200},
        {"id": "quantum_voyage", "name": "Voyage", "type": "Quantum", "manufacturer": "Eos", "size": "1", "grade": "C", "speed": 110000, "location": "Area18", "cost_auec": 11000},
        {"id": "quantum_atlas", "name": "Atlas", "type": "Quantum", "manufacturer": "RSI", "size": "2", "grade": "A", "speed": 141000, "location": "Lorville", "cost_auec": 36800},
        {"id": "quantum_bolon", "name": "Bolon", "type": "Quantum", "manufacturer": "Borea", "size": "2", "grade": "B", "speed": 135000, "location": "Port Olisar", "cost_auec": 28400},
        {"id": "quantum_pontes", "name": "Pontes", "type": "Quantum", "manufacturer": "Agni", "size": "2", "grade": "C", "speed": 130000, "location": "New Babbage", "cost_auec": 22000},
        {"id": "quantum_vk00", "name": "VK-00", "type": "Quantum", "manufacturer": "Agni", "size": "3", "grade": "A", "speed": 161000, "location": "Area18", "cost_auec": 73600},
        {"id": "quantum_crossfield", "name": "Crossfield", "type": "Quantum", "manufacturer": "Eos", "size": "3", "grade": "B", "speed": 155000, "location": "Lorville", "cost_auec": 56800},
        {"id": "quantum_beacon", "name": "Beacon", "type": "Quantum", "manufacturer": "Wei-Tek", "size": "3", "grade": "C", "speed": 150000, "location": "Port Olisar", "cost_auec": 44000},
        {"id": "radar_hawk", "name": "Hawk-3", "type": "Radar", "manufacturer": "Talon Navigation", "size": "1", "grade": "A", "range": 8000, "location": "New Babbage", "cost_auec": 9200},
        {"id": "radar_scout", "name": "Scout", "type": "Radar", "manufacturer": "Chimera Communications", "size": "1", "grade": "B", "range": 7500, "location": "Area18", "cost_auec": 7400},
        {"id": "radar_eagle", "name": "Eagle-Eye", "type": "Radar", "manufacturer": "Talon Navigation", "size": "2", "grade": "A", "range": 12000, "location": "Port Olisar", "cost_auec": 18400},
        {"id": "radar_optics", "name": "WideView Optics", "type": "Radar", "manufacturer": "Chimera Communications", "size": "2", "grade": "B", "range": 11000, "location": "Lorville", "cost_auec": 14800},
        {"id": "radar_nightjar", "name": "Nightjar", "type": "Radar", "manufacturer": "Talon Navigation", "size": "3", "grade": "A", "range": 16000, "location": "New Babbage", "cost_auec": 36800},
        {"id": "radar_sentinel", "name": "Sentinel", "type": "Radar", "manufacturer": "Chimera Communications", "size": "3", "grade": "B", "range": 15000, "location": "Area18", "cost_auec": 29600},
    ]


def _get_comprehensive_weapons_list():
    return [
        {"id": "weapon_badger", "name": "CF-117 Badger Repeater", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "1", "damage": 38, "rate": 600, "location": "Port Olisar", "cost_auec": 4800},
        {"id": "weapon_attrition1", "name": "Attrition-1", "type": "Energy", "manufacturer": "Hurston Dynamics", "size": "1", "damage": 42, "rate": 550, "location": "Lorville", "cost_auec": 5200},
        {"id": "weapon_scorpion", "name": "Scorpion GT-215", "type": "Energy", "manufacturer": "Banu", "size": "1", "damage": 40, "rate": 580, "location": "Area18", "cost_auec": 5600},
        {"id": "weapon_suckerpunch", "name": "Suckerpunch Distortion", "type": "Energy", "manufacturer": "Kastak Arms", "size": "1", "damage": 35, "rate": 620, "location": "GrimHEX", "cost_auec": 4400},
        {"id": "weapon_panther", "name": "CF-227 Panther Repeater", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "2", "damage": 62, "rate": 550, "location": "New Babbage", "cost_auec": 9600},
        {"id": "weapon_attrition2", "name": "Attrition-2", "type": "Energy", "manufacturer": "Hurston Dynamics", "size": "2", "damage": 68, "rate": 500, "location": "Lorville", "cost_auec": 10400},
        {"id": "weapon_omnisky6", "name": "Omnisky VI", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "2", "damage": 185, "rate": 180, "location": "Port Olisar", "cost_auec": 12800},
        {"id": "weapon_nn14", "name": "NN-14 Neutron Repeater", "type": "Energy", "manufacturer": "Neutron", "size": "2", "damage": 70, "rate": 350, "location": "Area18", "cost_auec": 11200},
        {"id": "weapon_m6a", "name": "M6A Laser Cannon", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "3", "damage": 210, "rate": 300, "location": "New Babbage", "cost_auec": 24800},
        {"id": "weapon_attrition3", "name": "Attrition-3", "type": "Energy", "manufacturer": "Hurston Dynamics", "size": "3", "damage": 225, "rate": 280, "location": "Lorville", "cost_auec": 26400},
        {"id": "weapon_omnisky9", "name": "Omnisky IX", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "3", "damage": 305, "rate": 150, "location": "Port Olisar", "cost_auec": 32000},
        {"id": "weapon_nn13", "name": "NN-13 Neutron Cannon", "type": "Energy", "manufacturer": "Neutron", "size": "3", "damage": 240, "rate": 260, "location": "Area18", "cost_auec": 28800},
        {"id": "weapon_m7a", "name": "M7A Laser Cannon", "type": "Energy", "manufacturer": "Klaus & Werner", "size": "4", "damage": 350, "rate": 280, "location": "New Babbage", "cost_auec": 52000},
        {"id": "weapon_attrition4", "name": "Attrition-4", "type": "Energy", "manufacturer": "Hurston Dynamics", "size": "4", "damage": 375, "rate": 260, "location": "Lorville", "cost_auec": 56000},
        {"id": "weapon_c788", "name": "C-788 Ballistic Cannon", "type": "Energy", "manufacturer": "Behring", "size": "4", "damage": 420, "rate": 200, "location": "Port Olisar", "cost_auec": 64000},
        {"id": "weapon_s38", "name": "S-38 Pistol", "type": "Ballistic", "manufacturer": "Gemini", "size": "1", "damage": 50, "rate": 400, "ammo_per_mag": 60, "location": "Lorville", "cost_auec": 3800},
        {"id": "weapon_longsword", "name": "Longsword-1", "type": "Ballistic", "manufacturer": "Behring", "size": "1", "damage": 52, "rate": 380, "ammo_per_mag": 55, "location": "Area18", "cost_auec": 4200},
        {"id": "weapon_sawbuck", "name": "Sawbuck Repeater", "type": "Ballistic", "manufacturer": "Gallenson Tactical", "size": "1", "damage": 48, "rate": 420, "ammo_per_mag": 65, "location": "Port Olisar", "cost_auec": 3600},
        {"id": "weapon_panther_ballistic", "name": "CF-337 Panther", "type": "Ballistic", "manufacturer": "Behring", "size": "2", "damage": 85, "rate": 700, "ammo_per_mag": 300, "location": "New Babbage", "cost_auec": 8800},
        {"id": "weapon_mantis", "name": "Mantis GT-220", "type": "Ballistic", "manufacturer": "Behring", "size": "2", "damage": 90, "rate": 650, "ammo_per_mag": 280, "location": "Lorville", "cost_auec": 9400},
        {"id": "weapon_revenant", "name": "Revenant Gatling", "type": "Ballistic", "manufacturer": "Apocalypse Arms", "size": "2", "damage": 45, "rate": 1200, "ammo_per_mag": 1500, "location": "GrimHEX", "cost_auec": 12600},
        {"id": "weapon_deadbolt2", "name": "Deadbolt II", "type": "Ballistic", "manufacturer": "Klaus & Werner", "size": "2", "damage": 220, "rate": 100, "ammo_per_mag": 40, "location": "Area18", "cost_auec": 14200},
        {"id": "weapon_longsword3", "name": "Longsword-3", "type": "Ballistic", "manufacturer": "Behring", "size": "3", "damage": 180, "rate": 400, "ammo_per_mag": 200, "location": "Port Olisar", "cost_auec": 22400},
        {"id": "weapon_sledge2", "name": "Sledge II Mass Driver", "type": "Ballistic", "manufacturer": "Klaus & Werner", "size": "3", "damage": 450, "rate": 75, "ammo_per_mag": 30, "location": "New Babbage", "cost_auec": 34000},
        {"id": "weapon_sawbuck3", "name": "Sawbuck Repeater III", "type": "Ballistic", "manufacturer": "Gallenson Tactical", "size": "3", "damage": 95, "rate": 650, "ammo_per_mag": 350, "location": "Lorville", "cost_auec": 18600},
        {"id": "weapon_combine", "name": "C-788 Combine Ballistic Cannon", "type": "Ballistic", "manufacturer": "Apocalypse Arms", "size": "4", "damage": 740, "rate": 120, "ammo_per_mag": 80, "location": "GrimHEX", "cost_auec": 68000},
        {"id": "weapon_m6a_ballistic", "name": "M6A Autocannon", "type": "Ballistic", "manufacturer": "Behring", "size": "4", "damage": 380, "rate": 350, "ammo_per_mag": 400, "location": "Area18", "cost_auec": 48000},
        {"id": "weapon_ad5b", "name": "AD5B Ballistic Cannon", "type": "Ballistic", "manufacturer": "Apocalypse Arms", "size": "5", "damage": 1200, "rate": 80, "ammo_per_mag": 60, "location": "GrimHEX", "cost_auec": 96000},
        {"id": "weapon_m8a", "name": "M8A Autocannon", "type": "Ballistic", "manufacturer": "Behring", "size": "5", "damage": 550, "rate": 280, "ammo_per_mag": 500, "location": "New Babbage", "cost_auec": 84000},
        {"id": "missile_spark1", "name": "Spark I", "type": "Missile", "manufacturer": "A&R", "size": "1", "damage": 1200, "rate": 1, "location": "Port Olisar", "cost_auec": 800},
        {"id": "missile_ignite1", "name": "Ignite I", "type": "Missile", "manufacturer": "A&R", "size": "1", "damage": 1350, "rate": 1, "location": "Area18", "cost_auec": 950},
        {"id": "missile_rattler1", "name": "Rattler I", "type": "Missile", "manufacturer": "Behring", "size": "1", "damage": 1180, "rate": 1, "location": "New Babbage", "cost_auec": 750},
        {"id": "missile_spark2", "name": "Spark II", "type": "Missile", "manufacturer": "A&R", "size": "2", "damage": 2400, "rate": 1, "location": "Port Olisar", "cost_auec": 1600},
        {"id": "missile_ignite2", "name": "Ignite II", "type": "Missile", "manufacturer": "A&R", "size": "2", "damage": 2700, "rate": 1, "location": "Lorville", "cost_auec": 1900},
        {"id": "missile_marksman", "name": "Marksman I", "type": "Missile", "manufacturer": "Behring", "size": "2", "damage": 2500, "rate": 1, "location": "Area18", "cost_auec": 1750},
        {"id": "missile_talon", "name": "Talon IR Missile", "type": "Missile", "manufacturer": "Behring", "size": "3", "damage": 4500, "rate": 1, "location": "New Babbage", "cost_auec": 3200},
        {"id": "missile_tempest", "name": "Tempest II", "type": "Missile", "manufacturer": "Behring", "size": "3", "damage": 4800, "rate": 1, "location": "Lorville", "cost_auec": 3600},
        {"id": "missile_arrow3", "name": "Arrow III", "type": "Missile", "manufacturer": "A&R", "size": "3", "damage": 4200, "rate": 1, "location": "Port Olisar", "cost_auec": 2800},
        {"id": "missile_pioneer", "name": "Pioneer", "type": "Missile", "manufacturer": "Behring", "size": "4", "damage": 8500, "rate": 1, "location": "Area18", "cost_auec": 6400},
        {"id": "missile_raptor", "name": "Raptor", "type": "Missile", "manufacturer": "A&R", "size": "4", "damage": 9000, "rate": 1, "location": "GrimHEX", "cost_auec": 7200},
        {"id": "torpedo_argos5", "name": "Argos V", "type": "Missile", "manufacturer": "Behring", "size": "5", "damage": 28000, "rate": 1, "location": "New Babbage", "cost_auec": 18000},
        {"id": "torpedo_seeker5", "name": "Seeker V", "type": "Missile", "manufacturer": "A&R", "size": "5", "damage": 30000, "rate": 1, "location": "Lorville", "cost_auec": 20000},
        {"id": "torpedo_argos9", "name": "Argos IX Torpedo", "type": "Missile", "manufacturer": "Behring", "size": "9", "damage": 125000, "rate": 1, "location": "Area18", "cost_auec": 85000},
        {"id": "torpedo_seeker9", "name": "Seeker IX Torpedo", "type": "Missile", "manufacturer": "A&R", "size": "9", "damage": 135000, "rate": 1, "location": "GrimHEX", "cost_auec": 92000},
        {"id": "weapon_mass_driver", "name": "Sledge Mass Driver", "type": "Ballistic", "manufacturer": "Klaus & Werner", "size": "4", "damage": 850, "rate": 60, "ammo_per_mag": 25, "location": "Port Olisar", "cost_auec": 72000},
        {"id": "weapon_plasma", "name": "Plasma Projector", "type": "Energy", "manufacturer": "Sakura Sun", "size": "4", "damage": 680, "rate": 90, "location": "New Babbage", "cost_auec": 58000},
        {"id": "weapon_emp", "name": "Suckerpunch EMP", "type": "Energy", "manufacturer": "Kastak Arms", "size": "3", "damage": 0, "rate": 30, "location": "GrimHEX", "cost_auec": 38000},
        {"id": "weapon_mining_laser", "name": "Hofstede-S1 Mining Laser", "type": "Energy", "manufacturer": "Greycat Industrial", "size": "2", "damage": 0, "rate": 1, "location": "Lorville", "cost_auec": 15000},
        {"id": "weapon_tractor", "name": "MaxLift Tractor Beam", "type": "Energy", "manufacturer": "Greycat Industrial", "size": "1", "damage": 0, "rate": 1, "location": "Area18", "cost_auec": 8000},
    ]
