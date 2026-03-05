# Star Citizen Fleet Manager (Companion) - PRD

## Original Problem Statement
Build a full-stack application called "Star Citizen Fleet Manager" / "Star Citizen Companion" for players to track ships, ground vehicles, components, weapons, and personal gear from Star Citizen.

## Architecture
- **Frontend**: React, Tailwind CSS, Shadcn UI, react-router-dom, axios, lucide-react, framer-motion
- **Backend**: FastAPI, Pydantic, JWT auth, modular routing (APIRouter)
- **Database**: MongoDB
- **External APIs**: starcitizen.tools (wiki), finder.cstone.space (CStone)

## What's Been Implemented
- User auth, fleet management, ship comparison, loadout builder, route planner, price tracker, dashboard
- **Ships page**: 203 unique ships (deduped), variant dropdowns for cosmetic editions (PYAM Exec, Wikelo, etc.)
- **Vehicles page**: 12 vehicles with variant dropdowns where applicable
- **Gear section**: Armor (81 items incl. 26 backpacks), FPS Weapons (50), Equipment (26)
  - All with CStone images, variant selectors, loot/purchase locations

## Completed (Mar 2026 - This Session)
1. FPS Weapons tab CStone integration
2. Equipment tab CStone integration
3. Refactored ship_data_enhancer.py into 4 focused modules
4. Added 27 missing armor sets from CStone
5. Migrated backpacks from Equipment to Armor tab (26 CStone backpack sets)
6. Fixed duplicate ships (17 duplicates removed) and added variant grouping (41 ships with variants)
7. Added variant dropdown to Ships and Vehicles pages
8. All tests passed: iterations 17-21 (100%)

## Backlog
- P2: Price change alerts for fleet ships
- P3: Wiki image integration for equipment without CStone coverage
- P3: Community loadout voting/rating system
- P3: Fleet value tracking over time
