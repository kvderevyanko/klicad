#!/usr/bin/env python3
"""Regression contract for TI TLV1117LV DCY drawing 4210278/C."""

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


NAME = "TI_TLV1117LV33DCYR_DCY_SOT223"
FULL_ID = f"Carrier:{NAME}"
DESCRIPTION = (
    "TI TLV1117LV33DCYR DCY/SOT-223 manufacturer land pattern; "
    "TI TLV1117LV Rev. C drawing 4210278/C. Pin 2 includes lead and tab."
)
TAGS = "TI TLV1117LV33DCYR DCY SOT-223 4210278C"

DEFAULT_BOARD = HERE / "esp32-e220.kicad_pcb"
DEFAULT_SCHEMATIC = HERE / "esp32-e220.kicad_sch"
DEFAULT_LOCAL = HERE / "esp32-e220.pretty" / f"{NAME}.kicad_mod"
DEFAULT_REFERENCE = (
    HERE / "evidence" / "residual-footprint-audit-2026-09-16"
    / "u4-implementation" / "named-backup" / "esp32-e220.kicad_pcb"
)
DEFAULT_SCHEMATIC_REFERENCE = (
    HERE / "evidence" / "residual-footprint-audit-2026-09-16"
    / "u4-implementation" / "named-backup" / "esp32-e220.kicad_sch"
)
SCHEMATIC_GENERATOR = HERE / "generate_esp32_e220.py"

