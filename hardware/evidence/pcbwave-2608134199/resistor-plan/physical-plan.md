# R2 and R8/R9 physical plans for order 2608134199

## R2

- Apply a dedicated UNI-ROYAL 0603W SMD footprint to R2. UNI-ROYAL Section 8, 0603 row gives gap A 0.90 ±0.05, each land axial length B 0.65 ±0.05, transverse width C 0.80 ±0.05 and overall span D 2.10 ±0.05 mm. Nominals conflict because A + 2B = 2.20. The target A 0.875, B 0.625, C 0.800 and D 2.125 satisfies all four intervals simultaneously. Document this interior-tolerance selection for PCBWAVE. See ../footprints/uni-royal-thick-film-v3.pdf, page 5.
- Set local pad centres x ±0.750, y 0, local dimensions 0.625 × 0.800 mm, existing roundrect fraction 0.20. R2 stays on F.Cu at (62.50,67.00), 90°. Global centres (62.50,67.75) /BUCK_IN and (62.50,66.25) /Q1_GATE. Existing 0.25-mm tracks terminate at (62.50,67.725) and (62.50,66.275), safely within each pad. Preserve both tracks.
- R2/scratch-drc.json reports 0 violations, 0 unconnected and 20 pre-existing native parity entries after refill. R2/contract.json passes against the unchanged protected baseline.

## R8 and R9

- Apply a Vishay CRCW0603 e3 reflow footprint to both M0/M1 pull-downs. Vishay document 20035 page 11 gives G 0.75, Y 0.75, X 1.00, Z 2.25 mm. Each pad is 0.750 × 1.000 mm at local ±0.750, existing roundrect fraction 0.20. [Vishay D/CRCW e3 datasheet](https://www.vishay.com/docs/20035/dcrcwe3.pdf)
- Preserve both placements at (40.00,35.00) and (46.00,35.00), 0° on F.Cu. Pad 1/2 centres are (39.25,35.00) /E220_M0 and (40.75,35.00) /GND, and (45.25,35.00) /E220_M1 and (46.75,35.00) /GND. Existing 0.25-mm track endpoints lie at x 39.275, 40.725, 45.275, 46.725 respectively, all at y 35, within the new pads. Preserve all tracks.
- R8-R9/scratch-drc.json reports 0 violations, 0 unconnected and 20 pre-existing native parity entries after refill. R8-R9/contract.json passes against the unchanged protected baseline.

For each transaction preserve existing resistor body, courtyard and origin, use matching F.Mask/F.Paste land openings and preserve all other footprints, ground connections, tracks, vias, zone outlines and keepouts. Add distinct identifiers to board, schematic, libraries and generators. Preserve the Yageo geometry for R1/R3/R4. Refill and verify raw DRC, authoritative parity and geometry contracts between transactions. Expected geometry DRC delta is zero. Unexpected findings require restoration of the individual transaction.

ROUTING PLAN READY
