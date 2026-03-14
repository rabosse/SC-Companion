# Star Citizen Fleet Manager - PRD

## Original Problem Statement
Build a full-stack application called "Star Citizen Fleet Manager" for players to track their ships and ground vehicles from the game Star Citizen, with detailed stats, comparison tools, loadout builders, and data sourced from `finder.cstone.space` and `starcitizen.tools`.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, react-router-dom, axios, framer-motion
- **Backend**: FastAPI, Pydantic, JWT authentication
- **Database**: MongoDB
- **Data Sources**: finder.cstone.space API, starcitizen.tools API, api.star-citizen.wiki

## Architecture
```
/app/backend/routes/ships.py       - Ships + Components + Weapons endpoints (with detail endpoints)
/app/backend/routes/fleet.py       - User fleet management
/app/backend/routes/gear.py        - FPS Gear/Weapons/Armor/Equipment + Rare Items
/app/backend/routes/loadouts.py    - Loadout builder
/app/backend/routes/price_tracker.py - Price tracking
/app/backend/routes/starmap.py     - Route/Chase planner
/app/backend/routes/wikelo.py      - Wikelo contracts
/app/backend/routes/auth.py        - JWT authentication
/app/backend/live_api.py           - Star Citizen Wiki API + curated hardpoint data
/app/backend/cstone_api.py         - CStone price/location/item data
/app/backend/personal_gear.py      - FPS weapons, armor, equipment data
/app/frontend/src/pages/Weapons.jsx        - Clickable weapon cards + detail modal with SCtools data
/app/frontend/src/pages/Components.jsx     - Clickable component cards + detail modal (inc. Radars)
/app/frontend/src/pages/Ships.jsx          - Ship database with filters
/app/frontend/src/pages/Dashboard.jsx      - Fleet dashboard + manufacturer colors
/app/frontend/src/pages/LoadoutBuilder.jsx - Loadout builder with fleet toggle
/app/frontend/src/pages/PersonalGear.jsx   - Gear page with Rare Items tab
```

## Completed Features
- [x] User authentication (Username/Password, JWT)
- [x] Ship database with 180 ships (158 flight-ready + 22 non-flight-ready)
- [x] Ground vehicle database
- [x] Fleet management (add/remove unlimited ships)
- [x] Ship comparison tool
- [x] Loadout builder with Fleet Only toggle
- [x] Dashboard with fleet stats, favorite manufacturer, color-coordinated fleet list
- [x] Components page with filtering/sorting + clickable detail modals with purchase locations
- [x] Weapons page with filtering/sorting + clickable detail modals with purchase locations
- [x] Radars included in component catalog (32 radars from starcitizen.tools)
- [x] Wikelo section with contracts
- [x] Ship/vehicle purchase locations
- [x] Route planner (including chase and interdiction)
- [x] Price tracking
- [x] Non-flight-ready ships with badges
- [x] Ship hardpoints fixed (Eclipse [9,9,9], Reclaimer [5,5], Talon Shrike [5,5], Liberator [5,5,4,4], Merchantman [7,7,5,5,4,4,4,4])
- [x] Wiki-injected ships now receive curated hardpoint data
- [x] Rare Item Locations tab on Gear page (86 items)
- [x] (P4) Icon cleanup - SpaceshipIcon in use, no boat icons
- [x] (P1) Full re-validation passed
- [x] (P3) Rare item locations complete

## API Endpoints
- `/api/ships` - All ships with hardpoints, images, purchase data
- `/api/vehicles` - Ground vehicles
- `/api/components` - 302 components (Cooler, Power, Quantum, Shield, Radar)
- `/api/components/{id}` - Component detail with purchase locations/prices
- `/api/weapons` - 146 ship weapons
- `/api/weapons/{id}` - Weapon detail with purchase locations/prices
- `/api/gear/rare-items` - 86 rare/loot-only items
- `/api/fleet/*` - Fleet management
- `/api/loadouts/*` - Loadout save/load/share
- `/api/auth/*` - Authentication

## Remaining/Backlog Tasks
- [ ] (P2) RSI Fleet Import tool
- [ ] Fleet value estimator (total aUEC + pledge cost)

## Known Issues
- Production deployment fails (suspected platform-level resource issue)
- /api/gear/rare-items first call can be slow (~30-60s) due to CStone data prefetch
- Component/Weapon detail modals load locations asynchronously (5-15s per item)
