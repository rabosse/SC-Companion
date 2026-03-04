"""Weapon data enhancer - CStone + Wiki images and variant data for FPS weapons."""

import httpx
import logging
import re

logger = logging.getLogger(__name__)

WIKI_API = "https://starcitizen.tools/api.php"
THUMB_SIZE = 600
CSTONE_IMG = "https://cstone.space/uifimages/{}.png"
CSTONE_WEAPON_API = "https://finder.cstone.space/GetFPSWeapons"

WEAPON_WIKI_OVERRIDES = {
    "Arclight Pistol": "Arclight Pistol", "Coda Pistol": "Coda Pistol",
    "LH86 Pistol": "LH86 Pistol", "Yubarev Pistol": "Yubarev Pistol",
    "C54 SMG": "C54 SMG", "Custodian SMG": "Custodian SMG", "Ripper SMG": "Ripper SMG",
    "S71 Rifle": "S71 Rifle", "Karna Rifle": "Karna Rifle",
    "P4-AR Assault Rifle": "P4-AR Rifle",
    "Parallax Assault Rifle": "Parallax Energy Assault Rifle",
    "F55 LMG": "F55 LMG", "Demeco LMG": "Demeco LMG", "FS-9 LMG": "FS-9 LMG",
    "BR-2 Shotgun": "BR-2 Shotgun",
    "Ravager-212 Shotgun": "Ravager-212 Twin Shotgun",
    "A03 Sniper Rifle": "A03 Sniper Rifle", "Arrowhead Sniper Rifle": "Arrowhead Sniper Rifle",
    "P6-LR Sniper Rifle": "P6-LR Sniper Rifle",
    "Animus Missile Launcher": "Animus Missile Launcher",
    "GP-33 Grenade Launcher": "GP-33 MOD Grenade Launcher",
    "Frag Grenade": "MK-4 Frag Grenade", "MedPen": "MedPen (Hemozal)", "OxyPen": "OxyPen",
}

_weapon_image_cache = {}
_weapon_cache_loaded = False
_cstone_weapon_cache = {}
_cstone_weapon_cache_loaded = False

_WEAPON_LOOT_LOCATIONS = {
    "Pistol": ["Bunker weapon racks", "NPC holster drops", "Outpost beige boxes"],
    "SMG": ["Security bunker racks", "Distribution center crates", "NPC drops"],
    "Assault Rifle": ["Bunker weapon racks & crates", "Security NPC drops", "Distribution centers"],
    "LMG": ["High-threat bunker weapon racks", "Heavy NPC drops", "Military outpost crates"],
    "Shotgun": ["Outlaw bunker racks", "Close-quarters NPC drops", "Distribution centers"],
    "Sniper Rifle": ["Sniper nest loot crates", "Long-range NPC drops", "High-security bunker racks"],
    "Railgun": ["Rare bunker boss drops", "High-threat facility racks", "Pyro contested zone crates"],
    "Grenade Launcher": ["Rare bunker weapon racks", "Heavy NPC boss drops", "Military facility crates"],
    "Missile Launcher": ["Rare heavy weapon crates", "Pyro facility racks", "Boss NPC drops"],
    "Medical Device": ["Medical supply vendors (all stations)", "Pharmacy (Orison, New Babbage)"],
    "Grenade": ["Bunker weapon racks", "NPC drops", "Outpost crates"],
    "Utility": ["Station shops (most locations)", "Cargo Decks", "NPC drops"],
}


