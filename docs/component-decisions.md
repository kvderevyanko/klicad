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
| Radio socket / footprint | **Unselected** | The official EBYTE download/library is evidence of a source asset, not approval for a KiCad footprint or an exact mating connector.  Select after official mechanical/pin-1/mating-socket audit at PCB stage. |
| M0/M1 reset mode | External 10-kOhm pull-down per line to GND | **PROJECT DESIGN CHOICE.** It forces documented `M1/M0=00` while GPIOs reset.  The EBYTE manual requires non-floating inputs but specifies no external resistor value. Prototype-verify GPIO high drive and mode transition. |
| E220 local bypass | `GRM188R61A106MAAL` 10 uF/10 V/X5R + `GRM188R71C104KA01D` 0.1 uF/16 V/X7R at VCC/GND | **PROJECT DESIGN CHOICE**, not claimed as an EBYTE-mandated value. Place locally after socket/mounting selection. |
| DevKit supply | `5V_SYS` to verified left-header pin 1 / VIN | 500 mA at 5 V is a conservative **PROJECT DESIGN ALLOCATION**, derived from the prior Espressif supply-capability basis; it is not a DevKit manufacturer current rating. Measure current and on-board-regulator thermal performance. |
| OLED | GPIO21/22 signal reservation only; VCC and pull-ups NC/DNP in Rev A | Exact display and its supply/current are unresolved.  Do not budget it or feed it from DevKit 3V3 until module and regulator margin are verified. |
| 5-V budget / Type-C policy | `5V_SYS` allocation 777.732 mA including 20 % margin; enable remains only at Type-C Medium/High | 648.110-mA pre-margin subtotal: DevKit 500 + E220 110 + WS 36.6 + AHCT 1.51 mA.  0.25-mA TUSB/enable allocation is pre-eFuse, giving 777.982 mA raw USB allocation and 722.018 mA to the 1.5-A policy.  Prototype validates cable/bursts/thermal. |

Official sources: [E220-T Series User Manual, EBYTE](https://www.cdebyte.com/pdf-down.aspx?id=4221), [E220-400T22D, EBYTE](https://www.cdebyte.com/products/E220-400T22D/4), [E220-900T22D, EBYTE](https://www.cdebyte.com/products/E220-900T22D/4), [TPS2596, TI](https://www.ti.com/lit/ds/symlink/tps2596.pdf), and [TUSB320LAI, TI](https://www.ti.com/lit/ds/symlink/tusb320lai.pdf).
