#!/usr/bin/env python3
"""Regression contract for U4's project-local DCY/SOT-223 identity."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True

import generate_stage7_footprints as stage7  # noqa: E402
from check_board_contract import at, first, forms, fvalue, prop_map, sexp, value  # noqa: E402


NAME = "TI_TLV1117LV33DCYR_DCY_SOT223"
FULL_ID = f"Carrier:{NAME}"
OLD_ID = "Package_TO_SOT_SMD:SOT-223-3_TabPin2"
NEW_DESCRIPTION = (
    "TI TLV1117LV33DCYR DCY/SOT-223. TI package drawing "
    "MPDS094A/4202506/B; frozen project IPC land pattern, not a "
    "TI-recommended land pattern. Pin 2 includes lead and tab."
)
OLD_DESCRIPTION = "module CMS SOT223 4 pins"
NEW_TAGS = "TI TLV1117LV33DCYR DCY SOT-223 project IPC"
OLD_TAGS = "CMS SOT"

DEFAULT_BOARD = HERE / "esp32-e220.kicad_pcb"
DEFAULT_SCHEMATIC = HERE / "esp32-e220.kicad_sch"
DEFAULT_LOCAL = HERE / "esp32-e220.pretty" / f"{NAME}.kicad_mod"
DEFAULT_REFERENCE = (
    HERE / "evidence" / "full-production-audit-2026-09-15"
    / "u4-library-resolution" / "10-esp32-e220.pre-u4-metadata.kicad_pcb"
)
DEFAULT_SCHEMATIC_REFERENCE = (
    HERE / "evidence" / "full-production-audit-2026-09-15"
    / "u4-library-resolution" / "10-esp32-e220.pre-u4-metadata.kicad_sch"
)
SCHEMATIC_GENERATOR = HERE / "generate_esp32_e220.py"

EXPECTED_PADS = [
    ("1", (-3.15, -2.30), (2.00, 1.50), (17.50, 24.70), "/GND"),
    ("2", (-3.15, 0.00), (2.00, 1.50), (17.50, 27.00), "/AUX_3V3"),
    ("2", (3.15, 0.00), (2.00, 3.80), (23.80, 27.00), "/AUX_3V3"),
    ("3", (-3.15, 2.30), (2.00, 1.50), (17.50, 29.30), "/5V_SYS"),
]


def close(actual: float, expected: float, tolerance: float = 0.0005) -> bool:
    return abs(actual - expected) <= tolerance


def point(node: list[Any] | None) -> tuple[float, float]:
    return fvalue(node, 1), fvalue(node, 2)


def find_footprint(root: list[Any], reference: str) -> list[Any]:
    matches = [
        footprint for footprint in forms(root, "footprint")
        if prop_map(footprint).get("Reference") == reference
    ]
    if len(matches) != 1:
        raise AssertionError(f"expected one {reference} footprint, found {len(matches)}")
    return matches[0]


def line_bbox(footprint: list[Any], layer: str) -> tuple[float, float, float, float] | None:
    points: list[tuple[float, float]] = []
    for item in forms(footprint, "fp_line"):
        if value(first(item, "layer"), 1) == layer:
            points.extend((point(first(item, "start")), point(first(item, "end"))))
    if not points:
        return None
    xs = [item[0] for item in points]
    ys = [item[1] for item in points]
    return min(xs), min(ys), max(xs), max(ys)


def ordered_pads(footprint: list[Any]) -> list[list[Any]]:
    return forms(footprint, "pad")


def check_geometry(footprint: list[Any], embedded: bool, failures: list[str]) -> None:
    pads = ordered_pads(footprint)
    if len(pads) != 4:
        failures.append(f"U4 has {len(pads)} pads, expected four lands")
        return
    actual_numbers = [value(pad, 1) for pad in pads]
    if actual_numbers != ["1", "2", "2", "3"]:
        failures.append(f"U4 pad order/numbers {actual_numbers!r}")
    origin = at(footprint)
    for pad, (number, expected_at, expected_size, expected_absolute, expected_net) in zip(pads, EXPECTED_PADS):
        actual_at = at(pad)[:2]
        actual_size = point(first(pad, "size"))
        if value(pad, 1) != number:
            failures.append(f"expected pad {number}, found {value(pad, 1)!r}")
        if not all(close(actual, target) for actual, target in zip(actual_at, expected_at)):
            failures.append(f"U4 pad {number} local centre {actual_at}, expected {expected_at}")
        if not all(close(actual, target) for actual, target in zip(actual_size, expected_size)):
            failures.append(f"U4 pad {number} size {actual_size}, expected {expected_size}")
        if value(pad, 2) != "smd" or value(pad, 3) != "rect":
            failures.append(f"U4 pad {number} is not smd rect")
        if embedded:
            absolute = (origin[0] + actual_at[0], origin[1] + actual_at[1])
            if not all(close(actual, target) for actual, target in zip(absolute, expected_absolute)):
                failures.append(f"U4 pad {number} absolute centre {absolute}, expected {expected_absolute}")
            net = first(pad, "net")
            actual_net = value(net, 1) if net is not None and len(net) == 2 else value(net, 2)
            if actual_net != expected_net:
                failures.append(f"U4 pad {number} net {actual_net!r}, expected {expected_net!r}")
    if line_bbox(footprint, "F.Fab") != (-1.85, -3.35, 1.85, 3.35):
        failures.append(f"U4 F.Fab bbox {line_bbox(footprint, 'F.Fab')}")
    if line_bbox(footprint, "F.CrtYd") != (-4.4, -3.6, 4.4, 3.6):
        failures.append(f"U4 F.CrtYd bbox {line_bbox(footprint, 'F.CrtYd')}")


def pad_uuid_map(footprint: list[Any]) -> dict[tuple[str, tuple[float, ...]], str]:
    return {
        (value(pad, 1), at(pad)): value(first(pad, "uuid"), 1)
        for pad in ordered_pads(footprint)
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
    generated = stage7.tlv1117lv33_dcy_sot223()
    local_text = args.local_footprint.read_text(encoding="utf-8")
    if local_text != generated:
        failures.append("project-local U4 footprint differs from generator output")
    local = sexp(local_text)
    if value(local, 1) != NAME:
        failures.append(f"local U4 footprint identity {value(local, 1)!r}")
    check_geometry(local, False, failures)

    board_text = args.board.read_text(encoding="utf-8")
    reference_text = args.reference.read_text(encoding="utf-8")
    board = sexp(board_text)
    reference = sexp(reference_text)
    u4 = find_footprint(board, "U4")
    old_u4 = find_footprint(reference, "U4")
    if value(u4, 1) != FULL_ID:
        failures.append(f"embedded U4 identity {value(u4, 1)!r}")
    if at(u4) != (20.65, 27.0, 0.0):
        failures.append(f"embedded U4 origin/rotation {at(u4)}")
    check_geometry(u4, True, failures)
    if value(first(u4, "uuid"), 1) != value(first(old_u4, "uuid"), 1):
        failures.append("U4 footprint UUID changed")
    if pad_uuid_map(u4) != pad_uuid_map(old_u4):
        failures.append("U4 pad UUIDs changed")

    reverted = board_text.replace(FULL_ID, OLD_ID, 1)
    reverted = reverted.replace(NEW_DESCRIPTION, OLD_DESCRIPTION, 1)
    reverted = reverted.replace(NEW_TAGS, OLD_TAGS, 1)
    if reverted != reference_text:
        failures.append("active board changed outside allowlisted U4 identity/description/tags")

    schematic_text = args.schematic.read_text(encoding="utf-8")
    schematic_reference_text = args.schematic_reference.read_text(encoding="utf-8")
    if schematic_text.count(FULL_ID) != 1 or OLD_ID in schematic_text:
        failures.append("active schematic U4 footprint identity is not exact")
    if schematic_text.replace(FULL_ID, OLD_ID, 1) != schematic_reference_text:
        failures.append("active schematic changed outside U4 footprint identity")
    expected_mapping = f'    "U4": ("TLV1117LV33DCYR", "{FULL_ID}"),'
    generator_text = SCHEMATIC_GENERATOR.read_text(encoding="utf-8")
    if generator_text.count(expected_mapping) != 1 or OLD_ID in generator_text:
        failures.append("schematic generator U4 footprint identity is not exact")

    payload = {
        "status": "FAIL" if failures else "PASS",
        "board": str(args.board),
        "reference": str(args.reference),
        "manufacturer_part": "TLV1117LV33DCYR",
        "package": "TI DCY / SOT-223, MPDS094A/4202506/B",
        "land_pattern_basis": "frozen project IPC/KiCad; TI does not publish a recommended land pattern",
        "footprint": FULL_ID,
        "source_local_exact": local_text == generated,
        "expected_origin_rotation": [20.65, 27.0, 0.0],
        "expected_pad_numbers": ["1", "2", "2", "3"],
        "expected_pads": [
            {
                "number": number,
                "local_centre_mm": list(local_at),
                "absolute_centre_mm": list(absolute),
                "size_mm": list(size),
                "net": net,
            }
            for number, local_at, size, absolute, net in EXPECTED_PADS
        ],
        "footprint_uuid_preserved": value(first(u4, "uuid"), 1) == value(first(old_u4, "uuid"), 1),
        "pad_uuids_preserved": pad_uuid_map(u4) == pad_uuid_map(old_u4),
        "outside_u4_metadata_delta": reverted != reference_text,
        "physical_status": "UNVERIFIED manufacturer land pattern; package-drawing compatible",
        "failures": failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
