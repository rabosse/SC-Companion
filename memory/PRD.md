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
- **External APIs**: starcitizen.tools (wiki), finder.cstone.space (CStone armor data)

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
  - 28 armor sets with images from Wiki + CStone APIs
  - 136/153 variants with unique images (89% coverage)
  - Per-variant acquisition data (sold status, price, specific loot locations)
  - Dynamic image, price, and location swapping on variant selection
  - Detail modal with clickable variant buttons
  - Loot-only variants show "LOOT ONLY" + specific farm locations
- Hide-on-scroll header, "Star Citizen Companion" branding

## Completed (Latest Session - Mar 2026)
1. Added 7 missing armor sets (ORC-mkX, ORC-mkV, MacFlex, Venture, Inquisitor, TrueDef-Pro, PAB-1)
2. Integrated CStone API (finder.cstone.space) for comprehensive armor variant images
3. Updated all variant names to match wiki/CStone naming for accurate image matching
4. Implemented variant-specific image swapping on card dropdown and modal buttons
5. Added per-variant acquisition data (sold status from CStone, prices, locations)
6. Added specific loot locations per armor set (ASD facilities, bunkers, outposts, etc.)
7. Frontend shows "LOOT ONLY" badge + specific farm locations for non-purchasable variants

## Backlog
- Price change alerts for fleet ships
- Refactor ship_data_enhancer.py into smaller modules
- Add more armor sets from CStone (27 additional sets available)
