# TPS62133 buck-island implementation report

Audience: `AGENT_FACING`. Date: 2026-08-18. This report records only the
approved separated-island implementation transaction on
`hardware/esp32-e220.kicad_pcb`; it is not reviewer approval or a production
release.

## Scope status

`SCOPE STATUS: READY FOR REVIEW`

Implemented scope: the U1/C1/C2/C3/C4/L1 TPS62133 cell, the Q1.2
`BUCK_IN` feed to that cell, its bounded local/plane GND returns, and the
required local VOS, SS/TR, FSW, FB, DEF, and EN connections. The accepted
J4/F1/D3/Q1/R1/R2 placement and `BAT_PLUS`, `BAT_FUSED`, and `Q1_GATE`
routing were retained. No schematic, topology, footprint source, ESP32,
E220, OLED, WS2812, RF, or module routing was changed. External `5V_SYS`
loads remain intentionally unrouted.

## C2 AVIN direct-route rework — 2026-08-18

This authorized reviewer-feedback transaction replaced **only** the C2.1
`/BUCK_IN` detour and preserved C2.2's existing local F.Cu GND-zone return
and the `(64.550,56.000)` 0.60/0.30-mm return via. Named rework backup:
`hardware/esp32-e220-pre-c2-avin-direct-rework.kicad_pcb` (SHA-256
`4d4959b6c1d2f89f76ba6e627a77cba9804accc0d2a39833e6ecd5dc107a2bd7`).

Removed copper: five F.Cu `/BUCK_IN` detour segments totalling 4.325 mm,
from C2.1 through `(66.200,56.000)`, `(66.200,57.100)`,
`(67.400,57.100)`, `(67.400,58.300)`, and `(67.700,58.300)`. Added copper:
one direct 0.20-mm F.Cu segment C2.1 `(66.725,56.000)` -> U1.10 AVIN
`(68.600,55.750)`, actual length **1.892 mm**. No other track, via, zone,
footprint, or topology was changed.

Rework baseline and final native DRC are each 0 geometry errors, 3 expected
`silk_over_copper` warnings, and 42 global out-of-scope unconnected items.
Final `cli_exit_code=0`; sync `sync_exit_code=0`, parity PASS. The new direct
AVIN bypass route and C2 local GND return are complete; `in_scope_unconnected=0`.

## Transaction control and baseline

Named pre-transaction backup:
`hardware/esp32-e220-pre-buck-candidate-implementation.kicad_pcb`
(SHA-256 `e60453f0ca4e0cf341ebb99343542a251205042650930872a6159c432f98c4b1`).

Baseline was KiCad `10.0.5`, 59 track/via objects (3 vias), 0 zones, native
DRC 0 violations / 46 global unconnected items, and parity PASS. Obsolete
legacy buck copper was removed before placement. The clean removal checkpoint
was 0 violations / 66 global unconnected items. The placement checkpoint was
0 geometry errors, 3 pre-existing `silk_over_copper` warnings, 66 global
unconnected items, and parity PASS.

## Adopted placement and pad geometry

| Ref | Position mm | Rotation |
| --- | --- | ---: |
| U1 | 70.000, 56.000 | 180 deg |
| C1 | 67.700, 59.225 | 0 deg |
| C2 | 66.000, 56.000 | 180 deg |
| C3 | 70.900, 59.225 | 180 deg |
| C4 | 67.000, 53.500 | 270 deg |
| L1 | 74.850, 56.525 | 90 deg |

L1 physical copper gap between P1 and P2 is **2.370 mm** after reload. No
via is in a pad, and none is between U1 fine-pitch pads.

Relevant actual pad centres are U1 SW 1/2/3=(71.400,56.750)/(71.400,56.250)/
(71.400,55.750), PVIN 11/12=(68.600,56.250)/(68.600,56.750), AVIN 10=
(68.600,55.750), EN 13=(69.250,57.400), VOS 14=(69.750,57.400), SS/TR 9=
(68.600,55.250), FSW 7=(69.750,54.600), C1.1=(66.700,59.225), C2.1=
(66.725,56.000), C3.1=(71.900,59.225), C4.1=(67.000,52.775), L1.1=
(74.850,58.200), and L1.2=(74.850,54.850).

