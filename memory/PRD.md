# Star Citizen Fleet Manager - PRD

## Original Problem Statement
Build a full-stack "Star Citizen Fleet Manager" allowing players to track ships, ground vehicles, components, weapons, with detailed information from the Star Citizen API.

## Core Features (Implemented)
- User authentication (username/password)
- Fleet management (add/remove unlimited vehicles)
- Ship/vehicle database with images, specs, and filtering
- Ship comparison tool
- Loadout builder with savable/shareable loadouts
- Fleet statistics dashboard
- Components and weapons pages with filtering
- Personal Gear section (Armor, FPS Weapons, Equipment)
- Route planner with fuel-aware calculations
- Interactive Canvas-based Starmap (Mobi-Glass style)
- Interdiction planner with tactical analysis
- **Enhanced Chase Planner** with location-aware pursuit analysis
- Purchase location display (in-game and RSI store)

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, Canvas API, lucide-react
- **Backend**: FastAPI, Pydantic, JWT auth, bcrypt
- **Database**: MongoDB
- **Data Sources**: starcitizen.tools API, cstone.space API

## Architecture
```
/app/backend/  → FastAPI server, routes/, data_enhancers/
/app/frontend/ → React SPA, pages/, components/
```

## Key API Endpoints
- `/api/auth/login`, `/api/auth/register`
- `/api/ships`, `/api/fleet`
- `/api/routes/locations`, `/api/routes/calculate`
- `/api/routes/interdiction`, `/api/routes/chase`, `/api/routes/chase/advanced`
- `/api/loadouts`, `/api/gear/*`, `/api/prices`

## DB Schema
- users: {username, email, password_hash, fleet[]}
- saved_loadouts: {user_id, ship_id, loadout_name, components, is_public, share_code}
- price_history: {item_id, item_type, snapshots[]}

## What's Been Implemented
- All core features listed above
- **Comprehensive hardpoint audit**: All 203 ships/vehicles have curated weapon hardpoints and component overrides (verified via starcitizen.tools, RSI, community sources)
- **Enhanced Chase Planner**: Location-aware pursuit analysis with escape route calculation, threat assessment, and Canvas visualization
- **Interdiction Planner**: Tactical analysis with arrival timelines, escape analysis, and smart intel
- **Starmap**: Canvas-based animated visualization with nebulas, glowing nodes, animated routes

## Remaining Tasks
### P1
- Real-time price tracking for in-game items
### P2
- RSI fleet import tool
### Low Priority
- Clean up ship_data_enhancer.py wrapper
- Fix React duplicate key warnings for ships with identical names
