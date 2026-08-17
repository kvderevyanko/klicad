# Требования: наземный LoRa-приёмник

Статус: этап требований. Этот документ не является схемой и не фиксирует
непроверенные номиналы, footprint'ы или электрические параметры.

## Назначение

Устройство — изготовляемая печатная плата наземного LoRa-приёмника. Контроллер
ESP32-WROOM-32E принимает данные от внешнего UART-модуля семейства EBYTE E220,
отображает состояние на OLED и управляет одним адресным светодиодом. USB-C
подаёт питание. Точная модель E220 на этом этапе не выбрана.

## Функциональные блоки

- ESP32-WROOM-32E (Wi-Fi/Bluetooth MCU-модуль с PCB-антенной).
- Внешний UART LoRa-модуль EBYTE E220 через отдельный разъём на основной PCB.
- OLED 0.96 inch с контроллером SSD1306 по I2C, через отдельный разъём.
- Один WS2812-совместимый статусный LED.
- USB-C только для приёма питания; передача USB-данных не требуется этим ТЗ.
- Входная защита/фильтрация питания и преобразование 5 V в 3.3 V.
- BOOT (GPIO0) и RESET/EN, интерфейс прошивки/отладки, тестовые точки.

## Исходное назначение GPIO

| Сигнал | ESP32 GPIO | Статус инженерной проверки |
| --- | ---: | --- |
| E220 TXD -> ESP32 RX | GPIO17 | Допустимый кандидат; окончательно проверить по выбранному ESP32 order code и E220 datasheet. |
| ESP32 TX -> E220 RXD | GPIO15 | **Проблема:** GPIO15 (MTDO) — strapping pin. Не фиксировать в схеме до проверки уровня E220 RXD во время reset. Предпочтительный кандидат для замены — GPIO16, если он свободен после выбора точного ESP32 order code и интерфейса отладки. |
| E220 M0 | GPIO26 | Допустимый кандидат, не strapping pin. Подтвердить electrical level и power-up requirement E220. |
| E220 M1 | GPIO27 | Допустимый кандидат, не strapping pin. Подтвердить electrical level и power-up requirement E220. |
| E220 AUX -> ESP32 | GPIO25 | Допустимый кандидат, не strapping pin. Подтвердить output type/level E220 и необходимость pull resistor. |
| OLED SDA | GPIO21 | Допустимый кандидат для I2C; pull-up и напряжение зависят от точного OLED-модуля. |
| OLED SCL | GPIO22 | Допустимый кандидат для I2C; pull-up и напряжение зависят от точного OLED-модуля. |
| WS2812 DATA | GPIO4 | Не strapping pin. Проверить состояние при reset и совместимость уровней с точной версией WS2812. |

GPIO0, GPIO2, GPIO5, GPIO12 (MTDI) и GPIO15 (MTDO) — strapping pins
ESP32. Espressif требует учитывать их уровни при включении; GPIO0 должен иметь
pull-up и не должен иметь большой конденсатор. GPIO6…GPIO11 заняты flash и не
могут использоваться. Поэтому GPIO15 как UART TX к внешнему неизвестному
модулю — риск: до подтверждения входной схемы E220 он может исказить sampled
strap level. Никакая замена GPIO не выполняется без отдельного решения.

## Питание

- Вход: USB-C VBUS, номинально 5 V в режиме sink-only. Полная USB-C
  реализация, выбранный receptacle, CC-цепи, допустимый ток, защита и ESD
  должны быть определены по официальной документации выбранных компонентов и
  применимой USB Type-C specification.
- ESP32: отдельная регулируемая шина 3.3 V. Официальный datasheet
  ESP32-WROOM-32E задаёт диапазон питания 3.0…3.6 V. Регулятор и его тепловой
  запас будут выбраны после расчёта худшего случая ESP32 и конечной E220.
- E220: отдельная шина `E220_VCC` предусматривается архитектурно, но её
  напряжение, источник (5 V или 3.3 V), пиковый ток, фильтрация и локальная
  развязка **не определены** до точной модели/официального datasheet EBYTE.
  `E220_VCC` нельзя соединять с 3.3 V или VBUS на схеме на этом этапе.
