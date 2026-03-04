"""Ship data enhancer - fetches images from Star Citizen Wiki by ship name.

Armor, weapon, and equipment enhancers have been refactored into separate modules:
  - armor_enhancer.py
  - weapon_enhancer.py
  - equipment_enhancer.py
"""

import httpx
import logging
import re

# Re-export from new modules for backward compatibility
from armor_enhancer import (
    fetch_armor_images, fetch_armor_variant_images, fetch_cstone_armor_images,
    get_armor_image, get_armor_variant_images, get_armor_variant_data,
    fetch_cstone_backpack_images,
    get_backpack_image, get_backpack_variant_images, get_backpack_variant_data,
)
from weapon_enhancer import (
    fetch_weapon_images, fetch_cstone_weapon_images,
    get_weapon_image, get_weapon_variant_images, get_weapon_variant_data,
)
from equipment_enhancer import (
    fetch_cstone_equipment_images,
    get_equipment_image, get_equipment_variant_images, get_equipment_variant_data,
)

logger = logging.getLogger(__name__)

WIKI_API = "https://starcitizen.tools/api.php"
THUMB_SIZE = 600

# Variant suffixes to strip when looking for a base ship image
VARIANT_SUFFIXES = [
    r"\s+wikelo\b.*",
    r"\s+pyam\s+exec.*",
    r"\s+teach'?s?\s+special.*",
    r"\s+2949\s+best\s+in\s+show.*",
    r"\s+executive\s+edition.*",
    r"\s+emerald.*",
    r"\s+citizencon\s+\d+.*",
    r"\s+pirate$",
    r"\s+star\s+kitten$",
    r"\s+cool\s+metal\s+color$",
    r"\s+geo\s+ikti$",
    r"\s+geo$",
    r"\s+ikti\s+rad$",
    r"\s+ikti$",
    r"\s+orange\s+line$",
    r"\s+snowland\s+color$",
    r"\s+carbon$",
    r"\s+talus$",
]

# Manual overrides: live API name -> wiki page title (only for names that differ)
NAME_OVERRIDES = {
    "A1 Spirit": "Spirit", "C1 Spirit": "Spirit",
    "A2 Hercules Starlifter": "A2 Hercules",
    "C2 Hercules Starlifter": "C2 Hercules Starlifter",
    "M2 Hercules Starlifter": "M2 Hercules Starlifter",
    "600i 2951 BIS": "600i Explorer", "600i Executive Edition": "600i Explorer", "600i": "600i Explorer",
    "85X Limited": "85X", "890 Jump": "890 Jump",
    "Dragonfly Yellowjacket": "Dragonfly", "Dragonfly Star Kitten": "Dragonfly",
    "Nox Wikelo Special": "Nox",
    "P-72 Archimedes Emerald": "P-72 Archimedes",
    "Fury LX": "Fury", "Fury MX": "Fury",
    "Pulse LX": "Pulse", "X1 Force": "X1", "X1 Velocity": "X1",
    "Golem OX": "Golem", "Guardian MX": "Guardian", "Guardian QI": "Guardian",
    "Ballista Dunestalker": "Ballista", "Ballista Snowblind": "Ballista",
    "Cutter Rambler": "Cutter", "Cutter Scout": "Cutter",
    "C8R Pisces Rescue": "C8 Pisces",
    "MOLE Carbon": "MOLE", "MOLE Talus": "MOLE",
    "MPUV Tractor": "MPUV Cargo",
    "Corsair PYAM Exec": "Corsair", "Cutlass Black PYAM Exec": "Cutlass Black",
    "L-22 Alpha Wolf": "L-21 Wolf", "Prowler Utility": "Prowler", "ROC-DS": "ROC",
    "Terrapin Medic": "Terrapin",
    "Sabre Firebird": "Sabre", "Sabre Peregrine": "Sabre",
    "Constellation Phoenix Emerald": "Constellation Phoenix",
    "Caterpillar Pirate": "Caterpillar",
    "Gladius Dunlevy": "Gladius", "Gladius Pirate": "Gladius", "Gladius Valiant": "Gladius",
    "F7C Hornet Wildfire Mk I": "F7C Hornet Mk II",
    "F7C-M Hornet Heartseeker Mk I": "F7C-M Super Hornet Mk II",
    "F7C-M Hornet Heartseeker Mk II": "F7C-M Super Hornet Mk II",
    "F7C-M Super Hornet Mk I": "F7C-M Super Hornet Mk II",
    "F7C-R Hornet Tracker Mk I": "F7C Hornet Mk II",
    "F7C-R Hornet Tracker Mk II": "F7C Hornet Mk II",
    "F7C-S Hornet Ghost Mk I": "F7C-S Hornet Ghost Mk II",
    "F7A Hornet Mk I": "F7A Hornet Mk II",
    "F7 Hornet Mk Wikelo": "F7C Hornet Mk II",
    "Hornet F7A Mk II PYAM Exec": "F7A Hornet Mk II",
    "F8C Lightning Executive Edition": "F8C Lightning",
    "F8C Lightning PYAM Exec": "F8C Lightning",
    "Starlancer MAX Wikelo Work Special": "Starlancer MAX",
    "Starlancer TAC Wikelo War Special": "Starlancer TAC",
    "Nomad Teach's Special": "Nomad", "Starfarer Teach's Special": "Starfarer",
    "Reclaimer Teach's Special": "Reclaimer", "Vulture Teach's Special": "Vulture",
    "Syulen PYAM Exec": "Syulen",
    "Mustang CitizenCon 2948 Edition": "Mustang Alpha",
    "ATLS Cool Metal Color": "ATLS", "ATLS GEO": "ATLS", "ATLS GEO IKTI": "ATLS",
    "ATLS IKTI": "ATLS", "ATLS IKTI Rad": "ATLS", "ATLS Orange Line": "ATLS",
    "ATLS Snowland Color": "ATLS",
    "Scorpius Wikelo Sneak Special": "Scorpius",
    "Constellation Taurus Wikelo War Special": "Constellation Taurus",
    "C1 Spirit Wikelo Special": "Spirit",
    "Prospector Wikelo Work Special": "Prospector",
    "RAFT Wikelo Work Special": "RAFT",
    "M50 Interceptor": "M50", "Vanduul Scythe": "Glaive",
    "Power Suit": "", "CSV-SM\n": "CSV-SM", "Esperia Stinger": "Glaive",
}

