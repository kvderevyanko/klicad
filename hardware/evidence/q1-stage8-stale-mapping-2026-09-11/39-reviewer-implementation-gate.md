# Q1 Stage-8 stale-mapping implementation gate

- Scope: `generate_stage8_placement.py` must not regenerate Q1.3 on `BAT_FUSED`.
- Source finding: the Stage-8 generator predated the J8/`BAT_SW` architecture update; it retained Q1.3=`BAT_FUSED` and omitted `/BAT_SW` from its net registry.
- Regeneration: `12-...` and `17-...` are non-active candidates generated before and after Stage 7. Both record Q1.1=`Q1_GATE`, Q1.2=`BUCK_IN`, Q1.3=`BAT_SW` and identical Q1 pad geometry.
- Footprint persistence: `14-...` and `16-...` have identical SHA-256 for `Diodes_DMP3130LQ-7_SOT23.kicad_mod` across Stage-7 regeneration.
- Active-board checks: parity, ERC, production metadata, and Q1 production-archive integrity PASS. Native DRC has the same two pre-existing warning-severity `lib_footprint_mismatch` entries for JP1 and U4 before and after this source-only change; it has zero geometric, zone, and unconnected findings.

SCOPE VERDICT: q1-stage8-stale-mapping PASS

REVIEW PASS
