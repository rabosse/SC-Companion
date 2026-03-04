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

# Per-set loot location data (for loot-only variants)
_SET_LOOT_LOCATIONS = {
    "ADP": ["Hurston security bunkers (Merlarian tab missions)", "Security NPC drops (Stanton)", "Bunker weapon racks & beige boxes"],
    "ADP-mk4": ["High-security bunkers (Pyro)", "Contested zone loot crates", "Xenomorph encounter zones"],
    "Antium": ["ASD Facilities (Lazarus, Phoenix hubs)", "Rare spawn in outpost beige boxes", "Pyro contested zones"],
    "Citadel": ["ASD Facilities (Lazarus/Phoenix, Pyro I)", "Checkmate Outpost (Olympus Principal)", "OLP stations above Aberdeen/Tamar", "Medical clinic beige boxes"],
    "Corbel": ["Ground bunker missions (Hurston/Stanton)", "Outlaw NPC drops", "Distribution center weapon racks"],
    "Defiance": ["Hurston bunkers & outposts", "Oil rigs (Cutters Rig, Makers Point)", "High-threat PvE mission loot"],
    "Morozov-SH": ["Crusader Security zone drops", "ASD Facilities", "Crusader patrol ship interdictions"],
    "Overlord": ["Pyro facilities (Lazarus, Tithanus 1-3, Phoenix)", "Beige boxes in blue buildings/warehouses", "Nine Tails NPC drops", "Subscriber flair (some variants)"],
    "Palatino": ["Rare bunker drops", "High-value target missions", "Pyro contested facilities"],
    "Artimex": ["Bunker missions (all regions)", "Distribution center loot", "Security facility weapon racks"],
    "Aril": ["Mining outpost loot crates", "Frontier exploration sites", "Abandoned facility beige boxes"],
    "Aves": ["Bounty hunter target drops", "Outlaw bunker missions", "Grim HEX area NPC drops"],
    "ORC-mkX": ["Bunker missions (all regions)", "Distribution centers", "Protector Marine NPC drops", "Hurston security zones"],
    "ORC-mkV": ["Security bunker missions", "Stanton patrol NPC drops", "Distribution center weapon racks"],
    "MacFlex": ["Cargo deck loot", "Common NPC drops (all regions)", "Station security zones"],
    "Venture": ["Exploration outpost loot", "Dumper's Depot overflow stock", "Civilian NPC drops"],
    "Inquisitor": ["Nine Tails NPC drops (Grim HEX area)", "Outlaw bunker missions", "Bounty target loot"],
    "TrueDef-Pro": ["Advocacy mission sites", "CDF facility loot", "Security NPC drops (all landing zones)"],
    "PAB-1": ["Crusader Security zone drops", "Police facility loot racks", "Hurston Security NPC drops"],
    "Lynx": ["General bunker missions", "Distribution center loot", "Common NPC drops"],
    "Arden-SL": ["Security facility weapon racks", "Crusader/Hurston Security NPC drops", "Cargo deck loot crates"],
    "FBL-8a": ["Military bunker missions", "Security NPC drops", "Outpost weapon racks"],
    "Calico": ["Outlaw bunker missions (Lorville area)", "Live Fire Weapons overflow", "Ground combat zone drops"],
    "Aztalan": ["Outlaw bunker missions", "Grim HEX area NPC loot", "Stealth operation sites"],
    "Sterling": ["Frontier outpost loot", "Exploration site beige boxes", "Rare NPC drops"],
    "Novikov": ["microTech surface mission loot", "Hatter Station area drops", "Cold-environment outpost crates"],
    "Pembroke": ["Extreme-environment outpost loot", "Mining facility crates", "Hazardous zone drops"],
    "Odyssey II": ["General station loot", "Cargo deck beige boxes", "Civilian area drops"],
    "Sol-III": ["Rare frontier drops", "High-value exploration sites", "Event exclusive spawns"],
}

