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
