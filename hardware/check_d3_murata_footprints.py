#!/usr/bin/env python3
"""Verify the controlled Littelfuse D3 and Murata capacitor correction.

The checker binds generator output, project-local footprints, schematic/source
assignments, embedded PCB geometry and nets, and the no-routing-change
transaction contract.  Zone fill polygons may change after refill; zone
outlines and every track/via remain immutable.
"""

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
DEFAULT_BOARD = HERE / "esp32-e220.kicad_pcb"
DEFAULT_REFERENCE = (
    HERE / "evidence" / "d3-murata-physical-correction-2026-09-16"
    / "implementation-backup" / "esp32-e220.pre-d3-murata.kicad_pcb"
)
LIBRARY = HERE / "esp32-e220.pretty"
SCHEMATIC = HERE / "esp32-e220.kicad_sch"
SCHEMATIC_GENERATOR = HERE / "generate_esp32_e220.py"
PLACEMENT_GENERATOR = HERE / "generate_stage8_placement.py"

sys.path.insert(0, str(HERE))
from check_board_contract import at, first, forms, fvalue, net_name, prop_map, sexp, value  # noqa: E402


spec = importlib.util.spec_from_file_location("stage7_footprints", HERE / "generate_stage7_footprints.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load generate_stage7_footprints.py")
stage7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage7)


LOCAL_SOURCES = {
    "Littelfuse_SMBJ10CA_DO214AA": stage7.smbj10ca,
    "Murata_GRM188_1608Metric": stage7.murata_grm188_standard,
    "Murata_GRM188R61A106MAAL_1608Metric": stage7.murata_grm188_c5,
    "Murata_GRM21_2012Metric": stage7.murata_grm21_standard,
    "Murata_GRM21BR61A226ME44_2012Metric": stage7.murata_grm21_c3,
}

