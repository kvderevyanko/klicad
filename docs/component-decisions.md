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
