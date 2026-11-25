# U4 project-local footprint identity handoff

`SCOPE STATUS: U4 SOURCE/METADATA IMPLEMENTATION COMPLETE — REVIEWER GATE REQUIRED`

This is an implementation status, not production approval. No commit, push, or
release archive was made.

## Cause and disposition

U4 referenced the mutable system-library identity
`Package_TO_SOT_SMD:SOT-223-3_TabPin2`. The embedded board copy is the legacy
rectangular-pad version, while the installed KiCad 10 library uses roundrect
pads and revised silk/pin-1 art. That visual/library-version drift generated the
remaining `lib_footprint_mismatch` warning even though copper centres and sizes,
F.Fab, F.CrtYd, placement, nets, and routing were unchanged.

The durable source is now generated as
`Carrier:TI_TLV1117LV33DCYR_DCY_SOT223` by
`hardware/generate_stage7_footprints.py`; the schematic assembly mapping in
`hardware/generate_esp32_e220.py`, active schematic, and active PCB use that
same identity. The new project-local footprint deliberately reproduces the
embedded active-board geometry rather than taking geometry from the changing
system KiCad library.

## Current / required / implemented delta

| Property | Pre-transaction | Required / implemented | Delta |
|---|---:|---:|---:|
| footprint identity | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` | `Carrier:TI_TLV1117LV33DCYR_DCY_SOT223` | metadata only |
| origin / rotation | `(20.65, 27.00) / 0 degrees` | same | `0 / 0 / 0` |
| pad 1 centre / size | `(-3.15,-2.30) / 2.00x1.50` | same | all `0 mm` |
| pad 2 lead centre / size | `(-3.15,0.00) / 2.00x1.50` | same | all `0 mm` |
| pad 2 tab centre / size | `(+3.15,0.00) / 2.00x3.80` | same | all `0 mm` |
| pad 3 centre / size | `(-3.15,+2.30) / 2.00x1.50` | same | all `0 mm` |
| pad shape/layers | rectangular, `F.Cu/F.Paste/F.Mask` | same | none |
| F.Fab bbox | `-1.85,-3.35 .. +1.85,+3.35` | same | none |
| F.CrtYd bbox | `-4.40,-3.60 .. +4.40,+3.60` | same | none |
| footprint/pad UUIDs | active checkpoint values | preserved | none |
| tracks / vias / zones | `202 / 58 / 4 copper zones` | same | none |

TI's DCY drawing MPDS094A/4202506/B gives body length 6.30..6.70 mm,
body width 3.30..3.70 mm, 2.30-mm lead pitch, 0.66..0.84-mm lead width,
minimum 0.75-mm lead length, and identifies the tab as pin 2. TI does **not**
give a recommended land pattern in the retained TLV1117LV datasheet. Therefore
this transaction resolves source reproducibility and the KiCad warning but does
not upgrade U4 to manufacturer-land-pattern PASS.

## Pin / pad / net mapping

| TI physical terminal | PCB land | Absolute centre (mm) | Net / function |
|---|---|---:|---|
| pin 1 | pad 1 | `(17.50,24.70)` | `GND` |
| pin 2 lead | pad 2 | `(17.50,27.00)` | `AUX_3V3` / OUT |
| pin 2 exposed tab | pad 2 | `(23.80,27.00)` | `AUX_3V3` / OUT |
| pin 3 | pad 3 | `(17.50,29.30)` | `5V_SYS` / IN |

## Verification

| Gate | Result | Evidence |
|---|---|---|
| pre-transaction fast contract | PASS | `00-pre-fast-contract.json` |
| scoped source/geometry invariant | PASS | `54-final-u4-invariant.json` |
| old system identity negative test | expected FAIL | `23-negative-old-metadata.json` |
| altered-pad negative test | expected FAIL | `24-negative-pad-geometry.json` |
| repeat footprint + schematic regeneration | byte-stable | `50-pre-repeat-regeneration.sha256`, `52-post-repeat-regeneration.sha256` |
| final fast board contract | PASS | `53-final-fast-contract.json` |
| native PCB DRC | PASS: 0 violations, 0 unconnected | `55-final-native-drc.json` |
| native schematic ERC | PASS: 0 violations | `56-final-native-erc.json` |
| schematic/PCB parity | PASS | `57-final-parity.json` |
| diagnostic Gerber comparison | PASS: copper/paste/mask/silk/fab numerically identical after volatile header removal | `35-diagnostic-export-audit.json` |
| diagnostic IPC-D-356 comparison | PASS: complete files byte-identical; U4 four records exact | `35-diagnostic-export-audit.json` |
| whitespace/error check | PASS | `58-git-diff-check.stdout` |

The native DRC category delta is exactly
`lib_footprint_mismatch: 1 -> 0`; geometric violations remain `0`, unconnected
items remain `0`, and no DRC exclusions or suppressions were added.

## Retained / deferred / failed

- Retained: all U4 physical geometry, placement, rotation, pad numbering,
  duplicate pad-2 lead/tab structure, nets, tracks, vias, zones, Fab/courtyard,
  paste/mask, and the existing pin-1 body chamfer.
- Deferred: a manufacturer land-pattern approval does not exist in the retained
  TI source. U4 remains **UNVERIFIED manufacturer land pattern / package-drawing
  compatible** until the separate IPC derivation is approved or a primary TI
  land-pattern source is found.
- Failed: none within this metadata/source transaction.

Next mandatory gate: independent `pcb_reviewer` implementation review.
