# Открытые инженерные вопросы

## Stage 1 history — BLOCKER (superseded where noted below)

1. **Какова точная модель EBYTE E220?** Нужны complete order code, datasheet
   revision и источник поставки. Без них неизвестны VCC, peak TX current, UART
   logic levels, M0/M1/AUX behaviour, pinout, габариты, antenna connection и
   механика/footprint разъёма. Не использовать условные T22D/T30D параметры.
2. **В каком регионе и в каком диапазоне/мощности работает LoRa?** Это
   определяет допустимую E220 variant, антенну, выходную мощность и RF layout.
3. **Какой тип E220 connection нужен?** Внешний DIP-модуль через socket,
   SMD-модуль через mating board, кабель или иной assembly. Нужны mating
   connector part number, keying, высота и правила крепления.
4. **Какой способ programming/debug требуется?** Выбрать: внешний 3.3 V
   USB-UART adapter/header или установленный bridge. Для каждой альтернативы
   нужны connector, pinout и boot/reset strategy.
5. **Подтверждается ли безопасный power-up level GPIO15 при соединении с E220
   RXD?** Иначе нужно формально утвердить перенос ESP32 TX на GPIO16 либо иной
   проверенный GPIO; менять GPIO молча нельзя.

## Stage 1 history — IMPORTANT

1. Точный ESP32-WROOM-32E order code (N4/N8/N16/R2, temperature grade),
   подтверждённый источник поставки и применяемый datasheet revision.
2. Worst-case power budget: ESP32 radio mode/duty cycle, OLED current,
   WS2812 brightness/current и E220 TX/RX peaks. Он определяет regulator,
   входную защиту, USB current requirement, тепловой запас и trace widths.
3. USB-C receptacle part number, sink-only current target, ESD/protection
   strategy и cable/environment assumptions. USB data не заявлены; не добавлять
   D+/D- или USB-UART без решения.
4. Точный OLED module: voltage, current, I2C address, external/integrated
   pull-ups, connector/pin order, board dimensions and mounting.
5. Точный WS2812-compatible LED: package, supply range, VIH/VIL, decoupling,
   data reset-state behavior и необходимость level shift.
6. E220 RF/antenna details: band, antenna type/gain, connector, cable, keepout,
   ground and placement restrictions из official EBYTE datasheet.
7. Габариты PCB, mounting holes, enclosure, connector access directions,
   installation environment and fabrication capability/stackup.
8. Требуемые test points и способ тестирования на производстве/в поле.

## OPTIONAL — улучшения, не требующие остановки требований

1. Возможность отключать питание E220 отдельным load switch, если она нужна по
   режимам эксплуатации; нельзя выбирать switch без peak current E220.
2. ESD-защита пользовательских внешних разъёмов и требуемый уровень
   испытаний/среды.
3. JTAG, additional LEDs, кнопки, serial logging, измерение входного напряжения
   и токовый мониторинг.
4. 4-layer PCB как вариант, если 2-layer не сможет обеспечить RF keepout,
   return paths, токовые петли и routing без компромиссов.

## Stage 2 — закрытые блокеры

1. **E220 model:** `E220-900T22D` is selected and verified using the official
   EBYTE product page/manual: pinout, VCC/logic/current, dimensions, 2.54 mm
   DIP, SMA-K/50 ohm and antenna guidance are now known.
2. **GPIO15 boot conflict:** resolved by changing the E220 RXD connection to
   ESP32 GPIO16. This is safe only with the selected `ESP32-WROOM-32E-N4`
   non-PSRAM module; the previous GPIO15 mapping must not reappear.
3. **Baseline regulator/boot/level-shift strategy:** TPS62162DSGR,
   ESP32 EN/GPIO0 manual circuit, and SN74AHCT1G125 are documented in
   `requirements.md` and `component-decisions.md`.

## Current BLOCKER — do not create the complete schematic yet

1. Region, legal channel/maximum transmit power, exact 868/915 MHz antenna and
   final enclosure arrangement for E220-900T22D are unselected.
2. Exact OLED module and WS2812-compatible LED are unknown; without their
   official datasheets, connector pinout, ratings and footprints cannot be
   guessed.
3. USB-C receptacle and 2.54 mm E220 mating socket part numbers/footprints are
   not selected. EBYTE's official `Pcb_lib` is available but has not been
   audited; no manual E220 footprint may be substituted.
4. A final worst-case power budget and USB-C source-current contract are absent.
   Passive Rd is sink attach only: it neither negotiates PD nor proves that a
   connected source can supply the final load. Decide whether input current
   detection/limiting is required.
