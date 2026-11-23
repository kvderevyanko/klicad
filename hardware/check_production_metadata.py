#!/usr/bin/env python3
"""Read-only Rev.1 production-metadata consistency gate."""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_schematic_pcb_sync as sync

EXPECTED = {
    "PCBA_POPULATE": {"C1","C2","C3","C4","C5","C6","C7","C8","C9","C10","D3","F1","J1","J2","J3","J4","J5","J8","JP1","L1","Q1","R1","R2","R3","R4","R8","R9","U1","U3","U4"},
    "DNP_USER": {"J6","J9"},
    "PLATED_TEST_HOLE": {"TP1","TP2","TP3","TP4","TP5"},
    "NO_FOOTPRINT_DNP": {"R10","R11"},
    "MECHANICAL_NPTH": {"H1","H2","H3"},
    "USER_INSTALLED_MODULE": {"ESP32_DEVKIT", "E220_T22D", "OLED_0P96"},
    "MANUAL_ACCESSORY": {"JP1_SHUNT"},
}
ORDER_MPN = {
    "J1": "SSW-115-02-G-S", "J2": "SSW-115-02-G-S", "J3": "SSW-107-02-G-S",
    "J4": "B2B-XH-A", "J5": "SSW-104-02-G-S", "J8": "B2B-XH-A", "JP1": "TSW-102-07-G-S",
    "L1": "XGL4020-222MEC", "Q1": "DMP3130LQ-7",
    "R1": "RC0603FR-07100KL", "R2": "0603WAF1004T5E",
    "R8": "CRCW060310K0FKEA", "R9": "CRCW060310K0FKEA",
    "U1": "TPS62133RGTR", "U3": "SN74AHCT1G125DBVR", "U4": "TLV1117LV33DCYR",
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, default=HERE / "production-metadata.json")
    parser.add_argument("--pcb", type=Path, default=HERE / "esp32-e220.kicad_pcb")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.metadata.read_text())
    classes = data["assembly_classes"]
    actual = {name: set(items) for name, items in classes.items() if name in EXPECTED}
    board_refs = set(sync.board(args.pcb))
    sch = sync.symbols()
    errors = []
    if actual != EXPECTED:
        errors.append("assembly classification does not exactly match approved Rev.1 reference sets")
    if board_refs != (EXPECTED["PCBA_POPULATE"] | EXPECTED["DNP_USER"] | EXPECTED["PLATED_TEST_HOLE"] | EXPECTED["MECHANICAL_NPTH"]):
        errors.append("PCB references do not exactly match production metadata")
    for ref, mpn in ORDER_MPN.items():
        item = classes["PCBA_POPULATE"].get(ref, {})
        if item.get("mpn") != mpn or item.get("procurement_policy", "EXACT_MPN") != "EXACT_MPN":
            errors.append(f"{ref} must specify exact order MPN {mpn}")
    for ref in EXPECTED["PCBA_POPULATE"]:
        item = classes["PCBA_POPULATE"][ref]
        if not item.get("mpn") and item.get("procurement_policy") != "APPROVED_GENERIC":
            errors.append(f"{ref} lacks MPN or APPROVED_GENERIC policy")
    for ref in EXPECTED["PLATED_TEST_HOLE"]:
        if classes["PLATED_TEST_HOLE"][ref].get("purchased_component") is not False:
            errors.append(f"{ref} must not require a purchased component")
    for ref in EXPECTED["MECHANICAL_NPTH"]:
        if classes["MECHANICAL_NPTH"][ref].get("purchased_component") is not False:
            errors.append(f"{ref} must not require a purchased component")
    if {ref: classes["PLATED_TEST_HOLE"][ref]["net"] for ref in EXPECTED["PLATED_TEST_HOLE"]} != {"TP1":"BAT_PLUS","TP2":"GND","TP3":"BUCK_IN","TP4":"5V_SYS","TP5":"5V_SYS"}:
        errors.append("test-hole net policy mismatch")
    if any(ref in board_refs or sch[ref]["on_board"] for ref in EXPECTED["NO_FOOTPRINT_DNP"]):
        errors.append("R10/R11 are no-footprint DNP only")
    forbidden = {"D2","J7","TP6","TP7","TP8","TP9","TP10"}
    if forbidden & (board_refs | set(sch)):
        errors.append("removed reference present")
    result = {"gate":"REV1 PRODUCTION METADATA","status":"PASS" if not errors else "FAIL","class_counts":{name:len(items) for name,items in classes.items()},"errors":errors}
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output: args.output.write_text(rendered)
    print(rendered, end="")
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
