from fastapi import APIRouter

from wikelo_data import WIKELO_INFO, WIKELO_CONTRACTS

router = APIRouter(prefix="/api/wikelo", tags=["wikelo"])


@router.get("/info")
async def get_wikelo_info():
    return {"success": True, "data": WIKELO_INFO}


@router.get("/contracts")
async def get_wikelo_contracts(category: str = None, active_only: bool = False):
    contracts = WIKELO_CONTRACTS
    if category:
        contracts = [c for c in contracts if c["category"].lower() == category.lower()]
    if active_only:
        contracts = [c for c in contracts if c["active"]]
    categories = {}
    for c in WIKELO_CONTRACTS:
        cat = c["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "active": 0}
        categories[cat]["total"] += 1
        if c["active"]:
            categories[cat]["active"] += 1
    return {
        "success": True,
        "data": contracts,
        "total": len(contracts),
        "categories": categories,
    }
