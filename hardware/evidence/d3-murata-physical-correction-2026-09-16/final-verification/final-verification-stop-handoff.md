# D3/Murata final-verification STOP handoff

Date: 2026-09-16

## SCOPE STATUS

`FINAL VERIFICATION STOPPED — REGRESSION CHECKER TOLERANCE DEFECT`

No production geometry, source, routing, via, zone, placement, net, or footprint
identity change was made by this verification activity.

## Verified checkpoint

- Retained Stage E parity: `PASS`; no production property mismatch.
- Retained Stage E scoped invariant: `PASS`; placements/rotations, tracks/vias,
  and zone outlines unchanged.
- Retained Stage E native DRC: zero violations and zero unconnected items.
- Pre-verification fast contract: `PASS` against the named pre-transaction
  reference with the approved transaction-scope contract.
- Two consecutive footprint-library and schematic regenerations are byte-stable.
  Pre-regeneration, pass-1, and pass-2 SHA-256 manifests are identical.
- The generated library, schematic, symbol library, and library tables are byte
  identical to the named pre-verification backup after regeneration.

## Stop condition

`hardware/check_d3_murata_footprints.py` returned `FAIL` only for embedded D3
non-copper drawing serialization:

- F.Fab expected `xmin=-2.2025`, active PCB serialized `xmin=-2.203`;
- F.CrtYd expected `xmin=-3.8`, active PCB parsed `xmin=-3.799999`.

The same report confirms exact generator-to-local footprint output, the intended
11-footprint allowlist, zero track deltas, zero via deltas, and unchanged zone
outlines. Pad geometry/nets did not fail. The defect is exact tuple equality in
`line_bbox()` validation instead of an explicit coordinate tolerance appropriate
for KiCad serialization.

## Retained evidence

- `00-pre-verification-fast-contract.json`
- `01-pre-regeneration-*.sha256`
- `02-pass1-*.sha256`
- `03-pass2-*.sha256`
- `04-scoped-invariant.json`
- `named-backup/`

## Required next action

Approve a checker-only correction that compares Fab/Courtyard bbox coordinates
with an explicit tolerance (recommended `0.001 mm`), then restart final
verification from the unchanged active design. Independent implementation review
remains pending. No commit, push, merge, release, Gerber, or IPC export was made.
