#!/usr/bin/env python3
"""Generate the Stage 4 native KiCad schematic from verified connection data.

The S-expression layout is derived from KiCad's installed Arduino_Nano template
(KiCad 10 reads and rewrites it natively).  Run this script, then open/save the
result in eeschema before releasing the schematic for review.
"""
from pathlib import Path
from uuid import uuid4

OUT = Path(__file__).with_name("esp32-e220.kicad_sch")
SYMLIB = Path(__file__).with_name("esp32-e220.kicad_sym")
TABLE = Path(__file__).with_name("sym-lib-table")

def u(): return str(uuid4())
def s(v): return round(v / 0.635) * 0.635
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
    for i, (num, name) in enumerate(pins):
        y = (len(pins) - 1) * 1.27 - i * 2.54
        lines.append(f'''        (pin passive line (at -5.08 {y} 0) (length 3.81)
          (name "{name}" (effects (font (size 1.0 1.0))))
          (number "{num}" (effects (font (size 1.0 1.0))))
        )''')
    lines.append("      )\n    )")
    return "\n".join(lines)

def instance(libid, ref, value, x, y, pins, datasheet=""):
    x, y = s(x), s(y)
    lines = [f'''  (symbol (lib_id "{libid}") (at {x} {y} 0) (unit 1)
    (in_bom yes) (on_board yes)
    (uuid {u()})''', prop("Reference", ref, 0, x, y - 22, False),
             prop("Value", value, 1, x, y + 22, False),
             prop("Footprint", "", 2, x, y, True), prop("Datasheet", datasheet, 3, x, y, True)]
    for n, _ in pins: lines.append(f'    (pin "{n}" (uuid {u()}))')
    lines.append("  )")
    return "\n".join(lines)

def label(net, x, y):
    x, y = s(x), s(y)
    return f'''  (label "{net}" (at {x} {y} 0)
    (effects (font (size 1.27 1.27)) (justify left bottom))
    (uuid {u()})
  )'''

def no_connect(x, y):
    x, y = s(x), s(y)
    return f'''  (no_connect (at {x} {y}) (uuid {u()}))'''

def note(text, x, y):
    return f'''  (text "{text}" (at {x} {y} 0)
    (effects (font (size 1.5 1.5)) (justify left bottom))
    (uuid {u()})
  )'''

left = [("1","VIN / 5V"),("2","GND"),("3","GPIO13"),("4","GPIO12"),("5","GPIO14"),
        ("6","GPIO27"),("7","GPIO26"),("8","GPIO25"),("9","GPIO33"),("10","GPIO32"),
        ("11","GPIO35"),("12","GPIO34"),("13","GPIO39/VN"),("14","GPIO36/VP"),("15","EN")]
right = [("1","3V3"),("2","GND"),("3","GPIO15"),("4","GPIO2"),("5","GPIO4"),
         ("6","GPIO16/RX2"),("7","GPIO17/TX2"),("8","GPIO5"),("9","GPIO18"),("10","GPIO19"),
         ("11","GPIO21"),("12","GPIO3/RX0"),("13","GPIO1/TX0"),("14","GPIO22"),("15","GPIO23")]
e220 = [("1","M0"),("2","M1"),("3","RXD"),("4","TXD"),("5","AUX"),("6","VCC"),("7","GND")]
usb = [("1","VBUS"),("2","CC1"),("3","CC2"),("4","GND")]
tusb = [("1","CC1"),("2","CC2"),("3","PORT"),("4","VBUS_DET"),("5","ADDR"),("6","INT_N/OUT3"),
        ("7","SDA/OUT1"),("8","SCL/OUT2"),("9","ID"),("10","GND"),("11","EN_N"),("12","VDD")]
tps = [("1","GND"),("2","dVdt"),("3","EN/UVLO"),("4","IN"),("5","OUT"),("6","FLT"),("7","ILM"),("8","OVLO")]
r2 = [("1","1"),("2","2")]
q1 = [("1","B"),("2","C"),("3","E")]

