"""Ship data enhancer - fetches images from Star Citizen Wiki and adds details to ship data"""

import httpx
import logging

logger = logging.getLogger(__name__)

WIKI_API = "https://starcitizen.tools/api.php"
THUMB_SIZE = 600

# ship_id -> wiki page title mapping
SHIP_WIKI_MAP = {
    # Origin Jumpworks
    "85x": "85X",
    "100i": "100i",
    "125a": "125a",
    "135c": "135c",
    "300i": "300i",
    "315p": "315p",
    "325a": "325a",
    "350r": "350r",
    "400i": "400i",
    "600i": "600i Explorer",
    "600i-touring": "600i Explorer",
    "890jump": "890 Jump",
    # Anvil Aerospace
    "arrow": "Arrow",
    "hawk": "Hawk",
    "hornet-f7c": "F7C Hornet Mk II",
    "hornet-f7cm": "F7C-M Super Hornet Mk II",
    "hornet-f7cs": "F7C-S Hornet Ghost Mk II",
    "hornet-f7a": "F7A Hornet Mk II",
    "gladiator": "Gladiator",
    "hurricane": "Hurricane",
    "terrapin": "Terrapin",
    "valkyrie": "Valkyrie",
    "carrack": "Carrack",
    "liberator": "Liberator",
    "crucible": "Crucible",
    # Roberts Space Industries
    "aurora-ln": "Aurora LN",
    "aurora-mr": "Aurora MR",
    "aurora-cl": "Aurora CL",
    "aurora-lx": "Aurora LX",
    "aurora-es": "Aurora ES",
    "mantis": "Mantis",
    "scorpius": "Scorpius",
    "constellation-andromeda": "Constellation Andromeda",
    "constellation-aquila": "Constellation Aquila",
    "constellation-taurus": "Constellation Taurus",
    "constellation-phoenix": "Constellation Phoenix",
    "perseus": "Perseus",
    "polaris": "Polaris",
    "galaxy": "Galaxy",
    # Aegis Dynamics
    "avenger-titan": "Avenger Titan",
    "avenger-stalker": "Avenger Stalker",
    "avenger-warlock": "Avenger Warlock",
    "sabre": "Sabre",
    "sabre-comet": "Sabre Comet",
    "gladius": "Gladius",
    "vanguard-warden": "Vanguard Warden",
    "vanguard-sentinel": "Vanguard Sentinel",
    "vanguard-harbinger": "Vanguard Harbinger",
    "vanguard-hoplite": "Vanguard Hoplite",
    "eclipse": "Eclipse",
    "retaliator": "Retaliator",
    "redeemer": "Redeemer",
    "hammerhead": "Hammerhead",
    "reclaimer": "Reclaimer",
    "nautilus": "Nautilus",
    "idris-p": "Idris-P",
    "idris-m": "Idris-M",
    "javelin": "Javelin",
    # Drake Interplanetary
    "dragonfly-black": "Dragonfly",
    "dragonfly-yellow": "Dragonfly",
    "buccaneer": "Buccaneer",
    "herald": "Herald",
    "cutlass-black": "Cutlass Black",
    "cutlass-red": "Cutlass Red",
    "cutlass-blue": "Cutlass Blue",
    "corsair": "Corsair",
    "caterpillar": "Caterpillar",
    "vulture": "Vulture",
    "kraken": "Kraken",
    # Crusader Industries
    "ares-ion": "Ares Star Fighter Ion",
    "ares-inferno": "Ares Star Fighter Inferno",
    "spirit-a1": "Spirit",
    "spirit-c1": "Spirit",
    "mercury": "Mercury Star Runner",
    "starlifter-m2": "M2 Hercules Starlifter",
    "starlifter-c2": "C2 Hercules Starlifter",
    "starlifter-a2": "A2 Hercules Starlifter",
    "genesis": "Genesis Starliner",
    "odyssey": "Odyssey",
    # MISC
    "prospector": "Prospector",
    "razor": "Razor",
    "reliant-kore": "Reliant Kore",
    "reliant-tana": "Reliant Tana",
    "reliant-sen": "Reliant Sen",
    "reliant-mako": "Reliant Mako",
    "freelancer": "Freelancer",
    "freelancer-dur": "Freelancer DUR",
    "freelancer-max": "Freelancer MAX",
    "freelancer-mis": "Freelancer MIS",
    "hull-a": "Hull A",
    "hull-b": "Hull B",
    "hull-c": "Hull C",
    "starfarer": "Starfarer",
    "starfarer-gemini": "Starfarer Gemini",
    "endeavor": "Endeavor",
    # Aopoa
    "nox": "Nox",
    "nox-kue": "Nox Kue",
    "khartu-al": "Khartu-al",
    "san-tok-yai": "San'tok.yāi",
    # Banu
    "defender": "Defender",
    "merchantman": "Merchantman",
    # Esperia
    "blade": "Blade",
    "glaive": "Glaive",
    "prowler": "Prowler",
    "talon": "Talon",
    "talon-shrike": "Talon Shrike",
    # Argo Astronautics
    "mpuv-cargo": "MPUV Cargo",
    "mpuv-personnel": "MPUV Personnel",
    "mole": "MOLE",
    "raft": "RAFT",
    # Consolidated Outland
    "mustang-alpha": "Mustang Alpha",
    "mustang-beta": "Mustang Beta",
    "mustang-gamma": "Mustang Gamma",
    "mustang-delta": "Mustang Delta",
    "mustang-omega": "Mustang Omega",
    "nomad": "Nomad",
    "pioneer": "Pioneer",
}

VEHICLE_WIKI_MAP = {
    "cyclone": "Cyclone",
    "nox": "Nox",
    "ursa": "Ursa",
    "nova": "Nova",
}

# In-memory image cache: wiki_title -> thumbnail_url
_image_cache = {}
_cache_loaded = False


async def fetch_all_wiki_images():
    """Batch-fetch all ship/vehicle images from starcitizen.tools wiki API."""
    global _image_cache, _cache_loaded
    if _cache_loaded:
        return

    all_titles = set(SHIP_WIKI_MAP.values()) | set(VEHICLE_WIKI_MAP.values())
    title_list = list(all_titles)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Wiki API supports up to 50 titles per request
        for i in range(0, len(title_list), 50):
            batch = title_list[i:i + 50]
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
                            logger.info(f"Cached image for: {title}")
            except Exception as e:
                logger.error(f"Wiki image fetch error for batch {i}: {e}")

    _cache_loaded = True
    logger.info(f"Wiki image cache loaded: {len(_image_cache)} images cached")


def get_ship_image(ship_id):
    """Get cached wiki image URL for a ship."""
    wiki_title = SHIP_WIKI_MAP.get(ship_id.lower(), "")
    return _image_cache.get(wiki_title, "")


def get_vehicle_image(vehicle_name):
    """Get cached wiki image URL for a vehicle."""
    # Try exact match by name key
    key = vehicle_name.lower().replace(" ", "").replace("rover", "").replace("tank", "").strip()
    for vid, wiki_title in VEHICLE_WIKI_MAP.items():
        if vid in key or key in vid:
            return _image_cache.get(wiki_title, "")
    # Direct title lookup
    return _image_cache.get(vehicle_name, "")


def enhance_ship_data(ships):
    """Add comprehensive details to ship list."""
    for ship in ships:
        # Use wiki image from cache
        img = get_ship_image(ship["id"])
        if img:
            ship["image"] = img
        elif not ship.get("image"):
            ship["image"] = ""

        # Add missing fields with defaults
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
