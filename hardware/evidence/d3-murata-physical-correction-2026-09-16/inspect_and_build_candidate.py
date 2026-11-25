#!/usr/bin/env python3
"""Read active geometry and make a geometry-only D3/Murata planning copy.

This is retained planner evidence.  It never writes the active PCB.
"""

from __future__ import annotations

import math
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[3]
ACTIVE = ROOT / "hardware" / "esp32-e220.kicad_pcb"
OUT = Path(__file__).resolve().parent / "candidate-d3-murata.kicad_pcb"

REFS = ("D3", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10")

# Pad sizes are X along the footprint-local terminal axis and Y transverse.
TARGET_SIZES = {
    "D3": (2.160, 2.260),
    "C1": (1.200, 1.300),
    "C2": (0.700, 0.700),
    "C3": (0.700, 1.300),
    "C4": (0.700, 0.700),
    "C5": (0.750, 0.900),
    "C6": (0.700, 0.700),
    "C7": (0.700, 0.700),
    "C8": (0.700, 0.700),
    "C9": (1.200, 1.300),
    "C10": (1.200, 1.300),
}


def mm(value: int) -> float:
    return pcbnew.ToMM(value)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I_MM(x, y)


def coord(pos: pcbnew.VECTOR2I) -> tuple[float, float]:
    return mm(pos.x), mm(pos.y)


def fp_by_ref(board: pcbnew.BOARD, ref: str) -> pcbnew.FOOTPRINT:
    found = [fp for fp in board.GetFootprints() if fp.GetReference() == ref]
    if len(found) != 1:
        raise RuntimeError(f"{ref}: expected one footprint, got {len(found)}")
    return found[0]


def track_desc(item: pcbnew.BOARD_CONNECTED_ITEM) -> str:
    if isinstance(item, pcbnew.PCB_VIA):
        x, y = coord(item.GetPosition())
        return (
            f"VIA net={item.GetNetname()} at=({x:.4f},{y:.4f}) "
            f"diameter={mm(item.GetWidth()):.4f} drill={mm(item.GetDrillValue()):.4f}"
        )
    sx, sy = coord(item.GetStart())
    ex, ey = coord(item.GetEnd())
    return (
        f"TRACK net={item.GetNetname()} layer={item.GetLayerName()} "
        f"start=({sx:.4f},{sy:.4f}) end=({ex:.4f},{ey:.4f}) "
        f"width={mm(item.GetWidth()):.4f}"
    )


def endpoints(item: pcbnew.BOARD_CONNECTED_ITEM) -> list[pcbnew.VECTOR2I]:
    if isinstance(item, pcbnew.PCB_VIA):
        return [item.GetPosition()]
    return [item.GetStart(), item.GetEnd()]


def rotate_local(x: float, y: float, degrees: float) -> tuple[float, float]:
    radians = math.radians(degrees)
    return (
        x * math.cos(radians) - y * math.sin(radians),
        x * math.sin(radians) + y * math.cos(radians),
    )


def set_d3_centres(fp: pcbnew.FOOTPRINT) -> None:
    fx, fy = coord(fp.GetPosition())
    angle = fp.GetOrientation().AsDegrees()
    local_x = {"1": -2.450, "2": 2.450}
    for pad in fp.Pads():
        dx, dy = rotate_local(local_x[pad.GetNumber()], 0.0, angle)
        pad.SetPosition(point(fx + dx, fy + dy))


def replace_courtyard(fp: pcbnew.FOOTPRINT, half_x: float, half_y: float) -> None:
    """Replace F.CrtYd with a local rectangle transformed to board coordinates."""
    for item in list(fp.GraphicalItems()):
        if item.GetLayer() == pcbnew.F_CrtYd:
            fp.Remove(item)
    fx, fy = coord(fp.GetPosition())
    angle = fp.GetOrientation().AsDegrees()
    local_segments = (
        ((-half_x, -half_y), (half_x, -half_y)),
        ((half_x, -half_y), (half_x, half_y)),
        ((half_x, half_y), (-half_x, half_y)),
        ((-half_x, half_y), (-half_x, -half_y)),
    )
    for (x1, y1), (x2, y2) in local_segments:
        dx1, dy1 = rotate_local(x1, y1, angle)
        dx2, dy2 = rotate_local(x2, y2, angle)
        item = pcbnew.PCB_SHAPE(fp)
        item.SetShape(pcbnew.S_SEGMENT)
        item.SetStart(point(fx + dx1, fy + dy1))
        item.SetEnd(point(fx + dx2, fy + dy2))
        item.SetLayer(pcbnew.F_CrtYd)
        item.SetWidth(pcbnew.FromMM(0.050))
        fp.Add(item)


def print_footprint(board: pcbnew.BOARD, ref: str, label: str) -> None:
    fp = fp_by_ref(board, ref)
    fx, fy = coord(fp.GetPosition())
    print(
        f"{label} {ref} footprint={fp.GetFPID().GetLibItemName()} "
        f"at=({fx:.4f},{fy:.4f}) rot={fp.GetOrientation().AsDegrees():.1f}"
    )
    tracks = list(board.GetTracks())
    for pad in sorted(fp.Pads(), key=lambda item: item.GetNumber()):
        px, py = coord(pad.GetPosition())
        size = pad.GetSize()
        mask_margin = pad.GetLocalSolderMaskMargin()
        mask_text = "inherited" if mask_margin is None else f"{mm(mask_margin):.4f}"
        print(
            f"  pad={pad.GetNumber()} net={pad.GetNetname()} center=({px:.4f},{py:.4f}) "
            f"size=({mm(size.x):.4f},{mm(size.y):.4f}) "
            f"local_mask_margin={mask_text}"
        )
        touching = []
        for item in tracks:
            if item.GetNetCode() != pad.GetNetCode():
                continue
            if any(pad.HitTest(endpoint) for endpoint in endpoints(item)):
                touching.append(track_desc(item))
        for text in sorted(set(touching)):
            print(f"    endpoint-in-pad: {text}")
    box = fp.GetCourtyard(pcbnew.F_Cu).BBox()
    print(
        f"  courtyard=({mm(box.GetX()):.4f},{mm(box.GetY()):.4f}).."
        f"({mm(box.GetRight()):.4f},{mm(box.GetBottom()):.4f})"
    )


def main() -> None:
    active = pcbnew.LoadBoard(str(ACTIVE))
    print(f"ACTIVE={ACTIVE}")
    for ref in REFS:
        print_footprint(active, ref, "OLD")

    candidate = pcbnew.LoadBoard(str(ACTIVE))
    for ref in REFS:
        fp = fp_by_ref(candidate, ref)
        width, height = TARGET_SIZES[ref]
        for pad in fp.Pads():
            pad.SetSize(point(width, height))
        if ref == "D3":
            set_d3_centres(fp)
            replace_courtyard(fp, 3.800, 2.500)
        elif ref in {"C1", "C9", "C10"}:
            # The fixed 1.20-mm land length reaches local X +/-1.60 mm.
            # A 1.65-mm half-width encloses copper and preserves a positive
            # courtyard gap to adjacent C3 at the frozen placement.
            replace_courtyard(fp, 1.650, 1.125)

    pcbnew.SaveBoard(str(OUT), candidate)
    print(f"CANDIDATE={OUT}")
    reread = pcbnew.LoadBoard(str(OUT))
    for ref in REFS:
        print_footprint(reread, ref, "NEW")


if __name__ == "__main__":
    main()
