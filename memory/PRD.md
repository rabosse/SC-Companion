# Star Citizen Fleet Manager - PRD

## Original Problem Statement
Build a full-stack application called "Star Citizen Fleet Manager" for players to track their ships and ground vehicles from the game Star Citizen, with detailed stats, comparison tools, loadout builders, and data sourced from `finder.cstone.space` and `starcitizen.tools`.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, react-router-dom, axios, framer-motion
- **Backend**: FastAPI, Pydantic, JWT authentication
- **Database**: MongoDB
- **Data Sources**: finder.cstone.space API, starcitizen.tools API, api.star-citizen.wiki, api.fleetyards.net

## Completed Features
- [x] User authentication (Username/Password, JWT) with auto-logout on expired token
- [x] Ship database with 180+ ships (verified hardpoints from Fleetyards API)
- [x] Ground vehicle database
- [x] Fleet management (add/remove unlimited ships)
- [x] Ship comparison tool
- [x] Loadout builder with Fleet Only toggle, **My Loadouts tab** (view/edit/delete), grouped by ship
- [x] Dashboard with fleet stats, favorite manufacturer, color-coordinated fleet list
- [x] Components page with clickable detail modals, purchase locations, prices, Radars included (302 total)
- [x] Weapons page with clickable detail modals, purchase locations, prices (146 weapons)
- [x] Wikelo section, Route planner, Price tracking, Community loadouts
- [x] Rare Item Locations tab on Gear page (86 items)
- [x] Auto-logout axios interceptor for expired tokens
- [x] **Shopping List with Visual Route Planner** - Cost breakdown, store groupings, SVG star map route with distances/travel times
- [x] **Starting Location Picker** - Dropdown with 36+ dockable locations + Route button that updates BOTH map and store list
- [x] **Zoomable/Pannable Route Map** - Scroll wheel zoom, click-drag pan, zoom in/out/reset buttons
- [x] **Complete Hardpoint Overhaul** - 200+ ships cross-referenced with Fleetyards API (2026-03-14). Key fixes: Arrow 4→3 weapons, Eclipse S9→S2, Retaliator 2→10, Reclaimer 2→18, Constellation turrets S3→S2, Talon/Talon Shrike corrected, Aurora correct S1, many more
- [x] **Hierarchical Store Location Resolver** - Parses CStone format "Pyro > Pyro V > Ignis > Ashland > shop_terminal" into map locations. Pyro system support added.

## Remaining/Backlog Tasks
- [ ] (P1) RSI Fleet Import tool
- [ ] (P2) Wikelo Section enhancements (contracts & required items)
- [ ] (P3) Chase/Interdiction Route Planner enhancements
- [ ] (P4) Real-time Price Tracking
- [ ] Fleet value estimator (total aUEC + pledge cost)

## Known Issues
- Production deployment fails (suspected platform-level resource issue)
