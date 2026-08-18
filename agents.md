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
