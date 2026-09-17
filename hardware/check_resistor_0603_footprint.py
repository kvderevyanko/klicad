#!/usr/bin/env python3
"""Focused invariant for the approved Yageo RC 0603 resistor correction."""

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
from check_board_contract import at, first, forms, fvalue, net_name, prop_map, sexp, value  # noqa: E402


TARGET_REFS = ("R1", "R2", "R3", "R4", "R8", "R9")
EXPECTED_PLACEMENT = {
    "R1": (58.5, 67.0, 90.0),
    "R2": (62.5, 67.0, 90.0),
    "R3": (86.0, 66.0, 0.0),
    "R4": (90.0, 66.0, 0.0),
    "R8": (40.0, 35.0, 0.0),
    "R9": (46.0, 35.0, 0.0),
}
EXPECTED_IDENTITY = {
    "R1": "Resistor_0603_1608Metric",
    "R2": "Resistor_0603_1608Metric",
    "R3": "Carrier:Resistor_0603_1608Metric",
    "R4": "Carrier:Resistor_0603_1608Metric",
    "R8": "Resistor_0603_1608Metric",
    "R9": "Resistor_0603_1608Metric",
}
EXPECTED_NETS = {
    "R1": {"1": "/Q1_GATE", "2": "/GND"},
    "R2": {"1": "/BUCK_IN", "2": "/Q1_GATE"},
    "R3": {"1": "/BUCK_IN", "2": "/BAT_SENSE"},
    "R4": {"1": "/BAT_SENSE", "2": "/GND"},
    "R8": {"1": "/E220_M0", "2": "/GND"},
    "R9": {"1": "/E220_M1", "2": "/GND"},
}
DEFAULT_REFERENCE = (
    HERE / "evidence" / "resistor-physical-implementation-2026-09-17"
    / "named-backup" / "esp32-e220.pre-resistor.kicad_pcb"
)
DEFAULT_REFERENCE_SCHEMATIC = (
    HERE / "evidence" / "resistor-physical-implementation-2026-09-17"
    / "named-backup" / "esp32-e220.pre-resistor.kicad_sch"
)
DEFAULT_OLD_FIXTURE = (
    HERE / "evidence" / "resistor-physical-implementation-2026-09-17"
    / "named-backup" / "Resistor_0603_1608Metric.pre-resistor.kicad_mod"
)


def point(node: list[Any] | None) -> tuple[float, float]:
    return fvalue(node, 1), fvalue(node, 2)


def by_reference(root: list[Any]) -> dict[str, list[Any]]:
    return {prop_map(item).get("Reference", ""): item for item in forms(root, "footprint")}


def pads_by_number(footprint: list[Any]) -> dict[str, list[Any]]:
    return {value(item, 1): item for item in forms(footprint, "pad")}


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


def replace_form(node: list[Any], head: str, replacement: list[Any]) -> None:
    for index, item in enumerate(node):
        if isinstance(item, list) and item and item[0] == head:
            node[index] = copy.deepcopy(replacement)
            return
    raise ValueError(f"missing {head} form")


def footprint_with_reference_geometry(current: list[Any], reference: list[Any]) -> list[Any]:
    normalized = copy.deepcopy(current)
    current_pads = pads_by_number(normalized)
    reference_pads = pads_by_number(reference)
    for number in ("1", "2"):
        replace_form(current_pads[number], "at", first(reference_pads[number], "at") or [])
        replace_form(current_pads[number], "size", first(reference_pads[number], "size") or [])
    return normalized


