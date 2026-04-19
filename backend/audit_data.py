"""
Data Accuracy Audit Script
Cross-references app data against scunpacked-data (DataForge extracted game data)
for Ships, Vehicles, Weapons, Components, and FPS Gear.
"""

import asyncio
import httpx
import json
import logging
import os
import sys

sys.path.insert(0, '/app/backend')

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

SCUNPACKED = "https://raw.githubusercontent.com/StarCitizenWiki/scunpacked-data/master"
APP_API = os.environ.get("APP_API", "")

# ---------- Fetch reference data from scunpacked (DataForge game data) ----------

async def fetch_reference_data():
    """Fetch all reference data from scunpacked-data repo."""
    async with httpx.AsyncClient(timeout=60) as client:
        logger.info("Fetching scunpacked-data (game files)...")
        ships_r, items_r, fps_r = await asyncio.gather(
            client.get(f"{SCUNPACKED}/ships.json"),
            client.get(f"{SCUNPACKED}/ship-items.json"),
            client.get(f"{SCUNPACKED}/fps-items.json"),
        )
    return {
        "ships": ships_r.json(),
        "ship_items": items_r.json(),
        "fps_items": fps_r.json(),
    }


async def fetch_app_data(api_url: str, token: str):
    """Fetch all data from our app's API."""
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=120) as client:
        logger.info("Fetching app data...")
        ships_r = await client.get(f"{api_url}/api/ships", headers=headers)
        logger.info(f"  Ships: {ships_r.status_code}")
        vehicles_r = await client.get(f"{api_url}/api/vehicles", headers=headers)
        logger.info(f"  Vehicles: {vehicles_r.status_code}")
        weapons_r = await client.get(f"{api_url}/api/weapons", headers=headers)
        logger.info(f"  Weapons: {weapons_r.status_code}")
        comps_r = await client.get(f"{api_url}/api/components", headers=headers)
        logger.info(f"  Components: {comps_r.status_code}")
        gear_weapons_r = await client.get(f"{api_url}/api/gear/weapons", headers=headers)
        logger.info(f"  FPS Weapons: {gear_weapons_r.status_code}")
    return {
        "ships": ships_r.json().get("data", []),
        "vehicles": vehicles_r.json().get("data", []),
        "weapons": weapons_r.json().get("data", []),
        "components": comps_r.json().get("data", []),
        "fps_weapons": gear_weapons_r.json().get("data", []),
    }


# ---------- Normalization helpers ----------

def norm(name):
    """Normalize a name for fuzzy matching."""
    if not name:
        return ""
    return name.lower().replace("-", " ").replace("_", " ").replace("'", "").replace("\"", "").strip()


def match_ship(app_ship, ref_ships):
    """Find the best matching reference ship for an app ship."""
    app_name = norm(app_ship.get("name", ""))
    app_mfr = norm(app_ship.get("manufacturer", ""))

    # Direct name match
    for ref in ref_ships:
        ref_name = norm(ref.get("Name", ""))
        if app_name == ref_name or app_name in ref_name or ref_name in app_name:
            return ref

    # Try manufacturer + short name
    for ref in ref_ships:
        ref_name = norm(ref.get("Name", ""))
        mfr_name = norm(ref.get("Manufacturer", {}).get("Name", ""))
        # Strip manufacturer prefix from ref name
        short_ref = ref_name.replace(mfr_name, "").strip()
        if app_name == short_ref or short_ref == app_name:
            return ref

    return None


def extract_weapon_hardpoints(ref_ship):
    """Extract weapon hardpoint info from scunpacked loadout data."""
    hardpoints = []
    loadout = ref_ship.get("Loadout", [])
    for item in loadout:
        hp_type = item.get("Type", "")
        if "Turret.GunTurret" in hp_type:
            editable = item.get("Editable", False)
            max_size = item.get("MaxSize", 0)
            hp_name = item.get("HardpointName", "")
            children = item.get("Children", [])
            # Count child gun slots
            gun_children = [c for c in children if "WeaponGun" in c.get("Type", "") or "Gun" in c.get("Type", "")]
            if editable:
                hardpoints.append({
                    "name": hp_name,
                    "max_size": max_size,
                    "gun_count": max(len(gun_children), 1),
                    "type": "weapon",
                })
    return hardpoints


def extract_component_slots(ref_ship):
    """Extract component slots (shields, power, cooler, QD) from loadout."""
    slots = {"shield": [], "power": [], "cooler": [], "qd": []}
    loadout = ref_ship.get("Loadout", [])
    for item in loadout:
        hp_type = item.get("Type", "")
        editable = item.get("Editable", True)
        max_size = item.get("MaxSize", 0)
        if "Shield" in hp_type and editable:
            slots["shield"].append(max_size)
        elif "PowerPlant" in hp_type and editable:
            slots["power"].append(max_size)
        elif "Cooler" in hp_type and editable:
            slots["cooler"].append(max_size)
        elif "QuantumDrive" in hp_type and editable:
            slots["qd"].append(max_size)
    return slots


