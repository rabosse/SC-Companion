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
- Ship comparison tool
- Loadout builder
- Star Citizen themed UI

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, Framer Motion, react-router-dom, axios
- **Backend**: FastAPI, Pydantic, JWT auth (python-jose), httpx
- **Database**: MongoDB (Motor async driver)
- **Image Source**: starcitizen.tools MediaWiki API (batch-fetched on startup, cached in memory)

## What's Implemented (as of Feb 27, 2026)
- [x] JWT-based login/registration (demo mode)
- [x] Ship database with 117 ships, all with real wiki images
- [x] Ship detail page with hero image and specs
- [x] Ground vehicles page with 4 vehicles and wiki images
- [x] Component catalog with search, type filter, SIZE FILTER, location, aUEC price
- [x] Weapons arsenal with search, type filter, SIZE FILTER, location, aUEC price
- [x] Fleet management (add/remove ships, fleet statistics)
- [x] Dashboard with featured ships (with images) and stats
- [x] Navigation with all pages
- [x] Star Citizen themed dark UI
- [x] Official Star Citizen logo in header

## Architecture
```
/app/
├── backend/
│   ├── .env (MONGO_URL, DB_NAME, JWT_SECRET, STAR_CITIZEN_API_KEY)
│   ├── server.py (FastAPI endpoints, ship/vehicle/component/weapon data)
│   ├── ship_data_enhancer.py (Wiki image fetching & caching, ship data enrichment)
│   └── requirements.txt
└── frontend/
    ├── .env (REACT_APP_BACKEND_URL)
    └── src/
        ├── App.js (routes, auth context)
        ├── components/ (Layout, SpaceshipIcon, ui/)
        └── pages/ (Login, Dashboard, Ships, ShipDetail, Vehicles, Components, Weapons, Fleet, Compare, LoadoutBuilder)
```

## API Endpoints
- POST /api/auth/login
- GET /api/ships, /api/ships/{ship_id}
- GET /api/vehicles
- GET /api/components
- GET /api/weapons
- GET /api/upgrades/{ship_id}
- POST /api/fleet/add
- GET /api/fleet/my
- DELETE /api/fleet/{fleet_id}

## Prioritized Backlog

### P0 (Critical)
- All critical features implemented and tested

### P1 (High)
- **Ship Comparison Tool**: Build out ComparePage.jsx for side-by-side ship comparison
- **Loadout Builder**: Develop LoadoutBuilder.jsx for ship loadout customization

### P2 (Medium)
- **Live API Integration**: Robustly implement Star Citizen Wiki API with mock data fallback
- **Data Migration**: Move mock data from server.py into MongoDB collections

### P3 (Low)
- Enhanced fleet statistics and analytics
- Mobile-responsive improvements
- Export fleet data functionality
