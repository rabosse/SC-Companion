from fastapi import APIRouter
from livery_scraper import get_liveries, start_background_load

router = APIRouter(prefix="/api/liveries", tags=["liveries"])


@router.get("")
async def get_all_liveries():
    """Get all ship liveries/paints grouped by ship series."""
    data, is_loading = get_liveries()
    if data is None:
        if not is_loading:
            start_background_load()
        return {"success": True, "data": [], "total_series": 0, "loading": True}
    result = []
    for series_name, paints in sorted(data.items()):
        result.append({
            "series": series_name,
            "paint_count": len(paints),
            "paints": paints,
        })
    return {"success": True, "data": result, "total_series": len(result), "loading": False}
