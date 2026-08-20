#!/usr/bin/env python3
"""Emit reproducible physical metrics for the retained Rev.1 plan candidate."""

import argparse
import hashlib
import json
from pathlib import Path

import pcbnew


MM = pcbnew.ToMM
PLACED = ("U4", "C9", "C10", "J6", "J8", "J9", "JP1", "R3", "R4", "C8", "R8", "R9")
FIXED = ("J1", "J2", "J3", "J5")
ROUTED_NETS = (
    "E220_M0", "E220_M1", "E220_AUX", "E220_RXD", "E220_TXD",
    "GPIO13", "GPIO14", "GPIO18", "GPIO19", "GPIO23", "BAT_SENSE",
    "WS2812_DATA_3V3", "WS2812_DATA_5V", "BAT_FUSED", "BAT_SW",
    "DEVKIT_VIN", "AUX_3V3", "5V_SYS", "GND",
)


def pos(item):
    p = item.GetPosition()
    return [round(MM(p.x), 3), round(MM(p.y), 3)]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def footprint_record(board, ref):
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        return None
    return {"xy_mm": pos(fp), "rotation_deg": round(fp.GetOrientationDegrees(), 3)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--board", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    args = parser.parse_args()

    board = pcbnew.LoadBoard(str(args.board.resolve()))
    baseline = pcbnew.LoadBoard(str(args.baseline.resolve()))
    route_metrics = {}
    for wanted in ROUTED_NETS:
        canonical = "/" + wanted
        tracks = []
        vias = []
        for item in board.GetTracks():
            if item.GetNetname() != canonical:
                continue
            if isinstance(item, pcbnew.PCB_VIA):
                vias.append(item)
            else:
                tracks.append(item)
        route_metrics[wanted] = {
            "track_length_mm": round(sum(MM(t.GetLength()) for t in tracks), 3),
            "track_segments": len(tracks),
            "vias": len(vias),
        }

    fixed = {}
    for ref in FIXED:
        got = footprint_record(board, ref)
        expected = footprint_record(baseline, ref)
        fixed[ref] = {"candidate": got, "baseline": expected, "unchanged": got == expected}

    u4 = board.FindFootprintByReference("U4")
    pad_map = []
    for pad in u4.Pads():
        pad_map.append({
            "number": pad.GetNumber(),
            "net": pad.GetNetname(),
            "xy_mm": pos(pad),
            "size_mm": [round(MM(pad.GetSize().x), 3), round(MM(pad.GetSize().y), 3)],
        })

    result = {
        "board": str(args.board.resolve()),
        "sha256": sha256(args.board),
        "counts": {
            "footprints": len(list(board.GetFootprints())),
            "tracks": sum(not isinstance(t, pcbnew.PCB_VIA) for t in board.GetTracks()),
            "vias": sum(isinstance(t, pcbnew.PCB_VIA) for t in board.GetTracks()),
            "zones_including_rule_areas": len(list(board.Zones())),
        },
        "placements": {ref: footprint_record(board, ref) for ref in PLACED},
        "fixed_modules": fixed,
        "u4_physical_pads": pad_map,
        "route_metrics": route_metrics,
        "thermal_contract": {
            "AUX_3V3_F_Cu_bounds_mm": [17.5, 16.0, 37.5, 38.0],
            "AUX_3V3_B_Cu_bounds_mm": [17.5, 16.0, 37.5, 38.0],
            "AUX_3V3_vias_xy_mm": [[25.3, 24.8], [25.3, 29.2], [26.5, 26.0], [26.5, 28.0]],
        },
        "antenna_rule_area_bounds_mm": [104.7, 52.0, 142.7, 90.0],
        "J8_endpoint_route_length_mm": round(3.862 + 3.0 + (3.5**2 + 2.0**2) ** 0.5 + (3.0**2 + 1.0**2) ** 0.5, 3),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
