# Passive and power SMD primary-source audit

Read-only audit, 2026-09-15.  Scope: populated C1--C10, R1--R4/R8/R9,
L1, D3 and F1.  The controlled PCB, project-local `*.pretty` footprint, and
the retained Q1/U3 correction F.Cu Gerber / IPC-D-356 all agree for the
geometry and pad/net chains recorded below.  That is a representation check;
the disposition is based on the cited manufacturer source, not that agreement.

## Exact numeric evidence

| Ref(s) / MPN | primary manufacturer source | manufacturer physical / land data, mm | local PCB and released Gerber / IPC-D-356 | pad/net check | disposition |
|---|---|---|---|---|---|
| L1 / Coilcraft `XFL4020-222MEB` | Coilcraft XFL4020, Document 745-3 Rev. 03/10/26, retained `primary/coilcraft-xfl4020.pdf`, p.3 screenshot `primary/coilcraft-xfl4020-page-3.png` | body 4.00 +/-0.30 x 4.00 +/-0.30, height 2.10 max; terminal length 3.25 typ, terminal width 1.57 +/-0.25; **recommended land:** two 0.98 x 3.40 lands, 2.37 inner gap, hence 3.35 centres. Dash identifies terminal direction/start (short) lead. | pads 1/2: 0.98 x 3.40, centres (-1.675,0)/(+1.675,0): each dimension delta 0.00, pitch delta 0.00. F.Cu flashes / IPC dimensions agree (`X0386Y1339`, 0.98 x 3.40). | 1 -> `BUCK_SW`; 2 -> `5V_SYS`; PCB/schematic parity PASS, Gerber X2 / IPC match. Footprint pin-1 marker is the Coilcraft dash. | **MANUFACTURER-LAND-PATTERN PASS** |
| F1 / Littelfuse `1812L200/16` | Littelfuse *PolySwitch Resettable PPTC, 1812L Series*, Rev. GD 06/10/24, official URL `https://www.littelfuse.com/~/media/electronics/datasheets/resettable_ptcs/littelfuse_ptc_1812l_datasheet.pdf.pdf`, pp.2,6. The official PDF endpoint returned HTTP 403 to retained-file retrieval; its primary indexed text is retained by the audit log/source URL, not substituted with a third-party copy. | exact MPN listed: 2.00-A hold, 16-V; body A=4.37..4.73, B=3.07..3.41; terminal C=0.40..0.70, D=0.30..1.20, E=0.15..0.65. **Recommended pad layout:** F=1.78 pad X length, G=3.45 **inner-edge to inner-edge** gap, H=3.15 pad Y height. Required centre pitch is F+G=5.23; centres are X=+/-2.615. | pads 1/2: 1.125 x 3.40, centres +/-2.1375, pitch 4.275. The controlled PCB and released Gerber/IPC agree (`X0443Y1339`, 1.125 x 3.40). Required minus current: pad X +0.655; pad Y -0.250; centre pitch +0.955; each pad centre must move outward by 0.4775. | 1 -> `BAT_PLUS`; 2 -> `BAT_FUSED`; PCB/schematic parity PASS; Gerber/IPC match current, wrong geometry. PPTC is non-polarized. | **FAIL — REAL MISMATCH** |
| D3 / Littelfuse `SMBJ10CA` | Littelfuse *SMBJ Series*, official URL `https://m.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_smbj_datasheet.pdf.pdf`; current official series drawing identifies DO-214AA (SMB J-bend): body B=4.06..4.75, C=3.30..3.94, height A=1.93..2.20; terminal D=1.99..2.61, E=0.76..1.52, G=5.21..5.59. | Two local pads 2.50 x 2.30, centres +/-2.15, 4.30 pitch; controlled PCB / F.Cu Gerber / IPC agree (`X0984Y0906`, 2.50 x 2.30). No exact manufacturer SMBJ10CA numerical recommended-pad source has been retained/verified in this audit, so a land delta cannot truthfully be asserted. | 1 -> `BAT_FUSED`; 2 -> `GND`; parity and Gerber/IPC PASS. `CA` is bidirectional: Littelfuse specifies cathode band only for unidirectional products; no cathode/orientation requirement applies to `SMBJ10CA`. Pads still retain numbers/nets for traceability. | **UNVERIFIED — manufacturer land pattern absent from retained primary evidence** |
| C2,C6,C7,C8 / Murata `GRM188R71C104KA01D`; C4 / `GRM1885C1H332JA01D`; C5 / `GRM188R61A106MAAL` | Murata official product family/package convention: GRM188 is 1608M / 0603 (1.6 x 0.8 nominal). Murata primary S-parameter page `https://www.murata.com/en-global/tool/data/sparameterdata/sparameter-mlcc/condition` records an **original measurement** land structure for 1608 as a=0.8, b=0.7, c=0.8; it is not stated to be the MPN mounting recommendation. Exact-MPN detailed-specification sheets were not retrievable from Murata's 403-protected PDF endpoint. | Two pads 0.95 x 1.00, centres +/-0.725 (1.45 pitch); PCB / F.Cu Gerber / IPC agree (`X0374Y0394`, 0.95 x 1.00). No manufacturer-recommended pad coordinate/dimension has been obtained; no numerical land delta is valid. | all 2 pads, parity/Gerber/IPC PASS: C2 `BUCK_IN/GND`; C4 `SS_TR/GND`; C5--C7 `5V_SYS/GND`; C8 `BAT_SENSE/GND`. MLCC has no polarity. | **UNVERIFIED — no exact-MPN manufacturer land pattern** |
| C1,C9,C10 / Murata `GRM21BR61E106KA73`; C3 / `GRM21BR61A226ME44` | Murata GRM21 is 2012M / 0805 (2.0 x 1.2 nominal). Same official Murata primary page records a 2012 measurement-land structure a=1.2, b=0.7, c=1.1, not a mounting recommendation; exact-MPN detailed sheets not retrievable from Murata's 403-protected PDF endpoint. | Two pads 1.15 x 1.40, centres +/-1.00 (2.00 pitch); PCB / F.Cu Gerber / IPC agree (`X0453Y0551`, 1.15 x 1.40). No manufacturer-recommended pad coordinate/dimension obtained; no numerical land delta is valid. | all 2 pads, parity/Gerber/IPC PASS: C1 `BUCK_IN/GND`; C3 `5V_SYS/GND`; C9 `5V_SYS/GND`; C10 `AUX_3V3/GND`. MLCC has no polarity. | **UNVERIFIED — no exact-MPN manufacturer land pattern** |
| R3 / Yageo `RC0603FR-0710KL`; R4 / `RC0603FR-073K3L` | Exact current Yageo one-page manufacturer sheets retained as `primary/yageo-rc0603fr-0710kl.html` and `primary/yageo-rc0603fr-073k3l.html` (both are PDF content). Each says 0603/1608, 2 terminals, L=1.60 +/-0.10, W=0.80 +/-0.10, T=0.45 +/-0.10, B1/B2=0.25 +/-0.15. Neither gives a recommended PCB land pattern. | Two pads 0.95 x 1.00, centres +/-0.725 (1.45 pitch); PCB / F.Cu Gerber / IPC agree (`X0374Y0394`, 0.95 x 1.00). The body/package is a match, but source has no pad coordinate/dimension to compare. | R3 1/2 -> `BUCK_IN/BAT_SENSE`; R4 1/2 -> `BAT_SENSE/GND`; parity/Gerber/IPC PASS. Resistors have no polarity. | **UNVERIFIED — physical case verified, manufacturer land pattern absent** |
| R1,R2,R8,R9 / `APPROVED_GENERIC` 0603 | No actual manufacturer MPN, approved-vendor part, or factory purchasing confirmation exists in the controlled BOM; therefore no primary manufacturer source identifies the physically installed part. | Contract only says `0603 / 1608`; current footprint is two 0.95 x 1.00 pads at 1.45 centres. A GENERIC-PACKAGE PASS requires the factory's actual selected MPN and its manufacturer package data. | PCB / Gerber / IPC agree (`X0374Y0394`, 0.95 x 1.00). | R1 `Q1_GATE/GND`; R2 `BUCK_IN/Q1_GATE`; R8 `E220_M0/GND`; R9 `E220_M1/GND`; parity/Gerber/IPC PASS. | **UNVERIFIED — factory part not identified; GENERIC-PACKAGE PASS cannot be issued** |

