"""Ship data enhancer - fetches images from Star Citizen Wiki by ship name."""

import httpx
import logging
import re

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
    "A1 Spirit": "Spirit",
    "C1 Spirit": "Spirit",
    "A2 Hercules Starlifter": "A2 Hercules",
    "C2 Hercules Starlifter": "C2 Hercules Starlifter",
    "M2 Hercules Starlifter": "M2 Hercules Starlifter",
    "600i 2951 BIS": "600i Explorer",
    "600i Executive Edition": "600i Explorer",
    "600i": "600i Explorer",
    "85X Limited": "85X",
    "890 Jump": "890 Jump",
    "Dragonfly Yellowjacket": "Dragonfly",
    "Dragonfly Star Kitten": "Dragonfly",
    "Nox Wikelo Special": "Nox",
    "P-72 Archimedes Emerald": "P-72 Archimedes",
    "Fury LX": "Fury",
    "Fury MX": "Fury",
    "Pulse LX": "Pulse",
    "X1 Force": "X1",
    "X1 Velocity": "X1",
    "Golem OX": "Golem",
    "Guardian MX": "Guardian",
    "Guardian QI": "Guardian",
    "Ballista Dunestalker": "Ballista",
    "Ballista Snowblind": "Ballista",
    "Cutter Rambler": "Cutter",
    "Cutter Scout": "Cutter",
    "C8R Pisces Rescue": "C8 Pisces",
    "MOLE Carbon": "MOLE",
    "MOLE Talus": "MOLE",
    "MPUV Tractor": "MPUV Cargo",
    "Corsair PYAM Exec": "Corsair",
    "Cutlass Black PYAM Exec": "Cutlass Black",
    "L-22 Alpha Wolf": "L-21 Wolf",
    "Prowler Utility": "Prowler",
    "ROC-DS": "ROC",
    "Terrapin Medic": "Terrapin",
    "Sabre Firebird": "Sabre",
    "Sabre Peregrine": "Sabre",
    "Constellation Phoenix Emerald": "Constellation Phoenix",
    "Caterpillar Pirate": "Caterpillar",
    "Gladius Dunlevy": "Gladius",
    "Gladius Pirate": "Gladius",
    "Gladius Valiant": "Gladius",
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
    "Nomad Teach's Special": "Nomad",
    "Starfarer Teach's Special": "Starfarer",
    "Reclaimer Teach's Special": "Reclaimer",
    "Vulture Teach's Special": "Vulture",
    "Syulen PYAM Exec": "Syulen",
    "Mustang CitizenCon 2948 Edition": "Mustang Alpha",
    "ATLS Cool Metal Color": "ATLS",
    "ATLS GEO": "ATLS",
    "ATLS GEO IKTI": "ATLS",
    "ATLS IKTI": "ATLS",
    "ATLS IKTI Rad": "ATLS",
    "ATLS Orange Line": "ATLS",
    "ATLS Snowland Color": "ATLS",
    "Scorpius Wikelo Sneak Special": "Scorpius",
    "Constellation Taurus Wikelo War Special": "Constellation Taurus",
    "C1 Spirit Wikelo Special": "Spirit",
    "Prospector Wikelo Work Special": "Prospector",
    "RAFT Wikelo Work Special": "RAFT",
    "M50 Interceptor": "M50",
    "Vanduul Scythe": "Glaive",
    "Power Suit": "",
    "CSV-SM\n": "CSV-SM",
    "Esperia Stinger": "Glaive",
}

# name -> image URL
_image_cache = {}
_cache_loaded = False


def _get_base_name(name):
    """Strip variant suffixes to get the base ship name for image lookup."""
    # Check overrides first
    if name in NAME_OVERRIDES:
        return NAME_OVERRIDES[name]
    # Strip known variant suffixes
    base = name
    for pattern in VARIANT_SUFFIXES:
        base = re.sub(pattern, "", base, flags=re.IGNORECASE).strip()
    return base


def _collect_wiki_titles(ship_names):
    """Build a set of wiki page titles to query from a list of ship names."""
    titles = set()
    for name in ship_names:
        wiki_title = _get_base_name(name)
        if wiki_title:
            titles.add(wiki_title)
        # Also add the original name in case it matches directly
        if name and name not in NAME_OVERRIDES:
            titles.add(name)
    return titles


