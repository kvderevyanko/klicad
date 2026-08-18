# ESP32 + LoRa ground receiver

Этот репозиторий содержит разработку реального наземного LoRa-приёмника на
ESP32-WROOM-32E и EBYTE E220-900T22D. Проект ведётся как производимое
электронное устройство: решения должны быть электрически проверяемыми,
подтверждёнными первичной документацией производителей и пригодными для
производства платы.

## Расположение файлов

- Все постоянные файлы проекта создавай только внутри этого корневого каталога
  (`/home/kirill/codex/kicad`) и его подкаталогов.
- Не создавай проектные документы, KiCad-файлы, скрипты, footprint'ы, BOM или
  производственные файлы в других каталогах.
- Временные диагностические файлы допускаются только в системном временном
  каталоге и не являются частью проекта.
- Документация живёт в `docs/`, KiCad-артефакты — в `hardware/`, а профиль
  специализированного агента — в `.codex/agents/pcb-engineer.toml`.

## Инженерный порядок работы

- Для схемы, PCB и проверки электроники используй профиль `pcb_engineer`.
- Не выдумывай электрические параметры, pinout, footprint или требования RF:
  критические решения подтверждай официальными источниками производителей.
- Работай стадиями: требования → верификация компонентов → schematic →
  ERC → footprints → placement → routing → DRC → engineering review.
- Не переходи к следующей стадии, пока незакрытые блокеры предыдущей не
  разрешены или явно не согласованы пользователем.
- Всегда выполняй прямые ограничения из последнего пользовательского запроса;
  они имеют приоритет над этим документом.

## Прогресс

После каждого существенного изменения обновляй этот раздел: дата, выполненный
этап, изменённые файлы, проверки и оставшиеся блокеры/вопросы. Не удаляй
историю решений.

- 2026-08-18 — Создано корневое руководство проекта. Постоянные файлы уже
  находятся в текущей рабочей папке; перенос не требуется. Stage 2
  (component verification) выполняется, schematic и PCB не созданы.
- 2026-08-18 — Stage 2: обновлены `docs/requirements.md`,
  `docs/architecture.md`, `docs/open-questions.md` и
  `docs/component-decisions.md`. Проверены official EBYTE E220-900T22D manual
  and product downloads, Espressif ESP32-WROOM-32E-N4 documentation, and TI
  TPS62162/SN74AHCT1G125/USB protection documentation. Rechecked KiCad 10.0.5
  with `kicad-cli sch erc` and `pcb drc`; no schematic/PCB/footprint created.
  Resolved: E220 model and GPIO15 boot conflict (use GPIO16 only with N4).
  Remaining blockers: final antenna/regulatory choice, OLED/WS2812 exact parts,
  connector/mating-socket footprints, USB-C source-current contract and final
  power budget.
- 2026-08-18 — Stage 2.1 corrective verification: updated
  `docs/requirements.md`, `docs/architecture.md`, `docs/open-questions.md` and
  `docs/component-decisions.md`. Selected WorldSemi `WS2812B-V5` only against
  its manufacturer document; recorded package/pins, 5 V logic basis, no
  manufacturer-specified DIN resistor or LED filter capacitor, and deliberately
  left its footprint unassigned. Added an explicit rail budget using the
  Espressif 379 mA RF peak / 500 mA rail allocation, E220 110 mA, WS allocation
  36.6 mA, AHCT 1.51 mA and `I_OLED = TBD`. Verified that TPS62162 1 A and
  passive-Rd USB-C are not yet sufficient claims for the unknown final load. No
  KiCad schematic, PCB, footprint or production file was created. Remaining
  blockers: OLED data/current, WS land pattern, USB-C source-current/protection,
  antenna/regulatory choice, connector footprints and final thermal/power review.
- 2026-08-18 — Создан корневой `readme.md` с назначением проекта, текущим
  Stage 2 status, принятыми решениями, структурой каталогов и оставшимися
  блокерами. KiCad-артефакты не создавались.
