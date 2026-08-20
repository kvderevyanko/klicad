# Rev.1 final active-board implementation handoff

## SCOPE STATUS

`REV1 FINAL ACTIVE PCB ATTEMPT REJECTED AND ROLLED BACK — STOP`

Post-gate audit found that the attempted implementation retained 20 x 22 mm F.Cu and B.Cu AUX_3V3 islands without the simplified scope's required TI thermal justification. This invalidates the physical plan and implementation gate. The active PCB has been restored byte-for-byte to the preserved rejected pre-recovery record; all implementation checkpoints below are retained as historical attempted evidence only and are not active-board authority.

The rejected active record was preserved before recovery. Its retained and transaction-copy SHA-256 is `bf502dfde6ebb1f05d5d8f95fa77dc6f3d484fd9ddcdb47d3511c4b82b5f5036`. Recovery used only the clean pre-expansion PCB and the reviewed final-scope plan. No active-board placement search occurred.

Final active SHA-256 is `b10bc94138397f3d3d393804dd02d285b2f19eaa5c3341b920835085dbf23464`. It is byte-identical to the final transaction-stage checkpoint. Its normalized placement, fixed-module, U4-pad, thermal, route-length/via, count, antenna, and J8 metrics are equal to the reviewed candidate; the different reviewed-candidate SHA is caused by regenerated KiCad object UUIDs and serialization.

## Controlled transaction result

| Subsection | Expected native DRC delta | Result |
|---|---:|---|
| baseline recovery + sync + antenna + J8/JP1 | 0 violations; 42 unconnected | PASS |
| U4/C9/C10 + AUX zones/vias/J5 feed | 0 violations; 32 unconnected | PASS |
| J9 / J_RGB | 0 violations; 30 unconnected | PASS |
| five E220 signals + R8/R9 | 0 violations; 21 unconnected | PASS |
| J6 BUTTONS five GPIO signals | 0 violations; 15 unconnected | PASS |
| BAT_SENSE | 0 violations; 9 unconnected | PASS |
| retained GPIO4-to-U3 completion | 0 violations; 8 unconnected | PASS |

Every subsection passed the fast contract, native DRC, and schematic-PCB parity. Named checkpoints and reports are retained in this directory. No rollback was required.

## Exact placements

| Ref | XY mm | Rotation |
|---|---:|---:|
| U4 | (20.650, 27.000) | 0 deg |
| C9 | (17.500, 33.000) | 270 deg |
| C10 | (14.400, 27.000) | 180 deg |
| J6 | (94.000, 18.000) | 0 deg |
| J9 / J_RGB | (100.000, 54.000) | 0 deg |
| J8 | (51.000, 76.000) | 0 deg |
| JP1 | (96.000, 14.000) | 90 deg |
| R3 | (86.000, 66.000) | 0 deg |
| R4 | (90.000, 66.000) | 0 deg |
| C8 | (88.000, 69.000) | 0 deg |
| R8 | (40.000, 35.000) | 0 deg |
| R9 | (46.000, 35.000) | 0 deg |

J1, J2, J3, and J5 are exact baseline XY/rotation matches. The ESP32, E220, and OLED remained fixed.

## Critical geometry and connectivity

- Board: 2 copper layers; 145.0 x 90.0 mm.
- Native `ESP32_ANTENNA_EXCLUSION`: X=104.7..142.7 mm, Y=52.0..90.0 mm; checker hit list empty.
- U4 physical pads: pad 1/GND at (17.5,24.7); small pad 2/AUX_3V3 at (17.5,27.0); tab pad 2/AUX_3V3 at (23.8,27.0); pad 3/5V_SYS at (17.5,29.3).
- AUX copper bounds: X=17.5..37.5, Y=16.0..38.0 on F.Cu and B.Cu. AUX vias: (25.3,24.8), (25.3,29.2), (26.5,26.0), (26.5,28.0).
- J8 endpoint route: 14.055 mm, 1.0-mm F.Cu, zero vias.
- J6 pads: 1=GND, 2=GPIO13, 3=GPIO14, 4=GPIO18, 5=GPIO19, 6=GPIO23.
- J9 pads: 1=5V_SYS, 2=WS2812_DATA_5V, 3=GND.
- J8 pads: 1=BAT_FUSED, 2=BAT_SW. JP1 pads: 1=5V_SYS, 2=DEVKIT_VIN.
- J7, D2, and TP6..TP10 are absent.

## Routed signals

| Net | Length mm | Vias |
|---|---:|---:|
| E220_M0 | 119.496 | 4 |
| E220_M1 | 122.104 | 6 |
| E220_AUX | 112.837 | 4 |
| E220_RXD | 138.360 | 4 |
| E220_TXD | 139.021 | 4 |
| GPIO13 | 17.209 | 1 |
| GPIO14 | 17.115 | 1 |
| GPIO18 | 47.906 | 1 |
| GPIO19 | 48.006 | 1 |
| GPIO23 | 53.175 | 3 |
| BAT_SENSE | 72.787 | 1 |
| WS2812_DATA_3V3 | 108.548 | 2 |
| WS2812_DATA_5V | 12.717 | 0 |

## Final machine gates

- Full board contract: PASS.
- Native DRC: 0 violations; 0 geometric, footprint/library, or zone violations; 8 visible unconnected items.
- Schematic-PCB parity: PASS; zero reference, property, or pad-net mismatches.
- Counts: 37 footprints, 180 tracks, 60 vias, 5 copper zones plus 1 rule area.
- Protected U1/C1/C2/C3/C4/L1 geometry: PASS against pre-expansion reference.

The eight remaining airwires are: three inherited GND connectivity reports, TP1/BAT_PLUS, TP3/BUCK_IN, R2/BUCK_IN, OLED_SDA, and OLED_SCL. None belongs to mandatory E220, BUTTONS, BAT_SENSE, RGB, J8, JP1, or AUX power connectivity.

Mounting holes were omitted and strain relief was deferred exactly as the approved plan specified; neither optional mechanical feature delayed electrical completion.

## Gate handoff

Retained: all reviewed final-scope physical placement, routing, zones, and RF keepout.

Deferred: OLED SDA/SCL fanout; mechanically reviewed mounting and strain-relief datums.

Failed subsections: none.

Next action: `ROUTING PLAN REVISION REQUIRED`. A new temporary plan and independent physical-plan gate must resolve the U4 thermal geometry from justified TI evidence before any future active-board recovery. No further PCB change was made in this transaction.
