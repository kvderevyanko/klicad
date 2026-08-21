# Rev.1 pre-production functional-silkscreen physical plan

## Scope and authoritative baseline

- Active PCB inspected read-only: `hardware/esp32-e220.kicad_pcb`, SHA-256 `fa4bfbc0db8a9b99583374f5a4f6836f2e5478efc125d0bf91d148ff16ddc1be`.
- Evidence candidate: `20-silkscreen-candidate-b.kicad_pcb`.
- Coupled group: 34 new user/service/orientation text objects on `F.SilkS`; there are no electrical endpoints, track widths, vias, return-path changes, footprint moves, copper changes, rule-area changes, zone changes, or Edge.Cuts changes.
- Default text construction is 0.80 x 0.80 mm with 0.15-mm stroke. The four high-level orientation labels use 0.90 or 1.00 mm height with the same 0.15-mm stroke.

## Reviewed coordinate contract

Coordinates are board coordinates in millimetres. Rotation is zero unless shown.

| Function | Text and centre coordinates |
|---|---|
| J4 battery | `BAT` (36.25, 71.20); `+` (35.00, 79.80); `GND/-` (38.00, 79.80) |
| J8 service switch | `POWER SW` (52.25, 71.20) |
| JP1 service link | `DEVKIT PWR` (97.00, 9.30); `OPEN FOR USB` (97.00, 10.70) |
| J5 OLED | `OLED` (68.30, 23.80), 90 degrees; pad-aligned `G` (66.40, 20.00), `3V3` (66.70, 22.54), `SCL` (66.70, 25.08), `SDA` (66.70, 27.62) |
| J6 BUTTONS | `BUTTONS` (99.00, 24.35), 90 degrees; pad-aligned `G`, `1`, `2`, `3`, `4`, `5` at x=97.20 and y=18.00, 20.54, 23.08, 25.62, 28.16, 30.70 |
| J9 RGB | `RGB` (105.30, 52.70); pad-aligned `5V`, `D`, `G` at x=103.10 and y=54.00, 56.54, 59.08; `MAX 3` (105.30, 60.40) |
| TP1...TP5 | `BAT+`, `GND`, `BUCK`, `5V`, `5V` at x=48, 53, 58, 63, 68 and y=89.00 |
| ESP32 module | `ESP32` (123.70, 8.20); `USB-C ↑` (123.70, 10.20); `ANT ↓` (123.70, 54.20) |
| E220 module | retain footprint `PIN 1 / M0`; add `E220` (15.50, 57.00), `SMA / ANT ↓` (15.50, 82.50), `400/900: MATCH ANT` (15.50, 85.00) |

The ESP32 directions follow the actual footprint envelope: USB access is toward decreasing board Y, and the antenna exclusion is toward increasing board Y. The E220 footprint's existing Fab-side antenna note is at its increasing-Y end, so the retained plan's down arrow points to the actual SMA/board-edge side.

## Candidate evaluation and machine proof

Candidate A used several 0.70/0.75-mm labels and was rejected because the project DRC reported 22 `text_height` warnings. Candidate B raises every label to the project minimum of 0.80 mm; it clearly dominates and no third candidate was needed.

- Native KiCad DRC: 0 violations, 0 unconnected (`22-candidate-b-drc.json`). The scope-local `fp-lib-table` resolves `Carrier` exactly to the authoritative project-local library, so footprint/library checks are real rather than silently skipped.
- Full board contract against the named pre-silkscreen protected reference: PASS; 37 footprints, 200 tracks, 58 vias, 4 copper zones, 2 copper layers, 145 x 90 mm.
- Schematic/PCB parity: PASS; 37 assembled PCB footprints plus R10/R11 intentional no-footprint DNP (`23-candidate-b-parity.json`).
- Normalized immutability: PASS (`26-candidate-b-geometry-delta.json`). Footprint origins/rotations/pads, every segment, every via, all four copper-zone definitions plus the native antenna keepout, and Edge.Cuts are byte-normalized identical. Copper, connectivity, and placement deltas are zero.
- Visual diagnostic: `21-candidate-b-top.png`; labels remain visible for installation/service and the prior J5/J9 outline collisions are absent.

## Preservation, checkpoint order, and expected delta

Preserve all existing footprint and board graphics. Add only the 34 reviewed `F.SilkS` texts above. No existing silkscreen needs deletion or movement; `J3 PIN 1 / M0` remains. Preserve all footprints, tracks, vias, zones/fills, the `ESP32_ANTENNA_EXCLUSION`, and Edge.Cuts exactly.

Implementation checkpoint order:

1. Confirm active SHA or normalized identity to this baseline and run the protected fast contract.
2. Create a named active-board backup.
3. Apply the complete 34-text logical transaction exactly from candidate B.
4. Run the fast contract, native DRC with warnings enabled, parity, and full contract.
5. Run normalized geometry comparison; expected copper/placement/connectivity delta is none and expected DRC delta is none.

Any silk/mask, silk/edge, text-height, contract, parity, or unrelated geometry finding is unexpected: roll back this entire text transaction, prove the restored state, and stop. Principal residual risks are copying the discarded sub-0.80-mm text sizes, restoring the old left-side J5 or close-right J9 coordinates, or changing a footprint-local graphic instead of adding board text; the exact candidate and normalized-delta gate control each risk.

ROUTING PLAN READY