- 2026-08-18 — Stage 3 gate review: перечитаны инженерные требования и
  решения, перепроверены KiCad package `10.0.5~ubuntu22.04.1` / `kicad-cli`
  `10.0.5`, libraries and available `sch erc` / `pcb drc` commands. Обновлён
  `docs/open-questions.md` с разделением реальных schematic blockers от
  footprint/RF-layout вопросов. Схема заблокирована: exact OLED electrical
  interface/current, USB-C current contract and input-protection chain, final
  3.3 V power/inductor/thermal capability, and verified E220 local-power
  arrangement are incomplete. `hardware/` remains empty; `.kicad_pro`,
  `.kicad_sch`, `.kicad_pcb` and production files не создавались.
- 2026-08-18 — Stage 3.1 blocker-resolution documentation: updated only
  `docs/requirements.md`, `docs/architecture.md`, `docs/open-questions.md` and
  `docs/component-decisions.md`. Selected GCT `USB4105-GF-A`, TI
  `TUSB320LAIRWBR`, `TPS259630DDAR` with 909-Ohm current-set resistor, and
  EVM-topology TPS62162 passives/TDK 2.2-uH inductor using manufacturer
  sources. The corrected Type-C design keeps the eFuse/ESP boot rail enabled;
  TUSB `OUT1/OUT2` are level-divided status inputs to GPIO32/GPIO33, with
  firmware low-load policy at Default current. Recorded 721.685-mA 3V3 and
  708.6/738.0-mA `5V_SYS` allocation (5.0/4.75 V). No schematic-level blocker
  remains for a configurable design; OLED module, RF, mechanics/footprints and
  prototype power validation remain IMPORTANT before PCB release. No KiCad
  project, schematic, PCB, footprint or production file was created.
- 2026-08-18 — Stage 3.1 narrow eFuse correction: updated only
  `docs/requirements.md`, `docs/architecture.md`, `docs/component-decisions.md`
  and `docs/open-questions.md`. Corrected the status-LED buffer reference to
  selected `SN74AHCT1G125DBVR`; rechecked TI TPS259630 data sheet
  and TPS2596EVM. Defined actual CIN/COUT, EN/UVLO, OVLO and dVdt parts and
  explicitly recorded `FLT`/reverse-power constraints. Corrected TUSB320 VDD
  decoupling to 0.1-uF/16-V/X7R, distinct from the 1-uF UFP VBUS bulk
  capacitor. No KiCad project, schematic, PCB, footprint or production file
  was created. Remaining validation: source-voltage constraint, eFuse
  soft-start/inrush/thermal measurements and all previously listed PCB items.
- 2026-08-18 — Stage 3.1 TUSB VDD correction: added onsemi `MMSD4148T1G`
  between VBUS_PRE and TUSB320 VDD, retaining local
  `GRM188R71C104KA01D` 0.1-uF/16-V/X7R decoupling and separate 1-uF UFP VBUS
  bulk capacitor. Validate diode-fed VDD across source and temperature range.
  No KiCad artifact was created.
- 2026-08-18 — Stage 3.2 final preflight: updated only requirements,
  architecture, open-questions and component-decisions after rechecking TI
  TUSB320LAI GPIO/non-failsafe behaviour and TPS259630 current limit. Found two
  real schematic blockers: VBUS pull-ups on TUSB OUT1/OUT2 can back-drive the
  diode-fed device, and the 0.949-A-min eFuse cannot bound Default Type-C
  (500-mA) boot current. No `.kicad_pro`, `.kicad_sch`, `.kicad_sym`, PCB or
  production file was created. Required next decision: a level-safe TUSB status
  interface plus a hardware-enforced Default-current/boot policy.
- 2026-08-18 — Stage 3.3 electrical resolution: documented a TUSB-VDD-domain
  OUT1/NPN/eFuse-EN hardware gate using 47-kOhm pull-up/base resistors,
  330-kOhm EN pull-up and MMBT3904LT1G. It holds the receiver off at
  detach/reset/Default/VDD-absent and enables only at Medium/High advertisement;
  the former VBUS divider/GPIO32/GPIO33 topology is forbidden. Documentation
  only in this update: no KiCad schematic/project/PCB artifact was retained.
