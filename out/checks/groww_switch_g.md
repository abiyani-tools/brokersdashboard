# Groww switch g-g: independent recompute

Script: `out/checks/groww_switch_g_check.py` (stdlib json/math/csv). Inputs: db snapshot, Groww fixtures/snapshot, reviewed facts, Angel calibration read from `parity_expected`. No engine code read.

**Result: 36/36 items agree** (36 to 1e-6 relative; 0 agree only to the bridge print precision).

| Item kind | Checked | Agree | Agree at 1e-6 |
|---|---:|---:|---:|
| ADR | 30 | 30 | 30 |
| daily | 4 | 4 | 4 |
| special | 2 | 2 | 2 |

## ADR, Rs crore per trading day (consolidated and panels)

| Period | Panel | My before | Bridge before | My after | Bridge after | Max rel diff | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| FY 2027 | Consolidated | 20.005274 | 20.005274 | 20.005274 | 20.005274 | 1.8e-08 | agree |
| FY 2027 | Broking | 17.728318 | 17.728318 | 17.728318 | 17.728318 | 2.4e-08 | agree |
| FY 2027 | MTF | 2.276956 | 2.276956 | 2.276956 | 2.276956 | 3.0e-08 | agree |
| FY 2027 | F&O | 12.187676 | 12.187676 | 12.187676 | 12.187676 | 1.7e-08 | agree |
| FY 2027 | Cash | 4.176738 | 4.176738 | 4.176738 | 4.176738 | 1.1e-07 | agree |
| FY 2027 | Commodities | 1.363903 | 1.363903 | 1.363903 | 1.363903 | 2.2e-07 | agree |
| Q2 FY 2027 | Consolidated | 18.582719 | 18.582719 | 18.582719 | 18.582719 | 7.4e-09 | agree |
| Q2 FY 2027 | Broking | 16.188957 | 16.188957 | 16.188957 | 16.188957 | 1.8e-08 | agree |
| Q2 FY 2027 | MTF | 2.393762 | 2.393762 | 2.393762 | 2.393762 | 6.4e-08 | agree |
| Q2 FY 2027 | F&O | 10.617876 | 10.617876 | 10.617876 | 10.617876 | 2.9e-08 | agree |
| Q2 FY 2027 | Cash | 4.123907 | 4.123907 | 4.123907 | 4.123907 | 1.9e-08 | agree |
| Q2 FY 2027 | Commodities | 1.447174 | 1.447174 | 1.447174 | 1.447174 | 4.2e-08 | agree |
| FY 2027 October | Consolidated | 23.298092 | 23.298092 | 23.298092 | 23.298092 | 1.1e-08 | agree |
| FY 2027 October | Broking | 20.783268 | 20.783268 | 20.783268 | 20.783268 | 8.7e-10 | agree |
| FY 2027 October | MTF | 2.514824 | 2.514824 | 2.514824 | 2.514824 | 9.0e-08 | agree |
| FY 2027 October | F&O | 14.458817 | 14.458817 | 14.458817 | 14.458817 | 5.4e-09 | agree |
| FY 2027 October | Cash | 4.538468 | 4.538468 | 4.538468 | 4.538468 | 8.1e-08 | agree |
| FY 2027 October | Commodities | 1.785983 | 1.785983 | 1.785983 | 1.785983 | 1.5e-07 | agree |
| FY 2026 | Consolidated | 16.016385 | 16.016385 | 16.075454 | 16.075454 | 2.7e-08 | agree |
| FY 2026 | Broking | 14.982565 | 14.982565 | 15.041634 | 15.041634 | 3.0e-08 | agree |
| FY 2026 | MTF | 1.033820 | 1.033820 | 1.033820 | 1.033820 | 1.6e-08 | agree |
| FY 2026 | F&O | 10.772896 | 10.772896 | 10.813984 | 10.813984 | 1.1e-08 | agree |
| FY 2026 | Cash | 3.325009 | 3.325009 | 3.330972 | 3.330972 | 1.4e-07 | agree |
| FY 2026 | Commodities | 0.884661 | 0.884661 | 0.896679 | 0.896679 | 3.6e-07 | agree |
| FY 2026 October | Consolidated | 16.547397 | 16.547397 | 17.199648 | 17.199648 | 2.2e-08 | agree |
| FY 2026 October | Broking | 15.434134 | 15.434134 | 16.086385 | 16.086385 | 1.7e-08 | agree |
| FY 2026 October | MTF | 1.113263 | 1.113263 | 1.113263 | 1.113263 | 3.9e-07 | agree |
| FY 2026 October | F&O | 11.350532 | 11.350532 | 11.855821 | 11.855821 | 5.0e-09 | agree |
| FY 2026 October | Cash | 3.402207 | 3.402207 | 3.519421 | 3.519421 | 1.4e-07 | agree |
| FY 2026 October | Commodities | 0.681395 | 0.681395 | 0.711143 | 0.711143 | 5.0e-07 | agree |

