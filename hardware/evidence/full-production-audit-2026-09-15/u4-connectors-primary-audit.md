# U4 and populated connector primary-source audit

Scope: U4, JP1, J1/J2/J3/J5, J4/J8.  Evidence is the active PCB and
schematic, the prior final U3 Gerber set under
`hardware/releases/rev1-q1-u3-footprint-correction-2026-09-15/`, and retained
manufacturer documents in `primary/`.  Coordinates below are local footprint
coordinates unless stated otherwise; Gerber/IPC dimensions use the IPC-D-356
values, which are in inches (converted in parentheses).

## Sources retained

| Manufacturer | MPN/source | Retained primary evidence |
|---|---|---|
| Texas Instruments | TLV1117LV33DCYR, TLV1117LV datasheet SBVS160C, DCY drawing MPDS094A/4202506/B | `primary/ti-tlv1117lv.pdf` |
| Samtec | SSW-115-02-G-S / SSW-107-02-G-S / SSW-104-02-G-S, SSW single-row recommended PCB layout | `primary/samtec-ssw-series-print.pdf`, `primary/samtec-ssw-single-row-footprint.pdf` |
| Samtec | TSW-102-07-G-S, TSW recommended PCB layout | `primary/samtec-tsw-series-print.pdf`, `primary/samtec-tsw-footprint.pdf` |
| JST | B2B-XH-A, XH connector drawing eXH | `primary/jst-exh.pdf` |

The source URLs are respectively `https://www.ti.com/lit/ds/symlink/tlv1117lv.pdf`,
`https://suddendocs.samtec.com/prints/ssw-1xx-xx-xxx-x-xx-xxx-xx-mkt.pdf`,
`https://suddendocs.samtec.com/prints/ssw-s.pdf`,
`https://suddendocs.samtec.com/prints/tsw-xxx-xx-xxx-x-xx-xxx-mkt.pdf`,
`https://suddendocs.samtec.com/prints/tsw-xxx-xx-x-x-xx-xxx-footprint.pdf`, and
`https://www.jst-mfg.com/product/pdf/eng/eXH.pdf`.

## Numerical comparison and pad/net evidence

