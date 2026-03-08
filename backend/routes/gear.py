from fastapi import APIRouter

from personal_gear import get_all_fps_weapons, get_all_armor_sets, get_all_equipment
from armor_enhancer import (
    get_armor_image, get_armor_variant_images, get_armor_variant_data,
    fetch_armor_images, fetch_armor_variant_images, fetch_cstone_armor_images,
    fetch_cstone_backpack_images,
    get_backpack_image, get_backpack_variant_images, get_backpack_variant_data,
)
from weapon_enhancer import (
    get_weapon_image, get_weapon_variant_images, get_weapon_variant_data,
    fetch_weapon_images, fetch_cstone_weapon_images,
)
from equipment_enhancer import (
    get_equipment_image, get_equipment_variant_images, get_equipment_variant_data,
    fetch_cstone_equipment_images,
)
from cstone_api import (
    get_fps_weapons as cstone_fps_weapons,
    get_all_armor as cstone_all_armor,
    prefetch_cstone_data,
)

router = APIRouter(prefix="/api/gear", tags=["gear"])

_variant_images_fetched = False


def _merge_fps_stats(curated_weapons: list) -> list:
    """Overlay CStone FPS weapon stats onto curated entries by fuzzy name match."""
    cstone = cstone_fps_weapons()
    if not cstone:
        return curated_weapons

    # Build lookup by lowercase name
    cstone_lookup = {}
    for w in cstone:
        key = w["name"].lower().strip()
        cstone_lookup[key] = w

    for w in curated_weapons:
        key = w["name"].lower().strip()
        match = cstone_lookup.get(key)
        if not match:
            # Try partial match: "P8-SC SMG" might be "P8-SC" in CStone
            for ckey, cval in cstone_lookup.items():
                if key in ckey or ckey in key:
                    match = cval
                    break
        if match:
            # Update stats from CStone
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
            if match.get("single_dps"):
                w["single_dps"] = match["single_dps"]
            if match.get("rapid_dps"):
                w["rapid_dps"] = match["rapid_dps"]
    return curated_weapons


def _merge_armor_stats(curated_armor: list) -> list:
    """Overlay CStone armor stats onto curated entries."""
    cstone = cstone_all_armor()
    if not cstone:
        return curated_armor

    cstone_lookup = {}
    for a in cstone:
        key = a["name"].lower().strip()
        cstone_lookup[key] = a

    for s in curated_armor:
        key = s["name"].lower().strip()
        match = cstone_lookup.get(key)
        if not match:
            for ckey, cval in cstone_lookup.items():
                if key in ckey or ckey in key:
                    match = cval
                    break
        if match:
            if match.get("damage_reduction"):
                s["damage_reduction"] = match["damage_reduction"]
            if match.get("min_temp"):
                s["temp_min"] = match["min_temp"]
            if match.get("max_temp"):
                s["temp_max"] = match["max_temp"]
            if match.get("radiation_resistance"):
                s["rad_resistance"] = match["radiation_resistance"]
    return curated_armor


@router.get("/weapons")
async def get_fps_weapons():
    global _variant_images_fetched
    await prefetch_cstone_data()
    weapons = get_all_fps_weapons()
    weapons = _merge_fps_stats(weapons)
    if not _variant_images_fetched:
        await fetch_armor_images()
        await fetch_cstone_armor_images()
        await fetch_cstone_backpack_images()
        await fetch_cstone_weapon_images()
        await fetch_cstone_equipment_images()
        await fetch_armor_variant_images(get_all_armor_sets())
        _variant_images_fetched = True
    for w in weapons:
        w["image"] = get_weapon_image(w["name"])
        w["variant_images"] = get_weapon_variant_images(w["name"], w.get("variants", []))
        w["variant_data"] = get_weapon_variant_data(
            w["name"], w.get("type", ""),
            w.get("variants", []),
            w.get("price_auec", 0),
            w.get("locations", []),
        )
    return {"success": True, "data": weapons}


@router.get("/armor")
async def get_armor_sets():
    global _variant_images_fetched
    await prefetch_cstone_data()
    sets = get_all_armor_sets()
    sets = _merge_armor_stats(sets)

    if not _variant_images_fetched:
        await fetch_armor_images()
        await fetch_cstone_armor_images()
        await fetch_cstone_backpack_images()
        await fetch_cstone_weapon_images()
        await fetch_cstone_equipment_images()
        await fetch_armor_variant_images(sets)
        _variant_images_fetched = True

    for s in sets:
        is_backpack = s.get("type") == "Backpack"
        if is_backpack:
            s["image"] = get_backpack_image(s["name"])
            s["variant_images"] = get_backpack_variant_images(s["name"], s.get("variants", []))
            s["variant_data"] = get_backpack_variant_data(
                s["name"], s.get("variants", []),
                s.get("price_auec", 0),
                s.get("locations", []),
                s.get("loot_locations", []),
            )
        else:
            s["image"] = get_armor_image(s["name"])
            s["variant_images"] = get_armor_variant_images(s["name"], s.get("variants", []))
            s["variant_data"] = get_armor_variant_data(
                s["name"], s.get("variants", []),
                s.get("price_auec", 0),
                s.get("locations", []),
                s.get("loot_locations", []),
            )
    return {"success": True, "data": sets}


@router.get("/equipment")
async def get_equipment():
    global _variant_images_fetched
    items = get_all_equipment()

    if not _variant_images_fetched:
        await fetch_armor_images()
        await fetch_cstone_armor_images()
        await fetch_cstone_backpack_images()
        await fetch_cstone_weapon_images()
        await fetch_cstone_equipment_images()
        await fetch_armor_variant_images(get_all_armor_sets())
        _variant_images_fetched = True

    for item in items:
        item["image"] = get_equipment_image(item["name"])
        item["variant_images"] = get_equipment_variant_images(
            item["name"], item.get("variants", [])
        )
        item["variant_data"] = get_equipment_variant_data(
            item["name"],
            item.get("type", ""),
            item.get("variants", []),
            item.get("price_auec", 0),
            item.get("locations", []),
        )
        if "loot_locations" not in item:
            item["loot_locations"] = []
    return {"success": True, "data": items}