# ---------- Audit functions ----------

def audit_ships(app_ships, ref_ships):
    """Audit ship data accuracy."""
    report = {"category": "Ships", "total_app": len(app_ships), "total_ref": len(ref_ships),
              "matched": 0, "unmatched": [], "issues": []}

    ref_spaceships = [s for s in ref_ships if s.get("IsSpaceship") and not s.get("IsVehicle")]

    for app_ship in app_ships:
        ref = match_ship(app_ship, ref_spaceships)
        if not ref:
            report["unmatched"].append(app_ship.get("name", "?"))
            continue

        report["matched"] += 1
        ship_name = app_ship.get("name", "?")
        issues = []

        # Check basic stats
        checks = [
            ("crew", app_ship.get("crew"), ref.get("Crew")),
            ("cargo", app_ship.get("cargo"), ref.get("Cargo", {}).get("CargoGrid") if isinstance(ref.get("Cargo"), dict) else ref.get("Cargo")),
            ("length", app_ship.get("length"), ref.get("Length")),
            ("width", app_ship.get("width"), ref.get("Width")),
            ("height", app_ship.get("height"), ref.get("Height")),
            ("mass", app_ship.get("mass"), ref.get("Mass")),
        ]

        for field, app_val, ref_val in checks:
            if app_val is not None and ref_val is not None:
                try:
                    a = float(app_val)
                    r = float(ref_val)
                    if r > 0 and abs(a - r) / r > 0.1:  # >10% difference
                        issues.append({
                            "field": field, "severity": "MEDIUM",
                            "app_value": app_val, "ref_value": ref_val,
                        })
                except (ValueError, TypeError):
                    pass

        # Check SCM speed
        ref_scm = ref.get("FlightCharacteristics", {}).get("IFCS", {}).get("ScmSpeed")
        app_scm = app_ship.get("scm_speed") or app_ship.get("speed")
        if app_scm and ref_scm:
            try:
                if abs(float(app_scm) - float(ref_scm)) > 5:
                    issues.append({
                        "field": "scm_speed", "severity": "MEDIUM",
                        "app_value": app_scm, "ref_value": ref_scm,
                    })
            except (ValueError, TypeError):
                pass

        # Check weapon hardpoints
        ref_hps = extract_weapon_hardpoints(ref)
        app_hps = app_ship.get("hardpoints", {}).get("weapons", [])
        if isinstance(app_hps, list):
            app_weapon_sizes = sorted([int(h) if isinstance(h, (int, float)) else int(h.get("maxSize", h.get("size", 0))) for h in app_hps], reverse=True)
        else:
            app_weapon_sizes = []
        ref_weapon_sizes = sorted([h["max_size"] for h in ref_hps], reverse=True)

        if app_weapon_sizes != ref_weapon_sizes:
            issues.append({
                "field": "weapon_hardpoints", "severity": "CRITICAL",
                "app_value": f"{len(app_weapon_sizes)}x weapons {app_weapon_sizes}",
                "ref_value": f"{len(ref_weapon_sizes)}x weapons {ref_weapon_sizes}",
            })

        # Check component slots
        ref_comps = extract_component_slots(ref)
        app_hardpoints = app_ship.get("hardpoints", {})

        comp_map = {
            "shield": "shield",
            "power": "power_plant",
            "cooler": "cooler",
            "qd": "quantum_drive",
        }
        for ref_key, app_key in comp_map.items():
            ref_sizes = sorted(ref_comps.get(ref_key, []), reverse=True)
            app_comp = app_hardpoints.get(app_key, {})
            if isinstance(app_comp, dict):
                app_sizes = sorted([app_comp.get("size", 0)] * app_comp.get("count", 0), reverse=True)
            elif isinstance(app_comp, list):
                app_sizes = sorted([int(s) if isinstance(s, (int, float)) else int(s.get("size", 0)) for s in app_comp], reverse=True)
            else:
                app_sizes = []
            if app_sizes != ref_sizes and ref_sizes:
                issues.append({
                    "field": f"component_{ref_key}", "severity": "HIGH",
                    "app_value": f"{len(app_sizes)}x {ref_key} S{app_sizes}",
                    "ref_value": f"{len(ref_sizes)}x {ref_key} S{ref_sizes}",
                })

        # Check manufacturer
        ref_mfr = ref.get("Manufacturer", {}).get("Name", "")
        app_mfr = app_ship.get("manufacturer", "")
        if ref_mfr and app_mfr and norm(app_mfr) != norm(ref_mfr):
            issues.append({
                "field": "manufacturer", "severity": "LOW",
                "app_value": app_mfr, "ref_value": ref_mfr,
            })

        # Check role/type
        ref_role = ref.get("Role", "")
        app_role = app_ship.get("type") or app_ship.get("role", "")
        if ref_role and app_role and norm(app_role) != norm(ref_role):
            issues.append({
                "field": "role", "severity": "LOW",
                "app_value": app_role, "ref_value": ref_role,
            })

        if issues:
            report["issues"].append({"name": ship_name, "ref_name": ref.get("Name", ""), "issues": issues})

    return report


