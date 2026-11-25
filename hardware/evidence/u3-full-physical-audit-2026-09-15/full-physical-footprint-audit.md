# Full physical-footprint audit — read-only baseline

Date: 2026-09-15.  Scope is the active controlled board SHA-256
`61549b45d4fe336986e76bcc78c5ca5532e67df604d155b140b1fd8a9d1bb109`, its
project-local library/generator, and the Q1-correction F.Cu Gerber
`7ae2eff8b659490bfb438997098e9cf46f438be53fdd90fdc0b76968a7c34252`.
The release self-audit records this exact board SHA; therefore its Gerber is
the applicable pre-U3-correction manufactured geometry, not a proxy.

## Method and hard limit

For every one of the 30 `PCBA_POPULATE` references (25 BOM rows), KiCad pad
count/number/net were machine-read and compared with the schematic netlist;
the result is `00-baseline-parity.json`: 0 pad/net mismatches.  F.Cu Gerber
X2 `P` and `N` attributes were inspected.  A status of PASS below requires an
actual manufacturer land-pattern drawing with a numerical match.  A body or
pitch-only drawing, an IPC/project pattern, a stale URL, or no exact MPN is
**UNVERIFIED**, never PASS.  Thus this is deliberately not a production
approval.

Current board source is `hardware/esp32-e220.kicad_pcb`; source-of-truth for
all project-local entries is `hardware/generate_stage7_footprints.py`.

## U3: real mismatch, numerical comparison

Primary source: TI `SN74AHCT1G125` SCLS378P Rev. P, package drawing
`DBV0005A`, drawing `4214839/K`, August 2024, retained as
`hardware/evidence/rev1-u3-dbv-release-2026-08-21/ti-sn74ahct1g125-rev-p.txt`
(original TI data sheet: https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf).
It identifies `SN74AHCT1G125DBVR` as **SOT-23 (DBV), 5**, not DRL.

TI DBV body is 2.75–3.05 by 1.45–1.75 mm (1.45-mm maximum height), lead
pitch is 0.95 mm for the three-pin side, lead width 0.30–0.50 mm, and the
example board layout is five 1.10 x 0.60-mm lands: three left-side lands at
Y=+0.95/0/-0.95 and two right-side lands at Y=+0.475/-0.475; side centrelines
are X=-1.300/+1.300.  The drawing's 2.60-mm arrows are explicitly
**pad-centre to pad-centre**, not an outer-copper span. Coordinates below use
the TI view: long land dimension X, body long dimension X, pin 1 upper-left.

| DBV item, mm | TI `4214839/K` | current U3 / released F.Cu Gerber | difference |
|---|---:|---:|---:|
| Land size (all 5) | 1.10 x 0.60 | 0.60 x 1.10 | axes rotated 90 degrees |
| 1 centre | (-1.300, +0.950) | (-0.950, +0.750) | (+0.350, -0.200) |
| 2 centre | (-1.300, 0.000) | (0.000, +0.750) | (+1.300, +0.750) |
| 3 centre | (-1.300, -0.950) | (+0.950, +0.750) | (+2.250, +1.700) |
| 4 centre | (+1.300, -0.475) | (+0.475, -0.750) | (-0.825, -0.275) |
| 5 centre | (+1.300, +0.475) | (-0.475, -0.750) | (-1.775, -1.225) |
| 1–2/2–3 pitch | 0.950 | 0.950, but horizontal | wrong axis |
| 5–4 pitch | 0.950 | 0.950, but horizontal | wrong axis |
| side-centre separation | 2.600 horizontal | 1.500 vertical | wrong axis and -1.100 |
| F.Fab body | max 3.00 x 1.75, pin-1 at upper-left | 3.00 x 1.75, pin-1 mark lower-left | pin relationship rotated |
| courtyard | manufacturer does not prescribe one | 3.50 x 3.60 | not a pass criterion |

At board origin `(89.000,54.000), 0 deg`, TI DBV centres should be 1
`(87.700,54.950)`, 2 `(87.700,54.000)`, 3 `(87.700,53.050)`, 4
`(90.300,53.525)`, 5 `(90.300,54.475)` mm.  Actual Gerber flashes are 1
`(88.050,54.750)`, 2 `(89.000,54.750)`, 3 `(89.950,54.750)`, 4
`(89.475,53.250)`, 5 `(88.525,53.250)` mm and use aperture D11, a 0.60 x
1.10-mm rounded rectangle.  This agrees byte-for-byte with the active board;
Gerber generation is not the source of the error.

| physical DBV pin / TI function | footprint pad | schematic net | Gerber net |
|---|---:|---|---|
| 1 / OE | 1 | GND | GND |
| 2 / A | 2 | WS2812_DATA_3V3 | WS2812_DATA_3V3 |
| 3 / GND | 3 | GND | GND |
| 4 / Y | 4 | WS2812_DATA_5V | WS2812_DATA_5V |
| 5 / VCC | 5 | 5V_SYS | 5V_SYS |

