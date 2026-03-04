"""Personal gear data: FPS weapons and armor sets for Star Citizen."""

# FPS WEAPONS - base variants with their skin/color variants grouped
# Structure: base weapon -> list of variants
# Locations: where to buy or find

FPS_WEAPONS = [
    # === PISTOLS ===
    {"id": "arclight-pistol", "name": "Arclight Pistol", "type": "Pistol", "size": 1, "manufacturer": "Klaus & Werner",
     "damage": 18, "ammo": 30, "fire_rate": "Semi/Burst", "effective_range": "50m",
     "description": "Versatile laser pistol. 30-round battery, single/3-round burst. PvP favorite.",
     "price_auec": 4850,
     "locations": ["Live Fire Weapons (most stations)", "Looted from NPCs"],
     "variants": ["Arclight \"Boneyard\" Pistol", "Arclight \"Nightlife\" Pistol", "Arclight \"Solarflare\" Pistol"]},

    {"id": "lh86-pistol", "name": "LH86 Pistol", "type": "Pistol", "size": 1, "manufacturer": "Kastak Arms",
     "damage": 20, "ammo": 20, "fire_rate": "Full Auto", "effective_range": "30m",
     "description": "Fully automatic ballistic pistol. High rate of fire, good for close combat.",
     "price_auec": 5200,
     "locations": ["Live Fire Weapons (Lorville)", "Live Fire Weapons (ArcCorp)"],
     "variants": ["LH86 \"Blight\" Pistol", "LH86 \"Gunmetal\" Pistol"]},

    {"id": "yubarev-pistol", "name": "Yubarev Pistol", "type": "Pistol", "size": 1, "manufacturer": "Gemini",
     "damage": 22, "ammo": 12, "fire_rate": "Semi-Auto", "effective_range": "45m",
     "description": "High-damage semi-auto ballistic pistol. Reliable sidearm.",
     "price_auec": 4400,
     "locations": ["Live Fire Weapons (most stations)", "Looted from NPCs"],
     "variants": ["Yubarev \"Executive\" Pistol", "Yubarev \"Nightfire\" Pistol"]},

    {"id": "coda-pistol", "name": "Coda Pistol", "type": "Pistol", "size": 1, "manufacturer": "Behring",
     "damage": 30, "ammo": 8, "fire_rate": "Semi-Auto", "effective_range": "55m",
     "description": "Heavy-hitting ballistic pistol. Highest pistol damage per shot.",
     "price_auec": 5800,
     "locations": ["Live Fire Weapons (Port Tressler)", "Live Fire Weapons (Everus Harbor)"],
     "variants": ["Coda \"Dunestalker\" Pistol", "Coda \"Snowblind\" Pistol"]},

    {"id": "vault-pistol", "name": "Vault Pistol", "type": "Pistol", "size": 1, "manufacturer": "Verified Offworld Laser Technologies",
     "damage": 15, "ammo": 40, "fire_rate": "Full Auto (Wind-up)", "effective_range": "35m",
     "description": "Fully automatic laser pistol with wind-up fire rate. Unique mechanic.",
     "price_auec": 3900,
     "locations": ["Live Fire Weapons (CRU-L1)", "Looted from NPCs"],
     "variants": ["Vault \"Rustbucket\" Pistol"]},

    # === SMGs ===
    {"id": "p8-smg", "name": "P8-SMG", "type": "SMG", "size": 1, "manufacturer": "Behring",
     "damage": 16, "ammo": 30, "fire_rate": "Full Auto", "effective_range": "40m",
     "description": "High DPS submachine gun. Meta weapon for CQB. Customizable with attachments.",
     "price_auec": 8200,
     "locations": ["Cutter's Rig (Hurston)", "Live Fire Weapons (most stations)", "Looted from security NPCs"],
     "variants": ["P8-SMG \"Igniter\" SMG", "P8-SMG \"Whiteout\" SMG", "P8-SMG \"Mudskipper\" SMG"]},

    {"id": "ripper-smg", "name": "Ripper SMG", "type": "SMG", "size": 1, "manufacturer": "Verified Offworld Laser Technologies",
     "damage": 12, "ammo": 45, "fire_rate": "Full Auto", "effective_range": "35m",
     "description": "Rapid-fire laser SMG. Large ammo pool, sustained fire capability.",
     "price_auec": 8900,
     "locations": ["Live Fire Weapons (ARC-L1)", "Live Fire Weapons (CRU-L5)"],
     "variants": ["Ripper \"Cobalt\" SMG", "Ripper \"Sandstorm\" SMG"]},

    {"id": "b8-smg", "name": "B8 SMG", "type": "SMG", "size": 1, "manufacturer": "Kastak Arms",
     "damage": 18, "ammo": 25, "fire_rate": "Full Auto", "effective_range": "30m",
     "description": "Close-quarters ballistic SMG. High stopping power at short range.",
     "price_auec": 7500,
     "locations": ["Cutter's Rig (Hurston)", "Looted from outlaws"],
     "variants": ["B8 \"Predator\" SMG", "B8 \"Nightstalker\" SMG"]},

    {"id": "custodian-smg", "name": "Custodian SMG", "type": "SMG", "size": 1, "manufacturer": "Behring",
     "damage": 14, "ammo": 60, "fire_rate": "Full Auto", "effective_range": "45m",
     "description": "Laser SMG with large battery. Good sustained damage output.",
     "price_auec": 7800,
     "locations": ["Live Fire Weapons (Port Olisar)", "Live Fire Weapons (Baijini Point)"],
     "variants": ["Custodian \"Callsign\" SMG", "Custodian \"Rime\" SMG"]},

    # === ASSAULT RIFLES ===
    {"id": "p4-ar", "name": "P4-AR Assault Rifle", "type": "Assault Rifle", "size": 2, "manufacturer": "Behring",
     "damage": 20, "ammo": 40, "fire_rate": "Full Auto/Semi", "effective_range": "65m",
     "description": "Classic ballistic assault rifle. 40-round mag, highly customizable. Best beginner weapon.",
     "price_auec": 13800,
     "locations": ["Live Fire Weapons (all stations)", "Looted from NPCs"],
     "variants": ["P4-AR \"Copperhead\" Assault Rifle", "P4-AR \"Dovetail\" Assault Rifle", "P4-AR \"Mesquite\" Assault Rifle"]},

    {"id": "karna-rifle", "name": "Karna Rifle", "type": "Assault Rifle", "size": 2, "manufacturer": "Kastak Arms",
     "damage": 25, "ammo": 60, "fire_rate": "Full Auto", "effective_range": "60m",
     "description": "Powerful laser assault rifle. Strong for PvE and PvP.",
     "price_auec": 17500,
     "locations": ["Live Fire Weapons (Lorville)", "Live Fire Weapons (CRU-L4)"],
     "variants": ["Karna \"Stinger\" Rifle", "Karna \"Ashfall\" Rifle"]},

    {"id": "parallax-ar", "name": "Parallax Assault Rifle", "type": "Assault Rifle", "size": 2, "manufacturer": "Verified Offworld Laser Technologies",
     "damage": 18, "ammo": 45, "fire_rate": "Full Auto", "effective_range": "70m",
     "description": "Versatile medium/long range laser assault rifle.",
     "price_auec": 16800,
     "locations": ["Live Fire Weapons (New Babbage)", "Live Fire Weapons (Area 18)"],
     "variants": ["Parallax \"Stalker\" Assault Rifle", "Parallax \"Tundra\" Assault Rifle"]},

    {"id": "c54-smg", "name": "C54 SMG", "type": "Assault Rifle", "size": 2, "manufacturer": "Kastak Arms",
     "damage": 22, "ammo": 30, "fire_rate": "Full Auto/Burst", "effective_range": "55m",
     "description": "Compact ballistic assault weapon. Good balance of damage and handling.",
     "price_auec": 9500,
     "locations": ["Live Fire Weapons (Grim HEX)", "Looted from outlaws"],
     "variants": ["C54 \"Bloodline\" SMG"]},

    {"id": "s71-rifle", "name": "S71 Rifle", "type": "Assault Rifle", "size": 2, "manufacturer": "Behring",
     "damage": 30, "ammo": 20, "fire_rate": "Semi-Auto", "effective_range": "80m",
     "description": "Semi-auto marksman rifle. High damage per shot, preferred for long range.",
     "price_auec": 15200,
     "locations": ["Cutter's Rig (Hurston)", "Live Fire Weapons (HUR-L1)"],
     "variants": ["S71 \"Wildfire\" Rifle", "S71 \"Frostbite\" Rifle"]},

    # === LMGs ===
    {"id": "f55-lmg", "name": "F55 LMG", "type": "LMG", "size": 3, "manufacturer": "Behring",
     "damage": 20, "ammo": 100, "fire_rate": "Full Auto (Gatling)", "effective_range": "50m",
     "description": "Handheld ballistic gatling gun. Extreme suppression capability.",
     "price_auec": 22400,
     "locations": ["Live Fire Weapons (Lorville)", "Live Fire Weapons (CRU-L4)"],
     "variants": ["F55 \"Nighthawk\" LMG", "F55 \"Sandstorm\" LMG"]},

    {"id": "fs9-lmg", "name": "FS-9 LMG", "type": "LMG", "size": 3, "manufacturer": "Kastak Arms",
     "damage": 22, "ammo": 80, "fire_rate": "Full Auto", "effective_range": "55m",
     "description": "Heavy ballistic LMG. Great for group combat.",
     "price_auec": 20600,
     "locations": ["Cutter's Rig (Hurston)", "Looted from NPCs"],
     "variants": ["FS-9 \"Bushwhacker\" LMG"]},

    {"id": "demeco-lmg", "name": "Demeco LMG", "type": "LMG", "size": 3, "manufacturer": "Verified Offworld Laser Technologies",
     "damage": 16, "ammo": 165, "fire_rate": "Full Auto", "effective_range": "55m",
     "description": "Laser LMG with massive battery. Sustained suppressive fire.",
     "price_auec": 24800,
     "locations": ["Live Fire Weapons (CRU-L5)", "Live Fire Weapons (ARC-L2)"],
     "variants": ["Demeco \"Redline\" LMG", "Demeco \"Whiteout\" LMG"]},

    # === SHOTGUNS ===
    {"id": "ravager-shotgun", "name": "Ravager-212 Shotgun", "type": "Shotgun", "size": 2, "manufacturer": "Apocalypse Arms",
     "damage": 80, "ammo": 8, "fire_rate": "Pump-Action", "effective_range": "15m",
     "description": "Devastating pump-action shotgun. One-shot potential at close range.",
     "price_auec": 13500,
     "locations": ["Live Fire Weapons (Grim HEX)", "Looted from outlaws"],
     "variants": ["Ravager-212 \"Brawler\" Shotgun", "Ravager-212 \"Rustbucket\" Shotgun"]},

    {"id": "br2-shotgun", "name": "BR-2 Shotgun", "type": "Shotgun", "size": 2, "manufacturer": "Behring",
     "damage": 60, "ammo": 6, "fire_rate": "Semi-Auto", "effective_range": "20m",
     "description": "Semi-automatic shotgun. Good for rapid follow-up shots.",
     "price_auec": 11200,
     "locations": ["Live Fire Weapons (Lorville)", "Live Fire Weapons (Area 18)"],
     "variants": ["BR-2 \"Copperhead\" Shotgun", "BR-2 \"Nighthawk\" Shotgun"]},

    {"id": "scalpel-shotgun", "name": "Scalpel Shotgun", "type": "Shotgun", "size": 2, "manufacturer": "Verified Offworld Laser Technologies",
     "damage": 45, "ammo": 20, "fire_rate": "Semi-Auto", "effective_range": "25m",
     "description": "Laser shotgun with tighter spread. More range than ballistic shotguns.",
     "price_auec": 12400,
     "locations": ["Live Fire Weapons (New Babbage)", "Live Fire Weapons (Port Tressler)"],
     "variants": ["Scalpel \"Ember\" Shotgun", "Scalpel \"Glacier\" Shotgun"]},

    # === SNIPER RIFLES ===
    {"id": "arrowhead-sniper", "name": "Arrowhead Sniper Rifle", "type": "Sniper Rifle", "size": 3, "manufacturer": "Klaus & Werner",
     "damage": 80, "ammo": 8, "fire_rate": "Bolt-Action", "effective_range": "200m",
     "description": "Long-range sniper rifle. Community favorite for precision engagements.",
     "price_auec": 21200,
     "locations": ["Live Fire Weapons (New Babbage)", "Live Fire Weapons (HUR-L5)"],
     "variants": ["Arrowhead \"Copperhead\" Sniper", "Arrowhead \"Thunderstrike\" Sniper"]},

    {"id": "p6-lr-sniper", "name": "P6-LR Sniper Rifle", "type": "Sniper Rifle", "size": 3, "manufacturer": "Behring",
     "damage": 100, "ammo": 5, "fire_rate": "Bolt-Action", "effective_range": "250m",
     "description": "50-cal ballistic sniper. 8x scope + rangefinder. Highest FPS damage.",
     "price_auec": 19400,
     "locations": ["Live Fire Weapons (Port Tressler)", "Live Fire Weapons (CRU-L1)"],
     "variants": ["P6-LR \"Ghost\" Sniper Rifle"]},

    {"id": "a03-sniper", "name": "A03 Sniper Rifle", "type": "Sniper Rifle", "size": 3, "manufacturer": "Gemini",
     "damage": 42, "ammo": 15, "fire_rate": "Semi-Auto", "effective_range": "150m",
     "description": "Semi-auto sniper with larger magazine. Good for follow-up shots.",
     "price_auec": 18600,
     "locations": ["Live Fire Weapons (Baijini Point)", "Live Fire Weapons (ARC-L1)"],
     "variants": ["A03 \"Canuto\" Sniper Rifle", "A03 \"Red Alert\" Sniper Rifle", "A03 \"Wildwood\" Sniper Rifle"]},

    # === RAILGUNS ===
    {"id": "deadrig-railgun", "name": "Deadrig Railgun", "type": "Railgun", "size": 4, "manufacturer": "Kastak Arms",
     "damage": 150, "ammo": 3, "fire_rate": "Charge", "effective_range": "300m",
     "description": "Electromagnetic railgun. Charges before firing. Extreme damage.",
     "price_auec": 14800,
     "locations": ["Grim HEX", "Looted from bunker bosses"],
     "variants": ["Deadrig \"Extinction\" Railgun"]},

    # === GRENADE LAUNCHERS ===
    {"id": "gp33-launcher", "name": "GP-33 Grenade Launcher", "type": "Grenade Launcher", "size": 3, "manufacturer": "Behring",
     "damage": 120, "ammo": 6, "fire_rate": "Semi-Auto", "effective_range": "80m",
     "description": "Six-round grenade launcher. Area denial and group damage.",
     "price_auec": 28500,
     "locations": ["Grim HEX", "Looted from bunker enemies"],
     "variants": ["GP-33 \"Copperhead\" Launcher"]},

    # === MISSILE LAUNCHERS ===
    {"id": "animus-launcher", "name": "Animus Missile Launcher", "type": "Missile Launcher", "size": 5, "manufacturer": "Apocalypse Arms",
     "damage": 150, "ammo": 1, "fire_rate": "Single-Shot", "effective_range": "200m",
     "description": "Shoulder-mounted missile launcher. Anti-vehicle capability.",
     "price_auec": 32000,
     "locations": ["Grim HEX", "Rare loot drop"],
     "variants": ["Animus \"Quite Useful\" Missile Launcher"]},

    # === MEDICAL ===
    {"id": "medgun", "name": "MedGun", "type": "Medical Device", "size": 1, "manufacturer": "CureLife",
     "damage": 0, "ammo": 100, "fire_rate": "Continuous", "effective_range": "5m",
     "description": "Medical healing device. Essential for team play.",
     "price_auec": 5500,
     "locations": ["Medical supply vendors (all stations)", "Pharmacy (Orison, New Babbage)"],
     "variants": ["MedGun Mk II", "MedGun \"Lifeline\""]},

    {"id": "multitool", "name": "Multi-Tool", "type": "Medical Device", "size": 1, "manufacturer": "Greycat Industrial",
     "damage": 0, "ammo": 0, "fire_rate": "N/A", "effective_range": "3m",
     "description": "Versatile utility tool. Healing, cutting, tractor beam with attachments.",
     "price_auec": 1200,
     "locations": ["Most station shops", "Cargo Decks"],
     "variants": []},

    # === GRENADES ===
    {"id": "frag-grenade", "name": "Frag Grenade", "type": "Grenade", "size": 0, "manufacturer": "Behring",
     "damage": 200, "ammo": 1, "fire_rate": "Throw", "effective_range": "30m",
     "description": "Standard fragmentation grenade. Lethal in enclosed spaces. 3.5s fuse.",
     "price_auec": 150,
     "locations": ["Live Fire Weapons (most stations)", "Looted from NPCs"],
     "variants": []},

    {"id": "flash-grenade", "name": "Flash Grenade", "type": "Grenade", "size": 0, "manufacturer": "Behring",
     "damage": 0, "ammo": 1, "fire_rate": "Throw", "effective_range": "20m",
     "description": "Flashbang. Blinds and disorients enemies. Essential for breaching.",
     "price_auec": 120,
     "locations": ["Live Fire Weapons (most stations)", "Looted from security NPCs"],
     "variants": []},

    {"id": "smoke-grenade", "name": "Smoke Grenade", "type": "Grenade", "size": 0, "manufacturer": "Behring",
     "damage": 0, "ammo": 1, "fire_rate": "Throw", "effective_range": "25m",
     "description": "Deploys thick smoke screen. Blocks line of sight for 15s.",
     "price_auec": 100,
     "locations": ["Live Fire Weapons (Lorville)", "Live Fire Weapons (Area 18)"],
     "variants": []},

    {"id": "emp-grenade", "name": "EMP Grenade", "type": "Grenade", "size": 0, "manufacturer": "Kastak Arms",
     "damage": 0, "ammo": 1, "fire_rate": "Throw", "effective_range": "15m",
     "description": "Electromagnetic pulse grenade. Disables electronics and shields temporarily.",
     "price_auec": 350,
     "locations": ["Grim HEX", "Rare loot from bunker bosses"],
     "variants": []},

    # === UTILITIES ===
    {"id": "medpen", "name": "MedPen", "type": "Utility", "size": 0, "manufacturer": "CureLife",
     "damage": 0, "ammo": 1, "fire_rate": "Inject", "effective_range": "Self",
     "description": "Emergency medical injector. Heals minor wounds and stops bleeding. Stackable.",
     "price_auec": 100,
     "locations": ["Medical supply vendors (all stations)", "Pharmacy (Orison, New Babbage)", "Looted from NPCs"],
     "variants": ["MedPen Mk II"]},

    {"id": "oxypen", "name": "OxyPen", "type": "Utility", "size": 0, "manufacturer": "CureLife",
     "damage": 0, "ammo": 1, "fire_rate": "Inject", "effective_range": "Self",
     "description": "Oxygen supplement injector. Restores O2 in emergency situations.",
     "price_auec": 75,
     "locations": ["Medical supply vendors (all stations)", "Pharmacy"],
     "variants": []},

    {"id": "adrenapen", "name": "AdrenaPen", "type": "Utility", "size": 0, "manufacturer": "CureLife",
     "damage": 0, "ammo": 1, "fire_rate": "Inject", "effective_range": "Self",
     "description": "Adrenaline injector. Temporarily boosts stamina and reduces pain effects.",
     "price_auec": 200,
     "locations": ["Pharmacy (Orison, New Babbage)", "Medical vendors"],
     "variants": []},

    {"id": "tractor-beam-tool", "name": "Tractor Beam (Multi-Tool)", "type": "Utility", "size": 0, "manufacturer": "Greycat Industrial",
     "damage": 0, "ammo": 0, "fire_rate": "Continuous", "effective_range": "10m",
     "description": "Multi-tool tractor beam attachment. Move cargo boxes and small objects.",
     "price_auec": 1750,
     "locations": ["Cargo Decks (all stations)", "Most station shops"],
     "variants": []},

    {"id": "cutting-tool", "name": "Cutting Tool (Multi-Tool)", "type": "Utility", "size": 0, "manufacturer": "Greycat Industrial",
     "damage": 0, "ammo": 0, "fire_rate": "Continuous", "effective_range": "1m",
     "description": "Multi-tool cutting attachment. Breach locked doors and panels.",
     "price_auec": 1400,
     "locations": ["Cargo Decks (all stations)", "Hardware shops"],
     "variants": []},

    {"id": "repair-tool", "name": "Repair Tool (Multi-Tool)", "type": "Utility", "size": 0, "manufacturer": "Greycat Industrial",
     "damage": 0, "ammo": 0, "fire_rate": "Continuous", "effective_range": "3m",
     "description": "Multi-tool repair attachment. Fix damaged ship components in the field.",
     "price_auec": 1600,
     "locations": ["Cargo Decks (all stations)", "Ship component shops"],
     "variants": []},
]


