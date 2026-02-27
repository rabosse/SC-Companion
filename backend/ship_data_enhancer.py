"""Ship data enhancer - adds comprehensive details and images to ship data"""

# AI-Generated and curated Star Citizen ship images
SHIP_IMAGE_MAP = {
    # Origin Jumpworks
    "600i": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/5bbbe7956c2ac57464046919d3ed747372521c64e822b5cc911ceeccea4cb1ca.png",
    "600i-touring": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/5bbbe7956c2ac57464046919d3ed747372521c64e822b5cc911ceeccea4cb1ca.png",
    
    # Anvil Aerospace  
    "carrack": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/f1aaf8aa99d6956abb695a14f50172146ebb74f71b832acfbbc3c6dcbe20e4a8.png",
    
    # Aegis Dynamics
    "avenger-titan": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/6107e05daecd3882d22fcef219b598a2a0590e3b4686573e4efddf1f854024d2.png",
    "avenger-stalker": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/6107e05daecd3882d22fcef219b598a2a0590e3b4686573e4efddf1f854024d2.png",
    "avenger-warlock": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/6107e05daecd3882d22fcef219b598a2a0590e3b4686573e4efddf1f854024d2.png",
    "hammerhead": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/2bb245c31dd3fbeb49b924641c1f604c7f57dd037fc5c1f512cbe23c07315fd2.png",
    
    # Drake Interplanetary
    "cutlass-black": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/7c451cab850615f6c5c3eb2ab27acc464b5f0f470dfe0545e6b1062463aff8ff.png",
    "cutlass-red": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/7c451cab850615f6c5c3eb2ab27acc464b5f0f470dfe0545e6b1062463aff8ff.png",
    "cutlass-blue": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/7c451cab850615f6c5c3eb2ab27acc464b5f0f470dfe0545e6b1062463aff8ff.png",
    
    # RSI
    "constellation-andromeda": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/74e27317f62928b99c97a22030c726a2c5ed6ae88bc346b40ae18ae1798d7e34.png",
    "constellation-aquila": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/74e27317f62928b99c97a22030c726a2c5ed6ae88bc346b40ae18ae1798d7e34.png",
    "constellation-taurus": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/74e27317f62928b99c97a22030c726a2c5ed6ae88bc346b40ae18ae1798d7e34.png",
    "constellation-phoenix": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/74e27317f62928b99c97a22030c726a2c5ed6ae88bc346b40ae18ae1798d7e34.png",
    
    # Crusader Industries
    "mercury": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/bb2b5e285ae70812df3c7e2ffab3eb0d155fd81cc04c90746166e27007fd6b9a.png",
    
    # MISC
    "freelancer": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/ca10111c0c8b590b1f32ba45597ea5c2ae09d14fcce68d2bb4b68c8180d5b4bc.png",
    "freelancer-dur": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/ca10111c0c8b590b1f32ba45597ea5c2ae09d14fcce68d2bb4b68c8180d5b4bc.png",
    "freelancer-max": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/ca10111c0c8b590b1f32ba45597ea5c2ae09d14fcce68d2bb4b68c8180d5b4bc.png",
    "freelancer-mis": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/ca10111c0c8b590b1f32ba45597ea5c2ae09d14fcce68d2bb4b68c8180d5b4bc.png",
}

# Generic ship images by size
GENERIC_SHIP_IMAGES = {
    "Small": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/6107e05daecd3882d22fcef219b598a2a0590e3b4686573e4efddf1f854024d2.png",
    "Medium": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/7c451cab850615f6c5c3eb2ab27acc464b5f0f470dfe0545e6b1062463aff8ff.png",
    "Large": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/f1aaf8aa99d6956abb695a14f50172146ebb74f71b832acfbbc3c6dcbe20e4a8.png",
    "Capital": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/2bb245c31dd3fbeb49b924641c1f604c7f57dd037fc5c1f512cbe23c07315fd2.png",
    "Snub": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/5bbbe7956c2ac57464046919d3ed747372521c64e822b5cc911ceeccea4cb1ca.png",
}

# Vehicle images
VEHICLE_IMAGE_MAP = {
    "cyclone": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/ca10111c0c8b590b1f32ba45597ea5c2ae09d14fcce68d2bb4b68c8180d5b4bc.png",
    "nox": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/6107e05daecd3882d22fcef219b598a2a0590e3b4686573e4efddf1f854024d2.png",
    "ursa": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/7c451cab850615f6c5c3eb2ab27acc464b5f0f470dfe0545e6b1062463aff8ff.png",
    "nova": "https://static.prod-images.emergentagent.com/jobs/e5d7fdda-bb6a-4127-85f4-64d7bd4ceb19/images/2bb245c31dd3fbeb49b924641c1f604c7f57dd037fc5c1f512cbe23c07315fd2.png",
}

def enhance_ship_data(ships):
    """Add comprehensive details to ship list"""
    for ship in ships:
        # Use mapped image if available
        ship_id_lower = ship['id'].lower()
        if ship_id_lower in SHIP_IMAGE_MAP:
            ship["image"] = SHIP_IMAGE_MAP[ship_id_lower]
        elif not ship.get('image'):
            # Use generic image based on ship size
            ship["image"] = GENERIC_SHIP_IMAGES.get(ship.get("size", "Medium"), GENERIC_SHIP_IMAGES["Medium"])
        
        # Add missing fields with defaults
        if "beam" not in ship:
            ship["beam"] = round(ship["length"] * 0.6, 1)
        if "height" not in ship:
            ship["height"] = round(ship["length"] * 0.3, 1)
        if "mass" not in ship:
            ship["mass"] = int(ship["length"] * 1000)
        if "max_speed" not in ship:
            ship["max_speed"] = 220 if ship["size"] == "Small" else (180 if ship["size"] == "Medium" else 150)
        if "role" not in ship:
            ship["role"] = "Multi-role"
        if "description" not in ship:
            ship["description"] = f"The {ship['name']} by {ship['manufacturer']} is a {ship['size'].lower()}-class vessel designed for versatility and performance."
        if "price" not in ship:
            price_map = {"Snub": 50000, "Small": 100000, "Medium": 500000, "Large": 2000000, "Capital": 10000000}
            ship["price"] = price_map.get(ship["size"], 100000)
        if "armor" not in ship:
            ship["armor"] = "Medium" if ship["size"] in ["Medium", "Large"] else "Light"
        if "manufacturer_code" not in ship:
            ship["manufacturer_code"] = ship["manufacturer"].split()[0][:3].upper()
            
    return ships

def get_vehicle_image(vehicle_name):
    """Get vehicle image"""
    vehicle_id = vehicle_name.lower().replace(' ', '-')
    if vehicle_id in VEHICLE_IMAGE_MAP:
        return VEHICLE_IMAGE_MAP[vehicle_id]
    # Use a generic vehicle image
    return GENERIC_SHIP_IMAGES["Small"]
