# Q1 production-error evidence audit

Scope: read-only audit of the controlled Rev.1 sources and the released Rev.1
fabrication package. No design source was modified.

## Superseded Q1 geometry conclusion

This initial audit correctly established the Q1 MPN, SOT23 package, pin map,
and released-Gerber identity, but its first reading of the Diodes `X1` drawing
dimension was wrong: it treated `X1=1.35 mm` as a lower-pad centre coordinate.
The drawing shows it is a centreline-to-outer-land-edge distance. The
independent physical-plan and implementation reviewers resolved this using the
same primary DS38728 drawing: pads 1/2 must be centred at `-0.950/+0.950 mm`
(`1.35 - 0.80/2`), not `-1.350/+1.350 mm`. The controlled board and the new
production package now contain the corrected geometry. The initial Q1 geometry
rows/conclusion below are retained as historical audit evidence only; the
authoritative Q1 conclusion is in
`q1-footprint-correction-implementation-gate-review.md`.

## Q1 — decisive evidence

| Item | Controlled/released implementation | Primary Diodes evidence | Result |
|---|---|---|---|
| MPN/package | `DMP3130LQ-7`; `Diodes_DMP3130LQ-7_SOT23` | DS38728 rev. 1-2, pp. 1 and 5: `DMP3130LQ-7`, case `SOT23` | MATCH |
| Symbol | `Project:DMP3130LQ_7`: 1=`G`, 2=`S`, 3=`D` | DS38728 p. 1 top view: 1=`G`, 2=`S`, 3=`D` | MATCH |
| nets | schematic/PCB: 1=`Q1_GATE`, 2=`BUCK_IN`, 3=`BAT_SW` | physical pin functions above | MATCH |
| copper | pads 1/2/3 at (-1.35,+1.00)/(+1.35,+1.00)/(0,-1.00) mm; each 0.80 x 0.90 mm | DS38728 p. 5 suggested SOT23 layout: X=0.80, Y=0.90, X1=1.35, Y1=2.90 mm | MATCH |
| courtyard | [-2.05,+2.05] x [-2.00,+2.00] mm = 4.10 x 4.00 mm | manufacturer does not prescribe a courtyard | EXPECTED REPRESENTATION DIFFERENCE |
| released Gerber | F.Cu aperture D30=`0.800000 x 0.900000`; Q1 centers (61.65,77.00), (64.35,77.00), (63.00,75.00) mm | same as above | MATCH |

The active PCB SHA-256 is `dd4d77d521adc1fd744d10b6e05f4a27169e30d988f70a3b9e50236608fda0e4`, exactly the source hash in the released Rev.1 manifest. Therefore the existing fabrication package contains the same Q1 land pattern, not an older/smaller variant.

Conclusion: the reported claim that the released Q1 footprint is substantially smaller than the official SOT23 land pattern is not reproducible from the controlled KiCad source or released Gerbers. Replacing this footprint would be an unsupported regression. Obtain from PCBWAVE the inspected board/order identity, component reel label/MPN, high-resolution top/bottom photos with scale, and their measured pad-to-pad/pad dimensions; compare against the coordinates above before any mutation.

## Whole-board package/pin-risk sweep

