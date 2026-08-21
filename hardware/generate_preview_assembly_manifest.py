#!/usr/bin/env python3
"""Generate a review-only Rev.1 assembly manifest; not a production BOM."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
metadata = json.loads((HERE / "production-metadata.json").read_text())
out = HERE / "evidence" / "rev1-preproduction-audit-2026-08-21" / "preview-assembly-manifest.json"
out.parent.mkdir(parents=True, exist_ok=True)
rows = []
for klass, items in metadata["assembly_classes"].items():
    for ref, item in sorted(items.items()):
        rows.append({"reference": ref, "assembly_class": klass, **item})
out.write_text(json.dumps({"kind":"REVIEW ONLY — NOT A PRODUCTION BOM OR CPL","rows":rows}, indent=2, sort_keys=True) + "\n")
print(out)
