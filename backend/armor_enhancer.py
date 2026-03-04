"""Armor data enhancer - CStone + Wiki images and variant data for armor sets."""

import httpx
import logging

logger = logging.getLogger(__name__)

WIKI_API = "https://starcitizen.tools/api.php"
THUMB_SIZE = 600
CSTONE_IMG = "https://cstone.space/uifimages/{}.png"
CSTONE_API = "https://finder.cstone.space/GetArmors/Torsos"

ARMOR_WIKI_OVERRIDES = {
    "ADP": "ADP", "ADP-mk4": "ADP-mk4", "Citadel": "Citadel", "Defiance": "Defiance",
    "Inquisitor": "Inquisitor", "TrueDef-Pro": "TrueDef-Pro", "Morozov-SH": "Morozov-SH",
    "RRS": "Roussimoff Rehabilitation Systems", "Overlord": "Overlord", "Palatino": "Palatino",
    "Artimex": "Artimex", "Aril": "Aril", "Aves": "Aves", "Novikov": "Novikov Exploration Suit",
    "Lynx": "Lynx", "Arden-SL": "Arden-SL", "Aztalan": "Aztalan", "Calico": "Calico",
    "FBL-8a": "FBL-8a", "Sterling": "Sterling", "Pembroke": "Pembroke Exploration Suit",
    "Odyssey II": "Odyssey II", "Sol-III": "Sol-III", "ORC-mkX": "ORC-mkX", "ORC-mkV": "ORC-mkV",
    "MacFlex": "MacFlex", "Venture": "Venture", "PAB-1": "PAB-1", "Corbel": "Corbel",
    "Antium": "Antium",
}

_armor_image_cache = {}
_armor_cache_loaded = False
_armor_variant_image_cache = {}
_armor_variant_cache_loaded = False
_cstone_armor_cache = {}
_cstone_cache_loaded = False

# Per-set loot location data
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
    global _armor_image_cache, _armor_cache_loaded
    if _armor_cache_loaded:
        return
    titles = list(set(ARMOR_WIKI_OVERRIDES.values()))
    logger.info(f"Fetching wiki armor images for {len(titles)} sets...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        titles_param = "|".join(t.replace(" ", "_") for t in titles)
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
                        _armor_image_cache[title] = original or thumb
        except Exception as e:
            logger.error(f"Armor image fetch error: {e}")
    _armor_cache_loaded = True
    logger.info(f"Armor image cache loaded: {len(_armor_image_cache)} images cached")


async def fetch_armor_variant_images(armor_sets):
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
                    "action": "query", "list": "allimages", "aifrom": wiki_prefix,
                    "ailimit": 50, "format": "json",
                }, follow_redirects=True)
                if resp.status_code != 200:
                    continue
                images = resp.json().get("query", {}).get("allimages", [])
                prefix_lower = wiki_prefix.lower().replace("-", "").replace(" ", "")
                core_images = {}
                set_images = {}
                for img in images:
                    fname = img["name"]
                    fname_lower = fname.lower().replace("-", "").replace(" ", "")
                    if prefix_lower not in fname_lower:
                        continue
                    if "core" in fname_lower and "ingame" in fname_lower:
                        core_images[fname] = img["url"]
                    elif "armor_set" in fname_lower:
                        set_images[fname] = img["url"]
                for variant in variants:
                    suffix = variant.replace(armor_name, "").strip()
                    if not suffix:
                        continue
                    suffix_normalized = suffix.replace("/", "_").replace(" ", "_").lower()
                    matched = False
                    for fname, url in core_images.items():
                        fname_part = fname.split("_-_")[0] if "_-_" in fname else fname
                        if "_Core_" in fname_part:
                            fname_variant = fname_part.split("_Core_", 1)[1].replace("_", " ").strip().lower()
                            fname_variant_norm = fname_variant.replace(" ", "_")
                            if suffix_normalized == fname_variant_norm or suffix.lower() == fname_variant:
                                _armor_variant_image_cache[variant] = url
                                matched = True
                                break
                    if not matched:
                        for fname, url in set_images.items():
                            fname_clean = fname.lower().replace("-", "").replace("_", "")
                            suffix_clean = suffix.lower().replace("-", "").replace(" ", "").replace("_", "")
                            if suffix_clean in fname_clean:
                                _armor_variant_image_cache[variant] = url
                                break
            except Exception as e:
                logger.error(f"Variant image fetch error for {armor_name}: {e}")
    _armor_variant_cache_loaded = True
    logger.info(f"Armor variant image cache loaded: {len(_armor_variant_image_cache)} variant images cached")


