#!/usr/bin/env python3
"""Replace only the obsolete U4 AUX_3V3 thermal copper on an evidence copy."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pcbnew


MM = pcbnew.ToMM
IU = pcbnew.FromMM
SOURCE_SHA256 = "b10bc94138397f3d3d393804dd02d285b2f19eaa5c3341b920835085dbf23464"
OLD_VIAS = {(25.3, 24.8), (25.3, 29.2), (26.5, 26.0), (26.5, 28.0)}
LOCAL_ZONE = ((22.0, 22.0), (30.0, 22.0), (30.0, 32.0), (22.0, 32.0))


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(IU(x), IU(y))


def xy(item: pcbnew.BOARD_ITEM) -> tuple[float, float]:
    pos = item.GetPosition()
    return round(MM(pos.x), 3), round(MM(pos.y), 3)


def build(source: Path, output: Path) -> None:
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise RuntimeError("retained source SHA-256 mismatch")
    board = pcbnew.LoadBoard(str(source.resolve()))

    aux_zones = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname() == "/AUX_3V3"]
    if sorted(z.GetLayer() for z in aux_zones) != sorted((pcbnew.F_Cu, pcbnew.B_Cu)):
        raise RuntimeError("expected exactly the obsolete F.Cu and B.Cu AUX_3V3 zones")
    for zone in aux_zones:
        board.Remove(zone)

    removed_vias = []
    for item in list(board.GetTracks()):
        if isinstance(item, pcbnew.PCB_VIA) and item.GetNetname() == "/AUX_3V3" and xy(item) in OLD_VIAS:
            removed_vias.append(xy(item))
            board.Remove(item)
    if set(removed_vias) != OLD_VIAS:
        raise RuntimeError(f"unexpected obsolete-via set: {removed_vias}")

    aux_net = next(net for net in board.GetNetsByNetcode().values() if net.GetNetname() == "/AUX_3V3")
    local = pcbnew.ZONE(board)
    local.SetNet(aux_net)
    local.SetLayer(pcbnew.F_Cu)
    local.SetAssignedPriority(2)
    local.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    local.SetLocalClearance(IU(0.20))
    local.SetMinThickness(IU(0.25))
    outline = local.Outline()
    outline.NewOutline()
    for x, y in LOCAL_ZONE:
        outline.Append(point(x, y))
    board.Add(local)

    pad_bridge = pcbnew.PCB_TRACK(board)
    pad_bridge.SetStart(point(17.5, 27.0))
    pad_bridge.SetEnd(point(23.8, 27.0))
    pad_bridge.SetWidth(IU(0.8))
    pad_bridge.SetLayer(pcbnew.F_Cu)
    pad_bridge.SetNet(aux_net)
    board.Add(pad_bridge)

    bridge = pcbnew.PCB_TRACK(board)
    bridge.SetStart(point(30.0, 22.54))
    bridge.SetEnd(point(37.5, 22.54))
    bridge.SetWidth(IU(0.8))
    bridge.SetLayer(pcbnew.F_Cu)
    bridge.SetNet(aux_net)
    board.Add(bridge)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    output.parent.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(output.resolve()), board)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.source, args.output)


if __name__ == "__main__":
    main()
