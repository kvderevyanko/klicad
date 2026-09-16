# U3 TI DBV physical correction plan

Role/scope: bounded read-only `pcb_routing_planner` plan. No active PCB,
schematic, generator, or project-local library file was changed.

## Decisive evidence and conflict

- Active PCB SHA-256 at inspection: `61549b45d4fe336986e76bcc78c5ca5532e67df604d155b140b1fd8a9d1bb109`.
- U3 is at `(89.000,54.000) mm`, rotation `0 deg`, on F.Cu.
- Primary source: TI `SN74AHCT1G125` data sheet `SCLS378P`, package
  `DBV0005A`, drawing `4214839/K`, 08/2024. Retained PDF SHA-256:
  `dbaf49b3af33690fc7f7356afe387e7815a56b8bb73fe1e88bf794f4fb8e0d2f`.
- Retained board-layout image:
  `primary/ti-dbv-board-layout-p24.png`; package image:
  `primary/ti-dbv-package-outline-p23.png`.
- Root IQC photo `260915154655565.png` qualitatively confirms that the real
  DBV lead rows lie outside the fabricated U3 pads. It is not used as a
  dimensional source because it has perspective and no scale.

`CONTEXT PROVENANCE CONFLICT`: `docs/agent-context.md`,
`hardware/esp32-e220.pretty/TI_SN74AHCT1G125DBVR_SOT23-5.kicad_mod`,
`hardware/generate_stage7_footprints.py`, and the prior
`hardware/evidence/rev1-u3-dbv-release-2026-08-21/routing-plan.md` call the
current geometry the TI pattern. TI drawing 4214839/K instead dimensions
`2.60 mm` between opposing pad-row centerlines and `1.90 mm` between pin-1
and pin-3 centerlines. The prior audit subtracted pad dimensions from these
centerline dimensions, while its DRC/library comparison only proved that the
same erroneous geometry was copied consistently. It did not compare Gerber
coordinates to the manufacturer drawing.

## Required footprint geometry

Use the existing board orientation (TI drawing rotated 90 degrees) and retain
the U3 origin and rotation.

| Pad | TI/current-orientation local center mm | Current local center mm | Required absolute center mm | Net/function |
|---|---:|---:|---:|---|
| 1 | `(-0.950,+1.300)` | `(-0.950,+0.750)` | `(88.050,55.300)` | `/GND`, OE low |
| 2 | `(0.000,+1.300)` | `(0.000,+0.750)` | `(89.000,55.300)` | `/WS2812_DATA_3V3`, A |
| 3 | `(+0.950,+1.300)` | `(+0.950,+0.750)` | `(89.950,55.300)` | `/GND`, GND |
| 4 | `(+0.950,-1.300)` | `(+0.475,-0.750)` | `(89.950,52.700)` | `/WS2812_DATA_5V`, Y |
| 5 | `(-0.950,-1.300)` | `(-0.475,-0.750)` | `(88.050,52.700)` | `/5V_SYS`, VCC |

All five copper/paste lands are `0.60 x 1.10 mm` in the current orientation,
with TI `R0.05 mm` corners (`roundrect_rratio=0.083333`), and the existing
`0.05 mm` NSMD mask expansion remains within TI's `0.07 mm max` surround.
Thus pad 1-2-3 pitch remains `0.95 mm`; pad 5-to-4 spacing changes
`0.95 -> 1.90 mm`; row-center spacing changes `1.50 -> 2.60 mm`.

TI package limits after the same rotation are body `2.75..3.05 x
1.45..1.75 mm`, overall lead envelope `2.60..3.00 mm` across the rows,
lead width `0.30..0.50 mm`, lead length `0.30..0.60 mm`, and height
`0.90..1.45 mm`. F.Fab should use the nominal midpoint body `2.90 x
1.60 mm`, with the existing pin-1-side chamfer; these nominal fab values
must not be described as maxima. F.CrtYd shall enclose the maximum body and
all lands with at least `0.25 mm`: local rectangle `x=+/-1.80`,
`y=+/-2.10 mm`. Move the F.Silk pin-1 mark clear of pad-1 mask while keeping
it adjacent to physical pin 1. Reference/value text may move outside that
courtyard; no copper depends on it.