EXPECTED_PADS = [
    ("1", (-2.90, -2.30), (2.15, 0.95), (17.75, 24.70), "/GND"),
    ("2", (-2.90, 0.00), (2.15, 0.95), (17.75, 27.00), "/AUX_3V3"),
    ("2", (2.90, 0.00), (2.15, 3.25), (23.55, 27.00), "/AUX_3V3"),
    ("3", (-2.90, 2.30), (2.15, 0.95), (17.75, 29.30), "/5V_SYS"),
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


def net_name(pad: list[Any]) -> str:
    net = first(pad, "net")
    if net is None:
        return ""
    return str(value(net, 1) if len(net) == 2 else value(net, 2))


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
        layers = first(pad, "layers")
        if layers is None or set(layers[1:]) != {"F.Cu", "F.Mask", "F.Paste"}:
            failures.append(f"U4 pad {number} layers do not provide 1:1 copper/paste/mask")
        mask = first(pad, "solder_mask_margin")
        if mask is None or not close(fvalue(mask, 1), 0.05):
            failures.append(f"U4 pad {number} solder-mask margin is not +0.05 mm")
        if first(pad, "solder_paste_margin") is not None or first(pad, "solder_paste_margin_ratio") is not None:
            failures.append(f"U4 pad {number} has an unexpected paste reduction/expansion")
        if embedded:
            absolute = (origin[0] + actual_at[0], origin[1] + actual_at[1])
            if not all(close(actual, target) for actual, target in zip(absolute, expected_absolute)):
                failures.append(f"U4 pad {number} absolute centre {absolute}, expected {expected_absolute}")
            if net_name(pad) != expected_net:
                failures.append(f"U4 pad {number} net {net_name(pad)!r}, expected {expected_net!r}")
    if line_bbox(footprint, "F.Fab") != (-1.85, -3.35, 1.85, 3.35):
        failures.append(f"U4 F.Fab bbox {line_bbox(footprint, 'F.Fab')}")
    if line_bbox(footprint, "F.CrtYd") != (-4.4, -3.6, 4.4, 3.6):
        failures.append(f"U4 F.CrtYd bbox {line_bbox(footprint, 'F.CrtYd')}")


def item_uuid(node: list[Any]) -> str:
    uuid = first(node, "uuid")
    return str(value(uuid, 1)) if uuid is not None else ""


def normalized_u4_matches_baseline(u4: list[Any], old_u4: list[Any]) -> bool:
    """Undo only the approved U4 fields; equality rejects every other delta."""
    normalized = copy.deepcopy(u4)
    old_pads = {item_uuid(pad): pad for pad in ordered_pads(old_u4)}
    for key in ("descr", "tags"):
        current = first(normalized, key)
        baseline = first(old_u4, key)
        if current is None or baseline is None:
            return False
        current[:] = copy.deepcopy(baseline)
    for pad in ordered_pads(normalized):
        old_pad = old_pads.get(item_uuid(pad))
        if old_pad is None:
            return False
        for key in ("at", "size"):
            current = first(pad, key)
            baseline = first(old_pad, key)
            if current is None or baseline is None:
                return False
            current[:] = copy.deepcopy(baseline)
        mask = first(pad, "solder_mask_margin")
        if mask is None:
            return False
        pad.remove(mask)
    return normalized == old_u4


def outside_u4_exact(board: list[Any], reference: list[Any]) -> bool:
    normalized = copy.deepcopy(board)
    u4 = find_footprint(normalized, "U4")
    old_u4 = find_footprint(reference, "U4")
    normalized[normalized.index(u4)] = copy.deepcopy(old_u4)
    return normalized == reference


def forms_exact(root: list[Any], reference: list[Any], kind: str) -> bool:
    return forms(root, kind) == forms(reference, kind)


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
    if value(first(local, "descr"), 1) != DESCRIPTION or value(first(local, "tags"), 1) != TAGS:
        failures.append("local U4 TI 4210278/C provenance metadata mismatch")
    check_geometry(local, False, failures)

    board = sexp(args.board.read_text(encoding="utf-8"))
    reference = sexp(args.reference.read_text(encoding="utf-8"))
    u4 = find_footprint(board, "U4")
    old_u4 = find_footprint(reference, "U4")
    if value(u4, 1) != FULL_ID:
        failures.append(f"embedded U4 identity {value(u4, 1)!r}")
    if at(u4) != (20.65, 27.0, 0.0):
        failures.append(f"embedded U4 origin/rotation {at(u4)}")
    if value(first(u4, "descr"), 1) != DESCRIPTION or value(first(u4, "tags"), 1) != TAGS:
        failures.append("embedded U4 TI 4210278/C provenance metadata mismatch")
    check_geometry(u4, True, failures)

    approved_u4_delta_only = normalized_u4_matches_baseline(u4, old_u4)
    if not approved_u4_delta_only:
        failures.append("embedded U4 changed outside approved description/tags/pad geometry/mask delta")
    board_outside_u4_exact = outside_u4_exact(board, reference)
    if not board_outside_u4_exact:
        failures.append("active PCB changed outside embedded U4")

    route_delta_zero = forms_exact(board, reference, "segment")
    via_delta_zero = forms_exact(board, reference, "via")
    zone_delta_zero = forms_exact(board, reference, "zone")
    for label, result in (("route", route_delta_zero), ("via", via_delta_zero), ("zone", zone_delta_zero)):
        if not result:
            failures.append(f"{label} delta is not zero versus approved baseline")

    schematic_text = args.schematic.read_text(encoding="utf-8")
    schematic_reference_text = args.schematic_reference.read_text(encoding="utf-8")
    schematic_connectivity_delta_zero = schematic_text == schematic_reference_text
    if not schematic_connectivity_delta_zero:
        failures.append("schematic changed versus approved baseline")
    expected_mapping = f'    "U4": ("TLV1117LV33DCYR", "{FULL_ID}"),'
    generator_text = SCHEMATIC_GENERATOR.read_text(encoding="utf-8")
    if generator_text.count(expected_mapping) != 1:
        failures.append("schematic generator U4 footprint identity is not exact")

    payload = {
        "status": "FAIL" if failures else "PASS",
        "board": str(args.board),
        "reference": str(args.reference),
        "manufacturer_part": "TLV1117LV33DCYR",
        "package": "TI DCY / SOT-223",
        "land_pattern_basis": "TI TLV1117LV Rev. C drawing 4210278/C",
        "footprint": FULL_ID,
        "source_local_exact": local_text == generated,
        "expected_origin_rotation": [20.65, 27.0, 0.0],
        "expected_pad_numbers": ["1", "2", "2", "3"],
        "expected_pads": [
            {
                "number": number,
                "local_centre_mm": list(local_at),
                "absolute_centre_mm": list(absolute),
                "copper_and_paste_mm": list(size),
                "mask_opening_mm": [size[0] + 0.10, size[1] + 0.10],
                "net": net,
            }
            for number, local_at, size, absolute, net in EXPECTED_PADS
        ],
        "solder_mask_margin_mm": 0.05,
        "paste_scale": "1:1 with copper",
        "fab_unchanged": line_bbox(u4, "F.Fab") == line_bbox(old_u4, "F.Fab"),
        "courtyard_unchanged": line_bbox(u4, "F.CrtYd") == line_bbox(old_u4, "F.CrtYd"),
        "approved_u4_delta_only": approved_u4_delta_only,
        "outside_u4_pcb_delta_zero": board_outside_u4_exact,
        "route_delta_zero": route_delta_zero,
        "via_delta_zero": via_delta_zero,
        "zone_outline_and_config_delta_zero": zone_delta_zero,
        "schematic_connectivity_delta_zero": schematic_connectivity_delta_zero,
        "physical_status": "MANUFACTURER LAND PATTERN PASS",
        "failures": failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
