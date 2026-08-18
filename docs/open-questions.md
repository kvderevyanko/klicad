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

## Stage 3.1 — reclassification after component verification

### BLOCKER — none for creating a configurable electrical schematic

OLED is now a defined 3V3/100-mA connector interface rather than a guessed
breakout; input parts and rated buck passives are selected; E220 decoupling is
an explicit project choice. No KiCad artifact is authorised by this statement.

### IMPORTANT — resolve before PCB release or prototype sign-off

1. Verify the actual OLED connector order, current, address and module pull-ups.
   A module exceeding the 100-mA allocation restarts the power review.
2. Test TUSB320 status into GPIO32/GPIO33 and the firmware policy: eFuse/ESP
   must boot at Default current, while Wi-Fi TX/E220/LED high-load operation is
   prohibited until Medium or High is observed. Validate startup, cable drop,
   inrush and TPS259630 faults on actual 1.5-A and 3-A sources.
3. Measure ESP32 RF/E220 TX overlap, buck thermal/transient response and E220
   10-uF/100-nF decoupling. The 85-% efficiency and 100-mA OLED cap are
   conservative project allocations, not manufacturer guarantees.
4. Confirm region/EIRP/channel, antenna/SMA/cable/enclosure and EBYTE RF
   placement guidance before layout.
5. Before PCB, audit GCT USB4105 layout, E220 mating socket/geometry,
   WS2812B-V5 land pattern, ESP32 module and all selected passive footprints.
6. Verify I2C rise time and decide fit/DNP for each 4.7-kOhm pull-up site.

### OPTIONAL

- Select manual serial header versus on-board USB-UART; USB-C stays power-only.
- Consider E220 load switching, telemetry and additional ESD/environment tests.

### Stage 3.1 correction — additional IMPORTANT validation

- Validate TPS259630 soft-start with all actual downstream capacitors and a
  plugged Type-C cable; calculated 275-mA capacitive inrush includes only the
  defined 1-uF eFuse COUT, 10-uF buck CIN and 10-uF E220 capacitor.
- OVLO nominally cuts at 5.58 V but cannot guarantee protection below E220's
  5.5-V maximum across tolerance.  Confirm the regulated 4.75…5.25-V source
  constraint in system validation; do not add a second 5V_SYS source because
  reverse-current blocking is not specified for TPS259630.

## Stage 3.2 — CURRENT BLOCKER: Type-C status and safe boot

1. **TUSB320 output level/power sequence:** the VBUS pull-up/divider
   architecture back-drives a non-failsafe TUSB GPIO pin above diode-fed VDD.
   Decide and verify a replacement: 3V3 pull-ups/direct ESP inputs with valid
   sequencing, or another approved level-safe status interface.
2. **Default-current electrical policy:** choose hardware. Either require
   Medium/High current before receiver power is enabled, or provide a verified
   500-mA-or-less boot rail and hardware-gated high-load rails. The current
   0.949-A-min eFuse setting cannot make a Default Type-C source safe.

These are electrical-schematic blockers. RF placement, OLED mechanics and
footprints remain IMPORTANT before PCB but do not stop schematic work here.

## Stage 3.3 — resolved Type-C blockers

The Stage 3.2 blockers are resolved by the hardware OUT1/Q1/EN path recorded
in `requirements.md` and `architecture.md`. It is fail-safe at VDD absent,
reset, detach and Default current, and only enables 5V_SYS at Medium/High.
The former VBUS pull-up/divider/GPIO32/GPIO33 path is forbidden historical
content. Remaining items are prototype validation (TUSB VDD ramp/diode drop,
attach behavior, eFuse startup) and all PCB/RF/mechanical IMPORTANT items.

## Stage 4 — current questions after removable-DevKit architecture change

All earlier bare-ESP32, `TPS62162`, EN/BOOT and programming-header questions
are superseded for the next schematic; they remain history only.

### BLOCKER — do not create a schematic

1. **Exact DevKit identity and header geometry.** Supply the manufacturer,
   orderable model/revision, official schematic and numbered/oriented 30-pin
   (2×15) header drawing for the USB-C/CH340C/ESP32-WROOM DevKit.  “30-pin
   USB-C CH340C” is not enough to define a schematic symbol.  In particular,
   `5V_SYS`, GPIO16/17/25/26/27 and GND positions must be verified rather than
   copied from a marketplace-style pinout.
