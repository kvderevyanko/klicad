# Independent JP1 implementation review

Reviewer role: `pcb_reviewer` (read-only).  Date: 2026-09-16.

## Scope and retained checkpoint

Reviewed only the JP1 `TSW-102-07-G-S` physical-footprint correction and the
explicit U4 warning deferral.  Retained pre-transaction checkpoint:
`10-esp32-e220.pre-jp1.kicad_pcb` and
`10-esp32-e220.pre-jp1.kicad_sch`.

## Primary physical evidence

Samtec's retained primary `primary/samtec-tsw-footprint.pdf` is headed
"RECOMMENDED P.C. BOARD LAYOUT FOR (X)TSW" and specifies, for the single-row
case, 0.100 in [2.54 mm] pitch and `.040 [1.02] DIA (TYP)`.  The retained
`primary/samtec-tsw-series-print.pdf` identifies the TSW family as
0.025 in [0.64 mm] square-post terminal strip assembly and defines single-row
body length `A = number of positions x 0.100 in [2.54 mm]`; thus this
two-position part has a 5.08-mm body length.

The active/project-local JP1 geometry is therefore numerically correct for
the manufacturer's specified land data:

| Check | Primary requirement | active / Gerber result | delta |
|---|---:|---:|---:|
| populated positions / pad numbers | 2 / 1,2 | 2 / 1,2 | 0 |
| pad centres | 2.540-mm pitch | local (0,0), (0,2.540); absolute (96.000,14.000), (98.540,14.000) mm | 0 |
| hole diameter | 1.020 mm typ | both PTH holes 1.020 mm; Excellon T3 at those two absolute centres | 0 |
| copper | no Samtec copper diameter specified | retained project annular-ring choice 1.700 x 1.700 mm | not claimed as manufacturer land dimension |
| body Fab | 2.54-mm single-row reference width; 5.08-mm two-position length | 2.54 x 5.08 mm | 0 |
| pin 1 orientation | first physical position | rectangular pad 1 and Fab/silkscreen pin-1 cue | correct |

## Independent machine evidence

- `hardware/check_board_contract.py`: all deterministic physical/topology
  checks PASS; the global result is FAIL exclusively because one U4
  `lib_footprint_mismatch` warning remains.  It has zero geometry, zone, or
  unconnected findings.
- `hardware/check_jp1_tsw_footprint.py`: PASS.  It proves exact Stage-7
  generator to project-local footprint identity, embedded identity and
  geometry, preserved JP1/pad UUIDs, exact schematic generator/active
  metadata, and no board change outside JP1 relative to the retained
  checkpoint.
- Independently rerun native checks: `70-review-native-drc.json` reports only
  U4 `lib_footprint_mismatch`, zero unconnected pads and zero footprint
  errors; `71-review-native-erc.json` reports 0 errors/0 warnings;
  `72-review-parity.json` is PASS with no electrical pad/net mismatch.
- `check_jp1_diagnostic_exports.py`: PASS.  Excellon T3 is 1.020 mm with two
  hits at (96.000,14.000) and (98.540,14.000) mm; Gerber copper is 1.700 mm
  with 2.540-mm pitch; IPC-D-356 maps JP1.1 to `/5V_SYS` and JP1.2 to
  `/DEVKIT_VIN`.
- Current controlled-file SHA-256 values equal the implementation handoff's
  `54-final-sha256.txt` values, so the reviewed evidence is the active state.

## Findings

- NOTE: The pre-correction 1.000-mm holes were 0.020 mm below the primary
  Samtec layout diameter.  The active corrected 1.020-mm holes remove that
  mismatch.
- MINOR: The remaining U4 library warning is outside this bounded JP1 scope;
  it is unsuppressed and remains a full-production-audit hold item.  It is
  not a JP1 physical or net/parity failure.

SCOPE VERDICT: JP1 PHYSICAL IMPLEMENTATION PASS

REVIEW PASS WITH MINOR ISSUES

The review approves only this JP1 corrective transaction.  It is not a
production-release or whole-board physical-audit approval.