| Ref(s) / MPN | Primary package / manufacturer's board data | Project-local / embedded PCB | Final Gerber / IPC-D-356 | Pin-to-pad-to-net result |
|---|---|---|---|---|
| U4 / TLV1117LV33DCYR | DCY SOT-223, 4 leads. Body L=6.30..6.70, W=3.30..3.70; lead pitch 2.30; lead width=0.66..0.84; lead length >=0.75; tab is pin 2. TI gives no recommended land pattern. | `Package_TO_SOT_SMD:SOT-223-3_TabPin2`; pad 1=(-3.15,-2.30), 2 lead=(-3.15,0), 2 tab=(+3.15,0), 3=(-3.15,+2.30); 2.00x1.50 for leads, 2.00x3.80 tab. Fab=6.70x3.70. | U4 pads 1/2/2/3: (6.890,-9.724)/(6.890,-10.630)/(9.370,-10.630)/(6.890,-11.535) in; copper 0.0787x0.0591 / tab 0.0787x0.1496 in = 2.00x1.50 / 2.00x3.80 mm. | TI pin 1 -> PCB 1 -> GND; pin 2 + tab -> PCB 2 -> AUX_3V3; pin 3 -> PCB 3 -> 5V_SYS. Exact schematic and IPC mapping. |
| JP1 / TSW-102-07-G-S | TSW single-row 2 positions; 2.54 pitch; 0.635-mm square post. Official recommended layout: 1.02-mm (0.040-in) finished/drill diameter. | Schematic calls generic KiCad `PinHeader_1x02_P2.54mm_Vertical`; embedded footprint holes=(0,0)/(0,2.54), drill=1.000 mm, Cu=1.70x1.70. | IPC centers (37.795,-5.512)/(38.795,-5.512) in after board 90-degree rotation, pitch 2.540 mm; PTH tool T2=1.000 mm. | physical pin 1 -> pad 1 -> 5V_SYS; physical pin 2 -> pad 2 -> DEVKIT_VIN. Net mapping matches schematic/IPC. **Hole delta: -0.020 mm versus Samtec recommendation.** |
| J1,J2 / SSW-115-02-G-S | SSW-S single row; 15 positions; 2.54 pitch; 1.04-mm (0.041-in) drill. Contact tail 0.79x0.41; body single-row width 2.41 ref. | Generated `Samtec_SSW_1x15_P2.54mm_THT`: 15 pads, (0,0)..(0,35.56), pitch 2.54; drill 1.040; Cu=1.70x1.70; Fab width 2.41; pin-1 rectangle/marker. | IPC D0409=1.039 mm drill; copper=1.699x1.699; 15 pads each, 2.540-mm pitch. | J1 pads 1..15: DEVKIT_VIN,GND,GPIO13,N/C,GPIO14,E220_AUX,E220_M1,E220_M0,N/C,BAT_SENSE,N/C,N/C,N/C,N/C,N/C. J2: DEVKIT_3V3,GND,N/C,N/C,WS2812_DATA_3V3,E220_TXD,E220_RXD,N/C,GPIO18,GPIO19,OLED_SDA,N/C,N/C,OLED_SCL,GPIO23. All physical pad numbers equal schematic/IPC pad numbers. |
| J3 / SSW-107-02-G-S | SSW-S single row; 7 positions; same 2.54 pitch and 1.04-mm drill requirement. | Generated `Samtec_SSW_1x07_P2.54mm_THT`: 7 pads, span 15.24, drill 1.040, Cu=1.70, Fab width 2.41, pin-1 marker. | IPC D0409=1.039-mm drill, Cu=1.699; seven 2.540-mm-spaced pads. | pads 1..7: E220_M0,E220_M1,E220_RXD,E220_TXD,E220_AUX,5V_SYS,GND; exact schematic/IPC mapping. |
| J5 / SSW-104-02-G-S | SSW-S single row; 4 positions; same 2.54 pitch and 1.04-mm drill requirement. | Generated `Samtec_SSW_1x04_P2.54mm_THT`: 4 pads, span 7.62, drill 1.040, Cu=1.70, Fab width 2.41, pin-1 marker. | IPC D0409=1.039-mm drill, Cu=1.699; four 2.540-mm-spaced pads. | pads 1..4: GND,AUX_3V3,OLED_SCL,OLED_SDA; exact schematic/IPC mapping. |
| J4,J8 / JST B2B-XH-A | XH top-entry 2-position header: 2.50-mm pitch, 0.64-mm square posts, 7.4-mm body length and 5.75-mm body depth. JST PCB layout identifies No.1 circuit and uses 1.00-mm drill for this header family. | Generated `JST_B2B-XH-A_1x02_P2.50mm_THT`: pads (0,0)/(2.50,0), drill=1.000; Cu=1.70x2.00; Fab 7.40x5.75; rectangular pad 1 and silk pin-1 side. | IPC D0394=1.0008-mm drill; copper=1.699x1.999; centres are 2.500 mm apart. | J4: 1=BAT_PLUS, 2=GND. J8: 1=BAT_FUSED, 2=BAT_SW. Both match schematic/IPC and No.1 indication. |

## Native `lib_footprint_mismatch` warnings

| Reference | Exact board-to-current-KiCad-library delta | Manufacturer physical implication |
|---|---|---|
| U4 | Copper centers and sizes are identical. The embedded legacy copy has rectangular pads and its top silk starts at x=-4.10; current KiCad 10 has roundrect pads and starts at x=-1.85 with a filled pin-1 triangle. The Fab/courtyard and pad coordinates/sizes remain unchanged. | This is stale KiCad presentation/metadata, **not** a detected DCY physical copper mismatch. TI gives no manufacturer land pattern, therefore this does not convert the U4 land pattern into a manufacturer-land-pattern approval. |
| JP1 | The embedded legacy generic header has 1.000-mm holes (pad 2 oval); current KiCad library also uses 1.000-mm holes but different graphics/pad style. The active source declares the generic KiCad header, not a Samtec-specific footprint. | The DRC warning itself is presentation/version drift, but it exposes an independent physical problem: the Gerber drill is 1.000 mm versus Samtec's 1.020-mm recommended layout. It is not harmless metadata. |

## Disposition

- U4 is mechanically and electrically consistent with TI's DCY package drawing, but its copper pattern is an IPC/KiCad pattern, not a manufacturer-specified land pattern: do not label it `manufacturer-land-pattern PASS` without an authoritative TI land-pattern source or an explicit approved IPC calculation record.
- J1/J2/J3/J5 and J4/J8 match the manufacturers' hole coordinate/drill requirements, pad count, package dimensions, polarity indication, and IPC net records.
- JP1 is a concrete numerical mismatch and needs a controlled footprint/source/PCB transaction: required drill 1.020 mm, current generated Gerber 1.000 mm, delta -0.020 mm. Its 2.540-mm pitch, count, numbering and nets are otherwise correct.

