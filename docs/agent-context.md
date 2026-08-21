# CURRENT PROJECT STATE

`STATE_SNAPSHOT_DATE`: 2026-08-21

`ACTIVE_BOARD_STATUS`: controlled Rev.1 connectivity-complete pre-production candidate; it is not production-released.

`ACTIVE_SCHEMATIC_STATUS`: approved Rev.1 source with clean ERC. `CURRENT_SCOPE`: documentation, assembly metadata, and silkscreen only. Connectivity, values, placement, tracks, vias, zones, antenna rule area, outline, and layer count are frozen.

## Active design files

* `hardware/esp32-e220.kicad_sch` — approved electrical schematic.
* `hardware/esp32-e220.kicad_pcb` — controlled PCB record, 37 footprints, 200 tracks, 58 vias, four zones, one rule area.
* `hardware/generate_esp32_e220.py` and `hardware/esp32-e220.kicad_sym` — reproducible electrical sources.
* `hardware/check_schematic_pcb_sync.py` — authoritative schematic/PCB parity gate.

## Approved electrical architecture

`BAT_PLUS -> F1 -> BAT_FUSED -> J8.1 -> external switch -> J8.2 -> BAT_SW -> Q1 -> BUCK_IN -> U1 TPS62133 -> 5V_SYS`; `D3 SMBJ10CA` shunts `BAT_FUSED` to `GND`. J8 is JST `B2B-XH-A`, 1=`BAT_FUSED`, 2=`BAT_SW`. Q1 `DMP3130LQ-7`: pin 1=`Q1_GATE`, 2=`BUCK_IN`, 3=`BAT_SW`.

`5V_SYS -> JP1 -> DEVKIT_VIN`. Normal service is `POWER_SW ON` / `JP1` closed. For USB service isolation, use `POWER_SW OFF` / `JP1` open when required; JP1 is not automatic power-domain isolation.

`5V_SYS -> U4 TLV1117LV33 -> AUX_3V3 -> J5 OLED`. U4 pin 3=`5V_SYS`, pin 2/tab=`AUX_3V3`, pin 1=`GND`; C9/C10 are local 10-uF capacitors. The released thermal geometry is an 8 x 10 mm F.Cu AUX_3V3 zone with no B.Cu AUX island or AUX thermal vias.

## Approved I/O and assembly policy

E220 uses GPIO17/TX2, GPIO16/RX2, GPIO25/M0, GPIO26/M1, and GPIO27/AUX. OLED J5 is 1=`GND`, 2=`AUX_3V3`, 3=GPIO22/SCL, 4=GPIO21/SDA; R10/R11 are `NO_FOOTPRINT_DNP` pull-up options. J6 is a `DNP_USER` six-hole BUTTONS interface: GND, GPIO13, GPIO14, GPIO18, GPIO19, GPIO23. J9 is a `DNP_USER` RGB output: `5V_SYS`, `WS2812_DATA_5V`, GND, maximum three pixels. D2, J7, and TP6...TP10 are absent. TP1...TP5 are retained plated probe holes.

U3 `SN74AHCT1G125DBVR` is TI DBV/SOT-23-5 drawing DBV0005A (`4214839/K`, 08/2024): pin 1=`GND`/OE, 2=`WS2812_DATA_3V3`/A, 3=`GND`, 4=`WS2812_DATA_5V`/Y, 5=`5V_SYS`/VCC. Its project-local released land pattern uses 0.60 x 1.10 mm pads.

Carrier sockets are factory populated: J1/J2 `SSW-115-02-G-S`, J3 `SSW-107-02-G-S`, J5 `SSW-104-02-G-S`. ESP32 DevKit, E220, and OLED are user-installed modules.

## Locked physical checkpoints

Rev.1 is a two-layer, 145 x 90 mm board. Preserve the ESP32 antenna exclusion, E220 SMA access, U1/C1/C2/C3/C4/L1 buck cell, U4/C9/C10 geometry, all completed E220/BUTTONS/RGB/BAT_SENSE/OLED routes, connected B.Cu GND regions, local F.Cu buck-GND zone, U1 GND vias, and E220 local return. The active board has zero native DRC violations and zero native unconnected items.

## Current deferred validation

OLED body fit is a first-article mechanical validation item; its electrical interface is complete. Mounting and battery strain relief are deferred to enclosure/harness work or Rev.2. Prototype validation remains required for input transient/inrush behaviour, U4 temperature under OLED load, external RGB loading, and the button panel.

## Evidence pointers

Use actual KiCad files for current geometry and counts. Current routing and U3 evidence are under `hardware/evidence/rev1-final-5-airwire-2026-08-21/` and `hardware/evidence/rev1-u3-dbv-release-2026-08-21/`. Earlier evidence mentioning partial routing, the rejected board, J7, D2, TP6...TP10, or a 300-mA AUX allocation is historical only.
