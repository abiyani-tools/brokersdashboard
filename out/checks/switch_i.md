# Switch (i) independent check: monthly inputs extended to September 2026

Script: `out/checks/switch_i_check.py` (stdlib only, snapshot JSON only, run with `python3 -I`). Result: **69 checked, 69 agree, 0 disagree**.
Nothing under `src/engine/` or `src/live/` was read.

## Method (units in brackets)
Before state (a-h) is rebuilt from raw `market_daily` rows (raw counts / 1e6 = Mn) and workbook seeds, with switch h's take rates and E values.

**F&O**, for month m in Jun..Sep 2026:
- G = share_m x market contracts_m (NSE + BSE F&O / 1e6, lake BSE on the 15 imputed days) [Mn contracts].
- F = E_q x C_m [Mn orders]. E = 300/407 for June, 256/367 for Jul-Sep.
- H = G / F.
- Worked example, June: G = 0.221 x 6838.9138 = 1511.4000; F = 0.737101 x 140.04 = 103.2236; H = 14.64200.
- Oct share = mean(0.222, 0.217, 0.225) = 0.221333. Oct H = Sep H.
- Daily Rs Cr = contracts / 1e6 / H x share x take rate / 10. Take rates are unchanged by (i).

**Commodity**:
- Y = total_orders x comm% [Mn]. Comm% is 40/406.14 for Q1 and 45/366.46 for Q2.
- X = Y / share. Z = MCX contracts_m / 1e6 / X.
- Before: Jul = mean(Apr, May, Jun Z) = 12.702228. Aug = mean(May, Jun, Jul) = 13.024399. Sep and Oct carry Aug.
- After: Jul, Aug, Sep are actual. Oct = mean(Jul, Aug, Sep) = 13.395211.
- Daily Rs Cr = MCX / 1e6 / Z x share x take rate / 10. Take rate: Q1 own rate, then Q2 own rate for Q2 and Q3 (switch h).

## Results (all AGREE)
- F&O H after: Jun 14.642002, Jul 15.806319, Aug 13.386539, Sep and Oct 14.469727. H before: 14.199750 for every month.
- F&O Oct share: 0.221 before, 0.221333 after.
- Commodity Z before: Jul 12.702228, Aug, Sep and Oct 13.024399. These equal the workbook's Z41:Z44 from `parity_expected`.
- Commodity Z after: Jul 11.913924, Aug 13.651016, Sep 14.620692, Oct 13.395211.
- Commodity share: Sep and Oct 0.437 before, 0.417 after.
- Changed days: F&O 99 (2026-06-01..2026-10-21), ratios 0.902424063 to 1.041549403. Commodity 80 (2026-07-01..2026-10-21), ratios 0.850049788 to 1.066166553.
- Sanity (switch h state): the F&O FY27 ADR before is 9.965732, and Q2 and Oct match too. The commodity FY27 ADR before is 1.567012.
- Sanity: Z for Apr, May and Jun rebuilt from raw equals the Excel Z38:Z40 to 1e-15.

| Rs Cr/day | before (mine) | after (mine) | after (claim) |
|---|---|---|---|
| F&O FY27 | 9.965732 | 9.783595 | 9.783595 |
| F&O Q2 | 8.749915 | 8.510622 | 8.510622 |
| F&O Oct | 11.874226 | 11.670252 | 11.670252 |
| Comm FY27 | 1.567012 | 1.517817 | 1.517817 |
| Comm Q2 | 1.617655 | 1.539989 | 1.539989 |
| Comm Oct | 1.937690 | 1.797823 | 1.797823 |
| Consol FY27 | 17.741633 | 17.510302 | 17.510302 |
| Consol Q2 | 16.812941 | 16.495983 | 16.495983 |
| Consol Oct | 20.559858 | 20.216017 | 20.216017 |

## Caveats
- Consolidated before is the a-h figure from the switch h check. Cash and MTF are not rebuilt here. After = before + dF&O + dComm, which is valid because cash and MTF are unchanged by (i).
- F&O Oct share 0.221333 differs from the unrounded mean by 1.5e-6 relative. That is within half a unit of the 6th printed decimal, so I counted it as agreeing.
- Comm Apr and May shares (0.567, 0.486) come from `parity_expected` `comm_share_m`. The `Commodities!AA38:AA39` seeds are not in the snapshot `facts`.