## Parameters that moved

| Segment | Quantity | Quarter | My before | Bridge before | My after | Bridge after | My d% | Bridge d% | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---|

## Inputs replaced (reviewed facts)

| Input | Period | My workbook | Bridge workbook | My live | Bridge live | Fact ids ok | Vintage ok | Verdict |
|---|---|---:|---:|---:|---:|---|---|---|

## Daily revenue rows that changed

| Segment | Days | Changed (mine / bridge) | First | Last | Ratio min (mine / bridge) | Ratio max (mine / bridge) | Verdict |
|---|---:|---|---|---|---|---|---|
| F&O | 573 | 0 / 0 |  |  |  /  |  /  | agree |
| Cash | 573 | 0 / 0 |  |  |  /  |  /  | agree |
| Commodities | 272 | 0 / 0 |  |  |  /  |  /  | agree |
| MTF | 507 | 0 / 0 |  |  |  /  |  /  | agree |

## Special sessions excluded from the F&O, cash and commodity averages

| Date | Session | Equity day | MCX day | F&O rev Rs Mn | Cash rev Rs Mn | Comm rev Rs Mn | MTF rev Rs Cr |
|---|---|---|---|---:|---:|---:|---:|
| 2023-11-12 | muhurat | True | False | None | None | None | None |
| 2024-01-20 | weekend | True | False | None | None | None | None |
| 2024-03-02 | dr_test | True | False | None | None | None | None |
| 2024-05-18 | dr_test | True | False | None | None | None | None |
| 2024-11-01 | muhurat | True | True | 0.0 | 0.0 | None | 0.3168581754265034 |
| 2025-02-01 | budget | True | True | 0.0 | 0.0 | None | 0.28400961198174535 |
| 2025-10-21 | muhurat | True | True | 12.447502009379038 | 10.579298060062126 | 0.5669072416644891 | 1.1187804039982059 |
| 2026-02-01 | budget | True | True | 102.34513918666737 | 41.311080773704205 | 1.9839084770556858 | 1.8235970631735934 |

## Notes

Information: under g-g the averages skip special days but the take rates were calibrated with them in the sums. 2026-02-01 (Budget Sunday) carries F&O revenue of 102.3 Rs Mn, i.e. 1.22% of Q4 FY26 F&O revenue; 2025-10-21 (Muhurat) 12.4 Rs Mn, 0.18% of Q3 FY26.
Only the averaging changes: the daily revenue rows are identical to g-f (0 changed rows in all four segments). F&O, cash and commodity averages skip the 8 special sessions (MTF keeps them); 'days before the segment went live' are not recomputed because only periods starting in FY25 touch them (FY 2026 and FY 2027 are unaffected).
Only the ADR consequences are recomputed. The spec's other g-g clauses ('labels from the calendar', 'comparisons follow the selected period', 'insufficient' flag for periods starting before go-live) are not visible in the bridge numbers and are not checked here (item: input taken as given).
Spec vs switch: the spec says 'the same live rules as Angel One' and points to switches d and h; the take-rate calibration sums still include special-session days (see information line), so the average over the non-special days of a calibrated quarter no longer ties exactly to reported revenue (about 1% for Q4 FY26 F&O).
