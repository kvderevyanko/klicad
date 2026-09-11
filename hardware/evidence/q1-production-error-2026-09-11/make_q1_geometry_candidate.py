#!/usr/bin/env python3
"""Build a read-only-planning candidate from the named Q1 baseline copy.

The output is evidence only.  It is not an implementation source and must not
replace the controlled active board.
"""

from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "esp32-e220-q1-prechange-reference.kicad_pcb"
OUTPUT = HERE / "esp32-e220-q1-geometry-candidate.kicad_pcb"
FOOTPRINT_SOURCE = HERE.parents[1] / "esp32-e220.pretty" / "Diodes_DMP3130LQ-7_SOT23.kicad_mod"
FOOTPRINT_OUTPUT = HERE / "esp32-e220.pretty" / "Diodes_DMP3130LQ-7_SOT23.kicad_mod"


def replace_exact(text: str, old: str, new: str, count: int) -> str:
    actual = text.count(old)
    if actual != count:
        raise SystemExit(f"expected {count} occurrences, found {actual}: {old!r}")
    return text.replace(old, new)


text = SOURCE.read_text()

# Manufacturer SOT23 drawing: X1 is centreline-to-outer-edge, so the centre
# coordinate is X1 - X/2 = 1.35 - 0.40 = 0.95 mm.
text = replace_exact(text, "\t\t\t(at -1.35 1)\n", "\t\t\t(at -0.95 1)\n", 1)
text = replace_exact(text, "\t\t\t(at 1.35 1)\n", "\t\t\t(at 0.95 1)\n", 1)

# Re-anchor only the three tracks that terminate at moved pads.  Downstream
# endpoints, widths, layers, vias, and all other copper remain byte-identical.
text = replace_exact(text, "\t\t(start 61.65 77)\n", "\t\t(start 62.05 77)\n", 1)
text = replace_exact(text, "\t\t(start 64.349999 77)\n", "\t\t(start 63.949999 77)\n", 2)

OUTPUT.write_text(text)
print(OUTPUT)

footprint_text = FOOTPRINT_SOURCE.read_text()
footprint_text = replace_exact(footprint_text, "(at -1.350 1.000)", "(at -0.950 1.000)", 1)
footprint_text = replace_exact(footprint_text, "(at 1.350 1.000)", "(at 0.950 1.000)", 1)
FOOTPRINT_OUTPUT.write_text(footprint_text)
print(FOOTPRINT_OUTPUT)
