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
- **External APIs**: starcitizen.tools (wiki), finder.cstone.space (CStone armor/weapon data)

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
- Personal Gear section (FPS Weapons, Armor Sets, Equipment)
  - **Armor tab**: 28 sets with CStone images, per-variant pricing/locations/loot data
  - **Weapons tab**: 50 weapons with CStone images, per-variant pricing/locations/loot data (COMPLETED Mar 2026)
  - **Equipment tab**: 30 items with clickable cards and detail modals
  - All 3 tabs share identical functionality: variant selectors, dynamic image/price/location updates, LOOT ONLY badges, detail modals with clickable variant buttons
- Hide-on-scroll header, "Star Citizen Companion" branding

## Completed (Mar 2026 - Latest Session)
1. Completed CStone API integration for FPS Weapons tab (feature parity with Armor)
2. Weapon cards now show CStone variant images, dynamic pricing, LOOT ONLY badges
3. Weapon variant selectors update card title, image, price, and Buy/Loot locations
4. GearDetailModal now supports both armor AND weapon variant interaction
5. Equipment cards made clickable with detail modal showing stats and locations
6. All 3 Gear tabs verified with 100% test pass rate (iteration 17)

## Backlog
- P0: CStone Integration for Equipment tab (variant images if CStone adds equipment endpoints)
- P2: Refactor ship_data_enhancer.py into smaller modules (armor_enhancer.py, weapon_enhancer.py)
- P2: Price change alerts for fleet ships
- P2: Add more armor sets from CStone (27 additional sets available)
