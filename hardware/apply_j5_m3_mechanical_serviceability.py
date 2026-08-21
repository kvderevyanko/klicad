#!/usr/bin/env python3
"""Reproduce the released Rev.1 J5 hand-solder and M3 mechanical update.

This transform is intentionally locked to the approved 9f15... source PCB and
writes a separate candidate.  The active PCB is never used as an output.
"""

from __future__ import annotations

import argparse
import hashlib
import math
from pathlib import Path

import pcbnew


RELEASED_SHA256 = "9f15f061cd98cf069137ce9181a9edf8d9903167ee9641b9fa9af746eb992acd"
HERE = Path(__file__).resolve().parent
ACTIVE = HERE / "esp32-e220.kicad_pcb"
LIBRARY = HERE / "esp32-e220.pretty"
MM = pcbnew.FromMM


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(MM(x), MM(y))


def mm_xy(vector: pcbnew.VECTOR2I) -> tuple[float, float]:
    return round(pcbnew.ToMM(vector.x), 3), round(pcbnew.ToMM(vector.y), 3)


def one_layer(layer: int) -> pcbnew.LSET:
    layers = pcbnew.LSET()
    layers.AddLayer(layer)
    return layers


def rectangle(xmin: float, ymin: float, xmax: float, ymax: float):
    return ((xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax))


def circle(cx: float, cy: float, radius: float, vertices: int = 32):
    return tuple(
        (cx + radius * math.cos(2 * math.pi * index / vertices),
         cy + radius * math.sin(2 * math.pi * index / vertices))
        for index in range(vertices)
    )


def add_rule_area(
    board: pcbnew.BOARD,
    name: str,
    outline: tuple[tuple[float, float], ...],
    layers: pcbnew.LSET,
    *,
    block_tracks: bool,
    block_vias: bool,
) -> None:
    area = pcbnew.ZONE(board)
    area.SetLayerSet(layers)
    area.SetZoneName(name)
    area.SetIsRuleArea(True)
    area.SetDoNotAllowTracks(block_tracks)
    area.SetDoNotAllowVias(block_vias)
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


def add_ground_track(board: pcbnew.BOARD) -> None:
    track = pcbnew.PCB_TRACK(board)
    track.SetNet(board.FindNet("/GND"))
    track.SetStart(point(63.000, 20.000))
    track.SetEnd(point(60.000, 20.000))
    track.SetWidth(MM(0.800))
    track.SetLayer(pcbnew.B_Cu)
    board.Add(track)


def add_hole(board: pcbnew.BOARD, reference: str, x: float, y: float) -> None:
    footprint = pcbnew.FootprintLoad(str(LIBRARY), "MountingHole_M3_NPTH_REV1")
    if footprint is None:
        raise RuntimeError("cannot load project-local M3 footprint")
    footprint.SetReference(reference)
    footprint.SetValue("M3 NPTH")
    footprint.SetFPID(pcbnew.LIB_ID("Carrier", "MountingHole_M3_NPTH_REV1"))
    footprint.SetPosition(point(x, y))
    footprint.SetExcludedFromBOM(True)
    footprint.SetExcludedFromPosFiles(True)
    board.Add(footprint)
    add_rule_area(
        board,
        f"{reference}_M3_COPPER_KEEPOUT",
        circle(x, y, 4.000),
        pcbnew.LSET.AllCuMask(),
        block_tracks=True,
        block_vias=True,
    )


def verify_source(board: pcbnew.BOARD) -> None:
    footprints = list(board.GetFootprints())
    tracks = list(board.GetTracks())
    if len(footprints) != 37 or len(tracks) != 259:
        # GetTracks includes the released 201 segments and 58 vias.
        raise RuntimeError(f"unexpected source counts: footprints={len(footprints)} tracks+vias={len(tracks)}")
    if any(board.FindFootprintByReference(ref) is not None for ref in ("H1", "H2", "H3")):
        raise RuntimeError("source already contains mounting holes")
    j5 = board.FindFootprintByReference("J5")
    if j5 is None or mm_xy(j5.GetPosition()) != (63.0, 20.0):
        raise RuntimeError("J5 source geometry mismatch")
    expected = {"1": ("/GND", (63.0, 20.0)), "2": ("/AUX_3V3", (63.0, 22.54)),
                "3": ("/OLED_SCL", (63.0, 25.08)), "4": ("/OLED_SDA", (63.0, 27.62))}
    actual = {pad.GetNumber(): (pad.GetNetname(), mm_xy(pad.GetPosition())) for pad in j5.Pads()}
    if actual != expected:
        raise RuntimeError(f"J5 pad/net mismatch: {actual}")
    names = {zone.GetZoneName() for zone in board.Zones() if zone.GetIsRuleArea()}
    required = {"ESP32_ANTENNA_EXCLUSION", "J6_HANDSOLDER_CLEARANCE", "J9_HANDSOLDER_CLEARANCE"}
    if names != required:
        raise RuntimeError(f"source rule-area mismatch: {sorted(names)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    if source == output or output == ACTIVE.resolve():
        raise RuntimeError("source/output must differ and output must not be the active PCB")
    actual_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    if actual_sha != RELEASED_SHA256:
        raise RuntimeError(f"released-source SHA mismatch: {actual_sha}")

    board = pcbnew.LoadBoard(str(source))
    verify_source(board)
    add_rule_area(
        board,
        "J5_HANDSOLDER_CLEARANCE",
        rectangle(60.800, 17.800, 65.200, 29.800),
        one_layer(pcbnew.B_Cu),
        block_tracks=False,
        block_vias=False,
    )
    add_ground_track(board)
    for reference, x, y in (("H1", 7.000, 7.000), ("H2", 80.000, 7.000), ("H3", 96.000, 83.000)):
        add_hole(board, reference, x, y)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    output.parent.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(output), board)


if __name__ == "__main__":
    main()
