# Rev.1 final five-airwire active implementation handoff

## Gate and controlled baseline

The independent read-only plan reviewer reported verbatim before active-board
mutation:

`SCOPE VERDICT: REV1 FINAL 5-AIRWIRE PLAN PASS`

`REVIEW PASS`

The reviewed authority was `03-candidate.kicad_pcb`. The active PCB and named
pre-implementation backup `10-active-pre-implementation.kicad_pcb` both had
SHA-256
`aec6bac3ae6710390cb5eba7477a1036d531b02adafb1cbea38091fd7987ef13`.
The initial deterministic state was 37 footprints, 185 tracks, 56 vias, four
copper zones, one rule area, two copper layers, 145 x 90 mm, contract PASS,
parity PASS, and native DRC 0 violations / 5 unconnected items.

The exact initial groups were:

1. `/GND`: C9.2-connected global component to the E220 C5.2/C6.2/J3.7 local
   return component.
2. `/GND`: isolated U1 F.Cu ground/PGND filled island to the global GND
   system.
3. `/GND`: J2.2 `(136.400,16.540)` to the J1.2-connected global component.
4. `/OLED_SDA`: J5.4 `(63.000,27.620)` to J2.11 `(136.400,39.400)`.
5. `/OLED_SCL`: J5.3 `(63.000,25.080)` to J2.14 `(136.400,47.020)`.

## Transaction results

Each transaction had a named preceding board backup. Before and after each
mutation the fast board contract passed against
`10-active-pre-implementation.kicad_pcb`; each post-transaction parity check
passed. Zones were explicitly refilled by the transaction tool and again by
native DRC.

| Transaction | Added geometry | Native DRC result |
| --- | --- | --- |
| 1, U1 GND release | GND vias `(68.700,54.000)` and `(70.500,53.000)`, 0.60/0.30 mm, F.Cu--B.Cu | 0 violations; 5 -> 4 unconnected |
| 2, E220 local return | `(24.725,51.000)->(24.725,47.900)`, B.Cu, 0.25 mm, 3.100 mm | 0 violations; 4 -> 3 unconnected |
| 3, ESP32 J2.2 GND | J1.2 `(111.000,16.540)->` J2.2 `(136.400,16.540)`, B.Cu, 0.50 mm, 25.400 mm | 0 violations; 3 -> 2 unconnected |
| 4, OLED_SDA | six F.Cu segments, 0.25 mm, 93.087772 mm, zero vias | 0 violations; 2 -> 1 unconnected |
| 5, OLED_SCL | seven F.Cu segments, 0.25 mm, 101.430391 mm, zero vias | 0 violations; 1 -> 0 unconnected |

OLED_SDA waypoints:
`(63.000,27.620) -> (96.000,12.000) -> (112.500,12.000) ->`
`(114.250,16.000) -> (114.250,25.500) -> (133.000,38.000) ->`
`(136.400,39.400)`.

OLED_SCL waypoints:
`(63.000,25.080) -> (97.000,10.900) -> (112.000,10.900) ->`
`(135.500,30.500) -> (137.000,30.500) -> (138.000,31.500) ->`
`(138.000,45.000) -> (136.400,47.020)`.

## U1 ground release proof

After transaction 1 and final refill, U1.5, U1.6, U1.8, U1.15, U1.16,
U1.EP, and both new vias are members of filled polygon 2 of the existing F.Cu
GND zone and polygon 0 of the global B.Cu GND plane. The same B.Cu polygon
contains accepted global-ground pads including C1.2, C2.2, C3.2, C4.2,
TP2.1, J9.3, U3.1, and U3.3. Native DRC has no `/GND` conflict with
`/SS_TR`, `/BUCK_IN`, or `/5V_SYS` and no other violation. Machine proof is
retained in `15-post-1-u1-gnd-proof.json` and
`32-final-active-metrics.json`.

## Final deterministic state

- Active PCB SHA-256:
  `0ed5189dcfb6a21822b05246acee0257cd03415e07cdea919861375e0d5d6c70`.
- Counts: 37 footprints, 200 tracks, 58 vias, four copper zones, one rule
  area.
- Full board contract with the protected baseline: PASS; two copper layers,
  145 x 90 mm, duplicate-pad PASS, antenna exclusion PASS, protected buck
  PASS, parity PASS, and native DRC summary PASS.
- Native DRC: 0 violations and 0 unconnected items. There are no geometric,
  footprint/library, or zone findings and no exclusions or waivers were added.
- Native ERC: 0 errors / 0 warnings.
- Schematic-PCB parity: PASS; 37 assembled schematic references / 37 PCB
  footprints and zero reference, property, pad-net, or raw-net mismatches.
- Invariance audit against the named baseline: all 241 baseline copper UUIDs
  retain identical geometry; all footprint/pad geometry is unchanged; all
  zone/rule-area outlines are unchanged. The only PCB geometry additions are
  15 tracks and two vias listed above.
- R2.1, TP1, TP3, E220 signal routes, J6, J9, U4 thermal geometry, antenna
  keepout, and all major-footprint positions/rotations are retained exactly.
  No schematic or production output was changed or generated.

`SCOPE STATUS: REV1 FINAL FIVE-AIRWIRE ACTIVE IMPLEMENTATION COMPLETE; FINAL BOUNDED REVIEW REQUIRED`

Next gate: independent `pcb_reviewer` implementation review for
`SCOPE VERDICT: REV1 CONNECTIVITY COMPLETION PASS` and `REVIEW PASS`.
