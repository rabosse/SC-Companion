"""Star Citizen system location data and route calculation for Stanton, Pyro, and Nyx."""

import math

# Quantum drive speeds by size (km/s) - averaged from game data
QD_SPEEDS = {
    0: 100_000,   # Snub / no QD
    1: 165_000,   # Small
    2: 190_000,   # Medium  
    3: 240_000,   # Large
    4: 280_000,   # Large+
    5: 319_000,   # Capital
    6: 718_000,   # Super-Capital
}

# Quantum fuel model per QD size class
# range_mkm = max quantum travel distance before empty
QD_FUEL_DEFAULTS = {
    0: {"range_mkm": 0},
    1: {"range_mkm": 120},     # Snub/Small ~120 Mkm
    2: {"range_mkm": 180},     # Small ~180 Mkm
    3: {"range_mkm": 100},     # Medium ~100 Mkm (faster but less efficient)
    4: {"range_mkm": 130},     # Large ~130 Mkm
    5: {"range_mkm": 250},     # Capital ~250 Mkm
    6: {"range_mkm": 2000},    # Super-Capital
}

# 2D map coordinates: (x, y) in arbitrary units for visual layout
# Systems are spread across the map; locations within each system orbit their star
SYSTEMS = {
    "stanton": {
        "name": "Stanton",
        "star": {"x": 0, "y": 0},
        "color": "#00D4FF",
    },
    "pyro": {
        "name": "Pyro",
        "star": {"x": 520, "y": -80},
        "color": "#FF4500",
    },
    "nyx": {
        "name": "Nyx",
        "star": {"x": -420, "y": -160},
        "color": "#A855F7",
    },
}

