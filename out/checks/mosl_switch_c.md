# MOSL switch m-c: independent recompute

Script: `out/checks/mosl_switch_c_check.py` (+ `mosl_common.py`), Python standard library only; inputs read with `git show 990eb5d:<path>`. Nothing under `src/engine/` or `src/live/` was read. Bridge: `out/bridges/mosl_c.md`.

Before = my state a+b, after = a+b+c: an FY / quarter / month average runs over the days that have a value; error rows (`#N/A`, `#VALUE!`), blank rows and key-less rows are left out instead of turning the whole average into the workbook's IFERROR 0. The "ADR" table is the unguarded statistic (a segment with no value in a period adds 0 to the sum; the live rows flag that period as insufficient), as the bridge says. **Not rechecked:** the bridge's count of 28 / 18 periods flagged insufficient and the weekly / weekday tables: the flagging rules are engine logic the spec does not define; only the ADR, parameter, row and day-count numbers are.

**Result: 77/77 items agree** (69 to 1e-6 relative or exact; 8 only to the bridge print precision).

ADR before / after values in the bridge table (60 numbers, printed to 6 decimals): max absolute difference 4.99e-07 Cr, max relative difference 4.46e-07 (a 6-decimal print can only resolve 5e-7 Cr).

| Item kind | Checked | Agree | Agree at 1e-6 / exact |
|---|---:|---:|---:|
| ADR | 30 | 30 | 29 |
| Consolidated headline | 5 | 5 | 4 |
| param | 2 | 2 | 1 |
| param set | 1 | 1 | 1 |
| daily rows | 12 | 12 | 12 |
| no-row days | 3 | 3 | 3 |
| keys | 4 | 4 | 4 |
| silent zero | 9 | 9 | 4 |
| days used | 8 | 8 | 8 |
| unchanged | 3 | 3 | 3 |

## Headline (Consolidated)

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| FY 2027 | before 6.083537 / after 8.650276 / d% 42.191551 | before 6.083537 / after 8.650276 / d% +42.1916% | agree | print (4 dp) | 1.2e-06 |
| Q2 FY 2027 | before 8.967060 / after 8.967060 / d% 0.000000 | before 8.967060 / after 8.967060 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| Q1 FY 2027 | before 8.197926 / after 8.197926 / d% 0.000000 | before 8.197926 / after 8.197926 / d% +0.0000% | agree | rel 1e-6 | 5.9e-08 |
| FY 2027 October | before 2.332592 / after 2.332592 / d% 0.000000 | before 2.332592 / after 2.332592 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| FY 2026 | before 7.642700 / after 7.642700 / d% 0.000000 | before 7.642700 / after 7.642700 / d% +0.0000% | agree | rel 1e-6 | 2.5e-09 |

