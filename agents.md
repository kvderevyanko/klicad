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
