# Independent physical plan gate, PCBWAVE 2608134199

Baseline board SHA-256 ff45f781b00e9a79451786dd18a8eae540c6f738ec26be57046277a478f4321e. Scope documents are ../l1-plan/physical-plan.md (SHA-256 2f0f7700cbb73dd33bb6622a99ed7f6cd2d9fe99d90d37b545ac2eca64068ea6) and ../resistor-plan/physical-plan.md (bdef04d1acca692ecc98740b651571b086224fd34bb544791c8db147ca7ee6bc).

| Scope | Independent check | Physical delta |
|---|---|---|
| L1 | Coilcraft documents 745-3 and 1529-3 show witness lines through the centre of each shaded land. Pad pitch 2.37 mm, axial length 0.98 mm, width 3.40 mm. Mark the short/start lead at BUCK_SW. The preregistered protected checkpoint differs from baseline only in L1 pad positions. | Pads move 0.490 mm towards centre each. The proposed two local F.Cu endpoints enter their pads by 0.35 mm. Body and courtyard retain their envelope. |
| R2 | UNI-ROYAL V.3 p. 5 gives A 0.90 ±0.05, B 0.65 ±0.05, C 0.80 ±0.05 and D 2.10 ±0.05 mm. Simultaneous nominal dimensions are inconsistent. The selected A 0.875, B 0.625, C 0.800, D 2.125 satisfy all four intervals and D = A + 2B. | Dedicated pads are centred on 1.50 mm pitch. Existing track ends are 0.025 mm from new pad centres. |
| R8/R9 | Vishay 20035 p. 11 gives reflow gap 0.75, axial length 0.75, transverse width 1.00 and span 2.25 mm. | Dedicated pads on 1.50 mm pitch retain both routes to each resistor. |

pre-contract.json passes including protected and antenna checkpoints. pre-drc.json has zero geometry violations and zero unconnected items. Three independent all-severity DRCs with refill and all-track errors are plan-0.json (L1), plan-1.json (R2) and plan-2.json (R8/R9). Each has zero geometry and zero opens. All 20 native schematic parity markers matched baseline by type, message and UUID. The geometric plans retain neighbouring routes, copper return paths and mechanical access. Each physical change requires its own controlled step and implementation review.

SCOPE VERDICT: L1 PHYSICAL PLAN PASS

SCOPE VERDICT: R2 PHYSICAL PLAN PASS

SCOPE VERDICT: R8/R9 PHYSICAL PLAN PASS

REVIEW PASS
