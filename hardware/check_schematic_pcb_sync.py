#!/usr/bin/env python3
"""Machine-checkable schematic/PCB assembly and electrical sync gate.

Usage: python3 hardware/check_schematic_pcb_sync.py [--pcb BOARD.kicad_pcb] [--output REPORT.json]
The board is read only.  The schematic netlist is exported to a temporary file.
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCH = HERE / "esp32-e220.kicad_sch"
PCB = HERE / "esp32-e220.kicad_pcb"
USB_C_POWER_NETS = {"USB_VBUS", "USB_C_5V", "VBUS", "CC1", "CC2"}
ALLOWED_NON_PCB_DNP = {"R10", "R11"}


def tokenize(text):
    result, token, quoted, escape = [], [], False, False
    for char in text:
        if quoted:
            if escape:
                token.append(char)
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                result.append("".join(token)); token = []; quoted = False
            else:
                token.append(char)
        elif char == '"':
            if token: result.append("".join(token)); token = []
            quoted = True
        elif char in "()":
            if token: result.append("".join(token)); token = []
            result.append(char)
        elif char.isspace():
            if token: result.append("".join(token)); token = []
        else:
            token.append(char)
    if token: result.append("".join(token))
    return result


def sexp(text):
    root, stack = [], []
    for token in tokenize(text):
        if token == "(":
            node = []
            (stack[-1] if stack else root).append(node)
            stack.append(node)
        elif token == ")":
            stack.pop()
        else:
            (stack[-1] if stack else root).append(token)
    if stack: raise ValueError("unbalanced S-expression")
    return root[0]


def forms(node, head):
    return [item for item in node[1:] if isinstance(item, list) and item and item[0] == head]


def first(node, head, default=None):
    entries = forms(node, head)
    return entries[0] if entries else default


def prop_map(node):
    return {item[1]: item[2] for item in forms(node, "property") if len(item) > 2}


def symbols():
    data = sexp(SCH.read_text())
    result = {}
    def visit(node):
        if not isinstance(node, list): return
        if node and node[0] == "symbol" and first(node, "lib_id"):
            props = prop_map(node); ref = props.get("Reference")
            if ref:
                board = (first(node, "on_board") or [None, "yes"])[1]
                result[ref] = {"on_board": board == "yes", "properties": props}
        for item in node:
            if isinstance(item, list): visit(item)
    visit(data)
    return result


def board(pcb_path=PCB):
    data, result = sexp(pcb_path.read_text()), {}
    for fp in forms(data, "footprint"):
        props = prop_map(fp); ref = props.get("Reference")
        if not ref: continue
        pads = {}
        for pad in forms(fp, "pad"):
            net = first(pad, "net")
            if len(pad) > 1 and net and len(net) > 1: pads[pad[1]] = net[-1]
        result[ref] = {"footprint": fp[1], "properties": props, "pads": pads}
    return result


def netlist():
    with tempfile.TemporaryDirectory() as temp:
        out = Path(temp) / "netlist.net"
        subprocess.run(["kicad-cli", "sch", "export", "netlist", "--output", str(out), str(SCH)], check=True, capture_output=True, text=True)
        data = sexp(out.read_text())
    expected = {}
    nets = first(data, "nets", [])
    for net in forms(nets, "net"):
        name = (first(net, "name") or [None, ""])[1]
        for node in forms(net, "node"):
            ref = (first(node, "ref") or [None, ""])[1]
            pin = (first(node, "pin") or [None, ""])[1]
            expected[(ref, pin)] = name
    return expected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcb", type=Path, default=PCB, help="PCB to audit; defaults to active esp32-e220.kicad_pcb")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    sch, pcb, expected = symbols(), board(args.pcb), netlist()
    non_pcb = {ref: item for ref, item in sch.items() if not item["on_board"] and not ref.startswith("#")}
    assembled = {ref: item for ref, item in sch.items() if item["on_board"] and not ref.startswith("#")}
    result = {
        "gate": "SCHEMATIC-PCB ELECTRICAL PARITY",
        "contract": {
            "pcb": str(args.pcb),
            "pcb_net_name": "exact Eeschema root-sheet name, including leading '/'",
        },
        "counts": {"schematic_assembled": len(assembled), "pcb_footprints": len(pcb), "intentional_non_pcb": len(non_pcb)},
        "intentional_non_pcb": {ref: "NO_FOOTPRINT_DNP" for ref in sorted(non_pcb)},
        "unexpected_non_pcb_items": sorted(set(non_pcb) - ALLOWED_NON_PCB_DNP),
        "board_only_references": sorted(set(pcb) - set(assembled)),
        "missing_pcb_footprints": sorted(set(assembled) - set(pcb)),
        "production_property_mismatches": [],
        "electrical_pad_net_mismatches": [],
        "kicad_raw_net_name_mismatches": [],
        "usb_c_power_nets_present": [],
    }
    for ref in sorted(set(assembled) & set(pcb)):
        sp, bp = assembled[ref]["properties"], pcb[ref]
        for field, actual in (("Value", bp["properties"].get("Value", "")), ("Footprint", bp["footprint"])):
            if sp.get(field, "") != actual:
                result["production_property_mismatches"].append({"reference": ref, "field": field, "schematic": sp.get(field, ""), "pcb": actual})
        for pin, pcb_net in bp["pads"].items():
            sch_net = expected.get((ref, pin))
            if sch_net is None:
                result["electrical_pad_net_mismatches"].append({"reference": ref, "pad": pin, "schematic": None, "pcb": pcb_net})
            elif sch_net.lstrip("/") != pcb_net.lstrip("/"):
                result["electrical_pad_net_mismatches"].append({"reference": ref, "pad": pin, "schematic": sch_net, "pcb": pcb_net})
            if sch_net is not None and sch_net != pcb_net:
                result["kicad_raw_net_name_mismatches"].append({"reference": ref, "pad": pin, "schematic": sch_net, "pcb": pcb_net})
            if pcb_net in USB_C_POWER_NETS:
                result["usb_c_power_nets_present"].append({"reference": ref, "pad": pin, "net": pcb_net})
    result["non_pcb_dnp_errors"] = [ref for ref, item in non_pcb.items() if item["properties"].get("DNP") != "YES"]
    blockers = ["board_only_references", "missing_pcb_footprints", "production_property_mismatches", "electrical_pad_net_mismatches", "kicad_raw_net_name_mismatches", "usb_c_power_nets_present", "non_pcb_dnp_errors", "unexpected_non_pcb_items"]
    result["status"] = "PASS" if not any(result[key] for key in blockers) else "FAIL"
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output: args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
