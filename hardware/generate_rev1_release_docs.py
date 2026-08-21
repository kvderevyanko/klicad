#!/usr/bin/env python3
"""Generate Rev.1 release BOM/manifests/docs from production metadata and PCB."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_schematic_pcb_sync as sync

def fp_details():
    result = {}
    for fp in sync.forms(sync.sexp((HERE / "esp32-e220.kicad_pcb").read_text()), "footprint"):
        props = sync.prop_map(fp)
        ref = props.get("Reference")
        if not ref:
            continue
        at = sync.first(fp, "at") or [None, "0", "0", "0"]
        layer = (sync.first(fp, "layer") or [None, "F.Cu"])[1]
        pads = sync.forms(fp, "pad")
        result[ref] = {
            "footprint": fp[1], "x": at[1], "y": at[2],
            "rotation": at[3] if len(at) > 3 else "0",
            "side": "Top" if layer == "F.Cu" else "Bottom",
            "tht": any(len(pad) > 2 and pad[2] == "thru_hole" for pad in pads),
        }
    return result

def write_csv(path, fields, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, required=True)
    args = parser.parse_args()
    assembly, docs = args.release / "assembly", args.release / "documentation"
    metadata = json.loads((HERE / "production-metadata.json").read_text())["assembly_classes"]
    board, schematic = fp_details(), sync.symbols()
    populated = metadata["PCBA_POPULATE"]
    missing = set(populated) - set(board)
    if missing:
        raise SystemExit(f"metadata PCBA refs missing from board: {sorted(missing)}")

    groups = defaultdict(list)
    for ref, item in populated.items():
        detail = board[ref]
        value = schematic[ref]["properties"].get("Value", "")
        policy = item.get("procurement_policy", "EXACT_MPN")
        key = (value, item.get("manufacturer", ""), item.get("mpn", ""), detail["footprint"], policy)
        groups[key].append(ref)
    bom_rows = []
    for index, (key, refs) in enumerate(sorted(groups.items()), 1):
        value, manufacturer, mpn, footprint, policy = key
        bom_rows.append({"Item": index, "Qty": len(refs), "References": ", ".join(sorted(refs)),
                         "Value": value, "Manufacturer": manufacturer, "MPN": mpn,
                         "Footprint": footprint, "AssemblyClass": "PCBA_POPULATE",
                         "ProcurementPolicy": policy, "Notes": populated[refs[0]].get("description", "")})
    write_csv(assembly / "BOM_REV1.csv",
              ["Item", "Qty", "References", "Value", "Manufacturer", "MPN", "Footprint", "AssemblyClass", "ProcurementPolicy", "Notes"], bom_rows)

    actions = {
        "DNP_USER": ("DO NOT POPULATE HEADER", "User may solder header/wires or connect harness later"),
        "PLATED_TEST_HOLE": ("NO COMPONENT; retain plated probe hole", "Probe only"),
        "NO_FOOTPRINT_DNP": ("NO PCB FOOTPRINT", "Optional pull-up remains unpopulated"),
        "USER_INSTALLED_MODULE": ("NOT SUPPLIED/PLACED BY PCBA FACTORY", "User installs removable module"),
        "MANUAL_ACCESSORY": ("SUPPLY SEPARATELY; no PCB footprint", "Manual installation/accessory"),
        "MECHANICAL_NPTH": ("NO COMPONENT; fabricate NPTH hole", "Enclosure mounting point"),
    }
    rows = []
    for klass in ("DNP_USER", "PLATED_TEST_HOLE", "NO_FOOTPRINT_DNP", "USER_INSTALLED_MODULE", "MANUAL_ACCESSORY", "MECHANICAL_NPTH"):
        for ref, item in sorted(metadata[klass].items()):
            factory, user = actions[klass]
            rows.append({"Reference/Identifier": ref, "Class": klass,
                         "Description": item.get("description", item.get("net", "")),
                         "Factory action": factory, "User action": user})
    write_csv(assembly / "DNP_USER_MANIFEST.csv",
              ["Reference/Identifier", "Class", "Description", "Factory action", "User action"], rows)

    tht_rows = []
    pin_notes = {
        "J1":"ESP32 left socket; follow silkscreen", "J2":"ESP32 right socket; follow silkscreen",
        "J3":"E220 socket; PIN 1 / M0 silkscreen", "J4":"1=BAT+, 2=GND",
        "J5":"1=GND, 2=AUX_3V3, 3=SCL, 4=SDA", "J8":"external POWER SW",
        "JP1":"DEVKIT PWR header; shunt supplied separately"}
    for ref in sorted(populated):
        if board[ref]["tht"]:
            item = populated[ref]
            tht_rows.append({"Reference":ref, "Manufacturer":item.get("manufacturer", ""),
                             "MPN":item.get("mpn", ""), "Side":board[ref]["side"],
                             "Orientation / pin-1 note":pin_notes.get(ref, "Follow silkscreen"),
                             "Functional description":item.get("description", "Through-hole PCBA part")})
    write_csv(assembly / "THT_ASSEMBLY.csv",
              ["Reference", "Manufacturer", "MPN", "Side", "Orientation / pin-1 note", "Functional description"], tht_rows)

    raw_cpl = assembly / ".cpl-kicad.csv"
    if not raw_cpl.exists():
        raise SystemExit("missing direct KiCad SMD position export")
    with raw_cpl.open(newline="") as stream:
        direct_cpl = list(csv.DictReader(stream))
    smd_refs = {ref for ref in populated if not board[ref]["tht"]}
    if {row["Ref"] for row in direct_cpl} != smd_refs:
        raise SystemExit("direct KiCad CPL does not exactly match SMD PCBA metadata")
    cpl_rows = []
    for row in sorted(direct_cpl, key=lambda item: item["Ref"]):
        cpl_rows.append({"Designator": row["Ref"], "Mid X": row["PosX"], "Mid Y": row["PosY"],
                         "Layer": row["Side"], "Rotation": row["Rot"], "Value": row["Val"],
                         "Package": row["Package"]})
    write_csv(assembly / "CPL_SMD_REV1.csv",
              ["Designator", "Mid X", "Mid Y", "Layer", "Rotation", "Value", "Package"], cpl_rows)
    raw_cpl.unlink()

    (docs / "FAB_NOTES.md").write_text("""# Rev.1 fabrication notes

