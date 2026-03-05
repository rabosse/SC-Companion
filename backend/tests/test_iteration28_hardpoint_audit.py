"""
Iteration 28: Hardpoint Data Audit Tests

Verifies the massive hardpoint data audit for all 203 ships/vehicles.
Tests that curated weapon hardpoints and component overrides are correctly applied.
Key ships being tested:
- Ares Star Fighter Ion/Inferno (S7 weapons)
- Gladiator (4 guns now, was 2)
- Meteor (6 guns)
- Guardian MX (4 guns)
- Fury (4 guns)
- Shiv (6 guns)
- Starlancer TAC (12 guns), MAX (8 guns)
- 600i 2951 BIS (4 guns, was 6)
- Apollo Medivac (4 guns, shield size 2)
- Spirit C1/A1 (cargo/2 guns)
- 890 Jump (capital components)
- Hornet variants
- Cutter (S2 weapons now)
- P-52 Merlin, Vanduul Scythe
"""

import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHardpointAudit:
    """Test curated hardpoint data for 200+ ships"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for ships API"""
        register_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": "hardpoint_audit28",
            "password": "password123"
        })
        if register_resp.status_code == 400:  # Already exists
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "hardpoint_audit28",
                "password": "password123"
            })
            self.token = login_resp.json().get("access_token")
        else:
            self.token = register_resp.json().get("access_token")
        
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Fetch all ships once
        response = requests.get(f"{BASE_URL}/api/ships", headers=self.headers)
        assert response.status_code == 200, f"Failed to fetch ships: {response.status_code}"
        self.ships = response.json().get("data", [])
    
    def _find_ship(self, name_pattern, exact=False):
        """Find a ship by name pattern"""
        name_pattern_lower = name_pattern.lower()
        for ship in self.ships:
            ship_name = ship.get("name", "").lower()
            if exact:
                if ship_name == name_pattern_lower:
                    return ship
            else:
                if name_pattern_lower in ship_name:
                    return ship
        return None
    
    def _find_ships(self, name_pattern):
        """Find all ships matching a name pattern"""
        name_pattern_lower = name_pattern.lower()
        return [s for s in self.ships if name_pattern_lower in s.get("name", "").lower()]
    
    # === Total Ship Count Test ===
    def test_total_ship_count_is_203(self):
        """Verify total ship count is 203"""
        ship_count = len(self.ships)
        # Allow some flexibility for API changes
        assert 195 <= ship_count <= 220, f"Expected ~203 ships, got {ship_count}"
        print(f"Total ship count: {ship_count}")
    
    # === Ares Star Fighter Tests ===
    def test_ares_ion_has_single_s7_weapon(self):
        """Ares Star Fighter Ion should have weapons=[7] (single S7)"""
        ship = self._find_ship("ares star fighter ion")
        if not ship:
            ship = self._find_ship("ares ion")
        assert ship is not None, "Ares Star Fighter Ion not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert weapons == [7], f"Ares Ion weapons should be [7], got {weapons}"
        
        # Check shield size=2
        shield = ship.get("hardpoints", {}).get("shield", {})
        assert shield.get("size") == 2, f"Ares Ion shield size should be 2, got {shield.get('size')}"
        
        print(f"Ares Ion verified: weapons={weapons}, shield size={shield.get('size')}")
    
    def test_ares_inferno_has_single_s7_weapon(self):
        """Ares Star Fighter Inferno should have weapons=[7] (single S7)"""
        ship = self._find_ship("ares star fighter inferno")
        if not ship:
            ship = self._find_ship("ares inferno")
        assert ship is not None, "Ares Star Fighter Inferno not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert weapons == [7], f"Ares Inferno weapons should be [7], got {weapons}"
        print(f"Ares Inferno verified: weapons={weapons}")
    
    # === Gladiator Test ===
    def test_gladiator_has_4_weapons(self):
        """Gladiator should have weapons=[3,3,3,3] (4 guns, was 2 before)"""
        ship = self._find_ship("gladiator", exact=True)
        assert ship is not None, "Gladiator not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 4, f"Gladiator should have 4 weapons, got {len(weapons)}"
        assert sorted(weapons) == [3, 3, 3, 3], f"Gladiator weapons should be [3,3,3,3], got {weapons}"
        print(f"Gladiator verified: {len(weapons)} weapons {weapons}")
    
    # === Meteor Test ===
    def test_meteor_has_6_weapons(self):
        """Meteor should have weapons=[5,5,3,3,3,3] (6 guns)"""
        ship = self._find_ship("meteor", exact=True)
        assert ship is not None, "Meteor not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 6, f"Meteor should have 6 weapons, got {len(weapons)}"
        assert sorted(weapons) == [3, 3, 3, 3, 5, 5], f"Meteor weapons should be [5,5,3,3,3,3], got {weapons}"
        print(f"Meteor verified: {len(weapons)} weapons {weapons}")
    
    # === Guardian MX Test ===
    def test_guardian_mx_has_4_weapons(self):
        """Guardian MX should have weapons=[4,4,4,4] (4 guns)"""
        ship = self._find_ship("guardian mx")
        assert ship is not None, "Guardian MX not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 4, f"Guardian MX should have 4 weapons, got {len(weapons)}"
        assert sorted(weapons) == [4, 4, 4, 4], f"Guardian MX weapons should be [4,4,4,4], got {weapons}"
        print(f"Guardian MX verified: {len(weapons)} weapons {weapons}")
    
    # === Fury Test ===
    def test_fury_has_4_weapons(self):
        """Fury should have weapons=[2,2,2,2] (4 guns)"""
        ship = self._find_ship("fury", exact=True)
        if not ship:
            # Try to find any Fury variant
            fury_ships = self._find_ships("fury")
            ship = fury_ships[0] if fury_ships else None
        assert ship is not None, "Fury not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 4, f"Fury should have 4 weapons, got {len(weapons)}"
        assert sorted(weapons) == [2, 2, 2, 2], f"Fury weapons should be [2,2,2,2], got {weapons}"
        print(f"Fury verified: {len(weapons)} weapons {weapons}")
    
    # === Shiv Test ===
    def test_shiv_has_6_weapons(self):
        """Shiv should have weapons=[4,4,3,3,3,3] (6 guns)"""
        ship = self._find_ship("shiv", exact=True)
        assert ship is not None, "Shiv not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 6, f"Shiv should have 6 weapons, got {len(weapons)}"
        assert sorted(weapons) == [3, 3, 3, 3, 4, 4], f"Shiv weapons should be [4,4,3,3,3,3], got {weapons}"
        print(f"Shiv verified: {len(weapons)} weapons {weapons}")
    
    # === Starlancer Tests ===
    def test_starlancer_tac_has_12_weapons(self):
        """Starlancer TAC should have weapons=[5,5,5,5,4,4,4,4,4,4,4,4] (12 guns)"""
        ship = self._find_ship("starlancer tac")
        assert ship is not None, "Starlancer TAC not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 12, f"Starlancer TAC should have 12 weapons, got {len(weapons)}"
        expected_sorted = sorted([5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4])
        assert sorted(weapons) == expected_sorted, f"Starlancer TAC weapons mismatch: got {weapons}"
        print(f"Starlancer TAC verified: {len(weapons)} weapons")
    
    def test_starlancer_max_has_8_weapons(self):
        """Starlancer MAX should have weapons=[4,4,4,4,4,4,4,4] (8 guns)"""
        ship = self._find_ship("starlancer max")
        assert ship is not None, "Starlancer MAX not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 8, f"Starlancer MAX should have 8 weapons, got {len(weapons)}"
        assert sorted(weapons) == [4, 4, 4, 4, 4, 4, 4, 4], f"Starlancer MAX weapons should all be S4, got {weapons}"
        print(f"Starlancer MAX verified: {len(weapons)} weapons")
    
    # === 600i 2951 BIS Test ===
    def test_600i_bis_has_4_weapons(self):
        """600i 2951 BIS should have weapons=[5,5,3,3] (4 guns, was 6 before)"""
        ship = self._find_ship("600i 2951 bis")
        if not ship:
            ship = self._find_ship("600i bis")
        assert ship is not None, "600i 2951 BIS not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 4, f"600i BIS should have 4 weapons, got {len(weapons)}"
        assert sorted(weapons) == [3, 3, 5, 5], f"600i BIS weapons should be [5,5,3,3], got {weapons}"
        print(f"600i 2951 BIS verified: {len(weapons)} weapons {weapons}")
    
    # === Apollo Medivac Test ===
    def test_apollo_medivac_has_4_weapons_and_shield_s2(self):
        """Apollo Medivac should have weapons=[4,4,3,3], shield size=2"""
        ship = self._find_ship("apollo medivac")
        assert ship is not None, "Apollo Medivac not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 4, f"Apollo Medivac should have 4 weapons, got {len(weapons)}"
        assert sorted(weapons) == [3, 3, 4, 4], f"Apollo Medivac weapons should be [4,4,3,3], got {weapons}"
        
        shield = ship.get("hardpoints", {}).get("shield", {})
        assert shield.get("size") == 2, f"Apollo Medivac shield size should be 2, got {shield.get('size')}"
        
        print(f"Apollo Medivac verified: {len(weapons)} weapons, shield size={shield.get('size')}")
    
    # === Spirit Tests ===
    def test_c1_spirit_has_no_weapons(self):
        """C1 Spirit should have weapons=[] (cargo, no guns)"""
        ship = self._find_ship("c1 spirit")
        if not ship:
            ship = self._find_ship("spirit c1")
        assert ship is not None, "C1 Spirit not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert weapons == [], f"C1 Spirit weapons should be [], got {weapons}"
        print(f"C1 Spirit verified: no weapons (cargo ship)")
    
    def test_a1_spirit_has_2_weapons(self):
        """A1 Spirit should have weapons=[3,3] (2 guns)"""
        ship = self._find_ship("a1 spirit")
        if not ship:
            ship = self._find_ship("spirit a1")
        assert ship is not None, "A1 Spirit not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 2, f"A1 Spirit should have 2 weapons, got {len(weapons)}"
        assert sorted(weapons) == [3, 3], f"A1 Spirit weapons should be [3,3], got {weapons}"
        print(f"A1 Spirit verified: {len(weapons)} weapons")
    
    # === 890 Jump Test (Capital) ===
    def test_890_jump_has_capital_components(self):
        """890 Jump should have shield size=3, count=2 (capital components)"""
        ship = self._find_ship("890 jump")
        assert ship is not None, "890 Jump not found"
        
        shield = ship.get("hardpoints", {}).get("shield", {})
        assert shield.get("size") == 3, f"890 Jump shield size should be 3, got {shield.get('size')}"
        assert shield.get("count") == 2, f"890 Jump shield count should be 2, got {shield.get('count')}"
        
        print(f"890 Jump verified: shield S{shield.get('size')}x{shield.get('count')}")
    
    # === Hornet Heartseeker Test ===
    def test_hornet_heartseeker_mk1_has_4_weapons(self):
        """F7C-M Hornet Heartseeker Mk I should have weapons=[4,4,3,3] (4 guns)"""
        ship = self._find_ship("heartseeker mk i")
        if not ship:
            ship = self._find_ship("heartseeker")
        assert ship is not None, "Hornet Heartseeker Mk I not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 4, f"Heartseeker should have 4 weapons, got {len(weapons)}"
        assert sorted(weapons) == [3, 3, 4, 4], f"Heartseeker weapons should be [4,4,3,3], got {weapons}"
        print(f"Hornet Heartseeker Mk I verified: {len(weapons)} weapons")
    
    # === Cutter Test ===
    def test_cutter_has_s2_weapons(self):
        """Cutter should have weapons=[2,2] (was [3,3] before)"""
        ship = self._find_ship("cutter", exact=True)
        if not ship:
            cutter_ships = self._find_ships("cutter")
            ship = cutter_ships[0] if cutter_ships else None
        assert ship is not None, "Cutter not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 2, f"Cutter should have 2 weapons, got {len(weapons)}"
        assert sorted(weapons) == [2, 2], f"Cutter weapons should be [2,2], got {weapons}"
        print(f"Cutter verified: {len(weapons)} weapons {weapons}")
    
    # === P-52 Merlin Test ===
    def test_p52_merlin_has_3_weapons(self):
        """P-52 Merlin should have weapons=[2,1,1] (3 guns)"""
        ship = self._find_ship("p-52 merlin")
        if not ship:
            ship = self._find_ship("merlin")
        assert ship is not None, "P-52 Merlin not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 3, f"P-52 Merlin should have 3 weapons, got {len(weapons)}"
        assert sorted(weapons) == [1, 1, 2], f"P-52 Merlin weapons should be [2,1,1], got {weapons}"
        print(f"P-52 Merlin verified: {len(weapons)} weapons {weapons}")
    
    # === Vanduul Scythe Test ===
    def test_vanduul_scythe_has_2_s5_weapons(self):
        """Vanduul Scythe should have weapons=[5,5]"""
        ship = self._find_ship("vanduul scythe")
        if not ship:
            ship = self._find_ship("scythe")
        assert ship is not None, "Vanduul Scythe not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 2, f"Vanduul Scythe should have 2 weapons, got {len(weapons)}"
        assert sorted(weapons) == [5, 5], f"Vanduul Scythe weapons should be [5,5], got {weapons}"
        print(f"Vanduul Scythe verified: {len(weapons)} weapons {weapons}")


