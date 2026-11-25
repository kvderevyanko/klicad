# Passive and D3 standard-derived footprint audit

Date: 2026-09-16. Read-only evidence audit. No controlled design, generator,
footprint, routing, Gerber, release, commit, or push was changed.

FACT: The controlled BOM identifies D3 as Littelfuse `SMBJ10CA`; this audit does not assume a PCBWAVE substitution. Littelfuse's primary SMBJ series drawing identifies `SMBJ10CA` as a bidirectional (`CA`) DO-214AA / SMB J-bend TVS. Package limits are body B=4.060..4.750, C=3.300..3.940, A=1.930..2.200; lead D=1.990..2.610, E=0.760..1.520, F=0..0.203; overall G=5.210..5.590 and standoff H=0.152..0.305 mm. The cathode band is explicitly only for unidirectional products; `SMBJ10CA` has no electrical polarity requirement.

SOURCE: Littelfuse, *Surface Mount – 600W, SMBJ series*, official primary PDF `https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_smbj_datasheet.pdf.pdf`, package table and `SMBJ10CA` electrical table; controlled BOM `hardware/production-metadata.json`.

CLASSIFICATION: MATCH for MPN, package, and bidirectional-polarity facts.

IMPACT: D3 pad 1=`BAT_FUSED`, pad 2=`GND` remains a traceability mapping, not a diode-orientation constraint.

FACT: D3 project-local and embedded copper are two 2.500 x 2.300 mm pads centred at (-2.150,0)/(+2.150,0) mm: 4.300 mm pitch and 1.800 mm inner copper gap. The retained export audit records the same F.Cu/IPC-D-356 geometry (the reported IPC dimensions differ only by inch-report quantization). The primary Littelfuse SMBJ source supplies package dimensions but no recommended PCB land dimensions.

SOURCE: `hardware/esp32-e220.pretty/Littelfuse_SMBJ10CA_DO214AA.kicad_mod`; `hardware/esp32-e220.kicad_pcb`; `hardware/evidence/full-production-audit-2026-09-15/passive-power-primary-audit.md`; Littelfuse source above.

CLASSIFICATION: INCONCLUSIVE for land-pattern approval.

IMPACT: No numeric manufacturer-land delta or `MANUFACTURER LAND PATTERN PASS` is supportable. The active D3 footprint must not change solely to obtain a label.

FACT: Murata `GRM188R71C104KA01D`, `GRM1885C1H332JA01D`, and `GRM188R61A106MAAL` are GRM 18-size / 1608 metric MLCCs; `GRM21BR61E106KA73` and `GRM21BR61A226ME44` are GRM 21-size / 2012 metric MLCCs. Murata's public primary catalog identifies the corresponding nominal case envelopes as 1.6 x 0.8 mm (18) and 2.0 x 1.25 mm (21). The exact-MPN detailed-specification sheets remain inaccessible from Murata's protected endpoint; the available primary source does not establish their exact terminal-length/terminal-thickness tolerances.

SOURCE: Murata primary catalog *Chip Monolithic Ceramic Capacitors for Automotive*, `https://go.murata.com/rs/382-MEZ-125/images/AS_2015-008_Continental-2015-2_Email-Thanks_Leaflet_202.pdf`, Table 2 and case tables; exact MPN list `hardware/production-metadata.json`; access result recorded in `hardware/evidence/full-production-audit-2026-09-15/passive-power-primary-audit.md`.

CLASSIFICATION: INCONCLUSIVE for exact-MPN terminal-tolerance confirmation.

IMPACT: The case-size identity is primary-source supported; a claim that every exact MPN terminal tolerance has been verified would not be supported by the retained primary evidence.

FACT: The same Murata primary catalog's reflow Table 2 explicitly covers `GQM/GR3/GRJ/GRM Series 18 size` and `GC3/GCD/GCE/GCJ/GCM Series 21 size`; it gives an `a/b/c` recommended-land range of 0.6..0.8 / 0.6..0.7 / 0.6..0.8 mm for 18 and 1.0..1.2 / 0.6..0.7 / 0.8..1.1 mm for 21. Its figure labels the three dimensions but the retained text extract does not preserve a machine-readable mapping from `a/b/c` to pad X, pad Y, and inner gap. The catalog also says its data are typical and requires approval-sheet/product-specification confirmation before ordering.

