# Rev.1 pre-production bounded PCB evidence audit

Scope: current active PCB/schematic, exact package/land-pattern facts, PTH/SMT DFM facts, current filled-zone evidence, and deterministic gates. No design files changed; no production outputs generated.

## Baseline facts

FACT: `esp32-e220.kicad_pcb` SHA-256 is `0ed5189dcfb6a21822b05246acee0257cd03415e07cdea919861375e0d5d6c70`; 37 footprints, 200 tracks, 58 vias, four zones, one rule area, 2 copper layers, 145 x 90 mm.
SOURCE: `sha256.txt`; `board-contract.txt`.
CLASSIFICATION: MATCH.
IMPACT: Current PCB matches the requested completed electrical/routing baseline.

FACT: Native DRC reports 0 violations and 0 unconnected items; parity reports PASS (37 schematic assembled / 37 PCB, R10/R11 intentional `NO_FOOTPRINT_DNP`); ERC report has no findings. Contract with protected reference `10-active-pre-implementation.kicad_pcb` passes.
SOURCE: `native-drc.json`, `parity.json`, `native-erc.rpt`, `board-contract.txt`.
CLASSIFICATION: MATCH.
IMPACT: No deterministic electrical or geometric blocker was found in the fresh baseline.

## Footprint / land-pattern facts

FACT: U1 is RGT0016C VQFN: PCB has 16 perimeter pads 0.60 x 0.24 mm, 0.50-mm pitch, 1.68 x 1.68-mm exposed pad and a 1.55 x 1.55-mm F.Paste aperture. The two post-routing GND vias are outside the exposed pad.
SOURCE: `hardware/esp32-e220.kicad_pcb` U1 footprint; TI TPS62133 Rev. F package/land-pattern drawing, https://www.ti.com/lit/ds/symlink/tps62133.pdf.
CLASSIFICATION: MATCH.
IMPACT: Perimeter and exposed-pad copper geometry matches TI's current RGT example. The paste aperture is an 85.9% single opening; TI's package drawing does not prescribe its segmentation. Confirm paste-release behaviour on the first article; no geometry change is evidenced by this audit.

FACT: U4 is a three-electrical-pad / four-lead representation of TI DCY SOT-223: pad 1, small pad 2 and large tab pad 2, pad 3; the board electrically maps tab and output lead to AUX_3V3.
SOURCE: `hardware/esp32-e220.kicad_pcb` U4 footprint and current parity result; TI TLV1117LV33DCYR product data, https://www.ti.com/product/TLV1117LV/part-details/TLV1117LV33DCYR.
CLASSIFICATION: EXPECTED REPRESENTATION DIFFERENCE.
IMPACT: TI calls DCY a four-lead package; KiCad's duplicate pad-2 tab representation is correct and passes the duplicate-pad-net contract.

FACT: U3 DBV SOT-23-5 copper pads in the active board are 0.60 x 0.80 mm on the TI-named footprint, at the correct 0.95-mm centre-line spacing.
SOURCE: `hardware/esp32-e220.kicad_pcb` U3 footprint.
CLASSIFICATION: REAL MISMATCH.
IMPACT: TI's current DBV0005A land-pattern example for SN74AHCT1G125 specifies five 0.60 x 1.10-mm pads at the same 0.95-mm spacing: https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf. This is a manufacturing-critical land-pattern mismatch. Copper/footprint edits are prohibited in this audit, so this is a PRE-PRODUCTION BLOCKER requiring a separately authorized electrical/footprint transaction and review.

FACT: L1 copper pads are 0.98 x 3.40 mm on 3.35-mm centres, exactly as stated in the local Coilcraft XFL4020-222MEB footprint description.
SOURCE: `hardware/esp32-e220.kicad_pcb` L1 footprint; Coilcraft XFL4020 current product/datasheet, https://www.coilcraft.com/en-us/products/power/high-voltage-inductors/xfl/xfl4020/xfl4020-222/.
CLASSIFICATION: MATCH.
IMPACT: No local L1 copper discrepancy found.

FACT: Q1 is a SOT-23 footprint with three 0.80 x 0.90-mm pads; F1 is 1812 with 1.125 x 3.40-mm pads; D3 is DO-214AA/SMBJ with 2.50 x 2.30-mm pads; 0603 resistor and Murata capacitor footprints have F.Cu/F.Mask/F.Paste pads and native DRC finds no mask/courtyard/geometry finding.
SOURCE: `hardware/esp32-e220.kicad_pcb`; Diodes DMP3130LQ-7 is SOT-23, https://www.diodes.com/_files/datasheets/DMP3130LQ.pdf; Littelfuse 1812L200/16 data, https://www.littelfuse.com/~/media/electronics/datasheets/resettable_ptcs/littelfuse_ptc_1812l_datasheet.pdf.pdf.
CLASSIFICATION: INCONCLUSIVE.
IMPACT: Package families match the named manufacturer parts, but the relevant manufacturer recommended-land-pattern PDFs for Q1/F1/D3 and the project-local Murata passive land patterns were not embedded or version-pinned in the project; no exact manufacturer-pad comparison can be made from the current controlled evidence.

