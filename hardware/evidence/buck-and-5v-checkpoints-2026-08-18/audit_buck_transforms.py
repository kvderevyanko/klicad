#!/usr/bin/env python3
"""Read-only native-footprint transform audit for the buck candidate."""

from __future__ import annotations

import json
from pathlib import Path

import pcbnew


ROOT = Path("hardware")
LIBRARY = ROOT / "esp32-e220.pretty"
ACTIVE = ROOT / "esp32-e220.kicad_pcb"
CANDIDATE = ROOT / "esp32-e220-assistant-buck-candidate.kicad_pcb"
STAGE8 = Path("/tmp/stage8-native-transform.kicad_pcb")
OUTPUT = Path("/tmp/buck-transform-audit.json")
PLACEMENT = {
    "U1": (70.0, 56.0, 180.0),
    "C1": (67.7, 59.225, 0.0),
    "C2": (66.0, 56.0, 180.0),
    "C3": (70.9, 59.225, 180.0),
    "C4": (67.0, 53.5, 270.0),
    "L1": (74.85, 56.525, 90.0),
}


def mm(value: int) -> float:
    return round(pcbnew.ToMM(value), 6)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def norm_angle(value: float) -> float:
    return round(value % 360.0, 6)


def pad_data(pad: pcbnew.PAD) -> dict:
    local = pad.GetFPRelativePosition()
    centre = pad.GetPosition()
    size = pad.GetSize()
    box = pad.GetBoundingBox()
    return {
        "number": str(pad.GetNumber()),
        "net": str(pad.GetNetname()),
        "local_xy_mm": [mm(local.x), mm(local.y)],
        "orientation_deg": norm_angle(pad.GetOrientationDegrees()),
        "global_xy_mm": [mm(centre.x), mm(centre.y)],
        "size_mm": [mm(size.x), mm(size.y)],
        "copper_bbox_mm": {
            "x_min": mm(box.GetX()),
            "y_min": mm(box.GetY()),
            "x_max": mm(box.GetRight()),
            "y_max": mm(box.GetBottom()),
        },
    }


def footprint_data(fp: pcbnew.FOOTPRINT) -> dict:
    pos = fp.GetPosition()
    return {
        "xy_mm": [mm(pos.x), mm(pos.y)],
        "orientation_deg": norm_angle(fp.GetOrientationDegrees()),
        "value": str(fp.GetValue()),
        "pads": [pad_data(p) for p in fp.Pads()],
    }


def exactly_equal(a: dict, b: dict) -> bool:
    return a == b


def edge_gap_l1(l1: dict) -> float:
    pads = {pad["number"]: pad for pad in l1["pads"]}
    # At 90 degrees the land lengths are along global X; clearance is along Y.
    p1, p2 = pads["1"]["copper_bbox_mm"], pads["2"]["copper_bbox_mm"]
    return round(p1["y_min"] - p2["y_max"], 6)


def copper_counts(board: pcbnew.BOARD) -> dict:
    tracks = list(board.GetTracks())
    return {
        "tracks": sum(not isinstance(item, pcbnew.PCB_VIA) for item in tracks),
        "vias": sum(isinstance(item, pcbnew.PCB_VIA) for item in tracks),
        "zones": len(list(board.Zones())),
    }