async def fetch_all_wiki_images(ship_names=None):
    """Batch-fetch ship images from starcitizen.tools wiki API.
    If ship_names is provided, query those; otherwise use a default set."""
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
                    "action": "query",
                    "prop": "pageimages",
                    "piprop": "thumbnail|original",
                    "pithumbsize": THUMB_SIZE,
                    "titles": titles_param,
                    "format": "json",
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
    """Get cached wiki image URL for a ship by name or ID."""
    # Try direct name match
    if ship_id_or_name in _image_cache:
        return _image_cache[ship_id_or_name]
    # Try base name (strip variant)
    base = _get_base_name(ship_id_or_name)
    if base and base in _image_cache:
        return _image_cache[base]
    return ""


def get_vehicle_image(vehicle_name):
    """Get cached wiki image URL for a vehicle by name."""
    return get_ship_image(vehicle_name)


# ---- Armor Image Support ----

ARMOR_WIKI_OVERRIDES = {
    "ADP": "ADP",
    "ADP-mk4": "ADP-mk4",
    "Citadel": "Citadel",
    "Defiance": "Defiance",
    "Inquisitor": "Inquisitor",
    "TrueDef-Pro": "TrueDef-Pro",
    "Morozov-SH": "Morozov-SH",
    "RRS": "Roussimoff Rehabilitation Systems",
    "Overlord": "Overlord",
    "Palatino": "Palatino",
    "Artimex": "Artimex",
    "Aril": "Aril",
    "Aves": "Aves",
    "Novikov": "Novikov Exploration Suit",
    "Lynx": "Lynx",
    "Arden-SL": "Arden-SL",
    "Aztalan": "Aztalan",
    "Calico": "Calico",
    "FBL-8a": "FBL-8a",
    "Sterling": "Sterling",
    "Pembroke": "Pembroke Exploration Suit",
    "Odyssey II": "Odyssey II",
    "Sol-III": "Sol-III",
    "ORC-mkX": "ORC-mkX",
    "ORC-mkV": "ORC-mkV",
    "MacFlex": "MacFlex",
    "Venture": "Venture",
    "PAB-1": "PAB-1",
    "Corbel": "Corbel",
    "Antium": "Antium",
}

_armor_image_cache = {}
_armor_cache_loaded = False
# variant name -> image URL  (e.g. "ORC-mkX Woodland" -> "https://...")
_armor_variant_image_cache = {}
_armor_variant_cache_loaded = False
# CStone UUID-based images: {set_name -> {variant_suffix -> uuid}}
_cstone_armor_cache = {}
_cstone_cache_loaded = False

CSTONE_API = "https://finder.cstone.space/GetArmors/Torsos"
CSTONE_IMG = "https://cstone.space/uifimages/{}.png"


