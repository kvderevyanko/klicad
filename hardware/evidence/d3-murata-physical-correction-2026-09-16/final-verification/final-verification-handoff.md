# D3 and Murata controlled correction — final verification handoff

Date: 2026-09-16

## SCOPE STATUS

`D3/MURATA IMPLEMENTATION VERIFICATION PASS — INDEPENDENT REVIEW REQUIRED`

This is a process status, not production approval. No release, commit, push, or
merge was performed by this verification phase.

## Checker-only correction

The authorized correction changes only
`hardware/check_d3_murata_footprints.py` drawing-bbox comparison:

- F.Fab/F.CrtYd coordinates use absolute
  `abs(actual - expected) <= 0.001 mm`;
- no rounding or relative tolerance is used;
- pad centres, sizes, pitch/gap, nets, IDs, placements, routes, vias, zones,
  parity and production-property checks retain their prior tolerances and logic;
- embedded regression cases prove a `0.001 mm` delta passes and a `0.002 mm`
  delta is rejected (`07-...json`, `11-...json`, `26-...json`).

## Implemented geometry verified

| Scope | Old land geometry | Verified new geometry |
|---|---|---|
| D3 `SMBJ10CA` | 2.500 x 2.300 mm; centres +/-2.150; gap 1.800; pitch 4.300 mm | 2.160 x 2.260 mm; centres +/-2.450; gap 2.740; pitch 4.900 mm |
| C2/C4/C6/C7/C8 GRM188 | 0.950 x 1.000 mm; centres +/-0.725; pitch 1.450 mm | 0.700 x 0.700 mm; `a=0.750`, `b=0.700`, `c=0.700`; centres/pitch unchanged |
| C5 GRM188R61A106MAAL | 0.950 x 1.000 mm; centres +/-0.725; pitch 1.450 mm | 0.750 x 0.900 mm; `a=0.700`, `b=0.750`, `c=0.900`; centres/pitch unchanged |
| C1/C9/C10 GRM21 | 1.150 x 1.400 mm; centres +/-1.000; pitch 2.000 mm | 1.200 x 1.300 mm; `a=0.800`, `b=1.200`, `c=1.300`; centres/pitch unchanged |
| C3 GRM21BR61A226ME44 | 1.150 x 1.400 mm; centres +/-1.000; pitch 2.000 mm | 0.700 x 1.300 mm; `a=1.300`, `b=0.700`, `c=1.300`; centres/pitch unchanged |

D3 remains `pad 1 -> /BAT_FUSED`, `pad 2 -> /GND`. All capacitor
pad-to-net mappings match the approved schematic. C3 and C5 origin/rotation and
pad centres are unchanged.

Identity invariants pass:

- C3: `Murata_GRM21BR61A226ME44_2012Metric`;
- C5: `Murata_GRM188R61A106MAAL_1608Metric`;
- C8 remains `Carrier:Murata_GRM188_1608Metric`;
- C9/C10 remain `Carrier:Murata_GRM21_2012Metric`;
- no cross-contamination exists between shared and MPN-specific geometry.

## Gate results

| Gate | Result | Evidence |
|---|---|---|
| Stage E retained parity/invariant/DRC | PASS | `../retry-2026-09-16/stage-e-*` |
| Checker boundary regression | PASS | `07-scoped-invariant-after-checker-fix.json` |
| Repeat footprint + schematic regeneration | PASS, pre/pass1/pass2 byte-identical | `08-*`, `09-*`, `10-*` |
| Post-regeneration scoped invariant | PASS | `11-post-regeneration-scoped-invariant.json` |
| Schematic/PCB parity | PASS; zero property or electrical mismatches | `12-parity.json` |
| Production metadata | PASS | `13-production-metadata.json` |
| Full board contract | PASS | `14-full-contract.json` |
| Native ERC | PASS, 0 violations | `15-native-erc.json` |
| Native DRC, normal | PASS, 0 violations / 0 unconnected | `16-native-drc-normal.json` |
| Native DRC, refilled diagnostic project | PASS, 0 violations / 0 unconnected | `18-native-drc-refilled-project-context.json` |
| Gerber F.Cu numeric audit | PASS, 22/22 pad flashes | `19-gerber-pad-audit.json` |
| IPC-D-356 numeric audit | PASS, 22/22 pad records | `20-ipc-d-356-pad-audit.json` |
| Schematic connectivity baseline diff | PASS, 127/127 pin-net pairs; zero deltas | `22-schematic-connectivity-diff.json` |
| Repository unit tests | PASS, 12 tests | `25-unit-tests.txt` |
| Final scoped invariant / fast contract | PASS / PASS | `26-*`, `27-*` |

`17-native-drc-refilled.json` is retained as invalid-context diagnostic evidence:
the first copied board lacked its `${KIPRJMOD}` footprint library and therefore
reported 12 missing-`Carrier` library warnings, with zero geometric violations
and zero unconnected items. The complete self-contained project-context rerun is
the authoritative refilled result in `18-...json`.

## Production-design delta proof

The scoped invariant compares the active board with the named pre-transaction
board and reports exactly these changed footprints:
`C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,D3`; changed segments `[]`; changed vias `[]`;
zone outlines/configuration unchanged. Footprint count remains 40, track count
202, via count 58, and the parsed zone/rule-area inventory remains 11.

The regenerated schematic connectivity comparison reports 127 pin-net pairs in
both states with zero changes. Parity also proves exact schematic/PCB footprint
property agreement, including the approved C3/C5 identity migrations.

Intended design/source/checker files in the worktree are:

- `hardware/esp32-e220.kicad_pcb`
- `hardware/esp32-e220.kicad_sch`
- `hardware/generate_esp32_e220.py`
- `hardware/generate_stage7_footprints.py`
- `hardware/generate_stage8_placement.py`
- `hardware/check_d3_murata_footprints.py`
- `hardware/esp32-e220.pretty/Littelfuse_SMBJ10CA_DO214AA.kicad_mod`
- `hardware/esp32-e220.pretty/Murata_GRM188_1608Metric.kicad_mod`
- `hardware/esp32-e220.pretty/Murata_GRM21_2012Metric.kicad_mod`
- `hardware/esp32-e220.pretty/Murata_GRM188R61A106MAAL_1608Metric.kicad_mod`
- `hardware/esp32-e220.pretty/Murata_GRM21BR61A226ME44_2012Metric.kicad_mod`

`hardware/.history` remains an unrelated pre-existing dirty nested-worktree item
and was not modified by this transaction. U4, Yageo, generic resistors, all other
footprints, all routes, vias, and zone outlines were not changed.

Next gate: independent `pcb_reviewer` implementation review of the active state
and retained evidence. `SAFE FOR PRODUCTION` must not be assigned at this stage.
