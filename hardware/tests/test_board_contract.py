#!/usr/bin/env python3
"""Stdlib tests for check_board_contract parser helpers."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_board_contract as contract


class BoardContractTests(unittest.TestCase):
    def pad(self, number, net, copper=True, xy=(0.0, 0.0)):
        return {"number": number, "net": net, "copper": copper, "xy": xy, "type": "smd", "local": (0, 0, 0)}

    def board(self, pads):
        return {"footprints": [{"ref": "U4", "name": "fixture", "at": (0, 0, 0), "pads": pads}], "tracks": [], "vias": [], "zones": [], "rule_areas": [], "copper_layers": [], "edge_points": [(0, 0), (10, 0), (10, 10), (0, 10)]}

    def test_duplicate_same_net_passes(self):
        check = contract.check_duplicate_pads(self.board([self.pad("2", "AUX_3V3"), self.pad("2", "AUX_3V3")]))
        self.assertEqual(check["status"], contract.PASS)

    def test_duplicate_netless_fails(self):
        check = contract.check_duplicate_pads(self.board([self.pad("2", ""), self.pad("2", "AUX_3V3")]))
        self.assertEqual(check["status"], contract.FAIL)
        self.assertEqual(check["evidence"][0]["reference"], "U4")

    def test_different_pad_numbers_not_compared(self):
        check = contract.check_duplicate_pads(self.board([self.pad("1", "GND"), self.pad("2", "AUX_3V3")]))
        self.assertEqual(check["status"], contract.PASS)

    def test_npth_is_ignored(self):
        check = contract.check_duplicate_pads(self.board([self.pad("2", "AUX_3V3"), self.pad("2", "", copper=False)]))
        self.assertEqual(check["status"], contract.PASS)

    def test_antenna_boundary_intersections(self):
        rect = {"xmin": 104.7, "xmax": 142.7, "ymin": 52.0, "ymax": 90.0}
        self.assertTrue(contract.in_rect((104.7, 52.0), rect))
        self.assertTrue(contract.segment_intersects_rect((100, 60), (110, 60), rect))
        self.assertFalse(contract.segment_intersects_rect((100, 51), (143, 51), rect))

    def test_antenna_zone_enclosing_rectangle_fails(self):
        data = self.board([])
        data["zones"] = [{"net": "/GND", "polygons": [[(100, 40), (150, 40), (150, 100), (100, 100)]]}]
        cfg = {"antenna_exclusion_mm": {"xmin": 104.7, "xmax": 142.7, "ymin": 52.0, "ymax": 90.0}, "antenna_approved_footprints": []}
        self.assertEqual(contract.check_antenna(data, cfg)["status"], contract.FAIL)

    def test_matching_rule_area_is_cross_checked(self):
        data = self.board([])
        data["rule_areas"] = [{"name": "ESP32_ANTENNA_EXCLUSION", "polygons": [[(104.7, 52.0), (142.7, 52.0), (142.7, 90.0), (104.7, 90.0)]], "native_keepout": True, "prohibitions": {"tracks": "not_allowed", "vias": "not_allowed", "copperpour": "not_allowed", "footprints": "not_allowed"}}]
        cfg = {"antenna_exclusion_mm": {"xmin": 104.7, "xmax": 142.7, "ymin": 52.0, "ymax": 90.0}, "antenna_rule_area_name": "ESP32_ANTENNA_EXCLUSION", "antenna_approved_footprints": []}
        self.assertEqual(contract.check_antenna(data, cfg)["evidence"]["rule_area_crosscheck"], contract.PASS)

    def test_native_keepout_zone_is_not_copper_zone(self):
        fixture = Path(__file__).resolve().parents[1] / "evidence" / "rev1-physical-recovery-2026-08-20" / "native-antenna-keepout-fixture.kicad_pcb"
        data = contract.parse_board(fixture)
        self.assertEqual(data["zones"], [])
        self.assertEqual(data["rule_areas"][0]["name"], "ESP32_ANTENNA_EXCLUSION")
        self.assertTrue(data["rule_areas"][0]["native_keepout"])
        self.assertEqual(data["rule_areas"][0]["prohibitions"]["tracks"], "not_allowed")

    def test_unrelated_rule_area_does_not_fail_antenna_check(self):
        data = self.board([])
        data["rule_areas"] = [{"name": "MOUNTING_KEEP_OUT", "polygons": [[(10, 10), (20, 10), (20, 20), (10, 20)]]}]
        cfg = {"antenna_exclusion_mm": {"xmin": 104.7, "xmax": 142.7, "ymin": 52.0, "ymax": 90.0}, "antenna_rule_area_name": "ESP32_ANTENNA_EXCLUSION", "antenna_approved_footprints": []}
        self.assertEqual(contract.check_antenna(data, cfg)["status"], contract.PASS)

    def test_reference_is_required_for_protected_checkpoint(self):
        cfg = {"protected_footprints": ["U4"]}
        self.assertEqual(contract.check_protected(self.board([]), None, cfg)["status"], contract.INC)

    def test_json_result_schema(self):
        check = contract.result("fixture", contract.PASS, {"count": 1})
        payload = {"board": "fixture.kicad_pcb", "mode": "fast", "checks": [check], "overall_status": contract.PASS}
        decoded = json.loads(json.dumps(payload))
        self.assertEqual(set(decoded), {"board", "mode", "checks", "overall_status"})
        self.assertEqual(set(decoded["checks"][0]), {"name", "status", "evidence"})


if __name__ == "__main__":
    unittest.main()
