#!/usr/bin/env python3
"""Apply only the reviewed J6/J9 hand-solder candidate to an evidence PCB.

This planner fixture refuses the active PCB path and the wrong released base.
It is evidence only; the implementation owner must create the production source.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pcbnew


RELEASED_SHA256 = "a9fa9493ec7dfbc3f0cfb2c761cb3d6d895543bd6ade34848f83fb86fcffec0c"
ACTIVE = Path("hardware/esp32-e220.kicad_pcb").resolve()
MM = pcbnew.FromMM


def pt(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(MM(x), MM(y))


def xy(item: pcbnew.PCB_TRACK, which: str) -> tuple[float, float]:
    point = getattr(item, which)()
    return (round(pcbnew.ToMM(point.x), 3), round(pcbnew.ToMM(point.y), 3))


def add_pour_keepout(board: pcbnew.BOARD, name: str,
                     outline: tuple[tuple[float, float], ...]) -> None:
    area = pcbnew.ZONE(board)
    area.SetLayer(pcbnew.B_Cu)
    area.SetZoneName(name)
    area.SetIsRuleArea(True)
    area.SetDoNotAllowTracks(False)
    area.SetDoNotAllowVias(False)
    area.SetDoNotAllowPads(False)
    area.SetDoNotAllowFootprints(False)
    area.SetDoNotAllowZoneFills(True)
    area.SetLocalClearance(MM(0))
    area.SetMinThickness(MM(0.25))
    polygon = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in outline:
        polygon.Append(pt(x, y))
    polygon.SetClosed(True)
    area.AddPolygon(polygon)
    board.Add(area)


def remove_exact_track(board: pcbnew.BOARD, net_name: str,
                       start: tuple[float, float], end: tuple[float, float],
                       width: float, layer: int) -> None:
    matches = []
    for item in board.GetTracks():
        if isinstance(item, pcbnew.PCB_VIA):
            continue
        forward = xy(item, "GetStart") == start and xy(item, "GetEnd") == end
        reverse = xy(item, "GetStart") == end and xy(item, "GetEnd") == start
        if (item.GetNetname() == net_name and item.GetLayer() == layer
                and round(pcbnew.ToMM(item.GetWidth()), 3) == width
                and (forward or reverse)):
            matches.append(item)
    if len(matches) != 1:
        raise RuntimeError(f"expected one legacy track, found {len(matches)}")
    board.Remove(matches[0])


def add_track(board: pcbnew.BOARD, start: tuple[float, float],
              end: tuple[float, float]) -> None:
    track = pcbnew.PCB_TRACK(board)
    track.SetNet(board.FindNet("/GND"))
    track.SetStart(pt(*start))
    track.SetEnd(pt(*end))
    track.SetWidth(MM(0.80))
    track.SetLayer(pcbnew.B_Cu)
    board.Add(track)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    args = parser.parse_args()
    target = args.board.resolve()
    if target == ACTIVE:
        raise RuntimeError("planner refuses active PCB")
    actual = hashlib.sha256(target.read_bytes()).hexdigest()
    if actual != RELEASED_SHA256:
        raise RuntimeError(f"released-base SHA mismatch: {actual}")

    board = pcbnew.LoadBoard(str(target))
    add_pour_keepout(
        board,
        "J6_HANDSOLDER_CLEARANCE",
        ((91.750, 15.750), (96.250, 15.750),
         (96.250, 32.950), (91.750, 32.950)),
    )
    add_pour_keepout(
        board,
        "J9_HANDSOLDER_CLEARANCE",
        ((97.750, 51.750), (103.000, 51.750),
         (103.000, 61.330), (97.750, 61.330)),
    )

    # Replace the legacy direct J6-to-ESP32 0.25-mm segment with a short,
    # visibly identifiable branch that exits the local no-pour window.
    remove_exact_track(board, "/GND", (94.000, 18.000),
                       (104.000, 18.000), 0.25, pcbnew.B_Cu)
    add_track(board, (94.000, 18.000), (97.000, 18.000))
    add_track(board, (100.000, 59.080), (97.000, 59.080))

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(target), board)


if __name__ == "__main__":
    main()
