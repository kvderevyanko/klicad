# Rev.1 final five-airwire local routing plan

## Scope and baseline

- Active controlled PCB: `hardware/esp32-e220.kicad_pcb`.
- Active and retained baseline SHA-256:
  `aec6bac3ae6710390cb5eba7477a1036d531b02adafb1cbea38091fd7987ef13`.
- Proof candidate: `03-candidate.kicad_pcb`, SHA-256
  `9f917898124e849137facbcf3d89f7f80a915e8510a5e57fa55ca86ca437c64a`.
- Scope is only the five remaining connectivity groups. No schematic,
  footprint, zone/rule-area outline, or pre-existing copper item changed.
  All 241 baseline track/via UUIDs retain identical geometry; the candidate
  adds 15 track segments and two vias.
- The active PCB remained byte-identical to the named baseline throughout
  planning. The accepted R2.1, TP1, and TP3 routes are baseline copper and are
  unchanged in the candidate.

Fresh native DRC on the active baseline reports zero geometric violations and
these exact five unconnected groups:

1. `/GND`: the C9.2-connected F.Cu component reported at `(17.5,34.0)` to
   the E220 C5.2/C6.2/J3.7 component reported at `(24.725,48.0)`.
2. `/GND`: two disconnected filled polygons of F.Cu zone
   `dfb51e4c-e86d-4bc2-86a0-24b548017a74`, resolving to the isolated U1
   ground/PGND island and the global GND system.
3. `/GND`: J2.2 `(136.4,16.54)` to the existing J1.2-connected B.Cu
   component reported at `(104.0,18.0)` and ending at J1.2 `(111.0,16.54)`.
4. `/OLED_SDA`: J5.4 `(63.0,27.62)` to J2.11 `(136.4,39.4)`.
5. `/OLED_SCL`: J5.3 `(63.0,25.08)` to J2.14 `(136.4,47.02)`.

## Bounded routing contract

The five groups are one bounded completion checkpoint, implemented in the
listed order. Coordinates are millimetres.

1. U1 ground island: add two `/GND` through vias, 0.60-mm diameter / 0.30-mm
   drill, at `(68.700,54.000)` and `(70.500,53.000)`. Both via centers are in
   filled island 2 of the existing F.Cu GND zone and filled polygon 0 of the
   existing main B.Cu GND plane. Do not add an F.Cu bridge and do not alter
   SW, VOS, SS/TR, BUCK_IN, or 5V_SYS copper.
2. E220 local ground: add one 0.25-mm B.Cu `/GND` segment from the existing
   via at `(24.725,51.000)` to `(24.725,47.900)`. Length: 3.100 mm. The end is
   inside the existing upper B.Cu GND fill; no E220 signal changes.
3. ESP32 J2.2 ground: add one straight 0.50-mm B.Cu `/GND` segment from J1.2
   `(111.000,16.540)` to J2.2 `(136.400,16.540)`. Length: 25.400 mm; no via.
4. `/OLED_SDA`: add six 0.25-mm F.Cu segments, zero vias, total planar length
   93.087772 mm, through:
   `(63.000,27.620) -> (96.000,12.000) -> (112.500,12.000) ->`
   `(114.250,16.000) -> (114.250,25.500) -> (133.000,38.000) ->`
   `(136.400,39.400)`.
5. `/OLED_SCL`: add seven 0.25-mm F.Cu segments, zero vias, total planar
   length 101.430391 mm, through:
   `(63.000,25.080) -> (97.000,10.900) -> (112.000,10.900) ->`
   `(135.500,30.500) -> (137.000,30.500) -> (138.000,31.500) ->`
   `(138.000,45.000) -> (136.400,47.020)`.

The I2C pair remains on F.Cu, so it does not split either B.Cu GND fill. Its
continuous return is the existing B.Cu plane. The two signal paths stay above
the antenna exclusion; the deterministic antenna hit list is empty. The
SDA descent at X=114.25 mm is the proved local clearance corridor between J1
and the retained GPIO18/GPIO19 fanout.

## U1 ground release proof

After refill, U1.5, U1.6, U1.8, U1.15, U1.16, U1.EP, and both proposed vias
all lie in the same existing F.Cu filled-GND island. Both vias simultaneously
lie in the single filled polygon of the main B.Cu GND plane. That B.Cu polygon
also contains the accepted global-ground pads C1.2, C2.2, C3.2, C4.2, TP2.1,
J9.3, U3.1, and U3.3. Native connectivity then reports zero unconnected
items. Native DRC reports no `/GND` conflict with `/SS_TR`, `/BUCK_IN`, or
`/5V_SYS`, and no other violation.

## Preserved geometry, checkpoints, and risk

- No footprint/pad position or rotation changes; no major-module movement.
- No zone or rule-area outline changes. Zone refill only recomputes fill
  around the added copper.
- Protected U1/C1/C2/C3/C4/L1 geometry passes its baseline comparison.
- R2.1, TP1, TP3, E220 signal, J6, J9, U4/AUX_3V3, and antenna-rule geometry
  remain byte-semantically unchanged by UUID/geometry comparison.
- After each active implementation transaction: refill where applicable, run
  `hardware/check_board_contract.py --fast` against the named backup, then
  native DRC. Expected unconnected delta is `5 -> 4 -> 3 -> 2 -> 1 -> 0`,
  with zero new violations at every checkpoint. Any other delta or any new
  violation requires rollback of only that transaction and STOP.
- After the fifth transaction: refill, full board contract against the named
  backup, schematic-PCB parity, and native DRC.

Three candidates were evaluated. Candidate 1 had three local SDA violations
at JP1/J1; candidate 2 cleared those but had three local SDA clearances to the
retained GPIO18/GPIO19 fanout. Candidate 3 is the bounded dominant result and
changes only the SDA approach needed to clear those exact objects.

Candidate 3 deterministic result after explicit refill:

- Board contract: PASS; two copper layers; 145 x 90 mm; protected buck PASS;
  antenna exclusion hits 0.
- Schematic-PCB parity: PASS.
- Native DRC: 0 geometric, footprint/library, and zone violations;
  0 unconnected items.
- Counts: 37 footprints, 200 tracks, 58 vias, 4 copper zones, 1 rule area.

This is a geometry plan only and does not claim active implementation or
independent reviewer approval.

SCOPE VERDICT: REV1 FINAL 5-AIRWIRE PLAN PASS

ROUTING PLAN READY
