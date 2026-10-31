# Groww switch g-b: independent recompute

Script: `out/checks/groww_switch_b_check.py` (stdlib json/math/csv). Inputs: db snapshot, Groww fixtures/snapshot, reviewed facts, Angel calibration read from `parity_expected`. No engine code read.

**Result: 47/47 items agree** (46 to 1e-6 relative; 1 agree only to the bridge print precision).

| Item kind | Checked | Agree | Agree at 1e-6 |
|---|---:|---:|---:|
| ADR | 30 | 30 | 30 |
| param | 6 | 6 | 5 |
| input | 5 | 5 | 5 |
| daily | 4 | 4 | 4 |
| tie | 2 | 2 | 2 |

## ADR, Rs crore per trading day (consolidated and panels)

| Period | Panel | My before | Bridge before | My after | Bridge after | Max rel diff | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| FY 2027 | Consolidated | 19.468553 | 19.468553 | 19.468553 | 19.468553 | 1.6e-08 | agree |
| FY 2027 | Broking | 17.139643 | 17.139643 | 17.139643 | 17.139643 | 1.1e-08 | agree |
| FY 2027 | MTF | 2.328909 | 2.328909 | 2.328909 | 2.328909 | 2.1e-07 | agree |
| FY 2027 | F&O | 11.955493 | 11.955493 | 11.955493 | 11.955493 | 4.8e-09 | agree |
| FY 2027 | Cash | 4.162446 | 4.162446 | 4.162446 | 4.162446 | 4.2e-08 | agree |
| FY 2027 | Commodities | 1.021704 | 1.021704 | 1.021704 | 1.021704 | 3.0e-07 | agree |
| Q2 FY 2027 | Consolidated | 18.682593 | 18.682593 | 18.682593 | 18.682593 | 1.1e-08 | agree |
| Q2 FY 2027 | Broking | 16.200229 | 16.200229 | 16.200229 | 16.200229 | 1.8e-11 | agree |
| Q2 FY 2027 | MTF | 2.482364 | 2.482364 | 2.482364 | 2.482364 | 8.6e-08 | agree |
| Q2 FY 2027 | F&O | 10.981340 | 10.981340 | 10.981340 | 10.981340 | 1.3e-08 | agree |
| Q2 FY 2027 | Cash | 4.099037 | 4.099037 | 4.099037 | 4.099037 | 5.5e-08 | agree |
| Q2 FY 2027 | Commodities | 1.119852 | 1.119852 | 1.119852 | 1.119852 | 7.8e-08 | agree |
| FY 2027 October | Consolidated | 17.505687 | 17.505687 | 17.505687 | 17.505687 | 2.8e-08 | agree |
| FY 2027 October | Broking | 14.608014 | 14.608014 | 14.608014 | 14.608014 | 1.4e-08 | agree |
| FY 2027 October | MTF | 2.897674 | 2.897674 | 2.897674 | 2.897674 | 1.1e-07 | agree |
| FY 2027 October | F&O | 8.714887 | 8.714887 | 8.714887 | 8.714887 | 8.4e-09 | agree |
| FY 2027 October | Cash | 4.511097 | 4.511097 | 4.511097 | 4.511097 | 4.7e-08 | agree |
| FY 2027 October | Commodities | 1.382030 | 1.382030 | 1.382030 | 1.382030 | 3.5e-07 | agree |
| FY 2026 | Consolidated | 12.996051 | 12.996051 | 15.906563 | 15.906563 | 2.3e-08 | agree |
| FY 2026 | Broking | 11.988643 | 11.988643 | 14.899155 | 14.899155 | 1.4e-08 | agree |
| FY 2026 | MTF | 1.007408 | 1.007408 | 1.007408 | 1.007408 | 2.1e-07 | agree |
| FY 2026 | F&O | 8.603497 | 8.603497 | 10.772896 | 10.772896 | 3.1e-08 | agree |
| FY 2026 | Cash | 2.583896 | 2.583896 | 3.325009 | 3.325009 | 1.7e-07 | agree |
| FY 2026 | Commodities | 0.801250 | 0.801250 | 0.801250 | 0.801250 | 3.1e-07 | agree |
| FY 2026 October | Consolidated | 16.556092 | 16.556092 | 16.556092 | 16.556092 | 2.3e-08 | agree |
| FY 2026 October | Broking | 15.468204 | 15.468204 | 15.468204 | 15.468204 | 1.9e-10 | agree |
| FY 2026 October | MTF | 1.087888 | 1.087888 | 1.087888 | 1.087888 | 3.5e-07 | agree |
| FY 2026 October | F&O | 11.350532 | 11.350532 | 11.350532 | 11.350532 | 2.5e-09 | agree |
| FY 2026 October | Cash | 3.402207 | 3.402207 | 3.402207 | 3.402207 | 1.4e-07 | agree |
| FY 2026 October | Commodities | 0.715465 | 0.715465 | 0.715465 | 0.715465 | 6.0e-07 | agree |