# PERSONAL ARMOR - base sets with variants (color schemes)
ARMOR_SETS = [
    # === HEAVY ARMOR ===
    {"id": "adp-heavy", "name": "ADP", "type": "Heavy", "manufacturer": "Clark Defense Systems",
     "temp_max": 105, "temp_min": -75, "radiation": 26800,
     "description": "Heavy combat armor. Excellent protection and environmental resistance.",
     "price_auec": 15400,
     "locations": ["Distribution Centers (all)", "Armor shops (Lorville, Area 18)"],
     "loot_locations": ["Bunker missions", "Distribution Centers"],
     "variants": ["ADP Aqua", "ADP Black", "ADP Dark Green", "ADP Grey", "ADP Olive", "ADP Twilight", "ADP Imperial", "ADP Sienna"]},

    {"id": "adp-mk4-heavy", "name": "ADP-mk4", "type": "Heavy", "manufacturer": "Clark Defense Systems",
     "temp_max": 100, "temp_min": -70, "radiation": 26800,
     "description": "Upgraded ADP variant. Found in contested zones. Rare.",
     "price_auec": 18200,
     "locations": ["Pyro One contested zones", "High-security bunkers"],
     "loot_locations": ["Pyro I", "Xenomorph encounter zones"],
     "variants": ["ADP-mk4 Red Alert", "ADP-mk4 Woodland"]},

    {"id": "antium-heavy", "name": "Antium", "type": "Heavy", "manufacturer": "Quirinus Tech",
     "temp_max": 120, "temp_min": -95, "radiation": 26800,
     "description": "Best environmental resistance of all heavy armors. Exploration-grade.",
     "price_auec": 16800,
     "locations": ["Dumper's Depot (New Babbage)", "Armor shops (Orison)"],
     "loot_locations": ["Cave exploration sites"],
     "variants": ["Antium Cobalt", "Antium Ember", "Antium Gold", "Antium Ice"]},

    {"id": "citadel-heavy", "name": "Citadel", "type": "Heavy", "manufacturer": "Kastak Arms",
     "temp_max": 100, "temp_min": -80, "radiation": 26800,
     "description": "Combat-focused heavy armor. Distinctive angular design.",
     "price_auec": 19500,
     "locations": ["ASD Facilities (Pyro)", "Crusader Security loot"],
     "loot_locations": ["ASD Facilities", "Security bunkers"],
     "variants": ["Citadel Ash", "Citadel Crimson", "Citadel Olive", "Citadel Storm"]},

    {"id": "corbel-heavy", "name": "Corbel", "type": "Heavy", "manufacturer": "Odin Munitions",
     "temp_max": 100, "temp_min": -70, "radiation": 26800,
     "description": "Rugged heavy armor designed for sustained ground operations.",
     "price_auec": 17600,
     "locations": ["Armor shops (Lorville)", "Distribution Centers"],
     "loot_locations": ["Ground bunker missions"],
     "variants": ["Corbel Dustwalker", "Corbel Nightwatch", "Corbel Frostbite", "Corbel Pyro"]},

    {"id": "defiance-heavy", "name": "Defiance", "type": "Heavy", "manufacturer": "Clark Defense Systems",
     "temp_max": 102, "temp_min": -72, "radiation": 26800,
     "description": "Premium heavy armor with enhanced protection.",
     "price_auec": 20200,
     "locations": ["Subscriber rewards", "Rare loot"],
     "loot_locations": ["High-threat bunkers"],
     "variants": ["Defiance Charcoal", "Defiance Desert", "Defiance Firestarter", "Defiance Hailstorm", "Defiance Sunchaser", "Defiance Tactical"]},

    {"id": "morozov-sh-heavy", "name": "Morozov-SH", "type": "Heavy", "manufacturer": "Roussimoff",
     "temp_max": 105, "temp_min": -75, "radiation": 26800,
     "description": "Crusader Security heavy armor. Distinct blue/white markings.",
     "price_auec": 12800,
     "locations": ["ASD Facilities", "Looted from Crusader Security NPCs"],
     "loot_locations": ["ASD Facilities", "Crusader security zones"],
     "variants": ["Morozov-SH Aftershock", "Morozov-SH Brushdrift", "Morozov-SH Crusader Edition", "Morozov-SH Redshift", "Morozov-SH Snowdrift", "Morozov-SH Terracotta", "Morozov-SH Thule"]},

    {"id": "overlord-heavy", "name": "Overlord", "type": "Heavy", "manufacturer": "Doomsday",
     "temp_max": 100, "temp_min": -70, "radiation": 26800,
     "description": "Intimidating heavy armor with skull motif. Popular with outlaws.",
     "price_auec": 13500,
     "locations": ["Grim HEX", "Subscription exclusive variants"],
     "loot_locations": ["Outlaw bunkers"],
     "variants": ["Overlord Dust Storm", "Overlord Predator", "Overlord Riptide", "Overlord Stinger", "Overlord Supernova", "Overlord Switchback"]},

    {"id": "palatino-heavy", "name": "Palatino", "type": "Heavy", "manufacturer": "Quirinus Tech",
     "temp_max": 100, "temp_min": -70, "radiation": 26800,
     "description": "Widely available heavy armor. Found at all distribution centers.",
     "price_auec": 11200,
     "locations": ["All Distribution Centers", "Armor shops (all landing zones)"],
     "loot_locations": ["Distribution Centers"],
     "variants": ["Palatino Forest", "Palatino Desert", "Palatino Urban", "Palatino Snow"]},

    # === MEDIUM ARMOR ===
    {"id": "artimex-medium", "name": "Artimex", "type": "Medium", "manufacturer": "Clark Defense Systems",
     "temp_max": 85, "temp_min": -55, "radiation": 26400,
     "description": "Balanced medium armor. Good mix of protection and mobility.",
     "price_auec": 14200,
     "locations": ["Armor shops (most stations)", "Distribution Centers"],
     "loot_locations": ["Bunker missions"],
     "variants": ["Artimex Canuto", "Artimex Lodestone", "Artimex Red Alert", "Artimex Wildwood"]},

    {"id": "aril-medium", "name": "Aril", "type": "Medium", "manufacturer": "Quirinus Tech",
     "temp_max": 88, "temp_min": -58, "radiation": 26400,
     "description": "Medium exploration armor with good environmental protection.",
     "price_auec": 8400,
     "locations": ["Dumper's Depot (New Babbage)", "Cargo Decks (most stations)"],
     "loot_locations": ["Mining outposts"],
     "variants": ["Aril Black Cherry", "Aril Harvester", "Aril Hazard", "Aril Quicksilver", "Aril Red Alert"]},

    {"id": "aves-medium", "name": "Aves", "type": "Medium", "manufacturer": "Kastak Arms",
     "temp_max": 82, "temp_min": -52, "radiation": 26400,
     "description": "Combat-oriented medium armor. Favored by bounty hunters.",
     "price_auec": 9200,
     "locations": ["Armor shops (Lorville)", "Grim HEX"],
     "loot_locations": ["Bounty hunt targets"],
     "variants": ["Aves Midnight", "Aves Sandstorm", "Aves Charcoal", "Aves Crimson"]},

    {"id": "novikov-medium", "name": "Novikov", "type": "Medium", "manufacturer": "Odin Munitions",
     "temp_max": 95, "temp_min": -65, "radiation": 26400,
     "description": "Exploration suit with excellent cold protection. Popular for microTech.",
     "price_auec": 10600,
     "locations": ["Hatter Station", "New Babbage shops"],
     "loot_locations": ["microTech surface missions"],
     "variants": ["Novikov Amber", "Novikov Polar", "Novikov Ember", "Novikov Storm"]},

    {"id": "lynx-medium", "name": "Lynx", "type": "Medium", "manufacturer": "Behring",
     "temp_max": 80, "temp_min": -50, "radiation": 26400,
     "description": "Tactical medium armor. Good for all-around combat operations.",
     "price_auec": 7800,
     "locations": ["Armor shops (most stations)"],
     "loot_locations": ["General NPC loot"],
     "variants": ["Lynx Blue", "Lynx Draas", "Lynx Firebrick", "Lynx Lichen", "Lynx Olive", "Lynx Orange", "Lynx Sandstorm", "Lynx Seagreen"]},

    # === LIGHT ARMOR ===
    {"id": "arden-sl-light", "name": "Arden-SL", "type": "Light", "manufacturer": "Roussimoff",
     "temp_max": 68, "temp_min": -38, "radiation": 26800,
     "description": "Light security armor. Minimal protection, maximum mobility.",
     "price_auec": 8800,
     "locations": ["Armor shops (most stations)", "Cargo Decks"],
     "loot_locations": ["Security NPC drops"],
     "variants": ["Arden-SL Archangel", "Arden-SL Balefire", "Arden-SL Red Alert", "Arden-SL Rime"]},

    {"id": "aztalan-light", "name": "Aztalan", "type": "Light", "manufacturer": "Tehachapi",
     "temp_max": 68, "temp_min": -38, "radiation": 26000,
     "description": "Lightweight stealth-oriented armor. Low profile design.",
     "price_auec": 6200,
     "locations": ["Armor shops (Area 18)", "Grim HEX"],
     "loot_locations": ["Outlaw bunkers"],
     "variants": ["Aztalan Night", "Aztalan Desert", "Aztalan Ember", "Aztalan Frost"]},

    {"id": "calico-light", "name": "Calico", "type": "Light", "manufacturer": "Kastak Arms",
     "temp_max": 69, "temp_min": -39, "radiation": 26000,
     "description": "Agile light combat armor. Designed for fast-movers.",
     "price_auec": 5800,
     "locations": ["Armor shops (Lorville)", "Live Fire Weapons"],
     "loot_locations": ["Ground combat zones"],
     "variants": ["Calico Tactical"]},

    {"id": "fbl-8a-light", "name": "FBL-8a", "type": "Light", "manufacturer": "Clark Defense Systems",
     "temp_max": 65, "temp_min": -35, "radiation": 26000,
     "description": "Standard light combat armor. Widely available and affordable.",
     "price_auec": 6800,
     "locations": ["Armor shops (all landing zones)"],
     "loot_locations": ["General NPC drops"],
     "variants": ["FBL-8a Arctic Digital", "FBL-8a Desert Digital", "FBL-8a Imperial Red"]},

    {"id": "sterling-light", "name": "Sterling", "type": "Light", "manufacturer": "Quirinus Tech",
     "temp_max": 70, "temp_min": -40, "radiation": 26000,
     "description": "Exploration light armor. Better environmental stats than most light sets.",
     "price_auec": 9800,
     "locations": ["Pyro One", "Larger loot locations"],
     "loot_locations": ["Pyro I facilities", "Exploration sites"],
     "variants": ["Sterling Explorer", "Sterling Ranger", "Sterling Shadow", "Sterling Frost"]},

    # === ADDITIONAL MISSING SETS ===
    {"id": "orc-mkx-medium", "name": "ORC-mkX", "type": "Medium", "manufacturer": "Clark Defense Systems",
     "temp_max": 91, "temp_min": -61, "radiation": 26400,
     "description": "Medium combat armor used by Protector Marines. Successor to ORC-mkV. 30% damage reduction. EVA-rated.",
     "price_auec": 3200,
     "locations": ["Galleria FPS Armor (Jump Points)", "MIC-L4", "Area 18 Armor shops"],
     "loot_locations": ["Bunker missions", "Distribution Centers"],
     "variants": ["ORC-mkX Desert", "ORC-mkX Iceborn", "ORC-mkX Nightfire", "ORC-mkX Woodland", "ORC-mkX Singularity", "ORC-mkX Arctic", "ORC-mkX Autumn", "ORC-mkX Twilight"]},

    {"id": "orc-mkv-medium", "name": "ORC-mkV", "type": "Medium", "manufacturer": "Clark Defense Systems",
     "temp_max": 85, "temp_min": -55, "radiation": 26400,
     "description": "Predecessor to the ORC-mkX. Reliable medium combat armor still widely found in the verse.",
     "price_auec": 2800,
     "locations": ["Armor shops (Hurston)", "Distribution Centers"],
     "loot_locations": ["Bunker missions", "Security NPC drops"],
     "variants": ["ORC-mkV Desert", "ORC-mkV Arctic", "ORC-mkV Woodland", "ORC-mkV Olive"]},

    {"id": "macflex-medium", "name": "MacFlex", "type": "Medium", "manufacturer": "Clark Defense Systems",
     "temp_max": 82, "temp_min": -52, "radiation": 26400,
     "description": "Flex-weave medium armor with excellent mobility. Common civilian and security armor.",
     "price_auec": 4200,
     "locations": ["Armor shops (most stations)", "Cargo Decks"],
     "loot_locations": ["Distribution Centers", "General NPC drops"],
     "variants": ["MacFlex Black", "MacFlex Aqua", "MacFlex Blue", "MacFlex Dark Green", "MacFlex Dark Red", "MacFlex Grey", "MacFlex Imperial", "MacFlex Olive", "MacFlex Orange"]},

    {"id": "venture-light", "name": "Venture", "type": "Light", "manufacturer": "RSI",
     "temp_max": 70, "temp_min": -40, "radiation": 26000,
     "description": "RSI light exploration armor. Space-optimized with glass cockpit HUD integration.",
     "price_auec": 7200,
     "locations": ["Clothing shops (most stations)", "Dumper's Depot"],
     "loot_locations": [],
     "variants": ["Venture Black", "Venture Aqua", "Venture Blue", "Venture Dark Green", "Venture Grey", "Venture Executive", "Venture Ascension", "Venture Envy", "Venture Lovestruck"]},

    {"id": "inquisitor-medium", "name": "Inquisitor", "type": "Medium", "manufacturer": "Kastak Arms",
     "temp_max": 88, "temp_min": -58, "radiation": 26400,
     "description": "Enforcement-grade medium armor. Distinctive angular visor design. Favored by bounty hunters.",
     "price_auec": 11500,
     "locations": ["Grim HEX", "Armor shops (Lorville)"],
     "loot_locations": ["Bunker missions", "Nine Tails enemy drops"],
     "variants": ["Inquisitor Black Steel", "Inquisitor Neon Pink", "Inquisitor Raven"]},

    {"id": "truedef-pro-light", "name": "TrueDef-Pro", "type": "Light", "manufacturer": "Virgil Ltd",
     "temp_max": 65, "temp_min": -35, "radiation": 26000,
     "description": "Law enforcement light armor. 20% damage reduction. Used by Advocacy and CDF personnel.",
     "price_auec": 5500,
     "locations": ["Armor shops (most stations)", "Security facilities"],
     "loot_locations": ["Security NPC drops", "Advocacy missions"],
     "variants": ["TrueDef-Pro Red Silver", "TrueDef-Pro Black Grey", "TrueDef-Pro Black Grey Red", "TrueDef-Pro CDF", "TrueDef-Pro Black Silver Green", "TrueDef-Pro Aqua Black"]},

    {"id": "pab1-light", "name": "PAB-1", "type": "Light", "manufacturer": "Clark Defense Systems",
     "temp_max": 65, "temp_min": -35, "radiation": 26000,
     "description": "Police and security light armor. Minimal protection with high visibility markings.",
     "price_auec": 4800,
     "locations": ["Armor shops (all landing zones)", "Security outfitters"],
     "loot_locations": ["Security NPC drops", "Crusader Security zones"],
     "variants": ["PAB-1 Black", "PAB-1 Aqua", "PAB-1 Blue", "PAB-1 Desert", "PAB-1 Red", "PAB-1 Crusader Edition", "PAB-1 Imperial"]},

    # === FLIGHT SUITS ===
    {"id": "odyssey-ii-flight", "name": "Odyssey II", "type": "Flight Suit", "manufacturer": "RSI",
     "temp_max": 70, "temp_min": -40, "radiation": 15200,
     "description": "Standard RSI flight suit. Starter equipment for most pilots.",
     "price_auec": 14800,
     "locations": ["All station clothing shops", "Default starter gear"],
     "loot_locations": [],
     "variants": ["Odyssey II Red", "Odyssey II Blue", "Odyssey II Black", "Odyssey II White", "Odyssey II Gold"]},

    {"id": "sol-iii-flight", "name": "Sol-III", "type": "Flight Suit", "manufacturer": "UEE Navy",
     "temp_max": 60, "temp_min": -30, "radiation": 15200,
     "description": "Military flight suit. UEE Navy standard issue.",
     "price_auec": 10200,
     "locations": ["Military surplus shops", "Looted from UEE Navy NPCs"],
     "loot_locations": ["UEE naval vessels"],
     "variants": ["Sol-III Olive", "Sol-III Grey", "Sol-III Navy", "Sol-III Black"]},
]


