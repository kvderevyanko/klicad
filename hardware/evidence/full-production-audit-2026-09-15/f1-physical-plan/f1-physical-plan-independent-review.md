# F1 physical-plan independent review

Read-only plan gate, 2026-09-16. Reviewed the controlled PCB, the
evidence-only candidate, `f1-physical-routing-plan.md`, and the primary
Littelfuse 1812L Series datasheet, Rev. GD 06/10/24, p.6 (`Pad Layout`),
official URL recorded in `../passive-power-primary-audit.md`.

## Machine gate

`hardware/check_board_contract.py` was run first on the controlled PCB and
the candidate. Counts, duplicate-pad/net consistency, mandatory netless-pad
check, ESP32 antenna exclusion, outline, and schematic/PCB parity pass. A
candidate-versus-controlled protected-checkpoint comparison also passes:
the protected footprint set is unchanged.

Native DRC on both boards has 0 unconnected items and 0 geometric, zone, or
courtyard violations. The candidate SHA-256 is
`3430e9a77797166cf4298c2d8b080766a62928f67be258cbda755dbd3824135a`.

The full contract remains `FAIL` on both boards solely because of the two
pre-existing `lib_footprint_mismatch` warnings at JP1 and U4. They are
outside F1 scope, unchanged in the candidate, and are not suppressed. This
is a release blocker, not a physical-plan failure; its resolution remains a
separate audited task.

`reviewer-active-contract.json` and `reviewer-candidate-contract.json` are
retained command-output records from an invalid `--full` invocation; the
checker has no such argument. They are not review evidence. The valid
full-mode results were obtained with the default invocation and are stated
above; native outputs are retained as `reviewer-*-native-drc.json`.

## Independent geometry and routing assessment

The Littelfuse pad-layout drawing gives two 1.78 x 3.15-mm lands with a
3.45-mm inner-edge gap. Therefore required centres are at local X +/-2.615
mm (5.230-mm pitch). The candidate implements exactly that geometry at F1
origin (44.250, 76.000): pad 1 centre (41.635, 76.000), `/BAT_PLUS`; pad 2
centre (46.865, 76.000), `/BAT_FUSED`.

Its F.CrtYd is local X +/-3.55 and Y +/-2.12. Copper extends only to local
X +/-3.505 and Y +/-1.575, so the courtyard contains the copper (minimum
X margin 0.045 mm). At the selected origin its X span is 40.700..47.800 mm.
The fixed JST courtyards are J4 X=32.050..40.450 mm and J8
X=48.050..56.450 mm, preserving 0.250-mm clearance at both sides. The
previous-origin alternative would overlap J8; relocating J8 would expand the
external-switch datum and is correctly rejected.

The candidate diff is bounded to F1 origin, F1 description/Fab/courtyard/pad
geometry, and exactly the six allowed 1.00-mm F.Cu segment endpoint edits.
It adds no via, zone, layer, connector, or rule-area change. Pad UUIDs and
pad-to-net mapping are retained. The `/BAT_PLUS -> F1.1 -> /BAT_FUSED`
series corridor and the D3 `/BAT_FUSED` branch remain continuous; there is
no return-path, keepout, or repair-access regression.

## Findings

- NOTE — The two retained JP1/U4 library warnings make the global DRC/contract
  non-clean and prevent any production disposition. They have no F1 geometry
  delta in this candidate.
- NOTE — The implementation owner must meet the plan's transaction gate:
  named backups; generator/local-footprint regeneration; the six-segment
  allowlist; active-board contract/parity/native-DRC before and after; and
  rollback on any unexpected delta.

SCOPE VERDICT: F1 PHYSICAL PLAN PASS

REVIEW PASS
