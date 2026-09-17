# Independent resistor physical-plan review

Review scope: `R1`, `R2`, `R3`, `R4`, `R8`, `R9`; no production design file was modified.

## Gate evidence

- Active `hardware/esp32-e220.kicad_pcb`, checked against the stated approved commit/reference: deterministic contract, schematic/PCB parity, protected checkpoint, and native DRC all PASS.
- The reviewed disposable candidate was regenerated from the active approved board, not just accepted from the planner copy. It was zone-refilled only in `reviewer-active-baseline-candidate.kicad_pcb`. Native DRC: zero errors, zero unconnected items. The only 12 warnings are identical isolated-copy `lib_footprint_issues` warnings for absent `Carrier` library configuration.
- `reviewer_geometry_check.py` uses KiCad effective shapes, and `reviewer-active-baseline-refilled-geometry.json` records all 14 attached F.Cu tracks: every endpoint is inside its proposed pad and every *whole track copper shape* overlaps its proposed pad. All widths are `0.250 mm`.

## Primary evidence and semantics

I inspected Fig. 4 in the retained official Yageo **CHIP RESISTORS — Mounting — Product Specification V10** directly (`primary/yageo-mount-v10-page-4.png`, source PDF `primary/yageo_PYu-R_Mount_10_19050818_343.pdf`). The arrows establish, without table arithmetic, that `A` is outside-to-outside land/paste span, `B` is inner land gap, `C` is one land length along the resistor axis, and `D` is transverse land width. The legend labels the hatched rectangles `solder land / solder paste pattern`; V10 provides no separate copper-versus-paste dimensions.

Table 1 (reflow), 0603 row is `A=2.60`, `B=0.80`, `C=0.90`, `D=0.80 mm`. The exact product sources are <https://www.yageo.com/en/Chart/Download/pdf/RC0603FR-0710KL> and <https://www.yageo.com/en/Chart/Download/pdf/RC0603FR-073K3L>; retained as `primary/yageo-rc0603fr-0710kl-product-sheet.pdf` and `primary/yageo-rc0603fr-073k3l-product-sheet.pdf`. The exact V10 source is <https://yageogroup.com/content/Resource%20Library/Product%20Guide-Catalog/yageo_PYu-R_Mount_10_19050818_343.pdf>. The two product PDFs have SHA-256 values matching the corresponding previously retained files under `hardware/evidence/residual-footprint-audit-2026-09-16/primary/`. They identify Yageo RC 0603/1608, 10 kOhm and 3.3 kOhm respectively. No source-retention conflict remains.

| geometry | old | manufacturer reflow | proposed |
|---|---:|---:|---:|
| A overall span | 2.400 | 2.600 | 2.600 mm |
| B inner gap | 0.500 | 0.800 | 0.800 mm |
| C land length | 0.950 | 0.900 | 0.900 mm |
| D land width | 1.000 | 0.800 | 0.800 mm |
| centre pitch | 1.450 | 1.700 derived | 1.700 mm |
| local centres | +/-0.725 | +/-0.850 derived | +/-0.850 mm |

The numeric proposal is correct. Each pad centre moves `0.125 mm` outward, while pad numbers, footprint identities, origins, rotations, nets, and layers are preserved.

## Placement, routing, and clearance

| Ref | origin; rot. | old pad centres 1 / 2 mm | proposed centres 1 / 2 mm | attached endpoints (mm), all 0.250 mm F.Cu | whole-copper overlap | nearest different-net copper | nearest courtyard | route |
|---|---|---|---|---|---|---|---|---|
| R1 | (58.500,67.000); 90 | (58.500,67.725) / (58.500,66.275) | (58.500,67.850) / (58.500,66.150) | (58.500,67.725), (58.500,66.275) | PASS, 2/2 | opposing pad, 0.800001 mm | R2, 2.210001 mm | no |
| R2 | (62.500,67.000); 90 | (62.500,67.725) / (62.500,66.275) | (62.500,67.850) / (62.500,66.150) | (62.500,67.725), (62.500,66.275) | PASS, 2/2 | opposing pad, 0.800001 mm | R1, 2.210001 mm | no |
| R3 | (86.000,66.000); 0 | (85.275,66.000) / (86.725,66.000) | (85.150,66.000) / (86.850,66.000) | (85.275,66.000); (86.725,66.000) x3 | PASS, 4/4 | opposing pad, 0.800001 mm | C8, 1.210001 mm | no |
| R4 | (90.000,66.000); 0 | (89.275,66.000) / (90.725,66.000) | (89.150,66.000) / (90.850,66.000) | (89.275,66.000), (90.725,66.000) | PASS, 2/2 | opposing pad, 0.800001 mm | C8, 1.210001 mm | no |
| R8 | (40.000,35.000); 0 | (39.275,35.000) / (40.725,35.000) | (39.150,35.000) / (40.850,35.000) | (39.275,35.000), (40.725,35.000) | PASS, 2/2 | opposing pad, 0.800001 mm | R9, 3.410001 mm | no |
| R9 | (46.000,35.000); 0 | (45.275,35.000) / (46.725,35.000) | (45.150,35.000) / (46.850,35.000) | (45.275,35.000), (46.725,35.000) | PASS, 2/2 | opposing pad, 0.800001 mm | R8, 3.410001 mm | no |

