#!/usr/bin/env python3
"""Deterministic J5 connectivity, M3 geometry, and copper-clearance proof."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pcbnew


HERE = Path(__file__).resolve().parent
BOARD = HERE / "10-j5-m3-candidate.kicad_pcb"
HOLES = {"H1": (7.0, 7.0), "H2": (80.0, 7.0), "H3": (96.0, 83.0)}


def mm(value: int) -> float:
    return round(pcbnew.ToMM(value), 4)


def point(value: pcbnew.VECTOR2I) -> list[float]:
    return [mm(value.x), mm(value.y)]


def distance_to_segment(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px-ax)*dx + (py-ay)*dy)/(dx*dx+dy*dy)))
    return math.hypot(px-(ax+t*dx), py-(ay+t*dy))


board = pcbnew.LoadBoard(str(BOARD))
connectivity = board.GetConnectivity()
rule_areas = {}
bcu_islands = []
for zone in board.Zones():
    if zone.GetIsRuleArea():
        name = zone.GetZoneName()
        if name == "J5_HANDSOLDER_CLEARANCE" or name in {
            "H1_M3_COPPER_KEEPOUT", "H2_M3_COPPER_KEEPOUT", "H3_M3_COPPER_KEEPOUT"
        }:
            box = zone.GetBoundingBox()
            rule_areas[name] = {
                "bbox_mm": [mm(box.GetX()), mm(box.GetY()), mm(box.GetWidth()), mm(box.GetHeight())],
                "layers": sorted(pcbnew.LayerName(layer) for layer in zone.GetLayerSet().Seq()),
                "copperpour_not_allowed": zone.GetDoNotAllowZoneFills(),
                "tracks_not_allowed": zone.GetDoNotAllowTracks(),
                "vias_not_allowed": zone.GetDoNotAllowVias(),
                "pads_allowed": not zone.GetDoNotAllowPads(),
                "footprints_allowed": not zone.GetDoNotAllowFootprints(),
            }
        continue
    if zone.GetNetname() == "/GND" and zone.GetLayer() == pcbnew.B_Cu:
        fills = zone.GetFilledPolysList(pcbnew.B_Cu)
        bcu_islands.extend(zone.IsIsland(pcbnew.B_Cu, index)
                           for index in range(fills.OutlineCount()))

j5 = board.FindFootprintByReference("J5")
j5_pads = {pad.GetNumber(): pad for pad in j5.Pads()}
j5_track = []
for item in board.GetTracks():
    if isinstance(item, pcbnew.PCB_VIA):
        continue
    ends = {tuple(point(item.GetStart())), tuple(point(item.GetEnd()))}
    if (item.GetNetname() == "/GND" and item.GetLayer() == pcbnew.B_Cu
            and mm(item.GetWidth()) == 0.8
            and ends == {(63.0, 20.0), (60.0, 20.0)}):
        j5_track.append({"start_mm": point(item.GetStart()), "end_mm": point(item.GetEnd()),
                         "layer": "B.Cu", "width_mm": 0.8, "length_mm": 3.0})

connected = connectivity.GetConnectedItems(j5_pads["1"])
j5_global_zones = [item for item in connected if isinstance(item, pcbnew.ZONE)
                   and not item.GetIsRuleArea() and item.GetNetname() == "/GND"
                   and item.GetLayer() == pcbnew.B_Cu]

holes = {}
copper_intrusions = []
filled_samples = []
for ref, (cx, cy) in HOLES.items():
    fp = board.FindFootprintByReference(ref)
    pads = list(fp.Pads())
    pad = pads[0] if len(pads) == 1 else None
    holes[ref] = {
        "position_mm": point(fp.GetPosition()),
        "rotation_deg": fp.GetOrientationDegrees(),
        "pad_count": len(pads),
        "pad_attribute": "NPTH" if pad and pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH else "OTHER",
        "drill_mm": point(pad.GetDrillSize()) if pad else None,
        "pad_size_mm": point(pad.GetSize()) if pad else None,
        "net": pad.GetNetname() if pad else None,
        "edge_center_distance_mm": min(cx, 145.0-cx, cy, 90.0-cy),
        "hole_edge_distance_mm": min(cx, 145.0-cx, cy, 90.0-cy)-1.6,
        "copper_keepout_diameter_mm": 8.0,
    }
    for item in board.GetTracks():
        if isinstance(item, pcbnew.PCB_VIA):
            p = item.GetPosition()
            clearance = math.hypot(pcbnew.ToMM(p.x)-cx, pcbnew.ToMM(p.y)-cy) - pcbnew.ToMM(item.GetWidth(pcbnew.F_Cu))/2
        else:
            a, b = item.GetStart(), item.GetEnd()
            clearance = distance_to_segment(cx, cy, pcbnew.ToMM(a.x), pcbnew.ToMM(a.y),
                                            pcbnew.ToMM(b.x), pcbnew.ToMM(b.y)) - pcbnew.ToMM(item.GetWidth())/2
        if clearance < 4.0 - 1e-6:
            copper_intrusions.append({"hole": ref, "type": type(item).__name__,
                                      "net": item.GetNetname(), "clearance_mm": round(clearance, 4)})
    for other in board.GetFootprints():
        if other.GetReference() == ref:
            continue
        for other_pad in other.Pads():
            if other_pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                continue
            p = other_pad.GetPosition()
            radius = max(pcbnew.ToMM(other_pad.GetSize().x), pcbnew.ToMM(other_pad.GetSize().y))/2
            clearance = math.hypot(pcbnew.ToMM(p.x)-cx, pcbnew.ToMM(p.y)-cy)-radius
            if clearance < 4.0 - 1e-6:
                copper_intrusions.append({"hole": ref, "type": "pad", "reference": other.GetReference(),
                                          "pad": other_pad.GetNumber(), "clearance_mm": round(clearance, 4)})
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        for zone in board.Zones():
            if zone.GetIsRuleArea() or not zone.IsOnLayer(layer):
                continue
            polys = zone.GetFilledPolysList(layer)
            for radius in (0.0, 1.0, 2.0, 3.0, 3.8):
                for degrees in range(0, 360, 15):
                    sample = pcbnew.VECTOR2I(pcbnew.FromMM(cx + radius*math.cos(math.radians(degrees))),
                                             pcbnew.FromMM(cy + radius*math.sin(math.radians(degrees))))
                    if polys.Contains(sample):
                        filled_samples.append({"hole": ref, "layer": pcbnew.LayerName(layer),
                                               "radius_mm": radius, "angle_deg": degrees,
                                               "zone": zone.GetNetname()})

expected_j5_nets = {"1": "/GND", "2": "/AUX_3V3", "3": "/OLED_SCL", "4": "/OLED_SDA"}
j5_rule = rule_areas.get("J5_HANDSOLDER_CLEARANCE", {})
m3_rules = [rule_areas.get(f"{ref}_M3_COPPER_KEEPOUT", {}) for ref in HOLES]
status = (
    {number: pad.GetNetname() for number, pad in j5_pads.items()} == expected_j5_nets
    and len(j5_track) == 1 and bool(j5_global_zones)
    and j5_rule.get("layers") == ["B.Cu"]
    and j5_rule.get("copperpour_not_allowed")
    and not j5_rule.get("tracks_not_allowed") and not j5_rule.get("vias_not_allowed")
    and len(rule_areas) == 4
    and all(rule.get("layers") == ["B.Cu", "F.Cu"]
            and rule.get("copperpour_not_allowed") and rule.get("tracks_not_allowed")
            and rule.get("vias_not_allowed") and rule.get("pads_allowed")
            and rule.get("footprints_allowed") for rule in m3_rules)
    and all(item["pad_count"] == 1 and item["pad_attribute"] == "NPTH"
            and item["drill_mm"] == [3.2, 3.2] and item["pad_size_mm"] == [3.2, 3.2]
            and item["net"] == "" and item["edge_center_distance_mm"] >= 7.0
            for item in holes.values())
    and not copper_intrusions and not filled_samples and not any(bcu_islands)
)

print(json.dumps({
    "status": "PASS" if status else "FAIL",
    "J5_pad_nets": {number: pad.GetNetname() for number, pad in j5_pads.items()},
    "J5_rule_area": j5_rule,
    "J5_explicit_GND_track": j5_track,
    "J5_connected_global_B_Cu_GND_zones": len(j5_global_zones),
    "holes": holes,
    "M3_rule_areas": {name: rule_areas[name] for name in sorted(rule_areas) if name.startswith("H")},
    "copper_intrusions_inside_M3_8mm_regions": copper_intrusions,
    "filled_zone_samples_inside_M3_7p6mm_diameter": filled_samples,
    "B_Cu_GND_filled_outline_island_flags": bcu_islands,
    "no_isolated_B_Cu_GND_fill": not any(bcu_islands),
    "antenna_clearance": {"H3_center_to_left_boundary_mm": 8.7,
                           "H3_keepout_to_left_boundary_mm": 4.7},
    "documented_module_envelopes": {
        "ESP32_mm": [109.65, 6.25, 137.75, 57.35],
        "OLED_mm": [50.95, 13.95, 77.05, 40.05],
        "H2_keepout_to_OLED_vertical_gap_mm": 2.95,
        "H3_keepout_to_ESP32_horizontal_gap_mm": 9.65,
    },
}, indent=2, sort_keys=True))
raise SystemExit(0 if status else 1)
