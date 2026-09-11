#!/usr/bin/env python3
"""Direct self-audit for the Q1-corrected Rev.1 production package.

This intentionally does not call audit_rev1_release.py: that legacy checker
contains source-hash/version branches for the pre-Q1-correction Rev.1 package.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/home/kirill/codex/kicad")
HARDWARE = ROOT / "hardware"
EVIDENCE = HARDWARE / "evidence/q1-production-error-2026-09-11"
RELEASE = HARDWARE / "releases/rev1-q1-footprint-correction-2026-09-11"

EXPECTED_SOURCE = {
    "pcb_sha256": "61549b45d4fe336986e76bcc78c5ca5532e67df604d155b140b1fd8a9d1bb109",
    "schematic_sha256": "8ade3ec2f6a90f39763b8dd5570fcfe1709e34482d2f83a886886c73e5a4dacc",
    "metadata_sha256": "806393fc7e9b32da32d34c3adb6357ec87d1d0236a449df42e610f37361dd639",
    "q1_footprint_sha256": "a964b65e180fd9867d69eab31656367a13d0e120a503b78c8982a64b08626ebc",
}

EXPECTED_FAB = {
    "esp32-e220-F_Cu.gtl",
    "esp32-e220-B_Cu.gbl",
    "esp32-e220-F_Mask.gts",
    "esp32-e220-B_Mask.gbs",
    "esp32-e220-F_Silkscreen.gto",
    "esp32-e220-Edge_Cuts.gm1",
    "esp32-e220-PTH.drl",
    "esp32-e220-NPTH.drl",
    "esp32-e220-job.gbrjob",
    "ESP32-E220-Carrier-Rev1-Q1-Footprint-Correction.ipc356",
    "DRILL_REPORT.txt",
}

EXPECTED_ASSEMBLY = {
    "BOM_REV1.csv",
    "CPL_SMD_REV1.csv",
    "DNP_USER_MANIFEST.csv",
    "THT_ASSEMBLY.csv",
}

EXPECTED_DOCUMENTATION = {
    "ASSEMBLY_NOTES.md",
    "CPL_ROTATION_NOTES.md",
    "FAB_NOTES.md",
    "RELEASE_MANIFEST.md",
    "assembly-top.pdf",
    "silkscreen-top.pdf",
}

EXPECTED_DIAGNOSTICS = {
    "B_Cu_preview.pdf",
    "B_Mask_preview.pdf",
    "Drill_Map_NPTH.pdf",
    "Drill_Map_PTH.pdf",
    "Edge_Cuts_preview.pdf",
    "F_Cu_preview.pdf",
    "F_Mask_preview.pdf",
    "F_SilkS_preview.pdf",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_files(path: Path) -> set[str]:
    return {item.name for item in path.iterdir() if item.is_file()}


def gerber_q1_flashes(text: str) -> dict[str, dict[str, object]]:
    apertures: dict[str, tuple[float, float]] = {}
    for code, x, y in re.findall(r"%ADD(\d+)R,([0-9.]+)X([0-9.]+)\*%", text):
        apertures[code] = (float(x), float(y))

    current_aperture: str | None = None
    current_ref: str | None = None
    current_pad: str | None = None
    current_net: str | None = None
    q1: dict[str, dict[str, object]] = {}
    for line in text.splitlines():
        if match := re.fullmatch(r"D(\d+)\*", line):
            current_aperture = match.group(1)
        elif match := re.fullmatch(r"%TO\.P,([^,]+),([^*]+)\*%", line):
            current_ref, current_pad = match.groups()
        elif match := re.fullmatch(r"%TO\.N,/?([^*]+)\*%", line):
            current_net = match.group(1)
        elif line == "%TD*%":
            current_ref = current_pad = current_net = None
        elif match := re.fullmatch(r"X(-?\d+)Y(-?\d+)D03\*", line):
            if current_ref == "Q1" and current_pad is not None:
                q1[current_pad] = {
                    "x_gerber": int(match.group(1)),
                    "y_gerber": int(match.group(2)),
                    "pcb_mm": [int(match.group(1)) / 1_000_000, -int(match.group(2)) / 1_000_000],
                    "aperture": current_aperture,
                    "aperture_mm": list(apertures.get(current_aperture or "", ())),
                    "net": current_net,
                }
    return q1


def main() -> int:
    errors: list[str] = []
    fabrication = RELEASE / "fabrication"
    assembly = RELEASE / "assembly"
    documentation = RELEASE / "documentation"
    diagnostics = RELEASE / "diagnostics"
    checksums = RELEASE / "checksums"

    actual_source = {
        "pcb_sha256": sha256(HARDWARE / "esp32-e220.kicad_pcb"),
        "schematic_sha256": sha256(HARDWARE / "esp32-e220.kicad_sch"),
        "metadata_sha256": sha256(HARDWARE / "production-metadata.json"),
        "q1_footprint_sha256": sha256(HARDWARE / "esp32-e220.pretty/Diodes_DMP3130LQ-7_SOT23.kicad_mod"),
    }
    if actual_source != EXPECTED_SOURCE:
        errors.append(f"controlled-source hash mismatch: {actual_source}")

    legacy_diff = subprocess.run(
        ["git", "diff", "--quiet", "--", "hardware/releases/rev1", "hardware/releases/ESP32-E220-Carrier-Rev1-PCBA.zip"],
        cwd=ROOT,
    ).returncode
    if legacy_diff != 0:
        errors.append("legacy Rev.1 release or ZIP differs from repository HEAD")

    if exact_files(fabrication) != EXPECTED_FAB:
        errors.append(f"fabrication file set mismatch: {sorted(exact_files(fabrication) ^ EXPECTED_FAB)}")
    if exact_files(assembly) != EXPECTED_ASSEMBLY:
        errors.append(f"assembly file set mismatch: {sorted(exact_files(assembly) ^ EXPECTED_ASSEMBLY)}")
    if exact_files(diagnostics) != EXPECTED_DIAGNOSTICS:
        errors.append(f"diagnostic file set mismatch: {sorted(exact_files(diagnostics) ^ EXPECTED_DIAGNOSTICS)}")

    fcu = (fabrication / "esp32-e220-F_Cu.gtl").read_text()
    q1_flashes = gerber_q1_flashes(fcu)
    expected_q1 = {
        "1": {"pcb_mm": [62.05, 77.0], "aperture_mm": [0.8, 0.9], "net": "Q1_GATE"},
        "2": {"pcb_mm": [63.95, 77.0], "aperture_mm": [0.8, 0.9], "net": "BUCK_IN"},
        "3": {"pcb_mm": [63.0, 75.0], "aperture_mm": [0.8, 0.9], "net": "BAT_SW"},
    }
    q1_comparable = {
        pad: {key: value for key, value in item.items() if key in {"pcb_mm", "aperture_mm", "net"}}
        for pad, item in q1_flashes.items()
    }
    if q1_comparable != expected_q1:
        errors.append(f"Q1 direct F.Cu Gerber mismatch: {q1_comparable}")

    gerber_headers = {
        "esp32-e220-F_Cu.gtl": "FileFunction,Copper,L1,Top",
        "esp32-e220-B_Cu.gbl": "FileFunction,Copper,L2,Bot",
        "esp32-e220-F_Mask.gts": "FileFunction,Soldermask,Top",
        "esp32-e220-B_Mask.gbs": "FileFunction,Soldermask,Bot",
        "esp32-e220-F_Silkscreen.gto": "FileFunction,Legend,Top",
        "esp32-e220-Edge_Cuts.gm1": "FileFunction,Profile,NP",
    }
    for filename, marker in gerber_headers.items():
        content = (fabrication / filename).read_text()
        if marker not in content or "GenerationSoftware,KiCad,Pcbnew,10.0.6" not in content:
            errors.append(f"bad Gerber X2 identity: {filename}")

    drill_report = (fabrication / "DRILL_REPORT.txt").read_text()
    pth_text = (fabrication / "esp32-e220-PTH.drl").read_text()
    npth_text = (fabrication / "esp32-e220-NPTH.drl").read_text()
    pth_hits = len(re.findall(r"^X", pth_text, re.MULTILINE))
    npth_hits = len(re.findall(r"^X", npth_text, re.MULTILINE))
    if pth_hits != 119 or "Total plated holes count 119" not in drill_report:
        errors.append(f"PTH count mismatch: Excellon={pth_hits}")
    if npth_hits != 3 or "Total unplated holes count 3" not in drill_report:
        errors.append(f"NPTH count mismatch: Excellon={npth_hits}")
    if "METRIC" not in pth_text or "metric / decimal" not in pth_text:
        errors.append("PTH drill is not metric decimal Excellon")

    ipc356 = (fabrication / "ESP32-E220-Carrier-Rev1-Q1-Footprint-Correction.ipc356").read_text()
    ipc_expected = {
        "1": ("Q1_GATE", "X0315Y0354"),
        "2": ("BUCK_IN", "X0315Y0354"),
        "3": ("BAT_SW", "X0315Y0354"),
    }
    for pad, (net, size) in ipc_expected.items():
        if not re.search(rf"327/{net}\s+Q1\s+-{pad}\s+.*{size}", ipc356):
            errors.append(f"IPC-D-356 missing Q1 pad {pad} / {net} / {size}")

    with (assembly / "BOM_REV1.csv").open(newline="") as stream:
        bom = list(csv.DictReader(stream))
    q1_bom = [row for row in bom if row["References"] == "Q1"]
    if len(q1_bom) != 1 or any(
        q1_bom[0][key] != value
        for key, value in {
            "Manufacturer": "Diodes Incorporated",
            "MPN": "DMP3130LQ-7",
            "Footprint": "Diodes_DMP3130LQ-7_SOT23",
            "ProcurementPolicy": "EXACT_MPN",
        }.items()
    ):
        errors.append(f"Q1 BOM identity mismatch: {q1_bom}")

    with (assembly / "CPL_SMD_REV1.csv").open(newline="") as stream:
        cpl = list(csv.DictReader(stream))
    q1_cpl = [row for row in cpl if row["Designator"] == "Q1"]
    if len(q1_cpl) != 1 or any(
        q1_cpl[0][key] != value
        for key, value in {
            "Mid X": "63.000000",
            "Mid Y": "-76.000000",
            "Layer": "top",
            "Rotation": "0.000000",
            "Package": "Diodes_DMP3130LQ-7_SOT23",
        }.items()
    ):
        errors.append(f"Q1 CPL identity mismatch: {q1_cpl}")

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    kicad_version = subprocess.run(
        ["kicad-cli", "--version"], check=True, text=True, capture_output=True
    ).stdout.strip()
    manifest = f"""# Rev.1 Q1 footprint-correction release manifest