def audit_vehicles(app_vehicles, ref_ships):
    """Audit ground vehicle data."""
    report = {"category": "Vehicles", "total_app": len(app_vehicles), "matched": 0,
              "unmatched": [], "issues": []}

    ref_vehicles = [s for s in ref_ships if s.get("IsVehicle")]
    report["total_ref"] = len(ref_vehicles)

    for app_v in app_vehicles:
        ref = match_ship(app_v, ref_vehicles)
        if not ref:
            report["unmatched"].append(app_v.get("name", "?"))
            continue

        report["matched"] += 1
        v_name = app_v.get("name", "?")
        issues = []

        checks = [
            ("crew", app_v.get("crew"), ref.get("Crew")),
            ("mass", app_v.get("mass"), ref.get("Mass")),
        ]
        for field, app_val, ref_val in checks:
            if app_val is not None and ref_val is not None:
                try:
                    a, r = float(app_val), float(ref_val)
                    if r > 0 and abs(a - r) / r > 0.1:
                        issues.append({"field": field, "severity": "MEDIUM", "app_value": app_val, "ref_value": ref_val})
                except (ValueError, TypeError):
                    pass

        ref_mfr = ref.get("Manufacturer", {}).get("Name", "")
        app_mfr = app_v.get("manufacturer", "")
        if ref_mfr and app_mfr and norm(app_mfr) != norm(ref_mfr):
            issues.append({"field": "manufacturer", "severity": "LOW", "app_value": app_mfr, "ref_value": ref_mfr})

        if issues:
            report["issues"].append({"name": v_name, "ref_name": ref.get("Name", ""), "issues": issues})

    return report


def audit_ship_weapons(app_weapons, ref_items):
    """Audit ship weapon data."""
    ref_weapons = [i for i in ref_items if i.get("type") == "WeaponGun"]
    report = {"category": "Ship Weapons", "total_app": len(app_weapons),
              "total_ref": len(ref_weapons), "matched": 0, "unmatched": [], "issues": []}

    for app_w in app_weapons:
        app_name = norm(app_w.get("name", ""))
        matched = None
        for ref_w in ref_weapons:
            ref_name = norm(ref_w.get("name", ""))
            if app_name == ref_name or app_name in ref_name or ref_name in app_name:
                matched = ref_w
                break

        if not matched:
            report["unmatched"].append(app_w.get("name", "?"))
            continue

        report["matched"] += 1
        issues = []

        # Check size
        app_size = int(app_w.get("size", 0))
        ref_size = int(matched.get("size", 0))
        if app_size != ref_size and ref_size > 0:
            issues.append({"field": "size", "severity": "CRITICAL", "app_value": app_size, "ref_value": ref_size})

        if issues:
            report["issues"].append({"name": app_w.get("name", "?"), "issues": issues})

    return report


def audit_components(app_components, ref_items):
    """Audit ship component data."""
    comp_types = {"Shield", "PowerPlant", "Cooler", "QuantumDrive", "Radar"}
    ref_comps = [i for i in ref_items if i.get("type") in comp_types]
    report = {"category": "Components", "total_app": len(app_components),
              "total_ref": len(ref_comps), "matched": 0, "unmatched": [], "issues": []}

    for app_c in app_components:
        app_name = norm(app_c.get("name", ""))
        matched = None
        for ref_c in ref_comps:
            ref_name = norm(ref_c.get("name", ""))
            if app_name == ref_name or app_name in ref_name or ref_name in app_name:
                matched = ref_c
                break

        if not matched:
            report["unmatched"].append(app_c.get("name", "?"))
            continue

        report["matched"] += 1
        issues = []

        app_size = int(app_c.get("size", 0))
        ref_size = int(matched.get("size", 0))
        if app_size != ref_size and ref_size > 0:
            issues.append({"field": "size", "severity": "HIGH", "app_value": app_size, "ref_value": ref_size})

        app_grade = str(app_c.get("grade", ""))
        ref_grade = str(matched.get("grade", ""))
        if app_grade and ref_grade and app_grade != ref_grade:
            issues.append({"field": "grade", "severity": "MEDIUM", "app_value": app_grade, "ref_value": ref_grade})

        if issues:
            report["issues"].append({"name": app_c.get("name", "?"), "issues": issues})

    return report