## Copper and return implementation

* `BUCK_IN`: Q1.2 (64.350,77.000) -> C1.1 feed is 19.293 mm F.Cu, 1.00-mm
  wide; the C1-to-PVIN/EN local branches use 0.60/0.40/0.25-mm F.Cu. C2.1
  -> U1.10 AVIN is the direct 1.892-mm, 0.20-mm F.Cu bypass path. Total
  `BUCK_IN` copper is 27.996 mm F.Cu.
* `BUCK_SW`: all F.Cu, no via and no zone. U1 SW pads join at 0.25 mm and
  run to L1.1 with 0.70-mm copper; total copper length 5.168 mm.
* Output: L1.2 edge (73.150,54.850) -> C3.1 is 0.60-mm F.Cu plus two
  0.60/0.30-mm vias, a 4.385-mm 0.80-mm B.Cu leg, and 0.60-mm F.Cu into
  C3.1. This is local to the cell; no external `5V_SYS` load is routed.
* VOS Kelvin path is separate from the output power leg: U1.14 -> C3.1,
  3.493 mm total, 0.20-mm F.Cu, ending only at the C3 output pad.
* SS/TR path U1.9 -> C4.1 is 4.075 mm, 0.20/0.25-mm F.Cu. C4.2 returns via
  the local F.Cu GND copper and its nearby return via.
* FSW uses 0.25-mm F.Cu/B.Cu configuration copper to the local output node;
  FB, DEF, AGND, PGND, and EP connect to the local F.Cu GND return structure.

Two GND zones were added and refilled with KiCad:

| Layer | Net | Boundary mm | Filled evidence |
| --- | --- | --- | --- |
| F.Cu | `/GND` | (64.0,52.0), (70.95,52.0), (70.95,60.75), (64.0,60.75) | 3 purposeful local filled contours / 458 points |
| B.Cu | `/GND` | (42.0,46.0), (103.0,46.0), (103.0,89.0), (42.0,89.0) | 1 continuous filled contour / 685 points |

The bounded B.Cu zone retains the ESP32 antenna, module, RF, and future
routing corridors outside that central rectangle. The F.Cu zone stops at
x=70.95 mm, clear of the SW copper to its right.

New GND thermal/return vias are all 0.60-mm diameter / 0.30-mm drill:

| XY mm | Purpose |
| --- | --- |
| 64.550, 56.000 | C2 / AVIN bypass return |
| 65.950, 54.225 | C4 SS/TR return |
| 68.700, 60.300 | C1 PVIN bypass return |
| 69.900, 60.300 | C3 output return |
| 59.500, 66.275 | retained R1 ground function into B.Cu return |
| 42.200, 70.500 | retained J4/D3 ground function into B.Cu return |

The three local `5V_SYS` transition vias are also 0.60/0.30 mm at
(69.750,53.750), (72.800,54.850), and (73.100,59.225). The two existing
`Q1_GATE` vias at (56.500,69.000) and (61.650,78.500), both 0.60/0.30 mm,
were retained unchanged.

## Native DRC and sync evidence

Each checkpoint was refilled and checked natively. Counts are global KiCad
unconnected items; the only warnings throughout are the three expected
placement-candidate `silk_over_copper` warnings.

| Checkpoint | Geometry ERROR | Silk WARNING | Global unconnected |
| --- | ---: | ---: | ---: |
| A `BUCK_IN` + C1/PVIN | 0 | 3 | 61 |
| B local GND | 0 | 3 | 49 |
| C C2/AVIN | 0 | 3 | 48 |
| D SW -> L1 | 0 | 3 | 45 |
| E L1 -> C3/output return | 0 | 3 | 44 |
| F VOS | 0 | 3 | 43 |
| G SS/TR + C4 | 0 | 3 | 43 |
| H FSW/FB/DEF/EN | 0 | 3 | 42 |
| I final zone refill | 0 | 3 | 42 |

Final command:

```sh
kicad-cli pcb drc --format json --severity-all --refill-zones --save-board \
  -o hardware/evidence/buck-and-5v-checkpoints-2026-08-18/buck-final-drc.json hardware/esp32-e220.kicad_pcb
```