2. **Two-USB power/backfeed behaviour.** The DevKit official documentation
   must state whether its USB-C VBUS is directly connected to its 5-V header,
   whether the header is safe to power while the programming USB-C is attached,
   and all permitted power-source combinations.  An exact CH340C chip document
   cannot answer this board-level question.  Pending evidence, Rev A requires
   physical removal of the DevKit or a powered-down/unplugged main board before
   the DevKit programming USB-C is connected.

### IMPORTANT — close before release/prototype sign-off

1. Obtain the exact DevKit 5-V input current/current-limit and regulator
   capability from its manufacturer; replace the superseded bare-module 3.3-V
   budget with a complete `5V_SYS` budget.
2. Confirm that the selected DevKit actually contains ESP32-WROOM (not a
   WROVER variant) and exposes GPIO16, GPIO17, GPIO25, GPIO26 and GPIO27.  The
   desired UART2 labels are logical firmware assignments, not a substitute for
   header evidence.
3. Decide whether normal E220 mode must be present before firmware configures
   GPIO25/26.  EBYTE documents only very weak internal pull-ups and says M0/M1
   cannot float; it does not give an external resistor value.  Do not fit
   invented pulls.  Ask EBYTE for an approved network if boot-time mode must be
   externally guaranteed.
4. Retain all existing E220 antenna/regional, OLED connector, WS2812 land
   pattern, USB-C protection/Type-C gate and `5V_SYS` transient/thermal checks
   before PCB release.

### Resolved logical E220 interface

The official EBYTE pin table confirms the requested logical mapping:
GPIO17→RXD(3), GPIO16←TXD(4), GPIO25→M0(1), GPIO26→M1(2), GPIO27←AUX(5),
`5V_SYS`→VCC(6), GND→GND(7).  It also confirms 3.3-V communication level,
M0/M1 weak pull-ups/non-floating constraint, and AUX output handling.  This
does not resolve the physical DevKit header positions.

