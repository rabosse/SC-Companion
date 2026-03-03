# Star Citizen Fleet Manager - PRD

## Original Problem Statement
Build a full-stack application called "Star Citizen Fleet Manager" that allows Star Citizen players to track their ships and ground vehicles. The app should use the Star Citizen API for data, support user authentication, fleet management, ship/vehicle images, component/weapon browsing with filters, ship comparison, and loadout building.

## Core Requirements
- User authentication (Username + Password with bcrypt hashing)
- Ship database with real images from Star Citizen Wiki
- Ground vehicle database with images
- Component catalog with size filtering, location, aUEC price
- Weapons arsenal with size filtering, location, aUEC price
- Personal fleet management (add/remove ships, persists to MongoDB)
- Fleet statistics dashboard
- Ship comparison tool (up to 5 ships)
- Loadout builder with SIZE RESTRICTIONS + saveable loadouts
- In-game purchase locations + aUEC prices for ships/vehicles
- RSI Pledge Store prices (USD) + direct links
- Star Citizen themed UI
- LIVE API integration with mock fallback
- Loadout sharing between users with community page

## Tech Stack
- **Frontend**: React, Tailwind CSS, Shadcn UI, Framer Motion, react-router-dom, axios
- **Backend**: FastAPI, Pydantic, JWT auth (python-jose), bcrypt, httpx
- **Database**: MongoDB (users, fleet, loadouts)
- **Image Source**: starcitizen.tools MediaWiki API
- **Data Source**: api.star-citizen.wiki LIVE API with mock fallback
- **Purchase Data**: starcitizen.tools wiki (static mapping of 130+ ships/vehicles)

## What's Implemented (as of Mar 3, 2026)
- [x] Username + Password login with bcrypt (auto-register on first login)
- [x] LIVE API: 276 ships, 178 weapons, 333 components from api.star-citizen.wiki
- [x] Ship images: 275/276 ships (99.6%) and 13/13 vehicles (100%) have images
- [x] In-game purchase locations: 130+ ships with all dealers and aUEC prices
- [x] RSI Pledge Store: USD prices + pledge URLs for all ships from live API
- [x] Ship detail "Where to Buy" section with all dealers + RSI store link
- [x] Component catalog: search, type filter, SIZE FILTER, real locations, real prices
- [x] Weapons arsenal: search, type filter, SIZE FILTER, real locations, real prices
- [x] Fleet management: add/remove ships, persists to MongoDB across sessions
- [x] Ship Comparison Tool: up to 5 ships with stat bars and best-value highlighting
- [x] Loadout Builder: SIZE RESTRICTIONS enforced, save/load/delete named loadouts to MongoDB
- [x] Dashboard with live stats (276 ships, 13 vehicles, 333 components, 178 weapons)
- [x] Auth persistence on page reload
- [x] Full navigation: Dashboard, My Fleet, Ships, Vehicles, Components, Weapons, Compare, Loadout, Community
- [x] Quick Fleet Import: Bulk-add ships via modal with search, manufacturer/size filters, multi-select
- [x] Data Auto-Refresh: TTL-based (1 hour) live API data refresh on app launch
- [x] **Loadout Sharing**: Save loadouts with share codes, shareable links
- [x] **Community Loadouts Page**: Browse all shared loadouts, search by ship, pagination
- [x] **Public Shared Loadout View**: Anyone can view a shared loadout (no login required)
- [x] **Clone Loadouts**: Authenticated users can clone any shared loadout to their collection
- [x] Deployment health check: PASSED - ready for production

## Architecture
```
/app/
├── backend/
│   ├── .env (MONGO_URL, DB_NAME, JWT_SECRET, STAR_CITIZEN_API_KEY)
│   ├── server.py (FastAPI endpoints, auth, fleet, loadout CRUD, community sharing)
│   ├── live_api.py (Live Star Citizen Wiki API + hardpoint data)
│   ├── ship_data_enhancer.py (Wiki image fetching by name, variant matching)
│   ├── ship_purchases.py (In-game purchase locations & aUEC prices)
│   └── requirements.txt
└── frontend/
    ├── .env (REACT_APP_BACKEND_URL)
    └── src/
        ├── App.js (routes, auth context with username/password)
        ├── components/ (Layout, SpaceshipIcon, ui/)
        └── pages/ (Login, Dashboard, Ships, ShipDetail, Vehicles, Components, Weapons, Fleet, Compare, LoadoutBuilder, CommunityLoadouts, SharedLoadout)
```

## API Endpoints
- POST /api/auth/login {username, password} - login/auto-register
- POST /api/auth/register {username, password}
- GET /api/ships (live API, includes purchase_locations, price_auec, msrp, pledge_url)
- GET /api/vehicles (includes purchase data)
- GET /api/components (live API with real locations/prices)
- GET /api/weapons (live API with real locations/prices)
- POST /api/fleet/add, GET /api/fleet/my, DELETE /api/fleet/{fleet_id}
- POST /api/fleet/bulk-add {ships: [{id, name, manufacturer}]} - Quick Import
- POST /api/loadouts/save (returns share_code), GET /api/loadouts/{ship_id}, DELETE /api/loadouts/{loadout_id}
- GET /api/loadouts/my/all - All user's loadouts
- GET /api/community/loadouts (PUBLIC - paginated, search by ship_name)
- GET /api/community/loadouts/{share_code} (PUBLIC - view shared loadout)
- POST /api/loadouts/clone/{share_code} (AUTH - clone to user's collection)
- GET /api/upgrades/{ship_id}

## Prioritized Backlog

### P2 (Medium)
- Data migration from static mappings to MongoDB collections
- Fleet value tracking over time
- Mobile-responsive optimizations

### P3 (Low)
- Export fleet/loadout data
- Enhanced fleet statistics and analytics
- Loadout ratings/votes in community page
