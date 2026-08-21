#!/usr/bin/env python3
"""Deterministic normalized delta gate for the J6/J9 planner candidate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from hardware.verify_project_state_reconciliation import canonical, forms, sexp


SCOPE = Path("hardware/evidence/rev1-j6-j9-handsolder-plan-2026-08-21")
BEFORE = sexp((SCOPE / "00-released-baseline.kicad_pcb").read_text())
AFTER = sexp((SCOPE / "10-j6-j9-handsolder-candidate.kicad_pcb").read_text())


def canon_set(root: list, tag: str) -> set[str]:
    return {canonical(item) for item in forms(root, tag)}


def strip_fills(zone: list) -> list:
    return [child for child in zone
            if not (isinstance(child, list) and child
                    and child[0] == "filled_polygon")]


before_segments = canon_set(BEFORE, "segment")
after_segments = canon_set(AFTER, "segment")
removed_segments = sorted(before_segments - after_segments)
added_segments = sorted(after_segments - before_segments)

before_zones = {canonical(strip_fills(zone)) for zone in forms(BEFORE, "zone")}
after_zones = {canonical(strip_fills(zone)) for zone in forms(AFTER, "zone")}
added_zones = sorted(after_zones - before_zones)
removed_zones = sorted(before_zones - after_zones)

unchanged = {}
for tag in ("footprint", "via", "gr_text", "gr_line", "gr_arc", "gr_rect", "gr_poly"):
    unchanged[tag] = canon_set(BEFORE, tag) == canon_set(AFTER, tag)

expected_removed = {
    '["segment",["start","94","18"],["end","104","18"],'
    '["width","0.25"],["layer","B.Cu"],["net","/GND"],'
    '["uuid","e9e75539-bbea-47a1-8cfb-41000d4e3f19"]]'
}
expected_added_signatures = {
    ((94.0, 18.0), (97.0, 18.0), 0.8, "B.Cu", "/GND"),
    ((100.0, 59.08), (97.0, 59.08), 0.8, "B.Cu", "/GND"),
}


def segment_signature(serialized: str) -> tuple:
    item = json.loads(serialized)
    fields = {child[0]: child[1:] for child in item[1:]}
    return (tuple(float(v) for v in fields["start"]),
            tuple(float(v) for v in fields["end"]),
            float(fields["width"][0]), fields["layer"][0], fields["net"][0])


added_rule_names = set()
for serialized in added_zones:
    item = json.loads(serialized)
    fields = {child[0]: child[1:] for child in item[1:]
              if isinstance(child, list) and child}
    if "keepout" in fields and "name" in fields:
        added_rule_names.add(fields["name"][0])

status = (
    all(unchanged.values())
    and set(removed_segments) == expected_removed
    and {segment_signature(item) for item in added_segments} == expected_added_signatures
    and not removed_zones
    and added_rule_names == {"J6_HANDSOLDER_CLEARANCE", "J9_HANDSOLDER_CLEARANCE"}
    and len(added_zones) == 2
)

result = {
    "status": "PASS" if status else "FAIL",
    "unchanged": unchanged,
    "removed_segments": [json.loads(item) for item in removed_segments],
    "added_segments": [json.loads(item) for item in added_segments],
    "removed_zone_definitions": len(removed_zones),
    "added_rule_areas": sorted(added_rule_names),
    "ordinary_zone_definitions_unchanged": not removed_zones,
    "filled_polygon_differences_ignored": "authorized consequences of the two new pour exclusions",
}
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if status else 1)
