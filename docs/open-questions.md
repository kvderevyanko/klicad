# Открытые инженерные вопросы

## BLOCKER — нельзя безопасно проектировать schematic

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

## IMPORTANT — schematic возможна только после своевременного решения; PCB без этого не начинать

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
