# Active agent context — ESP32 + E220 carrier Rev.1

Audience: `AGENT_FACING`. This is the concise English operational source for agents. Validate mutable geometry and checker counts against the actual files before acting.

## Product boundary

The PCB is a two-layer carrier for a removable 30-pin ESP32 DevKit, one removable EBYTE E220-400T22D or E220-900T22D, and a removable 0.96-inch OLED. The active carrier supply is an externally protected 2S Li-ion pack. Superseded carrier USB-C/TUSB320/eFuse power circuitry must not be restored. The DevKit's own USB-C must remain physically accessible and is subject to the documented Rev.A mutual-use/backfeed constraint.

Factory PCBA installs carrier sockets, battery protection, the TPS62133 power cell, passives, and released carrier circuitry. ESP32 DevKit, E220, and OLED modules are user-installed. R10/R11 are `NO_FOOTPRINT_DNP` OLED pull-up options.

## Approved electrical topology

Input path:

`BAT_PLUS -> F1 -> BAT_FUSED -> Q1 -> BUCK_IN -> U1 TPS62133 -> 5V_SYS`.

TVS shunt:

`BAT_FUSED -> D3 SMBJ10CA -> GND`.

Q1 DMP3130LQ-7 uses manufacturer pins 1=G, 2=S, 3=D. Approved nets are Q1.1=`Q1_GATE`, Q1.2=`BUCK_IN`, Q1.3=`BAT_FUSED`. Do not infer function from visual pad position.

TPS62133RGT functional map from TI TPS6213x Rev.F Table 6-1:

| Pins | Function | Approved net/intent |
| --- | --- | --- |
| 1, 2, 3 | SW | `BUCK_SW` to L1, short F.Cu only |
| 4 | PG | NC in the approved design |
| 5 | FB | GND for fixed output |
| 6 | AGND | local common ground/EP |
| 7 | FSW | `5V_SYS`, logic-high frequency selection; low-current configuration trace |
| 8 | DEF | GND output selection |
| 9 | SS/TR | `SS_TR` to C4; mandatory short control connection |
| 10 | AVIN | `BUCK_IN` with local C2 bypass |
| 11, 12 | PVIN | `BUCK_IN` with local C1 high-di/dt loop |
| 13 | EN | `BUCK_IN` |
| 14 | VOS | `5V_SYS` Kelvin sense at/near C3 output node, not a power branch |
| 15, 16 | PGND | local common ground/EP |
| EP | exposed pad | GND/thermal connection |

No schematic change is currently required for the TPS62133 cell.

## Module interfaces

E220 mapping: GPIO17/TX2 -> E220 RXD; GPIO16/RX2 <- E220 TXD; GPIO25 -> M0; GPIO26 -> M1; GPIO27 <- AUX. M0/M1 have local 10-kOhm pull-downs. E220 VCC uses local 10-uF + 100-nF decoupling. Preserve SMA access and RF separation.

OLED mapping: J5.1=GND, J5.2=DevKit 3V3, J5.3=GPIO22/SCL, J5.4=GPIO21/SDA. R10/R11 4.7-kOhm pull-ups are DNP/no-footprint. OLED final mechanical datum remains unresolved.

WS2812/AHCT: U3 SN74AHCT1G125 is approved. D2 remains `PLACEMENT_CANDIDATE_NOT_RELEASED`; do not production-approve its footprint or route final D2-dependent connections unless explicitly released.

## Mechanical and PCB baseline

Board outline: 145 x 90 mm. Planning stack: two layers, 1-oz outer copper assumption pending fabrication confirmation. ESP32, E220, OLED, and J4 locations are protected from casual movement. Preserve ESP32 antenna keepout, DevKit USB-C access, E220 SMA access, and module-removal clearance.

Planning rules:

* SIGNAL: preferred 0.25 mm, 0.20 mm minimum for tight escape, 0.20 mm clearance, 0.60/0.30-mm via.
* POWER: BAT_PLUS, BAT_FUSED, BUCK_IN, and main 5V_SYS preferred 1.0 mm; justified local 5V_SYS branches may use 0.8 mm.
* BUCK_SW: short local F.Cu, no via, minimum practical copper, 0.70 mm accepted where 0.80 mm violates actual clearance.

