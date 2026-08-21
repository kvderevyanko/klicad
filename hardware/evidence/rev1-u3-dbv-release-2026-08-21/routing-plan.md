# Rev.1 U3 DBV footprint-release physical plan

Role/scope: bounded read-only physical plan. The active PCB, schematic, generator, and active project-local footprint were not changed.

## Authoritative inputs

- Active PCB SHA-256: `0ed5189dcfb6a21822b05246acee0257cd03415e07cdea919861375e0d5d6c70` (`MATCH`).
- TI `SN74AHCT1G125` data sheet `SCLS378P`, Rev. P, revised March 2024: <https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf>.
- Embedded TI package drawing: `DBV0005A`, drawing `4214839/K`, August 2024.
- Retained primary evidence: `ti-sn74ahct1g125-rev-p.pdf`, SHA-256 `dbaf49b3af33690fc7f7356afe387e7815a56b8bb73fe1e88bf794f4fb8e0d2f`.

## Package and land-pattern audit

TI identifies `SN74AHCT1G125DBVR` as the 5-pin `DBV` SOT-23 package. TI pin functions are 1=`OE`, 2=`A`, 3=`GND`, 4=`Y`, 5=`VCC`.

The old project footprint was not correct as a complete manufacturer pattern:

- pads: 0.60 x 0.80 mm;
- pad-row center spacing: 2.00 mm (`y=+1.00/-1.00`);
- pad pitch along each row: 0.95 mm;
- F.Fab body: 3.00 x 2.90 mm;
- courtyard: 4.10 x 4.00 mm;
- pin-1 silk mark was on the pad-4/5 side rather than the pad-1 side.

The released candidate uses the complete TI `DBV0005A` example:

- five round-rectangle copper/paste pads: 0.60 x 1.10 mm, R0.05 mm;
- three-pad row centers at `(-0.950,+0.750)`, `(0,+0.750)`, `(+0.950,+0.750)` mm;
- two-pad row centers at `(-0.475,-0.750)`, `(+0.475,-0.750)` mm assigned to pins 5 and 4 respectively;
- 1.50-mm row-center spacing, 0.95-mm pitch, 2.60-mm total land-pattern span across the rows;
- F.Paste equals the TI 0.60 x 1.10-mm stencil apertures (TI example is based on a 0.125-mm stencil);
- non-solder-mask-defined openings use 0.05-mm mask expansion per side, within TI's stated 0.07-mm maximum surround;
- maximum-body F.Fab outline is 3.00 x 1.75 mm with a pin-1 chamfer;
- courtyard is 3.50 x 3.60 mm: 0.25 mm beyond the 3.00-mm maximum body in X and rounded outward from the 3.05-mm maximum overall lead envelope in Y;
- a dedicated F.Silk pin-1 circle is adjacent to physical pad 1 and clear of exposed mask in native DRC.

Candidate footprint source: `esp32-e220.pretty/TI_SN74AHCT1G125DBVR_SOT23-5.kicad_mod`. The description pins the TI drawing/revision and contains no provisional-release wording. Native DRC reports zero `lib_footprint_issues`, proving candidate board/library agreement.

## Electrical mapping proof

Actual schematic symbol pin functions and candidate PCB pad nets agree through the independent parity checker:

| Pin | TI function | PCB net | Required topology |
|---|---|---|---|
| 1 | OE | `/GND` | OE held low |
| 2 | A | `/WS2812_DATA_3V3` | ESP32-side data input |
| 3 | GND | `/GND` | local ground |
| 4 | Y | `/WS2812_DATA_5V` | J9.2 data output |
| 5 | VCC | `/5V_SYS` | 5-V supply / C7 bypass |

No symbol or pin numbering change is required. `SCHEMATIC AUDIT REQUESTED` is not triggered.

## Selected bounded routing contract

Candidate: `10-u3-dbv-candidate.kicad_pcb`.

Coupled group: only U3 pads 1...5, C7's existing local 5-V bypass branch/ground return, the existing U3-data input via, and the existing U3.4-to-J9.2 path.

