# Star Citizen Fleet Manager - PRD

## Original Problem Statement
Build a full-stack application called "Star Citizen Fleet Manager" that allows players to track their ships and ground vehicles from Star Citizen. Uses Star Citizen API for data, with user authentication and personal fleet management.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, react-router-dom, axios, lucide-react, framer-motion
- **Backend**: FastAPI, Pydantic, JWT auth, bcrypt
- **Database**: MongoDB (collections: users, user_fleet, loadouts, price_snapshots)
- **Data Source**: starcitizen.tools API (live) + static fallback data

## Core Requirements (All Implemented)
- User authentication (Username/Password)
- Ship/vehicle browsing with official images (~99% coverage)
- Fleet management (add/remove unlimited vehicles, quick import)
- Ship comparison tool (up to 5 ships)
- Loadout builder with savable/shareable loadouts + community page
- Fleet statistics dashboard (value in aUEC/USD, manufacturers, ship cards)
- Components/Weapons pages with size filtering, location, and aUEC price
- Ship/vehicle purchase locations (in-game and RSI store)
- Route planner for Stanton, Pyro, and Nyx systems
- Interdiction planner + Chase calculator
- Rare armor and FPS weapon/grenade/utility locations (38 weapons, 21 armor sets)
- Real-time price tracking with MongoDB snapshots (150+ items)

## Key DB Schema
- **users**: `{id, username, email, password_hash, created_at}`
- **user_fleet**: `{id, user_id, ship_id, ship_name, manufacturer, added_at}`
- **loadouts**: `{id, user_id, username, ship_id, ship_name, loadout_name, slots, share_code, updated_at}`
- **price_snapshots**: `{item_name, item_type, price_auec, price_usd, dealers/location, timestamp}`

## Key API Endpoints
- `/api/auth/register`, `/api/auth/login`
- `/api/ships`, `/api/vehicles`, `/api/components`, `/api/weapons`, `/api/upgrades/{ship_id}`
- `/api/fleet/add`, `/api/fleet/my`, `/api/fleet/{id}`, `/api/fleet/bulk-add`
- `/api/loadouts/save`, `/api/loadouts/my/all`, `/api/loadouts/{ship_id}`, `/api/loadouts/{id}` (DELETE)
- `/api/community/loadouts`, `/api/community/loadouts/{share_code}`, `/api/loadouts/clone/{share_code}`
- `/api/routes/locations`, `/api/routes/calculate`, `/api/routes/interdiction`, `/api/routes/chase`
- `/api/gear/weapons`, `/api/gear/armor`
- `/api/prices/summary`, `/api/prices/changes`, `/api/prices/snapshot`, `/api/prices/history/{name}`
- `/api/health`

## Architecture
```
/app/backend/
  server.py              # Thin orchestrator (~50 lines)
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

## Completed Features
- All core requirements above
- Backend refactored into modular routers
- Gear expanded with grenades (4) and utilities (6)
- Price Tracker with real-time API data, MongoDB snapshots, change detection

## Backlog / Future
- P3: Additional gear categories (medical supplies expansion)
- P3: Price change notifications/alerts