SOURCE: Murata catalog above, page 65, Table 2, lines 7072..7159 in the primary retrieval; source caveat lines 7200..7201.

CLASSIFICATION: INCONCLUSIVE for a numerical pad-by-pad comparison.

IMPACT: It would be unsafe to assign the three range columns to board axes from memory or infer them from the existing footprint. Therefore this source does not establish a `MANUFACTURER LAND PATTERN PASS` for the exact GRM MPNs.

FACT: Current GRM188 lands are 0.950 x 1.000 mm, centres (-0.725,0)/(+0.725,0): pitch 1.450 mm and inner gap 0.500 mm. Current GRM21 lands are 1.150 x 1.400 mm, centres (-1.000,0)/(+1.000,0): pitch 2.000 mm and inner gap 0.850 mm. Retained Gerber/IPC-D-356 evidence records the same dimensions; all are nonpolar two-terminal MLCCs. The relevant net mapping is C2 `BUCK_IN/GND`, C4 `SS_TR/GND`, C5/C6/C7 `5V_SYS/GND`, C8 `BAT_SENSE/GND`, C1/C3/C9 `5V_SYS/GND`, C10 `AUX_3V3/GND`.

SOURCE: `hardware/esp32-e220.pretty/Murata_GRM188_1608Metric.kicad_mod`; `hardware/esp32-e220.pretty/Murata_GRM21_2012Metric.kicad_mod`; active PCB; prior retained export evidence in `hardware/evidence/full-production-audit-2026-09-15/passive-power-primary-audit.md`.

CLASSIFICATION: MATCH between project-local, embedded, and retained Gerber/IPC representation.

IMPACT: This only proves export fidelity and pin/net mapping; it is not independent standard or manufacturer-land approval.

FACT: Yageo exact MPN primary sheets for `RC0603FR-0710KL` and `RC0603FR-073K3L` state 0603 / 1608, two terminals, L=1.60 +/-0.10, W=0.80 +/-0.10, T=0.45 +/-0.10, B1/B2=0.25 +/-0.15 mm; neither publishes a recommended PCB land pattern. The current footprint is 0.950 x 1.000 mm pads at (-0.725,0)/(+0.725,0), 1.450 mm pitch, 0.500 mm inner gap. R3 maps pad 1/2=`BUCK_IN/BAT_SENSE`; R4 maps pad 1/2=`BAT_SENSE/GND`; both are nonpolar.

SOURCE: retained primary manufacturer sheets `hardware/evidence/full-production-audit-2026-09-15/primary/yageo-rc0603fr-0710kl.html` and `yageo-rc0603fr-073k3l.html`; `hardware/esp32-e220.pretty/Resistor_0603_1608Metric.kicad_mod`; active PCB; prior retained export evidence in `hardware/evidence/full-production-audit-2026-09-15/passive-power-primary-audit.md`.

CLASSIFICATION: INCONCLUSIVE for land-pattern approval; MATCH for exact package and pin/net facts.

IMPACT: Yageo package data alone cannot yield toe, heel, side, fabrication, or placement allowances.

FACT: No licensed/reproducible IPC-7352 or IPC-7351B normative table, formula, density level, fabrication tolerance, placement tolerance, or toe/heel/side allowance record exists in this repository. No accessible primary IPC material was found that contains those numerical derivation inputs. KiCad/project descriptions call these pads “project IPC nominal”, but do not record a standard revision, calculation, or allowances; therefore they are not an independent standard basis.

SOURCE: repository search for `IPC-7352`, `IPC-7351B`, and footprint derivation records; local footprint descriptions above; U4 standard-basis evidence `hardware/evidence/standard-derived-footprint-audit-2026-09-16/u4-tlv1117lv33dcyr-standard-derived-audit.md` documents the same controlled absence.

CLASSIFICATION: INCONCLUSIVE.

IMPACT: A `STANDARD-DERIVED LAND PATTERN PASS` cannot truthfully be issued for D3, Murata GRM, or Yageo RC0603. Required closure is an organization-licensed/citable IPC extract or versioned calculation record specifying standard revision, density, package inputs, fabrication/placement tolerances, all resulting numeric allowances, and the target pad dimensions; then a fresh numeric Gerber comparison can be made.

AUDIT INCONCLUSIVE
