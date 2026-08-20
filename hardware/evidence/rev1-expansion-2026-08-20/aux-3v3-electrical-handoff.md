# AUX_3V3 electrical handoff

Status: `SCHEMATIC CHANGE REQUIRED` was authorized and implemented. This
electrical-owner evidence supersedes the external-3V3 mapping in
`electrical-handoff.md`; it is not a reviewer verdict, PCB release, or
authorization to synchronize the active board.

## Changed source and exact connectivity

| Path | Change |
| --- | --- |
| `hardware/generate_esp32_e220.py` | Added the reproducible U4 AUX_3V3 LDO cell, C9/C10, exact U4 package mapping, changed external 3V3 endpoints, and operational/thermal constraints. |
| `hardware/esp32-e220.kicad_sch` | Generated native schematic. |
| `hardware/esp32-e220.kicad_sym` | Generated `Project:TLV1117LV33DCY` symbol. |

The native netlist `esp32-e220-aux-3v3.net` proves:

| Net | Exact relevant nodes |
| --- | --- |
| `5V_SYS` | U4.3/IN, C9.1/CIN, existing 5-V loads and JP1.1. |
| `AUX_3V3` | U4.2/OUT+TAB, C10.1/COUT, J5.2, J6.9, J7.2, J7.12. R10.2 and R11.2 are also labelled `AUX_3V3` in the generated schematic; these DNP/non-PCB options are intentionally omitted from the KiCad exported netlist. |
| `DEVKIT_3V3` | J2.1 only. No accessory, OLED, pull-up, J6, or J7 supply pin remains on this net. |
| `GND` | U4.1, C9.2, C10.2. |

U4 source/package map is fixed as `TLV1117LV33DCYR`: symbol pin 1=GND,
pin 2=`AUX_3V3`, pin 3=`5V_SYS`; the package reference is KiCad's
`Package_TO_SOT_SMD:SOT-223-3_TabPin2`, whose two physical pad-2 shapes
represent the lead and tab. TI identifies DCY pin 2 and the tab as OUT.

## Component and capacitor verification

