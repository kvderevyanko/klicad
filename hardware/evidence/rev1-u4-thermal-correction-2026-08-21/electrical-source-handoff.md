# Rev.1 U4 thermal-policy electrical-source handoff

Date: 2026-08-21

## Disposition

The user-authorized U4 thermal-policy correction was implemented as a
documentation-only generated-source transaction. Electrical topology, symbol
definitions, footprints, component properties, and U4 package-pad mapping were
not changed. The active PCB was not edited.

## Exact source delta

Only the U4 physical-policy note changed in:

- `hardware/generate_esp32_e220.py`;
- generated `hardware/esp32-e220.kicad_sch`.

The cancelled `>=20x20mm` F.Cu/B.Cu islands and mandatory four-via requirement
were replaced with this controlling wording:

`U4 THERMAL POLICY @ 100.1mA 5V_SYS ALLOCATION: PAD1=GND; PAD2 LEAD+TAB=AUX_3V3; PAD3=5V_SYS. USE ORDINARY PROPORTIONATE LOCAL F.Cu ON OUT/TAB; B.Cu AUX_3V3 ISLAND / THERMAL-VIA ARRAY ONLY IF ANALYSIS REQUIRES.`

The exact pre/post diffs contain one changed note line in each file. Searches
of both current files find no remaining `20x20`, mandatory-four-via, or 300-mA
U4 instruction.

## Retained backup and hashes

| Artifact | SHA-256 |
| --- | --- |
| `generate_esp32_e220.pre-u4-thermal-policy-correction.py` | `90e7cc637f6b113d229e73981b040e6ca7a6c01ba3ab7885d7df0485e0532e27` |
| `esp32-e220.pre-u4-thermal-policy-correction.kicad_sch` | `c64364474e06d0f95523667bc0da6f9d4df6c4f023a7ddc1f876c488f631508c` |
| post-change `hardware/generate_esp32_e220.py` | `942d89b918c9e6a56ecb5bd935bef07a29c2fe695547324474247b0bfcae9482` |
| post-change `hardware/esp32-e220.kicad_sch` | `8ade3ec2f6a90f39763b8dd5570fcfe1709e34482d2f83a886886c73e5a4dacc` |
| unchanged `hardware/esp32-e220.kicad_sym` | `a2290fea4781d92b4987119117c9d389676ce7893a7129bdf53b3c1195af9e03` |
| unchanged `hardware/sym-lib-table` | `7f62e52557e75942e03fe36b9666a6d962029517dd2afde2d07fa3e10e0f1a52` |
| unchanged active PCB | `bf502dfde6ebb1f05d5d8f95fa77dc6f3d484fd9ddcdb47d3511c4b82b5f5036` |

Two consecutive source generations produced the same post-change schematic,
symbol-library, and symbol-table hashes.

## Validation

- Native KiCad 10.0.5 ERC: `0 errors / 0 warnings / 0 violations`.
  Artifact: `esp32-e220-post-source-correction-erc.rpt`.
- Schematic-PCB parity against retained successful candidate SHA-256
  `b10bc94138397f3d3d393804dd02d285b2f19eaa5c3341b920835085dbf23464`:
  `PASS`; 37 assembled schematic items, 37 PCB footprints, only R10/R11 as
  intentional `NO_FOOTPRINT_DNP`, and no reference, pad-net, raw-net, or
  production-property mismatches. Artifact:
  `post-source-correction-retained-candidate-parity.json`.
- KiCad pre/post netlist exports were retained. Their source-path metadata
  differs because the backup is stored in the evidence directory; the exact
  schematic diff and parity gate prove that the electrical content did not
  change.
- A pre-transaction fast contract against the active PCB reproduced its known
  rejected-state U4 duplicate-pad/netless-tab and antenna failures. This was
  expected from the current-state handoff, caused no source rollback, and the
  active PCB remained byte-identical.

## Risk and next gate

There is no electrical or parity impact from this wording-only correction.
The next electrical-source action is a bounded independent reviewer check of
the revised U4 note; physical planning and implementation remain owned by the
planner/layout/reviewer gate sequence.