## ADR by period and panel

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| FY 2027, Consolidated | before 6.083537 / after 8.650276 / delta 2.566739 / d% 42.191551 | before 6.083537 / after 8.650276 / delta +2.566739 / d% +42.1916% | agree | print (4 dp) | 1.2e-06 |
| FY 2027, Broking | before 1.871544 / after 4.438283 / delta 2.566739 / d% 137.145502 | before 1.871544 / after 4.438283 / delta +2.566739 / d% +137.1455% | agree | rel 1e-6 | 1.2e-07 |
| FY 2027, MTF | before 4.211993 / after 4.211993 / delta 0.000000 / d% 0.000000 | before 4.211993 / after 4.211993 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.0e-08 |
| FY 2027, F&O | before 1.871544 / after 1.871544 / delta 0.000000 / d% 0.000000 | before 1.871544 / after 1.871544 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.0e-07 |
| FY 2027, Cash | before 0.000000 / after 2.045402 / delta 2.045402 / d% - | before 0.000000 / after 2.045402 / delta +2.045402 / d%  | agree | rel 1e-6 | 2.0e-07 |
| FY 2027, Commodities | before 0.000000 / after 0.521337 / delta 0.521337 / d% - | before 0.000000 / after 0.521337 / delta +0.521337 / d%  | agree | rel 1e-6 | 1.8e-07 |
| Q2 FY 2027, Consolidated | before 8.967060 / after 8.967060 / delta 0.000000 / d% 0.000000 | before 8.967060 / after 8.967060 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| Q2 FY 2027, Broking | before 4.247980 / after 4.247980 / delta 0.000000 / d% 0.000000 | before 4.247980 / after 4.247980 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 9.1e-08 |
| Q2 FY 2027, MTF | before 4.719079 / after 4.719079 / delta 0.000000 / d% 0.000000 | before 4.719079 / after 4.719079 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 3.7e-08 |
| Q2 FY 2027, F&O | before 1.694618 / after 1.694618 / delta 0.000000 / d% 0.000000 | before 1.694618 / after 1.694618 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 2.1e-07 |
| Q2 FY 2027, Cash | before 2.031303 / after 2.031303 / delta 0.000000 / d% 0.000000 | before 2.031303 / after 2.031303 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.4e-08 |
| Q2 FY 2027, Commodities | before 0.522060 / after 0.522060 / delta 0.000000 / d% 0.000000 | before 0.522060 / after 0.522060 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 3.2e-07 |
| Q1 FY 2027, Consolidated | before 8.197926 / after 8.197926 / delta 0.000000 / d% 0.000000 | before 8.197926 / after 8.197926 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 5.9e-08 |
| Q1 FY 2027, Broking | before 4.544588 / after 4.544588 / delta 0.000000 / d% 0.000000 | before 4.544588 / after 4.544588 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 3.6e-08 |
| Q1 FY 2027, MTF | before 3.653339 / after 3.653339 / delta 0.000000 / d% 0.000000 | before 3.653339 / after 3.653339 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 9.6e-08 |
| Q1 FY 2027, F&O | before 1.963321 / after 1.963321 / delta 0.000000 / d% 0.000000 | before 1.963321 / after 1.963321 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.4e-08 |
| Q1 FY 2027, Cash | before 2.060675 / after 2.060675 / delta 0.000000 / d% 0.000000 | before 2.060675 / after 2.060675 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 7.5e-08 |
| Q1 FY 2027, Commodities | before 0.520592 / after 0.520592 / delta 0.000000 / d% 0.000000 | before 0.520592 / after 0.520592 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.5e-07 |
| FY 2027 October, Consolidated | before 2.332592 / after 2.332592 / delta 0.000000 / d% 0.000000 | before 2.332592 / after 2.332592 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| FY 2027 October, Broking | before 2.332592 / after 2.332592 / delta 0.000000 / d% 0.000000 | before 2.332592 / after 2.332592 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| FY 2027 October, MTF | before 0.000000 / after 0.000000 / delta 0.000000 / d% - | before 0.000000 / after 0.000000 / delta +0.000000 / d%  | agree | rel 1e-6 | 0.0e+00 |
| FY 2027 October, F&O | before 2.332592 / after 2.332592 / delta 0.000000 / d% 0.000000 | before 2.332592 / after 2.332592 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| FY 2027 October, Cash | before 0.000000 / after 0.000000 / delta 0.000000 / d% - | before 0.000000 / after 0.000000 / delta +0.000000 / d%  | agree | rel 1e-6 | 0.0e+00 |
| FY 2027 October, Commodities | before 0.000000 / after 0.000000 / delta 0.000000 / d% - | before 0.000000 / after 0.000000 / delta +0.000000 / d%  | agree | rel 1e-6 | 0.0e+00 |
| FY 2026, Consolidated | before 7.642700 / after 7.642700 / delta 0.000000 / d% 0.000000 | before 7.642700 / after 7.642700 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 2.5e-09 |
| FY 2026, Broking | before 4.329293 / after 4.329293 / delta 0.000000 / d% 0.000000 | before 4.329293 / after 4.329293 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| FY 2026, MTF | before 3.313407 / after 3.313407 / delta 0.000000 / d% 0.000000 | before 3.313407 / after 3.313407 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 5.9e-08 |
| FY 2026, F&O | before 1.849289 / after 1.849289 / delta 0.000000 / d% 0.000000 | before 1.849289 / after 1.849289 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 2.7e-07 |
| FY 2026, Cash | before 1.880952 / after 1.880952 / delta 0.000000 / d% 0.000000 | before 1.880952 / after 1.880952 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 2.6e-07 |
| FY 2026, Commodities | before 0.599053 / after 0.599053 / delta 0.000000 / d% 0.000000 | before 0.599053 / after 0.599053 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 3.9e-07 |

## Parameters that moved

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| Cash, model gross brokerage Rs Cr, Q3 FY 2027 | before 221.237185 / after - / d% - | before 221.24 / after — / d%  | agree | print (2 dp) | 1.3e-05 |
| Cash, model net brokerage Rs Cr, Q3 FY 2027 | before 0.000000 / after - / d% - | before 0.0000 / after — / d%  | agree | rel 1e-6 | 0.0e+00 |
| moved parameters: mine = bridge (2 listed) | only mine: []; only bridge: [] |  | agree | exact |  |

