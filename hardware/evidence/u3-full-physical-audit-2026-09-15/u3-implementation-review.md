# Independent U3 footprint-correction implementation gate

Role: `pcb_reviewer`; independent read-only implementation gate.  No active
design, schematic, generator, library, routing, zone, or release artifact was
modified by this review.  This is a bounded U3 implementation decision, not a
production-release decision.

## Gate basis

- Required plan gate is present in `u3-physical-plan-review.md` with
  `SCOPE VERDICT: U3 PHYSICAL PLAN PASS` and `REVIEW PASS`.
- Primary source checked: TI `SN74AHCT1G125` SCLS378P rev. P, package drawing
  DBV0005A `4214839/K`, 08/2024, retained at
  `primary/ti-sn74ahct1g125-rev-p.pdf` (SHA-256
  `dbaf49b3af33690fc7f7356afe387e7815a56b8bb73fe1e88bf794f4fb8e0d2f`).
  Its DBV example board layout specifies five `1.10 x 0.60 mm` lands,
  `R0.05` typical, three-lead-side pitch `2 x 0.95 mm`, and row-centre spacing
  `2.60 mm`.
- `hardware/check_board_contract.py` was run first, then repeated with
  `10-u3-implementation-backup.kicad_pcb` as its protected checkpoint.
  Counts, two-layer construction, outline, antenna exclusion, duplicate-pad/
  net check, required-pad-net check, protected checkpoint, and schematic/PCB
  parity pass.  Aggregate status is `FAIL`, correctly retained, solely because
  native DRC reports the two inherited warnings below; it is not a U3
  geometry/connectivity failure.

## Exact implementation verification

The active embedded U3 at `(89.000, 54.000) mm`, `0 deg`, its project-local
library footprint, and generator function `sn74ahct1g125()` agree exactly.
All have five and only five pads.  In the active orientation, the verified
coordinates/dimensions are:

| TI DBV0005A land / pin | local centre mm | copper mm | active net / schematic function |
|---|---:|---:|---|
| 1 | `(-0.950, +1.300)` | `0.600 x 1.100`, R0.05 | `/GND` / `OE` |
| 2 | `(0.000, +1.300)` | `0.600 x 1.100`, R0.05 | `/WS2812_DATA_3V3` / `A` |
| 3 | `(+0.950, +1.300)` | `0.600 x 1.100`, R0.05 | `/GND` / `GND` |
| 4 | `(+0.950, -1.300)` | `0.600 x 1.100`, R0.05 | `/WS2812_DATA_5V` / `Y` |
| 5 | `(-0.950, -1.300)` | `0.600 x 1.100`, R0.05 | `/5V_SYS` / `VCC` |

Thus the row-centre spacing is `2.60 mm`; the three-pad side and two-pad side
both have the specified `1.90 mm` end-to-end centre span.  Pin numbers are
the TI CCW DBV physical order and agree with the project symbol and parity
result.  `F.Fab` is the drawing-derived nominal `1.60 x 2.90 mm` body with
pin-1-side chamfer; `F.CrtYd` is `3.60 x 4.20 mm`; the sole F.SilkS pin-1
circle is `(-1.550, +1.750) mm`, clear of the pad-1 mask.

`hardware/check_u3_dbv_footprint.py` independently passes.  It verifies all
of the above in the active embedded footprint and local library, verifies
generator byte equality, and normalizes the board against retained checkpoint
`10-u3-implementation-backup.kicad_pcb`.  The normalized semantic delta is
`PASS`: only the corrected U3 geometry and exactly these five existing F.Cu
endpoint re-anchors differ; opposite endpoints, widths, layers, nets, UUIDs,
placement, vias, zones, rule areas, and all non-U3 board content are retained:

- `8b5ac9dc-4208-4f80-99be-6912b8d39d52`: U3.1 `(88.050,55.300)`;
- `02e750f7-1ae2-44c5-9fc4-c55c2823b1e9`: U3.2 `(89.000,55.300)`;
- `6308e9af-e3b4-4509-b16a-d1588a1cc74b`: U3.3 `(89.950,55.300)`;
- `32e0895c-bc20-429f-9684-018e7fcc24bb`: U3.4 `(89.950,52.700)`;
- `da2890d9-c14e-428c-9a65-9024952b7af6`: U3.5 `(88.050,52.700)`.

The active board SHA-256 is
`ef7cc377eb670115295f39cbd963e8910f2f4047cf5d740728abd09e1e4f25ea`;
the library SHA-256 is
`2f63828381821ca805033f3636ae06bafa95a82920a5340e76069a7b5233bad3`;
the generator SHA-256 is
`3b3ba925cd7556431e1be7194d7fa99cc01bb7132144a1efc42d8470a07fd395`.
These match the implementation handoff's post-regeneration retained hashes.

## Machine-gate results

- U3 invariant and bounded semantic delta: `PASS`.
- Schematic/PCB parity: `PASS`; no electrical pad/net mismatches, missing
  footprints, or production-property mismatches.
- Native ERC: `PASS`, zero violations.
- Independent native DRC: zero geometric, clearance, zone, and unconnected
  findings.  It reports precisely two inherited `lib_footprint_mismatch`
  warnings: JP1 (`PinHeader_1x02_P2.54mm_Vertical` versus
  `Connector_PinHeader_2.54mm`) and U4 (`SOT-223-3_TabPin2` versus
  `Package_TO_SOT_SMD`).  They are byte-for-byte the same category, references
  and locations as `active-baseline-native-drc.json`; U3 is not a DRC finding.
  They remain unsuppressed and are not evidence that JP1/U4 passed any
  physical-footprint audit.
- `git diff --check`: `PASS`.

New independent DRC/ERC evidence is retained as
`reviewer-implementation-native-drc.json` and
`reviewer-implementation-native-erc.json`.

## Findings and decision

NOTE — The aggregate board contract remains `FAIL` for the explicit inherited
JP1/U4 DRC warnings.  The protected-checkpoint comparison now passes against
the named U3 transaction backup.  The warnings are outside the approved U3
transaction, unchanged by it, and must remain visible to the full
physical-footprint audit/release gate.  This review does not mark the board or
any production package safe for production.

No U3 implementation-scope blocker, unexpected delta, topology change,
pin-map error, courtyard/Fab/pin-1 error, or routing/return-path regression
was found.

`SCOPE VERDICT: U3 FOOTPRINT CORRECTION IMPLEMENTATION PASS`

`REVIEW PASS`
