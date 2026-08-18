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
  `Carrier:Samtec_SSW_1x04_P2.54mm_THT`: 2.54-mm pitch, pin-1 rectangle and
  official Samtec SSW-S **1.040-mm drill**. The 1.70-mm copper lands are a
  documented **PROJECT LAND-PATTERN CHOICE** for the 0.64-mm SSW tail, not a
  claim that Samtec mandates a copper diameter. Confirm the annular ring with
  the fabricator/assembler before fabrication.
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

Both E220 product pages give the same 21 x 36-mm T22D DIP form. The shared
official manual drawing and EBYTE's 900 download `3D_E220-xxxT22D`
(`E220-xxxT22D(3D).step`) establish that this is shared 400/900-T22D geometry,
not a 400-only assumption. The official 900 `E220-900T22D-LIB` archive is
also available, so the 900 mechanical source is no longer a generic
user-measurement blocker.

The same drawing gives the non-electrical fixing-hole centres in its front-view
datum: hole 10/9/8 are X=3.50/6.04/8.58 mm, at 3.00 mm from the SMA-side
short edge. In the project footprint datum this is `(3.50,33.00)`,
`(6.04,33.00)`, `(8.58,33.00)` mm. EBYTE calls 8…10 **fixing holes** and
shows 1.50 x 2.00-mm top/bottom lands with a 0.90-mm hole. They are rendered
only as `Dwgs.User` clearance guides: the socket carrier does **not** create
an electrical pad or NPTH there until a mounting-method decision requires it.

The official drawing also identifies the SMA-side mechanical envelope: a
6.20-mm SMA body callout, nominal SMA axis at X=15.60 mm from the left body
edge, and a 12.8-mm side-view transverse envelope. It does not give a clearly
dimensioned mating-pin tail length or carrier-plane stack-up. Therefore Samtec
socket mating depth remains a **PROTOTYPE / PROCUREMENT DFM** check, not a
request to remeasure the known body or pin row. No user measurement is
requested for E220 at this gate.

