from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from star_systems import get_all_locations, get_systems, calculate_route, calculate_interdiction, calculate_chase, calculate_chase_advanced, QD_SPEEDS, QD_FUEL_DEFAULTS

router = APIRouter(prefix="/api/routes", tags=["starmap"])


@router.get("/locations")
async def get_route_locations():
    return {
        "success": True,
        "data": get_all_locations(),
        "systems": get_systems(),
        "qd_speeds": QD_SPEEDS,
        "qd_fuel": QD_FUEL_DEFAULTS,
    }


@router.get("/calculate")
async def calculate_travel_route(
    origin: str,
    destination: str,
    qd_size: int = 1,
    qd_speed: int = 0,
    qd_range: float = 0,
):
    result = calculate_route(origin, destination, qd_size, qd_speed, qd_range)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "data": result}


class InterdictionRequest(BaseModel):
    origins: list
    destination: str
    snare_range_mkm: float = 7.5
    your_qd_size: int = 1
    target_qd_size: int = 1


@router.post("/interdiction")
async def calculate_interdiction_route(data: InterdictionRequest):
    result = calculate_interdiction(data.origins, data.destination, data.snare_range_mkm, data.your_qd_size, data.target_qd_size)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "data": result}


class ChaseRequest(BaseModel):
    your_qd_size: int
    target_qd_size: int
    distance_mkm: float
    prep_time_seconds: int = 30


@router.post("/chase")
async def calculate_chase_scenario(data: ChaseRequest):
    result = calculate_chase(data.your_qd_size, data.target_qd_size, data.distance_mkm, data.prep_time_seconds)
    return {"success": True, "data": result}


class ChaseAdvancedRequest(BaseModel):
    your_position: str
    target_position: str
    your_qd_size: int = 1
    target_qd_size: int = 1
    prep_time_seconds: int = 30


@router.post("/chase/advanced")
async def calculate_chase_advanced_route(data: ChaseAdvancedRequest):
    result = calculate_chase_advanced(data.your_position, data.target_position, data.your_qd_size, data.target_qd_size, data.prep_time_seconds)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "data": result}
