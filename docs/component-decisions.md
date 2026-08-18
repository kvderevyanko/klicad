# Решения по компонентам

Статус: критерии выбора. Ни один сомнительный part number, nominal или
footprint не выбран на данном этапе.

## ESP32 module

- Определено: семейство `ESP32-WROOM-32E`; питание 3.0…3.6 V по официальному
  datasheet Espressif; требуется соблюдение official antenna placement/keepout.
- Выбрать: точный order code (flash/PSRAM option и temperature grade), источник
  поставки и revision datasheet.
- Критерии: подтверждённый land pattern, 3.3 V power integrity, boot/EN/GPIO0,
  strapping-safe interfaces, программирование UART0, antenna keepout.

## 5 V -> 3.3 V regulator

- Определено: требуется стабилизированная 3.3 V шина для ESP32.
- Выбрать: конкретный regulator, input/output capacitors, layout, thermal
  parameters и допустимый continuous/peak current.
- Критерии: worst-case power budget после выбора E220/OLED/LED, USB input
  conditions, dropout/efficiency, transient response, thermal margin, official
  datasheet/reference layout и доступность корпуса для производства.

## USB-C receptacle и входная защита

- Определено: USB-C используется как power input, без заявленного USB data.
- Выбрать: receptacle part number/footprint, CC sink implementation, power
  target, fuse/eFuse or equivalent protection, TVS/ESD and filtering.
- Критерии: official connector datasheet, USB Type-C compliance for selected
  sink-only use, VBUS current/power budget, ESD environment, mechanical stress,
  land pattern and manufacturer assembly rules.

## E220 connection

- Определено: внешний E220 предпочтителен для первой версии, чтобы main PCB не
  зависела от SMD footprint неизвестного модуля. Требуемые логические сигналы
  заданы как TXD, RXD, M0, M1, AUX, plus VCC/GND, но их pin numbers/order не
  известны.
- Выбрать: точный E220 part number, official manual, antenna/band, mating
  connector and its footprint, power rail and local decoupling.
- Критерии: VCC range, maximum/peak current, logic levels, boot/mode states,
  pinout, connector pitch/keying/current rating, module size/height, RF/antenna
  restrictions, legal radio configuration.

## WS2812 status LED and level handling

- Определено: ESP32 GPIO4 is the requested DATA source.
- Выбрать: exact LED variant/package, LED supply rail, local capacitor and any
  buffer/level shifter.
- Критерии: official VDD and VIH/VIL limits at the selected rail, data timing,
  reset-state behavior, GPIO4 boot-time effect, peak current/brightness policy,
  verified footprint and pin 1 orientation. Do not rely on empirical 3.3 V-to-5
  V compatibility.

## OLED connector

- Определено: I2C uses GPIO21/SDA and GPIO22/SCL.
- Выбрать: exact 0.96 inch SSD1306 module, connector, VCC, pin order, address,
  pull-ups and reset requirements.
- Критерии: official module datasheet, I2C voltage compatibility with ESP32,
  total bus pull-up resistance, cable length/noise and mechanical access.

## Programming / debug interface

- Определено: UART0/GPIO1 and GPIO3 are the ESP32 ROM serial programming path;
  EN and GPIO0 must be available for reset/download control.
- Выбрать: 3.3 V TTL header versus integrated USB-UART bridge, connector and
  pinout, auto-program circuit or manual buttons, ESD and test-point access.
- Критерии: Espressif boot sequence/reference circuit, adapter voltage level,
  field-service accessibility, no unwanted influence on boot strapping.

## Test points, passives and mechanics

- Определено: test access is required for rails, reset/boot and debug; final
  list is in `requirements.md`.
- Выбрать: test-point technology, locations, probe clearance, mounting holes,
  board outline, silkscreen conventions and fabrication limits.
- Критерии: DFM/assembly capability, safe probe access, no RF keepout violation,
  unambiguous polarity/pin-1 markings and required field diagnostics.

## KiCad library status

- Installed KiCad 6 standard libraries include generic connector/USB-C symbols,
  standard USB-C receptacle footprints, WS2812/WS2812B symbols and footprints,
  generic ESP32-WROOM-32 symbol/footprint, and test-point libraries.
- No exact standard `ESP32-WROOM-32E` entry was found locally; an exact symbol/
  footprint must be verified against Espressif datasheet or official Espressif
  KiCad library before use. No standard EBYTE E220 library entry was found.
- The installed display footprints are board-specific (for example, Adafruit
  modules), not a verified footprint for the unspecified OLED in this project.

## Stage 2 — confirmed component decisions

### ESP32 and E220 interface

- `ESP32-WROOM-32E-N4` is selected specifically because it has no PSRAM. GPIO16
  (module pin 27) and GPIO17 (pin 28) are available; variants with R2 PSRAM
  cannot use GPIO16. Final application mapping is GPIO17<-E220 TXD and
  GPIO16->E220 RXD; GPIO15 is rejected because it is MTDO strapping.
