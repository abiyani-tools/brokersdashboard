# Groww switch g-d: independent recompute

Script: `out/checks/groww_switch_d_check.py` (stdlib json/math/csv). Inputs: db snapshot, Groww fixtures/snapshot, reviewed facts, Angel calibration read from `parity_expected`. No engine code read.

**Result: 80/80 items agree** (66 to 1e-6 relative; 14 agree only to the bridge print precision).

| Item kind | Checked | Agree | Agree at 1e-6 |
|---|---:|---:|---:|
| ADR | 30 | 30 | 30 |
| param | 26 | 26 | 12 |
| input | 10 | 10 | 10 |
| daily | 4 | 4 | 4 |
| tie | 7 | 7 | 7 |
| input-x | 3 | 3 | 3 |

## ADR, Rs crore per trading day (consolidated and panels)

| Period | Panel | My before | Bridge before | My after | Bridge after | Max rel diff | Verdict |
|---|---|---:|---:|---:|---:|---:|---|
| FY 2027 | Consolidated | 20.112171 | 20.112171 | 20.143031 | 20.143031 | 2.1e-08 | agree |
| FY 2027 | Broking | 17.783261 | 17.783261 | 17.814122 | 17.814122 | 7.8e-09 | agree |
| FY 2027 | MTF | 2.328909 | 2.328909 | 2.328909 | 2.328909 | 2.1e-07 | agree |
| FY 2027 | F&O | 12.599111 | 12.599111 | 12.255779 | 12.255779 | 7.0e-09 | agree |
| FY 2027 | Cash | 4.162446 | 4.162446 | 4.185758 | 4.185758 | 4.2e-08 | agree |
| FY 2027 | Commodities | 1.021704 | 1.021704 | 1.372585 | 1.372585 | 3.0e-07 | agree |
| Q2 FY 2027 | Consolidated | 18.775865 | 18.775865 | 18.671320 | 18.671320 | 2.6e-08 | agree |
| Q2 FY 2027 | Broking | 16.293502 | 16.293502 | 16.188957 | 16.188957 | 1.9e-08 | agree |
| Q2 FY 2027 | MTF | 2.482364 | 2.482364 | 2.482364 | 2.482364 | 8.6e-08 | agree |
| Q2 FY 2027 | F&O | 11.074613 | 11.074613 | 10.617876 | 10.617876 | 2.9e-08 | agree |
| Q2 FY 2027 | Cash | 4.099037 | 4.099037 | 4.123907 | 4.123907 | 5.5e-08 | agree |
| Q2 FY 2027 | Commodities | 1.119852 | 1.119852 | 1.447174 | 1.447174 | 7.8e-08 | agree |
| FY 2027 October | Consolidated | 23.871576 | 23.871576 | 24.588926 | 24.588926 | 6.5e-09 | agree |
| FY 2027 October | Broking | 20.973902 | 20.973902 | 21.691252 | 21.691252 | 1.8e-08 | agree |
| FY 2027 October | MTF | 2.897674 | 2.897674 | 2.897674 | 2.897674 | 1.1e-07 | agree |
| FY 2027 October | F&O | 15.080776 | 15.080776 | 15.181758 | 15.181758 | 2.3e-08 | agree |
| FY 2027 October | Cash | 4.511097 | 4.511097 | 4.634212 | 4.634212 | 4.8e-08 | agree |
| FY 2027 October | Commodities | 1.382030 | 1.382030 | 1.875282 | 1.875282 | 3.5e-07 | agree |
| FY 2026 | Consolidated | 15.906563 | 15.906563 | 15.989974 | 15.989974 | 2.1e-08 | agree |
| FY 2026 | Broking | 14.899155 | 14.899155 | 14.982565 | 14.982565 | 3.0e-08 | agree |
| FY 2026 | MTF | 1.007408 | 1.007408 | 1.007408 | 1.007408 | 2.1e-07 | agree |
| FY 2026 | F&O | 10.772896 | 10.772896 | 10.772896 | 10.772896 | 1.0e-09 | agree |
| FY 2026 | Cash | 3.325009 | 3.325009 | 3.325009 | 3.325009 | 1.4e-07 | agree |
| FY 2026 | Commodities | 0.801250 | 0.801250 | 0.884661 | 0.884661 | 3.1e-07 | agree |
| FY 2026 October | Consolidated | 16.556092 | 16.556092 | 16.522023 | 16.522023 | 2.3e-08 | agree |
| FY 2026 October | Broking | 15.468204 | 15.468204 | 15.434134 | 15.434134 | 1.7e-08 | agree |
| FY 2026 October | MTF | 1.087888 | 1.087888 | 1.087888 | 1.087888 | 3.5e-07 | agree |
| FY 2026 October | F&O | 11.350532 | 11.350532 | 11.350532 | 11.350532 | 2.5e-09 | agree |
| FY 2026 October | Cash | 3.402207 | 3.402207 | 3.402207 | 3.402207 | 1.4e-07 | agree |
| FY 2026 October | Commodities | 0.715465 | 0.715465 | 0.681395 | 0.681395 | 6.0e-07 | agree |

