# D3 + Murata independent implementation review

Date: 2026-09-16
Reviewer role: `pcb_reviewer` (read-only)

## Scope and retained checkpoint

Reviewed the active design against approved baseline
`4679658c64471c2ef3e92f4956cb472d90d8a565`.  The retained named board
checkpoint is byte-identical to that baseline:

```
27f5465e098d380c8a1bf440a8bb1b31f801d256076176c99eb956985394ee30
```

The allowed embedded-footprint delta is exactly
`C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,D3`; no segments or vias changed, and
zone outlines/configuration are unchanged.  The board remains 40 footprints,
202 tracks, 58 vias, four zones, and seven rule areas.

## Physical result

| Scope | Active board / Gerber result | Verdict |
|---|---|---|
| D3 `SMBJ10CA` | `2.160 x 2.260 mm`; local centres `-2.450/+2.450001 mm`, 4.900001-mm pitch and 2.740001-mm inner gap; pad 1 `/BAT_FUSED`, pad 2 `/GND` | PASS. The 0.000001-mm serialized coordinate residue is below unchanged 0.0005-mm copper-coordinate invariant tolerance; Gerber emits 4.900001-mm centre spacing. |
| C2/C4/C6/C7/C8 shared GRM188 | `0.700 x 0.700 mm`, centres +/-0.725 mm, 1.450-mm pitch | PASS |
| C5 dedicated GRM188 | `0.750 x 0.900 mm`, centres +/-0.725 mm, 1.450-mm pitch | PASS |
| C1/C9/C10 shared GRM21 | `1.200 x 1.300 mm`, centres +/-1.000 mm, 2.000-mm pitch | PASS |
| C3 dedicated GRM21 | `0.700 x 1.300 mm`, centres +/-1.000 mm, 2.000-mm pitch | PASS |

The scoped invariant independently passed against the retained baseline. It
checks generator-to-local exactness, embedded geometry/pads/nets, origins and
rotations, C3/C5 source/PCB/schematic identity, all intended footprint deltas,
unchanged tracks/vias, and unchanged zone outline/configuration.

The identity migration is atomic and correct:

- C3: `Murata_GRM21BR61A226ME44_2012Metric` in schematic, embedded PCB,
  generator mapping, and matching local file.
- C5: `Murata_GRM188R61A106MAAL_1608Metric` in the same four layers.
- C8 remains `Carrier:Murata_GRM188_1608Metric`; C9/C10 remain
  `Carrier:Murata_GRM21_2012Metric`.

No electrical net changed: retained schematic connectivity comparison is
127/127 pin-net pairs with zero deltas. Independent parity finds zero
electrical and production-property mismatches.

## Checker-only correction

`check_d3_murata_footprints.py` limits its new absolute `<= 0.001 mm`
tolerance to F.Fab/F.CrtYd bbox comparison. Its built-in boundary regression
passes exactly 0.001 mm and rejects 0.002 mm. Pad centres/sizes, pitch/gap,
nets, IDs, placements, routes, vias, zones, and parity checks retain their
pre-existing logic and tolerances.

## Independent gate reruns

| Gate | Independent result |
|---|---|
| Full board contract, named baseline reference | PASS |
| Scoped D3/Murata invariant | PASS |
| Schematic/PCB parity | PASS; 0 electrical and production-property mismatches |
| Production metadata | PASS |
| Native ERC | PASS; 0 violations |
| Native DRC, normal | PASS; 0 violations, 0 unconnected |
| Native DRC, transient refilled board | PASS; 0 violations, 0 unconnected |
| Regeneration reproducibility (retained two-pass hashes) | PASS; schematic and every local footprint byte-stable |
| Gerber F.Cu numeric audit (retained) | PASS; 22/22 flashes |
| IPC-D-356 numeric audit (retained) | PASS; 22/22 records |

The current SHA-256 values match the retained final verification manifest for
the PCB, schematic, three generators, checker, and five affected local
footprints. No release, merge, or production export approval is implied.

## Findings

`NOTE` — `docs/agent-context.md` describes a stale 37-footprint/200-track
snapshot, whereas both baseline `4679658...` and the active controlled board
contain 40 footprints/202 tracks. Actual KiCad data and contract evidence were
used as authoritative; this does not affect the scoped verdict.

`NOTE` — `hardware/.history` was already dirty outside the controlled scope;
it was not reviewed as a D3/Murata change.

SCOPE VERDICT: D3 + MURATA PHYSICAL IMPLEMENTATION PASS

REVIEW PASS
