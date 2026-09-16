# JP1 physical correction implementation handoff

Implementation transaction: 2026-09-16.  Scope was limited to JP1
`TSW-102-07-G-S`, its project-local source footprint, schematic footprint
metadata, and the embedded active-board footprint.  No electrical topology,
symbol, value, pin mapping, net, track, via, zone, rule area, other footprint,
or production package was changed.

## Cause and numeric correction

The active design assigned JP1 to a generic KiCad 1x02 header with 1.000-mm
holes.  Samtec's official TSW recommended PCB layout specifies 1.02-mm
(0.040-in) finished holes for the TSW series 0.635-mm square posts.  Package
name/pitch agreement had hidden the physical hole mismatch.

| Item | Pre-transaction | Samtec required / implemented | Delta |
|---|---:|---:|---:|
| pad count / numbering | 2 / 1,2 | 2 / 1,2 | none |
| local pad centres | (0,0), (0,2.54) mm | same | none |
| absolute pad centres | (96.000,14.000), (98.540,14.000) mm | same | none |
| pitch | 2.540 mm | 2.540 mm | none |
| copper | 1.700 x 1.700 mm | same reviewed project annular-ring choice | none |
| finished/drilled hole | 1.000 mm | 1.020 mm | +0.020 mm |
| body Fab envelope | 2.54 x 5.08 mm | 2.54 x 5.08 mm | none |

The body length follows the official TSW series rule `A = number of positions
x 2.54 mm`, so two positions give 5.08 mm; the single-row body width is
2.54 mm reference.  The 1.70-mm copper diameter is not represented as a
manufacturer recommendation: it is the retained project annular-ring choice.

Pin/net mapping is unchanged and exact:

- physical pin 1 -> pad 1 -> `/5V_SYS`;
- physical pin 2 -> pad 2 -> `/DEVKIT_VIN`.

## Source-of-truth repair

- Added `samtec_tsw_102_07_g_s()` and generated
  `esp32-e220.pretty/Samtec_TSW-102-07-G-S_1x02_P2.54mm_THT.kicad_mod`.
- Updated the schematic assembly contract and active schematic footprint field
  to `Carrier:Samtec_TSW-102-07-G-S_1x02_P2.54mm_THT`.
- Replaced the embedded generic JP1 footprint while preserving footprint and
  pad UUIDs, origin, rotation, pad centres, copper, nets, and all routing.
- Added `check_jp1_tsw_footprint.py`.  It proves generator/local exactness,
  schematic generator/active metadata exactness, embedded geometry/nets,
  preserved UUIDs, and a zero board delta outside JP1.  The retained old board
  fails the checker for identity and both 1.000-mm holes as expected.

The patched schematic generator was reproduced in the evidence directory and
is byte-identical to the active schematic.  Regenerating Stage 7 left the
previously corrected F1 and U3 local footprints byte-identical to their named
pre-JP1 backups.

## Gates and category delta

| Gate | Result | Evidence |
|---|---|---|
| pre-transaction fast contract | PASS | `00-pre-fast-contract.json` |
| named board/schematic/source backups and hashes | retained | `10-*`, `10-backup-sha256.txt` |
| immediate post fast contract | PASS | `30-post-fast-contract.json` |
| final fast contract | PASS | `64-final-fast-contract.json` |
| scoped JP1 invariant | PASS | `65-final-jp1-invariant.json` |
| old-geometry negative regression | expected FAIL | `33-negative-old-geometry-invariant.json` |
| native PCB DRC | one U4 warning, 0 unconnected | `40-native-drc.json` |
| native PCB DRC after zone refill on diagnostic copy | same | `44-native-refilled-drc.json` |
| native ERC | PASS, 0 violations | `41-native-erc.json` |
| authoritative project schematic/PCB parity | PASS | `42-parity.json` |
| full contract | global FAIL only on U4 library mismatch | `43-full-contract.json` |
| diagnostic Gerber/Excellon/IPC-D-356 audit | PASS | `53-diagnostic-export-audit.json` |
| whitespace check | PASS | `55-git-diff-check.stdout` |

The native DRC delta is exactly the expected removal of JP1's
`lib_footprint_mismatch`: 2 warnings before, 1 after.  The retained warning is
U4 only.  Geometric violations, zone errors, and unconnected items remain
zero.  The warning was not excluded or suppressed.

Diagnostic Excellon tool T3 is 1.020 mm with exactly two hits at
(96.000,-14.000) and (98.540,-14.000) in file coordinates.  IPC-D-356 emits
JP1.1 `/5V_SYS` and JP1.2 `/DEVKIT_VIN`, both `D0402`, with 1.699-mm serialized
copper and 2.540-mm centre pitch.  F.Cu and B.Cu Gerbers contain the expected
1.700-mm rectangular pin-1 and oval pin-2 flashes at those centres.  These are
retained diagnostic exports, not a production release.

`CONTEXT PROVENANCE CONFLICT`: `docs/agent-context.md` says the active board
has zero native DRC violations.  Actual pre-transaction KiCad data had two
unsuppressed library-mismatch warnings (JP1 and U4); actual post-transaction
data has one (U4).  Actual KiCad reports are authoritative.

## Handoff

SCOPE STATUS: JP1 PHYSICAL IMPLEMENTATION COMPLETE — REVIEW REQUIRED

- Active JP1: origin (96.000, 14.000), rotation 90 degrees, F.Cu.
- Critical geometry: two 1.700 x 1.700-mm PTH pads, 2.540-mm pitch,
  1.020-mm holes.
- Contract/parity/DRC delta: fast PASS; parity PASS; JP1 DRC warning removed;
  one explicit U4 warning remains; no other category/count delta.
- Retained subsection: JP1 correction, durable source, regression and
  diagnostic fabrication evidence.
- Deferred subsection: U4 warning resolution and remaining production audit.
- Failed subsection: none in JP1 scope; rollback was not triggered.
- Next gate: independent `pcb_reviewer` implementation review.

No commit, push, release directory, or ZIP was created.  This process status
is not production approval.
