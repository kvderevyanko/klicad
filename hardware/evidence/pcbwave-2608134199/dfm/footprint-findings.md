# PCBWAVE order 2608134199 footprint and process evidence

| Scope | Evidence and conclusion |
|---|---|
| U3 | TI DBV0005A drawing 4214839/K confirms 0.60 × 1.10 mm lands, 0.95 mm pitch and 2.60 mm row centres. The table and actual PCB nets agree for all five pins. The September 11 archived Gerber still has U3's 1.50 mm row spacing. The September 15 archived Gerber and current PCB use 2.60 mm. PCBWAVE's received file is unknown. See ../footprints/ and https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf. |
| Q1 | Diodes datasheet DS38728 pp. 1, 5 gives SOT-23, 0.80 × 0.90 mm lands, G/S/D pins 1/2/3. The September 11 archived Gerber, active PCB, local footprint and Stage7 generator agree. See ../footprints/ and https://www.diodes.com/_files/datasheets/DMP3130LQ.pdf. |
| L1 | Coilcraft 745-3 and 1529-3 show 2.37 mm pad centre separation for both XFL4020 and XGL4020. The previous repo audit incorrectly inferred a 3.35 mm pitch from the drawing. See ../l1-plan/physical-plan.md for values, clearance and TPS62133 screen. |
| R1, R3, R4 | 0.90 × 0.80 mm lands on 1.70 mm centres match Yageo Mounting V10. R1 RC0603FR-07100KL is 100 kΩ ±1%, 0.10 W at 70 °C and 75 V maximum working voltage. |
| R2 | 0603WAF1004T5E, 1 MΩ ±1%, 0.10 W at 70 °C and 75 V maximum. UNI-ROYAL V.3 publishes inconsistent nominal dimensions. The chosen dimensions fit all four ranges simultaneously. See ../resistor-plan/physical-plan.md. |
| R8/R9 | CRCW060310K0FKEA, 10 kΩ ±1%, 75 V maximum, 0.10 W standard and 0.125 W extended mode at 70 °C. Vishay 20035 p. 11 reflow pattern is 0.75 × 1.00 mm per land, 0.75 mm gap. All listed R1/R2/R8/R9 parts are 0603 imperial / 1608 metric. |
| C1–C10, D3, F1 | Project-local Murata/Littelfuse geometries and values retain their manufacturer-referenced audited configuration. See ../../footprint-audit-closure-2026-09-17/footprint-audit-final-closure.md for primary-source details. |
| U1/U4, JP1, J1/J2/J3/J5, J4/J8 | See ../review/dfm-observations.md for pad and drill measurements, mask/paste and PCBWAVE process questions. |
| Board-only holes | Three Ø3.20 mm mounting holes are NPTH. Five TP plated holes remain open for probing. J6/J9 are plated and assembly-DNP. |
| Zones and antenna | The production contract checks all zone counts, H1–H3 mounting keepouts and the ESP32 antenna exclusion. Actual module and enclosure RF range remain first-article tests. See https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/pcb-layout-design.html. |

Historical single-transaction footprint scripts use older whole-board checkpoints. Their baseline delta failures are retained in ../baseline/. Current pad-level validation and the new bounded transaction checks address this revision.
