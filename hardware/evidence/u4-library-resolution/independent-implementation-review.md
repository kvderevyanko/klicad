# Independent U4 source/metadata implementation review

Scope: read-only implementation gate for the U4 project-local footprint
identity transaction only. Reviewed 2026-09-16 against the named retained
checkpoint `hardware/evidence/full-production-audit-2026-09-15/u4-library-resolution/10-esp32-e220.pre-u4-metadata.kicad_pcb`.

## Mandatory entry checks

- `python3 hardware/check_board_contract.py --reference <named checkpoint>`:
  PASS. The protected checkpoint, duplicate-pad/net invariant, netless-pad
  check, antenna exclusion, schematic/PCB parity, and native DRC summary all
  PASS (`independent-review-contract.json`).
- Native KiCad DRC: 0 violations and 0 unconnected items
  (`independent-review-native-drc.json`).
- Native KiCad ERC: 0 violations (`independent-review-native-erc.json`).
- Direct schematic/PCB parity: PASS, no electrical pad/net mismatch
  (`independent-review-parity.json`).

No deterministic blocker exists for this bounded gate. The initial contract
without `--reference` was intentionally not used as a verdict because its
mandatory protected checkpoint is INCONCLUSIVE without a reference.

## Independent evidence assessment

The active schematic, PCB, and generator now agree on the durable identity
`Carrier:TI_TLV1117LV33DCYR_DCY_SOT223`. The project-local module is generated
by `hardware/generate_stage7_footprints.py`; the schematic generator mapping is
in `hardware/generate_esp32_e220.py`. `check_u4_dcy_footprint.py` independently
passes on the active files (`independent-review-u4-invariant.json`): local module
equals generator output; U4's footprint and all pad UUIDs are retained; and
reverting only identity/description/tags reconstructs the named checkpoint.

The retained physical data are unchanged:

| Land | local centre mm | size mm | net |
|---|---:|---:|---|
| 1 | (-3.15, -2.30) | 2.00 x 1.50 | GND |
| 2 lead | (-3.15, 0.00) | 2.00 x 1.50 | AUX_3V3 |
| 2 tab | (+3.15, 0.00) | 2.00 x 3.80 | AUX_3V3 |
| 3 | (-3.15, +2.30) | 2.00 x 1.50 | 5V_SYS |

Origin/rotation remain `(20.65, 27.00, 0 degrees)`. The invariant also retains
the rectangular copper/paste/mask land type, F.Fab bbox
`(-1.85,-3.35)..(+1.85,+3.35)`, F.CrtYd bbox
`(-4.40,-3.60)..(+4.40,+3.60)`, pad numbering `1/2/2/3`, and their nets. The
transaction's diagnostic comparison independently finds all relevant Gerber
layers numerically identical after volatile-header removal and the complete
IPC-D-356 files byte-identical (`35-diagnostic-export-audit.json`). Therefore
the change removes only mutable-library metadata/version drift; it does not
change U4 copper, paste, mask, fabrication/courtyard data, routing, zones, or
pin/net connectivity.

TI primary evidence retained in
`hardware/evidence/full-production-audit-2026-09-15/primary/ti-tlv1117lv.pdf`
and the primary-source audit identifies `TLV1117LV33DCYR` as DCY/SOT-223:
2.30-mm lead pitch and pin-2 tab. The physical pin mapping remains pin 1 ->
GND, pin 2 lead and tab -> AUX_3V3/OUT, pin 3 -> 5V_SYS/IN. TI's retained DCY
drawing MPDS094A/4202506/B does not publish a recommended PCB land pattern.

## Findings

- NOTE — The prior `lib_footprint_mismatch` was a system-library
  presentation/version-drift warning. It is now removed without suppressions.
- NOTE — U4 remains `UNVERIFIED manufacturer land pattern; package-drawing
  compatible / frozen project IPC`. This gate must not be read as a TI
  manufacturer-land-pattern PASS or as production-release approval.

SCOPE VERDICT: U4 SOURCE/METADATA PASS

REVIEW PASS