The pin/net chain is electrically correct; the pad **locations relative to
the physical package** are not.  The generator comment and released evidence
mis-transcribed the **DRL0005A** pattern (0.67 x 0.30, 0.50 pitch, 1.48 span)
as though it were DBV0005A, then used coordinates which are the 90-degree
rotation of the required DBV pattern.  The prior PASS checked self-consistency
(generator/PCB/Gerber/parity) and package-name/body claims, rather than
normalising TI's drawing orientation and comparing every pad centre.  This is
a `REAL MISMATCH`, not a library representation difference.

### CONTEXT PROVENANCE CONFLICT — corrected 2026-09-15

This report's initial numerical draft incorrectly treated TI's `(2.60)` board
layout annotation as an outer-copper span and consequently used X=+/-0.750
mm. Primary image
`hardware/evidence/u3-full-physical-audit-2026-09-15/primary/ti-dbv-board-layout-p24.png`
shows the arrows terminate at pad centrelines; the correct separation is 2.60
mm and the corrected local X coordinates are +/-1.300 mm. The table above is
the corrected primary-evidence result. This correction strengthens, and does
not alter, the U3 `REAL MISMATCH` / FAIL classification.

## All populated MPNs

`Board geometry` gives pad count; local pad geometry; centre pitch/row pitch;
and `N` means pin numbering and schematic-to-PCB net parity were machine
checked.  `G` means the same pads/nets were found in the release Gerber X2
data.  Per-reference nets are in the following table.

| MPN; refs | official primary drawing/data source | board geometry (mm) | status |
|---|---|---|---|
| TI TPS62133RGT; U1 | TI data sheet, RGT0016C example board layout, 16 x 0.60x0.24, 0.50 pitch, 1.68x1.68 EP; https://www.ti.com/lit/ds/symlink/tps62133.pdf | 16 peripheral pads exactly 0.60x0.24 / 0.24x0.60 at 0.50; EP 1.68x1.68, paste 1.55x1.55; N,G | **PASS** |
| Diodes DMP3130LQ-7; Q1 | Diodes DS38728 suggested pad layout; retained primary PDF `q1-production-error-2026-09-11/DMP3130LQ-DS38728-official.pdf`; https://www.diodes.com/assets/Datasheets/DMP3130LQ.pdf | 3 pads 0.80x0.90; centres (-0.95,+1), (+0.95,+1), (0,-1); N,G | **PASS** |
| TI SN74AHCT1G125DBVR; U3 | TI SCLS378P, DBV0005A `4214839/K` | 5 pads 0.60x1.10 in the wrong rotated arrangement; N,G | **FAIL** |
| Murata GRM188R71C104KA01D; C2,C6,C7,C8 | Murata exact-MPN data sheet/package section must be captured from Murata. Project says “project IPC nominal”, not manufacturer land pattern. | 2 pads 0.95x1.00, 1.45 pitch; N,G | **UNVERIFIED** |
| Murata GRM1885C1H332JA01D; C4 | same condition | 2 pads 0.95x1.00, 1.45 pitch; N,G | **UNVERIFIED** |
| Murata GRM188R61A106MAAL; C5 | same condition | 2 pads 0.95x1.00, 1.45 pitch; N,G | **UNVERIFIED** |
| Murata GRM21BR61E106KA73; C1,C9,C10 | Murata exact-MPN data sheet/package section must be captured from Murata. | 2 pads 1.15x1.40, 2.00 pitch; N,G | **UNVERIFIED** |
| Murata GRM21BR61A226ME44; C3 | same condition | 2 pads 1.15x1.40, 2.00 pitch; N,G | **UNVERIFIED** |
| Yageo RC0603FR-0710KL; R3 | Yageo RC_L exact-MPN package data not retained; project pattern is IPC nominal. | 2 pads 0.95x1.00, 1.45 pitch; N,G | **UNVERIFIED** |
| Yageo RC0603FR-073K3L; R4 | same condition | 2 pads 0.95x1.00, 1.45 pitch; N,G | **UNVERIFIED** |
| approved generic 0603 resistors; R1,R2,R8,R9 | no exact MPN by procurement policy | 2 pads 0.95x1.00, 1.45 pitch; N,G | **UNVERIFIED** |
| Coilcraft XFL4020-222MEB; L1 | source must be re-obtained from Coilcraft; prior source URL is stale and no retained primary drawing is available. | 2 pads 0.98x3.40, 3.35 pitch; N,G | **UNVERIFIED** |
| Littelfuse SMBJ10CA; D3 | Littelfuse SMBJ data provides DO-214AA envelope; project explicitly calls 2.50x2.30 lands IPC nominal. | 2 pads 2.50x2.30, 4.30 pitch; N,G | **UNVERIFIED** |
| Littelfuse 1812L200/16; F1 | Littelfuse series data; project explicitly says no release-specific manufacturer PCB land pattern. | 2 pads 1.125x3.40, 4.275 pitch; N,G | **UNVERIFIED** |
| TI TLV1117LV33DCYR; U4 | TI TLV1117LV data sheet / DCY SOT-223 drawing; https://www.ti.com/lit/ds/symlink/tlv1117lv.pdf. No numerical comparison to TI land pattern retained. | pads 1/2/3 2.00x1.50 at (-3.15,-2.30), (-3.15,0), (-3.15,+2.30), plus pad-2 tab 2.00x3.80 at (+3.15,0); N,G | **UNVERIFIED** |
| Samtec SSW-115-02-G-S; J1,J2 | Samtec SSW drawing must be retained for an exact tail/land comparison. | 15 PTH, 1.04 drill, 1.70 copper, 2.54 pitch; N,G | **UNVERIFIED** |
| Samtec SSW-107-02-G-S; J3 | Samtec SSW drawing must be retained. Note active footprint is project-local `E220_T22D_Socket_400_900`, not a generic SSW-107 module. | 7 PTH, 1.04 drill, 1.70 copper, 2.54 pitch; N,G | **UNVERIFIED** |
| Samtec SSW-104-02-G-S; J5 | Samtec SSW drawing must be retained. | 4 PTH, 1.04 drill, 1.70 copper, 2.54 pitch; N,G | **UNVERIFIED** |
| Samtec TSW-102-07-G-S; JP1 | Samtec TSW drawing must be retained. Board uses KiCad library override (native DRC warning). | 2 PTH, 1.00 drill, 1.70 copper, 2.54 pitch; N,G | **UNVERIFIED** |
| JST B2B-XH-A; J4,J8 | JST eXH product drawing must be retained for full land comparison. | 2 PTH, 1.00 drill, 1.70x2.00 copper, 2.50 pitch; N,G | **UNVERIFIED** |

