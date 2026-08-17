# Предлагаемая архитектура

Статус: предварительная архитектура. Она задаёт границы блоков, но не является
разрешением на создание схемы. Все линии с `TBD` требуют подтверждения.

```text
USB-C receptacle (sink-only, 5 V)
  |
  +-- CC / ESD / input protection / filtering                     [TBD]
  |
  +-- protected 5 V ------------------------------------+---------+-- [TBD]
                                                   |     |
                                                   |     +--> E220_VCC
                                                   |            (5 V or 3.3 V TBD by exact E220 datasheet)
                                                   |
                                                   +--> 5 V -> 3.3 V regulator [TBD]
                                                              |
                                                              +--> ESP32-WROOM-32E
                                                              |      |
                                                              |      +--> E220 UART/control connector
                                                              |      |     TXD/RXD/M0/M1/AUX; pin order TBD
                                                              |      +--> OLED I2C connector: SDA/SCL; module TBD
                                                              |      +--> WS2812 DATA; LED supply/level handling TBD
                                                              |      +--> UART0 + EN + GPIO0 programming/debug
                                                              |
                                                              +--> OLED/logic only if their exact ratings allow
```

## Проверка корректности архитектуры

1. Разделение 5 V входа, 3.3 V rail ESP32 и условной `E220_VCC` — корректная
   отправная точка. Оно предотвращает неявное предположение, что любой E220
   питается от 3.3 V.
2. Напрямую соединять `E220_VCC` с любой из шин пока нельзя. Официальные
   страницы различных E220 демонстрируют разные variant/package/radio
   attributes; конкретный E220 datasheet определит напряжение и peak current.
3. Общая цифровая земля для MCU и внешнего E220 нужна, но placement должен
   исключить разрыв return paths и не нарушить antenna keepout ESP32/E220.
4. `GPIO15 -> E220 RXD` архитектурно рискован из-за boot strapping. Нельзя
   рассчитывать на high impedance RXD или на pull state M0/M1 без datasheet.
   До схемы требуется либо доказать безопасный startup level по документации
   выбранного E220, либо согласовать перенос TX на другой GPIO (кандидат:
   GPIO16; подтверждается вместе с точным ESP32 order code).
5. Интерфейс прошивки отделён от USB-C: power-only USB-C не предоставляет
   USB-to-UART. Нужен отдельный engineering decision о header или bridge.
6. WS2812 нельзя автоматически запитать от 5 V и считать 3.3 V GPIO valid.
   Питание LED, required VIH и необходимость level shifter определяются
   официальным datasheet точной LED версии.

## Границы верификации следующего этапа

До schematic для каждого блока будут зафиксированы: точная part number,
официальный datasheet/revision, рабочий диапазон, absolute maximum, peak/worst
current, logic thresholds, required external circuitry, package и land pattern.
После этого отдельно выполняются electrical review схемы, ERC и только затем
placement PCB/DRC. Успешная проверка формата файла не заменяет ни одну из этих
проверок.

## Последовательность проектирования после снятия блокеров

1. Утвердить E220 exact model, регион/частоту/антенну и firmware/debug strategy.
2. Составить worst-case power budget и выбрать verified regulator/protection/
   USB-C connector/OLED/LED.
3. Сверить GPIO, boot/reset и level compatibility с финальными datasheets.
4. Создать schematic, провести electrical review и ERC.
5. Назначить подтверждённые footprint'ы; затем выполнить RF-aware placement,
   routing и DRC.
6. Отдельно провести engineering/manufacturability review. Производственные
   файлы выпускаются только по отдельному запросу.
