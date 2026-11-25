# D3 + Murata controlled physical-correction plan

Role: `pcb_routing_planner` (read-only).  Active PCB/schematic/library files
were not changed.  One geometry-only candidate was evaluated at
`candidate-d3-murata.kicad_pcb`.

## Scope verdict

`SCOPE VERDICT: D3 + MURATA PHYSICAL PLAN PASS`

The manufacturer geometry fits the frozen placements without moving any
component, track, via, zone outline, rule area, or board feature.  The dominant
candidate is therefore a footprint-only copper/Fab/courtyard transaction plus
zone refill.  **No route endpoint edit is required.**

## Exact geometry contract

All dimensions are millimetres.  `b x c` is the individual land length along
the footprint-local terminal axis by transverse land width.  Pad numbers and
nets are invariant.

| Scope | Old | Required implementation | Local pad centres | Fab / courtyard |
|---|---|---|---|---|
| D3 `SMBJ10CA` | `2.50 x 2.30`, pitch `4.30`, gap `1.80` | `2.160 x 2.260`, pitch `4.900`, gap `2.740` | 1=`(-2.450,0)`, 2=`(+2.450,0)` | Correct F.Fab nominal to midpoint of official body limits: `4.405 x 3.620`; F.CrtYd local `x=+/-3.800`, `y=+/-2.500` |
| C2/C4/C6/C7/C8, GRM18 +/-0.10 | `b=.95 c=1.00`, `a=.50`, pitch `1.45` | `b=.70 c=.70`, `a=.75`, pitch `1.45` | `+/-0.725` | Existing `1.60 x .80` Fab and `x=+/-1.30,y=+/-0.90` courtyard remain valid |
| C5, GRM18 +/-0.15 | `b=.95 c=1.00`, `a=.50`, pitch `1.45` | `b=.75 c=.90`, `a=.70`, pitch `1.45` | `+/-0.725` | Existing `1.60 x .80` Fab and GRM18 courtyard remain valid |
| C1/C9/C10, GRM21 +/-0.15 | `b=1.15 c=1.40`, `a=.85`, pitch `2.00` | `b=1.20 c=1.30`, `a=.80`, pitch `2.00` | `+/-1.000` | Keep `2.00 x 1.25` Fab; expand F.CrtYd local X to `+/-1.650`, retain Y `+/-1.125` so the fixed 1.20-mm lands are enclosed without a C1/C3 courtyard violation |
| C3, GRM21 +/-0.20 | `b=1.15 c=1.40`, `a=.85`, pitch `2.00` | `b=.70 c=1.30`, `a=1.30`, pitch `2.00` | `+/-1.000` | Existing `2.00 x 1.25` Fab and `x=+/-1.50,y=+/-1.125` courtyard remain valid |

The selected `c` values are range midpoints.  They avoid the previous upper
bound values while retaining adequate landing width.  The 0.80-mm C6/C7
power traces may be wider than the selected 0.70-mm solder-mask opening at the
pad entry; that copper remains covered by mask outside the land.  Candidate
DRC reports no solder-mask bridge or copper-clearance violation after refill.

At the fixed D3 placement `(41.900,70.500,180 deg)`, the final absolute
centres are:

* pad 1 `(44.350,70.500)` -> `BAT_FUSED`;
* pad 2 `(39.450,70.500)` -> `GND`.

Murata absolute pad centres are unchanged from `01-geometry-inspection.txt`:
C1 `66.700/68.700 @ y59.225`; C2 `66.725/65.275 @ y56.000`;
C3 `71.900/69.900 @ y59.225`; C4 `(67.000,52.775)/(67.000,54.225)`;
C5 `23.275/24.725 @ y48.000`; C6 `20.580/22.030 @ y49.750`;
C7 `(85.500,54.725)/(85.500,53.275)`; C8 `87.275/88.725 @ y69.000`;
C9 `(17.500,32.000)/(17.500,34.000)`; C10 `15.400/13.400 @ y27.000`.

## Source-of-truth contract

The implementation owner must change only this physical subsection:

