# Independent U3 physical-plan gate

Role: `pcb_reviewer`, read-only plan gate.  No active design, generator, or
footprint-library file was changed.

## Preflight and review basis

- `hardware/check_board_contract.py` was run first.  All physical/electrical
  contract subsections relevant to this plan passed: two copper layers,
  outline, counts, duplicate-pad/net consistency, required electrical pads,
  antenna exclusion, and schematic/PCB parity.  Its overall `FAIL` is solely
  the pre-existing `lib_footprint_mismatch` warnings for `JP1` and `U4` plus a
  missing transaction reference; neither is a U3 copper, geometry, or
  connectivity finding.
- Primary evidence inspected: TI `SN74AHCT1G125`, `SCLS378P` rev. P and its
  DBV0005A drawing `4214839/K`, 08/2024, retained as
  `primary/ti-sn74ahct1g125-rev-p.pdf`, SHA-256
  `dbaf49b3af33690fc7f7356afe387e7815a56b8bb73fe1e88bf794f4fb8e0d2f`.
- The active-board SHA-256 is
  `61549b45d4fe336986e76bcc78c5ca5532e67df604d155b140b1fd8a9d1bb109`.

## Independent geometric check

TI's drawing explicitly specifies five exposed-metal lands `1.10 x 0.60 mm`,
`R0.05 mm` typical, a three-land side at `2 x 0.95 mm`, its end-to-end centre
span `1.90 mm`, and opposing-row centrelines `2.60 mm` apart.  In the active
board orientation (drawing rotated 90 degrees), the approved local centres
are exactly:

| Pad | local centre mm | copper mm | function / candidate net |
|---|---:|---:|---|
| 1 | `(-0.950, +1.300)` | `0.600 x 1.100`, R0.05 | OE / `/GND` |
| 2 | `(0.000, +1.300)` | `0.600 x 1.100`, R0.05 | A / `/WS2812_DATA_3V3` |
| 3 | `(+0.950, +1.300)` | `0.600 x 1.100`, R0.05 | GND / `/GND` |
| 4 | `(+0.950, -1.300)` | `0.600 x 1.100`, R0.05 | Y / `/WS2812_DATA_5V` |
| 5 | `(-0.950, -1.300)` | `0.600 x 1.100`, R0.05 | VCC / `/5V_SYS` |

This confirms both the DBV footprint orientation and the CCW physical pin
order.  The schematic symbol uses the same 1=`OE`, 2=`A`, 3=`GND`, 4=`Y`,
5=`VCC` map; candidate schematic/PCB parity is `PASS`, with no electrical
pad/net mismatches.

The proposed `F.CrtYd` `x=+/-1.80`, `y=+/-2.10 mm` encloses the corrected
outer lands (maximum `x=+/-1.25`, `y=+/-1.85 mm`) by at least `0.25 mm` in
the limiting direction.  The implementation must also replace the old Fab
outline by the drawing-derived nominal rotated `1.60 x 2.90 mm` body with
the pin-1-side chamfer; the candidate is a copper-routing proof and does not
yet make that Fab replacement.

## Local routing feasibility

The candidate retained at
`u3-ti-dbv-corrected-plan-candidate.kicad_pcb` makes exactly these five U3
endpoint re-anchors, with all opposite endpoints, widths, layers, vias,
zones, placement, and non-U3 copper retained:

| U3 pad | corrected endpoint -> retained endpoint | layer / width |
|---|---|---|
| 1 | `(88.050,55.300)` -> `(87.200,56.500)` | F.Cu / 0.50 mm |
| 2 | `(89.000,55.300)` -> `(89.000,58.000)` | F.Cu / 0.25 mm |
| 3 | `(89.950,55.300)` -> `(91.000,55.000)` | F.Cu / 0.50 mm |
| 4 | `(89.950,52.700)` -> `(94.000,51.500)` | F.Cu / 0.25 mm |
| 5 | `(88.050,52.700)` -> `(88.525,51.900)` | F.Cu / 0.50 mm |

C7's transformed courtyard is `x=84.60..86.40`, `y=52.70..55.30 mm`;
the proposed U3 courtyard is `x=87.20..90.80`, `y=51.90..56.10 mm`, leaving
`0.80 mm` horizontal clearance.  U3 remains 13.9 mm left of the ESP32
antenna-rule boundary at x=104.7 mm.  The B.Cu GND return and the three
existing U3/C7 return vias are unchanged.

Native DRC of the candidate found zero unconnected items and no copper,
clearance, zone, or other geometric violations.  The only two findings are
the exact inherited JP1/U4 library-mismatch warnings, matching
`active-baseline-native-drc.json`; output is retained as
`reviewer-plan-candidate-drc.json`.  Candidate parity is `PASS`, retained as
`reviewer-plan-candidate-parity.json`.

## Gate result

No planner-scope blocker, topology change, keepout intrusion, mechanical
collision, return-path break, or repairability issue was found.  The owner
must implement only the stated generator/embedded-footprint correction, Fab
replacement, courtyard/pin-1 mark update, and five endpoint moves; any
additional routing or DRC delta is outside this approval and requires
rollback to the named transaction checkpoint.

`SCOPE VERDICT: U3 PHYSICAL PLAN PASS`

`REVIEW PASS`