- 2026-08-18 — Stage 4 architecture change, documentation only: updated
  `docs/requirements.md`, `docs/architecture.md`, `docs/open-questions.md` and
  `docs/component-decisions.md`. The active controller is now a removable
  30-pin/2×15 USB-C/CH340C ESP32-WROOM DevKit supplied from `5V_SYS`; bare
  ESP32, 3.3-V MCU buck, EN/BOOT and programming-header design records are
  superseded history. Rechecked the official EBYTE E220-T manual: confirmed
  requested logical E220 pin mapping, 3.3-V UART, M0/M1 mode table and AUX
  constraint. Found a real schematic blocker: no exact DevKit
  manufacturer/orderable revision, official schematic, numbered header map or
  board-level USB-C/5-V backfeed rule has been supplied. No schematic or PCB
  was created or modified.
- 2026-08-18 — Stage 4.1 schematic: the user verified both 1×15 DevKit header
  maps/orientation and approved mutually-exclusive main-board/DevKit USB-C
  operation for Rev A. Created `hardware/esp32-e220.kicad_pro`,
  `hardware/esp32-e220.kicad_sch`, project-local `esp32-e220.kicad_sym`,
  `sym-lib-table`, and reproducible `generate_esp32_e220.py`; updated all four
  engineering documents and added `docs/schematic-review.md`. The schematic
  contains the removable DevKit sockets, E220 pin mapping and the documented
  TUSB320/TPS259630 fail-safe power gate/support network; it does not contain a
  bare ESP32 or a PCB. `kicad-cli sch erc --exit-code-violations` passed with
  0 errors and 0 warnings. Remaining work is prototype/power/RF/footprint and
  later PCB validation, not a schematic blocker.
- 2026-08-18 — Stage 5 modular-carrier documentation: updated only
  `docs/requirements.md`, `docs/architecture.md`, `docs/open-questions.md` and
  `docs/component-decisions.md`; no KiCad artifact was modified. Official
  EBYTE E220-T documentation/product pages were rechecked for both
  `E220-400T22D` and `E220-900T22D`: common seven-pin 3.3-V UART/control
  interface, 2.6–5.5-V T22 supply range, 90–110-mA 22-dBm emission current,
  common 21×36-mm / SMA-K form, and distinct 400-/900-MHz bands. Active design
  now accepts either installed radio; 10-kOhm M0/M1 pull-downs and local
  10-uF/100-nF bypass are explicit project choices. Recalculated protected
  `5V_SYS`: 648.110 mA subtotal and 777.732 mA with 20-% margin, using an
  explicitly non-manufacturer 500-mA DevKit allocation; OLED VCC/current is
  NC/DNP and excluded. Schematic blockers: none. PCB/prototype blockers remain
  socket/footprint, band-specific RF/antenna/legal settings, DevKit/rail
  thermal-transient measurement, display/LED mechanics and USB procedure.
- 2026-08-18 — Stage 5 schematic update: regenerated
  `hardware/esp32-e220.kicad_sch` reproducibly from
  `hardware/generate_esp32_e220.py`; project-local symbols were regenerated as
  part of that process. J3 is now labelled for exactly one EBYTE
  `E220-400T22D` or `E220-900T22D`, keeps the verified seven-pin / DevKit GPIO
  mapping, and has R8/R9 10-kOhm M0/M1 pull-downs to GND. C5/C6 now name the
  chosen Murata 10-uF/100-nF E220 decoupling MPNs. GPIO21/22 are explicitly
  OLED signal-only; OLED VCC and I2C pull-ups are NC/DNP. TUSB320/TPS259630
  OUT1/Q1 fail-safe gate was preserved. `kicad-cli sch erc
  --exit-code-violations` reports 0 errors and two documented intentional
  single-pin OLED-reservation warnings; no exclusion is used. No PCB created.
  PCB blockers remain final socket/footprint/mechanics, band-specific
  antenna/regulatory selection, LED/display mechanics, and prototype power/RF
  validation.
