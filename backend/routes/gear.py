from fastapi import APIRouter

from personal_gear import get_all_fps_weapons, get_all_armor_sets, get_all_equipment
from ship_data_enhancer import (
    get_armor_image, get_weapon_image, get_armor_variant_images,
    fetch_armor_variant_images, fetch_armor_images, fetch_cstone_armor_images,
)

router = APIRouter(prefix="/api/gear", tags=["gear"])

_variant_images_fetched = False


@router.get("/weapons")
async def get_fps_weapons():
    weapons = get_all_fps_weapons()
    for w in weapons:
        w["image"] = get_weapon_image(w["name"])
    return {"success": True, "data": weapons}


@router.get("/armor")
async def get_armor_sets():
    global _variant_images_fetched
    sets = get_all_armor_sets()

    # Ensure variant images are fetched (runs once)
    if not _variant_images_fetched:
        await fetch_armor_images()
        await fetch_cstone_armor_images()
        await fetch_armor_variant_images(sets)
        _variant_images_fetched = True

    for s in sets:
        s["image"] = get_armor_image(s["name"])
        s["variant_images"] = get_armor_variant_images(s["name"], s.get("variants", []))
    return {"success": True, "data": sets}


@router.get("/equipment")
async def get_equipment():
    return {"success": True, "data": get_all_equipment()}