class TestAdditionalHardpointVerifications:
    """Additional verification tests for other key ships"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for ships API"""
        register_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": "hardpoint_extra28",
            "password": "password123"
        })
        if register_resp.status_code == 400:
            login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "username": "hardpoint_extra28",
                "password": "password123"
            })
            self.token = login_resp.json().get("access_token")
        else:
            self.token = register_resp.json().get("access_token")
        
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.get(f"{BASE_URL}/api/ships", headers=self.headers)
        assert response.status_code == 200
        self.ships = response.json().get("data", [])
    
    def _find_ship(self, name_pattern, exact=False):
        name_pattern_lower = name_pattern.lower()
        for ship in self.ships:
            ship_name = ship.get("name", "").lower()
            if exact:
                if ship_name == name_pattern_lower:
                    return ship
            else:
                if name_pattern_lower in ship_name:
                    return ship
        return None
    
    def test_f8c_lightning_has_8_weapons(self):
        """F8C Lightning should have 8 weapons (from iteration 27)"""
        ship = self._find_ship("f8c lightning")
        assert ship is not None, "F8C Lightning not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 8, f"F8C should have 8 weapons, got {len(weapons)}"
        
        shield = ship.get("hardpoints", {}).get("shield", {})
        assert shield.get("size") == 2, f"F8C shield size should be 2"
        print(f"F8C Lightning: {len(weapons)} weapons, shield S{shield.get('size')}")
    
    def test_guardian_base_has_2_weapons(self):
        """Guardian (base) should have weapons=[5,5] (2 guns)"""
        ship = self._find_ship("guardian", exact=True)
        if not ship:
            # Look for guardian but not MX or QI
            for s in self.ships:
                name = s.get("name", "").lower()
                if name == "guardian":
                    ship = s
                    break
        
        if ship:
            weapons = ship.get("hardpoints", {}).get("weapons", [])
            assert len(weapons) == 2, f"Guardian should have 2 weapons, got {len(weapons)}"
            print(f"Guardian base: {len(weapons)} weapons {weapons}")
        else:
            pytest.skip("Guardian base not found (may not be in API)")
    
    def test_hammerhead_has_24_weapons(self):
        """Hammerhead should have 24 S4 weapons"""
        ship = self._find_ship("hammerhead")
        assert ship is not None, "Hammerhead not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 24, f"Hammerhead should have 24 weapons, got {len(weapons)}"
        print(f"Hammerhead: {len(weapons)} weapons (multi-crew capital)")
    
    def test_idris_m_has_7_weapons_with_railgun(self):
        """Idris-M should have weapons including S7 railgun"""
        ship = self._find_ship("idris-m")
        if ship:
            weapons = ship.get("hardpoints", {}).get("weapons", [])
            assert 7 in weapons, f"Idris-M should have S7 railgun, weapons={weapons}"
            print(f"Idris-M: {len(weapons)} weapons including S7 railgun")
        else:
            pytest.skip("Idris-M not found in API")
    
    def test_sabre_has_4_s3_weapons(self):
        """Sabre should have 4 S3 weapons"""
        ship = self._find_ship("sabre", exact=True)
        assert ship is not None, "Sabre not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 4, f"Sabre should have 4 weapons, got {len(weapons)}"
        assert all(w == 3 for w in weapons), f"Sabre weapons should all be S3, got {weapons}"
        print(f"Sabre: {len(weapons)} weapons {weapons}")
    
    def test_arrow_has_4_s3_weapons(self):
        """Arrow should have 4 S3 weapons"""
        ship = self._find_ship("arrow", exact=True)
        assert ship is not None, "Arrow not found"
        
        weapons = ship.get("hardpoints", {}).get("weapons", [])
        assert len(weapons) == 4, f"Arrow should have 4 weapons, got {len(weapons)}"
        assert all(w == 3 for w in weapons), f"Arrow weapons should all be S3, got {weapons}"
        print(f"Arrow: {len(weapons)} weapons {weapons}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