## Parameters that moved

| Segment | Quantity | Quarter | My before | Bridge before | My after | Bridge after | My d% | Bridge d% | Verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Cash | revenue Rs Mn | Q2 FY 2027 | — | — | 2680.54 | 2,680.54 | — | blank | agree |
| Cash | share (ADTO, legacy basis) | Q2 FY 2027 | 0.302 | 0.3020 | 0.308 | 0.3080 | 1.98675 | +1.987% | agree |
| Cash | share (ADTO, legacy basis) | Q3 FY 2027 | 0.302 | 0.3020 | 0.308 | 0.3080 | 1.98675 | +1.987% | agree |
| Cash | take rate Rs/order | Q2 FY 2027 | 20.1564 | 20.1564 | 19.8836 | 19.8836 | -1.35314 | -1.353% | agree |
| Cash | take rate Rs/order | Q3 FY 2027 | 20.1564 | 20.1564 | 20.3031 | 20.3031 | 0.727932 | +0.728% | agree |
| Commodities | revenue Rs Mn | Q4 FY 2026 | — | — | 690.991 | 690.99 | — | blank | agree |
| Commodities | revenue Rs Mn | Q1 FY 2027 | — | — | 758.848 | 758.85 | — | blank | agree |
| Commodities | revenue Rs Mn | Q2 FY 2027 | — | — | 955.135 | 955.13 | — | blank | agree |
| Commodities | share of Angel market orders | Q3 FY 2026 | 0.290849 | 0.2908 | 0.300716 | 0.3007 | 3.39225 | +3.392% | agree |
| Commodities | share of Angel market orders | Q4 FY 2026 | 0.290849 | 0.2908 | 0.42265 | 0.4227 | 45.3159 | +45.316% | agree |
| Commodities | share of Angel market orders | Q1 FY 2027 | 0.290849 | 0.2908 | 0.461144 | 0.4611 | 58.5507 | +58.551% | agree |
| Commodities | share of Angel market orders | Q2 FY 2027 | 0.290849 | 0.2908 | 0.423021 | 0.4230 | 45.4435 | +45.443% | agree |
| Commodities | share of Angel market orders | Q3 FY 2027 | 0.290849 | 0.2908 | 0.444172 | 0.4442 | 52.7157 | +52.716% | agree |
| Commodities | take rate Rs/order | Q3 FY 2026 | 24.2038 | 24.2038 | 22.2949 | 22.2949 | -7.88662 | -7.887% | agree |
| Commodities | take rate Rs/order | Q4 FY 2026 | 24.2038 | 24.2038 | 20.4732 | 20.4732 | -15.4133 | -15.413% | agree |
| Commodities | take rate Rs/order | Q1 FY 2027 | 24.2038 | 24.2038 | 21.5055 | 21.5055 | -11.1483 | -11.148% | agree |
| Commodities | take rate Rs/order | Q2 FY 2027 | 24.2038 | 24.2038 | 21.5055 | 21.5055 | -11.1483 | -11.148% | agree |
| Commodities | take rate Rs/order | Q3 FY 2027 | 24.2038 | 24.2038 | 21.5055 | 21.5055 | -11.1483 | -11.148% | agree |
| F&O | revenue Rs Mn | Q1 FY 2027 | — | — | 8037.6 | 8,037.60 | — | blank | agree |
| F&O | revenue Rs Mn | Q2 FY 2027 | — | — | 6901.62 | 6,901.62 | — | blank | agree |
| F&O | share (ADTO, legacy basis) | Q1 FY 2027 | 0.2226 | 0.2226 | 0.22 | 0.2200 | -1.16801 | -1.168% | agree |
| F&O | share (ADTO, legacy basis) | Q2 FY 2027 | 0.2226 | 0.2226 | 0.22 | 0.2200 | -1.16801 | -1.168% | agree |
| F&O | share (ADTO, legacy basis) | Q3 FY 2027 | 0.2226 | 0.2226 | 0.231 | 0.2310 | 3.77358 | +3.774% | agree |
| F&O | take rate Rs/order | Q1 FY 2027 | 27.4838 | 27.4838 | 27.1663 | 27.1663 | -1.1553 | -1.155% | agree |
| F&O | take rate Rs/order | Q2 FY 2027 | 27.4838 | 27.4838 | 26.6618 | 26.6618 | -2.9911 | -2.991% | agree |
| F&O | take rate Rs/order | Q3 FY 2027 | 27.4838 | 27.4838 | 26.6618 | 26.6618 | -2.9911 | -2.991% | agree |

## Inputs replaced (reviewed facts)

