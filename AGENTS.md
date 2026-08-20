# Agent operating rules

This is a real manufacturable ESP32 + E220 carrier. Treat actual KiCad data and primary manufacturer documentation as authoritative; never invent electrical, mechanical, package, pinout, thermal, RF, or manufacturing facts.

## Sources and context

Source order: actual KiCad design data; primary manufacturer documentation; reproducible project scripts/checkers; current-state snapshot; historical evidence. Report unresolved contradictions as `CONTEXT PROVENANCE CONFLICT` with both paths.

Default startup is exactly: `AGENTS.md`, `docs/agent-context.md`, scope-specific files, then primary evidence only when the decision needs it. Use `rg` and targeted reads. Do not recursively read documentation, old candidate reports, rejected-placement histories, unrelated evidence, or human-facing Russian documents unless resolving a concrete provenance conflict.

Agent-facing files, reports, handoffs, and comments are English. Human-facing documentation is Russian. Preserve technical identifiers verbatim. Keep outputs compact: exact facts/deltas, decisive evidence, blockers, changed/read paths; no raw logs or repeated history unless diagnosing a failure.

Keep every project command output, temporary board copy, DRC/ERC/parity report, screenshot, and retained test fixture inside this repository. Use a scope-specific `hardware/evidence/<scope>/` directory for transient-but-retained artifacts; do not use `/tmp` for project work or evidence.

## Active-design safety

`hardware/esp32-e220.kicad_pcb` and `hardware/esp32-e220.kicad_sch` are controlled records, never scratchpads. Do not invent topology changes to solve physical conflicts. A board/schematic edit is a bounded transaction: deterministic contract PASS, named backup, exact scope and expected DRC delta, one functional subsection, contract/DRC/parity recheck. An unexpected violation requires rollback, restored-state proof, and STOP. Never accumulate temporary violations or promise later cleanup.

Use machine checks before qualitative analysis. Never suppress a real ERC/DRC/parity/contract finding. Production Gerbers, drills, BOM, and placement outputs require explicit user authorization after reviewer approval. Preserve unrelated dirty-worktree changes.

## Ownership and gates

Only these roles exist: `pcb_engineer` (electrical/schematic/ERC), `pcb_evidence_auditor` (bounded read-only facts), `pcb_routing_planner` (read-only constrained physical plan), `pcb_layout_dfm` (approved physical implementation/DRC), and `pcb_reviewer` (independent gate). A writable owner never reviews its own work.

Electrical change: `pcb_engineer -> pcb_reviewer`; invoke the auditor only for a concrete evidence uncertainty.

Constrained physical change (new/moved footprint or zone, mounting/mechanical hole, coupled corridor, critical power loop, antenna/RF boundary, or placement affecting more than one route): `pcb_routing_planner -> pcb_reviewer PLAN GATE -> pcb_layout_dfm -> pcb_reviewer IMPLEMENTATION GATE`. The plan gate requires `SCOPE VERDICT: <scope> PHYSICAL PLAN PASS` and `REVIEW PASS`.

Simple local physical change with proven geometry: `pcb_layout_dfm -> pcb_reviewer`. Every active-board mutation follows `machine contract PASS -> transaction -> machine contract PASS -> DRC/parity -> rollback on unexpected FAIL`.
