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
                             ├─ MMSD4148T1G -> TUSB VDD + 0.1 uF; 1 uF VBUS bulk/CIN
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

### Stage 3.1 eFuse-network correction

`TPS259630DDAR` is not connected with bare control pins.  `CIN` is the selected
1-uF/10-V/X7R `GRM188R71A105KA61D` at IN and is also the permitted UFP port
bulk capacitance.  A second part of the same PN is the explicit 1-uF local
`COUT` at 5V_SYS.  `EN/UVLO` uses a 100-kOhm `ERA3AEB104V` pull-up to IN, as
TI permits for input below 6 V; `OVLO` uses 365-kOhm `ERA3AEB3653V` from IN and
100-kOhm `ERA3AEB104V` to GND.  `dVdt` uses 3.3-nF C0G
`GRM1885C1H332JA01D`, providing controlled rather than fastest turn-on.

The nominal OVLO calculation is 5.58 V.  It cannot be represented as a
precision 5.5-V E220 clamp because TI's OVLO threshold tolerance and divider
tolerance produce a wider range; normal safety remains the declared regulated
4.75…5.25-V input constraint.  `FLT` is intentionally NC (its external pull-up
is needed only if fault telemetry is used), and no reverse-current blocking is
claimed: 5V_SYS must have no alternate source. TUSB VDD is fed through
`MMSD4148T1G` and decoupled by 0.1-uF/16-V/X7R `GRM188R71C104KA01D`; its 1-uF
requirement belongs to the UFP VBUS port, not the VDD pin. Verify the diode-fed
2.75…5.0-V VDD range over source and temperature tolerance.

## Stage 3.2 — preflight correction required before schematic

The `OUT1/OUT2 -> VBUS pull-up -> divider` branch above is **invalid** and is
kept only as decision history. The 12-kOhm resistor is not isolation for the
TUSB pin: a released open-drain output rises toward `VBUS_PRE`, while TI
documents OUT[3:1] as non-failsafe when VDD is off. It must not be copied into
a schematic.

## Stage 3.3 — active fail-safe Type-C enable path

Stage 3.2 is resolved by a VDD-domain inverter, not a VBUS divider and not
firmware. `TUSB_VDD` is diode-fed from VBUS_PRE and has its local 100-nF
capacitor. `OUT1` has only a 47-kOhm pull-up to `TUSB_VDD`; it drives an
`MMBT3904LT1G` base through 47 kOhm. The NPN emitter is GND, collector is eFuse
EN/UVLO, and EN has a 330-kOhm pull-up to `TUSB_VDD`.

```text
TUSB_VDD --47k--+-- OUT1 --47k--> Q1 base
                |                    Q1 emitter -> GND
                +-- (only TUSB domain)
TUSB_VDD --330k------------------> TPS259630 EN/UVLO
                                  ^
                                  +-- Q1 collector
```

OUT1 release (unattached/Default/reset) turns Q1 on and forces EN low; OUT1
low (Medium/High) turns Q1 off and enables eFuse. VDD absent also makes the
EN pull-up 0 V. This preserves Type-C dead-battery attach, blocks ESP32 and
all `5V_SYS` load at Default current, and removes the forbidden VBUS divider/
GPIO32/GPIO33 path.

Likewise, eFuse enable at attach does not make a Default-current source safe:
the selected 0.949-A-min limit exceeds Type-C Default 500 mA. A fully electrical
source-current/boot policy is required before the first schematic. Until an
approved replacement exists, no KiCad netlist or symbol is generated.

## Stage 4 — active architecture: removable USB-C CH340C DevKit

This is the architecture to use for the next schematic once the blocker below
is resolved.  It supersedes the preceding bare-ESP32, `TPS62162`, EN/BOOT and
main-board UART0 content; those passages remain decision history only.

```text
Main-board USB-C / protection / Type-C current gate / eFuse
                                      |
                                      +--> 5V_SYS
                                             |
                                             +--> E220-900T22D VCC (pin 6)
                                             |
                                             +--> 30-pin 2×15 DevKit 5-V header pin [TBD]
                                                       |
                                                       +--> DevKit-local 3V3 / ESP32-WROOM
                                                       +--> DevKit-local EN, BOOT, CH340C,
                                                            programming USB-C

DevKit GPIO17 / UART2 TX  -----------> E220 RXD  (pin 3)
DevKit GPIO16 / UART2 RX  <----------- E220 TXD  (pin 4)
DevKit GPIO25              -----------> E220 M0   (pin 1)
DevKit GPIO26              -----------> E220 M1   (pin 2)
DevKit GPIO27              <----------- E220 AUX  (pin 5)
GND                         ----------- E220 GND  (pin 7)
```

`M1/M0=00` is EBYTE transmission mode; `01` is WOR send, `10` WOR receive and
`11` sleep/configuration.  The module's very weak internal pull-ups are
documented, but no external resistor value is; no arbitrary M0/M1 pulls are in
the active architecture.  The intended firmware must actively drive GPIO25/26
to the desired state, then use GPIO27 only as an AUX input.

The physical label `[TBD]` is deliberate.  “30-pin 2×15 USB-C CH340C ESP32
DevKit” is a class of boards, not an orderable, manufacturer-controlled part.
The official Espressif ESP32-DevKitC V4 cannot be substituted: it has Micro-USB
and 2×19 headers.  Its documentation also warns that its own USB input, 5-V
header input and 3.3-V header input are mutually exclusive.  That warns of the
same backfeed class but does not establish the behaviour of an unspecified
USB-C/CH340C clone.

