# 5V_SYS recovered power-budget ledger

Status: `POWER BUDGET PASS`.

This electrical-owner disposition approves the documented simultaneous
**project design allocation**. It is neither a manufacturer-maximum claim for
the unidentified removable DevKit nor a reviewer verdict, prototype result,
or physical-board release. No schematic topology or PCB data was changed.

## Evidence recovery and classifications

The historical allocation is authoritative in `docs/requirements.md:76-87`
at commit `01b53f7`. `docs/component-decisions.md:45` explicitly classifies
the DevKit 500-mA entry as a project allocation, not a maximum of an unknown
clone. The current schematic remains the source of connectivity: U1 creates
`5V_SYS`; U4.3 is on `5V_SYS`; U4.2/tab creates `AUX_3V3`; J5.2, J6.9,
J7.2/J7.12, R10.2, and R11.2 use `AUX_3V3`.

| Classification | Meaning in this decision |
| --- | --- |
| `MANUFACTURER MAXIMUM` | A bound explicitly published by the component or module manufacturer for stated conditions. |
| `PROJECT DESIGN ALLOCATION` | A conservative engineering allocation adopted for this carrier; it is not silently promoted to a manufacturer maximum. |
| `ENGINEERING MARGIN` | Arithmetic reserve applied to the simultaneous project allocation. |
| `PROTOTYPE VALIDATION` | Required test/measurement not proven by the allocation calculation. |

## Exact simultaneous 5V_SYS allocation

| `5V_SYS` load | Current | Classification and source |
| --- | ---: | --- |
| DevKit VIN through JP1/J1.1 | 500.000 mA | `PROJECT DESIGN ALLOCATION`. The actual removable board is not manufacturer-identified; this is expressly not a clone maximum. |
| E220-400T22D or E220-900T22D, 22-dBm emission | 110.000 mA | `MANUFACTURER MAXIMUM` published instantaneous emission current at the manual's stated 5.0-V / 25°C condition. EBYTE *E220-T Series User Manual*, revision 1.6 dated 2026-05-29, p. 6–8; retained `ebyte-e220-source-id4221.bin`, SHA-256 `48a2306808218dc888b1b9a4d002450aac51bc96c6789fb2501a7c315b470a01`. |
| D2 `WS2812B-V5` | 36.600 mA | `PROJECT DESIGN ALLOCATION`, deliberately retained although D2 is `PLACEMENT_CANDIDATE_NOT_RELEASED`; this does not release the footprint. |
| U3 `SN74AHCT1G125DBVR` | 1.510 mA | Conservative static engineering value: TI maximum 10-uA `ICC` plus maximum 1.5-mA `ΔICC` under the stated input condition. It does not bound dynamic or output-load current. TI `SCLS378P`, Rev. P, Table 5-5 / p. 5. https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf |
| U4 / `AUX_3V3` | 300.100 mA | `PROJECT DESIGN ALLOCATION`: 300.000-mA AUX output allocation plus 0.100-mA accounting convention. OLED is 100.000 mA of this total; J6/J7 together are the remaining 200.000 mA, not 200 mA each. |
| **Subtotal** | **948.210 mA** | Simultaneous design-allocation arithmetic. |
| **20% engineering margin** | **189.642 mA** | `ENGINEERING MARGIN`: `948.210 mA × 0.20`. |
| **Total 5V_SYS design allocation** | **1.137852 A** | `948.210 mA + 189.642 mA`. |

There is no OLED double count: the old independent OLED 100-mA allocation is
now wholly inside the 300.000-mA `AUX_3V3` allocation. The `0.100 mA`
addition is not a manufacturer-guaranteed U4 loaded input/ground-current
maximum. TI `TLV1117LV` `SBVS160C`, Rev. C, p. 5 specifies 100 uA maximum
quiescent current at zero load; the value above is solely the approved
project accounting convention. https://www.ti.com/lit/ds/symlink/tlv1117lv.pdf

## Power and battery calculations

Assumption: 85% is the conservative project efficiency assumption used for
this budget calculation, not a measured TPS62133 efficiency at every load,
input voltage, temperature, and operating mode.

| Quantity | Calculation | Result |
| --- | --- | ---: |
| 5-V output power | `5.0 V × 1.137852 A` | `5.689260 W` |
| Battery input power | `5.689260 W / 0.85` | `6.693247 W` |
| Battery current at 6.0 V | `6.693247 W / 6.0 V` | `1.115541 A` |
| Battery current at 7.4 V | `6.693247 W / 7.4 V` | `0.904493 A` |
| Battery current at 8.4 V | `6.693247 W / 8.4 V` | `0.796815 A` |

