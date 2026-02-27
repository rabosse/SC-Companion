"""Ship data enhancer - adds comprehensive details and images to ship data"""

def enhance_ship_data(ships):
    """Add comprehensive details to ship list"""
    # Try to use API images first, fall back to constructed URLs
    for ship in ships:
        # If API doesn't provide image, construct Star Citizen wiki image URL
        if not ship.get('image') or ship['image'] == '':
            # Use Star Citizen wiki/RSI website image pattern
            ship_slug = ship['name'].lower().replace(' ', '-').replace("'", '')
            ship['image'] = f"https://starcitizen.tools/images/thumb/{ship_slug}.jpg/800px-{ship_slug}.jpg"
        
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
            # Estimate price based on size
            price_map = {"Snub": 50000, "Small": 100000, "Medium": 500000, "Large": 2000000, "Capital": 10000000}
            ship["price"] = price_map.get(ship["size"], 100000)
        if "armor" not in ship:
            ship["armor"] = "Medium" if ship["size"] in ["Medium", "Large"] else "Light"
        if "manufacturer_code" not in ship:
            ship["manufacturer_code"] = ship["manufacturer"].split()[0][:3].upper()
            
    return ships

def get_vehicle_image(vehicle_name):
    """Get vehicle image from Star Citizen resources"""
    # Use Star Citizen wiki image pattern for vehicles
    vehicle_slug = vehicle_name.lower().replace(' ', '-')
    return f"https://starcitizen.tools/images/thumb/{vehicle_slug}.jpg/800px-{vehicle_slug}.jpg"
