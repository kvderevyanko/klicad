#!/usr/bin/env python3
"""Report J6/J9 rule-area, explicit-track, and filled-zone connectivity proof."""

from __future__ import annotations

import json
from pathlib import Path

import pcbnew


BOARD = Path(__file__).with_name("10-j6-j9-handsolder-candidate.kicad_pcb")


def mm(value: int) -> float:
    return round(pcbnew.ToMM(value), 3)


def point(value: pcbnew.VECTOR2I) -> list[float]:
    return [mm(value.x), mm(value.y)]


board = pcbnew.LoadBoard(str(BOARD))
connectivity = board.GetConnectivity()

rule_areas = {}
bcu_gnd_zones = []
island_flags = []
for zone in board.Zones():
    box = zone.GetBoundingBox()
    if zone.GetIsRuleArea():
        if zone.GetZoneName() in {"J6_HANDSOLDER_CLEARANCE", "J9_HANDSOLDER_CLEARANCE"}:
            rule_areas[zone.GetZoneName()] = {
                "layer": pcbnew.LayerName(zone.GetLayer()),
                "bbox_mm": [mm(box.GetX()), mm(box.GetY()),
                            mm(box.GetWidth()), mm(box.GetHeight())],
                "copperpour_not_allowed": zone.GetDoNotAllowZoneFills(),
                "tracks_allowed": not zone.GetDoNotAllowTracks(),
                "vias_allowed": not zone.GetDoNotAllowVias(),
                "pads_allowed": not zone.GetDoNotAllowPads(),
                "footprints_allowed": not zone.GetDoNotAllowFootprints(),
            }
        continue
    if zone.GetNetname() == "/GND" and zone.GetLayer() == pcbnew.B_Cu:
        bcu_gnd_zones.append(zone)
        fills = zone.GetFilledPolysList(pcbnew.B_Cu)
        for index in range(fills.OutlineCount()):
            island_flags.append(zone.IsIsland(pcbnew.B_Cu, index))

explicit_tracks = []
for item in board.GetTracks():
    if isinstance(item, pcbnew.PCB_VIA):
        continue
    signature = (point(item.GetStart()), point(item.GetEnd()),
                 mm(item.GetWidth()), pcbnew.LayerName(item.GetLayer()),
                 item.GetNetname())
    if signature in (
        ([94.0, 18.0], [97.0, 18.0], 0.8, "B.Cu", "/GND"),
        ([100.0, 59.08], [97.0, 59.08], 0.8, "B.Cu", "/GND"),
    ):
        explicit_tracks.append({
            "start_mm": signature[0], "end_mm": signature[1],
            "width_mm": signature[2], "layer": signature[3],
            "net": signature[4], "length_mm": 3.0,
        })

pad_proof = {}
for ref, number in (("J6", "1"), ("J9", "3")):
    footprint = board.FindFootprintByReference(ref)
    pad = next(item for item in footprint.Pads() if item.GetNumber() == number)
    connected = connectivity.GetConnectedItems(pad)
    connected_bcu_global_zones = {
        (mm(item.GetBoundingBox().GetX()), mm(item.GetBoundingBox().GetY()),
         mm(item.GetBoundingBox().GetWidth()), mm(item.GetBoundingBox().GetHeight()))
        for item in connected
        if isinstance(item, pcbnew.ZONE) and not item.GetIsRuleArea()
        and item.GetNetname() == "/GND" and item.GetLayer() == pcbnew.B_Cu
    }
    pad_proof[f"{ref}.{number}"] = {
        "net": pad.GetNetname(),
        "position_mm": point(pad.GetPosition()),
        "connected_item_count": len(connected),
        "connected_global_B_Cu_GND_zone_bboxes_mm": sorted(connected_bcu_global_zones),
    }

expected_pad_nets = {
    "J6": ["/GND", "/GPIO13", "/GPIO14", "/GPIO18", "/GPIO19", "/GPIO23"],
    "J9": ["/5V_SYS", "/WS2812_DATA_5V", "/GND"],
}
actual_pad_nets = {
    ref: [pad.GetNetname() for pad in sorted(board.FindFootprintByReference(ref).Pads(),
                                             key=lambda item: int(item.GetNumber()))]
    for ref in expected_pad_nets
}

status = (
    len(rule_areas) == 2
    and all(all((item["copperpour_not_allowed"], item["tracks_allowed"],
                     item["vias_allowed"], item["pads_allowed"],
                     item["footprints_allowed"])) for item in rule_areas.values())
    and len(explicit_tracks) == 2
    and all(item["connected_global_B_Cu_GND_zone_bboxes_mm"] for item in pad_proof.values())
    and not any(island_flags)
    and actual_pad_nets == expected_pad_nets
)

print(json.dumps({
    "status": "PASS" if status else "FAIL",
    "rule_areas": rule_areas,
    "explicit_tracks": explicit_tracks,
    "pad_global_connectivity": pad_proof,
    "B_Cu_GND_zone_count": len(bcu_gnd_zones),
    "B_Cu_filled_outline_island_flags": island_flags,
    "no_isolated_B_Cu_GND_fill": not any(island_flags),
    "J6_J9_pad_nets": actual_pad_nets,
}, indent=2, sort_keys=True))
raise SystemExit(0 if status else 1)
