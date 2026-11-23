#!/usr/bin/python3
"""Cross-check PCBWAVE fabrication and assembly data against the source PCB."""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import pcbnew


def rows(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def position(item):
    point = item.GetPosition()
    return point.x, -point.y


def drill_hits(path):
    data = path.read_text()
    assert "absolute / metric / decimal" in data and "\nMETRIC\n" in data, path
    tools = {int(tool): round(float(size) * 1e6)
             for tool, size in re.findall(r"^T(\d+)C([\d.]+)$", data, re.M)}
    hits = Counter()
    tool = None
    for line in data.splitlines():
        selected = re.fullmatch(r"T(\d+)", line)
        hit = re.fullmatch(r"X(-?[\d.]+)Y(-?[\d.]+)", line)
        if selected:
            tool = int(selected[1])
        if hit:
            x, y = (round(float(v) * 1e6) for v in hit.groups())
            hits[(x, y, tools[tool])] += 1
    return hits


def source_drills(board):
    plated, non_plated = Counter(), Counter()
    for pad in board.GetPads():
        drill = pad.GetDrillSize()
        if drill.x:
            assert drill.x == drill.y, "unexpected slotted pad"
            hits = non_plated if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH else plated
            hits[(*position(pad), drill.x)] += 1
    for via in board.GetTracks():
        if isinstance(via, pcbnew.PCB_VIA):
            plated[(*position(via), via.GetDrillValue())] += 1
    return plated, non_plated


def stable_fabrication_data(path):
    if path.suffix == ".gbrjob":
        data = json.loads(path.read_text())
        data["Header"].pop("CreationDate", None)
        return data
    return [line for line in path.read_text().splitlines()
            if "CreationDate" not in line
            and not line.startswith(("G04 Created by KiCad", "; DRILL file KiCad"))
            and not re.search(r"(report date|created on|date:)", line, re.I)]


def gerber_flashes(path):
    apertures = {}
    flashes = defaultdict(set)
    selected = None
    for line in path.read_text().splitlines():
        definition = re.fullmatch(r"%ADD(\d+)(R|RoundRect),(.+)\*%", line)
        if definition:
            key, shape, dimensions = definition.groups()
            values = [float(v) for v in dimensions.split("X")]
            if shape == "R":
                width, height = values[:2]
            else:
                radius, *corners, rotation = values
                assert rotation == 0, line
                x, y = corners[::2], corners[1::2]
                width, height = max(x) - min(x) + 2 * radius, max(y) - min(y) + 2 * radius
            apertures[key] = (round(width * 1e6), round(height * 1e6))
        aperture = re.fullmatch(r"D(\d+)\*", line)
        if aperture:
            selected = aperture[1]
        flash = re.fullmatch(r"X(-?\d+)Y(-?\d+)D03\*", line)
        if flash and selected in apertures:
            flashes[(int(flash[1]), int(flash[2]))].add(apertures[selected])
    return flashes


def check_land_flashes(fabrication, board):
    refs = ("L1", "Q1", "R1", "R2", "R8", "R9", "U1", "U3", "U4")
    counts = {}
    for extension, layer in (("gtl", pcbnew.F_Cu), ("gtp", pcbnew.F_Paste)):
        path, = fabrication.glob(f"*.{extension}")
        flashes = gerber_flashes(path)
        checked = 0
        for ref in refs:
            for pad in board.FindFootprintByReference(ref).Pads():
                if not pad.IsOnLayer(layer):
                    continue
                width, height = pad.GetSizeX(), pad.GetSizeY()
                if layer == pcbnew.F_Paste:
                    margin = pad.GetSolderPasteMargin(layer)
                    width, height = width + 2 * margin.x, height + 2 * margin.y
                if round(pad.GetOrientationDegrees()) % 180 == 90:
                    width, height = height, width
                assert (width, height) in flashes[position(pad)], (path.name, ref, pad.GetNumber())
                checked += 1
        counts[extension] = checked
    return counts


def check_cpl(assembly, raw_path, smd_refs):
    mapping = {
        "Ref": "Designator", "PosX": "Mid X", "PosY": "Mid Y", "Rot": "Rotation",
        "Side": "Layer", "Val": "Value", "Package": "Package",
    }
    raw = rows(raw_path)
    cpl = rows(assembly / "CPL_SMD_REV1.csv")
    assert Counter(row["Designator"] for row in cpl) == Counter(smd_refs)
    assert sorted(cpl, key=lambda row: row["Designator"]) == sorted(
        ({label: row[key] for key, label in mapping.items()} for row in raw),
        key=lambda row: row["Designator"],
    ), "CPL data differs from independent direct KiCad export"


def check_assembly(assembly, metadata, board, raw_cpl):
    parts = metadata["PCBA_POPULATE"]
    bom = rows(assembly / "BOM_REV1.csv")
    refs = Counter()
    for row in bom:
        batch = [ref.strip() for ref in row["References"].split(",")]
        assert int(row["Qty"]) == len(batch)
        refs.update(batch)
        for ref in batch:
            assert row["MPN"] == parts[ref]["mpn"]
            assert row["Manufacturer"] == parts[ref]["manufacturer"]
            assert row["ProcurementPolicy"] == "EXACT_MPN"
    assert refs == Counter(parts.keys())
    tht = rows(assembly / "THT_ASSEMBLY.csv")
    tht_refs = {
        fp.GetReference() for fp in board.GetFootprints() if fp.GetReference() in parts
        and any(pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for pad in fp.Pads())
    }
    assert Counter(row["Reference"] for row in tht) == Counter(tht_refs)
    for row in tht:
        assert row["MPN"] == parts[row["Reference"]]["mpn"]
    check_cpl(assembly, raw_cpl, set(parts) - tht_refs)
    dnp = rows(assembly / "DNP_USER_MANIFEST.csv")
    assert Counter((row["Class"], row["Reference/Identifier"]) for row in dnp) == Counter(
        (klass, ref) for klass, members in metadata.items()
        if klass != "PCBA_POPULATE" for ref in members
    )
    return {"bom_placements": len(refs), "smd_placements": len(refs) - len(tht_refs),
            "tht_placements": len(tht_refs), "dnp_manifest_rows": len(dnp)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--repeat-export", type=Path, required=True)
    parser.add_argument("--pcb", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args()
    fabrication = args.release / "fabrication"
    file_functions = {
        "gtl": "Copper,L1,Top", "gbl": "Copper,L2,Bot", "gts": "Soldermask,Top",
        "gbs": "Soldermask,Bot", "gto": "Legend,Top", "gm1": "Profile,NP",
        "gtp": "Paste,Top",
    }
    for extension, function in file_functions.items():
        path, = fabrication.glob(f"*.{extension}")
        assert f"FileFunction,{function}" in path.read_text(), path
    for path in sorted(fabrication.iterdir()):
        if path.suffix in {*("." + ext for ext in file_functions), ".gbrjob", ".drl"}:
            assert stable_fabrication_data(path) == stable_fabrication_data(
                args.repeat_export / path.name
            ), f"repeat export differs for {path.name}"
    edge, = fabrication.glob("*.gm1")
    profile = edge.read_text()
    points = {(int(x), int(y)) for x, y in re.findall(r"X(-?\d+)Y(-?\d+)D0[12]", profile)}
    assert points == {(0, 0), (145000000, 0), (145000000, -90000000), (0, -90000000)}
    assert profile.count("D01*") == 4

    board = pcbnew.LoadBoard(str(args.pcb))
    metadata = json.loads(args.metadata.read_text())["assembly_classes"]
    plated, non_plated = source_drills(board)
    for key, expected in (("PTH", plated), ("NPTH", non_plated)):
        path, = fabrication.glob(f"*-{key}.drl")
        assert drill_hits(path) == expected, f"{key} diameter or location differs from source"
    report = check_assembly(args.release / "assembly", metadata, board,
                            args.repeat_export / "raw-cpl.csv")
    report.update({"status": "PASS", "gerber_layers": list(file_functions.values()),
                   "checked_pad_flashes": check_land_flashes(fabrication, board),
                   "outline_mm": [145, 90], "pth_drill_hits": plated.total(),
                   "npth_drill_hits": non_plated.total()})
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
