# Rev.1 electrical scope-simplification handoff

Date: 2026-08-21

## Disposition

`SCHEMATIC CHANGE REQUIRED` was implemented as a bounded electrical/source
transaction. The active PCB was not edited. Independent `pcb_reviewer`
electrical approval is required before any physical synchronization.

## Exact source result

Removed completely from the current generated electrical source and project
footprint library:

- J7 `DISPLAY_AUX`;
- TP6, TP7, TP8, TP9, TP10;
- onboard D2 `WS2812B-V5` and its unreleased footprint candidate.

J1.9 remains the verified DevKit socket position named GPIO33, but is now an
intentional schematic no-connect because J7 removal leaves no approved GPIO33
interface.

Retained without topology/value changes: J8, JP1, BAT_SENSE R3/R4/C8,
U4/C9/C10, and E220 M0/M1 pull-downs R8/R9.

## J6 BUTTONS map

J6 is `DNP=YES`, value `BUTTONS 1x6 2.54mm DNP`, footprint
`Carrier:PinHeader_1x06_P2.54mm_Vertical`. It is a passive active-low panel
interface only, not a general GPIO header.

| J6 symbol pin / physical pad | Net | Verified DevKit socket endpoint |
| --- | --- | --- |
| 1 | `GND` | J1.2/J2.2 common GND |
| 2 | `GPIO13` | J1.3 |
| 3 | `GPIO14` | J1.5 |
| 4 | `GPIO18` | J2.9 |
| 5 | `GPIO19` | J2.10 |
| 6 | `GPIO23` | J2.15 |

Only normally-open contacts to J6.1/GND are authorized. Firmware must enable
pull-ups and interpret a pressed button as low. No external voltage, accessory
power, or general-purpose bidirectional use is authorized. Espressif lists the
ESP32 strapping pins as GPIO0/2/5/12/15; none of the five J6 GPIOs is a boot
strap. GPIO13/14 share JTAG functions, so button-panel use and JTAG use are
mutually constrained.

## External RGB interface

KiCad requires a numeric reference suffix, so the physical schematic reference
is J9 and its functional name/value contains `J_RGB`.

J9 is `DNP=YES`, value `J_RGB / RGB OUT 1x3 2.54mm DNP`, footprint
`Carrier:PinHeader_1x03_P2.54mm_Vertical`:

| J9 / `J_RGB` symbol pin / physical pad | Net/function |
| --- | --- |
| 1 | `5V_SYS` |
| 2 | `WS2812_DATA_5V`; driven by U3.4/Y |
| 3 | `GND` |

GPIO4 at J2.5 remains `WS2812_DATA_3V3` into U3.2/A. U3.1/OE and U3.3 are
GND, U3.5 and C7.1 are `5V_SYS`, and C7 remains the local 100-nF U3 bypass.
The external population policy is at most three WS2812B-V5 pixels.

WorldSemi specifies WS2812B-V5 VDD=3.7...5.3 V, `VIH` minimum 2.7 V at
VDD=5 V, 0.6-mA quiescent current, and a 12-mA condition for each RGB color.
Its typical application does not specify a DIN series resistor or an exact
value. No unevidenced series resistor was added. Cable ringing/EMC, external
local power integrity, reset behavior, and inrush require prototype testing.
Do not connect/use the RGB chain with the DevKit unpowered or assume a
guaranteed pixel state during reset.

Primary sources:

- WorldSemi WS2812B-V5:
  https://www.world-semi.co.kr/_files/ugd/89cd03_1023b0e9d135431aa1e6491bfc318112.pdf
- TI SN74AHCT1G125:
  https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf
- Espressif ESP32 GPIO/boot data:
  https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf

## Carrier library repair

`hardware/generate_stage7_footprints.py` now reproducibly writes
`hardware/fp-lib-table` with the `Carrier` nickname, generates the new 1x3 and
1x6 PTH footprints, and deletes the obsolete managed D2 footprint candidate.
The local library contains the exact referenced sources for:

