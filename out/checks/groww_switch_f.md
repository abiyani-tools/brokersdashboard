# Groww switch g-f: independent recompute

Script: `out/checks/groww_switch_f_check.py` (stdlib json/math/csv). Inputs: db snapshot, Groww fixtures/snapshot, reviewed facts, Angel calibration read from `parity_expected`. No engine code read.

**Result: 66/66 items agree** (49 to 1e-6 relative; 17 agree only to the bridge print precision).

| Item kind | Checked | Agree | Agree at 1e-6 |
|---|---:|---:|---:|
| ADR | 30 | 30 | 30 |
| param | 18 | 18 | 2 |
| input | 2 | 2 | 1 |
| daily | 4 | 4 | 4 |
| tie | 8 | 8 | 8 |
| days | 4 | 4 | 4 |

## ADR, Rs crore per trading day (consolidated and panels)

| Period | Panel | My before | Bridge before | My after | Bridge after | Max rel diff | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| FY 2027 | Consolidated | 19.985235 | 19.985235 | 20.005274 | 20.005274 | 1.8e-08 | agree |
| FY 2027 | Broking | 17.728318 | 17.728318 | 17.728318 | 17.728318 | 2.4e-08 | agree |
| FY 2027 | MTF | 2.256917 | 2.256917 | 2.276956 | 2.276956 | 6.6e-08 | agree |
| FY 2027 | F&O | 12.187676 | 12.187676 | 12.187676 | 12.187676 | 1.7e-08 | agree |
| FY 2027 | Cash | 4.176738 | 4.176738 | 4.176738 | 4.176738 | 1.1e-07 | agree |
| FY 2027 | Commodities | 1.363903 | 1.363903 | 1.363903 | 1.363903 | 2.2e-07 | agree |
| Q2 FY 2027 | Consolidated | 18.589965 | 18.589965 | 18.582719 | 18.582719 | 7.4e-09 | agree |
| Q2 FY 2027 | Broking | 16.188957 | 16.188957 | 16.188957 | 16.188957 | 1.8e-08 | agree |
| Q2 FY 2027 | MTF | 2.401008 | 2.401008 | 2.393762 | 2.393762 | 9.6e-08 | agree |
| Q2 FY 2027 | F&O | 10.617876 | 10.617876 | 10.617876 | 10.617876 | 2.9e-08 | agree |
| Q2 FY 2027 | Cash | 4.123907 | 4.123907 | 4.123907 | 4.123907 | 1.9e-08 | agree |
| Q2 FY 2027 | Commodities | 1.447174 | 1.447174 | 1.447174 | 1.447174 | 4.2e-08 | agree |
| FY 2027 October | Consolidated | 23.305704 | 23.305704 | 23.298092 | 23.298092 | 1.3e-08 | agree |
| FY 2027 October | Broking | 20.783268 | 20.783268 | 20.783268 | 20.783268 | 8.7e-10 | agree |
| FY 2027 October | MTF | 2.522436 | 2.522436 | 2.514824 | 2.514824 | 1.2e-07 | agree |
| FY 2027 October | F&O | 14.458817 | 14.458817 | 14.458817 | 14.458817 | 5.4e-09 | agree |
| FY 2027 October | Cash | 4.538468 | 4.538468 | 4.538468 | 4.538468 | 8.1e-08 | agree |
| FY 2027 October | Commodities | 1.785983 | 1.785983 | 1.785983 | 1.785983 | 1.5e-07 | agree |
| FY 2026 | Consolidated | 15.989974 | 15.989974 | 16.016385 | 16.016385 | 2.7e-08 | agree |
| FY 2026 | Broking | 14.982565 | 14.982565 | 14.982565 | 14.982565 | 3.0e-08 | agree |
| FY 2026 | MTF | 1.007408 | 1.007408 | 1.033820 | 1.033820 | 2.1e-07 | agree |
| FY 2026 | F&O | 10.772896 | 10.772896 | 10.772896 | 10.772896 | 1.0e-09 | agree |
| FY 2026 | Cash | 3.325009 | 3.325009 | 3.325009 | 3.325009 | 1.4e-07 | agree |
| FY 2026 | Commodities | 0.884661 | 0.884661 | 0.884661 | 0.884661 | 1.1e-07 | agree |
| FY 2026 October | Consolidated | 16.522023 | 16.522023 | 16.547397 | 16.547397 | 2.2e-08 | agree |
| FY 2026 October | Broking | 15.434134 | 15.434134 | 15.434134 | 15.434134 | 1.7e-08 | agree |
| FY 2026 October | MTF | 1.087888 | 1.087888 | 1.113263 | 1.113263 | 3.9e-07 | agree |
| FY 2026 October | F&O | 11.350532 | 11.350532 | 11.350532 | 11.350532 | 2.5e-09 | agree |
| FY 2026 October | Cash | 3.402207 | 3.402207 | 3.402207 | 3.402207 | 1.4e-07 | agree |
| FY 2026 October | Commodities | 0.681395 | 0.681395 | 0.681395 | 0.681395 | 2.5e-07 | agree |