TARGETS = {
    "D3": {
        "name": "Littelfuse_SMBJ10CA_DO214AA", "origin": (41.9, 70.5, 180.0),
        "centres": ((-2.45, 0.0), (2.45, 0.0)), "size": (2.16, 2.26),
        "nets": ("/BAT_FUSED", "/GND"), "fab": (-2.2025, -1.81, 2.2025, 1.81),
        "courtyard": (-3.8, -2.5, 3.8, 2.5), "old": ((2.5, 2.3), 4.3),
    },
    "C1": {
        "name": "Murata_GRM21_2012Metric", "origin": (67.7, 59.225, 0.0),
        "centres": ((-1.0, 0.0), (1.0, 0.0)), "size": (1.2, 1.3),
        "nets": ("/BUCK_IN", "/GND"), "fab": (-1.0, -0.625, 1.0, 0.625),
        "courtyard": (-1.65, -1.125, 1.65, 1.125), "old": ((1.15, 1.4), 2.0),
    },
    "C2": {
        "name": "Murata_GRM188_1608Metric", "origin": (66.0, 56.0, 180.0),
        "centres": ((-0.725, 0.0), (0.725, 0.0)), "size": (0.7, 0.7),
        "nets": ("/BUCK_IN", "/GND"), "fab": (-0.8, -0.4, 0.8, 0.4),
        "courtyard": (-1.3, -0.9, 1.3, 0.9), "old": ((0.95, 1.0), 1.45),
    },
    "C3": {
        "name": "Murata_GRM21BR61A226ME44_2012Metric", "origin": (70.9, 59.225, 180.0),
        "centres": ((-1.0, 0.0), (1.0, 0.0)), "size": (0.7, 1.3),
        "nets": ("/5V_SYS", "/GND"), "fab": (-1.0, -0.625, 1.0, 0.625),
        "courtyard": (-1.5, -1.125, 1.5, 1.125), "old": ((1.15, 1.4), 2.0),
    },
    "C4": {
        "name": "Murata_GRM188_1608Metric", "origin": (67.0, 53.5, -90.0),
        "centres": ((-0.725, 0.0), (0.725, 0.0)), "size": (0.7, 0.7),
        "nets": ("/SS_TR", "/GND"), "fab": (-0.8, -0.4, 0.8, 0.4),
        "courtyard": (-1.3, -0.9, 1.3, 0.9), "old": ((0.95, 1.0), 1.45),
    },
    "C5": {
        "name": "Murata_GRM188R61A106MAAL_1608Metric", "origin": (24.0, 48.0, 0.0),
        "centres": ((-0.725, 0.0), (0.725, 0.0)), "size": (0.75, 0.9),
        "nets": ("/5V_SYS", "/GND"), "fab": (-0.8, -0.4, 0.8, 0.4),
        "courtyard": (-1.3, -0.9, 1.3, 0.9), "old": ((0.95, 1.0), 1.45),
    },
    "C6": {
        "name": "Murata_GRM188_1608Metric", "origin": (21.305, 49.75, 0.0),
        "centres": ((-0.725, 0.0), (0.725, 0.0)), "size": (0.7, 0.7),
        "nets": ("/5V_SYS", "/GND"), "fab": (-0.8, -0.4, 0.8, 0.4),
        "courtyard": (-1.3, -0.9, 1.3, 0.9), "old": ((0.95, 1.0), 1.45),
    },
    "C7": {
        "name": "Murata_GRM188_1608Metric", "origin": (85.5, 54.0, 90.0),
        "centres": ((-0.725, 0.0), (0.725, 0.0)), "size": (0.7, 0.7),
        "nets": ("/5V_SYS", "/GND"), "fab": (-0.8, -0.4, 0.8, 0.4),
        "courtyard": (-1.3, -0.9, 1.3, 0.9), "old": ((0.95, 1.0), 1.45),
    },
    "C8": {
        "name": "Murata_GRM188_1608Metric", "origin": (88.0, 69.0, 0.0),
        "centres": ((-0.725, 0.0), (0.725, 0.0)), "size": (0.7, 0.7),
        "nets": ("/BAT_SENSE", "/GND"), "fab": (-0.8, -0.4, 0.8, 0.4),
        "courtyard": (-1.3, -0.9, 1.3, 0.9), "old": ((0.95, 1.0), 1.45),
    },
    "C9": {
        "name": "Murata_GRM21_2012Metric", "origin": (17.5, 33.0, -90.0),
        "centres": ((-1.0, 0.0), (1.0, 0.0)), "size": (1.2, 1.3),
        "nets": ("/5V_SYS", "/GND"), "fab": (-1.0, -0.625, 1.0, 0.625),
        "courtyard": (-1.65, -1.125, 1.65, 1.125), "old": ((1.15, 1.4), 2.0),
    },
    "C10": {
        "name": "Murata_GRM21_2012Metric", "origin": (14.4, 27.0, 180.0),
        "centres": ((-1.0, 0.0), (1.0, 0.0)), "size": (1.2, 1.3),
        "nets": ("/AUX_3V3", "/GND"), "fab": (-1.0, -0.625, 1.0, 0.625),
        "courtyard": (-1.65, -1.125, 1.65, 1.125), "old": ((1.15, 1.4), 2.0),
    },
}

BBOX_TOLERANCE_MM = 0.001


def close_pair(actual: tuple[float, float], expected: tuple[float, float], tol: float = 0.0005) -> bool:
    return all(abs(left - right) <= tol for left, right in zip(actual, expected))


def xy(node: list[Any] | None) -> tuple[float, float]:
    return fvalue(node, 1), fvalue(node, 2)


def line_bbox(footprint: list[Any], layer: str) -> tuple[float, float, float, float] | None:
    points: list[tuple[float, float]] = []
    for item in forms(footprint, "fp_line"):
        if value(first(item, "layer"), 1) == layer:
            points.extend((xy(first(item, "start")), xy(first(item, "end"))))
    if not points:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return min(xs), min(ys), max(xs), max(ys)


def close_bbox(
    actual: tuple[float, float, float, float] | None,
    expected: tuple[float, float, float, float],
) -> bool:
    """Compare drawing coordinates with absolute KiCad serialization tolerance."""
    return actual is not None and all(
        abs(actual_value - expected_value) <= BBOX_TOLERANCE_MM
        for actual_value, expected_value in zip(actual, expected)
    )


def check_bbox_tolerance_regression(failures: list[str]) -> dict[str, Any]:
    """Lock the bbox tolerance boundary without weakening copper checks."""
    origin = (0.0, 0.0, 0.0, 0.0)
    boundary_passes = close_bbox((0.001, -0.001, 0.001, -0.001), origin)
    outside_rejected = not close_bbox((0.002, 0.0, 0.0, 0.0), origin)
    if not boundary_passes:
        failures.append("bbox tolerance regression: 0.001 mm delta must pass")
    if not outside_rejected:
        failures.append("bbox tolerance regression: 0.002 mm delta must fail")
    return {
        "absolute_tolerance_mm": BBOX_TOLERANCE_MM,
        "0.001_mm_boundary_passes": boundary_passes,
        "0.002_mm_delta_rejected": outside_rejected,
    }


