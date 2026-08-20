#!/usr/bin/env python3
"""Read-only geometry inventory for the E220 signal-routing transaction."""
import pcbnew

BOARD = "hardware/esp32-e220.kicad_pcb"


def mm(value):
    return pcbnew.ToMM(value)


board = pcbnew.LoadBoard(BOARD)
print("ref  at(mm)          rotation  bbox(mm)")
for footprint in sorted(board.GetFootprints(), key=lambda item: item.GetReference()):
    position = footprint.GetPosition()
    box = footprint.GetBoundingBox()
    print(
        f"{footprint.GetReference():4} {mm(position.x):7.3f},{mm(position.y):7.3f} "
        f"{footprint.GetOrientationDegrees():7.1f} "
        f"({mm(box.GetX()):.1f},{mm(box.GetY()):.1f})-"
        f"({mm(box.GetRight()):.1f},{mm(box.GetBottom()):.1f})"
    )

print("\nzones")
for zone in board.Zones():
    box = zone.GetBoundingBox()
    print(
        zone.GetNetname(), pcbnew.LayerName(zone.GetLayer()),
        f"({mm(box.GetX()):.3f},{mm(box.GetY()):.3f})-"
        f"({mm(box.GetRight()):.3f},{mm(box.GetBottom()):.3f})",
    )

print("\ntracks")
for item in board.GetTracks():
    if isinstance(item, pcbnew.PCB_VIA):
        position = item.GetPosition()
        print(
            item.GetNetname(), "VIA", f"{mm(position.x):.3f},{mm(position.y):.3f}",
            f"dia={mm(item.GetWidth(pcbnew.F_Cu)):.3f}",
            f"drill={mm(item.GetDrillValue()):.3f}",
        )
    else:
        start, end = item.GetStart(), item.GetEnd()
        print(
            item.GetNetname(), pcbnew.LayerName(item.GetLayer()),
            f"{mm(start.x):.3f},{mm(start.y):.3f}->{mm(end.x):.3f},{mm(end.y):.3f}",
            f"w={mm(item.GetWidth()):.3f}",
        )
