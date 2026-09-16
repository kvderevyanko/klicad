# D3 + Murata identity-migration physical plan — independent review

Role: `pcb_reviewer` (read-only), 2026-09-16.  This is a plan gate only;
no controlled design source was changed by this review.

## Baseline gate

The active board SHA-256 is identical to the retained pre-transaction
checkpoint:

```
27f5465e098d380c8a1bf440a8bb1b31f801d256076176c99eb956985394ee30
```

`hardware/check_board_contract.py --reference
hardware/evidence/d3-murata-physical-correction-2026-09-16/implementation-backup/esp32-e220.pre-d3-murata.kicad_pcb`
is PASS, including protected checkpoints, schematic/PCB parity, and native
DRC (zero geometric violations and zero unconnected items).  The direct
project parity check also reports zero production-property and pad/net
mismatches.

## Migration and source-of-truth gate

The authorized split is physically necessary: C5 cannot receive its GRM18
`+/-0.15` land geometry from the shared `Murata_GRM188_1608Metric` source, and
C3 cannot receive its GRM21 `+/-0.20` geometry from the shared
`Murata_GRM21_2012Metric` source.

The amended plan correctly makes each split an atomic five-surface operation,
not an alias or presentation change:

| Ref | Baseline schematic/PCB ID | Authorized new ID | Required atomic surfaces |
|---|---|---|---|
| C5 | `Murata_GRM188_1608Metric` | `Murata_GRM188R61A106MAAL_1608Metric` | stage-7 generated local file; `ASSEMBLY_CONTRACT`; stage-8 placement source; schematic `Footprint`; embedded PCB footprint ID/geometry |
| C3 | `Murata_GRM21_2012Metric` | `Murata_GRM21BR61A226ME44_2012Metric` | stage-7 generated local file; `ASSEMBLY_CONTRACT`; stage-8 placement source; schematic `Footprint`; embedded PCB footprint ID/geometry |

The required local filenames are exactly
`Murata_GRM188R61A106MAAL_1608Metric.kicad_mod` and
`Murata_GRM21BR61A226ME44_2012Metric.kicad_mod`.  The baseline generator,
assembly contract, stage-8 source, schematic, and PCB consistently show the
old identities, so the migration has a definite, complete before-state.

The plan correctly preserves the existing `Carrier:` identities: C8 remains
`Carrier:Murata_GRM188_1608Metric`; C9/C10 remain
`Carrier:Murata_GRM21_2012Metric`.  The shared geometry sources then apply
only to C2/C4/C6/C7/C8 and C1/C9/C10 respectively; C5/C3 have no remaining
shared-source dependency.

## Physical feasibility gate

The read-only candidate and retained plan demonstrate that the approved
geometry fits the frozen board without routing repair:

* D3: `2.160 x 2.260 mm`, local centres `-2.450/+2.450 mm`; pad 1 remains
  `BAT_FUSED`, pad 2 remains `GND`.
* Shared GRM188: `.70 x .70 mm`, centres `+/- .725 mm`.
* Shared GRM21: `1.20 x 1.30 mm`, centres `+/-1.000 mm`, with the planned
  expanded courtyard.
* C5: `.75 x .90 mm`, centres `+/- .725 mm`.
* C3: `.70 x 1.30 mm`, centres `+/-1.000 mm`.

The candidate delta retains all footprint placements, rotations, tracks,
vias, zone outlines, and non-target pads.  In particular, C3/C5 pad centres,
numbers and nets remain invariant; only their land dimensions and authorized
identity will change during implementation.  D3 retained track endpoints
remain inside the new lands.  The candidate native DRC after refill has zero
geometric violations and zero unconnected items.

The candidate intentionally predates the approved C3/C5 identity migration:
it is valid only as a geometry/routing feasibility proof.  It is not evidence
that the five migration surfaces have already been applied.  The implementation
gate must independently prove each immediate post-C5 and post-C3 parity
checkpoint, exact new IDs, new local files, invariant pads/nets/placements,
and absence of cross-contamination before it can claim implementation PASS.

## Required staged checkpoints

The amended plan preserves the required order: D3; shared GRM188; shared
GRM21; atomic C5 with immediate parity; atomic C3 with immediate parity.
Each stage has a bounded rollback boundary.  Any production-property,
schematic/PCB, identity, net, placement, track/via, zone-outline, or
out-of-scope delta requires rollback of that stage and STOP.

## Findings

NOTE — U4, Yageo, and generic resistors remain explicitly outside this scope.

NOTE — No release, merge, or production claim is authorized by this plan gate.

SCOPE VERDICT: D3 + MURATA IDENTITY-MIGRATION PHYSICAL PLAN PASS

REVIEW PASS
