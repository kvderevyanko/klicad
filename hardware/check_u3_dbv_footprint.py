#!/usr/bin/env python3
"""Verify the corrected TI DBV0005A U3 footprint and bounded board delta."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_BOARD = HERE / "esp32-e220.kicad_pcb"
DEFAULT_REFERENCE = (
    HERE / "evidence" / "u3-full-physical-audit-2026-09-15"
    / "10-u3-implementation-backup.kicad_pcb"
)
FOOTPRINT = HERE / "esp32-e220.pretty" / "TI_SN74AHCT1G125DBVR_SOT23-5.kicad_mod"
GENERATOR = HERE / "generate_stage7_footprints.py"

sys.path.insert(0, str(HERE))
from check_board_contract import at, first, forms, fvalue, prop_map, sexp, value  # noqa: E402


PAD_EXPECTED = {
    "1": {"at": [-0.95, 1.30, 0.0], "size": [0.60, 1.10], "net": "/GND"},
    "2": {"at": [0.00, 1.30, 0.0], "size": [0.60, 1.10], "net": "/WS2812_DATA_3V3"},
    "3": {"at": [0.95, 1.30, 0.0], "size": [0.60, 1.10], "net": "/GND"},
    "4": {"at": [0.95, -1.30, 0.0], "size": [0.60, 1.10], "net": "/WS2812_DATA_5V"},
    "5": {"at": [-0.95, -1.30, 0.0], "size": [0.60, 1.10], "net": "/5V_SYS"},
}

FAB_LINES = {
    ((-0.8, -1.45), (0.8, -1.45)),
    ((0.8, -1.45), (0.8, 1.45)),
    ((0.8, 1.45), (-0.3, 1.45)),
    ((-0.3, 1.45), (-0.8, 0.95)),
    ((-0.8, 0.95), (-0.8, -1.45)),
}

COURTYARD_LINES = {
    ((-1.8, -2.1), (1.8, -2.1)),
    ((1.8, -2.1), (1.8, 2.1)),
    ((1.8, 2.1), (-1.8, 2.1)),
    ((-1.8, 2.1), (-1.8, -2.1)),
}

TRACKS = {
    "8b5ac9dc-4208-4f80-99be-6912b8d39d52": {
        "start": [88.05, 55.30], "end": [87.20, 56.50],
        "width": 0.50, "layer": "F.Cu", "net": "/GND",
    },
    "02e750f7-1ae2-44c5-9fc4-c55c2823b1e9": {
        "start": [89.00, 58.00], "end": [89.00, 55.30],
        "width": 0.25, "layer": "F.Cu", "net": "/WS2812_DATA_3V3",
    },
    "6308e9af-e3b4-4509-b16a-d1588a1cc74b": {
        "start": [89.95, 55.30], "end": [91.00, 55.00],
        "width": 0.50, "layer": "F.Cu", "net": "/GND",
    },
    "32e0895c-bc20-429f-9684-018e7fcc24bb": {
        "start": [89.95, 52.70], "end": [94.00, 51.50],
        "width": 0.25, "layer": "F.Cu", "net": "/WS2812_DATA_5V",
    },
    "da2890d9-c14e-428c-9a65-9024952b7af6": {
        "start": [88.525, 51.90], "end": [88.05, 52.70],
        "width": 0.50, "layer": "F.Cu", "net": "/5V_SYS",
    },
}


def xy(node: list[Any] | None) -> tuple[float, float]:
    return fvalue(node, 1), fvalue(node, 2)


def find_u3(root: list[Any]) -> list[Any]:
    matches = [fp for fp in forms(root, "footprint") if prop_map(fp).get("Reference") == "U3"]
    if len(matches) != 1:
        raise AssertionError(f"expected one U3, found {len(matches)}")
    return matches[0]


def find_uuid(items: list[list[Any]], uuid: str) -> list[Any]:
    matches = [item for item in items if value(first(item, "uuid"), 1) == uuid]
    if len(matches) != 1:
        raise AssertionError(f"expected one item UUID {uuid}, found {len(matches)}")
    return matches[0]


def replace_child(parent: list[Any], old: list[Any], new: list[Any]) -> None:
    parent[parent.index(old)] = copy.deepcopy(new)


def line_set(fp: list[Any], layer: str) -> set[tuple[tuple[float, float], tuple[float, float]]]:
    return {
        (xy(first(line, "start")), xy(first(line, "end")))
        for line in forms(fp, "fp_line")
        if value(first(line, "layer"), 1) == layer
    }


def pad_map(fp: list[Any]) -> dict[str, list[Any]]:
    return {value(pad, 1): pad for pad in forms(fp, "pad")}


def check_geometry(fp: list[Any], failures: list[str], require_nets: bool) -> None:
    pads = pad_map(fp)
    if set(pads) != set(PAD_EXPECTED):
        failures.append(f"U3 pad-number set mismatch: {sorted(pads)}")
        return
    for number, expected in PAD_EXPECTED.items():
        pad = pads[number]
        size = first(pad, "size")
        actual_at = list(at(pad))
        actual_size = [fvalue(size, 1), fvalue(size, 2)]
        if actual_at != expected["at"]:
            failures.append(f"U3 pad {number} centre mismatch: {actual_at}")
        if actual_size != expected["size"]:
            failures.append(f"U3 pad {number} size mismatch: {actual_size}")
        if value(pad, 3) != "roundrect":
            failures.append(f"U3 pad {number} is not roundrect")
        if fvalue(first(pad, "roundrect_rratio"), 1) != 0.083333:
            failures.append(f"U3 pad {number} is not R0.05 mm")
        if fvalue(first(pad, "solder_mask_margin"), 1) != 0.05:
            failures.append(f"U3 pad {number} mask margin is not 0.05 mm")
        if require_nets and value(first(pad, "net"), 1) != expected["net"]:
            failures.append(f"U3 pad {number} net mismatch: {value(first(pad, 'net'), 1)}")
    if line_set(fp, "F.Fab") != FAB_LINES:
        failures.append("U3 F.Fab is not the approved nominal 1.60 x 2.90 mm chamfered body")
    if line_set(fp, "F.CrtYd") != COURTYARD_LINES:
        failures.append("U3 F.CrtYd is not the approved 3.60 x 4.20 mm rectangle")
    circles = [
        circle for circle in forms(fp, "fp_circle")
        if value(first(circle, "layer"), 1) == "F.SilkS"
    ]
    if len(circles) != 1 or xy(first(circles[0], "center")) != (-1.55, 1.75) \
            or xy(first(circles[0], "end")) != (-1.4, 1.75):
        failures.append("U3 pin-1 silk marker geometry mismatch")


def normalize_allowed_delta(board_root: list[Any], reference_root: list[Any]) -> list[Any]:
    normalized = copy.deepcopy(board_root)
    u3 = find_u3(normalized)
    ref_u3 = find_u3(reference_root)

    ref_graphics = {
        value(first(item, "uuid"), 1): item
        for kind in ("fp_line", "fp_circle")
        for item in forms(ref_u3, kind)
    }
    for kind in ("fp_line", "fp_circle"):
        for item in forms(u3, kind):
            uuid = value(first(item, "uuid"), 1)
            ref_item = ref_graphics.get(uuid)
            if ref_item is None:
                continue
            layer = value(first(item, "layer"), 1)
            if layer not in {"F.Fab", "F.CrtYd", "F.SilkS"}:
                continue
            for coordinate in ("start", "end", "center"):
                current = first(item, coordinate)
                reference = first(ref_item, coordinate)
                if current is not None and reference is not None:
                    replace_child(item, current, reference)

    current_pads = pad_map(u3)
    reference_pads = pad_map(ref_u3)
    for number in PAD_EXPECTED:
        for field in ("at", "roundrect_rratio"):
            replace_child(current_pads[number], first(current_pads[number], field), first(reference_pads[number], field))

    for uuid in TRACKS:
        segment = find_uuid(forms(normalized, "segment"), uuid)
        ref_segment = find_uuid(forms(reference_root, "segment"), uuid)
        for field in ("start", "end"):
            current = first(segment, field)
            reference = first(ref_segment, field)
            if current != reference:
                replace_child(segment, current, reference)
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    failures: list[str] = []
    try:
        board_root = sexp(args.board.read_text())
        reference_root = sexp(args.reference.read_text())
        u3 = find_u3(board_root)
        if value(u3, 1) != "TI_SN74AHCT1G125DBVR_SOT23-5" or at(u3) != (89.0, 54.0, 0.0):
            failures.append("U3 identity/origin/rotation differs from approved state")
        check_geometry(u3, failures, require_nets=True)

        for uuid, expected in TRACKS.items():
            segment = find_uuid(forms(board_root, "segment"), uuid)
            actual = {
                "start": list(xy(first(segment, "start"))),
                "end": list(xy(first(segment, "end"))),
                "width": fvalue(first(segment, "width"), 1),
                "layer": value(first(segment, "layer"), 1),
                "net": value(first(segment, "net"), 1),
            }
            if actual != expected:
                failures.append(f"segment {uuid} mismatch: {actual}")

        if normalize_allowed_delta(board_root, reference_root) != reference_root:
            failures.append("board contains a semantic delta outside the approved U3 allowlist")

        library_root = sexp(FOOTPRINT.read_text())
        check_geometry(library_root, failures, require_nets=False)
        spec = importlib.util.spec_from_file_location("stage7", GENERATOR)
        if spec is None or spec.loader is None:
            raise AssertionError("could not load footprint generator")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if module.sn74ahct1g125() != FOOTPRINT.read_text():
            failures.append("project-local U3 footprint differs from generator output")
    except Exception as exc:
        failures.append(f"checker exception: {exc}")

    payload = {
        "status": "PASS" if not failures else "FAIL",
        "board": str(args.board),
        "reference": str(args.reference),
        "source_drawing": "TI DBV0005A 4214839/K, 08/2024",
        "u3_origin_mm": [89.0, 54.0, 0.0],
        "pads": PAD_EXPECTED,
        "fab_bbox_mm": [-0.8, -1.45, 0.8, 1.45],
        "courtyard_bbox_mm": [-1.8, -2.1, 1.8, 2.1],
        "allowed_segment_endpoint_uuids": sorted(TRACKS),
        "confirmed_segment_endpoints": TRACKS,
        "normalized_board_delta": (
            "PASS" if not any("outside the approved U3 allowlist" in item for item in failures)
            else "FAIL"
        ),
        "generator_matches_library": not any("generator output" in item for item in failures),
        "failures": failures,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
