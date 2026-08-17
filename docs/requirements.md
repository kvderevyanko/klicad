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
