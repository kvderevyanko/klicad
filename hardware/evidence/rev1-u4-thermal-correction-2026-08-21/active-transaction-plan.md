# Rev.1 corrected U4 active-board transaction

## Authorization and gate

- Scope: reproduce the already-reviewed Rev.1 candidate from the approved
  pre-expansion baseline, changing only the U4 thermal subsection to the
  reviewed F.Cu-only 8 x 10 mm AUX_3V3 implementation.
- Plan gate: `SCOPE VERDICT: REV1 U4 THERMAL PLAN PASS`; `REVIEW PASS`.
- Baseline: `hardware/esp32-e220-pre-rev1-expansion.kicad_pcb`, SHA-256
  `d87c0ff900c9ce113c4c36b5a2785a65848077673e34804a8e9166cec2a6b76c`.
- Protected reference: the same approved pre-expansion baseline.
- Rollback source: the named pre-transaction active-board backup retained in
  this evidence directory.

## Bounded stages and expected native-DRC delta

| Stage | Functional subsection | Expected violations | Expected airwires |
| --- | --- | ---: | ---: |
| 1 | recovery/sync/antenna + J8/JP1 | 0 | 42 |
| 2 | U4/C9/C10 + corrected AUX_3V3 + J5 feed | 0 | 32 |
| 3 | J9 functional RGB output | 0 | 30 |
| 4 | E220 signals + R8/R9 | 0 | 21 |
| 5 | J6 BUTTONS | 0 | 15 |
| 6 | BAT_SENSE | 0 | 9 |
| 7 | GPIO4-to-U3 completion | 0 | 8 |

Every checkpoint must pass the fast board contract, parity, and native DRC
before and after activation. Any unexpected violation requires restoration of
the immediately preceding named backup, restored-state proof, and STOP.

## Thermal delta contract

- one F.Cu AUX_3V3 zone: X=22.0..30.0 mm, Y=22.0..32.0 mm;
- no B.Cu AUX_3V3 zone;
- zero AUX_3V3 thermal vias;
- 0.8-mm F.Cu pad-2 bridge `(17.5,27.0) -> (23.8,27.0)`;
- 0.8-mm F.Cu feed bridge `(30.0,22.54) -> (37.5,22.54)`;
- U4/C9/C10 placement unchanged from the reviewed candidate.

No schematic, electrical topology, major-module placement, feature scope, or
production-output transaction is authorized.