async def fetch_cstone_armor_images():
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
                    "uuid": uuid, "sold": item.get("Sold", 0),
                }
        except Exception as e:
            logger.error(f"CStone fetch error: {e}")
    _cstone_cache_loaded = True
    total = sum(len(v) for v in _cstone_armor_cache.values())
    logger.info(f"CStone armor cache loaded: {len(_cstone_armor_cache)} sets, {total} total variants")


def get_armor_image(armor_name):
    cstone_set = _cstone_armor_cache.get(armor_name, {})
    base_entry = cstone_set.get("Base", {})
    base_uuid = base_entry.get("uuid", "") if isinstance(base_entry, dict) else ""
    if base_uuid:
        return CSTONE_IMG.format(base_uuid)
    wiki_title = ARMOR_WIKI_OVERRIDES.get(armor_name, armor_name)
    return _armor_image_cache.get(wiki_title, "")


def get_armor_variant_images(armor_name, variants):
    base_image = get_armor_image(armor_name)
    cstone_set = _cstone_armor_cache.get(armor_name, {})
    result = {}
    for v in variants:
        suffix = v.replace(armor_name, "").strip()
        entry = cstone_set.get(suffix, {})
        cstone_uuid = entry.get("uuid", "") if isinstance(entry, dict) else ""
        if cstone_uuid:
            result[v] = CSTONE_IMG.format(cstone_uuid)
            continue
        wiki_img = _armor_variant_image_cache.get(v)
        if wiki_img:
            result[v] = wiki_img
            continue
        result[v] = base_image
    return result


def _derive_variant_locations(armor_name, variant_name, suffix, sold):
    suffix_lower = suffix.lower().strip('"')
    locations = []
    loot_locations = []
    for pattern, locs in _EDITION_LOCATIONS.items():
        if pattern in suffix_lower:
            if sold:
                locations = locs
            else:
                loot_locations = locs
            return locations, loot_locations
    for kw in _EVENT_KEYWORDS:
        if kw in suffix_lower:
            loot_locations = ["Event exclusive / Limited time availability", "Subscriber flair reward"]
            return locations, loot_locations
    for kw in _LOOT_ONLY_KEYWORDS:
        if kw in suffix_lower:
            base_loot = _SET_LOOT_LOCATIONS.get(armor_name, ["Found in the verse"])
            loot_locations = base_loot[:2]
            return locations, loot_locations
    if sold:
        locations = ["Available at armor shops"]
    else:
        loot_locations = _SET_LOOT_LOCATIONS.get(armor_name, ["Looted from NPCs", "Found in the verse"])
    return locations, loot_locations


def get_armor_variant_data(armor_name, variants, base_price, base_locations, base_loot_locations):
    cstone_set = _cstone_armor_cache.get(armor_name, {})
    result = {}
    for v in variants:
        suffix = v.replace(armor_name, "").strip()
        entry = cstone_set.get(suffix, {})
        sold = entry.get("sold", 1) if isinstance(entry, dict) else 1
        if sold:
            derived_locs, derived_loot = _derive_variant_locations(armor_name, v, suffix, sold)
            result[v] = {
                "price_auec": base_price,
                "locations": derived_locs if derived_locs else base_locations,
                "loot_locations": derived_loot if derived_loot else base_loot_locations,
                "sold": True,
            }
        else:
            derived_locs, derived_loot = _derive_variant_locations(armor_name, v, suffix, sold)
            result[v] = {
                "price_auec": 0,
                "locations": derived_locs,
                "loot_locations": derived_loot if derived_loot else ["Looted from NPCs", "Found in the verse"],
                "sold": False,
            }
    return result
