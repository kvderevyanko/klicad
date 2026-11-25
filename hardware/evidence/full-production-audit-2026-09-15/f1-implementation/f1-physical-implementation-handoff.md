# F1 physical correction implementation handoff

Implementation transaction, 2026-09-16. Scope was limited to F1
`1812L200/16`, its reproducible project footprint, its active-board embedded
footprint, and the six route endpoints approved by the F1 physical plan. No
schematic, topology, connector, via, zone, rule-area, layer, or unrelated
footprint was changed. No production output was generated.

## Cause and numeric delta

The previous `fuse_1812()` source emitted an untraceable generic nominal
pattern and described it as `project IPC nominal`. It did not implement the
official Littelfuse 1812L Series Rev. GD `Pad Layout`. In that primary drawing,
F=1.78 mm is the land length, G=3.45 mm is the inner-edge gap (not centre
pitch), and H=3.15 mm is the land width. Therefore the required centre pitch
is F+G=5.23 mm.

| Item | Pre-transaction | Littelfuse required / implemented | Delta |
|---|---:|---:|---:|
| pad size | 1.125 x 3.400 mm | 1.780 x 3.150 mm | +0.655 x -0.250 mm |
| local pad centres | +/-2.138 mm serialized | +/-2.615 mm | outward 0.477 mm each |
| centre pitch | 4.276 mm serialized (4.275 source nominal) | 5.230 mm | +0.954 mm serialized |
| inner copper gap | 3.151 mm | 3.450 mm | +0.299 mm |
| F.Fab body | 4.50 x 3.20 mm | 4.55 x 3.24 mm midpoint | +0.05 x +0.04 mm |
| F.CrtYd | 5.50 x 4.20 mm | 7.10 x 4.24 mm | +1.60 x +0.04 mm |
| F1 origin | (45.000, 76.000) | (44.250, 76.000) | X -0.750 mm |
| absolute pad 1 | (42.862, 76.000) | (41.635, 76.000) | X -1.227 mm |
| absolute pad 2 | (47.138, 76.000) | (46.865, 76.000) | X -0.273 mm |

The implemented F.CrtYd is local X +/-3.55, Y +/-2.12. It contains the
manufacturer lands (X copper extent +/-3.505, 0.045-mm margin) and, at the
reviewed F1 origin, preserves 0.250 mm to each adjacent JST courtyard.

F1 is non-polarized. Numbering remains electrically controlled: pad 1 is
`/BAT_PLUS`; pad 2 is `/BAT_FUSED`. Pad UUIDs were retained.

## Implemented transaction

- Updated only `fuse_1812()` in `hardware/generate_stage7_footprints.py`.
- Regenerated `hardware/esp32-e220.pretty/Littelfuse_1812L200_16_4532Metric.kicad_mod`.
- Updated embedded F1 geometry and moved only F1 to (44.250, 76.000), 0
  degrees, F.Cu.
- Recentered exactly the six approved 1.00-mm F.Cu segment endpoints. The
  unchanged endpoints at J4.1, J8.1, D3.1, and TP1.1 remain fixed.
- Added `hardware/check_f1_1812l_footprint.py`. It checks
  generator-to-local exactness, embedded pads/Fab/courtyard/origin/nets,
  all non-F1 footprints, the six-segment allowlist, and unchanged
  vias/zones. `46-negative-old-geometry-invariant.json` proves that it rejects
  the complete old geometry.

The final controlled-board SHA-256 is
`3430e9a77797166cf4298c2d8b080766a62928f67be258cbda755dbd3824135a`,
identical to the independently reviewed plan candidate.

## Gates and exact category delta

| Gate | Result | Evidence |
|---|---|---|
| pre-transaction fast contract | PASS | `00-pre-fast-contract.json` |
| named backup and hashes | retained | `10-*`, `10-backup-sha256.txt` |
| immediate post fast contract | PASS | `21-post-fast-contract.json` |
| scoped F1 invariant | PASS | `44-final-f1-invariant-no-bytecode.json` |
| old-geometry negative regression | expected FAIL | `46-negative-old-geometry-invariant.json` |
| native PCB DRC, no refill | 2 known warnings, 0 unconnected | `30-native-drc.json` |
| native PCB DRC, in-memory refill | same | `31-native-refilled-drc.json` |
| native ERC | PASS, 0 violations | `32-native-erc.json` |
| schematic/PCB parity | PASS | `33-parity.json` |
| final fast contract | PASS | `48-final-fast-contract.json` |
| full board contract | global FAIL only on known warnings | `34-post-full-contract.json` |
| whitespace check | PASS | `47-git-diff-check.stdout` |

The DRC category/count delta from the audit baseline is exactly zero:
`lib_footprint_mismatch=2` at JP1 and U4 before and after, geometric
violations=0, zone errors=0, unconnected=0. These warnings were not
suppressed or reclassified. They remain production blockers outside this F1
transaction and require their separately scoped corrections/review.

## Handoff

SCOPE STATUS: F1 PHYSICAL IMPLEMENTATION COMPLETE — REVIEW REQUIRED

- Coordinates/rotation: F1 (44.250, 76.000), 0 degrees, F.Cu; pads at
  (41.635, 76.000) and (46.865, 76.000).
- Critical geometry: 1.780 x 3.150-mm lands, 5.230-mm centre pitch,
  F.CrtYd 7.10 x 4.24 mm.
- Contract/parity/DRC category delta: fast contract PASS; parity PASS; DRC
  zero category/count delta; full contract retains only the two outside-scope
  JP1/U4 warnings.
- Retained subsection: complete F1 correction and source-of-truth invariant.
- Deferred subsection: JP1/U4 warnings and the remaining full production
  audit.
- Failed subsection: none in F1 scope; rollback was not triggered.
- Next gate: independent `pcb_reviewer` implementation review.

This process status is not production approval.