# All navigable locations
# distance_from_star is in millions of km (Mkm), used for travel time calc
# map_x, map_y are visual 2D positions
LOCATIONS = [
    # === STANTON SYSTEM ===
    # Star
    {"id": "stanton-star", "name": "Stanton (Star)", "system": "stanton", "type": "star", "map_x": 0, "map_y": 0, "distance_from_star": 0},
    # Planets
    {"id": "hurston", "name": "Hurston", "system": "stanton", "type": "planet", "map_x": -80, "map_y": 60, "distance_from_star": 12.85, "landing_zone": "Lorville", "description": "Polluted mining world. Home to Hurston Dynamics."},
    {"id": "crusader", "name": "Crusader", "system": "stanton", "type": "planet", "map_x": 40, "map_y": 100, "distance_from_star": 20.93, "landing_zone": "Orison", "description": "Gas giant with floating platforms. Crusader Industries HQ."},
    {"id": "arccorp", "name": "ArcCorp", "system": "stanton", "type": "planet", "map_x": 100, "map_y": -30, "distance_from_star": 30.0, "landing_zone": "Area 18", "description": "Fully urbanized manufacturing planet."},
    {"id": "microtech", "name": "microTech", "system": "stanton", "type": "planet", "map_x": -30, "map_y": -110, "distance_from_star": 45.37, "landing_zone": "New Babbage", "description": "Frozen world. Home to microTech and mobiGlas."},
    # Hurston Moons
    {"id": "arial", "name": "Arial", "system": "stanton", "type": "moon", "map_x": -100, "map_y": 45, "distance_from_star": 12.6, "parent": "hurston"},
    {"id": "aberdeen", "name": "Aberdeen", "system": "stanton", "type": "moon", "map_x": -95, "map_y": 80, "distance_from_star": 13.1, "parent": "hurston"},
    {"id": "magda", "name": "Magda", "system": "stanton", "type": "moon", "map_x": -60, "map_y": 55, "distance_from_star": 12.9, "parent": "hurston"},
    {"id": "ita", "name": "Ita", "system": "stanton", "type": "moon", "map_x": -70, "map_y": 75, "distance_from_star": 13.0, "parent": "hurston"},
    # Crusader Moons
    {"id": "cellin", "name": "Cellin", "system": "stanton", "type": "moon", "map_x": 25, "map_y": 115, "distance_from_star": 20.5, "parent": "crusader"},
    {"id": "daymar", "name": "Daymar", "system": "stanton", "type": "moon", "map_x": 55, "map_y": 120, "distance_from_star": 21.3, "parent": "crusader"},
    {"id": "yela", "name": "Yela", "system": "stanton", "type": "moon", "map_x": 60, "map_y": 90, "distance_from_star": 21.0, "parent": "crusader"},
    # ArcCorp Moons
    {"id": "lyria", "name": "Lyria", "system": "stanton", "type": "moon", "map_x": 115, "map_y": -15, "distance_from_star": 29.5, "parent": "arccorp"},
    {"id": "wala", "name": "Wala", "system": "stanton", "type": "moon", "map_x": 120, "map_y": -45, "distance_from_star": 30.5, "parent": "arccorp"},
    # microTech Moons
    {"id": "calliope", "name": "Calliope", "system": "stanton", "type": "moon", "map_x": -15, "map_y": -125, "distance_from_star": 45.0, "parent": "microtech"},
    {"id": "clio", "name": "Clio", "system": "stanton", "type": "moon", "map_x": -50, "map_y": -120, "distance_from_star": 45.5, "parent": "microtech"},
    {"id": "euterpe", "name": "Euterpe", "system": "stanton", "type": "moon", "map_x": -40, "map_y": -100, "distance_from_star": 44.8, "parent": "microtech"},
    # Lagrange Points / Stations
    {"id": "hur-l1", "name": "HUR-L1", "system": "stanton", "type": "station", "map_x": -50, "map_y": 35, "distance_from_star": 10.0, "description": "Lagrange point between Stanton and Hurston"},
    {"id": "hur-l2", "name": "HUR-L2", "system": "stanton", "type": "station", "map_x": -110, "map_y": 65, "distance_from_star": 15.0},
    {"id": "hur-l3", "name": "HUR-L3", "system": "stanton", "type": "station", "map_x": -75, "map_y": 40, "distance_from_star": 11.5},
    {"id": "hur-l4", "name": "HUR-L4 Melodic Fields", "system": "stanton", "type": "station", "map_x": -55, "map_y": 80, "distance_from_star": 13.5},
    {"id": "hur-l5", "name": "HUR-L5 High Course", "system": "stanton", "type": "station", "map_x": -90, "map_y": 30, "distance_from_star": 14.0},
    {"id": "cru-l1", "name": "CRU-L1", "system": "stanton", "type": "station", "map_x": 20, "map_y": 65, "distance_from_star": 16.0},
    {"id": "cru-l4", "name": "CRU-L4 Shallow Fields", "system": "stanton", "type": "station", "map_x": 70, "map_y": 70, "distance_from_star": 22.5},
    {"id": "cru-l5", "name": "CRU-L5", "system": "stanton", "type": "station", "map_x": 15, "map_y": 130, "distance_from_star": 23.0},
    {"id": "arc-l1", "name": "ARC-L1", "system": "stanton", "type": "station", "map_x": 65, "map_y": -10, "distance_from_star": 25.0},
    {"id": "arc-l2", "name": "ARC-L2", "system": "stanton", "type": "station", "map_x": 130, "map_y": -30, "distance_from_star": 33.0},
    {"id": "arc-l3", "name": "ARC-L3", "system": "stanton", "type": "station", "map_x": 80, "map_y": -50, "distance_from_star": 28.0},
    {"id": "arc-l4", "name": "ARC-L4 Faint Glen", "system": "stanton", "type": "station", "map_x": 130, "map_y": 10, "distance_from_star": 32.0},
    {"id": "arc-l5", "name": "ARC-L5", "system": "stanton", "type": "station", "map_x": 85, "map_y": -60, "distance_from_star": 29.0},
    {"id": "mic-l1", "name": "MIC-L1 Shallow Frontier", "system": "stanton", "type": "station", "map_x": -10, "map_y": -75, "distance_from_star": 38.0},
    {"id": "mic-l2", "name": "MIC-L2 Long Forest", "system": "stanton", "type": "station", "map_x": -15, "map_y": -140, "distance_from_star": 50.0},
    {"id": "mic-l3", "name": "MIC-L3 Endless Odyssey", "system": "stanton", "type": "station", "map_x": -60, "map_y": -145, "distance_from_star": 48.0},
    {"id": "mic-l4", "name": "MIC-L4 Red Crossroads", "system": "stanton", "type": "station", "map_x": 10, "map_y": -130, "distance_from_star": 47.0},
    {"id": "mic-l5", "name": "MIC-L5 Modern Icarus", "system": "stanton", "type": "station", "map_x": -55, "map_y": -90, "distance_from_star": 42.0},
    # Key Stations
    {"id": "port-olisar", "name": "Port Olisar", "system": "stanton", "type": "station", "map_x": 35, "map_y": 85, "distance_from_star": 20.0, "description": "Legacy orbital station near Crusader"},
    {"id": "everus-harbor", "name": "Everus Harbor", "system": "stanton", "type": "station", "map_x": -85, "map_y": 50, "distance_from_star": 12.5, "description": "Hurston orbital station"},
    {"id": "baijini-point", "name": "Baijini Point", "system": "stanton", "type": "station", "map_x": 95, "map_y": -20, "distance_from_star": 29.8, "description": "ArcCorp orbital station"},
    {"id": "port-tressler", "name": "Port Tressler", "system": "stanton", "type": "station", "map_x": -25, "map_y": -105, "distance_from_star": 45.0, "description": "microTech orbital station"},
    {"id": "grim-hex", "name": "Grim HEX", "system": "stanton", "type": "station", "map_x": 75, "map_y": 95, "distance_from_star": 21.5, "description": "Pirate outpost in Yela's asteroid belt"},
    # Jump Points
    {"id": "stanton-pyro-gw", "name": "Stanton-Pyro Gateway", "system": "stanton", "type": "gateway", "map_x": 200, "map_y": -40, "distance_from_star": 55.0, "description": "Jump point to Pyro system"},
    {"id": "stanton-nyx-gw", "name": "Stanton-Nyx Gateway", "system": "stanton", "type": "gateway", "map_x": -180, "map_y": -60, "distance_from_star": 52.0, "description": "Jump point to Nyx system"},
    # Landing Zones / Cities
    {"id": "lorville", "name": "Lorville", "system": "stanton", "type": "city", "map_x": -82, "map_y": 63, "distance_from_star": 12.85, "parent": "hurston", "description": "Capital city of Hurston. Hurston Dynamics HQ. Major trading hub."},
    {"id": "orison", "name": "Orison", "system": "stanton", "type": "city", "map_x": 43, "map_y": 103, "distance_from_star": 20.93, "parent": "crusader", "description": "Floating platform city in Crusader's atmosphere. Crusader Industries HQ."},
    {"id": "area18", "name": "Area 18", "system": "stanton", "type": "city", "map_x": 103, "map_y": -27, "distance_from_star": 30.0, "parent": "arccorp", "description": "Commercial district on ArcCorp. Shopping, trading, and nightlife."},
    {"id": "new-babbage", "name": "New Babbage", "system": "stanton", "type": "city", "map_x": -27, "map_y": -107, "distance_from_star": 45.37, "parent": "microtech", "description": "Luxury city on microTech. Home to microTech and mobiGlas HQ."},
    # Rest Stops (R&R)
    {"id": "hur-r1", "name": "R&R HUR-L1", "system": "stanton", "type": "rest_stop", "map_x": -48, "map_y": 32, "distance_from_star": 10.1, "description": "Rest stop between Stanton star and Hurston. Refuel, repair, restock."},
    {"id": "hur-r2", "name": "R&R HUR-L2", "system": "stanton", "type": "rest_stop", "map_x": -112, "map_y": 68, "distance_from_star": 15.1, "description": "Rest stop beyond Hurston orbit."},
    {"id": "cru-r1", "name": "R&R CRU-L1", "system": "stanton", "type": "rest_stop", "map_x": 22, "map_y": 62, "distance_from_star": 16.1, "description": "Rest stop between Stanton star and Crusader."},
    {"id": "arc-r1", "name": "R&R ARC-L1", "system": "stanton", "type": "rest_stop", "map_x": 67, "map_y": -7, "distance_from_star": 25.1, "description": "Rest stop on approach to ArcCorp."},
    {"id": "mic-r1", "name": "R&R MIC-L1", "system": "stanton", "type": "rest_stop", "map_x": -8, "map_y": -72, "distance_from_star": 38.1, "description": "Rest stop on approach to microTech."},
    # Outposts & Mining Locations
    {"id": "kudre-ore", "name": "Kudre Ore", "system": "stanton", "type": "outpost", "map_x": -97, "map_y": 48, "distance_from_star": 12.7, "parent": "arial", "description": "Mining outpost on Arial."},
    {"id": "lathan", "name": "HDMS-Lathan", "system": "stanton", "type": "outpost", "map_x": -92, "map_y": 83, "distance_from_star": 13.2, "parent": "aberdeen", "description": "Hurston Dynamics facility on Aberdeen."},
    {"id": "shubin-sal5", "name": "Shubin Mining SAL-5", "system": "stanton", "type": "outpost", "map_x": 28, "map_y": 118, "distance_from_star": 20.6, "parent": "cellin", "description": "Shubin Mining facility on Cellin."},
    {"id": "bountiful-harvest", "name": "Bountiful Harvest", "system": "stanton", "type": "outpost", "map_x": 58, "map_y": 123, "distance_from_star": 21.4, "parent": "daymar", "description": "Hydroponics farm on Daymar."},
    {"id": "benson-mining", "name": "Benson Mining", "system": "stanton", "type": "outpost", "map_x": 63, "map_y": 93, "distance_from_star": 21.1, "parent": "yela", "description": "Mining outpost on Yela."},
    {"id": "humboldt-mines", "name": "Humboldt Mines", "system": "stanton", "type": "outpost", "map_x": 118, "map_y": -12, "distance_from_star": 29.6, "parent": "lyria", "description": "Mining facility on Lyria."},
    {"id": "samson-salvage", "name": "Samson & Sons Salvage", "system": "stanton", "type": "outpost", "map_x": 123, "map_y": -42, "distance_from_star": 30.6, "parent": "wala", "description": "Salvage yard on Wala."},
    {"id": "rayari-deltana", "name": "Rayari Deltana Research", "system": "stanton", "type": "outpost", "map_x": -12, "map_y": -128, "distance_from_star": 45.1, "parent": "calliope", "description": "Research outpost on Calliope."},
    {"id": "rayari-kaltag", "name": "Rayari Kaltag Research", "system": "stanton", "type": "outpost", "map_x": -47, "map_y": -123, "distance_from_star": 45.6, "parent": "clio", "description": "Research outpost on Clio."},

    # === PYRO SYSTEM ===
    {"id": "pyro-star", "name": "Pyro (Star)", "system": "pyro", "type": "star", "map_x": 520, "map_y": -80, "distance_from_star": 0},
    {"id": "pyro-i", "name": "Pyro I", "system": "pyro", "type": "planet", "map_x": 490, "map_y": -60, "distance_from_star": 5.0, "description": "Scorched inner planet"},
    {"id": "pyro-ii", "name": "Pyro II", "system": "pyro", "type": "planet", "map_x": 555, "map_y": -55, "distance_from_star": 12.0, "description": "Rocky desert world"},
    {"id": "pyro-iii", "name": "Pyro III (Bloom)", "system": "pyro", "type": "planet", "map_x": 570, "map_y": -100, "distance_from_star": 20.0, "description": "Habitable world with flora. Key destination."},
    {"id": "pyro-iv", "name": "Pyro IV", "system": "pyro", "type": "planet", "map_x": 500, "map_y": -130, "distance_from_star": 28.0, "description": "Ice giant"},
    {"id": "pyro-v", "name": "Pyro V", "system": "pyro", "type": "planet", "map_x": 465, "map_y": -110, "distance_from_star": 35.0, "description": "Gas giant"},
    {"id": "pyro-vi", "name": "Pyro VI", "system": "pyro", "type": "planet", "map_x": 540, "map_y": -145, "distance_from_star": 42.0, "description": "Frozen outer planet"},
    # Pyro Stations
    {"id": "ruin-station", "name": "Ruin Station", "system": "pyro", "type": "station", "map_x": 530, "map_y": -60, "distance_from_star": 8.0, "description": "Pirate hub in Pyro"},
    {"id": "checkmate-station", "name": "Checkmate Station", "system": "pyro", "type": "station", "map_x": 550, "map_y": -120, "distance_from_star": 25.0, "description": "Outlaw trading post"},
    # Pyro Gateway
    {"id": "pyro-stanton-gw", "name": "Pyro-Stanton Gateway", "system": "pyro", "type": "gateway", "map_x": 390, "map_y": -60, "distance_from_star": 50.0, "description": "Jump point back to Stanton"},
    {"id": "pyro-nyx-gw", "name": "Pyro-Nyx Gateway", "system": "pyro", "type": "gateway", "map_x": 450, "map_y": -160, "distance_from_star": 55.0, "description": "Jump point to Nyx system"},
    # Pyro Outposts & Settlements
    {"id": "pyro-bloom-settlement", "name": "Bloom Settlement", "system": "pyro", "type": "outpost", "map_x": 573, "map_y": -97, "distance_from_star": 20.1, "parent": "pyro-iii", "description": "Frontier settlement on Pyro III (Bloom). Only habitable zone in Pyro."},

    # === NYX SYSTEM ===
    {"id": "nyx-star", "name": "Nyx (Star)", "system": "nyx", "type": "star", "map_x": -420, "map_y": -160, "distance_from_star": 0},
    {"id": "delamar", "name": "Delamar", "system": "nyx", "type": "planet", "map_x": -380, "map_y": -140, "distance_from_star": 15.0, "landing_zone": "Levski", "description": "Protoplanet. Home to the People's Alliance."},
    {"id": "nyx-i", "name": "Nyx I", "system": "nyx", "type": "planet", "map_x": -450, "map_y": -145, "distance_from_star": 8.0, "description": "Barren inner world"},
    {"id": "nyx-ii", "name": "Nyx II", "system": "nyx", "type": "planet", "map_x": -440, "map_y": -190, "distance_from_star": 22.0, "description": "Frozen outer planet"},
    {"id": "nyx-iii", "name": "Nyx III", "system": "nyx", "type": "planet", "map_x": -395, "map_y": -200, "distance_from_star": 30.0, "description": "Gas giant"},
    # Nyx Stations
    {"id": "levski", "name": "Levski Station", "system": "nyx", "type": "station", "map_x": -375, "map_y": -150, "distance_from_star": 15.5, "description": "Underground settlement on Delamar"},
    # Nyx Cities
    {"id": "levski-city", "name": "Levski", "system": "nyx", "type": "city", "map_x": -378, "map_y": -143, "distance_from_star": 15.0, "parent": "delamar", "description": "Underground city on Delamar. People's Alliance capital. Black market hub."},
    # Nyx Gateways
    {"id": "nyx-stanton-gw", "name": "Nyx-Stanton Gateway", "system": "nyx", "type": "gateway", "map_x": -300, "map_y": -120, "distance_from_star": 48.0, "description": "Jump point back to Stanton"},
    {"id": "nyx-pyro-gw", "name": "Nyx-Pyro Gateway", "system": "nyx", "type": "gateway", "map_x": -350, "map_y": -195, "distance_from_star": 45.0, "description": "Jump point to Pyro system"},
]

