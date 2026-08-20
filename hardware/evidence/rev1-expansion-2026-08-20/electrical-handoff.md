# Rev.1 expansion electrical handoff

Status: `SCHEMATIC CHANGE REQUIRED` was authorized and implemented. This is an
electrical-owner handoff, not a reviewer verdict or a PCB release. The
external-3V3 portions of this earlier handoff are superseded by
`aux-3v3-electrical-handoff.md` in this directory.

## Changed electrical source

| Path | Change |
| --- | --- |
| `hardware/generate_esp32_e220.py` | Reproducible Rev.1 source: J6/J7/J8/JP1, BAT_SENSE divider, explicit `BAT_SW` and `DEVKIT_VIN` nets, component metadata, and deterministic UUID generation. |
| `hardware/esp32-e220.kicad_sch` | Generated native schematic from the source above. |
| `hardware/esp32-e220.kicad_sym` | Generated project symbols for the new connectors. |
| `hardware/esp32-e220.kicad_pro` | ERC `footprint_link_issues` is ignored; see the validation qualification below. |

No PCB, footprint geometry, placement, routing, zone, production, E220, USER,
or DISPLAY copper file was edited.

## Net and topology evidence

Direct native-netlist evidence is retained in `esp32-e220.net`.

| Function | Exact generated connectivity |
| --- | --- |
| J6 `USER_GPIO` | 1 GND; 2 GPIO13/J1.3; 3 GND; 4 GPIO14/J1.5; 5 GND; 6 GPIO18/J2.9; 7 GND; 8 GPIO19/J2.10; 9 DEVKIT_3V3/J2.1; 10 GPIO23/J2.15. |
| J7 `DISPLAY_AUX` | 1 GND; 2 DEVKIT_3V3; 3 OLED_SDA = GPIO21/J2.11; 4 OLED_SCL = GPIO22/J2.14; 5 GPIO18/J2.9; 6 GPIO23/J2.15; 7 GPIO19/J2.10; 8 GPIO13/J1.3; 9 GPIO14/J1.5; 10 GPIO33/J1.9; 11 GND; 12 DEVKIT_3V3. |
| BAT_SENSE | `BUCK_IN -> R3.1 -> R3.2/BAT_SENSE -> R4.1 -> R4.2/GND`, with `C8.1=BAT_SENSE`, `C8.2=GND`, and `J1.10=BAT_SENSE`. |
| External switch | `J4.1/BAT_PLUS -> F1.1 -> F1.2/BAT_FUSED -> D3.1 and J8.1`; external mechanical switch harness connects J8.1 to J8.2; `J8.2/BAT_SW -> Q1.3/D`. Q1.2/S remains `BUCK_IN`; Q1.1/G remains `Q1_GATE`. |
| DevKit power jumper | `5V_SYS -> JP1.1`; removable shunt; `JP1.2 -> DEVKIT_VIN -> J1.1`. The two nets are distinct in the native netlist. |

## Component and assembly choices

