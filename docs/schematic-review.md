# Stage 5 modular-carrier schematic review

Status: corrected after gate review; PCB has not been created.

## Scope and validation boundary

`hardware/esp32-e220.kicad_sch` is the Stage 5 carrier schematic.  It has a
removable two-header DevKit interface; it does not contain a bare ESP32,
main-board 3.3-V buck, EN/BOOT circuit or programming header.

The reproducible source is `hardware/generate_esp32_e220.py`.  The generator
now derives each label position from the same pin-row formula as its embedded
KiCad symbol: local Y is positive upward and sheet Y is `origin - local_y`.
This correction is material: the earlier inverse coordinate mapping could make
a label land on the mirror-image pin row despite a syntactically valid file.

The project-local `PWR_FLAG` instances are ERC source-boundary markers only:
`VBUS_PRE` is supplied by the attached Type-C source, `TUSB_VDD` is supplied
through D1, and GND is the common external return.  They are not BOM parts and
do not alter the physical circuit.

## Pin-by-pin electrical audit

All following assignments were checked from the generated pin endpoints, then
visually against the KiCad PDF export.

| Block | Verified pin/net assignment |
| --- | --- |
| J1 DevKit left | 1/VIN=`5V_SYS`; 2=GND; 6/GPIO27=`E220_AUX`; 7/GPIO26=`E220_M1`; 8/GPIO25=`E220_M0`. All other header pins explicitly NC. |
| J2 DevKit right | 2=GND; 5/GPIO4=`WS2812_DATA_3V3`; 6/GPIO16/RX2=`E220_TXD`; 7/GPIO17/TX2=`E220_RXD`; 11/GPIO21=`OLED_SDA`; 14/GPIO22=`OLED_SCL`. All other header pins explicitly NC. |
| J3 EBYTE universal socket | 1/M0=`E220_M0`; 2/M1=`E220_M1`; 3/RXD=`E220_RXD`; 4/TXD=`E220_TXD`; 5/AUX=`E220_AUX`; 6/VCC=`5V_SYS`; 7=GND. Thus GPIO17 drives E220 RXD and GPIO16 receives E220 TXD; GPIO15 is not used. |
| E220 support | R8 pin 1=`E220_M0`, pin 2=GND; R9 pin 1=`E220_M1`, pin 2=GND (both 10 kOhm project-choice pull-downs). C5/C6 each connect `5V_SYS` to GND and are respectively `GRM188R61A106MAAL` 10 uF/10 V/X5R and `GRM188R71C104KA01D` 100 nF/16 V/X7R. |
| J4 GCT USB4105-GF-A | A4/A9/B4/B9=`VBUS_PRE`; A1/A12/B1/B12 and shells SH1/SH2=GND; A5=CC1; B5=CC2. A6/B6 are only `USB_DP_NC`; A7/B7 are only `USB_DM_NC`; A8/B8 SBU are explicitly NC. There is no USB data connection to the DevKit/ESP. |
| U1 TI TUSB320LAIRWBR | 1=CC1; 2=CC2; 3/PORT=GND; 4=`VBUS_DET`; 5/ADDR=NC (GPIO mode); 6/INT_N/OUT3=NC; 7/SDA/OUT1=`OUT1`; 8/SCL/OUT2=NC; 9/ID=NC; 10=GND; 11/EN_N=GND; 12/VDD=`TUSB_VDD`. |
| U2 TI TPS259630DDAR | 1=GND; 2=`DVDT`; 3/EN/UVLO=`EFUSE_EN`; 4/IN=`VBUS_PRE`; 5/OUT=`5V_SYS`; 6/FLT=NC; 7=`ILM`; 8=`OVLO`; exposed thermal pad=`EP`=GND. `EP` is deliberately named rather than falsely numbered as lead 9, so a future footprint must map the physical exposed pad to the `EP` pad and GND. |
| D3 TI TPD1E10B06DPYR | 1/I/O=`VBUS_PRE`; 2=GND. This is the selected VBUS ESD diode at the raw Type-C VBUS node, before the eFuse. |
| Gate support | D1 `MMSD4148T1G`: 2/A=`VBUS_PRE`, 1/K=`TUSB_VDD`; R1=`VBUS_PRE`/`VBUS_DET`; R2=`TUSB_VDD`/`OUT1`; R3=`OUT1`/`QBASE`; R4=`TUSB_VDD`/`EFUSE_EN`; R5=`ILM`/GND; R6=`VBUS_PRE`/`OVLO`; R7=`OVLO`/GND; C1=`VBUS_PRE`/GND; C2=`TUSB_VDD`/GND; C3=`5V_SYS`/GND; C4=`DVDT`/GND. Q1 `MMBT3904LT1G` has 1/B=`QBASE`, 2/E=GND, 3/C=`EFUSE_EN`. These D1/Q1 physical pin assignments were rechecked against the official onsemi datasheets. |
| U3 TI SN74AHCT1G125DBVR | 1/OE=GND; 2/A=`WS2812_DATA_3V3`; 3=GND; 4/Y=`WS2812_DIN`; 5/VCC=`5V_SYS`. C7 is `GRM188R71C104KA01D` from `5V_SYS` to GND. |
| D2 WorldSemi WS2812B-V5 | 1/VDD=`5V_SYS`; 2/DOUT=NC; 3/VSS=GND; 4/DIN=`WS2812_DIN`. Footprint remains deliberately unassigned. |
| Test points | TP1=`5V_SYS`; TP2=`E220_VCC` measurement point on the same `5V_SYS` net; TP3=`E220_M0`; TP4=`E220_M1`; TP5=`E220_AUX`; TP6=`E220_RXD`; TP7=`E220_TXD`. The active test-point plan is therefore electrically present; exact test-point MPN, footprint and location remain PCB-stage work. |

