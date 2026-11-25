#!/usr/bin/env python3
"""Build a disposable PCB copy with the proposed Yageo 0603 land geometry."""

from __future__ import annotations

import sys

import pcbnew


TARGETS = {"R1", "R2", "R3", "R4", "R8", "R9"}
OLD_LOCAL_X_MM = {"1": -0.725, "2": 0.725}
NEW_LOCAL_X_MM = {"1": -0.850, "2": 0.850}


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_candidate.py INPUT.kicad_pcb OUTPUT.kicad_pcb")

    board = pcbnew.LoadBoard(sys.argv[1])
    found: set[str] = set()

    for footprint in board.GetFootprints():
        ref = footprint.GetReference()
        if ref not in TARGETS:
            continue
        found.add(ref)
        origin = footprint.GetPosition()
        pads = {pad.GetNumber(): pad for pad in footprint.Pads()}
        if set(pads) != {"1", "2"}:
            raise RuntimeError(f"{ref}: expected pads 1 and 2, got {sorted(pads)}")
        for number, new_local_x in NEW_LOCAL_X_MM.items():
            pad = pads[number]
            # Preserve KiCad's actual footprint transform by scaling the observed
            # centre vector instead of reimplementing its clockwise/Y-down rule.
            scale = new_local_x / OLD_LOCAL_X_MM[number]
            observed_dx = pad.GetPosition().x - origin.x
            observed_dy = pad.GetPosition().y - origin.y
            pad.SetPosition(
                pcbnew.VECTOR2I(
                    origin.x + round(observed_dx * scale),
                    origin.y + round(observed_dy * scale),
                )
            )
            pad.SetSize(pcbnew.VECTOR2I(mm(0.900), mm(0.800)))

    if found != TARGETS:
        raise RuntimeError(f"missing targets: {sorted(TARGETS - found)}")

    pcbnew.SaveBoard(sys.argv[2], board)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
