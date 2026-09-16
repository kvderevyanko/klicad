# JP1 physical correction transaction scope

Date: 2026-09-16

Authoritative manufacturer evidence: Samtec TSW series drawing and TSW
recommended PCB layout retained in the parent scope `primary/` directory.

## Fixed scope

- Add the exact project-local footprint identity
  `Carrier:Samtec_TSW-102-07-G-S_1x02_P2.54mm_THT` to
  `generate_stage7_footprints.py` and its generated `.pretty` library.
- Change only JP1's schematic footprint metadata in
  `generate_esp32_e220.py` and `esp32-e220.kicad_sch`; no symbol, pin, value,
  net, or wire changes.
- Replace only the embedded JP1 footprint in the active PCB while retaining
  footprint UUID, origin/pad 1 (96.000, 14.000), pad 2 (98.540, 14.000),
  rotation 90 degrees, two pad UUIDs, 1.70 x 1.70-mm copper, pad numbering,
  nets, and every route.
- Change both JP1 holes from 1.000 to 1.020 mm per the Samtec recommended
  layout.  Source-current delta is +0.020 mm drill diameter only.

## Expected machine-check delta

- Fast contract: PASS before and after; count/topology/protected geometry
  unchanged.
- Native DRC: `lib_footprint_mismatch` count changes from 2 to 1 by removing
  only the JP1 generic-library mismatch; the U4 mismatch remains explicit.
- Native DRC geometric violations, zone errors, and unconnected items remain
  zero.
- Native ERC remains zero violations.
- Project schematic/PCB parity remains PASS.

Any other active-board or electrical change, any new category, or any
unexpected check failure requires rollback to the named `10-*.pre-jp1`
backups, restored-state proof, and STOP.
