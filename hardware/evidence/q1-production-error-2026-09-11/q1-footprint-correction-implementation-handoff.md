# Q1 footprint correction: physical implementation handoff

## SCOPE STATUS

`Q1 FOOTPRINT CORRECTION IMPLEMENTED — IMPLEMENTATION REVIEW GATE REQUIRED`

The approved constrained physical transaction is complete. No Gerber, drill,
placement, BOM, or production-release package was generated.

## Controlled transaction

- Named checkpoint and implementation backup:
  `esp32-e220-q1-prechange-reference.kicad_pcb` and
  `esp32-e220-q1-implementation-backup.kicad_pcb`, both pre-change SHA-256
  `dd4d77d521adc1fd744d10b6e05f4a27169e30d988f70a3b9e50236608fda0e4`.
- Pre-change fast contract against the checkpoint: PASS.
- Post-change fast contract against the checkpoint: PASS.
- Explicit normalized whole-board delta proof: PASS. After normalizing only
  the approved Q1 description, pad-1/pad-2 centres, F.Fab/F.CrtYd endpoints,
  and the three named segment starts, the active board is semantically
  identical to the checkpoint. Pad properties and graphic/segment properties
  other than those coordinates are included in the equality check.
- The project-local Q1 footprint is byte-identical to the updated
  `dmp3130()` generator output. The stale whole-library generator was not run.

## Implemented geometry

Q1 remains on F.Cu at `(63.000, 76.000) mm`, rotation `0 deg`.

| Pad | Function/net | Local centre (mm) | Global centre (mm) | Size (mm) |
|---|---|---:|---:|---:|
| 1 | G / `Q1_GATE` | `(-0.950,+1.000)` | `(62.050,77.000)` | `0.80 x 0.90` |
| 2 | S / `BUCK_IN` | `(+0.950,+1.000)` | `(63.950,77.000)` | `0.80 x 0.90` |
| 3 | D / `BAT_SW` | `(0,-1.000)` | `(63.000,75.000)` | `0.80 x 0.90` |

The old lower-pad centre offset was `1.35 mm`; the corrected value is
`1.35 - 0.80/2 = 0.95 mm`, because Diodes dimension `X1` is measured to the
outer land edge. Lower-pad centre spacing changed from `2.70` to `1.90 mm`;
the copper envelope changed from `3.50 x 2.90` to `2.70 x 2.90 mm`.

- F.Fab: `x=[-0.65,+0.65]`, `y=[-1.45,+1.45]` mm
  (`1.30 x 2.90 mm`).
- F.CrtYd: `x=[-1.60,+1.60]`, `y=[-1.70,+1.70]` mm
  (`3.20 x 3.40 mm`).
- The existing clear silkscreen orientation/pin-1 marker was retained
  byte-identically.

## Bounded routing delta

Only these F.Cu segment starts changed; UUIDs, nets, downstream endpoints,
widths, and layers were preserved:

- `ce7bd062-9fb6-4c9c-8a39-64542cec1e84`, `Q1_GATE`, 0.25 mm:
  start `(62.050,77.000)`, end `(61.650,78.500)`.
- `a4eef94c-3eb6-420b-8595-5f49d55bb7bb`, `BUCK_IN`, 1.00 mm:
  start `(63.950,77.000)`, end `(65.500,77.000)`.
- `cb24be05-8b8c-4b70-b364-97c90cc107a3`, `BUCK_IN`, 1.00 mm:
  start `(63.950,77.000)`, end `(58.000,87.000)`.

The pad-3 `BAT_SW` segment, all vias, zones, rule areas, footprint origins,
and all non-Q1 copper remain unchanged. No subsection is deferred or failed.

## Verification and category delta

- Schematic/PCB parity: PASS; all mismatch arrays are empty.
- Native ERC: PASS, 0 errors and 0 warnings.
- Production metadata: PASS, no errors.
- Native DRC and in-memory zone-refilled DRC: 0 geometric violations and
  0 unconnected items. The in-memory refill did not change the board file
  (same before/after SHA-256
  `61549b45d4fe336986e76bcc78c5ca5532e67df604d155b140b1fd8a9d1bb109`).
- DRC normalized pre/post comparison: PASS. Both results contain exactly two
  inherited `lib_footprint_mismatch` warnings, JP1 and U4; Q1 has no library
  mismatch. There is no DRC category or count delta.
- Full deterministic wrapper: protected checkpoint and parity checks PASS,
  but overall status is FAIL solely because the wrapper treats the two
  inherited DRC warnings as violations. This is the expected baseline result,
  not an implementation regression.
- `git diff --check`: PASS.

`CONTEXT PROVENANCE CONFLICT`: `docs/agent-context.md` claims zero native DRC
violations, while both the actual pre-change and post-change KiCad 10.0.6 DRC
reports contain the two inherited JP1/U4 library-mismatch warnings. They are
not suppressed and were not changed in this scope.

## Changed source paths

- `hardware/esp32-e220.kicad_pcb`
- `hardware/esp32-e220.pretty/Diodes_DMP3130LQ-7_SOT23.kicad_mod`
- `hardware/generate_stage7_footprints.py`

New retained evidence and this handoff are under
`hardware/evidence/q1-production-error-2026-09-11/`.

## Retained / deferred / next gate

- Retained: Q1 pad numbers/nets, origin/rotation, pad 3, pad sizes, all
  downstream endpoints, widths/layers, vias, zones, and non-Q1 placement and
  copper.
- Deferred: production fabrication package generation, pending explicit user
  authorization after independent implementation review.
- Failed subsection: none. The inherited full-wrapper DRC status is disclosed
  above.
- Next required gate: independent `pcb_reviewer` implementation review.

SCOPE VERDICT: Q1 FOOTPRINT CORRECTION IMPLEMENTATION READY FOR REVIEW