- Общая земля нужна для цифрового UART/control-интерфейса; её возвратный путь,
  питание и RF-размещение будут проверяться при placement PCB.

## Интерфейсы и внешние подключения

- E220: разъём внешнего модуля должен нести только подтверждённые для выбранной
  модели питание, GND, TXD, RXD, M0, M1 и AUX. Число контактов, их порядок,
  шаг, keying, допустимый ток и механика не определены; распиновка разъёма не
  должна быть угадана.
- OLED: I2C SDA/SCL, питание и GND. Точный дисплейный модуль, его разъём,
  напряжение питания, встроенные pull-up и адрес ещё не известны.
- Программирование/debug: ESP32 ROM download использует UART0 (U0TXD/GPIO1 и
  U0RXD/GPIO3). Базовый вариант — отдельный 3.3 V TTL programming/debug header
  плюс BOOT/EN; выбор connector, автоматического reset/boot или встроенного
  USB-UART bridge пока не сделан.
- Пользовательские внешние разъёмы, габариты платы, крепёж и enclosure не
  заданы.

## Требования к PCB и RF

- Целевая плата — 2-layer только при условии, что после placement/routing будут
  сохранены непрерывные ground return paths и требования RF; число слоёв пока
  не фиксируется.
- Для ESP32-WROOM-32E обязателен antenna keepout и placement строго по разделу
  *PCB Layout Recommendations* официального datasheet. Численные границы
  keepout будут перенесены в PCB только из актуальной figure datasheet, а не
  оценены вручную.
- Антенна E220, диапазон частот, тип подключения (например, встроенный,
  SMA/IPEX/провод) и требования keepout неизвестны. Они блокируют RF placement
  и выпуск платы.
- Не вести сигналы/медь под keepout антенны, отделять E220 RF и ESP32 antenna
  от DC/DC и высокотоковых петель, предусмотреть ground plane и короткие цепи
  decoupling после выбора компонентов.

## Требования к BOOT/RESET и тестированию

- Нужны управляемые/доступные BOOT (GPIO0) и RESET/EN с цепями, проверенными по
  ESP32 Hardware Design Guidelines. Не подменять это только software reset.
- Перед schematic необходимо выбрать способ прошивки: внешний USB-UART header
  или установленный USB-UART bridge; USB-C в данном ТЗ сам по себе не означает
  USB programming.
- Предусмотреть доступные тестовые точки как минимум для GND, USB 5 V после
  входной защиты, 3.3 V, `E220_VCC` (после выбора), EN, GPIO0, UART0 TX/RX и
  E220 UART/control-сигналов, если это не конфликтует с RF/механикой.

## Ограничения и неизвестные параметры

- Точная E220 модель — блокирующая неизвестность: частотный диапазон, мощность,
  напряжение VCC, current peaks, UART/control logic levels, pinout, размеры,
  antenna interface и footprint/разъём неизвестны.
- Не выбраны regulator, USB-C receptacle, input protection/ESD, OLED module,
  WS2812 variant, programming/debug method и механические ограничения.
- Нет power budget, режима Wi-Fi/Bluetooth ESP32, duty cycle LoRa, требований
  по температуре, региону использования/радиорегуляторике и требуемой мощности
  E220.

## Проверенные первичные источники