## Days with no row; keys without gaps or zeros

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| F&O: 124 days with no row, 2023-09-29 .. 2024-03-28 | mine 124 days 2023-09-29 .. 2024-03-28 |  | agree | exact |  |
| Cash: 13 days with no row, 2026-10-01 .. 2026-10-21 | mine 13 days 2026-10-01 .. 2026-10-21 |  | agree | exact |  |
| Commodities: 7 days with no row, 2026-10-01 .. 2026-10-12 | mine 7 days 2026-10-01 .. 2026-10-12 |  | agree | exact |  |
| lake F&O and cash keys: every equity day from 2024-04-01 (634 days) present, status ok, non-zero (nse io, bse, nse cash, bse cash) |  |  | agree | exact |  |
| MCX key: every MCX calendar day from 2024-04-01 (660 days) present and non-zero |  |  | agree | exact |  |
| workbook-keyed cash (state a): every day present and non-zero |  |  | agree | exact |  |
| industry MTF book: every row present and non-zero (507 rows, 2024-10-01 .. 2026-10-19) |  |  | agree | exact |  |

## The silent zero in the workbook (Methodology issue 1) and the days used

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| workbook FY 2027 cash: 125 numeric rows, 13 error rows (Methodology 1: 125 / 13); IFERROR gives 0.0000, error rows skipped 1.8404 |  |  | agree | exact |  |
| workbook FY 2027 comm: 130 numeric rows, 7 error rows (Methodology 1: 130 / 7); IFERROR gives 0.0000, error rows skipped 0.6479 |  |  | agree | exact |  |
| workbook FY 2027 fo: 138 numeric rows, 0 error rows (Methodology 1: 138 / 0); IFERROR gives 1.8054, error rows skipped 1.8054 |  |  | agree | exact |  |
| workbook FY 2027 mtf: 124 numeric rows, 0 error rows (Methodology 1: 124 / 0); IFERROR gives 3.9876, error rows skipped 3.9876 |  |  | agree | exact |  |
| Methodology issue 1, FY 2027 cash with the error days skipped (workbook as saved) | 1.840362 | 1.840 | agree | print (3 dp) | 2.0e-04 |
| Methodology issue 1, FY 2027 commodities with the error days skipped (workbook as saved) | 0.647897 | 0.648 | agree | print (3 dp) | 1.6e-04 |
| Methodology issue 1, FY 2027 Broking with the error days skipped (workbook as saved) | 4.293688 | 4.294 | agree | print (3 dp) | 7.3e-05 |
| Methodology issue 1, FY 2027 Consolidated with the error days skipped (workbook as saved) | 8.281328 | 8.281 | agree | print (3 dp) | 4.0e-05 |
| Methodology issue 1, FY 2027 Broking as the workbook shows it (silent zeros) | 1.805429 | 1.805 | agree | print (3 dp) | 2.4e-04 |
| cash FY 2027 after m-c: 125 days with a value (expected 125) |  |  | agree | exact |  |
| comm FY 2027 after m-c: 130 days with a value (expected 130) |  |  | agree | exact |  |
| mtf FY 2027 after m-c: 124 days with a value (expected 124) |  |  | agree | exact |  |
| fo FY 2027 after m-c: 138 days with a value (expected 138) |  |  | agree | exact |  |
| cash FY 2027 October after m-c: 0 days with a value (expected 0) |  |  | agree | exact |  |
| comm FY 2027 October after m-c: 0 days with a value (expected 0) |  |  | agree | exact |  |
| fo FY 2027 October after m-c: 13 days with a value (expected 13) |  |  | agree | exact |  |
| FY 2027 October: cash and commodities have no value at all (flagged insufficient in the live rows, 0 added in the unguarded table) |  |  | agree | exact |  |
| Q2 FY 2027: no error row in the period, so m-c leaves every panel unchanged |  |  | agree | exact |  |
| Q1 FY 2027: no error row in the period, so m-c leaves every panel unchanged |  |  | agree | exact |  |
| FY 2026: no error row in the period, so m-c leaves every panel unchanged |  |  | agree | exact |  |

## Daily revenue rows that changed

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| F&O counts / dates | mine 758/634 changed 0 added 0 dropped 124 first  last ; bridge 758/634 changed 0 added 0 dropped 124 first  last  |  | agree | exact |  |
| F&O ratio min | - |  | agree | blank |  |
| F&O ratio max | - |  | agree | blank |  |
| Cash counts / dates | mine 634/621 changed 0 added 0 dropped 13 first  last ; bridge 634/621 changed 0 added 0 dropped 13 first  last  |  | agree | exact |  |
| Cash ratio min | - |  | agree | blank |  |
| Cash ratio max | - |  | agree | blank |  |
| Commodities counts / dates | mine 653/646 changed 0 added 0 dropped 7 first  last ; bridge 653/646 changed 0 added 0 dropped 7 first  last  |  | agree | exact |  |
| Commodities ratio min | - |  | agree | blank |  |
| Commodities ratio max | - |  | agree | blank |  |
| MTF counts / dates | mine 495/495 changed 0 added 0 dropped 0 first  last ; bridge 495/495 changed 0 added 0 dropped 0 first  last  |  | agree | exact |  |
| MTF ratio min | - |  | agree | blank |  |
| MTF ratio max | - |  | agree | blank |  |

