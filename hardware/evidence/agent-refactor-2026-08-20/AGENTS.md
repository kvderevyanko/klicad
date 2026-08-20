# Agent operating rules

This repository contains a real, manufacturable ESP32 + E220 carrier PCB. Electrical and physical claims must be traceable to actual KiCad data and primary manufacturer evidence.

## Language policy

Classify every prose-bearing project file before creating or editing it:

* `AGENT_FACING`: instructions, agent profiles, machine-checkable reports, active context, source-code comments, handoffs, and evidence that an agent is expected to read. Write these files in English only.
* `HUMAN_FACING`: the root `readme.md`, project history, explanatory requirements, architecture narratives, decision journals, and other documentation not required as agent input. Write these files in Russian, using Russian wording wherever practical.

Current explicit classification:

* `AGENT_FACING`: `AGENTS.md`, `.codex/**`, `docs/agent-context.md`, source code and code comments, machine/checker reports, `hardware/esp32-e220-power-routing-report.md`, and `hardware/esp32-e220.pretty/README.md`.
* `HUMAN_FACING`: `readme.md`, `docs/project-history.md`, and the explanatory `docs/*.md` files other than `docs/agent-context.md`.

Apply this policy to every future file. If a file serves both audiences, keep the operational agent facts in an English agent-facing file and link to them from the Russian human-facing narrative; do not create a mixed-language document.

Keep exact technical identifiers unchanged in both classes: reference designators, MPNs, net names, pin names, filenames, commands, code, KiCad tokens, fixed status strings, standards, units, and quoted manufacturer terminology.

Do not make agents read a Russian human-facing file as routine context. If facts from such a file become operationally necessary, extract the current verified facts into `docs/agent-context.md` in English and cite the primary source or actual KiCad evidence. Do not duplicate full histories.

When replying to the user, use the user's language. Agent-to-agent evidence and persistent agent-facing artifacts remain English.

## Context policy

Read this file and `docs/agent-context.md` first. Then use `rg` to load only scope-relevant agent-facing files and actual KiCad artifacts. Do not load the entire documentation history by default.

For independent work, send a minimal task packet: objective, exact scope, paths, constraints, required evidence, stop conditions, and output schema. Avoid full conversation forks when the task is self-contained. Do not run duplicate audits. Parallelize only independent read-only evidence work; PCB/schematic writers and reviewer gates run sequentially.

Keep all project commands, temporary boards, checker outputs, screenshots, and
machine reports inside this repository. Do not use `/tmp` for project work or
evidence. Store transient-but-retained evidence under `hardware/evidence/` in
an English, scope-specific subdirectory; use paths in that directory for
native ERC/DRC, parity, routing-proof, and review artifacts. Return only
verdict, decisive evidence, blockers, and changed/read paths to the parent.

## Role ownership

* `pcb_engineer`: electrical architecture, component verification, symbol/package pin mapping, schematic, ERC, and controlled schematic changes.
* `pcb_evidence_auditor`: read-only pin/package/pad/net, parity, variant, and generator-drift evidence.
* `pcb_routing_planner`: read-only constrained placement/routing feasibility before active-board edits.
* `pcb_layout_dfm`: physical footprint implementation, placement, routing, zones, PCB DRC, mechanics, DFA, and DFM.
* `pcb_reviewer`: independent read-only quality gate and the only role that issues `REVIEW PASS`, `REVIEW PASS WITH MINOR ISSUES`, or `REVIEW FAIL`.

Do not transfer placement/routing ownership to `pcb_engineer`. Do not let support agents issue design approval. Do not let a writable role review its own work.

## Stage and gate contract

Typical constrained PCB workflow:

`pcb_evidence_auditor (if facts are disputed) -> pcb_engineer (only for electrical uncertainty) -> pcb_reviewer electrical gate -> pcb_routing_planner -> pcb_layout_dfm -> pcb_reviewer physical gate`.

Every staged handoff separates process/scope status from reviewer gate status. A named scope PASS is not a global release. `REVIEW PASS WITH MINOR ISSUES` permits the next stage only with tracked minor findings.

Never silently expand scope, restore superseded architecture, change layer count, change electrical topology, suppress real ERC/DRC findings, or create production outputs without explicit authorization.

## File safety

Preserve unrelated user changes in the dirty worktree. Use `apply_patch` for text edits. Do not reset or regenerate the whole PCB when a bounded checkpoint can be retained. Production artifacts (Gerbers, drills, BOM, CPL/positions) require an explicit user request after reviewer approval.