def pads(footprint: list[Any]) -> dict[str, list[Any]]:
    return {value(item, 1): item for item in forms(footprint, "pad")}


def local_name(name: str) -> str:
    return name.split(":", 1)[-1]


def check_geometry(ref: str, footprint: list[Any], embedded: bool, failures: list[str]) -> None:
    expected = TARGETS[ref]
    actual_pads = pads(footprint)
    if sorted(actual_pads) != ["1", "2"]:
        failures.append(f"{ref}: pad numbers {sorted(actual_pads)}")
        return
    for index, number in enumerate(("1", "2")):
        pad = actual_pads[number]
        actual_at = at(pad)[:2]
        actual_size = xy(first(pad, "size"))
        if not close_pair(actual_at, expected["centres"][index]):
            failures.append(f"{ref}.{number}: local centre {actual_at}, expected {expected['centres'][index]}")
        if not close_pair(actual_size, expected["size"]):
            failures.append(f"{ref}.{number}: size {actual_size}, expected {expected['size']}")
        if value(pad, 2) != "smd" or value(pad, 3) != "roundrect":
            failures.append(f"{ref}.{number}: not SMD roundrect")
        if embedded and net_name(first(pad, "net")) != expected["nets"][index]:
            failures.append(f"{ref}.{number}: net {net_name(first(pad, 'net'))!r}, expected {expected['nets'][index]!r}")
    fab_bbox = line_bbox(footprint, "F.Fab")
    if not close_bbox(fab_bbox, expected["fab"]):
        failures.append(f"{ref}: F.Fab bbox {fab_bbox}, expected {expected['fab']}")
    courtyard_bbox = line_bbox(footprint, "F.CrtYd")
    if not close_bbox(courtyard_bbox, expected["courtyard"]):
        failures.append(f"{ref}: F.CrtYd bbox {courtyard_bbox}, expected {expected['courtyard']}")
    old_size, old_pitch = expected["old"]
    actual_pitch = abs(at(actual_pads["2"])[0] - at(actual_pads["1"])[0])
    if close_pair(xy(first(actual_pads["1"], "size")), old_size) and abs(actual_pitch - old_pitch) <= 0.0005:
        failures.append(f"{ref}: forbidden old land geometry remains")


def by_reference(root: list[Any]) -> dict[str, list[Any]]:
    return {prop_map(item).get("Reference", ""): item for item in forms(root, "footprint")}


def by_uuid(root: list[Any], head: str) -> dict[str, list[Any]]:
    return {value(first(item, "uuid"), 1): item for item in forms(root, head)}


def zone_without_fill(zone: list[Any]) -> list[Any]:
    return [copy.deepcopy(item) for item in zone if not (isinstance(item, list) and item and item[0] == "filled_polygon")]


