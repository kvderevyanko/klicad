#!/usr/bin/env python3
"""Read-only integrity check of the final Q1-corrected release ZIP."""

from __future__ import annotations

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path


ROOT = Path("/home/kirill/codex/kicad")
HARDWARE = ROOT / "hardware"
RELEASE = HARDWARE / "releases/rev1-q1-footprint-correction-2026-09-11"
ARCHIVE = HARDWARE / "releases/ESP32-E220-Carrier-Rev1-Q1-Footprint-Correction-2026-09-11.zip"
PREFIX = RELEASE.name + "/"
EXPECTED_PCB_SHA = "61549b45d4fe336986e76bcc78c5ca5532e67df604d155b140b1fd8a9d1bb109"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def main() -> int:
    errors: list[str] = []
    audit = json.loads((RELEASE / "checksums/package-self-audit.json").read_text())
    if audit.get("status") != "PASS" or audit.get("errors"):
        errors.append("package self-audit is not PASS")

    expected_checksums: dict[str, str] = {}
    for line in (RELEASE / "checksums/SHA256SUMS.txt").read_text().splitlines():
        digest, relative = line.split("  ", 1)
        expected_checksums[relative] = digest
        if sha(RELEASE / relative) != digest:
            errors.append(f"release checksum mismatch: {relative}")

    release_files = {
        str(path.relative_to(RELEASE)): path
        for path in RELEASE.rglob("*")
        if path.is_file()
    }
    with zipfile.ZipFile(ARCHIVE) as archive:
        corrupt = archive.testzip()
        if corrupt:
            errors.append(f"ZIP CRC failure: {corrupt}")
        archive_files = {
            name.removeprefix(PREFIX): name
            for name in archive.namelist()
            if not name.endswith("/") and name.startswith(PREFIX)
        }
        if set(archive_files) != set(release_files):
            errors.append(
                f"ZIP/release file-set mismatch: {sorted(set(archive_files) ^ set(release_files))}"
            )
        unexpected_roots = [
            name for name in archive.namelist()
            if not name.startswith(PREFIX)
        ]
        if unexpected_roots:
            errors.append(f"ZIP has unexpected root entries: {unexpected_roots}")
        for relative, member in archive_files.items():
            if sha_bytes(archive.read(member)) != sha(release_files[relative]):
                errors.append(f"ZIP payload differs from release tree: {relative}")

    if sha(HARDWARE / "esp32-e220.kicad_pcb") != EXPECTED_PCB_SHA:
        errors.append("active PCB changed after package generation")
    legacy_diff = subprocess.run(
        ["git", "diff", "--quiet", "--", "hardware/releases/rev1", "hardware/releases/ESP32-E220-Carrier-Rev1-PCBA.zip"],
        cwd=ROOT,
    ).returncode
    if legacy_diff != 0:
        errors.append("legacy Rev.1 package changed")

    result = {
        "gate": "Q1-CORRECTED RELEASE ARCHIVE INTEGRITY",
        "status": "PASS" if not errors else "FAIL",
        "archive": str(ARCHIVE.relative_to(ROOT)),
        "archive_sha256": sha(ARCHIVE),
        "archive_bytes": ARCHIVE.stat().st_size,
        "payload_files": len(release_files),
        "checksummed_files": len(expected_checksums),
        "package_self_audit": audit.get("status"),
        "active_pcb_sha256": sha(HARDWARE / "esp32-e220.kicad_pcb"),
        "legacy_release_unmodified_vs_head": legacy_diff == 0,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
