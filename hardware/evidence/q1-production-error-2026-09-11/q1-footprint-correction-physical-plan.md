# Q1 footprint correction: read-only physical plan

## Decisive evidence

- Controlled board snapshot: `hardware/esp32-e220.kicad_pcb`, SHA-256
  `dd4d77d521adc1fd744d10b6e05f4a27169e30d988f70a3b9e50236608fda0e4`.
- Official sources retained here: `DMP3130LQ-DS38728-official.pdf` and
  `Diodes-SOT23-package-information-official.pdf`. DS38728 identifies
  `DMP3130LQ-7` as SOT23. Its top view has the two lower terminals G (left) and
  S (right), and the upper terminal D. The schematic/PCB mapping is therefore
  physically coherent as 1/G=`Q1_GATE`, 2/S=`BUCK_IN`, 3/D=`BAT_SW`; no
  topology correction is requested by this plan.
- DS38728 suggested pattern dimensions are `C=2.0`, `X=0.8`, `X1=1.35`,
  `Y=0.9`, `Y1=2.9` mm. The drawing, not the table alone, is decisive:
  `X1` runs from the package centreline to the **outer edge** of the right
  lower land. It is not a pad-centre coordinate. Therefore each lower-pad
  centre is `X1 - X/2 = 1.35 - 0.40 = 0.95 mm` from the centreline.

## Confirmed defect and exact geometry delta

Q1 is at `(63.000, 76.000) mm`, rotation `0 deg`, F.Cu. All current pads are
`0.800 x 0.900 mm` and the vertical pitch is correctly `2.000 mm`. The defect
is the horizontal interpretation of `X1`:

| Pad | Net | Current local/global centre (mm) | Required local/global centre (mm) | Delta |
|---|---|---|---|---|
| 1 | `Q1_GATE` | `(-1.350,+1.000)` / `(61.650,77.000)` | `(-0.950,+1.000)` / `(62.050,77.000)` | `+0.400 X` |
| 2 | `BUCK_IN` | `(+1.350,+1.000)` / `(64.350,77.000)` | `(+0.950,+1.000)` / `(63.950,77.000)` | `-0.400 X` |
| 3 | `BAT_SW` | `(0,-1.000)` / `(63.000,75.000)` | unchanged | none |

Current lower-pad centre spacing is `2.700 mm`; required spacing is
`1.900 mm`. Current copper outer width is `3.500 mm`; required outer width is
`2.700 mm`. Thus the literal copper bounding box is too wide, but each lower
land is displaced 0.400 mm outward: the land ends approximately at the
physical lead centreline instead of covering the lead on both sides. That
lead-to-land misregistration explains PCBWAVE's poor/false-solder warning;
describing the complete footprint bounding box as “smaller” is not a literal
match to the active KiCad geometry.

The current F.Fab rectangle is also wrong for SOT23: it is `3.0 x 2.9 mm`.
Use the Diodes nominal body `H x B = 2.90 x 1.30 mm` (max
`3.00 x 1.40 mm`) in this orientation, with a pad-1 indication at the lower
left. Replace the oversized `4.10 x 4.00 mm` rectangular courtyard with a
`3.50 x 3.40 mm` courtyard centred on Q1 (0.25 mm around the max body and the
`2.90 mm` outer land span). Keep silkscreen outside solder-mask openings.

## Bounded routing contract

One candidate clearly dominates: retain Q1 origin/rotation and pad numbering,
correct the project-local Diodes land pattern, and re-anchor only the tracks
terminating at moved pads. A generic library substitution is not preferred
because the installed KiCad 10 `SOT-23` land dimensions are not the exact
Diodes `0.80 x 0.90 mm` recommendation and would introduce an avoidable
orientation/geometry translation.

- Coupled group: Q1 pads 1/2 plus three terminating F.Cu segments only.
- Re-anchor `ce7bd062-9fb6-4c9c-8a39-64542cec1e84`, `Q1_GATE`, F.Cu,
  0.25 mm: start `(61.650,77.000)` -> `(62.050,77.000)`; preserve end
  `(61.650,78.500)` and the 0.60/0.30 mm via there.
- Re-anchor `a4eef94c-3eb6-420b-8595-5f49d55bb7bb`, `BUCK_IN`, F.Cu,
  1.00 mm: start `(64.350,77.000)` -> `(63.950,77.000)`; preserve end
  `(65.500,77.000)`.
- Re-anchor `cb24be05-8b8c-4b70-b364-97c90cc107a3`, `BUCK_IN`, F.Cu,
  1.00 mm: start `(64.350,77.000)` -> `(63.950,77.000)`; preserve end
  `(58.000,87.000)`.
- Preserve pad-3/BAT_SW segment
  `02de816b-ba50-4df1-87ff-7b85e63e9ca3` at `(60.000,74.000)` ->
  `(63.000,75.000)`, 1.00 mm F.Cu.
- Add no vias and change no layers, widths, zones, rule areas, keepouts,
  component origins, or downstream endpoints. Preserve all non-Q1 copper.
- Return path: retain the existing B.Cu GND zone under this area; no return
  discontinuity or zone edit is needed. The BAT_SW -> Q1.3 -> Q1.2 -> BUCK_IN
  forward-power corridor remains on F.Cu at 1.00 mm.

The corrected lands move inward, away from unrelated nearby items. The nearest
other footprint origins are R2 at `(62.500,67.000)` (9.014 mm), R1 at
`(58.500,67.000)` (10.062 mm), TP4 at `(63.000,87.000)` (11.000 mm), and J8
at `(51.000,76.000)` (12.000 mm). No other placement or corridor must move.

## Transaction checkpoints and expected DRC delta

1. Electrical reviewer confirms the unchanged 1/G, 2/S, 3/D mapping.
2. Independent reviewer grants the physical plan gate.
3. Run the deterministic machine contract against the named pre-change board;
   it must PASS. Create the implementation backup.
4. In one transaction, update the project-local footprint and its generator,
   update the embedded Q1 footprint without moving its origin/rotation, then
   apply exactly the three endpoint changes above.
5. Re-run the machine contract against the pre-change reference, allowing only
   Q1 pad geometry and the named three segment endpoints. Re-run schematic/PCB
   parity, native DRC, and inspect the refilled-board ratsnest.
6. Require zero unconnected items, zero new geometry violations, no Q1 library
   mismatch, and no change to protected footprints/zones. Any unexpected
   result requires rollback and restored-state proof.

Pre-change machine contract and parity PASS. KiCad 10.0.6 reports zero
unconnected items and two pre-existing library-mismatch warnings (JP1 and U4),
with no geometric violations. Expected post-change delta is exactly zero:
the same two warnings, zero unconnected, and no new DRC category or count.

`CONTEXT PROVENANCE CONFLICT`: `docs/agent-context.md` says the active board has
zero native DRC violations, while the actual board checked with KiCad 10.0.6 in
`prechange-drc.json` has the two library-mismatch warnings above. They are
unrelated to Q1 but must not be hidden or counted as a Q1 regression.

The board under `esp32-e220-q1-geometry-candidate.kicad_pcb` is evidence-only;
its relocated project context creates extra missing-`Carrier` library warnings,
so it is not an implementation or release gate artifact.

SCOPE VERDICT: Q1 FOOTPRINT CORRECTION PHYSICAL PLAN PASS

Independent reviewer plan approval is still required before implementation.

ROUTING PLAN READY
