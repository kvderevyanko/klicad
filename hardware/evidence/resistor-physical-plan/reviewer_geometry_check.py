#!/usr/bin/env python3
"""Independent candidate checks for the six planned 0603 pad changes.

This evidence-only checker deliberately uses direct KiCad effective-shape
collision calls for whole-track overlap, rather than endpoint containment.
"""
from __future__ import annotations

import json
import argparse
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parent
BASELINE = ROOT / "analysis/baseline/esp32-e220.kicad_pcb"
CANDIDATE = ROOT / "analysis/diagnostic/esp32-e220.kicad_pcb"
OUTPUT = ROOT / "reviewer-geometry.json"
TARGETS = ("R1", "R2", "R3", "R4", "R8", "R9")
F_CU = pcbnew.F_Cu
F_CRTYD = pcbnew.F_CrtYd


def mm(point: pcbnew.VECTOR2I) -> list[float]:
    return [round(pcbnew.ToMM(point.x), 6), round(pcbnew.ToMM(point.y), 6)]


def item_id(item: pcbnew.BOARD_ITEM) -> str:
    return item.m_Uuid.AsString()


def gap_mm(a: pcbnew.SHAPE, b: pcbnew.SHAPE) -> float:
    if a.Collide(b, 0):
        return 0.0
    low, high = 0, pcbnew.FromMM(200)
    while high - low > 1:
        mid = (low + high) // 2
        if a.Collide(b, mid):
            high = mid
        else:
            low = mid
    return round(pcbnew.ToMM(high), 6)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--candidate", type=Path, default=CANDIDATE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    old, new = pcbnew.LoadBoard(str(args.baseline)), pcbnew.LoadBoard(str(args.candidate))
    old_fps = {fp.GetReference(): fp for fp in old.GetFootprints()}
    new_fps = {fp.GetReference(): fp for fp in new.GetFootprints()}
    new_tracks = {item_id(item): item for item in new.GetTracks()}
    result: dict[str, object] = {"references": {}, "failures": []}

    for ref in TARGETS:
        old_fp, new_fp = old_fps[ref], new_fps[ref]
        old_pads = {pad.GetNumber(): pad for pad in old_fp.Pads()}
        new_pads = {pad.GetNumber(): pad for pad in new_fp.Pads()}
        row: dict[str, object] = {
            "origin_mm": mm(new_fp.GetPosition()),
            "rotation_deg": new_fp.GetOrientationDegrees(),
            "identity_preserved": old_fp.GetFPIDAsString() == new_fp.GetFPIDAsString(),
            "pads": {},
            "attached_tracks": [],
        }
        own_shapes = []
        for number, expected_x in (("1", -0.85), ("2", 0.85)):
            old_pad, new_pad = old_pads[number], new_pads[number]
            pad_row = {
                "old_center_mm": mm(old_pad.GetPosition()),
                "new_center_mm": mm(new_pad.GetPosition()),
                "new_local_center_mm": mm(new_pad.GetFPRelativePosition()),
                "new_size_mm": mm(new_pad.GetSize()),
                "net_preserved": old_pad.GetNetname() == new_pad.GetNetname(),
                "layer_set_preserved": sorted(str(layer) for layer in old_pad.GetLayerSet().Seq())
                    == sorted(str(layer) for layer in new_pad.GetLayerSet().Seq()),
            }
            row["pads"][number] = pad_row
            if pad_row["new_local_center_mm"] != [expected_x, 0.0] or pad_row["new_size_mm"] != [0.9, 0.8]:
                result["failures"].append(f"{ref}.{number}: proposed geometry mismatch")
            old_shape, new_shape = old_pad.GetEffectiveShape(F_CU), new_pad.GetEffectiveShape(F_CU)
            own_shapes.append((new_pad, new_shape))
            for track in old.GetTracks():
                if isinstance(track, pcbnew.PCB_VIA) or track.GetLayer() != F_CU or track.GetNetCode() != old_pad.GetNetCode():
                    continue
                endpoint = track.GetStart() if old_shape.Collide(track.GetStart()) else (track.GetEnd() if old_shape.Collide(track.GetEnd()) else None)
                if endpoint is None:
                    continue
                candidate_track = new_tracks[item_id(track)]
                full_overlap = bool(new_shape.Collide(candidate_track.GetEffectiveShape(), 0))
                endpoint_inside = bool(new_shape.Collide(endpoint))
                row["attached_tracks"].append({
                    "pad": number,
                    "endpoint_mm": mm(endpoint),
                    "width_mm": round(pcbnew.ToMM(track.GetWidth()), 6),
                    "endpoint_inside_new_pad": endpoint_inside,
                    "whole_track_copper_overlaps_new_pad": full_overlap,
                })
                if not (endpoint_inside and full_overlap):
                    result["failures"].append(f"{ref}.{number}: track no longer overlaps proposed pad")
        foreign_copper = []
        for fp in new.GetFootprints():
            for pad in fp.Pads():
                if not pad.IsOnLayer(F_CU):
                    continue
                for own_pad, own_shape in own_shapes:
                    if pad is own_pad or pad.GetNetCode() == own_pad.GetNetCode():
                        continue
                    foreign_copper.append((gap_mm(own_shape, pad.GetEffectiveShape(F_CU)), f"pad {fp.GetReference()}.{pad.GetNumber()} {pad.GetNetname()}"))
        for track in new.GetTracks():
            if not (isinstance(track, pcbnew.PCB_VIA) or track.GetLayer() == F_CU):
                continue
            for own_pad, own_shape in own_shapes:
                if track.GetNetCode() != own_pad.GetNetCode():
                    foreign_copper.append((gap_mm(own_shape, track.GetEffectiveShape()), f"track/via {track.GetNetname()}"))
        fcu_zone_gaps = []
        for zone in new.Zones():
            if not zone.IsOnLayer(F_CU) or not zone.HasFilledPolysForLayer(F_CU):
                continue
            fill = zone.GetFilledPolysList(F_CU)
            if not fill.OutlineCount():
                continue
            for own_pad, own_shape in own_shapes:
                if zone.GetNetCode() != own_pad.GetNetCode():
                    fcu_zone_gaps.append((gap_mm(own_shape, fill), zone.GetNetname() or "<no-net>"))
        row["nearest_different_net_copper"] = min(foreign_copper, key=lambda item: item[0])
        row["nearest_different_net_fcu_zone"] = min(fcu_zone_gaps, key=lambda item: item[0]) if fcu_zone_gaps else None
        nearby_vias = []
        for via in (item for item in new.GetTracks() if isinstance(item, pcbnew.PCB_VIA)):
            distance = min(gap_mm(shape, via.GetEffectiveShape()) for _, shape in own_shapes)
            if distance <= 3.0:
                nearby_vias.append({"position_mm": mm(via.GetPosition()), "net": via.GetNetname(), "edge_gap_mm": distance})
        row["nearby_vias_within_3mm"] = sorted(nearby_vias, key=lambda item: item["edge_gap_mm"])
        courtyard = new_fp.GetCourtyard(F_CRTYD)
        court_neighbours = []
        for other_fp in new.GetFootprints():
            if other_fp.GetReference() == ref:
                continue
            other_courtyard = other_fp.GetCourtyard(F_CRTYD)
            if other_courtyard.OutlineCount():
                court_neighbours.append((gap_mm(courtyard, other_courtyard), other_fp.GetReference()))
        row["nearest_courtyard"] = min(court_neighbours)
        result["references"][ref] = row

    result["pass"] = not result["failures"]
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
