"""Star Citizen system location data and route calculation for Stanton, Pyro, and Nyx."""

import math

# Quantum drive speeds by size (km/s) - averaged from game data
QD_SPEEDS = {
    0: 100_000,   # Snub / no QD
    1: 165_000,   # Small
    2: 190_000,   # Medium  
    3: 240_000,   # Large
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

    # === NYX SYSTEM ===
    {"id": "nyx-star", "name": "Nyx (Star)", "system": "nyx", "type": "star", "map_x": -420, "map_y": -160, "distance_from_star": 0},
    {"id": "delamar", "name": "Delamar", "system": "nyx", "type": "planet", "map_x": -380, "map_y": -140, "distance_from_star": 15.0, "landing_zone": "Levski", "description": "Protoplanet. Home to the People's Alliance."},
    {"id": "nyx-i", "name": "Nyx I", "system": "nyx", "type": "planet", "map_x": -450, "map_y": -145, "distance_from_star": 8.0, "description": "Barren inner world"},
    {"id": "nyx-ii", "name": "Nyx II", "system": "nyx", "type": "planet", "map_x": -440, "map_y": -190, "distance_from_star": 22.0, "description": "Frozen outer planet"},
    {"id": "nyx-iii", "name": "Nyx III", "system": "nyx", "type": "planet", "map_x": -395, "map_y": -200, "distance_from_star": 30.0, "description": "Gas giant"},
    # Nyx Stations
    {"id": "levski", "name": "Levski Station", "system": "nyx", "type": "station", "map_x": -375, "map_y": -150, "distance_from_star": 15.5, "description": "Underground settlement on Delamar"},
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


def calculate_route(origin_id, destination_id, qd_size=1):
    """Calculate a quantum travel route between two locations."""
    origin = _loc_by_id.get(origin_id)
    dest = _loc_by_id.get(destination_id)
    if not origin or not dest:
        return {"error": "Location not found"}
    if origin_id == destination_id:
        return {"error": "Origin and destination are the same"}

    speed_kms = QD_SPEEDS.get(qd_size, QD_SPEEDS[1])
    waypoints = []
    total_distance_mkm = 0

    if origin["system"] == dest["system"]:
        # Same system: direct route
        dist = _distance_mkm(origin, dest)
        total_distance_mkm = dist
        waypoints.append({
            "from": origin["name"],
            "from_id": origin_id,
            "to": dest["name"],
            "to_id": destination_id,
            "distance_mkm": round(dist, 2),
            "type": "quantum",
        })
    else:
        # Cross-system route
        jumps = _find_jump_route(origin["system"], dest["system"])
        if not jumps:
            return {"error": f"No jump route from {origin['system']} to {dest['system']}"}

        prev_loc = origin
        for gw_origin_id, gw_dest_id, jump_dist in jumps:
            gw_origin = _loc_by_id[gw_origin_id]
            gw_dest = _loc_by_id[gw_dest_id]

            # Quantum to gateway
            leg_dist = _distance_mkm(prev_loc, gw_origin) or 20.0
            total_distance_mkm += leg_dist
            waypoints.append({
                "from": prev_loc["name"],
                "from_id": prev_loc["id"],
                "to": gw_origin["name"],
                "to_id": gw_origin_id,
                "distance_mkm": round(leg_dist, 2),
                "type": "quantum",
            })
            # Jump tunnel
            total_distance_mkm += jump_dist
            waypoints.append({
                "from": gw_origin["name"],
                "from_id": gw_origin_id,
                "to": gw_dest["name"],
                "to_id": gw_dest_id,
                "distance_mkm": round(jump_dist, 2),
                "type": "jump",
            })
            prev_loc = gw_dest

        # Final leg: gateway exit to destination
        final_dist = _distance_mkm(prev_loc, dest) or 20.0
        total_distance_mkm += final_dist
        waypoints.append({
            "from": prev_loc["name"],
            "from_id": prev_loc["id"],
            "to": dest["name"],
            "to_id": destination_id,
            "distance_mkm": round(final_dist, 2),
            "type": "quantum",
        })

    # Calculate travel time
    total_distance_km = total_distance_mkm * 1_000_000
    travel_time_s = total_distance_km / speed_kms
    # Add spool/calibration overhead per leg
    spool_time = len(waypoints) * 8  # ~8s per quantum spool

    return {
        "origin": {"id": origin_id, "name": origin["name"], "system": origin["system"]},
        "destination": {"id": destination_id, "name": dest["name"], "system": dest["system"]},
        "qd_size": qd_size,
        "qd_speed_kms": speed_kms,
        "total_distance_mkm": round(total_distance_mkm, 2),
        "total_distance_km": int(total_distance_km),
        "travel_time_seconds": round(travel_time_s + spool_time),
        "spool_time_seconds": spool_time,
        "waypoints": waypoints,
        "cross_system": origin["system"] != dest["system"],
    }
