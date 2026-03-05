"""Equipment data enhancer - CStone images for personal equipment (gadgets, tools)."""

import httpx
import logging

logger = logging.getLogger(__name__)

CSTONE_IMG = "https://cstone.space/uifimages/{}.png"
CSTONE_GADGET_API = "https://finder.cstone.space/GetGadgets"

# Map our equipment item names/ids -> CStone gadget names
_EQUIPMENT_CSTONE_MAP = {
    "MedPen": "MedPen (Hemozal)",
    "OxyPen": "OxyPen",
    "AdrenaPen": "AdrenaPen (Demexatrine)",
    "Hemozal": "DetoxPen (Resurgera)",
    "MedPen Mk II": "CorticoPen (Sterogen)",
}

# CStone gadget cache: {cstone_name -> {uuid, sold}}
_cstone_equipment_cache = {}
_cstone_equipment_loaded = False


async def fetch_cstone_equipment_images():
    global _cstone_equipment_cache, _cstone_equipment_loaded
    if _cstone_equipment_loaded:
        return

    logger.info("Fetching CStone equipment/gadget images...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(CSTONE_GADGET_API, follow_redirects=True)
            if resp.status_code != 200:
                logger.error(f"CStone gadget API returned {resp.status_code}")
                _cstone_equipment_loaded = True
                return

            items = resp.json()
            for item in items:
                name = item.get("Name", "")
                uuid = item.get("ItemId", "")
                if not uuid:
                    continue
                _cstone_equipment_cache[name] = {
                    "uuid": uuid,
                    "sold": item.get("Sold", 0),
                }
        except Exception as e:
            logger.error(f"CStone gadget fetch error: {e}")

    _cstone_equipment_loaded = True
    logger.info(f"CStone equipment cache loaded: {len(_cstone_equipment_cache)} items")


def get_equipment_image(item_name):
    """Get CStone image for equipment item by matching names."""
    cstone_name = _EQUIPMENT_CSTONE_MAP.get(item_name, "")
    if cstone_name and cstone_name in _cstone_equipment_cache:
        return CSTONE_IMG.format(_cstone_equipment_cache[cstone_name]["uuid"])
    # Try direct name match
    if item_name in _cstone_equipment_cache:
        return CSTONE_IMG.format(_cstone_equipment_cache[item_name]["uuid"])
    return ""


def get_equipment_variant_images(item_name, variants):
    """Get variant images for equipment (limited CStone coverage)."""
    base_image = get_equipment_image(item_name)
    result = {}
    for v in variants:
        # Check if variant name matches a CStone item
        cstone_name = _EQUIPMENT_CSTONE_MAP.get(v, v)
        if cstone_name in _cstone_equipment_cache:
            result[v] = CSTONE_IMG.format(_cstone_equipment_cache[cstone_name]["uuid"])
        else:
            result[v] = base_image
    return result


_EQUIPMENT_LOOT_LOCATIONS = {
    "Mining Head": ["Salvage operation loot crates", "Mining outpost beige boxes", "Derelict Reclaimer/Prospector loot"],
    "Mining Attachment": ["Mining outpost beige boxes", "Cave exploration crates", "NPC miner drops"],
    "Mining Module": ["Mining outpost crates", "Shubin facility beige boxes"],
    "Medical Device": ["Medical facility loot", "Hospital beige boxes", "Medic NPC drops"],
    "Undersuit": ["Bunker weapon racks", "NPC drops", "Outpost beige boxes"],
    "Salvage Tool": ["Derelict ship loot", "Salvage yard crates", "NPC salvager drops"],
    "Scanner": ["Exploration site loot", "Outpost crates", "NPC scout drops"],
    "Hacking Tool": ["Grim HEX loot crates", "Outlaw NPC drops", "Security facility beige boxes"],
}


def get_equipment_variant_data(item_name, item_type, variants, base_price, base_locations):
    """Get per-variant acquisition data for equipment."""
    type_loot = _EQUIPMENT_LOOT_LOCATIONS.get(item_type, ["Found in the verse"])
    result = {}
    for v in variants:
        cstone_name = _EQUIPMENT_CSTONE_MAP.get(v, v)
        entry = _cstone_equipment_cache.get(cstone_name, {})
        sold = entry.get("sold", 1) if isinstance(entry, dict) else 1
        if sold:
            result[v] = {
                "price_auec": base_price,
                "locations": base_locations,
                "loot_locations": [],
                "sold": True,
            }
        else:
            result[v] = {
                "price_auec": 0,
                "locations": [],
                "loot_locations": type_loot,
                "sold": False,
            }
    return result