# Jump point connections (bidirectional)
JUMP_CONNECTIONS = [
    ("stanton-pyro-gw", "pyro-stanton-gw", 100.0),   # 100 Mkm jump tunnel
    ("stanton-nyx-gw", "nyx-stanton-gw", 90.0),
    ("pyro-nyx-gw", "nyx-pyro-gw", 80.0),
]

_loc_by_id = {loc["id"]: loc for loc in LOCATIONS}


def get_all_locations():
    return LOCATIONS


def get_systems():
    return SYSTEMS


def get_locations_by_system(system_id):
    return [loc for loc in LOCATIONS if loc["system"] == system_id]


def _distance_mkm(loc_a, loc_b):
    """Calculate distance between two locations in millions of km."""
    if loc_a["system"] == loc_b["system"]:
        # Same system: use distance_from_star difference as approximation
        d_a = loc_a.get("distance_from_star", 0)
        d_b = loc_b.get("distance_from_star", 0)
        # Use 2D map distance as a proxy for relative positioning
        dx = loc_a["map_x"] - loc_b["map_x"]
        dy = loc_a["map_y"] - loc_b["map_y"]
        map_dist = math.sqrt(dx * dx + dy * dy)
        # Scale: map units roughly correspond to Mkm
        return max(abs(d_a - d_b), map_dist * 0.3)
    else:
        # Cross-system: need to go through jump points
        return None  # handled by route builder


def _find_jump_route(origin_sys, dest_sys):
    """Find jump point path between two systems."""
    # Direct connections
    for gw_a, gw_b, dist in JUMP_CONNECTIONS:
        loc_a = _loc_by_id[gw_a]
        loc_b = _loc_by_id[gw_b]
        if loc_a["system"] == origin_sys and loc_b["system"] == dest_sys:
            return [(gw_a, gw_b, dist)]
        if loc_a["system"] == dest_sys and loc_b["system"] == origin_sys:
            return [(gw_b, gw_a, dist)]
    # Two-hop: origin -> intermediate -> dest
    for gw_a1, gw_b1, d1 in JUMP_CONNECTIONS:
        la1, lb1 = _loc_by_id[gw_a1], _loc_by_id[gw_b1]
        mid_sys_a = la1["system"] if la1["system"] != origin_sys else lb1["system"]
        mid_sys_b = lb1["system"] if lb1["system"] != origin_sys else la1["system"]
        for mid_sys in [mid_sys_a, mid_sys_b]:
            for gw_a2, gw_b2, d2 in JUMP_CONNECTIONS:
                la2, lb2 = _loc_by_id[gw_a2], _loc_by_id[gw_b2]
                if (la2["system"] == mid_sys and lb2["system"] == dest_sys):
                    # Build path: origin_gw -> mid_gw (jump1) -> mid_other_gw -> dest_gw (jump2)
                    if la1["system"] == origin_sys:
                        return [(gw_a1, gw_b1, d1), (gw_a2, gw_b2, d2)]
                    else:
                        return [(gw_b1, gw_a1, d1), (gw_a2, gw_b2, d2)]
                if (lb2["system"] == mid_sys and la2["system"] == dest_sys):
                    if la1["system"] == origin_sys:
                        return [(gw_a1, gw_b1, d1), (gw_b2, gw_a2, d2)]
                    else:
                        return [(gw_b1, gw_a1, d1), (gw_b2, gw_a2, d2)]
    return []


def _get_rest_stops(system_id):
    """Get all rest stops in a given system, sorted by distance from star."""
    stops = [loc for loc in LOCATIONS if loc["system"] == system_id and loc["type"] == "rest_stop"]
    return sorted(stops, key=lambda l: l.get("distance_from_star", 0))


