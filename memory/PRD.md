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
├── armor_enhancer.py        # CStone + Wiki images for armor sets
├── weapon_enhancer.py       # CStone + Wiki images for FPS weapons
├── equipment_enhancer.py    # CStone gadget images for equipment
├── ship_data_enhancer.py    # Wiki images for ships/vehicles (re-exports from above)
├── personal_gear.py         # Static data for armor, weapons, equipment
├── routes/
│   ├── gear.py              # /api/gear/* endpoints (weapons, armor, equipment)
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
  - **Armor tab**: 28 sets with CStone images, per-variant pricing/locations/loot data
  - **Weapons tab**: 50 weapons with CStone images, per-variant pricing/locations/loot data
  - **Equipment tab**: 30 items with CStone images (medical items), image thumbnails, variant selectors, detail modals with stats
- Hide-on-scroll header, "Star Citizen Companion" branding

## Completed (Mar 2026 - Latest Session)
1. Completed CStone API integration for FPS Weapons tab (feature parity with Armor)
2. Completed CStone API integration for Equipment tab (GetGadgets endpoint for medical items)
3. Refactored ship_data_enhancer.py (805 lines) into 4 focused modules:
   - armor_enhancer.py, weapon_enhancer.py, equipment_enhancer.py, ship_data_enhancer.py (ships only)
4. EquipmentCard upgraded with image thumbnails, variant selectors, clickable detail modals
5. GearDetailModal extended to support all 3 item types (armor, weapons, equipment)
6. All tests passed: iteration 17 (100%), iteration 18 (100% - 19 backend + all frontend)

## Backlog
- P2: Add more armor sets from CStone (27 additional sets available)
- P2: Price change alerts for fleet ships
- P3: Wiki image integration for equipment items without CStone coverage (mining tools, backpacks)
