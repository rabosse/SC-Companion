from fastapi import APIRouter

from personal_gear import get_all_fps_weapons, get_all_armor_sets, get_all_equipment
from cstone_api import (
    get_fps_weapons as cstone_fps_weapons,
    get_all_armor as cstone_all_armor,
    prefetch_cstone_data,
    batch_fetch_locations,
    get_cached_locations,
    CSTONE_IMG_BASE,
)

router = APIRouter(prefix="/api/gear", tags=["gear"])

_locations_fetched = False

_SLOT_WORDS = {"helmet", "core", "arms", "legs", "undersuit", "backpack"}


def _strip_slot_words(name: str) -> str:
    parts = name.lower().strip().split()
    return " ".join(p for p in parts if p not in _SLOT_WORDS)


def _build_cstone_lookups():
    """Build all CStone lookup dicts once per request."""
    fps = cstone_fps_weapons()
    armor = cstone_all_armor()

    fps_lookup = {}
    for w in fps:
        fps_lookup[w["name"].lower().strip()] = w

    # Armor: stripped name -> first item (for stats/image)
    armor_first = {}
    for a in armor:
        stripped = _strip_slot_words(a["name"])
        if stripped not in armor_first:
            armor_first[stripped] = a

    # Armor: stripped name -> first SOLD item (for locations)
    armor_first_sold = {}
    for a in armor:
        stripped = _strip_slot_words(a["name"])
        if stripped not in armor_first_sold and a.get("sold") and a.get("id"):
            armor_first_sold[stripped] = a

    return fps_lookup, armor_first, armor_first_sold


def _find_match(name, lookup):
    """Find a match in lookup by exact then partial stripped name."""
    stripped = _strip_slot_words(name)
    match = lookup.get(stripped)
    if not match:
        for ck, cv in lookup.items():
            if stripped in ck or ck in stripped:
                return cv
    return match


def _cstone_image(item_id):
    """Get CStone image URL for an item."""
    if item_id:
        return f"{CSTONE_IMG_BASE}/{item_id}.png"
    return ""


async def _ensure_cstone_locations():
    global _locations_fetched
    if _locations_fetched:
        return
    await prefetch_cstone_data()

    curated_weapons = get_all_fps_weapons()
    curated_armor = get_all_armor_sets()
    fps_lookup, armor_first, armor_first_sold = _build_cstone_lookups()

    item_ids_to_fetch = []

    for w in curated_weapons:
        key = w["name"].lower().strip()
        match = fps_lookup.get(key)
        if not match:
            for ck, cv in fps_lookup.items():
                if key in ck or ck in key:
                    match = cv
                    break
        if match and match.get("sold") and match.get("id"):
            item_ids_to_fetch.append(match["id"])

    for s in curated_armor:
        names = [s["name"]] + s.get("variants", [])
        for name in names:
            match = _find_match(name, armor_first_sold)
            if match:
                item_ids_to_fetch.append(match["id"])

    item_ids_to_fetch = list(set(item_ids_to_fetch))
    if item_ids_to_fetch:
        await batch_fetch_locations(item_ids_to_fetch)
    _locations_fetched = True