`cli_exit_code=0`; `geometric_violations=0`; `footprint_errors=0`;
`zone_errors=0`; warnings are only 3 silkscreen items. The final sync command
was `python3 hardware/check_schematic_pcb_sync.py --pcb
hardware/esp32-e220.kicad_pcb --output hardware/evidence/buck-and-5v-checkpoints-2026-08-18/buck-final-sync.json` and returned
`sync_exit_code=0`, `status=PASS`, 33 assembled schematic references / 33 PCB
footprints, with 0 pad/net mismatches.

`in_scope_unconnected=0`: every mandatory U1/C1/C2/C3/C4/L1/Q1-cell
connection is complete. `out_of_scope_unconnected=42`: this includes the
intentional downstream `5V_SYS` airwire between L1.2 and C7.1, which is not
part of this authorized transaction, plus the remaining board routing.

## Generated review evidence

Non-production PDFs only:

* `hardware/esp32-e220-buck-implemented-top.pdf` — F.Cu, front references,
  vias, Q1 feed, and outline context.
* `hardware/esp32-e220-buck-implemented-bottom.pdf` — B.Cu fill, via field,
  and keepout/outline context.

Retained: battery protection, Q1 gate, all non-buck routing and module/RF
boundaries. Deferred: all external `5V_SYS` distribution, ESP32/E220/OLED/
WS2812 routing, production files, and independent PCB review.

---

# Post-C3 5V_SYS distribution implementation report

Audience: `AGENT_FACING`. Date: 2026-08-18. This is the controlled physical
implementation of the explicitly authorized downstream `5V_SYS` scope. It is
not an electrical change, reviewer approval, or production release.

## Scope status

`SCOPE STATUS: READY FOR REVIEW`

Implemented only: post-C3 `5V_SYS` distribution to J1.1 (ESP32 DevKit VIN),
J3.6 (E220 VCC) with C5/C6 local bypass, U3.5/C7.1, and the TP4/TP5 probe
branch. The C5/C6 and U3/C7 ground-return copper is an inseparable local
bypass-return implementation, not a change to topology. D2 remains
`PLACEMENT_CANDIDATE_NOT_RELEASED`; no D2 VCC, GND, or DIN copper was added.

Named byte-independent pre-transaction backup:
`hardware/esp32-e220-pre-5v-distribution.kicad_pcb`, SHA-256
`85cbf701b6930138f3a75eacf4809f240ae4b8ff0a55461fabbc1510bfbd5d77`.

## Baseline and routing contract

Baseline active board: `hardware/esp32-e220.kicad_pcb`, KiCad `10.0.5`, 55
tracks, 11 vias, and 2 GND zones. Native DRC had zero geometry, zone, and
footprint errors, three inherited `silk_over_copper` warnings, and 42 global
unconnected items. Electrical parity was PASS. Allowed endpoints were C3.1's
already-approved post-C3 local output node, J1.1, J3.6/C5.1/C6.1, U3.5/C7.1,
TP4.1, and TP5.1; GND work was limited to material bypass returns.

Retained without edit: all 66 baseline copper objects (55 tracks and 11
vias), both zone boundaries, U1/C1/C2/C3/C4/L1 placement and copper,
J4/F1/D3/Q1/R1/R2 placement and copper, `BAT_PLUS`, `BAT_FUSED`, and
`Q1_GATE`. A UUID comparison after final refill retained all 66/66 baseline
copper objects. U1/C1/C2/C3/C4/L1 and J4/F1/D3/Q1/R1/R2 positions and
rotations are byte-for-byte coordinate-equivalent to the backup.

The route begins only at the retained `/5V_SYS` output via at
`(73.100,59.225)` mm, which is already connected to C3.1. It never attaches
to `BUCK_SW`, U1.14 VOS, U1.7 FSW, or pre-C3 copper. VOS and FSW copper were
not changed.

## Implemented copper

