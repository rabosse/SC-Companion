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
  - FPS Weapons (38): Visual grid cards with wiki images (63% coverage), type+size badges, stats, variants, locations
  - Armor Sets (21): Visual grid cards with wiki images (86% coverage), type badges, stats, variants, locations
  - Equipment (30): Mining (10), Medical (4), Backpacks (4), Undersuits (5), Salvage Tools (3), Scanners (2), Hacking Tools (2)
- Real-time Price Tracker (150+ items, MongoDB snapshots, change detection)
- ~99% ship/vehicle image coverage
- Backend refactored into 7 modular routers

## Key API Endpoints
- `/api/auth/register`, `/api/auth/login`
- `/api/ships`, `/api/vehicles`, `/api/components`, `/api/weapons`, `/api/upgrades/{id}`
- `/api/fleet/*` (add, my, delete, bulk-add)
- `/api/loadouts/*` (save, list, delete, share)
- `/api/community/loadouts`, `/api/community/loadouts/{share_code}`
- `/api/routes/*` (locations, calculate, interdiction, chase)
- `/api/gear/weapons`, `/api/gear/armor`, `/api/gear/equipment`
- `/api/prices/*` (summary, changes, snapshot, history)
- `/api/health`

## Architecture
```
/app/backend/
  server.py, deps.py
  routes/ (auth, ships, fleet, loadouts, starmap, gear, prices)
  live_api.py, ship_data_enhancer.py, personal_gear.py, star_systems.py, ship_purchases.py

/app/frontend/src/
  App.js, pages/ (14 pages), components/ (Layout, Header, ui/)
```

## Backlog / Future
- P3: Price change notifications/alerts for fleet ships
