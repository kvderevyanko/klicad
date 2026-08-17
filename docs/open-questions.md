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
2. Exact OLED module is unknown; without its official datasheet, connector
   pinout, ratings and footprint cannot be guessed. `WS2812B-V5` is now
   electrically selected, but its manufacturer-verified PCB land pattern is
   still absent.
3. USB-C receptacle and 2.54 mm E220 mating socket part numbers/footprints are
   not selected. EBYTE's official `Pcb_lib` is available but has not been
   audited; no manual E220 footprint may be substituted.
4. A final worst-case power budget and USB-C source-current contract are absent.
   Passive Rd is sink attach only: it neither negotiates PD nor proves that a
   connected source can supply the final load. Decide whether input current
   detection/limiting is required.

## Stage 2.1 — status LED closed; remaining IMPORTANT items

1. **Resolved — status LED electrical identity:** `WS2812B-V5` has a
   manufacturer document for its four-pin 5050 package, 5 V conditions,
   `VIH`/`VIL` and current basis. The 5 V AHCT translator is retained. This
   closes the former “exact WS2812 unknown” electrical blocker.
2. **IMPORTANT — WS2812B-V5 footprint:** the manufacturer document does not
   provide a verified land pattern and the installed generic KiCad footprint has
   not been compared to it. No footprint is assigned. Confirm an exact official
   land pattern or a manufacturer-approved package drawing before PCB placement.
3. **BLOCKER — OLED and final 3.3 V budget:** `I_OLED` is explicitly unknown.
   A 1 A regulator cannot be approved until its module, voltage/pull-ups and
   current are documented and added to the 500 mA ESP32 allocation.
4. **BLOCKER — USB-C source-current / input protection:** the known 5 V load
   has an ideal lower bound of 478.11 mA before OLED and conversion losses.
   Select the receptacle, guaranteed source-current design target, fuse/eFuse or
   other overcurrent method, and verify the final value. Passive Rd alone is not
   a current contract.
5. **IMPORTANT — LED current interpretation:** WorldSemi gives 12 mA per colour
   condition and 0.6 mA working quiescent current but no total maximum supply
   current. The documented 36.6 mA is an allocation, not an absolute maximum;
   re-check the manufacturer document revision before production release.

## Stage 3 gate review — schematic decision

**Decision: do not create `.kicad_pro` or `.kicad_sch` yet.** The following
are genuine electrical-schematic blockers, not merely deferred footprint or
layout work:

1. **OLED interface is electrically undefined.** The exact 0.96-inch SSD1306
   module has no verified manufacturer document for VCC range, maximum current,
   connector pin order and whether SDA/SCL pull-ups are fitted and to which
   rail. A generic four-pin connector would guess at least its pin order and
   pull-up arrangement, while `I_OLED` prevents approval of the 3.3 V budget.
2. **USB-C input power path is incomplete.** `CC` Rd and the two ESD parts do
   not select the receptacle, input-current contract, overcurrent/reverse-power
   protection or a current-limiting component. The known ideal protected-5-V
   lower bound is already 478.11 mA before OLED and conversion losses, so an
   unqualified 500 mA source cannot be assumed safe. A final input chain cannot
   be drawn without these verified components/ratings.
3. **The 3.3 V rail cannot yet be approved.** `TPS62162DSGR` is a conditional
   1 A choice, but the actual OLED load, all auxiliary loads, conversion loss,
   transient requirement and thermal margin are unresolved. Its 2.2 uH
   inductor is only a reference value: no actual inductor with verified
   saturation/current rating has been selected. Drawing it as a real final
   power circuit would therefore imply unverified electrical capability.
4. **E220 local power implementation needs an explicit verified decision.**
   The selected E220-900T22D VCC/current/pinout are known, but this project has
   not yet recorded the manufacturer-required or otherwise verified local
   decoupling/filtering arrangement at its 5 V connector. Do not substitute a
   habitual capacitor value for a documented requirement.

The following remain important, but **do not by themselves block a schematic**:
the regional RF/antenna/enclosure decision, E220 mating-socket footprint,
USB-C receptacle footprint and WS2812B-V5 land pattern. They block footprint,
placement or PCB release and must be resolved before those stages.

Stage 3 environment recheck: package `kicad` is `10.0.5~ubuntu22.04.1`; both
`kicad-cli --version` and `kicad-cli version` report `10.0.5`. CLI help confirms
`kicad-cli sch erc` and `kicad-cli pcb drc` are available. Local libraries have
generic ESP32-WROOM-32, USB-C receptacle, WS2812B and test-point assets, but no
exact ESP32-WROOM-32E or E220-900T22D asset. `hardware/` contains no KiCad
project, schematic or PCB file.