| Function | Path endpoints mm | Layer / width | Physical length |
| --- | --- | --- | ---: |
| Output escape | retained post-C3 via `(73.100,59.225)` -> new trunk via `(80.000,64.000)` | B.Cu / 1.00 mm | 8.391 mm |
| Main F.Cu trunk | `(80.000,64.000)` -> `(80.000,54.725)` -> `(80.000,43.500)` | F.Cu / 1.00 mm | 20.500 mm |
| ESP32 VIN branch | `(80.000,43.500)` -> `(96.000,43.500)` -> `(96.000,14.000)` -> J1.1 `(111.000,14.000)` | F.Cu / 1.00 mm | 60.500 mm |
| E220 feed trunk | `(80.000,43.500)` -> `(20.580,43.500)` -> C6.1 `(20.580,49.750)` -> J3.6 `(20.580,53.500)` | F.Cu / 1.00 then 0.80 mm | 69.420 mm |
| E220 C5 branch | trunk tee `(23.275,43.500)` -> C5.1 `(23.275,48.000)` | F.Cu / 0.80 mm | 4.500 mm |
| U3/C7 branch | trunk tee `(80.000,54.725)` -> C7.1 `(85.500,54.725)` | F.Cu / 0.80 mm | 5.500 mm |
| U3 VCC local branch | C7.1 -> `(87.000,54.725)` -> `(87.000,51.900)` -> `(88.525,51.900)` -> U3.5 `(88.525,53.000)` | F.Cu / 0.50 mm | 6.950 mm |
| TP4/TP5 probe branch | `(80.000,64.000)` -> `(73.000,82.000)` -> common tee `(63.000,82.000)` with stubs to TP5.1 `(68.000,87.000)` and TP4.1 `(63.000,87.000)` | B.Cu / 0.80 mm | 19.313 mm common escape; 10.000 mm TP5 route, 20.000 mm TP4 route |

The 0.60/0.30-mm new `5V_SYS` layer-transition via at `(80.000,64.000)` is
the only added power via. The TP branch is a dead-end probe branch; neither
main ESP32 nor E220 load current traverses a test-point pad.

### Local bypass and return evidence

* C6.1 is directly 3.750 mm / 0.80-mm F.Cu from J3.6. Its GND pad C6.2
  `(22.030,49.750)` has a 1.250-mm / 0.50-mm F.Cu escape to a new
  0.60/0.30-mm via at `(22.030,51.000)`, then a 2.727-mm / 0.50-mm B.Cu
  return to J3.7 GND `(23.120,53.500)`.
* C5.1 has its independent 4.500-mm branch; C5.2 `(24.725,48.000)` has a
  3.000-mm / 0.50-mm F.Cu escape to a new 0.60/0.30-mm via at
  `(24.725,51.000)`, then a 2.971-mm / 0.50-mm B.Cu return to J3.7. C5 and
  C6 are therefore not daisy-chained through either capacitor.
* C7.2 `(85.500,53.275)` reaches a new 0.60/0.30-mm B.Cu-return via at
  `(85.500,51.900)` over 1.375 mm / 0.50-mm F.Cu. U3.1 and U3.3 GND have
  their own 0.60/0.30-mm return vias at `(87.200,56.500)` and
  `(91.000,55.000)`, with 1.724-mm and 1.050-mm / 0.50-mm F.Cu escapes.
  All three enter the retained continuous B.Cu GND fill.

Total added copper is 215.074 mm of `/5V_SYS` (167.370 mm F.Cu and
47.704 mm B.Cu) and 14.097 mm of `/GND` bypass return (8.399 mm F.Cu and
5.698 mm B.Cu), plus six new 0.60/0.30-mm vias: one `/5V_SYS`, five `/GND`.

## Boundaries, fills, and silkscreen

No new copper, via, or zone enters the ESP32 antenna reserve
`x=104.7..142.7, y=52.0..90.0` mm. The J1.1 entry is at y=14.000 mm and the
branch remains left of the module boundary until that direct pin entry. E220
work is limited to the upper socket VCC/bypass cluster at y=43.500..53.500
mm; no new copper is in the lower SMA/bottom-access region. No part was
moved.

