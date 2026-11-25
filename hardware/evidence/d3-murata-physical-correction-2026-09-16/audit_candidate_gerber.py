#!/usr/bin/env python3
"""Verify planning-candidate D3/Murata pad flashes in the X2 F.Cu Gerber."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
GERBER = HERE / "diagnostic-gerbers-x2" / "candidate-d3-murata-F_Cu.gtl"
OUT = HERE / "05-candidate-gerber-pad-audit.json"

EXPECTED = {
    "D3": {
        "1": ((44.350, 70.500), (2.160, 2.260), "BAT_FUSED"),
        "2": ((39.450, 70.500), (2.160, 2.260), "GND"),
    },
    "C1": {
        "1": ((66.700, 59.225), (1.200, 1.300), "BUCK_IN"),
        "2": ((68.700, 59.225), (1.200, 1.300), "GND"),
    },
    "C2": {
        "1": ((66.725, 56.000), (0.700, 0.700), "BUCK_IN"),
        "2": ((65.275, 56.000), (0.700, 0.700), "GND"),
    },
    "C3": {
        "1": ((71.900, 59.225), (0.700, 1.300), "5V_SYS"),
        "2": ((69.900, 59.225), (0.700, 1.300), "GND"),
    },
    "C4": {
        "1": ((67.000, 52.775), (0.700, 0.700), "SS_TR"),
        "2": ((67.000, 54.225), (0.700, 0.700), "GND"),
    },
    "C5": {
        "1": ((23.275, 48.000), (0.750, 0.900), "5V_SYS"),
        "2": ((24.725, 48.000), (0.750, 0.900), "GND"),
    },
    "C6": {
        "1": ((20.580, 49.750), (0.700, 0.700), "5V_SYS"),
        "2": ((22.030, 49.750), (0.700, 0.700), "GND"),
    },
    "C7": {
        "1": ((85.500, 54.725), (0.700, 0.700), "5V_SYS"),
        "2": ((85.500, 53.275), (0.700, 0.700), "GND"),
    },
    "C8": {
        "1": ((87.275, 69.000), (0.700, 0.700), "BAT_SENSE"),
        "2": ((88.725, 69.000), (0.700, 0.700), "GND"),
    },
    # C9 is rotated -90 degrees, so Gerber X/Y aperture extents are swapped.
    "C9": {
        "1": ((17.500, 32.000), (1.300, 1.200), "5V_SYS"),
        "2": ((17.500, 34.000), (1.300, 1.200), "GND"),
    },
    "C10": {
        "1": ((15.400, 27.000), (1.200, 1.300), "AUX_3V3"),
        "2": ((13.400, 27.000), (1.200, 1.300), "GND"),
    },
}


def close_pair(left: tuple[float, float], right: tuple[float, float]) -> bool:
    return all(math.isclose(a, b, abs_tol=0.000002) for a, b in zip(left, right))


def apertures(text: str) -> dict[str, tuple[float, float]]:
    result: dict[str, tuple[float, float]] = {}
    for line in text.splitlines():
        if match := re.fullmatch(r"%ADD(\d+)R,([0-9.]+)X([0-9.]+)\*%", line):
            code, x, y = match.groups()
            result[code] = (float(x), float(y))
        elif match := re.fullmatch(r"%ADD(\d+)RoundRect,([^*]+)\*%", line):
            code, values = match.groups()
            numbers = [float(value) for value in values.split("X")]
            radius = numbers[0]
            points = list(zip(numbers[1::2], numbers[2::2]))
            xs = [item[0] for item in points]
            ys = [item[1] for item in points]
            result[code] = (
                max(xs) - min(xs) + 2 * radius,
                max(ys) - min(ys) + 2 * radius,
            )
    return result


def flashes(text: str) -> dict[str, dict[str, dict[str, object]]]:
    aperture_map = apertures(text)
    active_aperture = active_ref = active_pad = active_net = None
    result: dict[str, dict[str, dict[str, object]]] = {}
    for line in text.splitlines():
        if match := re.fullmatch(r"D(\d+)\*", line):
            active_aperture = match.group(1)
        elif match := re.fullmatch(r"%TO\.P,([^,]+),([^*]+)\*%", line):
            active_ref, active_pad = match.groups()
        elif match := re.fullmatch(r"%TO\.N,/?([^*]+)\*%", line):
            active_net = match.group(1)
        elif line == "%TD*%":
            active_ref = active_pad = active_net = None
        elif match := re.fullmatch(r"X(-?\d+)Y(-?\d+)D03\*", line):
            if active_ref in EXPECTED and active_pad is not None:
                result.setdefault(active_ref, {})[active_pad] = {
                    "center_mm": [int(match.group(1)) / 1_000_000, -int(match.group(2)) / 1_000_000],
                    "aperture_mm": list(aperture_map[active_aperture]),
                    "net": active_net,
                }
    return result


def main() -> int:
    actual = flashes(GERBER.read_text(encoding="utf-8"))
    errors: list[str] = []
    for ref, pads in EXPECTED.items():
        for pad, (center, size, net) in pads.items():
            got = actual.get(ref, {}).get(pad)
            if got is None:
                errors.append(f"missing {ref}.{pad}")
                continue
            if not close_pair(tuple(got["center_mm"]), center):
                errors.append(f"{ref}.{pad} center {got['center_mm']} != {center}")
            if not close_pair(tuple(got["aperture_mm"]), size):
                errors.append(f"{ref}.{pad} aperture {got['aperture_mm']} != {size}")
            if got["net"] != net:
                errors.append(f"{ref}.{pad} net {got['net']} != {net}")
    OUT.write_text(json.dumps({"status": "PASS" if not errors else "FAIL", "pads": actual, "errors": errors}, indent=2) + "\n")
    print(f"{'PASS' if not errors else 'FAIL'}: {len(EXPECTED) * 2} Gerber pad flashes checked")
    for error in errors:
        print(error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
