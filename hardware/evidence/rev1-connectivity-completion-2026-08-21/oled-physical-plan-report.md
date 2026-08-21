# Rev.1 final-connectivity OLED routing plan

## Scope and authority

- Active baseline: `hardware/esp32-e220.kicad_pcb`, SHA-256
  `4f6fba9ed19c3f0290842b62f3ec087d28e3911c7d12f31d2e581aa1c8e26650`.
- Byte-identical retained snapshot: `00-active-baseline.kicad_pcb`.
- OLED-only proof candidate: `01-oled-candidate.kicad_pcb`, SHA-256
  `e5b45270dda72f84c48e815201ef6969b4805fe110cb243a34236a6daeed18f4`.
- The active PCB remained byte-identical to the baseline throughout planning.
- Coupled group is only `OLED_SDA` and `OLED_SCL`. No footprint, zone outline,
  board outline, rule area, or pre-existing track/via was changed.

## Exact initial native-DRC airwires

Native DRC on the active board reported zero geometric violations and exactly
eight unconnected pairs:

1. `/GND`: C9.2-connected 0.5-mm F.Cu track `(17.5,34)->(14,34)` and via
   `(14,34)` to the nearest other connected GND component, reported as C5.2
   `(24.725,48)` (UUIDs `ec0ee8c8...` and `03d7c258...`).
2. `/GND`: disconnected filled islands of the same F.Cu GND zone UUID
   `dfb51e4c...`; native DRC reports zone-to-itself at the zone origin
   `(64,52)`. Filled-polygon inspection resolves the isolated U1-ground island
   containing U1 pads 5/6/8/15/16/EP from the connected C1/C3 and C2/C4
   GND-island clusters. There is no distinct reference/pad item in the native
   DRC pair, so none is invented.
3. `/GND`: J2.2 `(136.4,16.54)` to the connected B.Cu GND branch
   `(104,18)->(111,16.54)`, which terminates at J1.2; the same component extends
   `(94,18)->(104,18)` from J6.1.
4. `/BAT_PLUS`: TP1.1 `(48,87)` to F.Cu BAT_PLUS track component reported at
   `(35,78.5)`, length 7.8620 mm.
5. `/BUCK_IN`: TP3.1 `(58,87)` to F.Cu BUCK_IN track component reported at
   `(64.349999,77)`, length 1.1500 mm.
6. `/BUCK_IN`: R2.1 `(62.5,67.725)` to F.Cu BUCK_IN track component reported at
   `(65.5,70)`, length 9.5000 mm.
7. `/OLED_SDA`: J5.4 `(63,27.62)` to J2.11 `(136.4,39.4)`.
8. `/OLED_SCL`: J5.3 `(63,25.08)` to J2.14 `(136.4,47.02)`.

Authoritative report: `00-active-native-drc.json`.

## Bounded routing contract

All signal segments are 0.25 mm wide. All vias are through vias, 0.60 mm
diameter with 0.30 mm drill. No 0.20-mm segment is needed.

`OLED_SDA`, total planar length 100.019519 mm: B.Cu 63.190181 mm and F.Cu
36.829339 mm, four vias.

- B.Cu: `(63,27.62) -> (78,27.62) -> (81,30.62) -> (81,46)`.
- Via: `(81,46)`.
- F.Cu: `(81,46) -> (97.5,46)`.
- Via: `(97.5,46)`.
- B.Cu: `(97.5,46) -> (104,46)`.
- Via: `(104,46)`.
- F.Cu: `(104,46) -> (108,50.8) -> (112.5,50.8) -> (114,50.3) -> (122,50.3)`.
- Via: `(122,50.3)`.
- B.Cu: `(122,50.3) -> (124,48.3) -> (124,42) -> (130,39.4) -> (136.4,39.4)`.

`OLED_SCL`, total planar length 95.987198 mm: B.Cu 60.403131 mm and F.Cu
35.584067 mm, four vias.

- B.Cu: `(63,25.08) -> (77,25.08) -> (82,30.08) -> (82,47)`.
- Via: `(82,47)`.
- F.Cu: `(82,47) -> (97.5,47)`.
- Via: `(97.5,47)`.
- B.Cu: `(97.5,47) -> (104,47)`.
- Via: `(104,47)`.
- F.Cu: `(104,47) -> (107.5,51.35) -> (112.5,51.35) -> (114,51.3) -> (122,51.3)`.
- Via: `(122,51.3)`.
- B.Cu: `(122,51.3) -> (126,51.3) -> (132,46.8) -> (134,47.02) -> (136.4,47.02)`.

The layer swaps have specific local purposes: B.Cu leaves the J5 PTH pads;
F.Cu crosses the existing B.Cu WS2812 corridor; B.Cu crosses the F.Cu 5V
spine; F.Cu passes below J1; final B.Cu fanout avoids the existing F.Cu
GPIO23 approach to J2. This is one dominant candidate; no floorplanning or
placement alternative is needed.

## Return path, keepouts, and preserved work

- Both GND planes remain present. Zone outlines are byte-semantically
  unchanged; refilling around the new signal copper creates no new GND
  airwire. Initial GND airwires remain exactly three in the candidate.
- The closest signal centerline to `ESP32_ANTENNA_EXCLUSION` is at Y=51.35 mm;
  the closest 0.60-mm via center is at Y=51.30 mm. The exclusion begins at
  Y=52.0 mm for X=104.7..142.7 mm. Contract hit list is empty.
- All pre-existing tracks and vias are preserved by UUID. E220 five-signal,
  BUTTONS, BAT_SENSE, RGB, U4/AUX, protected buck, and 5V routing item sets are
  unchanged.
- No copper zone, rule area, or placement is replaced. Only 26 signal
  segments and eight signal vias are added.

## Checkpoint order and expected DRC delta

1. Prove active SHA-256 and copy the active board to the named transaction
   backup before implementation.
2. Implement `OLED_SDA` exactly as listed; run fast board contract and native
   DRC. Expected delta: one OLED airwire removed and zero new violation.
3. Implement `OLED_SCL` exactly as listed; run fast board contract and native
   DRC. Expected delta: second OLED airwire removed and zero new violation.
4. Refill zones, then run full contract, parity, and native DRC before
   accepting the local checkpoint.

Candidate deterministic result: fast board contract PASS; schematic-PCB
parity PASS; native DRC 0 violations; unconnected items 8 -> 6, with only the
pre-existing GND x3, BAT_PLUS x1, and BUCK_IN x2 findings remaining. Counts
change 37 footprints / 182 tracks / 56 vias / 4 copper zones / 1 rule area to
37 / 208 / 64 / 4 / 1 for this OLED-only proof.

Risk is limited to exact transactional replay near the lower J1/antenna-rule
boundary. The listed coordinates already pass native keepout and clearance
checks; any deviation should fail fast rather than be improvised on the active
board.

SCOPE VERDICT: REV1 CONNECTIVITY OLED PLAN PASS

ROUTING PLAN READY
