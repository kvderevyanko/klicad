#!/usr/bin/env python3
"""Generate the un-routed Stage 7.1 preliminary mechanical-placement board.

This is deliberately not a routed or production PCB.  It creates only a
generous provisional outline, source-audited carrier footprints and visible
mechanical access/clearance guides.  There are no tracks, vias, copper zones,
net assignments, mounting NPTHs or fabrication outputs.
"""

from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parent
LIBRARY = ROOT / "esp32-e220.pretty"
OUTPUT = ROOT / "esp32-e220.kicad_pcb"


def v(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def add_line(board: pcbnew.BOARD, x1: float, y1: float, x2: float, y2: float,
             layer: int, width: float = 0.25) -> None:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.S_SEGMENT)
    shape.SetStart(v(x1, y1))
    shape.SetEnd(v(x2, y2))
    shape.SetLayer(layer)
    shape.SetWidth(pcbnew.FromMM(width))
    board.Add(shape)


def add_rect(board: pcbnew.BOARD, x1: float, y1: float, x2: float, y2: float,
             layer: int, width: float = 0.25) -> None:
    add_line(board, x1, y1, x2, y1, layer, width)
    add_line(board, x2, y1, x2, y2, layer, width)
    add_line(board, x2, y2, x1, y2, layer, width)
    add_line(board, x1, y2, x1, y1, layer, width)


def add_text(board: pcbnew.BOARD, message: str, x: float, y: float,
             layer: int = pcbnew.Dwgs_User, size: float = 1.4) -> None:
    graphic = pcbnew.PCB_TEXT(board)
    graphic.SetText(message)
    graphic.SetPosition(v(x, y))
    graphic.SetLayer(layer)
    graphic.SetTextSize(v(size, size))
    graphic.SetTextThickness(pcbnew.FromMM(0.22))
    board.Add(graphic)


def add_footprint(board: pcbnew.BOARD, source_name: str, reference: str,
                  x: float, y: float, rotation: float = 0.0) -> None:
    footprint = pcbnew.FootprintLoad(str(LIBRARY), source_name)
    if footprint is None:
        raise RuntimeError(f"Cannot load Carrier:{source_name}")
    footprint.SetReference(reference)
    footprint.SetPosition(v(x, y))
    footprint.SetOrientationDegrees(rotation)
    board.Add(footprint)


def main() -> None:
    board = pcbnew.BOARD()
    board.SetFileName(str(OUTPUT))
    title = board.GetTitleBlock()
    title.SetTitle("ESP32 + E220 carrier — Stage 7.1 preliminary mechanical placement")
    title.SetComment(0, "UNROUTED / NOT FOR PRODUCTION")
    title.SetComment(1, "No tracks, vias, zones or net assignments")
    title.SetComment(2, "Approved electrical baseline is schematic-controlled")

    # Preliminary outline only: generous for edge access and module clearance.
    add_rect(board, 0, 0, 160, 100, pcbnew.Edge_Cuts, 0.30)
    add_text(board, "STAGE 7.1 — PRELIMINARY MECHANICAL PLACEMENT ONLY", 80, 5,
             pcbnew.Dwgs_User, 2.0)
    add_text(board, "NO ROUTING / NO COPPER ZONES / NOT FOR PRODUCTION", 80, 8.5,
             pcbnew.Dwgs_User, 1.6)

    # Carrier power cluster: source-audited footprints, deliberately distant
    # from the ESP32/E220 antenna regions.  Locations are placement studies,
    # not final compact-layout placement.
    add_footprint(board, "JST_B2B-XH-A_1x02_P2.50mm_THT", "J4", 15, 82)
    add_footprint(board, "Littelfuse_1812L200_16_4532Metric", "F1", 27, 82)
    add_footprint(board, "Littelfuse_SMBJ10CA_DO214AA", "D3", 35, 82)
    add_footprint(board, "Diodes_DMP3130LQ-7_SOT23", "Q1", 43, 82)
    add_footprint(board, "TI_TPS62133RGT_RGT0016C", "U1", 50, 76)
    add_footprint(board, "Coilcraft_XFL4020-222MEB", "L1", 60, 76)
    add_footprint(board, "Murata_GRM21_2012Metric", "C1", 43, 72)
    add_footprint(board, "Murata_GRM188_1608Metric", "C2", 46, 70)
    add_footprint(board, "Murata_GRM21_2012Metric", "C3", 66, 76)
    add_footprint(board, "Murata_GRM188_1608Metric", "C4", 50, 70)
    add_rect(board, 8, 64, 70, 92, pcbnew.Dwgs_User, 0.25)
    add_text(board, "BATTERY / 5V BUCK — PLACE/AUDIT BEFORE ROUTING", 39, 94,
             pcbnew.Dwgs_User, 1.2)

    # E220 is rotated so its documented SMA side faces the lower carrier edge.
    # The module template carries the official 21x36, pin-row and fixed-hole
    # guides; its 5-mm Dwgs.User perimeter is an explicitly conservative guide.
    add_footprint(board, "E220_T22D_Socket_400_900", "J3", 36, 41, 180)
    add_text(board, "E220 SMA SIDE TO BOARD EDGE — KEEP TOOL / ANTENNA ACCESS", 25, 55,
             pcbnew.Dwgs_User, 1.2)

    # OLED mounting Y and hole diameter are still unresolved.  Place only its
    # envelope/template here; do not assert a final carrier-socket registration.
    add_footprint(board, "OLED_0p96_4pin_MechanicalTemplate_PENDING_DATUM",
                  "MECH_OLED", 72, 60)
    add_text(board, "OLED ENVELOPE ONLY — HEADER-Y / HOLE DIA PENDING", 85, 94,
             pcbnew.Dwgs_User, 1.2)

    # The DevKit template contains its verified 2x1x15 rows and a deliberately
    # conservative 28x51 body/antenna guide.  Its antenna end is at the upper
    # carrier edge; access guides prohibit placement/routing in that region.
    add_footprint(board, "ESP32_DevKit_30pin_Socket_2x15_MechanicalTemplate",
                  "MECH_ESP32", 112, 55)
    add_rect(board, 104, 88, 148, 100, pcbnew.Dwgs_User, 0.25)
    add_text(board, "ESP32 ANTENNA EDGE PLACEHOLDER — NO ROUTING / COMPONENTS", 126, 97,
             pcbnew.Dwgs_User, 1.0)
    add_text(board, "ESP32 USB-C END: DIRECT EXTERNAL ACCESS REQUIRED", 126, 43,
             pcbnew.Dwgs_User, 1.0)

    # Explicit test-point planning area; no test-point land patterns are chosen.
    add_rect(board, 72, 44, 99, 54, pcbnew.Dwgs_User, 0.25)
    add_text(board, "RESERVE PROTOTYPE TP ACCESS", 85.5, 49, pcbnew.Dwgs_User, 1.0)

    pcbnew.SaveBoard(str(OUTPUT), board)


if __name__ == "__main__":
    main()