## Coilcraft availability and compatible-footprint fact

Coilcraft's current XFL4020 data sheet says the legacy packaging code `B` is
being eliminated in favour of `C`; it lists `D` (13-inch reel) as factory
order / not stocked.  That does **not** authorize a BOM substitution.  The
same manufacturer page names `XGL4020-222ME_` as drop-in replacement, but any
candidate must still be ordered/electrically approved.  A compatible physical
replacement must at minimum retain the validated XFL pad geometry (two 0.98 x
3.40 mm lands, 3.35-mm centres), 4.00 +/-0.30-mm square envelope and terminal
1/start-lead dash orientation; board L1 pad 1 is `BUCK_SW` and must be the
high-dv/dt/start lead.

## Required controlled-design consequence

F1 is a documented physical footprint mismatch.  No controlled source has
been edited in this read-only audit.  Any correction must start with the
required geometry above, update `generate_stage7_footprints.py` and the local
footprint/embedded board in the prescribed physical transaction, reroute if
needed, and regenerate a new Gerber/IPC-D-356 before it can be re-audited.

## CONTEXT PROVENANCE CONFLICT — F1 datum correction

The preceding revision of this report at
`hardware/evidence/full-production-audit-2026-09-15/passive-power-primary-audit.md`
misread dimension G in the Littelfuse primary drawing as a centre pitch.
The authoritative primary path is Littelfuse's 1812L drawing at
`https://www.littelfuse.com/~/media/electronics/datasheets/resettable_ptcs/littelfuse_ptc_1812l_datasheet.pdf.pdf`;
its layout callouts identify F and H as pad dimensions and G as the
inner-edge gap.  Therefore the required pitch is 1.78 + 3.45 = 5.23 mm,
not 3.45 mm.  This is a correction to the required geometry and increases
the mismatch; it does not change the `REAL MISMATCH` classification.

AUDIT INCONCLUSIVE