libs = [
    libsym("Project:DevKit_Left_1x15", "J", "DEVKIT_LEFT_1x15", left, "User-verified left DevKit header; USB-C toward antenna"),
    libsym("Project:DevKit_Right_1x15", "J", "DEVKIT_RIGHT_1x15", right, "User-verified right DevKit header; USB-C toward antenna"),
    libsym("Project:E220_900T22D", "J", "E220-900T22D", e220, "EBYTE E220-900T22D, official pin definition"),
    libsym("Project:USB_C_POWER", "J", "USB-C power input", usb, "Power-only USB-C functional interface; connector PN USB4105-GF-A"),
    libsym("Project:TUSB320LAIRWBR", "U", "TUSB320LAIRWBR", tusb, "TI TUSB320LAI, 12-pin RWB pin functions"),
    libsym("Project:TPS259630DDAR", "U", "TPS259630DDAR", tps, "TI TPS259630, 8-pin DDA pin functions"),
    libsym("Project:R", "R", "R", r2, "Passive resistor"),
    libsym("Project:C", "C", "C", r2, "Passive capacitor"),
    libsym("Project:D", "D", "D", r2, "Diode"),
    libsym("Project:MMBT3904LT1G", "Q", "MMBT3904LT1G", q1, "onsemi NPN transistor"),
]

items = []
# Main modules.  Pin endpoint y values are calculated from the same simple
# stock-symbol geometry in libsym().
items += [instance("Project:DevKit_Left_1x15", "J1", "DEVKIT_LEFT (USB-C toward antenna)", 70, 80, left),
          instance("Project:DevKit_Right_1x15", "J2", "DEVKIT_RIGHT (USB-C toward antenna)", 70, 135, right),
          instance("Project:E220_900T22D", "J3", "E220-900T22D", 175, 105, e220,
                   "https://www.cdebyte.com/pdf-down.aspx?id=4221"),
          instance("Project:USB_C_POWER", "J4", "USB4105-GF-A", 25, 170, usb,
                   "https://gct.co/files/drawings/usb4105.pdf"),
          instance("Project:TUSB320LAIRWBR", "U1", "TUSB320LAIRWBR", 75, 190, tusb,
                   "https://www.ti.com/lit/ds/symlink/tusb320lai.pdf"),
          instance("Project:TPS259630DDAR", "U2", "TPS259630DDAR", 150, 190, tps,
                   "https://www.ti.com/lit/ds/symlink/tps2596.pdf")]

# Required eFuse support and fail-safe OUT1/Q1/EN network.
parts = [
    ("Project:D","D1","MMSD4148T1G",105,230,r2), ("Project:R","R1","900k 1%",75,230,r2),
    ("Project:R","R2","47k 0.1%",105,245,r2), ("Project:R","R3","47k 0.1%",125,245,r2),
    ("Project:R","R4","330k 0.1%",145,245,r2), ("Project:MMBT3904LT1G","Q1","MMBT3904LT1G",165,245,q1),
    ("Project:R","R5","909R 0.1%",175,230,r2), ("Project:R","R6","365k 0.1%",195,230,r2),
    ("Project:R","R7","100k 0.1%",215,230,r2), ("Project:C","C1","1uF 10V X7R",45,230,r2),
    ("Project:C","C2","100nF 16V X7R",65,245,r2), ("Project:C","C3","1uF 10V X7R",235,230,r2),
    ("Project:C","C4","3.3nF 50V C0G",195,245,r2), ("Project:C","C5","10uF 10V X5R",175,140,r2),
    ("Project:C","C6","100nF 16V X7R",195,140,r2),
]
for a,b,c,d,e,f in parts: items.append(instance(a,b,c,d,e,f))

# Only verified, required nets are labelled. Other DevKit pins are deliberately
# left open rather than tying them together through a fake NC net.
def py(base_y, count, n): return base_y - (count-1)*1.27 + (n-1)*2.54
for n, net in [(1,"5V_SYS"),(2,"GND"),(6,"E220_AUX"),(7,"E220_M1"),(8,"E220_M0")]:
    items.append(label(net, 64.92, py(80,15,n)))