The Type-C gate remains fail-safe by the documented architecture: at detach,
reset, VDD absence or Default-current advertisement, released OUT1 drives Q1
on and holds TPS259630 EN low.  OUT1 low only at Medium/High turns Q1 off and
allows the 330-kOhm `TUSB_VDD` pull-up to enable the eFuse.

OLED is intentionally only a future I2C signal reservation.  Its VCC and
pull-ups are not present or powered in Rev A; a precise module/connector is
still required before physical implementation.

## CC ESD / short-to-VBUS review blocker

The active documents previously selected `TPD4S311DRYR` for CC protection, but
that device is **not** in this schematic because no electrically valid rail is
available in the approved pre-gate architecture.  TI requires its `VPWR` to be
2.7…4.5 V, plus 0.3…1 uF at VPWR and a 0.1-uF VBIAS capacitor rated at least
35 V.  `5V_SYS` and DevKit 3V3 are deliberately absent at Default current;
using raw 5-V VBUS violates the 4.5-V recommended maximum, and using the
diode-fed `TUSB_VDD` has no documented ≤4.5-V maximum over VBUS/diode
tolerance.  It must therefore not be tied to either rail.

Official TI alternatives checked in this review do not remove that constraint:
`TPD2S300` also requires `VPWR=2.7…4.5 V` (and VM in the CC operating range),
while passive `TPD4E05U06` is an ESD diode array rather than a verified
24-V short-to-VBUS isolation solution.  No replacement is selected.  A future
approved decision must select a pre-gate auxiliary 2.7…4.5-V rail with
back-power analysis, or change the CC protection requirement/part and verify
the new device's short-to-VBUS behaviour.  Until then, CC protection is a real
schematic blocker; the VBUS diode D3 does not protect CC.

## KiCad validation

The regenerated file was read by KiCad 10.0.5 and exported successfully:

```text
XDG_CONFIG_HOME=/tmp/kicad-gate-config XDG_CACHE_HOME=/tmp/kicad-gate-cache \
XDG_DATA_HOME=/tmp/kicad-gate-data kicad-cli sch export pdf \
  hardware/esp32-e220.kicad_sch -o /tmp/esp32-e220-gate.pdf
# exit 0

XDG_CONFIG_HOME=/tmp/kicad-gate-config XDG_CACHE_HOME=/tmp/kicad-gate-cache \
XDG_DATA_HOME=/tmp/kicad-gate-data kicad-cli sch erc \
  hardware/esp32-e220.kicad_sch --exit-code-violations
# exit 5: 0 errors, 2 warnings
```

Both warnings are `isolated_pin_label` for `OLED_SDA` and `OLED_SCL`.  They
are visible, not excluded or suppressed, and follow directly from keeping a
signal-only reservation without inventing an OLED connector.  `--exit-code-
violations` treats warnings as violations, hence exit code 5 although ERC has
**zero errors**.  All prior power-input ERC errors were resolved with explicit
source-boundary PWR_FLAG markers rather than by changing verified electrical
pin types.

This is file-format and ERC validation plus a pin-level electrical audit.  The
CC-protection rail issue above prevents schematic release; it must be resolved
before any footprint/mechanics or PCB work.  Existing later-stage items remain:
final E220 socket/footprint, USB and WS2812 land patterns, antenna/band/
regulatory choice, DevKit mechanics, and prototype power/RF/transient tests.

## Stage 5 third-gate re-review — pre-gate protection correction

The preceding CC blocker is historical and **resolved in the regenerated
schematic**. The active pin-level audit additions are:

