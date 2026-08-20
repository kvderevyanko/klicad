#!/usr/bin/env python3
"""Emit exact final-board metrics and compare reviewed geometry semantically."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import pcbnew


MM = pcbnew.ToMM
MANDATORY_REV1_NETS = {
    "/AUX_3V3", "/BAT_FUSED", "/BAT_SENSE", "/BAT_SW", "/DEVKIT_VIN",
    "/E220_AUX", "/E220_M0", "/E220_M1", "/E220_RXD", "/E220_TXD",
    "/GPIO13", "/GPIO14", "/GPIO18", "/GPIO19", "/GPIO23",
    "/WS2812_DATA_3V3", "/WS2812_DATA_5V",
}


def xy(vector) -> tuple[float, float]:
    return round(MM(vector.x), 3), round(MM(vector.y), 3)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def footprints(board) -> list[dict]:
    records = []
    for item in board.GetFootprints():
        pads = []
        for pad in item.Pads():
            pads.append((pad.GetNumber(), pad.GetNetname(), xy(pad.GetPosition()), xy(pad.GetSize())))
        fpid = item.GetFPID()
        nickname = fpid.GetLibNickname()
        library_item = fpid.GetLibItemName()
        records.append({
            "reference": item.GetReference(),
            "footprint": f"{nickname}:{library_item}" if nickname else library_item,
            "xy_mm": xy(item.GetPosition()),
            "rotation_deg": round(item.GetOrientationDegrees(), 3),
            "pads": sorted(pads),
        })
    return sorted(records, key=lambda record: record["reference"])


def tracks(board) -> list[tuple]:
    records = []
    for item in board.GetTracks():
        if isinstance(item, pcbnew.PCB_VIA):
            records.append((
                "via", item.GetNetname(), xy(item.GetPosition()),
                round(MM(item.GetWidth(pcbnew.F_Cu)), 3), round(MM(item.GetDrillValue()), 3),
                item.GetLayer(), item.BottomLayer(),
            ))
        else:
            endpoints = sorted((xy(item.GetStart()), xy(item.GetEnd())))
            records.append((
                "track", item.GetNetname(), item.GetLayer(), endpoints[0], endpoints[1],
                round(MM(item.GetWidth()), 3),
            ))
    return sorted(records)


def zone_outlines(board) -> list[dict]:
    records = []
    for item in board.Zones():
        outlines = []
        polygon = item.Outline()
        for outline_index in range(polygon.OutlineCount()):
            outline = polygon.Outline(outline_index)
            outlines.append([xy(outline.CPoint(i)) for i in range(outline.PointCount())])
        records.append({
            "rule_area": bool(item.GetIsRuleArea()),
            "name": item.GetZoneName(),
            "net": item.GetNetname(),
            "layer": item.GetLayerName(),
            "priority": item.GetAssignedPriority(),
            "outlines_mm": outlines,
        })
    return sorted(records, key=lambda record: json.dumps(record, sort_keys=True))


def placement(board, reference: str) -> dict | None:
    item = board.FindFootprintByReference(reference)
    if item is None:
        return None
    fpid = item.GetFPID()
    nickname = fpid.GetLibNickname()
    library_item = fpid.GetLibItemName()
    return {
        "xy_mm": xy(item.GetPosition()),
        "rotation_deg": round(item.GetOrientationDegrees(), 3),
        "footprint": f"{nickname}:{library_item}" if nickname else library_item,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--board", type=Path, required=True)
    parser.add_argument("--reviewed", type=Path, required=True)
    parser.add_argument("--drc", type=Path, required=True)
    args = parser.parse_args()

    board = pcbnew.LoadBoard(str(args.board.resolve()))
    reviewed = pcbnew.LoadBoard(str(args.reviewed.resolve()))
    drc = json.loads(args.drc.read_text())
    board_footprints = footprints(board)
    reviewed_footprints = footprints(reviewed)
    board_tracks = tracks(board)
    reviewed_tracks = tracks(reviewed)
    board_zones = zone_outlines(board)
    reviewed_zones = zone_outlines(reviewed)

    airwire_nets = []
    for finding in drc.get("unconnected_items", []):
        names = set()
        for item in finding.get("items", []):
            names.update(re.findall(r"\[(/[^\]]+)\]", item.get("description", "")))
        airwire_nets.append(sorted(names))

    aux_zones = [
        item for item in board_zones
        if not item["rule_area"] and item["net"] == "/AUX_3V3"
    ]
    aux_vias = [
        record[2] for record in board_tracks
        if record[0] == "via" and record[1] == "/AUX_3V3"
    ]
    u4 = board.FindFootprintByReference("U4")
    u4_pads = sorted(({
        "number": pad.GetNumber(), "net": pad.GetNetname(),
        "xy_mm": xy(pad.GetPosition()), "size_mm": xy(pad.GetSize()),
    } for pad in u4.Pads()), key=lambda item: (item["number"], item["xy_mm"]))

    result = {
        "active_sha256": sha256(args.board),
        "reviewed_sha256": sha256(args.reviewed),
        "semantic_match_to_reviewed": {
            "footprints_and_pads": board_footprints == reviewed_footprints,
            "tracks_and_vias": board_tracks == reviewed_tracks,
            "zone_and_rule_area_outlines": board_zones == reviewed_zones,
        },
        "counts": {
            "footprints": len(list(board.GetFootprints())),
            "tracks": sum(not isinstance(item, pcbnew.PCB_VIA) for item in board.GetTracks()),
            "vias": sum(isinstance(item, pcbnew.PCB_VIA) for item in board.GetTracks()),
            "copper_zones": sum(not item.GetIsRuleArea() for item in board.Zones()),
            "rule_areas": sum(item.GetIsRuleArea() for item in board.Zones()),
        },
        "placements": {ref: placement(board, ref) for ref in ("U4", "C9", "C10")},
        "u4_pads": u4_pads,
        "aux_zones": aux_zones,
        "aux_vias_xy_mm": sorted(aux_vias),
        "scope_references": {
            ref: board.FindFootprintByReference(ref) is not None
            for ref in ("J6", "J7", "J9", "D2", "TP6", "TP7", "TP8", "TP9", "TP10")
        },
        "airwires": {
            "visible_count": len(airwire_nets),
            "net_sets": airwire_nets,
            "mandatory_rev1_count": sum(
                bool(set(nets) & MANDATORY_REV1_NETS) for nets in airwire_nets
            ),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
