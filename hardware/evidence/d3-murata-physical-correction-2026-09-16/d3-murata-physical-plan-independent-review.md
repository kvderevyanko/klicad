# D3 + Murata physical plan — independent review

Role: `pcb_reviewer` (read-only), 2026-09-16. Reviewed the active board,
the read-only candidate, the routing plan, and the retained Littelfuse/Murata
primary evidence. No controlled design source was changed.

## Baseline gate

`hardware/check_board_contract.py --board hardware/esp32-e220.kicad_pcb
--reference hardware/esp32-e220.kicad_pcb` is PASS. Independent native DRC
in `independent-plan-review-active-drc.json` reports zero violations and zero
unconnected items.

The candidate's own native run has zero geometric violations and zero
unconnected items after refill. Its twelve `lib_footprint_issues` warnings
are from opening an evidence copy without the project `Carrier` library path;
they are not active-board exclusions or waivers. Final implementation must
rerun the normal active-project DRC and may not inherit those warnings.

## Evidence and geometry verdict

Murata's retained exact-MPN Table 2 page defines `a` as the inner land gap,
`b` as individual land length along the terminal axis, and `c` as transverse
land width. The candidate applies the authorized in-range values exactly:

| Scope | a / b / c (mm) | Candidate local pad size and centres |
|---|---:|---|
| C2/C4/C6/C7/C8 GRM18 +/-0.10 | .75 / .70 / .70 | `.70 x .70`, `+/- .725` |
| C5 GRM18 +/-0.15 | .70 / .75 / .90 | `.75 x .90`, `+/- .725` |
| C1/C9/C10 GRM21 +/-0.15 | .80 / 1.20 / 1.30 | `1.20 x 1.30`, `+/- 1.000` |
| C3 GRM21 +/-0.20 | 1.30 / .70 / 1.30 | `.70 x 1.30`, `+/- 1.000` |

The retained Littelfuse SMBJ drawing evidence defines I as transverse land
width, J/L as individual land length, and K as the inner edge gap. The
candidate D3 is exactly `2.160 x 2.260 mm`, local centres `-2.450/+2.450 mm`,
and therefore pitch `4.900 mm` / gap `2.740 mm`. At the frozen `180 deg`
placement, pad 1 is `(44.350,70.500)` on `BAT_FUSED` and pad 2 is
`(39.450,70.500)` on `GND`; this preserves the approved pin/net chain.
`SMBJ10CA` is bidirectional, so no polarity constraint is introduced.

Candidate Gerber evidence checks all 22 target F.Cu flashes: centre,
aperture, rotation and net. `06-candidate-board-delta.json` proves all
footprint placements, 202 tracks, 58 vias, 11 zone outlines and all
non-target pads are unchanged. D3's retained route endpoints remain within
the new pads; Murata route-to-pad connections remain present. Thus no route
endpoint edit is required or authorized.

## Physical feasibility and source controls

The D3 Fab nominal (`4.405 x 3.620 mm`) is derived from the documented body
limits. Its `+/-3.800 x +/-2.500 mm` courtyard encloses the outward lands.
The GRM18 and C3 courtyards still enclose their reduced copper. C1/C9/C10
must use the planned expanded local X half-width `1.650 mm`, which encloses
the 1.20-mm long lands. The closest C1/C3 courtyard outlines are tight, but
the refilled candidate has no courtyard violation and the copper-to-copper
gap remains positive; placement, body clearance and critical buck topology
are unchanged.

The candidate deliberately exercises only embedded physical geometry. It
does not substitute for the required source split: implementation must create
MPN-specific C3/C5 local footprints and update their generator, schematic,
and Stage-8 identifiers, while retaining all values, pins, nets, UUIDs,
placements and non-target geometry. The required invariant must assert this
split and the unchanged-track contract.

## Findings

NOTE — The candidate-library DRC warnings are an evidence-copy library-path
artifact. They must not be copied to the active board or treated as accepted
production warnings.

NOTE — U4, Yageo and generic-resistor footprints are explicitly outside this
transaction.

SCOPE VERDICT: D3 + MURATA PHYSICAL PLAN PASS

REVIEW PASS