- 2026-08-18 — Stage 5 gate 1 mechanical-source audit: re-read the active
  documents, generator and schematic; no PCB/layout/footprint was created.
  Rechecked the two official EBYTE product downloads and the common manual
  Section 3.3 drawing titled `E220-400/900T22D Mechanical Dimensions and Pin
  Definitions`. It establishes common source geometry: 36.0 × 21.0 mm,
  seven 2.54-mm-pitch electrical pads, fixing holes 8…10, 1.50 × 2.00-mm pad
  lands and 0.90-mm holes. The 400T22D download names its 10-pad pattern and
  the 900T22D-linked PcbLib contains the common 400T22D pattern, but neither
  is treated as an approved KiCad footprint. Generator/symbol-table metadata
  is now Stage 5; schematic review and active docs record the finding. The
  universal socket, R8/R9, C5/C6, OLED NC/DNP, removable DevKit-only boundary
  and fail-safe Type-C gate remain in force. Final exact ERC rerun reports
  0 errors and the two already documented intentional `isolated_pin_label`
  warnings for signal-only OLED reservations; no ERC exclusion was added.
- 2026-08-18 — Stage 5 gate-review correction: fixed the reproducible KiCad
  generator's sheet-Y/pin-row transformation, regenerated
  `hardware/esp32-e220.kicad_sch` and project-local symbols, and manually
  audited every custom-symbol pin/net connection. The audit also exposed and
  corrected two real generic-symbol mistakes: D1 `MMSD4148T1G` now has
  A2=`VBUS_PRE` / K1=`TUSB_VDD`, and Q1 `MMBT3904LT1G` now has B1=`QBASE`,
  E2=GND, C3=`EFUSE_EN`, per onsemi. The exact 18-contact `USB4105-GF-A`
  electrical representation and GPIO4 -> `SN74AHCT1G125DBVR` ->
  `WS2812B-V5` block (with C7) are now present. KiCad 10.0.5 reads and exports
  the regenerated schematic (`kicad-cli sch export pdf` exit 0). Exact
  `kicad-cli sch erc --exit-code-violations` reports 0 errors and two visible,
  documented OLED signal-reservation warnings (therefore process exit 5);
  neither warning is excluded. Updated `docs/schematic-review.md`,
  `docs/component-decisions.md` and `docs/open-questions.md`. No PCB/layout
  artifact was created; remaining work is the existing PCB/prototype/RF
  blocker list and reviewer re-review.
- 2026-08-18 — Stage 5 second-gate correction: added only validated schematic
  content: D3 `TPD1E10B06DPYR` VBUS ESD (I/O1=`VBUS_PRE`, GND2), explicit
  TPS259630 `EP` thermal-pad-to-GND pin, and the active TP1…TP7 measurement
  nets (5V_SYS, E220 VCC, M0, M1, AUX, RXD, TXD). Re-generated the project
  symbols/schematic from `generate_esp32_e220.py`, manually audited affected
  endpoints and exported with KiCad 10.0.5 (PDF exit 0). ERC reports 0 errors
  and the same two documented OLED-reservation warnings; exact
  `--exit-code-violations` exit is 5. Re-read TI's official TPD4S311 and
  evaluated TPD2S300: both require a 2.7…4.5-V auxiliary VPWR domain, which
  cannot be supplied by raw 5 V, `5V_SYS`/DevKit 3V3 while gated off at Default,
  or unbounded diode-fed TUSB_VDD. `TPD4S311` is consequently not instantiated;
  this is a documented real schematic blocker pending an approved pre-gate
  auxiliary rail or different verified CC protection architecture. Updated
  requirements, architecture, decisions, open questions and schematic review.
  No PCB, layout, footprint or mechanical work was created.
