# F1 constrained physical plan

Read-only routing plan, 2026-09-16. The controlled PCB, schematic,
generator, and project-local footprint were not edited. The tested board is
the evidence-only candidate `esp32-e220-f1-proposed.kicad_pcb`.

## Authoritative geometry and current delta

The primary dimensional decision is already recorded in
`../passive-power-primary-audit.md`: Littelfuse `1812L200/16`, 1812L drawing,
lands 1.78 x 3.15 mm, 3.45-mm inner-edge gap, hence 5.23-mm centre pitch.
The part is non-polarized; pad numbers are nevertheless preserved for the
controlled net chain.

| Item | Controlled PCB | Required local geometry | Delta |
|---|---:|---:|---:|
| pad 1 centre | (-2.138, 0), absolute (42.862, 76.000) | (-2.615, 0) | local X -0.477 mm before placement change |
| pad 2 centre | (+2.138, 0), absolute (47.138, 76.000) | (+2.615, 0) | local X +0.477 mm before placement change |
| pad size, each | 1.125 x 3.400 | 1.780 x 3.150 | X +0.655; Y -0.250 mm |
| centre pitch | 4.276 serialized | 5.230 | +0.954 mm |
| inner copper gap | 3.151 | 3.450 | +0.299 mm |

The generator's nominal old pitch is 4.275 mm, but its three-decimal output
serializes centres as +/-2.138 and the embedded PCB therefore measures 4.276
mm. This 0.001-mm source/serialization discrepancy does not alter the
physical mismatch.

The tested F.Fab body is the midpoint of the official body limits:
4.55 x 3.24 mm. The initial evidence candidate used an F.CrtYd width of only
5.55 mm and did not contain the new copper, whose local X extent is
+/-3.505 mm. That candidate was rejected. The ready plan uses local
F.CrtYd X=+/-3.55 and Y=+/-2.12. The X boundary contains the copper with the
same approximately 0.05-mm containment margin as the old project footprint.

## Candidate selection

1. **Selected:** move only F1 from (45.000, 76.000) to
   **(44.250, 76.000), rotation 0 degrees, F.Cu**, use the official lands,
   and recenter the six directly attached 1.00-mm F.Cu segments. This centers
   the 7.10-mm-wide F1 courtyard in the fixed 7.60-mm corridor between J4 and
   J8, leaving 0.25 mm to each connector courtyard.
2. Rejected: keep F1 at X=45.000 with a valid copper-containing courtyard.
   Its right courtyard boundary is X=48.550 and overlaps J8's boundary at
   X=48.050 by 0.500 mm, producing a real `courtyards_overlap` error.
3. Rejected: move J8 right instead. That changes an external switch connector
   datum and the downstream `BAT_SW` corridor, expanding scope beyond the
   local fuse correction.

## Bounded placement and routing contract

Final F1 pads after the selected placement:

| Pad | Absolute centre | Size | Layers | Net |
|---|---:|---:|---|---|
| 1 | (41.635, 76.000) | 1.780 x 3.150 | F.Cu/F.Paste/F.Mask | `/BAT_PLUS` |
| 2 | (46.865, 76.000) | 1.780 x 3.150 | F.Cu/F.Paste/F.Mask | `/BAT_FUSED` |

The coupled scope is the DC input series corridor `/BAT_PLUS -> F1 ->
/BAT_FUSED`, including the D3 shunt branch on `/BAT_FUSED`. It is not a
differential pair. Preserve pad 1 -> `/BAT_PLUS`, pad 2 -> `/BAT_FUSED` and
all schematic connectivity.

Replace only these six F.Cu segment geometries; retain width 1.00 mm and all
unlisted endpoints:

| Net | Controlled segment | Required segment |
|---|---|---|
| `/BAT_PLUS` | (42.862,78.500) -> (48.000,87.000) | (41.635,78.500) -> (48.000,87.000) |
| `/BAT_PLUS` | (42.862,78.500) -> (42.862,76.000) | (41.635,78.500) -> (41.635,76.000) |
| `/BAT_PLUS` | (35.000,78.500) -> (42.862,78.500) | (35.000,78.500) -> (41.635,78.500) |
| `/BAT_FUSED` | (47.138,72.500) -> (44.050,72.500) | (46.865,72.500) -> (44.050,72.500) |
| `/BAT_FUSED` | (47.138,76.000) -> (51.000,76.000) | (46.865,76.000) -> (51.000,76.000) |
| `/BAT_FUSED` | (47.138,76.000) -> (47.138,72.500) | (46.865,76.000) -> (46.865,72.500) |

Preserve the 1.00-mm F.Cu segments J4.1 (35.000,76.000) ->
(35.000,78.500) and D3.1 (44.050,70.500) -> (44.050,72.500). Add no vias,
change no layers, and change no other copper. The complete tested nets remain:

- `/BAT_PLUS`: J4.1 -> F1.1 and TP1.1.
- `/BAT_FUSED`: F1.2 -> J8.1 and D3.1.

The B.Cu GND zone beneath/adjacent to the corridor, the GND via at
(42.200,70.500), all other zones, and every rule area/keepout remain
unchanged. There is no signal-return topology change. The battery return is
still the existing GND system; the candidate creates no plane split or void.

## Machine evidence and expected delta

The evidence candidate differs from the controlled board only in the F1
description/Fab/courtyard/pads, the F1 origin, and the six named segment
endpoint edits. Footprint/segment/via/zone counts remain 40/202/58/11.

- `candidate-drc.rpt`: 0 unconnected, no geometric/clearance/courtyard error.
- `candidate-refilled-drc.rpt`: same after zone refill in memory.
- Both retain exactly the two baseline `lib_footprint_mismatch` warnings for
  JP1 and U4; expected F1-scope DRC delta is zero.
- Candidate SHA-256:
  `3430e9a77797166cf4298c2d8b080766a62928f67be258cbda755dbd3824135a`.

The two JP1/U4 warnings are outside this routing plan and are not suppressed
or classified here.

## Implementation checkpoints and rollback

1. Obtain deterministic machine-contract PASS; make named backups of the
   controlled PCB, generator, and F1 local footprint, recording hashes.
2. Update only `fuse_1812()` in `generate_stage7_footprints.py` so regeneration
   emits the official pad geometry, midpoint Fab body, and copper-containing
   courtyard above; regenerate and prove the local footprint exact.
3. In one F1 transaction, update the embedded footprint, set origin/rotation
   exactly, preserve pad UUIDs/nets where supported, and replace only the six
   listed route endpoints.
4. Before refill, assert F1 pads/coordinates/sizes/nets, segment inventory,
   zero added vias, unchanged zones/rule areas, and unchanged non-F1
   footprints/copper.
5. Run machine contract, native DRC without refill, native DRC with refill,
   schematic/PCB parity, then the broader ERC/Gerber/IPC-D-356 gates required
   by the parent audit. Expected result is no new finding and 0 unconnected.
6. STOP and restore all three named backups if any unexpected contract,
   connectivity, clearance, courtyard, parity, zone, or inventory delta
   occurs. Re-run the machine contract and native DRC on the restored files
   to prove rollback before any further work.

Primary remaining implementation risks are generator drift, accidental
connector movement, loss of the D3 shunt branch, or editing copper outside the
six-segment allowlist. The exact assertions above bound each risk.

SCOPE VERDICT: F1 PHYSICAL PLAN PASS

ROUTING PLAN READY
