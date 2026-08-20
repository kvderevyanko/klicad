# E220 signal routing attempt — 2026-08-20

Audience: `AGENT_FACING`. This report records a blocked physical-routing
attempt. It is neither a reviewer result nor a production release.

## Scope status

`SCOPE STATUS: BLOCKED`

No copper was added to `hardware/esp32-e220.kicad_pcb`. The active board is
byte-identical to the named pre-stage backup; no routing subsection was applied
to the active PCB and no review/production PDF was generated.

## Verified mapping and baseline

The active PCB and approved schematic agree exactly with the intended mapping:

| Net | E220 | DevKit | Pull / test point |
| --- | --- | --- | --- |
| `/E220_M0` | J3.1 | J1.8 | R8.1; TP6 |
| `/E220_M1` | J3.2 | J1.7 | R9.1; TP7 |
| `/E220_AUX` | J3.5 | J1.6 | TP8 |
| `/E220_RXD` | J3.3 | J2.7 | TP9 |
| `/E220_TXD` | J3.4 | J2.6 | TP10 |

R8.2 and R9.2 are `/GND`. Baseline (KiCad 10.0.5) was 81 segments, 17 vias,
2 zones, zero geometric DRC findings, 29 global unconnected items, and parity
PASS (33 schematic assembled references / 33 PCB footprints; no pad/net
mismatch). Exact backup:
`hardware/esp32-e220-pre-e220-signal-routing.kicad_pcb`, SHA-256
`d87c0ff900c9ce113c4c36b5a2785a65848077673e34804a8e9166cec2a6b76c`.

## Temporary-copy feasibility evidence

All feasibility boards are retained under
`hardware/evidence/e220-signal-routing-2026-08-20/`; the active PCB was never
used as the proof target.

| Temporary checkpoint | Native geometry findings | Global unconnected | Result |
| --- | ---: | ---: | --- |
| M0 / R8 (`feasibility-bcu-a-drc.json`) | 0 | 25 | clean on copy |
| M0 + re-planned M1 / R9 (`feasibility-m1-replan-drc.json`) | 0 | 21 | clean on copy |
| Add AUX (`feasibility-bcu-c-drc.json`) | 25 | 19 | failed; discarded copy only |

The initial F.Cu-only plan crossed protected existing `/5V_SYS` copper. The
M0/M1 temporary proof therefore used short 0.60/0.30-mm via bridges only at
unavoidable crossings, with long testpoint paths retained on F.Cu over the
bounded B.Cu GND reference. That allowed M0 and M1 individually and together,
but not the five-net set.

## Concrete physical blocker

The available two-layer corridor is not mutually routeable with the required
clearances and protected copper under the provided placement constraints:

* J3 exits are fenced by the `/5V_SYS` vertical branches at x=20.580 and
  x=23.275 mm; the central 5V distribution additionally blocks the corridor
  at x=80.000 mm and the J1/J2 access path at y=14.000 mm.
* M0’s only DRC-clean passage requires crossings/bridges that place its trunk,
  R8 branch, TP6 drop, and J1.8 entrance around x=27/79/100/104 mm. A
  re-planned M1 can cross that geometry only by additional local B.Cu bridges.
* Adding `/E220_AUX` at the prescribed J3.5/J1.6/TP8 endpoints has no remaining
  0.20-mm-clear F.Cu channel: native DRC reports short/clearance/crossing and
  hole-to-hole violations against the M0/M1 copper and the protected existing
  GND/5V objects. The complete machine record is
  `feasibility-bcu-c-drc.json`.

This is a physical congestion blocker, not a schematic discrepancy. Any next
attempt needs an explicitly authorized coupled replan (for example a defined
alternate testpoint/route corridor, additional controlled layer authority, or
an approved placement change). Do not apply the temporary-copy route to the
active board.

## Required handoff fields

`cli_exit_code=0` for each native temporary-copy DRC invocation.
`geometric_violations=25` at the failing AUX checkpoint;
`in_scope_unconnected=15` on the unchanged active board (M0=3, M1=3,
AUX=2, RXD=2, TXD=2, R8/R9 GND returns=3);
`out_of_scope_unconnected=14`;
`footprint_errors=0`; `zone_errors=0`.
Parity was PASS on the unmodified active board. Retained: all active-board
subsections. Deferred/failed: M0/M1/AUX/RXD/TXD active implementation and the
requested top/bottom review PDFs.
