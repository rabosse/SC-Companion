"""Personal gear data: FPS weapons and armor sets for Star Citizen."""

# FPS WEAPONS - base variants with their skin/color variants grouped
# Structure: base weapon -> list of variants
# Locations: where to buy or find

FPS_WEAPONS = [
    # === PISTOLS ===
    {"id": "arclight-pistol", "name": "Arclight Pistol", "type": "Pistol", "size": 1, "manufacturer": "Klaus & Werner",
     "damage": 18, "ammo": 30, "fire_rate": "Semi/Burst", "effective_range": "50m",
     "description": "Versatile laser pistol. 30-round battery, single/3-round burst. PvP favorite.",
     "locations": ["Live Fire Weapons (most stations)", "Looted from NPCs"],
     "variants": ["Arclight \"Boneyard\" Pistol", "Arclight \"Nightlife\" Pistol", "Arclight \"Solarflare\" Pistol"]},

    {"id": "lh86-pistol", "name": "LH86 Pistol", "type": "Pistol", "size": 1, "manufacturer": "Kastak Arms",
     "damage": 20, "ammo": 20, "fire_rate": "Full Auto", "effective_range": "30m",
     "description": "Fully automatic ballistic pistol. High rate of fire, good for close combat.",
     "locations": ["Live Fire Weapons (Lorville)", "Live Fire Weapons (ArcCorp)"],
     "variants": ["LH86 \"Blight\" Pistol", "LH86 \"Gunmetal\" Pistol"]},

    {"id": "yubarev-pistol", "name": "Yubarev Pistol", "type": "Pistol", "size": 1, "manufacturer": "Gemini",
     "damage": 22, "ammo": 12, "fire_rate": "Semi-Auto", "effective_range": "45m",
     "description": "High-damage semi-auto ballistic pistol. Reliable sidearm.",
     "locations": ["Live Fire Weapons (most stations)", "Looted from NPCs"],
     "variants": ["Yubarev \"Executive\" Pistol", "Yubarev \"Nightfire\" Pistol"]},

    {"id": "coda-pistol", "name": "Coda Pistol", "type": "Pistol", "size": 1, "manufacturer": "Behring",
     "damage": 30, "ammo": 8, "fire_rate": "Semi-Auto", "effective_range": "55m",
     "description": "Heavy-hitting ballistic pistol. Highest pistol damage per shot.",
     "locations": ["Live Fire Weapons (Port Tressler)", "Live Fire Weapons (Everus Harbor)"],
     "variants": ["Coda \"Dunestalker\" Pistol", "Coda \"Snowblind\" Pistol"]},

    {"id": "vault-pistol", "name": "Vault Pistol", "type": "Pistol", "size": 1, "manufacturer": "Verified Offworld Laser Technologies",
     "damage": 15, "ammo": 40, "fire_rate": "Full Auto (Wind-up)", "effective_range": "35m",
     "description": "Fully automatic laser pistol with wind-up fire rate. Unique mechanic.",
     "locations": ["Live Fire Weapons (CRU-L1)", "Looted from NPCs"],
     "variants": ["Vault \"Rustbucket\" Pistol"]},

    # === SMGs ===
    {"id": "p8-smg", "name": "P8-SMG", "type": "SMG", "size": 1, "manufacturer": "Behring",
     "damage": 16, "ammo": 30, "fire_rate": "Full Auto", "effective_range": "40m",
     "description": "High DPS submachine gun. Meta weapon for CQB. Customizable with attachments.",
     "locations": ["Cutter's Rig (Hurston)", "Live Fire Weapons (most stations)", "Looted from security NPCs"],
     "variants": ["P8-SMG \"Igniter\" SMG", "P8-SMG \"Whiteout\" SMG", "P8-SMG \"Mudskipper\" SMG"]},

    {"id": "ripper-smg", "name": "Ripper SMG", "type": "SMG", "size": 1, "manufacturer": "Verified Offworld Laser Technologies",
     "damage": 12, "ammo": 45, "fire_rate": "Full Auto", "effective_range": "35m",
     "description": "Rapid-fire laser SMG. Large ammo pool, sustained fire capability.",
     "locations": ["Live Fire Weapons (ARC-L1)", "Live Fire Weapons (CRU-L5)"],
     "variants": ["Ripper \"Cobalt\" SMG", "Ripper \"Sandstorm\" SMG"]},

    {"id": "b8-smg", "name": "B8 SMG", "type": "SMG", "size": 1, "manufacturer": "Kastak Arms",
     "damage": 18, "ammo": 25, "fire_rate": "Full Auto", "effective_range": "30m",
     "description": "Close-quarters ballistic SMG. High stopping power at short range.",
     "locations": ["Cutter's Rig (Hurston)", "Looted from outlaws"],
     "variants": ["B8 \"Predator\" SMG", "B8 \"Nightstalker\" SMG"]},

    {"id": "custodian-smg", "name": "Custodian SMG", "type": "SMG", "size": 1, "manufacturer": "Behring",
     "damage": 14, "ammo": 60, "fire_rate": "Full Auto", "effective_range": "45m",
     "description": "Laser SMG with large battery. Good sustained damage output.",
     "locations": ["Live Fire Weapons (Port Olisar)", "Live Fire Weapons (Baijini Point)"],
     "variants": ["Custodian \"Callsign\" SMG", "Custodian \"Rime\" SMG"]},

    # === ASSAULT RIFLES ===
    {"id": "p4-ar", "name": "P4-AR Assault Rifle", "type": "Assault Rifle", "size": 2, "manufacturer": "Behring",
     "damage": 20, "ammo": 40, "fire_rate": "Full Auto/Semi", "effective_range": "65m",
     "description": "Classic ballistic assault rifle. 40-round mag, highly customizable. Best beginner weapon.",
     "locations": ["Live Fire Weapons (all stations)", "Looted from NPCs"],
     "variants": ["P4-AR \"Copperhead\" Assault Rifle", "P4-AR \"Dovetail\" Assault Rifle", "P4-AR \"Mesquite\" Assault Rifle"]},

    {"id": "karna-rifle", "name": "Karna Rifle", "type": "Assault Rifle", "size": 2, "manufacturer": "Kastak Arms",
     "damage": 25, "ammo": 60, "fire_rate": "Full Auto", "effective_range": "60m",
     "description": "Powerful laser assault rifle. Strong for PvE and PvP.",
     "locations": ["Live Fire Weapons (Lorville)", "Live Fire Weapons (CRU-L4)"],
     "variants": ["Karna \"Stinger\" Rifle", "Karna \"Ashfall\" Rifle"]},

    {"id": "parallax-ar", "name": "Parallax Assault Rifle", "type": "Assault Rifle", "size": 2, "manufacturer": "Verified Offworld Laser Technologies",
     "damage": 18, "ammo": 45, "fire_rate": "Full Auto", "effective_range": "70m",
     "description": "Versatile medium/long range laser assault rifle.",
     "locations": ["Live Fire Weapons (New Babbage)", "Live Fire Weapons (Area 18)"],
     "variants": ["Parallax \"Stalker\" Assault Rifle", "Parallax \"Tundra\" Assault Rifle"]},

    {"id": "c54-smg", "name": "C54 SMG", "type": "Assault Rifle", "size": 2, "manufacturer": "Kastak Arms",
     "damage": 22, "ammo": 30, "fire_rate": "Full Auto/Burst", "effective_range": "55m",
     "description": "Compact ballistic assault weapon. Good balance of damage and handling.",
     "locations": ["Live Fire Weapons (Grim HEX)", "Looted from outlaws"],
     "variants": ["C54 \"Bloodline\" SMG"]},

    {"id": "s71-rifle", "name": "S71 Rifle", "type": "Assault Rifle", "size": 2, "manufacturer": "Behring",
     "damage": 30, "ammo": 20, "fire_rate": "Semi-Auto", "effective_range": "80m",
     "description": "Semi-auto marksman rifle. High damage per shot, preferred for long range.",
     "locations": ["Cutter's Rig (Hurston)", "Live Fire Weapons (HUR-L1)"],
     "variants": ["S71 \"Wildfire\" Rifle", "S71 \"Frostbite\" Rifle"]},

    # === LMGs ===
    {"id": "f55-lmg", "name": "F55 LMG", "type": "LMG", "size": 3, "manufacturer": "Behring",
     "damage": 20, "ammo": 100, "fire_rate": "Full Auto (Gatling)", "effective_range": "50m",
     "description": "Handheld ballistic gatling gun. Extreme suppression capability.",
     "locations": ["Live Fire Weapons (Lorville)", "Live Fire Weapons (CRU-L4)"],
     "variants": ["F55 \"Nighthawk\" LMG", "F55 \"Sandstorm\" LMG"]},

    {"id": "fs9-lmg", "name": "FS-9 LMG", "type": "LMG", "size": 3, "manufacturer": "Kastak Arms",
     "damage": 22, "ammo": 80, "fire_rate": "Full Auto", "effective_range": "55m",
     "description": "Heavy ballistic LMG. Great for group combat.",
     "locations": ["Cutter's Rig (Hurston)", "Looted from NPCs"],
     "variants": ["FS-9 \"Bushwhacker\" LMG"]},

    {"id": "demeco-lmg", "name": "Demeco LMG", "type": "LMG", "size": 3, "manufacturer": "Verified Offworld Laser Technologies",
     "damage": 16, "ammo": 165, "fire_rate": "Full Auto", "effective_range": "55m",
     "description": "Laser LMG with massive battery. Sustained suppressive fire.",
     "locations": ["Live Fire Weapons (CRU-L5)", "Live Fire Weapons (ARC-L2)"],
     "variants": ["Demeco \"Redline\" LMG", "Demeco \"Whiteout\" LMG"]},

    # === SHOTGUNS ===
    {"id": "ravager-shotgun", "name": "Ravager-212 Shotgun", "type": "Shotgun", "size": 2, "manufacturer": "Apocalypse Arms",
     "damage": 80, "ammo": 8, "fire_rate": "Pump-Action", "effective_range": "15m",
     "description": "Devastating pump-action shotgun. One-shot potential at close range.",
     "locations": ["Live Fire Weapons (Grim HEX)", "Looted from outlaws"],
     "variants": ["Ravager-212 \"Brawler\" Shotgun", "Ravager-212 \"Rustbucket\" Shotgun"]},

    {"id": "br2-shotgun", "name": "BR-2 Shotgun", "type": "Shotgun", "size": 2, "manufacturer": "Behring",
     "damage": 60, "ammo": 6, "fire_rate": "Semi-Auto", "effective_range": "20m",
     "description": "Semi-automatic shotgun. Good for rapid follow-up shots.",
     "locations": ["Live Fire Weapons (Lorville)", "Live Fire Weapons (Area 18)"],
     "variants": ["BR-2 \"Copperhead\" Shotgun", "BR-2 \"Nighthawk\" Shotgun"]},

    {"id": "scalpel-shotgun", "name": "Scalpel Shotgun", "type": "Shotgun", "size": 2, "manufacturer": "Verified Offworld Laser Technologies",
     "damage": 45, "ammo": 20, "fire_rate": "Semi-Auto", "effective_range": "25m",
     "description": "Laser shotgun with tighter spread. More range than ballistic shotguns.",
     "locations": ["Live Fire Weapons (New Babbage)", "Live Fire Weapons (Port Tressler)"],
     "variants": ["Scalpel \"Ember\" Shotgun", "Scalpel \"Glacier\" Shotgun"]},

    # === SNIPER RIFLES ===
    {"id": "arrowhead-sniper", "name": "Arrowhead Sniper Rifle", "type": "Sniper Rifle", "size": 3, "manufacturer": "Klaus & Werner",
     "damage": 80, "ammo": 8, "fire_rate": "Bolt-Action", "effective_range": "200m",
     "description": "Long-range sniper rifle. Community favorite for precision engagements.",
     "locations": ["Live Fire Weapons (New Babbage)", "Live Fire Weapons (HUR-L5)"],
     "variants": ["Arrowhead \"Copperhead\" Sniper", "Arrowhead \"Thunderstrike\" Sniper"]},

    {"id": "p6-lr-sniper", "name": "P6-LR Sniper Rifle", "type": "Sniper Rifle", "size": 3, "manufacturer": "Behring",
     "damage": 100, "ammo": 5, "fire_rate": "Bolt-Action", "effective_range": "250m",
     "description": "50-cal ballistic sniper. 8x scope + rangefinder. Highest FPS damage.",
     "locations": ["Live Fire Weapons (Port Tressler)", "Live Fire Weapons (CRU-L1)"],
     "variants": ["P6-LR \"Ghost\" Sniper Rifle"]},

    {"id": "a03-sniper", "name": "A03 Sniper Rifle", "type": "Sniper Rifle", "size": 3, "manufacturer": "Gemini",
     "damage": 42, "ammo": 15, "fire_rate": "Semi-Auto", "effective_range": "150m",
     "description": "Semi-auto sniper with larger magazine. Good for follow-up shots.",
     "locations": ["Live Fire Weapons (Baijini Point)", "Live Fire Weapons (ARC-L1)"],
     "variants": ["A03 \"Canuto\" Sniper Rifle", "A03 \"Red Alert\" Sniper Rifle", "A03 \"Wildwood\" Sniper Rifle"]},

    # === RAILGUNS ===
    {"id": "deadrig-railgun", "name": "Deadrig Railgun", "type": "Railgun", "size": 4, "manufacturer": "Kastak Arms",
     "damage": 150, "ammo": 3, "fire_rate": "Charge", "effective_range": "300m",
     "description": "Electromagnetic railgun. Charges before firing. Extreme damage.",
     "locations": ["Grim HEX", "Looted from bunker bosses"],
     "variants": ["Deadrig \"Extinction\" Railgun"]},

    # === GRENADE LAUNCHERS ===
    {"id": "gp33-launcher", "name": "GP-33 Grenade Launcher", "type": "Grenade Launcher", "size": 3, "manufacturer": "Behring",
     "damage": 120, "ammo": 6, "fire_rate": "Semi-Auto", "effective_range": "80m",
     "description": "Six-round grenade launcher. Area denial and group damage.",
     "locations": ["Grim HEX", "Looted from bunker enemies"],
     "variants": ["GP-33 \"Copperhead\" Launcher"]},

    # === MISSILE LAUNCHERS ===
    {"id": "animus-launcher", "name": "Animus Missile Launcher", "type": "Missile Launcher", "size": 5, "manufacturer": "Apocalypse Arms",
     "damage": 150, "ammo": 1, "fire_rate": "Single-Shot", "effective_range": "200m",
     "description": "Shoulder-mounted missile launcher. Anti-vehicle capability.",
     "locations": ["Grim HEX", "Rare loot drop"],
     "variants": ["Animus \"Quite Useful\" Missile Launcher"]},

    # === MEDICAL ===
    {"id": "medgun", "name": "MedGun", "type": "Medical Device", "size": 1, "manufacturer": "CureLife",
     "damage": 0, "ammo": 100, "fire_rate": "Continuous", "effective_range": "5m",
     "description": "Medical healing device. Essential for team play.",
     "locations": ["Medical supply vendors (all stations)", "Pharmacy (Orison, New Babbage)"],
     "variants": ["MedGun Mk II", "MedGun \"Lifeline\""]},

    {"id": "multitool", "name": "Multi-Tool", "type": "Medical Device", "size": 1, "manufacturer": "Greycat Industrial",
     "damage": 0, "ammo": 0, "fire_rate": "N/A", "effective_range": "3m",
     "description": "Versatile utility tool. Healing, cutting, tractor beam with attachments.",
     "locations": ["Most station shops", "Cargo Decks"],
     "variants": []},

    # === GRENADES ===
    {"id": "frag-grenade", "name": "Frag Grenade", "type": "Grenade", "size": 0, "manufacturer": "Behring",
     "damage": 200, "ammo": 1, "fire_rate": "Throw", "effective_range": "30m",
     "description": "Standard fragmentation grenade. Lethal in enclosed spaces. 3.5s fuse.",
     "locations": ["Live Fire Weapons (most stations)", "Looted from NPCs"],
     "variants": []},

    {"id": "flash-grenade", "name": "Flash Grenade", "type": "Grenade", "size": 0, "manufacturer": "Behring",
     "damage": 0, "ammo": 1, "fire_rate": "Throw", "effective_range": "20m",
     "description": "Flashbang. Blinds and disorients enemies. Essential for breaching.",
     "locations": ["Live Fire Weapons (most stations)", "Looted from security NPCs"],
     "variants": []},

    {"id": "smoke-grenade", "name": "Smoke Grenade", "type": "Grenade", "size": 0, "manufacturer": "Behring",
     "damage": 0, "ammo": 1, "fire_rate": "Throw", "effective_range": "25m",
     "description": "Deploys thick smoke screen. Blocks line of sight for 15s.",
     "locations": ["Live Fire Weapons (Lorville)", "Live Fire Weapons (Area 18)"],
     "variants": []},

    {"id": "emp-grenade", "name": "EMP Grenade", "type": "Grenade", "size": 0, "manufacturer": "Kastak Arms",
     "damage": 0, "ammo": 1, "fire_rate": "Throw", "effective_range": "15m",
     "description": "Electromagnetic pulse grenade. Disables electronics and shields temporarily.",
     "locations": ["Grim HEX", "Rare loot from bunker bosses"],
     "variants": []},

    # === UTILITIES ===
    {"id": "medpen", "name": "MedPen", "type": "Utility", "size": 0, "manufacturer": "CureLife",
     "damage": 0, "ammo": 1, "fire_rate": "Inject", "effective_range": "Self",
     "description": "Emergency medical injector. Heals minor wounds and stops bleeding. Stackable.",
     "locations": ["Medical supply vendors (all stations)", "Pharmacy (Orison, New Babbage)", "Looted from NPCs"],
     "variants": ["MedPen Mk II"]},

    {"id": "oxypen", "name": "OxyPen", "type": "Utility", "size": 0, "manufacturer": "CureLife",
     "damage": 0, "ammo": 1, "fire_rate": "Inject", "effective_range": "Self",
     "description": "Oxygen supplement injector. Restores O2 in emergency situations.",
     "locations": ["Medical supply vendors (all stations)", "Pharmacy"],
     "variants": []},

    {"id": "adrenapen", "name": "AdrenaPen", "type": "Utility", "size": 0, "manufacturer": "CureLife",
     "damage": 0, "ammo": 1, "fire_rate": "Inject", "effective_range": "Self",
     "description": "Adrenaline injector. Temporarily boosts stamina and reduces pain effects.",
     "locations": ["Pharmacy (Orison, New Babbage)", "Medical vendors"],
     "variants": []},

    {"id": "tractor-beam-tool", "name": "Tractor Beam (Multi-Tool)", "type": "Utility", "size": 0, "manufacturer": "Greycat Industrial",
     "damage": 0, "ammo": 0, "fire_rate": "Continuous", "effective_range": "10m",
     "description": "Multi-tool tractor beam attachment. Move cargo boxes and small objects.",
     "locations": ["Cargo Decks (all stations)", "Most station shops"],
     "variants": []},

    {"id": "cutting-tool", "name": "Cutting Tool (Multi-Tool)", "type": "Utility", "size": 0, "manufacturer": "Greycat Industrial",
     "damage": 0, "ammo": 0, "fire_rate": "Continuous", "effective_range": "1m",
     "description": "Multi-tool cutting attachment. Breach locked doors and panels.",
     "locations": ["Cargo Decks (all stations)", "Hardware shops"],
     "variants": []},

    {"id": "repair-tool", "name": "Repair Tool (Multi-Tool)", "type": "Utility", "size": 0, "manufacturer": "Greycat Industrial",
     "damage": 0, "ammo": 0, "fire_rate": "Continuous", "effective_range": "3m",
     "description": "Multi-tool repair attachment. Fix damaged ship components in the field.",
     "locations": ["Cargo Decks (all stations)", "Ship component shops"],
     "variants": []},
]


