# Yageo 0603 resistor physical implementation handoff

Transaction date: 2026-09-17. Approved baseline: `b583d54c3913ef9bf37da9bce708d00fa9beb2d9` on `audit/full-footprint-review-2026-09-16`.

SCOPE STATUS: RESISTOR PHYSICAL IMPLEMENTATION COMPLETE — INDEPENDENT REVIEW REQUIRED

## Controlled delta

Production changes are limited to:

- `hardware/generate_stage7_footprints.py`: added the traceable `yageo_rc0603()` generator and selected it for the shared footprint.
- `hardware/esp32-e220.pretty/Resistor_0603_1608Metric.kicad_mod`: regenerated shared local footprint.
- `hardware/esp32-e220.kicad_pcb`: only pad `at` and `size` forms in embedded `R1/R2/R3/R4/R8/R9`.
- `hardware/check_resistor_0603_footprint.py`: focused invariant and old-geometry negative regression.

No schematic, production metadata, component origin/rotation, pad number/net/layer/UUID, track, via, zone, rule area, keepout, F.Fab, or F.CrtYd changed.

| Geometry | Baseline | Implemented |
|---|---:|---:|
| pad centres | +/-0.725 mm | +/-0.850 mm |
| pad size | 0.950 x 1.000 mm | 0.900 x 0.800 mm |
| centre pitch | 1.450 mm | 1.700 mm |
| inner gap | 0.500 mm | 0.800 mm |
| overall span | 2.400 mm | 2.600 mm |
| roundrect ratio | 0.20 | 0.20 |

All six component origins and rotations remain: R1 `(58.5,67.0,90)`, R2 `(62.5,67.0,90)`, R3 `(86.0,66.0,0)`, R4 `(90.0,66.0,0)`, R8 `(40.0,35.0,0)`, R9 `(46.0,35.0,0)`.

## Gates

| Gate | Result | Evidence |
|---|---|---|
| baseline active board equals commit production sources | PASS | pre-mutation `git diff --exit-code b583d54...` and `05-baseline-sha256.txt` |
| pre fast contract | PASS | `00-pre-fast-contract.json` |
| pre parity | PASS | `01-pre-parity.json` |
| pre native DRC | PASS, 0 violations / 0 unconnected | `02-pre-native-drc.json` |
| pre full contract | PASS | `03-pre-full-contract.json` |
| pre production metadata | PASS | `04-pre-production-metadata.json` |
| named backup/hash of active design | PASS | `named-backup/`, `05-baseline-sha256.txt` |
| immediate post fast contract | PASS | `10-post-fast-contract.json` |
| generator -> local exact reproducibility | PASS | generator rerun plus `12-post-regeneration-invariant.json` |
| final resistor invariant | PASS | `41-final-resistor-invariant.json` |
| exact six embedded footprint deltas | PASS | `41-final-resistor-invariant.json` |
| old 0.95x1.00 at +/-0.725 negative regression | PASS: exact fixture rejected with five geometry failures | `41-final-resistor-invariant.json` |
| schematic/PCB parity | PASS | `20-post-parity.json` |
| production metadata | PASS and byte-identical | `21-post-production-metadata.json`, hashes |
| native ERC | PASS, 0 violations | `22-post-native-erc.json` |
| native DRC normal | PASS, 0 violations / 0 unconnected | `23-post-native-drc.json` |
| full production contract | PASS | `24-post-full-contract.json`, `42-final-full-contract.json` |
| disposable zone refill + DRC | PASS, 0 violations / 0 unconnected | `30-refilled-native-drc.json`, `diagnostic-project/` |
| tracks / vias / zones and rule areas | exact S-expression delta zero | `41-final-resistor-invariant.json` |
| schematic connectivity / bytes | parity PASS; byte-identical | `20-post-parity.json`, `41-final-resistor-invariant.json` |
| whitespace | PASS | `git diff --check` |

The active-board SHA-256 is `494d592b2fcc014673364b866639d128eff16c73f2b5363dc282a7afe6314a4d`. The baseline board hash was `f930a29d948107fa695980e6419edc532cdf9e42c3d4d6b3ae3864a84e1a5580`.

## Diagnostic fabrication outputs

Diagnostic-only F.Cu/F.Mask/F.Paste Gerbers and IPC-D-356 are in `diagnostic-outputs/`; no production ZIP was created. `31-diagnostic-fabrication-audit.json` parses actual Gerber aperture definitions/flashes and IPC records.

- F.Cu: every R1/R2/R3/R4/R8/R9 pad is a separate `0.900 x 0.800 mm` local aperture at the expected absolute centre; pitch `1.700 mm`, inner gap `0.800 mm`.
- F.Mask: same dimensions/centres/pitch/gap as copper; exactly two separate openings per reference; no merge.
- F.Paste: same dimensions/centres/pitch/gap as copper; exactly two separate apertures per reference.
- IPC-D-356: both pads for every reference are present with the expected nets and centres. Quantization is within `0.002 mm`; reported sizes are `0.8992 x 0.8001 mm`.

Fabrication audit result: PASS.

## Review boundary

The required next gate is independent `pcb_reviewer` implementation review against Yageo Mounting V10 Fig.4/Table 1, exact R3/R4 MPN evidence, active baseline `b583d54...`, resulting PCB, diagnostic Gerbers, and IPC-D-356. This implementation handoff is not reviewer approval. Generic R1/R2/R8/R9 procurement classification remains deferred.