Both existing GND zones were refilled without boundary edits: F.Cu remains
three filled contours / 421 points, while the B.Cu `(42,46)..(103,89)` zone
remains one continuous filled contour / 751 points. It is not extended into
the ESP32 antenna or E220 SMA access regions.

After the electrical scope passed, only reference text was moved: U1 F.Silk
reference `(70.000,58.850)` -> `(61.500,61.500)` mm and L1 F.Silk reference
`(72.100,56.525)` -> `(78.000,51.000)` mm. This cleared all three inherited
silk warnings without moving parts or copper.

## Checkpoints and validation

| Checkpoint | Scope | Geometry / zone / footprint errors | Silk warnings | Global unconnected |
| --- | --- | ---: | ---: | ---: |
| A | C3 output escape, trunk, C7.1 terminus | 0 / 0 / 0 | 3 | 41 |
| B | ESP32 VIN | 0 / 0 / 0 | 3 | 40 |
| C | E220 VCC, C5/C6, bypass returns | 0 / 0 / 0 | 3 | 35 |
| D | U3/C7 VCC and returns | 0 / 0 / 0 | 3 | 31 |
| E | TP4/TP5 branch | 0 / 0 / 0 | 3 | 29 |
| Final after reference-text move | full scope | 0 / 0 / 0 | 0 | 29 |

The first D attempt created two local GND/5V shorts at U3.1; that transaction
alone was removed, baseline C was proven, and the lower-left U3.1 escape was
rerouted to `(87.200,56.500)`. A later geometry audit removed one same-net
duplicate B.Cu TP branch segment. Neither failed attempt remains in the
active PCB.

Final native command:

```sh
kicad-cli pcb drc --format json --severity-all --refill-zones --save-board \
  -o hardware/evidence/buck-and-5v-checkpoints-2026-08-18/5v-final-drc.json hardware/esp32-e220.kicad_pcb
```

`cli_exit_code=0`; `geometric_violations=0`; `zone_errors=0`;
`footprint_errors=0`; `in_scope_unconnected=0`; final silk warnings=0.
The checker command `python3 hardware/check_schematic_pcb_sync.py --pcb
hardware/esp32-e220.kicad_pcb --output hardware/evidence/buck-and-5v-checkpoints-2026-08-18/5v-final-sync.json` returned
`sync_exit_code=0`, parity PASS, 33 assembled schematic references / 33 PCB
footprints, and zero pad/net mismatches.

The exact sole remaining `/5V_SYS` airwire is D2.1 `(94.050,52.400)` to the
U3-side F.Cu `/5V_SYS` segment ending at `(87.000,51.900)`. It is deferred
solely because D2 is not released. There are no other `/5V_SYS` airwires.

The exact 29 final global airwires are that D2.1 item plus 28 out-of-scope
items: R8.2-GND to B.Cu GND track; R9.2-GND to R8.2-GND; F.Cu GND track to
R9.2-GND; F.Cu GND zone to J5.1; F.Cu GND zone-to-zone; D2.3-GND to GND via;
D2.3-GND to J1.2; J2.2-GND to J1.2; U3.2 to J2.5; U3.4 to D2.4; J3.1 to
R8.1; TP6 to R8.1; TP6 to J1.8; J3.2 to R9.1; TP7 to R9.1; TP7 to J1.7;
J3.3 to TP9; TP9 to J2.7; J3.4 to TP10; TP10 to J2.6; J3.5 to TP8; TP8 to
J1.6; TP1 to BAT_PLUS track; R2.1 to BUCK_IN track; BUCK_IN track to TP3;
J5.2 to J2.1; J5.4 to J2.11; and J5.3 to J2.14.

## Non-production evidence

* `hardware/esp32-e220-5v-top.pdf` — F.Cu distribution, reference text, and
  outline context.
* `hardware/esp32-e220-5v-bottom.pdf` — B.Cu GND fill, return vias, TP
  branch, and outline context.

Retained: the approved buck cell and input protection; all previous copper;
ESP32 USB/module-removal/antenna boundary; E220 socket/SMA/RF boundary; OLED
uncertainty; and D2 release hold. Deferred: D2 and all non-authorized signal,
OLED, UART, GPIO, and full-board routing. No production outputs were created.
