# Star Citizen Fleet Manager (Companion) - PRD

## Original Problem Statement
Build a full-stack application called "Star Citizen Fleet Manager" / "Star Citizen Companion" for players to track ships, ground vehicles, components, weapons, and personal gear from Star Citizen.

## Architecture
- **Frontend**: React, Tailwind CSS, Shadcn UI, react-router-dom, axios, lucide-react, framer-motion
- **Backend**: FastAPI, Pydantic, JWT auth, modular routing (APIRouter)
- **Database**: MongoDB
- **External APIs**: starcitizen.tools (wiki), finder.cstone.space (CStone armor/weapon/gadget/backpack data)

## Backend Module Structure
```
/app/backend/
├── server.py                # Main FastAPI app, startup events
├── armor_enhancer.py        # CStone + Wiki images for armor & backpacks (81 items)
├── weapon_enhancer.py       # CStone + Wiki images for FPS weapons (50 weapons)
├── equipment_enhancer.py    # CStone gadget images for equipment (26 items)
├── ship_data_enhancer.py    # Wiki images for ships/vehicles (re-exports)
├── personal_gear.py         # Static data for armor, weapons, equipment
├── routes/gear.py           # /api/gear/* endpoints
```

## What's Been Implemented
- User authentication, fleet management, ship comparison, loadout builder
- Route planner, price tracker, dashboard
- Personal Gear section - ALL 3 tabs:
  - **Armor Sets (81)**: 55 torso armor + 26 backpacks, all with CStone images, variant selectors, loot/purchase locations
  - **FPS Weapons (50)**: CStone images, per-variant pricing/locations/loot
  - **Equipment (26)**: Mining tools, undersuits, scanners, medical devices

## Completed (Mar 2026 - This Session)
1. FPS Weapons tab CStone integration
2. Equipment tab CStone integration
3. Refactored ship_data_enhancer.py into 4 focused modules
4. Added 27 missing armor sets from CStone
5. Migrated backpacks from Equipment to Armor tab (26 CStone backpack sets)
6. Backpack cards hide irrelevant temp/radiation stats
7. All tests passed: iterations 17-20 (100%)

## Backlog
- P2: Price change alerts for fleet ships
- P3: Wiki image integration for equipment without CStone coverage
- P3: Community loadout voting/rating system
- P3: Fleet value tracking over time
