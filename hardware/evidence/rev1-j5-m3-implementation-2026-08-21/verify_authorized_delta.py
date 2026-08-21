#!/usr/bin/env python3
"""Strict normalized-delta proof for the J5/M3 planner candidate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from hardware.verify_project_state_reconciliation import canonical, forms, prop_map, sexp


HERE = Path(__file__).resolve().parent
BEFORE = sexp((HERE / "10-active-pre-j5-m3-transaction-9f15f061.kicad_pcb").read_text())
AFTER = sexp((HERE / "20-regenerated-reviewed-implementation.kicad_pcb").read_text())


def canon_set(root, tag):
    return {canonical(item) for item in forms(root, tag)}


def strip_fills(zone):
    return [child for child in zone if not (isinstance(child, list) and child
                                             and child[0] == "filled_polygon")]


def footprint_map(root):
    return {prop_map(item).get("Reference", ""): canonical(item)
            for item in forms(root, "footprint")}


before_fp, after_fp = footprint_map(BEFORE), footprint_map(AFTER)
existing_fp_unchanged = all(before_fp[ref] == after_fp.get(ref) for ref in before_fp)
added_refs = sorted(set(after_fp)-set(before_fp))
before_segments, after_segments = canon_set(BEFORE, "segment"), canon_set(AFTER, "segment")
added_segments, removed_segments = after_segments-before_segments, before_segments-after_segments
before_zones = {canonical(strip_fills(zone)) for zone in forms(BEFORE, "zone")}
after_zones = {canonical(strip_fills(zone)) for zone in forms(AFTER, "zone")}
added_zones, removed_zones = after_zones-before_zones, before_zones-after_zones


def segment_signature(serialized):
    item = json.loads(serialized)
    fields = {child[0]: child[1:] for child in item[1:] if isinstance(child, list) and child}
    return (tuple(float(v) for v in fields["start"]), tuple(float(v) for v in fields["end"]),
            float(fields["width"][0]), fields["layer"][0], fields["net"][0])


added_rule_names = set()
for serialized in added_zones:
    item = json.loads(serialized)
    fields = {child[0]: child[1:] for child in item[1:] if isinstance(child, list) and child}
    if "keepout" in fields and "name" in fields:
        added_rule_names.add(fields["name"][0])

unchanged = {tag: canon_set(BEFORE, tag) == canon_set(AFTER, tag)
             for tag in ("via", "gr_text", "gr_line", "gr_arc", "gr_rect", "gr_poly")}
status = (
    existing_fp_unchanged and added_refs == ["H1", "H2", "H3"]
    and not removed_segments
    and {segment_signature(item) for item in added_segments}
        == {((63.0, 20.0), (60.0, 20.0), 0.8, "B.Cu", "/GND")}
    and not removed_zones and len(added_zones) == 4
    and added_rule_names == {"J5_HANDSOLDER_CLEARANCE", "H1_M3_COPPER_KEEPOUT",
                             "H2_M3_COPPER_KEEPOUT", "H3_M3_COPPER_KEEPOUT"}
    and all(unchanged.values())
)
print(json.dumps({
    "status": "PASS" if status else "FAIL",
    "existing_footprints_unchanged": existing_fp_unchanged,
    "added_footprint_references": added_refs,
    "added_segments": [json.loads(item) for item in sorted(added_segments)],
    "removed_segments": [json.loads(item) for item in sorted(removed_segments)],
    "added_rule_areas": sorted(added_rule_names),
    "removed_zone_definitions": len(removed_zones),
    "ordinary_and_existing_rule_area_definitions_unchanged": not removed_zones,
    "unchanged_board_items": unchanged,
    "filled_polygon_differences_ignored": "authorized consequences of four new rule areas",
}, indent=2, sort_keys=True))
raise SystemExit(0 if status else 1)
