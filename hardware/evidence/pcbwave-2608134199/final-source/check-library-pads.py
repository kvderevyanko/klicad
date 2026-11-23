#!/usr/bin/python3
"""Compare embedded lands with the corresponding project footprint libraries."""
import json
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent


def signature(pad):
    loc, size, drill = pad.GetFPRelativePosition(), pad.GetSize(), pad.GetDrillSize()
    copper = pad.IsOnLayer(pcbnew.F_Cu) or pad.IsOnLayer(pcbnew.B_Cu)
    radius = pad.GetRoundRectRadiusRatio() if pad.GetShape() == pcbnew.PAD_SHAPE_ROUNDRECT else 0
    return (pad.GetNumber() if copper else "", loc.x, loc.y,
            size.x, size.y, drill.x, drill.y, pad.GetAttribute(), pad.GetShape(),
            round(pad.GetFPRelativeOrientation().AsDegrees() % 360, 6),
            pad.GetLayerSet().FmtBin(), round(radius, 6),
            str(pad.GetLocalSolderMaskMargin()), str(pad.GetLocalSolderPasteMargin()),
            str(pad.GetLocalSolderPasteMarginRatio()))


board = pcbnew.LoadBoard(str(HERE / "esp32-e220.kicad_pcb"))
items = {}
for fp in sorted(board.GetFootprints(), key=lambda fp: fp.GetReference()):
    name = str(fp.GetFPID().GetLibItemName())
    library_fp = pcbnew.FootprintLoad(str(HERE / "esp32-e220.pretty"), name)
    embedded = sorted(signature(p) for p in fp.Pads())
    library = sorted(signature(p) for p in library_fp.Pads())
    assert len(embedded) == len(library), fp.GetReference()
    for a, b in zip(embedded, library):
        assert a[0] == b[0] and a[3:] == b[3:], fp.GetReference()
        assert max(abs(a[i] - b[i]) for i in (1, 2)) <= 1, fp.GetReference()
    items[fp.GetReference()] = {"library": name, "pads": len(embedded)}
print(json.dumps({"status": "PASS", "footprints": len(items), "position_tolerance_nm": 1,
                  "paste_only_pad_numbers_ignored": True, "checked": items}, indent=2))
