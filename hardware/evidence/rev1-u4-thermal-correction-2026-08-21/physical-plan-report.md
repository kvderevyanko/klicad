# Rev.1 U4 thermal correction physical plan

## Scope and authority

- Retained successful source: `hardware/evidence/rev1-final-integration-2026-08-21/07-final-approved-checkpoint.kicad_pcb`, SHA-256 `b10bc94138397f3d3d393804dd02d285b2f19eaa5c3341b920835085dbf23464`.
- Corrected evidence candidate: `02-u4-thermal-corrected-candidate.kicad_pcb`, SHA-256 `c492d1254e0ef19c95fe6a38357b1f93a4fc85c93c536a4da94afaf2f2e7e3de`.
- The active PCB remained SHA-256 `bf502dfde6ebb1f05d5d8f95fa77dc6f3d484fd9ddcdb47d3511c4b82b5f5036` throughout planning.
- Only the obsolete U4 AUX_3V3 thermal implementation and the two required local AUX bridges differ. All footprint placements, all non-AUX tracks, and all non-AUX zone/rule-area outlines are semantically identical to the retained source.

## Thermal basis

Official TI source: `tlv1117lv-official.pdf`, TLV1117LV datasheet Rev. C, SHA-256 `8bc2da7065088981056267ee366ee324cd46c5fa999f4cf076317b1b390cab53`.

- DCY/SOT-223 `RθJA = 62.9 degC/W`; TI states that PCB free copper area, heavier copper, and plated through holes affect heat removal. This metric is a reference-board value, not a guarantee for arbitrary geometry.
- `P_load = (5.0 - 3.3) * 0.1001 = 0.17017 W`.
- Conservative additional input ground/quiescent term: `5.0 * 0.000100 = 0.00050 W` using the datasheet 100-uA maximum. Therefore `P_total <= 0.17067 W`.
- Reference rise: `0.17067 * 62.9 = 10.735 degC`.
- At `TA = 50 degC`: reference `TJ = 60.735 degC`; margin to 125 degC is `64.265 degC`.
- At `TA = 60 degC`: reference `TJ = 70.735 degC`; margin is `54.265 degC`. The corresponding maximum allowable effective `θJA` before reaching 125 degC is about `380.85 degC/W`, showing large analytical margin while preserving the explicit limitation on applying the JEDEC reference value to this board.
- Prototype item remains `DEFERRED (explicitly allowed): U4 TEMPERATURE VALIDATION`.

## Bounded routing contract

Coupled group: U4, C9, C10, the local AUX_3V3 F.Cu spread, and the unchanged J5.2 AUX feed.

| Item | Exact placement / endpoint | Contract |
|---|---|---|
| U4 | origin `(20.650,27.000)`, 0 deg | Retain `Package_TO_SOT_SMD:SOT-223-3_TabPin2`; its 2.3-mm lead pitch, three 2.0 x 1.5-mm lead lands, and 2.0 x 3.8-mm tab land are compatible with TI DCY / JEDEC TO-261 AA mechanical data. Pad 1 `(17.5,24.7)` GND; small pad 2 `(17.5,27.0)` AUX_3V3; tab pad 2 `(23.8,27.0)` AUX_3V3; pad 3 `(17.5,29.3)` 5V_SYS. |
| C9 | origin `(17.500,33.000)`, 270 deg | Retain. Pad 1 `(17.5,32.0)` 5V_SYS is 2.7 mm center-to-center from U4.3 on the existing 0.8-mm F.Cu path; pad 2 `(17.5,34.0)` GND retains its 0.5-mm stub/via. |
| C10 | origin `(14.400,27.000)`, 180 deg | Retain. Pad 1 `(15.4,27.0)` AUX_3V3 is 2.1 mm center-to-center from U4 small pad 2 on the existing 0.8-mm F.Cu path; pad 2 `(13.4,27.0)` GND retains its 0.5-mm stub/via. |
| J5.2 | `(63.000,22.540)` | Retain the proven 0.8-mm F.Cu segment `(37.5,22.54) -> (63.0,22.54)`. |

Replace the old 20 x 22 mm F.Cu and B.Cu zones and the four AUX vias with exactly:

- one solid/full-pad-connect F.Cu AUX_3V3 rectangle, priority 2, X=`22.0..30.0` mm and Y=`22.0..32.0` mm: 8 x 10 mm nominal outline, 80 mm2;
- one 0.8-mm F.Cu pad bridge `(17.5,27.0) -> (23.8,27.0)`, connecting both physical pad-2 shapes and C10 to the tab spread;
- one 0.8-mm F.Cu route bridge `(30.0,22.54) -> (37.5,22.54)`, joining the local spread to the retained J5.2 segment;
- no B.Cu AUX_3V3 zone and zero AUX_3V3 thermal vias.

The unchanged 5V_SYS input path is 0.8-mm F.Cu. No new vias or layer changes are permitted in this coupled group.

## Return path, keepouts, and repairability

- Removing the old B.Cu AUX island restores rather than fragments the upper B.Cu GND plane. Existing local GND stubs/vias for U4.1, C9.2, and C10.2 remain unchanged. The three inherited GND airwires are unchanged and are not caused by this correction.
- The native `ESP32_ANTENNA_EXCLUSION` remains X=`104.7..142.7`, Y=`52.0..90.0` mm. Contract hit list is empty; the U4 correction is far outside it.
- No E220/SMA geometry, fixed module, major placement, non-AUX route, protected buck item, board outline, or layer stack changes.
- No via-in-pad, no underside AUX copper, and no thermal-via array. The standard pads, single-layer local spread, and exposed component perimeter preserve hand rework access.

## Checkpoint order and expected delta

1. Prove retained source SHA-256 and active-board non-mutation.
2. Remove exactly the two obsolete AUX zones and four named AUX vias.
3. Add the single local F.Cu zone and the two 0.8-mm F.Cu bridges.
4. Refill all zones; check for AUX airwires before accepting the checkpoint.
5. Run full board contract with the pre-Rev.1 protected reference, standalone parity, and native DRC with `--refill-zones`.

Expected versus retained source: footprints `37 -> 37`; tracks `180 -> 182`; vias `60 -> 56`; copper zones `5 -> 4`; native rule areas `1 -> 1`; geometric/library/zone violations `0 -> 0`; visible airwires `8 -> 8`. The eight retained airwires have the same net-category signature: GND, BAT_PLUS, BUCK_IN, OLED_SCL, and OLED_SDA; no AUX_3V3 airwire remains.

## Deterministic result

- Full board contract: PASS.
- Duplicate-pad consistency: PASS.
- Schematic-PCB parity: PASS, zero reference/property/pad-net mismatches.
- Native DRC after zone refill: 0 violations; 0 geometric, footprint/library, and zone violations; 8 unchanged inherited/deferred airwires.
- AUX connectivity: C10.1 -> U4 small pad 2 -> U4 tab pad 2 -> local F.Cu spread -> J5.2 complete.
- Antenna exclusion: PASS.
- Protected buck checkpoint: PASS.
- Zone-fill correctness: candidate was saved after `pcbnew.ZONE_FILLER`; native DRC independently refilled zones and reported zero zone violations and no AUX_3V3 unconnected item.

Risk: actual board `RθJA` depends on the manufactured PCB and ambient airflow. The calculation has large margin, but it does not convert TI's reference-board metric into a geometry-independent guarantee. Prototype U4 temperature validation remains the explicit deferred control.

SCOPE VERDICT: REV1 U4 THERMAL PLAN PASS

ROUTING PLAN READY
