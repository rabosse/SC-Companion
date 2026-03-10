# Star Citizen Fleet Manager - PRD

## Original Problem Statement
Build a full-stack "Star Citizen Fleet Manager" application allowing players to track ships, ground vehicles, components, weapons, and personal gear from Star Citizen. The app must use accurate game data from `finder.cstone.space` as the primary source of truth.

## Core Requirements
- User authentication (Username/Password) with fleet management
- Ship/vehicle catalog with accurate stats from CStone Finder
- Component catalog with Class filtering (Military, Civilian, Industrial, Stealth, Competition)
- Ship weapons, FPS weapons, armor, and equipment data
- Ship comparison tool, loadout builder with savable/shareable loadouts
- Route planner with starmap, interdiction planner
- Fleet dashboard with stats, saved loadouts, manufacturer breakdown
- Purchase locations and prices from CStone Finder
- Real-time price tracking for in-game items

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, Framer Motion
- **Backend**: FastAPI, Pydantic, JWT auth, bcrypt
- **Database**: MongoDB
- **Data Source**: finder.cstone.space (primary), starcitizen.tools (ship images/basic info)

## Architecture
```
/app/backend/
  cstone_api.py         - CStone Finder JSON API integration (primary data source)
  live_api.py           - Legacy starcitizen.tools API (ship info, images)
  server.py             - FastAPI app with startup prefetch
  star_systems.py       - Starmap data, route/interdiction/chase calculations
  ship_purchases.py     - Ship purchase info (dealers, prices)
  routes/
    ships.py            - /api/ships, /api/components, /api/weapons, /api/missiles, /api/item-locations
    gear.py             - /api/gear/weapons, /api/gear/armor, /api/gear/equipment
    fleet.py            - /api/fleet/add, /api/fleet/my, /api/fleet/{id}
    auth.py             - /api/auth/login, /api/auth/register
    loadouts.py         - /api/loadouts/*
    starmap.py          - /api/routes/locations, /api/routes/calculate, /api/routes/interdiction, /api/routes/chase/*
    prices.py           - /api/prices/summary, /api/prices/snapshot, /api/prices/changes, /api/prices/history/*

/app/frontend/src/pages/
  Dashboard.jsx         - Fleet overview with stats, quick actions, ship cards
  Components.jsx        - Component catalog with Class/Grade filters + sort
  PriceTracker.jsx      - Price tracking with current prices, changes, search, filters
  Ships.jsx, Vehicles.jsx, Weapons.jsx, PersonalGear.jsx, ShipDetail.jsx
  Fleet.jsx, RoutePlanner.jsx (Route/Interdiction/Chase tabs), etc.
```

## What's Been Implemented

### CStone Finder Data Integration (March 2026) - COMPLETE
- Created `cstone_api.py` with all CStone JSON API endpoints
- 270 vehicle components, 146 ship weapons, 65 missiles
- FPS weapons and armor stats merged from CStone
- Item purchase locations fetched from CStone detail pages
- Data cached in-memory with 1-hour TTL

### Ship & Vehicle Data Migration (March 2026) - COMPLETE (P0)
- Hybrid data strategy merging CStone + Wiki API data
- All ship/vehicle endpoints serve merged, accurate data
- Backend pre-caches ship purchase locations on startup

### Route Planner Validation (March 2026) - COMPLETE (P3)
- Route, Interdiction, and Chase tabs all functional
- Tested 100% (35/35 backend, all frontend flows)

### Price Tracker (March 2026) - COMPLETE (P1)
- 496 tracked items (239 ships, 82 weapons, 175 components)
- Deduplicated snapshot creation (no duplicate entries)
- All items shown (removed 50-item per-category cap)
- Current Prices and Price Changes tabs with search + type filters
- New Snapshot button for manual price capture
- Price history per item endpoint
- Automated snapshot on server startup
- Tested 100% (21/21 backend, all frontend flows)

### Dashboard Redesign (March 2026) - COMPLETE
- Simplified fleet stats, quick actions, ship cards with filters/sort

### Components Page Enhancement (March 2026) - COMPLETE
- Sort by Class (Military, Civilian, etc.) with ascending/descending toggle

### Previously Completed
- User authentication (JWT), Fleet management
- Ship comparison tool, Loadout builder with save/share
- Personal gear pages, Ship detail pages

## Prioritized Backlog

### P2 - RSI Fleet Import (de-prioritized by user)
- Import fleet from RSI account

### P3 - Full Re-validation
- Complete app-wide validation after all features done