async def fetch_armor_images():
    """Batch-fetch armor set images from the Star Citizen wiki."""
    global _armor_image_cache, _armor_cache_loaded
    if _armor_cache_loaded:
        return

    titles = list(set(ARMOR_WIKI_OVERRIDES.values()))
    logger.info(f"Fetching wiki armor images for {len(titles)} sets...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        titles_param = "|".join(t.replace(" ", "_") for t in titles)
        try:
            resp = await client.get(WIKI_API, params={
                "action": "query",
                "prop": "pageimages",
                "piprop": "thumbnail|original",
                "pithumbsize": THUMB_SIZE,
                "titles": titles_param,
                "format": "json",
            }, follow_redirects=True)
            if resp.status_code == 200:
                pages = resp.json().get("query", {}).get("pages", {})
                for page in pages.values():
                    title = page.get("title", "")
                    thumb = page.get("thumbnail", {}).get("source")
                    original = page.get("original", {}).get("source")
                    if thumb or original:
                        _armor_image_cache[title] = original or thumb
        except Exception as e:
            logger.error(f"Armor image fetch error: {e}")

    _armor_cache_loaded = True
    logger.info(f"Armor image cache loaded: {len(_armor_image_cache)} images cached")


async def fetch_armor_variant_images(armor_sets):
    """Fetch variant-specific images for all armor sets using the wiki allimages API.
    Looks for images matching pattern: {SetName}_Core_{VariantSuffix}_-_In-game_SCT_logo.jpg
    """
    global _armor_variant_image_cache, _armor_variant_cache_loaded
    if _armor_variant_cache_loaded:
        return

    async with httpx.AsyncClient(timeout=30.0) as client:
        for armor in armor_sets:
            armor_name = armor["name"]
            wiki_prefix = ARMOR_WIKI_OVERRIDES.get(armor_name, armor_name)
            variants = armor.get("variants", [])
            if not variants:
                continue

            try:
                resp = await client.get(WIKI_API, params={
                    "action": "query",
                    "list": "allimages",
                    "aifrom": wiki_prefix,
                    "ailimit": 50,
                    "format": "json",
                }, follow_redirects=True)
                if resp.status_code != 200:
                    continue

                images = resp.json().get("query", {}).get("allimages", [])
                # Build a lookup: normalize image filenames for matching
                prefix_lower = wiki_prefix.lower().replace("-", "").replace(" ", "")
                core_images = {}
                set_images = {}
                for img in images:
                    fname = img["name"]
                    fname_lower = fname.lower().replace("-", "").replace(" ", "")
                    # Only consider images that belong to this armor set
                    if prefix_lower not in fname_lower:
                        continue
                    # Variant core images: {Set}_Core_{Variant}_-_In-game_SCT_logo.jpg
                    if "core" in fname_lower and "ingame" in fname_lower:
                        core_images[fname] = img["url"]
                    # Full armor set images: {Set}_{Variant}_armor_set.jpg
                    elif "armor_set" in fname_lower:
                        set_images[fname] = img["url"]

                # Match variants to images
                for variant in variants:
                    # Extract the variant suffix (e.g., "ORC-mkX Woodland" -> "Woodland")
                    suffix = variant.replace(armor_name, "").strip()
                    if not suffix:
                        continue
                    # Normalize suffix for matching: "Red Silver" -> "red_silver"
                    suffix_normalized = suffix.replace("/", "_").replace(" ", "_").lower()

                    # Try core images first (best quality single-piece representation)
                    matched = False
                    for fname, url in core_images.items():
                        # Extract variant part from filename: {Set}_Core_{Variant}_-_In-game...
                        fname_part = fname.split("_-_")[0] if "_-_" in fname else fname
                        # Get the part after _Core_
                        if "_Core_" in fname_part:
                            fname_variant = fname_part.split("_Core_", 1)[1].replace("_", " ").strip().lower()
                            fname_variant_norm = fname_variant.replace(" ", "_")
                            if suffix_normalized == fname_variant_norm or suffix.lower() == fname_variant:
                                _armor_variant_image_cache[variant] = url
                                matched = True
                                break

                    # Fallback to full set images
                    if not matched:
                        for fname, url in set_images.items():
                            fname_clean = fname.lower().replace("-", "").replace("_", "")
                            suffix_clean = suffix.lower().replace("-", "").replace(" ", "").replace("_", "")
                            if suffix_clean in fname_clean:
                                _armor_variant_image_cache[variant] = url
                                matched = True
                                break

            except Exception as e:
                logger.error(f"Variant image fetch error for {armor_name}: {e}")

    _armor_variant_cache_loaded = True
    logger.info(f"Armor variant image cache loaded: {len(_armor_variant_image_cache)} variant images cached")


async def fetch_cstone_armor_images():
    """Fetch all armor torso items from CStone API and build UUID->image cache."""
    global _cstone_armor_cache, _cstone_cache_loaded
    if _cstone_cache_loaded:
        return

    logger.info("Fetching CStone armor images...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(CSTONE_API, follow_redirects=True)
            if resp.status_code != 200:
                logger.error(f"CStone API returned {resp.status_code}")
                _cstone_cache_loaded = True
                return

            items = resp.json()
            for item in items:
                name = item.get("Name", "")
                uuid = item.get("ItemId", "")
                if not uuid or "(Modified)" in name or "XenoThreat" in name:
                    continue
                if " Core" not in name:
                    continue

                parts = name.split(" Core", 1)
                set_name = parts[0].strip()
                variant = parts[1].strip() if len(parts) > 1 and parts[1].strip() else "Base"

                if set_name not in _cstone_armor_cache:
                    _cstone_armor_cache[set_name] = {}
                _cstone_armor_cache[set_name][variant] = uuid

        except Exception as e:
            logger.error(f"CStone fetch error: {e}")

    _cstone_cache_loaded = True
    total = sum(len(v) for v in _cstone_armor_cache.values())
    logger.info(f"CStone armor cache loaded: {len(_cstone_armor_cache)} sets, {total} total variants")


def get_armor_image(armor_name):
    """Get cached image URL for an armor set. CStone base image as fallback."""
    wiki_title = ARMOR_WIKI_OVERRIDES.get(armor_name, armor_name)
    wiki_img = _armor_image_cache.get(wiki_title, "")
    if wiki_img:
        return wiki_img
    # Fallback to CStone base image
    cstone_set = _cstone_armor_cache.get(armor_name, {})
    base_uuid = cstone_set.get("Base", "")
    if base_uuid:
        return CSTONE_IMG.format(base_uuid)
    return ""


def get_armor_variant_images(armor_name, variants):
    """Get a dict mapping variant names to their image URLs.
    Priority: 1) Wiki variant image, 2) CStone variant image, 3) Base image."""
    base_image = get_armor_image(armor_name)
    cstone_set = _cstone_armor_cache.get(armor_name, {})
    result = {}
    for v in variants:
        # Check wiki cache first
        wiki_img = _armor_variant_image_cache.get(v)
        if wiki_img:
            result[v] = wiki_img
            continue
        # Check CStone cache
        suffix = v.replace(armor_name, "").strip()
        cstone_uuid = cstone_set.get(suffix, "")
        if cstone_uuid:
            result[v] = CSTONE_IMG.format(cstone_uuid)
            continue
        # Fallback to base image
        result[v] = base_image
    return result


# ---- FPS Weapon Image Support ----

WEAPON_WIKI_OVERRIDES = {
    "Arclight Pistol": "Arclight Pistol",
    "Coda Pistol": "Coda Pistol",
    "LH86 Pistol": "LH86 Pistol",
    "Yubarev Pistol": "Yubarev Pistol",
    "C54 SMG": "C54 SMG",
    "Custodian SMG": "Custodian SMG",
    "Ripper SMG": "Ripper SMG",
    "S71 Rifle": "S71 Rifle",
    "Karna Rifle": "Karna Rifle",
    "P4-AR Assault Rifle": "P4-AR Rifle",
    "Parallax Assault Rifle": "Parallax Energy Assault Rifle",
    "F55 LMG": "F55 LMG",
    "Demeco LMG": "Demeco LMG",
    "FS-9 LMG": "FS-9 LMG",
    "BR-2 Shotgun": "BR-2 Shotgun",
    "Ravager-212 Shotgun": "Ravager-212 Twin Shotgun",
    "A03 Sniper Rifle": "A03 Sniper Rifle",
    "Arrowhead Sniper Rifle": "Arrowhead Sniper Rifle",
    "P6-LR Sniper Rifle": "P6-LR Sniper Rifle",
    "Animus Missile Launcher": "Animus Missile Launcher",
    "GP-33 Grenade Launcher": "GP-33 MOD Grenade Launcher",
    "Frag Grenade": "MK-4 Frag Grenade",
    "MedPen": "MedPen (Hemozal)",
    "OxyPen": "OxyPen",
}

_weapon_image_cache = {}
_weapon_cache_loaded = False


async def fetch_weapon_images():
    """Batch-fetch FPS weapon images from the Star Citizen wiki."""
    global _weapon_image_cache, _weapon_cache_loaded
    if _weapon_cache_loaded:
        return

    titles = list(set(WEAPON_WIKI_OVERRIDES.values()))
    logger.info(f"Fetching wiki weapon images for {len(titles)} items...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Process in batches of 15
        for i in range(0, len(titles), 15):
            batch = titles[i:i+15]
            titles_param = "|".join(t.replace(" ", "_") for t in batch)
            try:
                resp = await client.get(WIKI_API, params={
                    "action": "query",
                    "prop": "pageimages",
                    "piprop": "thumbnail|original",
                    "pithumbsize": THUMB_SIZE,
                    "titles": titles_param,
                    "format": "json",
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


def get_weapon_image(weapon_name):
    """Get cached wiki image URL for an FPS weapon by name."""
    wiki_title = WEAPON_WIKI_OVERRIDES.get(weapon_name, weapon_name)
    return _weapon_image_cache.get(wiki_title, "")


def enhance_ship_data(ships):
    """Add comprehensive details to ship list (mock fallback only)."""
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
