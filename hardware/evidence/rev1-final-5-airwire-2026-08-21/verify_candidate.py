#!/usr/bin/env python3
"""Emit reproducible metrics and invariance evidence for the bounded candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess

import pcbnew


def mm(value: int) -> float:
    return round(pcbnew.ToMM(value), 6)


def xy(point: pcbnew.VECTOR2I) -> list[float]:
    return [mm(point.x), mm(point.y)]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def item_signature(item: pcbnew.BOARD_CONNECTED_ITEM) -> dict:
    base = {"net": item.GetNetname(), "uuid": item.m_Uuid.AsString()}
    if isinstance(item, pcbnew.PCB_VIA):
        return base | {
            "type": "via",
            "at": xy(item.GetPosition()),
            "diameter_mm": mm(item.GetWidth(pcbnew.F_Cu)),
            "drill_mm": mm(item.GetDrillValue()),
            "top_layer": item.TopLayer(),
            "bottom_layer": item.BottomLayer(),
        }
    return base | {
        "type": "track",
        "start": xy(item.GetStart()),
        "end": xy(item.GetEnd()),
        "width_mm": mm(item.GetWidth()),
        "layer": item.GetLayer(),
    }


def footprint_signature(fp: pcbnew.FOOTPRINT) -> dict:
    pads = []
    for pad in fp.Pads():
        pads.append({
            "number": pad.GetNumber(),
            "net": pad.GetNetname(),
            "at": xy(pad.GetPosition()),
            "size": xy(pad.GetSize()),
        })
    return {
        "at": xy(fp.GetPosition()),
        "rotation_deg": fp.GetOrientationDegrees(),
        "layer": fp.GetLayer(),
        "pads": sorted(pads, key=lambda p: (p["number"], p["at"])),
    }


def outline_signature(zone: pcbnew.ZONE) -> dict:
    poly = zone.Outline()
    outlines = []
    for index in range(poly.OutlineCount()):
        line = poly.Outline(index)
        outlines.append([xy(line.CPoint(i)) for i in range(line.PointCount())])
    return {
        "net": zone.GetNetname(),
        "layers": list(zone.GetLayerSet().Seq()),
        "is_rule_area": zone.GetIsRuleArea(),
        "outlines": outlines,
    }


def route_length(items: list[dict]) -> float:
    total = 0.0
    for item in items:
        if item["type"] != "track":
            continue
        total += math.hypot(
            item["end"][0] - item["start"][0],
            item["end"][1] - item["start"][1],
        )
    return round(total, 6)


def layer_name(layer: int) -> str:
    return {pcbnew.F_Cu: "F.Cu", pcbnew.B_Cu: "B.Cu"}.get(layer, str(layer))


def build_metrics(baseline_path: Path, candidate_path: Path, drc_path: Path) -> dict:
    baseline = pcbnew.LoadBoard(str(baseline_path.resolve()))
    candidate = pcbnew.LoadBoard(str(candidate_path.resolve()))

    base_items = {i.m_Uuid.AsString(): item_signature(i) for i in baseline.GetTracks()}
    cand_items = {i.m_Uuid.AsString(): item_signature(i) for i in candidate.GetTracks()}
    missing = sorted(set(base_items) - set(cand_items))
    changed = sorted(k for k in base_items.keys() & cand_items if base_items[k] != cand_items[k])
    added = [cand_items[k] for k in sorted(set(cand_items) - set(base_items))]

    base_fp = {fp.GetReference(): footprint_signature(fp) for fp in baseline.GetFootprints()}
    cand_fp = {fp.GetReference(): footprint_signature(fp) for fp in candidate.GetFootprints()}
    changed_fp = sorted(ref for ref in base_fp.keys() | cand_fp if base_fp.get(ref) != cand_fp.get(ref))

    base_zones = {z.m_Uuid.AsString(): outline_signature(z) for z in baseline.Zones()}
    cand_zones = {z.m_Uuid.AsString(): outline_signature(z) for z in candidate.Zones()}
    changed_zones = sorted(
        key for key in base_zones.keys() | cand_zones if base_zones.get(key) != cand_zones.get(key)
    )

    groups: dict[str, list[dict]] = {}
    for item in added:
        groups.setdefault(item["net"], []).append(item)
    route_metrics = {}
    for net, items in sorted(groups.items()):
        tracks = [i for i in items if i["type"] == "track"]
        vias = [i for i in items if i["type"] == "via"]
        route_metrics[net] = {
            "track_segments": len(tracks),
            "length_mm": route_length(items),
            "widths_mm": sorted(set(i["width_mm"] for i in tracks)),
            "layers": sorted(set(layer_name(i["layer"]) for i in tracks)),
            "vias": len(vias),
            "via_geometry_mm": sorted(set((i["diameter_mm"], i["drill_mm"]) for i in vias)),
            "segments": [{k: i[k] for k in ("start", "end", "width_mm")}
                         | {"layer": layer_name(i["layer"])} for i in tracks],
            "via_coordinates": [i["at"] for i in vias],
        }

    # Explicit U1-ground proof: all six pad centers and both new via centers
    # must share one filled F.Cu island.  Both vias must also lie in the main
    # B.Cu GND polygon that contains known accepted global-ground components.
    test_points: dict[str, pcbnew.VECTOR2I] = {
        "VIA_GND_U1_A": pcbnew.VECTOR2I(pcbnew.FromMM(68.7), pcbnew.FromMM(54.0)),
        "VIA_GND_U1_B": pcbnew.VECTOR2I(pcbnew.FromMM(70.5), pcbnew.FromMM(53.0)),
    }
    for fp in candidate.GetFootprints():
        if fp.GetReference() == "U1":
            for pad in fp.Pads():
                if pad.GetNumber() in {"5", "6", "8", "15", "16", "EP"}:
                    test_points[f"U1.{pad.GetNumber()}"] = pad.GetPosition()

    f_membership: dict[str, list[int]] = {}
    b_membership: dict[str, list[int]] = {}
    global_b_pads: list[str] = []
    for zone in candidate.Zones():
        if zone.GetNetname() != "/GND":
            continue
        if zone.HasFilledPolysForLayer(pcbnew.F_Cu):
            polys = zone.GetFilledPolysList(pcbnew.F_Cu)
            for name, point in test_points.items():
                hits = [i for i in range(polys.OutlineCount()) if polys.Contains(point, i)]
                if hits:
                    f_membership[name] = hits
        if zone.HasFilledPolysForLayer(pcbnew.B_Cu) and zone.GetFilledPolysList(pcbnew.B_Cu).OutlineCount() == 1:
            polys = zone.GetFilledPolysList(pcbnew.B_Cu)
            for name, point in test_points.items():
                hits = [i for i in range(polys.OutlineCount()) if polys.Contains(point, i)]
                if hits:
                    b_membership[name] = hits
            for fp in candidate.GetFootprints():
                for pad in fp.Pads():
                    if pad.GetNetname() == "/GND" and polys.Contains(pad.GetPosition(), 0):
                        global_b_pads.append(f"{fp.GetReference()}.{pad.GetNumber()}")

    drc = json.loads(drc_path.read_text())
    return {
        "sha256": {
            "baseline": sha256(baseline_path),
            "candidate": sha256(candidate_path),
        },
        "counts": {
            "footprints": len(candidate.GetFootprints()),
            "tracks": sum(not isinstance(i, pcbnew.PCB_VIA) for i in candidate.GetTracks()),
            "vias": sum(isinstance(i, pcbnew.PCB_VIA) for i in candidate.GetTracks()),
            "copper_zones": sum(not z.GetIsRuleArea() for z in candidate.Zones()),
            "rule_areas": sum(z.GetIsRuleArea() for z in candidate.Zones()),
        },
        "invariance": {
            "baseline_copper_items": len(base_items),
            "missing_baseline_copper_uuids": missing,
            "changed_baseline_copper_uuids": changed,
            "added_tracks": sum(i["type"] == "track" for i in added),
            "added_vias": sum(i["type"] == "via" for i in added),
            "changed_footprints_or_pads": changed_fp,
            "changed_zone_or_rule_area_outlines": changed_zones,
        },
        "route_metrics": route_metrics,
        "u1_ground_proof": {
            "f_cu_filled_island_membership": f_membership,
            "b_cu_main_plane_membership": b_membership,
            "known_global_gnd_pads_in_same_b_cu_polygon": sorted(global_b_pads),
            "all_six_u1_pads_share_f_cu_island_with_both_vias":
                len(f_membership) == 8 and len({tuple(v) for v in f_membership.values()}) == 1,
            "both_vias_overlap_main_b_cu_gnd_polygon":
                set(b_membership) >= {"VIA_GND_U1_A", "VIA_GND_U1_B"},
        },
        "native_drc": {
            "violations": len(drc.get("violations", [])),
            "unconnected_items": len(drc.get("unconnected_items", [])),
            "categories": sorted({v.get("type", "unknown") for v in drc.get("violations", [])}),
        },
    }


def capture_contract(candidate: Path, baseline: Path, output: Path, temp_dir: Path) -> None:
    env = os.environ.copy()
    env["TMPDIR"] = str(temp_dir.resolve())
    command = [
        "python3", "hardware/check_board_contract.py",
        "--board", str(candidate), "--reference", str(baseline), "--json",
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True, env=env)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout)
    payload = json.loads(completed.stdout)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--drc", type=Path, required=True)
    parser.add_argument("--metrics-output", type=Path, required=True)
    parser.add_argument("--contract-output", type=Path, required=True)
    parser.add_argument("--temp-dir", type=Path, required=True)
    args = parser.parse_args()
    args.temp_dir.mkdir(parents=True, exist_ok=True)
    metrics = build_metrics(args.baseline, args.candidate, args.drc)
    args.metrics_output.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
    capture_contract(args.candidate, args.baseline, args.contract_output, args.temp_dir)


if __name__ == "__main__":
    main()