## Parameters that moved

| Segment | Quantity | Quarter | My before | Bridge before | My after | Bridge after | My d% | Bridge d% | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| MTF | Groww average book Rs Cr | Q3 FY 2025 | 537.497 | 537.50 | 539.664 | 539.66 | 0.403226 | +0.403% | agree |
| MTF | Groww average book Rs Cr | Q4 FY 2025 | 454.62 | 454.62 | 456.454 | 456.45 | 0.403226 | +0.403% | agree |
| MTF | Groww average book Rs Cr | Q1 FY 2026 | 761.315 | 761.31 | 770.675 | 770.67 | 1.22951 | +1.230% | agree |
| MTF | Groww average book Rs Cr | Q2 FY 2026 | 1346.55 | 1,346.55 | 1299.21 | 1,299.21 | -3.51563 | -3.516% | agree |
| MTF | Groww average book Rs Cr | Q3 FY 2026 | 1889.5 | 1,889.50 | 1881.88 | 1,881.88 | -0.403226 | -0.403% | agree |
| MTF | Groww average book Rs Cr | Q4 FY 2026 | 2834.83 | 2,834.83 | 2917.52 | 2,917.52 | 2.91667 | +2.917% | agree |
| MTF | Groww average book Rs Cr | Q1 FY 2027 | 3314.88 | 3,314.88 | 3469.39 | 3,469.39 | 4.66102 | +4.661% | agree |
| MTF | Groww average book Rs Cr | Q2 FY 2027 | — | — | 3954.91 | 3,954.91 | — | blank | agree |
| MTF | revenue Rs Cr | Q2 FY 2027 | — | — | 155.595 | 155.59 | — | blank | agree |
| MTF | share of industry book | Q3 FY 2025 | 0.00606199 | 0.0061 | 0.00680093 | 0.0068 | 12.1897 | +12.190% | agree |
| MTF | share of industry book | Q4 FY 2025 | 0.00582847 | 0.0058 | 0.00604259 | 0.0060 | 3.67381 | +3.674% | agree |
| MTF | share of industry book | Q1 FY 2026 | 0.00971891 | 0.0097 | 0.0102915 | 0.0103 | 5.89199 | +5.892% | agree |
| MTF | share of industry book | Q2 FY 2026 | 0.013882 | 0.0139 | 0.0140521 | 0.0141 | 1.22566 | +1.226% | agree |
| MTF | share of industry book | Q3 FY 2026 | 0.0165262 | 0.0165 | 0.0169804 | 0.0170 | 2.74841 | +2.748% | agree |
| MTF | share of industry book | Q4 FY 2026 | 0.0247224 | 0.0247 | 0.0255544 | 0.0256 | 3.36529 | +3.365% | agree |
| MTF | share of industry book | Q1 FY 2027 | 0.0278561 | 0.0279 | 0.0287318 | 0.0287 | 3.14352 | +3.144% | agree |
| MTF | share of industry book | Q2 FY 2027 | 0.0278561 | 0.0279 | 0.027885 | 0.0279 | 0.103484 | +0.103% | agree |
| MTF | share of industry book | Q3 FY 2027 | 0.0278561 | 0.0279 | 0.027885 | 0.0279 | 0.103484 | +0.103% | agree |