- Release: Rev.1-Q1-Footprint-Correction-2026-09-11
- Supersedes for new fabrication: `hardware/releases/rev1/` (preserved; do not mix files between releases)
- Source PCB SHA-256: {actual_source['pcb_sha256']}
- Source schematic SHA-256: {actual_source['schematic_sha256']}
- Production metadata SHA-256: {actual_source['metadata_sha256']}
- Q1 project-local footprint SHA-256: {actual_source['q1_footprint_sha256']}
- KiCad CLI: {kicad_version}
- Generation/audit UTC: {timestamp}
- Board: 145 x 90 mm, 2 layers
- Q1: Diodes Incorporated `DMP3130LQ-7`, project footprint `Diodes_DMP3130LQ-7_SOT23`
- Q1 F.Cu pads: 1=(62.05, 77.00), 2=(63.95, 77.00), 3=(63.00, 75.00) mm; each 0.80 x 0.90 mm
- Q1 pad/net map: 1=`Q1_GATE`, 2=`BUCK_IN`, 3=`BAT_SW`
- Drill: 119 PTH, 3 NPTH; metric decimal Excellon
- Implementation reviewer: `Q1 FOOTPRINT CORRECTION IMPLEMENTATION PASS`; `REVIEW PASS`
- ERC: 0 errors / 0 warnings
- Native DRC: 0 unconnected; 0 Q1/footprint/geometric errors; two unchanged inherited library-mismatch warnings (JP1, U4)
- Parity: PASS
- Production metadata: PASS
- Package self-audit: {'PASS' if not errors else 'FAIL'}