## Current physical state

The full-board and subsequent local TPS62133 routing attempts were rejected and must not be reused as routing authority. The active board `hardware/esp32-e220.kicad_pcb` still contains retained/partial historical copper and remains the project state of record until a reviewed replacement transaction is accepted. Recompute actual segment/via/airwire counts from the file before every stage.

A separate **unrouted placement candidate** now exists at `hardware/esp32-e220-assistant-buck-candidate.kicad_pcb`. It is deliberately generated with 0 tracks, 0 vias, and 0 zones so rejected copper cannot contaminate the feasibility proof. It moves only U1/C1/C2/C3/C4/L1 into free central board area and is **not reviewer-approved**. `hardware/make_assistant_buck_candidate.py` reproduces this candidate without overwriting the active board.

### Power-block placement policy

Treat the battery-protection block and the switching-regulator island as two physical blocks:

* protection: J4/F1/D3/Q1/R1/R2 near the battery connector;
* regulator island: U1/C1/C2/C3/C4/L1 as one compact coupled placement.

The Q1-source-to-C1 `BUCK_IN` route is an upstream DC feed. It must be low impedance and appropriately wide, but it is **not** the TPS62133 local high-di/dt input loop. Do not reject a good regulator-island placement solely because Q1-to-C1 is longer than a few millimetres. The critical local input loop is C1 -> PVIN/internal switch -> PGND/EP -> C1. Likewise, the critical output loop ends locally at L1/C3/PGND; the downstream `5V_SYS` distribution may be longer.

For TPS62133 feasibility proofs, do not force every capacitor GND pad to reach EP through a separate narrow F.Cu track. TI Rev.F section 11 requires AGND/PGND/EP to connect directly to the common system ground plane. A candidate proof may therefore use compact local F.Cu GND copper plus immediate GND vias into a continuous B.Cu plane. The high-di/dt loop area, actual filled copper, return continuity, SW isolation, and VOS separation still require explicit review. A zone/plane must not be used to hide an impossible signal/power corridor.

Do not reduce C1/C2/C3/C4/L1 package sizes merely to preserve legacy power-cell coordinates. First prove or reject a current-package candidate using actual copper on a retained `hardware/evidence/` copy through `pcb_routing_planner`, then obtain `pcb_reviewer` approval. Package/MPN changes require a separate evidence/electrical review.

The current candidate coordinates are documented in `hardware/assistant-buck-candidate.md`. Straight-line pad-centre distances are planning evidence only; they are not route lengths or DRC proof. Native KiCad DRC and the project parity checker are mandatory before adoption.

## Deferred items

* OLED mechanical datum/final short connector fanout: pending.
* D2 WS2812 footprint and D2-dependent routing: pending.
* Global B.Cu ground plane: not created; it requires a separate reviewed stage.
* Full-board routing: not authorized by the current local-cell state.

## Primary operational files

* `hardware/esp32-e220.kicad_sch` — approved electrical schematic.
* `hardware/esp32-e220.kicad_pcb` — current partial physical state.
* `hardware/generate_esp32_e220.py` — reproducible schematic source.
* `hardware/generate_stage7_footprints.py` — footprint-library source.
* `hardware/generate_stage8_placement.py` — pre-routing placement generator; never run it as a whole-board reset without explicit authorization.
* `hardware/check_schematic_pcb_sync.py` — approved machine sync gate.
* `hardware/esp32-e220-power-routing-report.md` — English detailed routing checkpoint evidence.
* `hardware/esp32-e220.pretty/README.md` — English footprint-library evidence.

## Required validation

Use native KiCad ERC/DRC and the project sync checker. Report DRC geometry separately from expected out-of-scope unconnected items. Never alter connectivity merely to silence a checker; classify representation differences versus real mismatches. Final electrical and physical acceptance belongs only to `pcb_reviewer`.
