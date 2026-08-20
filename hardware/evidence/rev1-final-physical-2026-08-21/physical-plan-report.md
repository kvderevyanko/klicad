# Rev.1 final physical planning gate

## Authority and retained candidate

- Source PCB: `hardware/esp32-e220-pre-rev1-expansion.kicad_pcb`.
- Connectivity authority: current `hardware/esp32-e220.kicad_sch`, exported as `current-approved.net`.
- Reproducible builder: `build_candidate.py`; it rejects the active PCB and baseline as output targets.
- Preferred candidate: `esp32-e220-rev1-final-candidate.kicad_pcb`.
- Candidate SHA-256: `798f6ca518353dd3545c263ce9b608a74e19fcfd6e6b44d35e9b98741473637b`.
- J1 ESP32 headers, J2 ESP32 headers, J3 E220 socket, and J5 OLED/AUX header retain their exact baseline XY and rotation. No module-floorplan escalation was used.
- Removed schematic objects D2 and TP6..TP10 are absent, not placeholders. The local `fp-lib-table` and `esp32-e220.pretty` copy make library resolution reproducible.

## Exact placement contract

| Ref | XY mm | Rotation | Physical intent |
|---|---:|---:|---|
| U4 | (20.650, 27.000) | 0 deg | SOT-223 AUX regulator in left rework area |
| C9 | (17.500, 33.000) | 270 deg | 5V_SYS input bypass at U4 |
| C10 | (14.400, 27.000) | 180 deg | AUX_3V3 output bypass at U4 |
| J6 | (94.000, 18.000) | 0 deg | BUTTONS, 1x6 2.54-mm PTH |
| J8 | (51.000, 76.000) | 0 deg | JST B2B-XH-A 1x2 PTH power switch loop |
| J9 | (100.000, 54.000) | 0 deg | J_RGB, 1x3 2.54-mm PTH |
| JP1 | (96.000, 14.000) | 90 deg | DEVKIT_PWR service jumper |
| R3 | (86.000, 66.000) | 0 deg | BAT_SENSE upper divider |
| R4 | (90.000, 66.000) | 0 deg | BAT_SENSE lower divider |
| C8 | (88.000, 69.000) | 0 deg | BAT_SENSE filter |
| R8 | (40.000, 35.000) | 0 deg | E220 M0 pull-down, moved out of route throat |
| R9 | (46.000, 35.000) | 0 deg | E220 M1 pull-down, moved out of route throat |

Optional mounting/strain-relief holes are omitted from this candidate; the final simplified scope did not require them, and no hole was added without a mechanically reviewed datum.

## Copper, RF, and thermal contract

- Board remains exactly 145 x 90 mm and two copper layers.
- Native `ESP32_ANTENNA_EXCLUSION` rule area is exactly X=104.7..142.7 mm, Y=52.0..90.0 mm and prohibits tracks, vias, zone fill, footprints, and pads. Contract hit list is empty. The closest new routed copper is the BAT_SENSE B.Cu segment centered at Y=51.0 mm, leaving 0.875 mm edge clearance after its 0.25-mm width.
- U4 AUX_3V3 heat spread is a solid 20.0 x 22.0 mm island on each of F.Cu and B.Cu, bounds X=17.5..37.5, Y=16.0..38.0 mm. Thermal vias are (25.3,24.8), (25.3,29.2), (26.5,26.0), and (26.5,28.0) mm; none is via-in-pad.
- Physical U4 proof: pad 1 at (17.5,24.7)=GND; small pad 2 at (17.5,27.0)=AUX_3V3; tab pad 2 at (23.8,27.0)=AUX_3V3; pad 3 at (17.5,29.3)=5V_SYS.
- A new upper B.Cu GND reference plane spans X=6.0..104.4 and Y=10.0..51.5 with a local notch only at the retained lower-plane join. The AUX thermal island is restricted to the far-left regulator area, so it does not fragment the central ESP32/E220 return plane.
- J5 remains fixed at (63,20); AUX_3V3 reaches J5.2 without entering the antenna area. The OLED mechanical/header reserve is otherwise unchanged. J3/E220 and its SMA-side access are unchanged.

## Bounded routing contract

All signal traces below are 0.25 mm. E220 and BUTTONS use the upper B.Cu plane as the return reference while on F.Cu; B.Cu crossings are short/local except the explicitly reported endpoint fans. The implementation checkpoint must preserve the stated corridors and rerun zone fill before DRC.