1. `hardware/generate_stage7_footprints.py`:
   * replace D3's old project/IPC pattern with the Littelfuse manufacturer
     pattern and corrected Fab/courtyard above;
   * change `Murata_GRM188_1608Metric` to the C2/C4/C6/C7/C8 geometry;
   * add the approved MPN-specific C5 footprint
     `Murata_GRM188R61A106MAAL_1608Metric`;
   * change `Murata_GRM21_2012Metric` to the C1/C9/C10 geometry;
   * add the approved MPN-specific C3 footprint
     `Murata_GRM21BR61A226ME44_2012Metric`.
2. Regenerate the four Murata local-library geometries and D3.  C3 and C5
   must no longer resolve to the shared generic case footprints.
3. Update the C3/C5 footprint identifiers in
   `hardware/generate_esp32_e220.py`, `hardware/esp32-e220.kicad_sch`, and
   `hardware/generate_stage8_placement.py`.  Do not change values, UUIDs,
   symbol pins, net labels, or topology.
4. Replace only the embedded D3 and C1..C10 footprint geometry/metadata in
   `hardware/esp32-e220.kicad_pcb`.  Preserve references, values, placement,
   rotation, pad numbers, nets, path/UUID, attributes, and all non-footprint
   copper.
5. Add `hardware/check_d3_murata_footprints.py` as a deterministic invariant
   over generator text, local footprints, schematic assignments, embedded
   pads/nets, positions/rotations, Fab/courtyard, and the unchanged-track
   contract.

U4, Yageo, generic resistors, and all other footprints are outside this
transaction.

## Approved atomic C5/C3 identifier migrations

These are exact controlled-record migrations, not aliases and not optional
renames:

| Ref | Old schematic/PCB footprint ID | New schematic/PCB footprint ID | New generated local file |
|---|---|---|---|
| C5 | `Murata_GRM188_1608Metric` | `Murata_GRM188R61A106MAAL_1608Metric` | `hardware/esp32-e220.pretty/Murata_GRM188R61A106MAAL_1608Metric.kicad_mod` |
| C3 | `Murata_GRM21_2012Metric` | `Murata_GRM21BR61A226ME44_2012Metric` | `hardware/esp32-e220.pretty/Murata_GRM21BR61A226ME44_2012Metric.kicad_mod` |

For each row, the following five changes are one indivisible transaction:

1. generator output/name in `hardware/generate_stage7_footprints.py` and the
   new local `.kicad_mod` file;
2. `ASSEMBLY_CONTRACT` footprint entry in
   `hardware/generate_esp32_e220.py`;
3. placement-source name in `hardware/generate_stage8_placement.py`;
4. active `hardware/esp32-e220.kicad_sch` `Footprint` property;
5. active `hardware/esp32-e220.kicad_pcb` footprint ID plus its approved
   embedded pad/courtyard geometry.

Do not leave any intermediate C5 or C3 state in which the schematic property,
PCB footprint ID, generator map, placement generator, or local file disagree.
Placement, rotation, pad centres, pad numbering, nets, paths/UUIDs, references,
values, tracks, vias, and zone outlines remain invariant through both ID
migrations.  Only pad sizes change for C5/C3; their centre positions remain
those stated above.

`C8` retains the exact assignment `Carrier:Murata_GRM188_1608Metric`.
`C9` and `C10` retain the exact assignment
`Carrier:Murata_GRM21_2012Metric`.  Their identifiers, schematic properties,
placements, rotations, pad centres, numbers, nets, and UUIDs are untouched.
Their embedded pad dimensions still receive the already-approved shared
GRM188/GRM21 geometry update; “untouched” here means no identifier migration
or unrelated metadata/topology change, not retention of the rejected old pad
sizes.

## Routing contract

### Preserved D3 copper

* F.Cu `BAT_FUSED`, width `1.000`: `(44.050,72.500)` ->
  `(44.050,70.500)`.  The retained endpoint lies inside new pad 1, whose
  X extent is `43.270..45.430`.
* F.Cu `GND`, width `1.000`: `(39.750,70.500)` -> `(38.000,70.500)`.
* F.Cu `GND`, width `.500`: `(39.750,70.500)` -> `(42.200,70.500)`.
  The shared retained endpoint lies inside new pad 2, whose X extent is
  `38.370..40.530`.
