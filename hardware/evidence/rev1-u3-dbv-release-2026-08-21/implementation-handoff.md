# Rev.1 U3 DBV footprint-release implementation handoff

## SCOPE STATUS

`U3 DBV FOOTPRINT RELEASE IMPLEMENTED — READY FOR INDEPENDENT IMPLEMENTATION GATE`

Received independent plan verdict before active mutation:

- `SCOPE VERDICT: U3 DBV FOOTPRINT RELEASE PASS`
- `REVIEW PASS`

The active pre-transaction PCB matched SHA-256
`0ed5189dcfb6a21822b05246acee0257cd03415e07cdea919861375e0d5d6c70`.
The protected-reference fast contract passed before mutation, and the named
rollback board is `30-active-pre-u3-transaction-backup.kicad_pcb`.

## Released source and geometry

Primary release evidence is TI `SN74AHCT1G125`, data sheet `SCLS378P`, Rev. P,
with package drawing `DBV0005A`, drawing `4214839/K`, August 2024. The retained
PDF SHA-256 is
`dbaf49b3af33690fc7f7356afe387e7815a56b8bb73fe1e88bf794f4fb8e0d2f`.

The authoritative `sn74ahct1g125()` generator now emits the reviewed released
footprint byte-identically. Obsolete provisional-release wording was removed
from the generator, footprint description, and project-local library README.

- U3 origin/rotation retained: `(89.000, 54.000) mm`, `0 degrees`.
- Pads 1/2/3: local centers `(-0.950,+0.750)`, `(0,+0.750)`,
  `(+0.950,+0.750) mm`.
- Pads 5/4: local centers `(-0.475,-0.750)`, `(+0.475,-0.750) mm`.
- All pads: `0.60 x 1.10 mm`, round-rectangle radius `0.05 mm`, TI paste,
  and `0.05 mm` NSMD mask expansion.
- F.Fab maximum-body outline: `3.00 x 1.75 mm`, pin-1 chamfer.
- F.CrtYd: `3.50 x 3.60 mm`.
- Pin-1 silk circle is adjacent to physical pad 1.

The electrical pin map is unchanged and parity-proven: 1/OE=`/GND`,
2/A=`/WS2812_DATA_3V3`, 3/GND=`/GND`, 4/Y=`/WS2812_DATA_5V`,
5/VCC=`/5V_SYS`.

## Bounded copper delta

Exactly five existing F.Cu endpoints moved by `0.25 mm`; segment UUIDs,
widths, nets, layers, and opposite endpoints are unchanged:

- U3.1 GND: `(88.050,55.000)` to `(88.050,54.750)`, width `0.50 mm`.
- U3.2 input: `(89.000,55.000)` to `(89.000,54.750)`, width `0.25 mm`.
- U3.3 GND: `(89.950,55.000)` to `(89.950,54.750)`, width `0.50 mm`.
- U3.4 output: `(89.475,53.000)` to `(89.475,53.250)`, width `0.25 mm`.
- U3.5 VCC: `(88.525,53.000)` to `(88.525,53.250)`, width `0.50 mm`.

C7 remains at `(85.500,54.000) mm`, 90 degrees. Its VCC-to-U3.5 path is
`7.200 mm`, F.Cu, zero vias; its GND branch remains `1.375 mm`, `0.50-mm`
F.Cu to the global-GND via at `(85.500,51.900)`. J9 stays at
`(100.000,54.000) mm`; U3.4-to-J9.2 remains `12.801 mm`, F.Cu, zero vias.

Strict normalized delta is `PASS`: every non-U3 footprint origin/rotation and
geometry, every via, zone/rule boundary/net, and Edge.Cuts are identical to the
approved baseline. No zone, antenna, buck, E220, OLED, J6, J8, JP1, J9-position,
or U4 geometry changed.

## Deterministic implementation gates

- Active PCB SHA-256: `161b4217c57829c8584ca8da0b984b63fcf0a6617011a35a424bbd57b308e804`.
- Source regeneration: `PASS`; generated U3 footprint is byte-identical to
  the reviewed candidate, SHA-256
  `c9923e3e5a73b0d4da3e774c3c79a09dd6110b87ac6974e6ae2a98bfa79a5a7a`.
- Board contract, protected reference: `PASS`; 37 footprints, 200 tracks,
  58 vias, 4 zones, 2 copper layers, 145 x 90 mm.
- Native DRC after explicit refill/save: 0 violations, 0 unconnected items.
- Schematic-PCB parity: `PASS`, 37/37 assembled, R10/R11 intentional
  `NO_FOOTPRINT_DNP`.
- Native ERC: 0 errors, 0 warnings.
- Rollback: not required; no unexpected violation occurred.
- Production outputs: none generated.

## Reviewer gate

Required next independent gate:

`SCOPE VERDICT: U3 DBV FOOTPRINT IMPLEMENTATION PASS`

`REVIEW PASS`
