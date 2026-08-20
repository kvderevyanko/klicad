#!/usr/bin/env python3
"""Controlled, additive E220 signal routing stages for a named board copy.

The script never selects an active board implicitly.  All coordinates are mm.
The approved temporary-copy feasibility plan is 0.25-mm F.Cu only; it adds no
signal vias and keeps the five long testpoint drops over the bounded B.Cu GND
reference region.
"""
import argparse
from pathlib import Path

import pcbnew

MM = pcbnew.FromMM


def point(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def track(board, net_name, start, end, layer=pcbnew.F_Cu, width=0.25):
    item = pcbnew.PCB_TRACK(board)
    item.SetNet(board.FindNet(net_name))
    item.SetStart(point(*start))
    item.SetEnd(point(*end))
    item.SetLayer(layer)
    item.SetWidth(MM(width))
    board.Add(item)


def route(board, net_name, points, layer=pcbnew.F_Cu, width=0.25):
    for start, end in zip(points, points[1:]):
        track(board, net_name, start, end, layer, width)


def via(board, net_name, position):
    item = pcbnew.PCB_VIA(board)
    item.SetNet(board.FindNet(net_name))
    item.SetPosition(point(*position))
    item.SetWidth(MM(0.60))
    item.SetDrill(MM(0.30))
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    board.Add(item)


def stage_a(board):
    # M0 primary trunk and its TP6/R8 branches.
    route(board, "/E220_M0", [(7.880, 53.500), (7.880, 45.000),
                               (19.500, 45.000)])
    via(board, "/E220_M0", (19.500, 45.000))
    route(board, "/E220_M0", [(19.500, 45.000), (24.500, 45.000)], pcbnew.B_Cu)
    via(board, "/E220_M0", (24.500, 45.000))
    route(board, "/E220_M0", [(24.500, 45.000), (27.000, 45.000),
                               (27.000, 48.000), (79.000, 48.000)])
    via(board, "/E220_M0", (79.000, 48.000))
    route(board, "/E220_M0", [(79.000, 48.000), (81.000, 48.000)], pcbnew.B_Cu)
    via(board, "/E220_M0", (81.000, 48.000))
    route(board, "/E220_M0", [(81.000, 48.000), (104.000, 48.000),
                               (104.000, 31.780),
                               (111.000, 31.780)])
    route(board, "/E220_M0", [(100.000, 48.000), (100.000, 83.000),
                               (73.000, 83.000), (73.000, 87.000)])
    route(board, "/E220_M0", [(30.000, 58.725), (30.000, 60.200),
                               (35.000, 60.200), (35.000, 48.000)])
    # R8.2 has a short, direct return to the E220 GND pin.
    route(board, "/GND", [(23.120, 53.500), (25.500, 55.900),
                          (30.000, 55.900), (30.000, 57.275)])


def stage_b(board):
    # M1 primary trunk and its TP7/R9 branches.
    route(board, "/E220_M1", [(10.420, 53.500), (10.420, 46.500),
                               (16.500, 46.500)])
    via(board, "/E220_M1", (16.500, 46.500))
    route(board, "/E220_M1", [(16.500, 46.500), (28.500, 46.500)], pcbnew.B_Cu)
    via(board, "/E220_M1", (28.500, 46.500))
    route(board, "/E220_M1", [(28.500, 46.500), (77.000, 46.500)])
    via(board, "/E220_M1", (77.000, 46.500))
    route(board, "/E220_M1", [(77.000, 46.500), (83.000, 46.500)], pcbnew.B_Cu)
    via(board, "/E220_M1", (83.000, 46.500))
    route(board, "/E220_M1", [(83.000, 46.500), (103.000, 46.500)])
    via(board, "/E220_M1", (103.000, 46.500))
    route(board, "/E220_M1", [(103.000, 46.500), (105.000, 46.500)], pcbnew.B_Cu)
    via(board, "/E220_M1", (105.000, 46.500))
    route(board, "/E220_M1", [(105.000, 46.500), (106.000, 46.500),
                               (106.000, 32.500)])
    via(board, "/E220_M1", (106.000, 32.500))
    route(board, "/E220_M1", [(106.000, 32.500), (106.000, 31.000)], pcbnew.B_Cu)
    via(board, "/E220_M1", (106.000, 31.000))
    route(board, "/E220_M1", [(106.000, 31.000), (106.000, 29.240),
                               (111.000, 29.240)])
    route(board, "/E220_M1", [(102.000, 46.500)])
    via(board, "/E220_M1", (102.000, 46.500))
    route(board, "/E220_M1", [(102.000, 46.500), (102.000, 49.000)], pcbnew.B_Cu)
    via(board, "/E220_M1", (102.000, 49.000))
    route(board, "/E220_M1", [(102.000, 49.000), (102.000, 83.500),
                               (78.000, 83.500), (78.000, 87.000)])
    route(board, "/E220_M1", [(37.000, 46.500)])
    via(board, "/E220_M1", (37.000, 46.500))
    route(board, "/E220_M1", [(37.000, 46.500), (37.000, 49.000)], pcbnew.B_Cu)
    via(board, "/E220_M1", (37.000, 49.000))
    route(board, "/E220_M1", [(37.000, 49.000), (37.000, 61.000)])
    via(board, "/E220_M1", (37.000, 61.000))
    route(board, "/E220_M1", [(37.000, 61.000), (34.000, 61.000),
                               (34.000, 58.725)], pcbnew.B_Cu)
    via(board, "/E220_M1", (34.000, 58.725))
    route(board, "/E220_M1", [(34.000, 58.725), (33.000, 58.725)])
    route(board, "/GND", [(33.000, 57.275), (33.000, 55.900),
                          (30.000, 55.900)])


def stage_c(board):
    route(board, "/E220_AUX", [(18.040, 53.500), (18.040, 51.500),
                                (27.000, 51.500), (27.000, 46.000),
                                (77.000, 46.000)])
    via(board, "/E220_AUX", (77.000, 46.000))
    route(board, "/E220_AUX", [(77.000, 46.000), (83.000, 46.000)], pcbnew.B_Cu)
    via(board, "/E220_AUX", (83.000, 46.000))
    route(board, "/E220_AUX", [(83.000, 46.000), (105.000, 46.000),
                                (105.000, 26.700),
                                (111.000, 26.700)])
    route(board, "/E220_AUX", [(101.000, 46.000), (101.000, 84.000),
                                (83.000, 84.000), (83.000, 87.000)])


def stage_d(board):
    route(board, "/E220_RXD", [(12.960, 53.500), (12.960, 46.500),
                                (17.500, 46.500)])
    via(board, "/E220_RXD", (17.500, 46.500))
    route(board, "/E220_RXD", [(17.500, 46.500), (26.500, 46.500)], pcbnew.B_Cu)
    via(board, "/E220_RXD", (26.500, 46.500))
    route(board, "/E220_RXD", [(26.500, 46.500), (76.000, 46.500)])
    via(board, "/E220_RXD", (76.000, 46.500))
    route(board, "/E220_RXD", [(76.000, 46.500), (84.000, 46.500)], pcbnew.B_Cu)
    via(board, "/E220_RXD", (84.000, 46.500))
    route(board, "/E220_RXD", [(84.000, 46.500), (107.000, 46.500),
                                (107.000, 15.300)])
    via(board, "/E220_RXD", (107.000, 15.300))
    route(board, "/E220_RXD", [(107.000, 15.300), (107.000, 12.700)], pcbnew.B_Cu)
    via(board, "/E220_RXD", (107.000, 12.700))
    route(board, "/E220_RXD", [(107.000, 12.700),
                                (132.000, 12.700), (132.000, 29.240),
                                (136.400, 29.240)])
    route(board, "/E220_RXD", [(101.500, 46.500), (101.500, 84.500),
                                (88.000, 84.500), (88.000, 87.000)])


def stage_e(board):
    route(board, "/E220_TXD", [(15.500, 53.500), (15.500, 52.000),
                                (28.000, 52.000), (28.000, 47.000),
                                (75.000, 47.000)])
    via(board, "/E220_TXD", (75.000, 47.000))
    route(board, "/E220_TXD", [(75.000, 47.000), (85.000, 47.000)], pcbnew.B_Cu)
    via(board, "/E220_TXD", (85.000, 47.000))
    route(board, "/E220_TXD", [(85.000, 47.000), (108.000, 47.000),
                                (108.000, 16.100)])
    via(board, "/E220_TXD", (108.000, 16.100))
    route(board, "/E220_TXD", [(108.000, 16.100), (108.000, 12.300)], pcbnew.B_Cu)
    via(board, "/E220_TXD", (108.000, 12.300))
    route(board, "/E220_TXD", [(108.000, 12.300),
                                (132.500, 12.300), (132.500, 26.700),
                                (136.400, 26.700)])
    route(board, "/E220_TXD", [(102.000, 47.000), (102.000, 85.000),
                                (93.000, 85.000), (93.000, 87.000)])


STAGES = {"A": stage_a, "B": stage_b, "C": stage_c, "D": stage_d, "E": stage_e}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--board", type=Path, required=True)
    parser.add_argument("stage", choices=STAGES)
    args = parser.parse_args()
    if args.board.name == "esp32-e220.kicad_pcb":
        raise SystemExit("refusing implicit active-board selection")
    board = pcbnew.LoadBoard(str(args.board))
    STAGES[args.stage](board)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(args.board), board)


if __name__ == "__main__":
    main()
