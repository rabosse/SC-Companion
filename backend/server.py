from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Star Citizen Fleet Manager")

# CORS - must be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints - MUST respond before anything else loads
@app.get("/health")
async def health_check_root():
    return {"status": "ok"}


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


# Include routers
from routes.auth import router as auth_router
from routes.ships import router as ships_router
from routes.fleet import router as fleet_router
from routes.loadouts import router as loadouts_router
from routes.starmap import router as starmap_router
from routes.gear import router as gear_router
from routes.prices import router as prices_router
from routes.wikelo import router as wikelo_router
from routes.liveries import router as liveries_router

app.include_router(auth_router)
app.include_router(ships_router)
app.include_router(fleet_router)
app.include_router(loadouts_router)
app.include_router(starmap_router)
app.include_router(gear_router)
app.include_router(prices_router)
app.include_router(wikelo_router)
app.include_router(liveries_router)


# Startup: delay ALL background work by 30 seconds to let health checks pass first
@app.on_event("startup")
async def startup_event():
    import asyncio

    async def _delayed_prefetch():
        """Wait for container to be fully ready before doing any background work."""
        try:
            await asyncio.sleep(30)
            logger.info("Starting delayed background prefetch...")

            from cstone_api import prefetch_cstone_data
            await prefetch_cstone_data()
            logger.info("CStone data prefetched")
        except Exception as e:
            logger.error(f"Prefetch CStone failed: {e}")

        try:
            from live_api import prefetch_all
            await prefetch_all()
            logger.info("Live API data prefetched")
        except Exception as e:
            logger.error(f"Prefetch live API failed: {e}")

        try:
            from live_api import _vehicles_cache
            from ship_data_enhancer import fetch_all_wiki_images
            all_names = [v["name"] for v in _vehicles_cache if v.get("name")]
            await fetch_all_wiki_images(ship_names=all_names)
            logger.info("Wiki images prefetched")
        except Exception as e:
            logger.error(f"Prefetch wiki images failed: {e}")

        try:
            from routes.prices import _take_snapshot
            await _take_snapshot()
            logger.info("Price snapshot taken")
        except Exception as e:
            logger.error(f"Price snapshot failed: {e}")

        try:
            from routes.gear import _ensure_cstone_locations
            await _ensure_cstone_locations()
        except Exception as e:
            logger.error(f"Gear locations failed: {e}")

        try:
            from cstone_api import get_ship_shops, batch_fetch_locations
            ships = get_ship_shops()
            sold_ids = [s["id"] for s in ships if s.get("sold") and s.get("id")]
            if sold_ids:
                await batch_fetch_locations(sold_ids)
        except Exception as e:
            logger.error(f"Ship locations failed: {e}")

        try:
            from livery_scraper import _load_liveries_background
            await _load_liveries_background()
            logger.info("Livery data prefetched")
        except Exception as e:
            logger.error(f"Prefetch liveries failed: {e}")

        logger.info("Background prefetch complete")

    asyncio.create_task(_delayed_prefetch())
    logger.info("Server started - health check ready")


@app.on_event("shutdown")
async def shutdown_db_client():
    try:
        from deps import _get_client
        c = _get_client()
        if c:
            c.close()
    except Exception:
        pass