def _find_nearest_rest_stop(current_loc, target_loc, system_id):
    """Find the rest stop closest to the path between current and target within the same system."""
    stops = _get_rest_stops(system_id)
    if not stops:
        return None
    best = None
    best_score = float("inf")
    cx, cy = current_loc["map_x"], current_loc["map_y"]
    tx, ty = target_loc["map_x"], target_loc["map_y"]
    for stop in stops:
        if stop["id"] == current_loc.get("id"):
            continue
        sx, sy = stop["map_x"], stop["map_y"]
        dist_from_cur = math.sqrt((sx - cx) ** 2 + (sy - cy) ** 2) * 0.3
        dist_to_target = math.sqrt((sx - tx) ** 2 + (sy - ty) ** 2) * 0.3
        score = dist_from_cur + dist_to_target
        if dist_from_cur > 0.5 and score < best_score:
            best_score = score
            best = stop
    return best


def calculate_route(origin_id, destination_id, qd_size=1, qd_speed_override=0, qd_range_mkm=0):
    """Calculate a quantum travel route between two locations with fuel tracking."""
    origin = _loc_by_id.get(origin_id)
    dest = _loc_by_id.get(destination_id)
    if not origin or not dest:
        return {"error": "Location not found"}
    if origin_id == destination_id:
        return {"error": "Origin and destination are the same"}

    speed_kms = qd_speed_override if qd_speed_override > 0 else QD_SPEEDS.get(qd_size, QD_SPEEDS.get(1, 165000))
    max_range = qd_range_mkm if qd_range_mkm > 0 else QD_FUEL_DEFAULTS.get(qd_size, {}).get("range_mkm", 180)

    raw_waypoints = []

    if origin["system"] == dest["system"]:
        dist = _distance_mkm(origin, dest)
        raw_waypoints.append({
            "from_loc": origin, "to_loc": dest,
            "distance_mkm": dist, "type": "quantum",
        })
    else:
        jumps = _find_jump_route(origin["system"], dest["system"])
        if not jumps:
            return {"error": f"No jump route from {origin['system']} to {dest['system']}"}
        prev_loc = origin
        for gw_origin_id, gw_dest_id, jump_dist in jumps:
            gw_origin = _loc_by_id[gw_origin_id]
            gw_dest = _loc_by_id[gw_dest_id]
            leg_dist = _distance_mkm(prev_loc, gw_origin) or 20.0
            raw_waypoints.append({
                "from_loc": prev_loc, "to_loc": gw_origin,
                "distance_mkm": leg_dist, "type": "quantum",
            })
            raw_waypoints.append({
                "from_loc": gw_origin, "to_loc": gw_dest,
                "distance_mkm": jump_dist, "type": "jump",
            })
            prev_loc = gw_dest
        final_dist = _distance_mkm(prev_loc, dest) or 20.0
        raw_waypoints.append({
            "from_loc": prev_loc, "to_loc": dest,
            "distance_mkm": final_dist, "type": "quantum",
        })

    # Process fuel stops
    waypoints = []
    fuel_remaining = max_range
    fuel_stops = 0
    total_distance_mkm = 0

    for wp in raw_waypoints:
        dist = wp["distance_mkm"]
        if wp["type"] == "jump":
            # Jumps don't consume quantum fuel
            waypoints.append({
                "from": wp["from_loc"]["name"], "from_id": wp["from_loc"]["id"],
                "to": wp["to_loc"]["name"], "to_id": wp["to_loc"]["id"],
                "distance_mkm": round(dist, 2), "type": "jump",
                "fuel_used_pct": 0, "fuel_remaining_pct": round((fuel_remaining / max_range) * 100) if max_range > 0 else 100,
            })
            total_distance_mkm += dist
            continue

        # Quantum leg — check if we need a fuel stop
        if max_range > 0 and dist > fuel_remaining:
            # Need a fuel stop before this leg
            rest_stop = _find_nearest_rest_stop(wp["from_loc"], wp["to_loc"], wp["from_loc"]["system"])
            if rest_stop and rest_stop["id"] != wp["from_loc"]["id"] and rest_stop["id"] != wp["to_loc"]["id"]:
                # Leg to rest stop
                d_to_stop = _distance_mkm(wp["from_loc"], rest_stop) or 5.0
                fuel_used_pct_1 = round((d_to_stop / max_range) * 100) if max_range > 0 else 0
                fuel_remaining = max(0, fuel_remaining - d_to_stop)
                waypoints.append({
                    "from": wp["from_loc"]["name"], "from_id": wp["from_loc"]["id"],
                    "to": rest_stop["name"], "to_id": rest_stop["id"],
                    "distance_mkm": round(d_to_stop, 2), "type": "quantum",
                    "fuel_used_pct": fuel_used_pct_1,
                    "fuel_remaining_pct": round((fuel_remaining / max_range) * 100) if max_range > 0 else 100,
                })
                total_distance_mkm += d_to_stop
                # Refuel
                waypoints.append({
                    "from": rest_stop["name"], "from_id": rest_stop["id"],
                    "to": rest_stop["name"], "to_id": rest_stop["id"],
                    "distance_mkm": 0, "type": "refuel",
                    "fuel_used_pct": 0, "fuel_remaining_pct": 100,
                })
                fuel_remaining = max_range
                fuel_stops += 1
                # Continue from rest stop to original destination
                d_from_stop = _distance_mkm(rest_stop, wp["to_loc"]) or 5.0
                fuel_used_pct_2 = round((d_from_stop / max_range) * 100) if max_range > 0 else 0
                fuel_remaining = max(0, fuel_remaining - d_from_stop)
                waypoints.append({
                    "from": rest_stop["name"], "from_id": rest_stop["id"],
                    "to": wp["to_loc"]["name"], "to_id": wp["to_loc"]["id"],
                    "distance_mkm": round(d_from_stop, 2), "type": "quantum",
                    "fuel_used_pct": fuel_used_pct_2,
                    "fuel_remaining_pct": round((fuel_remaining / max_range) * 100) if max_range > 0 else 100,
                })
                total_distance_mkm += d_from_stop
                continue

        # Normal quantum leg
        fuel_used_pct = round((dist / max_range) * 100) if max_range > 0 else 0
        fuel_remaining = max(0, fuel_remaining - dist)
        waypoints.append({
            "from": wp["from_loc"]["name"], "from_id": wp["from_loc"]["id"],
            "to": wp["to_loc"]["name"], "to_id": wp["to_loc"]["id"],
            "distance_mkm": round(dist, 2), "type": wp["type"],
            "fuel_used_pct": fuel_used_pct,
            "fuel_remaining_pct": round((fuel_remaining / max_range) * 100) if max_range > 0 else 100,
        })
        total_distance_mkm += dist

    # Calculate travel time (only for quantum legs)
    quantum_distance_km = sum(w["distance_mkm"] for w in waypoints if w["type"] == "quantum") * 1_000_000
    travel_time_s = quantum_distance_km / speed_kms if speed_kms > 0 else 0
    spool_time = sum(1 for w in waypoints if w["type"] in ("quantum", "jump")) * 8
    refuel_time = fuel_stops * 45  # ~45s per refuel stop

    return {
        "origin": {"id": origin_id, "name": origin["name"], "system": origin["system"]},
        "destination": {"id": destination_id, "name": dest["name"], "system": dest["system"]},
        "qd_size": qd_size,
        "qd_speed_kms": speed_kms,
        "qd_range_mkm": round(max_range, 1),
        "total_distance_mkm": round(total_distance_mkm, 2),
        "total_distance_km": int(total_distance_mkm * 1_000_000),
        "travel_time_seconds": round(travel_time_s + spool_time + refuel_time),
        "spool_time_seconds": spool_time,
        "refuel_time_seconds": refuel_time,
        "fuel_stops": fuel_stops,
        "fuel_remaining_pct": round((fuel_remaining / max_range) * 100) if max_range > 0 else 100,
        "waypoints": waypoints,
        "cross_system": origin["system"] != dest["system"],
    }


