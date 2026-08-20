#!/usr/bin/env python3
"""Generate the native KiCad 10 schematic and its review-oriented layout.

The electrical source of truth and the presentation are deliberately kept in
this one generator.  The sheet is a functional review drawing, not a netlist
dump: short local wires show each support circuit, while named labels bridge
the independent blocks.
"""
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

OUT = Path(__file__).with_name("esp32-e220.kicad_sch")
SYMLIB = Path(__file__).with_name("esp32-e220.kicad_sym")
TABLE = Path(__file__).with_name("sym-lib-table")

# Authoritative schematic-to-PCB assembly contract.  Keep this deliberately
# compact and use the exact project-local footprint identifiers instantiated by
# generate_stage7_footprints.py.  Human-readable circuit function belongs in
# notes/descriptions; Value is the approved procurement value/MPN and must
# therefore match the PCB.
ASSEMBLY_CONTRACT = {
    "C1": ("GRM21BR61E106KA73", "Murata_GRM21_2012Metric"),
    "C2": ("GRM188R71C104KA01D", "Murata_GRM188_1608Metric"),
    "C3": ("GRM21BR61A226ME44", "Murata_GRM21_2012Metric"),
    "C4": ("GRM1885C1H332JA01D", "Murata_GRM188_1608Metric"),
    "C5": ("GRM188R61A106MAAL", "Murata_GRM188_1608Metric"),
    "C6": ("GRM188R71C104KA01D", "Murata_GRM188_1608Metric"),
    "C7": ("GRM188R71C104KA01D", "Murata_GRM188_1608Metric"),
    "C8": ("GRM188R71C104KA01D", "Carrier:Murata_GRM188_1608Metric"),
    "C9": ("GRM21BR61E106KA73", "Carrier:Murata_GRM21_2012Metric"),
    "C10": ("GRM21BR61E106KA73", "Carrier:Murata_GRM21_2012Metric"),
    "D2": ("WS2812B-V5", "WorldSemi_WS2812B-V5_PLACEMENT_CANDIDATE_NOT_RELEASED"),
    "D3": ("SMBJ10CA", "Littelfuse_SMBJ10CA_DO214AA"),
    "F1": ("1812L200/16", "Littelfuse_1812L200_16_4532Metric"),
    "J1": ("SSW-115-02-G-S DEVKIT LEFT", "Samtec_SSW_1x15_P2.54mm_THT"),
    "J2": ("SSW-115-02-G-S DEVKIT RIGHT", "Samtec_SSW_1x15_P2.54mm_THT"),
    "J3": ("E220-400T22D / E220-900T22D SOCKET", "E220_T22D_Socket_400_900"),
    "J4": ("B2B-XH-A", "JST_B2B-XH-A_1x02_P2.50mm_THT"),
    "J5": ("SSW-104-02-G-S", "Samtec_SSW_1x04_P2.54mm_THT"),
    "J6": ("TSW-105-07-G-D", "Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical"),
    "J7": ("TSW-106-07-G-D", "Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical"),
    "J8": ("B2B-XH-A", "JST_B2B-XH-A_1x02_P2.50mm_THT"),
    "JP1": ("TSW-102-07-G-S + SNT-100-BK-G", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"),
    "L1": ("XFL4020-222MEB", "Coilcraft_XFL4020-222MEB"),
    "Q1": ("DMP3130LQ-7", "Diodes_DMP3130LQ-7_SOT23"),
    "R1": ("100k 1%", "Resistor_0603_1608Metric"),
    "R2": ("1M 1%", "Resistor_0603_1608Metric"),
    "R3": ("RC0603FR-0710KL", "Carrier:Resistor_0603_1608Metric"),
    "R4": ("RC0603FR-073K3L", "Carrier:Resistor_0603_1608Metric"),
    "R8": ("10k 1%", "Resistor_0603_1608Metric"),
    "R9": ("10k 1%", "Resistor_0603_1608Metric"),
    "TP1": ("BAT_PLUS", "TestPoint_THT_1p0mm_PROTOTYPE"),
    "TP2": ("GND", "TestPoint_THT_1p0mm_PROTOTYPE"),
    "TP3": ("BUCK_IN", "TestPoint_THT_1p0mm_PROTOTYPE"),
    "TP4": ("5V_SYS", "TestPoint_THT_1p0mm_PROTOTYPE"),
    "TP5": ("5V_SYS", "TestPoint_THT_1p0mm_PROTOTYPE"),
    "TP6": ("E220_M0", "TestPoint_THT_1p0mm_PROTOTYPE"),
    "TP7": ("E220_M1", "TestPoint_THT_1p0mm_PROTOTYPE"),
    "TP8": ("E220_AUX", "TestPoint_THT_1p0mm_PROTOTYPE"),
    "TP9": ("E220_RXD", "TestPoint_THT_1p0mm_PROTOTYPE"),
    "TP10": ("E220_TXD", "TestPoint_THT_1p0mm_PROTOTYPE"),
    "U1": ("TPS62133RGT", "TI_TPS62133RGT_RGT0016C"),
    "U3": ("SN74AHCT1G125DBVR", "TI_SN74AHCT1G125DBVR_SOT23-5"),
    "U4": ("TLV1117LV33DCYR", "Package_TO_SOT_SMD:SOT-223-3_TabPin2"),
}

# These two optional pull-ups are intentional non-PCB items: they remain DNP
# schematic options but must never request a PCB footprint.
NON_PCB_DNP = {"R10", "R11"}

UUID_COUNTER = 0

def u():
    """Return a stable UUID so two source-identical generations are byte-identical."""
    global UUID_COUNTER
    UUID_COUNTER += 1
    return str(uuid5(NAMESPACE_URL, f"esp32-e220-schematic-{UUID_COUNTER}"))
def s(v): return round(v / 1.27) * 1.27
def prop(name, value, ident, x, y, hide=False):
    h = " hide" if hide else ""
    return f'''    (property "{name}" "{value}" (id {ident}) (at {x} {y} 0)\n      (effects (font (size 1.27 1.27)){h})\n    )'''

def libsym(libid, ref, value, pins, description):
    # Pins on the left side, one 2.54-mm grid point apart, derived from the
    # stock Connector_Generic:Conn_01x15 symbol in Arduino_Nano.kicad_sch.
    height = max(12.7, len(pins) * 1.27 + 3.81)
    lines = [f'''    (symbol "{libid}" (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)
      (property "Reference" "{ref}" (id 0) (at 0 {height + 1.27} 0) (effects (font (size 1.27 1.27))))
      (property "Value" "{value}" (id 1) (at 0 {-height - 1.27} 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (id 3) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "ki_description" "{description}" (id 4) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "{libid.split(':')[-1]}_1_1"
        (rectangle (start -1.27 {height}) (end 2.54 {-height}) (stroke (width 0.254)) (fill (type background)))''']
    for i, pin in enumerate(pins):
        num, name = pin[0], pin[1]
        electrical_type = pin[2] if len(pin) > 2 else "passive"
        y = (len(pins) - 1) * 1.27 - i * 2.54
        lines.append(f'''        (pin {electrical_type} line (at -5.08 {y} 0) (length 3.81)
          (name "{name}" (effects (font (size 1.0 1.0))))
          (number "{num}" (effects (font (size 1.0 1.0))))
        )''')
    lines.append("      )\n    )")
    return "\n".join(lines)

def power_flag_libsym():
    """Native equivalent of KiCad power:PWR_FLAG for ERC source boundaries."""
    return '''    (symbol "Project:PWR_FLAG" (power) (pin_numbers hide) (pin_names (offset 0) hide) (in_bom yes) (on_board yes)
      (property "Reference" "#FLG" (id 0) (at 0 1.905 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "PWR_FLAG" (id 1) (at 0 3.81 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (id 3) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "ki_description" "ERC marker: this net is intentionally sourced by the declared upstream power path" (id 4) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "PWR_FLAG_0_0"
        (pin power_out line (at 0 0 90) (length 0)
          (name "pwr" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
      )
    )'''

def testpoint_libsym():
    """Exact compact geometry of KiCad's installed Connector:TestPoint."""
    return '''    (symbol "Project:TestPoint" (pin_numbers hide) (pin_names (offset 0.762) hide) (in_bom yes) (on_board yes)
      (property "Reference" "TP" (id 0) (at 0 6.858 0) (effects (font (size 1.27 1.27))))
      (property "Value" "TestPoint" (id 1) (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (id 2) (at 5.08 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "~" (id 3) (at 5.08 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "ki_description" "Schematic test point; exact physical test-point component deferred" (id 4) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "TestPoint_0_1"
        (circle (center 0 3.302) (radius 0.762) (stroke (width 0) (type default) (color 0 0 0 0)) (fill (type none)))
      )
      (symbol "TestPoint_1_1"
        (pin passive line (at 0 0 90) (length 2.54)
          (name "1" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
      )
    )'''

def instance(libid, ref, value, x, y, pins, datasheet="", dnp=False, assembly_dnp=False):
    x, y = s(x), s(y)
    value, footprint = ASSEMBLY_CONTRACT.get(ref, (value, ""))
    on_board = "no" if dnp else "yes"
    lines = [f'''  (symbol (lib_id "{libid}") (at {x} {y} 0) (unit 1)
    (in_bom yes) (on_board {on_board})
    (uuid {u()})''', prop("Reference", ref, 0, x + 5.08, y - 1.27, ref.startswith("#")),
             # Exact MPN/value metadata remains in the editable schematic, but
             # is hidden here to avoid long procurement strings obscuring pins.
             # Each functional block carries concise visible ref/value captions.
             prop("Value", value, 1, x + 5.08, y + 1.27, True),
             prop("Footprint", footprint, 2, x, y, True),
             # KiCad parity compares schematic fields literally.  Datasheets
             # are recorded in project documentation, rather than duplicated
             # in only one of the two manufacturing artefacts.
             prop("Datasheet", "", 3, x, y, True)]
    if dnp or assembly_dnp:
        lines.append(prop("DNP", "YES", 4, x, y, True))
    for pin in pins:
        lines.append(f'    (pin "{pin[0]}" (uuid {u()}))')
    lines.append("  )")
    return "\n".join(lines)

def testpoint_instance(ref, value, x, y):
    """Compact instance matching the native Connector:TestPoint geometry."""
    x, y = s(x), s(y)
    value, footprint = ASSEMBLY_CONTRACT[ref]
    return f'''  (symbol (lib_id "Project:TestPoint") (at {x} {y} 0) (unit 1)
    (in_bom yes) (on_board yes)
    (uuid {u()})
{prop("Reference", ref, 0, x + 3.0, y - 2.0, False)}
{prop("Value", value, 1, x + 3.0, y + 2.0, True)}
{prop("Footprint", footprint, 2, x, y, True)}
{prop("Datasheet", "~", 3, x, y, True)}
    (pin "1" (uuid {u()}))
  )'''

def label(net, x, y):
    x, y = s(x), s(y)
    return f'''  (label "{net}" (at {x} {y} 0)
    (effects (font (size 1.27 1.27)) (justify left bottom))
    (uuid {u()})
  )'''

def global_label(net, x, y, shape="bidirectional"):
    """Template-derived KiCad global label for an intentionally reserved I2C net."""
    x, y = s(x), s(y)
    return f'''  (global_label "{net}" (shape {shape}) (at {x} {y} 0)
    (effects (font (size 1.27 1.27)) (justify left bottom))
    (uuid {u()})
    (property "Intersheet References" "${{INTERSHEET_REFS}}" (id 0) (at 0 0 0)
      (effects (font (size 1.27 1.27)) hide)
    )
  )'''

def no_connect(x, y):
    x, y = s(x), s(y)
    return f'''  (no_connect (at {x} {y}) (uuid {u()}))'''

def note(text, x, y, size=1.5):
    text = text.replace('"', '\\"')
    return f'''  (text "{text}" (at {x} {y} 0)
    (effects (font (size {size} {size})) (justify left bottom))
    (uuid {u()})
  )'''

def wire(*points):
    """A local, visible connection.  Inter-block connectivity remains labels."""
    return "\n".join(f'''  (wire (pts (xy {s(x1)} {s(y1)}) (xy {s(x2)} {s(y2)}))
    (stroke (width 0) (type solid) (color 0 0 0 0))
    (uuid {u()})
  )''' for (x1, y1), (x2, y2) in zip(points, points[1:]))

def heading(text, x, y):
    return note(text, x, y, 2.0)

def pin_pos(center_x, center_y, pin_count, pin_number):
    """Return the exact left-side pin endpoint used by libsym().

    The lib-symbol coordinate system is positive upward, while sheet Y grows
    downward.  Thus the sheet endpoint is the symbol origin minus its local
    Y coordinate.  Keeping both formulae here prevents a label from being
    assigned to the mirror-image pin row.
    """
    x = s(center_x) - 5.08
    local_y = (pin_count - 1) * 1.27 - (pin_number - 1) * 2.54
    y = s(s(center_y) - local_y)
    return x, y

def pin_label(center_x, center_y, pin_count, pin_number, net):
    return label(net, *pin_pos(center_x, center_y, pin_count, pin_number))

def pin_no_connect(center_x, center_y, pin_count, pin_number):
    return no_connect(*pin_pos(center_x, center_y, pin_count, pin_number))

left = [("1","VIN / 5V"),("2","GND"),("3","GPIO13"),("4","GPIO12"),("5","GPIO14"),
        ("6","GPIO27"),("7","GPIO26"),("8","GPIO25"),("9","GPIO33"),("10","GPIO32"),
        ("11","GPIO35"),("12","GPIO34"),("13","GPIO39/VN"),("14","GPIO36/VP"),("15","EN")]
right = [("1","3V3"),("2","GND"),("3","GPIO15"),("4","GPIO2"),("5","GPIO4"),
         ("6","GPIO16/RX2"),("7","GPIO17/TX2"),("8","GPIO5"),("9","GPIO18"),("10","GPIO19"),
         ("11","GPIO21"),("12","GPIO3/RX0"),("13","GPIO1/TX0"),("14","GPIO22"),("15","GPIO23")]
e220 = [("1","M0","input"),("2","M1","input"),("3","RXD","input"),
        ("4","TXD","output"),("5","AUX","output"),("6","VCC","power_in"),("7","GND","power_in")]
oled_i2c = [("1","GND","power_in"),("2","VCC / 3V3","power_in"),
            ("3","SCL","bidirectional"),("4","SDA","bidirectional")]
battery = [("1","BAT+","passive"),("2","BAT-","passive")]
user_gpio = [("1","GND"),("2","GPIO13"),("3","GND"),("4","GPIO14"),("5","GND"),
             ("6","GPIO18"),("7","GND"),("8","GPIO19"),("9","AUX_3V3"),("10","GPIO23")]
display_aux = [("1","GND"),("2","AUX_3V3"),("3","GPIO21 / OLED_SDA"),("4","GPIO22 / OLED_SCL"),
               ("5","GPIO18"),("6","GPIO23"),("7","GPIO19"),("8","GPIO13"),("9","GPIO14"),
               ("10","GPIO33"),("11","GND"),("12","AUX_3V3")]
power_switch = [("1","BAT_FUSED"),("2","BAT_SW")]
devkit_pwr = [("1","5V_SYS"),("2","DEVKIT_VIN")]
# Exact TPS62133 pin numbers/names from TI Table 6-1.  The exposed thermal
# pad is explicitly an electrical GND pin for later footprint mapping.
# SW1/SW2/SW3 are parallel bond wires of one switch node.  They are marked
# passive in the custom symbol so ERC does not treat parallel physical pads as
# mutually-conflicting separate power sources.
tps62133 = [("1","SW","passive"),("2","SW","passive"),("3","SW","passive"),
            ("4","PG","open_collector"),("5","FB","input"),("6","AGND","power_in"),
            ("7","FSW","input"),("8","DEF","input"),("9","SS/TR","input"),
            ("10","AVIN","power_in"),("11","PVIN","power_in"),("12","PVIN","power_in"),
            ("13","EN","input"),("14","VOS","input"),("15","PGND","power_in"),
            ("16","PGND","power_in"),("EP","EXPOSED THERMAL PAD","power_in")]
ahct = [("1","OE","input"),("2","A","input"),("3","GND","power_in"),("4","Y","output"),("5","VCC","power_in")]
ws2812 = [("1","VDD","power_in"),("2","DOUT","output"),("3","VSS","power_in"),("4","DIN","input")]
tlv1117lv33 = [("1","GND","power_in"),("2","OUT / TAB","power_out"),("3","IN","power_in")]
testpoint = [("1","TP","passive")]
r2 = [("1","1"),("2","2")]
inductor = [("1","1","passive"),("2","2","passive")]
fuse = [("1","1","passive"),("2","2","passive")]
tvs = [("1","A","passive"),("2","K","passive")]
# Diodes Inc. DMP3130LQ-7 official SOT-23 top view: 1=G, 2=S, 3=D.
pmos = [("1","G","input"),("2","S","passive"),("3","D","passive")]

libs = [
    libsym("Project:DevKit_Left_1x15", "J", "DEVKIT_LEFT_1x15", left, "User-verified left DevKit header; USB-C toward antenna"),
    libsym("Project:DevKit_Right_1x15", "J", "DEVKIT_RIGHT_1x15", right, "User-verified right DevKit header; USB-C toward antenna"),
    libsym("Project:E220_T22D_400_900", "J", "E220-T22D 400/900 MHz", e220,
           "EBYTE E220-400T22D / E220-900T22D common verified pin definition"),
    libsym("Project:OLED_SSD1306_I2C_1x4", "J", "OLED SSD1306 I2C 1x4", oled_i2c,
           "User-installed 0.96 inch SSD1306 128x64 I2C module; user/seller-provided header order 1 GND, 2 VCC, 3 SCL, 4 SDA"),
    libsym("Project:Battery_2S_Protected_Input", "J", "PROTECTED 2S LI-ION INPUT", battery,
           "Carrier input only: externally protected 2S Li-ion pack, 6.0...8.4 V; not a charger or BMS interface"),
    libsym("Project:USER_GPIO_2x5", "J", "USER_GPIO 2x5", user_gpio,
           "User-installed GPIO expansion header; PCBA DNP, 2.54-mm PTH"),
    libsym("Project:DISPLAY_AUX_2x6", "J", "DISPLAY_AUX 2x6", display_aux,
           "User-installed display/auxiliary expansion header; PCBA DNP, 2.54-mm PTH"),
    libsym("Project:POWER_SW_1x2", "J", "POWER_SW 1x2", power_switch,
           "External mechanical power-switch harness connector; BAT_FUSED to BAT_SW"),
    libsym("Project:DEVKIT_PWR_1x2", "JP", "DEVKIT_PWR 1x2", devkit_pwr,
           "2.54-mm removable jumper: 5V_SYS to DEVKIT_VIN; header PCBA fitted, shunt user-installed"),
    libsym("Project:TPS62133RGT", "U", "TPS62133RGT", tps62133, "TI fixed 5-V 3-A synchronous buck, RGT VQFN-16 with exposed pad"),
    libsym("Project:SN74AHCT1G125DBVR", "U", "SN74AHCT1G125DBVR", ahct, "TI 5-V single buffer with 3-state output"),
    libsym("Project:TLV1117LV33DCY", "U", "TLV1117LV33DCYR", tlv1117lv33,
           "TI 3.3-V 1-A LDO, DCY SOT-223: pin 2 and tab are regulated OUT"),
    libsym("Project:WS2812B_V5", "D", "WS2812B-V5", ws2812, "WorldSemi 5-V intelligent RGB LED"),
    testpoint_libsym(),
    power_flag_libsym(),
    libsym("Project:R", "R", "R", r2, "Passive resistor"),
    libsym("Project:C", "C", "C", r2, "Passive capacitor"),
    libsym("Project:L", "L", "L", inductor, "Power inductor"),
    libsym("Project:F", "F", "F", fuse, "Resettable fuse"),
    libsym("Project:TVS", "D", "TVS", tvs, "Bidirectional TVS diode"),
    libsym("Project:DMP3130LQ_7", "Q", "DMP3130LQ-7", pmos, "Diodes Inc. P-channel reverse-polarity MOSFET"),
]

items = []
# Rev.1 active carrier: externally protected 2S pack only; USB-C input and
# pre-gate Type-C circuitry are intentionally absent from generated content.
items += [instance("Project:DevKit_Left_1x15", "J1", "DEVKIT_LEFT (USB-C toward antenna)", 70, 100, left),
          instance("Project:DevKit_Right_1x15", "J2", "DEVKIT_RIGHT (USB-C toward antenna)", 115, 100, right),
          instance("Project:E220_T22D_400_900", "J3", "E220-T22D SOCKET — FIT 400T22D OR 900T22D", 175, 105, e220,
                   "https://www.cdebyte.com/pdf-down.aspx?id=4221"),
          instance("Project:OLED_SSD1306_I2C_1x4", "J5", "OLED 0.96 SSD1306 128x64 I2C — FEMALE 1x4 SOCKET", 330, 175, oled_i2c),
          instance("Project:USER_GPIO_2x5", "J6", "USER_GPIO 2x5 — USER INSTALL / PCBA DNP", 235, 170, user_gpio,
                   assembly_dnp=True),
          instance("Project:DISPLAY_AUX_2x6", "J7", "DISPLAY_AUX 2x6 — USER INSTALL / PCBA DNP", 235, 210, display_aux,
                   assembly_dnp=True),
          instance("Project:POWER_SW_1x2", "J8", "POWER_SW — JST XH 2.50mm EXTERNAL SWITCH", 85, 170, power_switch,
                   "https://www.jst-mfg.com/product/pdf/eng/eXH.pdf"),
          instance("Project:DEVKIT_PWR_1x2", "JP1", "DEVKIT_PWR — HEADER PCBA FIT / SHUNT USER INSTALL", 85, 70, devkit_pwr,
                   "https://www.samtec.com/products/tsw-102-07-g-s"),
          instance("Project:Battery_2S_Protected_Input", "J4", "PROTECTED 2S LI-ION INPUT ONLY 6...8.4V", 25, 155, battery),
          instance("Project:TPS62133RGT", "U1", "TPS62133RGT (5V / 3A BUCK)", 130, 180, tps62133,
                   "https://www.ti.com/lit/ds/symlink/tps62133.pdf"),
          instance("Project:SN74AHCT1G125DBVR", "U3", "SN74AHCT1G125DBVR", 275, 105, ahct,
                   "https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf"),
          instance("Project:TLV1117LV33DCY", "U4", "TLV1117LV33DCYR (AUX_3V3 / 300mA ALLOCATION)", 265, 255, tlv1117lv33,
                   "https://www.ti.com/lit/ds/symlink/tlv1117lv.pdf"),
          instance("Project:WS2812B_V5", "D2", "WS2812B-V5", 325, 105, ws2812,
                   "https://www.world-semi.co.kr/_files/ugd/89cd03_1023b0e9d135431aa1e6491bfc318112.pdf"),
          instance("Project:F", "F1", "1812L200/16 (2A hold PPTC)", 45, 155, fuse,
                   "https://www.littelfuse.com/~/media/electronics/datasheets/resettable_ptcs/littelfuse_ptc_1812l_datasheet.pdf.pdf"),
          instance("Project:TVS", "D3", "SMBJ10CA (bidirectional TVS)", 65, 165, tvs,
                   "https://www.littelfuse.com/products/overvoltage-protection/tvs-diodes/surface-mount/smbj/smbj10ca"),
          instance("Project:DMP3130LQ_7", "Q1", "DMP3130LQ-7 (reverse-polarity)", 85, 155, pmos,
                   "https://www.diodes.com/_files/datasheets/DMP3130LQ.pdf"),
          instance("Project:L", "L1", "XFL4020-222MEB 2.2uH", 185, 180, inductor,
                   "https://www.coilcraft.com/getmedia/50632d43-da1e-4cdb-8ab4-3029cab51df3/xfl4020.pdf"),
          instance("Project:PWR_FLAG", "#FLG01", "PWR_FLAG", 35, 175, [("1", "pwr")]),
          instance("Project:PWR_FLAG", "#FLG02", "PWR_FLAG", 35, 185, [("1", "pwr")]),
          instance("Project:PWR_FLAG", "#FLG03", "PWR_FLAG", 35, 195, [("1", "pwr")]),
          instance("Project:PWR_FLAG", "#FLG04", "PWR_FLAG", 35, 205, [("1", "pwr")]),
          instance("Project:PWR_FLAG", "#FLG05", "PWR_FLAG", 35, 215, [("1", "pwr")]),
          testpoint_instance("TP1", "BAT_PLUS", 25, 230),
          testpoint_instance("TP2", "GND", 45, 230),
          testpoint_instance("TP3", "BUCK_IN", 65, 230),
          testpoint_instance("TP4", "5V_SYS", 85, 230),
          testpoint_instance("TP5", "E220_VCC", 105, 230),
          testpoint_instance("TP6", "E220_M0", 25, 240),
          testpoint_instance("TP7", "E220_M1", 45, 240),
          testpoint_instance("TP8", "E220_AUX", 65, 240),
          testpoint_instance("TP9", "E220_RXD", 85, 240),
          testpoint_instance("TP10", "E220_TXD", 105, 240)]

parts = [
    ("Project:R","R1","100k 1% (Q1 gate pull-down)",65,180,r2),
    ("Project:R","R2","1M 1% (Q1 gate-source)",85,180,r2),
    ("Project:R","R3","RC0603FR-0710KL 10k 1% (BAT_SENSE upper)",80,255,r2),
    ("Project:R","R4","RC0603FR-073K3L 3.3k 1% (BAT_SENSE lower)",100,255,r2),
    ("Project:C","C1","GRM21BR61E106KA73 10uF 25V X5R (BUCK IN)",105,205,r2),
    ("Project:C","C2","GRM188R71C104KA01D 100nF 16V X7R (AVIN)",125,205,r2),
    ("Project:C","C3","GRM21BR61A226ME44 22uF 10V X5R (BUCK OUT)",185,205,r2),
    ("Project:C","C4","GRM1885C1H332JA01D 3.3nF 50V C0G (SS/TR)",145,205,r2),
    ("Project:C","C5","GRM188R61A106MAAL 10uF 10V X5R",175,140,r2),
    ("Project:C","C6","GRM188R71C104KA01D 100nF 16V X7R",195,140,r2),
    ("Project:R","R8","10k 1% M0 reset pull-down",215,140,r2),
    ("Project:R","R9","10k 1% M1 reset pull-down",235,140,r2),
    ("Project:R","R10","DNP 4.7k 1% OLED SDA pull-up to AUX_3V3",300,185,r2),
    ("Project:R","R11","DNP 4.7k 1% OLED SCL pull-up to AUX_3V3",320,185,r2),
    ("Project:C","C7","GRM188R71C104KA01D 100nF 16V X7R",285,140,r2),
    ("Project:C","C8","GRM188R71C104KA01D 100nF 16V X7R (BAT_SENSE ADC FILTER)",120,255,r2),
    ("Project:C","C9","GRM21BR61E106KA73 10uF 25V X5R (U4 CIN)",295,255,r2),
    ("Project:C","C10","GRM21BR61E106KA73 10uF 25V X5R (U4 COUT)",315,255,r2),
]
for a,b,c,d,e,f in parts:
    items.append(instance(a,b,c,d,e,f,dnp=b in {"R10", "R11"}))

# Verified DevKit/E220/LED signals retained from Stage 5 plus authorized Rev.1 expansion.
for n, net in [(1,"DEVKIT_VIN"),(2,"GND"),(3,"GPIO13"),(5,"GPIO14"),(6,"E220_AUX"),(7,"E220_M1"),(8,"E220_M0"),
               (9,"GPIO33"),(10,"BAT_SENSE")]:
    items.append(pin_label(70,100,len(left),n,net))
for n in set(range(1,16)) - {1,2,3,5,6,7,8,9,10}: items.append(pin_no_connect(70,100,len(left),n))
for n, net in [(1,"DEVKIT_3V3"),(2,"GND"),(5,"WS2812_DATA_3V3"),(6,"E220_TXD"),(7,"E220_RXD"),
               (9,"GPIO18"),(10,"GPIO19"),(15,"GPIO23")]:
    items.append(pin_label(115,100,len(right),n,net))
# One-sheet I2C nets: local labels intentionally connect DevKit, socket and
# optional pull-up sites without creating a global-label/local-label ERC mix.
items += [label("OLED_SDA", *pin_pos(115,100,len(right),11)), label("OLED_SCL", *pin_pos(115,100,len(right),14))]
for n in set(range(1,16)) - {1,2,5,6,7,9,10,11,14,15}: items.append(pin_no_connect(115,100,len(right),n))
for n, net in [(1,"E220_M0"),(2,"E220_M1"),(3,"E220_RXD"),(4,"E220_TXD"),(5,"E220_AUX"),(6,"5V_SYS"),(7,"GND")]:
    items.append(pin_label(175,105,len(e220),n,net))
for n, net in [(1,"GND"),(2,"AUX_3V3"),(3,"OLED_SCL"),(4,"OLED_SDA")]:
    items.append(pin_label(330,175,len(oled_i2c),n,net))

# Battery connector, switch and protection: the P-MOS body diode must precharge from
# BAT_SW (D, pin 3) to BUCK_IN (S, pin 2). Correct polarity then produces
# negative VGS and enhanced conduction; reversed pack polarity leaves the body
# diode reverse-biased and VGS non-negative. D3 is across BAT_FUSED/GND.
items += [pin_label(25,155,len(battery),1,"BAT_PLUS"), pin_label(25,155,len(battery),2,"GND"),
          pin_label(45,155,len(fuse),1,"BAT_PLUS"), pin_label(45,155,len(fuse),2,"BAT_FUSED"),
          pin_label(65,165,len(tvs),1,"BAT_FUSED"), pin_label(65,165,len(tvs),2,"GND"),
          pin_label(85,170,len(power_switch),1,"BAT_FUSED"), pin_label(85,170,len(power_switch),2,"BAT_SW"),
          pin_label(85,155,len(pmos),1,"Q1_GATE"), pin_label(85,155,len(pmos),2,"BUCK_IN"), pin_label(85,155,len(pmos),3,"BAT_SW")]

# DEVKIT_PWR intentionally creates two separate nets: a removable shunt is the
# only approved connection from 5V_SYS to the DevKit VIN pad.
items += [pin_label(85,70,len(devkit_pwr),1,"5V_SYS"), pin_label(85,70,len(devkit_pwr),2,"DEVKIT_VIN")]

# BAT_SENSE is a strictly local divider from BUCK_IN to ADC1 GPIO32.  C8 is the
# Espressif-recommended 100-nF ADC-input filter capacitor.
items += [pin_label(80,255,2,1,"BUCK_IN"), pin_label(80,255,2,2,"BAT_SENSE"),
          pin_label(100,255,2,1,"BAT_SENSE"), pin_label(100,255,2,2,"GND"),
          pin_label(120,255,2,1,"BAT_SENSE"), pin_label(120,255,2,2,"GND")]

# User-installed expansion headers reuse existing, direct GPIO/I2C nets.  No
# series component or alternate signal identity is introduced by this stage.
for n, net in [(1,"GND"),(2,"GPIO13"),(3,"GND"),(4,"GPIO14"),(5,"GND"),(6,"GPIO18"),(7,"GND"),(8,"GPIO19"),(9,"AUX_3V3"),(10,"GPIO23")]:
    items.append(pin_label(235,170,len(user_gpio),n,net))
for n, net in [(1,"GND"),(2,"AUX_3V3"),(3,"OLED_SDA"),(4,"OLED_SCL"),(5,"GPIO18"),(6,"GPIO23"),
               (7,"GPIO19"),(8,"GPIO13"),(9,"GPIO14"),(10,"GPIO33"),(11,"GND"),(12,"AUX_3V3")]:
    items.append(pin_label(235,210,len(display_aux),n,net))

# TPS62133 fixed-5-V application per official data sheet. FSW=5V_SYS selects
# lower frequency; DEF/FB=GND keeps the nominal fixed output. PG is unused.
for n, net in [(1,"BUCK_SW"),(2,"BUCK_SW"),(3,"BUCK_SW"),(5,"GND"),(6,"GND"),(7,"5V_SYS"),
               (8,"GND"),(9,"SS_TR"),(10,"BUCK_IN"),(11,"BUCK_IN"),(12,"BUCK_IN"),
               (13,"BUCK_IN"),(14,"5V_SYS"),(15,"GND"),(16,"GND"),(17,"GND")]:
    items.append(pin_label(130,180,len(tps62133),n,net))
items.append(pin_no_connect(130,180,len(tps62133),4))
items += [pin_label(185,180,len(inductor),1,"BUCK_SW"), pin_label(185,180,len(inductor),2,"5V_SYS")]

for n, net in [(1,"GND"),(2,"WS2812_DATA_3V3"),(3,"GND"),(4,"WS2812_DIN"),(5,"5V_SYS")]: items.append(pin_label(275,105,len(ahct),n,net))
for n, net in [(1,"5V_SYS"),(3,"GND"),(4,"WS2812_DIN")]: items.append(pin_label(325,105,len(ws2812),n,net))
items.append(pin_no_connect(325,105,len(ws2812),2))

# U4 is the only authorized source of AUX_3V3.  The DCY tab is electrically
# identical to pin 2 and is therefore explicitly represented as AUX_3V3.
items += [pin_label(265,255,len(tlv1117lv33),1,"GND"), pin_label(265,255,len(tlv1117lv33),2,"AUX_3V3"),
          pin_label(265,255,len(tlv1117lv33),3,"5V_SYS"),
          pin_label(295,255,2,1,"5V_SYS"), pin_label(295,255,2,2,"GND"),
          pin_label(315,255,2,1,"AUX_3V3"), pin_label(315,255,2,2,"GND")]

for ref, x, y, net in [("TP1",25,230,"BAT_PLUS"),("TP2",45,230,"GND"),("TP3",65,230,"BUCK_IN"),("TP4",85,230,"5V_SYS"),("TP5",105,230,"5V_SYS"),
                       ("TP6",25,240,"E220_M0"),("TP7",45,240,"E220_M1"),("TP8",65,240,"E220_AUX"),("TP9",85,240,"E220_RXD"),("TP10",105,240,"E220_TXD")]: items.append(label(net,x,y))

# ERC source markers: external protected battery/return plus the explicitly
# declared protected BUCK_IN and U1-generated 5V_SYS domains.
items += [label("BAT_PLUS",35,175), label("GND",35,185), label("BUCK_IN",35,195), label("5V_SYS",35,205), label("DEVKIT_3V3",35,215)]

for x,y,a,b in [(65,180,"Q1_GATE","GND"),(85,180,"BUCK_IN","Q1_GATE"),(105,205,"BUCK_IN","GND"),(125,205,"BUCK_IN","GND"),
                (145,205,"SS_TR","GND"),(185,205,"5V_SYS","GND"),(175,140,"5V_SYS","GND"),(195,140,"5V_SYS","GND"),
                (215,140,"E220_M0","GND"),(235,140,"E220_M1","GND"),(285,140,"5V_SYS","GND"),
                (300,185,"OLED_SDA","AUX_3V3"),(320,185,"OLED_SCL","AUX_3V3")]: items += [pin_label(x,y,2,1,a),pin_label(x,y,2,2,b)]

items += [
    # Functional-block headers deliberately contain the operational information
    # needed while reviewing the carrier.  Historical decisions live in docs/.
    heading("A. BATTERY INPUT / PROTECTION", 18, 135),
    heading("B. 2S -> 5V BUCK", 105, 145),
    heading("H. AUX_3V3 LDO", 250, 242),
    note("U4 TLV1117LV33DCYR: 5V_SYS -> 3.3V AUX_3V3 | C9/C10 10uF X5R close to U4 | DCY tab = OUT", 250, 247),
    note("AUX_3V3 ALLOCATION: 300mA TOTAL = OLED 100mA + J6/J7 200mA COMBINED (NOT EACH). DEVKIT_3V3 IS NOT FOR EXTERNAL ACCESSORIES.", 155, 270),
    note("NORMAL: POWER_SW ON + JP1 CLOSED. USB SERVICE: POWER_SW OFF + JP1 OPEN WHEN ISOLATION IS DESIRED. GPIO IS NOT AUTOMATICALLY/COMPLETELY ISOLATED.", 155, 275),
    note("CARRIER ON + JP1 OPEN + DEVKIT UNPOWERED: POWERED PERIPHERALS MUST NOT ACTIVELY DRIVE GPIO (POLICY; NO EXTRA HW AUTHORIZED).", 155, 280),
    note("U4 LAYOUT REQUIREMENT: PAD2/TAB DIRECT TO >=20x20mm F.Cu AUX_3V3 + >=20x20mm B.Cu AUX_3V3, >=4 x 0.60/0.30mm vias within 3mm; pcb_layout_dfm must verify actual thermal result.", 155, 285),
    heading("A1. BATTERY SENSE (GPIO32 / ADC1_CH4)", 62, 242),
    note("BUCK_IN -> R3 10k 1% -> BAT_SENSE -> R4 3.3k 1% -> GND | C8 100nF BAT_SENSE-to-GND", 62, 247),
    heading("C. REMOVABLE ESP32 DEVKIT", 18, 52),
    note("30 PIN / 2x15   |   USB-C + CH340C ON MODULE", 18, 57),
    note("LEFT HEADER: J1                                      RIGHT HEADER: J2", 18, 62),
    note("USED: VIN via JP1, 3V3, GND | GPIO17/TX2, GPIO16/RX2, GPIO25/26/27, GPIO21/22, GPIO4, GPIO13/14/18/19/23/32/33", 18, 126),
    heading("D. E220-T22D UNIVERSAL SOCKET", 155, 70),
    note("E220-400T22D / E220-900T22D — user-installed module", 155, 75),
    heading("F. WS2812 STATUS LED", 260, 70),
    note("GPIO4 -> AHCT buffer -> DIN", 260, 75),
    heading("E. REMOVABLE OLED", 310, 150),
    note("0.96\" SSD1306 | 128x64 | I2C | USER INSTALLED", 310, 155),
    note("POWER INPUT: EXTERNALLY PROTECTED 2S LI-ION | 6.0 ... 8.4 V | NO CHARGER ON CARRIER PCB", 18, 18, 1.8),
    note("WARNING: TURN OFF / DISCONNECT BATTERY POWER BEFORE CONNECTING ESP32 DEVKIT USB-C TO A COMPUTER.", 18, 25, 1.8),
    note("ESP32 DEVKIT, E220 AND OLED ARE USER-INSTALLED MODULES.", 18, 32, 1.8),
    note("Inter-block links use net labels.  Local wires show the active power, bypass and interface support networks.", 18, 39),
    heading("G. USER EXPANSION", 215, 145),
    note("J6 USER_GPIO: 1 GND 2 GPIO13 3 GND 4 GPIO14 5 GND 6 GPIO18 7 GND 8 GPIO19 9 AUX_3V3 10 GPIO23", 215, 150),
    note("J7 DISPLAY_AUX: 1 GND 2 AUX_3V3 3 GPIO21/OLED_SDA 4 GPIO22/OLED_SCL 5 GPIO18 6 GPIO23 7 GPIO19 8 GPIO13 9 GPIO14 10 GPIO33 11 GND 12 AUX_3V3", 215, 155),
    note("J6/J7: user-install headers, PCBA DNP.  Direct nets only; no series/inline conditioning in this revision.", 215, 160),
    note("JP1 DEVKIT_PWR: 5V_SYS -> JP1.1 -> removable shunt -> JP1.2 -> DEVKIT_VIN -> J1.1", 18, 205),
    note("BAT+ -> F1 -> BAT_FUSED -> J8.1 -> EXTERNAL MECHANICAL SWITCH -> J8.2 -> BAT_SW -> Q1.3 -> BUCK_IN", 18, 210),
    note("                    |", 18, 214),
    note("                 D3 TVS", 18, 218),
    note("                    |", 18, 222),
    note("                   GND", 18, 226),
    note("U1 TPS62133RGT: C1 10uF input | C2 100nF AVIN | C4 3.3nF SS | L1 2.2uH | C3 22uF output", 115, 218),
    note("J5: 1 GND | 2 AUX_3V3 | 3 GPIO22/SCL | 4 GPIO21/SDA | R10/R11 4.7k DNP to AUX_3V3", 300, 205),
]

# Local wires: each endpoint already carries the same named net label, so these
# visual connections cannot alter the electrical source of truth.  They make
# power flow and local bypass/pull-down relationships inspectable in the PDF.
items += [
    # A. J4 -> PPTC -> external switch -> P-MOS; TVS and Q1 gate support are local.
    wire((20.32,153.67), (39.37,153.67)),
    wire((39.37,156.21), (59.69,156.21), (59.69,163.83)),
    wire((59.69,156.21), (80.01,168.91)),
    wire((80.01,154.94), (100.33,154.94), (100.33,182.88), (124.46,182.88)),
    # B. Buck input, AVIN bypass, switch/inductor/output and SS support.
    wire((100.33,182.88), (100.33,203.20)),
    wire((124.46,185.42), (119.38,185.42), (119.38,203.20)),
    wire((124.46,160.02), (180.34,160.02), (180.34,179.07)),
    wire((124.46,162.56), (180.34,162.56), (180.34,179.07)),
    wire((124.46,165.10), (180.34,165.10), (180.34,179.07)),
    wire((180.34,181.61), (180.34,203.20)),
    wire((124.46,180.34), (139.70,180.34), (139.70,203.20)),
    # D. E220 VCC bypass and immediately adjacent M0/M1 pull-downs.
    wire((170.18,110.49), (170.18,138.43)),
    wire((170.18,110.49), (190.50,110.49), (190.50,138.43)),
    wire((170.18,97.79), (209.55,97.79), (209.55,138.43)),
    wire((170.18,100.33), (229.87,100.33), (229.87,138.43)),
    # E. OLED I2C pins and optional DNP pull-up sites.
    wire((325.12,176.53), (314.96,176.53), (314.96,184.15)),
    wire((325.12,179.07), (294.64,179.07), (294.64,184.15)),
    # F. 3.3-V GPIO4 level buffer, local bypass and WS2812 DIN.
    wire((270.51,107.95), (300.00,107.95), (300.00,109.22), (320.04,109.22)),
    wire((270.51,110.49), (279.40,110.49), (279.40,138.43)),
]

body = "\n".join(items)
OUT.write_text(f'''(kicad_sch (version 20231120) (generator eeschema)
  (uuid {u()})
  (paper "A3")
  (title_block (title "ESP32 E220 LoRa Receiver — Rev.1 protected 2S battery carrier"))
  (lib_symbols
{chr(10).join(libs)}
  )
{body}
  (sheet_instances (path "/" (page "1")))
  (symbol_instances)
)
''')
SYMLIB.write_text("(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor)\n" + "\n".join(libs) + "\n)\n")
TABLE.write_text('''(sym_lib_table
  (version 7)
  (lib (name "Project")(type "KiCad")(uri "${KIPRJMOD}/esp32-e220.kicad_sym")(options "")(descr "Stage 5 modular-carrier project symbols"))
)
''')
print(OUT)
