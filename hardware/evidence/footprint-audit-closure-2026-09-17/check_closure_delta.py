#!/usr/bin/env python3
"""Verify the bounded footprint-audit documentation/metadata transaction."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any


EVIDENCE = Path(__file__).resolve().parent
HARDWARE = EVIDENCE.parents[1]
sys.path.insert(0, str(HARDWARE))
sys.dont_write_bytecode = True

import generate_stage7_footprints as stage7  # noqa: E402
from check_board_contract import at, first, forms, prop_map, sexp, value  # noqa: E402
from check_resistor_0603_footprint import (  # noqa: E402
    EXPECTED_NETS,
    geometry_failures as resistor_geometry_failures,
)


TARGET_REFS = ("R1", "R2", "R3", "R4", "R8", "R9")
GENERIC_REFS = ("R1", "R2", "R8", "R9")
DESCRIPTION = (
    "0603 (1608 metric) resistor footprint used by R1/R2/R3/R4/R8/R9. "
    "Yageo RC Mounting V10 Table 1 reflow lands: A=2.60, B=0.80, "
    "C=0.90, D=0.80 mm on 1.70-mm centres."
)
OLD_GENERATOR_DESCRIPTION = (
    "0603 (1608 metric) resistor footprint used by R1/R2/R3/R4/R8/R9/R10/R11. "
    "Yageo RC Mounting V10 Table 1 reflow lands: A=2.60, B=0.80, "
    "C=0.90, D=0.80 mm on 1.70-mm centres."
)
SUBSTITUTIONS = "allowed only when physical_substitution_restriction is satisfied"
RESTRICTION = (
    "Standard two-terminal chip resistor, 0603 imperial / 1608 metric, "
    "conventional wraparound terminals; manufacturer package or mounting "
    "recommendation compatible with 0.900 x 0.800 mm lands on 1.700-mm pitch, "
    "0.800-mm inner gap, and 2.600-mm span. Excludes 0402, 0805, special-terminal, "
    "reverse-geometry, and non-standard 0603 variants."
)


def by_reference(root: list[Any]) -> dict[str, list[Any]]:
    return {prop_map(item).get("Reference", ""): item for item in forms(root, "footprint")}


def replace_form(node: list[Any], head: str, replacement: list[Any]) -> None:
    for index, item in enumerate(node):
        if isinstance(item, list) and item and item[0] == head:
            node[index] = copy.deepcopy(replacement)
            return
    raise ValueError(f"missing {head} form")


def main() -> int:
    backup = EVIDENCE / "named-backup"
    failures: list[str] = []

    board_path = HARDWARE / "esp32-e220.kicad_pcb"
    board_before_path = backup / "esp32-e220.pre-closure.kicad_pcb"
    board = sexp(board_path.read_text(encoding="utf-8"))
    board_before = sexp(board_before_path.read_text(encoding="utf-8"))
    current_fps = by_reference(board)
    before_fps = by_reference(board_before)
    changed_footprints = sorted(
        ref for ref in set(current_fps) | set(before_fps)
        if current_fps.get(ref) != before_fps.get(ref)
    )
    if changed_footprints != sorted(TARGET_REFS):
        failures.append(f"changed footprints {changed_footprints}, expected {sorted(TARGET_REFS)}")

    pad_geometry_equal: dict[str, bool] = {}
    identity_equal: dict[str, bool] = {}
    placement_equal: dict[str, bool] = {}
    net_equal: dict[str, bool] = {}
    descriptions_exact: dict[str, bool] = {}
    description_only: dict[str, bool] = {}
    resistor_geometry_errors: list[str] = []
    for ref in TARGET_REFS:
        current = current_fps.get(ref)
        before = before_fps.get(ref)
        if current is None or before is None:
            failures.append(f"{ref}: missing current or baseline footprint")
            continue
        identity_equal[ref] = value(current, 1) == value(before, 1)
        placement_equal[ref] = at(current) == at(before)
        pad_geometry_equal[ref] = forms(current, "pad") == forms(before, "pad")
        net_equal[ref] = [first(pad, "net") for pad in forms(current, "pad")] == [
            first(pad, "net") for pad in forms(before, "pad")
        ]
        descriptions_exact[ref] = value(first(current, "descr"), 1) == DESCRIPTION
        resistor_geometry_errors.extend(resistor_geometry_failures(current, ref, EXPECTED_NETS[ref]))
        normalized = copy.deepcopy(current)
        replace_form(normalized, "descr", first(before, "descr") or [])
        description_only[ref] = normalized == before
        for label, result in (
            ("identity", identity_equal[ref]),
            ("placement", placement_equal[ref]),
            ("pad geometry", pad_geometry_equal[ref]),
            ("pad nets", net_equal[ref]),
            ("approved description", descriptions_exact[ref]),
            ("description-only delta", description_only[ref]),
        ):
            if not result:
                failures.append(f"{ref}: {label} check failed")

    structural_delta = {}
    for head, label in (
        ("net", "nets"),
        ("segment", "tracks"),
        ("via", "vias"),
        ("zone", "zones_rule_areas"),
    ):
        unchanged = forms(board, head) == forms(board_before, head)
        structural_delta[label] = "zero" if unchanged else "nonzero"
        if not unchanged:
            failures.append(f"{label} changed")

    local_path = HARDWARE / "esp32-e220.pretty" / "Resistor_0603_1608Metric.kicad_mod"
    local_before_path = backup / "Resistor_0603_1608Metric.pre-closure.kicad_mod"
    local_text = local_path.read_text(encoding="utf-8")
    local = sexp(local_text)
    local_before = sexp(local_before_path.read_text(encoding="utf-8"))
    local_normalized = copy.deepcopy(local)
    replace_form(local_normalized, "descr", first(local_before, "descr") or [])
    source_local_exact = local_text == stage7.yageo_rc0603()
    if not source_local_exact:
        failures.append("generator -> project-local resistor footprint exact equality failed")
    resistor_geometry_errors.extend(resistor_geometry_failures(local, "local"))
    if value(first(local, "descr"), 1) != DESCRIPTION or local_normalized != local_before:
        failures.append("project-local resistor footprint delta is not the exact description-only change")

    generator_path = HARDWARE / "generate_stage7_footprints.py"
    generator_before_path = backup / "generate_stage7_footprints.pre-closure.py"
    generator_text = generator_path.read_text(encoding="utf-8")
    generator_before_text = generator_before_path.read_text(encoding="utf-8")
    generator_only_description = (
        generator_text.replace(DESCRIPTION, OLD_GENERATOR_DESCRIPTION, 1) == generator_before_text
        and generator_text.count(DESCRIPTION) == 1
    )
    if not generator_only_description:
        failures.append("generator delta is not exactly the approved resistor description replacement")

    metadata_path = HARDWARE / "production-metadata.json"
    metadata_before_path = backup / "production-metadata.pre-closure.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata_before = json.loads(metadata_before_path.read_text(encoding="utf-8"))
    populate = metadata["assembly_classes"]["PCBA_POPULATE"]
    populate_before = metadata_before["assembly_classes"]["PCBA_POPULATE"]
    metadata_refs_exact: dict[str, bool] = {}
    normalized_metadata = copy.deepcopy(metadata)
    for ref in GENERIC_REFS:
        current_item = populate[ref]
        before_item = populate_before[ref]
        preserved = all(
            current_item.get(key) == before_item.get(key)
            for key in ("procurement_policy", "package", "resistance", "tolerance", "minimum_rating")
        )
        exact = (
            preserved
            and current_item.get("substitutions") == SUBSTITUTIONS
            and current_item.get("physical_substitution_restriction") == RESTRICTION
            and set(current_item) == set(before_item) | {"physical_substitution_restriction"}
        )
        metadata_refs_exact[ref] = exact
        if not exact:
            failures.append(f"{ref}: procurement metadata is not the exact approved constraint")
        normalized_metadata["assembly_classes"]["PCBA_POPULATE"][ref] = copy.deepcopy(before_item)
    metadata_only_target_refs = normalized_metadata == metadata_before
    if not metadata_only_target_refs:
        failures.append("production metadata has changes outside approved R1/R2/R8/R9 fields")

    schematic_unchanged = (
        (HARDWARE / "esp32-e220.kicad_sch").read_bytes()
        == (backup / "esp32-e220.pre-closure.kicad_sch").read_bytes()
    )
    if not schematic_unchanged:
        failures.append("schematic bytes changed")
    failures.extend(resistor_geometry_errors)

    payload = {
        "status": "FAIL" if failures else "PASS",
        "baseline": "ecfb03b79c6a41063ac21f1f7dc79750468a8b3a",
        "target_refs": list(TARGET_REFS),
        "changed_footprints": changed_footprints,
        "embedded_description_only": description_only,
        "descriptions_exact": descriptions_exact,
        "pad_geometry_delta": "zero" if all(pad_geometry_equal.values()) else "nonzero",
        "resistor_geometry_invariant": "PASS" if not resistor_geometry_errors else "FAIL",
        "resistor_geometry_mm": {
            "pad_centres_local": {"1": [-0.850, 0.0], "2": [0.850, 0.0]},
            "pad_size": [0.900, 0.800],
            "pitch": 1.700,
            "inner_gap": 0.800,
            "overall_span": 2.600,
            "roundrect_rratio": 0.20,
        },
        "track_delta": structural_delta.get("tracks"),
        "via_delta": structural_delta.get("vias"),
        "zone_rule_area_delta": structural_delta.get("zones_rule_areas"),
        "net_delta": structural_delta.get("nets"),
        "footprint_identity_delta": "zero" if all(identity_equal.values()) else "nonzero",
        "placement_delta": "zero" if all(placement_equal.values()) else "nonzero",
        "generator_local_exact": source_local_exact,
        "generator_only_description_delta": generator_only_description,
        "local_only_description_delta": local_normalized == local_before,
        "metadata_exact": metadata_refs_exact,
        "metadata_only_target_refs": metadata_only_target_refs,
        "l1_metadata_unchanged": populate["L1"] == populate_before["L1"],
        "schematic_byte_identical": schematic_unchanged,
        "failures": failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