def get_all_fps_weapons():
    return FPS_WEAPONS

def get_all_armor_sets():
    return ARMOR_SETS

def get_all_equipment():
    return EQUIPMENT


# === EQUIPMENT: Mining, Medical, Backpacks, Undersuits ===
EQUIPMENT = [
    # === MINING HEADS ===
    {"id": "arbor-mh1", "name": "Arbor MH1 Mining Head", "type": "Mining Head", "subtype": "Ship", "manufacturer": "Greycat Industrial",
     "stats": {"power": 3, "range": "200m", "resistance": "Low", "optimal_charge": "30-50%"},
     "description": "Starter mining head for Prospector. Low power, good for softer rocks.",
     "locations": ["Cargo Decks (most stations)", "Shubin Mining (all locations)"],
     "price_auec": 13000, "variants": []},

    {"id": "helix-mh1", "name": "Helix I Mining Head", "type": "Mining Head", "subtype": "Ship", "manufacturer": "Argo Astronautics",
     "stats": {"power": 5, "range": "200m", "resistance": "Medium", "optimal_charge": "25-55%"},
     "description": "Mid-tier mining head. Wider optimal charge window, more forgiving.",
     "locations": ["Shubin Mining (Lorville)", "Cargo Decks (Area 18)"],
     "price_auec": 82400, "variants": []},

    {"id": "lancet-mh1", "name": "Lancet MH1 Mining Head", "type": "Mining Head", "subtype": "Ship", "manufacturer": "Thermyte Concern",
     "stats": {"power": 4, "range": "250m", "resistance": "Medium", "optimal_charge": "20-60%"},
     "description": "Precision mining head. Best optimal window, ideal for quantanium.",
     "locations": ["Shubin Mining (New Babbage)", "ARC Mining (Orison)"],
     "price_auec": 108000, "variants": []},

    {"id": "hofstede-s1", "name": "Hofstede S1 Mining Head", "type": "Mining Head", "subtype": "Ship", "manufacturer": "Greycat Industrial",
     "stats": {"power": 6, "range": "200m", "resistance": "High", "optimal_charge": "35-50%"},
     "description": "High-power mining head. Cracks tougher deposits but narrower charge window.",
     "locations": ["Shubin Mining (Hurston)", "Cargo Decks (Lorville)"],
     "price_auec": 122000, "variants": []},

    {"id": "klein-s1", "name": "Klein S1 Mining Head", "type": "Mining Head", "subtype": "Ship", "manufacturer": "Thermyte Concern",
     "stats": {"power": 7, "range": "200m", "resistance": "Very High", "optimal_charge": "40-55%"},
     "description": "Top-tier mining head. Highest power, needed for the hardest rocks.",
     "locations": ["Shubin Mining (Area 18)", "Tammany & Sons (Levski)"],
     "price_auec": 146000, "variants": []},

    # === HAND MINING TOOLS ===
    {"id": "multitool-ore", "name": "OreBit Mining Attachment", "type": "Mining Attachment", "subtype": "Hand", "manufacturer": "Greycat Industrial",
     "stats": {"power": 1, "range": "15m", "resistance": "Low", "optimal_charge": "30-60%"},
     "description": "Multi-tool mining attachment. Mine hand-mineable deposits for gems and hadanite.",
     "locations": ["Cargo Decks (all stations)", "Mining outposts"],
     "price_auec": 1750, "variants": []},

    # === MINING CONSUMABLES ===
    {"id": "surge-module", "name": "Surge Mining Module", "type": "Mining Module", "subtype": "Consumable", "manufacturer": "Shubin Interstellar",
     "stats": {"effect": "+30% laser power for 4s", "charges": 4},
     "description": "Temporarily boosts mining laser power. Essential for cracking quantanium.",
     "locations": ["Shubin Mining (all locations)", "Cargo Decks"],
     "price_auec": 2200, "variants": []},

    {"id": "stampede-module", "name": "Stampede Mining Module", "type": "Mining Module", "subtype": "Consumable", "manufacturer": "Shubin Interstellar",
     "stats": {"effect": "+20% resistance reduction for 5s", "charges": 4},
     "description": "Reduces rock resistance temporarily. Pairs well with lower-power heads.",
     "locations": ["Shubin Mining (all locations)", "Cargo Decks"],
     "price_auec": 2800, "variants": []},

    {"id": "brandt-module", "name": "Brandt Mining Module", "type": "Mining Module", "subtype": "Consumable", "manufacturer": "Shubin Interstellar",
     "stats": {"effect": "+15% optimal window width for 6s", "charges": 4},
     "description": "Widens optimal charge window. Safer mining, less risk of overcharge.",
     "locations": ["Shubin Mining (most locations)", "Cargo Decks"],
     "price_auec": 1800, "variants": []},

    {"id": "forel-module", "name": "Forel Mining Module", "type": "Mining Module", "subtype": "Consumable", "manufacturer": "Shubin Interstellar",
     "stats": {"effect": "Reduces instability by 40%", "charges": 3},
     "description": "Stabilizes volatile rocks. Critical for quantanium to prevent detonation.",
     "locations": ["Shubin Mining (New Babbage)", "Cargo Decks (Port Tressler)"],
     "price_auec": 3200, "variants": []},

    # === MEDICAL SUPPLIES ===
    {"id": "medgun-paramedic", "name": "CuraLife Medical Gun (Paramedic)", "type": "Medical Device", "subtype": "Tool", "manufacturer": "CureLife",
     "stats": {"heal_rate": "Fast", "range": "5m", "drug_capacity": 4},
     "description": "Long-range medical device. Heal teammates from a distance. Essential for group play.",
     "locations": ["Pharmacies (all landing zones)", "Medical supply vendors"],
     "price_auec": 5500, "variants": []},

    {"id": "medpen-mk2", "name": "MedPen Mk II", "type": "Medical Device", "subtype": "Consumable", "manufacturer": "CureLife",
     "stats": {"heal_amount": "Major wounds", "blood_drug_level": "+15%"},
     "description": "Enhanced medical injector. Heals major wounds but adds drug toxicity.",
     "locations": ["Pharmacies (all landing zones)", "Medical kiosks"],
     "price_auec": 350, "variants": []},

    {"id": "hemozal", "name": "Hemozal", "type": "Medical Device", "subtype": "Consumable", "manufacturer": "CureLife",
     "stats": {"effect": "Removes blood drug level", "charges": 1},
     "description": "Detox injector. Clears accumulated drug effects from medical treatments.",
     "locations": ["Pharmacies (Orison, New Babbage)", "Hospital kiosks"],
     "price_auec": 200, "variants": []},

    {"id": "medical-stretcher", "name": "Medical Stretcher", "type": "Medical Device", "subtype": "Equipment", "manufacturer": "CureLife",
     "stats": {"capacity": "1 patient", "effect": "Stabilize + transport"},
     "description": "Deployable stretcher for transporting downed players. Used in Apollo/Cutlass Red.",
     "locations": ["Medical supply vendors", "Ship medical bays"],
     "price_auec": 0, "variants": []},

    # === BACKPACKS ===
    {"id": "pembroke-backpack", "name": "Pembroke Backpack", "type": "Backpack", "subtype": "Large", "manufacturer": "RSI",
     "stats": {"capacity": "2.85 SCU", "slots": 8},
     "description": "Large exploration backpack. Best capacity for extended surface missions.",
     "locations": ["Cargo Decks (most stations)", "Dumper's Depot"],
     "price_auec": 3600, "variants": ["Pembroke Red", "Pembroke Gold"]},

    {"id": "macflex-backpack", "name": "MacFlex Backpack", "type": "Backpack", "subtype": "Medium", "manufacturer": "Clark Defense Systems",
     "stats": {"capacity": "1.71 SCU", "slots": 6},
     "description": "Standard medium backpack. Good balance of capacity and mobility.",
     "locations": ["Armor shops (most stations)", "Cargo Decks"],
     "price_auec": 2400, "variants": []},

    {"id": "novikov-backpack", "name": "Novikov Backpack", "type": "Backpack", "subtype": "Large", "manufacturer": "Odin Munitions",
     "stats": {"capacity": "2.85 SCU", "slots": 8},
     "description": "Cold-weather exploration backpack. Pairs with Novikov armor set.",
     "locations": ["Hatter Station (microTech)", "New Babbage shops"],
     "price_auec": 4200, "variants": []},

    {"id": "mining-backpack", "name": "Mining Satchel", "type": "Backpack", "subtype": "Utility", "manufacturer": "Greycat Industrial",
     "stats": {"capacity": "0.85 SCU", "slots": 4, "bonus": "Hand-mined ore storage"},
     "description": "Specialized mining backpack. Store hand-mined gems and minerals directly.",
     "locations": ["Shubin Mining (all locations)", "Cargo Decks"],
     "price_auec": 1800, "variants": []},

    # === UNDERSUITS ===
    {"id": "alantin-undersuit", "name": "Alantin Undersuit", "type": "Undersuit", "subtype": "Standard", "manufacturer": "RSI",
     "stats": {"temp_max": 50, "temp_min": -20, "o2_capacity": "10 min"},
     "description": "Basic undersuit. Worn under all armor sets. Standard life support.",
     "locations": ["Clothing shops (all stations)", "Default starter gear"],
     "price_auec": 800, "variants": ["Alantin White", "Alantin Black"]},

    {"id": "venture-undersuit", "name": "Venture Undersuit", "type": "Undersuit", "subtype": "Exploration", "manufacturer": "RSI",
     "stats": {"temp_max": 65, "temp_min": -35, "o2_capacity": "15 min"},
     "description": "Enhanced exploration undersuit. Better temperature range and O2 capacity.",
     "locations": ["Clothing shops (New Babbage, Orison)", "Dumper's Depot"],
     "price_auec": 2200, "variants": ["Venture Pathfinder"]},

    {"id": "arden-undersuit", "name": "Arden Undersuit", "type": "Undersuit", "subtype": "Tactical", "manufacturer": "Roussimoff",
     "stats": {"temp_max": 55, "temp_min": -25, "o2_capacity": "12 min"},
     "description": "Tactical undersuit with reinforced weave. Slightly better damage mitigation.",
     "locations": ["Armor shops (Lorville)", "Military surplus"],
     "price_auec": 1500, "variants": ["Arden Black", "Arden Navy"]},

    {"id": "novikov-undersuit", "name": "Novikov Undersuit", "type": "Undersuit", "subtype": "Cold Weather", "manufacturer": "Odin Munitions",
     "stats": {"temp_max": 45, "temp_min": -55, "o2_capacity": "14 min"},
     "description": "Cold-weather specialist undersuit. Best-in-class cold protection.",
     "locations": ["Hatter Station (microTech)", "New Babbage shops"],
     "price_auec": 3000, "variants": []},

    {"id": "pembroke-undersuit", "name": "Pembroke Undersuit", "type": "Undersuit", "subtype": "Heat Resistant", "manufacturer": "RSI",
     "stats": {"temp_max": 85, "temp_min": -10, "o2_capacity": "14 min"},
     "description": "Heat-resistant undersuit. Essential for extreme heat environments.",
     "locations": ["Cargo Decks (Lorville)", "Armor shops (ArcCorp)"],
     "price_auec": 3400, "variants": []},

    # === SALVAGE TOOLS ===
    {"id": "salvage-multitool", "name": "Salvage Attachment (Multi-Tool)", "type": "Salvage Tool", "subtype": "Hand", "manufacturer": "Greycat Industrial",
     "stats": {"range": "8m", "rate": "Slow", "material": "RMC"},
     "description": "Multi-tool salvage attachment. Strip hull materials (RMC) from derelict ships by hand.",
     "locations": ["Cargo Decks (all stations)", "Dumper's Depot"],
     "price_auec": 2100, "variants": []},

    {"id": "reclaimer-claw", "name": "Reclaimer Salvage Claw", "type": "Salvage Tool", "subtype": "Ship", "manufacturer": "Aegis Dynamics",
     "stats": {"range": "50m", "rate": "Fast", "material": "RMC + Components"},
     "description": "Ship-mounted industrial salvage arm. Strips ships at scale. Exclusive to Reclaimer.",
     "locations": ["Included with Reclaimer", "Cannot be purchased separately"],
     "price_auec": 0, "variants": []},

    {"id": "vulture-scraper", "name": "Vulture Scraper Module", "type": "Salvage Tool", "subtype": "Ship", "manufacturer": "Drake Interplanetary",
     "stats": {"range": "30m", "rate": "Medium", "material": "RMC"},
     "description": "Medium salvage beam for the Vulture. Good balance of speed and capacity.",
     "locations": ["Included with Vulture", "Cannot be purchased separately"],
     "price_auec": 0, "variants": []},

    # === SCANNING TOOLS ===
    {"id": "scanning-module", "name": "Scanning Attachment (Multi-Tool)", "type": "Scanner", "subtype": "Hand", "manufacturer": "Greycat Industrial",
     "stats": {"range": "100m", "detection": "Mineral deposits, items, NPCs"},
     "description": "Multi-tool scanning attachment. Detect mineable deposits and lootable items.",
     "locations": ["Cargo Decks (all stations)", "Mining outposts"],
     "price_auec": 1500, "variants": []},

    {"id": "ping-scanner", "name": "Ship Ping Scanner", "type": "Scanner", "subtype": "Ship", "manufacturer": "Various",
     "stats": {"range": "Varies by radar", "detection": "Ships, stations, POIs"},
     "description": "Built-in ship scanner. Range depends on installed radar component.",
     "locations": ["Default on all ships", "Upgrade via radar components"],
     "price_auec": 0, "variants": []},

    # === HACKING TOOLS ===
    {"id": "crypto-key", "name": "CryptoKey", "type": "Hacking Tool", "subtype": "Consumable", "manufacturer": "Coda Systems",
     "stats": {"uses": 1, "effect": "Bypass security panel", "success_rate": "75%"},
     "description": "Single-use hacking chip. Bypass locked doors and security panels in bunkers.",
     "locations": ["Grim HEX", "Looted from outlaw NPCs", "Rare loot from bunkers"],
     "price_auec": 500, "variants": []},

    {"id": "e-warfare-device", "name": "E-War Device", "type": "Hacking Tool", "subtype": "Ship", "manufacturer": "Aegis Dynamics",
     "stats": {"range": "3km", "effect": "Disrupt target systems", "duration": "8s"},
     "description": "Ship-mounted electronic warfare suite. Disrupts enemy shields and targeting. Vanguard Sentinel exclusive.",
     "locations": ["Included with Vanguard Sentinel"],
     "price_auec": 0, "variants": []},
]
