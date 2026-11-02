# MOSL switch m-d: independent recompute

Script: `out/checks/mosl_switch_d_check.py` (+ `mosl_common.py`), Python standard library only; inputs read with `git show 990eb5d:<path>` (calendar, keys, facts). Nothing under `src/engine/` or `src/live/` was read. Bridge: `out/bridges/mosl_d.md`.

Before = my state a+b+c, after = a+b+c+d. m-d changes the statistics, not the daily rows: periods and labels come from the calendar (`fy`, `q_fy`, `fy_month`), YoY is the same period one year back, and the calendar's special sessions are left out of the F&O, cash and commodity averages (MTF keeps them). Quarter calibration still spreads each quarter over every row, special sessions included, so the average over the other days is a little below the quarter total / days. **Not rechecked:** the weekly and weekday tables and the 28 flagged periods (not shown with numbers for this switch).

**Result: 74/74 items agree** (62 to 1e-6 relative or exact; 12 only to the bridge print precision).

ADR before / after values in the bridge table (60 numbers, printed to 6 decimals): max absolute difference 4.99e-07 Cr, max relative difference 6.39e-07 (a 6-decimal print can only resolve 5e-7 Cr).

| Item kind | Checked | Agree | Agree at 1e-6 / exact |
|---|---:|---:|---:|
| ADR | 30 | 30 | 25 |
| Consolidated headline | 5 | 5 | 4 |
| daily rows | 12 | 12 | 12 |
| special | 12 | 12 | 12 |
| labels | 8 | 8 | 8 |
| YoY table | 7 | 7 | 1 |

## Headline (Consolidated)

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| FY 2027 | before 8.650276 / after 8.650276 / d% 0.000000 | before 8.650276 / after 8.650276 / d% +0.0000% | agree | rel 1e-6 | 1.9e-08 |
| Q2 FY 2027 | before 8.967060 / after 8.967060 / d% 0.000000 | before 8.967060 / after 8.967060 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| Q1 FY 2027 | before 8.197926 / after 8.197926 / d% 0.000000 | before 8.197926 / after 8.197926 / d% +0.0000% | agree | rel 1e-6 | 5.9e-08 |
| FY 2027 October | before 2.332592 / after 2.332592 / d% 0.000000 | before 2.332592 / after 2.332592 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| FY 2026 | before 7.642700 / after 7.662290 / d% 0.256322 | before 7.642700 / after 7.662290 / d% +0.2563% | agree | print (4 dp) | 8.5e-05 |

## ADR by period and panel

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| FY 2027, Consolidated | before 8.650276 / after 8.650276 / delta 0.000000 / d% 0.000000 | before 8.650276 / after 8.650276 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.9e-08 |
| FY 2027, Broking | before 4.438283 / after 4.438283 / delta 0.000000 / d% 0.000000 | before 4.438283 / after 4.438283 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 2.8e-08 |
| FY 2027, MTF | before 4.211993 / after 4.211993 / delta 0.000000 / d% 0.000000 | before 4.211993 / after 4.211993 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.0e-08 |
| FY 2027, F&O | before 1.871544 / after 1.871544 / delta 0.000000 / d% 0.000000 | before 1.871544 / after 1.871544 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.0e-07 |
| FY 2027, Cash | before 2.045402 / after 2.045402 / delta 0.000000 / d% 0.000000 | before 2.045402 / after 2.045402 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 2.0e-07 |
| FY 2027, Commodities | before 0.521337 / after 0.521337 / delta 0.000000 / d% 0.000000 | before 0.521337 / after 0.521337 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.8e-07 |
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
| FY 2026, Consolidated | before 7.642700 / after 7.662290 / delta 0.019590 / d% 0.256322 | before 7.642700 / after 7.662290 / delta +0.019590 / d% +0.2563% | agree | print (4 dp) | 8.5e-05 |
| FY 2026, Broking | before 4.329293 / after 4.348883 / delta 0.019590 / d% 0.452497 | before 4.329293 / after 4.348883 / delta +0.019590 / d% +0.4525% | agree | print (4 dp) | 7.6e-06 |
| FY 2026, MTF | before 3.313407 / after 3.313407 / delta 0.000000 / d% 0.000000 | before 3.313407 / after 3.313407 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 5.9e-08 |
| FY 2026, F&O | before 1.849289 / after 1.857828 / delta 0.008539 / d% 0.461772 | before 1.849289 / after 1.857828 / delta +0.008539 / d% +0.4618% | agree | print (4 dp) | 6.1e-05 |
| FY 2026, Cash | before 1.880952 / after 1.888062 / delta 0.007111 / d% 0.378030 | before 1.880952 / after 1.888062 / delta +0.007111 / d% +0.3780% | agree | print (4 dp) | 7.9e-05 |
| FY 2026, Commodities | before 0.599053 / after 0.602993 / delta 0.003940 / d% 0.657679 | before 0.599053 / after 0.602993 / delta +0.003940 / d% +0.6577% | agree | print (4 dp) | 3.9e-05 |

