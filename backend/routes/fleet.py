from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

from deps import db, get_current_user, UserFleet

router = APIRouter(prefix="/api/fleet", tags=["fleet"])


class BulkFleetRequest(BaseModel):
    ships: list


@router.post("/add")
async def add_to_fleet(ship_data: dict, user_id: str = Depends(get_current_user)):
    fleet_item = UserFleet(
        user_id=user_id,
        ship_id=ship_data.get('id'),
        ship_name=ship_data.get('name'),
        manufacturer=ship_data.get('manufacturer')
    )
    doc = fleet_item.model_dump()
    doc['added_at'] = doc['added_at'].isoformat()
    await db.user_fleet.insert_one(doc)
    return {"success": True, "message": "Ship added to fleet"}


@router.get("/my")
async def get_my_fleet(user_id: str = Depends(get_current_user)):
    fleet = await db.user_fleet.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    from datetime import datetime
    for item in fleet:
        if isinstance(item.get('added_at'), str):
            item['added_at'] = datetime.fromisoformat(item['added_at'])
    return {"success": True, "data": fleet}


@router.delete("/{fleet_id}")
async def remove_from_fleet(fleet_id: str, user_id: str = Depends(get_current_user)):
    result = await db.user_fleet.delete_one({"id": fleet_id, "user_id": user_id})
    if result.deleted_count > 0:
        return {"success": True, "message": "Ship removed from fleet"}
    raise HTTPException(status_code=404, detail="Ship not found in fleet")


@router.post("/bulk-add")
async def bulk_add_to_fleet(data: BulkFleetRequest, user_id: str = Depends(get_current_user)):
    ship_ids = [s.get("id") for s in data.ships]
    existing_docs = await db.user_fleet.find(
        {"user_id": user_id, "ship_id": {"$in": ship_ids}}, {"_id": 0, "ship_id": 1}
    ).to_list(1000)
    existing_ids = {doc["ship_id"] for doc in existing_docs}

    added = 0
    skipped = 0
    to_insert = []
    for ship in data.ships:
        if ship.get("id") in existing_ids:
            skipped += 1
            continue
        fleet_item = UserFleet(
            user_id=user_id,
            ship_id=ship.get("id"),
            ship_name=ship.get("name"),
            manufacturer=ship.get("manufacturer")
        )
        doc = fleet_item.model_dump()
        doc["added_at"] = doc["added_at"].isoformat()
        to_insert.append(doc)
        added += 1
    if to_insert:
        await db.user_fleet.insert_many(to_insert)
    return {"success": True, "message": f"{added} ships added, {skipped} already in fleet", "added": added, "skipped": skipped}
