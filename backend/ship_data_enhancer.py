"""Ship data enhancer - adds comprehensive details and images to ship data"""

# Actual working Star Citizen ship image URLs from community resources
SHIP_IMAGE_MAP = {
    # Origin Jumpworks
    "85x": "https://starcitizen.tools/images/thumb/3/3f/85X_-_Hangar.jpg/1200px-85X_-_Hangar.jpg",
    "100i": "https://starcitizen.tools/images/thumb/5/57/100i_in_space_-_Isometric.jpg/1200px-100i_in_space_-_Isometric.jpg",
    "125a": "https://starcitizen.tools/images/thumb/c/cb/125a_in_space_-_Isometric.jpg/1200px-125a_in_space_-_Isometric.jpg",
    "300i": "https://starcitizen.tools/images/thumb/f/f3/300i_in_space_-_Isometric.jpg/1200px-300i_in_space_-_Isometric.jpg",
    "315p": "https://starcitizen.tools/images/thumb/3/35/315p_in_space_-_Isometric.jpg/1200px-315p_in_space_-_Isometric.jpg",
    "325a": "https://starcitizen.tools/images/thumb/c/c4/325a_in_space_-_Isometric.jpg/1200px-325a_in_space_-_Isometric.jpg",
    "400i": "https://starcitizen.tools/images/thumb/8/8e/400i_in_space_-_Front.jpg/1200px-400i_in_space_-_Front.jpg",
    "600i": "https://starcitizen.tools/images/thumb/e/e4/600i_Explorer_in_space_-_Isometric.jpg/1200px-600i_Explorer_in_space_-_Isometric.jpg",
    "890jump": "https://starcitizen.tools/images/thumb/5/54/890_Jump_in_space_-_Isometric.jpg/1200px-890_Jump_in_space_-_Isometric.jpg",
    
    # Anvil Aerospace  
    "arrow": "https://starcitizen.tools/images/thumb/f/f4/Arrow_in_space_-_Isometric.jpg/1200px-Arrow_in_space_-_Isometric.jpg",
    "carrack": "https://starcitizen.tools/images/thumb/7/7f/Carrack_in_space_-_Isometric.jpg/1200px-Carrack_in_space_-_Isometric.jpg",
    "hornet-f7c": "https://starcitizen.tools/images/thumb/6/6d/Hornet_F7C_in_space_-_Isometric.jpg/1200px-Hornet_F7C_in_space_-_Isometric.jpg",
    "valkyrie": "https://starcitizen.tools/images/thumb/9/94/Valkyrie_in_space_-_Isometric.jpg/1200px-Valkyrie_in_space_-_Isometric.jpg",
    
    # RSI
    "constellation-andromeda": "https://starcitizen.tools/images/thumb/d/d5/Constellation_Andromeda_in_space_-_Isometric.jpg/1200px-Constellation_Andromeda_in_space_-_Isometric.jpg",
    "aurora-mr": "https://starcitizen.tools/images/thumb/a/a6/Aurora_MR_in_space_-_Isometric.jpg/1200px-Aurora_MR_in_space_-_Isometric.jpg",
    "mantis": "https://starcitizen.tools/images/thumb/e/ef/Mantis_in_space_-_Isometric.jpg/1200px-Mantis_in_space_-_Isometric.jpg",
    
    # Aegis Dynamics
    "avenger-titan": "https://starcitizen.tools/images/thumb/f/fc/Avenger_Titan_in_space_-_Isometric.jpg/1200px-Avenger_Titan_in_space_-_Isometric.jpg",
    "gladius": "https://starcitizen.tools/images/thumb/1/1c/Gladius_in_space_-_Isometric.jpg/1200px-Gladius_in_space_-_Isometric.jpg",
    "sabre": "https://starcitizen.tools/images/thumb/b/b9/Sabre_in_space_-_Isometric.jpg/1200px-Sabre_in_space_-_Isometric.jpg",
    "vanguard-warden": "https://starcitizen.tools/images/thumb/4/49/Vanguard_Warden_in_space_-_Isometric.jpg/1200px-Vanguard_Warden_in_space_-_Isometric.jpg",
    "hammerhead": "https://starcitizen.tools/images/thumb/b/bc/Hammerhead_in_space_-_Isometric.jpg/1200px-Hammerhead_in_space_-_Isometric.jpg",
    "reclaimer": "https://starcitizen.tools/images/thumb/c/cc/Reclaimer_in_space_-_Isometric.jpg/1200px-Reclaimer_in_space_-_Isometric.jpg",
    
    # Drake Interplanetary
    "cutlass-black": "https://starcitizen.tools/images/thumb/d/d2/Cutlass_Black_in_space_-_Isometric.jpg/1200px-Cutlass_Black_in_space_-_Isometric.jpg",
    "caterpillar": "https://starcitizen.tools/images/thumb/8/87/Caterpillar_in_space_-_Isometric.jpg/1200px-Caterpillar_in_space_-_Isometric.jpg",
    "corsair": "https://starcitizen.tools/images/thumb/1/18/Corsair_in_space_-_Isometric.jpg/1200px-Corsair_in_space_-_Isometric.jpg",
    
    # Crusader Industries
    "mercury": "https://starcitizen.tools/images/thumb/f/f2/Mercury_Star_Runner_in_space_-_Isometric.jpg/1200px-Mercury_Star_Runner_in_space_-_Isometric.jpg",
    "starlifter-c2": "https://starcitizen.tools/images/thumb/1/11/C2_Hercules_in_space_-_Isometric.jpg/1200px-C2_Hercules_in_space_-_Isometric.jpg",
    "starlifter-m2": "https://starcitizen.tools/images/thumb/a/a7/M2_Hercules_in_space_-_Isometric.jpg/1200px-M2_Hercules_in_space_-_Isometric.jpg",
    "ares-ion": "https://starcitizen.tools/images/thumb/5/5a/Ares_Ion_in_space_-_Isometric.jpg/1200px-Ares_Ion_in_space_-_Isometric.jpg",
    
    # MISC
    "prospector": "https://starcitizen.tools/images/thumb/3/3a/Prospector_in_space_-_Isometric.jpg/1200px-Prospector_in_space_-_Isometric.jpg",
    "freelancer": "https://starcitizen.tools/images/thumb/d/db/Freelancer_in_space_-_Isometric.jpg/1200px-Freelancer_in_space_-_Isometric.jpg",
    "starfarer": "https://starcitizen.tools/images/thumb/2/2d/Starfarer_in_space_-_Isometric.jpg/1200px-Starfarer_in_space_-_Isometric.jpg",
}

