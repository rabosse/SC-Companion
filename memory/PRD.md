# Star Citizen Fleet Manager (Companion) - PRD

## Original Problem Statement
Build a full-stack application called "Star Citizen Fleet Manager" / "Star Citizen Companion" for players to track ships, ground vehicles, components, weapons, and personal gear from Star Citizen.

## Core Requirements
- User authentication (Username/Password)
- Fleet management (add/remove ships, quick import)
- Ship, vehicle, component, and weapon data pages
- Detailed item information with stock vs upgrade comparison
- Ship comparison tool
- Loadout builder with savable/shareable loadouts
- Dashboard with fleet statistics
- Route planner for Stanton, Pyro, Nyx systems
- Interdiction planner
- Personal gear section (FPS weapons, armor, equipment)
- Real-time price tracking
- Data from Star Citizen Wiki API + CStone API

## Architecture
- **Frontend**: React, Tailwind CSS, Shadcn UI, react-router-dom, axios, lucide-react, framer-motion
- **Backend**: FastAPI, Pydantic, JWT auth, modular routing (APIRouter)
- **Database**: MongoDB
- **External APIs**: starcitizen.tools (wiki), finder.cstone.space (CStone armor/weapon/gadget data)

## Backend Module Structure (Refactored Mar 2026)
```
/app/backend/
├── server.py                # Main FastAPI app, startup events
├── armor_enhancer.py        # CStone + Wiki images for armor sets (55 sets)
├── weapon_enhancer.py       # CStone + Wiki images for FPS weapons (50 weapons)
├── equipment_enhancer.py    # CStone gadget images for equipment (30 items)
├── ship_data_enhancer.py    # Wiki images for ships/vehicles (re-exports from above)
├── personal_gear.py         # Static data for armor, weapons, equipment
├── routes/
│   ├── gear.py              # /api/gear/* endpoints
│   ├── auth.py, fleet.py, ships.py, loadouts.py, etc.
```

## Key DB Schema
- **users**: `{username, email, password_hash, fleet: [str]}`
- **saved_loadouts**: `{user_id, ship_id, loadout_name, components, is_public, share_code}`
- **price_history**: `{item_id, item_type, snapshots: [dict]}`

## What's Been Implemented
- User authentication (register/login)
- Fleet management with Quick Import
- Ships, Vehicles, Components, Weapons pages
- Ship Comparison tool
- Loadout Builder with sharing
- Route Planner (Stanton, Pyro, Nyx) with interdiction/chase modes
- Dashboard with fleet overview and total value
- Price Tracker page
- Personal Gear section - ALL 3 tabs fully integrated:
  - **Armor tab**: 55 sets (28 original + 27 new from CStone) with CStone images, variant data, loot locations
  - **Weapons tab**: 50 weapons with CStone images, per-variant pricing/locations/loot data
  - **Equipment tab**: 30 items with CStone images (medical items), variant selectors
- Backend refactored into modular enhancer files

## Completed (Mar 2026 - This Session)
1. FPS Weapons tab CStone integration (feature parity with Armor)
2. Equipment tab CStone integration (GetGadgets API for medical items)
3. Refactored ship_data_enhancer.py into 4 focused modules
4. Added 27 missing armor sets from CStone:
   - Heavy: Ana, Bokto, Citadel-SE, DCP Armor, Dust Devil, Dust Devil Armor, Morozov-SH-I, Wrecker
   - Medium: Aves Shrike/Starchaser/Talon, Carrion, Clash, DustUp, GCD-Army, Stitcher, Strata (12 vars), Testudo (7 vars)
   - Light: Aztalan Galena/Tamarack, Carnifex, Carnifex Armor, Chiron, Field Recon Suit, Geist Armor (8 vars), Microid Battle Suit (5 vars), Piecemeal Armor
5. Fixed base image fallback for sets without "Base" CStone variant
6. All tests passed: iterations 17 (100%), 18 (100%), 19 (100%)

## Backlog
- P2: Price change alerts for fleet ships
- P3: Wiki image integration for equipment without CStone coverage
- P3: Community loadout voting/rating system
- P3: Fleet value tracking over time (historical charts)
