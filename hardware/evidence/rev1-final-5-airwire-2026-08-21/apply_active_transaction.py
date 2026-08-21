#!/usr/bin/env python3
"""Apply one reviewed Rev.1 five-airwire transaction to the active PCB."""

from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew


MM = pcbnew.FromMM


def point(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(MM(x_mm), MM(y_mm))


def add_track(
    board: pcbnew.BOARD,
    net_name: str,
    layer: int,
    width_mm: float,
    points: list[tuple[float, float]],
) -> None:
    net = board.FindNet(net_name)
    if net is None:
        raise RuntimeError(f"missing net: {net_name}")
    for start, end in zip(points, points[1:]):
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(point(*start))
        track.SetEnd(point(*end))
        track.SetWidth(MM(width_mm))
        track.SetLayer(layer)
        track.SetNet(net)
        board.Add(track)


def add_via(
    board: pcbnew.BOARD,
    net_name: str,
    at: tuple[float, float],
    diameter_mm: float = 0.60,
    drill_mm: float = 0.30,
) -> None:
    net = board.FindNet(net_name)
    if net is None:
        raise RuntimeError(f"missing net: {net_name}")
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(*at))
    via.SetWidth(MM(diameter_mm))
    via.SetDrill(MM(drill_mm))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(net)
    board.Add(via)


def apply_transaction(board: pcbnew.BOARD, transaction: str) -> None:
    if transaction == "1":
        add_via(board, "/GND", (68.700, 54.000))
        add_via(board, "/GND", (70.500, 53.000))
    elif transaction == "2":
        add_track(board, "/GND", pcbnew.B_Cu, 0.25, [
            (24.725, 51.000),
            (24.725, 47.900),
        ])
    elif transaction == "3":
        add_track(board, "/GND", pcbnew.B_Cu, 0.50, [
            (111.000, 16.540),
            (136.400, 16.540),
        ])
    elif transaction == "4":
        add_track(board, "/OLED_SDA", pcbnew.F_Cu, 0.25, [
            (63.000, 27.620),
            (96.000, 12.000),
            (112.500, 12.000),
            (114.250, 16.000),
            (114.250, 25.500),
            (133.000, 38.000),
            (136.400, 39.400),
        ])
    elif transaction == "5":
        add_track(board, "/OLED_SCL", pcbnew.F_Cu, 0.25, [
            (63.000, 25.080),
            (97.000, 10.900),
            (112.000, 10.900),
            (135.500, 30.500),
            (137.000, 30.500),
            (138.000, 31.500),
            (138.000, 45.000),
            (136.400, 47.020),
        ])
    else:
        raise ValueError(f"unknown transaction: {transaction}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("transaction", choices=list("12345"))
    parser.add_argument("--board", type=Path, required=True)
    args = parser.parse_args()

    board_path = args.board.resolve()
    board = pcbnew.LoadBoard(str(board_path))
    apply_transaction(board, args.transaction)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(board_path), board)


if __name__ == "__main__":
    main()
