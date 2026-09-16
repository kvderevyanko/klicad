# Rev.1 Q1+U3 footprint-correction release manifest

- Release: Rev.1-Q1-U3-Footprint-Correction-2026-09-15
- Supersedes for new fabrication: `hardware/releases/rev1-q1-footprint-correction-2026-09-11/` (preserved; do not mix files between releases)
- Source PCB SHA-256: ef7cc377eb670115295f39cbd963e8910f2f4047cf5d740728abd09e1e4f25ea
- Source schematic SHA-256: 8ade3ec2f6a90f39763b8dd5570fcfe1709e34482d2f83a886886c73e5a4dacc
- Production metadata SHA-256: 806393fc7e9b32da32d34c3adb6357ec87d1d0236a449df42e610f37361dd639
- Q1 project-local footprint SHA-256: a964b65e180fd9867d69eab31656367a13d0e120a503b78c8982a64b08626ebc
- U3 project-local footprint SHA-256: 2f63828381821ca805033f3636ae06bafa95a82920a5340e76069a7b5233bad3
- KiCad CLI: 10.0.6
- Generation/audit UTC: 2026-09-15T09:29:59+00:00
- Board: 145 x 90 mm, 2 layers
- Q1: Diodes Incorporated `DMP3130LQ-7`, project footprint `Diodes_DMP3130LQ-7_SOT23`
- Q1 F.Cu pads: 1=(62.05, 77.00), 2=(63.95, 77.00), 3=(63.00, 75.00) mm; each 0.80 x 0.90 mm
- Q1 pad/net map: 1=`Q1_GATE`, 2=`BUCK_IN`, 3=`BAT_SW`
- U3: TI `SN74AHCT1G125DBVR`, DBV0005A `4214839/K`, project footprint `TI_SN74AHCT1G125DBVR_SOT23-5`
- U3 F.Cu pads: 1=(88.05,55.30), 2=(89.00,55.30), 3=(89.95,55.30), 4=(89.95,52.70), 5=(88.05,52.70) mm; each 0.60 x 1.10 mm, R0.05
- U3 pad/net map: 1=`GND`, 2=`WS2812_DATA_3V3`, 3=`GND`, 4=`WS2812_DATA_5V`, 5=`5V_SYS`
- Drill: 119 PTH, 3 NPTH; metric decimal Excellon
- Implementation reviewer: `U3 FOOTPRINT CORRECTION IMPLEMENTATION PASS`; `REVIEW PASS`
- ERC: 0 errors / 0 warnings
- Native DRC: 0 unconnected; 0 Q1/footprint/geometric errors; two unchanged inherited library-mismatch warnings (JP1, U4)
- Parity: PASS
- Production metadata: PASS
- Package integrity self-audit: PASS
- Full physical-footprint audit disposition: HOLD — remaining populated MPNs are UNVERIFIED; this package is NOT SAFE FOR PRODUCTION.

This directory is one indivisible production revision. Do not combine its
Gerbers, drills, IPC-D-356, BOM, CPL, or documentation with the preserved
previous Q1-correction package. The Q1 and U3 copper checks above were read
directly from the generated F.Cu Gerber and IPC-D-356, not inferred only from
the KiCad board.  Do not submit this package for manufacture until every
UNVERIFIED populated MPN has a retained primary numerical comparison.