# Edition-specific location overrides
_EDITION_LOCATIONS = {
    "crusader edition": ["Orison - Crusader Industries showroom", "Port Olisar armor shops", "Crusader Security NPC drops"],
    "hurston edition": ["Lorville - Tammany and Sons", "Hurston Security NPC drops", "HDMS outpost loot"],
    "covalex edition": ["Covalex Shipping Hub loot", "Covalex delivery mission rewards"],
    "microtech edition": ["New Babbage - Commons shops", "microTech Security NPC drops"],
    "cry-astro edition": ["Cry-Astro Rest Stop loot crates", "Service beacon reward drops"],
    "greycat edition": ["Greycat Industrial facility loot", "Mining outpost drops"],
    "sakura sun edition": ["Subscriber exclusive / Special event reward"],
    "carrack edition": ["Carrack exploration mission reward"],
    "red alert": ["High-threat bunker raids", "Emergency response mission loot"],
    "woodland": ["Forest/jungle planet surface loot (Hurston, microTech)", "Ground patrol NPC drops"],
    "desert": ["Desert planet surface loot (Daymar, Hurston)", "Arid outpost beige boxes"],
    "arctic": ["Frozen planet surface loot (microTech, Yela)", "Cold-environment outpost crates"],
    "imperial": ["High-end armor shops (limited stock)", "VIP escort mission rewards"],
    "executive": ["Premium shops (Area 18, New Babbage)", "Corporate facility loot"],
    "tactical": ["Military bunker missions", "Tactical operation NPC drops"],
    "scorched": ["Pyro surface loot", "Fire/heat zone outpost crates"],
    "cdf": ["CDF (Crusader Defense Force) facility raids", "Military patrol NPC drops"],
}
_LOOT_ONLY_KEYWORDS = {"rust society", "damaged", "justified", "righteous", "epoque", "rucksack"}
_EVENT_KEYWORDS = {"ascension", "envy", "lovestruck", "starcrossed", "pathfinder", "voyager", "hearthrob"}


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
    """Fetch all armor torso items from CStone API and build UUID->image cache + variant metadata."""
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
                _cstone_armor_cache[set_name][variant] = {
                    "uuid": uuid,
                    "sold": item.get("Sold", 0),
                }

        except Exception as e:
            logger.error(f"CStone fetch error: {e}")

    _cstone_cache_loaded = True
    total = sum(len(v) for v in _cstone_armor_cache.values())
    logger.info(f"CStone armor cache loaded: {len(_cstone_armor_cache)} sets, {total} total variants")


def get_armor_image(armor_name):
    """Get cached image URL for an armor set. CStone is primary, wiki as fallback."""
    # CStone first - consistent, accurate in-game images
    cstone_set = _cstone_armor_cache.get(armor_name, {})
    base_entry = cstone_set.get("Base", {})
    base_uuid = base_entry.get("uuid", "") if isinstance(base_entry, dict) else ""
    if base_uuid:
        return CSTONE_IMG.format(base_uuid)
    # Fallback to wiki
    wiki_title = ARMOR_WIKI_OVERRIDES.get(armor_name, armor_name)
    return _armor_image_cache.get(wiki_title, "")


def get_armor_variant_images(armor_name, variants):
    """Get a dict mapping variant names to their image URLs.
    Priority: 1) CStone variant image, 2) Wiki variant image, 3) Base image."""
    base_image = get_armor_image(armor_name)
    cstone_set = _cstone_armor_cache.get(armor_name, {})
    result = {}
    for v in variants:
        # CStone first - consistent in-game renders
        suffix = v.replace(armor_name, "").strip()
        entry = cstone_set.get(suffix, {})
        cstone_uuid = entry.get("uuid", "") if isinstance(entry, dict) else ""
        if cstone_uuid:
            result[v] = CSTONE_IMG.format(cstone_uuid)
            continue
        # Wiki fallback
        wiki_img = _armor_variant_image_cache.get(v)
        if wiki_img:
            result[v] = wiki_img
            continue
        # Fallback to base image
        result[v] = base_image
    return result