## Supply, magnetics, and input-path comparisons

| Item | Source-bound value | Calculation and disposition |
| --- | --- | --- |
| U1 TPS62133 | 3.0-A continuous output rating; 3.6-A minimum static current limit at VIN=12 V / TA=25°C | `1.137852 A / 3.0 A = 37.9284%`; continuous-rating headroom = `1.862148 A`. The `3.6 A` condition has `2.462148 A` arithmetic distance, but must never replace the 3.0-A continuous rating or be treated as a 6.0-V guarantee. TI `SLVSAG7F`, Rev. F, Table 7-5 / p. 5. https://www.ti.com/lit/ds/symlink/tps62133.pdf |
| L1 Coilcraft `XFL4020-222MEB` | The `XFL4020-222ME_` data row gives 2.2 uH, maximum DCR 23.50 mOhm, 3.1-A `Isat` at 10% inductance drop, and 6.0-A `Irms` for 20°C rise. | At the DC allocation: `I²R = 1.137852² × 0.02350 = 0.030426 W`; DC-only distance to 3.1 A `Isat` = `1.962148 A`. The peak current including ripple is not calculated here, so this is not saturation proof. Official Coilcraft data: https://www.coilcraft.com/getmedia/50632d43-da1b-4cdb-8ab4-3029cab51df3/xfl4020.pdf |
| F1 Littelfuse `1812L200/16` | `Ihold=2.0 A` at 20°C; temperature-rerated `Ihold=1.29 A` at 85°C. | At worst calculated battery current 1.115541 A (6.0 V), 85°C `Ihold` headroom = `0.174459 A`. This is a steady allocation comparison, not a time-current or startup proof. Littelfuse 1812L, revised 2024-06-10, pp. 2–3. https://www.littelfuse.com/~/media/electronics/datasheets/resettable_ptcs/littelfuse_ptc_1812l_datasheet.pdf.pdf |
| J4 JST `B2B-XH-A` | 3-A AC/DC rating with AWG22 for the XH series. | 1.115541-A worst calculated battery current is below 3 A; the mating housing/contact/wire and temperature remain part of the harness qualification. Official JST XH data: https://www.jst-mfg.com/product/pdf/eng/eXH.pdf |
| Q1 Diodes `DMP3130LQ-7` | At VGS=-4.5 V, steady-state continuous ID is 2.6 A at TA=70°C; RDS(ON) maximum 95 mOhm in the stated test. | The 1.115541-A 6-V battery allocation is below that published current condition. This is not a final temperature proof for the actual copper, ambient, or switch/inrush path. Diodes `DS38728 Rev. 1-2`, p. 2. https://www.diodes.com/_files/datasheets/DMP3130LQ.pdf |
| J8 JST VH `B2PS-VH(LF)(SN)` | 10-A AC/DC rating with AWG16 and standard header. | Difference from 1.115541-A worst calculated battery current = `8.884459 A`; selected VH is adequate for the allocation. The actual mating harness must retain the stated contact and wire conditions. Official JST VH data: https://www.jst-mfg.com/product/pdf/eng/eVH.pdf |

## Required prototype validation

`POWER BUDGET PASS` does not close these physical checks:

* DevKit VIN burst, Wi-Fi/BT/RF, USB-service, and startup current on the
  actually selected board;
* startup inrush and external capacitance/current on J5/J6/J7, including the
  policy-limited AUX population;
* U4 junction temperature and output regulation at 300-mA AUX allocation on
  the actual copper implementation;
* L1 peak current including ripple, actual DCR temperature rise, and
  TPS62133 transient/current-limit behavior;
* F1 time-current response and hot-board derating, Q1 temperature/drop, and
  J4/J8 harness wire/contact heating.

The source/generator and earlier ERC evidence remain unchanged: generated
schematic SHA-256 `554b551f4132bc52f47f3acc4f71228f56661dce084eab12a316e4b949416f53`,
symbol SHA-256 `55893d5ac1c810fc401e2fba930fd367e0642c4888b4d26215c7a48256663e8b`,
and native `0 errors / 0 warnings` in `esp32-e220-post-budget-context-erc.rpt`.
These representation checks do not substitute for the prototype validation
above.
