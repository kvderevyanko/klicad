# Rev.1 final integration rollback proof

`SCOPE STATUS: IMPLEMENTATION ATTEMPT REJECTED; ACTIVE BOARD RESTORED; STOP`

## Stop condition

The attempted final active board retained AUX_3V3 copper islands of X=17.5..37.5 mm and Y=16.0..38.0 mm on both F.Cu and B.Cu: 20 x 22 mm per layer. The simplified Rev.1 scope prohibited retaining giant approximately 20 x 20 mm islands unless actual TI thermal analysis required them. The retained plan/evidence established the approximately 100-mA OLED allocation but did not establish that thermal requirement.

## Retained attempted checkpoint

- Attempted final checkpoint: `07-final-approved-checkpoint.kicad_pcb`.
- Attempted final SHA-256: `b10bc94138397f3d3d393804dd02d285b2f19eaa5c3341b920835085dbf23464`.
- The full attempted transaction evidence remains in this directory and is historical only.

## Exact restoration proof

- Restoration source: `hardware/esp32-e220-rev1-partial-rejected.kicad_pcb`.
- Recorded rejected-board SHA-256: `bf502dfde6ebb1f05d5d8f95fa77dc6f3d484fd9ddcdb47d3511c4b82b5f5036`.
- Restored active-board SHA-256: `bf502dfde6ebb1f05d5d8f95fa77dc6f3d484fd9ddcdb47d3511c4b82b5f5036`.
- `rollback-restored-fast-contract.json` is byte-identical to `active-pre-recovery-fast-contract.json`.

The restored contract intentionally reproduces the known rejected state: protected buck geometry PASS, two layers PASS, 145 x 90 mm PASS, and the same known duplicate-U4-pad, antenna-intrusion, and stale-parity-era board defects. This expected FAIL is proof of exact pre-recovery restoration, not an approval.

No alternate thermal copper, placement, routing, or other PCB change was attempted after the stop condition.

`ROUTING PLAN REVISION REQUIRED`