# Default QED Snare range in map units (visual radius on the 2D map)
DEFAULT_SNARE_RANGE_MAP = 25  # covers ~7.5 Mkm at our scale


def _point_to_line_distance(px, py, ax, ay, bx, by):
    """Distance from point (px,py) to the line segment (ax,ay)-(bx,by)."""
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.sqrt((px - ax) ** 2 + (py - ay) ** 2)
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    proj_x = ax + t * dx
    proj_y = ay + t * dy
    return math.sqrt((px - proj_x) ** 2 + (py - proj_y) ** 2)


def _nearby_pois(px, py, radius_map, exclude_ids=None):
    """Find notable locations near a map point."""
    pois = []
    exclude = set(exclude_ids or [])
    for loc in LOCATIONS:
        if loc["id"] in exclude:
            continue
        dist = math.sqrt((loc["map_x"] - px) ** 2 + (loc["map_y"] - py) ** 2)
        if dist <= radius_map:
            pois.append({
                "id": loc["id"],
                "name": loc["name"],
                "type": loc["type"],
                "system": loc["system"],
                "distance_map": round(dist, 2),
                "distance_mkm": round(dist * 0.3, 2),
            })
    pois.sort(key=lambda p: p["distance_map"])
    return pois


def _find_second_snare(route_lines, first_pos, first_range, snare_range_map, dest):
    """Find optimal position for a second snare to cover routes missed by the first."""
    uncovered = []
    for rl in route_lines:
        d = _point_to_line_distance(first_pos["x"], first_pos["y"],
                                    rl["start_x"], rl["start_y"], rl["end_x"], rl["end_y"])
        if d > first_range:
            uncovered.append(rl)
    if not uncovered:
        return None

    # Find best position for second snare along uncovered routes
    avg_sx = sum(r["start_x"] for r in uncovered) / len(uncovered)
    avg_sy = sum(r["start_y"] for r in uncovered) / len(uncovered)
    dx = dest["map_x"] - avg_sx
    dy = dest["map_y"] - avg_sy
    total_len = math.sqrt(dx * dx + dy * dy)
    if total_len == 0:
        return None

    best_pos = None
    best_cov = 0
    for i in range(200):
        t = i / 200.0
        px = avg_sx + dx * t
        py = avg_sy + dy * t
        covered = sum(1 for rl in uncovered
                      if _point_to_line_distance(px, py, rl["start_x"], rl["start_y"],
                                                 rl["end_x"], rl["end_y"]) <= snare_range_map)
        if covered > best_cov:
            best_cov = covered
            best_pos = {"x": round(px, 2), "y": round(py, 2)}

    if best_pos and best_cov > 0:
        return {"position": best_pos, "covers": best_cov, "total_uncovered": len(uncovered)}
    return None


def calculate_interdiction(origin_ids, destination_id, snare_range_mkm=7.5, your_qd_size=1, target_qd_size=1):
    """Calculate optimal QED snare position with full tactical analysis."""
    dest = _loc_by_id.get(destination_id)
    if not dest:
        return {"error": "Destination not found"}

    origins = []
    for oid in origin_ids:
        loc = _loc_by_id.get(oid)
        if loc:
            origins.append(loc)
    if not origins:
        return {"error": "No valid origins"}

    your_speed = QD_SPEEDS.get(your_qd_size, QD_SPEEDS[1])
    target_speed = QD_SPEEDS.get(target_qd_size, QD_SPEEDS[1])

    # Build route lines from each origin to destination
    route_lines = []
    for orig in origins:
        if orig["system"] == dest["system"]:
            route_lines.append({
                "origin": orig,
                "start_x": orig["map_x"], "start_y": orig["map_y"],
                "end_x": dest["map_x"], "end_y": dest["map_y"],
            })
        else:
            jumps = _find_jump_route(orig["system"], dest["system"])
            if jumps:
                last_gw_id = jumps[-1][1]
                gw = _loc_by_id[last_gw_id]
                route_lines.append({
                    "origin": orig,
                    "start_x": gw["map_x"], "start_y": gw["map_y"],
                    "end_x": dest["map_x"], "end_y": dest["map_y"],
                })

    if not route_lines:
        return {"error": "No valid routes to destination"}

    snare_range_map = snare_range_mkm / 0.3

    # --- Find optimal primary snare ---
    best_pos = None
    best_dist_to_dest = float('inf')
    avg_sx = sum(r["start_x"] for r in route_lines) / len(route_lines)
    avg_sy = sum(r["start_y"] for r in route_lines) / len(route_lines)
    dx = dest["map_x"] - avg_sx
    dy = dest["map_y"] - avg_sy
    total_len = math.sqrt(dx * dx + dy * dy)
    if total_len == 0:
        return {"error": "Origins and destination overlap"}

    for i in range(200):
        t = i / 200.0
        px = avg_sx + dx * t
        py = avg_sy + dy * t
        max_dist = 0
        for rl in route_lines:
            d = _point_to_line_distance(px, py, rl["start_x"], rl["start_y"], rl["end_x"], rl["end_y"])
            max_dist = max(max_dist, d)
        if max_dist <= snare_range_map:
            dist_to_dest = math.sqrt((px - dest["map_x"]) ** 2 + (py - dest["map_y"]) ** 2)
            if dist_to_dest < best_dist_to_dest:
                best_dist_to_dest = dist_to_dest
                best_pos = {"x": round(px, 2), "y": round(py, 2), "max_route_dist": round(max_dist, 2)}

    # Fallback if no full coverage
    if not best_pos:
        px = avg_sx + dx * 0.7
        py = avg_sy + dy * 0.7
        best_pos = {"x": round(px, 2), "y": round(py, 2), "max_route_dist": 0}
        best_dist_to_dest = math.sqrt((px - dest["map_x"]) ** 2 + (py - dest["map_y"]) ** 2)

    # --- Per-route analysis ---
    route_details = []
    covered_count = 0
    for rl in route_lines:
        orig = rl["origin"]
        d_to_snare = _point_to_line_distance(best_pos["x"], best_pos["y"],
                                             rl["start_x"], rl["start_y"], rl["end_x"], rl["end_y"])
        is_covered = d_to_snare <= snare_range_map
        if is_covered:
            covered_count += 1

        # Route distance (map units -> Mkm)
        route_dist_map = math.sqrt((rl["end_x"] - rl["start_x"]) ** 2 + (rl["end_y"] - rl["start_y"]) ** 2)
        route_dist_mkm = round(route_dist_map * 0.3, 2)

        # Time for target to travel this route
        route_dist_km = route_dist_mkm * 1_000_000
        target_travel_time = round(route_dist_km / target_speed) if target_speed > 0 else 0

        # Time for target to reach snare zone (fraction along route * total time)
        # Find the closest point on the route to the snare
        sdx, sdy = rl["end_x"] - rl["start_x"], rl["end_y"] - rl["start_y"]
        seg_len_sq = sdx * sdx + sdy * sdy
        if seg_len_sq > 0:
            t_proj = max(0, min(1, ((best_pos["x"] - rl["start_x"]) * sdx + (best_pos["y"] - rl["start_y"]) * sdy) / seg_len_sq))
        else:
            t_proj = 0
        time_to_snare = round(target_travel_time * t_proj)

        route_details.append({
            "origin_id": orig["id"],
            "origin_name": orig["name"],
            "origin_system": orig["system"],
            "distance_mkm": route_dist_mkm,
            "target_travel_time_s": target_travel_time,
            "time_to_snare_s": time_to_snare,
            "covered": is_covered,
            "deviation_mkm": round(d_to_snare * 0.3, 2),
        })

    coverage_pct = round((covered_count / len(route_lines)) * 100) if route_lines else 0

    # --- Timing windows ---
    arrival_times = sorted([r["time_to_snare_s"] for r in route_details if r["covered"]])
    if len(arrival_times) >= 2:
        timing_window = arrival_times[-1] - arrival_times[0]
        timing_note = f"Targets arrive over a {round(timing_window)}s window ({round(timing_window/60,1)} min)"
    elif len(arrival_times) == 1:
        timing_note = f"Single route — target reaches snare zone in ~{arrival_times[0]}s"
    else:
        timing_note = "No covered routes"
        timing_window = 0

    # --- Escape analysis ---
    can_escape = target_speed >= your_speed
    speed_diff = your_speed - target_speed
    if can_escape:
        escape_note = "Target QD is equal or faster — they may escape if interdiction fails. Consider EMP or disabling their QD."
    else:
        escape_note = f"Your QD is {speed_diff:,} km/s faster. You can pursue if they run."

    # --- Nearby POI warnings ---
    pois = _nearby_pois(best_pos["x"], best_pos["y"], snare_range_map * 1.5,
                        exclude_ids=[destination_id] + origin_ids)
    comm_arrays = [p for p in pois if 'comm' in p["name"].lower() or 'relay' in p["name"].lower()]
    stations_nearby = [p for p in pois if p["type"] in ("station", "rest_stop")]

    # --- Tactical notes ---
    tactics = []
    if comm_arrays:
        tactics.append(f"COMM ARRAY nearby ({comm_arrays[0]['name']}, {comm_arrays[0]['distance_mkm']} Mkm) — disable it first to avoid crime stat.")
    if stations_nearby:
        tactics.append(f"Station nearby ({stations_nearby[0]['name']}, {stations_nearby[0]['distance_mkm']} Mkm) — target may attempt to dock for safety.")
    if coverage_pct < 100:
        uncov = [r for r in route_details if not r["covered"]]
        tactics.append(f"{len(uncov)} route(s) not covered. Consider adding a second snare or repositioning.")
    if len(route_details) == 1:
        tactics.append("Single approach vector — guaranteed intercept if snare is active.")
    elif len(route_details) >= 4:
        tactics.append("Many approach vectors — a wing of snare ships improves coverage.")
    snare_dist_mkm = round(best_dist_to_dest * 0.3, 2)
    if snare_dist_mkm < 3:
        tactics.append("Snare very close to destination — target may reach safety quickly after interdiction.")
    if not tactics:
        tactics.append("Clean intercept zone with good coverage. Deploy snare and wait.")

    # --- Multi-snare suggestion ---
    second_snare = None
    if coverage_pct < 100:
        second_snare = _find_second_snare(route_lines, best_pos, snare_range_map, snare_range_map, dest)

    msg = f"Optimal interdiction position found! {covered_count}/{len(route_lines)} routes covered." if coverage_pct == 100 else f"Best position covers {covered_count}/{len(route_lines)} routes ({coverage_pct}%)."

    return {
        "success": coverage_pct == 100,
        "message": msg,
        "snare_position": best_pos,
        "snare_range_map": round(snare_range_map, 2),
        "snare_range_mkm": snare_range_mkm,
        "distance_to_dest_mkm": snare_dist_mkm,
        "coverage_pct": coverage_pct,
        "routes_covered": covered_count,
        "routes_total": len(route_lines),
        "route_lines": [{"from": r["origin"]["name"], "from_id": r["origin"]["id"],
                         "sx": r["start_x"], "sy": r["start_y"],
                         "ex": r["end_x"], "ey": r["end_y"]} for r in route_lines],
        "route_details": route_details,
        "destination": {"id": destination_id, "name": dest["name"]},
        "timing": {
            "arrival_times": arrival_times,
            "window_seconds": round(timing_window) if len(arrival_times) >= 2 else 0,
            "note": timing_note,
        },
        "escape_analysis": {
            "can_escape": can_escape,
            "your_speed_kms": your_speed,
            "target_speed_kms": target_speed,
            "speed_diff_kms": speed_diff,
            "note": escape_note,
        },
        "nearby_pois": pois[:6],
        "tactical_notes": tactics,
        "second_snare": second_snare,
    }