# PERSONAL ARMOR - base sets with variants (color schemes)
ARMOR_SETS = [
    # === HEAVY ARMOR ===
    {"id": "adp-heavy", "name": "ADP", "type": "Heavy", "manufacturer": "Clark Defense Systems",
     "temp_max": 105, "temp_min": -75, "radiation": 26800,
     "description": "Heavy combat armor. Excellent protection and environmental resistance.",
     "locations": ["Distribution Centers (all)", "Armor shops (Lorville, Area 18)"],
     "loot_locations": ["Bunker missions", "Distribution Centers"],
     "variants": ["ADP Stormcloud", "ADP Desert"]},

    {"id": "adp-mk4-heavy", "name": "ADP-mk4", "type": "Heavy", "manufacturer": "Clark Defense Systems",
     "temp_max": 100, "temp_min": -70, "radiation": 26800,
     "description": "Upgraded ADP variant. Found in contested zones. Rare.",
     "locations": ["Pyro One contested zones", "High-security bunkers"],
     "loot_locations": ["Pyro I", "Xenomorph encounter zones"],
     "variants": ["ADP-mk4 Desert Storm", "ADP-mk4 Snow"]},

    {"id": "antium-heavy", "name": "Antium", "type": "Heavy", "manufacturer": "Quirinus Tech",
     "temp_max": 120, "temp_min": -95, "radiation": 26800,
     "description": "Best environmental resistance of all heavy armors. Exploration-grade.",
     "locations": ["Dumper's Depot (New Babbage)", "Armor shops (Orison)"],
     "loot_locations": ["Cave exploration sites"],
     "variants": ["Antium Cobalt", "Antium Ember"]},

    {"id": "citadel-heavy", "name": "Citadel", "type": "Heavy", "manufacturer": "Kastak Arms",
     "temp_max": 100, "temp_min": -80, "radiation": 26800,
     "description": "Combat-focused heavy armor. Distinctive angular design.",
     "locations": ["ASD Facilities (Pyro)", "Crusader Security loot"],
     "loot_locations": ["ASD Facilities", "Security bunkers"],
     "variants": ["Citadel Ash", "Citadel Crimson"]},

    {"id": "corbel-heavy", "name": "Corbel", "type": "Heavy", "manufacturer": "Odin Munitions",
     "temp_max": 100, "temp_min": -70, "radiation": 26800,
     "description": "Rugged heavy armor designed for sustained ground operations.",
     "locations": ["Armor shops (Lorville)", "Distribution Centers"],
     "loot_locations": ["Ground bunker missions"],
     "variants": ["Corbel Dustwalker", "Corbel Nightwatch"]},

    {"id": "defiance-heavy", "name": "Defiance", "type": "Heavy", "manufacturer": "Clark Defense Systems",
     "temp_max": 102, "temp_min": -72, "radiation": 26800,
     "description": "Premium heavy armor with enhanced protection.",
     "locations": ["Subscriber rewards", "Rare loot"],
     "loot_locations": ["High-threat bunkers"],
     "variants": ["Defiance Sandstorm", "Defiance Arctic"]},

    {"id": "morozov-sh-heavy", "name": "Morozov-SH", "type": "Heavy", "manufacturer": "Roussimoff",
     "temp_max": 105, "temp_min": -75, "radiation": 26800,
     "description": "Crusader Security heavy armor. Distinct blue/white markings.",
     "locations": ["ASD Facilities", "Looted from Crusader Security NPCs"],
     "loot_locations": ["ASD Facilities", "Crusader security zones"],
     "variants": ["Morozov-SH Desert", "Morozov-SH Arctic"]},

    {"id": "overlord-heavy", "name": "Overlord", "type": "Heavy", "manufacturer": "Doomsday",
     "temp_max": 100, "temp_min": -70, "radiation": 26800,
     "description": "Intimidating heavy armor with skull motif. Popular with outlaws.",
     "locations": ["Grim HEX", "Subscription exclusive variants"],
     "loot_locations": ["Outlaw bunkers"],
     "variants": ["Overlord Dust Storm", "Overlord Nightstalker", "Overlord Rime"]},

    {"id": "palatino-heavy", "name": "Palatino", "type": "Heavy", "manufacturer": "Quirinus Tech",
     "temp_max": 100, "temp_min": -70, "radiation": 26800,
     "description": "Widely available heavy armor. Found at all distribution centers.",
     "locations": ["All Distribution Centers", "Armor shops (all landing zones)"],
     "loot_locations": ["Distribution Centers"],
     "variants": ["Palatino Forest", "Palatino Desert"]},

    # === MEDIUM ARMOR ===
    {"id": "artimex-medium", "name": "Artimex", "type": "Medium", "manufacturer": "Clark Defense Systems",
     "temp_max": 85, "temp_min": -55, "radiation": 26400,
     "description": "Balanced medium armor. Good mix of protection and mobility.",
     "locations": ["Armor shops (most stations)", "Distribution Centers"],
     "loot_locations": ["Bunker missions"],
     "variants": ["Artimex Ash", "Artimex Cobalt"]},

    {"id": "aril-medium", "name": "Aril", "type": "Medium", "manufacturer": "Quirinus Tech",
     "temp_max": 88, "temp_min": -58, "radiation": 26400,
     "description": "Medium exploration armor with good environmental protection.",
     "locations": ["Dumper's Depot (New Babbage)", "Cargo Decks (most stations)"],
     "loot_locations": ["Mining outposts"],
     "variants": ["Aril Snow", "Aril Forest"]},

    {"id": "aves-medium", "name": "Aves", "type": "Medium", "manufacturer": "Kastak Arms",
     "temp_max": 82, "temp_min": -52, "radiation": 26400,
     "description": "Combat-oriented medium armor. Favored by bounty hunters.",
     "locations": ["Armor shops (Lorville)", "Grim HEX"],
     "loot_locations": ["Bounty hunt targets"],
     "variants": ["Aves Midnight", "Aves Sandstorm"]},

    {"id": "novikov-medium", "name": "Novikov", "type": "Medium", "manufacturer": "Odin Munitions",
     "temp_max": 95, "temp_min": -65, "radiation": 26400,
     "description": "Exploration suit with excellent cold protection. Popular for microTech.",
     "locations": ["Hatter Station", "New Babbage shops"],
     "loot_locations": ["microTech surface missions"],
     "variants": ["Novikov Amber", "Novikov Polar"]},

    {"id": "lynx-medium", "name": "Lynx", "type": "Medium", "manufacturer": "Behring",
     "temp_max": 80, "temp_min": -50, "radiation": 26400,
     "description": "Tactical medium armor. Good for all-around combat operations.",
     "locations": ["Armor shops (most stations)"],
     "loot_locations": ["General NPC loot"],
     "variants": ["Lynx Ranger", "Lynx Shadow"]},

    # === LIGHT ARMOR ===
    {"id": "arden-sl-light", "name": "Arden-SL", "type": "Light", "manufacturer": "Roussimoff",
     "temp_max": 68, "temp_min": -38, "radiation": 26800,
     "description": "Light security armor. Minimal protection, maximum mobility.",
     "locations": ["Armor shops (most stations)", "Cargo Decks"],
     "loot_locations": ["Security NPC drops"],
     "variants": ["Arden-SL Blue", "Arden-SL White"]},

    {"id": "aztalan-light", "name": "Aztalan", "type": "Light", "manufacturer": "Tehachapi",
     "temp_max": 68, "temp_min": -38, "radiation": 26000,
     "description": "Lightweight stealth-oriented armor. Low profile design.",
     "locations": ["Armor shops (Area 18)", "Grim HEX"],
     "loot_locations": ["Outlaw bunkers"],
     "variants": ["Aztalan Night", "Aztalan Desert"]},

    {"id": "calico-light", "name": "Calico", "type": "Light", "manufacturer": "Kastak Arms",
     "temp_max": 69, "temp_min": -39, "radiation": 26000,
     "description": "Agile light combat armor. Designed for fast-movers.",
     "locations": ["Armor shops (Lorville)", "Live Fire Weapons"],
     "loot_locations": ["Ground combat zones"],
     "variants": ["Calico Crimson", "Calico Midnight"]},

    {"id": "fbl-8a-light", "name": "FBL-8a", "type": "Light", "manufacturer": "Clark Defense Systems",
     "temp_max": 65, "temp_min": -35, "radiation": 26000,
     "description": "Standard light combat armor. Widely available and affordable.",
     "locations": ["Armor shops (all landing zones)"],
     "loot_locations": ["General NPC drops"],
     "variants": ["FBL-8a Forest", "FBL-8a Urban"]},

    {"id": "sterling-light", "name": "Sterling", "type": "Light", "manufacturer": "Quirinus Tech",
     "temp_max": 70, "temp_min": -40, "radiation": 26000,
     "description": "Exploration light armor. Better environmental stats than most light sets.",
     "locations": ["Pyro One", "Larger loot locations"],
     "loot_locations": ["Pyro I facilities", "Exploration sites"],
     "variants": ["Sterling Explorer", "Sterling Ranger"]},

    # === FLIGHT SUITS ===
    {"id": "odyssey-ii-flight", "name": "Odyssey II", "type": "Flight Suit", "manufacturer": "RSI",
     "temp_max": 70, "temp_min": -40, "radiation": 15200,
     "description": "Standard RSI flight suit. Starter equipment for most pilots.",
     "locations": ["All station clothing shops", "Default starter gear"],
     "loot_locations": [],
     "variants": ["Odyssey II Red", "Odyssey II Blue", "Odyssey II Black"]},

    {"id": "sol-iii-flight", "name": "Sol-III", "type": "Flight Suit", "manufacturer": "UEE Navy",
     "temp_max": 60, "temp_min": -30, "radiation": 15200,
     "description": "Military flight suit. UEE Navy standard issue.",
     "locations": ["Military surplus shops", "Looted from UEE Navy NPCs"],
     "loot_locations": ["UEE naval vessels"],
     "variants": ["Sol-III Olive", "Sol-III Grey"]},
]


def get_all_fps_weapons():
    return FPS_WEAPONS

def get_all_armor_sets():
    return ARMOR_SETS
