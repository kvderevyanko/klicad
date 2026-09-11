# Independent plan gate — Q1 footprint correction

## Scope reviewed

Read-only review of the controlled board, the named pre-change checkpoint,
the evidence-only candidate, `q1-footprint-correction-physical-plan.md`, and
the retained primary Diodes PDFs. No controlled source was modified.

## Decisive geometry adjudication

`DMP3130LQ-DS38728-official.pdf`, p. 5, and the current Diodes SOT23 package
information drawing both show `X1=1.35 mm` from the component centreline to
the **outer edge** of a lower pad. It is not a pad-centre distance. With
`X=0.80 mm`, each lower-pad centre must be `1.35 - 0.80/2 = 0.95 mm` from the
centreline. `Y=0.90`, `C=2.00`, and `Y1=2.90 mm` agree with the existing
vertical geometry.

The active Q1 is therefore defective only in the X locations of pads 1 and 2:

| Item | Active | Required |
|---|---:|---:|
| Pad 1 / `Q1_GATE` local centre | `(-1.350,+1.000)` | `(-0.950,+1.000)` |
| Pad 2 / `BUCK_IN` local centre | `(+1.350,+1.000)` | `(+0.950,+1.000)` |
| Pad 3 / `BAT_SW` local centre | `(0,-1.000)` | unchanged |
| All pad copper | `0.80 x 0.90 mm` | unchanged |
| Copper envelope | `3.50 x 2.90 mm` | `2.70 x 2.90 mm` |

The source/footprint/physical-pin chain is preserved: symbol pin 1 / pad 1 /
Diodes G = `Q1_GATE`; pin 2 / pad 2 / Diodes S = `BUCK_IN`; pin 3 / pad 3 /
Diodes D = `BAT_SW`. The top-view orientation is the standard SOT-23 lower
left/lower right/upper arrangement. No electrical or pin-numbering change is
approved or needed.

## Approved implementation boundary

1. In the project-local `Diodes_DMP3130LQ-7_SOT23` footprint and Q1's embedded
   board instance, set pads 1/2 to `(-0.950,+1.000)` / `(+0.950,+1.000)` mm.
   Preserve pad sizes, Q1 origin `(63.000,76.000) mm`, rotation, layers,
   pad numbers, nets, and pad 3.
2. Re-anchor exactly these F.Cu endpoints, preserving all other endpoints,
   widths, layers, and UUIDs: `ce7bd062-9fb6-4c9c-8a39-64542cec1e84` start to
   `(62.050,77.000)`; `a4eef94c-3eb6-420b-8595-5f49d55bb7bb` and
   `cb24be05-8b8c-4b70-b364-97c90cc107a3` starts to `(63.950,77.000)`.
3. Correct the footprint representation without changing copper: F.Fab body
   is nominal `B x H = 1.30 x 2.90 mm` in this orientation, so use
   `x=[-0.65,+0.65]`, `y=[-1.45,+1.45]`. The current `3.00 x 2.90 mm` F.Fab
   rectangle is not the SOT23 body. A conservative 0.25-mm courtyard around
   the maximum of body and corrected copper is `3.20 x 3.40 mm`,
   `x=[-1.60,+1.60]`, `y=[-1.70,+1.70]`. The manufacturer does not prescribe
   a courtyard; this is a project representation rule, not a Diodes land
   dimension. Keep the pad-1 marking clear of mask openings.
4. Do not alter any other footprint, zone, rule area, via, layer, component
   origin, or downstream trace endpoint. In particular retain the B.Cu GND
   pour and the Q1.3 `BAT_SW` 1.00-mm F.Cu segment.

The bounded routing change is feasible. The two 1.00-mm `BUCK_IN` tracks and
the 0.25-mm gate track merely shorten/re-angle at their Q1 endpoints. They
remain isolated from unrelated copper; the nearest other footprint origin is
R2 at 9.014 mm. No antenna boundary, mechanical keepout, buck-cell placement,
return path, zone, or repairability constraint is affected.

## Required transaction evidence

Use `esp32-e220-q1-prechange-reference.kicad_pcb` (SHA-256
`dd4d77d521adc1fd744d10b6e05f4a27169e30d988f70a3b9e50236608fda0e4`) as the
named backup/checkpoint. Before and after the transaction, the deterministic
contract against that reference must pass, allowing only the Q1 footprint
geometry/graphics and the three endpoints above. Require parity PASS, ERC
PASS, zero unconnected items, zero new DRC geometry violations, and the
unchanged two inherited library-mismatch warnings for JP1 and U4.

The evidence-only candidate reports no unconnected items or geometry
violations. Its ten additional `Carrier` library warnings are an artefact of
running a board outside `hardware/`, where `${KIPRJMOD}/esp32-e220.pretty`
cannot resolve; they are not an active-board result and cannot be used as the
implementation DRC gate.

`CONTEXT PROVENANCE CONFLICT`: `docs/agent-context.md` states zero native DRC
violations, whereas `prechange-drc.json` records two inherited
`lib_footprint_mismatch` warnings (JP1 and U4), with zero unconnected items
and zero geometry violations. This is unrelated to Q1 and must remain visible.

SCOPE VERDICT: Q1 FOOTPRINT CORRECTION PHYSICAL PLAN PASS

REVIEW PASS
