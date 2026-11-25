# Independent review — U4 TI DCY physical correction plan

Date: 2026-09-16
Review scope: read-only review of `u4-ti-dcy-physical-correction-plan.md`
against TI drawing `4210278/C` and the active controlled board.  The reviewer
did not modify board, schematic, footprints, routing, zones, metadata, or
release files.

## Verdict

`SCOPE VERDICT: U4 PHYSICAL PLAN PASS`

`REVIEW PASS`

## Independent findings

1. TI `4210278/C` matches the plan's copper exactly: lead lands
   `2.15 x 0.95 mm`, tab `2.15 x 3.25 mm`, 2.30-mm lead pitch, 5.80-mm
   lead-row/tab-row separation, and project-local row centres `-2.90/+2.90`.
2. TI `SBVS160C` and active board nets agree: pin 1=`/GND`; pin-2 lead and
   tab=`/AUX_3V3`; pin 3=`/5V_SYS`.
3. Every existing U4-connected track endpoint remains inside its proposed
   copper envelope.  The empty routing delta allowlist is correct; moving a
   track endpoint is neither required nor permitted by this plan.
4. The active global board mask margin is zero.  That does not produce the
   preferred positive NSMD opening in TI's detail.  The planned local
   `solder_mask_margin 0.05 mm` is positive, is within TI's `0.07 mm MAX`,
   and requires no global fabrication-rule mutation.
5. TI's 0.125-mm stencil example is one-to-one with the proposed lands.
   Normal KiCad paste openings are valid for the candidate; final stencil
   remains subject to assembly-site acceptance under TI Note D.
6. TI's land drawing specifies neither Fab nor courtyard.  Retaining the
   existing F.Fab and F.CrtYd is correct because both enclose the candidate.
7. Candidate minimum different-net copper clearance is 1.425 mm and nearest
   different-net via copper gap is 1.871 mm.  No zone, placement, courtyard,
   or mask feasibility conflict was found.  The earlier `no via within 5 mm`
   observation is only origin-centred and is not used as the clearance claim.
8. `00-current-u4-invariant.json` remains an explicit baseline **FAIL** from
   the old identity-only checker.  It is not suppressed: the checker must be
   updated within the future bounded implementation transaction.

## Boundary

This is a plan gate only.  It grants no footprint/PCB/schematic edit and no
release authorization.  External confirmation is required before starting the
approved transaction scope in the plan.