for n in set(range(1,16)) - {1,2,6,7,8}:
    items.append(no_connect(64.92, py(80,15,n)))
for n, net in [(2,"GND"),(6,"E220_TXD"),(7,"E220_RXD")]:
    items.append(label(net, 64.92, py(135,15,n)))
for n in set(range(1,16)) - {2,6,7}:
    items.append(no_connect(64.92, py(135,15,n)))
for n, net in [(1,"E220_M0"),(2,"E220_M1"),(3,"E220_RXD"),(4,"E220_TXD"),(5,"E220_AUX"),(6,"5V_SYS"),(7,"GND")]:
    items.append(label(net, 169.92, py(105,7,n)))
for n, net in [(1,"VBUS_PRE"),(2,"CC1"),(3,"CC2"),(4,"GND")]:
    items.append(label(net, 19.92, py(170,4,n)))
for n, net in [(1,"CC1"),(2,"CC2"),(3,"GND"),(4,"VBUS_DET"),(5,"NC"),(6,"NC"),(7,"OUT1"),(8,"NC"),(9,"NC"),(10,"GND"),(11,"GND"),(12,"TUSB_VDD")]:
    items.append(label(net, 69.92, py(190,12,n)))
for n, net in [(1,"GND"),(2,"DVDT"),(3,"EFUSE_EN"),(4,"VBUS_PRE"),(5,"5V_SYS"),(6,"NC"),(7,"ILM"),(8,"OVLO")]:
    items.append(label(net, 144.92, py(190,8,n)))

# Passive net labels in pin order (both ends); visually explicit component values
# plus named nets make this a reviewable schematic without relying on hidden text.
for x,y,a,b in [(105,230,"VBUS_PRE","TUSB_VDD"),(75,230,"VBUS_PRE","VBUS_DET"),(105,245,"TUSB_VDD","OUT1"),
                (125,245,"OUT1","QBASE"),(145,245,"TUSB_VDD","EFUSE_EN"),(175,230,"ILM","GND"),
                (195,230,"VBUS_PRE","OVLO"),(215,230,"OVLO","GND"),(45,230,"VBUS_PRE","GND"),
                (65,245,"TUSB_VDD","GND"),(235,230,"5V_SYS","GND"),(195,245,"DVDT","GND"),
                (175,140,"5V_SYS","GND"),(195,140,"5V_SYS","GND")]:
    items += [label(a,x-5.08,y-1.27), label(b,x-5.08,y+1.27)]
# Q1: B, C, E.
items += [label("QBASE",159.92,py(245,3,1)), label("EFUSE_EN",159.92,py(245,3,2)), label("GND",159.92,py(245,3,3))]

items += [
    note("Stage 4 — main board only. DevKit USB-C programming and main-board USB-C power are mutually exclusive (approved Rev A policy).", 18, 20),
    note("No bare ESP32, 3V3 buck, EN/BOOT or programming circuit on this PCB. J1/J2 are the verified removable DevKit sockets.", 18, 26),
    note("E220: firmware drives M0/M1; no unverified external pull resistor. AUX is input-only, no pull-down.", 18, 32),
    note("TUSB320 UFP/GPIO: PORT=GND, ADDR=NC, EN_N=GND. OUT1/Q1 gates TPS259630: Default/detach OFF; Medium/High ON.", 18, 38),
    note("Pin-level Type-C and eFuse support components are documented with their official PNs and values. Footprints intentionally unassigned at schematic stage.", 18, 44),
]

body = "\n".join(items)
OUT.write_text(f'''(kicad_sch (version 20210126) (generator eeschema)
  (uuid {u()})
  (paper "A4")
  (title_block (title "ESP32 E220 LoRa Receiver — Stage 4"))
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
  (lib (name "Project")(type "KiCad")(uri "${KIPRJMOD}/esp32-e220.kicad_sym")(options "")(descr "Stage 4 verified project symbols"))
)
''')
print(OUT)
