# Star Citizen Fleet Manager - PRD

## Original Problem Statement
Build a full-stack application called "Star Citizen Companion" that allows players to track ships, ground vehicles, components, weapons, and personal gear from Star Citizen.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, react-router-dom, axios, lucide-react, framer-motion
- **Backend**: FastAPI, Pydantic, JWT auth, bcrypt
- **Database**: MongoDB (collections: users, user_fleet, loadouts, price_snapshots)
- **Data Source**: starcitizen.tools API (live) + static fallback

## What's Implemented (All Complete)
- Auth (register/login JWT), Fleet management, Ship comparison, Loadout builder + sharing
- Dashboard (fleet value aUEC/USD, manufacturers, ship cards)
- Route Planner (Stanton/Pyro/Nyx, 81 locations: planets, moons, cities, rest stops, outposts, stations, gateways)
- Interdiction Planner + Chase Calculator
- Gear page (3 tabs):
  - FPS Weapons (38): Grid cards with wiki images (63%), aUEC prices, detail popup modal
  - Armor Sets (21): Grid cards with wiki images (86%), aUEC prices, 4-5 variants each, detail popup modal
  - Equipment (30): Mining/Medical/Backpacks/Undersuits/Salvage/Scanners/Hacking
- Price Tracker (150+ items, MongoDB snapshots, change detection)
- Auto-hiding header on scroll with "Star Citizen Companion" branding
- ~99% ship/vehicle image coverage, 7 modular backend routers

## Key API Endpoints
- Auth, Fleet, Ships/Vehicles/Components/Weapons, Loadouts, Community
- `/api/routes/locations` (81 locs), `/api/routes/calculate`, `/api/routes/interdiction`, `/api/routes/chase`
- `/api/gear/weapons`, `/api/gear/armor`, `/api/gear/equipment`
- `/api/prices/summary`, `/api/prices/changes`, `/api/prices/snapshot`, `/api/prices/history/{name}`
- `/api/health`

## Backlog
- Price change alerts for fleet ships