| Block | Verified pin/net assignment |
| --- | --- |
| U4 TLV70433DBVR | 1/GND=GND; 2/IN=`VBUS_PRE`; 3/OUT=`PRE_GATE_3V3`; 4/5=NC. U4 is a fixed-output LDO and has no enable pin. |
| U4 local bypass | C8=`VBUS_PRE`/GND and C9=`PRE_GATE_3V3`/GND, both `GRM188R71A105KA61D` 1-uF/10-V/X7R. C2 remains `PRE_GATE_3V3`/GND 0.1-uF TUSB VDD bypass. |
| U5 TPD4S311YBFR | A2/C_CC1=`C_CC1`, A3/C_CC2=`C_CC2`, B2/RPD_G1=`C_CC1`, B3/RPD_G2=`C_CC2`, D3/CC1=`TUSB_CC1`, D4/CC2=`TUSB_CC2`; C1/C2/C3=GND; C4/VPWR=`PRE_GATE_3V3`; A4/VBIAS=`TPD4_VBIAS`; A1/B1/D1/D2 SBU and B4/FLT=NC. |
| U5 required capacitors | C10 `GRM188R71A105KA61D`=`PRE_GATE_3V3`/GND (1-uF VPWR bypass); C11 `GRM188R71H104KA93D`=`TPD4_VBIAS`/GND (0.1-uF, 50-V X7R). |
| J4 / U1 CC boundary | J4 A5 -> `C_CC1`; J4 B5 -> `C_CC2`. U5 protected sides route only to U1 1/CC1=`TUSB_CC1` and 2/CC2=`TUSB_CC2`; no CC connects to ESP. U1 12/VDD=`PRE_GATE_3V3`, 4/VBUS_DET=`VBUS_DET` through R1=900 kOhm from VBUS_PRE. |
| Gate | R2=47 kOhm `PRE_GATE_3V3`->OUT1; R3=47 kOhm OUT1->Q1 base; R4=330 kOhm `PRE_GATE_3V3`->TPS EN. Thus OUT1 released -> Q1 on -> eFuse disabled; OUT1 low -> Q1 off -> eFuse enabled. The former D1/MMSD4148 TUSB_VDD path is absent. |

TI requires the TPD4 RPD pins to be tied to their connector-side CC nodes for
dead-battery resistors. That is what the U5 wiring implements; no external
permanent 5.1-kOhm Rd is added. PRE_GATE_3V3 is available before `5V_SYS`, so
this does not reintroduce a circular Default-current boot dependency. At 3.3 V
OUT1 low sinks 70.2 uA through R2; released OUT1 supplies about 27.7 uA into
the Q1 base through R2+R3, while R4's enabled-state leakage load is bounded by
the TPS2596 ±0.1-uA EN specification. This is a valid fail-safe hardware
interlock, not firmware gating.

Validation after regeneration:

```text
kicad-cli sch export pdf hardware/esp32-e220.kicad_sch \
  -o /tmp/esp32-e220-pregate.pdf
# exit 0

kicad-cli sch erc hardware/esp32-e220.kicad_sch --exit-code-violations \
  -o esp32-e220-erc.rpt
# exit 5: 0 errors, 2 warnings
```

The only warnings are the intentionally visible `isolated_pin_label` warnings
on `OLED_SDA` and `OLED_SCL`; they are not suppressed. The CC protection
topology is no longer a schematic blocker. No footprint, placement, routing or
PCB artifact was created; U5 DSBGA footprint/assembly verification remains a
PCB-stage blocker.