## PTH facts

FACT: J1/J2/J3/J5 use 1.040-mm drills with 1.70-mm circular copper pads (0.330-mm radial annular ring). J4/J8 use 1.000-mm drills with 1.70 x 2.00-mm pads (0.350-mm minimum radial ring). J6/J9 use 1.000-mm drills with 1.70-mm pads (0.350-mm radial ring). TP1...TP5 use 1.000-mm drills with 2.00-mm pads (0.500-mm radial ring). All use `*.Cu` and `*.Mask`.
SOURCE: `hardware/esp32-e220.kicad_pcb` footprint pad definitions.
CLASSIFICATION: MATCH.
IMPACT: Actual PTH geometry matches the stated design concepts, provides substantial annular ring for ordinary low-cost fabrication and hand rework, and has no native DRC finding.

FACT: JP1 footprint geometry is the same 1.00-mm drill / 1.70-mm copper 2.54-mm PTH header class; Samtec TSW-102-07-G-S is a 0.635-mm square-post 2.54-mm through-hole header.
SOURCE: `hardware/esp32-e220.kicad_pcb`; Samtec current product page, https://www.samtec.com/products/tsw-102-07-g-s?v=2.
CLASSIFICATION: MATCH.
IMPACT: Nominal hole clearance to the specified 0.635-mm post is 0.365 mm before plating; no fit blocker is evidenced.

FACT: JST lists B2B-XH-A in the XH series at 2.50-mm pitch; active J4/J8 use that pitch and PTH geometry.
SOURCE: `hardware/esp32-e220.kicad_pcb`; JST XH primary catalogue, https://www.jst-mfg.com/product/pdf/eng/eXH.pdf.
CLASSIFICATION: MATCH.
IMPACT: No pitch/footprint-family conflict found.

## Zones / access / assembly facts

FACT: Current board retains 8 x 10-mm F.Cu AUX_3V3 zone, one F.Cu GND buck zone, two B.Cu GND zones, and named `ESP32_ANTENNA_EXCLUSION`; fresh contract reports no antenna hits and native DRC has zero zone errors.
SOURCE: `hardware/esp32-e220.kicad_pcb`; `board-contract.txt`; `native-drc.json`.
CLASSIFICATION: MATCH.
IMPACT: No fresh isolated-zone or rule-area finding. Earlier final-routing proof identifies U1 GND pads/vias in the local F.Cu GND polygon joined to global B.Cu GND and the E220 local return stub joined to B.Cu GND; see `hardware/evidence/rev1-final-5-airwire-2026-08-21/implementation-handoff.md`.

FACT: The board has no mounting-hole or battery strain-relief footprint. Battery, switch, JP1, module sockets, SMA side, OLED socket, J6/J9 headers, and TP1...TP5 are present on the bare PCB.
SOURCE: `hardware/esp32-e220.kicad_pcb` footprint inventory and drawing geometry.
CLASSIFICATION: EXPECTED REPRESENTATION DIFFERENCE.
IMPACT: Consistent with the requested Rev.1 enclosure/first-article deferral; enclosure-dependent access and harness retention remain FIRST-ARTICLE RISKS, not bare-PCB blockers.

FACT: Current active PCB has no `Manufacturer`, `MPN`, or `AssemblyClass` footprint properties. J3 Value currently says `E220-400T22D / E220-900T22D SOCKET`; J1/J2/J5/JP1 Values encode the desired Samtec identities; TP1...TP5 are physical `TestPoint_THT_1p0mm_PROTOTYPE` holes and R10/R11 are already `NO_FOOTPRINT_DNP` in parity.
SOURCE: `hardware/esp32-e220.kicad_pcb`; `parity.json`; `hardware/check_schematic_pcb_sync.py`.
CLASSIFICATION: STALE DATA.
IMPACT: Release-metadata cleanup is required before a deterministic production-metadata checker can pass. Expected classification counts implied by the current 37 footprints are 30 PCBA_POPULATE, 2 DNP_USER (J6/J9), 5 PLATED_TEST_HOLE (TP1...TP5), plus 2 NO_FOOTPRINT_DNP (R10/R11); the user-installed ESP32/E220/OLED modules are not PCB footprints.

FACT: Title block still says `SIGNAL ROUTING INCOMPLETE / NOT FOR PRODUCTION`; Dwgs.User still includes `D2 LAND PATTERN = PCB RELEASE BLOCKER` and `SIGNAL ROUTING PENDING`.
SOURCE: `hardware/esp32-e220.kicad_pcb` lines 12, 6854, 6953.
CLASSIFICATION: STALE DATA.
IMPACT: Allowed status/silkscreen cleanup is required; it must not be treated as an electrical/copper change.

## Disposition

BLOCKER: U3 DBV land-pattern pad length is 0.80 mm versus TI's 1.10-mm current example. This cannot be corrected during the metadata-only audit.

FIRST-ARTICLE RISKS: U1 single 85.9% EP paste opening requires process observation; no enclosure datum exists for mounting, battery strain relief, or final module/harness access; OLED body fit remains unverified.
