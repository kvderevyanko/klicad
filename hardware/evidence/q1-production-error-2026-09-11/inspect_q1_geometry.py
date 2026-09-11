#!/usr/bin/env python3
"""Read-only geometry inventory for the Q1 footprint-correction plan."""

from pathlib import Path
import math

import pcbnew


ROOT = Path(__file__).resolve().parents[3]
BOARD_PATH = ROOT / "hardware" / "esp32-e220.kicad_pcb"
MM = pcbnew.ToMM


def xy(point):
    return (MM(point.x), MM(point.y))


def fmt_xy(point):
    x, y = xy(point)
    return f"({x:.3f}, {y:.3f})"


board = pcbnew.LoadBoard(str(BOARD_PATH))
q1 = next(fp for fp in board.GetFootprints() if fp.GetReference() == "Q1")
qx, qy = xy(q1.GetPosition())

print(f"board={BOARD_PATH.relative_to(ROOT)}")
print(
    f"Q1 footprint={q1.GetFPID().GetLibItemName()} position={fmt_xy(q1.GetPosition())} "
    f"rotation={q1.GetOrientationDegrees():.3f} layer={board.GetLayerName(q1.GetLayer())}"
)
print("Q1 pads:")
for pad in sorted(q1.Pads(), key=lambda item: item.GetNumber()):
    sx, sy = MM(pad.GetSize().x), MM(pad.GetSize().y)
    print(
        f"  pad={pad.GetNumber()} net={pad.GetNetname()} position={fmt_xy(pad.GetPosition())} "
        f"size=({sx:.3f}, {sy:.3f}) rotation={pad.GetOrientationDegrees():.3f}"
    )

print("nearby footprints (reference point within 12 mm):")
near_footprints = []
for fp in board.GetFootprints():
    fx, fy = xy(fp.GetPosition())
    distance = math.hypot(fx - qx, fy - qy)
    if fp.GetReference() != "Q1" and distance <= 12.0:
        near_footprints.append((distance, fp))
for distance, fp in sorted(near_footprints, key=lambda item: item[0]):
    print(
        f"  ref={fp.GetReference()} footprint={fp.GetFPID().GetLibItemName()} "
        f"position={fmt_xy(fp.GetPosition())} rotation={fp.GetOrientationDegrees():.3f} "
        f"distance={distance:.3f}"
    )

print("copper items with an endpoint/position within 8 mm of Q1:")
near_tracks = []
for item in board.GetTracks():
    if isinstance(item, pcbnew.PCB_VIA):
        points = [item.GetPosition()]
        kind = "via"
    else:
        points = [item.GetStart(), item.GetEnd()]
        kind = "segment"
    distance = min(math.hypot(xy(point)[0] - qx, xy(point)[1] - qy) for point in points)
    if distance <= 8.0:
        near_tracks.append((distance, kind, item))
for distance, kind, item in sorted(near_tracks, key=lambda entry: (entry[0], entry[1], entry[2].GetNetname())):
    if kind == "via":
        print(
            f"  via net={item.GetNetname()} at={fmt_xy(item.GetPosition())} "
            f"diameter={MM(item.GetWidth()):.3f} drill={MM(item.GetDrillValue()):.3f} distance={distance:.3f}"
        )
    else:
        print(
            f"  segment net={item.GetNetname()} layer={board.GetLayerName(item.GetLayer())} "
            f"start={fmt_xy(item.GetStart())} end={fmt_xy(item.GetEnd())} "
            f"width={MM(item.GetWidth()):.3f} distance={distance:.3f}"
        )

print("zones whose bounding box contains Q1 reference point:")
for zone in board.Zones():
    box = zone.GetBoundingBox()
    pos = q1.GetPosition()
    if box.Contains(pos):
        print(
            f"  net={zone.GetNetname()} layers={','.join(board.GetLayerName(layer) for layer in zone.GetLayerSet().Seq())} "
            f"clearance={MM(zone.GetLocalClearance()):.3f} min_thickness={MM(zone.GetMinThickness()):.3f}"
        )

settings = board.GetDesignSettings()
print(f"board min_clearance={MM(settings.GetSmallestClearanceValue()):.3f}")
