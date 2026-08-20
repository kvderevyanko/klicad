# Rev.1 scope-simplification rollback

Date: 2026-08-20

## Disposition

The first bounded generated-schematic transaction was rolled back in full.
No active PCB mutation occurred.

## Trigger

Native KiCad 10.0.5 ERC after the attempted source simplification reported one
new warning:

- `isolated_pin_label`: label `GPIO33` connected to only one pin.

Cause: removing J7 also removed the only remote endpoint of the existing
J1.9=`GPIO33` label. The initial transaction scope did not explicitly include
changing J1.9 from a labelled endpoint to an intentional no-connect, so the
new ERC finding was treated as unexpected and not repaired incrementally.

Evidence: `erc-after-source.json`.

## Restored-state proof

- Native ERC after rollback: 0 violations (`erc-restored.json`).
- Restored schematic SHA-256:
  `1607defc14cd9bc711566d671d53e996c54363b1dbd22effa2f1a1a0fd18f490`.
- Restored schematic generator SHA-256:
  `8b246f3ee05df31d8e41e470045aafe6d0b87fa61660cc62ef6be60ddc189ee3`.
- Restored footprint generator SHA-256:
  `e1227e1f5a19fc3867549d0fe8c812b3a9981161f3b9ca323bdbd70430083eb5`.
- Restored `fp-lib-table` SHA-256:
  `6e26f1f5051f7f506dfe9c2550baeb5820a82a56988c6a7fb50055a22c5e1a15`.
- Active PCB remained byte-identical, SHA-256:
  `bf502dfde6ebb1f05d5d8f95fa77dc6f3d484fd9ddcdb47d3511c4b82b5f5036`.

## Required revised transaction contract

Before retrying, explicitly include this deterministic consequence of J7
removal: J1.9 (the verified DevKit socket position for GPIO33) becomes an
intentional schematic no-connect. No other GPIO map or topology change is
implied.

The primary-source audit performed before the failed transaction remains
usable: WorldSemi's WS2812B-V5 document does not specify a DIN series resistor
or exact resistor value, so none may be invented; the proposed maximum-three-
pixel allocation is 3 x (36.0 mA RGB working current + 0.6 mA quiescent) =
109.800 mA.