Sources: [TLV704, TI](https://www.ti.com/lit/ds/symlink/tlv704.pdf),
[TPD4S311, TI](https://www.ti.com/lit/ds/symlink/tpd4s311.pdf),
[TUSB320LAI, TI](https://www.ti.com/lit/ds/symlink/tusb320lai.pdf), and
[TPS2596, TI](https://www.ti.com/lit/ds/symlink/tps2596.pdf).

## Rev.1 schematic re-review — protected 2S battery carrier

The preceding USB-C/CC/pre-gate review is retained only as history. The active
generated schematic has no USB4105, TUSB320, TPD4S311, TPD1E10B06, TLV704,
TPS259630, CC net, `VBUS_PRE`, `PRE_GATE_3V3` or OUT1 gate.

| Block | Pin/net audit |
| --- | --- |
| J4 | 1/BAT+=`BAT_PLUS`; 2/BAT-=GND. Value is “PROTECTED 2S LI-ION INPUT ONLY 6...8.4V”. |
| Input protection | F1 1=`BAT_PLUS`, 2=`BAT_FUSED`; D3 `SMBJ10CA`=`BAT_FUSED`/GND; Q1 `DMP3130LQ-7` **1/G=`Q1_GATE`, 2/S=`BUCK_IN`, 3/D=`BAT_FUSED`**. R1=`Q1_GATE`/GND=100 kOhm and R2=`BUCK_IN`/`Q1_GATE`=1 Mohm. This orientation is the reviewed P-MOS RPP topology: intrinsic diode BAT_FUSED -> BUCK_IN under correct polarity, reverse-biased for reverse battery. |
| U1 TPS62133RGT | 1/2/3 SW=`BUCK_SW`; 4/PG=NC; 5/FB=GND; 6/AGND=GND; 7/FSW=`5V_SYS`; 8/DEF=GND; 9/SS/TR=`SS_TR`; 10/AVIN, 11/12 PVIN, 13/EN=`BUCK_IN`; 14/VOS=`5V_SYS`; 15/16 PGND and EP=GND. L1 joins `BUCK_SW` to `5V_SYS`. |
| U1 support | C1=`BUCK_IN`/GND 10 uF/25 V; C2=`BUCK_IN`/GND 0.1 uF/16 V; C3=`5V_SYS`/GND 22 uF/10 V; C4=`SS_TR`/GND 3.3 nF/50 V. |
| Existing blocks | DevKit VIN remains `5V_SYS`; E220 6/VCC=`5V_SYS`, M0/M1 pulldowns and UART/control mapping are unchanged; WS2812/AHCT block is unchanged. |
| Test points | TP1=`BAT_PLUS`; TP2=GND; TP3=`BUCK_IN`; TP4=`5V_SYS`; TP5 is named E220_VCC measurement point on `5V_SYS`; TP6/7/8/9/10=`E220_M0/M1/AUX/RXD/TXD`. |

The reviewed electrical policy is no on-board charger/BMS and no main switch;
the battery is disconnected or external BMS output off before DevKit USB-C
programming. This policy is explicit in the schematic notes and requirements.

KiCad 10.0.5 validation after regeneration:

```text
kicad-cli sch export pdf hardware/esp32-e220.kicad_sch \
  -o /tmp/esp32-e220-rev1.pdf
# exit 0

kicad-cli sch erc hardware/esp32-e220.kicad_sch --exit-code-violations \
  -o esp32-e220-erc.rpt
# exit 5: 0 errors, 2 warnings
```

The two warnings are the existing visible `isolated_pin_label` warnings for
the intentionally signal-only OLED SDA/SCL reservations; no warning is hidden.
No PCB, footprint assignment, placement or routing was performed. Remaining
layout-release blockers are the exact battery connector/land patterns, buck
thermal/EMI layout, input-transient test and mechanical strain relief.

Sources: [TPS62133, TI](https://www.ti.com/lit/ds/symlink/tps62133.pdf),
[DMP3130LQ, Diodes Inc.](https://www.diodes.com/_files/datasheets/DMP3130LQ.pdf),
and [1812L PPTC, Littelfuse](https://www.littelfuse.com/~/media/electronics/datasheets/resettable_ptcs/littelfuse_ptc_1812l_datasheet.pdf.pdf).

## Rev.1 OLED update — reviewed

The preceding isolated OLED-reservation warnings are superseded. The active
schematic now has J5 with 1=GND, 2=`DEVKIT_3V3`, 3=`OLED_SCL` (GPIO22), and
4=`OLED_SDA` (GPIO21). R10 SDA and R11 SCL are each `DNP=YES`, 4.7-kOhm 1-%
sites from the respective bus to `DEVKIT_3V3`; no 5-V OLED VCC or pull-up
exists. J5 is labelled as a removable female 1x4 socket; no footprint is
assigned.

Manual net audit verified J2 right header pin 1=`DEVKIT_3V3`, pin 11/GPIO21
to `OLED_SDA`, pin 14/GPIO22 to `OLED_SCL`; J5 mapping is exactly
1/GND, 2/3V3, 3/SCL, 4/SDA. The frozen Rev.1 battery input, Q1 RPP orientation,
TPS62133 network, E220 socket and WS/AHCT paths are unchanged.

KiCad 10.0.5 validation after reproducible generator regeneration:

```text
kicad-cli sch export pdf hardware/esp32-e220.kicad_sch \
  -o /tmp/esp32-e220-oled.pdf
# exit 0

kicad-cli sch erc hardware/esp32-e220.kicad_sch --exit-code-violations \
  -o esp32-e220-erc.rpt
# exit 0: Found 0 violations
```

Thus ERC has 0 errors and 0 warnings; no warning was suppressed or excluded.
No PCB, footprint assignment, placement or routing was performed. Remaining
OLED work is prototype validation of the actual module/regulator and the
PCB-stage user measurement of `OLED_MOUNT_Y`.