- `E220-900T22D` is selected as an external 2.54 mm DIP module. Pin sequence:
  M0/M1/RXD/TXD/AUX/VCC/GND = 1/2/3/4/5/6/7. It uses 3.3 V communication levels
  even with 5 V supply, so no level translation is selected on the E220 UART or
  control lines. M0/M1 are MCU-driven and cannot float.
- EBYTE provides an official `Pcb_lib`/3D download on its product page. No local
  standard KiCad E220 library exists, and no E220 footprint has been made or
  imported. It must first be audited against the manual and selected mating
  socket.
- Stage 2 verification of that download: official URL
  `https://www.cdebyte.com/pdf-down.aspx?id=1717` is a RAR archive containing
  `E220系列-PcbLib.PcbLib` (Altium PcbLib, timestamp 2022-07-06), not a native
  KiCad library. It proves EBYTE publishes a source library, but does **not**
  approve a direct KiCad footprint assignment. Audit exact E220-900T22D
  geometry/pin 1 against the current manual before any controlled conversion.

### Power and USB-C

- `TPS62162DSGR` selected: 3.3 V fixed output, 3…17 V input, 1 A capability.
  Required TI reference values: 2.2 µH L, 10 µF ceramic CIN, 22 µF X5R/X7R
  COUT; fixed FB to AGND and thermal pad to AGND. Exact passives/footprints wait
  for availability and footprint verification.
- E220 is fed from protected 5.0 V, not the 3.3 V rail. EBYTE table lists
  110 mA TX momentary, 8 mA RX and 3 µA sleep; 5 V is chosen because full RF
  output is guaranteed at >=5 V. Do not exceed 5.5 V.
- USB-C discrete sink topology selected: CC1/CC2 each receive 5.1 kOhm Rd to
  GND; `TPD4S311` protects CC and `TPD1E10B06` protects default-5-V VBUS.
  Receptacle, fuse/eFuse and current contract remain intentionally unselected.

### BOOT/RESET and WS2812 data

- EN uses Espressif's recommended 10 kOhm pull-up plus 1 µF RC and RESET-to-GND
  button. GPIO0 uses 10 kOhm pull-up and BOOT-to-GND button, with no high-value
  capacitor. Programming remains external 3.3 V UART0/manual boot.
- `SN74AHCT1G125DBVR` is selected only for 3.3 V GPIO4 to 5 V WS2812 DIN
  translation: 5 V VCC, OE low, 0.1 µF local bypass. The exact LED remains a
  blocker; no WS2812 footprint is assigned.

### KiCad recheck

- KiCad executable and `kicad-cli` are now version `10.0.5`. Both
  `kicad-cli sch erc` and `kicad-cli pcb drc` are available. In this sandbox set
  `XDG_CACHE_HOME`, `XDG_CONFIG_HOME` and `XDG_DATA_HOME` under `/tmp` before
  running the CLI, because the default user locations are read-only.
- Local standard libraries still offer generic ESP32-WROOM-32, USB-C,
  WS2812/WS2812B and test-point assets, but no exact ESP32-WROOM-32E or
  E220-900T22D entry. Exact assets require manufacturer-source verification.

## Stage 2.1 — WS2812B-V5 and power decision record

### WS2812 status LED

- Selected exact electrical part: `WS2812B-V5` by WorldSemi, top-SMD 5050,
  four pins `VDD/DOUT/VSS/DIN`, 5.0 × 5.4 × 1.57 mm. It is powered from the
  protected 5.0 V rail and receives data only from the 5 V
  `SN74AHCT1G125DBVR` output.
- The manufacturer document gives `VIH >= 2.7 V`, `VIL <= 0.7 V`, 12 mA per
  RGB channel condition and 0.6 mA working quiescent current. It does not state
  a total maximum supply current. The approved budgeting number is therefore
  36.6 mA (`3 × 12 + 0.6`), labelled a bounded allocation rather than a formal
  maximum.
- No DIN series-resistor value is selected: the manufacturer document does not
  specify one. No LED-local bypass capacitor is selected either: its typical
  circuit says no filter capacitor is required and specifies no capacitance.
  The AHCT still requires its manufacturer-recommended local 0.1 uF bypass.
- Footprint plan: **none assigned**. The generic KiCad WS2812B asset is not
  approved for this V5 package because no official land pattern comparison has
  been performed. A verified manufacturer pad layout is needed before placement.

### Updated rail decision

- ESP32 3.3 V design allocation is 500 mA, backed by Espressif's minimum
  supply-capability guidance; the cited ESP32-WROOM-32E RF table reports a
  379 mA peak in its highest listed Wi-Fi TX test. OLED is `TBD`, not estimated.
