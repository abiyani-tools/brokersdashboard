# Groww orders check: independent recompute

Script: `out/checks/groww_orders_check.py` (stdlib json/math/csv). Inputs: db snapshot, Groww fixtures/snapshot, reviewed facts, Angel calibration read from `parity_expected`. No engine code read.

**Result: 13/13 items agree** (5 to 1e-6 relative; 8 agree only to the bridge print precision).

| Item kind | Checked | Agree | Agree at 1e-6 |
|---|---:|---:|---:|
| orders | 8 | 8 | 0 |
| q2fy27 | 5 | 5 | 5 |

## Bridge table recomputed (tolerance: half of the last printed digit)

| Quarter | Disclosed (mine / bridge) | Parity F&O | cash | comm | total | gap % | Live F&O | cash | comm | total | gap % | New-basis total | gap % | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q3 FY 2025 | 454.2094 / 454.2 | — | — | — | — | — | — | — | — | — | — | — | — | agree |
| Q4 FY 2025 | 357.7146 / 357.7 | — | — | — | — | — | — | — | — | — | — | — | — | agree |
| Q1 FY 2026 | 378.5570 / 378.6 | — | — | — | — | — | 165.7 | 98.3 | 0.0 | 264.1 | -30.2 | 132.0 | -65.1 | agree |
| Q2 FY 2026 | 415.7070 / 415.7 | 206.1 | 100.7 | 0.0 | 306.8 | -26.2 | 206.1 | 100.7 | 0.0 | 306.8 | -26.2 | 153.4 | -63.1 | agree |
| Q3 FY 2026 | 474.1940 / 474.2 | 230.5 | 107.0 | 21.9 | 359.4 | -24.2 | 230.5 | 107.0 | 19.8 | 357.3 | -24.7 | 188.5 | -60.2 | agree |
| Q4 FY 2026 | 587.3902 / 587.4 | 306.1 | 122.3 | 26.5 | 455.0 | -22.5 | 306.1 | 122.3 | 33.8 | 462.2 | -21.3 | 248.0 | -57.8 | agree |
| Q1 FY 2027 | 560.1558 / 560.2 | 299.4 | 116.3 | 25.4 | 441.1 | -21.3 | 295.9 | 116.3 | 35.3 | 447.4 | -20.1 | 241.4 | -56.9 | agree |
| Q2 FY 2027 | 517.3050 / 517.3 | 259.7 | 132.2 | 34.9 | 426.8 | -17.5 | 258.9 | 134.8 | 44.4 | 438.1 | -15.3 | 241.2 | -53.4 | agree |

## Q2 FY27 sanity check

| Item | Value |
|---|---:|
| Disclosed total, Q2 FY27 (Mn orders) | 517.3050 |
| Sum of NSE+BSE F&O contracts (Mn, lake BSE) | 16886.64 |
| Sum of cash trades (Mn) | 2691.95 |
| Sum of MCX contracts (Mn) | 1357.04 |
| Model F&O orders (Mn) | 258.86 |
| Model cash orders (Mn) | 134.81 |
| Model commodity orders (Mn) | 44.41 |
| Model total (Mn) | 438.08 |
| Gap vs disclosed, legacy-basis shares | -15.3% |
| Gap excluding commodity (handbook defines Broking Orders as Stocks and Derivatives) | -23.9% |
| Gap with new-basis shares (F&O and cash halved) | -53.4% |

## Notes

Disclosed total confirmed against the handbook JSON and fact 10095; independently confirmed once by reading `2026_10_Q2_FY27_KPI_Handbook.xlsx`, Operational KPIs E10 = 51.7305 Cr, E36 = 65 days (done outside the script, which stays stdlib json/math/csv). The same handbook defines Broking Orders as orders in Stocks and Derivatives, with Equity and Commodity Derivatives listed as separate product lines, so whether commodity orders belong in the disclosed total is not settled by the glossary.
Orders implied by the model = daily market orders (contracts / Angel contracts-per-order, trades / Angel trades-per-order) x Groww ADTO share on the legacy (exchange x 1) basis. The shares are turnover shares applied to order counts (spec D6), so the persistent -15% to -30% gap is partly a unit mismatch, and halving the shares for the new basis widens it to -53% to -65%, i.e. the legacy basis is the closer one.
Special-session days and the Q3 FY25/Q4 FY25 zero-fill rows are included/excluded exactly as the bridge says (not live before Q1 FY26 under g-b).
