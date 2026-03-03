from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, timezone
import uuid
import secrets

from deps import db, get_current_user

router = APIRouter(prefix="/api", tags=["loadouts"])


def _generate_share_code():
    return secrets.token_urlsafe(6)


class SaveLoadoutRequest(BaseModel):
    ship_id: str
    ship_name: str
    loadout_name: str
    slots: Dict[str, Any]


@router.post("/loadouts/save")
async def save_loadout(data: SaveLoadoutRequest, user_id: str = Depends(get_current_user)):
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "username": 1})
    username = user_doc["username"] if user_doc else "Unknown"

    loadout_id = str(uuid.uuid4())
    share_code = _generate_share_code()
    doc = {
        "id": loadout_id,
        "user_id": user_id,
        "username": username,
        "ship_id": data.ship_id,
        "ship_name": data.ship_name,
        "loadout_name": data.loadout_name,
        "slots": data.slots,
        "share_code": share_code,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    existing = await db.loadouts.find_one(
        {"user_id": user_id, "ship_id": data.ship_id, "loadout_name": data.loadout_name}, {"_id": 0}
    )
    if existing:
        doc["share_code"] = existing.get("share_code", share_code)
    await db.loadouts.find_one_and_update(
        {"user_id": user_id, "ship_id": data.ship_id, "loadout_name": data.loadout_name},
        {"$set": doc},
        upsert=True,
        return_document=False,
    )
    return {"success": True, "message": "Loadout saved", "id": loadout_id, "share_code": doc["share_code"]}


@router.get("/loadouts/my/all")
async def get_all_my_loadouts(user_id: str = Depends(get_current_user)):
    loadouts = await db.loadouts.find({"user_id": user_id}, {"_id": 0}).to_list(500)
    return {"success": True, "data": loadouts}


@router.get("/loadouts/{ship_id}")
async def get_ship_loadouts(ship_id: str, user_id: str = Depends(get_current_user)):
    loadouts = await db.loadouts.find(
        {"user_id": user_id, "ship_id": ship_id}, {"_id": 0}
    ).to_list(100)
    return {"success": True, "data": loadouts}


@router.delete("/loadouts/{loadout_id}")
async def delete_loadout(loadout_id: str, user_id: str = Depends(get_current_user)):
    result = await db.loadouts.delete_one({"id": loadout_id, "user_id": user_id})
    if result.deleted_count > 0:
        return {"success": True, "message": "Loadout deleted"}
    raise HTTPException(status_code=404, detail="Loadout not found")


@router.get("/community/loadouts")
async def get_community_loadouts(page: int = 1, limit: int = 20, ship_name: str = ""):
    query = {"share_code": {"$exists": True, "$ne": None}}
    if ship_name:
        query["ship_name"] = {"$regex": ship_name, "$options": "i"}
    skip = (page - 1) * limit
    loadouts = await db.loadouts.find(query, {"_id": 0}).sort("updated_at", -1).skip(skip).limit(limit).to_list(limit)
    total = await db.loadouts.count_documents(query)
    return {"success": True, "data": loadouts, "total": total, "page": page}


@router.get("/community/loadouts/{share_code}")
async def get_shared_loadout(share_code: str):
    loadout = await db.loadouts.find_one({"share_code": share_code}, {"_id": 0})
    if not loadout:
        raise HTTPException(status_code=404, detail="Loadout not found")
    return {"success": True, "data": loadout}


@router.post("/loadouts/clone/{share_code}")
async def clone_loadout(share_code: str, user_id: str = Depends(get_current_user)):
    source = await db.loadouts.find_one({"share_code": share_code}, {"_id": 0})
    if not source:
        raise HTTPException(status_code=404, detail="Loadout not found")

    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "username": 1})
    username = user_doc["username"] if user_doc else "Unknown"

    new_id = str(uuid.uuid4())
    new_code = _generate_share_code()
    cloned = {
        "id": new_id,
        "user_id": user_id,
        "username": username,
        "ship_id": source["ship_id"],
        "ship_name": source["ship_name"],
        "loadout_name": f"{source['loadout_name']} (copy)",
        "slots": source["slots"],
        "share_code": new_code,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.loadouts.insert_one(cloned)
    return {"success": True, "message": "Loadout cloned to your collection", "id": new_id}