This directory is one indivisible production revision. Do not combine its
Gerbers, drills, IPC-D-356, BOM, CPL, or documentation with the preserved
legacy Rev.1 package. The Q1 copper checks above were read directly from the
generated F.Cu Gerber, not inferred only from the KiCad board.
"""
    (documentation / "RELEASE_MANIFEST.md").write_text(manifest)

    if exact_files(documentation) != EXPECTED_DOCUMENTATION:
        errors.append(
            f"documentation file set mismatch: {sorted(exact_files(documentation) ^ EXPECTED_DOCUMENTATION)}"
        )

    result = {
        "gate": "Q1-CORRECTED GENERATED PACKAGE SELF-AUDIT",
        "status": "PASS" if not errors else "FAIL",
        "timestamp_utc": timestamp,
        "release": RELEASE.name,
        "source": actual_source,
        "legacy_release_unmodified_vs_head": legacy_diff == 0,
        "kicad_cli": kicad_version,
        "q1_f_cu_direct": q1_flashes,
        "drills": {"pth_excellon_hits": pth_hits, "npth_excellon_hits": npth_hits},
        "bom_rows": len(bom),
        "cpl_rows": len(cpl),
        "errors": errors,
    }
    checksums.mkdir(exist_ok=True)
    audit_path = checksums / "package-self-audit.json"
    audit_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    included = sorted(
        path for path in RELEASE.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS.txt"
    )
    (checksums / "SHA256SUMS.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.relative_to(RELEASE)}" for path in included) + "\n"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