* No D3 via is added, deleted, or moved.  `SMBJ10CA` is bidirectional; there
  is no cathode orientation constraint.

### Preserved Murata copper

Every connected track endpoint remains at its present pad centre and remained
inside the reduced candidate land.  This includes the C1/C2/C3/C4 buck cell,
C5/C6 E220 supply/return, C7 U3 bypass, C8 BAT_SENSE filter, and C9/C10 U4
input/output bypass.  Preserve all present layer, width, and via choices.
The candidate contains the same `260` tracks/vias as the active board and the
same `11` zone outlines.

No coupled route group changes.  Return paths remain the existing F.Cu/B.Cu
GND system and local filled zones.  The ESP32 antenna rule area, E220 access
area, buck critical-loop placement, mounting holes, edge clearance, and every
other keepout are preserved.

## Transaction checkpoints and expected DRC delta

1. Record machine contract PASS and named backups of every active/source file
   above before mutation.
2. **D3 stage:** update D3 generator/local/embedded geometry and Fab/courtyard;
   run the D3 invariant and machine contract before proceeding.
3. **Shared GRM188 stage:** update only the shared local footprint and embedded
   C2/C4/C6/C7/C8 pad geometry.  No schematic footprint ID changes.  Run the
   group invariant and contract before proceeding.
4. **Shared GRM21 stage:** update only the shared local footprint and embedded
   C1/C9/C10 pad/courtyard geometry.  Preserve the C8/C9/C10 identifiers above.
   Refill zones, then run the group invariant and contract before proceeding.
5. **C5 atomic migration stage:** apply all five migration surfaces listed in
   the migration table, then immediately run schematic/PCB parity.  It must
   PASS before any C3 edit.  Also run the physical invariant and DRC.
6. **C3 atomic migration stage:** apply all five migration surfaces listed in
   the migration table, then immediately run schematic/PCB parity.  It must
   PASS before aggregate checks.  Also run the physical invariant and DRC.
7. Prove two successive footprint generations byte-identical for all five
   affected local-library files, and run the aggregate D3/Murata invariant.
   Before every stage close, assert all placements, tracks/vias, zone outlines,
   and out-of-stage pads are byte/geometry invariant.
8. Refill zones where required.  The only candidate pre-refill geometric error was expected:
   C1 pad 1 grew by `0.025 mm` per longitudinal edge and stale GND fill showed
   `.1755 mm` instead of `.2000 mm`.  Refill removed it without changing the
   zone outline.
9. Require native DRC `0` geometric violations and `0` unconnected, custom
   schematic/PCB parity PASS, ERC PASS, and full board contract PASS.  Any
   route, via, placement, zone-outline, U4, Yageo, or generic-resistor delta is
   unexpected: rollback and stop.
10. Export diagnostic Gerber/IPC-D-356 only after the transaction gates, then
   prove all 22 target pad flashes: size, centre, pitch, orientation, pad/net.
11. Independent implementation review is mandatory before commit/push.

The active baseline native DRC has zero violations/unconnected.  Native
`--schematic-parity` also reports seven known policy-level warnings for the
intentional J6/J9 DNP footprints and H1/H2/H3 mechanical holes; the project
custom parity gate handles those intentional cases.  They must not increase.

## Candidate evidence

* `01-geometry-inspection.txt`: old/new pads and every endpoint landing.
* `03-candidate-prefill-drc.json`: one real stale-fill clearance finding plus
  evidence-copy library-path warnings.
* `04-candidate-refilled-drc.json`: zero geometry violations and zero
  unconnected; its twelve remaining warnings are only the evidence copy's
  missing `Carrier` library context, not active-board waivers.
* `05-candidate-gerber-pad-audit.json`: PASS, 22/22 F.Cu flashes.
* `candidate-d3-murata.ipc356`: D3 and Murata coordinates, dimensions,
  rotations, pad numbers, and nets agree with the candidate contract.
* `06-candidate-board-delta.json`: PASS; all placements and all 260
  tracks/vias identical, only D3/C1..C10 pad geometry changed.

Residual implementation risks are bounded to C1 zone refill, exact schematic
footprint-name parity for split C3/C5 footprints, and regeneration drift.
The checkpoints above turn each into a stop condition.

ROUTING PLAN READY