- [ESP32-WROOM-32E & ESP32-WROOM-32UE Datasheet v2.1, Espressif](https://documentation.espressif.com/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf): ESP32-WROOM-32E, питание 3.0…3.6 V, pin definitions, boot configurations, current table, land pattern и placement/antenna рекомендации.
- [ESP32 Hardware Design Guidelines — Schematic Checklist, Espressif](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html): strapping, reset/boot, GPIO и schematic review requirements.
- [ESP-IDF GPIO & RTC GPIO, Espressif](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/gpio.html): список strapping pins и ограничения GPIO.
- [E220-400T22D, официальный каталог EBYTE](https://www.cdebyte.com/products/E220-400T22D/4) и [E220-900T30D, официальный каталог EBYTE](https://www.cdebyte.com/products/E220-900T30D/2): использованы только как подтверждение того, что внутри семейства E220 различаются диапазон, мощность, размеры и исполнение. Их параметры **не применяются** к этому устройству до выбора модели.

## Stage 2 — подтверждённые требования и замены Stage 1

Этот раздел имеет приоритет над исходными открытыми вопросами выше и сохраняет
историю принятых решений.

### Выбранные модули и GPIO

- MCU: `ESP32-WROOM-32E-N4` — 4 MB Quad-SPI flash, без PSRAM, диапазон
  -40…85 °C. Это именно non-PSRAM variant: ESP32-WROOM-32E datasheet указывает,
  что в R2 variants GPIO16 подключён к embedded PSRAM и недоступен.
- LoRa: внешний `E220-900T22D`, DIP 21 × 36 mm, 2.54 mm pin header, SMA-K
  antenna interface около 50 ohm, band 850.125…930.125 MHz, rated 22 dBm.
- `E220 TXD -> GPIO17`, `GPIO16 -> E220 RXD`, `GPIO26 -> M0`,
  `GPIO27 -> M1`, `E220 AUX -> GPIO25`. Это документированная замена исходной
  линии GPIO15: GPIO15/MTDO — strapping pin, а GPIO16/17 доступны у выбранного
  N4 (module pins 27/28); UART signal can be assigned via GPIO Matrix.
- E220 header: pin 1 M0, 2 M1, 3 RXD, 4 TXD, 5 AUX, 6 VCC, 7 GND. M0/M1 имеют
  very-weak pull-up и не могут оставаться floating; AUX — status/self-test
  output, low during self-test.

### Питание, USB-C и уровни

- `E220_VCC = protected 5.0 V`. Official EBYTE electrical table sets 2.7…5.5 V
  and 3.3 V communication level; its pin-definition table sets 3.0…5.5 V. To
  avoid relying on the conflicting lower bound, use 5.0 V nominal; full output
  power is guaranteed at >=5 V and VCC must never exceed 5.5 V. Current table:
  TX 110 mA momentary, RX 8 mA, sleep 3 µA. The E220 digital lines are 3.3 V,
  therefore direct ESP32 UART/control logic is intended; 5 V TTL is prohibited.
- 3.3 V rail: `TPS62162DSGR` fixed 3.3 V synchronous buck (TI), VIN 3…17 V,
  up to 1 A. Reference values: 2.2 µH inductor, 10 µF ceramic input capacitor,
  22 µF ceramic X5R/X7R output capacitor; fixed-version FB to AGND and exposed
  pad to AGND. This meets Espressif's no-less-than-500-mA recommendation but
  does not replace a final system power budget.
- USB-C remains sink-only/default 5 V, no PD and no data: use a 5.1 kOhm Rd
  resistor from each of CC1 and CC2 to GND; `TPD4S311` protects CC pins and
  `TPD1E10B06` protects VBUS. The latter is a 5.5 V VRWM device and must not be
  used for any USB-PD voltage. Exact receptacle, source-current contract and
  overcurrent protection remain unresolved.
- For a 5 V WS2812, the selected one-way level shifter is
  `SN74AHCT1G125DBVR` powered by 5 V: GPIO4 -> A, Y -> DIN, OE tied low and
  0.1 µF VCC bypass placed at the IC. Its VIH(max)=2.0 V at VCC=4.5…5.5 V, so
  ESP32 3.3 V high is valid. Exact LED still requires its official datasheet.

### BOOT/RESET and programming

- Selected manual baseline: UART0 external 3.3 V TTL programming/debug header,
  not USB-C data or an onboard USB-UART bridge.
- EN: 10 kOhm pull-up to 3.3 V, 1 µF to GND, normally-open RESET switch to GND.
  Espressif specifies EN/CHIP_PU must not float, recommends this RC, and states
  50 µs minimum stabilisation and reset-low timing.
- GPIO0: 10 kOhm pull-up to 3.3 V and normally-open BOOT switch to GND; do not
  add a high-value capacitor. GPIO0=0 with GPIO2=0 selects UART download mode.

### Stage 2 official sources

- [ESP32-WROOM-32E & ESP32-WROOM-32UE Datasheet v2.1, Espressif](https://documentation.espressif.com/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf): N4/non-PSRAM ordering, GPIO16/17 mapping, strapping and module pin table.
- [ESP32 Hardware Design Guidelines, Espressif](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html): 500 mA supply recommendation, EN 10 kOhm/1 µF, GPIO0 and UART guidance.
- [E220-900T22D product page, EBYTE](https://www.cdebyte.com/products/E220-900T22D/4) and [official E220-xxxTxxx manual, EBYTE](https://www.cdebyte.com/pdf-down.aspx?id=3552): pinout, electrical/current table, dimensions, 2.54 mm DIP and SMA-K/50 ohm interface.
- [TPS62162 datasheet, TI](https://www.ti.com/lit/ds/symlink/tps62162.pdf): 3.3 V/1 A buck and reference L/C values.
- [SN74AHCT1G125 datasheet, TI](https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf): 5 V AHCT level shifting and bypass guidance.
- [USB Type-C specification, USB-IF](https://usb.org/usb-type-cr-cable-and-connector-specification), [TUSB320 datasheet, TI](https://www.ti.com/lit/ds/symlink/tusb320.pdf), [TPD4S311, TI](https://www.ti.com/product/TPD4S311), and [TPD1E10B06, TI](https://www.ti.com/lit/ds/symlink/tpd1e10b06.pdf): sink Rd and selected ESD protection.

## Stage 2.1 — WS2812B selection and bounded power budget

This section supersedes the previous “exact WS2812 unknown” status. It is a
component-verification record, not permission to create a schematic or a PCB.

### Status LED

- Selected LED: `WS2812B-V5` from WorldSemi. The manufacturer document calls it
  a four-pin, top-SMD 5050 intelligent RGB LED: `VDD`, `DOUT`, `VSS`, `DIN`.
  Its package outline is 5.0 × 5.4 × 1.57 mm. The authoritative document is
  [WS2812B-V5, WorldSemi](https://www.world-semi.co.kr/_files/ugd/89cd03_1023b0e9d135431aa1e6491bfc318112.pdf);
  the document itself identifies WorldSemi and `world-semi.com`. Procurement
  must require this exact orderable part/datasheet revision — a marketplace
  listing merely named “WS2812B” is not equivalent.
- Rail: protected 5.0 V. The data sheet gives its electrical data at 5 V and
  lists 3.7…5.3 V under **absolute maximum ratings**, not as a recommended
  operating range. Therefore this project does not infer a broader allowable
  rail range from that table; it requires a regulated 5.0 V nominal rail and a
  revision check before purchase.
- Logic: `DIN` requires `VIH >= 2.7 V` and `VIL <= 0.7 V`. The existing
  `SN74AHCT1G125DBVR` at 5 V remains justified: TI guarantees `VOH >= 3.8 V`
  at 4.5 V supply and -8 mA, which exceeds the LED's 2.7 V input-high minimum.
  GPIO4 has no direct connection to the LED DIN.
- Current: WorldSemi states 12 mA in the condition column for each R/G/B LED
  characteristic and 0.6 mA working quiescent current. It does **not** publish
  a single total “maximum supply current” number. The only defensible
  full-white budget allocation from that source is `3 × 12 mA + 0.6 mA =
  36.6 mA`; it is a bounded design allocation from the documented channel
  condition, **not** a manufacturer-guaranteed absolute total maximum. Firmware
  must treat 36.6 mA as the status-LED full-white allocation until a newer
  manufacturer revision supplies an explicit total limit.
- Series resistor: the WorldSemi document specifies no DIN series-resistor
  value. No resistor value or resistor footprint is selected; one must not be
  invented. It may be evaluated after the exact layout/trace is known as a
  signal-integrity/EMC decision.
- Local bypass: the WorldSemi typical application explicitly says the peripheral
  circuit does not need a filter capacitor. It gives no local-bypass value, so
  no LED-local capacitor or capacitor footprint is claimed as a manufacturer
  requirement. This does not remove the separately selected 0.1 uF bypass at
  the AHCT IC or the regulator output capacitors.
- Footprint status: **not assigned**. The installed generic KiCad WS2812B
  footprint has not been verified against this V5 package or a
  manufacturer-recommended land pattern; the cited document supplies package
  dimensions but no verified PCB land pattern. A footprint must be verified
  before the PCB stage; no manual substitute is approved now.

### Explicit power budget — current information only

All rows below can occur concurrently unless firmware/hardware deliberately
proves otherwise. `TBD` is deliberately not replaced by an estimate.

| Rail | Consumer / condition | Official source value | Budget value used | Status |
| --- | --- | ---: | ---: | --- |
| 3.3 V | ESP32-WROOM-32E-N4, Wi-Fi TX 802.11b 20 MHz, 1 Mbps, 19.5 dBm | 379 mA peak (239 mA average), at 3.3 V / 25 °C / 100% TX duty | **500 mA** bounded rail allocation | Espressif's tested peak is 379 mA; 500 mA is the separate Espressif supply-capability recommendation, hence a conservative allocation rather than a claim of measured absolute maximum. |
| 3.3 V | OLED module | unknown — module/rail/current not selected | `I_OLED = TBD` | No numerical allocation is permitted until the exact module datasheet is selected. |
| 5.0 V | E220-900T22D TX | 110 mA momentary | **110 mA** | Selected EBYTE module, full-power rail. |
| 5.0 V | WS2812B-V5, full white | no explicit total maximum; 12 mA per R/G/B condition plus 0.6 mA working quiescent | **36.6 mA** | Bounded allocation, not a guaranteed total-Imax specification. |
| 5.0 V | SN74AHCT1G125, one input near 3.4 V | 1.5 mA max `ΔICC`; 10 uA max static `ICC` | **1.51 mA** | Conservative static-plus-`ΔICC` data-sheet allocation; dynamic LED-data switching is not separately guaranteed there. |
| 5.0 V | TPS62162 input for the 3.3 V allocation | no guaranteed conversion-efficiency/current figure selected for this exact operating point | **at least 330 mA ideal**, plus `0.66 × I_OLED` ideal | Energy lower bound only: `(3.3 V / 5.0 V) × (500 mA + I_OLED)`. A real converter draws more because efficiency is below 100%. |

Consequences, stated without an assumed efficiency:

- The known direct 5 V consumers total **148.11 mA**. With only the ESP32
  500 mA allocation and an ideal converter, the protected-5-V load is already
  **at least 478.11 mA** (`110 + 36.6 + 1.51 + 330` mA), before OLED current,
  converter losses, connector/ESD losses and other auxiliaries. The real value
  is higher.
- `TPS62162DSGR` is a 1 A, 3.3 V buck. It supports the current known 500 mA
  ESP32 allocation with a nominal **less than 500 mA** remaining output budget,
  but it is **not yet demonstrated adequate** for `500 mA + I_OLED + all
  remaining 3.3 V loads`, transient response and thermal conditions. OLED
  selection and a regulator/layout thermal review remain required.
- The 5 V topology meets the selected **voltage** requirements for E220, AHCT
  and WS2812B-V5. It does **not** yet meet a proven USB-C **source-current**
  requirement: a passive Rd sink does not negotiate a guaranteed current, and a
  nominal 500 mA source leaves only 21.89 mA above the ideal lower bound before
  losses/OLED. Do not release a schematic until the receptacle/source-current
  contract, protection/fuse strategy and current limit are selected against the
  final budget.

Additional Stage 2.1 official sources:

- [ESP32-WROOM-32E & ESP32-WROOM-32UE Datasheet v2.1, table 16, Espressif](https://documentation.espressif.com/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf): 379 mA peak for the cited Wi-Fi TX condition; the measurements are at 3.3 V and 25 °C.
- [ESP32 Hardware Design Guidelines — schematic checklist, Espressif](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32/schematic-checklist.html): recommends a 3.3 V supply capable of no less than 500 mA.
- [WS2812B-V5 manufacturer document, WorldSemi](https://www.world-semi.co.kr/_files/ugd/89cd03_1023b0e9d135431aa1e6491bfc318112.pdf) and [WorldSemi WS2812 family catalogue](https://world-semi.com/ws2812-family/): package/pins, 5 V electrical conditions, logic thresholds, 12 mA × 3 family current and the no-filter-capacitor statement.
- [SN74AHCT1G125 datasheet, TI](https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf): 5 V operating range, `VOH`, `ΔICC`, static `ICC` and 0.1 uF IC bypass recommendation.

## Stage 3.1 — resolved electrical decisions and final allocation

### Decision status

The labels used below deliberately distinguish **manufacturer requirement**,
**calculated engineering requirement**, **conservative allocation**, and
**PROJECT DESIGN CHOICE**.  A project choice is not disguised as a data-sheet
requirement.  Missing breakout-module and PCB land-pattern information is an
important PCB-release issue, not a reason to guess it or to prevent a
configurable schematic interface.

### USB-C and 5-V system rail

- **Selected receptacle:** GCT `USB4105-GF-A`.  Its official drawing identifies
  the four VBUS and GND contacts, CC1/CC2 and the manufacturer recommended PCB
  layout; VBUS contact rating is 5.00 A.  This is a power-only interface:
  D+/D- and SBU are intentionally NC.
- **Selected Type-C controller:** TI `TUSB320LAIRWBR`, configured as UFP with
  `PORT=GND`, `EN_N=GND`, `ADDR=NC`.  **Manufacturer requirements:** it uses
  internal Rd, needs a 900-kOhm ±1-% `VBUS_DET` connection to VBUS and 1…10-uF
  UFP bulk capacitance (1 uF in TI's example).  The earlier discrete 5.1-kOhm
  Rd concept is superseded; it must not coexist with the controller.
- **PROJECT DESIGN CHOICE:** the eFuse is enabled whenever valid VBUS is
  present (`EN` tied to its input), so ESP32 can boot and read Type-C status;
  do **not** gate the complete ESP supply on `OUT1`.  TI documents UFP GPIO
  states as `OUT1/OUT2 = H/L` for Default, `L/H` for Medium (1.5 A), `L/L` for
  High (3 A), and `H/H` when unattached.  Both outputs are open drain.  Pull
  each output to VBUS and feed ESP32 through a 12-kOhm/20-kOhm divider: 5.25 V
  becomes 3.28 V.  Assign OUT1 to GPIO32 and OUT2 to GPIO33; neither is a
  strapping pin.  Firmware must hold E220 asleep/off, keep the LED dark and
  avoid Wi-Fi TX until those pins are read.  Default current is thus a
  constrained diagnostic/boot mode, not normal receiver operation.  This is
  current detection, not USB-PD negotiation.
- **Selected eFuse:** TI `TPS259630DDAR` and Panasonic `ERA3AEB9090V` (909 Ohm,
  0.1 %, 0.1 W).  TI characterises that resistor setting as 1.005-A typical and
  0.949…1.051-A current limit.  `TPS259630` is the selected latch-off protected
  `5V_SYS` switch.  Its adjustable OVLO is not claimed to be a precision E220
  5.5-V clamp.  The supported 4.75…5.25-V receptacle input is a **PROJECT
  DESIGN REQUIREMENT** to be tested with the final source/cable.
- `TPD1E10B06DPYR` (VBUS) and `TPD4S311DRYR` (CC) remain selected ESD devices;
  they are not DC voltage regulators or eFuse substitutes.

### Buck, E220 and OLED interface

- **Manufacturer/EVM basis:** TI `TPS62162DSGR` is the selected fixed 3.3-V,
  1-A buck.  The TPS621x0 EVM validates the 2.2-uH / 10-uF input / 22-uF output
  topology; it does not make its obsolete EVM inductor a current procurement
  choice.
- **Selected parts / manufacturer ratings:** TDK `VLS3012CX-2R2M-1` is 2.2 uH
  ±20 %, 1.70-A saturation-current rating (30-% inductance drop), 2.55-A
  temperature-rise rating and 74-mOhm maximum DCR.  Murata
  `GRM21BR61E106KA73` is 10 uF ±10 %, 25 V X5R 0805 (`CIN`); Murata
  `GRM21BR61A226ME44` is 22 uF ±20 %, 10 V X5R 0805 (`COUT`).  These are
  **PROJECT DESIGN CHOICES** backed by manufacturer ratings.  Their exact land
  patterns are to be taken from manufacturers at PCB stage.
- **E220:** EBYTE publishes VCC/current but does not prescribe a local capacitor
  value in the selected manual.  The explicit **PROJECT DESIGN CHOICE** is
  `GRM188R61A106MAAL` (10 uF, 10 V X5R) plus `GRM188R71C104KA01D` (0.1 uF,
  16 V X7R) between E220 VCC/GND, positioned locally in later placement.  It
  needs TX-burst measurement; it is not called an EBYTE requirement.
- **OLED:** connector contract is now `GND, 3V3, SDA, SCL`, 3.3-V only, with a
  100-mA **PROJECT DESIGN ALLOCATION**.  SDA/SCL each have a configurable
  4.7-kOhm, 1-% population site to 3V3: fit it or DNP it after checking the
  real module's pull-ups.  Calculated two-line-low current is 1.404 mA.

### Power budget

| Item | Value | Classification |
| --- | ---: | --- |
| ESP32 3V3 | 500.000 mA | Conservative allocation; Espressif RF table's cited peak is 379 mA while its supply guidance requires at least 500 mA capability. |
| OLED connector 3V3 | 100.000 mA | PROJECT DESIGN allocation, not an assertion about an unknown breakout. |
| I2C pulls, both low | 1.404 mA | Calculated: `2 × 3.3 V / 4.7 kOhm`. |
| 3V3 active subtotal | 601.404 mA | Calculated. |
| 3V3 design allocation | 721.685 mA | Conservative allocation: active subtotal plus 20 % margin. |
| E220 5V TX | 110.000 mA | EBYTE manufacturer value. |
| WS2812B-V5 5V | 36.600 mA | Bounded allocation from documented `3 × 12 mA + 0.6 mA`. |
| AHCT 5V | 1.510 mA | Conservative TI static plus `ΔICC` allocation. |
| TUSB320 / status dividers | 0.398 mA | Typical controller plus calculated two `5.25 V / (12 kOhm + 20 kOhm)` divider currents. |

**Calculated engineering check:** `P_3V3 = 3.3 × 0.721685 = 2.382 W`.  The
85-% converter efficiency used here is a conservative **PROJECT DESIGN
ALLOCATION**, not a TPS62162 guaranteed efficiency point.  It gives 560.5 mA
buck input at 5.0 V, or 590.0 mA at 4.75 V.  Thus `5V_SYS` needs 708.6 mA at
5.0 V (`560.5 + 110 + 36.6 + 1.51`) and 738.0 mA at 4.75 V.  This is below
TPS259630's 0.949-A minimum characterised limit by at least 211 mA, and the
3V3 allocation is 278 mA below TPS62162's 1-A rating.  Both margins require
prototype transient/thermal validation.  An OLED exceeding 100 mA restarts
this review.

Stage 3.1 primary sources: [USB4105 drawing, GCT](https://gct.co/files/drawings/usb4105.pdf), [USB4105, GCT](https://gct.co/connector/usb4105), [TUSB320LAI, TI](https://www.ti.com/lit/ds/symlink/tusb320lai.pdf), [TPS2596, TI](https://www.ti.com/lit/ds/symlink/tps2596.pdf), [TPS621x0 EVM, TI](https://www.ti.com/lit/ug/slvu483a/slvu483a.pdf), [TDK VLS3012CX-2R2M-1](https://product.tdk.com/en/search/inductor/inductor/automotive-inductor/info?part_no=VLS3012CX-2R2M-1), [Murata GRM21BR61E106KA73](https://search.murata.com/en-US/partdetail?partno=GRM21BR61E106KA73), [Murata GRM21BR61A226ME44](https://search.murata.com/en-US/partdetail?partno=GRM21BR61A226ME44), [Murata GRM188R61A106MAAL](https://search.murata.com/en-US/partdetail?partno=GRM188R61A106MAAL), [Murata GRM188R71C104KA01D](https://search.murata.com/en-US/partdetail?partno=GRM188R71C104KA01D), and [SN74AHCT1G04, TI](https://www.ti.com/lit/ds/symlink/sn74ahct1g04.pdf).
