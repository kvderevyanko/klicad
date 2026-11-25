# F1 final diagnostic Gerber / IPC-D-356 audit

Read-only audit, 2026-09-16, against the current controlled board after the
F1, JP1, and U4 transactions. The generated files under
`diagnostic-fabrication/` are retained evidence only; they are not a release
or manufacturing package. The active PCB SHA-256 was unchanged by export:
`27f5465e098d380c8a1bf440a8bb1b31f801d256076176c99eb956985394ee30`.

The physical requirement remains the primary Littelfuse 1812L Series Rev. GD
recommended pad layout already reviewed in
`../passive-power-primary-audit.md`: two 1.78 x 3.15-mm lands, 3.45-mm
inner-edge gap, hence 5.23-mm centre pitch. `1812L200/16` is non-polarized;
pad numbering is retained to control the series-net mapping.

## Numeric comparison

| Item | Manufacturer requirement | Active PCB | Diagnostic Gerber | IPC-D-356 converted to mm | Result |
|---|---:|---:|---:|---:|---|
| pad 1 centre | layout datum | (41.635, 76.000) | (41.635, 76.000) | (41.63568, 75.99934) | PASS |
| pad 2 centre | layout datum | (46.865, 76.000) | (46.865, 76.000) | (46.86554, 75.99934) | PASS |
| pad width x height | 1.780 x 3.150 | 1.780 x 3.150 | 1.780 x 3.150 | 1.78054 x 3.14960 | PASS |
| centre pitch | 5.230 | 5.230 | 5.230 | 5.22986 | PASS |
| inner copper gap | 3.450 | 3.450 | 3.450 | 3.44932 from rounded fields | PASS |

Gerber file coordinates invert board Y, so the literal flashes are
`(41.635,-76.000)` and `(46.865,-76.000)`; the table reports their board
coordinates. F.Cu uses aperture D14, while F.Paste uses D12 and F.Mask uses
D14. All three carry the identical RoundRect macro parameters. The macro
extents are `2*(0.534+0.356)=1.780 mm` in X and
`2*(1.219+0.356)=3.150 mm` in Y.

IPC-D-356 stores inch fields at 0.0001-inch resolution. Its exact F1 records
are:

- pad 1: `/BAT_PLUS`, `X+016392Y-029921X0701Y1240`;
- pad 2: `/BAT_FUSED`, `X+018451Y-029921X0701Y1240`.

The maximum observed conversion difference from the exact Gerber/board data
is 0.00068 mm, below the 0.00127-mm half-step quantization bound.

## Pin, pad, and net mapping

| Physical terminal | PCB pad | F.Cu X2 attribute | IPC-D-356 net | Function |
|---|---|---|---|---|
| terminal 1 (non-polarized) | F1.1 | `/BAT_PLUS` | `/BAT_PLUS` | fuse input from battery connector |
| terminal 2 (non-polarized) | F1.2 | `/BAT_FUSED` | `/BAT_FUSED` | protected output to switch connector and D3 branch |

F.Cu explicitly carries `%TO.P,F1,1*%` / `%TO.N,/BAT_PLUS*%` and
`%TO.P,F1,2*%` / `%TO.N,/BAT_FUSED*%` at the expected flashes. F.Paste and
F.Mask reproduce both land centres and the exact pad aperture.

## Evidence and disposition

- `20-f1-final-export-audit.json`: reproducible board/Gerber/IPC numeric
  checker, status PASS with no failures.
- `21-diagnostic-output-sha256.txt`: hashes of all diagnostic outputs.
- `00-source-board-sha256.txt` and `12-post-export-board-sha256.txt`:
  identical active-board hashes proving read-only export.

F1 FINAL DIAGNOSTIC GERBER / IPC-D-356 AUDIT: PASS

This result closes only the F1 fabrication-output consistency check. It is
not a global production disposition and does not create or approve a release.
