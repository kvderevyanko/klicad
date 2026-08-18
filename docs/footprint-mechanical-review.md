# Stage 7 — footprint and mechanical verification

Status: `DFM REVIEW REQUIRED`. This record covers footprint and mechanical
preparation only. The approved Rev.1 electrical schematic was not edited; no
PCB, board outline, placement or routing exists.

## Project-local library

`hardware/fp-lib-table` maps `Carrier` to `hardware/esp32-e220.pretty`.
`hardware/generate_stage7_footprints.py` regenerates all files in that library.
`kicad-cli fp export svg` under KiCad 10.0.5 exported each generated footprint
successfully.

## Production connector selections

| Ref. | Carrier-side preferred MPN | Basis / status |
| --- | --- | --- |
| J4 battery | JST `B2B-XH-A` | Exact XH top-entry THT 2-pin header; 2.50-mm pitch, 3 A AC/DC with AWG22 and 9.8-mm assembled height. Mating cable is `XHP-2` + `SXH-001T-P0.6`. PCBA-vendor availability/harness is procurement TBD. |
| J1, J2 DevKit | Samtec `SSW-115-02-G-S` (two) | Exact single-row 15-position THT socket: 2.54-mm pitch, 0.64-mm square tail, 4.7 A/pin (two powered), 8.51-mm insulator height and 3.68…6.35-mm mating insertion depth. Verify actual DevKit pin projection before release. |
| J3 E220 | Samtec `SSW-107-02-G-S` | Same verified SSW family, seven contacts. Verify actual E220 pin projection by sample before release. |
| J5 OLED | Samtec `SSW-104-02-G-S` | Same verified SSW family, four contacts. Verify actual OLED pin projection before release. |

