# U4 TLV1117LV33DCYR DCY: standard-derived footprint audit

Date: 2026-09-16  
Scope: read-only evidence audit of U4 only.  No board, schematic, generator,
footprint, routing, Gerber, release, commit, or push was changed by this audit.

## Evidence and access state

| Evidence | Revision / access | What it establishes |
|---|---|---|
| TI `TLV1117LV` datasheet, `SBVS160C`, January 2023, retained as `../full-production-audit-2026-09-15/primary/ti-tlv1117lv.pdf` and `.txt` | Primary manufacturer source, locally retained and readable | Exact MPN family package table, top-view pinout, and embedded package drawing `MPDS094A` / `4202506/B`. |
| TI package drawing `MPDS094A`, `4202506/B`, June 2002, pages 15--16 of the same TI datasheet | Primary manufacturer source | DCY / R-PDSO-G4 mechanical envelope and terminal dimensions.  The drawing says it is JEDEC TO-261 variation AA. |
| `hardware/esp32-e220.kicad_pcb`, `hardware/esp32-e220.pretty/TI_TLV1117LV33DCYR_DCY_SOT223.kicad_mod`, and `hardware/generate_stage7_footprints.py` | Actual controlled design and project source-of-truth | Current local/embedded land coordinates, dimensions, Fab and courtyard. |
| `hardware/check_u4_dcy_footprint.py` run on 2026-09-16 | Reproducible project invariant, PASS | Local generator output equals local footprint; embedded footprint has the stated copper geometry and pin/net mapping. |
| `../full-production-audit-2026-09-15/u4-library-resolution/diagnostic-post/esp32-e220-post.d356` and `35-diagnostic-export-audit.json` | Retained diagnostic Gerber / IPC-D-356 evidence | Exported copper dimensions, centres and net mapping.  Its U4 copper was proven byte-identical to the identity-only U4 transaction's pre-export. |
| IPC-7352 / IPC-7351B | **Not available in this repository under a licensed/reproducible copy.** | No normative land-pattern table, density level, fabrication tolerance, placement tolerance, or toe/heel/side allowance values are accessible to this audit. |

TI does **not** publish a recommended PCB land pattern in `SBVS160C` or in
`MPDS094A/4202506/B`.  The project description accurately calls the present
pattern a frozen project IPC/KiCad pattern; it is not a TI land pattern.

The installed KiCad `SOT-223` library has geometrically similar copper, but it
is not used as a standard source or as proof: it provides no traceable
IPC-7352/IPC-7351B density-level calculation and no authoritative TI-DCY
terminal-to-land derivation.

## TI physical package facts

All dimensions are mm, from TI `MPDS094A/4202506/B`; tolerances are the drawing
limits, not inferred nominal values.

| Feature | TI value | Audit use |
|---|---:|---|
| Package | DCY, R-PDSO-G4, SOT-223, 4 pins | Exact package of `TLV1117LV33DCYR` in `SBVS160C`. |
| Mold body length | 6.30--6.70 | Project Fab length is 6.70. |
| Mold body width | 3.30--3.70 | Project Fab width is 3.70. |
| Lead-row pitch | 2.30 | Current pad-1 to pad-2 and pad-2 to pad-3 centre pitch is 2.30. |
| Lead width | 0.66--0.84 | Requires a documented IPC side allowance to derive a land width; none is available. |
| Lead contact length | 0.75 minimum | Requires a documented IPC heel/toe allowance to derive a land length; none is available. |
| Lead thickness | 0.23--0.35 | Package-fit fact; no land calculation without the standard's rules. |
| Standoff | 0.02--0.10 | Package-fit fact. |
| Overall height | 1.50--1.70, 1.80 maximum | Package-fit fact. |
| Pin identity | 1=GND; 2=OUT and tab; 3=IN | TI Figure 5-1 and Table 5-1. |

The drawing also gives the tab and lead outline, but does not turn that outline
into a board-land recommendation.  In particular, it supplies neither a tab
land size nor terminal-specific toe, heel, and side fillet targets.

## Current land pattern and export comparison

Footprint origin is `(20.650, 27.000)` mm, rotation `0 degrees`.  Local axes
are the footprint axes; the three small lead lands are vertically spaced in
this board orientation.  `F.Fab` is `x=-1.850..+1.850`,
`y=-3.350..+3.350` (3.70 x 6.70 mm); the project courtyard is
`x=-4.400..+4.400`, `y=-3.600..+3.600`.

| Physical terminal | Footprint pad / local centre mm | Project copper mm | IPC-D-356 centre / copper inch | Numeric delta to Gerber | Schematic net |
|---|---|---:|---|---:|---|
| pin 1, GND lead | `1`, `(-3.150, -2.300)` | `2.000 x 1.500` | `(6.890, -9.724)`, `0.0787 x 0.0591` | reporting quantization only (about `-0.0010 x +0.0011` mm) | `GND` |
| pin 2, OUT lead | `2`, `(-3.150, 0.000)` | `2.000 x 1.500` | `(6.890, -10.630)`, `0.0787 x 0.0591` | reporting quantization only | `AUX_3V3` |
| pin 2, OUT tab | `2`, `(+3.150, 0.000)` | `2.000 x 3.800` | `(9.370, -10.630)`, `0.0787 x 0.1496` | reporting quantization only (about `-0.0010 x -0.0002` mm) | `AUX_3V3` |
| pin 3, IN lead | `3`, `(-3.150, +2.300)` | `2.000 x 1.500` | `(6.890, -11.535)`, `0.0787 x 0.0591` | reporting quantization only | `5V_SYS` |

The invariant also checks absolute centres `(17.500,24.700)`,
`(17.500,27.000)`, `(23.800,27.000)`, `(17.500,29.300)` mm.  Pad number order
is exactly `1, 2, 2, 3`; the two physical terminals that TI identifies as OUT
are intentionally shorted by duplicate pad number 2.  The two small-pad
centre-pitch deltas versus TI are `0.000 mm` for both 1--2 and 2--3.  There is
no polarity reversal: pin 1 maps to GND, the tab maps to OUT/AUX_3V3, and pin
3 maps to IN/5V_SYS in PCB, schematic, and IPC-D-356.

## Standard-derived calculation disposition

A `STANDARD-DERIVED LAND PATTERN PASS` requires a reproducible statement of:

1. the cited IPC-7352 or IPC-7351B table/formula and density level;
2. input terminal maxima/minima from TI;
3. chosen fabrication and placement tolerances; and
4. resulting toe, heel, and side allowances, including a separate tab-land
   calculation.

Only item 2 is presently evidenced.  Selecting the remaining numeric values
from memory, from an unversioned KiCad library, or by reverse-engineering the
existing `2.00 x 1.50` and `2.00 x 3.80` lands would be circular and would not
meet the requested standard-based evidence threshold.  Therefore this audit
does not calculate a credible min/nom/max target range and does not relabel
the footprint PASS merely because its Gerber matches the project source.

## Disposition

**U4 remains `UNVERIFIED` for land-pattern approval.**  It is
manufacturer-package and pin/net verified, and generated Gerber/IPC geometry
is numerically identical to the controlled footprint, but neither a TI
recommended land pattern nor an accessible, reproducible IPC-7352/IPC-7351B
derivation is available.  Required closure evidence is a licensed/citable IPC
standard extract or an organization-approved, versioned standard-derived
calculation record containing the four inputs above.  No footprint change is
indicated by this finding.
