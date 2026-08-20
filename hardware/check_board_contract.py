#!/usr/bin/env python3
"""Read-only deterministic contract checks for the ESP32 + E220 PCB.

Full mode invokes the established schematic/PCB parity checker and KiCad DRC.
Fast mode limits itself to parsed board invariants suitable for transactions.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
DEFAULT_BOARD = HERE / "esp32-e220.kicad_pcb"
DEFAULT_CONFIG = HERE / "board_contract.json"
SYNC_CHECKER = HERE / "check_schematic_pcb_sync.py"
PASS, FAIL, NA, INC = "PASS", "FAIL", "NOT_APPLICABLE", "INCONCLUSIVE"


def tokenize(text: str) -> list[str]:
    tokens, token, quoted, escaped = [], [], False, False
    for char in text:
        if quoted:
            if escaped:
                token.append(char); escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                tokens.append("".join(token)); token = []; quoted = False
            else:
                token.append(char)
        elif char == '"':
            if token: tokens.append("".join(token)); token = []
            quoted = True
        elif char in "()":
            if token: tokens.append("".join(token)); token = []
            tokens.append(char)
        elif char.isspace():
            if token: tokens.append("".join(token)); token = []
        else:
            token.append(char)
    if quoted:
        raise ValueError("unterminated quoted string")
    if token: tokens.append("".join(token))
    return tokens


def sexp(text: str) -> list[Any]:
    root: list[Any] = []; stack: list[list[Any]] = []
    for item in tokenize(text):
        if item == "(":
            node: list[Any] = []
            (stack[-1] if stack else root).append(node); stack.append(node)
        elif item == ")":
            if not stack: raise ValueError("unbalanced closing parenthesis")
            stack.pop()
        else:
            (stack[-1] if stack else root).append(item)
    if stack or len(root) != 1:
        raise ValueError("unbalanced S-expression")
    return root[0]


def forms(node: list[Any], head: str) -> list[list[Any]]:
    return [x for x in node[1:] if isinstance(x, list) and x and x[0] == head]


def first(node: list[Any], head: str) -> list[Any] | None:
    items = forms(node, head)
    return items[0] if items else None


def value(node: list[Any] | None, index: int, default: str = "") -> str:
    return str(node[index]) if node is not None and len(node) > index else default


def fvalue(node: list[Any] | None, index: int, default: float = 0.0) -> float:
    try: return float(value(node, index))
    except ValueError: return default


def net_name(node: list[Any] | None) -> str:
    """Accept KiCad 10 `(net "/GND")` and older `(net 1 "/GND")` forms."""
    if node is None: return ""
    return value(node, 1) if len(node) == 2 else value(node, 2)


def prop_map(node: list[Any]) -> dict[str, str]:
    return {value(x, 1): value(x, 2) for x in forms(node, "property")}


def at(node: list[Any]) -> tuple[float, float, float]:
    item = first(node, "at")
    return fvalue(item, 1), fvalue(item, 2), fvalue(item, 3)


def rotate(x: float, y: float, degrees: float) -> tuple[float, float]:
    angle = math.radians(degrees)
    return x * math.cos(angle) - y * math.sin(angle), x * math.sin(angle) + y * math.cos(angle)


def absolute_point(fp_at: tuple[float, float, float], local: tuple[float, float, float]) -> tuple[float, float]:
    dx, dy = rotate(local[0], local[1], fp_at[2])
    return round(fp_at[0] + dx, 6), round(fp_at[1] + dy, 6)


def is_copper_pad(pad: list[Any]) -> bool:
    pad_type = value(pad, 2)
    layers = first(pad, "layers") or []
    return pad_type != "np_thru_hole" and any("Cu" in str(layer) for layer in layers[1:])


def parse_board(path: Path) -> dict[str, Any]:
    root = sexp(path.read_text())
    if not root or root[0] != "kicad_pcb": raise ValueError("not a KiCad PCB S-expression")
    footprints = []
    for fp in forms(root, "footprint"):
        fp_at = at(fp); pads = []
        for pad in forms(fp, "pad"):
            local = at(pad); net = first(pad, "net")
            pads.append({
                "number": value(pad, 1), "type": value(pad, 2), "net": net_name(net),
                "copper": is_copper_pad(pad), "xy": absolute_point(fp_at, local), "local": local,
            })
        footprints.append({"ref": prop_map(fp).get("Reference", ""), "name": value(fp, 1), "at": fp_at, "pads": pads})
    def segment_points(item: list[Any]) -> list[tuple[float, float]]:
        return [(fvalue(first(item, key), 1), fvalue(first(item, key), 2)) for key in ("start", "end")]
    def polygons_from(node: list[Any], include_filled: bool = False) -> list[list[tuple[float, float]]]:
        polygons = []
        heads = forms(node, "polygon") + (forms(node, "filled_polygon") if include_filled else [])
        for polygon in heads:
            pts = first(polygon, "pts")
            if pts: polygons.append([(fvalue(p, 1), fvalue(p, 2)) for p in forms(pts, "xy")])
        return polygons
    zones, rule_areas = [], []
    for zone in forms(root, "zone"):
        # KiCad 10 serializes a rule area as a top-level `zone` carrying a
        # `keepout` form.  It is not copper, even though it has a Cu layer
        # set, so it must never be reported as copper intrusion into itself.
        keepout = first(zone, "keepout")
        if keepout is not None:
            rule_areas.append({
                "name": value(first(zone, "name"), 1),
                "polygons": polygons_from(zone),
                "native_keepout": True,
                "prohibitions": {key: value(first(keepout, key), 1) for key in ("tracks", "vias", "copperpour", "footprints")},
            })
        else:
            zones.append({"net": net_name(first(zone, "net")), "polygons": polygons_from(zone, include_filled=True)})
    # Accept the legacy parser form too, but classify it explicitly so a
    # KiCad-native enforceable keepout can be required for the antenna gate.
    rule_areas.extend({"name": value(first(area, "name"), 1), "polygons": polygons_from(area), "native_keepout": False, "prohibitions": {}} for area in forms(root, "rule_area"))
    layers = first(root, "layers") or []
    edge_points = []
    for line in forms(root, "gr_line"):
        if value(first(line, "layer"), 1) == "Edge.Cuts": edge_points.extend(segment_points(line))
    return {
        "footprints": footprints, "tracks": [segment_points(x) for x in forms(root, "segment")],
        "vias": [(fvalue(first(x, "at"), 1), fvalue(first(x, "at"), 2)) for x in forms(root, "via")],
        "zones": zones, "rule_areas": rule_areas,
        "copper_layers": [x for x in layers[1:] if len(x) > 1 and str(x[1]).endswith(".Cu")],
        "edge_points": edge_points,
    }


def result(name: str, status: str, evidence: Any) -> dict[str, Any]:
    return {"name": name, "status": status, "evidence": evidence}


def in_rect(point: tuple[float, float], rect: dict[str, float]) -> bool:
    return rect["xmin"] <= point[0] <= rect["xmax"] and rect["ymin"] <= point[1] <= rect["ymax"]


def segment_intersects_rect(a: tuple[float, float], b: tuple[float, float], rect: dict[str, float]) -> bool:
    if in_rect(a, rect) or in_rect(b, rect): return True
    # Liang-Barsky clipping: a nonempty clipped interval means intersection.
    dx, dy = b[0] - a[0], b[1] - a[1]; low, high = 0.0, 1.0
    for p, q in ((-dx, a[0] - rect["xmin"]), (dx, rect["xmax"] - a[0]), (-dy, a[1] - rect["ymin"]), (dy, rect["ymax"] - a[1])):
        if p == 0:
            if q < 0: return False
        else:
            t = q / p
            if p < 0: low = max(low, t)
            else: high = min(high, t)
    return low <= high


def point_in_polygon(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    """Ray casting with boundaries already handled by segment/rectangle checks."""
    inside = False
    for left, right in zip(polygon, polygon[1:] + polygon[:1]):
        if (left[1] > point[1]) != (right[1] > point[1]):
            x_cross = (right[0] - left[0]) * (point[1] - left[1]) / (right[1] - left[1]) + left[0]
            if point[0] < x_cross: inside = not inside
    return inside


def polygon_intersects_rect(polygon: list[tuple[float, float]], rect: dict[str, float]) -> bool:
    if not polygon: return False
    corners = [(rect["xmin"], rect["ymin"]), (rect["xmin"], rect["ymax"]), (rect["xmax"], rect["ymin"]), (rect["xmax"], rect["ymax"])]
    return any(in_rect(point, rect) for point in polygon) or any(point_in_polygon(corner, polygon) for corner in corners) or any(segment_intersects_rect(left, right, rect) for left, right in zip(polygon, polygon[1:] + polygon[:1]))


def check_outline(data: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    points = data["edge_points"]
    if not points: return result("BOARD OUTLINE", INC, "no Edge.Cuts line endpoints parsed")
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    width, height = max(xs) - min(xs), max(ys) - min(ys)
    target = cfg["outline_mm"]; tolerance = target["tolerance"]
    status = PASS if abs(width - target["width"]) <= tolerance and abs(height - target["height"]) <= tolerance else FAIL
    return result("BOARD OUTLINE", status, {"bbox_mm": [min(xs), min(ys), max(xs), max(ys)], "width_mm": width, "height_mm": height, "tolerance_mm": tolerance})


def check_duplicate_pads(data: dict[str, Any]) -> dict[str, Any]:
    failures = []
    for fp in data["footprints"]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for pad in fp["pads"]:
            if pad["copper"] and pad["number"]: groups.setdefault(pad["number"], []).append(pad)
        for number, pads in groups.items():
            if len(pads) > 1 and len({pad["net"] for pad in pads}) > 1:
                failures.append({"reference": fp["ref"], "pad": number, "nets": sorted({pad["net"] or "<no net>" for pad in pads}), "pads": [{"net": p["net"] or "<no net>", "xy_mm": p["xy"]} for p in pads]})
    return result("DUPLICATE PAD NUMBER NET CONSISTENCY", FAIL if failures else PASS, failures or "all duplicate copper-pad numbers have one canonical net")


def check_netless(data: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    allowed = cfg.get("allowed_netless_pads", {}); failures = []
    for fp in data["footprints"]:
        if not fp["ref"]: continue
        for pad in fp["pads"]:
            if pad["copper"] and not pad["net"] and pad["number"] not in allowed.get(fp["ref"], []):
                failures.append({"reference": fp["ref"], "pad": pad["number"], "xy_mm": pad["xy"]})
    return result("REQUIRED ELECTRICAL PAD NETLESS", FAIL if failures else PASS, failures or "no unexpected netless copper pads")


def check_antenna(data: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    rect = cfg["antenna_exclusion_mm"]; approved = set(cfg.get("antenna_approved_footprints", [])); hits = []
    rule_areas = data.get("rule_areas", [])
    named_rule_areas = [area for area in rule_areas if area.get("name") == cfg.get("antenna_rule_area_name")]
    def matches_rect(polygon: list[tuple[float, float]]) -> bool:
        if not polygon: return False
        xs, ys = [point[0] for point in polygon], [point[1] for point in polygon]
        return all(abs(actual - expected) <= 0.01 for actual, expected in ((min(xs), rect["xmin"]), (max(xs), rect["xmax"]), (min(ys), rect["ymin"]), (max(ys), rect["ymax"])))
    required_prohibitions = {"tracks", "vias", "copperpour", "footprints"}
    def enforceable(area: dict[str, Any]) -> bool:
        return area.get("native_keepout", False) and all(area.get("prohibitions", {}).get(key) == "not_allowed" for key in required_prohibitions)
    rule_area_status = NA if not named_rule_areas else (PASS if any(matches_rect(polygon) and enforceable(area) for area in named_rule_areas for polygon in area["polygons"]) else FAIL)
    for track in data["tracks"]:
        if len(track) == 2 and segment_intersects_rect(track[0], track[1], rect): hits.append({"type": "track", "xy_mm": track})
    for via in data["vias"]:
        if in_rect(via, rect): hits.append({"type": "via", "xy_mm": via})
    for zone in data["zones"]:
        if any(polygon_intersects_rect(polygon, rect) for polygon in zone["polygons"]): hits.append({"type": "zone", "net": zone["net"]})
    for fp in data["footprints"]:
        if fp["ref"] not in approved and (in_rect((fp["at"][0], fp["at"][1]), rect) or any(in_rect(p["xy"], rect) for p in fp["pads"])):
            hits.append({"type": "footprint_or_pad", "reference": fp["ref"], "origin_mm": fp["at"][:2]})
    status = FAIL if hits or rule_area_status == FAIL else PASS
    return result("ESP32 ANTENNA EXCLUSION", status, {"rect_mm": rect, "approved_boundary_refs": sorted(approved), "antenna_rule_area_name": cfg.get("antenna_rule_area_name"), "rule_area_crosscheck": rule_area_status, "hits": hits})


def check_edge(data: dict[str, Any]) -> dict[str, Any]:
    points = data["edge_points"]
    if not points: return result("BOARD EDGE", INC, "outline unavailable")
    xmin, xmax = min(p[0] for p in points), max(p[0] for p in points); ymin, ymax = min(p[1] for p in points), max(p[1] for p in points)
    outside = [{"reference": fp["ref"], "pad": p["number"], "xy_mm": p["xy"]} for fp in data["footprints"] for p in fp["pads"] if p["copper"] and not (xmin <= p["xy"][0] <= xmax and ymin <= p["xy"][1] <= ymax)]
    return result("BOARD EDGE", FAIL if outside else PASS, outside or {"pad_outside_outline": 0, "near-edge": "native DRC is authoritative in full mode"})


def normalized_geometry(data: dict[str, Any], refs: Iterable[str]) -> dict[str, Any]:
    by_ref = {fp["ref"]: fp for fp in data["footprints"]}; payload = {}
    for ref in refs:
        fp = by_ref.get(ref)
        if not fp: payload[ref] = None; continue
        pads = [{"number": p["number"], "xy_mm": [round(x, 4) for x in p["xy"]]} for p in fp["pads"]]
        payload[ref] = {"origin_mm": [round(x, 4) for x in fp["at"]], "pads": sorted(pads, key=lambda p: (p["number"], p["xy_mm"]))}
    return payload


def check_protected(data: dict[str, Any], reference: Path | None, cfg: dict[str, Any]) -> dict[str, Any]:
    if reference is None: return result("PROTECTED CHECKPOINT", INC, "--reference is required for a transaction-safe contract")
    if not reference.is_file(): return result("PROTECTED CHECKPOINT", INC, f"reference board missing: {reference}")
    try: expected = normalized_geometry(parse_board(reference), cfg["protected_footprints"])
    except Exception as exc: return result("PROTECTED CHECKPOINT", INC, f"reference parse failed: {exc}")
    actual = normalized_geometry(data, cfg["protected_footprints"])
    changed = {ref: {"reference": expected[ref], "board": actual[ref]} for ref in expected if expected[ref] != actual[ref]}
    return result("PROTECTED CHECKPOINT", FAIL if changed else PASS, changed or {"references": cfg["protected_footprints"], "comparison": "normalized footprint origin/rotation and pad geometry"})


def run_parity(board: Path) -> dict[str, Any]:
    command = [sys.executable, str(SYNC_CHECKER), "--pcb", str(board)]
    completed = subprocess.run(command, capture_output=True, text=True)
    try: payload = json.loads(completed.stdout)
    except json.JSONDecodeError: return result("SCHEMATIC-PCB PARITY", INC, {"exit_code": completed.returncode, "error": completed.stderr.strip()[-500:]})
    return result("SCHEMATIC-PCB PARITY", payload.get("status", INC), {"exit_code": completed.returncode, "mismatch_counts": {key: len(payload.get(key, [])) for key in ("board_only_references", "missing_pcb_footprints", "production_property_mismatches", "electrical_pad_net_mismatches")}})


def run_drc(board: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="board-contract-drc-") as temp:
        report = Path(temp) / "drc.json"
        command = ["kicad-cli", "pcb", "drc", "--format", "json", "--output", str(report), "--exit-code-violations", str(board)]
        completed = subprocess.run(command, capture_output=True, text=True)
        try: payload = json.loads(report.read_text())
        except (OSError, json.JSONDecodeError): return result("NATIVE DRC SUMMARY", INC, {"exit_code": completed.returncode, "stderr": completed.stderr.strip()[-500:]})
    violations = payload.get("violations", []); categories: dict[str, int] = {}
    for violation in violations: categories[violation.get("type", "unknown")] = categories.get(violation.get("type", "unknown"), 0) + 1
    geometry_types = {"clearance", "shorting_items", "hole_clearance", "courtyards_overlap", "edge_clearance", "solder_mask_bridge"}
    evidence = {"exit_code": completed.returncode, "geometric_violations": sum(n for key, n in categories.items() if key in geometry_types), "footprint_errors": sum(n for key, n in categories.items() if "footprint" in key or "courtyard" in key), "zone_errors": sum(n for key, n in categories.items() if "zone" in key), "unconnected_items": len(payload.get("unconnected_items", [])), "categories": categories}
    return result("NATIVE DRC SUMMARY", PASS if not violations else FAIL, evidence)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--fast", action="store_true", help="skip parity and native DRC")
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    args = parser.parse_args()
    checks: list[dict[str, Any]] = []
    try:
        cfg = json.loads(args.config.read_text()); data = parse_board(args.board)
        checks.append(result("BOARD LOAD", PASS, {"board": str(args.board)}))
    except Exception as exc:
        checks.append(result("BOARD LOAD", FAIL, {"board": str(args.board), "error": str(exc)}))
        payload = {"board": str(args.board), "mode": "fast" if args.fast else "full", "checks": checks, "overall_status": FAIL}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else "BOARD LOAD: FAIL\n" + str(exc)); return 1
    checks.extend([result("COPPER LAYERS", PASS if len(data["copper_layers"]) == 2 else FAIL, {"count": len(data["copper_layers"]), "layers": data["copper_layers"]}), check_outline(data, cfg), result("COUNTS", PASS, {"footprints": len(data["footprints"]), "tracks": len(data["tracks"]), "vias": len(data["vias"]), "zones": len(data["zones"])}), check_duplicate_pads(data), check_netless(data, cfg), check_antenna(data, cfg), check_edge(data), check_protected(data, args.reference, cfg)])
    if args.fast:
        checks.extend([result("SCHEMATIC-PCB PARITY", NA, "--fast"), result("NATIVE DRC SUMMARY", NA, "--fast")])
    else:
        checks.extend([run_parity(args.board), run_drc(args.board)])
    overall = PASS if all(check["status"] in (PASS, NA) for check in checks) else FAIL
    payload = {"board": str(args.board), "mode": "fast" if args.fast else "full", "checks": checks, "overall_status": overall}
    if args.json: print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for check in checks:
            print(f'{check["name"]}: {check["status"]} — {json.dumps(check["evidence"], sort_keys=True)}')
        print(f"OVERALL: {overall}")
    return 0 if overall == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
