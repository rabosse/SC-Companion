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
/app/backend/routes/ships.py    - Ship database (180 ships, 22 non-flight-ready)
/app/backend/routes/fleet.py    - User fleet management
/app/backend/routes/gear.py     - FPS Gear/Weapons
/app/backend/routes/loadouts.py - Loadout builder
/app/backend/routes/price_tracker.py - Price tracking
/app/backend/routes/starmap.py  - Route/Chase planner
/app/backend/routes/wikelo.py   - Wikelo contracts section
/app/backend/routes/auth.py     - JWT authentication
/app/backend/live_api.py        - Star Citizen Wiki API integration
/app/backend/data_enhancers/cstone_api.py - CStone price/location data
/app/frontend/src/pages/Ships.jsx      - Ship database with filters
/app/frontend/src/pages/Dashboard.jsx  - Fleet dashboard with filters + manufacturer colors
/app/frontend/src/pages/Fleet.jsx      - Fleet management
/app/frontend/src/pages/LoadoutBuilder.jsx - Loadout builder with fleet toggle
/app/frontend/src/pages/Wikelo.jsx     - Wikelo contracts
/app/frontend/src/pages/PriceTracker.jsx - Price tracking
```

## Completed Features
- [x] User authentication (Username/Password, JWT)
- [x] Ship database with 180 ships (158 flight-ready + 22 non-flight-ready from wiki)
- [x] Ground vehicle database (12+ vehicles)
- [x] Fleet management (add/remove unlimited ships)
- [x] Ship comparison tool
- [x] Loadout builder (savable/shareable)
- [x] Dashboard with fleet stats and advanced filtering (Size, Type, Manufacturer, SCU)
- [x] Components and Weapons pages with filtering/sorting
- [x] Wikelo section with contracts and item requirements
- [x] Ship/vehicle purchase locations (in-game and RSI store)
- [x] Route planner (including chase and interdiction)
- [x] Price tracking for in-game items
- [x] Non-flight-ready ships with "Not Flight Ready" flag
- [x] Flight Ready toggle filter on Ships page (All / Flight Ready / Not Flight Ready)
- [x] Ships page sort/filter options (Size, Type/Role, Manufacturer, Cargo)
- [x] Ground vehicles properly excluded from Ships section
- [x] Avenger variants properly grouped (Stalker, Warlock, Renegade under Titan)
- [x] Loadout Builder "Fleet Only" toggle (All Ships / My Fleet)
- [x] Dashboard "Favorite Manufacturer" display with color-coded breakdown
- [x] Fleet list color-coordination (ship names + manufacturer names match manufacturer color)

## Remaining/Backlog Tasks
- [ ] (P1) Full re-validation of all features after data changes
- [ ] (P2) RSI Fleet Import tool
- [ ] (P3) Rare item locations (armor/FPS weapons)
- [ ] (P4) Replace boat icons with spaceship icons

## Known Issues
- Production deployment fails (suspected platform-level resource issue, not code)
