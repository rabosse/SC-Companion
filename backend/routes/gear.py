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

router = APIRouter(prefix="/api/gear", tags=["gear"])

_variant_images_fetched = False


@router.get("/weapons")
async def get_fps_weapons():
    global _variant_images_fetched
    weapons = get_all_fps_weapons()
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
    sets = get_all_armor_sets()

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
