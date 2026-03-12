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
/app/backend/routes/ships.py       - Ship database (180 ships, 22 non-flight-ready)
/app/backend/routes/fleet.py       - User fleet management
/app/backend/routes/gear.py        - FPS Gear/Weapons/Armor/Equipment + Rare Items endpoint
/app/backend/routes/loadouts.py    - Loadout builder
/app/backend/routes/price_tracker.py - Price tracking
/app/backend/routes/starmap.py     - Route/Chase planner
/app/backend/routes/wikelo.py      - Wikelo contracts section
/app/backend/routes/auth.py        - JWT authentication
/app/backend/personal_gear.py      - FPS weapons, armor, equipment data
/app/backend/live_api.py           - Star Citizen Wiki API integration
/app/backend/data_enhancers/cstone_api.py - CStone price/location data
/app/frontend/src/pages/Ships.jsx           - Ship database with filters
/app/frontend/src/pages/Dashboard.jsx       - Fleet dashboard + manufacturer colors
/app/frontend/src/pages/Fleet.jsx           - Fleet management
/app/frontend/src/pages/LoadoutBuilder.jsx  - Loadout builder with fleet toggle
/app/frontend/src/pages/PersonalGear.jsx    - Gear page with Rare Items tab
/app/frontend/src/pages/Wikelo.jsx          - Wikelo contracts
/app/frontend/src/pages/PriceTracker.jsx    - Price tracking
```

## Completed Features
- [x] User authentication (Username/Password, JWT)
- [x] Ship database with 180 ships (158 flight-ready + 22 non-flight-ready)
- [x] Ground vehicle database (12+ vehicles)
- [x] Fleet management (add/remove unlimited ships)
- [x] Ship comparison tool
- [x] Loadout builder (savable/shareable) with Fleet Only toggle
- [x] Dashboard with fleet stats, favorite manufacturer, color-coordinated fleet list
- [x] Components and Weapons pages with filtering/sorting
- [x] Wikelo section with contracts and item requirements
- [x] Ship/vehicle purchase locations (in-game and RSI store)
- [x] Route planner (including chase and interdiction)
- [x] Price tracking for in-game items
- [x] Non-flight-ready ships with "Not Flight Ready" badge
- [x] Flight Ready/Size/Type/Manufacturer/SCU filters on Ships page
- [x] Ground vehicles excluded from Ships section
- [x] Avenger variants properly grouped
- [x] (P4) Replaced boat icons — custom SpaceshipIcon in use, unused Anchor import removed
- [x] (P1) Full re-validation — 96% backend, 100% frontend (23/24 + 13/13)
- [x] (P3) Rare Item Locations — /api/gear/rare-items endpoint + Rare Items tab on Gear page (86 items: 15 weapons, 70 armor, 1 equipment; 26 loot-only)

## Remaining/Backlog Tasks
- [ ] (P2) RSI Fleet Import tool
- [ ] Fleet value estimator (total aUEC + pledge cost)

## Known Issues
- Production deployment fails (suspected platform-level resource issue)
- /api/gear/rare-items first call can be slow (~30-60s) due to CStone data prefetch