| Input | Period | My workbook | Bridge workbook | My live | Bridge live | Fact ids ok | Vintage ok | Verdict |
|---|---|---:|---:|---:|---:|---|---|---|
| revmix_cash | Q2 FY 2027 | — | — | 0.174 | 0.1740 | yes | yes | agree |
| revmix_comm | Q4 FY 2026 | 0.04 | 0.0400 | 0.045 | 0.0450 | yes | yes | agree |
| revmix_comm | Q1 FY 2027 | 0.049 | 0.0490 | 0.049 | 0.0490 | yes | yes | agree |
| revmix_comm | Q2 FY 2027 | — | — | 0.062 | 0.0620 | yes | yes | agree |
| revmix_fo | Q1 FY 2027 | 0.52 | 0.5200 | 0.519 | 0.5190 | yes | yes | agree |
| revmix_fo | Q2 FY 2027 | — | — | 0.448 | 0.4480 | yes | yes | agree |
| share_cash_adto_q | Q2 FY 2027 | — | — | 0.308 | 0.3080 | yes | yes | agree |
| share_fo_adto_q | Q1 FY 2027 | 0.22 | 0.2200 | 0.22 | 0.2200 | yes | yes | agree |
| share_fo_adto_q | Q2 FY 2027 | — | — | 0.22 | 0.2200 | yes | yes | agree |
| total_income | Q2 FY 2027 | — | — | 15405.4 | 15,405.40 | yes | yes | agree |

## Daily revenue rows that changed

| Segment | Days | Changed (mine / bridge) | First | Last | Ratio min (mine / bridge) | Ratio max (mine / bridge) | Verdict |
|---|---:|---|---|---|---|---|---|
| F&O | 573 | 138 / 138 | 2026-04-01 | 2026-10-21 | 0.958758184 / 0.958758184 | 1.006696093 / 1.006696093 | agree |
| Cash | 573 | 78 / 78 | 2026-07-01 | 2026-10-21 | 1.006067353 / 1.006067353 | 1.027291490 / 1.027291490 | agree |
| Commodities | 272 | 272 / 272 | 2025-10-01 | 2026-10-21 | 0.952380952 / 0.952380952 | 1.408750347 / 1.408750347 | agree |
| MTF | 507 | 0 / 0 |  |  |  /  |  /  | agree |

## Tie-out of newly calibrated quarters (self-consistency, not in the bridge)

| Segment | Quarter | Reported revenue | Sum of daily revenue | Rel diff | Tolerance | Verdict |
|---|---|---:|---:|---:|---:|---|
| fo | Q1 FY 2027 | 8037.5973 | 8037.7272 | 1.62e-05 | 5e-03 | agree |
| fo | Q2 FY 2027 | 6901.6192 | 6901.6192 | 1.11e-16 | 5e-03 | agree |
| cash | Q2 FY 2027 | 2680.5396 | 2680.5396 | 2.22e-16 | 1e-09 | agree |
| comm | Q3 FY 2026 | 441.3752 | 441.3752 | 0.00e+00 | 1e-09 | agree |
| comm | Q4 FY 2026 | 690.9907 | 690.9907 | 1.11e-16 | 1e-09 | agree |
| comm | Q1 FY 2027 | 758.8483 | 758.8483 | 5.55e-16 | 1e-09 | agree |
| comm | Q2 FY 2027 | 955.1348 | 955.1348 | 2.22e-16 | 1e-09 | agree |

## Cross-check of the commodity market-order denominator (input consistency)

| Quarter | Sum of daily market orders (mine) | Sum of Angel monthly market orders (db snapshot) | Rel diff | Verdict |
|---|---:|---:|---:|---|
| Q3 FY 2026 | 65.833284 | 65.833284 | 4.4e-16 | agree |
| Q4 FY 2026 | 79.855608 | 79.855608 | 0.0e+00 | agree |
| Q1 FY 2027 | 76.518989 | 76.518989 | 2.2e-16 | agree |

## Notes

Calibration rule recomputed: each reported quarter solves the take rate (F&O, cash) so that revenue = mix x total income; F&O Q1/Q2 FY27 use shares 0.22 (facts 10080/10082, legacy = 2 x printed) and the mean of the three monthly Angel CPOs; cash Q2 FY27 uses share 0.308 and Angel's Q2 FY27 trades/order 6.15024. Commodities: take rate is Angel's quarterly take rate (22.29495, 20.4732, 21.5055, and 21.5055 for Q2 FY27), share = revenue / take rate / sum of market orders, no 5% growth inside reported quarters. Q3 FY27 (estimate): F&O share = Q2 x 1.05, commodity share = Q2 x 1.05, cash take rate = trailing mean of the last 3 actuals; take rates otherwise carried.
Spec vs switch: the spec (g-d) and D12 describe 'take rate and share calibrated' for commodities and 'Groww-specific once calibrated'. The switch calibrates the share and keeps Angel's quarterly commodity take rate (borrowed). The Q2 FY27 Angel take rate (21.5055) is Angel's own carried estimate, since Angel has no Q2 FY27 actual, and the Q2 FY27 commodity market orders rest on Angel's estimated contracts per order for Jul-Sep 2026. The commodity share therefore absorbs Angel's estimate error.
The F&O Q1 FY27 take rate uses the quarterly mean of the monthly CPOs (Apr 14.424, May and Jun 14.352), not the workbook's unused 14.743.
Shares 0.22 / 0.22 / 0.308 are read visually from letter charts (fact notes); a 0.005 misread on the printed new-basis share is 4.5% on the F&O take rate.
