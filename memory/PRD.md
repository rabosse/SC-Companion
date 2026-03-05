# Star Citizen Fleet Manager - PRD

## Original Problem Statement
Build a full-stack "Star Citizen Fleet Manager" application to allow players to track their ships, ground vehicles, components, weapons, and personal gear from the game Star Citizen. The app integrates with Star Citizen community APIs for live game data.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn UI + framer-motion
- **Backend**: FastAPI + MongoDB + JWT Auth
- **Data Sources**: `starcitizen.tools` Wiki API, `cstone.space` API
- **Database**: MongoDB (users, saved_loadouts, price_history)

## Core Requirements
- User authentication (username/password, JWT)
- Fleet management (add/remove ships/vehicles)
- Ship/vehicle pages with variants and official images
- Ship comparison tool
- Loadout builder with savable/shareable loadouts
- Dashboard with fleet statistics
- Components and Weapons pages with filtering
- Personal Gear section (Armor, FPS Weapons, Equipment, Backpacks)
- Route planner with fuel calculations
- Interdiction planner
- Real-time price tracking

## What's Been Implemented
### Phase 1 (Complete)
- User auth (register/login with JWT)
- Fleet management (add/remove ships)
- Ships & Vehicles pages with variant dropdowns
- Ship comparison tool
- Dashboard with fleet stats
- Components & Weapons pages
- Loadout builder with savable loadouts

### Phase 2 (Complete)
- Personal Gear section (Armor, FPS Weapons, Equipment) unified UI
- Backpacks correctly categorized under Armor
- 27 new armor sets added from CStone API
- Backend code refactored into modular enhancers

### Phase 3 (Complete - Feb 2026)
- **Route Planner Overhaul**: Complete redesign with Mobi-Glass HUD aesthetic, fuel consumption model, fuel stops at rest stations, cross-system routing with jump waypoints
- **Fleet Integration**: Toggle switch between Fleet ships and All Ships in route planner ship selector; ship QD stats (speed, range, fuel) displayed
- **Weapon Hardpoint Accuracy**: Curated per-ship hardpoint mapping for 100+ ships replacing generic size-based approximation; ships now expose quantum drive data from the Wiki API
- **Starmap Visual Overhaul**: Complete rewrite of the star map canvas with requestAnimationFrame animation loop — 500 twinkling stars, per-system nebula glow (blue Stanton, red Pyro, purple Nyx), multi-layer star halos, atmospheric planet bodies, diamond gateways, pulsing node highlights, animated flowing route lines, HUD scan-line sweep, smart zoom-based labels, orbit rings
- **Gear Tab Unification**: Equipment tab rewritten to match Armor/Weapons layout — 3-column card grid, large image headers, type/subtype badges, Buy/Loot location sections, variant selector, and detail modal all unified across all 3 gear tabs

## Prioritized Backlog
### P1 - Next
- Real-time price tracking improvements for in-game items
- Interdiction planner enhancements (advanced planning)

### P2 - Future
- RSI fleet import tool
- Price change alerts for fleet ships
- Community loadout voting/rating system
- Fleet value tracking over time