@router.get("/weapons")
async def get_fps_weapons():
    await _ensure_cstone_locations()
    weapons = get_all_fps_weapons()
    fps_lookup, _, _ = _build_cstone_lookups()

    for w in weapons:
        key = w["name"].lower().strip()
        match = fps_lookup.get(key)
        if not match:
            for ck, cv in fps_lookup.items():
                if key in ck or ck in key:
                    match = cv
                    break

        if match:
            if match.get("alpha_damage"):
                w["damage"] = match["alpha_damage"]
            if match.get("max_dps"):
                w["dps"] = match["max_dps"]
            if match.get("magazine_capacity"):
                w["ammo"] = match["magazine_capacity"]
            if match.get("bullet_speed"):
                w["bullet_speed"] = match["bullet_speed"]
            if match.get("max_fire_rate"):
                w["rpm"] = match["max_fire_rate"]

            # CStone image
            w["image"] = _cstone_image(match.get("id"))

            # CStone locations
            if match.get("sold") and match.get("id"):
                locs = get_cached_locations(match["id"])
                if locs:
                    w["locations"] = [loc["location"] for loc in locs]
                    prices = [loc["price"] for loc in locs if loc.get("price")]
                    if prices:
                        w["price_auec"] = min(prices)

        # Variant images from CStone
        vi = {}
        for vname in w.get("variants", []):
            vkey = vname.lower().strip()
            vmatch = fps_lookup.get(vkey)
            if not vmatch:
                for ck, cv in fps_lookup.items():
                    if vkey in ck or ck in vkey:
                        vmatch = cv
                        break
            vi[vname] = _cstone_image(vmatch["id"]) if vmatch else w.get("image", "")
        w["variant_images"] = vi

        # Variant data
        vd = {}
        for vname in w.get("variants", []):
            vkey = vname.lower().strip()
            vmatch = fps_lookup.get(vkey)
            if not vmatch:
                for ck, cv in fps_lookup.items():
                    if vkey in ck or ck in vkey:
                        vmatch = cv
                        break
            vlocs = []
            vprice = w.get("price_auec", 0)
            if vmatch and vmatch.get("sold") and vmatch.get("id"):
                cached = get_cached_locations(vmatch["id"])
                if cached:
                    vlocs = [loc["location"] for loc in cached]
                    prices = [loc["price"] for loc in cached if loc.get("price")]
                    if prices:
                        vprice = min(prices)
            vd[vname] = {
                "type": w.get("type", ""),
                "locations": vlocs if vlocs else w.get("locations", []),
                "loot_locations": w.get("loot_locations", []),
                "price_auec": vprice,
            }
        w["variant_data"] = vd

    return {"success": True, "data": weapons}


@router.get("/armor")
async def get_armor_sets():
    await _ensure_cstone_locations()
    sets = get_all_armor_sets()
    _, armor_first, armor_first_sold = _build_cstone_lookups()

    for s in sets:
        # Match base armor to CStone
        match = _find_match(s["name"], armor_first)

        if match:
            if match.get("damage_reduction"):
                s["damage_reduction"] = match["damage_reduction"]
            if match.get("min_temp"):
                s["temp_min"] = match["min_temp"]
            if match.get("max_temp"):
                s["temp_max"] = match["max_temp"]
            if match.get("radiation_resistance"):
                s["rad_resistance"] = match["radiation_resistance"]
            s["image"] = _cstone_image(match.get("id"))

        # Base locations from CStone
        sold_match = _find_match(s["name"], armor_first_sold)
        if sold_match:
            locs = get_cached_locations(sold_match["id"])
            if locs:
                s["locations"] = [loc["location"] for loc in locs]
                prices = [loc["price"] for loc in locs if loc.get("price")]
                if prices:
                    s["price_auec"] = min(prices)

        # Variant images and data from CStone
        vi = {}
        vd = {}
        for vname in s.get("variants", []):
            vmatch = _find_match(vname, armor_first)
            vi[vname] = _cstone_image(vmatch["id"]) if vmatch else s.get("image", "")

            # Variant locations
            vsold = _find_match(vname, armor_first_sold)
            vlocs = []
            vprice = s.get("price_auec", 0)
            if vsold:
                cached = get_cached_locations(vsold["id"])
                if cached:
                    vlocs = [loc["location"] for loc in cached]
                    prices = [loc["price"] for loc in cached if loc.get("price")]
                    if prices:
                        vprice = min(prices)

            vd[vname] = {
                "type": s.get("type", ""),
                "locations": vlocs if vlocs else s.get("locations", []),
                "loot_locations": s.get("loot_locations", []),
                "price_auec": vprice,
            }

        s["variant_images"] = vi
        s["variant_data"] = vd

    return {"success": True, "data": sets}


