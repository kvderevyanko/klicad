#!/usr/bin/env python3
"""Prove the active-board delta is exactly the approved Q1 transaction."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path


sys.dont_write_bytecode = True


EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[2]
HARDWARE = ROOT / "hardware"
REFERENCE = EVIDENCE / "esp32-e220-q1-prechange-reference.kicad_pcb"
BOARD = HARDWARE / "esp32-e220.kicad_pcb"
FOOTPRINT = HARDWARE / "esp32-e220.pretty" / "Diodes_DMP3130LQ-7_SOT23.kicad_mod"
GENERATOR = HARDWARE / "generate_stage7_footprints.py"

sys.path.insert(0, str(HARDWARE))
from check_board_contract import at, first, forms, fvalue, prop_map, sexp, value  # noqa: E402


Q1_DESCRIPTION = (
    "Diodes DMP3130LQ-7 SOT23, DS38728 suggested pad layout: "
    "0.80 x 0.90 mm lands; X1=1.35 mm is centreline to outer land edge, "
    "giving 0.95-mm lower-pad centre offsets."
)
TRACKS = {
    "ce7bd062-9fb6-4c9c-8a39-64542cec1e84": {
        "start": [62.05, 77.0], "end": [61.65, 78.5], "width": 0.25,
        "layer": "F.Cu", "net": "/Q1_GATE",
    },
    "a4eef94c-3eb6-420b-8595-5f49d55bb7bb": {
        "start": [63.95, 77.0], "end": [65.5, 77.0], "width": 1.0,
        "layer": "F.Cu", "net": "/BUCK_IN",
    },
    "cb24be05-8b8c-4b70-b364-97c90cc107a3": {
        "start": [63.95, 77.0], "end": [58.0, 87.0], "width": 1.0,
        "layer": "F.Cu", "net": "/BUCK_IN",
    },
}
PAD_EXPECTED = {
    "1": {"at": [-0.95, 1.0, 0.0], "size": [0.8, 0.9], "net": "/Q1_GATE"},
    "2": {"at": [0.95, 1.0, 0.0], "size": [0.8, 0.9], "net": "/BUCK_IN"},
    "3": {"at": [0.0, -1.0, 0.0], "size": [0.8, 0.9], "net": "/BAT_SW"},
}
FAB_LINES = {
    ((-0.65, -1.45), (0.65, -1.45)),
    ((0.65, -1.45), (0.65, 1.45)),
    ((0.65, 1.45), (-0.65, 1.45)),
    ((-0.65, 1.45), (-0.65, -1.45)),
}
COURTYARD_LINES = {
    ((-1.6, -1.7), (1.6, -1.7)),
    ((1.6, -1.7), (1.6, 1.7)),
    ((1.6, 1.7), (-1.6, 1.7)),
    ((-1.6, 1.7), (-1.6, -1.7)),
}


def xy(node: list) -> tuple[float, float]:
    return fvalue(node, 1), fvalue(node, 2)


def find_q1(root: list) -> list:
    matches = [fp for fp in forms(root, "footprint") if prop_map(fp).get("Reference") == "Q1"]
    if len(matches) != 1:
        raise AssertionError(f"expected one Q1, found {len(matches)}")
    return matches[0]


def find_uuid(items: list[list], uuid: str) -> list:
    matches = [item for item in items if value(first(item, "uuid"), 1) == uuid]
    if len(matches) != 1:
        raise AssertionError(f"expected one item UUID {uuid}, found {len(matches)}")
    return matches[0]


def replace_child(parent: list, old: list, new: list) -> None:
    parent[parent.index(old)] = copy.deepcopy(new)


def line_set(fp: list, layer: str) -> set[tuple[tuple[float, float], tuple[float, float]]]:
    return {
        (xy(first(line, "start")), xy(first(line, "end")))
        for line in forms(fp, "fp_line")
        if value(first(line, "layer"), 1) == layer
    }


def main() -> int:
    failures: list[str] = []
    try:
        reference_root = sexp(REFERENCE.read_text())
        board_root = sexp(BOARD.read_text())
        normalized = copy.deepcopy(board_root)
        ref_q1 = find_q1(reference_root)
        q1 = find_q1(normalized)

        if value(q1, 1) != "Diodes_DMP3130LQ-7_SOT23" or at(q1) != (63.0, 76.0, 0.0):
            failures.append("Q1 footprint identity/origin/rotation differs from approved state")
        if value(first(q1, "descr"), 1) != Q1_DESCRIPTION:
            failures.append("Q1 description does not record the corrected X1 interpretation")

        pads = {value(pad, 1): pad for pad in forms(q1, "pad")}
        ref_pads = {value(pad, 1): pad for pad in forms(ref_q1, "pad")}
        if set(pads) != {"1", "2", "3"}:
            failures.append(f"Q1 pad-number set changed: {sorted(pads)}")
        for number, expected in PAD_EXPECTED.items():
            pad = pads[number]
            size = first(pad, "size")
            actual = {
                "at": list(at(pad)),
                "size": [fvalue(size, 1), fvalue(size, 2)],
                "net": value(first(pad, "net"), 1),
            }
            if actual != expected:
                failures.append(f"Q1 pad {number} mismatch: {actual}")
            if number in {"1", "2"}:
                replace_child(pad, first(pad, "at"), first(ref_pads[number], "at"))

        if line_set(q1, "F.Fab") != FAB_LINES:
            failures.append("Q1 F.Fab is not the approved 1.30 x 2.90 mm rectangle")
        if line_set(q1, "F.CrtYd") != COURTYARD_LINES:
            failures.append("Q1 F.CrtYd is not the approved 3.20 x 3.40 mm rectangle")

        ref_lines = {value(first(line, "uuid"), 1): line for line in forms(ref_q1, "fp_line")}
        for line in list(forms(q1, "fp_line")):
            layer = value(first(line, "layer"), 1)
            if layer in {"F.Fab", "F.CrtYd"}:
                ref_line = ref_lines[value(first(line, "uuid"), 1)]
                replace_child(line, first(line, "start"), first(ref_line, "start"))
                replace_child(line, first(line, "end"), first(ref_line, "end"))
        replace_child(q1, first(q1, "descr"), first(ref_q1, "descr"))

        board_segments = forms(normalized, "segment")
        reference_segments = forms(reference_root, "segment")
        for uuid, expected in TRACKS.items():
            segment = find_uuid(board_segments, uuid)
            actual = {
                "start": list(xy(first(segment, "start"))),
                "end": list(xy(first(segment, "end"))),
                "width": fvalue(first(segment, "width"), 1),
                "layer": value(first(segment, "layer"), 1),
                "net": value(first(segment, "net"), 1),
            }
            if actual != expected:
                failures.append(f"segment {uuid} mismatch: {actual}")
            ref_segment = find_uuid(reference_segments, uuid)
            replace_child(segment, first(segment, "start"), first(ref_segment, "start"))

        if normalized != reference_root:
            failures.append("board contains a semantic delta outside the approved Q1 allowlist")

        spec = importlib.util.spec_from_file_location("stage7", GENERATOR)
        if spec is None or spec.loader is None:
            raise AssertionError("could not load footprint generator")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if module.dmp3130() != FOOTPRINT.read_text():
            failures.append("project-local Q1 footprint differs from dmp3130() generator output")
    except Exception as exc:
        failures.append(f"checker exception: {exc}")

    payload = {
        "status": "PASS" if not failures else "FAIL",
        "reference": str(REFERENCE.relative_to(ROOT)),
        "board": str(BOARD.relative_to(ROOT)),
        "allowed_board_delta": {
            "q1": "description, pad-1/pad-2 centres, F.Fab, F.CrtYd",
            "segment_start_uuids": sorted(TRACKS),
        },
        "confirmed_q1": {
            "origin_mm": [63.0, 76.0, 0.0],
            "pads": PAD_EXPECTED,
            "f_fab_bbox_mm": [-0.65, -1.45, 0.65, 1.45],
            "f_courtyard_bbox_mm": [-1.6, -1.7, 1.6, 1.7],
        },
        "confirmed_tracks": TRACKS,
        "local_footprint_matches_generator": not any("generator output" in item for item in failures),
        "failures": failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
