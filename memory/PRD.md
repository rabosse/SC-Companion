# Star Citizen Fleet Manager - PRD

## Original Problem Statement
Build a full-stack application called "Star Citizen Fleet Manager" for players to track their ships and ground vehicles from the game Star Citizen, with detailed stats, comparison tools, loadout builders, and data sourced from `finder.cstone.space` and `starcitizen.tools`.

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, react-router-dom, axios, framer-motion
- **Backend**: FastAPI, Pydantic, JWT authentication
- **Database**: MongoDB
- **Data Sources**: finder.cstone.space API, starcitizen.tools API, api.star-citizen.wiki

## Completed Features
- [x] User authentication (Username/Password, JWT) with auto-logout on expired token
- [x] Ship database with 180 ships (158 flight-ready + 22 non-flight-ready)
- [x] Ground vehicle database
- [x] Fleet management (add/remove unlimited ships)
- [x] Ship comparison tool
- [x] Loadout builder with Fleet Only toggle, **My Loadouts tab** (view/edit/delete), grouped by ship
- [x] Dashboard with fleet stats, favorite manufacturer, color-coordinated fleet list
- [x] Components page with clickable detail modals, purchase locations, prices, **Radars included** (302 total)
- [x] Weapons page with clickable detail modals, purchase locations, prices (146 weapons)
- [x] Wikelo section, Route planner, Price tracking, Community loadouts
- [x] Ship hardpoints fixed (Eclipse, Reclaimer, Talon Shrike, Liberator, Merchantman)
- [x] Rare Item Locations tab on Gear page (86 items)
- [x] Auto-logout axios interceptor for expired tokens

## Remaining/Backlog Tasks
- [ ] (P2) RSI Fleet Import tool
- [ ] Fleet value estimator (total aUEC + pledge cost)

## Known Issues
- Production deployment fails (suspected platform-level resource issue)
