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
- [x] Ground vehicle database, Fleet management, Ship comparison tool
- [x] Loadout builder with Fleet Only toggle, My Loadouts tab, tags, filters, sorting
- [x] Dashboard with fleet stats, Components page, Weapons page with detail modals
- [x] Shopping List with Visual Route Planner + Zoomable Map + Smart gate-jump-last routing
- [x] Complete Hardpoint Overhaul, Wikelo section, Route planner, Price tracking
- [x] **Liveries Page** — 101 ship series, 846 paints. Component-style cards with paint image, description, acquisition badge, aUEC/USD pricing. Click opens detail modal with full image, description, RSI Store link, and **In-Game Purchase Locations** (store names + prices, cheapest highlighted green). Filters: search, acquisition type dropdown, Fleet Only toggle. Sort by series/name/price/acquisition. (2026-03-16)

## Key Architecture
- `backend/livery_scraper.py` — Background scraper: wiki paint data + CStone location matching + batch image resolution
- `backend/routes/liveries.py` — GET /api/liveries endpoint
- `frontend/src/pages/Liveries.jsx` — Flat paint card grid + PaintDetailModal (component-style)

## Remaining/Backlog Tasks
- [ ] (P1) RSI Fleet Import tool
- [ ] (P2) Wikelo Section enhancements (contracts & required items)
- [ ] (P3) Chase/Interdiction Route Planner enhancements
- [ ] (P4) Real-time Price Tracking
- [ ] Fleet value estimator, LoadoutBuilder.jsx refactor

## Known Issues
- Production deployment fails (suspected platform-level resource issue)
