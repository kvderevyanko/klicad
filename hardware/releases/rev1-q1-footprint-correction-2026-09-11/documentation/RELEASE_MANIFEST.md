# Rev.1 Q1 footprint-correction release manifest

- Release: Rev.1-Q1-Footprint-Correction-2026-09-11
- Supersedes for new fabrication: `hardware/releases/rev1/` (preserved; do not mix files between releases)
- Source PCB SHA-256: 61549b45d4fe336986e76bcc78c5ca5532e67df604d155b140b1fd8a9d1bb109
- Source schematic SHA-256: 8ade3ec2f6a90f39763b8dd5570fcfe1709e34482d2f83a886886c73e5a4dacc
- Production metadata SHA-256: 806393fc7e9b32da32d34c3adb6357ec87d1d0236a449df42e610f37361dd639
- Q1 project-local footprint SHA-256: a964b65e180fd9867d69eab31656367a13d0e120a503b78c8982a64b08626ebc
- KiCad CLI: 10.0.6
- Generation/audit UTC: 2026-09-11T04:40:17+00:00
- Board: 145 x 90 mm, 2 layers
- Q1: Diodes Incorporated `DMP3130LQ-7`, project footprint `Diodes_DMP3130LQ-7_SOT23`
- Q1 F.Cu pads: 1=(62.05, 77.00), 2=(63.95, 77.00), 3=(63.00, 75.00) mm; each 0.80 x 0.90 mm
- Q1 pad/net map: 1=`Q1_GATE`, 2=`BUCK_IN`, 3=`BAT_SW`
- Drill: 119 PTH, 3 NPTH; metric decimal Excellon
- Implementation reviewer: `Q1 FOOTPRINT CORRECTION IMPLEMENTATION PASS`; `REVIEW PASS`
- ERC: 0 errors / 0 warnings
- Native DRC: 0 unconnected; 0 Q1/footprint/geometric errors; two unchanged inherited library-mismatch warnings (JP1, U4)
- Parity: PASS
- Production metadata: PASS
- Package self-audit: PASS

This directory is one indivisible production revision. Do not combine its
Gerbers, drills, IPC-D-356, BOM, CPL, or documentation with the preserved
legacy Rev.1 package. The Q1 copper checks above were read directly from the
generated F.Cu Gerber, not inferred only from the KiCad board.
