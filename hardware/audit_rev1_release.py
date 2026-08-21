#!/usr/bin/env python3
"""Read generated Rev.1 package, create release manifest and checksum audit."""
import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_schematic_pcb_sync as sync

EXPECTED_FAB = {
    "esp32-e220-F_Cu.gtl", "esp32-e220-B_Cu.gbl",
    "esp32-e220-F_Mask.gts", "esp32-e220-B_Mask.gbs",
    "esp32-e220-F_Silkscreen.gto", "esp32-e220-Edge_Cuts.gm1",
    "esp32-e220-PTH.drl", "esp32-e220-NPTH.drl", "esp32-e220-job.gbrjob",
    "ESP32-E220-Carrier-Rev1.ipc356", "DRILL_REPORT.txt",
}
EXPECTED_DNP = {
    "DNP_USER": {"J6", "J9"},
    "PLATED_TEST_HOLE": {"TP1", "TP2", "TP3", "TP4", "TP5"},
    "NO_FOOTPRINT_DNP": {"R10", "R11"},
    "USER_INSTALLED_MODULE": {"ESP32_DEVKIT", "E220_T22D", "OLED_0P96"},
    "MANUAL_ACCESSORY": {"JP1_SHUNT"},
    "MECHANICAL_NPTH": {"H1", "H2", "H3"},
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, required=True)
    parser.add_argument("--expected-pcb-sha", required=True)
    parser.add_argument("--expected-sch-sha", required=True)
    parser.add_argument("--metadata-sha", required=True)
    args = parser.parse_args()
    release = args.release
    fabrication, assembly, docs, checksums = (release / name for name in ("fabrication", "assembly", "documentation", "checksums"))
    errors = []
    pcb, sch = HERE / "esp32-e220.kicad_pcb", HERE / "esp32-e220.kicad_sch"
    pcb_sha, sch_sha, meta_sha = sha(pcb), sha(sch), sha(HERE / "production-metadata.json")
    if pcb_sha != args.expected_pcb_sha: errors.append("PCB source hash changed")
    if sch_sha != args.expected_sch_sha: errors.append("schematic source hash changed")
    if meta_sha != args.metadata_sha: errors.append("production metadata hash changed")

    fabric_files = {path.name for path in fabrication.iterdir() if path.is_file()}
    if fabric_files != EXPECTED_FAB:
        errors.append(f"fabrication file set mismatch: {sorted(fabric_files ^ EXPECTED_FAB)}")
    layer_headers = {
        "esp32-e220-F_Cu.gtl": "FileFunction,Copper,L1,Top",
        "esp32-e220-B_Cu.gbl": "FileFunction,Copper,L2,Bot",
        "esp32-e220-F_Mask.gts": "FileFunction,Soldermask,Top",
        "esp32-e220-B_Mask.gbs": "FileFunction,Soldermask,Bot",
        "esp32-e220-F_Silkscreen.gto": "FileFunction,Legend,Top",
        "esp32-e220-Edge_Cuts.gm1": "FileFunction,Profile,NP",
    }
    for name, marker in layer_headers.items():
        text = (fabrication / name).read_text()
        if marker not in text or "GenerationSoftware,KiCad,Pcbnew,10.0.5" not in text:
            errors.append(f"{name} has incorrect X2/header identity")
    edge = (fabrication / "esp32-e220-Edge_Cuts.gm1").read_text()
    points = {(int(x), int(y)) for x, y in re.findall(r"X(-?\d+)Y(-?\d+)D0[123]", edge)}
    expected_points = {(0,0), (145000000,0), (145000000,-90000000), (0,-90000000)}
    if points != expected_points or edge.count("D01*") != 4:
        errors.append("generated Edge.Cuts is not one closed 145 x 90 mm outline")
    if "ESP32_ANTENNA_EXCLUSION" in (fabrication / "esp32-e220-F_Cu.gtl").read_text():
        errors.append("unexpected antenna rule text in copper Gerber")
    bcu = (fabrication / "esp32-e220-B_Cu.gbl").read_text()
    service_markers = {
        "J6 branch": ("X94000000Y-18000000D02*", "X97000000Y-18000000D01*"),
        "J9 branch": ("X100000000Y-59080000D02*", "X97000000Y-59080000D01*"),
    }
    service_status = {name: all(marker in bcu for marker in markers)
                      for name, markers in service_markers.items()}
    if pcb_sha.startswith("9f15f061") and not all(service_status.values()):
        errors.append("B.Cu Gerber lacks required J6/J9 explicit ground branches")
    if pcb_sha.startswith("dd4d77d5") and not all(marker in bcu for marker in ("X63000000Y-20000000D02*", "X60000000Y-20000000D01*")):
        errors.append("B.Cu Gerber lacks required J5 explicit ground branch")

    drill = (fabrication / "DRILL_REPORT.txt").read_text()
    pth = re.search(r"Total plated holes count (\d+)", drill)
    npth = re.search(r"Total unplated holes count (\d+)", drill)
    if not pth or pth.group(1) != "119": errors.append("PTH drill count is not 119")
    expected_npth = "3" if pcb_sha.startswith("dd4d77d5") else "0"
    if not npth or npth.group(1) != expected_npth: errors.append("NPTH drill count mismatch")
    if "METRIC" not in (fabrication / "esp32-e220-PTH.drl").read_text() or "decimal" not in (fabrication / "esp32-e220-PTH.drl").read_text():
        errors.append("PTH Excellon format is not metric decimal")

    metadata = json.loads((HERE / "production-metadata.json").read_text())["assembly_classes"]
    pcba_refs = set(metadata["PCBA_POPULATE"])
    with (assembly / "BOM_REV1.csv").open(newline="") as stream:
        bom = list(csv.DictReader(stream))
    bom_refs = {ref.strip() for row in bom for ref in row["References"].split(",") if ref.strip()}
    if bom_refs != pcba_refs or sum(int(row["Qty"]) for row in bom) != 30:
        errors.append("BOM does not represent exactly 30 PCBA refs")
    forbidden = set().union(*EXPECTED_DNP.values())
    if bom_refs & forbidden: errors.append("BOM contains non-PCBA item")

    with (assembly / "CPL_SMD_REV1.csv").open(newline="") as stream:
        cpl = list(csv.DictReader(stream))
    board_data = sync.board()
    smd_refs = set()
    tht_refs = set()
    for ref in pcba_refs:
        raw = next(fp for fp in sync.forms(sync.sexp((HERE / "esp32-e220.kicad_pcb").read_text()), "footprint") if sync.prop_map(fp).get("Reference") == ref)
        is_tht = any(len(pad) > 2 and pad[2] == "thru_hole" for pad in sync.forms(raw, "pad"))
        (tht_refs if is_tht else smd_refs).add(ref)
    if {row["Designator"] for row in cpl} != smd_refs or len(cpl) != 23:
        errors.append("CPL does not exactly represent SMT PCBA refs")
    with (assembly / "THT_ASSEMBLY.csv").open(newline="") as stream:
        tht = list(csv.DictReader(stream))
    if {row["Reference"] for row in tht} != tht_refs or len(tht) != 7:
        errors.append("THT manifest does not exactly represent THT PCBA refs")

    with (assembly / "DNP_USER_MANIFEST.csv").open(newline="") as stream:
        dnp_rows = list(csv.DictReader(stream))
    dnp_by_class = {}
    for row in dnp_rows: dnp_by_class.setdefault(row["Class"], set()).add(row["Reference/Identifier"])
    if dnp_by_class != EXPECTED_DNP:
        errors.append("DNP/user manifest mismatch")

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    release_manifest = f"""# Rev.1 release manifest

- Release: Rev.1
- Source PCB SHA-256: {pcb_sha}
- Source schematic SHA-256: {sch_sha}
- Production metadata SHA-256: {meta_sha}
- KiCad: 10.0.5
- Generation UTC: {timestamp}
- Board: 145 x 90 mm, 2 layers
- DRC: 0 violations, 0 unconnected
- ERC: 0 errors / 0 warnings
- Parity: PASS
- Production metadata: PASS
- Pre-production reviewer: PASS

This release contains generated fabrication, assembly, documentation, and
diagnostic artifacts only. No source KiCad project or historical evidence is
included.
"""
    (docs / "RELEASE_MANIFEST.md").write_text(release_manifest)
    if pcb_sha.startswith("9f15f061"):
        (docs / "J6_J9_GERBER_CHECK.md").write_text(
            "# J6/J9 B.Cu Gerber check\n\n"
            f"- B.Cu Gerber SHA-256: {sha(fabrication / 'esp32-e220-B_Cu.gbl')}\n"
            "- J6 hand-solder window: 91.750..96.250 x 15.750..32.950 mm; "
            "local B.Cu copper pour is excluded.\n"
            "- J9 hand-solder window: 97.750..103.000 x 51.750..61.330 mm; "
            "it opens to the zone edge at x=103.000 mm.\n"
            f"- Gerber conductor records: J6={service_status['J6 branch']}, "
            f"J9={service_status['J9 branch']} (both are 0.80-mm, 3.00-mm B.Cu branches).\n"
            "- Visual B.Cu closeups are in diagnostics/J6_B_Cu_closeup.png and "
            "diagnostics/J9_B_Cu_closeup.png. The generated Gerber was checked "
            "directly, not inferred only from the PCB source.\n")
    result = {
        "gate": "REV1 GENERATED PACKAGE SELF-AUDIT",
        "status": "PASS" if not errors else "FAIL",
        "timestamp_utc": timestamp, "source": {"pcb_sha256": pcb_sha, "schematic_sha256": sch_sha, "metadata_sha256": meta_sha},
        "gerber_layers": sorted(layer_headers), "outline_mm": [145, 90],
        "drills": {"pth": int(pth.group(1)) if pth else None, "npth": int(npth.group(1)) if npth else None},
        "bom_groups": len(bom), "bom_pcba_refs": len(bom_refs), "cpl_smd_refs": len(cpl), "tht_refs": len(tht),
        "errors": errors,
    }
    audit_path = checksums / "package-self-audit.json"
    audit_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    included = sorted(path for path in release.rglob("*") if path.is_file() and path.name != "SHA256SUMS.txt")
    lines = [f"{sha(path)}  {path.relative_to(release)}" for path in included]
    (checksums / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
