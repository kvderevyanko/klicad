# Independent implementation review — Yageo RC 0603 correction

Review date: 2026-09-17
Reviewer role: `pcb_reviewer` (read-only)
Approved transaction baseline: `b583d54c3913ef9bf37da9bce708d00fa9beb2d9`

## Result

SCOPE VERDICT: RESISTOR PHYSICAL IMPLEMENTATION PASS

REVIEW PASS

## Baseline and permitted delta

- The named PCB and schematic backups SHA-256-match the corresponding blobs at
  `b583d54`; the retained historical `analysis/baseline/` PCB was not used.
- The active PCB delta contains exactly twelve `at`/`size` edits: pads 1 and 2
  of `R1`, `R2`, `R3`, `R4`, `R8`, and `R9`.  No other embedded-footprint form
  differs.  The source delta is limited to the approved generator, shared local
  footprint, PCB pad forms, and new focused checker.  Schematic and production
  metadata are unchanged.
- `hardware/.history` was already a dirty nested subproject and is outside this
  transaction; it is not an active-design delta and must remain excluded from
  the implementation commit.

## Manufacturer evidence and resulting geometry

Direct inspection of retained Yageo *CHIP RESISTORS — Mounting — Product
Specification V10*, Fig. 4 and Table 1, confirms the drawing semantics:
`A` is outer copper span, `B` inner land gap, `C` one land length along the
resistor axis, and `D` land width.  The 0603 reflow row is
`A/B/C/D = 2.60/0.80/0.90/0.80 mm`.

The exact retained product sheets identify `RC0603FR-0710KL` as 10-kOhm 1%
0603/1608 and `RC0603FR-073K3L` as 3.3-kOhm 1% 0603/1608.  The active board
maps them respectively to R3 and R4.

Actual local and all six embedded pads are `0.900 x 0.800 mm`, centres
`(-0.850, 0)` and `(+0.850, 0)`, pitch `1.700 mm`, inner gap `0.800 mm`, and
outer span `2.600 mm`.  `roundrect_rratio 0.20`, pad numbers, nets, layer sets,
origins, and rotations are retained.  The focused invariant also proves that
the exact old `0.950 x 1.000 mm` at `+/-0.725 mm` fixture is rejected.

## Independent gates

| Gate | Result | Independent evidence |
|---|---|---|
| Full contract against named `b583d54` backup | PASS | reviewer invocation; protected checkpoint, parity, native DRC all PASS |
| Generator-to-local exact equality and six-ref invariant | PASS | `check_resistor_0603_footprint.py` |
| Schematic/PCB parity | PASS | `53-reviewer-parity.json` |
| Production metadata | PASS | `54-reviewer-production-metadata.json` |
| Native ERC | PASS; 0 violations | `50-reviewer-native-erc.json` |
| Native DRC, active board | PASS; 0 violations, 0 unconnected | `51-reviewer-native-drc.json` |
| Native DRC, disposable refilled copy | PASS; 0 violations, 0 unconnected | `52-reviewer-native-refilled-drc.json` |
| Whole-track effective-shape review | PASS | `55-reviewer-full-copper-geometry.json` |

The disposable copy is not a production source.  Saving it with KiCad only
reordered four existing U4 pad `solder_mask_margin` forms and recomputed one
zone-fill vertex; its native DRC is clean.  Neither serialization-only change
exists in the active PCB.

## Routing and physical containment

The independent effective-shape check uses the active `b583d54` backup and
resulting active PCB.  All 14 attached F.Cu tracks remain geometrically
unchanged, are 0.250 mm wide, have their endpoints inside the corrected pads,
and their whole copper shapes overlap the corresponding corrected pad.
Track, via, and zone/rule-area deltas are each zero.  The nearest different-net
copper clearance is at least 0.800001 mm; the nearest courtyards remain
separate.  No routing edit is required or permitted.

## Fabrication audit

`audit_diagnostic_outputs.py` was independently rerun against the retained
actual diagnostic Gerbers and IPC-D-356, with zero failures.

- F.Cu, F.Mask, and F.Paste each have two separate apertures for every target
  reference, with local `0.900 x 0.800 mm` geometry, pitch `1.700 mm`, and
  gap `0.800 mm`; no mask or paste apertures merge.
- IPC-D-356 reports both pads and expected nets for every target.  Its unit
  quantization reports `0.8992 x 0.8001 mm` and centres within 0.002 mm of
  nominal.
- No local mask or paste override exists.  Gerber evidence confirms the
  project zero-expansion and 1:1 copper/mask/paste treatment.  Yageo V10 gives
  no additional NSMD/SMD, mask-expansion, dam, or stencil-aperture requirement.

## Reviewed paths

- `hardware/generate_stage7_footprints.py`
- `hardware/esp32-e220.pretty/Resistor_0603_1608Metric.kicad_mod`
- `hardware/esp32-e220.kicad_pcb`
- `hardware/check_resistor_0603_footprint.py`
- `hardware/evidence/resistor-physical-plan/primary/`
- `hardware/evidence/resistor-physical-implementation-2026-09-17/`
