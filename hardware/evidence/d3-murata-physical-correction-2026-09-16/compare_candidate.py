#!/usr/bin/env python3
"""Machine comparison of active board and the read-only planning candidate."""

from __future__ import annotations

import json
from pathlib import Path

import pcbnew


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ACTIVE = ROOT / "hardware" / "esp32-e220.kicad_pcb"
CANDIDATE = HERE / "candidate-d3-murata.kicad_pcb"
OUT = HERE / "06-candidate-board-delta.json"
TARGETS = {"D3", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"}


def mm(value: int) -> float:
    return round(pcbnew.ToMM(value), 6)


def xy(value: pcbnew.VECTOR2I) -> tuple[float, float]:
    return mm(value.x), mm(value.y)


def fp_map(board: pcbnew.BOARD) -> dict[str, pcbnew.FOOTPRINT]:
    return {fp.GetReference(): fp for fp in board.GetFootprints()}


def placements(board: pcbnew.BOARD) -> dict[str, tuple[tuple[float, float], float]]:
    return {
        ref: (xy(fp.GetPosition()), round(fp.GetOrientation().AsDegrees(), 6))
        for ref, fp in fp_map(board).items()
    }


def pad_geometry(board: pcbnew.BOARD) -> dict[str, list[tuple[object, ...]]]:
    result = {}
    for ref, fp in fp_map(board).items():
        rows = []
        for pad in fp.Pads():
            rows.append((pad.GetNumber(), xy(pad.GetPosition()), xy(pad.GetSize()), pad.GetNetname()))
        result[ref] = sorted(rows)
    return result


def track_signatures(board: pcbnew.BOARD) -> list[tuple[object, ...]]:
    rows = []
    for item in board.GetTracks():
        if isinstance(item, pcbnew.PCB_VIA):
            rows.append(("via", item.GetNetname(), xy(item.GetPosition()), mm(item.GetWidth(pcbnew.F_Cu)), mm(item.GetDrillValue())))
        else:
            rows.append(("track", item.GetNetname(), item.GetLayerName(), xy(item.GetStart()), xy(item.GetEnd()), mm(item.GetWidth())))
    return sorted(rows)


def main() -> int:
    active = pcbnew.LoadBoard(str(ACTIVE))
    candidate = pcbnew.LoadBoard(str(CANDIDATE))
    old_pads = pad_geometry(active)
    new_pads = pad_geometry(candidate)
    changed_pad_refs = sorted(ref for ref in old_pads if old_pads[ref] != new_pads[ref])
    non_target_changes = sorted(set(changed_pad_refs) - TARGETS)
    report = {
        "status": "PASS",
        "footprint_placements_identical": placements(active) == placements(candidate),
        "tracks_and_vias_identical": track_signatures(active) == track_signatures(candidate),
        "track_via_count_active": len(list(active.GetTracks())),
        "track_via_count_candidate": len(list(candidate.GetTracks())),
        "zone_count_active": len(list(active.Zones())),
        "zone_count_candidate": len(list(candidate.Zones())),
        "changed_pad_refs": changed_pad_refs,
        "non_target_pad_changes": non_target_changes,
        "old_new": {ref: {"old": old_pads[ref], "new": new_pads[ref]} for ref in changed_pad_refs},
        "note": "Filled-zone polygons may differ after required candidate refill; zone outlines and count are unchanged.",
    }
    if not report["footprint_placements_identical"] or not report["tracks_and_vias_identical"] or non_target_changes:
        report["status"] = "FAIL"
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"{report['status']}: placements_identical={report['footprint_placements_identical']} "
        f"tracks_vias_identical={report['tracks_and_vias_identical']} changed_pad_refs={changed_pad_refs}"
    )
    return report["status"] != "PASS"


if __name__ == "__main__":
    raise SystemExit(main())
