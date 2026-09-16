#!/usr/bin/env python3
"""Regression contract for the Littelfuse 1812L200/16 F1 correction."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True

import generate_stage7_footprints as stage7  # noqa: E402
from check_board_contract import at, first, forms, fvalue, prop_map, sexp, value  # noqa: E402


DEFAULT_BOARD = HERE / "esp32-e220.kicad_pcb"
DEFAULT_LOCAL = HERE / "esp32-e220.pretty" / "Littelfuse_1812L200_16_4532Metric.kicad_mod"
DEFAULT_REFERENCE = (
    HERE
    / "evidence"
    / "full-production-audit-2026-09-15"
    / "f1-implementation"
    / "10-esp32-e220.pre-f1.kicad_pcb"
)

EXPECTED_SEGMENTS = {
    "01cb0d3e-c640-4898-bd6d-c3c98dd2c2f1": ("/BAT_PLUS", (41.635, 78.5), (48.0, 87.0)),
    "5bd83154-5890-4fb2-9b14-a90d9902d6de": ("/BAT_PLUS", (41.635, 78.5), (41.635, 76.0)),
    "d6f11b0f-dde0-46c7-a409-4dbaaff09603": ("/BAT_PLUS", (35.0, 78.5), (41.635, 78.5)),
    "9acd9b87-3c41-4f24-8cf8-e01baf241d9b": ("/BAT_FUSED", (46.865, 72.5), (44.05, 72.5)),
    "e2f6e3bc-4117-4dd9-a338-e4bc7c5826a1": ("/BAT_FUSED", (46.865, 76.0), (51.0, 76.0)),
    "f617d508-72c6-4f5a-96ac-fdaf00b28a39": ("/BAT_FUSED", (46.865, 76.0), (46.865, 72.5)),
}


def close(actual: float, expected: float, tolerance: float = 0.0005) -> bool:
    return abs(actual - expected) <= tolerance


def point(node: list[Any] | None) -> tuple[float, float]:
    return fvalue(node, 1), fvalue(node, 2)


def line_bbox(footprint: list[Any], layer: str) -> tuple[float, float, float, float] | None:
    points = []
    for item in forms(footprint, "fp_line"):
        if value(first(item, "layer"), 1) == layer:
            points.extend((point(first(item, "start")), point(first(item, "end"))))
    if not points:
        return None
    xs = [item[0] for item in points]
    ys = [item[1] for item in points]
    return min(xs), min(ys), max(xs), max(ys)


def pads_by_number(footprint: list[Any]) -> dict[str, list[Any]]:
    return {value(item, 1): item for item in forms(footprint, "pad")}


def check_footprint_geometry(footprint: list[Any], embedded: bool, failures: list[str]) -> None:
    expected = {
        "1": ((-2.615, 0.0), (1.780, 3.150), "/BAT_PLUS"),
        "2": ((2.615, 0.0), (1.780, 3.150), "/BAT_FUSED"),
    }
    pads = pads_by_number(footprint)
    if sorted(pads) != ["1", "2"]:
        failures.append(f"{'embedded' if embedded else 'local'} pad numbers: {sorted(pads)}")
        return
    for number, (expected_at, expected_size, expected_net) in expected.items():
        pad = pads[number]
        pad_at = at(pad)[:2]
        size = point(first(pad, "size"))
        if not all(close(actual, target) for actual, target in zip(pad_at, expected_at)):
            failures.append(f"pad {number} local centre {pad_at}, expected {expected_at}")
        if not all(close(actual, target) for actual, target in zip(size, expected_size)):
            failures.append(f"pad {number} size {size}, expected {expected_size}")
        if value(pad, 2) != "smd" or value(pad, 3) != "roundrect":
            failures.append(f"pad {number} type/shape is not smd roundrect")
        if embedded:
            net = first(pad, "net")
            actual_net = value(net, 1) if net is not None and len(net) == 2 else value(net, 2)
            if actual_net != expected_net:
                failures.append(f"pad {number} net {actual_net!r}, expected {expected_net!r}")
    if line_bbox(footprint, "F.Fab") != (-2.275, -1.62, 2.275, 1.62):
        failures.append(f"F.Fab bbox {line_bbox(footprint, 'F.Fab')}")
    if line_bbox(footprint, "F.CrtYd") != (-3.55, -2.12, 3.55, 2.12):
        failures.append(f"F.CrtYd bbox {line_bbox(footprint, 'F.CrtYd')}")


def by_reference(root: list[Any]) -> dict[str, list[Any]]:
    return {prop_map(item).get("Reference", ""): item for item in forms(root, "footprint")}


def by_uuid(root: list[Any], head: str) -> dict[str, list[Any]]:
    return {value(first(item, "uuid"), 1): item for item in forms(root, head)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    parser.add_argument("--local-footprint", type=Path, default=DEFAULT_LOCAL)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    args = parser.parse_args()

    failures: list[str] = []
    generated = stage7.fuse_1812()
    local_text = args.local_footprint.read_text(encoding="utf-8")
    if local_text != generated:
        failures.append("project-local footprint differs from fuse_1812() output")

    local = sexp(local_text)
    if value(local, 1) != "Littelfuse_1812L200_16_4532Metric":
        failures.append(f"local footprint identity {value(local, 1)!r}")
    check_footprint_geometry(local, False, failures)

    board = sexp(args.board.read_text(encoding="utf-8"))
    reference = sexp(args.reference.read_text(encoding="utf-8"))
    board_fps = by_reference(board)
    reference_fps = by_reference(reference)
    f1 = board_fps.get("F1")
    if f1 is None:
        failures.append("embedded F1 missing")
    else:
        if at(f1) != (44.25, 76.0, 0.0):
            failures.append(f"embedded F1 origin/rotation {at(f1)}")
        check_footprint_geometry(f1, True, failures)

    changed_footprints = sorted(
        ref for ref in set(board_fps) | set(reference_fps)
        if board_fps.get(ref) != reference_fps.get(ref)
    )
    if changed_footprints != ["F1"]:
        failures.append(f"footprint allowlist delta {changed_footprints}, expected ['F1']")

    board_segments = by_uuid(board, "segment")
    reference_segments = by_uuid(reference, "segment")
    changed_segments = sorted(
        uuid for uuid in set(board_segments) | set(reference_segments)
        if board_segments.get(uuid) != reference_segments.get(uuid)
    )
    if changed_segments != sorted(EXPECTED_SEGMENTS):
        failures.append(f"segment allowlist delta {changed_segments}")
    for uuid, (expected_net, expected_start, expected_end) in EXPECTED_SEGMENTS.items():
        segment = board_segments.get(uuid)
        if segment is None:
            failures.append(f"segment {uuid} missing")
            continue
        net = first(segment, "net")
        actual_net = value(net, 1) if net is not None and len(net) == 2 else value(net, 2)
        if (
            point(first(segment, "start")) != expected_start
            or point(first(segment, "end")) != expected_end
            or not close(fvalue(first(segment, "width"), 1), 1.0)
            or value(first(segment, "layer"), 1) != "F.Cu"
            or actual_net != expected_net
        ):
            failures.append(
                f"segment {uuid} is not {expected_net} {expected_start}->{expected_end}, 1.00 mm F.Cu"
            )

    for head in ("via", "zone"):
        if forms(board, head) != forms(reference, head):
            failures.append(f"unexpected {head} delta")
    if len(forms(board, "segment")) != 202 or len(forms(board, "via")) != 58:
        failures.append("board segment/via inventory changed")
    if len(forms(board, "zone")) != 11:
        failures.append("board zone/rule-area inventory changed")

    payload = {
        "status": "FAIL" if failures else "PASS",
        "board": str(args.board),
        "reference": str(args.reference),
        "source_local_exact": local_text == generated,
        "expected_origin_mm": [44.25, 76.0, 0.0],
        "expected_pad_centres_local_mm": {"1": [-2.615, 0.0], "2": [2.615, 0.0]},
        "expected_pad_size_mm": [1.78, 3.15],
        "expected_pad_nets": {"1": "/BAT_PLUS", "2": "/BAT_FUSED"},
        "changed_footprints": changed_footprints,
        "changed_segments": changed_segments,
        "failures": failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
