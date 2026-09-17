#!/usr/bin/env python3
"""Numerically audit diagnostic Gerber and IPC-D-356 resistor outputs."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUTS = HERE / "diagnostic-outputs"
REFS = ("R1", "R2", "R3", "R4", "R8", "R9")
ROTATION = {"R1": 90, "R2": 90, "R3": 0, "R4": 0, "R8": 0, "R9": 0}
NETS = {
    "R1": {"1": "/Q1_GATE", "2": "/GND"},
    "R2": {"1": "/BUCK_IN", "2": "/Q1_GATE"},
    "R3": {"1": "/BUCK_IN", "2": "/BAT_SENSE"},
    "R4": {"1": "/BAT_SENSE", "2": "/GND"},
    "R8": {"1": "/E220_M0", "2": "/GND"},
    "R9": {"1": "/E220_M1", "2": "/GND"},
}
CENTRES = {
    "R1": {"1": (58.5, 67.85), "2": (58.5, 66.15)},
    "R2": {"1": (62.5, 67.85), "2": (62.5, 66.15)},
    "R3": {"1": (85.15, 66.0), "2": (86.85, 66.0)},
    "R4": {"1": (89.15, 66.0), "2": (90.85, 66.0)},
    "R8": {"1": (39.15, 35.0), "2": (40.85, 35.0)},
    "R9": {"1": (45.15, 35.0), "2": (46.85, 35.0)},
}


def aperture_dimensions(line: str) -> tuple[int, tuple[float, float]] | None:
    match = re.match(r"%ADD(\d+)(RoundRect|R|O|C),(.+)\*%", line)
    if not match:
        return None
    number, shape, payload = int(match.group(1)), match.group(2), match.group(3)
    values = [float(item) for item in payload.split("X")]
    if shape == "RoundRect":
        radius = values[0]
        xs = values[1::2]
        ys = values[2::2]
        dims = (max(xs) - min(xs) + 2 * radius, max(ys) - min(ys) + 2 * radius)
    elif shape in {"R", "O"}:
        dims = (values[0], values[1])
    else:
        dims = (values[0], values[0])
    return number, dims


def read_gerber(path: Path, copper: bool) -> dict[str, list[dict[str, object]]]:
    apertures: dict[int, tuple[float, float]] = {}
    result = {ref: [] for ref in REFS}
    aperture = 0
    ref = ""
    pad = ""
    for raw in path.read_text().splitlines():
        parsed = aperture_dimensions(raw)
        if parsed:
            apertures[parsed[0]] = parsed[1]
            continue
        select = re.fullmatch(r"D(\d+)\*", raw)
        if select:
            aperture = int(select.group(1))
            continue
        attr = re.fullmatch(r"%TO\.(?:P|C),([^,\*]+)(?:,([^\*]+))?\*%", raw)
        if attr:
            ref = attr.group(1)
            pad = attr.group(2) or ""
            continue
        if raw == "%TD*%":
            ref = pad = ""
            continue
        flash = re.fullmatch(r"X(-?\d+)Y(-?\d+)D03\*", raw)
        if flash and ref in result:
            number = pad if copper else str(len(result[ref]) + 1)
            result[ref].append({
                "pad": number,
                "centre_mm": [int(flash.group(1)) / 1_000_000, abs(int(flash.group(2))) / 1_000_000],
                "aperture": aperture,
                "absolute_size_mm": list(apertures[aperture]),
            })
    return result


def audit_gerber(path: Path, copper: bool) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    flashes = read_gerber(path, copper)
    report: dict[str, object] = {}
    for ref in REFS:
        items = flashes[ref]
        if len(items) != 2:
            failures.append(f"{path.name}: {ref} has {len(items)} flashes, expected 2 separate apertures")
            continue
        items.sort(key=lambda item: str(item["pad"]))
        for item in items:
            pad = str(item["pad"])
            expected_centre = CENTRES[ref][pad]
            actual_centre = tuple(float(value) for value in item["centre_mm"])
            if actual_centre != expected_centre:
                failures.append(f"{path.name}: {ref}.{pad} centre {actual_centre}, expected {expected_centre}")
            absolute_size = tuple(round(float(value), 6) for value in item["absolute_size_mm"])
            expected_absolute = (0.8, 0.9) if ROTATION[ref] == 90 else (0.9, 0.8)
            if absolute_size != expected_absolute:
                failures.append(f"{path.name}: {ref}.{pad} aperture {absolute_size}, expected {expected_absolute}")
        c1 = tuple(float(value) for value in items[0]["centre_mm"])
        c2 = tuple(float(value) for value in items[1]["centre_mm"])
        pitch = round(math.dist(c1, c2), 6)
        gap = round(pitch - 0.9, 6)
        if (pitch, gap) != (1.7, 0.8):
            failures.append(f"{path.name}: {ref} pitch/gap {(pitch, gap)}")
        report[ref] = {
            "pad_flashes": items,
            "local_pad_size_mm": [0.9, 0.8],
            "pitch_mm": pitch,
            "inner_gap_mm": gap,
            "separate_apertures": len(items) == 2,
        }
    return report, failures


def audit_ipc(path: Path) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    report: dict[str, object] = {ref: {} for ref in REFS}
    pattern = re.compile(
        r"^327(?P<net>.{14})\s+(?P<ref>R[123489])\s+-(?P<pad>[12])\s+"
        r"A01X(?P<x>[+-]\d+)Y(?P<y>[+-]\d+)X(?P<sx>\d+)Y(?P<sy>\d+)R(?P<rot>\d+)S2$"
    )
    for line in path.read_text().splitlines():
        match = pattern.match(line)
        if not match:
            continue
        ref, pad = match.group("ref"), match.group("pad")
        centre = (int(match.group("x")) * 0.0001 * 25.4, abs(int(match.group("y"))) * 0.0001 * 25.4)
        size = (int(match.group("sx")) * 0.0001 * 25.4, int(match.group("sy")) * 0.0001 * 25.4)
        net = match.group("net").strip()
        expected_net = NETS[ref][pad]
        if net != expected_net:
            failures.append(f"IPC: {ref}.{pad} net {net!r}, expected {expected_net!r}")
        if math.dist(centre, CENTRES[ref][pad]) > 0.002:
            failures.append(f"IPC: {ref}.{pad} centre {centre}, expected {CENTRES[ref][pad]}")
        if max(abs(size[index] - target) for index, target in enumerate((0.9, 0.8))) > 0.002:
            failures.append(f"IPC: {ref}.{pad} size {size}, expected (0.9, 0.8)")
        report[ref][pad] = {
            "net": net,
            "centre_mm": [round(centre[0], 4), round(centre[1], 4)],
            "size_mm": [round(size[0], 4), round(size[1], 4)],
            "rotation_code": int(match.group("rot")),
        }
    for ref in REFS:
        if sorted(report[ref]) != ["1", "2"]:
            failures.append(f"IPC: {ref} pad inventory {sorted(report[ref])}")
    return report, failures


def main() -> int:
    failures: list[str] = []
    layers: dict[str, object] = {}
    for key, filename, copper in (
        ("F.Cu", "esp32-e220-F_Cu.gtl", True),
        ("F.Mask", "esp32-e220-F_Mask.gts", False),
        ("F.Paste", "esp32-e220-F_Paste.gtp", False),
    ):
        report, layer_failures = audit_gerber(OUTPUTS / filename, copper)
        layers[key] = report
        failures.extend(layer_failures)
    ipc, ipc_failures = audit_ipc(OUTPUTS / "esp32-e220.d356")
    failures.extend(ipc_failures)
    payload = {
        "status": "FAIL" if failures else "PASS",
        "gerber": layers,
        "ipc_d_356": ipc,
        "failures": failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
