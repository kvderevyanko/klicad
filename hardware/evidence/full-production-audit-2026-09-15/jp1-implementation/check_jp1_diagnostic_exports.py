#!/usr/bin/env python3
"""Check the retained diagnostic Gerber, Excellon, and IPC-D-356 JP1 data."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent / "diagnostic-fabrication"
PTH = (ROOT / "esp32-e220-PTH.drl").read_text(encoding="ascii")
REPORT = (ROOT / "DRILL_REPORT.txt").read_text(encoding="utf-8")
IPC = (ROOT / "ESP32-E220-Carrier-Rev1-JP1-DIAGNOSTIC.ipc356").read_text(encoding="ascii")
FCU = (ROOT / "esp32-e220-F_Cu.gbr").read_text(encoding="ascii")
BCU = (ROOT / "esp32-e220-B_Cu.gbr").read_text(encoding="ascii")

failures = []
tools = dict(re.findall(r"^(T\d+)C([0-9.]+)$", PTH, re.MULTILINE))
if tools.get("T3") != "1.020":
    failures.append(f"T3 is {tools.get('T3')!r}, expected 1.020 mm")
tool3 = re.search(r"^T3\n(.*?)(?=^T\d+\n|^M30)", PTH, re.MULTILINE | re.DOTALL)
hits = set(re.findall(r"^X([-0-9.]+)Y([-0-9.]+)$", tool3.group(1), re.MULTILINE)) if tool3 else set()
expected_hits = {("96.0", "-14.0"), ("98.54", "-14.0")}
if hits != expected_hits:
    failures.append(f"T3 hits {sorted(hits)}, expected {sorted(expected_hits)}")
if 'T3  1.020mm  0.0402"  (2 holes)' not in REPORT:
    failures.append("drill report lacks exact two-hole 1.020-mm tool entry")

ipc_lines = [line for line in IPC.splitlines() if "JP1" in line]
expected_ipc = {
    "1": ("/5V_SYS", "D0402", "X+037795Y-005512", "X0669Y0669", "R270"),
    "2": ("/DEVKIT_VIN", "D0402", "X+038795Y-005512", "X0669Y0669", "R270"),
}
for number, fields in expected_ipc.items():
    matches = [line for line in ipc_lines if f"-{number}" in line]
    if len(matches) != 1 or not all(field in matches[0] for field in fields):
        failures.append(f"IPC-D-356 JP1 pad {number} mismatch: {matches}")

for label, gerber, expected in (
    ("F.Cu", FCU, (("D12", "1", "96000000"), ("D13", "2", "98540000"))),
    ("B.Cu", BCU, (("D10", "1", "96000000"), ("D11", "2", "98540000"))),
):
    for aperture, pad, x in expected:
        pattern = rf"{aperture}\*\n%TO\.P,JP1,{pad}\*%.*?X{x}Y-14000000D03\*"
        if not re.search(pattern, gerber, re.DOTALL):
            failures.append(f"{label} JP1 pad {pad} aperture/centre mismatch")
if "%ADD12R,1.700000X1.700000*%" not in FCU or "%ADD13O,1.700000X1.700000*%" not in FCU:
    failures.append("F.Cu JP1 1.700-mm rectangular/oval apertures missing")
if "%ADD10R,1.700000X1.700000*%" not in BCU or "%ADD11O,1.700000X1.700000*%" not in BCU:
    failures.append("B.Cu JP1 1.700-mm rectangular/oval apertures missing")

payload = {
    "status": "FAIL" if failures else "PASS",
    "scope": "diagnostic exports only; not a production release",
    "drill_tool": {"id": "T3", "diameter_mm": 1.020, "hits_mm": [[96.0, 14.0], [98.54, 14.0]]},
    "ipc_d356": {"1": {"net": "/5V_SYS", "drill_in": 0.0402}, "2": {"net": "/DEVKIT_VIN", "drill_in": 0.0402}},
    "gerber_copper_mm": {"pad_size": [1.70, 1.70], "pitch": 2.54},
    "failures": failures,
}
print(json.dumps(payload, indent=2, sort_keys=True))
raise SystemExit(1 if failures else 0)
