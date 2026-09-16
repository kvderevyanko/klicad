# U4 TLV1117LV33DCYR / TI DCY physical correction plan

Date: 2026-09-16
Scope: plan and independent review only.  This document authorizes no design
mutation, release, commit, or push.

## Preconditions observed

- `00-current-u4-invariant.json`: **FAIL**.  This is the obsolete U4
  identity-only invariant: it still asserts that TI publishes no land pattern
  and compares the controlled board/schematic against the pre-U4-metadata
  reference outside its former allowlist.  Its observed current pad/net facts
  remain usable as read-only input, but its overall status is not a baseline
  PASS and must not be suppressed.  Updating this checker to the approved TI
  geometry is a required part of the future bounded transaction.
- `01-current-native-drc.json`: 0 violations and 0 unconnected items.
- `04-current-full-contract.json`: PASS; `05-current-parity.json`: PASS.
- U4 origin/rotation is fixed at `(20.650, 27.000, 0 deg)`.
- TI `SBVS160C` / `MPDS094A` confirms pin 1=GND, pin 2 and tab=OUT,
  pin 3=IN.  The active board maps them to `/GND`, `/AUX_3V3`,
  `/AUX_3V3`, `/5V_SYS` respectively.

Primary layout source: TI `4210278/C`, `DCY (R-PDSO-G4) PLASTIC SMALL
OUTLINE`, example board layout and 0.125-mm stencil example.  This source,
not the previous KiCad pattern and not the contradictory Ultra Librarian
preview, controls the proposed copper/mask/paste geometry.

## OLD / MANUFACTURER / DELTA

All land values below use the active footprint axes, i.e. the TI drawing
rotated 90 degrees into the existing board orientation.

| Item | Current | TI 4210278/C | Delta / plan |
|---|---:|---:|---|
| Pins 1/2/3 `F.Cu` | 2.00 x 1.50 mm, `x=-3.15` | 2.15 x 0.95 mm, `x=-2.90` | Replace geometry; move local row +0.25 mm inward. |
| Tab pin 2 `F.Cu` | 2.00 x 3.80 mm, `x=+3.15` | 2.15 x 3.25 mm, `x=+2.90` | Replace geometry; move local tab -0.25 mm inward. |
| Lead pitch | 2.30 mm | 2.30 mm | Retain. |
| Lead-row to tab-row centre separation | 6.30 mm | 5.80 mm | Reduce by 0.50 mm through the two 0.25-mm moves. |
| `F.Paste` | implicit 1:1 with current pad | TI 0.125-mm example is 1:1: 0.95 x 2.15 mm leads and 3.25 x 2.15 mm tab in TI axes | Use ordinary pad paste on the new TI copper; no unreviewed reduction/windowing.  Assembly site still owns final stencil acceptance under TI Note D. |
| `F.Mask` | board `(pad_to_mask_clearance 0)`; no U4 override, so aperture is copper-sized | TI prefers NSMD and permits mask opening up to 0.07 mm all around | Add only a U4 per-pad `solder_mask_margin 0.05 mm`: NSMD, within TI maximum, and does not alter global rules. |
| `F.Fab` | mechanical body bbox 3.70 x 6.70 mm | Package drawing maximum body 3.70 x 6.70 mm; land drawing supplies no alternate Fab | Retain. |
| `F.CrtYd` | local `x=-4.40..+4.40`, `y=-3.60..+3.60` | TI land drawing supplies no courtyard | Retain; it encloses the proposed copper extents. |

The proposed explicit mask openings are 2.25 x 1.05 mm for each lead and
2.25 x 3.35 mm for the tab.  `0.05 mm` is deliberately not a new board-wide
fabrication rule: it is a local value already used by the released TI U3
footprint, is positive (therefore NSMD), and is no greater than TI's
`0.07 mm MAX` detail.  No retained PCBWAVE fabrication profile supplies a
different global mask compensation; the post-transaction Gerber must therefore
be inspected directly.

## Exact proposed footprint geometry

Keep U4's footprint identity, origin, rotation, reference, value, pad numbers,
and electrical mapping.  The source-of-truth local pads shall be:

