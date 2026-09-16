# F1 physical-implementation independent review

Read-only implementation gate, 2026-09-16. Reviewed only the F1 correction
transaction: active PCB, `generate_stage7_footprints.py`, generated local
F1 footprint, plan/gate evidence, and the Littelfuse 1812L Series primary
datasheet, Rev. GD 06/10/24, p.6 Pad Layout (official URL recorded in
`../passive-power-primary-audit.md`). No controlled design file was edited by
this review.

## Required geometry and implemented result

The primary drawing gives 1.78 x 3.15 mm lands and a 3.45-mm inner-edge gap.
The required pitch is consequently 1.78 + 3.45 = 5.23 mm, with centres at
local X = -2.615 and +2.615 mm. The active PCB implements those exact values:

| Item | Required | Active F1 | Delta |
|---|---:|---:|---:|
| pad 1 centre | (-2.615, 0) | (-2.615, 0) | (0, 0) mm |
| pad 2 centre | (+2.615, 0) | (+2.615, 0) | (0, 0) mm |
| pad size, each | 1.780 x 3.150 mm | 1.780 x 3.150 mm | (0, 0) mm |
| centre pitch | 5.230 mm | 5.230 mm | 0 mm |
| F.Fab body | midpoint 4.55 x 3.24 mm | 4.55 x 3.24 mm | 0 mm |

F1 is at (44.250, 76.000), 0 degrees, F.Cu. Its F.CrtYd is 7.10 x 4.24 mm
(local X +/-3.55, Y +/-2.12); the lands end at local X +/-3.505, so it
contains the copper. The selected placement preserves 0.250 mm to the fixed
J4/J8 courtyards, as independently established in the approved physical plan.
F1.1 remains `/BAT_PLUS`; F1.2 remains `/BAT_FUSED`; the PPTC is
non-polarized.

## Transaction-boundary verification

`hardware/check_f1_1812l_footprint.py` passes against the named pre-F1
backup. It proves source-to-local regeneration exactness, F1 pad/nets/Fab/
courtyard/origin, unchanged non-F1 footprints, exactly the approved six
1.00-mm F.Cu segment UUID edits, and unchanged vias/zones. Its retained
negative test rejects the old F1 geometry.

The active PCB SHA-256 is
`3430e9a77797166cf4298c2d8b080766a62928f67be258cbda755dbd3824135a`,
which byte-matches the approved candidate
`../f1-physical-plan/esp32-e220-f1-proposed.kicad_pcb`. No unexpected active
PCB delta exists within the F1 transaction boundary.

## Machine gates

| Gate | Result | Independent retained evidence |
|---|---|---|
| protected checkpoint versus pre-F1 board | PASS | `53-reviewer-full-contract.json` |
| F1 generator/local/PCB/routing invariant | PASS | command output above; owner record `44-final-f1-invariant-no-bytecode.json` |
| native DRC, no refill | 2 unchanged external warnings; 0 unconnected; 0 geometric/zone violations | `50-reviewer-native-drc.json` |
| native DRC, in-memory refill | same | `54-reviewer-native-refilled-drc.json` |
| ERC | PASS, 0 violations | `51-reviewer-native-erc.json` |
| schematic/PCB parity | PASS | `52-reviewer-parity.json` |

The two DRC warnings are exactly the pre-existing `lib_footprint_mismatch`
records for JP1 at (96.000, 14.000) and U4 at (20.650, 27.000). They are
identical before/after F1 and are neither suppressed nor reclassified. They
make the *global* full contract FAIL and remain a production-release blocker,
but are not an F1 implementation delta. JP1/U4 require their separately
scoped audited correction/review.

## Findings

- NOTE — New Gerber/IPC-D-356 production-output audit is explicitly deferred
  to the parent full-production audit after all footprint transactions; this
  gate authorizes no production export or release.
- NOTE — The global contract remains FAIL solely for the two unchanged JP1/U4
  warnings described above. This F1 approval does not change the board's
  `HOLD — NOT SAFE FOR PRODUCTION` status.

SCOPE VERDICT: F1 PHYSICAL IMPLEMENTATION PASS

REVIEW PASS
