#!/usr/bin/env python3
"""Build the reviewed JP1-only candidate; never writes the active board."""

from pathlib import Path

import pcbnew


EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[2]
SOURCE_BOARD = ROOT / "esp32-e220.kicad_pcb"
LIBRARY = ROOT / "esp32-e220.pretty"
OUTPUT_BOARD = EVIDENCE / "esp32-e220-jp1-candidate.kicad_pcb"
FOOTPRINT_NAME = "Samtec_TSW-102-07-G-S_1x02_P2.54mm_THT"


def copy_field_placement(target, source) -> None:
    target.SetPosition(source.GetPosition())
    target.SetTextAngle(source.GetTextAngle())
    target.SetLayer(source.GetLayer())
    target.SetVisible(source.IsVisible())


def main() -> None:
    board = pcbnew.LoadBoard(str(SOURCE_BOARD))
    old = next(fp for fp in board.GetFootprints() if fp.GetReference() == "JP1")
    replacement = pcbnew.FootprintLoad(str(LIBRARY), FOOTPRINT_NAME)
    if replacement is None:
        raise RuntimeError(f"Cannot load {LIBRARY / (FOOTPRINT_NAME + '.kicad_mod')}")

    old_pads = {pad.GetNumber(): pad for pad in old.Pads()}
    if set(old_pads) != {"1", "2"}:
        raise RuntimeError(f"Unexpected JP1 pads: {sorted(old_pads)}")

    replacement.SetFPIDAsString(f"Carrier:{FOOTPRINT_NAME}")
    replacement.SetReference("JP1")
    replacement.SetValue(old.GetValue())
    replacement.SetPosition(old.GetPosition())
    replacement.SetOrientation(old.GetOrientation())
    replacement.SetPath(old.GetPath())
    replacement.SetLocked(old.IsLocked())
    replacement.SetUuidDirect(old.m_Uuid)
    copy_field_placement(replacement.Reference(), old.Reference())
    copy_field_placement(replacement.Value(), old.Value())

    for number, old_pad in old_pads.items():
        new_pad = replacement.FindPadByNumber(number)
        if new_pad is None:
            raise RuntimeError(f"Replacement JP1 missing pad {number}")
        new_pad.SetNet(old_pad.GetNet())
        new_pad.SetUuidDirect(old_pad.m_Uuid)

    board.Remove(old)
    board.Add(replacement)
    board.BuildListOfNets()
    pcbnew.SaveBoard(str(OUTPUT_BOARD), board)
    print(OUTPUT_BOARD)


if __name__ == "__main__":
    main()
