#!/usr/bin/env python3
"""Verify that the U4 metadata transaction leaves diagnostic exports unchanged."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRE = HERE / "diagnostic-pre"
POST = HERE / "diagnostic-post"
SUFFIXES = ["F_Cu.gtl", "F_Paste.gtp", "F_Mask.gts", "F_Silkscreen.gto", "F_Fab.gbr"]
EXPECTED_IPC = [
    ("/GND", "1", "+006890", "-009724", "0787", "0591"),
    ("/AUX_3V3", "2", "+006890", "-010630", "0787", "0591"),
    ("/AUX_3V3", "2", "+009370", "-010630", "0787", "1496"),
    ("/5V_SYS", "3", "+006890", "-011535", "0787", "0591"),
]


def one(directory: Path, suffix: str) -> Path:
    matches = list(directory.glob(f"*-{suffix}"))
    if len(matches) != 1:
        raise AssertionError(f"expected one *-{suffix} in {directory}, found {matches}")
    return matches[0]


def normalized_gerber(path: Path) -> bytes:
    lines = path.read_text(encoding="utf-8").splitlines()
    kept = [
        line for line in lines
        if not line.startswith("%TF.CreationDate,")
        and not line.startswith("%TF.ProjectId,")
        and not line.startswith("G04 Created by KiCad")
    ]
    return ("\n".join(kept) + "\n").encode("utf-8")


def u4_ipc(path: Path) -> list[tuple[str, str, str, str, str, str]]:
    pattern = re.compile(
        r"^327(?P<net>/\S+)\s+U4\s+-(?P<pad>\d+)\s+"
        r"A01X(?P<x>[+-]\d{6})Y(?P<y>[+-]\d{6})X(?P<sx>\d{4})Y(?P<sy>\d{4})"
    )
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            records.append(tuple(match.group(key) for key in ("net", "pad", "x", "y", "sx", "sy")))
    return records


failures: list[str] = []
layers: dict[str, dict[str, object]] = {}
for suffix in SUFFIXES:
    pre = normalized_gerber(one(PRE, suffix))
    post = normalized_gerber(one(POST, suffix))
    equal = pre == post
    if not equal:
        failures.append(f"normalized Gerber differs: {suffix}")
    layers[suffix] = {
        "equal_after_metadata_normalization": equal,
        "pre_sha256": hashlib.sha256(pre).hexdigest(),
        "post_sha256": hashlib.sha256(post).hexdigest(),
    }

pre_ipc_path = PRE / "esp32-e220-pre.d356"
post_ipc_path = POST / "esp32-e220-post.d356"
pre_ipc = pre_ipc_path.read_bytes()
post_ipc = post_ipc_path.read_bytes()
if pre_ipc != post_ipc:
    failures.append("full IPC-D-356 outputs differ")
pre_u4 = u4_ipc(pre_ipc_path)
post_u4 = u4_ipc(post_ipc_path)
if pre_u4 != EXPECTED_IPC:
    failures.append(f"pre U4 IPC records {pre_u4!r}")
if post_u4 != EXPECTED_IPC:
    failures.append(f"post U4 IPC records {post_u4!r}")

print(json.dumps({
    "status": "FAIL" if failures else "PASS",
    "scope": "diagnostic Gerber and IPC-D-356 equivalence across U4 identity-only transaction",
    "gerber_layers": layers,
    "ipc_d356_full_file_equal": pre_ipc == post_ipc,
    "u4_records_units": "IPC-D-356 inch fields (4 decimal places)",
    "u4_pre": pre_u4,
    "u4_post": post_u4,
    "failures": failures,
}, indent=2, sort_keys=True))

raise SystemExit(1 if failures else 0)
