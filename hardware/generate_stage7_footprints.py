#!/usr/bin/env python3
"""Generate Stage 7 interface/mechanical KiCad footprints reproducibly.

No PCB is generated here.  Dimensions and release limits are documented in
docs/footprint-mechanical-review.md; this script deliberately preserves TBD
mechanical data as guide graphics rather than inventing pads or holes.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parent
LIBRARY = ROOT / "esp32-e220.pretty"


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
        '(size 1.700 1.700) (drill 1.000) (layers "*.Cu" "*.Mask"))\n'
    )


def header(name: str, positions: int) -> str:
    last = (positions - 1) * 2.54
    contents = [
        f'(footprint "{name}" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "Samtec SSW through-hole socket, 2.54 mm pitch, 0.64 mm square tail; Stage 7 project copy")\n',
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


def esp32_template() -> str:
    # Only the rows are datum-verified.  The body is intentionally unregistered
    # to the headers: it is a visual envelope, not a placement datum.
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
        text("user", "ANTENNA END — KEEP OUT LOCATION TBD", 12.7, last + 1.6, "F.SilkS", 0.75),
        text("user", "BODY 28 x 51 USER-MEASURED — DATUM REGISTRATION TBD", 12.7, last / 2, "Dwgs.User", 0.85),
        rect(-1.350, -1.400, 26.750, last + 1.400, "F.CrtYd", 0.05),
        line(-1.350, -1.400, -0.300, -1.400, "F.SilkS", 0.35),
        line(24.350, -1.400, 25.400, -1.400, "F.SilkS", 0.35),
    ]
    # Illustrative, explicitly unregistered envelope: do not use it for placement.
    contents.append(rect(-1.300, -7.720, 26.700, 43.280, "Dwgs.User", 0.20))
    for index in range(15):
        y = index * 2.54
        contents.append(pad(f"L{index + 1}", 0, y, index == 0))
        contents.append(pad(f"R{index + 1}", 25.4, y, index == 0))
    contents.append(")\n")
    return "".join(contents)


def e220_socket() -> str:
    # EBYTE common 400/900T22D geometry uses lower-left module-body datum.
    contents = [
        '(footprint "E220_T22D_Socket_400_900" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "Carrier-side 1x7 Samtec SSW socket for common EBYTE E220-400T22D / E220-900T22D geometry; not EBYTE solder-pad pattern")\n',
        '  (tags "EBYTE E220 400T22D 900T22D socket 2.54mm")\n',
        '  (attr through_hole)\n',
        text("reference", "J_E220", 10.5, -3.0, "F.SilkS"),
        text("value", "E220-400T22D / E220-900T22D SOCKET", 10.5, 39.0, "F.Fab", 0.85),
        text("user", "PIN 1 / M0", 2.88, -1.1, "F.SilkS", 0.75),
        text("user", "SMA / ANTENNA SIDE — KEEP ACCESS CLEAR", 10.5, 34.8, "F.SilkS", 0.70),
        text("user", "400 MHz and 900 MHz antennas are NOT interchangeable", 10.5, 37.3, "Dwgs.User", 0.70),
        text("user", "EBYTE fixed-hole geometry / underside clearance: TBD", 10.5, 39.0, "Dwgs.User", 0.65),
        rect(0, 0, 21.0, 36.0, "F.Fab", 0.10),
        rect(-1.0, -1.0, 22.0, 37.0, "F.CrtYd", 0.05),
        rect(-0.3, -0.3, 21.3, 36.3, "F.SilkS", 0.12),
        line(1.88, 0.2, 2.88, 0.2, "F.SilkS", 0.35),
    ]
    for index in range(7):
        contents.append(pad(str(index + 1), 2.88 + index * 2.54, 1.50, index == 0))
    contents.append(")\n")
    return "".join(contents)


def oled_template() -> str:
    # The module body and X/Y hole-centre spacing are supplied by the user.
    # Hole diameter and connector datum are not present in the current source.
    contents = [
        '(footprint "OLED_0p96_4pin_MechanicalTemplate_PENDING_DATUM" (version 20240108) (generator "stage7")\n',
        '  (layer "F.Cu")\n',
        '  (descr "0.96in SSD1306 I2C OLED template. 26x26 mm body and 21.740x22.000 mm mount-centre spacing known; header datum and hole diameter TBD.")\n',
        '  (tags "OLED SSD1306 0.96 4pin mechanical template PENDING DATUM")\n',
        '  (attr through_hole)\n',
        text("reference", "MECH**", 13.0, -3.0, "F.SilkS"),
        text("value", "OLED 0.96in mechanical template — NOT PRODUCTION APPROVED", 13.0, 29.0, "F.Fab", 0.80),
        text("user", "BODY 26.000 x 26.000 USER/SUPPLIER DRAWING", 13.0, 13.0, "Dwgs.User", 0.75),
        text("user", "MOUNT-SPACING GUIDE (unregistered): X=21.740, Y=22.000; HOLE DIA TBD", 13.0, 15.0, "Dwgs.User", 0.70),
        text("user", "1x4 HEADER DATUM / DISPLAY / NOTCH: TBD", 13.0, 17.0, "Dwgs.User", 0.70),
        rect(0, 0, 26.0, 26.0, "F.Fab", 0.10),
        rect(-1.0, -1.0, 27.0, 27.0, "F.CrtYd", 0.05),
    ]
    # The source supplies only the spacing, not either hole-to-board-edge datum.
    # These are therefore coordinates in an independent *hole-spacing guide*,
    # not locations on the 26 x 26 mm body outline above.
    for x in (35.0, 56.74):
        for y in (0.0, 22.0):
            contents.append(circle(x, y, 1.0, "Dwgs.User", 0.15))
    # This four-pad row is an interface guide only.  Its body registration is TBD.
    contents.extend((
        text("user", "INTERFACE ONLY: 1 GND  2 VCC  3 SCL  4 SDA", 3.81, -1.4, "F.SilkS", 0.65),
        pad("1", 0, 0, True),
        pad("2", 2.54, 0),
        pad("3", 5.08, 0),
        pad("4", 7.62, 0),
        ")\n",
    ))
    return "".join(contents)


def main() -> None:
    LIBRARY.mkdir(exist_ok=True)
    footprints = {
        "Samtec_SSW_1x15_P2.54mm_THT.kicad_mod": header("Samtec_SSW_1x15_P2.54mm_THT", 15),
        "Samtec_SSW_1x07_P2.54mm_THT.kicad_mod": header("Samtec_SSW_1x07_P2.54mm_THT", 7),
        "Samtec_SSW_1x04_P2.54mm_THT.kicad_mod": header("Samtec_SSW_1x04_P2.54mm_THT", 4),
        "ESP32_DevKit_30pin_Socket_2x15_MechanicalTemplate.kicad_mod": esp32_template(),
        "E220_T22D_Socket_400_900.kicad_mod": e220_socket(),
        "OLED_0p96_4pin_MechanicalTemplate_PENDING_DATUM.kicad_mod": oled_template(),
    }
    for filename, content in footprints.items():
        (LIBRARY / filename).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
