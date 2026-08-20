# CURRENT PROJECT STATE

`STATE_SNAPSHOT_DATE`: 2026-08-20

`ACTIVE_BOARD_STATUS`: controlled routing record; partial Rev.1 expansion is blocked and not physically approved

`ACTIVE_SCHEMATIC_STATUS`: bounded Rev.1 scope simplification implemented; independent electrical review required before physical use
`CURRENT_SCOPE`: physical recovery remains paused pending electrical review of the simplified source

## Active design files

* `hardware/esp32-e220.kicad_sch` — approved electrical schematic.
* `hardware/esp32-e220.kicad_pcb` — active controlled-routing PCB record, not a production release.
* `hardware/generate_esp32_e220.py` and `hardware/esp32-e220.kicad_sym` — reproducible electrical sources.
* `hardware/check_schematic_pcb_sync.py` — authoritative schematic/PCB parity gate.

## Hard project constraints

Rev.1 prefers two copper layers and a 145 x 90 mm outline. Preserve ESP32 DevKit USB-C access, ESP32 antenna exclusion, E220 SMA/RF access, module-removal clearance, and protected ESP32/E220/J4 locations. Planning rules: SIGNAL 0.25 mm preferred / 0.20 mm minimum and 0.20 mm clearance; POWER 1.0 mm preferred (justified local `5V_SYS` branches 0.8 mm); `BUCK_SW` short F.Cu, no via, 0.70 mm accepted only where 0.80 mm fails actual clearance.

## Approved electrical architecture

Active input path: `BAT_PLUS -> F1 -> BAT_FUSED -> J8.1 -> external mechanical switch -> J8.2 -> BAT_SW -> Q1 -> BUCK_IN -> U1 TPS62133 -> 5V_SYS`; `D3 SMBJ10CA` shunts `BAT_FUSED` to `GND`. J8 is JST `B2B-XH-A`, 1=`BAT_FUSED`, 2=`BAT_SW`. Q1 `DMP3130LQ-7`: pin 1=`Q1_GATE`, 2=`BUCK_IN`, 3=`BAT_SW`. U1 `TPS62133RGT`: SW 1/2/3=`BUCK_SW`; PG 4=NC; FB 5=`GND`; AGND/EP=`GND`; FSW 7=`5V_SYS`; DEF 8=`GND`; SS/TR 9=`SS_TR` to C4; AVIN 10/PVIN 11/12=`BUCK_IN`; EN 13=`BUCK_IN`; VOS 14 Kelvin to the C3 `5V_SYS` node; PGND 15/16=`GND`.

`U4` is `TLV1117LV33DCYR`: pin 3=`5V_SYS`, pin 2/tab=`AUX_3V3`, pin 1=`GND`; C9/C10 are local 10-uF `GRM21BR61E106KA73`. Do not restore superseded carrier USB-C/TUSB320/eFuse circuitry. Primary electrical source: `hardware/evidence/rev1-expansion-2026-08-20/aux-3v3-electrical-handoff.md`.

## Approved GPIO map

E220: GPIO17/TX2 -> RXD, GPIO16/RX2 <- TXD, GPIO25 -> M0, GPIO26 -> M1, GPIO27 <- AUX; M0/M1 have local 10-kOhm pull-downs. OLED J5: 1=`GND`, 2=`AUX_3V3`, 3=GPIO22/SCL, 4=GPIO21/SDA; R10/R11 are `NO_FOOTPRINT_DNP` 4.7-kOhm options to `AUX_3V3`. J6 is a DNP active-low button interface only: 1=`GND`, 2=GPIO13, 3=GPIO14, 4=GPIO18, 5=GPIO19, 6=GPIO23; no external voltage or general-GPIO use. J7 is removed and J1.9/GPIO33 is intentionally NC. U3 `SN74AHCT1G125` drives J9 / functional `J_RGB`: 1=`5V_SYS`, 2=`WS2812_DATA_5V`, 3=`GND`, maximum three external WS2812B-V5 pixels. Onboard D2 and TP6...TP10 are removed; TP1...TP5 remain.

## Approved power budget

`5V_SYS` design allocation is 985.692 mA including 20% margin: 500.000 mA DevKit + 110.000 mA E220 + 1.510 mA U3 + 100.100 mA U4/OLED accounting + 109.800 mA for at most three external WS2812B-V5 pixels gives an 821.410-mA subtotal and 164.282-mA margin. `TPS62133` continuous rating is 3.0 A. `AUX_3V3` allocation is OLED/J5-only at 100 mA; J6 has no power pin. `DEVKIT_3V3` is J2.1 only and is not an accessory supply. Evidence: `hardware/evidence/rev1-scope-simplification-2026-08-20/power-budget.md`.

## Locked physical checkpoints

The accepted controlled-routing checkpoint retains the input protection, TPS62133 buck cell, post-C3 `5V_SYS` distribution, VOS Kelvin connection, FSW connection, bounded B.Cu GND plane, and local F.Cu buck-GND zone. The protected buck-cell references are `U1`, `C1`, `C2`, `C3`, `C4`, `L1`. Evidence: `hardware/esp32-e220-power-routing-report.md` and `hardware/evidence/buck-and-5v-checkpoints-2026-08-18/`.

`hardware/esp32-e220-assistant-buck-candidate.kicad_pcb` is an unreleased 0-track/0-via/0-zone historical candidate, not routing authority. The active board is still the rejected partial Rev.1 physical implementation and was not synchronized during the electrical simplification. It therefore contains stale D2/TP6...TP10 and old J6/J7-era parity state in addition to the rejected U4/antenna defects. It must be recovered only after the required reviewer and physical gates. Evidence: `hardware/evidence/rev1-expansion-2026-08-20/physical-handoff.md` and `hardware/evidence/rev1-scope-simplification-2026-08-20/handoff.md`.

## Mechanical/RF keepouts

Conservative ESP32 antenna exclusion: X=104.7...142.7 mm, Y=52.0...90.0 mm. No tracks, vias, copper/zones, or new footprint bodies/pads in this region. Existing approved socket-boundary behavior is explicitly exempt only where recorded in the current board/checker evidence. Preserve E220 RF separation and SMA access.

## Current assembly policy

Factory PCBA installs carrier sockets, battery protection, TPS62133 cell, passives, and released carrier circuitry. ESP32 DevKit, E220, and OLED are user-installed. Normal service: `POWER_SW ON`/`JP1` closed; for USB service, `POWER_SW OFF`/`JP1` open when isolation is desired. This is not complete GPIO isolation: powered peripherals must not drive GPIO with an unpowered DevKit.

## Current unresolved/deferred items

OLED mechanical datum/fanout is pending. Non-power E220/OLED/button/RGB/BAT_SENSE routing is pending; no signal test-point endpoints remain. `AUX_3V3` physical footprint verification, thermal copper/vias, connector placement, parity, and DRC are pending. Prototype validation remains required for transient/inrush/thermal/current behavior, the external three-pixel RGB chain, and the button panel. The active board still has stale D2/TP6...TP10 objects that later physical recovery must remove transactionally.

## Authoritative evidence pointers

Use actual KiCad files for mutable geometry and counts. For the current simplified electrical scope and power policy use `hardware/evidence/rev1-scope-simplification-2026-08-20/handoff.md` and `power-budget.md`; older Rev.1 expansion evidence is historical where it mentions J7, D2, TP6...TP10, or a 300-mA AUX allocation. For partial physical state use `hardware/evidence/rev1-expansion-2026-08-20/physical-handoff.md`; for accepted buck/5V checkpoint use `hardware/esp32-e220-power-routing-report.md`.
