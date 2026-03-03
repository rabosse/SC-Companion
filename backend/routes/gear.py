from fastapi import APIRouter

from personal_gear import get_all_fps_weapons, get_all_armor_sets, get_all_equipment

router = APIRouter(prefix="/api/gear", tags=["gear"])


@router.get("/weapons")
async def get_fps_weapons():
    return {"success": True, "data": get_all_fps_weapons()}


@router.get("/armor")
async def get_armor_sets():
    return {"success": True, "data": get_all_armor_sets()}


@router.get("/equipment")
async def get_equipment():
    return {"success": True, "data": get_all_equipment()}