| Physical terminal | Pad number | Local centre mm | `F.Cu` mm | `F.Mask` margin | `F.Paste` |
|---|---:|---:|---:|---:|---:|
| pin 1 GND | `1` | `(-2.90, -2.30)` | `2.15 x 0.95` | `+0.05 mm` | `2.15 x 0.95` |
| pin 2 OUT lead | `2` | `(-2.90, 0.00)` | `2.15 x 0.95` | `+0.05 mm` | `2.15 x 0.95` |
| pin 2 OUT tab | `2` | `(+2.90, 0.00)` | `2.15 x 3.25` | `+0.05 mm` | `2.15 x 3.25` |
| pin 3 IN | `3` | `(-2.90, +2.30)` | `2.15 x 0.95` | `+0.05 mm` | `2.15 x 0.95` |

## Route-impact and routing delta allowlist

`02-u4-candidate-endpoint-containment.json` independently evaluates all
same-net track ends inside their proposed copper lands.

| U4 terminal | Current absolute centre mm | Proposed absolute centre mm | Attached endpoints mm / width | In proposed copper? | Routing action |
|---|---:|---:|---|---|---|
| pin 1 GND | `(17.50, 24.70)` | `(17.75, 24.70)` | `(17.50,24.70)` / 0.50 | Yes | Preserve endpoint and track. |
| pin 2 lead AUX_3V3 | `(17.50, 27.00)` | `(17.75, 27.00)` | two ends `(17.50,27.00)` / 0.80 | Yes | Preserve both. |
| pin 2 tab AUX_3V3 | `(23.80, 27.00)` | `(23.55, 27.00)` | `(23.80,27.00)` / 0.80 | Yes | Preserve endpoint and track. |
| pin 3 5V_SYS | `(17.50, 29.30)` | `(17.75, 29.30)` | `(17.50,29.30)` / 0.80 | Yes | Preserve endpoint and track. |

**Routing delta allowlist: empty.**  There is no authority to move a track
endpoint for visual symmetry.  A candidate may change a route only if an
actual post-change DRC/connection failure proves it necessary; that is an
unexpected violation and requires rollback/stop under the controlled-board
transaction rule.

## Neighbour and implementation feasibility

- No via is within 5 mm of U4; the nearest different-net via has 1.871 mm
  copper gap to the candidate.  No candidate-intersecting via was found.
- The minimum different-net F.Cu copper clearance to the candidate is
  1.425 mm, above the 0.20-mm project clearance.
- The existing `/AUX_3V3` F.Cu zone is `x=22..30`, `y=22..32` mm and fully
  surrounds the proposed tab.  It remains same-net; zones are not to be edited.
- Nearby parts are C10 at `(14.40,27.00)` and C9 at `(17.50,33.00)`.
  C10 has 0.675-mm copper gap to the proposed lead geometry and 0.575 mm
  after the planned 0.05-mm mask opening; no mask bridge is indicated.
- Existing Fab/courtyard remain enclosing.  Candidate clearance, mask bridge,
  courtyard and paste result are still mandatory native-DRC/Gerber checks
  after implementation; the present result is plan feasibility, not an
  implementation claim.

## Bounded future transaction scope

Allowed only after this plan has `REVIEW PASS` and external approval:

1. `hardware/generate_stage7_footprints.py` U4 source-of-truth;
2. `hardware/esp32-e220.pretty/TI_TLV1117LV33DCYR_DCY_SOT223.kicad_mod`;
3. embedded U4 footprint in `hardware/esp32-e220.kicad_pcb`;
4. `hardware/check_u4_dcy_footprint.py` invariant.

The candidate must not alter schematic footprint identity, U4 origin/rotation,
pad/net mapping, tracks, vias, zones, placement, `F.Fab`, `F.CrtYd`, or any
other footprint.  Route edits are explicitly disallowed by the empty allowlist.

Required transaction gates: baseline full contract and named backup; one U4
functional subsection; post-change contract, invariant, native DRC,
schematic/PCB parity, direct Gerber `F.Cu/F.Mask/F.Paste` audit, and IPC-D-356
audit; rollback and STOP on any unexpected result.

## Scope verdict

`SCOPE VERDICT: U4 PHYSICAL PLAN PASS`

The plan is feasible without routing, zone, placement, Fab, or courtyard
change.  It remains pending independent reviewer `REVIEW PASS` and external
approval before any controlled-board transaction.
