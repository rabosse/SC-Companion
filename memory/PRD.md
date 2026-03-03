# Star Citizen Fleet Manager - PRD

## Original Problem Statement
Build a full-stack application called "Star Citizen Fleet Manager" that allows players to track their ships and ground vehicles from Star Citizen. Uses Star Citizen API for data, with user authentication and personal fleet management.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, react-router-dom, axios, lucide-react, framer-motion
- **Backend**: FastAPI, Pydantic, JWT auth, bcrypt
- **Database**: MongoDB
- **Data Source**: starcitizen.tools API (live) + static fallback data

## Core Requirements
- User authentication (Username/Password)
- Ship/vehicle browsing with official images
- Fleet management (add/remove unlimited vehicles)
- Ship comparison tool (up to 5 ships)
- Loadout builder with savable/shareable loadouts
- Fleet statistics dashboard
- Components/Weapons pages with size filtering, location, and aUEC price
- Ship/vehicle purchase locations (in-game and RSI store)
- Quick fleet import tool
- Auto-updating data reflecting game patches
- Route planner for Stanton, Pyro, and Nyx systems
- Interdiction planner for pirating
- Rare armor and FPS weapon locations

## Key DB Schema
- **users**: `{username, email, password_hash, fleet: list[str]}`
- **saved_loadouts**: `{user_id, ship_id, loadout_name, components, is_public, share_code}`

## What's Implemented (All Complete)
- User Authentication (register/login with JWT)
- Ships, Vehicles, Components, Weapons pages with live API data
- Fleet Management with Quick Import
- Ship Comparison (up to 5 ships)
- Loadout Builder with hardpoint rules enforcement
- Loadout Sharing (save, load, share via code, community page)
- Route Planner (Stanton, Pyro, Nyx systems)
- Interdiction Planner (QED snare positioning)
- Chase Calculator (pursuit scenarios)
- Comprehensive Dashboard (fleet overview, value, manufacturers, ship cards)
- Personal Gear page (28 FPS weapons, 21 armor sets with locations)
- Health endpoint for deployment readiness
- ~99% ship/vehicle image coverage via name-based matching

## Key API Endpoints
- `/api/auth/register`, `/api/auth/login`
- `/api/fleet/bulk-add`
- `/api/community-loadouts`, `/api/loadouts/{share_code}`, `/api/loadouts/{loadout_id}/clone`
- `/api/locations`, `/api/route`
- `/api/route/interdict`, `/api/route/chase`
- `/api/gear/weapons`, `/api/gear/armor`
- `/api/health`

## Architecture
```
/app/
  backend/
    server.py, live_api.py, data_enhancer.py, personal_gear.py, starmap_data.py
    requirements.txt, .env, tests/
  frontend/
    src/
      App.js, index.js
      components/ (Layout.jsx, Header.jsx, SpaceshipIcon.jsx, ui/)
      pages/ (Dashboard, Fleet, Ships, ShipDetail, Vehicles, Components, Weapons,
              Compare, LoadoutBuilder, CommunityLoadouts, SharedLoadout,
              RoutePlanner, PersonalGear, Login)
```

## Backlog / Future Enhancements
- P1: Refactor server.py into feature-specific routers (routes/starmap.py, routes/loadouts.py, etc.)
- P2: Simplify data_enhancer.py (now only a fallback)
- P2: Additional gear data (grenades, utilities, medical items)
- P3: Real-time price tracking integration
- P3: Organization/guild fleet management

## Test Reports
- /app/test_reports/iteration_10.json (Latest - Gear page: 100% pass, 41 tests)
