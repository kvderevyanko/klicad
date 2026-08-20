# Rev.1 physical recovery — read-only planner result

Role: `pcb_routing_planner`. The active PCB was not modified. The preferred
candidate was built from `hardware/esp32-e220-pre-rev1-expansion.kicad_pcb`
plus current schematic connectivity and retained only as planner evidence.

## Machine result

- Preferred temporary board: `/tmp/esp32-e220-rev1-plan-v3/esp32-e220-rev1-physical-plan-candidate.kicad_pcb`
- Retained evidence copy: `esp32-e220-rev1-physical-plan-candidate.kicad_pcb`
- Retained copy SHA-256: `07bff09d339994b226fd517e2c265d115b2203c0cc6d657f1481558d829d3819`
- Fast and full board contract: PASS.
- Native KiCad 10.0.5 DRC: 0 violations; 55 unconnected items.
- Schematic-PCB parity: PASS; 43 assembled schematic references, 43 PCB
  electrical references, no missing/board-only/property/pad-net mismatches.
- Candidate counts: 49 footprints including six anonymous mechanical-only
  footprints, 89 tracks, 24 vias, 5 copper zones, 2 copper layers.
- Outline: 145.0 x 90.0 mm, unchanged.
- Protected `U1/C1/C2/C3/C4/L1` normalized geometry: unchanged.

## Preferred placement and bounded copper contract

| Item | X mm | Y mm | Rotation | Contract |
| --- | ---: | ---: | ---: | --- |
| U4 | 20.650 | 27.000 | 0 deg | `SOT-223-3_TabPin2`; pad 1 GND, both physical pad-2 shapes AUX_3V3, pad 3 5V_SYS |
| C9 | 17.500 | 33.000 | 270 deg | pad 1 5V_SYS, pad 2 GND; 0.80-mm F.Cu input branch |
| C10 | 14.400 | 27.000 | 180 deg | pad 1 AUX_3V3, pad 2 GND; 0.80-mm F.Cu output branch |
| J6 | 101.000 | 26.000 | 0 deg | `PinHeader_2x05_P2.54mm_Vertical`; DNP/user solder header |
| J7 | 43.000 | 20.000 | 0 deg | `PinHeader_2x06_P2.54mm_Vertical`; DNP/user solder header |
| J8 | 51.000 | 76.000 | 0 deg | `JST_B2B-XH-A_1x02_P2.50mm_THT`; 1=BAT_FUSED, 2=BAT_SW |
| JP1 | 96.000 | 14.000 | 90 deg | 1=5V_SYS, 2=DEVKIT_VIN; 1.00-mm F.Cu to J1.1 |
| R3 | 85.000 | 38.000 | 0 deg | 10.0 kOhm, BUCK_IN to BAT_SENSE |
| R4 | 89.000 | 38.000 | 0 deg | 3.30 kOhm, BAT_SENSE to GND |
| C8 | 92.000 | 38.000 | 0 deg | 100 nF, BAT_SENSE to GND |

U4 thermal copper is a priority-2 AUX_3V3 rectangle on both F.Cu and B.Cu:
X=17.500...37.500 mm, Y=16.000...38.000 mm (20.0 x 22.0 mm).
Both pad-2 shapes use solid zone connection. Four 0.60/0.30-mm AUX_3V3 vias
are at `(25.300,24.800)`, `(25.300,29.200)`, `(26.500,26.000)`, and
`(26.500,28.000)` mm. Their centre distances from the tab centre
`(23.800,27.000)` are 2.663, 2.663, 2.879, and 2.879 mm; none is via-in-pad.
The three local GND endpoints use 0.50-mm F.Cu to 0.60/0.30-mm vias and a
priority-1 B.Cu GND extension X=6.000...44.000, Y=10.000...48.000. That zone
overlaps the retained central B.Cu GND plane at X=42...44/Y=46...48 while
the higher-priority AUX zone carves only the upper-left thermal island.

J8 replaces only the downstream F1-to-Q1 copper. The 1.00-mm F.Cu path is
F1.2 `(47.138,76.000)` to J8.1 `(51.000,76.000)` = 3.862 mm, then J8.2
`(53.500,76.000)` through `(56.500,76.000)` and `(60.000,74.000)` to Q1.3
`(63.000,75.000)` = 10.193 mm. Total carrier copper around the external
switch is approximately 14.055 mm with zero vias. The retained F1-to-D3
BAT_FUSED branch is unchanged. Official JST XH evidence rates the selected
B2B-XH-A/XHP-2 family at 3 A with AWG22, above the 2-A project requirement.

The real KiCad rule area is named `ESP32_ANTENNA_EXCLUSION`, spans
X=104.700...142.700/Y=52.000...90.000 mm on F.Cu and B.Cu, and prohibits
tracks, vias, pads, zone fill, and footprints. Existing graphical annotation
is retained. The deterministic antenna check passes. Nearest new mechanical
geometry is H4: its 2.1-mm courtyard ends at X=103.100, leaving 1.600 mm to
the rule boundary. No expansion copper enters the rule area.

Mechanical-only NPTH positions:

- M3 3.20-mm holes: `(7.000,7.000)`, `(80.000,7.000)`,
  `(7.000,44.000)`, `(101.000,84.000)` mm.
- Cable-tie 2.50-mm holes: `(33.000,84.000)`, `(40.000,84.000)` mm.

J7's courtyard ends at X=47.375, leaving 3.625 mm to the OLED reserve at
X=51.000. The nearest new strain-relief courtyard is 4.325 mm right of the
J3/E220 footprint courtyard; the upper-left M3 courtyard is 4.875 mm above
it. No item occupies the E220 module/SMA access boundary. J6 has a 3.750-mm
courtyard gap to J1 and is outside the antenna rule area. JP1 remains directly
accessible above the DevKit power entry. All new connectors are PTH and J6/J7
are 2.54-mm serviceable solder points.

## Required remaining-signal proof

The candidate is not releasable as a routing plan because the mandated
two-layer future-signal feasibility proof is absent. R8/R9 and TP6...TP10
remain at their retained baseline positions. The directly applicable machine
evidence in `hardware/esp32-e220-signal-routing-report.md` proves that this
same placement/corridor set cannot accept M0, M1, and AUX together after M0/M1
are routed: the AUX checkpoint produces 25 geometric violations. This
candidate adds J8/holes/headers and does not relocate those movable endpoints,
so it does not remove the documented blocker. RXD/TXD and the full J6/J7 plus
BAT_SENSE endpoint fanout were not experimentally routed either.

A safe revision must relocate R8/R9 and/or TP6...TP10 and produce a clean
temporary-board route proof for the coupled E220 group plus J6/J7/BAT_SENSE,
while preserving the exact antenna, power, OLED, RF, and protected-buck
contracts above. Expected native DRC delta for the accepted placement-only
candidate is zero violations; no active-board implementation is authorized
from this blocked plan.

ROUTING PLAN BLOCKED
