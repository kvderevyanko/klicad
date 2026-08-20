#!/usr/bin/env python3
"""Build the fixed-module Rev.1 final-physical routing proof on a non-active copy."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parents[3]
HW = ROOT / "hardware"
BASE = HW / "esp32-e220-pre-rev1-expansion.kicad_pcb"
ACTIVE = HW / "esp32-e220.kicad_pcb"
LOCAL = HW / "esp32-e220.pretty"
STD = Path("/usr/share/kicad/footprints")
IU = pcbnew.FromMM


def sync_module():
    path = HW / "check_schematic_pcb_sync.py"
    spec = importlib.util.spec_from_file_location("scope_sync", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pt(x, y):
    return pcbnew.VECTOR2I(IU(x), IU(y))


def get_net(board, name):
    wanted = name if name.startswith("/") else "/" + name
    for item in board.GetNetsByNetcode().values():
        if item.GetNetname() == wanted:
            return item
    item = pcbnew.NETINFO_ITEM(board, wanted)
    board.Add(item)
    return item


def load_fp(board, directory, lib_name, ref, value, footprint, x, y, rotation=0):
    item = pcbnew.FootprintLoad(str(directory), lib_name)
    if item is None:
        raise RuntimeError(f"cannot load {directory}/{lib_name}")
    item.SetReference(ref)
    item.SetValue(value)
    nickname, name = footprint.split(":", 1) if ":" in footprint else ("", footprint)
    item.SetFPID(pcbnew.LIB_ID(nickname, name))
    item.SetPosition(pt(x, y))
    item.SetOrientation(pcbnew.EDA_ANGLE(rotation, pcbnew.DEGREES_T))
    board.Add(item)
    return item


def pads(item, number):
    result = [pad for pad in item.Pads() if pad.GetNumber() == str(number)]
    if not result:
        raise RuntimeError(f"{item.GetReference()}: missing pad {number}")
    return result


def pad(item, number):
    result = pads(item, number)
    if len(result) != 1:
        raise RuntimeError(f"{item.GetReference()}: expected one pad {number}, got {len(result)}")
    return result[0]


def assign_all(board, item, number, name):
    canonical = get_net(board, name)
    for physical in pads(item, number):
        physical.SetNet(canonical)


def track(board, name, a, b, width=0.25, layer=pcbnew.F_Cu):
    item = pcbnew.PCB_TRACK(board)
    item.SetStart(pt(*a)); item.SetEnd(pt(*b)); item.SetWidth(IU(width))
    item.SetLayer(layer); item.SetNet(get_net(board, name)); board.Add(item)
    return item


def path(board, name, points, width=0.25, layer=pcbnew.F_Cu):
    for a, b in zip(points, points[1:]):
        track(board, name, a, b, width, layer)


def via(board, name, x, y, diameter=0.60, drill=0.30):
    item = pcbnew.PCB_VIA(board)
    item.SetPosition(pt(x, y)); item.SetWidth(IU(diameter)); item.SetDrill(IU(drill))
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); item.SetNet(get_net(board, name)); board.Add(item)
    return item


def remove_edge(board, net_name, endpoints):
    wanted = net_name if net_name.startswith("/") else "/" + net_name
    for item in list(board.GetTracks()):
        if isinstance(item, pcbnew.PCB_VIA) or item.GetNetname() != wanted:
            continue
        a = (round(item.GetStart().x / 1e6, 3), round(item.GetStart().y / 1e6, 3))
        b = (round(item.GetEnd().x / 1e6, 3), round(item.GetEnd().y / 1e6, 3))
        if {a, b} == set(endpoints):
            board.Remove(item)


def zone(board, name, layer, points, priority):
    item = pcbnew.ZONE(board)
    item.SetNet(get_net(board, name)); item.SetLayer(layer); item.SetAssignedPriority(priority)
    item.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    item.SetLocalClearance(IU(0.20)); item.SetMinThickness(IU(0.25))
    outline = item.Outline(); outline.NewOutline()
    for x, y in points:
        outline.Append(pt(x, y))
    board.Add(item)
    return item


def antenna_rule(board):
    item = pcbnew.ZONE(board)
    item.SetIsRuleArea(True); item.SetZoneName("ESP32_ANTENNA_EXCLUSION")
    item.SetLayerSet(pcbnew.LSET.AllCuMask())
    item.SetDoNotAllowTracks(True); item.SetDoNotAllowVias(True)
    item.SetDoNotAllowZoneFills(True); item.SetDoNotAllowFootprints(True); item.SetDoNotAllowPads(True)
    outline = item.Outline(); outline.NewOutline()
    for xy in ((104.7, 52.0), (142.7, 52.0), (142.7, 90.0), (104.7, 90.0)):
        outline.Append(pt(*xy))
    board.Add(item)


def synchronize(board, module):
    expected = module.netlist()
    for footprint in board.GetFootprints():
        ref = footprint.GetReference()
        if not ref:
            continue
        for physical in footprint.Pads():
            name = expected.get((ref, physical.GetNumber()))
            if name and not name.startswith("unconnected-"):
                assign_all(board, footprint, physical.GetNumber(), name)


STAGES = (
    "sync-antenna",
    "j8-jp1",
    "u4-aux",
    "rgb",
    "e220",
    "buttons",
    "bat-sense",
    "final",
)


def build(source, output, stop_after="final", checkpoint_dir=None):
    if source.resolve() != BASE.resolve():
        raise RuntimeError(f"source must be {BASE}")
    if output.resolve() in {ACTIVE.resolve(), BASE.resolve()}:
        raise RuntimeError("active/baseline output forbidden")
    board = pcbnew.LoadBoard(str(source.resolve()))
    module = sync_module(); symbols = module.symbols()

    def save_checkpoint(stage):
        if checkpoint_dir is not None:
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            pcbnew.SaveBoard(str((checkpoint_dir / f"{stage}.kicad_pcb").resolve()), board)
        if stop_after != stage:
            return False
        output.parent.mkdir(parents=True, exist_ok=True)
        pcbnew.SaveBoard(str(output.resolve()), board)
        print(f"source={source.resolve()}")
        print(f"output={output.resolve()}")
        print(f"stage={stage}")
        return True

    # Current electrical source deletes these objects completely; no placeholders.
    for ref in ("D2", "TP6", "TP7", "TP8", "TP9", "TP10"):
        item = board.FindFootprintByReference(ref)
        if item is None:
            raise RuntimeError(f"baseline missing expected removable {ref}")
        board.Remove(item)

    specs = {
        "J6": (LOCAL, "PinHeader_1x06_P2.54mm_Vertical", 94.0, 18.0, 0),
        "J8": (LOCAL, "JST_B2B-XH-A_1x02_P2.50mm_THT", 51.0, 76.0, 0),
        "J9": (LOCAL, "PinHeader_1x03_P2.54mm_Vertical", 100.0, 54.0, 0),
        "JP1": (STD / "Connector_PinHeader_2.54mm.pretty", "PinHeader_1x02_P2.54mm_Vertical", 96.0, 14.0, 90),
        "R3": (LOCAL, "Resistor_0603_1608Metric", 86.0, 66.0, 0),
        "R4": (LOCAL, "Resistor_0603_1608Metric", 90.0, 66.0, 0),
        "C8": (LOCAL, "Murata_GRM188_1608Metric", 88.0, 69.0, 0),
        "U4": (STD / "Package_TO_SOT_SMD.pretty", "SOT-223-3_TabPin2", 20.65, 27.0, 0),
        "C9": (LOCAL, "Murata_GRM21_2012Metric", 17.5, 33.0, 270),
        "C10": (LOCAL, "Murata_GRM21_2012Metric", 14.4, 27.0, 180),
    }
    added = {}
    for ref, (directory, lib_name, x, y, rot) in specs.items():
        props = symbols[ref]["properties"]
        added[ref] = load_fp(board, directory, lib_name, ref, props["Value"], props["Footprint"], x, y, rot)
        if props.get("DNP") == "YES":
            added[ref].SetDNP(True)

    # The library-default reference fields for adjacent J6 and JP1 overlap.
    # Move only their text, leaving both footprint origins unchanged.
    j6_ref = added["J6"].Reference()
    j6_ref.SetPosition(pt(90.0, 22.0))
    j6_ref.SetTextAngle(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
    jp1_ref = added["JP1"].Reference()
    jp1_ref.SetPosition(pt(102.0, 14.0))
    jp1_ref.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))

    # R8/R9 are retained source items but moved out of the E220 route throat.
    for ref, x in (("R8", 40.0), ("R9", 46.0)):
        item = board.FindFootprintByReference(ref)
        item.SetPosition(pt(x, 35.0)); item.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))

    synchronize(board, module)
    if {p.GetNetname() for p in pads(added["U4"], "2")} != {"/AUX_3V3"}:
        raise RuntimeError("DUPLICATE PAD NET ASSIGNMENT TOOLING BLOCKER")
    antenna_rule(board)
    if save_checkpoint("sync-antenna"):
        return

    # J8: retain F1/D3 branch, replace only downstream F1-to-Q1 copper.
    for edge in (
        ((47.138, 76.0), (50.5, 76.0)), ((50.5, 76.0), (50.5, 74.0)),
        ((50.5, 74.0), (60.0, 74.0)), ((60.0, 74.0), (63.0, 75.0)),
    ):
        remove_edge(board, "BAT_FUSED", edge)
    path(board, "BAT_FUSED", [(47.138, 76.0), (51.0, 76.0)], 1.0)
    path(board, "BAT_SW", [(53.5, 76.0), (56.5, 76.0), (60.0, 74.0), (63.0, 75.0)], 1.0)

    # JP1 and DevKit VIN isolation.
    remove_edge(board, "5V_SYS", ((96.0, 14.0), (111.0, 14.0)))
    path(board, "DEVKIT_VIN", [(98.54, 14.0), (111.0, 14.0)], 1.0)
    if save_checkpoint("j8-jp1"):
        return

    # Upper B.Cu reference plane and U4 solid dual-layer thermal island.
    zone(board, "GND", pcbnew.B_Cu, [(6, 10), (104.4, 10), (104.4, 51.5), (44, 51.5), (44, 48), (6, 48)], 1)
    zone(board, "AUX_3V3", pcbnew.F_Cu, [(17.5, 16), (37.5, 16), (37.5, 38), (17.5, 38)], 2)
    zone(board, "AUX_3V3", pcbnew.B_Cu, [(17.5, 16), (37.5, 16), (37.5, 38), (17.5, 38)], 2)
    path(board, "5V_SYS", [(20.58, 43.5), (12, 41), (12, 32), (17.5, 32), (17.5, 29.3)], 0.8)
    path(board, "AUX_3V3", [(15.4, 27), (17.5, 27)], 0.8)
    path(board, "AUX_3V3", [(37.5, 22.54), (63.0, 22.54)], 0.8)
    for points in ([(17.5, 24.7), (15.5, 24.7)], [(13.4, 27), (12, 27)], [(17.5, 34), (14, 34)]):
        path(board, "GND", points, 0.5); via(board, "GND", *points[-1])
    for x, y in ((25.3, 24.8), (25.3, 29.2), (26.5, 26.0), (26.5, 28.0)):
        via(board, "AUX_3V3", x, y)
    if save_checkpoint("u4-aux"):
        return

    # J9 functional RGB output: power, level-shifted data, and ground.
    path(board, "5V_SYS", [(96, 43.5), (100, 43.5), (100, 54)], 1.0)
    path(board, "WS2812_DATA_5V", [(89.475, 53), (94, 51.5), (98, 54), (100, 56.54)], 0.25)
    path(board, "GND", [(100, 59.08), (97, 59.08)], 0.5); via(board, "GND", 97, 59.08)
    if save_checkpoint("rgb"):
        return

    # E220: five parallel F.Cu trunks above the protected y=43.5 power trunk.
    e220 = {
        "E220_M0": ((7.88, 53.5), (27.0, 39.2), 104.0, (111.0, 31.78)),
        "E220_M1": ((10.42, 53.5), (27.8, 39.9), 105.0, (111.0, 29.24)),
        "E220_RXD": ((12.96, 53.5), (28.6, 40.6), 108.5, (136.4, 29.24)),
        "E220_TXD": ((15.5, 53.5), (29.4, 41.3), 109.3, (136.4, 26.7)),
        "E220_AUX": ((18.04, 53.5), (30.2, 42.0), 100.5, (111.0, 26.7)),
    }
    bridge_x = {
        "E220_M0": (92.2, 97.0), "E220_M1": (92.9, 97.7),
        "E220_RXD": (93.6, 98.4), "E220_TXD": (94.3, 99.1),
        "E220_AUX": (95.0, 99.8),
    }
    for name, (source_pad, entry, xturn, target) in e220.items():
        left_x, right_x = bridge_x[name]
        path(board, name, [source_pad, entry], 0.25, pcbnew.B_Cu); via(board, name, *entry)
        path(board, name, [entry, (left_x, entry[1])], 0.25)
        via(board, name, left_x, entry[1])
        path(board, name, [(left_x, entry[1]), (right_x, entry[1])], 0.25, pcbnew.B_Cu)
        via(board, name, right_x, entry[1])
        if name == "E220_RXD":
            path(board, name, [(right_x, entry[1]), (xturn, entry[1]), (xturn, 30.51)], 0.25); via(board, name, xturn, 30.51)
            path(board, name, [(xturn, 30.51), (115, 30.51), (130, 30.51), (134, 29.24), target], 0.25, pcbnew.B_Cu)
        elif name == "E220_TXD":
            path(board, name, [(right_x, entry[1]), (xturn, entry[1]), (xturn, 27.97)], 0.25); via(board, name, xturn, 27.97)
            path(board, name, [(xturn, 27.97), (115, 27.97), (130, 27.97), (134, 26.7), target], 0.25, pcbnew.B_Cu)
        elif name == "E220_AUX":
            path(board, name, [(right_x, entry[1]), (xturn, entry[1])], 0.25)
            via(board, name, xturn, entry[1])
            path(board, name, [(xturn, entry[1]), (xturn, target[1]), target], 0.25, pcbnew.B_Cu)
        else:
            path(board, name, [(right_x, entry[1]), (xturn, entry[1]), (xturn, target[1])], 0.25); via(board, name, xturn, target[1])
            path(board, name, [(xturn, target[1]), target], 0.25, pcbnew.B_Cu)

    # M0/M1 local pull-downs sit above the five-lane trunk and return directly
    # into the new upper B.Cu GND reference plane.
    path(board, "E220_M0", [(39.275, 35.0), (39.275, 39.2)], 0.25)
    path(board, "E220_M1", [(45.275, 35.0), (44.0, 35.0)], 0.25); via(board, "E220_M1", 44.0, 35.0)
    path(board, "E220_M1", [(44.0, 35.0), (44.0, 39.9)], 0.25, pcbnew.B_Cu); via(board, "E220_M1", 44.0, 39.9)
    path(board, "GND", [(40.725, 35.0), (41.5, 35.0)], 0.25); via(board, "GND", 41.5, 35.0)
    path(board, "GND", [(46.725, 35.0), (47.5, 35.0)], 0.25); via(board, "GND", 47.5, 35.0)
    if save_checkpoint("e220"):
        return

    # BUTTONS J6: two left-header F.Cu branches and three B.Cu crossings to J2.
    path(board, "GND", [(94, 18), (104, 18), (111, 16.54)], 0.25, pcbnew.B_Cu)
    path(board, "GPIO13", [(94, 20.54), (98, 20.54)], 0.25, pcbnew.B_Cu); via(board, "GPIO13", 98, 20.54)
    path(board, "GPIO13", [(98, 20.54), (106, 20.54), (111, 19.08)], 0.25)
    path(board, "GPIO14", [(94, 23.08), (98, 23.08)], 0.25, pcbnew.B_Cu); via(board, "GPIO14", 98, 23.08)
    path(board, "GPIO14", [(98, 23.08), (106, 23.08), (111, 24.16)], 0.25)
    path(board, "GPIO18", [(94, 25.62), (106, 20.35), (115, 20.35)], 0.25, pcbnew.B_Cu); via(board, "GPIO18", 115, 20.35)
    path(board, "GPIO18", [(115, 20.35), (130, 32.0), (136.4, 34.32)], 0.25)
    path(board, "GPIO19", [(94, 28.16), (105.5, 22.89), (115, 22.89)], 0.25, pcbnew.B_Cu); via(board, "GPIO19", 115, 22.89)
    path(board, "GPIO19", [(115, 22.89), (130.5, 35.0), (136.4, 36.86)], 0.25)
    # GPIO23 crosses three existing orthogonal barriers with short alternating
    # layer bridges: 5V_SYS on F.Cu, E220_AUX on B.Cu, then E220_M1 on F.Cu.
    path(board, "GPIO23", [(94, 30.7), (99, 30.7)], 0.25, pcbnew.B_Cu); via(board, "GPIO23", 99, 30.7)
    path(board, "GPIO23", [(99, 30.7), (102.5, 30.7)], 0.25); via(board, "GPIO23", 102.5, 30.7)
    path(board, "GPIO23", [(102.5, 30.7), (102.5, 38.13), (118, 38.13)], 0.25, pcbnew.B_Cu); via(board, "GPIO23", 118, 38.13)
    path(board, "GPIO23", [(118, 38.13), (126, 43.0), (131, 47.0), (136.4, 49.56)], 0.25)
    if save_checkpoint("buttons"):
        return

    # OLED SDA/SCL fanout remains outside this proof: the controlling context
    # explicitly keeps the OLED mechanical datum/fanout pending.

    # BAT_SENSE divider/local bypass plus one B.Cu ADC endpoint route.
    path(board, "BUCK_IN", [(65.5, 70), (75, 70), (82, 66), (85.275, 66)], 0.25)
    path(board, "BAT_SENSE", [(86.725, 66), (89.275, 66)], 0.25)
    path(board, "BAT_SENSE", [(86.725, 66), (87.275, 69)], 0.25)
    path(board, "GND", [(90.725, 66), (90.725, 69), (88.725, 69)], 0.25)
    via(board, "GND", 90.725, 69)
    path(board, "BAT_SENSE", [(86.725, 66), (86.725, 63)], 0.25)
    via(board, "BAT_SENSE", 86.725, 63)
    path(board, "BAT_SENSE", [(86.725, 63), (96, 57), (96, 51), (120, 51), (120, 36.86), (111, 36.86)], 0.25, pcbnew.B_Cu)
    if save_checkpoint("bat-sense"):
        return

    # GPIO4 input to U3 and retained power test-point completion.
    path(board, "WS2812_DATA_3V3", [(136.4, 24.16), (133.5, 24.16), (130, 10), (105, 10)], 0.25)
    via(board, "WS2812_DATA_3V3", 105, 10)
    path(board, "WS2812_DATA_3V3", [(105, 10), (90, 10), (90, 50), (89, 58)], 0.25, pcbnew.B_Cu)
    via(board, "WS2812_DATA_3V3", 89, 58)
    path(board, "WS2812_DATA_3V3", [(89, 58), (89, 55)], 0.25)

    output.parent.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(output.resolve()), board)
    if checkpoint_dir is not None:
        pcbnew.SaveBoard(str((checkpoint_dir / "final.kicad_pcb").resolve()), board)
    print(f"source={source.resolve()}")
    print(f"output={output.resolve()}")
    print("fixed=J1,J2,J3,J5")
    print("removed=D2,TP6,TP7,TP8,TP9,TP10")
    print("U4_PAD2=/AUX_3V3,/AUX_3V3")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=BASE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stop-after", choices=STAGES, default="final")
    parser.add_argument("--checkpoint-dir", type=Path)
    args = parser.parse_args(); build(args.source, args.output, args.stop_after, args.checkpoint_dir)


if __name__ == "__main__":
    main()
