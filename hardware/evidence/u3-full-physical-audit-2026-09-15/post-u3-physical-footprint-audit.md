# Full physical-footprint audit — post-U3 correction

This is the final disposition for board SHA-256
`ef7cc377eb670115295f39cbd963e8910f2f4047cf5d740728abd09e1e4f25ea` and
release `rev1-q1-u3-footprint-correction-2026-09-15`.  It supersedes only the
U3 `FAIL` row in `full-physical-footprint-audit.md`; all other rows retain the
same primary-evidence status.

## U3 numerical closeout

Primary source: TI `SN74AHCT1G125` SCLS378P Rev. P, DBV0005A
`4214839/K`, 08/2024.  The drawing is retained as
`primary/ti-dbv-board-layout-p24.png` and its 2.60-mm horizontal dimension is
between **pad centrelines**.  The active footprint is the 90-degree drawing
orientation already used on the board.

| Physical pin / function | TI local centre, current orientation mm | final PCB / F.Cu Gerber centre mm | copper/paste | delta |
|---|---:|---:|---:|---:|
| 1 / OE | (-0.950, +1.300) | (88.050, 55.300) | 0.600 x 1.100, R0.05 | 0.000 |
| 2 / A | (0.000, +1.300) | (89.000, 55.300) | 0.600 x 1.100, R0.05 | 0.000 |
| 3 / GND | (+0.950, +1.300) | (89.950, 55.300) | 0.600 x 1.100, R0.05 | 0.000 |
| 4 / Y | (+0.950, -1.300) | (89.950, 52.700) | 0.600 x 1.100, R0.05 | 0.000 |
| 5 / VCC | (-0.950, -1.300) | (88.050, 52.700) | 0.600 x 1.100, R0.05 | 0.000 |

The row-centre separation is 2.600 mm and both 1-to-3 and 5-to-4 spans are
1.900 mm.  F.Cu X2 attributes confirm the five complete net names; IPC-D-356
independently confirms every U3 pad number and `X0236Y0433` (0.60 x 1.10 mm).
The direct Gerber audit is `checksums/package-self-audit.json` in the release.

| physical pin -> pad -> schematic net/function |
|---|
| 1 -> 1 -> GND / OE low |
| 2 -> 2 -> WS2812_DATA_3V3 / A |
| 3 -> 3 -> GND / GND |
| 4 -> 4 -> WS2812_DATA_5V / Y |
| 5 -> 5 -> 5V_SYS / VCC |

**U3: PASS.**  The generator, project library, embedded PCB footprint, F.Cu
Gerber, and IPC-D-356 have the same numerical geometry and numbering.

## Final per-MPN disposition

| MPN / references | final status |
|---|---|
| TPS62133RGT / U1 | PASS |
| DMP3130LQ-7 / Q1 | PASS |
| SN74AHCT1G125DBVR / U3 | PASS |
| GRM188R71C104KA01D / C2,C6,C7,C8 | UNVERIFIED |
| GRM1885C1H332JA01D / C4 | UNVERIFIED |
| GRM188R61A106MAAL / C5 | UNVERIFIED |
| GRM21BR61E106KA73 / C1,C9,C10 | UNVERIFIED |
| GRM21BR61A226ME44 / C3 | UNVERIFIED |
| RC0603FR-0710KL / R3 | UNVERIFIED |
| RC0603FR-073K3L / R4 | UNVERIFIED |
| generic 0603 resistors / R1,R2,R8,R9 | UNVERIFIED |
| XFL4020-222MEB / L1 | UNVERIFIED |
| SMBJ10CA / D3 | UNVERIFIED |
| 1812L200/16 / F1 | UNVERIFIED |
| TLV1117LV33DCYR / U4 | UNVERIFIED |
| SSW-115-02-G-S / J1,J2 | UNVERIFIED |
| SSW-107-02-G-S / J3 | UNVERIFIED |
| SSW-104-02-G-S / J5 | UNVERIFIED |
| TSW-102-07-G-S / JP1 | UNVERIFIED |
| B2B-XH-A / J4,J8 | UNVERIFIED |

No other footprint was changed in this correction.  The audit disposition is
**HOLD — NOT SAFE FOR PRODUCTION** until each UNVERIFIED row has a retained
primary manufacturer numerical land-pattern comparison.
