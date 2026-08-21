#!/usr/bin/env python3
"""Build the read-only Rev.1 J5/M3 plan candidate from the exact release."""

from __future__ import annotations

import argparse
import hashlib
import math
from pathlib import Path

import pcbnew


RELEASED_SHA256 = "9f15f061cd98cf069137ce9181a9edf8d9903167ee9641b9fa9af746eb992acd"
ACTIVE = Path("hardware/esp32-e220.kicad_pcb").resolve()
HERE = Path(__file__).resolve().parent
MM = pcbnew.FromMM


def pt(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(MM(x), MM(y))


def add_rule_area(board: pcbnew.BOARD, name: str,
                  points: tuple[tuple[float, float], ...],
                  layers: pcbnew.LSET, tracks: bool, vias: bool) -> None:
    area = pcbnew.ZONE(board)
    area.SetLayerSet(layers)
    area.SetZoneName(name)
    area.SetIsRuleArea(True)
    area.SetDoNotAllowTracks(tracks)
    area.SetDoNotAllowVias(vias)
    area.SetDoNotAllowPads(False)
    area.SetDoNotAllowFootprints(False)
    area.SetDoNotAllowZoneFills(True)
    area.SetLocalClearance(MM(0))
    area.SetMinThickness(MM(0.25))
    polygon = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in points:
        polygon.Append(pt(x, y))
    polygon.SetClosed(True)
    area.AddPolygon(polygon)
    board.Add(area)


def rectangle(xmin: float, ymin: float, xmax: float, ymax: float):
    return ((xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax))


def circle(cx: float, cy: float, radius: float, vertices: int = 32):
    return tuple(
        (cx + radius * math.cos(2 * math.pi * index / vertices),
         cy + radius * math.sin(2 * math.pi * index / vertices))
        for index in range(vertices)
    )


def one_layer(layer: int) -> pcbnew.LSET:
    layers = pcbnew.LSET()
    layers.AddLayer(layer)
    return layers


def add_ground_track(board: pcbnew.BOARD,
                     start: tuple[float, float], end: tuple[float, float]) -> None:
    track = pcbnew.PCB_TRACK(board)
    track.SetNet(board.FindNet("/GND"))
    track.SetStart(pt(*start))
    track.SetEnd(pt(*end))
    track.SetWidth(MM(0.80))
    track.SetLayer(pcbnew.B_Cu)
    board.Add(track)


def add_hole(board: pcbnew.BOARD, ref: str, x: float, y: float) -> None:
    fp = pcbnew.FootprintLoad(str(HERE), "MountingHole_M3_NPTH_REV1")
    if fp is None:
        raise RuntimeError("cannot load candidate M3 footprint")
    fp.SetReference(ref)
    fp.SetValue("M3 NPTH")
    fp.SetFPID(pcbnew.LIB_ID("PlanCarrier", "MountingHole_M3_NPTH_REV1"))
    fp.SetPosition(pt(x, y))
    fp.SetExcludedFromBOM(True)
    fp.SetExcludedFromPosFiles(True)
    board.Add(fp)
    add_rule_area(
        board, f"{ref}_M3_COPPER_KEEPOUT", circle(x, y, 4.0),
        pcbnew.LSET.AllCuMask(), tracks=True, vias=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if source == ACTIVE or output == ACTIVE or source == output:
        raise RuntimeError("planner refuses active PCB or in-place mutation")
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    if actual != RELEASED_SHA256:
        raise RuntimeError(f"released-base SHA mismatch: {actual}")

    board = pcbnew.LoadBoard(str(source))
    if board.FindFootprintByReference("J5") is None:
        raise RuntimeError("J5 missing")
    add_rule_area(
        board, "J5_HANDSOLDER_CLEARANCE",
        rectangle(60.800, 17.800, 65.200, 29.800),
        one_layer(pcbnew.B_Cu), tracks=False, vias=False,
    )
    add_ground_track(board, (63.000, 20.000), (60.000, 20.000))

    # H2=138,7 is rejected because it overlaps the documented ESP32 module
    # body. H2=101,7 is rejected because the 8-mm keepout intersects the
    # released OLED and WS2812 routes. H2=80,7 is the clean top-edge corridor.
    for ref, x, y in (("H1", 7.000, 7.000),
                      ("H2", 80.000, 7.000),
                      ("H3", 96.000, 83.000)):
        add_hole(board, ref, x, y)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    output.parent.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(output), board)


if __name__ == "__main__":
    main()
