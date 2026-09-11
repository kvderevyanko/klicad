# Rev.1 fabrication notes

## Verified board

- Board: 145 x 90 mm
- Layers: 2
- Fabrication set: F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, Edge.Cuts, and Excellon drills.

## Recommended economical order parameters

- Material: FR-4
- Nominal thickness: 1.6 mm
- Outer copper: 1 oz (approximately 35 um)
- Solder mask: green
- Silkscreen: white
- Finish: lead-free HASL

These are order parameters, not encoded geometry. ENIG is acceptable if the
selected assembler recommends it for QFN assembly and its price impact is
acceptable. Rev.1 has no controlled-impedance requirement, castellations,
edge plating, blind vias, or buried vias.

## First-article notes

- Verify OLED mechanical/body fit on the actual module.
- Rev.1 has three M3 mounting holes: H1/H2/H3, each 3.20-mm NPTH with an 8-mm copper-free screw-head region. Enclosure/standoffs must respect these mechanical clearances.
- Battery strain relief is enclosure/harness responsibility.
- Visually/process inspect the U1 exposed-pad assembly.
- U4 operating temperature may be checked during first-article power validation.
- Prototype power-transient validation remains recommended.