## Physical pad → net inventory

All entries below are `physical pad number -> schematic net`, and are exact
also in PCB pads (parity PASS).  Passive polarity/side is not a functional
pin claim; pins are listed to make the physical attachment auditable.

| refs | pad → net |
|---|---|
| C1 | 1 BUCK_IN; 2 GND |
| C2 | 1 BUCK_IN; 2 GND |
| C3 | 1 5V_SYS; 2 GND |
| C4 | 1 SS_TR; 2 GND |
| C5,C6,C7 | 1 5V_SYS; 2 GND |
| C8 | 1 BAT_SENSE; 2 GND |
| C9 | 1 5V_SYS; 2 GND |
| C10 | 1 AUX_3V3; 2 GND |
| D3 | 1 BAT_FUSED; 2 GND |
| F1 | 1 BAT_PLUS; 2 BAT_FUSED |
| L1 | 1 BUCK_SW; 2 5V_SYS |
| Q1 | 1 Q1_GATE; 2 BUCK_IN; 3 BAT_SW |
| R1 | 1 Q1_GATE; 2 GND |
| R2 | 1 BUCK_IN; 2 Q1_GATE |
| R3 | 1 BUCK_IN; 2 BAT_SENSE |
| R4 | 1 BAT_SENSE; 2 GND |
| R8,R9 | 1 E220_M0/E220_M1 respectively; 2 GND |
| U1 | 1–3 BUCK_SW; 5,6,8,15,16,EP GND; 7,14 5V_SYS; 9 SS_TR; 10–13 BUCK_IN |
| U3 | 1 GND; 2 WS2812_DATA_3V3; 3 GND; 4 WS2812_DATA_5V; 5 5V_SYS |
| U4 | 1 GND; 2/tab AUX_3V3; 3 5V_SYS |
| J1 | 1 DEVKIT_VIN; 2 GND; 3 GPIO13; 5 GPIO14; 6 E220_AUX; 7 E220_M1; 8 E220_M0; 10 BAT_SENSE |
| J2 | 1 DEVKIT_3V3; 2 GND; 5 WS2812_DATA_3V3; 6 E220_TXD; 7 E220_RXD; 9 GPIO18; 10 GPIO19; 11 OLED_SDA; 14 OLED_SCL; 15 GPIO23 |
| J3 | 1 E220_M0; 2 E220_M1; 3 E220_RXD; 4 E220_TXD; 5 E220_AUX; 6 5V_SYS; 7 GND |
| J4 | 1 BAT_PLUS; 2 GND |
| J5 | 1 GND; 2 AUX_3V3; 3 OLED_SCL; 4 OLED_SDA |
| J8 | 1 BAT_FUSED; 2 BAT_SW |
| JP1 | 1 5V_SYS; 2 DEVKIT_VIN |

## Decision

PASS: U1, Q1.  FAIL: U3.  UNVERIFIED: every other populated MPN/group in the
table, including every generic/procurement-flexible resistor.  No MPN is
silently omitted.  `DNP_USER` J6/J9, plated test holes TP1–TP5, R10/R11
`NO_FOOTPRINT_DNP`, H1–H3 `MECHANICAL_NPTH`, modules, and the JP1 shunt are
not factory-installed PCB components and are excluded from this MPN audit.

Consequently the pre-U3 Gerber and any derivative archive are **not safe for
production**.  Before a new production package may be called safe, correct
U3 from DBV0005A and obtain/retain the listed manufacturer drawings, then
perform the same centre/size/number/net/Gerber comparison for every
UNVERIFIED row.
