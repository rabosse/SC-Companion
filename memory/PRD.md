# Star Citizen Fleet Manager - PRD

## Original Problem Statement
Build a full-stack application called "Star Citizen Fleet Manager" that allows players to track their ships and ground vehicles from Star Citizen. Uses Star Citizen API for data, with user authentication and personal fleet management.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, react-router-dom, axios, lucide-react, framer-motion
- **Backend**: FastAPI, Pydantic, JWT auth, bcrypt
- **Database**: MongoDB (collections: users, user_fleet, loadouts, price_snapshots)
- **Data Source**: starcitizen.tools API (live) + static fallback data

## What's Implemented (All Complete)
- User Authentication (register/login with JWT)
- Ships, Vehicles, Components, Weapons pages with live API data
- Fleet Management with Quick Import
- Ship Comparison (up to 5 ships)
- Loadout Builder with hardpoint rules + sharing via code + community page
- Comprehensive Dashboard (fleet value aUEC/USD, manufacturers, ship cards)
- Route Planner (Stanton, Pyro, Nyx) + Interdiction Planner + Chase Calculator
- Personal Gear page with 3 tabs:
  - FPS Weapons (38): Pistols, SMGs, ARs, LMGs, Shotguns, Snipers, Railguns, Grenades, Utilities
  - Armor Sets (21): Heavy, Medium, Light, Flight Suits
  - Equipment (23): Mining Heads (5), Mining Modules (4), Mining Attachment (1), Medical Devices (4), Backpacks (4), Undersuits (5)
- Real-time Price Tracker (150+ items, MongoDB snapshots, change detection)
- ~99% ship/vehicle image coverage
- Backend refactored into 7 modular routers

## Key API Endpoints
- `/api/auth/register`, `/api/auth/login`
- `/api/ships`, `/api/vehicles`, `/api/components`, `/api/weapons`, `/api/upgrades/{id}`
- `/api/fleet/add`, `/api/fleet/my`, `/api/fleet/{id}`, `/api/fleet/bulk-add`
- `/api/loadouts/save`, `/api/loadouts/my/all`, `/api/loadouts/{ship_id}`, `/api/loadouts/{id}` (DELETE)
- `/api/community/loadouts`, `/api/community/loadouts/{share_code}`, `/api/loadouts/clone/{share_code}`
- `/api/routes/locations`, `/api/routes/calculate`, `/api/routes/interdiction`, `/api/routes/chase`
- `/api/gear/weapons`, `/api/gear/armor`, `/api/gear/equipment`
- `/api/prices/summary`, `/api/prices/changes`, `/api/prices/snapshot`, `/api/prices/history/{name}`
- `/api/health`

## Architecture
```
/app/backend/
  server.py              # Thin orchestrator (~55 lines)
  deps.py                # Shared: DB, models, JWT auth
  routes/
    auth.py, ships.py, fleet.py, loadouts.py, starmap.py, gear.py, prices.py
  live_api.py, ship_data_enhancer.py, personal_gear.py, star_systems.py, ship_purchases.py

/app/frontend/src/
  App.js, index.js
  components/ (Layout.jsx, Header.jsx, ui/)
  pages/ (Dashboard, Fleet, Ships, ShipDetail, Vehicles, Components, Weapons,
          Compare, LoadoutBuilder, CommunityLoadouts, SharedLoadout,
          RoutePlanner, PersonalGear, PriceTracker, Login)
```

## Backlog / Future
- P3: Price change notifications/alerts for fleet ships
- P3: Additional equipment (salvage tools, tractor beams, ship components browser)
