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

## Stage 2 — подтверждённая архитектура

```text
USB-C receptacle (sink-only/default 5 V; exact connector TBD)
  |
  +-- CC1 -> 5.1 kOhm Rd -> GND; CC2 -> 5.1 kOhm Rd -> GND
  |   +-- TPD4S311 protects CC1/CC2
  +-- VBUS -> TPD1E10B06 -> protected 5 V
                           |-- E220-900T22D VCC (5.0 V, 110 mA TX peak)
                           +-- TPS62162DSGR -> 3.3 V / 1 A
                               (2.2 µH, 10 µF input, 22 µF output)
                                  |-- ESP32-WROOM-32E-N4
                                  |    |-- GPIO17 <- E220 TXD; GPIO16 -> E220 RXD
                                  |    |-- GPIO26 -> M0; GPIO27 -> M1; GPIO25 <- AUX
                                  |    |-- GPIO21/22 -> OLED I2C (module TBD)
                                  |    |-- GPIO4 -> SN74AHCT1G125 (5 V) -> WS2812 DIN
                                  |    +-- UART0, manual EN/RESET and GPIO0/BOOT
                                  +-- OLED only after its 3.3 V compatibility is verified
```

The former conditional `E220_VCC` and GPIO15 risk are resolved. This does not
resolve the final power budget, USB-C source-current contract, OLED/WS2812
selection, connector footprints, regional channel/antenna, or mechanics. Those
remain blockers to a complete schematic; no `.kicad_pro`, schematic or PCB is
created at this stage.

## Stage 2.1 — verified status LED and rail sufficiency

`WS2812B-V5` is now the selected 5 V status LED, driven through the existing
5 V `SN74AHCT1G125` level shifter. Its package land pattern is still unassigned,
so this is an architectural connection only, not a PCB-ready placement.

The following is a lower-bound check, not a claim that the final USB-C input is
adequate:

```text
protected 5 V direct loads: E220 TX 110 mA + WS2812B-V5 36.6 mA
                            + AHCT allocation 1.51 mA = 148.11 mA
TPS62162 input, ideal lower bound for 3.3 V: 0.66 × (500 mA + I_OLED)
-----------------------------------------------------------------------
protected 5 V lower bound: 478.11 mA + 0.66 × I_OLED, before losses
```

The 1 A TPS62162 output is conditionally sufficient for the 500 mA ESP32 rail
allocation only; the OLED remains `TBD`, and converter thermal/transient margin
is unverified. Likewise, the protected 5 V rail supplies the correct nominal
voltages but cannot be considered USB-current compliant yet: the base ideal
lower bound is already close to 500 mA. The exact USB-C receptacle, advertised
 source-current design target and protection/current-limit device therefore stay
 as schematic blockers.

## Stage 3.1 — controlled input and boot architecture

```text
USB4105-GF-A (power-only USB-C)
  CC1/CC2 ── TPD4S311 ── TUSB320LAIRWBR (UFP / internal Rd)
  VBUS    ── TPD1E10B06 ── VBUS_PRE ── TPS259630DDAR ── 5V_SYS
                             │                 EN = VBUS_PRE
                             ├─ TUSB VDD + 1 uF
                             ├─ 900 kOhm ±1 % -> VBUS_DET
                             └─ OUT1/OUT2 -> 12k/20k dividers -> GPIO32/GPIO33
                                                            (Type-C status)

5V_SYS ── E220 VCC + 10 uF/100 nF
        ── WS2812B-V5 via 5-V SN74AHCT1G125
        ── TPS62162DSGR (2.2 uH, 10 uF CIN, 22 uF COUT) ── 3V3
                                                               ├─ ESP32
                                                               └─ 3V3 OLED port
                                                                  + I2C 4.7k/DNP
```

`OUT1/OUT2` are **telemetry inputs**, not a power-enable interlock.  Their TI
UFP truth table is: unattached `H/H`, Default `H/L`, Medium/1.5-A `L/H`, and
High/3-A `L/L`.  Since outputs are open drain and TUSB320 runs from pre-switch
VBUS, pull them to VBUS and divide to ESP32 with 12-kOhm/20-kOhm pairs, making
5.25 V into 3.28 V.  The eFuse stays enabled for ESP32 boot power. Firmware
reads status before normal operation: at Default it must remain low-load (no
Wi-Fi TX, E220 asleep/off, LED dark); Medium or High is required for the
defined full-load allocation. This is not a USB-PD negotiation guarantee.

The full-load calculation is 721.685 mA at 3V3 and 708.6 mA at `5V_SYS`
(738.0 mA with 4.75-V converter input) using a conservative 85-% efficiency
allocation. It has 211 mA margin to the TPS259630 minimum characterised limit
and 278 mA to TPS62162's rating. The small pre-eFuse controller/divider load is
additional to raw VBUS and not double-counted in `5V_SYS`.