@router.get("/equipment")
async def get_equipment():
    items = get_all_equipment()
    for item in items:
        # Equipment doesn't have CStone matches typically, use empty image
        if not item.get("image"):
            item["image"] = ""
        vi = {}
        vd = {}
        for vname in item.get("variants", []):
            vi[vname] = item.get("image", "")
            vd[vname] = {
                "type": item.get("type", ""),
                "locations": item.get("locations", []),
                "loot_locations": item.get("loot_locations", []),
                "price_auec": item.get("price_auec", 0),
            }
        item["variant_images"] = vi
        item["variant_data"] = vd
        if "loot_locations" not in item:
            item["loot_locations"] = []
    return {"success": True, "data": items}


def _extract_loot_locations(locations: list) -> tuple:
    """Split locations into buy and loot lists based on keywords."""
    loot_keywords = ("loot", "rare", "boss", "drop")
    buy, loot = [], []
    for loc in locations:
        if any(kw in loc.lower() for kw in loot_keywords):
            loot.append(loc)
        else:
            buy.append(loc)
    return buy, loot


@router.get("/rare-items")
async def get_rare_items():
    """Return all loot-only / rare items across weapons, armor, and equipment."""
    await _ensure_cstone_locations()

    weapons = get_all_fps_weapons()
    armor_sets = get_all_armor_sets()
    equipment_items = get_all_equipment()

    fps_lookup, armor_first, armor_first_sold = _build_cstone_lookups()

    rare = []

    # Rare weapons: explicit loot_locations OR loot keywords in locations
    for w in weapons:
        explicit_loot = w.get("loot_locations", [])
        all_locs = w.get("locations", [])
        buy_locs, inferred_loot = _extract_loot_locations(all_locs)
        loot_locs = explicit_loot or inferred_loot
        is_loot_only = w.get("price_auec", 0) == 0 and len(buy_locs) == 0
        has_loot = len(loot_locs) > 0
        if not has_loot:
            continue
        key = w["name"].lower().strip()
        match = fps_lookup.get(key)
        if not match:
            for ck, cv in fps_lookup.items():
                if key in ck or ck in key:
                    match = cv
                    break
        image = _cstone_image(match.get("id")) if match else ""
        rare.append({
            "id": w["id"],
            "name": w["name"],
            "category": "weapon",
            "type": w.get("type", ""),
            "manufacturer": w.get("manufacturer", ""),
            "description": w.get("description", ""),
            "image": image,
            "loot_locations": loot_locs,
            "buy_locations": buy_locs,
            "price_auec": w.get("price_auec", 0),
            "loot_only": is_loot_only,
        })

    # Rare armor: loot-only sets (price 0, no purchase locations)
    for s in armor_sets:
        explicit_loot = s.get("loot_locations", [])
        all_locs = s.get("locations", [])
        buy_locs, inferred_loot = _extract_loot_locations(all_locs)
        loot_locs = explicit_loot or inferred_loot
        is_loot_only = s.get("price_auec", 0) == 0 and len(buy_locs) == 0
        if not loot_locs:
            continue
        match = _find_match(s["name"], armor_first)
        image = _cstone_image(match.get("id")) if match else ""
        rare.append({
            "id": s["id"],
            "name": s["name"],
            "category": "armor",
            "type": s.get("type", ""),
            "manufacturer": s.get("manufacturer", ""),
            "description": s.get("description", ""),
            "image": image,
            "loot_locations": loot_locs,
            "buy_locations": buy_locs,
            "price_auec": s.get("price_auec", 0),
            "loot_only": is_loot_only,
        })

    # Rare equipment
    for item in equipment_items:
        explicit_loot = item.get("loot_locations", [])
        all_locs = item.get("locations", [])
        buy_locs, inferred_loot = _extract_loot_locations(all_locs)
        loot_locs = explicit_loot or inferred_loot
        is_loot_only = item.get("price_auec", 0) == 0 and len(buy_locs) == 0
        if not loot_locs:
            continue
        rare.append({
            "id": item["id"],
            "name": item["name"],
            "category": "equipment",
            "type": item.get("type", ""),
            "manufacturer": item.get("manufacturer", ""),
            "description": item.get("description", ""),
            "image": item.get("image", ""),
            "loot_locations": loot_locs,
            "buy_locations": buy_locs,
            "price_auec": item.get("price_auec", 0),
            "loot_only": is_loot_only,
        })

    return {"success": True, "data": rare, "total": len(rare)}
