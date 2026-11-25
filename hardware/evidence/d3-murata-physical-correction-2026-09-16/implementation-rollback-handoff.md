# D3 + Murata implementation transaction — rollback handoff

Role: `pcb_layout_dfm`, 2026-09-16.

## SCOPE STATUS

`ROLLED BACK — IMPLEMENTATION GATE NOT READY`

No D3/Murata correction remains in any controlled design/source file.  The
active PCB and all mutated source/local-footprint files were restored from the
named `implementation-backup/` checkpoint.  Unrelated `hardware/.history` was
not touched.

## Attempted reviewed geometry

The attempted footprint-only transaction used the approved plan geometry:
D3 `2.160 x 2.260 mm` at local `+/-2.450 mm`; C2/C4/C6/C7/C8
`.700 x .700 mm`; C5 `.750 x .900 mm`; C1/C9/C10 `1.200 x 1.300 mm`;
C3 `.700 x 1.300 mm`.  No component placement, segment, via, or zone outline
changed.  The prefill invariant recorded the exact target-footprint allowlist,
zero segment deltas, zero via deltas, and unchanged zone outlines.

## Rollback trigger

The first active prefill gate found an unexpected schematic/PCB property
parity failure.  The attempted transaction wrote C3/C5 board FPIDs with a
`Carrier:` prefix, while the reviewed schematic source used the same two new
identifiers without that prefix.  Connectivity and pad nets were unchanged,
but `production_property_mismatches` contained C3 and C5, so the transaction
was rolled back rather than repaired in place.

The native prefill DRC contained only the planned stale-fill C1 clearance
finding (`0.1755 mm` actual versus `0.2000 mm` required) and zero unconnected
items.  It was not retained on the active board.  The preliminary invariant
also exposed a comparison-tolerance defect: pcbnew serialized one D3
courtyard coordinate as `-3.799999 mm`; the intended geometry is `-3.800 mm`.

## Restored-state proof

* Active PCB SHA-256 equals the named backup:
  `27f5465e098d380c8a1bf440a8bb1b31f801d256076176c99eb956985394ee30`.
* Restored fast board contract: PASS.
* Restored full board contract: PASS.
* Restored native DRC: `0` violations, `0` unconnected.
* Restored custom schematic/PCB parity: PASS.

Retained reports are `rollback-10-restored-fast-contract.json`,
`rollback-11-restored-full-contract.json`,
`rollback-12-restored-native-drc.json`, and
`rollback-13-restored-parity.json`.  Failed-attempt controlled files and the
two generated MPN-specific footprints are recoverably retained under
`rollback-artifacts/`; they are not active sources.

## Required next transaction adjustment

Choose one exact canonical FPID spelling for C3/C5 and use it in schematic,
placement source, and embedded PCB.  The minimal correction is to keep the
reviewed unqualified identifiers in all three locations instead of adding the
board-only `Carrier:` prefix.  The invariant must compare Fab/courtyard
coordinates with a numerical tolerance suitable for pcbnew nanometre rotation
serialization.  A new baseline contract and named backup are required before
retrying the active transaction.