| Coupled group / endpoints | Layer contract | Vias | Routed length |
|---|---|---:|---:|
| E220_M0 J3.2 -> J1.8; lane Y=39.2 | B entry, F trunk, staggered B bridge, F/B endpoint | 4 | 119.496 mm |
| E220_M1 J3.3 -> J1.7; lane Y=39.9, plus R9.1 | B entry, F trunk, staggered B bridge, F/B endpoint | 6 | 122.104 mm |
| E220_AUX J3.6 -> J1.6; lane Y=42.0 | B entry, F trunk, staggered B bridge, B endpoint | 4 | 112.837 mm |
| E220_RXD J3.4 -> J2.7; lane Y=40.6 | B entry, F trunk, staggered B bridge, F/B endpoint | 4 | 138.360 mm |
| E220_TXD J3.5 -> J2.6; lane Y=41.3 | B entry, F trunk, staggered B bridge, F/B endpoint | 4 | 139.021 mm |
| GPIO13 J6.2 -> J1.3 | B escape, via at (98,20.54), F endpoint | 1 | 17.209 mm |
| GPIO14 J6.3 -> J1.5 | B escape, via at (98,23.08), F endpoint | 1 | 17.115 mm |
| GPIO18 J6.4 -> J2.9 | B escape, via at (115,20.35), F endpoint | 1 | 47.906 mm |
| GPIO19 J6.5 -> J2.10 | B escape, via at (115,22.89), F endpoint | 1 | 48.006 mm |
| GPIO23 J6.6 -> J2.15 | B/F/B bridge at X=99/102.5, through J1 pad-row gap Y=38.13, F endpoint from (118,38.13) | 3 | 53.175 mm |
| BAT_SENSE R3.2/R4.1/C8.1 -> J1.10 | local F, via at (86.725,63), B via X=96/Y=51 corridor and right-side endpoint | 1 | 72.787 mm |
| WS2812_DATA_3V3 J2.5 -> U3.2 | F/B/F, vias (105,10) and (89,58) | 2 | 108.548 mm |
| WS2812_DATA_5V U3.4 -> J9.2 | F.Cu | 0 | 12.717 mm |

Power/aux widths and endpoints:

- BAT_FUSED F1.2 -> J8.1: 1.0-mm F.Cu, 3.862-mm new endpoint leg, zero vias.
- BAT_SW J8.2 -> Q1.3: 1.0-mm F.Cu, 10.193 mm, zero vias. End-to-end F1/J8/Q1 routed path is 14.055 mm excluding the connector body.
- DEVKIT_VIN JP1.2 -> J1.1: 1.0-mm F.Cu, 12.460 mm, zero vias; JP1.1 remains on 5V_SYS.
- U4 5V_SYS feed: 0.8-mm F.Cu from the retained Y=43.5 corridor. AUX_3V3 output/J5 feed is 0.8-mm F.Cu plus dual-layer thermal copper and four vias.
- J9.1 5V_SYS uses 1.0-mm F.Cu; J9.3 uses a 0.5-mm GND stub and local GND via.

Preserved copper: protected buck refs U1/C1/C2/C3/C4/L1 are byte-normalized geometry matches to baseline. The retained Y=43.5 5V_SYS trunk is preserved except the reviewed JP1 branch isolation. J8 replaces only the rejected downstream F1-to-Q1 round-trip segment.

## Checkpoint order and expected DRC delta

1. Synchronize exact footprints/nets and prove both U4 pad-2 shapes are AUX_3V3.
2. Add/refill the antenna rule area and confirm zero hits.
3. Place fixed-coordinate parts and R8/R9; confirm J1/J2/J3/J5 unchanged.
4. Route J8/JP1, U4/AUX, RGB, E220, BUTTONS, then BAT_SENSE in that order.
5. Add/refill upper GND and AUX zones; run contract, parity, and native DRC.

Expected versus clean baseline: footprint count 33 -> 37, copper tracks 81 -> 180, vias 17 -> 60, copper zones 2 -> 5, plus one native rule area. Baseline native DRC was 0 geometric violations / 29 unconnected; candidate is 0 geometric violations / 8 unconnected. Full deterministic contract and schematic-PCB parity both pass; footprint/library and zone errors are zero.

The eight remaining airwires contain no requested E220, BUTTONS, BAT_SENSE, RGB, J8, JP1, or AUX endpoint: three are inherited GND zone/island connectivity reports, three are inherited BAT_PLUS/BUCK_IN test-point or R2 endpoint reports, and two are the explicitly pending OLED_SDA/OLED_SCL fanout. These must remain visible to the implementation/reviewer gates; they are not suppressed.

## Risks and release boundary

- GPIO23 uses a deliberately bounded three-via layer weave and a 0.25-mm passage at Y=38.13 between J1 pad rows. Its coordinates are contractual; do not improvise this route on the active PCB.
- BAT_SENSE is longer than the other button/ADC routes but remains away from BUCK_SW, uses B.Cu for the long run, and has only one via.
- Short E220 layer bridges require the upper GND plane to be filled before reviewing return continuity.
- No active PCB was used as a scratchpad. This is a plan candidate only and has no reviewer or implementation approval.

ROUTING PLAN READY