Sources: [E220-400T22D](https://www.cdebyte.com/products/E220-400T22D/4),
[E220-900T22D](https://www.cdebyte.com/products/E220-900T22D/4),
[E220-T series manual](https://www.cdebyte.com/pdf-down.aspx?id=4221),
[official 900 3D STEP](https://www.cdebyte.com/Uploadfiles/Files/2023-8-17/2023817941188606.zip),
and [official 900 library](https://www.cdebyte.com/pdf-down.aspx?id=1717).

## OLED status

The newest user drawing supersedes earlier seller data: PCB body is **26.000 x
26.000 mm**, with four mount-centre spacing **X=21.740 mm, Y=22.000 mm**.
`OLED_MOUNT_Y` is therefore resolved. It also fixes the horizontal header
datum: pin 1/GND is **X=9.190 mm from the left PCB edge**, so VCC/SCL/SDA are
respectively X=11.730/14.270/16.810 mm. The template records these numbers;
the actual carrier connector remains the separate `Samtec_SSW_1x04` footprint.

The drawing still does not unambiguously provide the header-row Y datum,
mounting-hole finished diameter, or the display/glass/flex/notch clearance
envelope. It therefore has no actual mounting holes and is not
production-approved. Do not derive any edge offset or drill size from the
26-mm body and spacing alone. The exact minimal user measurement request is:

- **OLED-A:** top PCB edge to centreline of the 1x4 header row;
- **OLED-B:** actual finished mounting-hole diameter.

## Power-stage footprint audit and placement constraints

| MPN | Candidate / status | Mandatory placement constraint |
| --- | --- | --- |
| `TPS62133RGT` | `Carrier:TI_TPS62133RGT_RGT0016C` verified against TI RGT0016C: 3x3 mm, 0.5-mm pitch, 1.68x1.68-mm EP and **1.55x1.55-mm EP paste aperture (~85%)**. | EP=GND; use TI's 1.55-mm stencil opening. Under-EP vias only if tented/plugged/filled. Keep PVIN/PGND and SW/L1 loops small. |
| `XFL4020-222MEB` | Unassigned. | Obtain/compare exact Coilcraft land pattern and body before release; place beside SW, away from both antenna regions. |
| `DMP3130LQ-7` | `Package_TO_SOT_SMD:SOT-23` candidate. | Confirm current Diodes land pattern before assignment. |
| `1812L200/16` | `Fuse:Fuse_1812_4532Metric` candidate. | Confirm Littelfuse package/thermal space before assignment. |
| `SMBJ10CA` | Unassigned. | Confirm exact SMBJ land pattern/body and allocate copper heat path. |
| C1/C3/C2/C4 | 0805/0805/0603/0603 candidates. | Verify exact Murata case codes; C1/C2 at PVIN/AVIN return, C3 at L1/VOS return, C4 at SS/TR. |

Source: [TPS62133 datasheet/package drawing](https://www.ti.com/lit/ds/symlink/tps62133.pdf).

## Open footprint/mechanical blockers

1. OLED: `OLED-A` header-row Y datum and `OLED-B` finished hole diameter are
   the only measurements needed to register the known connector and X/Y
   mounting pattern. Display/flex/notch clearance is a later mechanical
   placement/enclosure constraint, not a reason to discard known coordinates.
2. ESP32: measure the defined A/B/C/D/E header-to-body, USB-C and antenna
   datums below.
3. E220: common 400/900 source geometry is verified. Validate only the
   selected Samtec socket's actual mating insertion on a first article; do not
   request a duplicate body/pin-row measurement from the user.
4. Power components: final L1/D3/capacitor land patterns, TPS EP/paste/vias
   and PCBA assembly capability require final audit.
5. Battery: harness, strain relief, connector accessibility, enclosure and
   board outline are not defined.

The PCBA may populate only carrier parts (including these sockets). The DevKit,
E220 and OLED are user-installed. Keep all listed test points accessible after
modules are inserted. Do not route before the independent footprint review.

## Stage 7 corrective primary-source audit — 2026-08-18

This subsection supersedes the earlier use of *candidate* generic footprints.
The project-local library is regenerated by
`hardware/generate_stage7_footprints.py`; its files were parsed and SVG-exported
by `kicad-cli fp export svg` with KiCad 10.0.5. This is a file-format check,
not a release/DFM approval.

### Audited footprints and primary evidence

| Item | Project footprint | Exact geometry recorded | Verification state / source |
| --- | --- | --- | --- |
| J4 | `Carrier:JST_B2B-XH-A_1x02_P2.50mm_THT` | pitch 2.500 mm; drills 1.000 mm; lands 1.70 x 2.00 mm; body -2.45…4.95 × -2.35…3.40 mm; pin 1 rectangular. | **FOOTPRINT VERIFIED** against JST eXH B2B-XH-A drawing. Mates are XHP-2 housing and SXH-001T-P0.6 contact. |
| J1/J2/J3/J5 | `Carrier:Samtec_SSW_1x15_P2.54mm_THT`, `...1x07...`, `...1x04...` | official SSW-S pitch 2.540 mm and drill **1.040 mm**; project copper land 1.70 mm; insulator drawing envelope used in library. | **FOOTPRINT VERIFIED with a PROCUREMENT DFM note**: Samtec's official `ssw-s.pdf` directly confirms the single-row hole pattern. It gives no copper-pad diameter, so 1.70-mm copper is a documented project annular-ring choice for the official 0.64-mm square tail; assembler confirmation remains required. |
| U1 | `Carrier:TI_TPS62133RGT_RGT0016C` | 16 lands 0.600 mm radial × 0.240 mm tangential; peripheral centres at ±1.400 mm, 0.500-mm pitch; EP 1.680 x 1.680 mm; **single 1.550 x 1.550-mm paste aperture (85.1% EP coverage)**. | **FOOTPRINT VERIFIED** from TI RGT0016C example board/stencil drawings. Pin-1 marked. |
| L1 | `Carrier:Coilcraft_XFL4020-222MEB` | 0.980 x 3.400-mm lands, 3.350-mm centre spacing; nominal 4.0 x 4.0-mm body; pin 1/start-lead marking. | **FOOTPRINT VERIFIED** from Coilcraft recommended land-pattern drawing. During layout the marked terminal must be on the low-EMI side described by Coilcraft. |
| Q1 | `Carrier:Diodes_DMP3130LQ-7_SOT23` | 0.800 x 0.900-mm lands; bottom centres X=±1.350 mm/Y=1.000 mm, top centre (0,-1.000) mm; extent Y=2.900 mm. | **FOOTPRINT VERIFIED** from Diodes DS38728 suggested pad layout. This maps package pins 1/2/3; compare final CAD orientation to the schematic pin names before PCB assignment. |
| F1 | `Carrier:Littelfuse_1812L200_16_4532Metric` | body 4.50 x 3.20 mm; 1.125 x 3.40-mm lands, 4.275-mm centres. | **FOOTPRINT / PROCUREMENT DFM OPEN**: Littelfuse primary data verifies the exact 1812L200/16 family and ratings, but does not furnish this PCB land pattern. The land pattern is a clearly-labelled IPC/project choice pending assembler confirmation. |
| D3 | `Carrier:Littelfuse_SMBJ10CA_DO214AA` | official DO-214AA body envelope 4.06…4.75 x 3.30…3.94 mm; 2.50 x 2.30-mm lands on 4.30-mm centres. | **FOOTPRINT / PROCUREMENT DFM OPEN**: official package envelope verified; land size is labelled project IPC nominal pending the selected assembler's pad rule. Bidirectional TVS means no functional cathode orientation, but reference/fab convention still uses pad 1/2. |
| C1/C3 | `Carrier:Murata_GRM21_2012Metric` | GRM21 = 2012 metric/0805 case; 1.15 x 1.40-mm project IPC lands on 2.00-mm centres. | **PROCUREMENT DFM OPEN**: the Murata exact MPNs/case codes are verified; the land is a documented IPC/project implementation, not an asserted Murata recommended land pattern. |
| C2/C4/C5/C6/C7 | `Carrier:Murata_GRM188_1608Metric` | GRM188 = 1608 metric/0603 case; 0.95 x 1.00-mm project IPC lands on 1.45-mm centres. | Same status as C1/C3. |
| R1/R2/R8/R9/R10/R11 | `Carrier:Resistor_0603_1608Metric` | 1608/0603, 0.95 x 1.00-mm project IPC lands on 1.45-mm centres. | **PROCUREMENT DFM OPEN**: no resistor MPN/package has been selected in the approved electrical baseline; this does not change any electrical value. |

Primary sources: [JST XH/eXH drawing](https://www.jst-mfg.com/product/pdf/eng/eXH.pdf),
[Samtec SSW-115-02-G-S page](https://www.samtec.com/products/ssw-115-02-g-s) and
[Samtec SSW single-row recommended PC-board layout](https://suddendocs.samtec.com/prints/ssw-s.pdf),
[TI TPS62133 / RGT0016C package drawing](https://www.ti.com/lit/ds/symlink/tps62133.pdf),
[Coilcraft XFL4020 drawing](https://www.coilcraft.com/getmedia/50632d43-da1b-4cdb-8ab4-3029cab51df3/xfl4020.pdf),
[Diodes DMP3130LQ DS38728](https://www.diodes.com/_files/datasheets/DMP3130LQ.pdf),
[Littelfuse 1812L data](https://www.littelfuse.com/~/media/electronics/datasheets/resettable_ptcs/littelfuse_ptc_1812l_datasheet.pdf.pdf),
and [Littelfuse SMBJ data](https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_smbj_datasheet.pdf.pdf).

**RGT0016C generator correction:** a preliminary-board DRC exposed an
incorrect earlier interpretation of TI's 2.800-mm reference dimension. In the
official RGT0016C example, it is the spacing between opposite peripheral-pad
centrelines, therefore the centres are ±1.400 mm. The 0.600-mm land dimension
is radial and 0.240 mm is tangential. This preserves clearance to TI's
1.680-mm EP and does not alter the approved electrical topology.

### Layout constraints are separate from land patterns

`TPS62133RGT` has an **LAYOUT THERMAL / EMI** requirement, not merely an EP
footprint: solder the EP to GND, minimize PVIN/PGND/CIN and SW/L1/COUT loops,
and use TI's optional 0.20-mm-under-EP vias only when the PCB/assembly flow
controls them (TI recommends filled, plugged or tented vias when they are under
paste). Do not place an automatic via array from the footprint generator.

`XFL4020` must be kept in the converter loop and away from the ESP32/E220 RF
regions. `D3`, `F1` and Q1 are input-protection components: their **LAYOUT
THERMAL** task is short, wide BAT current routing; this does not alter the
approved topology.

### Modules — current coordinate status and required evidence

**ESP32 DevKit — PRELIMINARY PLACEMENT PERMITTED.** The verified electrical
coordinates remain `L1=(0,0)…L15=(0,35.560)`,
`R1=(25.400,0)…R15=(25.400,35.560)` mm. The 28 x 51-mm body is
USER-MEASURED only. Rev.1 now adopts a deliberate conservative policy rather
than blocking early mechanics on clone-specific A/B/C/D/E datums: use the full
28 x 51-mm envelope, maintain at least 5 mm from other removable module
envelopes (more for vertical removal), keep the USB-C end accessible, put the
antenna end at a carrier edge, and reserve a no-components/no-routing antenna
placeholder. A/B/C/D/E are historical optional refinement measurements, not
current placement blockers.

**E220 — MODULE MECHANICAL REVIEW: PASS WITH PROTOTYPE MATING NOTE.** The
official shared manual, 900 product download `3D_E220-xxxT22D`, and 900
library support one common socket template: seven contacts
`(2.880+n×2.540,1.500)` mm for n=0…6, 21 x 36-mm body, three non-electrical
fixing sites and SMA-side envelope. This is sufficient for the universal
mechanical template. The open item is not a user measurement: verify the
selected socket's 3.68…6.35-mm insertion depth against a received E220 sample
before PCBA release. The EBYTE “fixed holes” 8…10 remain non-electrical
guide-only features until a mechanical retention choice is made.

**OLED — PRELIMINARY PLACEMENT PERMITTED; PRODUCTION MOUNTING PATTERN BLOCKED.**
Authoritative user/seller-provided geometry fixes body **26.000 x 26.000 mm**,
mount centre spacing **X=21.740 mm, Y=22.000 mm**, and the 1x4 pin-X positions
GND/VCC/SCL/SDA = **9.190/11.730/14.270/16.810 mm** from the left edge. The
only data needed to register the connector and mounting pattern are
**OLED-A** header-row Y and **OLED-B** finished hole diameter. These do not
block a conservative preliminary envelope/clearance placement with no routing.
Display/flex and notch callouts remain a placement/enclosure clearance
constraint. The library deliberately creates neither NPTH nor a falsely
registered mounting pattern until OLED-A/B arrive.

### Gate state

`DFM REVIEW REQUIRED`. There is no electrical change and no final placement or
routing. The remaining issues are distinctly **FOOTPRINT**, **MECHANICAL
PLACEMENT**, **LAYOUT THERMAL**, or **PROCUREMENT DFM** issues; none is being
misreported as a schematic blocker.

### Stage 7.1 preliminary mechanical board

`hardware/generate_stage7_preliminary_pcb.py` reproducibly creates
`hardware/esp32-e220.kicad_pcb` as an explicitly **un-routed, netless,
mechanical placement study**. It has a provisional 160 x 100-mm outline,
source-audited power-component footprints, the E220/OLED/DevKit mechanical
templates, access guides and a prototype-test-point reserve. It deliberately
has **no tracks, vias, copper zones, net assignments, board release outline or
manufacturing outputs**.

The current KiCad 10 DRC of that study reports zero violations and zero
footprint errors after the RGT0016C coordinate correction. This only verifies
file/footprint hygiene for the study; it is **not** schematic-to-PCB
consistency, routed-board DRC, thermal validation or production DFM approval.
Routing remains gated on an independent preliminary-placement review and then
on synchronizing the approved schematic's complete component population.

## Stage 8 — synchronized functional placement (unrouted)

`hardware/generate_stage8_placement.py` supersedes the netless Stage 7.1
study as the reproducible current PCB generator. It instantiates the active
carrier references, creates the approved schematic net names and assigns every
active pad by the reviewed reference/pin map. KiCad 10.0.5 CLI has no
`update-from-schematic` command; the generator therefore provides an explicit,
reviewable reference/pad/net binding rather than claiming that the old netless
board is synchronized.

The generated board has **33 footprints, 18 named electrical nets, 0 tracks,
0 vias and 0 copper zones**. `R10` and `R11` are the approved I2C **DNP**
sites; they intentionally have **no PCB footprint** and are recorded as such
rather than silently omitted. Schematic-only `PWR_FLAG` markers are also
intentional no-footprint items. All remaining active carrier references are
instantiated exactly once: J1/J2/J3/J4/J5, U1/U3, D2, F1, D3, Q1, L1,
C1…C7, R1/R2/R8/R9 and TP1…TP10.

### Placement / access constraints

- The prior 160 x 100-mm outline is retired as a **temporary mechanical study
  canvas**, not a target board size.
- The generated 145 x 90-mm outline is the **preferred comfortable preliminary
  Rev.1 outline**, not a released board outline. A 135 x 85-mm outline is the
  current **minimum practical candidate** but leaves materially less USB-C,
  SMA, OLED and buck-layout reserve.
- Width is driven by the 28-mm DevKit envelope plus direct USB-C/antenna-edge
  access, the separated 26-mm OLED reserve and the E220 SMA-side access.
  Height is driven by the 36-mm E220 envelope/SMA access, a separate compact
  battery-to-buck cell and the accessible prototype-test bank.
- Removable module envelopes use at least 5 mm clearance; the layout reserves
  7…10 mm where access or an adjustment reserve is needed. The DevKit is at
  the right edge with a no-components/no-routing antenna placeholder and an
  explicit USB-C corridor. E220's SMA side faces the bottom edge. OLED has a
  conservative 36 x 36-mm reservation around its known 26 x 26-mm body.
- The compact power cell is ordered `J4 → F1 → D3/Q1 → CIN/U1 → L1 → COUT`.
  It is physically segregated from the two RF access regions. `C1/C2` are
  adjacent to U1 input, L1 immediately follows SW and C3 is at the output.
  U1 EP=GND; thermal vias, SW copper extent, and the final PGND return are
  explicitly deferred to the approved routing/thermal stage.

### Stage 8 validation and non-routing DRC interpretation

`kicad-cli pcb drc hardware/esp32-e220.kicad_pcb` reports **0 geometric DRC
violations and 72 unconnected-item findings**. The 72 findings are expected
airwires because routing is prohibited in this stage; they are not waived or
excluded. There are no tracks, vias or zones to hide a connection.

### Release boundaries remaining after placement

- **OLED mechanical / PCB release blocker:** OLED-A (header-row Y) and OLED-B
  (finished mounting-hole diameter). They do not block unrelated placement or
  later routing outside the conservative OLED reserve.
- **PCB release / footprint blocker:** the WS2812B-V5 footprint is a visible
  `WorldSemi_WS2812B-V5_PLACEMENT_CANDIDATE_NOT_RELEASED`, because the project
  still lacks an auditable manufacturer recommended land pattern. It is placed
  for functional clearance only, never approved for fabrication.
- **Layout/thermal blocker:** final TPS62133 thermal-via, return-path and
  switch-node implementation; this is a power-routing review item, not a
  reason to alter its verified EP footprint.
- **Prototype validation:** verify actual E220-to-Samtec mating depth before
  PCBA release. This no longer blocks routing. Enclosure/access review is a
  PCB-release/enclosure-validation item because no enclosure is specified.

### Stage 8 corrective power/RF placement — pending independent re-review

The first Stage 8 reviewer found that the preliminary power-cell placement had
not been laid out against the **actual** TPS62133RGT pad sides, and that C6,
the WS2812 candidate D2 and TP10 were too close to, or inside, reserved module
areas.  This correction changes **placement only**; it does not change the
approved electrical schematic, pad/net mapping, outline, or add any routing.

`U1` remains at `(72.000, 72.000)` mm and 0 degrees.  On the audited
RGT0016C footprint, that puts SW1/2/3 (pins 1/2/3) on the **left** and
AVIN/PVIN (pins 10/11/12) on the **right**.  The corrected compact cell is
therefore physically ordered:

`C1/C2 (input, right) -> U1 PVIN/AVIN -> U1 SW (left) -> L1 -> C3 (5V_SYS)`.

Direct pad-centre evidence from the regenerated board is:

| Required local pair | Coordinates (mm) | Direct distance |
| --- | --- | ---: |
| PVIN12 to C1.1 | `(73.400,71.250)` to `(74.600,69.500)` | 2.122 mm |
| AVIN10 to C2.1 | `(73.400,72.250)` to `(74.675,72.600)` | 1.322 mm |
| SW2 to L1.1 | `(70.600,71.750)` to `(67.975,71.750)` | 2.625 mm |
| L1.2 to C3.1 | `(64.625,71.750)` to `(63.200,71.750)` | 1.425 mm |
| J3 pin 6/VCC to C6.1 | `(20.580,53.500)` to `(20.580,49.750)` | 3.750 mm |
| J3 pin 6/VCC to C5.1 | `(20.580,53.500)` to `(23.275,48.000)` | 6.125 mm |

`L1` is rotated 180 degrees specifically so its marked pad 1 (`BUCK_SW`)
faces U1 SW, and its pad 2 (`5V_SYS`) faces C3.  C1/C2 are outside the U1
courtyard, and the subsequent routing review must use a local PGND/EP return
and keep the SW copper only between U1 SW and L1.  No trace, via or copper
zone has been created by this placement correction.

For E220, C6 and C5 are now on the pin-row side of the socket, above the
21 x 36-mm module body/courtyard rather than below the installed module.  C6
is the closest high-frequency bypass; C5 is the nearby local bulk capacitor.

The declared DevKit antenna placeholder is
`X=104.700…142.700 mm`, `Y=52.000…90.000 mm`.  D2 was moved to `(96.500,
54.000)` mm; its F.Fab body stops at X=99.000 mm, leaving 5.700 mm to the
placeholder. U3/C7 and the complete TP1…TP10 bank were moved to the left;
TP10 is at `(93.000,87.000)` mm. An automated bounding-box audit finds no
non-DevKit footprint within the placeholder.

KiCad 10.0.5 `pcb drc` after regeneration reports **0 DRC violations** and
**0 footprint errors**. Its **72 unconnected items** are the expected
unrouted airwires and remain visible; they have not been excluded. The required
next gate is an independent placement review, not routing.
