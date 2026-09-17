#!/usr/bin/env python3
"""Extract deterministic old/new resistor routing and neighbourhood facts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pcbnew


TARGETS = {"R1", "R2", "R3", "R4", "R8", "R9"}
F_CU = pcbnew.F_Cu
F_CRTYD = pcbnew.F_CrtYd


def xy(point: pcbnew.VECTOR2I) -> list[float]:
    return [round(pcbnew.ToMM(point.x), 6), round(pcbnew.ToMM(point.y), 6)]


def shape_gap_mm(a: pcbnew.SHAPE, b: pcbnew.SHAPE, upper_mm: float = 200.0) -> float:
    if a.Collide(b, 0):
        return 0.0
    low, high = 0, pcbnew.FromMM(upper_mm)
    while low + 1 < high:
        mid = (low + high) // 2
        if a.Collide(b, mid):
            high = mid
        else:
            low = mid
    return round(pcbnew.ToMM(high), 6)


def track_desc(track: pcbnew.BOARD_ITEM) -> str:
    if isinstance(track, pcbnew.PCB_VIA):
        return f"via {xy(track.GetPosition())} net={track.GetNetname()} dia={pcbnew.ToMM(track.GetWidth(F_CU)):.3f}"
    return (
        f"track {xy(track.GetStart())}->{xy(track.GetEnd())} "
        f"net={track.GetNetname()} width={pcbnew.ToMM(track.GetWidth()):.3f}"
    )


def item_uuid(item: pcbnew.BOARD_ITEM) -> str:
    return item.m_Uuid.AsString()


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: analyze_candidate.py OLD.kicad_pcb NEW.kicad_pcb OUTPUT.json")
    old = pcbnew.LoadBoard(sys.argv[1])
    new = pcbnew.LoadBoard(sys.argv[2])
    old_fps = {f.GetReference(): f for f in old.GetFootprints()}
    new_fps = {f.GetReference(): f for f in new.GetFootprints()}
    new_tracks = {item_uuid(t): t for t in new.GetTracks()}

    results: dict[str, object] = {}
    for ref in sorted(TARGETS):
        old_fp, new_fp = old_fps[ref], new_fps[ref]
        old_pads = {p.GetNumber(): p for p in old_fp.Pads()}
        new_pads = {p.GetNumber(): p for p in new_fp.Pads()}
        attached: list[dict[str, object]] = []
        for number in ("1", "2"):
            old_pad = old_pads[number]
            old_shape = old_pad.GetEffectiveShape(F_CU)
            new_pad = new_pads[number]
            new_shape = new_pad.GetEffectiveShape(F_CU)
            for track in old.GetTracks():
                if isinstance(track, pcbnew.PCB_VIA) or track.GetLayer() != F_CU:
                    continue
                if track.GetNetCode() != old_pad.GetNetCode():
                    continue
                start_in = old_shape.Collide(track.GetStart())
                end_in = old_shape.Collide(track.GetEnd())
                if not (start_in or end_in):
                    continue
                candidate_track = new_tracks[item_uuid(track)]
                endpoint = track.GetStart() if start_in else track.GetEnd()
                attached.append(
                    {
                        "pad": number,
                        "net": old_pad.GetNetname(),
                        "track_start": xy(track.GetStart()),
                        "track_end": xy(track.GetEnd()),
                        "attached_endpoint": xy(endpoint),
                        "width_mm": round(pcbnew.ToMM(track.GetWidth()), 6),
                        "endpoint_inside_proposed": bool(new_shape.Collide(endpoint)),
                        "full_track_shape_overlaps_proposed": bool(
                            new_shape.Collide(candidate_track.GetEffectiveShape(), 0)
                        ),
                        "uuid": item_uuid(track),
                    }
                )

        proposed_shapes = [p.GetEffectiveShape(F_CU) for p in new_pads.values()]
        copper_candidates: list[tuple[float, str]] = []
        for other_fp in new.GetFootprints():
            for pad in other_fp.Pads():
                if not pad.IsOnLayer(F_CU):
                    continue
                for own_pad, own_shape in zip(new_pads.values(), proposed_shapes):
                    if pad.GetNetCode() == own_pad.GetNetCode() or pad is own_pad:
                        continue
                    copper_candidates.append(
                        (
                            shape_gap_mm(own_shape, pad.GetEffectiveShape(F_CU)),
                            f"pad {other_fp.GetReference()}.{pad.GetNumber()} net={pad.GetNetname()}",
                        )
                    )
        for track in new.GetTracks():
            if not (isinstance(track, pcbnew.PCB_VIA) or track.GetLayer() == F_CU):
                continue
            for own_pad, own_shape in zip(new_pads.values(), proposed_shapes):
                if track.GetNetCode() == own_pad.GetNetCode():
                    continue
                copper_candidates.append(
                    (shape_gap_mm(own_shape, track.GetEffectiveShape()), track_desc(track))
                )
        for zone in new.Zones():
            if not zone.HasFilledPolysForLayer(F_CU):
                continue
            filled = zone.GetFilledPolysList(F_CU)
            if not filled.OutlineCount():
                continue
            for own_pad, own_shape in zip(new_pads.values(), proposed_shapes):
                if zone.GetNetCode() == own_pad.GetNetCode():
                    continue
                copper_candidates.append(
                    (
                        shape_gap_mm(own_shape, filled),
                        f"filled F.Cu zone net={zone.GetNetname() or '<no-net>'}",
                    )
                )
        nearest_copper = min(copper_candidates, key=lambda entry: entry[0])

        nearby_vias: list[dict[str, object]] = []
        for via in (t for t in new.GetTracks() if isinstance(t, pcbnew.PCB_VIA)):
            gap = min(shape_gap_mm(shape, via.GetEffectiveShape()) for shape in proposed_shapes)
            if gap <= 3.0:
                nearby_vias.append(
                    {
                        "position": xy(via.GetPosition()),
                        "net": via.GetNetname(),
                        "diameter_mm": round(pcbnew.ToMM(via.GetWidth(F_CU)), 6),
                        "edge_gap_mm": gap,
                    }
                )
        nearby_vias.sort(key=lambda entry: entry["edge_gap_mm"])

        courtyard = new_fp.GetCourtyard(F_CRTYD)
        courtyard_neighbours: list[tuple[float, str]] = []
        for other_fp in new.GetFootprints():
            if other_fp.GetReference() == ref:
                continue
            other = other_fp.GetCourtyard(F_CRTYD)
            if not other.OutlineCount():
                continue
            courtyard_neighbours.append((shape_gap_mm(courtyard, other), other_fp.GetReference()))
        courtyard_neighbours.sort()

        results[ref] = {
            "origin": xy(new_fp.GetPosition()),
            "rotation_deg": new_fp.GetOrientationDegrees(),
            "pads": {
                number: {
                    "net": old_pads[number].GetNetname(),
                    "old_center": xy(old_pads[number].GetPosition()),
                    "new_center": xy(new_pads[number].GetPosition()),
                    "old_size": xy(old_pads[number].GetSize()),
                    "new_size": xy(new_pads[number].GetSize()),
                }
                for number in ("1", "2")
            },
            "attached_tracks": attached,
            "nearest_different_net_copper": {
                "edge_gap_mm": nearest_copper[0],
                "item": nearest_copper[1],
            },
            "nearby_vias_within_3mm": nearby_vias,
            "nearest_courtyard": (
                {"edge_gap_mm": courtyard_neighbours[0][0], "reference": courtyard_neighbours[0][1]}
                if courtyard_neighbours
                else None
            ),
        }

    settings = new.GetDesignSettings()
    output = {
        "old_board": sys.argv[1],
        "candidate_board": sys.argv[2],
        "design_settings": {
            "solder_mask_expansion_mm": pcbnew.ToMM(settings.m_SolderMaskExpansion),
            "solder_mask_min_width_mm": pcbnew.ToMM(settings.m_SolderMaskMinWidth),
            "solder_paste_margin_mm": pcbnew.ToMM(settings.m_SolderPasteMargin),
            "solder_paste_margin_ratio": settings.m_SolderPasteMarginRatio,
        },
        "references": results,
    }
    Path(sys.argv[3]).write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
