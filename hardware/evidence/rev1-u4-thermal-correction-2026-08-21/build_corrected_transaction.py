#!/usr/bin/env python3
"""Reproduce the reviewed Rev.1 transaction with corrected U4 thermal copper.

This wrapper deliberately reuses the already-proven fixed-module routing builder
and changes only its U4 AUX_3V3 thermal subsection.  Outputs remain forbidden at
the active-board and retained-baseline paths by the imported builder.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[3]
HW = ROOT / "hardware"
BASE = HW / "esp32-e220-pre-rev1-expansion.kicad_pcb"
BUILDER = HW / "evidence/rev1-final-physical-2026-08-21/build_candidate.py"
BASE_SHA256 = "d87c0ff900c9ce113c4c36b5a2785a65848077673e34804a8e9166cec2a6b76c"
LOCAL_ZONE = [(22.0, 22.0), (30.0, 22.0), (30.0, 32.0), (22.0, 32.0)]
OLD_AUX_VIAS = {(25.3, 24.8), (25.3, 29.2), (26.5, 26.0), (26.5, 28.0)}


def load_builder():
    spec = importlib.util.spec_from_file_location("rev1_fixed_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BUILDER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def xy_mm(item) -> tuple[float, float]:
    pos = item.GetPosition()
    return round(pcbnew.ToMM(pos.x), 3), round(pcbnew.ToMM(pos.y), 3)


def assert_corrected_u4(board_path: Path) -> None:
    board = pcbnew.LoadBoard(str(board_path.resolve()))
    aux_vias = {
        xy_mm(item)
        for item in board.GetTracks()
        if isinstance(item, pcbnew.PCB_VIA) and item.GetNetname() == "/AUX_3V3"
    }
    if aux_vias:
        raise RuntimeError(f"AUX_3V3 vias remain: {sorted(aux_vias)}")

    aux_zones = [
        zone for zone in board.Zones()
        if not zone.GetIsRuleArea() and zone.GetNetname() == "/AUX_3V3"
    ]
    if len(aux_zones) != 1 or aux_zones[0].GetLayer() != pcbnew.F_Cu:
        raise RuntimeError("expected exactly one F.Cu AUX_3V3 zone")
    points = []
    outline = aux_zones[0].Outline().Outline(0)
    for index in range(outline.PointCount()):
        point = outline.CPoint(index)
        points.append((round(pcbnew.ToMM(point.x), 3), round(pcbnew.ToMM(point.y), 3)))
    if points != LOCAL_ZONE:
        raise RuntimeError(f"unexpected AUX_3V3 zone outline: {points}")

    u4 = board.FindFootprintByReference("U4")
    pad2_nets = [pad.GetNetname() for pad in u4.Pads() if pad.GetNumber() == "2"]
    if pad2_nets != ["/AUX_3V3", "/AUX_3V3"]:
        raise RuntimeError(f"U4 duplicate pad-2 mapping mismatch: {pad2_nets}")


def build(source: Path, output: Path, stop_after: str, checkpoint_dir: Path | None) -> None:
    if hashlib.sha256(source.read_bytes()).hexdigest() != BASE_SHA256:
        raise RuntimeError("approved pre-expansion baseline SHA-256 mismatch")

    module = load_builder()
    original_zone = module.zone
    original_via = module.via
    original_path = module.path

    def corrected_zone(board, name, layer, points, priority):
        if name == "AUX_3V3":
            if layer == pcbnew.F_Cu:
                return original_zone(board, name, layer, LOCAL_ZONE, priority)
            if layer == pcbnew.B_Cu:
                return None
        return original_zone(board, name, layer, points, priority)

    def corrected_via(board, name, x, y, diameter=0.60, drill=0.30):
        if name == "AUX_3V3" and (round(x, 3), round(y, 3)) in OLD_AUX_VIAS:
            return None
        return original_via(board, name, x, y, diameter, drill)

    def corrected_path(board, name, points, width=0.25, layer=pcbnew.F_Cu):
        result = original_path(board, name, points, width, layer)
        if name == "AUX_3V3" and points == [(15.4, 27), (17.5, 27)]:
            original_path(board, name, [(17.5, 27), (23.8, 27)], 0.8, pcbnew.F_Cu)
        elif name == "AUX_3V3" and points == [(37.5, 22.54), (63.0, 22.54)]:
            original_path(board, name, [(30.0, 22.54), (37.5, 22.54)], 0.8, pcbnew.F_Cu)
        return result

    module.zone = corrected_zone
    module.via = corrected_via
    module.path = corrected_path
    module.build(source, output, stop_after, checkpoint_dir)
    if stop_after in {"u4-aux", "rgb", "e220", "buttons", "bat-sense", "final"}:
        assert_corrected_u4(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=BASE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stop-after", choices=(
        "sync-antenna", "j8-jp1", "u4-aux", "rgb", "e220", "buttons", "bat-sense", "final"
    ), default="final")
    parser.add_argument("--checkpoint-dir", type=Path)
    args = parser.parse_args()
    build(args.source, args.output, args.stop_after, args.checkpoint_dir)


if __name__ == "__main__":
    main()