def check_local(failures: list[str]) -> None:
    checked_names: set[str] = set()
    representative = {value["name"]: ref for ref, value in TARGETS.items()}
    for name, generator in LOCAL_SOURCES.items():
        path = LIBRARY / f"{name}.kicad_mod"
        if not path.is_file():
            failures.append(f"local footprint missing: {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        if text != generator():
            failures.append(f"{path.name}: differs from generator output")
        footprint = sexp(text)
        if value(footprint, 1) != name:
            failures.append(f"{path.name}: identity {value(footprint, 1)!r}")
        ref = representative[name]
        check_geometry(ref, footprint, False, failures)
        checked_names.add(name)
    if checked_names != set(LOCAL_SOURCES):
        failures.append(f"local footprint inventory checked {sorted(checked_names)}")

    source = SCHEMATIC_GENERATOR.read_text(encoding="utf-8")
    placement = PLACEMENT_GENERATOR.read_text(encoding="utf-8")
    source_literals = {
        '"C3": ("GRM21BR61A226ME44", "Murata_GRM21BR61A226ME44_2012Metric")',
        '"C5": ("GRM188R61A106MAAL", "Murata_GRM188R61A106MAAL_1608Metric")',
    }
    placement_literals = {
        'add_footprint(board, "Murata_GRM21BR61A226ME44_2012Metric", "C3", "GRM21BR61A226ME44"',
        'add_footprint(board, "Murata_GRM188R61A106MAAL_1608Metric", "C5", "GRM188R61A106MAAL"',
    }
    for literal in source_literals:
        if literal not in source:
            failures.append(f"schematic generator missing {literal}")
    for literal in placement_literals:
        if literal not in placement:
            failures.append(f"placement generator missing {literal}")

    schematic = sexp(SCHEMATIC.read_text(encoding="utf-8"))
    assignments = {
        prop_map(symbol).get("Reference"): prop_map(symbol).get("Footprint")
        for symbol in forms(schematic, "symbol")
        if prop_map(symbol).get("Reference") in {"C3", "C5"}
    }
    expected_assignments = {
        "C3": "Murata_GRM21BR61A226ME44_2012Metric",
        "C5": "Murata_GRM188R61A106MAAL_1608Metric",
    }
    if assignments != expected_assignments:
        failures.append(f"schematic C3/C5 assignments {assignments}, expected {expected_assignments}")


def check_board(board_path: Path, reference_path: Path, failures: list[str]) -> dict[str, Any]:
    board = sexp(board_path.read_text(encoding="utf-8"))
    reference = sexp(reference_path.read_text(encoding="utf-8"))
    board_fps = by_reference(board)
    reference_fps = by_reference(reference)
    for ref, expected in TARGETS.items():
        footprint = board_fps.get(ref)
        if footprint is None:
            failures.append(f"{ref}: embedded footprint missing")
            continue
        if local_name(value(footprint, 1)) != expected["name"]:
            failures.append(f"{ref}: embedded identity {value(footprint, 1)!r}, expected {expected['name']!r}")
        if at(footprint) != expected["origin"]:
            failures.append(f"{ref}: origin/rotation {at(footprint)}, expected {expected['origin']}")
        check_geometry(ref, footprint, True, failures)

    changed_footprints = sorted(
        ref for ref in set(board_fps) | set(reference_fps)
        if board_fps.get(ref) != reference_fps.get(ref)
    )
    if changed_footprints != sorted(TARGETS):
        failures.append(f"footprint allowlist delta {changed_footprints}, expected {sorted(TARGETS)}")

    board_segments = by_uuid(board, "segment")
    reference_segments = by_uuid(reference, "segment")
    changed_segments = sorted(
        uuid for uuid in set(board_segments) | set(reference_segments)
        if board_segments.get(uuid) != reference_segments.get(uuid)
    )
    if changed_segments:
        failures.append(f"unexpected segment delta {changed_segments}")
    board_vias = by_uuid(board, "via")
    reference_vias = by_uuid(reference, "via")
    changed_vias = sorted(
        uuid for uuid in set(board_vias) | set(reference_vias)
        if board_vias.get(uuid) != reference_vias.get(uuid)
    )
    if changed_vias:
        failures.append(f"unexpected via delta {changed_vias}")

    board_zones = forms(board, "zone")
    reference_zones = forms(reference, "zone")
    zone_outlines_unchanged = (
        len(board_zones) == len(reference_zones)
        and all(zone_without_fill(left) == zone_without_fill(right) for left, right in zip(board_zones, reference_zones))
    )
    if not zone_outlines_unchanged:
        failures.append("zone outline/configuration delta")
    if len(board_segments) != 202 or len(board_vias) != 58 or len(board_zones) != 11:
        failures.append(
            f"board copper inventory segments={len(board_segments)} vias={len(board_vias)} zones={len(board_zones)}"
        )
    return {
        "changed_footprints": changed_footprints,
        "changed_segments": changed_segments,
        "changed_vias": changed_vias,
        "zone_outlines_unchanged": zone_outlines_unchanged,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--local-only", action="store_true")
    args = parser.parse_args()

    failures: list[str] = []
    bbox_regression = check_bbox_tolerance_regression(failures)
    check_local(failures)
    board_delta: dict[str, Any] | None = None
    if not args.local_only:
        board_delta = check_board(args.board, args.reference, failures)
    payload = {
        "status": "FAIL" if failures else "PASS",
        "mode": "local-only" if args.local_only else "full",
        "board": None if args.local_only else str(args.board),
        "reference": None if args.local_only else str(args.reference),
        "target_references": sorted(TARGETS),
        "bbox_tolerance_regression": bbox_regression,
        "source_local_exact": not any("differs from generator" in item for item in failures),
        "board_delta": board_delta,
        "failures": failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
