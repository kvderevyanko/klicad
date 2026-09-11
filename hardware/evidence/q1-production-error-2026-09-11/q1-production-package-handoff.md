# Q1-corrected production package handoff

## SCOPE STATUS

`Q1-CORRECTED PRODUCTION PACKAGE GENERATED — SELF-AUDIT PASS`

- Release directory: `hardware/releases/rev1-q1-footprint-correction-2026-09-11/`
- Archive: `hardware/releases/ESP32-E220-Carrier-Rev1-Q1-Footprint-Correction-2026-09-11.zip`
- Archive SHA-256: `f73af617de933ccc6f5711d3044aae0209fe0a45801aee45330c778f160da43e`
- Archive size: 357981 bytes; 31 files; ZIP CRC and byte-for-byte tree comparison PASS.
- Source PCB SHA-256: `61549b45d4fe336986e76bcc78c5ca5532e67df604d155b140b1fd8a9d1bb109`
- Source schematic SHA-256: `8ade3ec2f6a90f39763b8dd5570fcfe1709e34482d2f83a886886c73e5a4dacc`
- Production metadata SHA-256: `806393fc7e9b32da32d34c3adb6357ec87d1d0236a449df42e610f37361dd639`
- Q1 footprint SHA-256: `a964b65e180fd9867d69eab31656367a13d0e120a503b78c8982a64b08626ebc`

Direct F.Cu Gerber audit found rectangular aperture D30=`0.800000 x
0.900000` at Q1 pad centres 1=(62.05,77.00), 2=(63.95,77.00), and
3=(63.00,75.00) mm. Gerber object/net attributes are 1=`Q1_GATE`,
2=`BUCK_IN`, 3=`BAT_SW`. IPC-D-356 independently carries the same Q1
pad/net map and 0.80 x 0.90 mm pad dimensions.

Excellon and drill-report counts agree: 119 PTH and 3 NPTH. The package also
contains the Gerber job file, IPC-D-356, BOM, direct KiCad CPL, THT and
DNP/user manifests, assembly/fabrication notes, assembly/silkscreen PDFs,
layer previews, drill maps, release manifest, self-audit, and per-file
checksums.

The active PCB hash was unchanged by generation. The tracked legacy
`hardware/releases/rev1/` tree and
`hardware/releases/ESP32-E220-Carrier-Rev1-PCBA.zip` are unchanged versus
repository HEAD. The legacy hard-coded `audit_rev1_release.py` was not used
to claim PASS; the retained Q1-specific generator and direct audit are
`generate_q1_corrected_release.sh` and `audit_q1_corrected_release.py`.

Implementation gate basis: ERC 0 errors / 0 warnings; parity PASS;
production metadata PASS; native DRC 0 unconnected and no Q1/geometric
errors. Two inherited `lib_footprint_mismatch` warnings for JP1/U4 remain
unchanged and unsuppressed.
