#!/usr/bin/env python3
"""Strict normalized U3 candidate delta gate; reads boards and writes JSON evidence."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCOPE = Path(__file__).resolve().parent
HARDWARE = SCOPE.parents[1]
sys.path.insert(0, str(HARDWARE))
from check_board_contract import at, first, forms, prop_map, sexp, value  # noqa: E402

BASELINE = SCOPE / "00-active-baseline.kicad_pcb"
CANDIDATE = SCOPE / "10-u3-dbv-candidate.kicad_pcb"
REPORT = SCOPE / "15-normalized-delta.json"

ALLOWED_SEGMENTS = {
    "da2890d9-c14e-428c-9a65-9024952b7af6": {
        "net": "/5V_SYS", "old": [[88.525, 51.9], [88.525, 53.0]], "new": [[88.525, 51.9], [88.525, 53.25]]
    },
    "6308e9af-e3b4-4509-b16a-d1588a1cc74b": {
        "net": "/GND", "old": [[89.95, 55.0], [91.0, 55.0]], "new": [[89.95, 54.75], [91.0, 55.0]]
    },
    "8b5ac9dc-4208-4f80-99be-6912b8d39d52": {
        "net": "/GND", "old": [[88.05, 55.0], [87.2, 56.5]], "new": [[88.05, 54.75], [87.2, 56.5]]
    },
    "02e750f7-1ae2-44c5-9fc4-c55c2823b1e9": {
        "net": "/WS2812_DATA_3V3", "old": [[89.0, 58.0], [89.0, 55.0]], "new": [[89.0, 58.0], [89.0, 54.75]]
    },
    "32e0895c-bc20-429f-9684-018e7fcc24bb": {
        "net": "/WS2812_DATA_5V", "old": [[89.475, 53.0], [94.0, 51.5]], "new": [[89.475, 53.25], [94.0, 51.5]]
    },
}


def scrub(node, strip_filled=False):
    if not isinstance(node, list):
        return node
    if node and isinstance(node[0], str) and node[0] in {"uuid", "tstamp"}:
        return None
    if strip_filled and node and isinstance(node[0], str) and node[0] in {"filled_polygon", "filled_areas_thickness"}:
        return None
    return [item for child in node if (item := scrub(child, strip_filled)) is not None]


def load(path):
    return sexp(path.read_text())


def by_ref(root):
    return {prop_map(fp).get("Reference", ""): fp for fp in forms(root, "footprint")}


def by_uuid(root, head):
    result = {}
    for item in forms(root, head):
        uid = value(first(item, "uuid"), 1)
        result[uid] = item
    return result


def xy(item, key):
    node = first(item, key)
    return [float(value(node, 1)), float(value(node, 2))]


def segment_payload(item):
    return {
        "start": xy(item, "start"),
        "end": xy(item, "end"),
        "width": float(value(first(item, "width"), 1)),
        "layer": value(first(item, "layer"), 1),
        "net": value(first(item, "net"), 1),
    }


def main():
    old, new = load(BASELINE), load(CANDIDATE)
    old_fp, new_fp = by_ref(old), by_ref(new)
    non_u3_changed = [ref for ref in sorted(old_fp) if ref != "U3" and scrub(old_fp[ref]) != scrub(new_fp.get(ref, []))]
    u3_origin_unchanged = at(old_fp["U3"]) == at(new_fp["U3"]) == (89.0, 54.0, 0.0)

    old_segments, new_segments = by_uuid(old, "segment"), by_uuid(new, "segment")
    segment_changes = []
    unexpected_segments = []
    for uid in sorted(set(old_segments) | set(new_segments)):
        if scrub(old_segments.get(uid, [])) == scrub(new_segments.get(uid, [])):
            continue
        before, after = segment_payload(old_segments[uid]), segment_payload(new_segments[uid])
        segment_changes.append({"uuid": uid, "before": before, "after": after})
        allowed = ALLOWED_SEGMENTS.get(uid)
        if not allowed or before["net"] != allowed["net"] or after["net"] != allowed["net"] or [before["start"], before["end"]] != allowed["old"] or [after["start"], after["end"]] != allowed["new"] or before["width"] != after["width"] or before["layer"] != after["layer"]:
            unexpected_segments.append(uid)

    vias_unchanged = scrub(forms(old, "via")) == scrub(forms(new, "via"))
    zones_unchanged = scrub(forms(old, "zone"), strip_filled=True) == scrub(forms(new, "zone"), strip_filled=True)
    edges_old = [item for head in ("gr_line", "gr_arc", "gr_rect", "gr_poly") for item in forms(old, head) if value(first(item, "layer"), 1) == "Edge.Cuts"]
    edges_new = [item for head in ("gr_line", "gr_arc", "gr_rect", "gr_poly") for item in forms(new, head) if value(first(item, "layer"), 1) == "Edge.Cuts"]
    edge_unchanged = scrub(edges_old) == scrub(edges_new)
    expected_changed = set(ALLOWED_SEGMENTS)
    observed_changed = {item["uuid"] for item in segment_changes}

    checks = {
        "all_non_U3_footprints_identical": not non_u3_changed,
        "U3_origin_rotation_unchanged": u3_origin_unchanged,
        "only_expected_U3_local_segments_changed": not unexpected_segments and observed_changed == expected_changed,
        "all_vias_identical": vias_unchanged,
        "zone_boundaries_nets_rules_identical": zones_unchanged,
        "Edge_Cuts_identical": edge_unchanged,
    }
    payload = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "non_U3_footprints_changed": non_u3_changed,
        "segment_changes": segment_changes,
        "unexpected_segment_changes": unexpected_segments,
        "summary": "Only U3 footprint geometry and the five 0.25-mm local pad-endpoint shifts differ." if all(checks.values()) else "Unexpected normalized physical delta present.",
    }
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