_image_cache = {}
_cache_loaded = False


def _get_base_name(name):
    if name in NAME_OVERRIDES:
        return NAME_OVERRIDES[name]
    base = name
    for pattern in VARIANT_SUFFIXES:
        base = re.sub(pattern, "", base, flags=re.IGNORECASE).strip()
    return base


def _collect_wiki_titles(ship_names):
    titles = set()
    for name in ship_names:
        wiki_title = _get_base_name(name)
        if wiki_title:
            titles.add(wiki_title)
        if name and name not in NAME_OVERRIDES:
            titles.add(name)
    return titles


async def fetch_all_wiki_images(ship_names=None):
    global _image_cache, _cache_loaded
    if _cache_loaded and not ship_names:
        return
    if not ship_names:
        ship_names = []
    all_titles = list(_collect_wiki_titles(ship_names))
    logger.info(f"Fetching wiki images for {len(all_titles)} unique titles...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(0, len(all_titles), 50):
            batch = all_titles[i:i + 50]
            titles_param = "|".join(t.replace(" ", "_") for t in batch)
            try:
                resp = await client.get(WIKI_API, params={
                    "action": "query", "prop": "pageimages", "piprop": "thumbnail|original",
                    "pithumbsize": THUMB_SIZE, "titles": titles_param, "format": "json",
                }, follow_redirects=True)
                if resp.status_code == 200:
                    data = resp.json()
                    pages = data.get("query", {}).get("pages", {})
                    for page in pages.values():
                        title = page.get("title", "")
                        thumb = page.get("thumbnail", {}).get("source")
                        original = page.get("original", {}).get("source")
                        if thumb or original:
                            _image_cache[title] = original or thumb
            except Exception as e:
                logger.error(f"Wiki image fetch error for batch {i}: {e}")
    _cache_loaded = True
    logger.info(f"Wiki image cache loaded: {len(_image_cache)} images cached")


def get_ship_image(ship_id_or_name):
    if ship_id_or_name in _image_cache:
        return _image_cache[ship_id_or_name]
    base = _get_base_name(ship_id_or_name)
    if base and base in _image_cache:
        return _image_cache[base]
    return ""


def get_vehicle_image(vehicle_name):
    return get_ship_image(vehicle_name)


def enhance_ship_data(ships):
    for ship in ships:
        img = get_ship_image(ship.get("name", ""))
        if img:
            ship["image"] = img
        elif not ship.get("image"):
            ship["image"] = ""
        if "beam" not in ship:
            ship["beam"] = round(ship.get("length", 20) * 0.6, 1)
        if "height" not in ship:
            ship["height"] = round(ship.get("length", 20) * 0.3, 1)
        if "mass" not in ship:
            ship["mass"] = int(ship.get("length", 20) * 1000)
        if "max_speed" not in ship:
            ship["max_speed"] = 220 if ship.get("size") == "Small" else (180 if ship.get("size") == "Medium" else 150)
        if "role" not in ship:
            ship["role"] = "Multi-role"
        if "description" not in ship:
            ship["description"] = f"The {ship['name']} by {ship['manufacturer']} is a {ship.get('size', 'multi').lower()}-class vessel designed for versatility and performance."
        if "price" not in ship:
            price_map = {"Snub": 50000, "Small": 100000, "Medium": 500000, "Large": 2000000, "Capital": 10000000}
            ship["price"] = price_map.get(ship.get("size"), 100000)
        if "armor" not in ship:
            ship["armor"] = "Medium" if ship.get("size") in ["Medium", "Large"] else "Light"
        if "manufacturer_code" not in ship:
            ship["manufacturer_code"] = ship["manufacturer"].split()[0][:3].upper()
    return ships
