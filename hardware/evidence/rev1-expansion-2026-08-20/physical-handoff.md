# Rev.1 expansion physical handoff

SCOPE STATUS: BLOCKED

This is a `pcb_layout_dfm` transaction handoff, not a reviewer verdict.

## Result retained on the active board

* Named exact backup: `hardware/esp32-e220-pre-rev1-expansion.kicad_pcb`,
  SHA-256 `d87c0ff900c9ce113c4c36b5a2785a65848077673e34804a8e9166cec2a6b76c`.
  Active-board SHA-256 after retained transactions: `bf502dfde6ebb1f05d5d8f95fa77dc6f3d484fd9ddcdb47d3511c4b82b5f5036`.
* Retained transactions: A (J8 switch insertion), B (JP1/J1.1 isolated
  branch), C (BAT_SENSE local branch), D (U4/C9/C10 placement, AUX copper,
  J5.2 net update). Each retained transaction was native-DRC checked; final
  native DRC has `geometric_violations=0`, `zone_errors=0`, and
  `footprint_errors=0`.
* Final current board counts: 41 footprints, 96 segments, 25 vias, 4 zones.
  The baseline was 33/81/17/2.
* Changed locations (mm/deg): J8 `(105.0,78.0,90)`, JP1 `(96.0,14.0,270)`,
  R3 `(86.0,66.0,0)`, R4 `(90.0,66.0,0)`, C8 `(88.0,69.0,0)`, U4
  `(125.0,68.0,0)`, C9 `(115.0,60.0,180)`, C10 `(135.0,68.0,0)`.
* A retains D3 upstream and reworks only the F1 downstream positive copper:
  1.00-mm `BAT_FUSED` to J8.1 and 1.00-mm `BAT_SW` J8.2-to-Q1.3, with two
  0.80/0.40-mm power vias in the switched branch. B retains the accepted 5V
  trunk, makes J1.1 `DEVKIT_VIN`, and uses JP1.1=`5V_SYS`, JP1.2=`DEVKIT_VIN`.
  C is a 0.25-mm `BUCK_IN -> R3 -> BAT_SENSE -> R4/C8` local branch, physically
  away from BUCK_SW. D uses a 0.80-mm 5V branch and 22 x 22-mm AUX_3V3 zones
  on F.Cu and B.Cu; four 0.60/0.30-mm AUX_3V3 vias are within 3 mm of U4 tab.

## Required blocker

`J6`, `J7`, the four M3 NPTH holes, the two strain-relief NPTH holes, and
their required silkscreen were attempted as one mechanics transaction. Native
DRC found 40 violations (headers/hole locations collide with the protected
module and J8 geometry). That transaction was restored in full; no experimental
mechanical geometry remains active. Therefore the active board deliberately
lacks J6/J7 and all six authorized non-electrical holes.

The active board also has C9/C10 GND ratsnest endpoints. The available outer
thermal area is present, but direct capacitor ground-return geometry cannot be
claimed until a coupled mechanical/return-path replan; consequently U4 thermal
release at 0.510 W is **not** established. Do not call this stage DRC-clean:
the native geometry is zero, but there are mandatory in-scope airwires.

## Validation and classifications

* `cli_exit_code=0` for final `kicad-cli pcb drc`; artifact:
  `final-restored-drc.json`. It has 33 global airwires.
* `in_scope_unconnected`: U4/C9/C10 ground-return and AUX_3V3 endpoint
  completion; J6/J7 are absent and thus parity blockers.
* `out_of_scope_unconnected`: the pre-existing signal/OLED/E220/radio/D2 and
  TP1/TP3 deferred airwires, plus no USER/DISPLAY GPIO copper (intentionally
  untouched).
* Final `SCHEMATIC-PCB ELECTRICAL PARITY` is `FAIL` only because `J6` and `J7`
  are missing; there are no remaining electrical pad-net mismatches. See
  `final-restored-parity.json`.
* No M3 or strain-relief hole is retained. No production Gerber/BOM/CPL/PDF
  was generated. Existing ESP32/E220/OLED placements and protected buck,
  BUCK_SW, VOS, FSW, C1/C2/C3/C4, E220 VCC/C5/C6, and U3/C7 geometry were not
  moved.

## DFM / next action

J8 is accessible at the lower service edge with its harness body clear of Q1
gate copper. JP1 is accessible beside the DevKit power entry. The standard
JST VH footprint has 1.70-mm drilled, 2.70-mm PTH pads. Independent review
found the retained U4 footprint instance defective: the lead portion of
physical pad 2 is netless while only the pad-2 tab is `AUX_3V3`; both shapes
must be `AUX_3V3` for the TI DCY mapping. Do not treat the nominal footprint
map as verified until this local rework is completed.

The next physical step requires a coupled placement/review decision for J6,
J7, the six holes, and C9/C10 ground returns before continuing. Do not issue
`PCB READY FOR REVIEW` from this handoff.