def audit_fps_weapons(app_fps, ref_fps_items):
    """Audit FPS weapon data."""
    ref_fps = [i for i in ref_fps_items if i.get("type") == "WeaponPersonal"]
    report = {"category": "FPS Weapons", "total_app": len(app_fps),
              "total_ref": len(ref_fps), "matched": 0, "unmatched": [], "issues": []}

    for app_w in app_fps:
        app_name = norm(app_w.get("name", ""))
        matched = None
        for ref_w in ref_fps:
            ref_name = norm(ref_w.get("name", ""))
            if app_name == ref_name or app_name in ref_name or ref_name in app_name:
                matched = ref_w
                break
        if not matched:
            report["unmatched"].append(app_w.get("name", "?"))
            continue
        report["matched"] += 1

    return report


# ---------- Report generation ----------

def generate_report(reports):
    """Generate a formatted audit report."""
    lines = []
    lines.append("=" * 80)
    lines.append("  STAR CITIZEN FLEET MANAGER — DATA ACCURACY AUDIT")
    lines.append("  Source: scunpacked-data (DataForge game files)")
    lines.append("=" * 80)

    total_critical = 0
    total_high = 0
    total_medium = 0
    total_low = 0

    for report in reports:
        cat = report["category"]
        lines.append(f"\n{'─' * 60}")
        lines.append(f"  {cat.upper()}")
        lines.append(f"  App: {report['total_app']} | Reference: {report['total_ref']} | Matched: {report['matched']}")
        if report.get("unmatched"):
            lines.append(f"  Unmatched ({len(report['unmatched'])}): {', '.join(report['unmatched'][:10])}")
            if len(report['unmatched']) > 10:
                lines.append(f"    ...and {len(report['unmatched']) - 10} more")
        lines.append(f"  Issues found: {len(report['issues'])}")

        for entry in report["issues"]:
            name = entry.get("name", "?")
            ref_name = entry.get("ref_name", "")
            ref_note = f" (ref: {ref_name})" if ref_name and ref_name != name else ""
            lines.append(f"\n  [{name}]{ref_note}")
            for issue in entry["issues"]:
                sev = issue["severity"]
                if sev == "CRITICAL": total_critical += 1
                elif sev == "HIGH": total_high += 1
                elif sev == "MEDIUM": total_medium += 1
                else: total_low += 1
                lines.append(f"    [{sev}] {issue['field']}: app={issue['app_value']} | game={issue['ref_value']}")

    lines.append(f"\n{'=' * 80}")
    lines.append(f"  SUMMARY")
    lines.append(f"  CRITICAL: {total_critical} | HIGH: {total_high} | MEDIUM: {total_medium} | LOW: {total_low}")
    lines.append(f"  Total issues: {total_critical + total_high + total_medium + total_low}")
    lines.append(f"{'=' * 80}")

    return "\n".join(lines)


async def main():
    # Use localhost for internal API calls (faster, no proxy timeout)
    api_url = "http://localhost:8001"

    # Login to get token
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{api_url}/api/auth/login",
                                 json={"username": "audit_user", "password": "audit_pass"})
        token = resp.json()["access_token"]

    # Fetch all data
    ref_data = await fetch_reference_data()
    app_data = await fetch_app_data(api_url, token)

    logger.info(f"Reference: {len(ref_data['ships'])} ships, {len(ref_data['ship_items'])} ship items, {len(ref_data['fps_items'])} fps items")
    logger.info(f"App: {len(app_data['ships'])} ships, {len(app_data['vehicles'])} vehicles, {len(app_data['weapons'])} weapons, {len(app_data['components'])} components, {len(app_data['fps_weapons'])} fps weapons")

    # Run audits
    reports = []
    reports.append(audit_ships(app_data["ships"], ref_data["ships"]))
    reports.append(audit_vehicles(app_data["vehicles"], ref_data["ships"]))
    reports.append(audit_ship_weapons(app_data["weapons"], ref_data["ship_items"]))
    reports.append(audit_components(app_data["components"], ref_data["ship_items"]))
    reports.append(audit_fps_weapons(app_data["fps_weapons"], ref_data["fps_items"]))

    # Generate and save report
    report_text = generate_report(reports)
    print(report_text)

    with open("/app/audit_report.txt", "w") as f:
        f.write(report_text)
    logger.info("Report saved to /app/audit_report.txt")

    # Also save as JSON for programmatic use
    with open("/app/audit_report.json", "w") as f:
        json.dump(reports, f, indent=2, default=str)
    logger.info("JSON report saved to /app/audit_report.json")


if __name__ == "__main__":
    asyncio.run(main())