| References / exact MPN | Package/pin evidence checked | Result |
|---|---|---|
| U1 `TPS62133RGT` | TI datasheet: RGT 16-pin 3x3 VQFN with exposed pad. Board has pads 1..16+EP, project footprint lands 0.60x0.24 and EP 1.68x1.68; schematic/PCB pin numbers agree. | MATCH |
| U3 `SN74AHCT1G125DBVR` | TI: DBV SOT-23-5. Board has pads 1..5, 0.60x1.10 at official DBV row geometry; function map 1=OE, 2=A, 3=GND, 4=Y, 5=VCC agrees. | MATCH |
| U4 `TLV1117LV33DCYR` | TI: DCY SOT-223, 4 leads; 1=GND, 2+tab=OUT, 3=IN. Board uses `SOT-223-3_TabPin2` (pad 2 duplicated for tab) and schematic nets agree. | MATCH |
| D3 `SMBJ10CA` | Local audited footprint: DO-214AA/SMB, pads 1/2. Device is bidirectional; no polarity/pin inversion risk identified. Its 2.50x2.30 land is project IPC nominal, not an available manufacturer drawing in this audit. | INCONCLUSIVE |
| F1 `1812L200/16` | Local footprint 4532/1812, pads 1/2; project IPC nominal land pattern. | INCONCLUSIVE |
| L1 `XFL4020-222MEB` | Local footprint is two pads, 0.98x3.40 on 3.35 centers and explicitly states manufacturer pattern; source URL currently returns HTTP 404, so current primary confirmation was unavailable. | STALE DATA |
| J4,J8 `B2B-XH-A` | Official JST eXH PDF confirms 2.50-mm pitch and nominal 1.0-mm two-circuit drill. Board pads 1/2 use 2.50-mm pitch and 1.00-mm drill. | MATCH |
| J1,J2 `SSW-115-02-G-S`; J3 `SSW-107-02-G-S`; J5 `SSW-104-02-G-S` | Board pads are sequential and 2.54-mm pitch, 1.04-mm drills; local library identifies the Samtec SSW layout. Current primary Samtec drawing was not retrieved in this audit. | INCONCLUSIVE |
| C1/C3/C9/C10 Murata GRM21; C2/C4/C5/C6/C7/C8 Murata GRM188; R3/R4 Yageo RC0603 | Part-number case-family and named footprints agree: GRM21=2012/0805, GRM188/RC0603=1608/0603; two terminal pads only. Current manufacturer drawings were not retrieved. | INCONCLUSIVE |
| R1/R2/R8/R9 | Explicit approved-generic 0603/1608, two-pad footprints. | EXPECTED REPRESENTATION DIFFERENCE |
| JP1 `TSW-102-07-G-S` | Two sequential 2.54-mm PTH pads. Mating shunt is separately supplied/no PCB footprint. | INCONCLUSIVE |
| J6/J9; TP1..TP5; H1..H3; R10/R11; ESP32/E220/OLED | Respectively DNP_USER, plated test holes, MECHANICAL_ONLY, NO_FOOTPRINT, USER_INSTALLED. Excluded from PCBA component-placement MPN risk. | EXPECTED REPRESENTATION DIFFERENCE |

### All PCBA-populated references: MPN → package → footprint → pads

`Confirmed` means the manufacturer PDF was retrieved and the mechanical/pin
claim was compared. `Not verified` means no primary drawing for that exact MPN
was retrieved; it is not evidence of an assembly fault.

