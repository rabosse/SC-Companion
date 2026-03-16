"""Scrape ship/vehicle paint (livery) data from starcitizen.tools wiki."""

import re
import httpx
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

WIKI_API = "https://starcitizen.tools/api.php"

# Cache
_livery_cache: Optional[dict] = None
_loading = False


async def _search_paint_pages() -> list[str]:
    """Find all 'series/Paints' pages on the wiki."""
    pages = []
    offset = 0
    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            resp = await client.get(WIKI_API, params={
                "action": "query", "list": "search",
                "srsearch": "intitle:Paints series",
                "srnamespace": "0", "srlimit": "50", "sroffset": str(offset),
                "format": "json",
            })
            data = resp.json()
            results = data.get("query", {}).get("search", [])
            for r in results:
                if "/Paints" in r["title"]:
                    pages.append(r["title"])
            if len(results) < 50:
                break
            offset += 50
    return pages


def _parse_paints_wikitext(wikitext: str, series_name: str) -> list[dict]:
    """Parse paint entries from a series/Paints wikitext page."""
    paints = []
    sections = re.split(r'===\s*"?([^"=]+?)"?\s*===', wikitext)
    i = 1
    while i < len(sections) - 1:
        name = sections[i].strip().strip('"')
        content = sections[i + 1]
        i += 2

        paint = {"name": name, "description": "", "price_auec": None,
                 "price_usd": None, "store_url": None, "image_file": None,
                 "acquisition": "Unknown"}

        rows = re.split(r'\|-', content)
        for row in rows:
            cells = re.split(r'\|(?!\|)', row)
            data_cells = [c.strip() for c in cells if c.strip() and not c.strip().startswith('!') and not c.strip().startswith('{')]
            if len(data_cells) >= 3:
                desc = data_cells[0]
                desc = re.sub(r'\[\[([^|\]]+\|)?([^\]]+)\]\]', r'\2', desc)
                desc = re.sub(r'<ref[^>]*?>.*?</ref>', '', desc, flags=re.DOTALL)
                desc = re.sub(r'<ref[^>]*?/>', '', desc)
                desc = re.sub(r'<ref\b[^>]*>.*', '', desc, flags=re.DOTALL)  # unclosed ref tags
                desc = re.sub(r'\{\{[^}]*\}\}', '', desc)  # template tags
                desc = re.sub(r"'''", '', desc)
                desc = re.sub(r"''", '', desc)
                paint["description"] = desc.strip()

                auec_cell = data_cells[1]
                usd_cell = data_cells[2] if len(data_cells) > 2 else ""

                auec_match = re.search(r'([\d,]+)', auec_cell)
                if auec_match and "not available" not in auec_cell.lower():
                    paint["price_auec"] = int(auec_match.group(1).replace(',', ''))

                url_match = re.search(r'\[(https?://[^\s\]]+)\s+([^\]]+)\]', usd_cell)
                if url_match:
                    paint["store_url"] = url_match.group(1)
                    price_num = re.search(r'([\d.]+)', url_match.group(2))
                    if price_num:
                        paint["price_usd"] = float(price_num.group(1))

                if paint["price_auec"]:
                    paint["acquisition"] = "In-Game"
                elif paint["store_url"]:
                    paint["acquisition"] = "RSI Store"
                elif "reward" in (auec_cell + usd_cell + desc).lower():
                    paint["acquisition"] = "Event Reward"
                elif "limited" in desc.lower():
                    paint["acquisition"] = "Limited Edition"
                elif "subscriber" in desc.lower():
                    paint["acquisition"] = "Subscriber"
                else:
                    paint["acquisition"] = "Special"
                break

        img_match = re.search(r'\[\[File:([^|\]]+)', content)
        if img_match:
            paint["image_file"] = img_match.group(1).strip()

        paints.append(paint)
    return paints


async def _fetch_and_parse_page(client: httpx.AsyncClient, sem: asyncio.Semaphore, page_title: str) -> tuple:
    """Fetch and parse a single paint page with concurrency control."""
    async with sem:
        try:
            resp = await client.get(WIKI_API, params={
                "action": "parse", "page": page_title,
                "prop": "wikitext", "format": "json",
            })
            data = resp.json()
            wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
            series_name = page_title.replace(" series/Paints", "").replace("/Paints", "").strip()
            paints = _parse_paints_wikitext(wikitext, series_name)
            return series_name, paints
        except Exception as e:
            logger.warning(f"Failed to parse {page_title}: {e}")
            return None, []


async def _resolve_images_batch(all_files: dict) -> dict:
    """Batch resolve wiki File: names to direct URLs."""
    filenames = list(all_files.keys())
    resolved = {}
    async with httpx.AsyncClient(timeout=30) as client:
        for batch_start in range(0, len(filenames), 50):
            batch = filenames[batch_start:batch_start + 50]
            titles = "|".join(f"File:{f}" for f in batch)
            try:
                resp = await client.get(WIKI_API, params={
                    "action": "query", "titles": titles,
                    "prop": "imageinfo", "iiprop": "url", "format": "json",
                })
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                for page in pages.values():
                    title = page.get("title", "").replace("File:", "")
                    for img in page.get("imageinfo", []):
                        resolved[title] = img.get("url", "")
            except Exception as e:
                logger.warning(f"Image batch resolve error: {e}")
    return resolved


async def _load_liveries_background():
    """Background task to load all livery data."""
    global _livery_cache, _loading
    _loading = True
    try:
        logger.info("Starting livery data fetch from starcitizen.tools...")
        paint_pages = await _search_paint_pages()
        logger.info(f"Found {len(paint_pages)} paint pages, fetching concurrently...")

        sem = asyncio.Semaphore(10)  # 10 concurrent requests
        async with httpx.AsyncClient(timeout=30) as client:
            tasks = [_fetch_and_parse_page(client, sem, page) for page in paint_pages]
            results = await asyncio.gather(*tasks)

        all_liveries = {}
        all_files = {}
        for series_name, paints in results:
            if series_name and paints:
                for p in paints:
                    p["series"] = series_name
                    if p.get("image_file"):
                        all_files[p["image_file"]] = None
                all_liveries[series_name] = paints

        # Batch resolve images
        logger.info(f"Resolving {len(all_files)} image URLs...")
        resolved = await _resolve_images_batch(all_files)

        for paints in all_liveries.values():
            for p in paints:
                if p.get("image_file") and p["image_file"] in resolved:
                    p["image_url"] = resolved[p["image_file"]]
                p.pop("image_file", None)

        total_paints = sum(len(v) for v in all_liveries.values())
        logger.info(f"Livery data ready: {len(all_liveries)} series, {total_paints} paints")
        _livery_cache = all_liveries
    except Exception as e:
        logger.error(f"Livery loading failed: {e}")
        _livery_cache = {}
    finally:
        _loading = False


def start_background_load():
    """Trigger background loading of livery data."""
    asyncio.create_task(_load_liveries_background())


def get_liveries() -> tuple:
    """Returns (data_or_none, is_loading)."""
    return _livery_cache, _loading
