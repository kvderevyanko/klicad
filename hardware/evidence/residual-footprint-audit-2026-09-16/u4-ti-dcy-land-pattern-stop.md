# U4 TI DCY land-pattern comparison — STOP handoff

Date: 2026-09-16
Scope: `U4` only.  The controlled PCB, schematic, generators, local footprint,
production metadata, routing, and released production files were not changed.

## Primary evidence

1. TI `TLV1117LV` datasheet `SBVS160C`, page 21, package drawing
   `MPDS094A` / `4202506/B`: `TLV1117LV33DCYR` is `DCY`, four-pin
   `SOT-223`; pin 1 = GND, pin 2 and tab = OUT, pin 3 = IN.  The package
   drawing says it falls within JEDEC `TO-261` variation `AA`.
2. TI `LAND PATTERN DATA`, drawing `4210278/C` (07/2013), headed
   `DCY (R-PDSO-G4) PLASTIC SMALL-OUTLINE`: official TI example board layout
   and 0.125-mm-stencil example.  It gives 0.95 x 2.15 mm lead lands,
   3.25 x 2.15 mm tab land, 2.30-mm lead pitch, 5.80-mm lead-row to tab-row
   centre spacing, and 0.07-mm maximum all-around NSMD mask expansion.

The current TLV1117LV datasheet does not embed drawing `4210278/C`; TI's
package search advertises package footprint information, and the dated TI
package-land drawing is the applicable primary source for the same DCY
R-PDSO-G4 package.  The TI CAD link through Ultra Librarian was not used:
the previously retained public preview is an unrelated `YDC4` 2x2 footprint
(`CONTEXT PROVENANCE CONFLICT` in
`hardware/evidence/d3-murata-u4-manufacturer-reaudit-2026-09-16/u4-ti-ultralibrarian-crosscheck.md`).

Primary URLs:

- `https://www.ti.com/lit/pdf/sbvs160`
- `https://www.ti.com/lit/ds/symlink/lm2940c.pdf` (TI DCY package family)
- `https://www.ti.com/packaging/docs/searchproductbypackage.tsp`

`primary/ti-lm2940c-dcy-land-pattern.pdf` is retained from TI for the same
DCY mechanical drawing.  It confirms `MPDS094A/4202506/B`; it does not
replace drawing `4210278/C` as the numerical land-pattern source.

## Numeric comparison

TI drawing axes have the three leads horizontally below the tab.  The project
placement is its 90-degree rotation: therefore dimensions below are expressed
in the project-local axes (`x` lead/tab row direction; `y` lead pitch).

| Feature | Current controlled copper | TI 4210278/C rotated to project axes | Delta current - TI |
|---|---:|---:|---:|
| pins 1/2/3 lead land | 2.00 x 1.50 mm | 2.15 x 0.95 mm | -0.15 x +0.55 mm |
| tab land (pin 2) | 2.00 x 3.80 mm | 2.15 x 3.25 mm | -0.15 x +0.55 mm |
| lead pitch | 2.30 mm | 2.30 mm | 0.00 mm |
| lead-row to tab-row centres | 6.30 mm | 5.80 mm | +0.50 mm |
| lead/tab local row centres | -3.15 / +3.15 mm | -2.90 / +2.90 mm | -0.25 / +0.25 mm |

The current lead pads are wider than TI's example and 0.15 mm shorter in the
orthogonal direction; the current tab is 0.55 mm longer in its width direction
and 0.15 mm shorter in the orthogonal direction.  The 0.50-mm row-spacing
difference means this is not merely a mask or corner-radius difference.

## Required disposition

`U4: FAIL` for **manufacturer-land-pattern conformance**.  The package,
pin mapping, duplicate pad-2 tab connection, and board/schematic nets remain
verified, but the current copper does not numerically equal TI drawing
`4210278/C`.  This handoff makes no claim that the existing KiCad geometry is
unmountable; it must not be labelled `MANUFACTURER LAND PATTERN PASS` or
`ENGINEERING-FIT PASS` in place of the published applicable TI pattern.

## Proposed fix — not applied

Use a DCY-specific footprint transaction only after an electrical/layout owner
and independent reviewer approve it.  The source-based candidate is:

- pins 1/2/3: centres `(-2.90, -2.30)`, `(-2.90, 0)`,
  `(-2.90, +2.30)` mm; copper `2.15 x 0.95` mm;
- tab, pad 2: centre `(+2.90, 0)` mm; copper `2.15 x 3.25` mm;
- non-solder-mask-defined copper with the TI 0.07-mm all-around mask detail,
  and a separately reviewed paste aperture.

Before any mutation: baseline contract PASS, named backup, full physical plan
and reviewer plan gate.  After a candidate only: contract, native DRC,
schematic/PCB parity, mask/courtyard/adjacent-copper review, Gerber, and
IPC-D-356 checks.  Do not reuse the contradictory Ultra Librarian preview.