| Ref(s) | MPN | datasheet package | actual footprint | physical pad numbering | status |
|---|---|---|---|---|---|
| C1 | GRM21BR61E106KA73 | 2012/0805 family (not verified) | `Murata_GRM21_2012Metric` | 1,2 | Not verified |
| C2,C6,C7 | GRM188R71C104KA01D | 1608/0603 family (not verified) | `Murata_GRM188_1608Metric` | 1,2 | Not verified |
| C3 | GRM21BR61A226ME44 | 2012/0805 family (not verified) | `Murata_GRM21_2012Metric` | 1,2 | Not verified |
| C4 | GRM1885C1H332JA01D | 1608/0603 family (not verified) | `Murata_GRM188_1608Metric` | 1,2 | Not verified |
| C5 | GRM188R61A106MAAL | 1608/0603 family (not verified) | `Murata_GRM188_1608Metric` | 1,2 | Not verified |
| C8 | GRM188R71C104KA01D | 1608/0603 family (not verified) | `Carrier:Murata_GRM188_1608Metric` | 1,2 | Not verified |
| C9,C10 | GRM21BR61E106KA73 | 2012/0805 family (not verified) | `Carrier:Murata_GRM21_2012Metric` | 1,2 | Not verified |
| D3 | SMBJ10CA | DO-214AA / SMB (not verified) | `Littelfuse_SMBJ10CA_DO214AA` | 1,2 | Not verified; bidirectional device |
| F1 | 1812L200/16 | 4532/1812 (not verified) | `Littelfuse_1812L200_16_4532Metric` | 1,2 | Not verified |
| J1,J2 | SSW-115-02-G-S | 1x15, 2.54-mm SSW socket (not verified) | `Samtec_SSW_1x15_P2.54mm_THT` | 1..15 sequential | Not verified |
| J3 | SSW-107-02-G-S | 1x7, 2.54-mm SSW socket (not verified) | `E220_T22D_Socket_400_900` | 1..7 sequential | Not verified; project carrier pattern |
| J4,J8 | B2B-XH-A | XH, 2 circuits, 2.50-mm pitch, 1.0-mm hole | `JST_B2B-XH-A_1x02_P2.50mm_THT` | 1,2 | Confirmed |
| J5 | SSW-104-02-G-S | 1x4, 2.54-mm SSW socket (not verified) | `Samtec_SSW_1x04_P2.54mm_THT` | 1..4 sequential | Not verified |
| JP1 | TSW-102-07-G-S | 1x2, 2.54-mm header (not verified) | `PinHeader_1x02_P2.54mm_Vertical` | 1,2 | Not verified |
| L1 | XFL4020-222MEB | source primary URL is stale (HTTP 404) | `Coilcraft_XFL4020-222MEB` | 1,2 | Suspicious source provenance only; no geometry mismatch established |
| Q1 | DMP3130LQ-7 | SOT23 | `Diodes_DMP3130LQ-7_SOT23` | 1=G, 2=S, 3=D | Confirmed |
| R1 | approved generic 100 kOhm | 1608/0603 specified in metadata | `Resistor_0603_1608Metric` | 1,2 | Confirmed metadata requirement |
| R2 | approved generic 1 MOhm | 1608/0603 specified in metadata | `Resistor_0603_1608Metric` | 1,2 | Confirmed metadata requirement |
| R3 | RC0603FR-0710KL | 1608/0603 family (not verified) | `Carrier:Resistor_0603_1608Metric` | 1,2 | Not verified |
| R4 | RC0603FR-073K3L | 1608/0603 family (not verified) | `Carrier:Resistor_0603_1608Metric` | 1,2 | Not verified |
| R8,R9 | approved generic 10 kOhm | 1608/0603 specified in metadata | `Resistor_0603_1608Metric` | 1,2 | Confirmed metadata requirement |
| U1 | TPS62133RGT | RGT, VQFN-16, 3x3, EP | `TI_TPS62133RGT_RGT0016C` | 1..16, EP | Confirmed |
| U3 | SN74AHCT1G125DBVR | DBV, SOT-23-5 | `TI_SN74AHCT1G125DBVR_SOT23-5` | 1..5 | Confirmed |
| U4 | TLV1117LV33DCYR | DCY, SOT-223, 4 leads | `SOT-223-3_TabPin2` | 1, 2, tab=2, 3 | Confirmed |

Package geometry and schematic electrical correctness are separate tests. The
table audits package/footprint/pad identity. For the three ICs and Q1,
schematic pin number → PCB pad → manufacturer physical pin was also checked;
all are MATCH. For the passive two-terminal items, polarity is either absent
or (D3) explicitly bidirectional. Connector circuit-to-system assignments
remain a schematic/interface review concern, not a package-numbering mismatch
found by this audit.

## Generator provenance hazard

`hardware/generate_stage8_placement.py:255` assigns `Q1.3` to `BAT_FUSED`, while the active schematic, active PCB, generator `generate_esp32_e220.py`, and `docs/agent-context.md` assign it to `BAT_SW`. This is `STALE DATA`; do not regenerate the active board from that script without an electrical-owner correction and gate.

## Sources read

- `hardware/esp32-e220.kicad_sch` (Q1 symbol/instance and nets)
- `hardware/esp32-e220.kicad_sym` (Q1 symbol pin names/numbers)
- `hardware/esp32-e220.kicad_pcb` (embedded Q1 footprint/pads/nets)
- `hardware/esp32-e220.pretty/Diodes_DMP3130LQ-7_SOT23.kicad_mod`
- `hardware/releases/rev1/fabrication/esp32-e220-F_Cu.gtl`, `.../F_Mask.gts`, and release manifest
- Diodes DS38728: `DMP3130LQ-Diodes-DS38728.pdf`, retrieved from `https://www.diodes.com/assets/Datasheets/DMP3130LQ.pdf`
- TI primary PDFs retained here: `tps62133.pdf`, `sn74ahct1g125.pdf`, `tlv1117lv.pdf`; JST primary `eXH.pdf`.
