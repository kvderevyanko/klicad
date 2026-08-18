# Stage 5 modular-carrier schematic review

Status: schematic created; PCB has not been created.

## Scope

`hardware/esp32-e220.kicad_sch` is the Stage 5 main-board schematic.  The
removable ESP32 DevKit is represented only by two verified 1×15 socket headers;
there is no bare ESP32, 3.3-V MCU regulator, CH340C, EN/BOOT circuit or
main-board programming header.

## Electrical review

- Header orientation is explicit: USB-C toward antenna is pin 1 on each row.
  `5V_SYS` is left-1/VIN; grounds are left-2 and right-2.
- J3 is explicitly the common EBYTE E220-T22D interface: populate exactly one
  `E220-400T22D` or `E220-900T22D`.  It is wired to the verified EBYTE pins
  M0=1, M1=2, RXD=3, TXD=4, AUX=5, VCC=6 and GND=7.  The DevKit nets are
  GPIO25/26/17/16/27 respectively; GPIO15 is not used.
- E220 operates from `5V_SYS`; its UART/control interface is 3.3 V.  R8 and
  R9 are 10-kOhm M0/M1-to-GND pull-downs.  They are an explicit **PROJECT
  DESIGN CHOICE** for reset mode `M1/M0=00`, not a claimed EBYTE resistor
  requirement.  AUX has no pull-down or external load.
- C5 is `GRM188R61A106MAAL` (10 uF, 10 V, X5R) and C6 is
  `GRM188R71C104KA01D` (100 nF, 16 V, X7R), both VCC-to-GND at the E220
  interface.  This is the documented local-decoupling project choice.
- GPIO21/`OLED_SDA` and GPIO22/`OLED_SCL` are signal-only Rev A reservations.
  OLED VCC and I2C pull-ups are NC/DNP and no OLED current source is present
  on the carrier.
- USB-C/eFuse uses the approved `TUSB320LAIRWBR` UFP/GPIO configuration and
  `TPS259630DDAR` support network.  OUT1 through the two 47-kOhm resistors and
  `MMBT3904LT1G` holds eFuse EN low at detach/Default and enables only at
  Medium/High.  The documented 900k VBUS_DET, 330k EN, 909R ILM, 365k/100k
  OVLO and 3.3nF dVdt parts are present.
- Rev A requires the main-board USB-C to be disconnected before using DevKit
  USB-C programming.  This is a required operating procedure, not diode OR-ing.

## Validation

The reproducible generator is
`hardware/generate_esp32_e220.py`; it writes project-local symbols and the
native KiCad S-expression from the installed KiCad template structure.  The
schematic was opened with `eeschema` under `xvfb-run`; KiCad read the file.  The
final generated version was checked with:

```text
XDG_CONFIG_HOME=/tmp/kicad-config XDG_CACHE_HOME=/tmp/kicad-cache \
XDG_DATA_HOME=/tmp/kicad-data kicad-cli sch erc \
  hardware/esp32-e220.kicad_sch --exit-code-violations
```

Result: **0 errors, 2 warnings**.  The two warnings are
`isolated_pin_label` for `OLED_SDA` and `OLED_SCL`: each is deliberately a
single-pin signal reservation because no OLED connector/power contract has
been selected.  No ERC exclusion or hidden error is used.  They must disappear
when a verified OLED connector/power design is introduced, or be removed if
the optional OLED interface is abandoned.

This validates file format and ERC only.  Prototype power, thermal, RF,
antenna, actual DevKit current and footprint/layout verification remain before
PCB release.