def main() -> None:
    active = pcbnew.LoadBoard(str(ACTIVE))
    candidate = pcbnew.LoadBoard(str(CANDIDATE))
    stage8 = pcbnew.LoadBoard(str(STAGE8))
    if not all((active, candidate, stage8)):
        raise RuntimeError("unable to load one or more audit boards")

    output: dict = {
        "candidate_copper_counts": copper_counts(candidate),
        "buck_refs": {},
        "non_buck_footprint_transform_changes": [],
        "footprint_value_or_pad_net_mismatches": [],
    }

    for ref in PLACEMENT:
        actual = candidate.FindFootprintByReference(ref)
        independent = stage8.FindFootprintByReference(ref)
        if actual is None or independent is None:
            raise RuntimeError(f"{ref}: missing from candidate or Stage-8 board")
        library_name = str(actual.GetFPID().GetLibItemName())
        expected = pcbnew.FootprintLoad(str(LIBRARY), library_name)
        if expected is None:
            raise RuntimeError(f"{ref}: cannot load library footprint {library_name}")
        reference_board = pcbnew.BOARD()
        reference_board.Add(expected)
        x, y, angle = PLACEMENT[ref]
        expected.SetPosition(point(x, y))
        expected.SetOrientationDegrees(angle)
        actual_data = footprint_data(actual)
        expected_data = footprint_data(expected)
        stage8_data = footprint_data(independent)
        # FootprintLoad has no board net attachments; compare physical data only.
        expected_physical = {k: actual_data[k] for k in ("xy_mm", "orientation_deg")}
        expected_physical["pads"] = sorted([
            {key: value for key, value in pad.items() if key != "net"}
            for pad in expected_data["pads"]
        ], key=lambda pad: pad["number"])
        actual_physical = {k: actual_data[k] for k in ("xy_mm", "orientation_deg")}
        actual_physical["pads"] = sorted([
            {key: value for key, value in pad.items() if key != "net"}
            for pad in actual_data["pads"]
        ], key=lambda pad: pad["number"])
        stage8_physical = {k: stage8_data[k] for k in ("xy_mm", "orientation_deg")}
        stage8_physical["pads"] = sorted([
            {key: value for key, value in pad.items() if key != "net"}
            for pad in stage8_data["pads"]
        ], key=lambda pad: pad["number"])
        output["buck_refs"][ref] = {
            "library_footprint": library_name,
            "candidate": actual_data,
            "matches_library_after_transform": exactly_equal(actual_physical, expected_physical),
            "matches_independent_stage8": exactly_equal(actual_physical, stage8_physical),
            "direct_library_physical_differences": [
                {"candidate": actual_pad, "library": expected_pad}
                for actual_pad, expected_pad in zip(
                    actual_physical["pads"], expected_physical["pads"]
                )
                if actual_pad != expected_pad
            ],
        }

    output["l1_pad1_pad2_copper_edge_gap_mm"] = edge_gap_l1(
        output["buck_refs"]["L1"]["candidate"]
    )

    active_refs = {fp.GetReference(): fp for fp in active.GetFootprints()}
    candidate_refs = {fp.GetReference(): fp for fp in candidate.GetFootprints()}
    if set(active_refs) != set(candidate_refs):
        output["footprint_reference_set_mismatch"] = {
            "active_only": sorted(set(active_refs) - set(candidate_refs)),
            "candidate_only": sorted(set(candidate_refs) - set(active_refs)),
        }
    for ref in sorted(set(active_refs) & set(candidate_refs)):
        before, after = footprint_data(active_refs[ref]), footprint_data(candidate_refs[ref])
        if ref not in PLACEMENT and (
            before["xy_mm"] != after["xy_mm"]
            or before["orientation_deg"] != after["orientation_deg"]
        ):
            output["non_buck_footprint_transform_changes"].append(ref)
        if before["value"] != after["value"] or [
            (p["number"], p["net"]) for p in before["pads"]
        ] != [
            (p["number"], p["net"]) for p in after["pads"]
        ]:
            output["footprint_value_or_pad_net_mismatches"].append(ref)

    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate_copper_counts": output["candidate_copper_counts"],
        "all_buck_refs_match_library": all(
            item["matches_library_after_transform"]
            for item in output["buck_refs"].values()
        ),
        "all_buck_refs_match_stage8": all(
            item["matches_independent_stage8"]
            for item in output["buck_refs"].values()
        ),
        "l1_pad1_pad2_copper_edge_gap_mm": output[
            "l1_pad1_pad2_copper_edge_gap_mm"
        ],
        "non_buck_footprint_transform_changes": output[
            "non_buck_footprint_transform_changes"
        ],
        "footprint_value_or_pad_net_mismatches": output[
            "footprint_value_or_pad_net_mismatches"
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