| Reference | Exact MPN / footprint field | Assembly classification |
| --- | --- | --- |
| J6 | Samtec `TSW-105-07-G-D` / `Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical` | 2.54-mm PTH user expansion; PCBA DNP, user-installed header. |
| J7 | Samtec `TSW-106-07-G-D` / `Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical` | 2.54-mm PTH user expansion; PCBA DNP, user-installed header. |
| J8 | JST `B2PS-VH(LF)(SN)` / `Connector_JST:JST_VH_B2PS-VH_1x02_P3.96mm_Horizontal` | Factory-PCBA external switch-harness connector. JST VH is 3.96-mm PTH and rated 10 A AC/DC with AWG16 base-post configuration; this exceeds the 2-A-hold F1 upstream limit. Mating harness remains `VHR-2N` plus appropriate crimp contacts/wire. |
| JP1 | Samtec `TSW-102-07-G-S` header + `SNT-100-BK-G` shunt / `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | Header factory-PCBA fitted; removable shunt user-installed. This keeps DevKit USB-C mutual-use control explicit. |
| R3 | Yageo `RC0603FR-0710KL`, 10.0 kOhm 1% / `Carrier:Resistor_0603_1608Metric` | Factory-PCBA fitted. |
| R4 | Yageo `RC0603FR-073K3L`, 3.30 kOhm 1% / `Carrier:Resistor_0603_1608Metric` | Factory-PCBA fitted. |
| C8 | Murata `GRM188R71C104KA01D`, 100 nF 16 V X7R / `Carrier:Murata_GRM188_1608Metric` | Factory-PCBA fitted. |

## BAT_SENSE electrical basis

Primary sources:

* Espressif, *ESP32 Series Datasheet v5.3*, Table 2-1, p. 14: GPIO32 is
  `ADC1_CH4` (not ADC2): https://documentation.espressif.com/esp32_datasheet_en.html
* Espressif, *ESP32 Hardware Design Guidelines*, Release master, §1.3.11 ADC,
  PDF p. 16: ADC1 is recommended because ADC2 cannot be used with Wi-Fi;
  attenuation 3 has a calibrated effective range of 150 to 2450 mV and
  ±60 mV total error; add a 0.1-uF filter capacitor from an ADC pin to ground:
  https://documentation.espressif.com/esp-hardware-design-guidelines/en/latest/esp32/esp-hardware-design-guidelines-en-master-esp32.pdf

Use ADC1_CH4/GPIO32 at 11 dB attenuation (`ADC_ATTEN_DB_11`; attenuation 3 in
the cited hardware guideline). The divider ratio is `3.30/(10.0+3.30) =
0.248120`.

| BUCK_IN | BAT_SENSE nominal | Divider current |
| ---: | ---: | ---: |
| 6.0 V | 1.489 V | 451 uA |
| 7.4 V | 1.836 V | 556 uA |
| 8.4 V | 2.084 V | 632 uA |

At 8.4 V with independent 1% extremes that maximize output
(`R3=9.90 kOhm`, `R4=3.333 kOhm`), BAT_SENSE is 2.116 V. This retains 334 mV
to the 2.450-V calibrated-range upper edge. The divider Thevenin resistance is
2.48 kOhm. With C8=100 nF, the filter time constant is 248 us, cutoff is
approximately 641 Hz, and a five-time-constant settling interval is 1.24 ms.
The local capacitor supplies ADC sampling charge; firmware must allow this
settling time after enabling or switching the measurement path and use ADC
calibration because the cited source specifies ADC total error.

## Validation and source/actual-schematic synchronization

| Check | Result | Retained artifact |
| --- | --- | --- |
| Native KiCad ERC | `0 errors / 0 warnings` | `esp32-e220-erc.rpt` |
| Native netlist export | PASS; exact ref/pin/net evidence above | `esp32-e220.net` |
| Source reproducibility | PASS. Two consecutive `python3 hardware/generate_esp32_e220.py` runs produced identical SHA-256 values: schematic `5ac83c5c88fd6e3ad7d756f06af5cbe3a0393faad0dfb4e16bb332373fcaafd9`; symbols `738162cf88383ff1ca1f898dad1f94334051cff272c96745db805e3e39f11ff1`. | generator and generated files |
| Active PCB sync | Expected pre-layout `FAIL`; no existing reference property mismatch, no board-only reference, no USB-C power net. The only changed existing pad nets are J1.1 `/5V_SYS -> /DEVKIT_VIN` and Q1.3 `/BAT_FUSED -> /BAT_SW`; the missing PCB footprints are C8, J6, J7, J8, JP1, R3, and R4. | `active-pcb-sync.json` |

ERC qualification: the project historically stores active-board-matching local
footprint identifiers without a library prefix. Native KiCad reports these as
`footprint_link_issues`, which is a library-resolution diagnostic rather than
an electrical violation. It is ignored in the schematic ERC project settings
to make the native electrical result unambiguous; no electrical ERC category
was suppressed. Physical footprint existence, land pattern, placement, and
pad mapping remain a mandatory layout/reviewer gate.

## Reviewer risks and next gate

* The active PCB intentionally lags the approved schematic. `pcb_layout_dfm`
  must add/verify J6/J7/J8/JP1/R3/R4/C8 footprints, correct 2xN odd/even pad
  orientation, external-switch harness polarity, and all resulting airwires.
* J6 and J7 are direct exposed ESP32 nets without added series protection,
  ESD, or level translation by authorization. External accessories must be
  3.3-V-compatible and must not drive a DevKit pin unless the firmware/design
  explicitly permits it.
* BAT_SENSE reading accuracy depends on firmware calibration and allowing the
  calculated RC settling time. It measures post-switch `BUCK_IN`, so it is
  intentionally inactive when J8 is open.
* The existing DevKit USB-C warning note remains on the schematic. No human
  documentation was changed in this stage.

Next gate: independent `pcb_reviewer` electrical review, then the approved
handoff to `pcb_layout_dfm`; do not sync, place, or route the active PCB from
this role.
