#!/usr/bin/env python3
"""Numerically audit final diagnostic Gerber/IPC-D-356 output for F1."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parents[2]
FAB = HERE / "diagnostic-fabrication"
BOARD = HARDWARE / "esp32-e220.kicad_pcb"
sys.path.insert(0, str(HARDWARE))
sys.dont_write_bytecode = True

from check_board_contract import at, first, forms, fvalue, prop_map, sexp, value  # noqa: E402


EXPECTED_CENTRES = {"1": (41.635, 76.0), "2": (46.865, 76.0)}
EXPECTED_LOCAL = {"1": (-2.615, 0.0), "2": (2.615, 0.0)}
EXPECTED_NETS = {"1": "/BAT_PLUS", "2": "/BAT_FUSED"}
EXPECTED_SIZE = (1.78, 3.15)
EXPECTED_PITCH = 5.23
GERBER_COORDS = {"1": ("41635000", "-76000000"), "2": ("46865000", "-76000000")}
ROUNDRECT = (
    "RoundRect,0.356000X-0.534000X-1.219000X0.534000X-1.219000"
    "X0.534000X1.219000X-0.534000X1.219000X0"
)
IPC_EXPECTED = {
    "1": ("/BAT_PLUS", "+016392", "-029921", "0701", "1240"),
    "2": ("/BAT_FUSED", "+018451", "-029921", "0701", "1240"),
}


def close_pair(actual: tuple[float, float], expected: tuple[float, float], tolerance: float) -> bool:
    return all(abs(a - e) <= tolerance for a, e in zip(actual, expected))


def board_checks(failures: list[str]) -> dict[str, Any]:
    root = sexp(BOARD.read_text(encoding="utf-8"))
    matches = [fp for fp in forms(root, "footprint") if prop_map(fp).get("Reference") == "F1"]
    if len(matches) != 1:
        failures.append(f"board F1 count {len(matches)}")
        return {}
    f1 = matches[0]
    origin = at(f1)
    if origin != (44.25, 76.0, 0.0):
        failures.append(f"board F1 origin {origin}")
    pads = {value(pad, 1): pad for pad in forms(f1, "pad")}
    if sorted(pads) != ["1", "2"]:
        failures.append(f"board F1 pad numbers {sorted(pads)}")
    result: dict[str, Any] = {"origin_mm": list(origin), "pads": {}}
    for number in ("1", "2"):
        pad = pads.get(number)
        if pad is None:
            continue
        local = at(pad)[:2]
        size_node = first(pad, "size")
        size = (fvalue(size_node, 1), fvalue(size_node, 2))
        net_node = first(pad, "net")
        net = value(net_node, 1) if net_node is not None and len(net_node) == 2 else value(net_node, 2)
        absolute = (origin[0] + local[0], origin[1] + local[1])
        if not close_pair(local, EXPECTED_LOCAL[number], 0.0005):
            failures.append(f"board F1.{number} local centre {local}")
        if not close_pair(absolute, EXPECTED_CENTRES[number], 0.0005):
            failures.append(f"board F1.{number} absolute centre {absolute}")
        if not close_pair(size, EXPECTED_SIZE, 0.0005):
            failures.append(f"board F1.{number} size {size}")
        if net != EXPECTED_NETS[number]:
            failures.append(f"board F1.{number} net {net!r}")
        result["pads"][number] = {
            "local_centre_mm": list(local),
            "absolute_centre_mm": list(absolute),
            "size_mm": list(size),
            "net": net,
        }
    if pads.keys() >= {"1", "2"}:
        pitch = at(pads["2"])[0] - at(pads["1"])[0]
        result["pitch_mm"] = pitch
        if abs(pitch - EXPECTED_PITCH) > 0.0005:
            failures.append(f"board F1 pitch {pitch}")
    return result


def aperture(text: str, number: str) -> str | None:
    match = re.search(rf"^%ADD{re.escape(number)}(.+)\*%$", text, re.MULTILINE)
    return match.group(1) if match else None


def gerber_checks(failures: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for layer, filename in (
        ("F.Cu", "esp32-e220-F_Cu.gtl"),
        ("F.Paste", "esp32-e220-F_Paste.gtp"),
        ("F.Mask", "esp32-e220-F_Mask.gts"),
    ):
        text = (FAB / filename).read_text(encoding="ascii")
        if layer == "F.Cu":
            pattern = re.compile(
                r"D(?P<ap>\d+)\*\n"
                r"%TO\.P,F1,1\*%\n%TO\.N,/BAT_PLUS\*%\nX41635000Y-76000000D03\*\n"
                r"%TO\.P,F1,2\*%\n%TO\.N,/BAT_FUSED\*%\nX46865000Y-76000000D03\*"
            )
        else:
            pattern = re.compile(
                r"D(?P<ap>\d+)\*\n%TO\.C,F1\*%\n"
                r"X41635000Y-76000000D03\*\nX46865000Y-76000000D03\*"
            )
        match = pattern.search(text)
        if not match:
            failures.append(f"{layer} lacks exact F1 flashes/attributes")
            result[layer] = {"matched": False}
            continue
        ap = match.group("ap")
        definition = aperture(text, ap)
        if definition != ROUNDRECT:
            failures.append(f"{layer} F1 aperture D{ap} is {definition!r}")
        # RoundRect macro: total X=2*(0.534+0.356)=1.780 mm and
        # total Y=2*(1.219+0.356)=3.150 mm.
        result[layer] = {
            "matched": True,
            "aperture": f"D{ap}",
            "aperture_definition": definition,
            "derived_size_mm": [1.780, 3.150],
            "file_centres_mm": [[41.635, -76.0], [46.865, -76.0]],
            "board_centres_mm": [[41.635, 76.0], [46.865, 76.0]],
            "pitch_mm": 5.230,
        }
    return result


def ipc_checks(failures: list[str]) -> dict[str, Any]:
    text = (FAB / "esp32-e220-f1-final.d356").read_text(encoding="ascii")
    pattern = re.compile(
        r"^327(?P<net>/\S+)\s+F1\s+-(?P<pad>[12])\s+"
        r"A01X(?P<x>[+-]\d{6})Y(?P<y>[+-]\d{6})X(?P<sx>\d{4})Y(?P<sy>\d{4})R000S2$",
        re.MULTILINE,
    )
    records = {match.group("pad"): match.groupdict() for match in pattern.finditer(text)}
    if sorted(records) != ["1", "2"]:
        failures.append(f"IPC-D-356 F1 record set {sorted(records)}")
    result: dict[str, Any] = {}
    converted: dict[str, tuple[float, float]] = {}
    for number, expected in IPC_EXPECTED.items():
        record = records.get(number)
        if record is None:
            continue
        actual = tuple(record[key] for key in ("net", "x", "y", "sx", "sy"))
        if actual != expected:
            failures.append(f"IPC-D-356 F1.{number} fields {actual}, expected {expected}")
        x_mm = int(record["x"]) * 0.0001 * 25.4
        y_mm = -int(record["y"]) * 0.0001 * 25.4
        sx_mm = int(record["sx"]) * 0.0001 * 25.4
        sy_mm = int(record["sy"]) * 0.0001 * 25.4
        converted[number] = (x_mm, y_mm)
        if not close_pair((x_mm, y_mm), EXPECTED_CENTRES[number], 0.0013):
            failures.append(f"IPC-D-356 F1.{number} converted centre {(x_mm, y_mm)}")
        if not close_pair((sx_mm, sy_mm), EXPECTED_SIZE, 0.0013):
            failures.append(f"IPC-D-356 F1.{number} converted size {(sx_mm, sy_mm)}")
        result[number] = {
            "net": record["net"],
            "raw_inch_1e4": {key: record[key] for key in ("x", "y", "sx", "sy")},
            "converted_centre_mm": [round(x_mm, 6), round(y_mm, 6)],
            "converted_size_mm": [round(sx_mm, 6), round(sy_mm, 6)],
        }
    if converted.keys() >= {"1", "2"}:
        pitch = converted["2"][0] - converted["1"][0]
        result["converted_pitch_mm"] = round(pitch, 6)
        if abs(pitch - EXPECTED_PITCH) > 0.0013:
            failures.append(f"IPC-D-356 converted pitch {pitch}")
    return result


def main() -> int:
    failures: list[str] = []
    board = board_checks(failures)
    gerber = gerber_checks(failures)
    ipc = ipc_checks(failures)
    payload = {
        "status": "FAIL" if failures else "PASS",
        "scope": "diagnostic non-release F1 board/Gerber/IPC-D-356 audit",
        "physical_part": "Littelfuse 1812L200/16, non-polarized",
        "expected": {
            "pad_numbers": ["1", "2"],
            "absolute_centres_mm": EXPECTED_CENTRES,
            "size_mm": list(EXPECTED_SIZE),
            "pitch_mm": EXPECTED_PITCH,
            "pad_nets": EXPECTED_NETS,
        },
        "board": board,
        "gerber": gerber,
        "ipc_d356": ipc,
        "failures": failures,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
