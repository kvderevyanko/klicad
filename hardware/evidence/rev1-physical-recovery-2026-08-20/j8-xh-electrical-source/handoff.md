# J8 XH electrical-source handoff

Date: 2026-08-20

## Disposition

`SCHEMATIC CHANGE REQUIRED` was satisfied as a bounded production-property
change. J8 topology and nets were not changed.

## Decisive evidence

- User-authorized selection: the compact JST XH 2-position family already used
  by J4, with project requirement J8 >= 2 A continuous.
- Existing project evidence in
  `hardware/evidence/rev1-expansion-2026-08-20/5v-sys-budget-ledger.md`
  records the official JST XH rating as 3 A AC/DC with AWG22 and cites the
  primary JST XH data sheet: `https://www.jst-mfg.com/product/pdf/eng/eXH.pdf`.
  This exceeds the 2-A project requirement. Mating contact, wire gauge,
  harness temperature, and strain relief remain assembly-qualification items.
- Project-local footprint
  `hardware/esp32-e220.pretty/JST_B2B-XH-A_1x02_P2.50mm_THT.kicad_mod`
  contains exactly physical pads 1 and 2 at 2.50-mm pitch.

## Exact electrical-source delta

- `hardware/generate_esp32_e220.py`:
  - J8 Value: `B2PS-VH(LF)(SN)` -> `B2B-XH-A`
  - J8 Footprint:
    `Connector_JST:JST_VH_B2PS-VH_1x02_P3.96mm_Horizontal` ->
    `JST_B2B-XH-A_1x02_P2.50mm_THT`
  - source annotation/data-sheet pointer: JST VH 3.96 mm/eVH -> JST XH
    2.50 mm/eXH
- Regenerated `hardware/esp32-e220.kicad_sch`. Its byte-level delta from the
  named backup is limited to J8 Value and Footprint properties.
- `hardware/esp32-e220.kicad_sym` and `hardware/sym-lib-table` regenerated
  byte-identically.
- `hardware/esp32-e220.kicad_pcb` was not edited.

## Approved J8 pad map and retained topology

| Symbol pin | Function/net | Footprint pad |
| --- | --- | --- |
| J8.1 | `BAT_FUSED` | 1 |
| J8.2 | `BAT_SW` | 2 |

Exported connectivity remains `F1.2 -> BAT_FUSED -> J8.1`, external mechanical
switch, `J8.2 -> BAT_SW -> Q1.3`. No electrical component, pin, wire, label,
or net was added, removed, or renamed.

## Validation

- Native KiCad 10.0.5 ERC before: 0 violations
  (`erc-before.json`).
- Native KiCad 10.0.5 ERC after: 0 violations
  (`erc-after.json`).
- Exported post-change netlist (`esp32-e220.after-j8-xh.net`) proves exact J8
  Value/Footprint and J8.1=`BAT_FUSED`, J8.2=`BAT_SW`.
- Generator rerun was byte-stable:
  - generator SHA-256:
    `8b246f3ee05df31d8e41e470045aafe6d0b87fa61660cc62ef6be60ddc189ee3`
  - schematic SHA-256:
    `1607defc14cd9bc711566d671d53e996c54363b1dbd22effa2f1a1a0fd18f490`
  - symbol library SHA-256:
    `55893d5ac1c810fc401e2fba930fd367e0642c4888b4d26215c7a48256663e8b`
- Named pre-change schematic backup:
  `esp32-e220.before-j8-xh.kicad_sch`, SHA-256
  `554b551f4132bc52f47f3acc4f71228f56661dce084eab12a316e4b949416f53`.
- Active PCB SHA-256 remained
  `bf502dfde6ebb1f05d5d8f95fa77dc6f3d484fd9ddcdb47d3511c4b82b5f5036`.

## Parity impact and risk

The authoritative read-only parity check against the known rejected active PCB
reports only its already-missing J6/J7 plus the expected stale J8 Value and
Footprint properties. It reports zero electrical pad/net mismatches. The
active PCB must not be synchronized from this change until the independent
electrical reviewer gate and the required physical plan gate pass.

`CONTEXT PROVENANCE CONFLICT`: current human-facing
`docs/requirements.md` and `docs/component-decisions.md` still describe J8 as
JST VH, while the user-authorized controlling electrical source now selects
JST XH. Those documents were outside this bounded source transaction and were
not edited.

## Next gate

Independent `pcb_reviewer` electrical review of the J8 production-property
change is required before the updated schematic may be used for active-board
recovery. No PCB implementation is authorized by this handoff.
