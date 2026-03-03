from fastapi import APIRouter

from personal_gear import get_all_fps_weapons, get_all_armor_sets

router = APIRouter(prefix="/api/gear", tags=["gear"])


@router.get("/weapons")
async def get_fps_weapons():
    return {"success": True, "data": get_all_fps_weapons()}


@router.get("/armor")
async def get_armor_sets():
    return {"success": True, "data": get_all_armor_sets()}