def calculate_chase(your_qd_size, target_qd_size, distance_mkm, prep_time_seconds=30):
    """Simple chase calculator (legacy). Used as fallback."""
    your_speed = QD_SPEEDS.get(your_qd_size, QD_SPEEDS[1])
    target_speed = QD_SPEEDS.get(target_qd_size, QD_SPEEDS[1])
    distance_km = distance_mkm * 1_000_000

    if your_speed > target_speed:
        closing_speed = your_speed - target_speed
        catch_time = distance_km / closing_speed
        total_time = catch_time + prep_time_seconds
        return {
            "can_catch": True, "your_speed_kms": your_speed, "target_speed_kms": target_speed,
            "speed_advantage_kms": your_speed - target_speed,
            "closing_time_seconds": round(catch_time), "total_time_seconds": round(total_time),
            "prep_time_seconds": prep_time_seconds, "distance_mkm": distance_mkm,
            "verdict": f"You can catch the target in ~{round(total_time)}s ({round(total_time/60, 1)} min). Your QD is {your_speed - target_speed:,} km/s faster.",
        }
    elif your_speed == target_speed:
        return {"can_catch": False, "your_speed_kms": your_speed, "target_speed_kms": target_speed,
                "speed_advantage_kms": 0, "verdict": "Same QD speed — you cannot close the gap. Consider upgrading your quantum drive."}
    else:
        return {"can_catch": False, "your_speed_kms": your_speed, "target_speed_kms": target_speed,
                "speed_advantage_kms": your_speed - target_speed,
                "verdict": f"Target's QD is {target_speed - your_speed:,} km/s faster. You cannot catch them in quantum. Use interdiction instead."}


