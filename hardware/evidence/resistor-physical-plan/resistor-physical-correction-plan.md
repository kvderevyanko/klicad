# Resistor shared-footprint physical correction plan

Scope: `R1`, `R2`, `R3`, `R4`, `R8`, `R9`; shared footprint `Resistor_0603_1608Metric`.

Baseline: `5f068c20e2bd7cce1e02133a1115a4397a630c55` on `audit/full-footprint-review-2026-09-16`.
This is a read-only plan. Production design files were not changed.

## Primary sources and drawing semantics

- Exact Yageo product source, `RC0603FR-0710KL`: <https://www.yageo.com/en/Chart/Download/pdf/RC0603FR-0710KL>; retained product sheet: `primary/yageo-rc0603fr-0710kl-product-sheet.pdf`. It identifies YAGEO RC, 10 kOhm, 1%, 0603/1608, nominal body `1.6 x 0.8 mm`.
- Exact Yageo product source, `RC0603FR-073K3L`: <https://www.yageo.com/en/Chart/Download/pdf/RC0603FR-073K3L>; retained product sheet: `primary/yageo-rc0603fr-073k3l-product-sheet.pdf`. It identifies YAGEO RC, 3.3 kOhm, 1%, 0603/1608, nominal body `1.6 x 0.8 mm`.
- Yageo, **CHIP RESISTORS — Mounting — Product Specification V10**, 2018-02-13: <https://yageogroup.com/content/Resource%20Library/Product%20Guide-Catalog/yageo_PYu-R_Mount_10_19050818_343.pdf>; retained as `primary/yageo_PYu-R_Mount_10_19050818_343.pdf`, page 4 also retained as `primary/yageo-mount-v10-page-4.png`.

Fig. 4 was inspected directly, not inferred from the table arithmetic. Its dimension arrows show:

- `A`: outside edge to outside edge of the two hatched rectangles, therefore total land/paste-pattern span.
- `B`: facing inner edge to facing inner edge, therefore inner land gap.
- `C`: one rectangle's dimension parallel to the component long axis, therefore individual land length.
- `D`: one rectangle's transverse dimension, therefore land width.

The Fig. 4 legend calls the same hatched geometry `solder land / solder paste pattern`. Table 1 is explicitly the **reflow soldering** table and its 0603 row is `A=2.60`, `B=0.80`, `C=0.90`, `D=0.80 mm`.

## A. Exact geometry

| Quantity | Current | Yageo reflow 0603 | Proposed |
|---|---:|---:|---:|
| overall span A | 2.400 mm | 2.600 mm | 2.600 mm |
| inner gap B | 0.500 mm | 0.800 mm | 0.800 mm |
| pad length C, long axis | 0.950 mm | 0.900 mm | 0.900 mm |
| pad width D | 1.000 mm | 0.800 mm | 0.800 mm |
| centre pitch | 1.450 mm | 1.700 mm | 1.700 mm |
| local centres | `(-0.725,0)`, `(+0.725,0)` | derived `(-0.850,0)`, `(+0.850,0)` | `(-0.850,0)`, `(+0.850,0)` |

Each centre moves `0.125 mm` outward. Pad numbers remain 1/2. The existing `roundrect_rratio 0.20` is retained: Yageo specifies the A/B/C/D envelope but no corner radius, so adding a corner-shape change is outside this correction. Component origins, rotations, nets, tracks, vias, and zones remain fixed.

## B. Six-placement routing result

Every listed route is on `F.Cu` and is `0.250 mm` wide. Each attached endpoint remains at the old pad centre. Relative to the proposed pad centre it is `0.125 mm` inward, hence `0.325 mm` from the nearest axial copper edge. The full 0.250-mm track cross-section has `0.275 mm` side margin within the 0.800-mm pad width. KiCad effective-shape tests confirm both endpoint containment and track-capsule/pad overlap for every segment; this is not an endpoint-only conclusion.