| Ref | Exact MPN | Footprint reference | Function |
| --- | --- | --- | --- |
| U4 | TI `TLV1117LV33DCYR` | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` | Fixed 3.3-V LDO, DCY/SOT-223. |
| C9 | Murata `GRM21BR61E106KA73` | `Carrier:Murata_GRM21_2012Metric` | 10-uF, 25-V, X5R CIN. |
| C10 | Murata `GRM21BR61E106KA73` | `Carrier:Murata_GRM21_2012Metric` | 10-uF, 25-V, X5R COUT. |

Primary sources and applicable revision/page evidence:

* TI, *TLV1117LV 1-A Positive Fixed-Voltage LDO*, `SBVS160C`, Rev. C,
  revised January 2023: Table 5-1 / p. 3 gives DCY 1=GND, 2+tab=OUT,
  3=IN; recommended VIN is 2.0 to 5.5 V on p. 5; p. 13 requires a 1-uF
  ceramic COUT and effective COUT above 0.5 uF, recommends 0.1 to 1.0 uF
  low-ESR CIN, and specifies X5R/X7R ceramic use. The same page requires
  capacitors close to the device. https://www.ti.com/lit/ds/symlink/tlv1117lv.pdf
* Murata, `GRM21BR61E106KA73-01A`, product reference sheet, 9 January 2025:
  10 uF, 25 VDC, X5R, 0805, ±10%.
  https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM21BR61E106KA73-01A.pdf

C9/C10 are deliberately 10x the nominal TI 1-uF recommendation and have a
25-V rating at 5.0-V and 3.3-V service, respectively. Even before voltage
bias allowance, worst nominal tolerance and X5R temperature change leave
`10 uF × 0.90 × 0.85 = 7.65 uF`; this is far above the 0.5-uF effective-COUT
stability floor. `pcb_layout_dfm` must nevertheless retain the exact MPN or
verify an approved Murata DC-bias/temperature curve before substitution.

## Allocation, operating policy, and limitations

`AUX_3V3` has a hard 300-mA total allocation:

| Consumer class | Allocation |
| --- | ---: |
| OLED through J5 | 100 mA |
| J6 and J7 combined | 200 mA total, not 200 mA per connector |
| AUX_3V3 total | 300 mA |

`DEVKIT_3V3` is not an external-accessory rail; J2.1 alone remains on it.

Normal operation is `POWER_SW ON` and `JP1 closed`. USB service is
`POWER_SW OFF` and `JP1 open` when isolation is desired. This architecture
does **not** claim automatic or complete GPIO isolation. With carrier power
on, JP1 open, and the DevKit unpowered, any powered peripheral connected to
J5/J6/J7 must not actively drive a GPIO. This is an operating policy
limitation; no extra isolation hardware is authorized in this revision.

## Thermal and 5V_SYS accounting

At the allocated maximum, U4 dissipation is:

`P_D = (5.0 V - 3.3 V) × 0.300 A = 0.510 W`.

TI's Rev. C p. 14 gives this power equation and states that copper area,
heavier copper, and plated through-holes improve heat removal; it requires
reliable operation below 125°C junction temperature and explicitly says
thermal shutdown is not a substitute for proper heatsinking. The data-sheet
DCY `RthetaJA=62.9 °C/W` characterization value is **not** final-board
evidence and is not used as a release calculation.

Required physical implementation constraint for `pcb_layout_dfm`:

* connect U4 pad 2/tab directly, without thermal spokes, to at least a
  20 mm × 20 mm continuous F.Cu `AUX_3V3` copper area and an at least
  20 mm × 20 mm B.Cu `AUX_3V3` copper area;
* use at least four 0.60/0.30-mm `AUX_3V3` thermal vias within 3 mm of the
  tab; keep C9/C10 immediately adjacent with direct ground returns;
* verify actual-board thermal performance at 0.510 W and the product's
  declared worst ambient, preserving `TJ < 125°C` without thermal cycling.

This handoff originally recorded a lack of traceable aggregate `5V_SYS`
allocation. That statement is superseded by the recovered historical project
design allocation and the current calculation in
`5v-sys-budget-ledger.md`: total `5V_SYS` allocation `1.137852 A`, including
the 300.100-mA U4/AUX accounting convention and 20% engineering margin.
`POWER BUDGET PASS` applies to that design allocation, not to an unidentified
DevKit manufacturer maximum. TI's 100-uA maximum U4 quiescent-current figure
remains a no-load specification and is not claimed as a loaded-ground-current
maximum. The ledger retains the required prototype validation for DevKit
bursts/startup, external inrush, U4 thermal operation, and converter/magnetics
transients.

## Validation and layout implications

| Check | Result | Artifact |
| --- | --- | --- |
| Native KiCad ERC | `0 errors / 0 warnings` | `esp32-e220-aux-3v3-erc.rpt` |
| Native netlist | PASS; direct ref/pin/net evidence above | `esp32-e220-aux-3v3.net` |
| Generator reproducibility | PASS. Two consecutive generations: schematic SHA-256 `554b551f4132bc52f47f3acc4f71228f56661dce084eab12a316e4b949416f53`; symbols SHA-256 `55893d5ac1c810fc401e2fba930fd367e0642c4888b4d26215c7a48256663e8b`. | generator and generated files |
| Active PCB sync | Expected pre-layout `FAIL`: changed existing J5.2 `/DEVKIT_3V3 -> /AUX_3V3` in addition to earlier authorized J1.1 and Q1.3 changes; missing PCB refs C8/C9/C10/J6/J7/J8/JP1/R3/R4/U4. | `active-pcb-sync-aux-3v3.json` |

No active PCB, routing, placement, zone, or physical footprint source was
edited. The layout owner must verify the standard DCY footprint against the
TI package drawing, implement the required thermal geometry without violating
antenna/RF/mechanical constraints, and rerun board parity/DRC.