def calculate_chase_advanced(your_position_id, target_position_id, your_qd_size=1, target_qd_size=1, prep_time_seconds=30):
    """Advanced pursuit planner: analyses every escape destination a target might flee to."""
    your_loc = _loc_by_id.get(your_position_id)
    target_loc = _loc_by_id.get(target_position_id)
    if not your_loc:
        return {"error": "Your position not found"}
    if not target_loc:
        return {"error": "Target position not found"}

    your_speed = QD_SPEEDS.get(your_qd_size, QD_SPEEDS[1])
    target_speed = QD_SPEEDS.get(target_qd_size, QD_SPEEDS[1])
    target_range_mkm = QD_FUEL_DEFAULTS.get(target_qd_size, {}).get("range_mkm", 180)

    # Distance between you and target
    sep_dist_map = math.sqrt((your_loc["map_x"] - target_loc["map_x"]) ** 2 +
                             (your_loc["map_y"] - target_loc["map_y"]) ** 2)
    sep_dist_mkm = round(sep_dist_map * 0.3, 2)

    # Find potential escape destinations for the target
    # (dockable locations: stations, rest_stops, cities, gateways — within their QD fuel range & same system or via gateway)
    escape_types = {"station", "rest_stop", "city", "gateway"}
    escape_destinations = []

    for loc in LOCATIONS:
        if loc["id"] == target_position_id or loc["id"] == your_position_id:
            continue
        if loc["type"] not in escape_types:
            continue

        # Calculate target's distance to this escape point
        target_dist = _distance_mkm(target_loc, loc)
        if target_dist is None:
            # Cross-system — only reachable via gateway, skip for simplicity
            continue
        if target_dist > target_range_mkm:
            continue  # Out of fuel range
        if target_dist < 0.5:
            continue  # Too close, effectively same location

        # Calculate your distance to intercept (head to same location)
        your_dist = _distance_mkm(your_loc, loc)
        if your_dist is None:
            continue

        target_travel_km = target_dist * 1_000_000
        your_travel_km = your_dist * 1_000_000

        target_time = round(target_travel_km / target_speed) if target_speed > 0 else 9999
        your_time = round(your_travel_km / your_speed + prep_time_seconds) if your_speed > 0 else 9999

        can_intercept = your_time <= target_time
        time_diff = target_time - your_time  # positive = you arrive first

        escape_destinations.append({
            "id": loc["id"],
            "name": loc["name"],
            "type": loc["type"],
            "system": loc["system"],
            "target_distance_mkm": round(target_dist, 2),
            "your_distance_mkm": round(your_dist, 2),
            "target_time_s": target_time,
            "your_time_s": your_time,
            "can_intercept": can_intercept,
            "time_margin_s": time_diff,
            "map_x": loc["map_x"],
            "map_y": loc["map_y"],
        })

    # Sort: interceptable first (by time margin desc), then non-interceptable (by time margin desc)
    escape_destinations.sort(key=lambda d: (-int(d["can_intercept"]), -d["time_margin_s"]))

    interceptable = [d for d in escape_destinations if d["can_intercept"]]
    escapable = [d for d in escape_destinations if not d["can_intercept"]]
    total = len(escape_destinations)
    intercept_pct = round((len(interceptable) / total) * 100) if total > 0 else 0

    # Pursuit recommendation
    if len(interceptable) == total and total > 0:
        recommendation = "Full pursuit advantage — you can reach every escape destination before the target."
        threat_level = "low"
    elif len(interceptable) > len(escapable):
        recommendation = f"You control {len(interceptable)}/{total} escape routes. Focus on blocking the {len(escapable)} uncovered destination(s)."
        threat_level = "medium"
    elif len(interceptable) > 0:
        recommendation = f"Target has {len(escapable)} escape options you can't reach in time. Consider interdiction instead of pursuit."
        threat_level = "high"
    else:
        recommendation = "Target can reach all safe havens before you. Deploy QED snare or disengage."
        threat_level = "critical"

    # Best pursuit destination: the one where you arrive earliest relative to target
    best_pursuit = interceptable[0] if interceptable else None

    # Tactical notes
    tactics = []
    if your_speed > target_speed:
        tactics.append(f"Speed advantage: {your_speed - target_speed:,} km/s faster. Direct pursuit viable in open space.")
    elif your_speed == target_speed:
        tactics.append("Matched QD speed — you can't close in open space. Cut them off at a destination.")
    else:
        tactics.append(f"Target is {target_speed - your_speed:,} km/s faster. Direct pursuit futile — focus on interception points.")

    if prep_time_seconds > 15:
        tactics.append(f"{prep_time_seconds}s prep delay costs you {round(your_speed * prep_time_seconds / 1_000_000, 1)} Mkm of ground.")

    gateways_escape = [d for d in escapable if d["type"] == "gateway"]
    if gateways_escape:
        tactics.append(f"Target can flee to {gateways_escape[0]['name']} — they may jump systems. Act fast.")

    stations_close = [d for d in escape_destinations if d["type"] in ("station", "rest_stop") and d["target_distance_mkm"] < 5]
    if stations_close:
        tactics.append(f"Target is close to {stations_close[0]['name']} ({stations_close[0]['target_distance_mkm']} Mkm). They may dock before you arrive.")

    if best_pursuit:
        tactics.append(f"Best intercept: head to {best_pursuit['name']} — you arrive {abs(best_pursuit['time_margin_s'])}s before the target.")

    if not tactics:
        tactics.append("Assess the situation — consider wing support or coordinated interdiction.")

    # Build chase lines for canvas visualization
    chase_lines = []
    for dest in escape_destinations[:12]:
        chase_lines.append({
            "target_x": target_loc["map_x"], "target_y": target_loc["map_y"],
            "dest_x": dest["map_x"], "dest_y": dest["map_y"],
            "your_x": your_loc["map_x"], "your_y": your_loc["map_y"],
            "can_intercept": dest["can_intercept"],
            "dest_name": dest["name"],
        })

    return {
        "your_position": {"id": your_position_id, "name": your_loc["name"], "system": your_loc["system"],
                          "map_x": your_loc["map_x"], "map_y": your_loc["map_y"]},
        "target_position": {"id": target_position_id, "name": target_loc["name"], "system": target_loc["system"],
                            "map_x": target_loc["map_x"], "map_y": target_loc["map_y"]},
        "separation_mkm": sep_dist_mkm,
        "your_speed_kms": your_speed,
        "target_speed_kms": target_speed,
        "speed_diff_kms": your_speed - target_speed,
        "prep_time_seconds": prep_time_seconds,
        "intercept_pct": intercept_pct,
        "interceptable_count": len(interceptable),
        "escapable_count": len(escapable),
        "total_destinations": total,
        "threat_level": threat_level,
        "recommendation": recommendation,
        "best_pursuit": best_pursuit,
        "escape_destinations": escape_destinations[:15],
        "tactical_notes": tactics,
        "chase_lines": chase_lines,
    }



# ── Shopping Trip Route Planner ──────────────────────────────────────────

# Mapping from common CStone store location substrings to our location IDs
_STORE_TO_LOCATION = {
    "area 18": "area18",
    "area18": "area18",
    "arccorp": "area18",
    "new babbage": "new-babbage",
    "new_babbage": "new-babbage",
    "microtech": "new-babbage",
    "lorville": "lorville",
    "hurston": "lorville",
    "orison": "orison",
    "crusader": "orison",
    "port olisar": "port-olisar",
    "grim hex": "grim-hex",
    "grimhex": "grim-hex",
    "everus harbor": "everus-harbor",
    "everus": "everus-harbor",
    "baijini point": "baijini-point",
    "baijini": "baijini-point",
    "port tressler": "port-tressler",
    "tressler": "port-tressler",
    "levski": "levski-city",
    "ruin station": "ruin-station",
    "bloom": "pyro-bloom-settlement",
    "ashland": "pyro-bloom-settlement",
    "ignis": "pyro-bloom-settlement",
    "pyro v": "pyro-v",
    "pyro": "ruin-station",
    "checkmate": "checkmate-station",
    "gaspar": "ruin-station",
    "stanton": "port-olisar",
}

# Build a reverse lookup of location names (lowercase) -> id
_loc_by_name_lower = {loc["name"].lower(): loc["id"] for loc in LOCATIONS}


def _resolve_store_to_location(store_name: str):
    """Map a CStone store name like 'Centermass @ Area 18' to a LOCATIONS entry."""
    name_lower = store_name.lower().strip()

    # Handle hierarchical CStone format: "Stanton > ArcCorp > Area 18 > TDD > shop_terminal"
    segments = [s.strip().lower() for s in name_lower.split(">") if s.strip()]

    # Try each segment individually (most specific first, reversed)
    for seg in reversed(segments):
        if seg in ("shop_terminal", "admin", "cargo"):
            continue  # skip generic segments
        if seg in _loc_by_name_lower:
            return _loc_by_id[_loc_by_name_lower[seg]]
        for keyword, loc_id in _STORE_TO_LOCATION.items():
            if keyword in seg or seg in keyword:
                loc = _loc_by_id.get(loc_id)
                if loc:
                    return loc
        for loc in LOCATIONS:
            if loc["name"].lower() in seg or seg in loc["name"].lower():
                return loc

    # Direct name match on full string
    if name_lower in _loc_by_name_lower:
        return _loc_by_id[_loc_by_name_lower[name_lower]]

    # Check our curated mapping (substring match on full string)
    for keyword, loc_id in _STORE_TO_LOCATION.items():
        if keyword in name_lower:
            return _loc_by_id.get(loc_id)

    # Fuzzy: check if any location name is contained in the full store name
    for loc in LOCATIONS:
        if loc["name"].lower() in name_lower:
            return loc

    # Reverse: check if the store name is contained in any location name
    for loc in LOCATIONS:
        if name_lower in loc["name"].lower():
            return loc

    return None


