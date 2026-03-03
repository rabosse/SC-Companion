from fastapi import APIRouter
from datetime import datetime, timezone

from deps import db
from live_api import fetch_live_vehicles, fetch_live_weapons, fetch_live_components
from ship_purchases import get_purchase_info

router = APIRouter(prefix="/api/prices", tags=["prices"])

COLLECTION = "price_snapshots"


async def _take_snapshot():
    """Capture current prices from live API + static purchase data and store in MongoDB."""
    now = datetime.now(timezone.utc).isoformat()
    entries = []

    # Ship prices from live API + purchase data
    vehicles = await fetch_live_vehicles()
    for v in vehicles:
        if v.get("is_ground_vehicle"):
            continue
        pinfo = get_purchase_info(v["name"])
        auec = pinfo["price_auec"]
        usd = v.get("msrp") or 0
        if auec > 0 or usd > 0:
            entries.append({
                "item_name": v["name"],
                "item_type": "ship",
                "price_auec": auec,
                "price_usd": usd,
                "dealers": pinfo["dealers"],
                "timestamp": now,
            })

    # Weapon prices
    weapons = await fetch_live_weapons()
    for w in weapons:
        if w.get("cost_auec", 0) > 0:
            entries.append({
                "item_name": w["name"],
                "item_type": "weapon",
                "price_auec": w["cost_auec"],
                "price_usd": 0,
                "location": w.get("location", ""),
                "timestamp": now,
            })

    # Component prices
    components = await fetch_live_components()
    for c in components:
        if c.get("cost_auec", 0) > 0:
            entries.append({
                "item_name": c["name"],
                "item_type": "component",
                "price_auec": c["cost_auec"],
                "price_usd": 0,
                "location": c.get("location", ""),
                "timestamp": now,
            })

    if entries:
        await db[COLLECTION].insert_many(entries)

    return len(entries)


async def _get_previous_snapshot_time():
    """Get the timestamp of the most recent complete snapshot before the current one."""
    pipeline = [
        {"$group": {"_id": "$timestamp"}},
        {"$sort": {"_id": -1}},
        {"$limit": 2},
    ]
    results = await db[COLLECTION].aggregate(pipeline).to_list(2)
    if len(results) >= 2:
        return results[1]["_id"]
    return None


@router.get("/snapshot")
async def take_price_snapshot():
    """Manually trigger a price snapshot (also runs on startup)."""
    count = await _take_snapshot()
    return {"success": True, "message": f"Captured {count} price entries"}


@router.get("/changes")
async def get_price_changes(item_type: str = ""):
    """Get items whose price changed between the two most recent snapshots."""
    # Get the two most recent snapshot timestamps
    pipeline = [
        {"$group": {"_id": "$timestamp"}},
        {"$sort": {"_id": -1}},
        {"$limit": 2},
    ]
    timestamps = await db[COLLECTION].aggregate(pipeline).to_list(2)

    if len(timestamps) < 2:
        return {"success": True, "data": [], "message": "Need at least 2 snapshots to detect changes"}

    latest_ts = timestamps[0]["_id"]
    previous_ts = timestamps[1]["_id"]

    query_latest = {"timestamp": latest_ts}
    query_prev = {"timestamp": previous_ts}
    if item_type:
        query_latest["item_type"] = item_type
        query_prev["item_type"] = item_type

    latest_docs = await db[COLLECTION].find(query_latest, {"_id": 0}).to_list(5000)
    prev_docs = await db[COLLECTION].find(query_prev, {"_id": 0}).to_list(5000)

    prev_map = {d["item_name"]: d for d in prev_docs}
    changes = []
    for doc in latest_docs:
        name = doc["item_name"]
        prev = prev_map.get(name)
        if prev:
            old_price = prev["price_auec"]
            new_price = doc["price_auec"]
            if old_price != new_price and old_price > 0:
                pct = round(((new_price - old_price) / old_price) * 100, 1)
                changes.append({
                    "item_name": name,
                    "item_type": doc["item_type"],
                    "old_price": old_price,
                    "new_price": new_price,
                    "change": new_price - old_price,
                    "change_pct": pct,
                    "direction": "up" if new_price > old_price else "down",
                    "timestamp": doc["timestamp"],
                })
        elif doc["price_auec"] > 0:
            changes.append({
                "item_name": name,
                "item_type": doc["item_type"],
                "old_price": 0,
                "new_price": doc["price_auec"],
                "change": doc["price_auec"],
                "change_pct": 100,
                "direction": "new",
                "timestamp": doc["timestamp"],
            })

    changes.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
    return {
        "success": True,
        "data": changes,
        "latest_snapshot": latest_ts,
        "previous_snapshot": previous_ts,
        "total_changes": len(changes),
    }


@router.get("/history/{item_name}")
async def get_price_history(item_name: str):
    """Get price history for a specific item across all snapshots."""
    pipeline = [
        {"$match": {"item_name": {"$regex": item_name, "$options": "i"}}},
        {"$sort": {"timestamp": 1}},
        {"$project": {"_id": 0}},
    ]
    history = await db[COLLECTION].aggregate(pipeline).to_list(500)
    return {"success": True, "data": history}


@router.get("/summary")
async def get_price_summary():
    """Get a summary of latest prices for all tracked items."""
    # Get latest timestamp
    pipeline = [
        {"$group": {"_id": "$timestamp"}},
        {"$sort": {"_id": -1}},
        {"$limit": 1},
    ]
    timestamps = await db[COLLECTION].aggregate(pipeline).to_list(1)
    if not timestamps:
        return {"success": True, "data": {"ships": [], "weapons": [], "components": []}, "snapshot_count": 0}

    latest_ts = timestamps[0]["_id"]
    docs = await db[COLLECTION].find({"timestamp": latest_ts}, {"_id": 0}).to_list(5000)

    ships = [d for d in docs if d["item_type"] == "ship"]
    weapons = [d for d in docs if d["item_type"] == "weapon"]
    components = [d for d in docs if d["item_type"] == "component"]

    # Count total snapshots
    all_ts = await db[COLLECTION].aggregate([{"$group": {"_id": "$timestamp"}}]).to_list(100)

    return {
        "success": True,
        "data": {
            "ships": sorted(ships, key=lambda x: x["price_auec"], reverse=True)[:50],
            "weapons": sorted(weapons, key=lambda x: x["price_auec"], reverse=True)[:50],
            "components": sorted(components, key=lambda x: x["price_auec"], reverse=True)[:50],
        },
        "snapshot_count": len(all_ts),
        "latest_snapshot": latest_ts,
    }
