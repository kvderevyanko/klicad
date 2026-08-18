#!/usr/bin/env python3
"""Fingerprint and compare the electrical/physical PCB state without editing it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def tokenize(text: str) -> list[str]:
    result: list[str] = []
    token: list[str] = []
    quoted = escape = False
    for char in text:
        if quoted:
            if escape:
                token.append(char)
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                result.append("".join(token))
                token = []
                quoted = False
            else:
                token.append(char)
        elif char == '"':
            if token:
                result.append("".join(token))
                token = []
            quoted = True
        elif char in "()":
            if token:
                result.append("".join(token))
                token = []
            result.append(char)
        elif char.isspace():
            if token:
                result.append("".join(token))
                token = []
        else:
            token.append(char)
    if token:
        result.append("".join(token))
    return result


def sexp(text: str) -> list:
    root: list = []
    stack: list[list] = []
    for token in tokenize(text):
        if token == "(":
            node: list = []
            (stack[-1] if stack else root).append(node)
            stack.append(node)
        elif token == ")":
            stack.pop()
        else:
            (stack[-1] if stack else root).append(token)
    if stack:
        raise ValueError("unbalanced S-expression")
    return root[0]


def forms(node: list, head: str) -> list[list]:
    return [item for item in node[1:] if isinstance(item, list) and item and item[0] == head]


def first(node: list, head: str, default: list | None = None) -> list | None:
    found = forms(node, head)
    return found[0] if found else default


def prop_map(node: list) -> dict[str, str]:
    return {item[1]: item[2] for item in forms(node, "property") if len(item) > 2}


def list_values(node: list | None, start: int = 1) -> list[str]:
    return node[start:] if node else []


def pad_fingerprint(pad: list) -> dict:
    return {
        "at": list_values(first(pad, "at")),
        "drill": list_values(first(pad, "drill")),
        "layers": list_values(first(pad, "layers")),
        "net": (first(pad, "net") or [None, ""])[1],
        "number": pad[1],
        "shape": pad[3],
        "size": list_values(first(pad, "size")),
        "type": pad[2],
        "uuid": (first(pad, "uuid") or [None, ""])[1],
    }


def footprint_fingerprint(footprint: list) -> dict:
    properties = prop_map(footprint)
    return {
        "at": list_values(first(footprint, "at")),
        "footprint": footprint[1],
        "layer": (first(footprint, "layer") or [None, ""])[1],
        "pads": [pad_fingerprint(pad) for pad in forms(footprint, "pad")],
        "reference": properties.get("Reference", ""),
        "uuid": (first(footprint, "uuid") or [None, ""])[1],
        "value": properties.get("Value", ""),
    }


def track_fingerprint(item: list, kind: str) -> dict:
    return {
        "at": list_values(first(item, "at")),
        "drill": list_values(first(item, "drill")),
        "end": list_values(first(item, "end")),
        "kind": kind,
        "layer": (first(item, "layer") or [None, ""])[1],
        "layers": list_values(first(item, "layers")),
        "net": (first(item, "net") or [None, ""])[1],
        "size": list_values(first(item, "size")),
        "start": list_values(first(item, "start")),
        "uuid": (first(item, "uuid") or [None, ""])[1],
        "width": list_values(first(item, "width")),
    }


def snapshot(board_path: Path) -> dict:
    board = sexp(board_path.read_text())
    footprints = [footprint_fingerprint(item) for item in forms(board, "footprint")]
    segments = [track_fingerprint(item, "segment") for item in forms(board, "segment")]
    vias = [track_fingerprint(item, "via") for item in forms(board, "via")]
    zones = [{
        "definition": item,
        "layer": (first(item, "layer") or [None, ""])[1],
        "layers": list_values(first(item, "layers")),
        "net": (first(item, "net") or [None, ""])[1],
        "uuid": (first(item, "uuid") or [None, ""])[1],
    } for item in forms(board, "zone")]
    edge_cuts = [item for item in forms(board, "gr_line")
                 if (first(item, "layer") or [None, ""])[1] == "Edge.Cuts"]
    core = {
        "board_outline_edge_cuts": edge_cuts,
        "counts": {
            "edge_cuts_graphics": len(edge_cuts),
            "footprints": len(footprints),
            "segments": len(segments),
            "vias": len(vias),
            "zones": len(zones),
        },
        "footprints": footprints,
        "segments": segments,
        "vias": vias,
        "zones": zones,
    }
    digest = hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        **core,
        "generator": "KiCad S-expression parser",
        "schema": "project-state-fingerprint.v1",
        "sha256": digest,
        "source": str(board_path),
    }


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sorted_items(items: list[dict]) -> list[dict]:
    return sorted(items, key=canonical)


def comparison(before: dict, after: dict) -> dict:
    fields = ("counts", "footprints", "segments", "vias", "zones", "board_outline_edge_cuts")
    equal = {}
    for field in fields:
        before_value = before[field] if field == "counts" else sorted_items(before[field])
        after_value = after[field] if field == "counts" else sorted_items(after[field])
        equal[field] = canonical(before_value) == canonical(after_value)
    status = "PASS" if all(equal.values()) else "FAIL"
    return {
        "after_fingerprint_sha256": after["sha256"],
        "before_fingerprint_sha256": before.get("sha256", ""),
        "comparison_scope": "footprint XY/rotation and pads; segment/via UUID and geometry; zones with boundaries/fills; Edge.Cuts",
        "electrical_connectivity_changes": 0 if status == "PASS" else None,
        "copper_geometry_changes": 0 if status == "PASS" else None,
        "field_equality": equal,
        "placement_changes": 0 if status == "PASS" else None,
        "status": status,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcb", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--comparison-output", type=Path)
    args = parser.parse_args()
    after = snapshot(args.pcb)
    args.output.write_text(json.dumps(after, indent=2, sort_keys=True) + "\n")
    if args.baseline or args.comparison_output:
        if not (args.baseline and args.comparison_output):
            parser.error("--baseline and --comparison-output must be used together")
        before = json.loads(args.baseline.read_text())
        result = comparison(before, after)
        args.comparison_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(result["status"])


if __name__ == "__main__":
    main()
