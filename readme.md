# ESP32 + E220 ground receiver carrier

Проект KiCad Rev.1 для carrier-платы наземного LoRa-приёмника: съёмный
ESP32 DevKit, съёмный EBYTE E220-T22D (400 или 900 MHz) и питание от
защищённого двухэлементного Li-ion входа. Это инженерный проект, а не
демонстрационная схема.

## Текущий статус

Завершён controlled **pre-routing repair**. Схема и PCB существуют, но плата
остаётся **UNROUTED / NOT FOR PRODUCTION**:

- 33 установочных PCB footprints;
- 0 tracks, 0 vias, 0 copper zones;
- KiCad DRC: 0 геометрических violations; 72 ожидаемых unrouted airwires;
- KiCad schematic parity: 0 findings;
- независимый reviewer: **ROUTING GEOMETRY PASS**.

Электрическая parity подтверждена машинным gate:
`python3 hardware/check_schematic_pcb_sync.py --output hardware/esp32-e220-sync-report.json`.
Он проверяет 33/33 assembled references, reference/value/footprint matching,
pad-to-net matching и отсутствие устаревших USB-C power nets. Единственные
преднамеренно не-PCB позиции — `R10` и `R11`, обе `DNP` /
`NO_FOOTPRINT_DNP`.

## Принятый pre-routing placement

- Входная цепь: `J4 → F1 → BAT_FUSED → Q1 → BUCK_IN`; `D3 SMBJ10CA` —
  шунт `BAT_FUSED → GND`, не последовательный элемент.
- D3 размещён рядом с J4/F1: J4.2 GND→D3.2 GND = 5.942 mm,
  F1.2 BAT_FUSED→D3.1 = 6.308 mm. В следующей стадии это будет короткая,
  широкая локальная surge-return петля.
- C1/C2 развёрнуты на входной стороне TPS62133RGT: PVIN12→C1.1 = 2.583 mm,
  C1.2 GND→EP = 3.338 mm; AVIN10→C2.1 = 2.204 mm,
  C2.2 GND→PGND8 = 2.919 mm.
- SW geometry сохранена: U1 SW2→L1.1 = 2.625 mm. Планируется только короткий
  локальный F.Cu участок; vias в `BUCK_SW` запрещены.
- B.Cu GND plane признан осуществимым; THT socket rows создадут только
  локальные перфорации. Во время routing нельзя разрывать return paths UART/I²C.

## Границы следующей стадии

Routing пока не начинать без нового reviewer gate. Утверждённые planning rules
(при допущении 1 oz outer copper, которое нужно подтвердить у производителя):

- SIGNAL: 0.20–0.25 mm, clearance 0.20 mm, via 0.60/0.30 mm;
- POWER (`BAT_PLUS`, `BAT_FUSED`, `BUCK_IN`, main `5V_SYS`): 1.0 mm;
  обоснованные ветви `5V_SYS` могут быть 0.8 mm;
- `BUCK_SW`: примерно 0.8 mm, только локальный F.Cu, без via и без ground pour
  под/внутри switch copper.

`D2` имеет статус `PLACEMENT_CANDIDATE_NOT_RELEASED`: **WS2812 footprint
release PENDING**, его сети пока не трассировать. OLED mechanical A/B также
остаются deferred и не должны блокировать routing остальной платы.

## Структура

- `hardware/esp32-e220.kicad_sch` — утверждённая электрическая схема.
- `hardware/esp32-e220.kicad_pcb` — сохранённый placement-only PCB.
- `hardware/generate_esp32_e220.py` и `hardware/generate_stage8_placement.py`
  — воспроизводимые генераторы схемы и placement.
- `hardware/check_schematic_pcb_sync.py` и
  `hardware/esp32-e220-sync-report.json` — machine-checkable sync gate/report.
- `docs/` — требования, архитектура, component decisions и mechanical review.
- `agents.md` — правила проекта и журнал существенных изменений.

Критические параметры, pinout, footprint и RF/EMI требования сверяются с
официальной документацией производителей. Подробные ограничения и источники —
в [docs/requirements.md](docs/requirements.md).