The old endpoints sit `0.125 mm` inward from the new centres, leaving `0.325 mm` to the axial pad edge; a 0.250-mm track has `0.275 mm` transverse margin within a 0.800-mm-wide pad. No routed width approaches the proposed pad width.

Nearby via edge gaps (mm) are: R1 `0.300001` GND and `1.498878` Q1_GATE; R2 `2.300001` GND; R3 `2.300001` BAT_SENSE; R4 `2.300001` GND; R8 `0` GND and `2.400001` E220_M1; R9 `0` GND, `0.400001` E220_M1, and `2.900001` GND. The zero gaps are valid same-net connections. Nearest different-net filled F.Cu zone gaps are R1 `8.495327`, R2 `5.134106`, R3 `14.662626`, R4 `18.471320`, R8 `9.155798`, and R9 `14.977274 mm`; no F.Cu zone is within 3 mm. No courtyard overlap is introduced.

## Mask, paste, graphics, and routing disposition

V10 gives no mask-defined/NSMD rule, mask expansion, mask dam, stencil thickness, or paste-aperture reduction. The current pads explicitly retain `F.Cu`, `F.Mask`, and `F.Paste`; board mask expansion and paste margin/ratio are zero. The proposed 1:1 copper/mask/paste rectangles therefore each have `0.800 mm` inner separation: no mask bridge or paste interaction is introduced. Keep global rules unchanged. Numerically inspect F.Cu/F.Mask/F.Paste Gerbers only after approved implementation; this plan authorizes no release output.

Keep F.Fab unchanged (`1.600 x 0.800 mm` body) and F.CrtYd unchanged (`2.600 x 1.800 mm`). The product sheets support the Fab body envelope; V10 specifies no courtyard. The courtyard has zero axial margin beyond the planned land span, but the candidate has no courtyard overlap, so this is a retained, non-blocking scope boundary rather than a reason to alter graphics.

Routing-delta allowlist: **empty**. No track endpoint, segment, width, layer, via, zone, keepout, return path, or route may change. Only the two pad centres/sizes in each named embedded footprint are permitted.

## Scope and provenance disposition

The planner's retained `analysis/baseline/esp32-e220.kicad_pcb` is not byte-identical to the stated `5f068c20e2bd7cce1e02133a1115a4397a630c55`: it differs from the active/commit board only in four U4 pad net-token orderings and one U4 zone-fill vertex, outside this scope. This is a retained-snapshot discrepancy, not an electrical or geometric contradiction. The active board is byte-identical to the approved commit; I regenerated and refilled the reviewer candidate directly from it, with the same PASS result. Preserve this note with the plan; do not treat the old copied snapshot as the transaction input.

The future controlled transaction is correctly limited to `hardware/generate_stage7_footprints.py`, `hardware/esp32-e220.pretty/Resistor_0603_1608Metric.kicad_mod`, only the embedded `R1/R2/R3/R4/R8/R9` pads in `hardware/esp32-e220.kicad_pcb`, and a focused resistor invariant/checker (plus focused test if needed). `hardware/esp32-e220.kicad_sch` remains unchanged. The generic procurement rule remains conditional: R1/R2/R8/R9 need a standard two-terminal 0603/1608 body/termination envelope compatible with this land pattern; exclude 0402, 0805, and non-standard/special-terminal 0603. No generic-package PASS is assigned here.

SCOPE VERDICT: RESISTOR PHYSICAL PLAN PASS

REVIEW PASS
