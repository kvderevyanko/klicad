#!/usr/bin/env python3
"""Build an unrouted TPS62133 placement candidate through KiCad's API.

The helper reads the active board but never writes it.  It uses ``pcbnew`` to
move complete footprints so KiCad updates all child-pad and child-text
transformations.  It intentionally removes all copper items from the copied
candidate; the output remains a placement candidate until later routing and
review gates accept it.
"""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    import pcbnew
except ImportError as exc:  # pragma: no cover - exercised only without KiCad
    raise SystemExit(
        "FAIL: pcbnew Python API is required; refusing unsafe S-expression editing"
    ) from exc


ACTIVE_PCB = Path("hardware/esp32-e220.kicad_pcb")
DEFAULT_SOURCE = ACTIVE_PCB
DEFAULT_OUTPUT = Path("hardware/esp32-e220-assistant-buck-candidate.kicad_pcb")

# Candidate coordinates in millimetres / degrees.  These retain the current
# footprints, values, nets, and board architecture; only the named footprint
# transforms are intentionally changed.
PLACEMENT = {
    "U1": (70.0, 56.0, 180.0),
    "C1": (67.7, 59.225, 0.0),
    "C2": (66.0, 56.0, 180.0),
    "C3": (70.9, 59.225, 180.0),
    "C4": (67.0, 53.5, 270.0),
    "L1": (74.85, 56.525, 90.0),
}


def point_mm(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def format_mm(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def ensure_safe_output(source: Path, output: Path) -> None:
    active = ACTIVE_PCB.resolve()
    if output.resolve() == active:
        raise ValueError(f"refusing to overwrite active PCB: {active}")
    if output.resolve() == source.resolve():
        raise ValueError("refusing to overwrite source PCB")


def remove_copper(board: pcbnew.BOARD) -> dict[str, int]:
    """Remove all tracks/vias and zones through pcbnew board objects."""
    removed = {"track_or_via": 0, "zone": 0}
    for item in list(board.GetTracks()):
        board.Remove(item)
        removed["track_or_via"] += 1
    for zone in list(board.Zones()):
        board.Remove(zone)
        removed["zone"] += 1
    return removed


def assert_unrouted(board: pcbnew.BOARD) -> None:
    tracks_or_vias = len(list(board.GetTracks()))
    zones = len(list(board.Zones()))
    if tracks_or_vias or zones:
        raise RuntimeError(
            "candidate still contains copper: "
            f"track_or_via={tracks_or_vias} zone={zones}"
        )


def build_candidate(source: Path, output: Path) -> None:
    ensure_safe_output(source, output)
    board = pcbnew.LoadBoard(str(source))
    if board is None:
        raise RuntimeError(f"failed to load source PCB: {source}")

    found: set[str] = set()
    for ref, (x, y, rotation) in PLACEMENT.items():
        footprint = board.FindFootprintByReference(ref)
        if footprint is None:
            continue
        footprint.SetPosition(point_mm(x, y))
        footprint.SetOrientationDegrees(rotation)
        found.add(ref)

    missing = sorted(set(PLACEMENT) - found)
    if missing:
        raise RuntimeError(f"candidate refs missing from PCB: {', '.join(missing)}")

    removed = remove_copper(board)
    assert_unrouted(board)

    output.parent.mkdir(parents=True, exist_ok=True)
    board.Save(str(output))

    # Reload the saved board to verify KiCad's serialized result, rather than
    # trusting only the in-memory object state.
    saved = pcbnew.LoadBoard(str(output))
    if saved is None:
        raise RuntimeError(f"failed to reload candidate PCB: {output}")
    assert_unrouted(saved)

    print(f"source: {source}")
    print(f"output: {output}")
    print(f"removed from source: {removed}")
    print("candidate copper: track=0 via=0 zone=0")
    for ref in sorted(PLACEMENT):
        x, y, rotation = PLACEMENT[ref]
        print(f"{ref}: ({format_mm(x)}, {format_mm(y)}, {format_mm(rotation)} deg)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build_candidate(args.source, args.output)


if __name__ == "__main__":
    main()