- C8 -> `Carrier:Murata_GRM188_1608Metric`;
- C9/C10 -> `Carrier:Murata_GRM21_2012Metric`;
- R3/R4 -> `Carrier:Resistor_0603_1608Metric`;
- J6 -> `Carrier:PinHeader_1x06_P2.54mm_Vertical`;
- J9 -> `Carrier:PinHeader_1x03_P2.54mm_Vertical`.

The new PTH footprints have exact pads 1...N at 2.54-mm pitch, 1.00-mm drill,
and 1.70-mm project-choice copper. They are generic user-installed
header/solder points, not factory-fitted Samtec sockets.

## Power budget

Fresh simultaneous allocation:

- DevKit: 500.000 mA;
- E220: 110.000 mA;
- U3: 1.510 mA;
- U4 plus OLED-only AUX allocation: 100.100 mA;
- maximum three external WS2812B-V5 pixels: 109.800 mA;
- subtotal: 821.410 mA;
- 20% margin: 164.282 mA;
- total `5V_SYS`: 985.692 mA.

Full arithmetic, component headroom, and source qualifications are in
`power-budget.md`. `POWER BUDGET PASS` applies only to this allocation.

## Validation

- Named retry backup:
  `esp32-e220.pre-scope-simplification-retry.kicad_sch`, SHA-256
  `1607defc14cd9bc711566d671d53e996c54363b1dbd22effa2f1a1a0fd18f490`.
- Native KiCad 10.0.5 ERC before retry: 0 violations.
- Native KiCad 10.0.5 ERC final: 0 errors / 0 warnings / 0 exclusions.
- Netlist export completed without annotation warnings.
- Generated assembled schematic count: 37; R10/R11 remain the only intentional
  `NO_FOOTPRINT_DNP` items.
- Netlist proves all J6/J9 maps above, J1.9 intentional no-connect, and absence
  of D2/J7/TP6...TP10 references.
- Two consecutive source generations were byte-identical for the schematic,
  symbols, `fp-lib-table`, and both new footprints.
- Final SHA-256:
  - schematic:
    `c64364474e06d0f95523667bc0da6f9d4df6c4f023a7ddc1f876c488f631508c`;
  - symbols:
    `a2290fea4781d92b4987119117c9d389676ce7893a7129bdf53b3c1195af9e03`;
  - schematic generator:
    `90e7cc637f6b113d229e73981b040e6ca7a6c01ba3ab7885d7df0485e0532e27`;
  - footprint generator:
    `66fdc0fa77a00c16c3e9ce36b956aa94259dc99bfa549b4ec0babae00201ddee`;
  - `fp-lib-table`:
    `1e2a3636bc8224edb44245469e84ce490ccb22af1d7057faf483c5d8e5d9aa6d`.
- Active PCB SHA-256 remained
  `bf502dfde6ebb1f05d5d8f95fa77dc6f3d484fd9ddcdb47d3511c4b82b5f5036`.

## Expected parity impact

The authoritative read-only parity check against the known rejected active PCB
reports:

- board-only D2 and TP6...TP10;
- missing J6 and J9;
- U3.4 old `/WS2812_DIN` versus new `/WS2812_DATA_5V`;
- the already-approved J8 VH-to-XH production-property delta.

This `FAIL` is expected and blocks active-board use until physical recovery;
it is not an electrical-source validation failure.

## Context and next gate

`CONTEXT PROVENANCE CONFLICT`:

- controlling electrical source:
  `hardware/generate_esp32_e220.py` and `hardware/esp32-e220.kicad_sch`;
- stale historical physical generator:
  `hardware/generate_stage8_placement.py` still requests D2 and TP6...TP10;
- stale active-board contract allowance:
  `hardware/board_contract.json` still mentions D2 pad 2.

Those physical/checker sources were outside pcb_engineer ownership and were not
edited. They must be reconciled by the appropriate tooling/physical owner
before a new candidate is generated. Next gate: independent `pcb_reviewer`
electrical review. No active PCB synchronization is authorized by this handoff.
