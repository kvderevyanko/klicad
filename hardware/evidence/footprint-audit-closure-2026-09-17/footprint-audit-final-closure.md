# Final component-footprint audit closure

Approved active baseline: `ecfb03b79c6a41063ac21f1f7dc79750468a8b3a` on
`audit/full-footprint-review-2026-09-16`.

## Closure status

- Physical footprint FAIL: **0**.
- UNVERIFIED: **0**.
- R3/R4: **MANUFACTURER LAND PATTERN PASS**, based on
  `RC0603FR-0710KL` / `RC0603FR-073K3L`, Yageo Mounting V10
  Fig. 4/Table 1, and the implemented PCB/Gerber/IPC evidence retained in the
  preceding approved resistor implementation checkpoint.
- R1/R2/R8/R9: implemented land pattern remains physically closed; production
  procurement is conditional on the exact substitute MPN satisfying the recorded
  physical-substitution restriction.
- All previously closed footprints remain closed. In particular, current Q1, U3,
  F1, JP1, D3, C1..C10, U4, and R1/R2/R3/R4/R8/R9 geometry is unchanged from the
  approved active baseline.

## Final PCBA component-footprint matrix

| Ref(s) | MPN / procurement class | Package | Evidence source | Evidence class | Implemented geometry | Final status |
|---|---|---|---|---|---|---|
| C2,C4,C6,C7,C8 | Murata GRM188 variants | 1608M | Murata Table 2 | MANUFACTURER LAND PATTERN PASS | Approved current geometry | PASS |
| C5 | GRM188R61A106MAAL | 1608M | Murata Table 2 | MANUFACTURER LAND PATTERN PASS | Approved current geometry | PASS |
| C1,C9,C10 | GRM21BR61E106KA73 | 2012M | Murata Table 2 | MANUFACTURER LAND PATTERN PASS | Approved current geometry | PASS |
| C3 | GRM21BR61A226ME44 | 2012M | Murata Table 2 | MANUFACTURER LAND PATTERN PASS | Approved current geometry | PASS |
| D3 | Littelfuse SMBJ10CA | DO-214AA | Littelfuse solder-pad drawing | MANUFACTURER LAND PATTERN PASS | Approved current geometry | PASS |
| F1 | Littelfuse 1812L200/16 | 4532 | Littelfuse pad layout | MANUFACTURER LAND PATTERN PASS | Approved current geometry | PASS |
| L1 | Coilcraft XFL4020-222MEB | 4020 | Coilcraft recommended land pattern | MANUFACTURER LAND PATTERN PASS | Approved current geometry | PASS for specified MPN; conditional only if substituted |
| Q1 | DMP3130LQ-7 | SOT-23 | Diodes suggested layout | MANUFACTURER LAND PATTERN PASS | Approved current geometry | PASS |
| R3 | RC0603FR-0710KL | 0603/1608 | Yageo RC + Mounting V10 | MANUFACTURER LAND PATTERN PASS | Approved Yageo shared lands | PASS |
| R4 | RC0603FR-073K3L | 0603/1608 | Yageo RC + Mounting V10 | MANUFACTURER LAND PATTERN PASS | Approved Yageo shared lands | PASS |
| R1,R2,R8,R9 | APPROVED_GENERIC | 0603/1608 | Recorded physical-substitution restriction | PROCUREMENT-CONDITIONAL | Approved Yageo shared lands | Exact production MPN confirmation required |
| U1 | TPS62133RGT | RGT VQFN-16 | TI layout example | MANUFACTURER LAND PATTERN PASS | Approved current geometry | PASS |
| U3 | SN74AHCT1G125DBVR | DBV/SOT-23-5 | TI DBV0005A | MANUFACTURER LAND PATTERN PASS | Approved current geometry | PASS |
| U4 | TLV1117LV33DCYR | DCY/SOT-223 | TI drawing 4210278/C | MANUFACTURER LAND PATTERN PASS | Approved current geometry | PASS |
| J1,J2 | SSW-115-02-G-S | 1x15 socket | Samtec drill/pitch + project annular ring | ENGINEERING-FIT PASS | Approved current geometry | PASS |
| J3 | SSW-107-02-G-S | 1x7 socket | Samtec drill/pitch + project annular ring | ENGINEERING-FIT PASS | Approved current geometry | PASS |
| J5 | SSW-104-02-G-S | 1x4 socket | Samtec drill/pitch + project annular ring | ENGINEERING-FIT PASS | Approved current geometry | PASS |
| JP1 | TSW-102-07-G-S | 1x2 header | Samtec layout | ENGINEERING-FIT PASS | Approved current geometry | PASS |
| J4,J8 | JST B2B-XH-A | XH 1x2 | JST drill/pitch + project annular ring | ENGINEERING-FIT PASS | Approved current geometry | PASS |

## Procurement conditions before production release

1. For R1/R2/R8/R9, PCBWAVE must identify the exact production substitute MPN.
   It must be a standard two-terminal 0603 imperial / 1608 metric chip resistor
   with conventional wraparound terminals and a manufacturer package/mounting
   recommendation compatible with 0.900 x 0.800 mm lands on 1.700-mm pitch,
   0.800-mm inner gap, and 2.600-mm span. 0402, 0805, special-terminal,
   reverse-geometry, and non-standard 0603 variants are excluded.
2. L1 `XFL4020-222MEB` itself is **MANUFACTURER LAND PATTERN PASS**. If PCBWAVE
   installs this specified MPN, its footprint gate is closed. If it is unavailable
   and PCBWAVE proposes a substitute, the exact substitute MPN and datasheet must
   receive external footprint-compatibility review before production release.
   A same-parameter substitute is not implicitly approved.

L1 production metadata, specified MPN, and footprint were not changed in this
transaction.

## Controlled documentation/metadata transaction

The resistor generator, project-local footprint, and embedded R1/R2/R3/R4/R8/R9
descriptions now consistently exclude no-footprint DNP R10/R11 and state the
implemented Yageo mounting geometry. R1/R2/R8/R9 metadata retains resistance,
tolerance, minimum rating, package, and `APPROVED_GENERIC`; it adds the exact
physical-substitution restriction and constrains substitutions to it.

`20-final-closure-resistor-invariant.json` proves exact target geometry and zero
pad/track/via/zone-rule/net/placement/identity delta. Native ERC and DRC remain
clean. No Gerbers, drills, release archive, or other manufacturing output was
generated because fabrication geometry did not change.
