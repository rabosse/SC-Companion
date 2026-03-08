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
  routes/
    ships.py            - /api/ships, /api/components, /api/weapons, /api/missiles, /api/item-locations
    gear.py             - /api/gear/weapons, /api/gear/armor, /api/gear/equipment
    fleet.py            - /api/fleet/add, /api/fleet/my, /api/fleet/{id}
    auth.py             - /api/auth/login, /api/auth/register
    loadouts.py         - /api/loadouts/*
    starmap.py          - /api/starmap/*, /api/chase

/app/frontend/src/pages/
  Dashboard.jsx         - Fleet overview with stats, quick actions, ship cards
  Components.jsx        - Component catalog with Class/Grade filters + sort
  Ships.jsx, Vehicles.jsx, Weapons.jsx, PersonalGear.jsx, ShipDetail.jsx
  Fleet.jsx, RoutePlanner.jsx, etc.
```

## What's Been Implemented

### CStone Finder Data Integration (March 2026) - COMPLETE
- Created `cstone_api.py` with all CStone JSON API endpoints
- 270 vehicle components (coolers, power plants, quantum drives, shields)
- 146 ship weapons with accurate DPS, damage, fire rate, range
- 65 missiles with damage and speed data
- FPS weapons stats merged from CStone into curated entries
- Armor stats merged from CStone
- Item purchase locations fetched from CStone detail pages
- Data cached in-memory with 1-hour TTL

### Dashboard Redesign (March 2026) - COMPLETE
- Simplified fleet stats (Ships, Vehicles, Loadouts, Manufacturers)
- Quick Actions moved to horizontal row above fleet
- Ship cards with images, size tags, component/weapon summary, MANAGE button
- Filter tabs (All/Ships/Land) + sort by Name/Size
- Saved Loadouts + Favorite Manufacturer sections

### Components Page Enhancement (March 2026) - COMPLETE
- Sort by Class dropdown (Military, Civilian, Industrial, Stealth, Competition)
- Ascending/Descending toggle
- CStone data with real Class field (not derived from Grade)

### Previously Completed
- User authentication (JWT)
- Fleet management (add/remove ships)
- Ship comparison tool
- Loadout builder with save/share
- Route planner with starmap
- Interdiction/Chase planner
- Personal gear pages (FPS weapons, armor, equipment)
- Ship detail pages with upgrade recommendations

## Prioritized Backlog

### P1 - Re-validate Chase Planner
- Chase planner was completed but needs verification post-data overhaul

### P2 - Real-time Price Tracking
- Track in-game item prices over time

### P3 - RSI Fleet Import
- Import fleet from RSI account
