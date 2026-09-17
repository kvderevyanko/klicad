#!/usr/bin/env python3
"""Generate Stage 7 interface/mechanical KiCad footprints reproducibly.

No PCB is generated here.  Dimensions and release limits are documented in
docs/footprint-mechanical-review.md; this script deliberately preserves TBD
mechanical data as guide graphics rather than inventing pads or holes.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parent
LIBRARY = ROOT / "esp32-e220.pretty"
FP_TABLE = ROOT / "fp-lib-table"


def text(kind: str, value: str, x: float, y: float, layer: str, size: float = 1.0) -> str:
    return (
        f'  (fp_text {kind} "{value}" (at {x:.3f} {y:.3f}) (layer "{layer}")\n'
        f'    (effects (font (size {size:.3f} {size:.3f}) (thickness 0.15)))\n'
        "  )\n"
    )


def line(x1: float, y1: float, x2: float, y2: float, layer: str, width: float) -> str:
    return (
        f'  (fp_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) '
        f'(stroke (width {width:.3f}) (type default)) (fill none) (layer "{layer}"))\n'
    )


def rect(x1: float, y1: float, x2: float, y2: float, layer: str, width: float) -> str:
    return "".join((
        line(x1, y1, x2, y1, layer, width),
        line(x2, y1, x2, y2, layer, width),
        line(x2, y2, x1, y2, layer, width),
        line(x1, y2, x1, y1, layer, width),
    ))


def circle(x: float, y: float, radius: float, layer: str, width: float) -> str:
    return (
        f'  (fp_circle (center {x:.3f} {y:.3f}) (end {x + radius:.3f} {y:.3f}) '
        f'(stroke (width {width:.3f}) (type dash)) (fill none) (layer "{layer}"))\n'
    )


def pad(number: str, x: float, y: float, first: bool = False) -> str:
    shape = "rect" if first else "oval"
    return (
        f'  (pad "{number}" thru_hole {shape} (at {x:.3f} {y:.3f}) '
        '(size 1.700 1.700) (drill 1.040) (layers "*.Cu" "*.Mask"))\n'
    )


def smd_pad(number: str, x: float, y: float, sx: float, sy: float,
            shape: str = "roundrect") -> str:
    """SMD land.  Dimensions must be traceable in the mechanical review."""
    extra = ' (roundrect_rratio 0.20)' if shape == "roundrect" else ""
    return (
        f'  (pad "{number}" smd {shape} (at {x:.3f} {y:.3f}) '
        f'(size {sx:.3f} {sy:.3f}) (layers "F.Cu" "F.Paste" "F.Mask"){extra})\n'
    )


def passive(name: str, description: str, body_x: float, body_y: float,
            pad_x: float, pad_y: float, pad_pitch: float) -> str:
    """Two-terminal project copy; package size comes from the named MPN."""
    return "".join((
        f'(footprint "{name}" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        f'  (descr "{description}")\n',
        '  (attr smd)\n',
        text("reference", "REF**", 0, -body_y / 2 - 1.0, "F.SilkS"),
        text("value", name, 0, body_y / 2 + 1.0, "F.Fab", 0.75),
        rect(-body_x / 2, -body_y / 2, body_x / 2, body_y / 2, "F.Fab", 0.10),
        rect(-body_x / 2 - 0.5, -body_y / 2 - 0.5, body_x / 2 + 0.5, body_y / 2 + 0.5, "F.CrtYd", 0.05),
        smd_pad("1", -pad_pitch / 2, 0, pad_x, pad_y),
        smd_pad("2", pad_pitch / 2, 0, pad_x, pad_y),
        ")\n",
    ))


def murata_grm188_standard() -> str:
    """GRM18 +/-0.10-mm group manufacturer Table 2 land geometry."""
    return passive(
        "Murata_GRM188_1608Metric",
        "Murata GRM18 1608 metric C2/C4/C6/C7/C8. Manufacturer Table 2 reflow lands: a=0.75, b=0.70, c=0.70 mm on 1.45-mm centres.",
        1.60, 0.80, 0.70, 0.70, 1.45,
    )


def murata_grm21_standard() -> str:
    """GRM21 +/-0.15-mm group manufacturer Table 2 land geometry."""
    name = "Murata_GRM21_2012Metric"
    description = (
        "Murata GRM21 2012 metric C1/C9/C10. Manufacturer Table 2 reflow lands: "
        "a=0.80, b=1.20, c=1.30 mm on 2.00-mm centres."
    )
    return "".join((
        f'(footprint "{name}" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        f'  (descr "{description}")\n',
        '  (attr smd)\n',
        text("reference", "REF**", 0, -1.625, "F.SilkS"),
        text("value", name, 0, 1.625, "F.Fab", 0.75),
        rect(-1.000, -0.625, 1.000, 0.625, "F.Fab", 0.10),
        rect(-1.650, -1.125, 1.650, 1.125, "F.CrtYd", 0.05),
        smd_pad("1", -1.000, 0, 1.200, 1.300),
        smd_pad("2", 1.000, 0, 1.200, 1.300),
        ")\n",
    ))


def murata_grm188_c5() -> str:
    """GRM188R61A106MAAL +/-0.15-mm manufacturer Table 2 lands."""
    return passive(
        "Murata_GRM188R61A106MAAL_1608Metric",
        "Murata GRM188R61A106MAAL 1608 metric C5. Manufacturer Table 2 reflow lands: a=0.70, b=0.75, c=0.90 mm on 1.45-mm centres.",
        1.60, 0.80, 0.75, 0.90, 1.45,
    )


def yageo_rc0603() -> str:
    """Yageo RC 0603/1608 Mounting V10 Table 1 reflow lands."""
    return passive(
        "Resistor_0603_1608Metric",
        "0603 (1608 metric) resistor footprint used by R1/R2/R3/R4/R8/R9/R10/R11. Yageo RC Mounting V10 Table 1 reflow lands: A=2.60, B=0.80, C=0.90, D=0.80 mm on 1.70-mm centres.",
        1.60, 0.80, 0.90, 0.80, 1.70,
    )


def murata_grm21_c3() -> str:
    """GRM21BR61A226ME44 +/-0.20-mm manufacturer Table 2 lands."""
    return passive(
        "Murata_GRM21BR61A226ME44_2012Metric",
        "Murata GRM21BR61A226ME44 2012 metric C3. Manufacturer Table 2 reflow lands: a=1.30, b=0.70, c=1.30 mm on 2.00-mm centres.",
        2.00, 1.25, 0.70, 1.30, 2.00,
    )


def tps62133() -> str:
    """TI RGT0016C example land pattern, not a copied generic VQFN."""
    items = [
        '(footprint "TI_TPS62133RGT_RGT0016C" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "TI TPS62133RGT, RGT0016C VQFN-16 3x3 mm. TI datasheet example layout: 16x 0.60x0.24 lands, 1.68x1.68 exposed metal; optional 0.20 vias at 0.58 grid are layout-level.")\n',
        '  (attr smd)\n',
        text("reference", "U", 0, -2.85, "F.SilkS"),
        text("value", "TPS62133RGT", 0, 2.35, "F.Fab"),
        rect(-1.5, -1.5, 1.5, 1.5, "F.Fab", 0.10),
        rect(-2.0, -2.0, 2.0, 2.0, "F.CrtYd", 0.05),
        line(-1.5, -2.05, -0.75, -2.05, "F.SilkS", 0.30),
    ]
    # TI top-view numbering: 1..4 left, 5..8 bottom, 9..12 right, 13..16 top.
    # TI's RGT0016C example board drawing gives 0.600 mm in the radial
    # direction and 0.240 mm tangentially.  Its 2.800-mm reference dimension
    # places the opposite peripheral-pad centrelines at +/-1.400 mm; treating
    # it as an outside-pad extent (the prior +/-1.100-mm interpretation)
    # falsely overlaps the official 1.680-mm EP.
    for number, y in enumerate((-0.75, -0.25, 0.25, 0.75), start=1):
        items.append(smd_pad(str(number), -1.40, y, 0.60, 0.24, "rect"))
    for number, x in enumerate((-0.75, -0.25, 0.25, 0.75), start=5):
        items.append(smd_pad(str(number), x, 1.40, 0.24, 0.60, "rect"))
    for number, y in enumerate((0.75, 0.25, -0.25, -0.75), start=9):
        items.append(smd_pad(str(number), 1.40, y, 0.60, 0.24, "rect"))
    for number, x in enumerate((0.75, 0.25, -0.25, -0.75), start=13):
        items.append(smd_pad(str(number), x, -1.40, 0.24, 0.60, "rect"))
    # TI RGT0016C official stencil example: 1.55-mm EP aperture, about 85%
    # of the 1.68-mm exposed metal.  Thermal vias remain layout-level.
    items.append('  (pad "EP" smd rect (at 0 0) (size 1.680 1.680) (layers "F.Cu" "F.Mask"))\n')
    items.append('  (pad "EP" smd rect (at 0 0) (size 1.550 1.550) (layers "F.Paste"))\n')
    items.append(")\n")
    return "".join(items)


def xfl4020() -> str:
    return "".join((
        '(footprint "Coilcraft_XFL4020-222MEB" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "Coilcraft XFL4020-222MEB. Manufacturer recommended land pattern: two 0.98x3.40 mm lands on 3.35-mm centres; dashed mark identifies pin 1/start lead.")\n',
        '  (attr smd)\n', text("reference", "L", 0, -2.75, "F.SilkS"), text("value", "XFL4020-222MEB", 0, 2.75, "F.Fab"),
        rect(-2.0, -2.0, 2.0, 2.0, "F.Fab", 0.10), rect(-2.55, -2.25, 2.55, 2.25, "F.CrtYd", 0.05),
        line(-2.0, -2.0, -1.25, -2.0, "F.SilkS", 0.30),
        smd_pad("1", -1.675, 0, 0.980, 3.400, "rect"), smd_pad("2", 1.675, 0, 0.980, 3.400, "rect"), ")\n",
    ))


def dmp3130() -> str:
    return "".join((
        '(footprint "Diodes_DMP3130LQ-7_SOT23" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "Diodes DMP3130LQ-7 SOT23, DS38728 suggested pad layout: 0.80 x 0.90 mm lands; X1=1.35 mm is centreline to outer land edge, giving 0.95-mm lower-pad centre offsets.")\n',
        '  (attr smd)\n', text("reference", "Q", 0, -2.35, "F.SilkS"), text("value", "DMP3130LQ-7", 0, 2.35, "F.Fab"),
        rect(-0.65, -1.45, 0.65, 1.45, "F.Fab", 0.10), rect(-1.60, -1.70, 1.60, 1.70, "F.CrtYd", 0.05),
        line(-1.50, -1.45, -0.75, -1.45, "F.SilkS", 0.30),
        smd_pad("1", -0.95, 1.00, 0.80, 0.90, "rect"), smd_pad("2", 0.95, 1.00, 0.80, 0.90, "rect"), smd_pad("3", 0, -1.00, 0.80, 0.90, "rect"), ")\n",
    ))


def sn74ahct1g125() -> str:
    """TI DBV0005A SOT-23-5 manufacturer land pattern.

    Source: TI SN74AHCT1G125 data sheet SCLS378P, Rev. P, and package drawing
    DBV0005A 4214839/K, August 2024.  The drawing dimensions the opposing
    pad-row centrelines at 2.60 mm and the three-lead-side centres at
    2 x 0.95 mm.  Lands are 0.60 x 1.10 mm with R0.05 mm corners.
    """
    return "".join((
        '(footprint "TI_SN74AHCT1G125DBVR_SOT23-5" (version 20240108) (generator "u3-ti-dbv-correction")\n',
        '  (layer "F.Cu")\n',
        '  (descr "TI SN74AHCT1G125DBVR, DBV0005A SOT-23-5 released land pattern; TI drawing 4214839/K, 08/2024.")\n',
        '  (attr smd)\n', text("reference", "U", 0, -2.35, "F.SilkS"), text("value", "SN74AHCT1G125DBVR", 0, 2.35, "F.Fab", 0.75),
        line(-0.800, -1.450, 0.800, -1.450, "F.Fab", 0.100),
        line(0.800, -1.450, 0.800, 1.450, "F.Fab", 0.100),
        line(0.800, 1.450, -0.300, 1.450, "F.Fab", 0.100),
        line(-0.300, 1.450, -0.800, 0.950, "F.Fab", 0.100),
        line(-0.800, 0.950, -0.800, -1.450, "F.Fab", 0.100),
        rect(-1.800, -2.100, 1.800, 2.100, "F.CrtYd", 0.050),
        '  (fp_circle (center -1.550 1.750) (end -1.400 1.750) (stroke (width 0.150) (type default)) (fill none) (layer "F.SilkS"))\n',
        '  (pad "1" smd roundrect (at -0.950 1.300) (size 0.600 1.100) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.083333) (solder_mask_margin 0.050))\n',
        '  (pad "2" smd roundrect (at 0.000 1.300) (size 0.600 1.100) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.083333) (solder_mask_margin 0.050))\n',
        '  (pad "3" smd roundrect (at 0.950 1.300) (size 0.600 1.100) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.083333) (solder_mask_margin 0.050))\n',
        '  (pad "4" smd roundrect (at 0.950 -1.300) (size 0.600 1.100) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.083333) (solder_mask_margin 0.050))\n',
        '  (pad "5" smd roundrect (at -0.950 -1.300) (size 0.600 1.100) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.083333) (solder_mask_margin 0.050))\n',
        ')\n',
    ))


def tlv1117lv33_dcy_sot223() -> str:
    """TI TLV1117LV DCY land pattern, drawing 4210278/C.

    The drawing is included in the TLV1117LV Rev. C (SBVS160C) datasheet and
    defines copper, preferred NSMD mask treatment, and the 0.125-mm stencil
    example.  The footprint axes rotate the drawing 90 degrees.
    """
    return "".join((
        '(footprint "TI_TLV1117LV33DCYR_DCY_SOT223" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "TI TLV1117LV33DCYR DCY/SOT-223 manufacturer land pattern; TI TLV1117LV Rev. C drawing 4210278/C. Pin 2 includes lead and tab.")\n',
        '  (tags "TI TLV1117LV33DCYR DCY SOT-223 4210278C")\n',
        '  (attr smd)\n',
        text("reference", "U", 0, -4.5, "F.SilkS"),
        text("value", "TLV1117LV33DCYR", 0, 4.5, "F.Fab"),
        line(-4.10, -3.41, 1.91, -3.41, "F.SilkS", 0.12),
        line(-1.85, 3.41, 1.91, 3.41, "F.SilkS", 0.12),
        line(1.91, -3.41, 1.91, -2.15, "F.SilkS", 0.12),
        line(1.91, 3.41, 1.91, 2.15, "F.SilkS", 0.12),
        rect(-4.40, -3.60, 4.40, 3.60, "F.CrtYd", 0.05),
        line(-1.85, -2.35, -1.85, 3.35, "F.Fab", 0.10),
        line(-1.85, -2.35, -0.85, -3.35, "F.Fab", 0.10),
        line(-1.85, 3.35, 1.85, 3.35, "F.Fab", 0.10),
        line(-0.85, -3.35, 1.85, -3.35, "F.Fab", 0.10),
        line(1.85, -3.35, 1.85, 3.35, "F.Fab", 0.10),
        '  (fp_text user "${REFERENCE}" (at 0 0 90) (layer "F.Fab")\n'
        '    (effects (font (size 0.800 0.800) (thickness 0.120)))\n'
        '  )\n',
        '  (pad "1" smd rect (at -2.900 -2.300) (size 2.150 0.950) (layers "F.Cu" "F.Paste" "F.Mask") (solder_mask_margin 0.050))\n',
        '  (pad "2" smd rect (at -2.900 0.000) (size 2.150 0.950) (layers "F.Cu" "F.Paste" "F.Mask") (solder_mask_margin 0.050))\n',
        '  (pad "2" smd rect (at 2.900 0.000) (size 2.150 3.250) (layers "F.Cu" "F.Paste" "F.Mask") (solder_mask_margin 0.050))\n',
        '  (pad "3" smd rect (at -2.900 2.300) (size 2.150 0.950) (layers "F.Cu" "F.Paste" "F.Mask") (solder_mask_margin 0.050))\n',
        '  (model "${KICAD6_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-223.wrl"\n'
        '    (offset (xyz 0 0 0))\n'
        '    (scale (xyz 1 1 1))\n'
        '    (rotate (xyz 0 0 0))\n'
        '  )\n',
        ')\n',
    ))


def testpoint() -> str:
    return "".join((
        '(footprint "TestPoint_THT_1p0mm_PROTOTYPE" (version 20240108) (generator "stage8")\n',
        '  (layer "F.Cu")\n',
        '  (descr "Stage-8 prototype test point: 1.00-mm drill, 2.00-mm copper. Test-point MPN remains a procurement/DFM selection.")\n',
        '  (attr through_hole)\n', text("reference", "TP", 0, -2.0, "F.SilkS"), text("value", "TESTPOINT", 0, 2.0, "F.Fab", 0.70),
        circle(0, 0, 1.30, "F.SilkS", 0.20), circle(0, 0, 1.80, "F.CrtYd", 0.05),
        '  (pad "1" thru_hole circle (at 0 0) (size 2.000 2.000) (drill 1.000) (layers "*.Cu" "*.Mask"))\n',
        ')\n',
    ))


def jst_xh_b2b_xh_a() -> str:
    """JST B2B-XH-A: official 2.50-mm XH header geometry, project copy."""
    contents = [
        '(footprint "JST_B2B-XH-A_1x02_P2.50mm_THT" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "JST B2B-XH-A vertical XH 2-position. JST eXH drawing: 2.50-mm pitch, 1.00-mm drilled holes; mates XHP-2/SXH-001T-P0.6.")\n',
        '  (attr through_hole)\n',
        text("reference", "J", 1.25, -3.55, "F.SilkS"), text("value", "B2B-XH-A", 1.25, 4.6, "F.Fab"),
        rect(-2.45, -2.35, 4.95, 3.40, "F.Fab", 0.10),
        rect(-2.95, -2.85, 5.45, 3.90, "F.CrtYd", 0.05),
        line(-2.45, -2.35, -0.75, -2.35, "F.SilkS", 0.30),
        '  (pad "1" thru_hole rect (at 0 0) (size 1.700 2.000) (drill 1.000) (layers "*.Cu" "*.Mask"))\n',
        '  (pad "2" thru_hole oval (at 2.500 0) (size 1.700 2.000) (drill 1.000) (layers "*.Cu" "*.Mask"))\n',
        ')\n',
    ]
    return "".join(contents)


def smbj10ca() -> str:
    """Littelfuse SMBJ/DO-214AA manufacturer-recommended land pattern.

    Littelfuse SMBJ series drawing Rev. JC defines 2.160 x 2.260 mm lands,
    a 2.740-mm inner gap, and therefore a 4.900-mm centre pitch.  The F.Fab
    body uses the midpoint of the official package limits: 4.405 x 3.620 mm.
    SMBJ10CA is bidirectional, so neither land carries a polarity constraint.
    """
    return "".join((
        '(footprint "Littelfuse_SMBJ10CA_DO214AA" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "Littelfuse SMBJ10CA bidirectional TVS in DO-214AA/SMB. Manufacturer recommended solder lands: 2.160x2.260 mm, 2.740-mm inner gap, 4.900-mm centre pitch.")\n',
        '  (attr smd)\n',
        text("reference", "REF**", 0, -2.810, "F.SilkS"),
        text("value", "Littelfuse_SMBJ10CA_DO214AA", 0, 2.810, "F.Fab", 0.75),
        rect(-2.2025, -1.810, 2.2025, 1.810, "F.Fab", 0.10),
        rect(-3.800, -2.500, 3.800, 2.500, "F.CrtYd", 0.05),
        smd_pad("1", -2.450, 0, 2.160, 2.260),
        smd_pad("2", 2.450, 0, 2.160, 2.260),
        ")\n",
    ))


def fuse_1812() -> str:
    """Littelfuse 1812L manufacturer-recommended pad layout.

    The official 1812L Series drawing (Rev. GD, 06/10/24) specifies each
    land as F=1.78 mm by H=3.15 mm and G=3.45 mm between the inner land
    edges.  The resulting land-centre pitch is F+G=5.23 mm.  The F.Fab body
    uses the midpoint of the official A and B limits: 4.55 x 3.24 mm.
    """
    return "".join((
        '(footprint "Littelfuse_1812L200_16_4532Metric" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "Littelfuse 1812L200/16 PolySwitch. Official 1812L recommended pad layout: each land 1.78x3.15 mm, 3.45-mm inner gap, 5.23-mm centre pitch.")\n',
        '  (attr smd)\n',
        text("reference", "REF**", 0, -2.60, "F.SilkS"),
        text("value", "Littelfuse_1812L200_16_4532Metric", 0, 2.60, "F.Fab", 0.75),
        rect(-2.275, -1.620, 2.275, 1.620, "F.Fab", 0.10),
        # The manufacturer lands extend to local X +/-3.505 mm.  Preserve
        # the reviewed 0.045-mm copper containment and connector clearance.
        rect(-3.550, -2.120, 3.550, 2.120, "F.CrtYd", 0.05),
        smd_pad("1", -2.615, 0, 1.780, 3.150),
        smd_pad("2", 2.615, 0, 1.780, 3.150),
        ")\n",
    ))


def header(name: str, positions: int) -> str:
    last = (positions - 1) * 2.54
    contents = [
        f'(footprint "{name}" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "Samtec SSW through-hole socket. Official SSW-S layout: 2.54 mm pitch, 1.04 mm drill. 1.70 mm copper is a project annular-ring choice for the 0.64 mm square tail.")\n',
        '  (tags "Samtec SSW socket 2.54mm THT")\n',
        '  (attr through_hole)\n',
        text("reference", "REF**", 0, -2.5, "F.SilkS"),
        text("value", name, 0, last + 2.5, "F.Fab"),
        text("user", "${REFERENCE}", 0, last / 2, "F.Fab"),
        rect(-1.205, -1.270, 1.205, last + 1.270, "F.Fab", 0.10),
        rect(-1.350, -1.400, 1.350, last + 1.400, "F.SilkS", 0.12),
        rect(-1.850, -1.900, 1.850, last + 1.900, "F.CrtYd", 0.05),
        line(-1.350, -1.400, -0.350, -1.400, "F.SilkS", 0.35),
    ]
    contents.extend(pad(str(index + 1), 0, index * 2.54, index == 0) for index in range(positions))
    contents.append(")\n")
    return "".join(contents)


def samtec_tsw_102_07_g_s() -> str:
    """Samtec TSW-102-07-G-S manufacturer-recommended PCB geometry.

    Samtec drawing TSW-XXX-XX-X-X-XX-XXX defines the populated part as a
    two-position, single-row, 2.54-mm-pitch strip with 0.635-mm square posts.
    The official TSW recommended PCB layout specifies 1.02-mm finished holes.
    The 1.70-mm copper diameter is the reviewed project annular-ring choice.
    """
    name = "Samtec_TSW-102-07-G-S_1x02_P2.54mm_THT"
    return "".join((
        f'(footprint "{name}" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "Samtec TSW-102-07-G-S straight single-row header. Official TSW layout: 2.54-mm pitch, 1.02-mm finished holes for 0.635-mm square posts; 1.70-mm copper is the reviewed project annular-ring choice.")\n',
        '  (tags "Samtec TSW-102-07-G-S 2.54mm THT")\n',
        '  (attr through_hole)\n',
        text("reference", "JP", 0, -2.50, "F.SilkS"),
        text("value", name, 0, 5.04, "F.Fab", 0.75),
        line(-1.270, -0.635, -0.635, -1.270, "F.Fab", 0.10),
        line(-0.635, -1.270, 1.270, -1.270, "F.Fab", 0.10),
        line(1.270, -1.270, 1.270, 3.810, "F.Fab", 0.10),
        line(1.270, 3.810, -1.270, 3.810, "F.Fab", 0.10),
        line(-1.270, 3.810, -1.270, -0.635, "F.Fab", 0.10),
        rect(-1.350, -1.400, 1.350, 3.940, "F.SilkS", 0.12),
        line(-1.350, -1.400, -0.350, -1.400, "F.SilkS", 0.35),
        rect(-1.850, -1.900, 1.850, 4.440, "F.CrtYd", 0.05),
        text("user", "${REFERENCE}", 0, 1.270, "F.Fab"),
        '  (pad "1" thru_hole rect (at 0 0) (size 1.700 1.700) (drill 1.020) (layers "*.Cu" "*.Mask"))\n',
        '  (pad "2" thru_hole oval (at 0 2.540) (size 1.700 1.700) (drill 1.020) (layers "*.Cu" "*.Mask"))\n',
        ")\n",
    ))


def pin_header(name: str, positions: int) -> str:
    """Generic 2.54-mm PTH user header/solder-point footprint.

    J6 and J_RGB are DNP interfaces rather than factory-fitted Samtec sockets.
    The 1.00-mm drill and 1.70-mm copper are explicit project DFM choices for
    common repairable 2.54-mm square-post headers or direct wire soldering.
    """
    last = (positions - 1) * 2.54
    contents = [
        f'(footprint "{name}" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "Generic 2.54-mm vertical PTH header/solder points; 1.00-mm drill and 1.70-mm copper are project DFM choices. User-installed / PCBA DNP.")\n',
        '  (tags "2.54mm PTH header solder point DNP")\n',
        '  (attr through_hole)\n',
        text("reference", "J", 0, -2.50, "F.SilkS"),
        text("value", name, 0, last + 2.50, "F.Fab", 0.75),
        rect(-1.27, -1.27, 1.27, last + 1.27, "F.Fab", 0.10),
        rect(-1.50, -1.50, 1.50, last + 1.50, "F.SilkS", 0.12),
        rect(-1.85, -1.85, 1.85, last + 1.85, "F.CrtYd", 0.05),
        line(-1.50, -1.50, -0.35, -1.50, "F.SilkS", 0.35),
    ]
    for index in range(positions):
        shape = "rect" if index == 0 else "oval"
        contents.append(
            f'  (pad "{index + 1}" thru_hole {shape} (at 0 {index * 2.54:.3f}) '
            '(size 1.700 1.700) (drill 1.000) (layers "*.Cu" "*.Mask"))\n'
        )
    contents.append(")\n")
    return "".join(contents)


def esp32_template() -> str:
    # Only the rows are datum-verified.  The body is intentionally unregistered
    # to the headers.  Rev.1 permits it for *conservative preliminary placement*
    # only: no routing/copper shall occupy its body, USB-access or antenna-end
    # placeholder clearance until a final module-specific drawing is available.
    last = 14 * 2.54
    contents = [
        '(footprint "ESP32_DevKit_30pin_Socket_2x15_MechanicalTemplate" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "ESP32 DevKit 2x1x15 socket mechanical template. Only socket rows are verified; 28x51 body envelope is user-measured and not registered to header datum.")\n',
        '  (tags "ESP32 DevKit 30 pin mechanical template USER-MEASURED")\n',
        '  (attr through_hole)\n',
        text("reference", "MECH**", 12.7, -3.0, "F.SilkS"),
        text("value", "ESP32 DevKit 30-pin mechanical template", 12.7, last + 3.0, "F.Fab"),
        text("user", "USB-C END / PIN 1", 12.7, -1.6, "F.SilkS", 0.85),
        text("user", "ANTENNA END — CONSERVATIVE NO ROUTING / NO COMPONENTS", 12.7, last + 1.6, "F.Fab", 0.80),
        text("user", "BODY 28 x 51 USER-MEASURED — PRELIMINARY ENVELOPE ONLY", 12.7, last / 2, "Dwgs.User", 0.75),
        rect(-1.350, -1.400, 26.750, last + 1.400, "F.CrtYd", 0.05),
        line(-1.350, -1.400, -0.300, -1.400, "F.SilkS", 0.35),
        line(24.350, -1.400, 25.400, -1.400, "F.SilkS", 0.35),
    ]
    # Illustrative, explicitly unregistered body and a 5-mm preliminary clearance
    # guide: acceptable for Stage 7 mechanical planning, never a release datum.
    contents.append(rect(-1.300, -7.720, 26.700, 43.280, "Dwgs.User", 0.20))
    contents.append(rect(-6.300, -12.720, 31.700, 48.280, "Dwgs.User", 0.20))
    for index in range(15):
        y = index * 2.54
        contents.append(pad(f"L{index + 1}", 0, y, index == 0))
        contents.append(pad(f"R{index + 1}", 25.4, y, index == 0))
    contents.append(")\n")
    return "".join(contents)


def e220_socket() -> str:
    # EBYTE common 400/900T22D geometry uses the pin-row short edge as Y=0.
    # The official E220-T manual establishes the seven electrical pads and the
    # three *mechanical* fixing-hole sites.  They are intentionally guide-only:
    # this removable-module carrier must not turn the module's non-electrical
    # fixing holes into carrier contacts or NPTH without a mounting decision.
    contents = [
        '(footprint "E220_T22D_Socket_400_900" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "Carrier-side 1x7 Samtec SSW socket for common EBYTE E220-400T22D / E220-900T22D geometry; not EBYTE solder-pad pattern")\n',
        '  (tags "EBYTE E220 400T22D 900T22D socket 2.54mm")\n',
        '  (attr through_hole)\n',
        text("reference", "J_E220", 10.5, -3.0, "F.SilkS"),
        text("value", "E220-400T22D / E220-900T22D SOCKET", 10.5, 39.0, "F.Fab", 0.85),
        text("user", "PIN 1 / M0", 2.88, -1.1, "F.SilkS", 0.80),
        text("user", "SMA / ANTENNA SIDE — KEEP ACCESS CLEAR", 10.5, 34.8, "F.Fab", 0.80),
        text("user", "400 MHz and 900 MHz antennas are NOT interchangeable", 10.5, 37.3, "Dwgs.User", 0.70),
        text("user", "5-mm PRELIMINARY MODULE CLEARANCE — NO ROUTING", 10.5, 40.4, "Dwgs.User", 0.62),
        text("user", "FIXING-HOLE GUIDE ONLY: 8/9/10; NO CARRIER CONTACT OR NPTH", 10.5, 39.0, "Dwgs.User", 0.62),
        rect(0, 0, 21.0, 36.0, "F.Fab", 0.10),
        rect(-1.0, -1.0, 22.0, 37.0, "F.CrtYd", 0.05),
        rect(-0.3, -0.3, 21.3, 36.3, "F.SilkS", 0.12),
        rect(-5.0, -5.0, 26.0, 41.0, "Dwgs.User", 0.20),
        line(1.88, 0.2, 2.88, 0.2, "F.SilkS", 0.35),
    ]
    for index in range(7):
        contents.append(pad(str(index + 1), 2.88 + index * 2.54, 1.50, index == 0))
    # Manual front-view coordinates, transformed to this footprint datum:
    # holes 10/9/8 at X=3.50/6.04/8.58 mm and 3.00 mm from the SMA-side edge,
    # hence Y=36.00-3.00=33.00 mm.  They are visibility/clearance guides only.
    for number, x in (("10", 3.50), ("9", 6.04), ("8", 8.58)):
        contents.append(circle(x, 33.00, 0.75, "Dwgs.User", 0.15))
        contents.append(text("user", number, x, 33.00, "Dwgs.User", 0.60))
    contents.append(")\n")
    return "".join(contents)


def oled_template() -> str:
    # The user drawing supplies the body, mounting-hole spacing and *horizontal*
    # GND-pin datum.  It does not provide header-row Y or finished hole diameter;
    # do not turn this template into a placement datum or an NPTH pattern.
    contents = [
        '(footprint "OLED_0p96_4pin_MechanicalTemplate_PENDING_DATUM" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "0.96in SSD1306 I2C OLED template. Body 26x26; mount spacing 21.740x22.000; GND header X=9.190 mm from left edge. Header Y and hole diameter TBD.")\n',
        '  (tags "OLED SSD1306 0.96 4pin mechanical template PENDING DATUM")\n',
        '  (attr through_hole)\n',
        text("reference", "MECH**", 13.0, -3.0, "F.SilkS"),
        text("value", "OLED 0.96in mechanical template — NOT PRODUCTION APPROVED", 13.0, 29.0, "F.Fab", 0.80),
        text("user", "BODY 26.000 x 26.000 USER/SUPPLIER DRAWING", 13.0, 13.0, "Dwgs.User", 0.75),
        text("user", "MOUNT-SPACING GUIDE (unregistered): X=21.740, Y=22.000; HOLE DIA TBD", 13.0, 15.0, "Dwgs.User", 0.70),
        text("user", "HEADER X: GND=9.190, VCC=11.730, SCL=14.270, SDA=16.810; Y TBD", 13.0, 17.0, "Dwgs.User", 0.60),
        text("user", "DISPLAY / FLEX / NOTCH: TBD", 13.0, 18.5, "Dwgs.User", 0.70),
        text("user", "5-mm PRELIMINARY MODULE CLEARANCE — NO ROUTING", 13.0, 20.0, "Dwgs.User", 0.62),
        rect(0, 0, 26.0, 26.0, "F.Fab", 0.10),
        rect(-1.0, -1.0, 27.0, 27.0, "F.CrtYd", 0.05),
        rect(-5.0, -5.0, 31.0, 31.0, "Dwgs.User", 0.20),
    ]
    # The source supplies only the spacing, not either hole-to-board-edge datum.
    # These are therefore coordinates in an independent *hole-spacing guide*,
    # not locations on the 26 x 26 mm body outline above.
    for x in (35.0, 56.74):
        for y in (0.0, 22.0):
            contents.append(circle(x, y, 1.0, "Dwgs.User", 0.15))
    # This four-pad row is an interface guide only.  Its body registration is
    # incomplete until the header Y datum is known.  The *actual* carrier
    # socket is the separate Samtec SSW-104 footprint.
    contents.extend((
        text("user", "INTERFACE ONLY: 1 GND  2 VCC  3 SCL  4 SDA", 3.81, -1.4, "F.Fab", 0.80),
        pad("1", 0, 0, True),
        pad("2", 2.54, 0),
        pad("3", 5.08, 0),
        pad("4", 7.62, 0),
        ")\n",
    ))
    return "".join(contents)


def mounting_hole_m3_npth() -> str:
    """Rev.1 enclosure mounting hole: 3.20-mm NPTH, no copper pad.

    The separate layout-level 8.00-mm F.Cu/B.Cu keepout is intentionally not
    embedded in the footprint so it is machine-visible as a named rule area.
    """
    return "".join((
        '(footprint "MountingHole_M3_NPTH_REV1" (version 20240108) (generator "rev1-final-mechanical-serviceability")\n',
        '  (layer "F.Cu")\n',
        '  (descr "Rev.1 mechanical mounting hole: 3.20 mm NPTH, M3, 8.00 mm screw-head courtyard")\n',
        '  (attr through_hole exclude_from_pos_files exclude_from_bom)\n',
        text("reference", "H", 0, -5.000, "F.SilkS"),
        '  (fp_text value "M3 NPTH" (at 0 5.000) (layer "F.Fab") hide\n'
        '    (effects (font (size 1.000 1.000) (thickness 0.150))))\n',
        '  (fp_circle (center 0 0) (end 4.000 0) (stroke (width 0.150) (type default)) (fill none) (layer "F.SilkS"))\n',
        '  (fp_circle (center 0 0) (end 1.600 0) (stroke (width 0.100) (type default)) (fill none) (layer "F.Fab"))\n',
        '  (fp_circle (center 0 0) (end 4.000 0) (stroke (width 0.050) (type default)) (fill none) (layer "F.CrtYd"))\n',
        '  (pad "" np_thru_hole circle (at 0 0) (size 3.200 3.200) (drill 3.200) (layers "*.Cu" "*.Mask"))\n',
        ')\n',
    ))


def main() -> None:
    LIBRARY.mkdir(exist_ok=True)
    # This managed candidate belonged only to the removed onboard D2.  Delete
    # it reproducibly so an older generated library cannot silently retain it.
    (LIBRARY / "WorldSemi_WS2812B-V5_PLACEMENT_CANDIDATE_NOT_RELEASED.kicad_mod").unlink(missing_ok=True)
    footprints = {
        "Samtec_SSW_1x15_P2.54mm_THT.kicad_mod": header("Samtec_SSW_1x15_P2.54mm_THT", 15),
        "Samtec_SSW_1x07_P2.54mm_THT.kicad_mod": header("Samtec_SSW_1x07_P2.54mm_THT", 7),
        "Samtec_SSW_1x04_P2.54mm_THT.kicad_mod": header("Samtec_SSW_1x04_P2.54mm_THT", 4),
        "Samtec_TSW-102-07-G-S_1x02_P2.54mm_THT.kicad_mod": samtec_tsw_102_07_g_s(),
        "PinHeader_1x03_P2.54mm_Vertical.kicad_mod": pin_header("PinHeader_1x03_P2.54mm_Vertical", 3),
        "PinHeader_1x06_P2.54mm_Vertical.kicad_mod": pin_header("PinHeader_1x06_P2.54mm_Vertical", 6),
        "JST_B2B-XH-A_1x02_P2.50mm_THT.kicad_mod": jst_xh_b2b_xh_a(),
        "ESP32_DevKit_30pin_Socket_2x15_MechanicalTemplate.kicad_mod": esp32_template(),
        "E220_T22D_Socket_400_900.kicad_mod": e220_socket(),
        "OLED_0p96_4pin_MechanicalTemplate_PENDING_DATUM.kicad_mod": oled_template(),
        "MountingHole_M3_NPTH_REV1.kicad_mod": mounting_hole_m3_npth(),
        "TI_TPS62133RGT_RGT0016C.kicad_mod": tps62133(),
        "Coilcraft_XFL4020-222MEB.kicad_mod": xfl4020(),
        "Diodes_DMP3130LQ-7_SOT23.kicad_mod": dmp3130(),
        "TI_SN74AHCT1G125DBVR_SOT23-5.kicad_mod": sn74ahct1g125(),
        "TI_TLV1117LV33DCYR_DCY_SOT223.kicad_mod": tlv1117lv33_dcy_sot223(),
        "TestPoint_THT_1p0mm_PROTOTYPE.kicad_mod": testpoint(),
        "Littelfuse_SMBJ10CA_DO214AA.kicad_mod": smbj10ca(),
        "Littelfuse_1812L200_16_4532Metric.kicad_mod": fuse_1812(),
        "Murata_GRM21_2012Metric.kicad_mod": murata_grm21_standard(),
        "Murata_GRM21BR61A226ME44_2012Metric.kicad_mod": murata_grm21_c3(),
        "Murata_GRM188_1608Metric.kicad_mod": murata_grm188_standard(),
        "Murata_GRM188R61A106MAAL_1608Metric.kicad_mod": murata_grm188_c5(),
        "Resistor_0603_1608Metric.kicad_mod": yageo_rc0603(),
    }
    for filename, content in footprints.items():
        (LIBRARY / filename).write_text(content, encoding="utf-8")
    FP_TABLE.write_text('''(fp_lib_table
  (version 7)
  (lib (name "Carrier")(type "KiCad")(uri "${KIPRJMOD}/esp32-e220.pretty")(options "")(descr "Reproducible ESP32-E220 carrier footprints"))
)
''', encoding="utf-8")


if __name__ == "__main__":
    main()
