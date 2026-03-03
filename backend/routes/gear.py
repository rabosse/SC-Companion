from fastapi import APIRouter

from personal_gear import get_all_fps_weapons, get_all_armor_sets, get_all_equipment
from ship_data_enhancer import get_armor_image, get_weapon_image

router = APIRouter(prefix="/api/gear", tags=["gear"])


@router.get("/weapons")
async def get_fps_weapons():
    weapons = get_all_fps_weapons()
    for w in weapons:
        w["image"] = get_weapon_image(w["name"])
    return {"success": True, "data": weapons}


@router.get("/armor")
async def get_armor_sets():
    sets = get_all_armor_sets()
    for s in sets:
        s["image"] = get_armor_image(s["name"])
    return {"success": True, "data": sets}


@router.get("/equipment")
async def get_equipment():
    return {"success": True, "data": get_all_equipment()}
