# Rev.1 pre-production title/Dwgs.User/silkscreen transaction handoff

## SCOPE STATUS

`TITLE / DWGS.USER CLEANUP RETAINED; FUNCTIONAL SILKSCREEN TRANSACTION ROLLED BACK AND STOPPED`

The active starting PCB SHA-256 was
`161b4217c57829c8584ca8da0b984b63fcf0a6617011a35a424bbd57b308e804`,
byte-identical to the independently reviewed U3 candidate
`hardware/evidence/rev1-u3-dbv-release-2026-08-21/10-u3-dbv-candidate.kicad_pcb`.
The pre-transaction protected-reference fast contract passed. Named rollback
board: `40-active-pre-silkscreen-backup.kicad_pcb`.

## Retained transaction

The PCB title block now states:

- `ESP32 + E220 Carrier — Rev.1`
- `CONNECTIVITY COMPLETE / PRE-PRODUCTION CANDIDATE`
- `2-LAYER / 145 x 90 mm`
- `ESP32 / E220 / OLED USER-INSTALLED`
- `PRODUCTION RELEASE REQUIRES FINAL FAB PACKAGE GATE`

The obsolete `D2 LAND PATTERN = PCB RELEASE BLOCKER` Dwgs.User note was
removed. The stale routing, board-outline, antenna-placeholder, OLED-fit, and
test-point-bank notes were updated to the present pre-production state while
retaining the useful engineering drawings and notes. This logical transaction
passed protected fast contract and native DRC with zero violations and zero
unconnected items (`41-title-dwgs-native-drc.json`).

## Rolled-back functional silkscreen transaction

The attempted functional-label group produced three new native
`silk_overlap` warnings:

- J5 `SCL` text at `(60.500, 25.080)` overlapped the J5 F.Silk outline segment
  near `(61.650, 29.020)`.
- J5 `SDA` text at `(60.500, 27.620)` overlapped the same J5 F.Silk outline.
- J9 `5V` text at `(102.000, 54.000)` overlapped the J9 F.Silk outline segment
  near `(101.500, 52.500)`.

Per the active-board fail-fast rule, the entire functional-label logical group
was rolled back. No alternate coordinates were searched on the active board.
The failed diagnostic is `42-functional-silkscreen-native-drc.json`; restored
proof is `43-restored-after-silk-rollback-native-drc.json`.

## Restored deterministic state

- Restored active PCB SHA-256:
  `fa4bfbc0db8a9b99583374f5a4f6836f2e5478efc125d0bf91d148ff16ddc1be`.
- Full board contract: `PASS`; 37 footprints, 200 tracks, 58 vias, 4 zones,
  2 copper layers, 145 x 90 mm.
- Native DRC: 0 violations, 0 unconnected items.
- Schematic-PCB parity: `PASS` (`44-restored-parity.json`).
- Normalized comparison against `40-active-pre-silkscreen-backup.kicad_pcb`:
  every footprint, segment, via, zone/rule boundary/net, and Edge.Cuts item is
  identical. `COPPER / PLACEMENT DELTA = NONE`.

## Next gate

`SILKSCREEN PLACEMENT REVISION REQUIRED`

The active board remains electrically clean. The remaining functional/service
and ESP32/E220 orientation silkscreen labels need a reviewed collision-free
coordinate plan before another bounded active-board transaction.
