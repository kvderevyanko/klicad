# J6/J9 hand-solder clearance implementation handoff

## SCOPE STATUS

`IMPLEMENTED — AWAITING INDEPENDENT IMPLEMENTATION REVIEW`

The active board is byte-for-byte identical to the reviewed temporary
candidate.  Active PCB SHA-256:

`9f15f061cd98cf069137ce9181a9edf8d9903167ee9641b9fa9af746eb992acd`

Named pre-transaction backup:

`50-active-pre-j6-j9-serviceability-a9fa9493.kicad_pcb`

## Implemented geometry

* `J6_HANDSOLDER_CLEARANCE`: native B.Cu copper-pour-only rule area,
  rectangle `(91.750, 15.750)` to `(96.250, 32.950)` mm. Tracks, vias,
  pads, and footprints remain allowed.
* J6.1 explicit GND branch: B.Cu, 0.80 mm, 3.00 mm,
  `(94.000, 18.000) -> (97.000, 18.000)`. It replaces only the released
  0.25-mm B.Cu segment `(94.000, 18.000) -> (104.000, 18.000)`.
* `J9_HANDSOLDER_CLEARANCE`: native B.Cu copper-pour-only rule area,
  rectangle `(97.750, 51.750)` to `(103.000, 61.330)` mm. Tracks, vias,
  pads, and footprints remain allowed.
* J9.3 explicit GND branch: B.Cu, 0.80 mm, 3.00 mm,
  `(100.000, 59.080) -> (97.000, 59.080)`.

Final counts: 37 footprints, 201 tracks, 58 vias, four copper zones, three
rule areas, two copper layers, 145 x 90 mm.

## Machine gates

* Pre-transaction released SHA: PASS (`a9fa9493...ffec0c`).
* Protected fast contract before and after: PASS.
* Full board contract: PASS.
* Native DRC: 0 violations, 0 unconnected items.
* ERC: 0 errors, 0 warnings.
* Schematic-PCB parity: PASS.
* Production metadata: PASS.
* Antenna exclusion and protected buck contract checks: PASS.
* J6.1 and J9.3 global-GND connectivity: PASS.
* Filled B.Cu GND island flags: four `false`; no isolated GND fill.

## Reproducibility and delta

`hardware/apply_j6_j9_handsolder_clearance.py` is the narrowly scoped,
SHA-gated authoritative transform from the released PCB.  Its regenerated
board matches the active implementation for footprints, segments, vias,
rule areas, filled zones, and graphics after non-geometric UUID identity is
ignored (`64-authoritative-reproduction-proof.json`: PASS).

`verify_authorized_delta.py`: PASS.  Apart from the two reviewed rule areas,
the two new explicit GND tracks, removal of the one superseded J6 GND
segment, and resulting zone-fill polygons, footprints, pads, vias, F.Cu,
unrelated B.Cu tracks, ordinary zone definitions, antenna rule area,
Edge.Cuts, silk, and schematic are unchanged.

## Retained and next gate

All J6/J9 signal nets, J9 5V and data routes, U3/J9 path, ESP32/E220/OLED
routing, protected buck geometry, U4, antenna exclusion, outline, placement,
silkscreen, and schematic are retained.

Next required independent gate:

`SCOPE VERDICT: REV1 J6/J9 SERVICEABILITY CORRECTION PASS`

`REVIEW PASS`