Sources: [E220-T Series User Manual, EBYTE](https://www.cdebyte.com/pdf-down.aspx?id=4221), [E220-900T22D, EBYTE](https://www.cdebyte.com/products/E220-900T22D/4), and [ESP32-DevKitC V4 User Guide, Espressif](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html).

## Stage 4.1 — blocker resolution

### BLOCKER — none for the Stage 4 schematic

The user verified the exact left/right 1×15 maps, orientation (USB-C toward
antenna), and all required signal positions.  The Rev A mutual-exclusion rule
for main-board USB-C power versus DevKit USB-C programming is also approved.
These supersede the Stage 4 blocker entries above.

### IMPORTANT — before PCB release or normal field operation

1. Enforce the approved mutual-exclusive USB procedure in assembly/user
   documentation and silkscreen; it is not a hardware power mux.
2. Verify the selected actual DevKit's 5-V current and thermal behaviour in
   the full `5V_SYS` power budget and prototype test.
3. Retain the existing RF/antenna, OLED, WS2812, footprint, Type-C transient
   and eFuse-startup validation items.  They are not schematic blockers.

## Stage 5 — modular E220-T22D carrier gate

The user-verified DevKit mapping remains authoritative.  The active radio
population is one EBYTE `E220-400T22D` or `E220-900T22D`; their documented
common T22D electrical interface is now the carrier interface.  This section
supersedes the earlier single-900T22D-only and no-external-M0/M1-bias records.

### SCHEMATIC BLOCKER — none

The active electrical design is sufficiently defined for a controlled
schematic update: common T22D pin functions, 3.3-V UART/control levels,
`5V_SYS` VCC, explicit 10-kOhm M0/M1 pull-down project choice, DevKit header
mapping, Type-C gate and a bounded 5-V allocation are recorded.  A final PCB
footprint, RF antenna selection or a manufacturer current rating for the
removable DevKit is not a schematic blocker when the documented 500-mA design
allocation is used and clearly labelled as such.

### PCB RELEASE BLOCKERS

1. **Socket / footprint mechanics.** Select and audit the exact mating socket
   or module mounting method against current official EBYTE mechanical data:
   pin-1 orientation, header pitch, hole pattern, body keepout, courtyard and
   assembly method.  The official common 400/900-T22D drawing now verifies the
   underlying 36 × 21-mm / 2.54-mm-pitch / ten-pad-and-hole source geometry;
   do not nevertheless convert or assign the EBYTE source library blindly.
2. **RF population and legal operating configuration.** Choose one installed
   band module, a matching SMA-K antenna/cable, region, permitted channel plan
   and transmit settings.  The common electrical carrier does not make one
   antenna or radio configuration valid for both 400- and 900-MHz modules.
3. **Unverified display/LED mechanics.** OLED power remains NC/DNP; before its
   addition choose the exact module, its supply/pull-ups/current and connector.
   Audit the WS2812B-V5 land pattern before PCB placement.
4. **Carrier mechanics.** Define DevKit socket footprint, standoffs/retention,
   board outline and service markings, including the mutual-exclusive USB-C
   warning.

### PROTOTYPE VALIDATION REQUIRED

1. Measure the actual selected DevKit VIN current and its on-board 3.3-V
   regulator temperature.  The 500-mA VIN entry is a conservative **PROJECT
   DESIGN ALLOCATION** based on previous Espressif guidance, not a DevKit
   manufacturer rating.
2. At worst cable/source voltage and radio emission bursts, verify `5V_SYS`
   voltage, TPS259630 start-up/current-limit/thermal behaviour and Type-C
   attach transitions.  The 777.732-mA allocation leaves 171.268 mA to the
   eFuse's 0.949-A minimum characterised limit; it is not a transient proof.
3. Verify reset/start-up behaviour of GPIO25/GPIO26 with 10-kOhm external
   pull-downs and confirm that firmware establishes the intended E220 mode
   before radio use.  Verify UART/AUX timing on the actual module.
4. Verify the Rev A operational rule: main-board USB-C disconnected before
   DevKit programming USB-C connection.  This is not an OR-ing circuit.

### OPTIONAL IMPROVEMENTS

- Add a documented module-presence indication or labelled radio-band option
  once the exact socket is selected.
- Add controlled test points for `5V_SYS`, E220 VCC, M0, M1, AUX and UART
  signals after placement/RF review.
- Consider a later revision with a verified power-path controller if
  simultaneous DevKit programming and carrier power is a product requirement.

Sources: [E220-T Series User Manual, EBYTE](https://www.cdebyte.com/pdf-down.aspx?id=4221), [E220-400T22D, EBYTE](https://www.cdebyte.com/products/E220-400T22D/4), [E220-900T22D, EBYTE](https://www.cdebyte.com/products/E220-900T22D/4), [TPS2596, TI](https://www.ti.com/lit/ds/symlink/tps2596.pdf), and [TUSB320LAI, TI](https://www.ti.com/lit/ds/symlink/tusb320lai.pdf).

### Stage 5 gate-review status

The regenerated schematic has no ERC errors after correction of its generated
pin-row coordinates and exact D1/Q1 physical pin orders.  The only remaining
ERC findings are two visible `isolated_pin_label` warnings for the deliberately
unpopulated OLED SDA/SCL reservation.  They are not electrical schematic
blockers and were not excluded.  The PCB-release blockers above are unchanged:
they include the exact OLED interface, E220/DevKit/USB/WS2812 mechanical
implementations, band-specific antenna/regulatory choice, and prototype power
validation.

### Stage 5 second-gate — SCHEMATIC BLOCKER

**CC short-to-VBUS/ESD protection has no approved supply topology.**
`TPD4S311DRYR` requires 2.7…4.5-V VPWR (with 0.3…1-uF VPWR bypass) and a
0.1-uF VBIAS capacitor rated at least 35 V.  The currently approved Type-C
gate intentionally leaves `5V_SYS` and DevKit 3V3 off at Default current; raw
VBUS is 5 V and diode-fed `TUSB_VDD` is not bounded below 4.5 V.  Therefore it
cannot be connected without violating the official operating conditions or
creating a circular CC-detection gate.  TI `TPD2S300` was also checked and
has the same 2.7…4.5-V VPWR requirement.  Resolve one of:

1. Select and verify a pre-gate 2.7…4.5-V auxiliary supply, including all
   TPD4S311 required capacitors and no-back-power behaviour; or
2. Approve another official CC protection architecture that demonstrably meets
   the required short-to-VBUS and ESD conditions without that rail.

This is a schematic blocker.  No footprint/mechanics/PCB step is authorised
until it is resolved.

### Stage 5 third-gate disposition — CC protection blocker resolved

**RESOLVED (schematic):** the above CC-protection blocker is superseded by
U4 `TLV70433DBVR`, which produces `PRE_GATE_3V3` directly from `VBUS_PRE`.
This rail meets U5 `TPD4S311YBFR` VPWR=2.7…4.5 V and simultaneously powers U1
`TUSB320LAIRWBR` and the fail-safe OUT1/EN pull-ups. U5 is now instantiated
with its exact A2/A3/B2/B3/D3/D4 CC mapping and required C10/C11 capacitors.
The old MMSD4148-fed `TUSB_VDD` is removed.

The prior 0.250-mA raw-side allocation is superseded by a **0.500-mA PROJECT
DESIGN ALLOCATION**: identified values total 279.8 uA, but U1's cited 70-uA
UFP current has no maximum in the official table. This allocation is a
prototype-validation item, not a schematic blocker.

Remaining items are not CC topology blockers:

- **IMPORTANT / prototype:** test attach/detach and current-mode gate timing
  with representative Type-C sources; verify actual PRE_GATE_3V3 current and
  prohibited simultaneous DevKit/main-board USB back-power behaviour.
- **PCB blocker:** verify the exact `TPD4S311YBFR` DSBGA land pattern and
  assembly capability before assigning a footprint; do not infer it from the
  schematic symbol.
- **PCB/prototype:** retain all previously recorded connector, E220, antenna,
  LED, OLED and mechanical validation items.

Sources: [TLV704, TI](https://www.ti.com/lit/ds/symlink/tlv704.pdf),
[TPD4S311, TI](https://www.ti.com/lit/ds/symlink/tpd4s311.pdf), and
[TUSB320LAI, TI](https://www.ti.com/lit/ds/symlink/tusb320lai.pdf).

## Rev.1 disposition — battery power path

**RESOLVED (schematic):** the former CC-protection blocker no longer applies;
the entire USB-C/CC/pre-gate path is superseded and absent from the active
schematic. Rev.1 has a defined protected 2S battery to 5-V path.

**IMPORTANT / prototype:** confirm U1 output regulation, thermal rise and
transient response with the actual pack leads at 6.0 V and full load; validate
F1 temperature derating/trip behavior, Q1/TVS temperature, pack-BMS response
and no-backpower compliance with the approved battery-off-before-DevKit-USB
programming policy.

**PCB blockers:** choose/verify exact J4 physical connector and current rating,
TPS62133 RGT exposed-pad/land pattern, L1/C1/C3 land patterns and placement,
TVS heat/current path, F1 derating, and battery wire/strain-relief mechanics.
These do not block the electrical schematic but block layout/release.

## Rev.1 OLED disposition (current)

The former active OLED signal-only/NC-DNP decision is superseded: J5 is now
powered from `DEVKIT_3V3`, and its 1=GND/2=VCC/3=SCL/4=SDA order is
user/seller-provided. The schematic is not blocked by the stated connector
contract. R10/R11 are 4.7-kOhm 3.3-V DNP sites, so no unreviewed parallel
pull-up is fitted.

- **IMPORTANT / prototype:** identify the actual module's installed pull-ups,
  I2C address and peak current; confirm DevKit 3.3-V regulation/thermal rise
  at the separate 100-mA OLED project allocation. A module above 100 mA
  restarts the 5-V/battery budget review.
- **PCB blocker:** the latest USER-PROVIDED drawing resolves body 26.000x26.000
  mm and mounting-centre spacing X=21.740 mm/Y=22.000 mm (`OLED_MOUNT_Y`
  closed). The source drawing is not available in the workspace for audit of
  hole diameter, actual hole/header datums, display/flex clearance or
  bottom-notch/cutout geometry. Do not derive those missing values; obtain the
  drawing/callouts before a production mounting footprint, placement or
  enclosure feature.
- **Optional:** populate R10/R11 only if the actual bus capacitance and module
  pull-up arrangement require them; do not fit them by default.

## Stage 7 corrective classification — footprint/mechanical only

The following are not electrical-schematic blockers and do not authorize a
schematic topology change.

### FOOTPRINT

1. **OLED:** the known 26.000 x 26.000-mm body and 21.740 x 22.000-mm mounting
   centre spacing are usable mechanical constraints, but a production mounting
   pattern still needs the drawing/callouts for hole diameter and all
   header-to-body/display/flex/notch datums. Do not infer them.
2. **E220:** common 400/900 electrical socket coordinates are documented.
   Universal *mechanical* release needs an independent 900T22D CAD/sample
   confirmation of SMA-K position, thickness, pin projection and fixed-hole /
   underside geometry.

### MECHANICAL PLACEMENT

1. Measure DevKit header datum to its 28 x 51-mm body, USB-C and antenna. The
   two 1x15 row geometry is already verified, but it cannot establish the
   carrier edge or copper antenna keepout.
2. Define board/enclosure, battery-harness bend/strain relief, module vertical
   removal clearances and prototype test-point access.

### LAYOUT THERMAL / EMI

1. Implement TPS62133 EP solder/thermal-via policy and TI's compact input and
   switch loops during placement/routing; validate with the contracted PCBA
   process.
2. Keep Coilcraft L1 / buck SW and battery-transient loop away from the ESP32
   and E220 antenna regions.

### PROCUREMENT DFM

1. Samtec's official SSW single-row print now verifies the 2.540-mm / 1.040-mm
   hole pattern for SSW-115/107/104-02-G-S. The remaining item is assembler
   confirmation of the documented 1.70-mm project copper annular ring; Samtec
   does not state a copper-pad diameter in that print.
2. Have the selected assembler confirm the explicitly-project-IPC lands for
   `1812L200/16`, `SMBJ10CA`, Murata GRM21/GRM188 and unselected 0603 resistor
   MPNs. This is a pad/process release gate, not permission to change values.

## Stage 7 module-mechanical disposition — current

### FOOTPRINT BLOCKER

1. **OLED only:** provide **OLED-A**, top PCB edge to 1x4 header-row centreline,
   and **OLED-B**, finished mounting-hole diameter. The 26.000 x 26.000-mm
   body, X=21.740/Y=22.000-mm mount spacing, 2.540-mm pitch and GND/VCC/SCL/SDA
   X positions (9.190/11.730/14.270/16.810 mm from left) are already fixed.

### MECHANICAL PLACEMENT BLOCKER

1. Define board/enclosure, battery-harness bend/strain relief, module vertical
   removal clearances and prototype test-point access.

### PROTOTYPE / PROCUREMENT DFM NOTE

1. **E220:** no user measurement is requested. Official EBYTE common manual,
   E220-900T22D 3D STEP and library establish the common 400/900 geometry.
   Check the selected Samtec socket's insertion depth against a received module
   before PCBA release. Treat EBYTE holes 8…10 as non-electrical mechanical
   guides unless a later retention decision requires carrier features.
2. Retain the existing assembler confirmation and TPS62133 thermal/EMI layout
   constraints from the preceding Stage 7 classification.

## Stage 7.1 — active conservative preliminary-placement policy

The earlier A/B/C/D/E ESP32 clone request is **superseded as an active
blocker**. It is retained above only as historical refinement information.
Preliminary mechanical placement is now authorised with these constraints:

- DevKit envelope 28 x 51 mm, E220 envelope 21 x 36 mm and OLED envelope
  26 x 26 mm;
- at least 5 mm between removable module physical envelopes, with additional
  clearance for insertion/removal, USB cable, SMA/tool and screw/standoff use;
- ESP32 antenna end at a carrier edge with conservative no-components/no-routing
  placeholder; ESP32 USB-C remains directly accessible;
- E220 SMA side faces a board/enclosure access edge;
- **no routing** until the reviewer accepts the preliminary placement.

OLED-A (header-row Y) and OLED-B (hole diameter) remain a **production OLED
mounting-pattern** blocker, not a blocker to an un-routed preliminary envelope.

## Stage 8 — active placement / release classification

### OLED MECHANICAL / PCB RELEASE BLOCKER

1. Supply **OLED-A** (top PCB edge to 1x4 header-row centreline Y) and
   **OLED-B** (finished mounting-hole diameter). The 26.000 x 26.000-mm body,
   X=21.740/Y=22.000-mm mount spacing and header pin-X dimensions are already
   fixed and must not be requested again.
2. Confirm display-glass/flex/notch clearance before the final OLED mounting
   and enclosure release. A 36 x 36-mm conservative placement reserve exists,
   so this is not a power/RF placement or unrelated-routing blocker.

### PCB RELEASE / FOOTPRINT BLOCKER

1. Audit/approve a manufacturer land pattern for `WS2812B-V5`; the current
   visible PCB object is a placement candidate only and must not be fabricated
   as a released footprint.

### LAYOUT / THERMAL BLOCKER

1. Before routing release, approve TPS62133 EP-to-GND thermal-via policy,
   PVIN/PGND and SW/L1/COUT loop implementation, high-current copper width,
   and antenna/RF keepouts. These are routing-stage constraints, not schematic
   changes.

### PROTOTYPE VALIDATION / ENCLOSURE VALIDATION

1. Verify selected Samtec `SSW-107-02-G-S` mating depth with an E220 sample;
   no new user measurement is requested from the E220 module.
2. Verify the DevKit USB-C, E220 SMA and battery-harness access in the eventual
   enclosure. No enclosure is defined, so this is a PCB-release/enclosure item,
   not a routing blocker.
3. Confirm assembler capability for project-IPC passives and the 1.70-mm
   Samtec annular-ring choice before PCBA release.
