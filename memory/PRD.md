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
- [x] Loadout builder with Fleet Only toggle, My Loadouts tab (view/edit/delete), grouped by ship
- [x] Dashboard with fleet stats, favorite manufacturer, color-coordinated fleet list
- [x] Components page with clickable detail modals, purchase locations, prices, Radars included
- [x] Weapons page with clickable detail modals, purchase locations, prices
- [x] Wikelo section, Route planner, Price tracking, Community loadouts
- [x] Rare Item Locations tab on Gear page
- [x] Auto-logout axios interceptor for expired tokens
- [x] Shopping List with Visual Route Planner + Starting Location Picker + Zoomable Map
- [x] Complete Hardpoint Overhaul (200+ ships from Fleetyards API)
- [x] Component Class & Grade Tags + Filter Buttons in Loadout Builder
- [x] Weapon Damage Type Filters + DPS/Ammo Sort Buttons in Loadout Builder
- [x] Smart Route Planner — gate jumps always last, same-system stores visited first
- [x] **Liveries Page** — 98 ship series, 815 paints from starcitizen.tools wiki. Clickable detail modal with full paint sidebar, image swapping, acquisition tags, pricing. In-game purchase locations from CStone API (store names + aUEC prices). RSI Store links. Search, Fleet Only toggle, acquisition filters. (2026-03-16)

## Key Architecture
- `backend/livery_scraper.py` — Background scraper: wiki paint data + CStone location matching + batch image resolution
- `backend/routes/liveries.py` — GET /api/liveries endpoint
- `frontend/src/pages/Liveries.jsx` — Liveries page with PaintViewer cards + LiveryDetailModal

## Remaining/Backlog Tasks
- [ ] (P1) RSI Fleet Import tool
- [ ] (P2) Wikelo Section enhancements (contracts & required items)
- [ ] (P3) Chase/Interdiction Route Planner enhancements
- [ ] (P4) Real-time Price Tracking
- [ ] Fleet value estimator (total aUEC + pledge cost)
- [ ] LoadoutBuilder.jsx refactor (1400+ lines → smaller components)

## Known Issues
- Production deployment fails (suspected platform-level resource issue)