def _derive_variant_locations(armor_name, variant_name, suffix, sold):
    """Derive acquisition locations for a specific variant based on its name, set, and sold status."""
    suffix_lower = suffix.lower().strip('"')
    locations = []
    loot_locations = []

    # Check edition-specific location overrides first
    for pattern, locs in _EDITION_LOCATIONS.items():
        if pattern in suffix_lower:
            if sold:
                locations = locs
            else:
                loot_locations = locs
            return locations, loot_locations

    # Check event keywords
    for kw in _EVENT_KEYWORDS:
        if kw in suffix_lower:
            loot_locations = ["Event exclusive / Limited time availability", "Subscriber flair reward"]
            return locations, loot_locations

    # Check loot-only keywords
    for kw in _LOOT_ONLY_KEYWORDS:
        if kw in suffix_lower:
            base_loot = _SET_LOOT_LOCATIONS.get(armor_name, ["Found in the verse"])
            loot_locations = base_loot[:2]
            return locations, loot_locations

    if sold:
        # Purchasable: use "available at armor shops" generically
        locations = ["Available at armor shops"]
    else:
        # Loot-only: use set-specific loot locations
        loot_locations = _SET_LOOT_LOCATIONS.get(armor_name, ["Looted from NPCs", "Found in the verse"])

    return locations, loot_locations


def get_armor_variant_data(armor_name, variants, base_price, base_locations, base_loot_locations):
    """Get per-variant acquisition data: locations, prices, sold status."""
    cstone_set = _cstone_armor_cache.get(armor_name, {})
    result = {}
    for v in variants:
        suffix = v.replace(armor_name, "").strip()
        entry = cstone_set.get(suffix, {})
        sold = entry.get("sold", 1) if isinstance(entry, dict) else 1

        if sold:
            # Purchasable: use base price and derive locations
            derived_locs, derived_loot = _derive_variant_locations(armor_name, v, suffix, sold)
            result[v] = {
                "price_auec": base_price,
                "locations": derived_locs if derived_locs else base_locations,
                "loot_locations": derived_loot if derived_loot else base_loot_locations,
                "sold": True,
            }
        else:
            # Loot only: no price, derive loot locations
            derived_locs, derived_loot = _derive_variant_locations(armor_name, v, suffix, sold)
            result[v] = {
                "price_auec": 0,
                "locations": derived_locs,
                "loot_locations": derived_loot if derived_loot else ["Looted from NPCs", "Found in the verse"],
                "sold": False,
            }
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

# CStone weapon cache: {base_weapon_name -> {variant_suffix -> {uuid, sold}}}
_cstone_weapon_cache = {}
_cstone_weapon_cache_loaded = False

CSTONE_WEAPON_API = "https://finder.cstone.space/GetFPSWeapons"

# Per-weapon-type loot locations
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


async def fetch_cstone_weapon_images():
    """Fetch all FPS weapons from CStone API and build variant cache."""
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

                # Parse: '{Base} "{Variant}" {Type}' or '{Base} {Type}'
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
                    "uuid": uuid,
                    "sold": item.get("Sold", 0),
                }

        except Exception as e:
            logger.error(f"CStone weapon fetch error: {e}")

    _cstone_weapon_cache_loaded = True
    total = sum(len(v) for v in _cstone_weapon_cache.values())
    logger.info(f"CStone weapon cache loaded: {len(_cstone_weapon_cache)} weapons, {total} total variants")


def get_weapon_image(weapon_name):
    """Get image URL for a weapon. CStone primary, wiki fallback."""
    # CStone first
    cstone_wep = _cstone_weapon_cache.get(weapon_name, {})
    base_entry = cstone_wep.get("Base", {})
    base_uuid = base_entry.get("uuid", "") if isinstance(base_entry, dict) else ""
    if base_uuid:
        return CSTONE_IMG.format(base_uuid)
    # Wiki fallback
    wiki_title = WEAPON_WIKI_OVERRIDES.get(weapon_name, weapon_name)
    return _weapon_image_cache.get(wiki_title, "")


def get_weapon_variant_images(weapon_name, variants):
    """Get a dict mapping weapon variant names to CStone image URLs."""
    base_image = get_weapon_image(weapon_name)
    cstone_wep = _cstone_weapon_cache.get(weapon_name, {})
    result = {}
    for v in variants:
        # Extract the variant suffix in quotes: 'Arclight "Boneyard" Pistol' -> 'Boneyard'
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
    """Get per-variant acquisition data for weapons."""
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
