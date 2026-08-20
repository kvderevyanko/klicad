# Rev.1 expansion and service interface — routing contracts

Audience: `AGENT_FACING`. Active board: `hardware/esp32-e220.kicad_pcb`.
Named pre-transaction backup: `hardware/esp32-e220-pre-rev1-expansion.kicad_pcb`.

## BASELINE

* KiCad: `10.0.5`; SHA-256 of active board and backup before mutation:
  `d87c0ff900c9ce113c4c36b5a2785a65848077673e34804a8e9166cec2a6b76c`.
* 33 footprints, 81 segments, 17 vias, 2 zones. Native `kicad-cli pcb drc`
  reports zero violations and 29 global unconnected items.
* Schematic-PCB parity is the approved pre-layout `FAIL`: ten missing Rev.1
  footprints plus pad-net deltas J1.1, J5.2, and Q1.3. Details are retained
  in `baseline-parity.json`.
* Preserved copper: all accepted BAT_PLUS, D3 shunt, BUCK_IN, BUCK_SW, C1/C2/
  C3/C4, VOS, FSW, E220 VCC/C5/C6, and U3/C7 geometry. Deferred items are all
  signal/OLED routing, D2, and the existing TP1/TP3 airwires.

## A — external switch harness J8

Affected refs/nets: J8, F1.2 `BAT_FUSED`, D3.1 `BAT_FUSED`, Q1.3 `BAT_SW`.
J8 is `Connector_JST:JST_VH_B2PS-VH_1x02_P3.96mm_Horizontal`, pin 1
`BAT_FUSED`, pin 2 `BAT_SW`; its pin-1 mark and 1.70-mm drilled PTH pads are
retained from the KiCad JST VH land pattern. Replaces only the accepted F1-to-
Q1 downstream `BAT_FUSED` copper. F.Cu is 1.00 mm, no vias. Return path is
not applicable to the switched positive harness; D3 stays upstream. J8 is
kept accessible at the input side. Acceptance: no new DRC category and exact
Q1/J8 pad parity.

## B — DEVKIT power isolation JP1

Affected refs/nets: JP1, J1.1; `5V_SYS`, `DEVKIT_VIN`. JP1 is
`Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical`, pin 1 `5V_SYS`,
pin 2 `DEVKIT_VIN`. Only the existing final 5V branch at J1.1 is replaced;
the post-C3 trunk, VOS Kelvin, and all other 5V branches stay fixed. F.Cu
uses 1.00 mm for the main branch and 0.80 mm local branch, with no via in the
JP1-to-J1 service branch. Acceptance: no new DRC category and exact
J1/JP1 parity.

## C — BAT_SENSE

Affected refs/nets: R3, R4, C8, J1.10; `BUCK_IN`, `BAT_SENSE`, `GND`.
R3/R4/C8 use audited project 0603/0603/0603 land patterns: 0.95 x 1.00-mm
lands on 1.45-mm centres. It is a low-current 0.25-mm F.Cu branch, placed
away from BUCK_SW with a local GND via at C8. Acceptance: no BUCK_SW geometry
change, no new DRC category, and exact pad parity.

## D — U4 AUX_3V3 cell

Affected refs/nets: U4, C9, C10; `5V_SYS`, `AUX_3V3`, `GND`. U4 uses
`Package_TO_SOT_SMD:SOT-223-3_TabPin2`, verified against TI DCY: pad 1=GND,
pad 2 and tab=AUX_3V3, pad 3=5V_SYS. C9/C10 use the project Murata 0805 land
pattern (1.40 x 1.40-mm lands at 2.00-mm centres). A 0.80-mm local 5V branch
uses B.Cu only outside the preserved buck geometry and transitions with a
0.60/0.30-mm via. A solid-connected AUX_3V3 zone is added on each outer layer
with at least four 0.60/0.30-mm thermal vias within 3 mm of the tab. GND
capacitor returns use local vias. Acceptance: refill, zero native geometry,
zone, and footprint errors, and final full parity PASS. Actual thermal copper
dimensions and constraints are recorded in the final report rather than
assumed here.
