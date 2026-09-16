#!/usr/bin/env python3
"""Direct numeric audit of U4 Gerbers and IPC-D-356."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GERBER = ROOT / "fabrication" / "gerber"
IPC = ROOT / "fabrication" / "esp32-e220-U4.ipc356"

EXPECTED_CENTRES = [
    (17.75, -24.70),
    (17.75, -27.00),
    (23.55, -27.00),
    (17.75, -29.30),
]
EXPECTED_COPPER = [(2.15, 0.95), (2.15, 0.95), (2.15, 3.25), (2.15, 0.95)]
EXPECTED_MASK = [(2.25, 1.05), (2.25, 1.05), (2.25, 3.35), (2.25, 1.05)]
EXPECTED_PADS = ["1", "2", "2", "3"]
EXPECTED_NETS = ["GND", "AUX_3V3", "AUX_3V3", "5V_SYS"]


def close_pair(actual: tuple[float, float], expected: tuple[float, float], tol: float) -> bool:
    return all(abs(a - e) <= tol for a, e in zip(actual, expected))


def apertures(text: str) -> dict[int, tuple[float, float]]:
    result: dict[int, tuple[float, float]] = {}
    for match in re.finditer(r"%ADD(\d+)R,([0-9.]+)X([0-9.]+)\*%", text):
        result[int(match.group(1))] = (float(match.group(2)), float(match.group(3)))
    for match in re.finditer(r"%ADD(\d+)RoundRect,([^*]+)\*%", text):
        values = [float(item) for item in match.group(2).split("X")[:-1]]
        radius = values[0]
        xs = values[1::2]
        ys = values[2::2]
        result[int(match.group(1))] = (
            max(xs) - min(xs) + 2 * radius,
            max(ys) - min(ys) + 2 * radius,
        )
    return result


def u4_flashes(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    aps = apertures(text)
    selected: int | None = None
    in_u4 = False
    flashes: list[dict[str, object]] = []
    for line in text.splitlines():
        dcode = re.fullmatch(r"D(\d+)\*", line)
        if dcode:
            selected = int(dcode.group(1))
            continue
        if line == "%TO.C,U4*%" or line.startswith("%TO.P,U4,"):
            in_u4 = True
            continue
        if line == "%TD*%":
            in_u4 = False
            continue
        flash = re.fullmatch(r"X(-?\d+)Y(-?\d+)D03\*", line)
        if in_u4 and flash:
            if selected not in aps:
                raise AssertionError(f"U4 flash uses unknown aperture D{selected} in {path}")
            flashes.append({
                "centre_mm": [int(flash.group(1)) / 1_000_000, int(flash.group(2)) / 1_000_000],
                "aperture": f"D{selected}",
                "dimensions_mm": list(aps[selected]),
            })
    return flashes


def audit_gerber(path: Path, expected_sizes: list[tuple[float, float]]) -> dict[str, object]:
    flashes = u4_flashes(path)
    failures: list[str] = []
    if len(flashes) != 4:
        failures.append(f"expected four U4 flashes, found {len(flashes)}")
    for index, (flash, centre, size) in enumerate(zip(flashes, EXPECTED_CENTRES, expected_sizes), 1):
        actual_centre = tuple(float(v) for v in flash["centre_mm"])
        actual_size = tuple(float(v) for v in flash["dimensions_mm"])
        if not close_pair(actual_centre, centre, 0.000001):
            failures.append(f"flash {index} centre {actual_centre} != {centre}")
        if not close_pair(actual_size, size, 0.000001):
            failures.append(f"flash {index} size {actual_size} != {size}")
    if len(flashes) == 4:
        lead_pitch = abs(float(flashes[1]["centre_mm"][1]) - float(flashes[0]["centre_mm"][1]))
        lead_pitch_2 = abs(float(flashes[3]["centre_mm"][1]) - float(flashes[1]["centre_mm"][1]))
        row_separation = abs(float(flashes[2]["centre_mm"][0]) - float(flashes[1]["centre_mm"][0]))
    else:
        lead_pitch = lead_pitch_2 = row_separation = float("nan")
    if abs(lead_pitch - 2.30) > 0.000001 or abs(lead_pitch_2 - 2.30) > 0.000001:
        failures.append("lead pitch is not 2.30 mm")
    if abs(row_separation - 5.80) > 0.000001:
        failures.append("lead-to-tab row separation is not 5.80 mm")
    return {
        "path": str(path),
        "status": "FAIL" if failures else "PASS",
        "u4_flashes": flashes,
        "lead_pitch_mm": [lead_pitch, lead_pitch_2],
        "lead_to_tab_row_separation_mm": row_separation,
        "failures": failures,
    }


def audit_ipc() -> dict[str, object]:
    pattern = re.compile(
        r"^327/(\S+)\s+U4\s+-(\d)\s+A01X([+-]\d+)Y([+-]\d+)X(\d+)Y(\d+)R(\d+)S2$"
    )
    scale = 0.00254  # IPC-D-356 CUST 0: 0.1 mil per integer unit.
    records: list[dict[str, object]] = []
    for line in IPC.read_text(encoding="utf-8").splitlines():
        match = pattern.fullmatch(line)
        if not match:
            continue
        records.append({
            "net": match.group(1),
            "pad": match.group(2),
            "centre_mm": [int(match.group(3)) * scale, int(match.group(4)) * scale],
            "dimensions_mm": [int(match.group(5)) * scale, int(match.group(6)) * scale],
            "rotation": int(match.group(7)),
        })
    failures: list[str] = []
    if len(records) != 4:
        failures.append(f"expected four U4 IPC records, found {len(records)}")
    for index, (record, pad, net, centre, size) in enumerate(
        zip(records, EXPECTED_PADS, EXPECTED_NETS, EXPECTED_CENTRES, EXPECTED_COPPER), 1
    ):
        if record["pad"] != pad or record["net"] != net:
            failures.append(f"record {index} pad/net {record['pad']}/{record['net']} != {pad}/{net}")
        if not close_pair(tuple(record["centre_mm"]), centre, 0.0013):
            failures.append(f"record {index} centre {record['centre_mm']} outside IPC quantization tolerance")
        if not close_pair(tuple(record["dimensions_mm"]), size, 0.0013):
            failures.append(f"record {index} size {record['dimensions_mm']} outside IPC quantization tolerance")
    return {
        "path": str(IPC),
        "units": "CUST 0 (0.1 mil integer units)",
        "quantization_tolerance_mm": 0.0013,
        "status": "FAIL" if failures else "PASS",
        "u4_records": records,
        "failures": failures,
    }


def main() -> int:
    layers = {
        "F.Cu": audit_gerber(GERBER / "esp32-e220-F_Cu.gtl", EXPECTED_COPPER),
        "F.Mask": audit_gerber(GERBER / "esp32-e220-F_Mask.gts", EXPECTED_MASK),
        "F.Paste": audit_gerber(GERBER / "esp32-e220-F_Paste.gtp", EXPECTED_COPPER),
    }
    ipc = audit_ipc()
    failures = [name for name, audit in layers.items() if audit["status"] != "PASS"]
    if ipc["status"] != "PASS":
        failures.append("IPC-D-356")
    payload = {
        "status": "FAIL" if failures else "PASS",
        "gerber": layers,
        "ipc_d_356": ipc,
        "failed_gates": failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
