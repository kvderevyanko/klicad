# CPL rotation notes

CPL_SMD_REV1.csv is KiCad's direct position export. Its X, Y, side, and
rotation are authoritative board-export values; do not remap angles to an
assembler convention without validating that assembler's import preview.

Orientation-sensitive SMT items include U1 TPS62133, U3 SN74AHCT1G125,
U4 TLV1117LV33, Q1 DMP3130LQ-7, and polarized/marked capacitors where the
assembler's library requires orientation. D3 SMBJ10CA is bidirectional and
F1 is non-polar. Use assembly-top.pdf and silkscreen-top.pdf to map any
vendor-specific rotation convention.