def geometry_failures(footprint: list[Any], label: str, expected_nets: dict[str, str] | None = None) -> list[str]:
    failures: list[str] = []
    pads = pads_by_number(footprint)
    if sorted(pads) != ["1", "2"]:
        return [f"{label}: pad numbers {sorted(pads)}, expected ['1', '2']"]
    expected_at = {"1": (-0.850, 0.0), "2": (0.850, 0.0)}
    for number in ("1", "2"):
        pad = pads[number]
        if at(pad)[:2] != expected_at[number]:
            failures.append(f"{label}: pad {number} centre {at(pad)[:2]}, expected {expected_at[number]}")
        if point(first(pad, "size")) != (0.900, 0.800):
            failures.append(f"{label}: pad {number} size {point(first(pad, 'size'))}, expected (0.9, 0.8)")
        if value(pad, 2) != "smd" or value(pad, 3) != "roundrect":
            failures.append(f"{label}: pad {number} is not smd roundrect")
        if fvalue(first(pad, "roundrect_rratio"), 1) != 0.20:
            failures.append(f"{label}: pad {number} roundrect ratio changed")
        layers = first(pad, "layers") or []
        if set(str(item) for item in layers[1:]) != {"F.Cu", "F.Mask", "F.Paste"}:
            failures.append(f"{label}: pad {number} layer set {layers[1:]}")
        for override in ("solder_mask_margin", "solder_paste_margin", "solder_paste_margin_ratio"):
            if first(pad, override) is not None:
                failures.append(f"{label}: pad {number} has forbidden local {override}")
        if expected_nets is not None and net_name(first(pad, "net")) != expected_nets[number]:
            failures.append(f"{label}: pad {number} net {net_name(first(pad, 'net'))!r}")
    pitch = at(pads["2"])[0] - at(pads["1"])[0]
    gap = pitch - point(first(pads["1"], "size"))[0]
    span = pitch + point(first(pads["1"], "size"))[0]
    if tuple(round(item, 6) for item in (pitch, gap, span)) != (1.700, 0.800, 2.600):
        failures.append(f"{label}: pitch/gap/span {(pitch, gap, span)}")
    if line_bbox(footprint, "F.Fab") != (-0.8, -0.4, 0.8, 0.4):
        failures.append(f"{label}: F.Fab changed: {line_bbox(footprint, 'F.Fab')}")
    if line_bbox(footprint, "F.CrtYd") != (-1.3, -0.9, 1.3, 0.9):
        failures.append(f"{label}: F.CrtYd changed: {line_bbox(footprint, 'F.CrtYd')}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, default=HERE / "esp32-e220.kicad_pcb")
    parser.add_argument("--local-footprint", type=Path, default=HERE / "esp32-e220.pretty" / "Resistor_0603_1608Metric.kicad_mod")
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--schematic", type=Path, default=HERE / "esp32-e220.kicad_sch")
    parser.add_argument("--reference-schematic", type=Path, default=DEFAULT_REFERENCE_SCHEMATIC)
    parser.add_argument("--old-geometry-fixture", type=Path, default=DEFAULT_OLD_FIXTURE)
    args = parser.parse_args()

    failures: list[str] = []
    generated_text = stage7.yageo_rc0603()
    local_text = args.local_footprint.read_text(encoding="utf-8")
    if local_text != generated_text:
        failures.append("generator -> project-local footprint exact equality failed")
    local = sexp(local_text)
    if value(local, 1) != "Resistor_0603_1608Metric":
        failures.append(f"local footprint identity {value(local, 1)!r}")
    failures.extend(geometry_failures(local, "local"))

    old_fixture = sexp(args.old_geometry_fixture.read_text(encoding="utf-8"))
    if forms(local, "fp_line") != forms(old_fixture, "fp_line"):
        failures.append("project-local F.Fab/F.CrtYd changed from the approved baseline")
    old_geometry_rejections = geometry_failures(old_fixture, "old-geometry-fixture")
    old_pads = pads_by_number(old_fixture)
    old_is_exact = (
        at(old_pads.get("1", []))[:2] == (-0.725, 0.0)
        and at(old_pads.get("2", []))[:2] == (0.725, 0.0)
        and point(first(old_pads.get("1", []), "size")) == (0.950, 1.000)
        and point(first(old_pads.get("2", []), "size")) == (0.950, 1.000)
    )
    if not old_is_exact or not old_geometry_rejections:
        failures.append("negative regression did not prove rejection of 0.95x1.00 at +/-0.725")

    board = sexp(args.board.read_text(encoding="utf-8"))
    reference = sexp(args.reference.read_text(encoding="utf-8"))
    board_fps = by_reference(board)
    reference_fps = by_reference(reference)
    resistor_refs = tuple(sorted(
        ref for ref, footprint in board_fps.items()
        if value(footprint, 1).split(":")[-1] == "Resistor_0603_1608Metric"
    ))
    if resistor_refs != tuple(sorted(TARGET_REFS)):
        failures.append(f"exact target refs {resistor_refs}, expected {tuple(sorted(TARGET_REFS))}")

    changed_footprints = sorted(
        ref for ref in set(board_fps) | set(reference_fps)
        if board_fps.get(ref) != reference_fps.get(ref)
    )
    if changed_footprints != sorted(TARGET_REFS):
        failures.append(f"footprint delta {changed_footprints}, expected {sorted(TARGET_REFS)}")

    for ref in TARGET_REFS:
        footprint = board_fps.get(ref)
        baseline = reference_fps.get(ref)
        if footprint is None or baseline is None:
            failures.append(f"{ref}: missing current or baseline footprint")
            continue
        if value(footprint, 1) != EXPECTED_IDENTITY[ref] or value(footprint, 1) != value(baseline, 1):
            failures.append(f"{ref}: footprint identity changed: {value(footprint, 1)!r}")
        if at(footprint) != EXPECTED_PLACEMENT[ref] or at(footprint) != at(baseline):
            failures.append(f"{ref}: origin/rotation changed: {at(footprint)}")
        failures.extend(geometry_failures(footprint, ref, EXPECTED_NETS[ref]))
        if forms(footprint, "fp_line") != forms(baseline, "fp_line"):
            failures.append(f"{ref}: F.Fab/F.CrtYd or other line graphics changed")
        if footprint_with_reference_geometry(footprint, baseline) != baseline:
            failures.append(f"{ref}: embedded change is not limited to pad at/size geometry")

    for head, label in (("segment", "tracks"), ("via", "vias"), ("zone", "zones/rule areas")):
        if forms(board, head) != forms(reference, head):
            failures.append(f"{label} changed")
    if args.schematic.read_bytes() != args.reference_schematic.read_bytes():
        failures.append("schematic changed")

    payload = {
        "status": "FAIL" if failures else "PASS",
        "target_refs": list(TARGET_REFS),
        "changed_footprints": changed_footprints,
        "source_local_exact": local_text == generated_text,
        "local_identity": value(local, 1),
        "pad_centres_local_mm": {"1": [-0.850, 0.0], "2": [0.850, 0.0]},
        "pad_size_mm": [0.900, 0.800],
        "pitch_mm": 1.700,
        "inner_gap_mm": 0.800,
        "overall_span_mm": 2.600,
        "roundrect_rratio": 0.20,
        "routing_delta": "zero" if forms(board, "segment") == forms(reference, "segment") else "nonzero",
        "via_delta": "zero" if forms(board, "via") == forms(reference, "via") else "nonzero",
        "zone_rule_area_delta": "zero" if forms(board, "zone") == forms(reference, "zone") else "nonzero",
        "schematic_byte_identical": args.schematic.read_bytes() == args.reference_schematic.read_bytes(),
        "negative_old_geometry": {
            "fixture_is_exact_0.95x1.00_at_plus_minus_0.725": old_is_exact,
            "rejected": bool(old_geometry_rejections),
            "rejection_count": len(old_geometry_rejections),
        },
        "failures": failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
