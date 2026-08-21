#!/usr/bin/env python3
"""Prove authoritative J6/J9 regeneration matches active physical geometry."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from hardware.verify_project_state_reconciliation import canonical, forms, sexp


SCOPE = Path(__file__).resolve().parent
ACTIVE = sexp((Path("hardware/esp32-e220.kicad_pcb")).read_text())
REGENERATED = sexp((SCOPE / "60-authoritative-regeneration.kicad_pcb").read_text())


def without_uuids(value):
    if not isinstance(value, list):
        return value
    return [without_uuids(child) for child in value
            if not (isinstance(child, list) and child and child[0] == "uuid")]


def geometry_set(root: list, tag: str) -> set[str]:
    return {canonical(without_uuids(item)) for item in forms(root, tag)}


tags = ("footprint", "segment", "via", "zone", "gr_line", "gr_arc",
        "gr_rect", "gr_poly")
equality = {tag: geometry_set(ACTIVE, tag) == geometry_set(REGENERATED, tag)
            for tag in tags}
status = all(equality.values())
result = {
    "status": "PASS" if status else "FAIL",
    "comparison": "all physical geometry and filled zones; UUID identity ignored",
    "field_equality": equality,
}
rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
(SCOPE / "64-authoritative-reproduction-proof.json").write_text(rendered)
print(rendered, end="")
raise SystemExit(0 if status else 1)
