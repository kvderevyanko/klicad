#!/usr/bin/env python3
"""Reproduce the released Rev.1 J6/J9 B.Cu hand-solder correction.

The transform is intentionally narrow and accepts only the reviewed Rev.1
release PCB as its input.  It writes a separate output board, leaving its
source untouched.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pcbnew


RELEASED_SHA256 = "a9fa9493ec7dfbc3f0cfb2c761cb3d6d895543bd6ade34848f83fb86fcffec0c"
MM = pcbnew.FromMM


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(MM(x), MM(y))


def track_xy(track: pcbnew.PCB_TRACK, getter: str) -> tuple[float, float]:
    xy = getattr(track, getter)()
    return round(pcbnew.ToMM(xy.x), 3), round(pcbnew.ToMM(xy.y), 3)


def add_pour_keepout(
    board: pcbnew.BOARD,
    name: str,
    outline: tuple[tuple[float, float], ...],
) -> None:
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
        polygon.Append(point(x, y))
    polygon.SetClosed(True)
    area.AddPolygon(polygon)
    board.Add(area)


def remove_released_j6_ground_track(board: pcbnew.BOARD) -> None:
    expected = {(94.0, 18.0), (104.0, 18.0)}
    matches = []
    for item in board.GetTracks():
        if isinstance(item, pcbnew.PCB_VIA):
            continue
        if (
            item.GetNetname() == "/GND"
            and item.GetLayer() == pcbnew.B_Cu
            and round(pcbnew.ToMM(item.GetWidth()), 3) == 0.25
            and {track_xy(item, "GetStart"), track_xy(item, "GetEnd")} == expected
        ):
            matches.append(item)
    if len(matches) != 1:
        raise RuntimeError(f"expected one released J6 GND track, found {len(matches)}")
    board.Remove(matches[0])


def add_ground_track(
    board: pcbnew.BOARD,
    start: tuple[float, float],
    end: tuple[float, float],
) -> None:
    track = pcbnew.PCB_TRACK(board)
    track.SetNet(board.FindNet("/GND"))
    track.SetStart(point(*start))
    track.SetEnd(point(*end))
    track.SetWidth(MM(0.80))
    track.SetLayer(pcbnew.B_Cu)
    board.Add(track)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if source == output:
        raise RuntimeError("source and output must differ")
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    if actual != RELEASED_SHA256:
        raise RuntimeError(f"released-source SHA mismatch: {actual}")

    board = pcbnew.LoadBoard(str(source))
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
    remove_released_j6_ground_track(board)
    add_ground_track(board, (94.000, 18.000), (97.000, 18.000))
    add_ground_track(board, (100.000, 59.080), (97.000, 59.080))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    output.parent.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(output), board)


if __name__ == "__main__":
    main()