- The direct 5 V allocation is E220 110 mA + WS2812B-V5 36.6 mA + AHCT 1.51 mA
  = 148.11 mA. The buck's ideal input lower bound for `500 mA + I_OLED` at 3.3 V
  from 5 V is `0.66 × (500 mA + I_OLED)`. Thus the known total is at least
  478.11 mA plus OLED contribution and all real conversion losses.
- `TPS62162DSGR` (1 A output) remains selected only conditionally: it covers
  the known ESP32 allocation but has no approved total headroom until OLED,
  thermal conditions and all 3.3 V auxiliaries are verified. USB-C receptacle,
  source-current capability and current protection remain unselected because a
  500 mA source cannot be shown sufficient.

Sources: [WorldSemi WS2812B-V5](https://www.world-semi.co.kr/_files/ugd/89cd03_1023b0e9d135431aa1e6491bfc318112.pdf), [WorldSemi WS2812 catalogue](https://world-semi.com/ws2812-family/), [ESP32-WROOM-32E datasheet](https://documentation.espressif.com/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf), [ESP32 Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html), and [SN74AHCT1G125, TI](https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf).

## Stage 3.1 — selected schematic-level parts

| Function | Selected part | Evidence and controlled decision |
| --- | --- | --- |
| USB-C receptacle | GCT `USB4105-GF-A` | Official drawing/layout; power-only VBUS/GND/CC use. PCB footprint deferred to official layout audit. |
| Type-C status | TI `TUSB320LAIRWBR` | UFP internal Rd; VBUS_DET 900 kOhm ±1 %; open-drain OUT1/OUT2. VDD is fed through onsemi `MMSD4148T1G` and uses `GRM188R71C104KA01D` 0.1-uF/16-V/X7R. The separate VBUS bulk requirement is 1…10 uF. `PORT=GND`, `EN_N=GND`, `ADDR=NC`. |
| Status to ESP | 12-kOhm/20-kOhm divider per output | **PROJECT DESIGN CHOICE.** Pull OUT1/OUT2 to VBUS and divide to GPIO32/GPIO33; 5.25 V -> 3.28 V. No high-voltage signal connects directly to ESP32. |
| eFuse | TI `TPS259630DDAR` + Panasonic `ERA3AEB9090V` | 909 Ohm gives 1.005-A typical / 0.949…1.051-A characterised current limit. EN uses 100-kOhm `ERA3AEB104V` from IN (not a direct tie); for below 6 V this is TI-supported and permits ESP boot at Default Type-C current. |
| Buck L/C | TPS62162DSGR; TDK `VLS3012CX-2R2M-1`; Murata `GRM21BR61E106KA73` / `GRM21BR61A226ME44` | 2.2 uH; 1.70-A saturation, 2.55-A temperature rise, 74 mOhm max DCR; 10-uF 25-V X5R CIN and 22-uF 10-V X5R COUT. EVM validates values/topology; actual parts are project selections. |
| E220 local capacitors | Murata `GRM188R61A106MAAL` / `GRM188R71C104KA01D` | 10-uF 10-V X5R + 0.1-uF 16-V X7R **PROJECT DESIGN CHOICE**, not a claimed EBYTE value. |
| OLED bus | 4.7-kOhm 1-% fit/DNP sites | **PROJECT DESIGN CHOICE:** connector GND/3V3/SDA/SCL, 100-mA allocation; configured after verified module pull-ups. |

The Type-C policy is deliberately two-stage: ESP32 has boot power on any valid
attach, then firmware reads TI's `OUT1/OUT2` truth table. Default (`H/L`) is
low-load diagnostic boot only; full concurrent budget requires Medium (`L/H`)
or High (`L/L`). This avoids a circular design in which ESP cannot boot to read
the very status that would enable it.

Full-load design allocation is 721.685 mA at 3V3 (500-mA ESP32, 100-mA OLED,
1.404-mA I2C, then 20-% margin). Its calculated input is 560.5 mA at 5 V using
85-% efficiency; with 110-mA E220, 36.6-mA WS2812B and 1.51-mA AHCT it is
708.6 mA at 5 V / 738.0 mA at 4.75 V. This passes the selected 1-A buck and
0.949-A minimum eFuse-limit check but is awaiting hardware transient/thermal
validation.

### Stage 3.1 eFuse support-network correction

| Pin / function | Actual component decision | Status |
| --- | --- | --- |
| IN / VBUS bulk | `GRM188R71A105KA61D`, 1 uF ±10 %, 10 V X7R | TI requires at least 0.01 uF locally and recommends >0.1 uF for a remote source; **project choice** 1 uF also lies in UFP's 1…10-uF port-bulk window. |
| OUT | second `GRM188R71A105KA61D`, 1 uF ±10 %, 10 V X7R | **Project choice** local output bypass; TPS2596 gives no mandatory fixed `COUT`. |
| EN/UVLO | `ERA3AEB104V`, 100 kOhm ±0.1 %, IN-to-EN | Manufacturer-permitted connection below 6 V; EN must not float. Internal UVLO is retained. |
| OVLO | `ERA3AEB3653V` 365 kOhm ±0.1 % + `ERA3AEB104V` 100 kOhm ±0.1 % | **Project choice:** 5.58-V nominal cutoff. Required divider prevents a floating OVLO pin, but is not credited as an E220 5.5-V precision clamp. |
| dVdt | `GRM1885C1H332JA01D`, 3.3 nF ±5 %, 50 V C0G | **Project choice:** TI-controlled slew setting. About 275 mA calculated initial capacitive inrush for the documented 21-uF local output-side capacitance. |
| FLT / reverse power | FLT NC; no alternate 5V_SYS source | FLT pull-up is unnecessary when unused. TPS259630 reverse-current blocking is not specified; this is a project topology constraint. |

The only selected level shifter is `SN74AHCT1G125DBVR` for WS2812B-V5 DIN. It
is not used in the Type-C/eFuse path.

## Stage 3.2 — Type-C preflight hold

The status-to-ESP row above is superseded and must not enter a schematic:
pulling TUSB OUT1/OUT2 to `VBUS_PRE` and then dividing them leaves the TUSB
pins pulled toward VBUS. This conflicts with TI's non-failsafe-pin warning when
VDD is off. No replacement values or nets are selected until the sequencing and
logic-level decision is approved.

The selected TPS259630 / 909-Ohm setting is a 1-A-class rail protector, not
500-mA Default-Type-C enforcement. A revised hardware boot/source-current
architecture is required before Type-C/eFuse/ESP32 blocks enter KiCad.

## Stage 3.3 — active Type-C enable decision

| Function | Selected part / net | Engineering result |
| --- | --- | --- |
| OUT1 pull-up | `ERA3AEB473V`, 47 kOhm, `TUSB_VDD` only | No VBUS pull-up and no ESP connection. Default/released OUT1 drives Q1 on. |
| Inverter | onsemi `MMBT3904LT1G`; base through second `ERA3AEB473V` 47 kOhm | Collector sinks eFuse EN when OUT1 is released; emitter GND. |
| eFuse enable pull-up | `ERA3AEB334V`, 330 kOhm, `TUSB_VDD` to EN/UVLO | VDD absent -> EN low; at 2.75-V min VDD it is above 1.22-V EN-high max. |
| Current policy | `5V_SYS` is absent at Default | Hardware, not firmware, restricts full receiver operation to Medium/High advertised source current. |

The enable path itself consumes at most 106 uA through OUT1 (Medium/High) and
about 55 uA in Default. Together with the 70-uA typical TUSB active current,
the conservative pre-eFuse allocation is 0.25 mA. The former divider and ESP
GPIO32/GPIO33 parts are forbidden and not fitted.

Sources: [GCT USB4105 drawing](https://gct.co/files/drawings/usb4105.pdf), [TUSB320LAI, TI](https://www.ti.com/lit/ds/symlink/tusb320lai.pdf), [TPS2596, TI](https://www.ti.com/lit/ds/symlink/tps2596.pdf), [TPS621x0 EVM, TI](https://www.ti.com/lit/ug/slvu483a/slvu483a.pdf), [TDK VLS3012CX](https://product.tdk.com/en/search/inductor/inductor/automotive-inductor/info?part_no=VLS3012CX-2R2M-1), [Murata GRM21BR61E106KA73](https://search.murata.com/en-US/partdetail?partno=GRM21BR61E106KA73), [Murata GRM21BR61A226ME44](https://search.murata.com/en-US/partdetail?partno=GRM21BR61A226ME44), [E220 manual, EBYTE](https://www.cdebyte.com/pdf-down.aspx?id=3552).

## Stage 4 — active component boundary: removable DevKit

This record supersedes the earlier selection of a bare ESP32-WROOM-32E-N4,
`TPS62162DSGR`, bare-module EN/GPIO0 circuitry and external UART0 programming
header for the next schematic.  They remain historical design records only.

| Function | Active decision | What remains unselected / why |
| --- | --- | --- |
| ESP32 controller | A removable USB-C/CH340C ESP32-WROOM DevKit with 30 pins / 2×15 headers, powered from `5V_SYS` at its verified 5-V header input | **BLOCKER:** exact manufacturer/orderable model/revision, official schematic, header numbering/orientation and 5-V current input data.  No generic DevKit symbol or footprint is authorised. |
| Main-board ESP power/reset/programming | Omitted: no 3.3-V MCU buck, bare ESP32, EN/BOOT circuit or main-board programming header | These functions must be present on the verified DevKit.  The main PCB must not duplicate or drive them. |
| DevKit programming USB-C | DevKit-local function only | **BLOCKER:** board-level VBUS/header isolation and permitted dual-power state.  Rev A service procedure is removal/power-down before programming, pending documentation. |
| E220 UART/control | `GPIO17→RXD(3)`, `GPIO16←TXD(4)`, `GPIO25→M0(1)`, `GPIO26→M1(2)`, `GPIO27←AUX(5)` | Electrical EBYTE pin functions are verified; physical header pins and any clone-specific GPIO circuitry are not. |
| E220 mode bias | No external value selected | EBYTE calls M0/M1 very-weak-pull-up inputs and says they cannot float, but gives no external resistor or mandatory startup network.  Firmware controls them; request EBYTE guidance if a pre-firmware mode is required. |
| E220 supply | `5V_SYS→VCC(6)`, GND→GND(7); 5.0-V nominal project choice | EBYTE confirms 2.6…5.5-V supply range for 22-dBm products, 3.3-V communications and 90…110-mA TX.  Recalculate the system current budget with the selected DevKit's documented 5-V load. |

The official Espressif ESP32-DevKitC V4 documentation is deliberately **not**
used as a replacement component choice: it is a Micro-USB / 2×19 official
board, whereas the requested board is USB-C / CH340C / 2×15.  It is useful
only as primary-source evidence that a board's power-source combinations and
header map are specific to that board.

Sources: [E220-T Series User Manual, EBYTE](https://www.cdebyte.com/pdf-down.aspx?id=4221), [E220-900T22D product page, EBYTE](https://www.cdebyte.com/products/E220-900T22D/4), and [ESP32-DevKitC V4 User Guide, Espressif](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html).

### Stage 4.1 — DevKit interface frozen for schematic

The user-provided, verified source fixes the socket interface: two 1×15
headers, each pin 1 at the USB-C/antenna end.  The left header order is `VIN,
GND, 13, 12, 14, 27, 26, 25, 33, 32, 35, 34, 39/VN, 36/VP, EN`; the right order
is `3V3, GND, 15, 2, 4, 16/RX2, 17/TX2, 5, 18, 19, 21, 3/RX0, 1/TX0, 22, 23`.

This authorises project-local symbols for the two headers only; it does not
select their mating footprint.  `5V_SYS` connects only to left pin 1 (VIN),
and E220 uses left 6/7/8 and right 6/7 as documented.  The approved Rev A
programming constraint is operational mutual exclusion of the two USB-C ports,
not a new electrical component or source-selection circuit.

## Stage 5 — active modular carrier decision record

This section supersedes the active single `E220-900T22D` population decision.
The earlier bare-ESP32, main-board `TPS62162`, EN/BOOT and programmer circuits
remain superseded history and shall not be restored to the carrier schematic.

| Function | Active decision | Verification / remaining decision |
| --- | --- | --- |
| Radio population | One removable EBYTE `E220-400T22D` **or** `E220-900T22D` | EBYTE documents one common 400/900-T22D pin-definition section; both pages say UART, 22 dBm, SMA-K and 21 × 36 mm.  The 400-MHz and 900-MHz variants are RF alternatives, not a single antenna choice. |
| Electrical radio interface | Pins 1…7 = M0, M1, RXD, TXD, AUX, VCC, GND; 3.3-V UART/control and `5V_SYS` VCC | Direct connection only to DevKit 3.3-V GPIOs.  Use the manual's 3.3-V communication specification rather than treating the product-page 3.3/5-V I/O wording as a 5-V interface guarantee. |
| Radio socket / footprint | **Unselected** | EBYTE Section 3.3 is a common `E220-400/900T22D` source drawing: 36 × 21 mm, seven 2.54-mm-pitch electrical pads plus holes 8…10, 1.50 × 2.00-mm pads / 0.90-mm holes. This confirms common source coordinates, but the official Altium PcbLib/download is not approval for a KiCad footprint or an exact mating connector. Select only after controlled mechanical/pin-1/mating-socket audit at PCB stage. |
| M0/M1 reset mode | External 10-kOhm pull-down per line to GND | **PROJECT DESIGN CHOICE.** It forces documented `M1/M0=00` while GPIOs reset.  The EBYTE manual requires non-floating inputs but specifies no external resistor value. Prototype-verify GPIO high drive and mode transition. |
| E220 local bypass | `GRM188R61A106MAAL` 10 uF/10 V/X5R + `GRM188R71C104KA01D` 0.1 uF/16 V/X7R at VCC/GND | **PROJECT DESIGN CHOICE**, not claimed as an EBYTE-mandated value. Place locally after socket/mounting selection. |
| DevKit supply | `5V_SYS` to verified left-header pin 1 / VIN | 500 mA at 5 V is a conservative **PROJECT DESIGN ALLOCATION**, derived from the prior Espressif supply-capability basis; it is not a DevKit manufacturer current rating. Measure current and on-board-regulator thermal performance. |
| OLED | GPIO21/22 signal reservation only; VCC and pull-ups NC/DNP in Rev A | Exact display and its supply/current are unresolved.  Do not budget it or feed it from DevKit 3V3 until module and regulator margin are verified. |
| 5-V budget / Type-C policy | `5V_SYS` allocation 777.732 mA including 20 % margin; enable remains only at Type-C Medium/High | 648.110-mA pre-margin subtotal: DevKit 500 + E220 110 + WS 36.6 + AHCT 1.51 mA.  0.25-mA TUSB/enable allocation is pre-eFuse, giving 777.982 mA raw USB allocation and 722.018 mA to the 1.5-A policy.  Prototype validates cable/bursts/thermal. |

Official sources: [E220-T Series User Manual, EBYTE](https://www.cdebyte.com/pdf-down.aspx?id=4221), [E220-400T22D, EBYTE](https://www.cdebyte.com/products/E220-400T22D/4), [E220-900T22D, EBYTE](https://www.cdebyte.com/products/E220-900T22D/4), [TPS2596, TI](https://www.ti.com/lit/ds/symlink/tps2596.pdf), and [TUSB320LAI, TI](https://www.ti.com/lit/ds/symlink/tusb320lai.pdf).

### Stage 5 gate-review implementation correction

The review of the generated KiCad file confirms the selected `USB4105-GF-A`
is represented by its complete official electrical contact set, rather than a
four-pin abstraction: all four VBUS contacts, four signal GND contacts, both
shell contacts, CC1/CC2, both D+ and both D- contacts, and both SBU contacts.
Only VBUS/GND/CC join active circuitry; D+/D- remain paired local NC nets and
SBU is NC.

The actual schematic now also instantiates the active status path selected in
Stage 2.1: `SN74AHCT1G125DBVR` (OE=GND, 5-V VCC, 100-nF local C7) drives a
`WS2812B-V5` DIN from GPIO4.  This does not select a WS2812 footprint.

Two physical pin-order checks were material to the fail-safe gate and are
frozen in the project symbols: onsemi `MMSD4148T1G` is pin 1 cathode / pin 2
anode, so D1 is `VBUS_PRE` (A2) to `TUSB_VDD` (K1); onsemi
`MMBT3904LT1G` is pin 1 base / pin 2 emitter / pin 3 collector, so Q1 is
`QBASE`/GND/`EFUSE_EN`.  These replace the prior generic-symbol assumptions;
no package footprint is selected by this pin-order correction.

The non-BOM PWR_FLAG markers on `VBUS_PRE`, `TUSB_VDD`, and GND are explicit
KiCad ERC source-boundary annotations.  They do not represent components or
change the approved electrical topology.

Sources: [USB4105 drawing, GCT](https://gct.co/files/drawings/usb4105.pdf), [SN74AHCT1G125, TI](https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf), [WS2812B-V5, WorldSemi](https://www.world-semi.co.kr/_files/ugd/89cd03_1023b0e9d135431aa1e6491bfc318112.pdf), [MMSD4148T1G, onsemi](https://www.onsemi.com/pdf/datasheet/mmsd4148t1-d.pdf), and [MMBT3904LT1G, onsemi](https://www.onsemi.com/pdf/datasheet/mmbt3904lt1-d.pdf).

### Stage 5 second-gate ESD / thermal-pad correction

- `TPD1E10B06DPYR` is now instantiated as D3 on raw `VBUS_PRE`: TI pin 1 is
  the protected I/O and pin 2 is GND.  It is a VBUS ESD diode, not a source or
  regulator.
- TPS259630's actual non-numbered exposed thermal pad is represented by the
  explicit schematic pin `EP`, connected to GND.  This is a **footprint
  mapping requirement**: a later verified DDA SOIC-EP footprint must map its
  exposed pad to `EP`/GND; it must not leave that pad electrically absent.
- The active test-point plan is now schematic-level: TP1 `5V_SYS`, TP2 named
  E220_VCC on `5V_SYS`, TP3 M0, TP4 M1, TP5 AUX, TP6 E220 RXD and TP7 E220
  TXD.  Test-point part numbers, land patterns and placements are still not
  selected.
- The prior `TPD4S311DRYR` CC decision is **on hold, not implemented**.  Its
  official 2.7…4.5-V `VPWR`, 0.3…1-uF VPWR bypass and 0.1-uF ≥35-V VBIAS
  capacitor cannot be powered safely by raw 5 V, `5V_SYS`, DevKit 3V3 or the
  non-bounded diode-fed `TUSB_VDD` in the active Default-current gate.  TI
  `TPD2S300` was evaluated as a possible replacement but has the same
  2.7…4.5-V VPWR requirement; no supplyless verified 24-V short-to-VBUS CC
  protector was selected.  Do not replace it silently with a 5.5-V passive ESD
  array, because that does not establish the required 24-V isolation.

Sources: [TPD1E10B06, TI](https://www.ti.com/lit/ds/symlink/tpd1e10b06.pdf), [TPD4S311, TI](https://www.ti.com/lit/ds/symlink/tpd4s311.pdf), [TPD2S300, TI](https://www.ti.com/lit/ds/symlink/tpd2s300.pdf), and [TPS2596, TI](https://www.ti.com/lit/ds/symlink/tps2596.pdf).

### Stage 5 third-gate decision — approved pre-gate rail and CC protector

| Function | Selected component / implementation | Status and verification basis |
| --- | --- | --- |
| Pre-gate 3.3-V LDO | TI `TLV70433DBVR` (U4), DBV/SOT-23-5: 1=GND, 2=VBUS_PRE IN, 3=PRE_GATE_3V3 OUT, 4/5=NC | **Manufacturer requirement:** 2.5…24-V operating input, 150-mA maximum output; IN cap >=0.1 uF and OUT cap >=1 uF nominal with >0.47-uF effective. No EN pin exists. |
| U4 local capacitors | C8/C9 Murata `GRM188R71A105KA61D`, 1 uF ±10 %, 10 V X7R | **PROJECT DESIGN CHOICE** of a verified part above the required capacitance/rating. Dedicated local IN/OUT parts; C9 is not replaced by a remote capacitor. |
| CC/SBU short-to-VBUS + ESD | TI `TPD4S311YBFR` (U5) | **Manufacturer requirement:** VPWR=2.7…4.5 V, C4=PRE_GATE_3V3; 0.3…1 uF bypass. C10 is the selected 1-uF Murata MPN. C1/C2/C3=GND; A4/VBIAS gets 0.1 uF >=35 V. |
| U5 VBIAS capacitor | C11 Murata `GRM188R71H104KA93D`, 0.1 uF ±10 %, 50 V X7R | Meets TI's 0.1-uF/at-least-35-V requirement. Exact land pattern remains deferred. |
| CC topology | J4 CC1 -> U5 A2/C_CC1 + B2/RPD_G1; J4 CC2 -> U5 A3/C_CC2 + B3/RPD_G2; U5 D3/D4 -> U1 CC1/CC2 | **Manufacturer requirement:** tie RPD_G1/G2 to C_CC1/C_CC2 when dead-battery resistors are needed. Therefore no discrete permanent 5.1-kOhm Rd is populated. Unused SBU and FLT are NC. |
| U1 and gate pull-ups | U1 VDD, R2=47 kOhm OUT1 pull-up and R4=330 kOhm TPS EN pull-up are all `PRE_GATE_3V3` | **Approved architecture:** raw VBUS is absent from the OUT1/EN logic. U1 has C2 `GRM188R71C104KA01D` 0.1 uF/16 V/X7R VDD bypass. |

The previous `MMSD4148T1G` diode-fed `TUSB_VDD` and “TPD4S311 on hold”
decisions are **superseded history** and are not present in the current
schematic.  The U5 symbol preserves official DSBGA ball IDs rather than
inventing a numerical pinout; no U5 footprint is assigned or approved.

Sources: [TLV704, TI](https://www.ti.com/lit/ds/symlink/tlv704.pdf),
[TPD4S311, TI](https://www.ti.com/lit/ds/symlink/tpd4s311.pdf),
[TUSB320LAI, TI](https://www.ti.com/lit/ds/symlink/tusb320lai.pdf),
[Murata GRM188R71A105KA61D](https://search.murata.com/en-US/partdetail?partno=GRM188R71A105KA61D),
and [Murata GRM188R71H104KA93D](https://www.murata.com/en-us/products/productdetail?partno=GRM188R71H104KA93%23).

## Rev.1 active decisions — battery carrier

The USB4105/TUSB320/TPD1E10B06/TPD4S311/TLV704/TPS259630 and all CC/pre-gate
logic are superseded and removed from the active schematic; retain prior text
only as design history.

| Block | Active choice | Basis |
| --- | --- | --- |
| Input connector | J4 generic 2-pin, “PROTECTED 2S LI-ION INPUT ONLY 6...8.4V” | Required interface only; no unverified physical connector footprint selected. |
| Buck | TI `TPS62133RGT`, fixed 5 V, 3 A | Official 3…17-V operation, 100-% duty cycle and fixed 5-V variant. Valid at 6-V input by documented drop calculation. |
| Inductor/filter | `XFL4020-222MEB`, C1=10 uF/25 V, C2=0.1 uF/16 V, C3=22 uF/10 V, C4=3.3 nF/50 V | TI recommended topology/component values; named real components and ratings in requirements. |
| Overcurrent | Littelfuse `1812L200/16` | 2-A hold / 3.5-A trip / 16-V PPTC; protects carrier only and requires thermal derating test. |
| Reverse polarity | Diodes `DMP3130LQ-7` + R1=100 kOhm, R2=1 Mohm | 30-V P-MOS; official 1/G,2/S,3/D. **Corrected orientation:** D3=`BAT_FUSED`, S2=`BUCK_IN`, R2=`BUCK_IN`->G. The intrinsic diode then faces BAT_FUSED -> BUCK_IN for correct-polarity precharge and blocks reverse battery. Values produce -5.45…-7.64 V VGS for correct 6.0…8.4-V polarity. |
| Transient clamp | Littelfuse `SMBJ10CA` from BAT_FUSED to GND | PROJECT DESIGN CHOICE justified by external battery lead transient; bidirectional to avoid an intentional reverse-battery diode short. |
| Switch | No on-board switch in Rev.1 | Explicit choice: disconnect pack or disable external BMS output for programming; do not infer a charge/power switch. |

## APPROVED ELECTRICAL BASELINE — Rev.1 battery carrier

The external protected 2S/BMS input, `TPS62133RGT` 5-V converter,
`1812L200/16`, `DMP3130LQ-7`, `SMBJ10CA`, `XFL4020-222MEB` and named C1...C4
support network are **APPROVED ELECTRICAL BASELINE**. The current DevKit,
E220 and WS/AHCT choices are included. Do not change these without a new
documented electrical finding or user-approved scope change.

## Rev.1 OLED connector decision

| Block | Active choice | Basis / limit |
| --- | --- | --- |
| OLED interface | J5 removable female 1x4 socket, order 1=GND, 2=VCC, 3=SCL, 4=SDA; preferred carrier socket `SSW-104-02-G-S` | User-provided order. Samtec SSW is a 2.54-mm THT socket family; final supplier availability and actual OLED pin projection remain procurement/mechanical checks. |
| Supply | J5 VCC=`DEVKIT_3V3` only | SSD1306 logic VDD is 1.65...3.3 V; common Adafruit 0.96-in breakout uses 3.3-V power/logic. This supports 3.3 V, not an assertion that every generic module is identical. 5 V is prohibited. |
| I2C nets | GPIO22 -> SCL, GPIO21 -> SDA | User-verified DevKit mapping retained. |
| Carrier pull-ups | R10 SDA and R11 SCL, each 4.7 kOhm 1 %, to DEVKIT_3V3; `DNP=YES` | PROJECT DESIGN CHOICE. Typical breakout boards may already pull up I2C. Default DNP avoids parallel pulls; if fitted, `R_EFFECTIVE=4.7k||R_MODULE`. |
| OLED current | 100 mA at 3.3 V / extra 100 mA at `5V_SYS` | Conservative PROJECT DESIGN ALLOCATION, not module max. Adafruit's common-board guide reports about 20 mA average; exact user module and DevKit regulator require prototype validation. |
| Mechanics | 26.000x26.000-mm body, 2.540-mm 1x4, mounting-centre spacing X=21.740 mm/Y=22.000 mm | **USER-PROVIDED drawing data.** This supersedes the former 25.2x26/X=21/Y=TBD approximation. Hole diameter, all header/body datums, display/flex clearance and notch/cutout remain unverified; only a non-production mechanical template exists. |

## Stage 7 — selected carrier connectors and mechanical-footprint status

These choices do not change the approved electrical topology. They select
carrier PCBA connectors and are further detailed in
`docs/footprint-mechanical-review.md`.

| Carrier function | Preferred exact MPN | Status / limitation |
| --- | --- | --- |
| J4 protected 2S input | JST `B2B-XH-A` | 2-pin THT XH header, 2.50-mm pitch, 3-A rating with AWG22. `XHP-2` + `SXH-001T-P0.6` is the matching harness choice. Final wire/strain relief and sourcing remain PCB/procurement work. |
| J1/J2 DevKit sockets | 2 × Samtec `SSW-115-02-G-S` | 15-position 2.54-mm THT socket. Actual DevKit male-pin projection and body/antenna datum must be measured before placement release. |
| J3 radio socket | Samtec `SSW-107-02-G-S` | 7-position 2.54-mm THT socket. `Carrier:E220_T22D_Socket_400_900` is a source-geometry-compatible template, not production approval of SMA/fixed-hole/underside mechanics. |
| J5 OLED socket | Samtec `SSW-104-02-G-S` | 4-position 2.54-mm THT socket. OLED X/Y mounting spacing is now known, but hole diameter/header/body datum and display/notch geometry still prohibit a production mounting footprint. |

The project-local `Carrier` library has reproducible SSW connector and module
templates. It does not assign them to the frozen schematic during this
mechanical-audit stage.
