# Simplified Rev.1 5V_SYS power budget

Date: 2026-08-21

Status: `POWER BUDGET PASS` for the stated simultaneous design allocation.
This is not a substitute for prototype transient, inrush, cable, or thermal
validation.

## Allocation

| Consumer | Allocation | Basis |
| --- | ---: | --- |
| ESP32 DevKit VIN | 500.000 mA | Project design allocation; not a manufacturer maximum for the unidentified removable board. |
| E220-400T22D or E220-900T22D at 22 dBm | 110.000 mA | EBYTE published maximum instantaneous transmit current at its stated 5.0-V / 25°C condition; retained source identity is recorded in the earlier Rev.1 ledger. |
| U3 `SN74AHCT1G125DBVR` | 1.510 mA | Conservative static sum of TI maximum 10-uA `ICC` and 1.5-mA `Delta ICC` at the cited input condition; not a dynamic/output-load bound. Official TI `SCLS378P`: https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf |
| U4 plus OLED/J5 | 100.100 mA | 100.000-mA OLED project allocation plus the retained 0.100-mA U4 accounting convention. The TI 100-uA figure is a no-load quiescent-current maximum, not a loaded-ground-current guarantee. |
| J9 / functional `J_RGB`, maximum three WS2812B-V5 pixels | 109.800 mA | 3 x (36.000-mA RGB working-current basis + 0.600-mA quiescent current) from the official WorldSemi document. |
| **Subtotal** | **821.410 mA** | Simultaneous allocation. |
| **Engineering margin, 20%** | **164.282 mA** | `821.410 mA x 0.20`. |
| **Total 5V_SYS allocation** | **985.692 mA** | `821.410 + 164.282 mA`. |

`AUX_3V3` is OLED-only at 100.000 mA. J6 has no power pin. J7 and onboard D2
do not exist in the simplified electrical source. The external RGB population
limit is three pixels total, not three chains or an open-ended connector
allowance.

## Derived steady-state checks

The retained 85% conversion-efficiency assumption gives:

| Quantity | Result |
| --- | ---: |
| `5V_SYS` output power | 4.928460 W |
| Estimated battery input power | 5.798188 W |
| Battery current at 6.0 V | 0.966365 A |
| Battery current at 7.4 V | 0.783539 A |
| Battery current at 8.4 V | 0.690261 A |

| Component/path | Check at the stated allocation |
| --- | --- |
| U1 TPS62133 3.0-A continuous rating | 32.8564% used; 2.014308-A headroom. |
| L1 `XFL4020-222MEB` | DC-only `I^2R` estimate 0.022832 W at 23.50-mOhm maximum DCR; 2.114308-A arithmetic distance to 3.1-A `Isat`. Ripple/peak current remains unproven. |
| F1 `1812L200/16` | 0.323635-A headroom to the cited 1.29-A `Ihold` at 85°C. Startup and time-current behavior remain unproven. |
| Q1 `DMP3130LQ-7` | 1.633635-A arithmetic distance to the cited 2.6-A / 70°C / VGS=-4.5-V condition; actual copper temperature remains unproven. |
| J4/J8 JST XH | 2.033635-A arithmetic distance to the 3-A AWG22 XH rating. Harness contacts, wire, crimp, temperature, and strain relief require qualification. Official JST XH data: https://www.jst-mfg.com/product/pdf/eng/eXH.pdf |

## WS2812 interface evidence and limitation

WorldSemi WS2812B-V5 specifies VDD 3.7...5.3 V, `VIH` minimum 2.7 V at
VDD=5 V, 0.6-mA quiescent current, and a 12-mA working-current condition for
each of R/G/B. Its typical application circuit does not specify a DIN series
resistor or a resistor value. No series resistor is therefore authorized by
this evidence. External cable length, edge ringing, EMC, first-pixel local
power integrity, power-up behavior, and the actual three-pixel current require
prototype validation. Official WorldSemi document:
https://www.world-semi.co.kr/_files/ugd/89cd03_1023b0e9d135431aa1e6491bfc318112.pdf
