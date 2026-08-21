#!/usr/bin/env python3
"""Build the bounded OLED-only routing proof on an evidence PCB copy."""

from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew


MM = pcbnew.FromMM


def point(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(MM(x_mm), MM(y_mm))


def add_path(
    board: pcbnew.BOARD,
    net_name: str,
    layer: int,
    points: list[tuple[float, float]],
) -> None:
    net = board.FindNet(net_name)
    if net is None:
        raise RuntimeError(f"net not found: {net_name}")

    for start, end in zip(points, points[1:]):
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(point(*start))
        track.SetEnd(point(*end))
        track.SetWidth(MM(0.25))
        track.SetLayer(layer)
        track.SetNet(net)
        board.Add(track)


def add_via(board: pcbnew.BOARD, net_name: str, at: tuple[float, float]) -> None:
    net = board.FindNet(net_name)
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(*at))
    via.SetWidth(MM(0.60))
    via.SetDrill(MM(0.30))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(net)
    board.Add(via)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    board = pcbnew.LoadBoard(str(args.input.resolve()))

    # Start on B.Cu from the J5 through-hole pads and descend left of the
    # existing B.Cu WS2812 crossing.  F.Cu then passes below the E220 bundle,
    # the 5V spine, and the lower end of J1 without entering the antenna rule
    # area.  A final B.Cu fanout avoids the existing GPIO23 approach to J2.
    add_path(board, "/OLED_SDA", pcbnew.B_Cu, [
        (63.000, 27.620),
        (78.000, 27.620),
        (81.000, 30.620),
        (81.000, 46.000),
    ])
    add_via(board, "/OLED_SDA", (81.000, 46.000))
    add_path(board, "/OLED_SDA", pcbnew.F_Cu, [
        (81.000, 46.000),
        (97.500, 46.000),
    ])
    add_via(board, "/OLED_SDA", (97.500, 46.000))
    add_path(board, "/OLED_SDA", pcbnew.B_Cu, [
        (97.500, 46.000),
        (104.000, 46.000),
    ])
    add_via(board, "/OLED_SDA", (104.000, 46.000))
    add_path(board, "/OLED_SDA", pcbnew.F_Cu, [
        (104.000, 46.000),
        (108.000, 50.800),
        (112.500, 50.800),
        (114.000, 50.300),
        (122.000, 50.300),
    ])
    add_via(board, "/OLED_SDA", (122.000, 50.300))
    add_path(board, "/OLED_SDA", pcbnew.B_Cu, [
        (122.000, 50.300),
        (124.000, 48.300),
        (124.000, 42.000),
        (130.000, 39.400),
        (136.400, 39.400),
    ])

    add_path(board, "/OLED_SCL", pcbnew.B_Cu, [
        (63.000, 25.080),
        (77.000, 25.080),
        (82.000, 30.080),
        (82.000, 47.000),
    ])
    add_via(board, "/OLED_SCL", (82.000, 47.000))
    add_path(board, "/OLED_SCL", pcbnew.F_Cu, [
        (82.000, 47.000),
        (97.500, 47.000),
    ])
    add_via(board, "/OLED_SCL", (97.500, 47.000))
    add_path(board, "/OLED_SCL", pcbnew.B_Cu, [
        (97.500, 47.000),
        (104.000, 47.000),
    ])
    add_via(board, "/OLED_SCL", (104.000, 47.000))
    add_path(board, "/OLED_SCL", pcbnew.F_Cu, [
        (104.000, 47.000),
        (107.500, 51.350),
        (112.500, 51.350),
        (114.000, 51.300),
        (122.000, 51.300),
    ])
    add_via(board, "/OLED_SCL", (122.000, 51.300))
    add_path(board, "/OLED_SCL", pcbnew.B_Cu, [
        (122.000, 51.300),
        (126.000, 51.300),
        (132.000, 46.800),
        (134.000, 47.020),
        (136.400, 47.020),
    ])

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(str(args.output.resolve()), board)


if __name__ == "__main__":
    main()