- U3 origin/rotation: retain `(89.000,54.000) mm`, `0 degrees`.
- C7: retain `(85.500,54.000) mm`, `90 degrees`.
- J9: retain `(100.000,54.000) mm`, `0 degrees`.
- U3.1 `/GND`: pad center `(88.050,54.750)`; shift only the attached 0.50-mm F.Cu segment endpoint from `(88.050,55.000)` by 0.25 mm. Existing via `(87.200,56.500)` and return plane stay unchanged.
- U3.2 `/WS2812_DATA_3V3`: pad center `(89.000,54.750)`; shift only the attached 0.25-mm F.Cu segment endpoint from `(89.000,55.000)` by 0.25 mm. Existing via `(89.000,58.000)` and all B.Cu data routing stay unchanged.
- U3.3 `/GND`: pad center `(89.950,54.750)`; shift only the attached 0.50-mm F.Cu segment endpoint from `(89.950,55.000)` by 0.25 mm. Existing via `(91.000,55.000)` and return plane stay unchanged.
- U3.4 `/WS2812_DATA_5V`: pad center `(89.475,53.250)`; shift only the attached 0.25-mm F.Cu segment endpoint from `(89.475,53.000)` by 0.25 mm. Remaining path through `(94.000,51.500) -> (98.000,54.000) -> J9.2 (100.000,56.540)` stays unchanged; resulting U3.4-to-J9.2 path is 12.801 mm, F.Cu, zero vias.
- U3.5 `/5V_SYS`: pad center `(88.525,53.250)`; shift only the attached 0.50-mm F.Cu segment endpoint from `(88.525,53.000)` by 0.25 mm. C7-to-U3.5 path remains C7.1 `(85.500,54.725) -> (87.000,54.725) -> (87.000,51.900) -> (88.525,51.900) -> U3.5`, 7.200 mm, F.Cu, zero vias.
- C7 return: C7.2 `(85.500,53.275)` to the existing global-GND via `(85.500,51.900)`, 1.375 mm, 0.50-mm F.Cu. U3's two short GND branches terminate in the existing global B.Cu plane. C7 remains a local 100-nF bypass at 3.5-mm component-center separation; no bypass component or via relocation is necessary.
- Vias added/removed: none.
- Return path: existing B.Cu GND plane through the unchanged U3.1/U3.3 and C7.2 GND vias; no new return discontinuity.
- Keepouts: U3/C7/J9 are left of `ESP32_ANTENNA_EXCLUSION` X-min 104.7 mm; antenna rule area, zones, buck, E220, OLED, J6, J8, JP1 and Edge.Cuts are untouched.

Exactly five existing segment endpoints change. Track count remains 200; via count remains 58. The exploratory `20-u3-dbv-short-vcc-candidate.kicad_pcb` is retained only as non-authoritative evidence and must not be implemented; the selected candidate minimizes copper change while already satisfying the C7 functional check and every deterministic gate.

## Deterministic candidate gates

- Native DRC after explicit refill: 0 violations, 0 unconnected items (`11-u3-dbv-candidate-drc.json`).
- Board contract with protected baseline `00-active-baseline.kicad_pcb`: `PASS`; 2 copper layers, 145 x 90 mm, 37 footprints, 200 tracks, 58 vias, 4 zones (`12-board-contract.json`).
- Schematic-PCB parity: `PASS`, 37/37 assembled, R10/R11 intentional `NO_FOOTPRINT_DNP` (`13-parity.json`).
- Native ERC: 0 errors, 0 warnings (`14-native-erc.json`).
- Strict normalized delta: `PASS`; every non-U3 footprint, every via, every zone/rule boundary/net, and Edge.Cuts are identical. Only the five listed U3-attached segment endpoints differ (`15-normalized-delta.json`).

Expected active-transaction DRC delta: none. Violation count and unconnected count must remain zero.

## Implementation checkpoints after independent plan approval

1. Verify active PCB SHA still equals the controlled baseline and run the transaction-fast contract.
2. Create the named active backup.
3. Update the authoritative generator/source and regenerate the project-local footprint exactly from the reviewed candidate library definition.
4. Replace only U3's embedded footprint at unchanged origin/rotation and apply the five reviewed endpoint shifts.
5. Run fast contract, explicit zone refill/native DRC, parity, and full protected-reference contract.
6. Run the strict normalized immutability comparison. Any unexpected footprint, copper, via, zone, rule-area, or Edge.Cuts delta requires rollback and STOP.

Risks for the implementation gate: generator/library/embedded-footprint drift; a pin-1 marker copied to the wrong side; track endpoints snapping to old pad centers; any source regeneration that alters unrelated schematic content. Each is covered by library DRC, parity, native DRC, and normalized-delta checks.

ROUTING PLAN READY