## Q2 FY27 "YoY": workbook comparator vs the same quarter last year

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| Q2 FY27 YoY, Consolidated | workbook YoY (vs Q4 FY26, session kept) 16.194391 / live YoY (vs Q2 FY26) 20.110956 / Q2 FY27 8.967060 / Q4 FY26 7.737644 / Q2 FY26 7.465647 | workbook YoY (vs Q4 FY26, session kept) +16.2% / live YoY (vs Q2 FY26) +20.1% / Q2 FY27 8.967060 / Q4 FY26 7.737644 / Q2 FY26 7.465647 | agree | print (1 dp) | 5.5e-04 |
| Q2 FY27 YoY, Broking | workbook YoY (vs Q4 FY26, session kept) -4.225224 / live YoY (vs Q2 FY26) 9.393932 / Q2 FY27 4.247980 / Q4 FY26 4.455738 / Q2 FY26 3.883196 | workbook YoY (vs Q4 FY26, session kept) -4.2% / live YoY (vs Q2 FY26) +9.4% / Q2 FY27 4.247980 / Q4 FY26 4.455738 / Q2 FY26 3.883196 | agree | print (1 dp) | 6.0e-03 |
| Q2 FY27 YoY, MTF | workbook YoY (vs Q4 FY26, session kept) 43.790815 / live YoY (vs Q2 FY26) 31.727667 / Q2 FY27 4.719079 / Q4 FY26 3.281906 / Q2 FY26 3.582451 | workbook YoY (vs Q4 FY26, session kept) +43.8% / live YoY (vs Q2 FY26) +31.7% / Q2 FY27 4.719079 / Q4 FY26 3.281906 / Q2 FY26 3.582451 | agree | print (1 dp) | 8.7e-04 |
| Q2 FY27 YoY, F&O | workbook YoY (vs Q4 FY26, session kept) -12.782871 / live YoY (vs Q2 FY26) -2.734077 / Q2 FY27 1.694618 / Q4 FY26 1.952394 / Q2 FY26 1.742252 | workbook YoY (vs Q4 FY26, session kept) -12.8% / live YoY (vs Q2 FY26) -2.7% / Q2 FY27 1.694618 / Q4 FY26 1.952394 / Q2 FY26 1.742252 | agree | print (1 dp) | 1.3e-02 |
| Q2 FY27 YoY, Cash | workbook YoY (vs Q4 FY26, session kept) 19.663996 / live YoY (vs Q2 FY26) 19.691712 / Q2 FY27 2.031303 / Q4 FY26 1.698015 / Q2 FY26 1.697112 | workbook YoY (vs Q4 FY26, session kept) +19.7% / live YoY (vs Q2 FY26) +19.7% / Q2 FY27 2.031303 / Q4 FY26 1.698015 / Q2 FY26 1.697112 | agree | print (1 dp) | 1.8e-03 |
| Q2 FY27 YoY, Commodities | workbook YoY (vs Q4 FY26, session kept) -34.323231 / live YoY (vs Q2 FY26) 17.625800 / Q2 FY27 0.522060 / Q4 FY26 0.805330 / Q2 FY26 0.443831 | workbook YoY (vs Q4 FY26, session kept) -34.3% / live YoY (vs Q2 FY26) +17.6% / Q2 FY27 0.522060 / Q4 FY26 0.805330 / Q2 FY26 0.443831 | agree | print (1 dp) | 1.5e-03 |
| finding: Q2 FY27 / printed Q4 FY26 - 1 differs from the printed workbook YoY for Consolidated, Broking, F&O, Cash, Commodities (Q4 FY26 column excludes the 1 Feb 2026 session, the workbook YoY includes it) |  |  | agree | exact |  |