| Ref | Origin; rotation | Old pad centres 1 / 2 | Proposed pad centres 1 / 2 | Attached track segments (attached endpoint) | Full-copper / connectivity | Route edit | Nearest different-net copper | Mask / paste |
|---|---|---|---|---|---|---|---|---|
| R1 | `(58.500,67.000)`; 90 deg | `(58.500,67.725)` / `(58.500,66.275)` | `(58.500,67.850)` / `(58.500,66.150)` | P1 `(58.500,68.750)->(58.500,67.725)`; P2 `(58.500,66.275)->(59.500,66.275)` | YES / valid | no | `0.800 mm`, opposing pad | zero-expansion mask; 1:1 paste; no bridge/intersection |
| R2 | `(62.500,67.000)`; 90 deg | `(62.500,67.725)` / `(62.500,66.275)` | `(62.500,67.850)` / `(62.500,66.150)` | P1 `(62.500,67.725)->(65.500,70.000)`; P2 `(62.500,64.500)->(62.500,66.275)` | YES / valid | no | `0.800 mm`, opposing pad | same; no bridge/intersection |
| R3 | `(86.000,66.000)`; 0 deg | `(85.275,66.000)` / `(86.725,66.000)` | `(85.150,66.000)` / `(86.850,66.000)` | P1 `(82.000,66.000)->(85.275,66.000)`; P2 `(86.725,66.000)->(89.275,66.000)`, `(86.725,66.000)->(86.725,63.000)`, `(86.725,66.000)->(87.275,69.000)` | YES / valid, all four | no | `0.800 mm`, opposing pad | same; no bridge/intersection |
| R4 | `(90.000,66.000)`; 0 deg | `(89.275,66.000)` / `(90.725,66.000)` | `(89.150,66.000)` / `(90.850,66.000)` | P1 `(86.725,66.000)->(89.275,66.000)`; P2 `(90.725,66.000)->(90.725,69.000)` | YES / valid | no | `0.800 mm`, opposing pad | same; no bridge/intersection |
| R8 | `(40.000,35.000)`; 0 deg | `(39.275,35.000)` / `(40.725,35.000)` | `(39.150,35.000)` / `(40.850,35.000)` | P1 `(39.275,35.000)->(39.275,39.200)`; P2 `(40.725,35.000)->(41.500,35.000)` | YES / valid | no | `0.800 mm`, opposing pad | same; no bridge/intersection |
| R9 | `(46.000,35.000)`; 0 deg | `(45.275,35.000)` / `(46.725,35.000)` | `(45.150,35.000)` / `(46.850,35.000)` | P1 `(45.275,35.000)->(44.000,35.000)`; P2 `(46.725,35.000)->(47.500,35.000)` | YES / valid | no | `0.800 mm`, opposing pad | same; no bridge/intersection |

No track width approaches the new `0.800 mm` pad width; all are `0.250 mm`.

Disposable-candidate native DRC, both stale-fill and refilled, reports `0` unconnected items and no geometry errors. Its 12 warnings are only the isolated copy's missing `Carrier` library configuration and are identical to the isolated baseline copy; geometry/connectivity DRC delta is zero. Evidence: `analysis/baseline-refilled-drc.json`, `analysis/candidate-stale-fill-drc.json`, `analysis/candidate-refilled-drc.json`.

## Neighbour, clearance, zone, and courtyard checks

Exact proposed-shape measurements are in `analysis/candidate-geometry.json`.

| Ref | Nearby vias (copper edge gap from proposed pads) | Nearest other courtyard | Zone disposition |
|---|---|---|---|
| R1 | GND `(59.500,66.275)`, same-net, `0.300 mm`; Q1_GATE `(56.500,69.000)`, same-net, `1.499 mm` | R2, `2.210 mm` | B.Cu GND beneath; no F.Cu zone within 3 mm |
| R2 | GND `(59.500,66.275)`, different-net, `2.300 mm` | R1, `2.210 mm` | B.Cu GND beneath; no F.Cu zone within 3 mm |
| R3 | BAT_SENSE `(86.725,63.000)`, same-net, `2.300 mm` | C8, `1.210 mm` | B.Cu GND beneath; no F.Cu zone within 3 mm |
| R4 | GND `(90.725,69.000)`, same-net, `2.300 mm` | C8, `1.210 mm` | B.Cu GND beneath; no F.Cu zone within 3 mm |
| R8 | GND `(41.500,35.000)`, same-net/connected; E220_M1 `(44.000,35.000)`, different-net, `2.400 mm` | R9, `3.410 mm` | B.Cu GND beneath; no F.Cu zone within 3 mm |
| R9 | GND `(47.500,35.000)`, same-net/connected; E220_M1 `(44.000,35.000)`, same-net, `0.400 mm`; GND `(41.500,35.000)`, same-net, `2.900 mm` | R8, `3.410 mm` | B.Cu GND beneath; no F.Cu zone within 3 mm |