def get_starting_locations():
    """Return dockable locations suitable as starting points for a shopping trip."""
    dockable_types = {"city", "station", "rest_stop"}
    results = []
    for loc in LOCATIONS:
        if loc["type"] in dockable_types:
            results.append({
                "id": loc["id"],
                "name": loc["name"],
                "system": loc["system"],
                "type": loc["type"],
            })
    results.sort(key=lambda x: (x["system"], x["type"] != "city", x["name"]))
    return results


def plan_shopping_trip(store_names: list, qd_size: int = 1, origin_id: str = None):
    """
    Given a list of store names from CStone, resolve them to map locations
    and compute an efficient multi-stop route using nearest-neighbor heuristic.
    If origin_id is provided, use that location as the starting point.
    Returns ordered stops with coordinates, legs with distances and travel times.
    """
    speed_kms = QD_SPEEDS.get(qd_size, QD_SPEEDS.get(1, 165000))

    # Resolve origin if provided
    origin_loc = None
    if origin_id:
        origin_loc = _loc_by_id.get(origin_id)

    # Deduplicate and resolve stores to locations
    seen_ids = set()
    if origin_loc:
        seen_ids.add(origin_loc["id"])
    stops = []
    unresolved = []
    for store in store_names:
        loc = _resolve_store_to_location(store)
        if loc and loc["id"] not in seen_ids:
            seen_ids.add(loc["id"])
            stops.append({"store_name": store, "location": loc})
        elif loc and loc["id"] == (origin_loc["id"] if origin_loc else None):
            # Store resolves to the origin — still include it as a shopping stop
            stops.append({"store_name": store, "location": loc})
        elif not loc:
            unresolved.append(store)

    if len(stops) < 1:
        return {"error": "Could not resolve any store locations to the star map"}

    # If only 1 stop and no origin, simple result
    if len(stops) == 1 and not origin_loc:
        loc = stops[0]["location"]
        return {
            "stops": [{
                "order": 1,
                "store_name": stops[0]["store_name"],
                "location_name": loc["name"],
                "location_id": loc["id"],
                "system": loc["system"],
                "map_x": loc["map_x"],
                "map_y": loc["map_y"],
                "type": loc.get("type", ""),
                "is_origin": False,
            }],
            "legs": [],
            "total_distance_mkm": 0,
            "total_travel_time_s": 0,
            "qd_size": qd_size,
            "qd_speed_kms": speed_kms,
            "unresolved_stores": unresolved,
            "origin": None,
            "systems": SYSTEMS,
            "context_locations": _get_context_locations([s["location"] for s in stops]),
        }

    # Build the greedy nearest-neighbor route
    # If origin is provided, start from origin; otherwise start from first store
    if origin_loc:
        # Start routing from origin — find nearest store to origin first
        remaining = list(range(len(stops)))
        ordered = []
        current_loc = origin_loc
        while remaining:
            best_idx = None
            best_dist = float("inf")
            for idx in remaining:
                candidate = stops[idx]["location"]
                dist = _distance_mkm(current_loc, candidate)
                if dist is not None and dist < best_dist:
                    best_dist = dist
                    best_idx = idx
            if best_idx is not None:
                ordered.append(best_idx)
                remaining.remove(best_idx)
                current_loc = stops[best_idx]["location"]
            else:
                ordered.append(remaining.pop(0))
                current_loc = stops[ordered[-1]]["location"]
    else:
        remaining = list(range(len(stops)))
        ordered = [remaining.pop(0)]

    while remaining:
        current = stops[ordered[-1]]["location"]
        best_idx = None
        best_dist = float("inf")
        for idx in remaining:
            candidate = stops[idx]["location"]
            dist = _distance_mkm(current, candidate)
            if dist is not None and dist < best_dist:
                best_dist = dist
                best_idx = idx
        if best_idx is not None:
            ordered.append(best_idx)
            remaining.remove(best_idx)
        else:
            # Cross-system fallback: just append in order
            ordered.append(remaining.pop(0))

    # Build result
    ordered_stops = [stops[i] for i in ordered]
    result_stops = []
    legs = []
    total_dist = 0
    total_time = 0

    # If origin provided, add it as the starting point
    origin_result = None
    if origin_loc:
        origin_result = {
            "id": origin_loc["id"],
            "name": origin_loc["name"],
            "system": origin_loc["system"],
            "map_x": origin_loc["map_x"],
            "map_y": origin_loc["map_y"],
            "type": origin_loc.get("type", ""),
        }
        # Add leg from origin to first stop
        first_stop_loc = ordered_stops[0]["location"]
        dist = _distance_mkm(origin_loc, first_stop_loc)
        if dist is None:
            dist = 50.0
        travel_km = dist * 1_000_000
        travel_s = round(travel_km / speed_kms) if speed_kms > 0 else 0
        spool_s = 8
        legs.append({
            "from_name": origin_loc["name"],
            "from_id": origin_loc["id"],
            "from_x": origin_loc["map_x"],
            "from_y": origin_loc["map_y"],
            "to_name": first_stop_loc["name"],
            "to_id": first_stop_loc["id"],
            "to_x": first_stop_loc["map_x"],
            "to_y": first_stop_loc["map_y"],
            "distance_mkm": round(dist, 2),
            "travel_time_s": travel_s + spool_s,
        })
        total_dist += dist
        total_time += travel_s + spool_s

    for i, stop in enumerate(ordered_stops):
        loc = stop["location"]
        result_stops.append({
            "order": i + 1,
            "store_name": stop["store_name"],
            "location_name": loc["name"],
            "location_id": loc["id"],
            "system": loc["system"],
            "map_x": loc["map_x"],
            "map_y": loc["map_y"],
            "type": loc.get("type", ""),
            "is_origin": False,
        })

        if i > 0:
            prev_loc = ordered_stops[i - 1]["location"]
            dist = _distance_mkm(prev_loc, loc)
            if dist is None:
                dist = 50.0  # cross-system fallback estimate
            travel_km = dist * 1_000_000
            travel_s = round(travel_km / speed_kms) if speed_kms > 0 else 0
            spool_s = 8  # spool-up time per jump

            legs.append({
                "from_name": prev_loc["name"],
                "from_id": prev_loc["id"],
                "from_x": prev_loc["map_x"],
                "from_y": prev_loc["map_y"],
                "to_name": loc["name"],
                "to_id": loc["id"],
                "to_x": loc["map_x"],
                "to_y": loc["map_y"],
                "distance_mkm": round(dist, 2),
                "travel_time_s": travel_s + spool_s,
            })
            total_dist += dist
            total_time += travel_s + spool_s

    all_route_locs = [s["location"] for s in ordered_stops]
    if origin_loc:
        all_route_locs = [origin_loc] + all_route_locs

    return {
        "stops": result_stops,
        "legs": legs,
        "total_distance_mkm": round(total_dist, 2),
        "total_travel_time_s": round(total_time),
        "qd_size": qd_size,
        "qd_speed_kms": speed_kms,
        "unresolved_stores": unresolved,
        "origin": origin_result,
        "systems": SYSTEMS,
        "context_locations": _get_context_locations(all_route_locs),
    }


def _get_context_locations(route_locs):
    """Return nearby landmark locations (planets, cities) for map context."""
    # Collect systems involved
    systems = set(loc["system"] for loc in route_locs)
    context = []
    seen = set(loc["id"] for loc in route_locs)
    for loc in LOCATIONS:
        if loc["system"] in systems and loc["id"] not in seen:
            if loc["type"] in ("planet", "city", "star"):
                context.append({
                    "name": loc["name"],
                    "id": loc["id"],
                    "type": loc["type"],
                    "system": loc["system"],
                    "map_x": loc["map_x"],
                    "map_y": loc["map_y"],
                })
    return context
