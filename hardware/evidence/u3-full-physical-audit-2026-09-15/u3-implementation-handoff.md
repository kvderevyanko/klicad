# U3 TI DBV physical implementation handoff

Role/scope: `pcb_layout_dfm`; bounded implementation after the retained
`SCOPE VERDICT: U3 PHYSICAL PLAN PASS` and independent `REVIEW PASS` in
`u3-physical-plan-review.md`. No schematic, topology, component value,
placement, via, zone boundary, rule area, or unrelated footprint changed.

## SCOPE STATUS

`U3 TI DBV PHYSICAL IMPLEMENTATION COMPLETE; IMPLEMENTATION REVIEW REQUIRED`

The active U3 remains at `(89.000,54.000) mm`, rotation `0 deg`, F.Cu. Its
TI DBV0005A `4214839/K` geometry is now:

| Pad | local centre mm | absolute centre mm | copper/paste mm | R | net/function |
|---|---:|---:|---:|---:|---|
| 1 | `(-0.950,+1.300)` | `(88.050,55.300)` | `0.600 x 1.100` | `0.05` | `/GND`, OE low |
| 2 | `(0.000,+1.300)` | `(89.000,55.300)` | `0.600 x 1.100` | `0.05` | `/WS2812_DATA_3V3`, A |
| 3 | `(+0.950,+1.300)` | `(89.950,55.300)` | `0.600 x 1.100` | `0.05` | `/GND`, GND |
| 4 | `(+0.950,-1.300)` | `(89.950,52.700)` | `0.600 x 1.100` | `0.05` | `/WS2812_DATA_5V`, Y |
| 5 | `(-0.950,-1.300)` | `(88.050,52.700)` | `0.600 x 1.100` | `0.05` | `/5V_SYS`, VCC |

Row-centre spacing is `2.60 mm`; pad 1-to-3 centre span and pad 5-to-4
centre span are both `1.90 mm`. The mask expansion remains `0.05 mm`.
F.Fab is the drawing-derived nominal rotated `1.60 x 2.90 mm` body with the
pin-1-side chamfer. F.CrtYd is `3.60 x 4.20 mm` (`x=+/-1.80`,
`y=+/-2.10 mm`). The F.SilkS pin-1 circle is centred at
`(-1.550,+1.750) mm`, clear of pad-1 mask.

Exactly five existing F.Cu segment endpoints were re-anchored. Opposite
endpoints, UUIDs, nets, layers, and widths are unchanged:

| UUID | corrected U3 endpoint -> retained endpoint | width/net |
|---|---|---|
| `8b5ac9dc-4208-4f80-99be-6912b8d39d52` | `(88.050,55.300) -> (87.200,56.500)` | `0.50`, `/GND` |
| `02e750f7-1ae2-44c5-9fc4-c55c2823b1e9` | `(89.000,55.300) -> (89.000,58.000)` | `0.25`, `/WS2812_DATA_3V3` |
| `6308e9af-e3b4-4509-b16a-d1588a1cc74b` | `(89.950,55.300) -> (91.000,55.000)` | `0.50`, `/GND` |
| `32e0895c-bc20-429f-9684-018e7fcc24bb` | `(89.950,52.700) -> (94.000,51.500)` | `0.25`, `/WS2812_DATA_5V` |
| `da2890d9-c14e-428c-9a65-9024952b7af6` | `(88.050,52.700) -> (88.525,51.900)` | `0.50`, `/5V_SYS` |

## Transaction and machine results

- Named checkpoint:
  `10-u3-implementation-backup.kicad_pcb`, SHA-256
  `61549b45d4fe336986e76bcc78c5ca5532e67df604d155b140b1fd8a9d1bb109`.
- Pre-mutation fast contract: `PASS` against the approved Q1 checkpoint.
- Post-mutation fast contract: `PASS` against the named U3 checkpoint.
- Counts retained: 40 footprints, 202 tracks, 58 vias, four zones, seven
  rule areas, two copper layers, `145 x 90 mm` outline.
- Zones were explicitly refilled and the active board saved by native KiCad.
- Native DRC: zero geometric/clearance/zone findings and zero unconnected
  items. The only two reports are the unchanged inherited
  `lib_footprint_mismatch` warnings for JP1 and U4; U3 has no library
  mismatch. Baseline and post categories/counts are identical. Evidence:
  `active-baseline-native-drc.json`, `21-post-u3-native-drc.json`.
- Schematic/PCB parity: `PASS`; no missing footprints, pad/net mismatches,
  production-property mismatches, or unexpected board-only references.
  Evidence: `23-post-u3-parity.json`.
- Native ERC: zero violations. Evidence: `24-post-u3-native-erc.json`.
- Full contract structural checks and parity pass; its aggregate status is
  `FAIL` only because it deliberately counts the same two inherited JP1/U4
  library warnings. They were neither suppressed nor changed.
- U3 invariant and normalized semantic delta: `PASS`; only embedded U3
  approved geometry and the five endpoint coordinates differ from the named
  checkpoint. Generator output is byte-identical to the local library file.
  Evidence: `26-final-u3-dbv-invariant.json`.
- Negative regression: the same invariant rejects the prior active geometry
  for all five incorrect centres, all five R0.10 corners, old Fab/courtyard,
  old marker, and all five old endpoints. Evidence:
  `25-regression-old-u3-must-fail.json`.
- Regeneration is idempotent. Before and after rerunning
  `generate_stage7_footprints.py`, SHA-256 values were unchanged:
  generator `3b3ba925cd7556431e1be7194d7fa99cc01bb7132144a1efc42d8470a07fd395`,
  U3 library footprint
  `2f63828381821ca805033f3636ae06bafa95a82920a5340e76069a7b5233bad3`,
  active PCB `ef7cc377eb670115295f39cbd963e8910f2f4047cf5d740728abd09e1e4f25ea`.
  A full generated-library comparison found only the intended U3 footprint
  difference from the pre-transaction library snapshot.
- `git diff --check`: `PASS`.

## Changed paths

- `hardware/generate_stage7_footprints.py`
- `hardware/esp32-e220.pretty/TI_SN74AHCT1G125DBVR_SOT23-5.kicad_mod`
- `hardware/esp32-e220.kicad_pcb`
- `hardware/check_u3_dbv_footprint.py`
- evidence artifacts in this scope directory

Retained subsection: corrected U3 footprint and five local endpoint moves.
Deferred: global per-MPN audit/release packaging owned by the parent scope.
Failed subsection: none. No production ZIP was created or overwritten.

Next gate: independent `pcb_reviewer` implementation review. This handoff is
not production approval and does not claim the board is safe for production.
