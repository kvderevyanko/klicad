#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/kirill/codex/kicad"
BOARD="$ROOT/hardware/esp32-e220.kicad_pcb"
EVIDENCE="$ROOT/hardware/evidence/q1-production-error-2026-09-11"
RELEASE="$ROOT/hardware/releases/rev1-q1-footprint-correction-2026-09-11"
ZIP="$ROOT/hardware/releases/ESP32-E220-Carrier-Rev1-Q1-Footprint-Correction-2026-09-11.zip"
FAB="$RELEASE/fabrication"
ASM="$RELEASE/assembly"
DOC="$RELEASE/documentation"
DIAG="$RELEASE/diagnostics"

EXPECTED_PCB_SHA="61549b45d4fe336986e76bcc78c5ca5532e67df604d155b140b1fd8a9d1bb109"

test ! -e "$RELEASE"
test ! -e "$ZIP"
test "$(sha256sum "$BOARD" | cut -d' ' -f1)" = "$EXPECTED_PCB_SHA"

mkdir -p "$FAB" "$ASM" "$DOC" "$DIAG" "$RELEASE/checksums"

kicad-cli pcb export gerbers \
  --output "$FAB" \
  --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,Edge.Cuts \
  --precision 6 \
  "$BOARD"

kicad-cli pcb export drill \
  --output "$FAB" \
  --format excellon \
  --excellon-units mm \
  --excellon-zeros-format decimal \
  --excellon-separate-th \
  --generate-map \
  --map-format pdf \
  --generate-report \
  --report-path "$FAB/DRILL_REPORT.txt" \
  "$BOARD"

mv "$FAB/esp32-e220-PTH-drl_map.pdf" "$DIAG/Drill_Map_PTH.pdf"
mv "$FAB/esp32-e220-NPTH-drl_map.pdf" "$DIAG/Drill_Map_NPTH.pdf"

kicad-cli pcb export ipcd356 \
  --output "$FAB/ESP32-E220-Carrier-Rev1-Q1-Footprint-Correction.ipc356" \
  "$BOARD"

kicad-cli pcb export pos \
  --output "$ASM/.cpl-kicad.csv" \
  --side both \
  --format csv \
  --units mm \
  --smd-only \
  --exclude-dnp \
  "$BOARD"

python3 "$ROOT/hardware/generate_rev1_release_docs.py" --release "$RELEASE"

kicad-cli pcb export pdf --mode-single --black-and-white \
  --output "$DOC/assembly-top.pdf" \
  --layers F.Fab,F.CrtYd,Edge.Cuts "$BOARD"
kicad-cli pcb export pdf --mode-single --black-and-white \
  --output "$DOC/silkscreen-top.pdf" \
  --layers F.Silkscreen,Edge.Cuts "$BOARD"

kicad-cli pcb export pdf --mode-single --black-and-white \
  --output "$DIAG/F_Cu_preview.pdf" --layers F.Cu,Edge.Cuts "$BOARD"
kicad-cli pcb export pdf --mode-single --black-and-white \
  --output "$DIAG/B_Cu_preview.pdf" --layers B.Cu,Edge.Cuts "$BOARD"
kicad-cli pcb export pdf --mode-single --black-and-white \
  --output "$DIAG/F_Mask_preview.pdf" --layers F.Mask,Edge.Cuts "$BOARD"
kicad-cli pcb export pdf --mode-single --black-and-white \
  --output "$DIAG/B_Mask_preview.pdf" --layers B.Mask,Edge.Cuts "$BOARD"
kicad-cli pcb export pdf --mode-single --black-and-white \
  --output "$DIAG/F_SilkS_preview.pdf" --layers F.Silkscreen,Edge.Cuts "$BOARD"
kicad-cli pcb export pdf --mode-single --black-and-white \
  --output "$DIAG/Edge_Cuts_preview.pdf" --layers Edge.Cuts "$BOARD"

test "$(sha256sum "$BOARD" | cut -d' ' -f1)" = "$EXPECTED_PCB_SHA"

python3 "$EVIDENCE/audit_q1_corrected_release.py"

(
  cd "$ROOT/hardware/releases"
  zip -X -r "$ZIP" "rev1-q1-footprint-correction-2026-09-11"
)
