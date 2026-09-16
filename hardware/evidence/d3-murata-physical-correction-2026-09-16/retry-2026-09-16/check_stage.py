#!/usr/bin/env python3
"""Verify one bounded D3/Murata implementation stage against the baseline."""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from pathlib import Path
from typing import Any

import pcbnew


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HARDWARE = ROOT / "hardware"
ACTIVE = HARDWARE / "esp32-e220.kicad_pcb"
BASELINE = HERE.parent / "implementation-backup" / "esp32-e220.pre-d3-murata.kicad_pcb"
sys.path.insert(0, str(HARDWARE))
from check_board_contract import forms, sexp  # noqa: E402


ORDER = ("d3", "grm188", "grm21", "c5", "c3")
REFS = ("D3", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10")
GROUP = {
    "D3": "d3", "C2": "grm188", "C4": "grm188", "C6": "grm188", "C7": "grm188", "C8": "grm188",
    "C1": "grm21", "C9": "grm21", "C10": "grm21", "C5": "c5", "C3": "c3",
}
EXPECTED_SIZE = {
    "D3": (2.160, 2.260),
    "C2": (0.700, 0.700), "C4": (0.700, 0.700), "C6": (0.700, 0.700),
    "C7": (0.700, 0.700), "C8": (0.700, 0.700),
    "C1": (1.200, 1.300), "C9": (1.200, 1.300), "C10": (1.200, 1.300),
    "C5": (0.750, 0.900), "C3": (0.700, 1.300),
}
EXPECTED_ID = {
    "C3": "Murata_GRM21BR61A226ME44_2012Metric",
    "C5": "Murata_GRM188R61A106MAAL_1608Metric",
    "C8": "Carrier:Murata_GRM188_1608Metric",
    "C9": "Carrier:Murata_GRM21_2012Metric",
    "C10": "Carrier:Murata_GRM21_2012Metric",
}
EXPECTED_NETS = {
    "D3": {"1": "/BAT_FUSED", "2": "/GND"},
    "C1": {"1": "/BUCK_IN", "2": "/GND"}, "C2": {"1": "/BUCK_IN", "2": "/GND"},
    "C3": {"1": "/5V_SYS", "2": "/GND"}, "C4": {"1": "/SS_TR", "2": "/GND"},
    "C5": {"1": "/5V_SYS", "2": "/GND"}, "C6": {"1": "/5V_SYS", "2": "/GND"},
    "C7": {"1": "/5V_SYS", "2": "/GND"}, "C8": {"1": "/BAT_SENSE", "2": "/GND"},
    "C9": {"1": "/5V_SYS", "2": "/GND"}, "C10": {"1": "/AUX_3V3", "2": "/GND"},
}


def mm(value: int) -> float:
    return round(pcbnew.ToMM(value), 6)


def xy(value: pcbnew.VECTOR2I) -> tuple[float, float]:
    return mm(value.x), mm(value.y)


def fp_map(board: pcbnew.BOARD) -> dict[str, pcbnew.FOOTPRINT]:
    return {fp.GetReference(): fp for fp in board.GetFootprints()}


def track_signatures(board: pcbnew.BOARD) -> list[tuple[object, ...]]:
    rows = []
    for item in board.GetTracks():
        if isinstance(item, pcbnew.PCB_VIA):
            rows.append(("via", item.GetNetname(), xy(item.GetPosition()), mm(item.GetWidth(pcbnew.F_Cu)), mm(item.GetDrillValue())))
        else:
            rows.append(("track", item.GetNetname(), item.GetLayerName(), xy(item.GetStart()), xy(item.GetEnd()), mm(item.GetWidth())))
    return sorted(rows)


def zone_without_fill(zone: list[Any]) -> list[Any]:
    return [copy.deepcopy(item) for item in zone if not (isinstance(item, list) and item and item[0] in {"filled_polygon", "fill_segments"})]


def close_pair(left: tuple[float, float], right: tuple[float, float], tolerance: float = 0.0005) -> bool:
    return all(abs(a - b) <= tolerance for a, b in zip(left, right))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, choices=ORDER)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    completed = set(ORDER[: ORDER.index(args.stage) + 1])
    board = pcbnew.LoadBoard(str(ACTIVE))
    baseline = pcbnew.LoadBoard(str(BASELINE))
    fps = fp_map(board)
    baseline_fps = fp_map(baseline)
    failures: list[str] = []

    for ref in REFS:
        fp = fps[ref]
        old = baseline_fps[ref]
        if xy(fp.GetPosition()) != xy(old.GetPosition()) or fp.GetOrientation().AsDegrees() != old.GetOrientation().AsDegrees():
            failures.append(f"{ref}: placement/rotation changed")
        nets = {pad.GetNumber(): pad.GetNetname() for pad in fp.Pads()}
        if nets != EXPECTED_NETS[ref]:
            failures.append(f"{ref}: nets {nets}")
        if ref in EXPECTED_ID:
            expected_id = EXPECTED_ID[ref] if GROUP[ref] in completed else old.GetFPIDAsString()
            if fp.GetFPIDAsString() != expected_id:
                failures.append(f"{ref}: identity {fp.GetFPIDAsString()!r}, expected {expected_id!r}")
        if GROUP[ref] in completed:
            for pad in fp.Pads():
                if not close_pair(xy(pad.GetSize()), EXPECTED_SIZE[ref]):
                    failures.append(f"{ref}.{pad.GetNumber()}: size {xy(pad.GetSize())}, expected {EXPECTED_SIZE[ref]}")
            if ref == "D3":
                expected_centres = {"1": (44.350, 70.500), "2": (39.450, 70.500)}
                for pad in fp.Pads():
                    if not close_pair(xy(pad.GetPosition()), expected_centres[pad.GetNumber()]):
                        failures.append(f"D3.{pad.GetNumber()}: centre {xy(pad.GetPosition())}")
            else:
                old_centres = {pad.GetNumber(): xy(pad.GetPosition()) for pad in old.Pads()}
                for pad in fp.Pads():
                    if xy(pad.GetPosition()) != old_centres[pad.GetNumber()]:
                        failures.append(f"{ref}.{pad.GetNumber()}: centre changed")
        else:
            old_pads = {pad.GetNumber(): (xy(pad.GetPosition()), xy(pad.GetSize()), pad.GetNetname()) for pad in old.Pads()}
            new_pads = {pad.GetNumber(): (xy(pad.GetPosition()), xy(pad.GetSize()), pad.GetNetname()) for pad in fp.Pads()}
            if new_pads != old_pads:
                failures.append(f"{ref}: future-stage pad geometry changed early")

    if track_signatures(board) != track_signatures(baseline):
        failures.append("track/via signatures changed")
    active_zones = forms(sexp(ACTIVE.read_text(encoding="utf-8")), "zone")
    baseline_zones = forms(sexp(BASELINE.read_text(encoding="utf-8")), "zone")
    if len(active_zones) != len(baseline_zones) or any(
        zone_without_fill(a) != zone_without_fill(b) for a, b in zip(active_zones, baseline_zones)
    ):
        failures.append("zone outlines/configuration changed")

    report = {
        "status": "FAIL" if failures else "PASS",
        "stage": args.stage,
        "completed_groups": sorted(completed),
        "placements_rotations_unchanged": not any("placement/rotation" in item for item in failures),
        "tracks_vias_unchanged": "track/via signatures changed" not in failures,
        "zone_outlines_unchanged": "zone outlines/configuration changed" not in failures,
        "failures": failures,
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