async def fetch_weapon_images():
    global _weapon_image_cache, _weapon_cache_loaded
    if _weapon_cache_loaded:
        return
    titles = list(set(WEAPON_WIKI_OVERRIDES.values()))
    logger.info(f"Fetching wiki weapon images for {len(titles)} items...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(0, len(titles), 15):
            batch = titles[i:i+15]
            titles_param = "|".join(t.replace(" ", "_") for t in batch)
            try:
                resp = await client.get(WIKI_API, params={
                    "action": "query", "prop": "pageimages", "piprop": "thumbnail|original",
                    "pithumbsize": THUMB_SIZE, "titles": titles_param, "format": "json",
                }, follow_redirects=True)
                if resp.status_code == 200:
                    pages = resp.json().get("query", {}).get("pages", {})
                    for page in pages.values():
                        title = page.get("title", "")
                        thumb = page.get("thumbnail", {}).get("source")
                        original = page.get("original", {}).get("source")
                        if thumb or original:
                            _weapon_image_cache[title] = original or thumb
            except Exception as e:
                logger.error(f"Weapon image fetch error: {e}")
    _weapon_cache_loaded = True
    logger.info(f"Weapon image cache loaded: {len(_weapon_image_cache)} images cached")


async def fetch_cstone_weapon_images():
    global _cstone_weapon_cache, _cstone_weapon_cache_loaded
    if _cstone_weapon_cache_loaded:
        return
    logger.info("Fetching CStone weapon images...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(CSTONE_WEAPON_API, follow_redirects=True)
            if resp.status_code != 200:
                logger.error(f"CStone weapon API returned {resp.status_code}")
                _cstone_weapon_cache_loaded = True
                return
            items = resp.json()
            for item in items:
                name = item.get("Name", "")
                uuid = item.get("ItemId", "")
                if not uuid or "(Modified)" in name:
                    continue
                match = re.match(r'^(.*?)\s*"(.*?)"\s*(.*?)$', name)
                if match:
                    base = (match.group(1).strip() + " " + match.group(3).strip()).strip()
                    variant = match.group(2).strip()
                else:
                    base = name
                    variant = "Base"
                if base not in _cstone_weapon_cache:
                    _cstone_weapon_cache[base] = {}
                _cstone_weapon_cache[base][variant] = {
                    "uuid": uuid, "sold": item.get("Sold", 0),
                }
        except Exception as e:
            logger.error(f"CStone weapon fetch error: {e}")
    _cstone_weapon_cache_loaded = True
    total = sum(len(v) for v in _cstone_weapon_cache.values())
    logger.info(f"CStone weapon cache loaded: {len(_cstone_weapon_cache)} weapons, {total} total variants")


def get_weapon_image(weapon_name):
    cstone_wep = _cstone_weapon_cache.get(weapon_name, {})
    base_entry = cstone_wep.get("Base", {})
    base_uuid = base_entry.get("uuid", "") if isinstance(base_entry, dict) else ""
    if base_uuid:
        return CSTONE_IMG.format(base_uuid)
    wiki_title = WEAPON_WIKI_OVERRIDES.get(weapon_name, weapon_name)
    return _weapon_image_cache.get(wiki_title, "")


def get_weapon_variant_images(weapon_name, variants):
    base_image = get_weapon_image(weapon_name)
    cstone_wep = _cstone_weapon_cache.get(weapon_name, {})
    result = {}
    for v in variants:
        match = re.match(r'^.*?"(.*?)".*?$', v)
        suffix = match.group(1) if match else v.replace(weapon_name, "").strip()
        entry = cstone_wep.get(suffix, {})
        cstone_uuid = entry.get("uuid", "") if isinstance(entry, dict) else ""
        if cstone_uuid:
            result[v] = CSTONE_IMG.format(cstone_uuid)
        else:
            result[v] = base_image
    return result


def get_weapon_variant_data(weapon_name, weapon_type, variants, base_price, base_locations):
    cstone_wep = _cstone_weapon_cache.get(weapon_name, {})
    type_loot = _WEAPON_LOOT_LOCATIONS.get(weapon_type, ["Found in the verse"])
    result = {}
    for v in variants:
        match = re.match(r'^.*?"(.*?)".*?$', v)
        suffix = match.group(1) if match else v.replace(weapon_name, "").strip()
        entry = cstone_wep.get(suffix, {})
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
