#!/usr/bin/env python3
"""Controlled post-C3 5V_SYS distribution transaction for a selected PCB.

Each named stage adds only the manually reviewed copper in its routing
contract.  This script deliberately does not change footprints, netlists,
zones, or retained buck-cell copper.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew


MM = pcbnew.FromMM


def pt(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(MM(x), MM(y))


def net(board: pcbnew.BOARD, name: str) -> pcbnew.NETINFO_ITEM:
    item = board.FindNet(name)
    if item is None:
        raise RuntimeError(f"Missing approved net {name}")
    return item


def segment(board: pcbnew.BOARD, net_name: str, start: tuple[float, float],
            end: tuple[float, float], width: float,
            layer: int = pcbnew.F_Cu) -> None:
    track = pcbnew.PCB_TRACK(board)
    track.SetNet(net(board, net_name))
    track.SetStart(pt(*start))
    track.SetEnd(pt(*end))
    track.SetWidth(MM(width))
    track.SetLayer(layer)
    board.Add(track)


def via(board: pcbnew.BOARD, net_name: str, pos: tuple[float, float],
        diameter: float = 0.60, drill: float = 0.30) -> None:
    item = pcbnew.PCB_VIA(board)
    item.SetNet(net(board, net_name))
    item.SetPosition(pt(*pos))
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    item.SetWidth(MM(diameter))
    item.SetDrill(MM(drill))
    board.Add(item)


def stage_a(board: pcbnew.BOARD) -> None:
    # Main output trunk: the extension begins at retained post-C3 node via
    # (73.100,59.225); B.Cu is used only to exit below L1/C3, then F.Cu is
    # clear of the buck island.  No retained buck copper is modified.
    segment(board, "/5V_SYS", (73.100, 59.225), (80.000, 64.000), 1.00,
            pcbnew.B_Cu)
    via(board, "/5V_SYS", (80.000, 64.000))
    segment(board, "/5V_SYS", (80.000, 64.000), (80.000, 54.725), 1.00)
    # C7.1 is a real, local 5V_SYS endpoint at this first checkpoint; all
    # later branches tee from the connected trunk rather than leaving copper
    # dangling between transactions.
    segment(board, "/5V_SYS", (80.000, 54.725), (85.500, 54.725), 0.80)


def stage_b(board: pcbnew.BOARD) -> None:
    # Independent ESP32 VIN branch; x=96 corridor stays left of the protected
    # module/antenna outline until the final direct entry to J1.1.
    segment(board, "/5V_SYS", (80.000, 54.725), (80.000, 43.500), 1.00)
    segment(board, "/5V_SYS", (80.000, 43.500), (96.000, 43.500), 1.00)
    segment(board, "/5V_SYS", (96.000, 43.500), (96.000, 14.000), 1.00)
    segment(board, "/5V_SYS", (96.000, 14.000), (111.000, 14.000), 1.00)


def stage_c(board: pcbnew.BOARD) -> None:
    # Independent E220 branch and local bypass star.  C6 reaches J3.6
    # directly; C5 is not daisy-chained through either capacitor.
    segment(board, "/5V_SYS", (80.000, 43.500), (20.580, 43.500), 1.00)
    segment(board, "/5V_SYS", (20.580, 43.500), (20.580, 49.750), 0.80)
    segment(board, "/5V_SYS", (20.580, 49.750), (20.580, 53.500), 0.80)
    segment(board, "/5V_SYS", (23.275, 43.500), (23.275, 48.000), 0.80)
    # C5/C6 local returns: short F.Cu exits into B.Cu and then to J3.7.
    segment(board, "/GND", (22.030, 49.750), (22.030, 51.000), 0.50)
    via(board, "/GND", (22.030, 51.000))
    segment(board, "/GND", (22.030, 51.000), (23.120, 53.500), 0.50,
            pcbnew.B_Cu)
    segment(board, "/GND", (24.725, 48.000), (24.725, 51.000), 0.50)
    via(board, "/GND", (24.725, 51.000))
    segment(board, "/GND", (24.725, 51.000), (23.120, 53.500), 0.50,
            pcbnew.B_Cu)


def stage_d(board: pcbnew.BOARD) -> None:
    # U3/C7 low-current branch.  C7.1 is the local bypass branch point.
    segment(board, "/5V_SYS", (85.500, 54.725), (87.000, 54.725), 0.50)
    segment(board, "/5V_SYS", (87.000, 54.725), (87.000, 51.900), 0.50)
    segment(board, "/5V_SYS", (87.000, 51.900), (88.525, 51.900), 0.50)
    segment(board, "/5V_SYS", (88.525, 51.900), (88.525, 53.000), 0.50)
    # Purposeful local B.Cu GND returns for C7 and the two U3 ground pads.
    segment(board, "/GND", (85.500, 53.275), (85.500, 51.900), 0.50)
    via(board, "/GND", (85.500, 51.900))
    segment(board, "/GND", (88.050, 55.000), (87.200, 56.500), 0.50)
    via(board, "/GND", (87.200, 56.500))
    segment(board, "/GND", (89.950, 55.000), (91.000, 55.000), 0.50)
    via(board, "/GND", (91.000, 55.000))


def stage_e(board: pcbnew.BOARD) -> None:
    # Dedicated probe branch.  TP4 and TP5 each have their own stub and are
    # not used as series conductors for the downstream loads.
    segment(board, "/5V_SYS", (80.000, 64.000), (73.000, 82.000), 0.80,
            pcbnew.B_Cu)
    segment(board, "/5V_SYS", (68.000, 82.000), (68.000, 87.000), 0.80,
            pcbnew.B_Cu)
    segment(board, "/5V_SYS", (73.000, 82.000), (63.000, 82.000), 0.80,
            pcbnew.B_Cu)
    segment(board, "/5V_SYS", (63.000, 82.000), (63.000, 87.000), 0.80,
            pcbnew.B_Cu)


STAGES = {"A": stage_a, "B": stage_b, "C": stage_c, "D": stage_d,
          "E": stage_e}

# Exact copper signatures of the accepted five post-C3 checkpoints.  These
# guard against duplicate geometry if a completed stage is invoked again.
STAGE_SIGNATURES = {
    "A": {
        "tracks": (("/5V_SYS", (73.100, 59.225), (80.000, 64.000), 1.00, pcbnew.B_Cu),
                   ("/5V_SYS", (80.000, 64.000), (80.000, 54.725), 1.00, pcbnew.F_Cu),
                   ("/5V_SYS", (80.000, 54.725), (85.500, 54.725), 0.80, pcbnew.F_Cu)),
        "vias": (("/5V_SYS", (80.000, 64.000), 0.60, 0.30),),
    },
    "B": {
        "tracks": (("/5V_SYS", (80.000, 54.725), (80.000, 43.500), 1.00, pcbnew.F_Cu),
                   ("/5V_SYS", (80.000, 43.500), (96.000, 43.500), 1.00, pcbnew.F_Cu),
                   ("/5V_SYS", (96.000, 43.500), (96.000, 14.000), 1.00, pcbnew.F_Cu),
                   ("/5V_SYS", (96.000, 14.000), (111.000, 14.000), 1.00, pcbnew.F_Cu)),
        "vias": (),
    },
    "C": {
        "tracks": (("/5V_SYS", (80.000, 43.500), (20.580, 43.500), 1.00, pcbnew.F_Cu),
                   ("/5V_SYS", (20.580, 43.500), (20.580, 49.750), 0.80, pcbnew.F_Cu),
                   ("/5V_SYS", (20.580, 49.750), (20.580, 53.500), 0.80, pcbnew.F_Cu),
                   ("/5V_SYS", (23.275, 43.500), (23.275, 48.000), 0.80, pcbnew.F_Cu),
                   ("/GND", (22.030, 49.750), (22.030, 51.000), 0.50, pcbnew.F_Cu),
                   ("/GND", (22.030, 51.000), (23.120, 53.500), 0.50, pcbnew.B_Cu),
                   ("/GND", (24.725, 48.000), (24.725, 51.000), 0.50, pcbnew.F_Cu),
                   ("/GND", (24.725, 51.000), (23.120, 53.500), 0.50, pcbnew.B_Cu)),
        "vias": (("/GND", (22.030, 51.000), 0.60, 0.30),
                 ("/GND", (24.725, 51.000), 0.60, 0.30)),
    },
    "D": {
        "tracks": (("/5V_SYS", (85.500, 54.725), (87.000, 54.725), 0.50, pcbnew.F_Cu),
                   ("/5V_SYS", (87.000, 54.725), (87.000, 51.900), 0.50, pcbnew.F_Cu),
                   ("/5V_SYS", (87.000, 51.900), (88.525, 51.900), 0.50, pcbnew.F_Cu),
                   ("/5V_SYS", (88.525, 51.900), (88.525, 53.000), 0.50, pcbnew.F_Cu),
                   ("/GND", (85.500, 53.275), (85.500, 51.900), 0.50, pcbnew.F_Cu),
                   ("/GND", (88.050, 55.000), (87.200, 56.500), 0.50, pcbnew.F_Cu),
                   ("/GND", (89.950, 55.000), (91.000, 55.000), 0.50, pcbnew.F_Cu)),
        "vias": (("/GND", (85.500, 51.900), 0.60, 0.30),
                 ("/GND", (87.200, 56.500), 0.60, 0.30),
                 ("/GND", (91.000, 55.000), 0.60, 0.30)),
    },
    "E": {
        "tracks": (("/5V_SYS", (80.000, 64.000), (73.000, 82.000), 0.80, pcbnew.B_Cu),
                   ("/5V_SYS", (68.000, 82.000), (68.000, 87.000), 0.80, pcbnew.B_Cu),
                   ("/5V_SYS", (73.000, 82.000), (63.000, 82.000), 0.80, pcbnew.B_Cu),
                   ("/5V_SYS", (63.000, 82.000), (63.000, 87.000), 0.80, pcbnew.B_Cu)),
        "vias": (),
    },
}


def mm_tuple(point: pcbnew.VECTOR2I) -> tuple[float, float]:
    return (round(pcbnew.ToMM(point.x), 3), round(pcbnew.ToMM(point.y), 3))


def stage_application_state(board: pcbnew.BOARD, stage: str) -> str:
    """Return absent, partial, or complete for an exact checkpoint signature."""
    signature = STAGE_SIGNATURES[stage]
    tracks = {
        (item.GetNetname(), mm_tuple(item.GetStart()), mm_tuple(item.GetEnd()),
         round(pcbnew.ToMM(item.GetWidth()), 3), item.GetLayer())
        for item in board.GetTracks() if not isinstance(item, pcbnew.PCB_VIA)
    }
    vias = {
        (item.GetNetname(), mm_tuple(item.GetPosition()),
         round(pcbnew.ToMM(item.GetWidth(pcbnew.F_Cu)), 3),
         round(pcbnew.ToMM(item.GetDrillValue()), 3),
         item.TopLayer(), item.BottomLayer())
        for item in board.GetTracks() if isinstance(item, pcbnew.PCB_VIA)
    }
    expected_tracks = set(signature["tracks"])
    expected_vias = {
        (net_name, position, diameter, drill, pcbnew.F_Cu, pcbnew.B_Cu)
        for net_name, position, diameter, drill in signature["vias"]
    }
    found = len(expected_tracks & tracks) + len(expected_vias & vias)
    required = len(expected_tracks) + len(expected_vias)
    if found == required:
        return "complete"
    return "partial" if found else "absent"


def rollback_d(board: pcbnew.BOARD) -> None:
    """Remove exactly the failed D-transaction objects, leaving A-C intact."""
    tracks = {
        ("/5V_SYS", (85.500, 54.725), (87.000, 54.725)),
        ("/5V_SYS", (87.000, 54.725), (87.000, 51.900)),
        ("/5V_SYS", (87.000, 51.900), (88.525, 51.900)),
        ("/5V_SYS", (88.525, 51.900), (88.525, 53.000)),
        ("/GND", (85.500, 53.275), (85.500, 51.900)),
        ("/GND", (88.050, 55.000), (87.000, 55.000)),
        ("/GND", (89.950, 55.000), (91.000, 55.000)),
    }
    vias = {("/GND", (85.500, 51.900)), ("/GND", (87.000, 55.000)),
            ("/GND", (91.000, 55.000))}
    removed = 0
    for item in list(board.GetTracks()):
        if isinstance(item, pcbnew.PCB_VIA):
            if (item.GetNetname(), mm_tuple(item.GetPosition())) in vias:
                board.Remove(item)
                removed += 1
            continue
        key = (item.GetNetname(), mm_tuple(item.GetStart()), mm_tuple(item.GetEnd()))
        if key in tracks:
            board.Remove(item)
            removed += 1
    if removed != 10:
        raise RuntimeError(f"Failed D rollback: removed {removed}, expected 10")


def move_silk(board: pcbnew.BOARD) -> None:
    """Move only the two inherited F.Silkscreen reference fields."""
    positions = {"U1": (61.500, 61.500), "L1": (78.000, 51.000)}
    for reference, position in positions.items():
        footprint = board.FindFootprintByReference(reference)
        if footprint is None:
            raise RuntimeError(f"Missing reference {reference}")
        field = footprint.Reference()
        if field.GetLayer() != pcbnew.F_SilkS:
            raise RuntimeError(f"{reference} reference is not on F.Silkscreen")
        field.SetPosition(pt(*position))


def rollback_e_duplicate(board: pcbnew.BOARD) -> None:
    """Remove the one redundant same-net E-stage overlap after inspection."""
    target = ("/5V_SYS", (73.000, 82.000), (68.000, 82.000))
    for item in list(board.GetTracks()):
        if isinstance(item, pcbnew.PCB_VIA):
            continue
        key = (item.GetNetname(), mm_tuple(item.GetStart()), mm_tuple(item.GetEnd()))
        if key == target:
            board.Remove(item)
            return
    raise RuntimeError("Failed E cleanup: duplicate segment was not found")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--board", type=Path, required=True,
                        help="explicit target board; active PCB is never selected implicitly")
    parser.add_argument("stage", choices=[*STAGES, "rollback-d", "rollback-e-duplicate", "move-silk"])
    args = parser.parse_args()
    board = pcbnew.LoadBoard(str(args.board))
    if args.stage in STAGES:
        state = stage_application_state(board, args.stage)
        if state == "complete":
            raise RuntimeError(f"STAGE ALREADY APPLIED: {args.stage} on {args.board}")
        if state == "partial":
            raise RuntimeError(f"STAGE PARTIALLY APPLIED: {args.stage} on {args.board}; refusing duplicate copper")
    if args.stage == "rollback-d":
        rollback_d(board)
    elif args.stage == "rollback-e-duplicate":
        rollback_e_duplicate(board)
    elif args.stage == "move-silk":
        move_silk(board)
    else:
        STAGES[args.stage](board)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(args.board), board)


if __name__ == "__main__":
    main()
