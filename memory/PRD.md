# Star Citizen Fleet Manager - PRD

## Original Problem Statement
Build a full-stack application called "Star Citizen Fleet Manager" that allows Star Citizen players to track their ships and ground vehicles. The app should use the Star Citizen API for data, support user authentication, fleet management, ship/vehicle images, component/weapon browsing with filters, ship comparison, and loadout building.

## Core Requirements
- User authentication (JWT-based, demo mode)
- Ship database with real images from Star Citizen Wiki
- Ground vehicle database with images
- Component catalog with size filtering, location, aUEC price
- Weapons arsenal with size filtering, location, aUEC price
- Personal fleet management (add/remove ships)
- Fleet statistics dashboard
- Ship comparison tool (up to 5 ships)
- Loadout builder with SIZE RESTRICTIONS (only compatible parts shown)
- Star Citizen themed UI
- LIVE API integration with mock fallback

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, Framer Motion, react-router-dom, axios
- **Backend**: FastAPI, Pydantic, JWT auth (python-jose), httpx
- **Database**: MongoDB (Motor async driver)
- **Image Source**: starcitizen.tools MediaWiki API (batch-fetched on startup, cached)
- **Data Source**: api.star-citizen.wiki LIVE API with mock fallback

## What's Implemented (as of Feb 27, 2026)
- [x] JWT-based login/registration (demo mode)
- [x] LIVE API integration: 276 ships, 178 weapons, 333 components from api.star-citizen.wiki
- [x] Ship images: 117 matched wiki images from starcitizen.tools
- [x] Ship detail page with hero image, specs (crew min-max, cargo, speed, shield HP)
- [x] Ground vehicles with wiki images
- [x] Component catalog: search, type filter, SIZE FILTER, real locations, real aUEC prices
- [x] Weapons arsenal: search, type filter, SIZE FILTER, real locations, real aUEC prices
- [x] Fleet management (add/remove ships, fleet statistics)
- [x] Ship Comparison Tool: up to 5 ships, search, stat bars, best-value highlighting
- [x] Loadout Builder: SIZE RESTRICTIONS enforced (components exact size match, weapons <= max size)
- [x] Dashboard with featured ships (real images) and stats
- [x] Auth persistence on page reload (authLoading state)
- [x] Nav: Dashboard, My Fleet, Ships, Vehicles, Components, Weapons, Compare, Loadout
- [x] Star Citizen themed dark UI with official logo

## Architecture
```
/app/
├── backend/
│   ├── .env (MONGO_URL, DB_NAME, JWT_SECRET, STAR_CITIZEN_API_KEY)
│   ├── server.py (FastAPI endpoints, mock data fallback)
│   ├── live_api.py (Live Star Citizen Wiki API integration + hardpoint data)
│   ├── ship_data_enhancer.py (Wiki image fetching & caching)
│   └── requirements.txt
└── frontend/
    ├── .env (REACT_APP_BACKEND_URL)
    └── src/
        ├── App.js (routes, auth context with loading state)
        ├── components/ (Layout with full nav, SpaceshipIcon, ui/)
        └── pages/ (Login, Dashboard, Ships, ShipDetail, Vehicles, Components, Weapons, Fleet, Compare, LoadoutBuilder)
```

## API Endpoints
- POST /api/auth/login, POST /api/auth/register
- GET /api/ships (live API with mock fallback, includes hardpoints data)
- GET /api/vehicles (live API with mock fallback)
- GET /api/components (live API: 333 components with real prices/locations)
- GET /api/weapons (live API: 178 weapons with real prices/locations)
- GET /api/upgrades/{ship_id}
- POST /api/fleet/add, GET /api/fleet/my, DELETE /api/fleet/{fleet_id}

## Loadout Builder - Size Restriction System
Ships have hardpoints derived from API `size_class` and `power_pools`:
- size_class 2 (Small): S1 components, 3 weapon hardpoints
- size_class 3 (Medium): S2 components, 4 weapon hardpoints
- size_class 4 (Large): S2 components, 4 weapon hardpoints
- size_class 5 (Capital): S3 components, 6 weapon hardpoints
Components: exact size match required. Weapons: <= hardpoint max size.

## Prioritized Backlog

### P0 (Critical) - All done!

### P1 (High)
- **More ship image coverage**: Currently 117/276 ships have matched wiki images
- **Loadout persistence**: Save/load loadouts to MongoDB per user

### P2 (Medium)
- **Data migration**: Move mock data into MongoDB collections
- **Loadout sharing**: Share loadout builds with other users
- **Fleet value tracking**: Track fleet total value over time

### P3 (Low)
- Enhanced fleet statistics and analytics
- Mobile-responsive improvements
- Export fleet/loadout data functionality