**Schematic blocker:** exact manufacturer part number/revision, official
schematic and numbered 2×15 header drawing, including the relation of USB-C
VBUS, 5-V header pin, on-board regulator and CH340C.  Until supplied, do not
instantiate a DevKit header symbol, 5-V connection, E220 netlist, schematic or
PCB.  Rev A programming is operationally limited to a DevKit removed from the
powered main board (or a powered-down main-board USB-C input) before using the
DevKit USB-C connector.

Sources: [E220-T Series User Manual, EBYTE](https://www.cdebyte.com/pdf-down.aspx?id=4221) and [ESP32-DevKitC V4 User Guide, Espressif](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html).

### Stage 4.1 — schematic authorisation

The user has supplied the verified pin-by-pin two-header mapping and approved
the mutually-exclusive two-USB Rev A policy.  The former Stage 4 physical
header/backfeed blockers are closed.  The main-board schematic therefore uses
two distinct 1×15 socket symbols, with USB-C facing the antenna at pin 1 for
both headers:

- left 1 `VIN` = `5V_SYS`; left 2 = GND; left 6/7/8 = GPIO27/26/25;
- right 2 = GND; right 6/7 = GPIO16/RX2 and GPIO17/TX2;
- E220 connects GPIO17→RXD(3), GPIO16←TXD(4), GPIO25→M0(1), GPIO26→M1(2),
  GPIO27←AUX(5), `5V_SYS`→VCC(6) and GND→GND(7).

The approved USB policy is an explicit text constraint on the schematic: the
main-board USB-C must be disconnected before the DevKit programming USB-C is
attached.  It deliberately does not claim electrical source OR-ing.

## Stage 5 — active modular E220-T22D carrier architecture

This is the active architecture for the next carrier revision.  It supersedes
the single `E220-900T22D` population assumption and all preceding bare-ESP32 /
main-board-3V3-buck blocks.  It accepts exactly one `E220-400T22D` or
`E220-900T22D` installed module through their common verified electrical
interface; changing module does not authorise reuse of a 400-MHz antenna at
900 MHz, or vice versa.

```text
Main USB-C -> protection / TUSB320 OUT1 gate / TPS259630 -> 5V_SYS
                                                        |
                                                        +--> DevKit VIN (left-1)
                                                        |     +--> DevKit-local ESP32 / 3V3 / USB-C / CH340C
                                                        |
                                                        +--> E220-T22D-compatible module VCC (pin 6)
                                                        |     +--> 10 uF || 0.1 uF local VCC decoupling
                                                        |
                                                        +--> WS2812B-V5 + 5-V AHCT buffer

DevKit GPIO17/TX2 -> E220 RXD (3)       GPIO16/RX2 <- E220 TXD (4)
DevKit GPIO25 -> E220 M0 (1) -- 10 kOhm -> GND
DevKit GPIO26 -> E220 M1 (2) -- 10 kOhm -> GND
DevKit GPIO27 <- E220 AUX (5)           GND ----------- E220 GND (7)

DevKit GPIO21/GPIO22 -> optional OLED I2C signals only; VCC NC/DNP in Rev A
```

The 10-kOhm M0/M1 pull-downs are an explicit **PROJECT DESIGN CHOICE** to hold
the documented `M1/M0=00` transmission mode while DevKit GPIOs are reset.  The
EBYTE manual requires that inputs do not float but does not prescribe an
external resistor value.  The pull-downs are therefore not presented as EBYTE
requirements and their interaction with the actual DevKit's start-up state is
a prototype check.

The active 5-V design allocation is 777.732 mA: 500 mA DevKit project
allocation + 110 mA worst T22D emission + 36.6 mA WS2812 allocation + 1.51 mA
AHCT allocation, then 20 % margin.  No OLED current is included: its VCC is
not supplied from DevKit 3V3 in Rev A.  The 0.25-mA Type-C/TUSB enable circuit
allocation is pre-eFuse and separate: raw USB allocation is 777.982 mA, with
722.018 mA to the 1.5-A source policy.  This passes the 0.949-A minimum
TPS259630 limit by 171.268 mA, subject to cable, burst and thermal prototype
testing.

Mechanical compatibility is intentionally not asserted: EBYTE's official
manual/product pages establish common T22D electrical pinout and 21 × 36 mm
module size, but no final carrier socket, pin-header footprint, mounting-hole
pattern or courtyard is selected.  The EBYTE-provided PCB library is not a
KiCad footprint approval.  The module's SMA-K demands a band-specific antenna
and is a PCB/RF-release matter, not an electrical-schematic blocker.

Sources: [E220-T Series User Manual, EBYTE](https://www.cdebyte.com/pdf-down.aspx?id=4221), [E220-400T22D, EBYTE](https://www.cdebyte.com/products/E220-400T22D/4), [E220-900T22D, EBYTE](https://www.cdebyte.com/products/E220-900T22D/4), [TPS2596, TI](https://www.ti.com/lit/ds/symlink/tps2596.pdf), and [TUSB320LAI, TI](https://www.ti.com/lit/ds/symlink/tusb320lai.pdf).