There is no proposed courtyard overlap. Proposed F.Paste apertures are confined to their own pads and have `0.800 mm` inner gap; no adjacent-footprint paste interaction is introduced. Zone refill was performed only on `analysis/diagnostic/esp32-e220.kicad_pcb`.

## C. Routing delta allowlist

Empty. No segment endpoint, layer, width, via, zone, return path, keepout, or coupled route may change. Preserve every listed endpoint exactly. The only board copper changes allowed are the two embedded pad shapes/centres in each of the six footprints.

## D. F.Fab / F.CrtYd disposition

- Keep F.Fab unchanged: its `1.600 x 0.800 mm` body box matches the nominal body dimensions in both exact Yageo product sheets.
- Keep F.CrtYd unchanged: `2.600 x 1.800 mm`. Yageo V10 specifies land/paste geometry, not courtyard geometry. Its axial boundary equals the proposed land outer span; this is intentionally retained under the stated scope and introduces no courtyard overlap.

## E. Mask / paste disposition

Yageo V10 does not specify solder-mask-defined versus non-solder-mask-defined lands, solder-mask expansion, or a minimum mask dam. It does depict the same A/B/C/D hatched rectangles as `solder land / solder paste pattern`, but gives no stencil thickness, area reduction, or other aperture-processing rule.

Current project behaviour is explicit `F.Cu F.Paste F.Mask` on each SMD pad, global/local mask expansion `0`, paste margin `0`, paste ratio `0`, and no footprint override. Preserve that normal 1:1 mask/paste treatment and do not change global rules. Candidate DRC has no solder-mask bridge violation. After approved implementation, numerically audit diagnostic F.Cu/F.Mask/F.Paste Gerbers: copper/mask/paste bounding envelopes must be `0.900 x 0.800 mm`, centres/pitch as planned, mask/paste gap `0.800 mm`, and no unintended aperture merge. This is a diagnostic export gate, not release authorization.

## Generic package procurement rule

For `R1/R2/R8/R9`, procurement shall be limited to a standard 0603 imperial / 1608 metric, two-terminal SMD resistor with physical body and termination envelope compatible with the approved shared 0603 land pattern. Explicitly exclude 0402, 0805, and non-standard or special-terminal 0603 variants. No exact commodity MPN is required now. `GENERIC-PACKAGE PASS` may be assigned only after independent physical-package compatibility justification following the shared-footprint correction.

## F. Proposed controlled transaction scope

After an independent plan gate only:

1. Machine contract PASS; record hashes and named backups.
2. Change only `hardware/generate_stage7_footprints.py`, `hardware/esp32-e220.pretty/Resistor_0603_1608Metric.kicad_mod`, embedded R1/R2/R3/R4/R8/R9 pads in `hardware/esp32-e220.kicad_pcb`, and a dedicated resistor invariant/checker (plus its focused test if required).
3. Preserve pad numbers, footprint identity, origins, rotations, nets, every track/via/zone/rule area, F.Fab, and F.CrtYd. `hardware/esp32-e220.kicad_sch` remains byte-identical.
4. Checker contract: exact six refs; centres `+/-0.850 mm`; pad size `0.900 x 0.800 mm`; roundrect ratio unchanged; expected origins/rotations/nets; generator/local/embedded parity; reject old geometry.
5. Re-run checker, machine contract, normal native DRC, disposable-copy refilled DRC, and schematic/PCB parity. Expected DRC/unconnected delta: zero. Any unexpected violation requires rollback and restored-state proof.
6. Only after the implementation review, create numeric diagnostic Gerber evidence; do not create a production release without separate authorization.

Risks retained for the gate: Yageo gives no mask-definition rule; the current roundrect corner treatment is preserved rather than manufacturer-mandated; F.CrtYd has zero axial margin beyond the land envelope; generic MPN package compatibility remains a procurement gate. None requires a routing change.

Planner recommendation: the bounded physical plan is ready for independent plan-gate review. This document does not claim `REVIEW PASS` or implementation approval.

ROUTING PLAN READY