## Inputs replaced (reviewed facts)

| Input | Period | My workbook | Bridge workbook | My live | Bridge live | Fact ids ok | Vintage ok | Verdict |
|---|---|---:|---:|---:|---:|---|---|---|
| mtf_revenue | Q2 FY 2027 | — | — | 155.595 | 155.59 | yes | yes | agree |
| mtf_yield | Q1 FY 2027 | 0.1495 | 0.1495 | 0.1495 | 0.1495 | yes | yes | agree |

## Daily revenue rows that changed

| Segment | Days | Changed (mine / bridge) | First | Last | Ratio min (mine / bridge) | Ratio max (mine / bridge) | Verdict |
|---|---:|---|---|---|---|---|---|
| F&O | 573 | 0 / 0 |  |  |  /  |  /  | agree |
| Cash | 573 | 0 / 0 |  |  |  /  |  /  | agree |
| Commodities | 272 | 0 / 0 |  |  |  /  |  /  | agree |
| MTF | 507 | 507 / 507 | 2024-10-01 | 2026-10-19 | 0.996982069 / 0.996982069 | 1.108380253 / 1.108380253 | agree |

## Tie-out of MTF quarters (daily sum vs disclosed revenue; self-consistency)

| Quarter | Disclosed MTF revenue (Rs Cr) | Sum of daily MTF revenue | Rel diff | Verdict |
|---|---:|---:|---:|---|
| Q3 FY 2025 | 20.088940 | 20.088940 | 4.4e-16 | agree |
| Q4 FY 2025 | 16.991440 | 16.991440 | 4.4e-16 | agree |
| Q1 FY 2026 | 28.454130 | 28.454130 | 1.1e-16 | agree |
| Q2 FY 2026 | 50.327459 | 50.327459 | 2.2e-16 | agree |
| Q3 FY 2026 | 70.620032 | 70.620032 | 6.7e-16 | agree |
| Q4 FY 2026 | 105.951915 | 105.951915 | 2.2e-16 | agree |
| Q1 FY 2027 | 123.893600 | 123.893600 | 4.4e-16 | agree |
| Q2 FY 2027 | 155.594540 | 155.594540 | 0.0e+00 | agree |

## Trading-day basis

| Item | Mine | Bridge text | Verdict |
|---|---|---|---|
| FY 2025 equity days (calendar) | 249 | 249 | agree |
| FY 2026 equity days (calendar) | 247 | 247 | agree |
| FY 2027 basis | 138 days so far, FY26 count (247) used | FY 2027 247 | agree |
| FY 2026 = sum of handbook trading days | 247 | 247 | agree |

## Notes

Information: Q1 FY27 has 60 trading days (handbook) but 59 industry-book rows; missing day(s): 2026-04-08. The share is calibrated on the 59 rows, so the quarter ties, and the bridge average book (3,469.39) uses 59 days.
MTF recompute: daily revenue = share_q x industry daily book x 0.1495 / (equity days of the FY: FY25 249, FY26 247, FY27 247 as FY26's count because FY27 is incomplete). Share_q = disclosed MTF revenue / sum over the quarter's industry-book days of (book x 0.1495 / days of FY), so each reported quarter ties to its revenue exactly. Groww average book = revenue / (0.1495 x quarter rows / FY days); share is therefore on the average of the daily industry book, not the rounded monthly average of the workbook (this accounts for the +12.2% move in the Q3 FY25 share). Q3 FY27 carries the Q2 FY27 actual share. MTF revenue Q2 FY27 = 0.101 x 15,405.40 / 10 = 155.59 Cr.
Spec vs switch: the spec says '14.95% x the actual trading days of each FY'. FY 2027 is incomplete, so the switch uses FY 2026's 247, not FY 2027's actual days. It has no effect on any reported quarter (the share is calibrated on the same days) but does set the level of the Q3 FY27 estimate. The spec's 'share = disclosed MTF revenue / the industry book' is implemented as a calibration that ties each quarter's daily sum to the disclosed revenue.
The 14.95% is a spoken figure on calls (facts 10102/10103), applied to the whole book; the bridge notes the filed book-yield check of 14.2-16.5%.