# Vehicle images
VEHICLE_IMAGE_MAP = {
    "cyclone": "https://starcitizen.tools/images/thumb/9/9b/Cyclone_in_Hurston.jpg/1200px-Cyclone_in_Hurston.jpg",
    "nox": "https://starcitizen.tools/images/thumb/4/43/Nox_Kue_-_Landed.jpg/1200px-Nox_Kue_-_Landed.jpg",
    "ursa": "https://starcitizen.tools/images/thumb/0/0f/Ursa_Rover_in_Hurston.jpg/1200px-Ursa_Rover_in_Hurston.jpg",
    "nova": "https://starcitizen.tools/images/thumb/8/8f/Nova_Tank.jpg/1200px-Nova_Tank.jpg",
}

def enhance_ship_data(ships):
    """Add comprehensive details to ship list"""
    for ship in ships:
        # Use mapped image if available, otherwise use placeholder
        ship_id_lower = ship['id'].lower()
        if ship_id_lower in SHIP_IMAGE_MAP:
            ship["image"] = SHIP_IMAGE_MAP[ship_id_lower]
        elif not ship.get('image'):
            # Use a nice space-themed placeholder
            ship["image"] = f"https://via.placeholder.com/800x450/0a0e27/00d4ff?text={ship['name'].replace(' ', '+')}"
        
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
    return f"https://via.placeholder.com/800x450/2d1f00/ffc107?text={vehicle_name.replace(' ', '+')}"
