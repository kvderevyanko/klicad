#!/usr/bin/env python3
"""Apply one reviewed D3/Murata physical stage to the active PCB."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import pcbnew


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ACTIVE = ROOT / "hardware" / "esp32-e220.kicad_pcb"


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


def assert_inventory(board: pcbnew.BOARD) -> None:
    if len(list(board.GetFootprints())) != 40:
        raise RuntimeError("footprint inventory changed")
    if len(list(board.GetTracks())) != 260:
        raise RuntimeError("track/via inventory changed")
    if len(list(board.Zones())) != 11:
        raise RuntimeError("zone/rule-area inventory changed")


def set_sizes(board: pcbnew.BOARD, refs: tuple[str, ...], size: tuple[float, float], description: str) -> None:
    for ref in refs:
        fp = fp_by_ref(board, ref)
        fp.SetLibDescription(description)
        for pad in fp.Pads():
            pad.SetSize(point(*size))


def apply_stage(stage: str) -> None:
    board = pcbnew.LoadBoard(str(ACTIVE))
    assert_inventory(board)
    if stage == "d3":
        fp = fp_by_ref(board, "D3")
        fp.SetLibDescription(
            "Littelfuse SMBJ10CA bidirectional TVS in DO-214AA/SMB. Manufacturer recommended solder lands: "
            "2.160x2.260 mm, 2.740-mm inner gap, 4.900-mm centre pitch."
        )
        fx, fy = coord(fp.GetPosition())
        angle = fp.GetOrientation().AsDegrees()
        for pad in fp.Pads():
            if pad.GetNumber() not in {"1", "2"}:
                raise RuntimeError(f"D3 unexpected pad {pad.GetNumber()}")
            pad.SetSize(point(2.160, 2.260))
            local_x = -2.450 if pad.GetNumber() == "1" else 2.450
            dx, dy = rotate_local(local_x, 0.0, angle)
            pad.SetPosition(point(fx + dx, fy + dy))
        replace_rectangle(fp, pcbnew.F_Fab, 2.2025, 1.810)
        replace_rectangle(fp, pcbnew.F_CrtYd, 3.800, 2.500)
    elif stage == "grm188":
        set_sizes(
            board,
            ("C2", "C4", "C6", "C7", "C8"),
            (0.700, 0.700),
            "Murata GRM18 1608 metric C2/C4/C6/C7/C8. Manufacturer Table 2 reflow lands: "
            "a=0.75, b=0.70, c=0.70 mm on 1.45-mm centres.",
        )
    elif stage == "grm21":
        set_sizes(
            board,
            ("C1", "C9", "C10"),
            (1.200, 1.300),
            "Murata GRM21 2012 metric C1/C9/C10. Manufacturer Table 2 reflow lands: "
            "a=0.80, b=1.20, c=1.30 mm on 2.00-mm centres.",
        )
        for ref in ("C1", "C9", "C10"):
            replace_rectangle(fp_by_ref(board, ref), pcbnew.F_CrtYd, 1.650, 1.125)
    elif stage == "c5":
        fp = fp_by_ref(board, "C5")
        fp.SetFPIDAsString("Murata_GRM188R61A106MAAL_1608Metric")
        set_sizes(
            board,
            ("C5",),
            (0.750, 0.900),
            "Murata GRM188R61A106MAAL 1608 metric C5. Manufacturer Table 2 reflow lands: "
            "a=0.70, b=0.75, c=0.90 mm on 1.45-mm centres.",
        )
    elif stage == "c3":
        fp = fp_by_ref(board, "C3")
        fp.SetFPIDAsString("Murata_GRM21BR61A226ME44_2012Metric")
        set_sizes(
            board,
            ("C3",),
            (0.700, 1.300),
            "Murata GRM21BR61A226ME44 2012 metric C3. Manufacturer Table 2 reflow lands: "
            "a=1.30, b=0.70, c=1.30 mm on 2.00-mm centres.",
        )
    elif stage == "refill":
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    else:
        raise RuntimeError(f"unsupported stage {stage}")
    pcbnew.SaveBoard(str(ACTIVE), board)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("d3", "grm188", "grm21", "c5", "c3", "refill"))
    args = parser.parse_args()
    apply_stage(args.stage)


if __name__ == "__main__":
    main()