## Verified board

- Board: 145 x 90 mm
- Layers: 2
- Fabrication set: F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, Edge.Cuts, and Excellon drills.

## Recommended economical order parameters

- Material: FR-4
- Nominal thickness: 1.6 mm
- Outer copper: 1 oz (approximately 35 um)
- Solder mask: green
- Silkscreen: white
- Finish: lead-free HASL

These are order parameters, not encoded geometry. ENIG is acceptable if the
selected assembler recommends it for QFN assembly and its price impact is
acceptable. Rev.1 has no controlled-impedance requirement, castellations,
edge plating, blind vias, or buried vias.

## First-article notes

- Verify OLED mechanical/body fit on the actual module.
- Rev.1 has three M3 mounting holes: H1/H2/H3, each 3.20-mm NPTH with an 8-mm copper-free screw-head region. Enclosure/standoffs must respect these mechanical clearances.
- Battery strain relief is enclosure/harness responsibility.
- Visually/process inspect the U1 exposed-pad assembly.
- U4 operating temperature may be checked during first-article power validation.
- Prototype power-transient validation remains recommended.
""")
    (docs / "ASSEMBLY_NOTES.md").write_text("""# Rev.1 assembly notes

## Factory population

Factory populates all PCBA_POPULATE items, including carrier sockets J1/J2
(ESP32), J3 (E220), and J5 (OLED), and the JP1 header.

Factory does not populate J6 BUTTONS, J9 RGB, TP1...TP5, R10/R11, ESP32
DevKit, the E220 module, or the OLED module. TP1...TP5 are plated probe holes
only. The JP1 shunt is separate manual accessory SNT-100-BK-G, not a
pick-and-place footprint.

## Connector orientation

- J4 BATTERY: pad 1 = BAT+, pad 2 = GND.
- J8: external POWER SW connection.
- J5: GND, AUX_3V3, SCL, SDA.
- J6: GND, BTN1, BTN2, BTN3, BTN4, BTN5.
- J9: 5V, WS2812 DATA, GND.
- ESP32 USB-C/antenna orientation and E220 SMA/antenna orientation follow PCB silkscreen.

## JP1 service policy

- NORMAL: POWER_SW ON, JP1 CLOSED.
- USB SERVICE / carrier isolation: POWER_SW OFF, JP1 OPEN when isolation is required.

JP1 is not automatic power OR-ing.
""")
    (docs / "CPL_ROTATION_NOTES.md").write_text("""# CPL rotation notes

CPL_SMD_REV1.csv is KiCad's direct position export. Its X, Y, side, and
rotation are authoritative board-export values; do not remap angles to an
assembler convention without validating that assembler's import preview.

Orientation-sensitive SMT items include U1 TPS62133, U3 SN74AHCT1G125,
U4 TLV1117LV33, Q1 DMP3130LQ-7, and polarized/marked capacitors where the
assembler's library requires orientation. D3 SMBJ10CA is bidirectional and
F1 is non-polar. Use assembly-top.pdf and silkscreen-top.pdf to map any
vendor-specific rotation convention.
""")

if __name__ == "__main__":
    main()
