# U4 project-local footprint identity transaction

## Baseline

- Active board SHA-256: `6ce74f0e689d0f34d3dcdf50be797e553cbd168323aca1e6d358a146d7ff09e2`.
- Active schematic SHA-256: `7b2d4e786bb11b34214db266202a3fb6ec47f8bb2495d3ae834195f6154686ad`.
- Named board checkpoint: `10-esp32-e220.pre-u4-metadata.kicad_pcb`.
- Named schematic checkpoint: `10-esp32-e220.pre-u4-metadata.kicad_sch`.
- Pre-transaction fast contract: `PASS` in `00-pre-fast-contract.json`.
- Native DRC baseline after reviewed F1 and JP1 transactions: one
  `lib_footprint_mismatch` warning at U4, zero unconnected items and no physical
  DRC error.

## Exact scope

1. Add a generated project-local footprint named
   `Carrier:TI_TLV1117LV33DCYR_DCY_SOT223` that reproduces the active embedded
   U4 footprint's copper, paste, mask, F.Fab, F.CrtYd, pin-1 indication, and 3D
   model transform.
2. Change only U4's footprint identity in the schematic source generator,
   active schematic, and active PCB from the mutable system-library identity
   `Package_TO_SOT_SMD:SOT-223-3_TabPin2` to the new project-local identity.
3. Preserve U4 origin `(20.65, 27.00, 0 degrees)`, footprint/pad UUIDs, pad
   numbers `1/2/2/3`, pad centres, pad sizes, pad shapes, layer sets, nets, and
   all tracks/vias/zones.

## Expected delta

- Native DRC: remove exactly the remaining U4 `lib_footprint_mismatch`; expected
  result is zero DRC violations and zero unconnected items.
- ERC and schematic/PCB parity remain PASS.
- Copper/paste/mask Gerber and IPC-D-356 U4 pad coordinates and dimensions are
  byte/numerically unchanged relative to the named board checkpoint.
- No physical footprint approval is created by this transaction. TI's DCY
  package drawing supports package/pin compatibility, but TI publishes no
  recommended land pattern in the retained source; U4 remains package-drawing
  only / land-pattern `UNVERIFIED` pending the separately approved IPC record.

## Rollback rule

Any U4 physical geometry, net, route, zone, ERC/parity regression, unexpected
DRC item, or delta outside the allowlisted U4 identity/source metadata requires
restoring the two named checkpoints and stopping.