## Parameters that moved

| Segment | Quantity | Quarter | My before | Bridge before | My after | Bridge after | My d% | Bridge d% | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Cash | revenue Rs Mn | Q1 FY 2026 | — | — | 1830.55 | 1,830.55 | — | blank | agree |
| Cash | share (ADTO, legacy basis) | Q1 FY 2026 | — | — | 0.236 | 0.2360 | — | blank | agree |
| Cash | take rate Rs/order | Q1 FY 2026 | — | — | 18.6158 | 18.6158 | — | blank | agree |
| F&O | revenue Rs Mn | Q1 FY 2026 | — | — | 5349.38 | 5,349.38 | — | blank | agree |
| F&O | share (ADTO, legacy basis) | Q1 FY 2026 | — | — | 0.144 | 0.1440 | — | blank | agree |
| F&O | take rate Rs/order | Q1 FY 2026 | — | — | 32.3292 | 32.3292 | — | blank | agree |

## Inputs replaced (reviewed facts)

| Input | Period | My workbook | Bridge workbook | My live | Bridge live | Fact ids ok | Vintage ok | Verdict |
|---|---|---:|---:|---:|---:|---|---|---|
| revmix_cash | Q1 FY 2026 | 0.19 | 0.1900 | 0.193 | 0.1930 | yes | yes | agree |
| revmix_fo | Q1 FY 2026 | 0.56 | 0.5600 | 0.564 | 0.5640 | yes | yes | agree |
| share_cash_adto_q | Q1 FY 2026 | — | — | 0.236 | 0.2360 | yes | yes | agree |
| share_fo_adto_q | Q1 FY 2026 | — | — | 0.144 | 0.1440 | yes | yes | agree |
| total_income | Q1 FY 2026 | — | — | 9484.71 | 9,484.71 | yes | yes | agree |

## Daily revenue rows that changed

| Segment | Days | Changed (mine / bridge) | First | Last | Ratio min (mine / bridge) | Ratio max (mine / bridge) | Verdict |
|---|---:|---|---|---|---|---|---|
| F&O | 573 | 61 / 61 | 2025-04-01 | 2025-06-30 |  /  |  /  | agree |
| Cash | 573 | 61 / 61 | 2025-04-01 | 2025-06-30 |  /  |  /  | agree |
| Commodities | 272 | 0 / 0 |  |  |  /  |  /  | agree |
| MTF | 507 | 0 / 0 |  |  |  /  |  /  | agree |

## Tie-out of newly calibrated quarters (self-consistency, not in the bridge)

| Segment | Quarter | Reported revenue | Sum of daily revenue | Rel diff | Tolerance | Verdict |
|---|---|---:|---:|---:|---:|---|
| fo | Q1 FY 2026 | 5349.3764 | 5358.4149 | 1.69e-03 | 5e-03 | agree |
| cash | Q1 FY 2026 | 1830.5490 | 1830.5490 | 2.22e-16 | 1e-09 | agree |

## Notes

Sensitivity (information, not a check): if the Q1 FY26 cash mix were restated by the Q2 FY26 ratio (0.9175), FY 2026 cash ADR would be 3.263886 instead of 3.325009 (-1.84%).
Q1 FY26 calibration: revenue = mix x 9,484.71 Rs Mn (fact 10055); mixes F&O 0.564, cash 0.193 (original classification, facts 10041/10042); shares are legacy basis = 2 x printed new basis (0.072, 0.118 giving 0.144, 0.236; facts 10078/10079); trades per order Q1 FY26 = Angel's 5.62978; F&O contracts per order = mean of Angel's Apr/May/Jun 2025 values.
Spec vs switch: consistent with the spec ('no figures before Q1 FY26'): Q3 FY25 and Q4 FY25 F&O/cash remain numeric zero in the daily rows (they are statistics only until g-g flags them).
FY 2026 changes only through Q1 FY26 days; FY27 and Q2 FY27 are untouched (ADR delta exactly 0).
