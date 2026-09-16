#!/usr/bin/env python3
"""Regression contract for the Samtec TSW-102-07-G-S JP1 correction."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True

import generate_stage7_footprints as stage7  # noqa: E402
from check_board_contract import at, first, forms, fvalue, prop_map, sexp, value  # noqa: E402


NAME = "Samtec_TSW-102-07-G-S_1x02_P2.54mm_THT"
FULL_ID = f"Carrier:{NAME}"
DEFAULT_BOARD = HERE / "esp32-e220.kicad_pcb"
DEFAULT_SCHEMATIC = HERE / "esp32-e220.kicad_sch"
DEFAULT_LOCAL = HERE / "esp32-e220.pretty" / f"{NAME}.kicad_mod"
SCHEMATIC_GENERATOR = HERE / "generate_esp32_e220.py"
DEFAULT_REFERENCE = (
    HERE / "evidence" / "full-production-audit-2026-09-15"
    / "jp1-implementation" / "10-esp32-e220.pre-jp1.kicad_pcb"
)
DEFAULT_SCHEMATIC_REFERENCE = (
    HERE / "evidence" / "full-production-audit-2026-09-15"
    / "jp1-implementation" / "10-esp32-e220.pre-jp1.kicad_sch"
)
OLD_ID = "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"
EXPECTED_PADS = {
    "1": {"local": (0.0, 0.0), "absolute": (96.0, 14.0), "net": "/5V_SYS"},
    "2": {"local": (0.0, 2.54), "absolute": (98.54, 14.0), "net": "/DEVKIT_VIN"},
}


def find_footprint(root: list[Any], reference: str) -> list[Any]:
    matches = [
        footprint for footprint in forms(root, "footprint")
        if prop_map(footprint).get("Reference") == reference
    ]
    if len(matches) != 1:
        raise AssertionError(f"expected one {reference} footprint, found {len(matches)}")
    return matches[0]


def pads_by_number(footprint: list[Any]) -> dict[str, list[Any]]:
    return {value(pad, 1): pad for pad in forms(footprint, "pad")}


def close(actual: float, expected: float, tolerance: float = 0.0005) -> bool:
    return abs(actual - expected) <= tolerance


def check_geometry(footprint: list[Any], embedded: bool, failures: list[str]) -> None:
    pads = pads_by_number(footprint)
    if set(pads) != set(EXPECTED_PADS):
        failures.append(f"JP1 pad numbers {sorted(pads)}, expected ['1', '2']")
        return
    for number, expected in EXPECTED_PADS.items():
        pad = pads[number]
        pad_at = at(pad)
        size = first(pad, "size")
        drill = first(pad, "drill")
        if not all(close(actual, target) for actual, target in zip(pad_at[:2], expected["local"])):
            failures.append(f"JP1 pad {number} local centre {pad_at[:2]}")
        if not close(fvalue(size, 1), 1.70) or not close(fvalue(size, 2), 1.70):
            failures.append(f"JP1 pad {number} copper size is not 1.70 x 1.70 mm")
        if drill is None or not close(fvalue(drill, 1), 1.020):
            failures.append(f"JP1 pad {number} drill is not 1.020 mm")
        expected_shape = "rect" if number == "1" else "oval"
        if value(pad, 2) != "thru_hole" or value(pad, 3) != expected_shape:
            failures.append(f"JP1 pad {number} type/shape is not thru_hole {expected_shape}")
        if embedded:
            net = value(first(pad, "net"), 1)
            if net != expected["net"]:
                failures.append(f"JP1 pad {number} net {net!r}, expected {expected['net']!r}")


def absolute_pad_centres(footprint: list[Any]) -> dict[str, tuple[float, float]]:
    origin = at(footprint)
    # KiCad PCB positive rotation is clockwise in board coordinates.  JP1 is
    # fixed at +90 degrees: local (x,y) -> absolute (ox+y, oy-x).
    return {
        number: (origin[0] + at(pad)[1], origin[1] - at(pad)[0])
        for number, pad in pads_by_number(footprint).items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    parser.add_argument("--schematic", type=Path, default=DEFAULT_SCHEMATIC)
    parser.add_argument("--local-footprint", type=Path, default=DEFAULT_LOCAL)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--schematic-reference", type=Path, default=DEFAULT_SCHEMATIC_REFERENCE)
    args = parser.parse_args()

    failures: list[str] = []
    generated = stage7.samtec_tsw_102_07_g_s()
    local_text = args.local_footprint.read_text(encoding="utf-8")
    if local_text != generated:
        failures.append("project-local footprint differs from generator output")
    local = sexp(local_text)
    if value(local, 1) != NAME:
        failures.append(f"local footprint identity {value(local, 1)!r}")
    check_geometry(local, False, failures)

    board = sexp(args.board.read_text(encoding="utf-8"))
    reference = sexp(args.reference.read_text(encoding="utf-8"))
    jp1 = find_footprint(board, "JP1")
    reference_jp1 = find_footprint(reference, "JP1")
    if value(jp1, 1) != FULL_ID:
        failures.append(f"embedded JP1 identity {value(jp1, 1)!r}")
    if at(jp1) != (96.0, 14.0, 90.0):
        failures.append(f"embedded JP1 origin/rotation {at(jp1)}")
    if prop_map(jp1).get("Value") != "TSW-102-07-G-S + SNT-100-BK-G":
        failures.append("embedded JP1 value changed")
    check_geometry(jp1, True, failures)
    absolute = absolute_pad_centres(jp1)
    for number, expected in EXPECTED_PADS.items():
        if not all(close(actual, target) for actual, target in zip(absolute[number], expected["absolute"])):
            failures.append(f"JP1 pad {number} absolute centre {absolute[number]}")

    current_pad_uuids = {
        number: value(first(pad, "uuid"), 1)
        for number, pad in pads_by_number(jp1).items()
    }
    reference_pad_uuids = {
        number: value(first(pad, "uuid"), 1)
        for number, pad in pads_by_number(reference_jp1).items()
    }
    if value(first(jp1, "uuid"), 1) != value(first(reference_jp1, "uuid"), 1):
        failures.append("JP1 footprint UUID changed")
    if current_pad_uuids != reference_pad_uuids:
        failures.append("JP1 pad UUIDs changed")

    normalized = copy.deepcopy(board)
    normalized_jp1 = find_footprint(normalized, "JP1")
    normalized[normalized.index(normalized_jp1)] = copy.deepcopy(reference_jp1)
    if normalized != reference:
        failures.append("active board changed outside the JP1 footprint block")

    schematic_text = args.schematic.read_text(encoding="utf-8")
    schematic_reference_text = args.schematic_reference.read_text(encoding="utf-8")
    if schematic_text.count(FULL_ID) != 1 or OLD_ID in schematic_text:
        failures.append("active schematic JP1 footprint metadata is not exact")
    if schematic_text.replace(FULL_ID, OLD_ID) != schematic_reference_text:
        failures.append("active schematic changed outside JP1 footprint metadata")
    expected_generator_contract = (
        '    "JP1": ("TSW-102-07-G-S + SNT-100-BK-G", '
        f'"{FULL_ID}"),'
    )
    generator_text = SCHEMATIC_GENERATOR.read_text(encoding="utf-8")
    if generator_text.count(expected_generator_contract) != 1 or OLD_ID in generator_text:
        failures.append("schematic generator JP1 assembly contract is not exact")

    payload = {
        "status": "FAIL" if failures else "PASS",
        "board": str(args.board),
        "reference": str(args.reference),
        "manufacturer_part": "TSW-102-07-G-S",
        "footprint": FULL_ID,
        "source_local_exact": local_text == generated,
        "expected_origin_rotation": [96.0, 14.0, 90.0],
        "expected_pad_local_centres_mm": {k: list(v["local"]) for k, v in EXPECTED_PADS.items()},
        "expected_pad_absolute_centres_mm": {k: list(v["absolute"]) for k, v in EXPECTED_PADS.items()},
        "expected_pad_size_mm": [1.70, 1.70],
        "expected_drill_mm": 1.020,
        "expected_pitch_mm": 2.540,
        "expected_pad_nets": {k: v["net"] for k, v in EXPECTED_PADS.items()},
        "pad_uuids_preserved": current_pad_uuids == reference_pad_uuids,
        "outside_jp1_board_delta": normalized != reference,
        "failures": failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
