#!/usr/bin/env python3
"""Build the read-only Rev.1 physical-plan candidate from the retained baseline.

The output must be a non-active PCB path.  The script imports the current
schematic netlist through the maintained parity checker and assigns every
physical pad instance sharing a pad number to the same canonical net.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[3]
HARDWARE = ROOT / "hardware"
BASELINE = HARDWARE / "esp32-e220-pre-rev1-expansion.kicad_pcb"
ACTIVE = HARDWARE / "esp32-e220.kicad_pcb"
LOCAL = HARDWARE / "esp32-e220.pretty"
STD = Path("/usr/share/kicad/footprints")
IU = pcbnew.FromMM


def load_sync_module():
    path = HARDWARE / "check_schematic_pcb_sync.py"
    spec = importlib.util.spec_from_file_location("rev1_sync", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(IU(x), IU(y))


def net(board: pcbnew.BOARD, name: str) -> pcbnew.NETINFO_ITEM:
    wanted = name if name.startswith("/") else "/" + name
    for item in board.GetNetsByNetcode().values():
        if item.GetNetname() == wanted:
            return item
    item = pcbnew.NETINFO_ITEM(board, wanted)
    board.Add(item)
    return item


def load_footprint(
    board: pcbnew.BOARD,
    directory: Path,
    library_name: str,
    reference: str,
    value: str,
    footprint_property: str,
    x: float,
    y: float,
    rotation: float = 0,
) -> pcbnew.FOOTPRINT:
    item = pcbnew.FootprintLoad(str(directory), library_name)
    if item is None:
        raise RuntimeError(f"cannot load {directory}/{library_name}")
    item.SetReference(reference)
    item.SetValue(value)
    if ":" in footprint_property:
        nickname, name = footprint_property.split(":", 1)
    else:
        nickname, name = "", footprint_property
    item.SetFPID(pcbnew.LIB_ID(nickname, name))
    item.SetPosition(point(x, y))
    item.SetOrientation(pcbnew.EDA_ANGLE(rotation, pcbnew.DEGREES_T))
    board.Add(item)
    return item


def all_pads(item: pcbnew.FOOTPRINT, number: str) -> list[pcbnew.PAD]:
    pads = [pad for pad in item.Pads() if pad.GetNumber() == str(number)]
    if not pads:
        raise RuntimeError(f"{item.GetReference() or item.GetValue()}: pad {number} missing")
    return pads


def one_pad(item: pcbnew.FOOTPRINT, number: str) -> pcbnew.PAD:
    pads = all_pads(item, number)
    if len(pads) != 1:
        raise RuntimeError(f"{item.GetReference()}: pad {number} has {len(pads)} physical instances")
    return pads[0]


def assign_all(item: pcbnew.FOOTPRINT, number: str, net_name: str, board: pcbnew.BOARD) -> None:
    canonical = net(board, net_name)
    for pad in all_pads(item, number):
        pad.SetNet(canonical)


def add_track(
    board: pcbnew.BOARD,
    net_name: str,
    start: tuple[float, float],
    end: tuple[float, float],
    width: float,
    layer: int = pcbnew.F_Cu,
) -> pcbnew.PCB_TRACK:
    item = pcbnew.PCB_TRACK(board)
    item.SetStart(point(*start))
    item.SetEnd(point(*end))
    item.SetWidth(IU(width))
    item.SetLayer(layer)
    item.SetNet(net(board, net_name))
    board.Add(item)
    return item


def add_via(board: pcbnew.BOARD, net_name: str, x: float, y: float, diameter: float = 0.60, drill: float = 0.30) -> pcbnew.PCB_VIA:
    item = pcbnew.PCB_VIA(board)
    item.SetPosition(point(x, y))
    item.SetWidth(IU(diameter))
    item.SetDrill(IU(drill))
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    item.SetNet(net(board, net_name))
    board.Add(item)
    return item


def remove_track_by_endpoints(board: pcbnew.BOARD, net_name: str, endpoints: set[tuple[float, float]]) -> None:
    wanted = net_name if net_name.startswith("/") else "/" + net_name
    for item in list(board.GetTracks()):
        if not isinstance(item, pcbnew.PCB_TRACK) or isinstance(item, pcbnew.PCB_VIA):
            continue
        if item.GetNetname() != wanted:
            continue
        start = (round(item.GetStart().x / 1e6, 3), round(item.GetStart().y / 1e6, 3))
        end = (round(item.GetEnd().x / 1e6, 3), round(item.GetEnd().y / 1e6, 3))
        if {start, end} == endpoints:
            board.Remove(item)


def add_polygon_zone(
    board: pcbnew.BOARD,
    net_name: str,
    layer: int,
    bounds: tuple[float, float, float, float],
    priority: int = 1,
) -> pcbnew.ZONE:
    xmin, ymin, xmax, ymax = bounds
    item = pcbnew.ZONE(board)
    item.SetNet(net(board, net_name))
    item.SetLayer(layer)
    item.SetAssignedPriority(priority)
    item.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    item.SetLocalClearance(IU(0.20))
    item.SetMinThickness(IU(0.25))
    outline = item.Outline()
    outline.NewOutline()
    for x, y in ((xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)):
        outline.Append(point(x, y))
    board.Add(item)
    return item


def add_antenna_rule_area(board: pcbnew.BOARD) -> pcbnew.ZONE:
    item = pcbnew.ZONE(board)
    item.SetIsRuleArea(True)
    item.SetZoneName("ESP32_ANTENNA_EXCLUSION")
    item.SetLayerSet(pcbnew.LSET.AllCuMask())
    item.SetDoNotAllowTracks(True)
    item.SetDoNotAllowVias(True)
    item.SetDoNotAllowZoneFills(True)
    item.SetDoNotAllowFootprints(True)
    item.SetDoNotAllowPads(True)
    outline = item.Outline()
    outline.NewOutline()
    for x, y in ((104.7, 52.0), (142.7, 52.0), (142.7, 90.0), (104.7, 90.0)):
        outline.Append(point(x, y))
    board.Add(item)
    return item


def add_mechanical_hole(board: pcbnew.BOARD, library_name: str, label: str, x: float, y: float) -> pcbnew.FOOTPRINT:
    item = load_footprint(board, LOCAL, library_name, "", label, library_name, x, y, 0)
    item.SetExcludedFromBOM(True)
    item.SetExcludedFromPosFiles(True)
    return item


def schematic_properties(sync_module) -> dict[str, dict[str, str]]:
    symbols = sync_module.symbols()
    refs = ("J6", "J7", "J8", "JP1", "R3", "R4", "C8", "U4", "C9", "C10")
    return {ref: symbols[ref]["properties"] for ref in refs}


def add_schematic_footprints(board: pcbnew.BOARD, props: dict[str, dict[str, str]]) -> dict[str, pcbnew.FOOTPRINT]:
    target_j8 = "JST_B2B-XH-A_1x02_P2.50mm_THT"
    j8_prop = props["J8"]["Footprint"]
    if j8_prop != target_j8:
        raise RuntimeError(
            "J8 schematic footprint is not the user-authorized compact XH selection: "
            f"{j8_prop!r}; expected {target_j8!r}"
        )

    specs = {
        "J6": (STD / "Connector_PinHeader_2.54mm.pretty", "PinHeader_2x05_P2.54mm_Vertical", 101.0, 26.0, 0),
        "J7": (STD / "Connector_PinHeader_2.54mm.pretty", "PinHeader_2x06_P2.54mm_Vertical", 43.0, 20.0, 0),
        "J8": (LOCAL, target_j8, 51.0, 76.0, 0),
        "JP1": (STD / "Connector_PinHeader_2.54mm.pretty", "PinHeader_1x02_P2.54mm_Vertical", 96.0, 14.0, 90),
        "R3": (LOCAL, "Resistor_0603_1608Metric", 85.0, 38.0, 0),
        "R4": (LOCAL, "Resistor_0603_1608Metric", 89.0, 38.0, 0),
        "C8": (LOCAL, "Murata_GRM188_1608Metric", 92.0, 38.0, 0),
        "U4": (STD / "Package_TO_SOT_SMD.pretty", "SOT-223-3_TabPin2", 20.65, 27.0, 0),
        "C9": (LOCAL, "Murata_GRM21_2012Metric", 17.5, 33.0, 270),
        "C10": (LOCAL, "Murata_GRM21_2012Metric", 14.4, 27.0, 180),
    }
    result = {}
    for ref, (directory, library_name, x, y, rotation) in specs.items():
        p = props[ref]
        result[ref] = load_footprint(
            board, directory, library_name, ref, p["Value"], p["Footprint"], x, y, rotation
        )
        if p.get("DNP") == "YES":
            result[ref].SetDNP(True)
    return result


def synchronize_connectivity(board: pcbnew.BOARD, footprints: dict[str, pcbnew.FOOTPRINT], sync_module) -> None:
    expected = sync_module.netlist()
    for footprint in board.GetFootprints():
        ref = footprint.GetReference()
        if not ref:
            continue
        for pad in footprint.Pads():
            name = expected.get((ref, pad.GetNumber()))
            if name and not name.startswith("unconnected-"):
                assign_all(footprint, pad.GetNumber(), name, board)

    # Explicit duplicate-instance release assertion before any copper work.
    u4_pad2 = all_pads(footprints["U4"], "2")
    if len(u4_pad2) != 2 or {pad.GetNetname() for pad in u4_pad2} != {"/AUX_3V3"}:
        raise RuntimeError(
            "DUPLICATE PAD NET ASSIGNMENT TOOLING BLOCKER: "
            f"U4 pad-2 physical instances={[(pad.GetNetname(), pad.GetPosition().x/1e6, pad.GetPosition().y/1e6) for pad in u4_pad2]}"
        )


def implement_power_geometry(board: pcbnew.BOARD, fp: dict[str, pcbnew.FOOTPRINT]) -> None:
    # J8 insertion: preserve the F1/D3 branch and replace only F1.2-to-Q1.3 copper.
    for edge in (
        {(47.138, 76.0), (50.5, 76.0)},
        {(50.5, 76.0), (50.5, 74.0)},
        {(50.5, 74.0), (60.0, 74.0)},
        {(60.0, 74.0), (63.0, 75.0)},
    ):
        remove_track_by_endpoints(board, "BAT_FUSED", edge)
    add_track(board, "BAT_FUSED", (47.138, 76.0), (51.0, 76.0), 1.0)
    add_track(board, "BAT_SW", (53.5, 76.0), (56.5, 76.0), 1.0)
    add_track(board, "BAT_SW", (56.5, 76.0), (60.0, 74.0), 1.0)
    add_track(board, "BAT_SW", (60.0, 74.0), (63.0, 75.0), 1.0)

    # JP1 reuses the accepted 5V_SYS vertical endpoint at (96,14).
    remove_track_by_endpoints(board, "5V_SYS", {(96.0, 14.0), (111.0, 14.0)})
    add_track(board, "DEVKIT_VIN", (98.54, 14.0), (111.0, 14.0), 1.0)

    # U4 local input/output/ground geometry and the reviewed thermal concept.
    add_track(board, "5V_SYS", (20.58, 43.5), (12.0, 41.0), 0.8)
    add_track(board, "5V_SYS", (12.0, 41.0), (12.0, 32.0), 0.8)
    add_track(board, "5V_SYS", (12.0, 32.0), (17.5, 32.0), 0.8)
    add_track(board, "5V_SYS", (17.5, 32.0), (17.5, 29.3), 0.8)
    add_track(board, "AUX_3V3", (15.4, 27.0), (17.5, 27.0), 0.8)

    add_track(board, "GND", (17.5, 24.7), (15.5, 24.7), 0.5)
    add_via(board, "GND", 15.5, 24.7)
    add_track(board, "GND", (13.4, 27.0), (12.0, 27.0), 0.5)
    add_via(board, "GND", 12.0, 27.0)
    add_track(board, "GND", (17.5, 34.0), (14.0, 34.0), 0.5)
    add_via(board, "GND", 14.0, 34.0)

    for x, y in ((25.3, 24.8), (25.3, 29.2), (26.5, 26.0), (26.5, 28.0)):
        add_via(board, "AUX_3V3", x, y)
    # Extend the existing B.Cu GND plane into the upper-left regulator region.
    # The higher-priority AUX_3V3 zone carves its dedicated thermal island while
    # the surrounding GND copper gives U4/C9/C10 short return paths and overlaps
    # the retained central B.Cu GND plane at X=42...44/Y=46...48.
    add_polygon_zone(board, "GND", pcbnew.B_Cu, (6.0, 10.0, 44.0, 48.0), priority=1)
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        add_polygon_zone(board, "AUX_3V3", layer, (17.5, 16.0, 37.5, 38.0), priority=2)


def build(source: Path, output: Path) -> None:
    source = source.resolve()
    output = output.resolve()
    if source != BASELINE.resolve():
        raise RuntimeError(f"source must be retained baseline {BASELINE}, got {source}")
    if output == ACTIVE.resolve() or output == source:
        raise RuntimeError("output must not be the active PCB or retained baseline")

    board = pcbnew.LoadBoard(str(source))
    if board is None:
        raise RuntimeError(f"cannot load {source}")
    sync_module = load_sync_module()
    props = schematic_properties(sync_module)
    footprints = add_schematic_footprints(board, props)
    synchronize_connectivity(board, footprints, sync_module)

    add_antenna_rule_area(board)
    implement_power_geometry(board, footprints)

    for library_name, label, x, y in (
        ("MountingHole_M3_NPTH", "H1 M3 NPTH", 7.0, 7.0),
        ("MountingHole_M3_NPTH", "H2 M3 NPTH", 80.0, 7.0),
        ("MountingHole_M3_NPTH", "H3 M3 NPTH", 7.0, 44.0),
        ("MountingHole_M3_NPTH", "H4 M3 NPTH", 101.0, 84.0),
        ("StrainRelief_NPTH_2p5mm", "SR1 CABLE TIE NPTH", 33.0, 84.0),
        ("StrainRelief_NPTH_2p5mm", "SR2 CABLE TIE NPTH", 40.0, 84.0),
    ):
        add_mechanical_hole(board, library_name, label, x, y)

    output.parent.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(output), board)
    print(f"source={source}")
    print(f"output={output}")
    print("U4_PAD2_PHYSICAL_INSTANCES=2")
    print("U4_PAD2_NET=/AUX_3V3")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=BASELINE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.source, args.output)


if __name__ == "__main__":
    main()
