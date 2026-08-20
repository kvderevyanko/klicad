# E220 signal routing contract — 2026-08-20

Audience: `AGENT_FACING`. This is a physical-only routing contract for
`hardware/esp32-e220.kicad_pcb`; it authorizes no schematic or topology change.

## Baseline and preserved state

* Baseline: KiCad 10.0.5; 81 segments, 17 vias, 2 GND zones; zero native
  geometric violations, 29 global unconnected items, and schematic/PCB parity
  PASS.
* Named exact backup: `hardware/esp32-e220-pre-e220-signal-routing.kicad_pcb`.
* Retain all pre-existing copper, both GND-zone boundaries, ESP32 antenna and
  USB-access reservations, E220 socket/SMA/RF access, input protection, buck,
  accepted `5V_SYS`, E220 VCC/C5/C6, U3/C7, and all out-of-scope routing.

## Actual pad contract

| Subsection | Net | Required pads / termination |
| --- | --- | --- |
| A | `/E220_M0` | J3.1 (7.880,53.500), R8.1 (30.000,58.725), TP6 (73.000,87.000), J1.8 (111.000,31.780); R8.2 (30.000,57.275) local `/GND` return |
| B | `/E220_M1` | J3.2 (10.420,53.500), R9.1 (33.000,58.725), TP7 (78.000,87.000), J1.7 (111.000,29.240); R9.2 (33.000,57.275) local `/GND` return |
| C | `/E220_AUX` | J3.5 (18.040,53.500), TP8 (83.000,87.000), J1.6 (111.000,26.700) |
| D | `/E220_RXD` | J3.3 (12.960,53.500), TP9 (88.000,87.000), J2.7 (136.400,29.240) |
| E | `/E220_TXD` | J3.4 (15.500,53.500), TP10 (93.000,87.000), J2.6 (136.400,26.700) |

## Geometry, layer, and acceptance criteria

* Route on F.Cu at 0.25 mm with 0.20-mm clearance; a 0.20-mm short escape is
  permitted only if a native DRC proof requires it. No signal vias are planned.
  Existing B.Cu GND remains the continuous return reference where the five long
  testpoint branches traverse its bounded region.
* M0/M1 are routed as continuous J3-to-DevKit trunks with junction branches to
  R8/R9 and TP6/TP7. R8.2/R9.2 receive short direct 0.25-mm local GND returns
  to J3.7, outside the buck and RF regions.
* TP6–TP10 are branch endpoints, not series conductors. Routes avoid BUCK_SW,
  L1/U1 copper, the F.Cu local buck zone, the E220 SMA/RF boundary, and the
  ESP32 antenna keepout.
* Zones are refilled following every subsection. Acceptance after each
  subsection: no new native geometric, footprint, zone, hole, pad, wrong-net,
  clearance, courtyard, or board-edge finding versus baseline; only the
  subsection's planned airwires are removed. A failed subsection is restored
  from its immediately preceding checkpoint before any later work.