Pin numbering must remain counter-clockwise as shown by TI: pins 1/2/3 on
the three-lead side, pin 4 opposite pin 3, pin 5 opposite pin 1. No
connectivity defect was found; `SCHEMATIC AUDIT REQUESTED` is not triggered.

## Selected routing contract

Candidate A clearly dominates: keep U3, C7, J9, all vias, and all downstream
copper fixed; re-anchor exactly one existing F.Cu segment per U3 pad.

| Net/end point | Replace existing segment | Required segment | Width/layer | Preserved opposite end |
|---|---|---|---|---|
| U3.1 `/GND` | `(88.050,54.750)->(87.200,56.500)` | `(88.050,55.300)->(87.200,56.500)` | `0.50 mm`, F.Cu | GND via `(87.200,56.500)` |
| U3.2 input | `(89.000,58.000)->(89.000,54.750)` | `(89.000,58.000)->(89.000,55.300)` | `0.25 mm`, F.Cu | data via `(89.000,58.000)` |
| U3.3 `/GND` | `(89.950,54.750)->(91.000,55.000)` | `(89.950,55.300)->(91.000,55.000)` | `0.50 mm`, F.Cu | GND via `(91.000,55.000)` |
| U3.4 output | `(89.475,53.250)->(94.000,51.500)` | `(89.950,52.700)->(94.000,51.500)` | `0.25 mm`, F.Cu | output path through `(94.000,51.500)` |
| U3.5 VCC | `(88.525,51.900)->(88.525,53.250)` | `(88.525,51.900)->(88.050,52.700)` | `0.50 mm`, F.Cu | C7 supply path at `(88.525,51.900)` |

Vias added/moved/removed: none. Preserve all 58 active vias, especially U3
GND vias `(87.200,56.500)` and `(91.000,55.000)`, input via
`(89.000,58.000)`, and C7 GND via `(85.500,51.900)`, all `0.60/0.30 mm`.
Track count remains 200. C7 remains `(85.500,54.000)`, rotation 90 degrees;
J9 remains `(100.000,54.000)`. No zone, keepout, rule area, antenna boundary,
layer, width, or return-path change is permitted.

Return path is the unchanged B.Cu GND plane reached independently by U3.1,
U3.3, and C7.2. The corrected footprint stays left of
`ESP32_ANTENNA_EXCLUSION` (X-min `104.7 mm`) and has no courtyard overlap with
C7. Candidate-board DRC reports zero unconnected items and zero geometric,
clearance, or copper violations. Its extra evidence-directory warnings are
only unresolved `Carrier` library-table items; the active baseline separately
has the two inherited JP1/U4 library-mismatch warnings.

## Transaction/checkpoint contract

1. Require independent reviewer `REVIEW PASS` on this plan.
2. Confirm the active PCB hash/current machine contract, then create a named
   backup under this evidence scope.
3. Correct `sn74ahct1g125()` in `hardware/generate_stage7_footprints.py`,
   regenerate the project-local footprint, and prove byte equality with the
   intended library artifact. Add an invariant that checks all five local pad
   centers, sizes, R0.05 corners, mask margin, fab/courtyard, and numbering.
4. Replace only embedded U3 at unchanged origin/rotation and apply the five
   segment replacements above in one bounded subsection.
5. Run the fast machine contract, refill zones, native DRC, schematic/PCB
   parity, footprint-to-library equality, and normalized pre/post delta.
6. Expected DRC delta versus the active baseline: none; zero unconnected,
   zero new geometric/clearance/zone findings, and only the same two inherited
   JP1/U4 library-mismatch warnings. Any other delta requires rollback,
   restored-state proof, and STOP.

Risks: repeating the prior centerline/overall-span misreading; mirroring pins
4/5; retaining R0.10 instead of TI R0.05 corners; snapping routes to the old
centers; generator/library/embedded-footprint drift; or letting an unrelated
regeneration alter copper or placement. The numeric invariant, five exact
endpoint changes, normalized delta, parity, and DRC gates cover these risks.

`SCOPE VERDICT: U3 PHYSICAL PLAN PASS`

ROUTING PLAN READY
