#!/usr/bin/env python3
"""Generate the Stage 8 synchronized, unrouted Rev.1 placement PCB.

This is deliberately a placement-only deliverable.  It creates the approved
carrier-side footprints and their schematic net identities, but never creates
tracks, vias, copper zones, Gerbers, a release outline, or a manufacturing
BOM.  All locations are reproducible and documented in the Stage 8 review.
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
             layer: int = pcbnew.Dwgs_User, size: float = 1.2) -> None:
    graphic = pcbnew.PCB_TEXT(board)
    graphic.SetText(message)
    graphic.SetPosition(v(x, y))
    graphic.SetLayer(layer)
    graphic.SetTextSize(v(size, size))
    graphic.SetTextThickness(pcbnew.FromMM(0.20))
    board.Add(graphic)


def add_footprint(board: pcbnew.BOARD, source_name: str, reference: str,
                  value: str, x: float, y: float, rotation: float = 0.0,
                  path: str | None = None) -> pcbnew.FOOTPRINT:
    footprint = pcbnew.FootprintLoad(str(LIBRARY), source_name)
    if footprint is None:
        raise RuntimeError(f"Cannot load Carrier:{source_name}")
    footprint.SetReference(reference)
    footprint.SetValue(value)
    footprint.SetPosition(v(x, y))
    footprint.SetOrientationDegrees(rotation)
    if path:
        footprint.SetPath(path)
    # KiCad 10's Python bindings do not expose a stable custom-property writer
    # for FOOTPRINT.  The source and status are therefore embedded in the
    # reproducible generator and footprint descriptions rather than written as
    # ad-hoc board fields.
    board.Add(footprint)
    return footprint


def main() -> None:
    board = pcbnew.BOARD()
    board.SetFileName(str(OUTPUT))
    title = board.GetTitleBlock()
    title.SetTitle("ESP32 + E220 carrier — Stage 8 functional placement")
    title.SetComment(0, "UNROUTED / NOT FOR PRODUCTION")
    title.SetComment(1, "145 x 90 mm preferred comfortable preliminary outline")
    title.SetComment(2, "All active carrier components instantiated; R10/R11 DNP/no-footprint")
    title.SetComment(3, "Approved electrical baseline remains schematic-controlled")

    # This is deliberately a *proposed* comfortable outline, not the prior
    # 160 x 100 study canvas and not a board-release drawing.
    add_rect(board, 0, 0, 145, 90, pcbnew.Edge_Cuts, 0.30)
    add_text(board, "STAGE 8 — FUNCTIONAL PLACEMENT ONLY / NO ROUTING", 65, 3.5,
             pcbnew.Dwgs_User, 1.6)
    add_text(board, "PREFERRED COMFORTABLE PRELIMINARY OUTLINE: 145 x 90 mm", 72.5, 6.5,
             pcbnew.Dwgs_User, 1.1)

    # Net identities mirror the approved schematic.  KiCad 10 CLI has no
    # update-from-schematic subcommand; creating these named nets/pad bindings
    # reproducibly makes the pending airwires and later schematic/PCB audit
    # explicit rather than retaining the previous netless mechanical study.
    net_names = [
        "GND", "BAT_PLUS", "BAT_FUSED", "BUCK_IN", "Q1_GATE", "BUCK_SW",
        "SS_TR", "5V_SYS", "DEVKIT_3V3", "E220_M0", "E220_M1", "E220_RXD",
        "E220_TXD", "E220_AUX", "OLED_SDA", "OLED_SCL", "WS2812_DATA_3V3",
        "WS2812_DIN",
    ]
    nets: dict[str, pcbnew.NETINFO_ITEM] = {}
    for name in net_names:
        net = pcbnew.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net

    def connect(fp: pcbnew.FOOTPRINT, assignments: dict[str, str]) -> None:
        for number, net_name in assignments.items():
            pad = fp.FindPadByNumber(number)
            if pad is None:
                raise RuntimeError(f"{fp.GetReference()}: missing pad {number}")
            pad.SetNet(nets[net_name])

    # POWER CELL: the compact placement follows the TI topology direction.
    # It is intentionally separated from the radio and ESP antenna-edge regions.
    j4 = add_footprint(board, "JST_B2B-XH-A_1x02_P2.50mm_THT", "J4", "B2B-XH-A", 35, 76)
    f1 = add_footprint(board, "Littelfuse_1812L200_16_4532Metric", "F1", "1812L200/16", 45, 76)
    d3 = add_footprint(board, "Littelfuse_SMBJ10CA_DO214AA", "D3", "SMBJ10CA", 54, 76)
    q1 = add_footprint(board, "Diodes_DMP3130LQ-7_SOT23", "Q1", "DMP3130LQ-7", 63, 76)
    q1.Reference().SetLayer(pcbnew.F_Fab)
    # TPS62133RGT at 0 degrees is intentional and follows the *actual* RGT
    # pad map: SW1/2/3 are the left-side pads 1/2/3, while AVIN/PVIN are the
    # right-side pads 10/11/12.  Keeping this orientation prevents the old
    # crossed power-cell placement caused by treating the package as symmetric.
    u1 = add_footprint(board, "TI_TPS62133RGT_RGT0016C", "U1", "TPS62133RGT", 72, 72)
    # Input ceramics are on the AVIN/PVIN side.  Their BUCK_IN terminals face
    # U1: C1.1=(74.600,69.500), nearest PVIN=(73.400,71.250), 2.122 mm;
    # C2.1=(74.675,72.600), AVIN=(73.400,72.250), 1.322 mm.
    c1 = add_footprint(board, "Murata_GRM21_2012Metric", "C1", "GRM21BR61E106KA73", 75.6, 69.5)
    c2 = add_footprint(board, "Murata_GRM188_1608Metric", "C2", "GRM188R71C104KA01D", 75.4, 72.6)
    c2.Reference().SetLayer(pcbnew.F_Fab)
    c4 = add_footprint(board, "Murata_GRM188_1608Metric", "C4", "GRM1885C1H332JA01D", 73.4, 76.0, 90)
    # L1 is rotated 180 degrees: its marked pad 1 (BUCK_SW) is closest to the
    # real SW pad side, while pad 2 points to C3/5V_SYS.  L1.1=(67.975,71.750)
    # is 2.625 mm from SW2=(70.600,71.750); L1.2=(64.625,71.750) to
    # C3.1=(63.200,71.750) is 1.425 mm.  C3 ground gets a local short return
    # to the PGND/EP plane during routing; no route is created in this stage.
    l1 = add_footprint(board, "Coilcraft_XFL4020-222MEB", "L1", "XFL4020-222MEB", 66.3, 71.75, 180)
    c3 = add_footprint(board, "Murata_GRM21_2012Metric", "C3", "GRM21BR61A226ME44", 62.2, 71.75, 180)
    # Keep the non-switching reverse-polarity gate divider out of both the
    # SW/L1 courtyard and the high-current power loop.
    r1 = add_footprint(board, "Resistor_0603_1608Metric", "R1", "100k 1%", 58.5, 67, 90)
    r2 = add_footprint(board, "Resistor_0603_1608Metric", "R2", "1M 1%", 62.5, 67, 90)
    add_rect(board, 30, 62, 94, 84, pcbnew.Dwgs_User, 0.25)
    add_text(board, "COMPACT BUCK POWER CELL: J4→F1→D3/Q1→CIN/U1→L1→COUT", 62, 86.5,
             pcbnew.Dwgs_User, 0.95)
    add_text(board, "ACTUAL PAD-SIDE CHECK: PVIN→C1 2.12 mm; AVIN→C2 1.32 mm; SW→L1 2.63 mm; L1→COUT 1.43 mm", 62, 84.8,
             pcbnew.Dwgs_User, 0.70)
    add_text(board, "U1 EP=GND. THERMAL VIAS / SW-COPPER POLICY: LAYOUT REVIEW REQUIRED", 62, 88.2,
             pcbnew.Dwgs_User, 0.80)

    # Removable radio: SMA side faces the left edge.  The footprint itself
    # contains the common official 400/900 coordinates and guide-only holes.
    j3 = add_footprint(board, "E220_T22D_Socket_400_900", "J3",
                        "E220-400T22D / E220-900T22D SOCKET", 5, 52)
    # J3.6 VCC=(20.580,53.500) and J3.7 GND=(23.120,53.500).  Put the 100-nF
    # capacitor immediately on the pin-row side of the removable module, not
    # underneath its 21x36-mm body: C6.1=(20.580,49.750), 3.750 mm to VCC.
    # C5 provides the same local bulk function without entering the body
    # envelope: C5.1=(23.275,48.000), 6.125 mm to VCC.
    c5 = add_footprint(board, "Murata_GRM188_1608Metric", "C5", "GRM188R61A106MAAL", 24.0, 48.0)
    c6 = add_footprint(board, "Murata_GRM188_1608Metric", "C6", "GRM188R71C104KA01D", 21.305, 49.75)
    c5.Reference().SetLayer(pcbnew.F_Fab)
    c6.Reference().SetLayer(pcbnew.F_Fab)
    r8 = add_footprint(board, "Resistor_0603_1608Metric", "R8", "10k 1%", 30, 58, 90)
    r9 = add_footprint(board, "Resistor_0603_1608Metric", "R9", "10k 1%", 33, 58, 90)
    add_rect(board, 0, 47, 41, 89, pcbnew.Dwgs_User, 0.20)
    add_text(board, "E220 SMA / ANTENNA ACCESS TO BOTTOM EDGE — NO POWER CELL", 20, 45, pcbnew.Dwgs_User, 0.90)

    # OLED socket is real and electrically connected.  Its module body/mount
    # guide remains a deliberately generous 36 x 36-mm reserve because OLED-A
    # and OLED-B are not yet known; this cannot force a power/RF relocation.
    j5 = add_footprint(board, "Samtec_SSW_1x04_P2.54mm_THT", "J5",
                        "SSW-104-02-G-S", 63, 20)
    add_rect(board, 46, 9, 82, 45, pcbnew.Dwgs_User, 0.25)
    add_rect(board, 51, 14, 77, 40, pcbnew.F_Fab, 0.10)
    add_text(board, "OLED 26x26 ENVELOPE + EXTRA ADJUSTMENT RESERVE", 64, 47, pcbnew.Dwgs_User, 0.80)
    add_text(board, "KNOWN: MOUNT X=21.740 Y=22.000; OLED-A/B PENDING", 64, 48.5, pcbnew.Dwgs_User, 0.75)

    # Socketed DevKit.  The two electrical headers are actual footprints, with
    # their user-verified 25.400-mm row spacing; body/antenna is a conservative
    # guide rather than an unverified clone-specific tight datum.
    j1 = add_footprint(board, "Samtec_SSW_1x15_P2.54mm_THT", "J1",
                        "SSW-115-02-G-S DEVKIT LEFT", 111, 14)
    j2 = add_footprint(board, "Samtec_SSW_1x15_P2.54mm_THT", "J2",
                        "SSW-115-02-G-S DEVKIT RIGHT", 136.4, 14)
    add_rect(board, 109.7, 6.3, 137.7, 57.3, pcbnew.F_Fab, 0.10)
    add_rect(board, 104.7, 1.3, 142.7, 62.3, pcbnew.Dwgs_User, 0.25)
    add_rect(board, 104.7, 52, 142.7, 90, pcbnew.Dwgs_User, 0.20)
    add_text(board, "ESP32 DEVKIT 28x51 USER-MEASURED ENVELOPE — REMOVABLE", 123.7, 64, pcbnew.Dwgs_User, 0.80)
    add_text(board, "ANTENNA-EDGE PLACEHOLDER: NO ROUTING / COMPONENTS", 123.7, 66, pcbnew.Dwgs_User, 0.80)
    add_text(board, "USB-C ACCESS CORRIDOR — KEEP DIRECTLY ACCESSIBLE", 123.7, 68, pcbnew.Dwgs_User, 0.80)

    # Status indicator, outside the RF envelopes and near an observable edge.
    # All status parts remain left of the DevKit antenna placeholder beginning
    # at X=104.700 mm.  D2 body ends at X=99.000 mm, leaving 5.700 mm.
    u3 = add_footprint(board, "TI_SN74AHCT1G125DBVR_SOT23-5", "U3", "SN74AHCT1G125DBVR", 89.0, 54)
    u3.Reference().SetLayer(pcbnew.F_Fab)
    c7 = add_footprint(board, "Murata_GRM188_1608Metric", "C7", "GRM188R71C104KA01D", 85.5, 54, 90)
    d2 = add_footprint(board, "WorldSemi_WS2812B-V5_PLACEMENT_CANDIDATE_NOT_RELEASED", "D2", "WS2812B-V5", 96.5, 54)
    add_text(board, "D2 LAND PATTERN = PCB RELEASE BLOCKER; PLACEMENT ONLY", 93, 60.5, pcbnew.Dwgs_User, 0.75)

    # Prototype test access is deliberately clear of module body envelopes.
    tps = {}
    for ref, net, x, y in [
        # Entire test-point bank is left of the DevKit antenna placeholder;
        # TP10 centre is X=93.000 mm, so even its 1.8-mm courtyard is clear.
        ("TP1", "BAT_PLUS", 48, 87), ("TP2", "GND", 53, 87),
        ("TP3", "BUCK_IN", 58, 87), ("TP4", "5V_SYS", 63, 87),
        ("TP5", "5V_SYS", 68, 87), ("TP6", "E220_M0", 73, 87),
        ("TP7", "E220_M1", 78, 87), ("TP8", "E220_AUX", 83, 87),
        ("TP9", "E220_RXD", 88, 87), ("TP10", "E220_TXD", 93, 87),
    ]:
        tps[ref] = add_footprint(board, "TestPoint_THT_1p0mm_PROTOTYPE", ref, net, x, y)
    add_text(board, "PROTOTYPE TEST-POINT BANK — OUTSIDE DEVKIT ANTENNA PLACEHOLDER", 70.5, 89.1, pcbnew.Dwgs_User, 0.68)

    # Exact net/pad mapping, intentionally kept beside placement data for a
    # reproducible schematic↔PCB audit.
    connect(j4, {"1": "BAT_PLUS", "2": "GND"})
    connect(f1, {"1": "BAT_PLUS", "2": "BAT_FUSED"})
    connect(d3, {"1": "BAT_FUSED", "2": "GND"})
    connect(q1, {"1": "Q1_GATE", "2": "BUCK_IN", "3": "BAT_FUSED"})
    connect(r1, {"1": "Q1_GATE", "2": "GND"})
    connect(r2, {"1": "BUCK_IN", "2": "Q1_GATE"})
    connect(u1, {"1": "BUCK_SW", "2": "BUCK_SW", "3": "BUCK_SW", "5": "GND", "6": "GND",
                 "7": "5V_SYS", "8": "GND", "9": "SS_TR", "10": "BUCK_IN", "11": "BUCK_IN",
                 "12": "BUCK_IN", "13": "BUCK_IN", "14": "5V_SYS", "15": "GND", "16": "GND", "EP": "GND"})
    connect(l1, {"1": "BUCK_SW", "2": "5V_SYS"})
    connect(c1, {"1": "BUCK_IN", "2": "GND"})
    connect(c2, {"1": "BUCK_IN", "2": "GND"})
    connect(c3, {"1": "5V_SYS", "2": "GND"})
    connect(c4, {"1": "SS_TR", "2": "GND"})
    connect(j1, {"1": "5V_SYS", "2": "GND", "6": "E220_AUX", "7": "E220_M1", "8": "E220_M0"})
    connect(j2, {"1": "DEVKIT_3V3", "2": "GND", "5": "WS2812_DATA_3V3", "6": "E220_TXD", "7": "E220_RXD", "11": "OLED_SDA", "14": "OLED_SCL"})
    connect(j3, {"1": "E220_M0", "2": "E220_M1", "3": "E220_RXD", "4": "E220_TXD", "5": "E220_AUX", "6": "5V_SYS", "7": "GND"})
    connect(c5, {"1": "5V_SYS", "2": "GND"})
    connect(c6, {"1": "5V_SYS", "2": "GND"})
    connect(r8, {"1": "E220_M0", "2": "GND"})
    connect(r9, {"1": "E220_M1", "2": "GND"})
    connect(j5, {"1": "GND", "2": "DEVKIT_3V3", "3": "OLED_SCL", "4": "OLED_SDA"})
    connect(u3, {"1": "GND", "2": "WS2812_DATA_3V3", "3": "GND", "4": "WS2812_DIN", "5": "5V_SYS"})
    connect(c7, {"1": "5V_SYS", "2": "GND"})
    connect(d2, {"1": "5V_SYS", "3": "GND", "4": "WS2812_DIN"})
    for ref, net in [("TP1", "BAT_PLUS"), ("TP2", "GND"), ("TP3", "BUCK_IN"), ("TP4", "5V_SYS"),
                     ("TP5", "5V_SYS"), ("TP6", "E220_M0"), ("TP7", "E220_M1"), ("TP8", "E220_AUX"),
                     ("TP9", "E220_RXD"), ("TP10", "E220_TXD")]:
        connect(tps[ref], {"1": net})

    board.BuildListOfNets()
    pcbnew.SaveBoard(str(OUTPUT), board)


if __name__ == "__main__":
    main()
