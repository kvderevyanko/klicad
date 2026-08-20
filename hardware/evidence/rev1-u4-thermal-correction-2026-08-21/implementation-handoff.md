# Rev.1 corrected U4 active-board implementation handoff

## SCOPE STATUS

`REV1 U4 THERMAL-CORRECTED ACTIVE IMPLEMENTATION COMPLETE — PCB READY FOR INDEPENDENT IMPLEMENTATION REVIEW`

The reviewed Rev.1 transaction was reproduced from the approved clean
pre-expansion baseline and activated in seven bounded checkpoints. The active
PCB was never used for placement search or alternate thermal experiments.

- Active PCB SHA-256: `4f6fba9ed19c3f0290842b62f3ec087d28e3911c7d12f31d2e581aa1c8e26650`.
- Final active PCB is byte-identical to `16-stage7-final.kicad_pcb`.
- The final active board is semantically identical to reviewed candidate
  `c492d1254e0ef19c95fe6a38357b1f93a4fc85c93c536a4da94afaf2f2e7e3de`
  for footprint/pad placement, tracks/vias, and zone/rule-area outlines.
- Named original active backup: `17-active-pre-transaction.kicad_pcb`, SHA-256
  `bf502dfde6ebb1f05d5d8f95fa77dc6f3d484fd9ddcdb47d3511c4b82b5f5036`.

An initial stage-1 activation was conservatively restored byte-for-byte after
KiCad's `--exit-code-violations` behavior treated the expected incomplete-stage
airwires as a nonzero exit despite reporting zero violations. The exact
restoration hash was proved before resuming. Subsequent acceptance used the
native JSON criteria: zero `violations` and the exact planned airwire count.
No geometry change or alternate placement was attempted during that event.

## Controlled transaction

| Stage | Functional subsection | Native violations | Airwires | Fast contract | Parity |
| --- | --- | ---: | ---: | --- | --- |
| 1 | recovery/sync/antenna + J8/JP1 | 0 | 42 | PASS | PASS |
| 2 | U4/C9/C10 + corrected AUX_3V3 + J5 feed | 0 | 32 | PASS | PASS |
| 3 | J9 functional RGB output | 0 | 30 | PASS | PASS |
| 4 | E220 signals + R8/R9 | 0 | 21 | PASS | PASS |
| 5 | J6 BUTTONS | 0 | 15 | PASS | PASS |
| 6 | BAT_SENSE | 0 | 9 | PASS | PASS |
| 7 | GPIO4-to-U3 completion | 0 | 8 | PASS | PASS |

Each active mutation had a named preceding PCB backup in this directory. Every
activated checkpoint passed the fast contract before and after native refill
DRC, plus standalone schematic-PCB parity.

## U4 corrected geometry

- U4 `(20.650,27.000)`, 0 deg;
  C9 `(17.500,33.000)`, 270 deg;
  C10 `(14.400,27.000)`, 180 deg.
- U4 pad 1 `(17.5,24.7)`=`GND`; small physical pad 2
  `(17.5,27.0)`=`AUX_3V3`; tab physical pad 2
  `(23.8,27.0)`=`AUX_3V3`; pad 3 `(17.5,29.3)`=`5V_SYS`.
- One full-connect, priority-2 F.Cu AUX_3V3 zone: X=22.0..30.0 mm,
  Y=22.0..32.0 mm, nominal 8 x 10 mm.
- 0.8-mm F.Cu pad bridge `(17.5,27.0) -> (23.8,27.0)` and feed bridge
  `(30.0,22.54) -> (37.5,22.54)`.
- No B.Cu AUX_3V3 thermal zone and zero AUX_3V3 thermal vias.
- Duplicate-pad consistency: PASS. J5 AUX feed is complete. No AUX_3V3
  unconnected item remains.

## Final deterministic gates

- Full board contract: PASS.
- Native refill DRC: 0 geometric violations, 0 footprint/library violations,
  0 zone violations; 8 visible inherited/deferred unconnected items.
- Schematic-PCB parity: PASS; 37 assembled schematic items, 37 PCB footprints,
  no reference/property/pad-net mismatch; R10/R11 remain intentional
  `NO_FOOTPRINT_DNP` items.
- ESP32 antenna exclusion: PASS; hit list empty.
- Protected U1/C1/C2/C3/C4/L1 checkpoint: PASS.
- Counts: 37 footprints, 182 tracks, 56 vias, 4 copper zones, 1 rule area.
- Board: 2 copper layers; 145 x 90 mm.

The eight visible airwires have net signature: GND x3, BAT_PLUS x1, BUCK_IN
x2, OLED_SDA x1, OLED_SCL x1. None belongs to a mandatory Rev.1 integration
route. Mandatory Rev.1 airwire count is 0: E220, BUTTONS, BAT_SENSE, RGB, J8,
JP1, and AUX_3V3 routing are complete.

## Scope retention and next gate

Retained: J6 BUTTONS, J9 / functional J_RGB, the approved module placements,
all already-proven routing, Carrier footprint references, and native
`ESP32_ANTENNA_EXCLUSION`.

Absent as required: J7, D2, TP6, TP7, TP8, TP9, TP10.

Deferred: OLED SDA/SCL fanout; inherited TP1/TP3 and R2 endpoints; the three
native GND connectivity reports; `U4 TEMPERATURE VALIDATION` during prototype
testing. These are not mandatory Rev.1 integration routes.

Failed subsections: none.

No schematic, electrical topology, GPIO/feature scope, major-module placement,
or production-output change was made. No production files were generated.

Next gate: independent `pcb_reviewer` implementation review for
`SCOPE VERDICT: REV1 EXPANSION INTEGRATION PASS` and `REVIEW PASS`.
