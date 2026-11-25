# D3 — Littelfuse SMBJ10CA manufacturer re-audit

## FACT

| Check | OLD: active project-local / embedded PCB / diagnostic Gerber | MANUFACTURER: Littelfuse SMBJ series Rev. JC, 04-Jul-2025 | DELTA |
|---|---:|---:|---:|
| Case | DO-214AA claimed; Fab body `4.60 x 4.00 mm` | JEDEC DO-214AA (SMB J-Bend); body B=`4.060..4.750 mm`, C=`3.300..3.940 mm`, A=`1.930..2.200 mm`; lead D=`1.990..2.610 mm`, E=`0.760..1.520 mm`, F=`0..0.203 mm`, H=`0.152..0.305 mm` | Package identification is consistent; Fab nominal body is not the land pattern. |
| Land transverse dimension | `2.30 mm` (pad Y) | I=`2.260 mm` (the vertical/transverse solder-land arrow) | `+0.040 mm` |
| Land longitudinal dimension | `2.50 mm` (pad X) | J=`2.160 mm` and L=`2.160 mm` (the two equal longitudinal solder-land arrows, one per terminal) | `+0.340 mm` |
| Inner land-edge separation | `1.800 mm` = `4.300 - 2.500` | K=`2.740 mm` (inner-edge-to-inner-edge arrow) | `-0.940 mm` |
| Centre pitch | `4.300 mm`; local centres `(-2.150,0)/(+2.150,0)` | `2.160 + 2.740 = 4.900 mm`; required local centres `(-2.450,0)/(+2.450,0)` | `-0.600 mm`; each current centre is `0.300 mm` too near the package centre |
| Embedded PCB / diagnostic Gerber / IPC-D-356 | PCB D3 is at `(41.900,70.500,180)` with pad 1 `(-2.15,0)`, pad 2 `(+2.15,0)`, both `2.50 x 2.30 mm`; IPC-D-356 reports `D3-1 BAT_FUSED A01X+017343Y-027756X0984Y0906R180S2` and `D3-2 GND A01X+015650Y-027756X0984Y0906R180S2`. The reported 169.3-mil centre separation is `4.300 mm`; aperture dimensions are `2.50 x 2.30 mm`. | Required copper is two `2.160 x 2.260 mm` lands, `2.740 mm` inner gap, `4.900 mm` centre pitch. | Gerber is a faithful rendering of the incorrect current footprint; it is not a manufacturing-source match. |
| Electrical terminal/polarity | physical terminal 1 -> PCB pad 1 -> schematic pin 1 -> `BAT_FUSED`; physical terminal 2 -> PCB pad 2 -> schematic pin 2 -> `GND`. | The `CA` ordering code is bi-directional; the manufacturer functional diagram is symmetric. The cathode-band statement applies to uni-directional parts only. | No electrical polarity/orientation constraint for SMBJ10CA; pin/net mapping is valid. |

The pad-layout graphic was read as a drawing, not inferred from the table: its caption is **Solder Pads (all dimensions in mm)**. I is the transverse pad dimension, J/L are the equal individual longitudinal pad dimensions, and K is the clear inner gap between the two pad inner edges. Thus `2.16 + 2.74 = 4.90 mm` is the correct derived centre pitch; K is not a centre pitch.

## SOURCE

Primary manufacturer source: [Littelfuse, *TVS Diodes — Surface Mount 600 W, SMBJ series*, Rev. JC, 04-Jul-2025, p. 5/6 in browser pagination (PDF page labelled Physical Specifications / Dimensions)](https://www.littelfuse.com/assetdocs/tvs-diodes-smbj-series-datasheet?assetguid=ba555e99-a12d-4f72-a0b6-86b06c67171e). It identifies `SMBJ10CA` in the bi-directional ordering/electrical tables and specifies the DO-214AA (SMB J-Bend) mechanical and `Solder Pads` drawing.

Project sources inspected: `hardware/esp32-e220.pretty/Littelfuse_SMBJ10CA_DO214AA.kicad_mod`, `hardware/esp32-e220.kicad_pcb` D3 footprint, and `hardware/evidence/full-production-audit-2026-09-15/jp1-implementation/diagnostic-fabrication/ESP32-E220-Carrier-Rev1-JP1-DIAGNOSTIC.ipc356`.

## CLASSIFICATION

REAL MISMATCH — **FAIL**. Current D3 copper is not the official Littelfuse recommended solder-pad layout. This overturns the earlier `UNVERIFIED` disposition: the authoritative manufacturer land pattern exists, and it differs materially in both pitch/gap and pad length.

## IMPACT

Do not release or call D3 production-safe. A subsequent controlled physical-change transaction must first preserve this OLD/MANUFACTURER/DELTA record, then change the generator source of truth, project-local footprint, embedded PCB footprint, and only those local routes required by the outward `0.300 mm` pad-centre movement. It must re-run DRC, parity, Gerber, IPC-D-356, and independent implementation review. No board, schematic, footprint, Gerber, release, commit, or push was changed by this audit.

AUDIT COMPLETE
