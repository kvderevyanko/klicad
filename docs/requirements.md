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
