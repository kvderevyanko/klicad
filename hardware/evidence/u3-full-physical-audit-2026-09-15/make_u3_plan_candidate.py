#!/usr/bin/env python3
"""Create a read-only U3 physical-plan candidate from the active PCB.

The output is retained evidence only.  This script must never write the active
PCB, schematic, generator, or project-local footprint library.
"""

from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "hardware" / "esp32-e220.kicad_pcb"
OUTPUT = HERE / "u3-ti-dbv-corrected-plan-candidate.kicad_pcb"


def replace_exact(text: str, old: str, new: str, count: int = 1) -> str:
    actual = text.count(old)
    if actual != count:
        raise SystemExit(f"expected {count} occurrences, found {actual}: {old!r}")
    return text.replace(old, new)


text = SOURCE.read_text()
start = text.index('\t(footprint "TI_SN74AHCT1G125DBVR_SOT23-5"')
depth = 0
end = None
for index in range(start, len(text)):
    if text[index] == "(":
        depth += 1
    elif text[index] == ")":
        depth -= 1
        if depth == 0:
            end = index + 1
            break
if end is None:
    raise SystemExit("U3 footprint block is unbalanced")

block = text[start:end]
for old, new in (
    ("\t\t\t(center -1.55 1.5)\n", "\t\t\t(center -1.75 2.2)\n"),
    ("\t\t\t(end -1.4 1.5)\n", "\t\t\t(end -1.6 2.2)\n"),
    ("\t\t\t(start -1.75 -1.8)\n", "\t\t\t(start -1.8 -2.1)\n"),
    ("\t\t\t(end 1.75 -1.8)\n", "\t\t\t(end 1.8 -2.1)\n"),
    ("\t\t\t(start -1.75 1.8)\n", "\t\t\t(start -1.8 2.1)\n"),
    ("\t\t\t(end -1.75 -1.8)\n", "\t\t\t(end -1.8 -2.1)\n"),
    ("\t\t\t(start 1.75 -1.8)\n", "\t\t\t(start 1.8 -2.1)\n"),
    ("\t\t\t(end 1.75 1.8)\n", "\t\t\t(end 1.8 2.1)\n"),
    ("\t\t\t(start 1.75 1.8)\n", "\t\t\t(start 1.8 2.1)\n"),
    ("\t\t\t(end -1.75 1.8)\n", "\t\t\t(end -1.8 2.1)\n"),
    ("\t\t\t(at -0.95 0.75)\n", "\t\t\t(at -0.95 1.3)\n"),
    ("\t\t\t(at 0 0.75)\n", "\t\t\t(at 0 1.3)\n"),
    ("\t\t\t(at 0.95 0.75)\n", "\t\t\t(at 0.95 1.3)\n"),
    ("\t\t\t(at 0.475 -0.75)\n", "\t\t\t(at 0.95 -1.3)\n"),
    ("\t\t\t(at -0.475 -0.75)\n", "\t\t\t(at -0.95 -1.3)\n"),
):
    block = replace_exact(block, old, new)
block = replace_exact(block, "\t\t\t(roundrect_rratio 0.166667)\n", "\t\t\t(roundrect_rratio 0.083333)\n", 5)
text = text[:start] + block + text[end:]

# Re-anchor exactly one existing F.Cu segment per corrected pad.  Opposite
# endpoints, widths, layers, nets, all vias, and all non-U3 copper stay fixed.
for old, new in (
    ("\t\t(start 88.05 54.75)\n", "\t\t(start 88.05 55.3)\n"),
    ("\t\t(end 89 54.75)\n", "\t\t(end 89 55.3)\n"),
    ("\t\t(start 89.95 54.75)\n", "\t\t(start 89.95 55.3)\n"),
    ("\t\t(start 89.475 53.25)\n", "\t\t(start 89.95 52.7)\n"),
    ("\t\t(end 88.525 53.25)\n", "\t\t(end 88.05 52.7)\n"),
):
    text = replace_exact(text, old, new)

OUTPUT.write_text(text)
print(OUTPUT)
