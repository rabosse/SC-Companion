"""Ship data enhancer - adds comprehensive details and images to ship data"""

def enhance_ship_data(ships):
    """Add comprehensive details to ship list"""
    # Ship images from various sources
    ship_images = {
        "default": "https://images.unsplash.com/photo-1761603059659-baf7d8124c6f?q=85",
        "fighter": "https://images.unsplash.com/photo-1725201545124-3ecd19db4bc7?q=85",
        "large": "https://images.unsplash.com/photo-1767469194952-6b6720d8108e?q=85",
        "capital": "https://images.unsplash.com/photo-1758685295938-e27200ff3f6c?q=85",
        "military": "https://images.unsplash.com/photo-1614121174144-bd53a169780e?q=85",
        "sleek": "https://images.unsplash.com/photo-1743267822072-efdabbacc8c6?q=85",
    }
    
    # Vehicle images
    vehicle_images = {
        "rover": "https://images.unsplash.com/photo-1590314831339-07e29f3c1c37?q=85",
        "vehicle": "https://images.unsplash.com/photo-1722231525969-666c3606f690?q=85",
        "heavy": "https://images.unsplash.com/photo-1745688810809-5040dc0cd002?q=85",
    }
    
    # Enhanced details for each ship
    for ship in ships:
        # Add image based on size/type
        if ship["size"] == "Capital":
            ship["image"] = ship_images["capital"]
        elif ship["size"] == "Large":
            ship["image"] = ship_images["large"]
        elif ship["size"] == "Small" or ship["size"] == "Medium":
            ship["image"] = ship_images["fighter"]
        else:
            ship["image"] = ship_images["default"]
            
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

def get_vehicle_image(vehicle_type):
    """Get appropriate vehicle image"""
    vehicle_images = {
        "Ground": "https://images.unsplash.com/photo-1590314831339-07e29f3c1c37?q=85",
        "Hover": "https://images.unsplash.com/photo-1722231525969-666c3606f690?q=85",
        "Heavy": "https://images.unsplash.com/photo-1745688810809-5040dc0cd002?q=85",
    }
    return vehicle_images.get(vehicle_type, vehicle_images["Ground"])
