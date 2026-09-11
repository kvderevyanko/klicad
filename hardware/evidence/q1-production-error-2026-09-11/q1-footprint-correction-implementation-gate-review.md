# Independent implementation gate — Q1 footprint correction

## Scope and checkpoint

Read-only review of the active implementation against
`esp32-e220-q1-prechange-reference.kicad_pcb` and the retained primary Diodes
evidence. The named checkpoint and implementation backup have SHA-256
`dd4d77d521adc1fd744d10b6e05f4a27169e30d988f70a3b9e50236608fda0e4`.
No controlled source was modified by this reviewer.

## Findings

- **NOTE — implemented land pattern:** DS38728 p. 5 defines `X1=1.35 mm` to
  the lower-land outer edge. With `X=0.80 mm`, the active pad centres are now
  the required `(-0.950,+1.000)` / `(+0.950,+1.000)` mm. Pad 3 remains
  `(0,-1.000)` mm; all pads remain `0.80 x 0.90 mm`.
- **NOTE — pin-map retention:** active schematic/board parity confirms
  pin/pad 1=`Q1_GATE`/Diodes G, 2=`BUCK_IN`/Diodes S, and 3=`BAT_SW`/Diodes D.
  Q1 origin, rotation, pad numbering, and pad 3 are unchanged.
- **NOTE — bounded physical work:** only the approved F.Fab/F.CrtYd graphics
  and three F.Cu segment starts changed. The gate's delta checker passes,
  including equality of all other board semantics and byte identity between
  the local footprint and `generate_stage7_footprints.py` output. No via,
  zone, rule-area, keepout, component origin, width, layer, or downstream
  endpoint changed.
- **NOTE — verified package representation:** the F.Fab body is `1.30 x 2.90`
  mm (Diodes nominal `B x H`) and the project courtyard is `3.20 x 3.40` mm;
  the latter is a conservative project rule, not a manufacturer land
  dimension. The retained pad-1 silkscreen marker remains clear of the pad-3
  mask opening.
- **NOTE — machine gates independently rerun:** Q1 implementation delta PASS;
  schematic/PCB parity PASS; production metadata PASS; ERC has 0 errors and
  0 warnings. Native DRC has 0 unconnected pads and 0 footprint/geometric
  errors.
- **NOTE — inherited warning baseline:** native DRC still reports exactly two
  pre-existing `lib_footprint_mismatch` warnings, JP1 and U4, with no Q1
  warning and no pre/post category/count delta. `check_board_contract.py`
  therefore returns overall FAIL solely because it promotes those warnings;
  every affected contract subsection, including protected checkpoint and
  parity, is PASS.

`CONTEXT PROVENANCE CONFLICT`: `docs/agent-context.md` states zero native DRC
violations, while the retained pre-change and independently rerun post-change
DRC each show the two inherited JP1/U4 library-mismatch warnings. They are
outside this scope, unchanged, and unsuppressed.

SCOPE VERDICT: Q1 FOOTPRINT CORRECTION IMPLEMENTATION PASS

REVIEW PASS
