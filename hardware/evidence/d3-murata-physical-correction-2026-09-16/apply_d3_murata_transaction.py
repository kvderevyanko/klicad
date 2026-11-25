#!/usr/bin/env python3
"""Apply the reviewed D3/Murata geometry transaction to the active PCB."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[3]
ACTIVE = ROOT / "hardware" / "esp32-e220.kicad_pcb"
BACKUP = Path(__file__).resolve().parent / "implementation-backup" / "esp32-e220.pre-d3-murata.kicad_pcb"

SIZES = {
    "D3": (2.160, 2.260),
    "C1": (1.200, 1.300), "C9": (1.200, 1.300), "C10": (1.200, 1.300),
    "C2": (0.700, 0.700), "C4": (0.700, 0.700),
    "C6": (0.700, 0.700), "C7": (0.700, 0.700), "C8": (0.700, 0.700),
    "C3": (0.700, 1.300),
    "C5": (0.750, 0.900),
}

OLD_SIZES = {
    "D3": (2.500, 2.300),
    "C1": (1.150, 1.400), "C3": (1.150, 1.400),
    "C9": (1.150, 1.400), "C10": (1.150, 1.400),
    "C2": (0.950, 1.000), "C4": (0.950, 1.000), "C5": (0.950, 1.000),
    "C6": (0.950, 1.000), "C7": (0.950, 1.000), "C8": (0.950, 1.000),
}

NETS = {
    "D3": {"1": "/BAT_FUSED", "2": "/GND"},
    "C1": {"1": "/BUCK_IN", "2": "/GND"},
    "C2": {"1": "/BUCK_IN", "2": "/GND"},
    "C3": {"1": "/5V_SYS", "2": "/GND"},
    "C4": {"1": "/SS_TR", "2": "/GND"},
    "C5": {"1": "/5V_SYS", "2": "/GND"},
    "C6": {"1": "/5V_SYS", "2": "/GND"},
    "C7": {"1": "/5V_SYS", "2": "/GND"},
    "C8": {"1": "/BAT_SENSE", "2": "/GND"},
    "C9": {"1": "/5V_SYS", "2": "/GND"},
    "C10": {"1": "/AUX_3V3", "2": "/GND"},
}

DESCRIPTIONS = {
    "D3": "Littelfuse SMBJ10CA in DO-214AA/SMB. Manufacturer recommended solder pad layout: 2.160x2.260 mm lands, 2.740-mm inner gap, 4.900-mm centre pitch; bidirectional CA device.",
    "C1": "Murata GRM21 2012 metric (0805), C1/C9/C10. Manufacturer Table 2 reflow lands: a=0.80, b=1.20, c=1.30 mm on 2.00-mm centres.",
    "C2": "Murata GRM18 1608 metric (0603), C2/C4/C6/C7/C8. Manufacturer Table 2 reflow lands: a=0.75, b=0.70, c=0.70 mm on 1.45-mm centres.",
    "C3": "Murata GRM21BR61A226ME44 2012 metric (0805), C3. Manufacturer Table 2 reflow lands: a=1.30, b=0.70, c=1.30 mm on 2.00-mm centres.",
    "C4": "Murata GRM18 1608 metric (0603), C2/C4/C6/C7/C8. Manufacturer Table 2 reflow lands: a=0.75, b=0.70, c=0.70 mm on 1.45-mm centres.",
    "C5": "Murata GRM188R61A106MAAL 1608 metric (0603), C5. Manufacturer Table 2 reflow lands: a=0.70, b=0.75, c=0.90 mm on 1.45-mm centres.",
    "C6": "Murata GRM18 1608 metric (0603), C2/C4/C6/C7/C8. Manufacturer Table 2 reflow lands: a=0.75, b=0.70, c=0.70 mm on 1.45-mm centres.",
    "C7": "Murata GRM18 1608 metric (0603), C2/C4/C6/C7/C8. Manufacturer Table 2 reflow lands: a=0.75, b=0.70, c=0.70 mm on 1.45-mm centres.",
    "C8": "Murata GRM18 1608 metric (0603), C2/C4/C6/C7/C8. Manufacturer Table 2 reflow lands: a=0.75, b=0.70, c=0.70 mm on 1.45-mm centres.",
    "C9": "Murata GRM21 2012 metric (0805), C1/C9/C10. Manufacturer Table 2 reflow lands: a=0.80, b=1.20, c=1.30 mm on 2.00-mm centres.",
    "C10": "Murata GRM21 2012 metric (0805), C1/C9/C10. Manufacturer Table 2 reflow lands: a=0.80, b=1.20, c=1.30 mm on 2.00-mm centres.",
}


def mm(value: int) -> float:
    return pcbnew.ToMM(value)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I_MM(x, y)


def coord(pos: pcbnew.VECTOR2I) -> tuple[float, float]:
    return mm(pos.x), mm(pos.y)


def fp_by_ref(board: pcbnew.BOARD, ref: str) -> pcbnew.FOOTPRINT:
    matches = [fp for fp in board.GetFootprints() if fp.GetReference() == ref]
    if len(matches) != 1:
        raise RuntimeError(f"{ref}: expected one footprint, found {len(matches)}")
    return matches[0]


def rotate_local(x: float, y: float, degrees: float) -> tuple[float, float]:
    angle = math.radians(degrees)
    return x * math.cos(angle) - y * math.sin(angle), x * math.sin(angle) + y * math.cos(angle)


def replace_rectangle(fp: pcbnew.FOOTPRINT, layer: int, half_x: float, half_y: float) -> None:
    for item in list(fp.GraphicalItems()):
        if item.GetLayer() == layer:
            fp.Remove(item)
    fx, fy = coord(fp.GetPosition())
    angle = fp.GetOrientation().AsDegrees()
    segments = (
        ((-half_x, -half_y), (half_x, -half_y)),
        ((half_x, -half_y), (half_x, half_y)),
        ((half_x, half_y), (-half_x, half_y)),
        ((-half_x, half_y), (-half_x, -half_y)),
    )
    for (x1, y1), (x2, y2) in segments:
        dx1, dy1 = rotate_local(x1, y1, angle)
        dx2, dy2 = rotate_local(x2, y2, angle)
        item = pcbnew.PCB_SHAPE(fp)
        item.SetShape(pcbnew.S_SEGMENT)
        item.SetStart(point(fx + dx1, fy + dy1))
        item.SetEnd(point(fx + dx2, fy + dy2))
        item.SetLayer(layer)
        item.SetWidth(pcbnew.FromMM(0.100 if layer == pcbnew.F_Fab else 0.050))
        fp.Add(item)


def assert_prestate(board: pcbnew.BOARD) -> None:
    if ACTIVE.read_bytes() != BACKUP.read_bytes():
        raise RuntimeError("active PCB is not the named approved pre-transaction backup")
    if len(list(board.GetFootprints())) != 40 or len(list(board.GetTracks())) != 260 or len(list(board.Zones())) != 11:
        raise RuntimeError("active PCB inventory differs from approved baseline")
    for ref, old_size in OLD_SIZES.items():
        fp = fp_by_ref(board, ref)
        actual_nets = {pad.GetNumber(): pad.GetNetname() for pad in fp.Pads()}
        if actual_nets != NETS[ref]:
            raise RuntimeError(f"{ref}: prestate nets {actual_nets}, expected {NETS[ref]}")
        for pad in fp.Pads():
            size = coord(pad.GetSize())
            if any(abs(actual - expected) > 0.0005 for actual, expected in zip(size, old_size)):
                raise RuntimeError(f"{ref}.{pad.GetNumber()}: prestate size {size}, expected {old_size}")


def apply_geometry() -> None:
    board = pcbnew.LoadBoard(str(ACTIVE))
    assert_prestate(board)
    for ref, size in SIZES.items():
        fp = fp_by_ref(board, ref)
        fp.SetLibDescription(DESCRIPTIONS[ref])
        for pad in fp.Pads():
            pad.SetSize(point(*size))
        if ref == "D3":
            fx, fy = coord(fp.GetPosition())
            angle = fp.GetOrientation().AsDegrees()
            for pad in fp.Pads():
                local_x = -2.450 if pad.GetNumber() == "1" else 2.450
                dx, dy = rotate_local(local_x, 0.0, angle)
                pad.SetPosition(point(fx + dx, fy + dy))
            replace_rectangle(fp, pcbnew.F_Fab, 2.2025, 1.8100)
            replace_rectangle(fp, pcbnew.F_CrtYd, 3.800, 2.500)
        elif ref in {"C1", "C9", "C10"}:
            replace_rectangle(fp, pcbnew.F_CrtYd, 1.650, 1.125)
        elif ref == "C3":
            fp.SetFPIDAsString("Carrier:Murata_GRM21BR61A226ME44_2012Metric")
        elif ref == "C5":
            fp.SetFPIDAsString("Carrier:Murata_GRM188R61A106MAAL_1608Metric")
    pcbnew.SaveBoard(str(ACTIVE), board)


def refill() -> None:
    board = pcbnew.LoadBoard(str(ACTIVE))
    if len(list(board.GetTracks())) != 260 or len(list(board.Zones())) != 11:
        raise RuntimeError("pre-refill PCB inventory differs from approved transaction")
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(ACTIVE), board)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("geometry", "refill"))
    args = parser.parse_args()
    if args.phase == "geometry":
        apply_geometry()
    else:
        refill()


if __name__ == "__main__":
    main()
