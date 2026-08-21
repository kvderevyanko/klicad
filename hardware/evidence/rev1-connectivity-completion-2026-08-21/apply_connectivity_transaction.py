#!/usr/bin/env python3
"""Apply one approved Rev.1 final-connectivity PCB routing transaction."""

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
    width_mm: float,
    points: list[tuple[float, float]],
) -> None:
    net = board.FindNet(net_name)
    if net is None:
        raise RuntimeError(f"net not found: {net_name}")
    for start, end in zip(points, points[1:]):
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(point(*start))
        track.SetEnd(point(*end))
        track.SetWidth(MM(width_mm))
        track.SetLayer(layer)
        track.SetNet(net)
        board.Add(track)


def add_via(board: pcbnew.BOARD, net_name: str, at: tuple[float, float]) -> None:
    net = board.FindNet(net_name)
    if net is None:
        raise RuntimeError(f"net not found: {net_name}")
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(*at))
    via.SetWidth(MM(0.60))
    via.SetDrill(MM(0.30))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(net)
    board.Add(via)


def apply_transaction(board: pcbnew.BOARD, transaction: str) -> None:
    if transaction == "A":
        # R2.1 BUCK_IN local gate-source-resistor branch.
        add_path(board, "/BUCK_IN", pcbnew.F_Cu, 0.25, [
            (62.500, 67.725),
            (65.500, 70.000),
        ])
    elif transaction == "B":
        # TP3 is a dead-end BUCK_IN diagnostic branch, never a series path.
        add_path(board, "/BUCK_IN", pcbnew.F_Cu, 1.00, [
            (64.350, 77.000),
            (58.000, 87.000),
        ])
    elif transaction == "C":
        # TP1 is a dead-end BAT_PLUS diagnostic branch from the accepted path.
        add_path(board, "/BAT_PLUS", pcbnew.F_Cu, 1.00, [
            (42.862, 78.500),
            (48.000, 87.000),
        ])
    elif transaction == "D":
        # C9.2 branch into the already-connected top-left GND component.
        add_path(board, "/GND", pcbnew.B_Cu, 0.50, [
            (14.000, 34.000),
            (12.000, 27.000),
        ])
        # Join the isolated U1 F.Cu GND-zone island to the C4 GND cluster.
        add_path(board, "/GND", pcbnew.F_Cu, 0.25, [
            (69.250, 54.600),
            (67.000, 54.225),
        ])
        # Bond the second ESP32 DevKit GND pin to the accepted J1/J6 branch.
        add_path(board, "/GND", pcbnew.B_Cu, 0.50, [
            (111.000, 16.540),
            (136.400, 16.540),
        ])
    elif transaction == "E":
        add_path(board, "/OLED_SDA", pcbnew.B_Cu, 0.25, [
            (63.000, 27.620), (78.000, 27.620),
            (81.000, 30.620), (81.000, 46.000),
        ])
        add_via(board, "/OLED_SDA", (81.000, 46.000))
        add_path(board, "/OLED_SDA", pcbnew.F_Cu, 0.25, [
            (81.000, 46.000), (97.500, 46.000),
        ])
        add_via(board, "/OLED_SDA", (97.500, 46.000))
        add_path(board, "/OLED_SDA", pcbnew.B_Cu, 0.25, [
            (97.500, 46.000), (104.000, 46.000),
        ])
        add_via(board, "/OLED_SDA", (104.000, 46.000))
        add_path(board, "/OLED_SDA", pcbnew.F_Cu, 0.25, [
            (104.000, 46.000), (108.000, 50.800),
            (112.500, 50.800), (114.000, 50.300),
            (122.000, 50.300),
        ])
        add_via(board, "/OLED_SDA", (122.000, 50.300))
        add_path(board, "/OLED_SDA", pcbnew.B_Cu, 0.25, [
            (122.000, 50.300), (124.000, 48.300),
            (124.000, 42.000), (130.000, 39.400),
            (136.400, 39.400),
        ])
    elif transaction == "F":
        add_path(board, "/OLED_SCL", pcbnew.B_Cu, 0.25, [
            (63.000, 25.080), (77.000, 25.080),
            (82.000, 30.080), (82.000, 47.000),
        ])
        add_via(board, "/OLED_SCL", (82.000, 47.000))
        add_path(board, "/OLED_SCL", pcbnew.F_Cu, 0.25, [
            (82.000, 47.000), (97.500, 47.000),
        ])
        add_via(board, "/OLED_SCL", (97.500, 47.000))
        add_path(board, "/OLED_SCL", pcbnew.B_Cu, 0.25, [
            (97.500, 47.000), (104.000, 47.000),
        ])
        add_via(board, "/OLED_SCL", (104.000, 47.000))
        add_path(board, "/OLED_SCL", pcbnew.F_Cu, 0.25, [
            (104.000, 47.000), (107.500, 51.350),
            (112.500, 51.350), (114.000, 51.300),
            (122.000, 51.300),
        ])
        add_via(board, "/OLED_SCL", (122.000, 51.300))
        add_path(board, "/OLED_SCL", pcbnew.B_Cu, 0.25, [
            (122.000, 51.300), (126.000, 51.300),
            (132.000, 46.800), (134.000, 47.020),
            (136.400, 47.020),
        ])
    else:
        raise ValueError(f"unknown transaction: {transaction}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("transaction", choices=list("ABCDEF"))
    parser.add_argument("--board", type=Path, required=True)
    args = parser.parse_args()

    board_path = args.board.resolve()
    board = pcbnew.LoadBoard(str(board_path))
    apply_transaction(board, args.transaction)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(board_path), board)


if __name__ == "__main__":
    main()
