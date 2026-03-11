from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import os
import logging

from deps import client
from ship_data_enhancer import fetch_all_wiki_images
from live_api import prefetch_all
from cstone_api import prefetch_cstone_data

from routes.auth import router as auth_router
from routes.ships import router as ships_router
from routes.fleet import router as fleet_router
from routes.loadouts import router as loadouts_router
from routes.starmap import router as starmap_router
from routes.gear import router as gear_router
from routes.prices import router as prices_router
from routes.wikelo import router as wikelo_router

app = FastAPI(title="Star Citizen Fleet Manager")

# Include all feature routers
app.include_router(auth_router)
app.include_router(ships_router)
app.include_router(fleet_router)
app.include_router(loadouts_router)
app.include_router(starmap_router)
app.include_router(gear_router)
app.include_router(prices_router)
app.include_router(wikelo_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def _prefetch_gear_locations():
    """Background task to pre-fetch CStone purchase locations for curated gear."""
    try:
        from routes.gear import _ensure_cstone_locations
        await _ensure_cstone_locations()
        logger.info("CStone gear purchase locations pre-fetched")
    except Exception as e:
        logger.error(f"Failed to prefetch gear locations: {e}")


async def _prefetch_ship_locations():
    """Background task to pre-fetch CStone purchase locations for ships/vehicles."""
    try:
        from cstone_api import get_ship_shops, batch_fetch_locations
        ships = get_ship_shops()
        # Only fetch for ships marked as sold in-game
        sold_ids = [s["id"] for s in ships if s.get("sold") and s.get("id")]
        if sold_ids:
            await batch_fetch_locations(sold_ids)
            logger.info(f"CStone ship purchase locations pre-fetched for {len(sold_ids)} ships")
    except Exception as e:
        logger.error(f"Failed to prefetch ship locations: {e}")


@app.on_event("startup")
async def startup_event():
    import asyncio

    async def _background_prefetch():
        """Run all prefetch operations in the background so the app starts immediately."""
        try:
            await prefetch_cstone_data()
            logger.info("CStone data prefetched")
        except Exception as e:
            logger.error(f"Failed to prefetch CStone data: {e}")

        try:
            await prefetch_all()
            logger.info("Live API data prefetched")
        except Exception as e:
            logger.error(f"Failed to prefetch live API data: {e}")

        try:
            from live_api import _vehicles_cache
            all_names = [v["name"] for v in _vehicles_cache if v.get("name")]
            await fetch_all_wiki_images(ship_names=all_names)
            logger.info("Wiki images prefetched")
        except Exception as e:
            logger.error(f"Failed to prefetch wiki images: {e}")

        try:
            from routes.prices import _take_snapshot
            await _take_snapshot()
            logger.info("Price snapshot taken")
        except Exception as e:
            logger.error(f"Failed to take price snapshot: {e}")

        await _prefetch_gear_locations()
        await _prefetch_ship_locations()

    # Run all prefetch in background so the server starts immediately
    asyncio.create_task(_background_prefetch())


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