Sources: [JST XH official catalogue](https://www.jst-mfg.com/product/pdf/eng/eXH.pdf),
[JST XH product page](https://www.jst.com/products/crimp-style-connectors-wire-to-board-type/xh-connector/),
[Samtec SSW through-hole catalogue](https://suddendocs.samtec.com/catalog_english/ssw_th.pdf),
and [Samtec SSW-115-02-G-S](https://www.samtec.com/products/ssw-115-02-g-s).

## Footprints created

- `Carrier:Samtec_SSW_1x15_P2.54mm_THT`,
  `Carrier:Samtec_SSW_1x07_P2.54mm_THT`, and
  `Carrier:Samtec_SSW_1x04_P2.54mm_THT`: 2.54-mm pitch, pin-1 rectangle,
  1.00-mm drill / 1.70-mm copper lands. The land sizes are a documented
  **PROJECT LAND-PATTERN CHOICE** for the 0.64-mm SSW tail, not a claim that
  Samtec mandates them. Archive/compare the part-specific Samtec footprint
  download before fabrication.
- J4 uses the installed exact KiCad stock footprint
  `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical`, whose description
  cites the JST official drawing. It has not been copied or modified.
- `Carrier:ESP32_DevKit_30pin_Socket_2x15_MechanicalTemplate`: rows are
  verified; full module geometry is deliberately non-production.
- `Carrier:E220_T22D_Socket_400_900`: a carrier-side 1x7 socket, **not** the
  EBYTE module solder pad pattern.
- `Carrier:OLED_0p96_4pin_MechanicalTemplate_PENDING_DATUM`: interface/body
  template only; no mounting NPTH is present.

## ESP32 DevKit coordinates

With left header pin 1 at `L1=(0,0)` and the USB-C/pin-1 ends aligned, the
verified socket rows are:

| Feature | Coordinate |
| --- | --- |
| `L1…L15` | X=0, Y=0…35.560 in 2.540-mm increments |
| `R1…R15` | X=25.400, Y=0…35.560 in 2.540-mm increments |
| Row centres | 25.400 mm USER-MEASURED / verified |
| Body | 28.0 x 51.0 mm USER-MEASURED only |

The body envelope is not registered to the header datum, so it cannot yet set
a true removal courtyard, USB-C access opening, board edge or antenna keepout.
The template labels the USB-C/pin-1 and antenna ends but does not invent an
antenna location. Until actual datums are measured, use the full DevKit envelope
as a no-component/no-copper planning region.

## E220 universal socket coordinates

The official common EBYTE *E220-400/900T22D Mechanical Dimensions and Pin
Definitions* drawing gives the shared body/pin geometry below, with the module
body lower-left as local origin:

| Feature | Value |
| --- | --- |
| Body | X=0…21.000, Y=0…36.000 mm |
| Pin row | Y=1.500 mm from short edge; 2.540-mm pitch |
| Pads 1…7 | `(2.880,1.500)`, `(5.420,1.500)`, `(7.960,1.500)`, `(10.500,1.500)`, `(13.040,1.500)`, `(15.580,1.500)`, `(18.120,1.500)` mm |
| Pin span / side margins | 15.240 mm / 2.880 mm nominal |

Both E220 product pages give the same 21 x 36-mm T22D DIP form, and the
common official drawing verifies equality of these body and seven-pin
coordinates. It does **not** yet production-approve the common socket: compare
the independent 900T22D CAD/sample for SMA-K location, thickness, actual pin
projection and underside features. Drawing holes 8…10 are labelled fixed holes
(1.50 x 2.00-mm lands / 0.90-mm holes), but their role is unknown; no carrier
hole or electrical pad is invented.

Sources: [E220-400T22D](https://www.cdebyte.com/products/E220-400T22D/4),
[E220-900T22D](https://www.cdebyte.com/products/E220-900T22D/4), and
[E220-T series manual](https://www.cdebyte.com/pdf-down.aspx?id=4221).

## OLED status

The newest user drawing supersedes earlier seller data: PCB body is **26.000 x
26.000 mm**, with four mount-centre spacing **X=21.740 mm, Y=22.000 mm**.
`OLED_MOUNT_Y` is therefore resolved. The template preserves those values as a
separate, explicitly unregistered guide because the underlying drawing is not
available in this workspace to verify mount-hole diameter, hole-to-body/header
datums, display/glass/flex clearance or bottom notch/cutout geometry. It has
no actual mounting holes and is not production-approved. Do not derive any
edge offset or drill size from the 26-mm body and spacing alone.

## Power-stage footprint audit and placement constraints

| MPN | Candidate / status | Mandatory placement constraint |
| --- | --- | --- |
| `TPS62133RGT` | `Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm` verified against TI RGT0016C: 3x3 mm, 0.5-mm pitch, 1.68x1.68-mm EP and four 0.68-mm paste apertures. | EP=GND; use four paste windows. Under-EP vias only if tented/plugged/filled. Keep PVIN/PGND and SW/L1 loops small. |
| `XFL4020-222MEB` | Unassigned. | Obtain/compare exact Coilcraft land pattern and body before release; place beside SW, away from both antenna regions. |
| `DMP3130LQ-7` | `Package_TO_SOT_SMD:SOT-23` candidate. | Confirm current Diodes land pattern before assignment. |
| `1812L200/16` | `Fuse:Fuse_1812_4532Metric` candidate. | Confirm Littelfuse package/thermal space before assignment. |
| `SMBJ10CA` | Unassigned. | Confirm exact SMBJ land pattern/body and allocate copper heat path. |
| C1/C3/C2/C4 | 0805/0805/0603/0603 candidates. | Verify exact Murata case codes; C1/C2 at PVIN/AVIN return, C3 at L1/VOS return, C4 at SS/TR. |

Source: [TPS62133 datasheet/package drawing](https://www.ti.com/lit/ds/symlink/tps62133.pdf).

## Open footprint/mechanical blockers

1. OLED: attach/audit the drawing to obtain hole diameter, all body/header
   datums, display window, flex and notch geometry; the X/Y spacing alone is
   insufficient for a mounting footprint.
2. ESP32: measure header-to-body, header-to-USB-C and header-to-antenna datums.
3. E220: compare independent 900T22D CAD/sample with 400T22D and select socket
   after actual pin-fit confirmation; resolve fixed-hole treatment.
4. Power components: final L1/D3/capacitor land patterns, TPS EP/paste/vias
   and PCBA assembly capability require final audit.
5. Battery: harness, strain relief, connector accessibility, enclosure and
   board outline are not defined.

The PCBA may populate only carrier parts (including these sockets). The DevKit,
E220 and OLED are user-installed. Keep all listed test points accessible after
modules are inserted. Do not route before the independent footprint review.