## Special sessions

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| special sessions = the calendar's special_session days: 2023-11-12, 2024-01-20, 2024-03-02, 2024-05-18, 2024-11-01, 2025-02-01, 2025-10-21, 2026-02-01 |  |  | agree | exact |  |
| 2023-11-12 (muhurat, FY 2024): excluded from F&O / cash / commodity averages, kept by MTF (MTF row absent) |  |  | agree | exact |  |
| 2024-01-20 (weekend, FY 2024): excluded from F&O / cash / commodity averages, kept by MTF (MTF row absent) |  |  | agree | exact |  |
| 2024-03-02 (dr_test, FY 2024): excluded from F&O / cash / commodity averages, kept by MTF (MTF row absent) |  |  | agree | exact |  |
| 2024-05-18 (dr_test, FY 2025): excluded from F&O / cash / commodity averages, kept by MTF (MTF row absent) |  |  | agree | exact |  |
| 2024-11-01 (muhurat, FY 2025): excluded from F&O / cash / commodity averages, kept by MTF (MTF row present) |  |  | agree | exact |  |
| 2025-02-01 (budget, FY 2025): excluded from F&O / cash / commodity averages, kept by MTF (MTF row present) |  |  | agree | exact |  |
| 2025-10-21 (muhurat, FY 2026): excluded from F&O / cash / commodity averages, kept by MTF (MTF row present) |  |  | agree | exact |  |
| 2026-02-01 (budget, FY 2026): excluded from F&O / cash / commodity averages, kept by MTF (MTF row present) |  |  | agree | exact |  |
| FY 2026 holds ['2025-10-21', '2026-02-01'], FY 2027 holds 0 special sessions: only FY 2026 moves in the ADR table |  |  | agree | exact |  |
| MTF FY 2026 keeps the two sessions: MTF ADR with them 3.313407 (bridge 3.313407), it would be 3.311599 without them |  |  | agree | exact |  |
| daily rows unchanged by m-d (bridge: 0 changed rows): the quarter totals still tie to the data book over all rows |  |  | agree | exact |  |

## Labels and panel order

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| YoY of Q2 FY 2027 = Q2 FY 2026 (exists in the calendar: True) |  |  | agree | exact |  |
| YoY of Q1 FY 2027 = Q1 FY 2026 (exists in the calendar: True) |  |  | agree | exact |  |
| YoY of FY 2027 = FY 2026 (exists in the calendar: True) |  |  | agree | exact |  |
| YoY of FY 2027 September = FY 2026 September (exists in the calendar: True) |  |  | agree | exact |  |
| YoY of FY 2027 October = FY 2026 October (exists in the calendar: True) |  |  | agree | exact |  |
| workbook quarter rows are ['Q2 FY 2027', 'Q1 FY 2027', 'Q4 FY 2026']: the third ("YoY") row is Q4 FY 2026, two quarters back from Q2 FY 2027, not Q2 FY 2026 |  |  | agree | exact |  |
| bridge panel order is Consolidated, Broking, MTF, F&O, Cash, Commodities for every period (workbook band 3 swaps Cash and Commodities) |  |  | agree | exact |  |
| MTF as NII with no net panel: MTF series is NII (share x book x yield / 247), no net / gross applied |  |  | agree | exact |  |

## Daily revenue rows that changed

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| F&O counts / dates | mine 634/634 changed 0 added 0 dropped 0 first  last ; bridge 634/634 changed 0 added 0 dropped 0 first  last  |  | agree | exact |  |
| F&O ratio min | - |  | agree | blank |  |
| F&O ratio max | - |  | agree | blank |  |
| Cash counts / dates | mine 621/621 changed 0 added 0 dropped 0 first  last ; bridge 621/621 changed 0 added 0 dropped 0 first  last  |  | agree | exact |  |
| Cash ratio min | - |  | agree | blank |  |
| Cash ratio max | - |  | agree | blank |  |
| Commodities counts / dates | mine 646/646 changed 0 added 0 dropped 0 first  last ; bridge 646/646 changed 0 added 0 dropped 0 first  last  |  | agree | exact |  |
| Commodities ratio min | - |  | agree | blank |  |
| Commodities ratio max | - |  | agree | blank |  |
| MTF counts / dates | mine 495/495 changed 0 added 0 dropped 0 first  last ; bridge 495/495 changed 0 added 0 dropped 0 first  last  |  | agree | exact |  |
| MTF ratio min | - |  | agree | blank |  |
| MTF ratio max | - |  | agree | blank |  |