- 2026-08-18 — Stage 5 third-gate correction: the approved pre-gate solution
  is implemented reproducibly in `hardware/generate_esp32_e220.py` and its
  regenerated KiCad schematic. U4 `TLV70433DBVR` now converts `VBUS_PRE` to
  `PRE_GATE_3V3`, with dedicated C8/C9 1-uF `GRM188R71A105KA61D` capacitors;
  it powers U1 TUSB320 VDD, U5 `TPD4S311YBFR` VPWR (C10 1 uF) and the R2/R4
  OUT1/eFuse-enable pull-ups. U5 is connected at its official DSBGA ball IDs:
  C_CC1/C_CC2 from J4; RPD_G1/RPD_G2 tied to those connector-side nodes for
  dead-battery Rd; protected CC1/CC2 to TUSB; VBIAS C11 0.1-uF/50-V X7R to
  GND; unused SBU/FLT NC. The obsolete MMSD4148-fed TUSB_VDD path was removed.
  Calculated gate checks at 3.3 V: OUT1-low sink 70.2 uA; default released
  OUT1 base drive about 27.7 uA and Q1 holds EN low; TPS EN pull-up is valid.
  Revised pre-eFuse allocation is 0.500 mA (project allocation; identified
  sum 279.8 uA) and raw total allocation 778.232 mA. KiCad 10.0.5 PDF export
  succeeds; ERC is 0 errors with the same two visible OLED-reservation
  warnings (exact `--exit-code-violations` exit 5). Updated all four active
  documents plus `docs/schematic-review.md`; no PCB, footprint, layout or
  routing work was created. Remaining checks are prototype/PCB-stage, not a
  CC schematic blocker.
- 2026-08-18 — Rev.1 battery-architecture update: superseded the active
  USB-C/CC/pre-gate/TPS259630 path in the reproducible generator and
  regenerated schematic. The active input is J4 external protected 2S pack
  only (`BAT+`/GND, 6.0...8.4 V): `BAT+ -> 1812L200/16 PPTC -> SMBJ10CA
  transient node -> DMP3130LQ-7 P-MOS reverse-polarity stage -> BUCK_IN ->
  TPS62133RGT -> 5V_SYS`. U1 uses its exact official pin functions, L1
  XFL4020-222MEB, 10-uF/25-V input, 0.1-uF AVIN, 22-uF output and 3.3-nF
  soft-start components. E220, DevKit, WS/AHCT and OLED signal reservation
  remain. Added TP1 BAT+, TP2 GND, TP3 BUCK_IN, TP4 5V_SYS, TP5 E220 VCC and
  five E220 control/UART points. The 5V allocation remains 777.732 mA;
  calculated 85-%-efficiency battery currents are 0.5446/0.6182/0.7625 A at
  8.4/7.4/6.0 V. KiCad PDF export succeeds; exact ERC has 0 errors and the
  two existing visible OLED warnings (exit 5 with `--exit-code-violations`).
  Updated all five engineering documents. No PCB, footprint assignment,
  placement or routing work was created; connector/thermal/EMI/prototype
  checks remain for the next gated review.
- 2026-08-18 — Rev.1 reviewer correction: corrected a real P-MOS
  reverse-battery orientation fault in the reproducible generator and all
  active review/decision documents. For DMP3130LQ-7 official pins 1=G, 2=S,
  3=D, Q1 is now D3=`BAT_FUSED`, S2=`BUCK_IN`, and R2 is `BUCK_IN`-to-gate.
  This makes the intrinsic diode face BAT_FUSED -> BUCK_IN for correct-polarity
  precharge and reverse-bias under a reversed pack. The VGS calculation and
  power-loss allocations are unchanged because source is the regulated input
  node in normal conduction. Schematic regeneration, PDF read and ERC are
  repeated before re-review; no PCB work is performed.
- 2026-08-18 — Rev.1 OLED activation: froze the existing protected-2S battery
  input and `TPS62133RGT`/`1812L200/16`/`DMP3130LQ-7`/`SMBJ10CA`/
  `XFL4020-222MEB` electrical baseline. Replaced the old signal-only OLED
  reservation with J5 removable female 1x4: 1=GND, 2=DevKit 3V3,
  3=GPIO22/SCL and 4=GPIO21/SDA. Added default-DNP R10/R11 4.7-kOhm 3.3-V
  pull-up sites, with no 5-V OLED supply/pull-up. Added a separate conservative
  100-mA OLED allocation outside the 500-mA DevKit allocation: `5V_SYS`
  subtotal 748.110 mA, 897.732 mA with 20-% margin, and 0.6287/0.7136/0.8801-A
  battery current at 8.4/7.4/6.0 V using the established 85-% methodology.
  Regenerated schematic, PDF export and exact ERC pass with 0 violations.
  Updated all five engineering documents. No PCB, footprint, placement,
  routing or Gerber work was created; OLED mechanics remain a PCB-stage
  measurement blocker and DevKit-regulator capability a prototype check.
