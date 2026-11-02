# MOSL switch m-b: independent recompute

Script: `out/checks/mosl_switch_b_check.py` (+ `mosl_common.py`), Python standard library only; inputs read with `git show 990eb5d:<path>` (reviewed facts; workbook keys `snapshot/mosl_snapshot_2026-10-23.json`; lake keys `snapshot/mosl_lake_2026-11-02.json` = ExchangesDash main as read 2 Nov 2026; MCX, calendar, industry book `snapshot/db_snapshot_2026-10-23.json`). Nothing under `src/engine/` or `src/live/` was read. Bridge: `out/bridges/mosl_b.md`.

Before = my state a (m-a recomputed), after = a + b: the cash key is the lake `nse_cash/turnover_cr` + `bse_cash/turnover_cr` on its own date and the F&O key the lake `nse_fo/io_contracts` + `bse_fo/contracts`; the quarter totals stay the data-book net brokerage, only the day shape moves. Months of the bridge (FY 2027 September, FY 2027 August, FY 2026 September) are checked as well.

**Result: 102/104 items agree** (79 to 1e-6 relative or exact; 23 only to the bridge print precision).

**2 item(s) DIFFER** (listed below with cause).

ADR before / after values in the bridge table (96 numbers, printed to 6 decimals): max absolute difference 4.99e-07 Cr, max relative difference 5.45e-07 (a 6-decimal print can only resolve 5e-7 Cr).

| Item kind | Checked | Agree | Agree at 1e-6 / exact |
|---|---:|---:|---:|
| ADR | 48 | 48 | 35 |
| Consolidated headline | 5 | 5 | 4 |
| param | 9 | 9 | 0 |
| param set | 1 | 1 | 1 |
| daily rows | 12 | 10 | 10 |
| cash key | 5 | 5 | 5 |
| F&O key | 4 | 4 | 4 |
| tie to data book | 20 | 20 | 20 |

## Differences and their cause

- `F&O counts / dates` (mine 757/758 changed 61 added 1 dropped 0 first 2024-04-01 last 2024-06-28; bridge 757/758 changed 385 added 1 dropped 0 first 2024-04-01 last 2026-10-21; bridge value -). Not a value difference. Rows whose value moves by more than 1e-9 relative: 61 (Q1 FY25, 2024-04-01 .. 2024-06-28, the 31 May 2024 row appears and the quarter total is spread over one more day: ratio 0.984555296, equal to the bridge min). The bridge counts 385 as changed: the other 324 rows are unchanged in my model even under exact float inequality (same keys: the lake equals the workbook on all 756 common days), so they can only be ulp-level arithmetic noise in the bridge (its ratio max prints 1.000000000). No ADR, parameter or other count is affected.
- `F&O ratio max` (0.9845552963586366; bridge value 1.000000000). Same cause: the bridge max ratio 1.000000000 comes from those noise rows; my changed rows are all Q1 FY25 with ratio 0.984555296.

## Headline (Consolidated)

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| FY 2027 | before 6.083537 / after 6.083537 / d% 0.000000 | before 6.083537 / after 6.083537 / d% +0.0000% | agree | rel 1e-6 | 2.5e-08 |
| Q2 FY 2027 | before 8.967060 / after 8.967060 / d% 0.000000 | before 8.967060 / after 8.967060 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| Q1 FY 2027 | before 8.197926 / after 8.197926 / d% 0.000000 | before 8.197926 / after 8.197926 / d% +0.0000% | agree | print (4 dp) | 1.0e+00 |
| FY 2027 October | before 2.332592 / after 2.332592 / d% 0.000000 | before 2.332592 / after 2.332592 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| FY 2026 | before 7.642700 / after 7.642700 / d% 0.000000 | before 7.642700 / after 7.642700 / d% +0.0000% | agree | rel 1e-6 | 2.5e-09 |

## ADR by period and panel (before, after, delta, delta %)

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| FY 2027, Consolidated | before 6.083537 / after 6.083537 / delta 0.000000 / d% 0.000000 | before 6.083537 / after 6.083537 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 2.5e-08 |
| FY 2027, Broking | before 1.871544 / after 1.871544 / delta 0.000000 / d% 0.000000 | before 1.871544 / after 1.871544 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.0e-07 |
| FY 2027, MTF | before 4.211993 / after 4.211993 / delta 0.000000 / d% 0.000000 | before 4.211993 / after 4.211993 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.0e-08 |
| FY 2027, F&O | before 1.871544 / after 1.871544 / delta 0.000000 / d% 0.000000 | before 1.871544 / after 1.871544 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.0e-07 |
| FY 2027, Cash | before 0.000000 / after 0.000000 / delta 0.000000 / d% - | before 0.000000 / after 0.000000 / delta +0.000000 / d%  | agree | rel 1e-6 | 0.0e+00 |
| FY 2027, Commodities | before 0.000000 / after 0.000000 / delta 0.000000 / d% - | before 0.000000 / after 0.000000 / delta +0.000000 / d%  | agree | rel 1e-6 | 0.0e+00 |
| Q2 FY 2027, Consolidated | before 8.967060 / after 8.967060 / delta 0.000000 / d% 0.000000 | before 8.967060 / after 8.967060 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| Q2 FY 2027, Broking | before 4.247980 / after 4.247980 / delta 0.000000 / d% 0.000000 | before 4.247980 / after 4.247980 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 9.1e-08 |
| Q2 FY 2027, MTF | before 4.719079 / after 4.719079 / delta 0.000000 / d% 0.000000 | before 4.719079 / after 4.719079 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 3.7e-08 |
| Q2 FY 2027, F&O | before 1.694618 / after 1.694618 / delta 0.000000 / d% 0.000000 | before 1.694618 / after 1.694618 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 2.1e-07 |
| Q2 FY 2027, Cash | before 2.031303 / after 2.031303 / delta 0.000000 / d% 0.000000 | before 2.031303 / after 2.031303 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.4e-08 |
| Q2 FY 2027, Commodities | before 0.522060 / after 0.522060 / delta 0.000000 / d% 0.000000 | before 0.522060 / after 0.522060 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 3.2e-07 |
| Q1 FY 2027, Consolidated | before 8.197926 / after 8.197926 / delta 0.000000 / d% 0.000000 | before 8.197926 / after 8.197926 / delta +0.000000 / d% +0.0000% | agree | print (4 dp) | 1.0e+00 |
| Q1 FY 2027, Broking | before 4.544588 / after 4.544588 / delta 0.000000 / d% 0.000000 | before 4.544588 / after 4.544588 / delta +0.000000 / d% +0.0000% | agree | print (4 dp) | 1.0e+00 |
| Q1 FY 2027, MTF | before 3.653339 / after 3.653339 / delta 0.000000 / d% 0.000000 | before 3.653339 / after 3.653339 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 9.6e-08 |
| Q1 FY 2027, F&O | before 1.963321 / after 1.963321 / delta 0.000000 / d% 0.000000 | before 1.963321 / after 1.963321 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.4e-08 |
| Q1 FY 2027, Cash | before 2.060675 / after 2.060675 / delta 0.000000 / d% 0.000000 | before 2.060675 / after 2.060675 / delta +0.000000 / d% +0.0000% | agree | print (4 dp) | 1.0e+00 |
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
| FY 2026, Cash | before 1.880952 / after 1.880952 / delta 0.000000 / d% 0.000000 | before 1.880952 / after 1.880952 / delta +0.000000 / d% +0.0000% | agree | print (4 dp) | 1.0e+00 |
| FY 2026, Commodities | before 0.599053 / after 0.599053 / delta 0.000000 / d% 0.000000 | before 0.599053 / after 0.599053 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 3.9e-07 |
| FY 2027 September, Consolidated | before 9.230728 / after 9.237757 / delta 0.007029 / d% 0.076149 | before 9.230728 / after 9.237757 / delta +0.007029 / d% +0.0761% | agree | print (4 dp) | 6.4e-04 |
| FY 2027 September, Broking | before 4.290353 / after 4.297382 / delta 0.007029 / d% 0.163835 | before 4.290353 / after 4.297382 / delta +0.007029 / d% +0.1638% | agree | print (4 dp) | 2.1e-04 |
| FY 2027 September, MTF | before 4.940375 / after 4.940375 / delta 0.000000 / d% 0.000000 | before 4.940375 / after 4.940375 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 3.2e-08 |
| FY 2027 September, F&O | before 1.704934 / after 1.704934 / delta 0.000000 / d% 0.000000 | before 1.704934 / after 1.704934 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 7.5e-08 |
| FY 2027 September, Cash | before 1.977761 / after 1.984791 / delta 0.007029 / d% 0.355406 | before 1.977761 / after 1.984791 / delta +0.007029 / d% +0.3554% | agree | print (4 dp) | 1.7e-05 |
| FY 2027 September, Commodities | before 0.607658 / after 0.607658 / delta 0.000000 / d% 0.000000 | before 0.607658 / after 0.607658 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 5.5e-07 |
| FY 2027 August, Consolidated | before 8.695724 / after 8.729330 / delta 0.033606 / d% 0.386467 | before 8.695724 / after 8.729330 / delta +0.033606 / d% +0.3865% | agree | print (4 dp) | 8.4e-05 |
| FY 2027 August, Broking | before 3.983725 / after 4.017331 / delta 0.033606 / d% 0.843586 | before 3.983725 / after 4.017331 / delta +0.033606 / d% +0.8436% | agree | print (4 dp) | 1.7e-05 |
| FY 2027 August, MTF | before 4.711999 / after 4.711999 / delta 0.000000 / d% 0.000000 | before 4.711999 / after 4.711999 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.0e-07 |
| FY 2027 August, F&O | before 1.456093 / after 1.456093 / delta 0.000000 / d% 0.000000 | before 1.456093 / after 1.456093 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 2.0e-07 |
| FY 2027 August, Cash | before 2.019779 / after 2.053385 / delta 0.033606 / d% 1.663852 | before 2.019779 / after 2.053385 / delta +0.033606 / d% +1.6639% | agree | print (4 dp) | 2.9e-05 |
| FY 2027 August, Commodities | before 0.507852 / after 0.507852 / delta 0.000000 / d% 0.000000 | before 0.507852 / after 0.507852 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 8.2e-08 |
| FY 2026 September, Consolidated | before 7.806113 / after 7.843211 / delta 0.037098 / d% 0.475244 | before 7.806113 / after 7.843211 / delta +0.037098 / d% +0.4752% | agree | print (4 dp) | 9.2e-05 |
| FY 2026 September, Broking | before 4.072312 / after 4.109410 / delta 0.037098 / d% 0.910983 | before 4.072312 / after 4.109410 / delta +0.037098 / d% +0.9110% | agree | print (4 dp) | 1.8e-05 |
| FY 2026 September, MTF | before 3.733801 / after 3.733801 / delta 0.000000 / d% 0.000000 | before 3.733801 / after 3.733801 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 6.7e-08 |
| FY 2026 September, F&O | before 1.852181 / after 1.852181 / delta 0.000000 / d% 0.000000 | before 1.852181 / after 1.852181 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.6e-07 |
| FY 2026 September, Cash | before 1.699012 / after 1.736110 / delta 0.037098 / d% 2.183509 | before 1.699012 / after 1.736110 / delta +0.037098 / d% +2.1835% | agree | print (4 dp) | 4.1e-06 |
| FY 2026 September, Commodities | before 0.521119 / after 0.521119 / delta 0.000000 / d% 0.000000 | before 0.521119 / after 0.521119 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 5.0e-08 |

## Parameters that moved

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| Cash, 'delivery ratio' H, Q1 FY 2026 | before 2.573030 / after 2.575873 / d% 0.110514 | before 2.5730 / after 2.5759 / d% +0.111% | agree | print (3 dp) | 4.4e-03 |
| Cash, 'delivery ratio' H, Q2 FY 2026 | before 2.654826 / after 2.644795 / d% -0.377834 | before 2.6548 / after 2.6448 / d% -0.378% | agree | print (3 dp) | 4.4e-04 |
| Cash, 'delivery ratio' H, Q3 FY 2026 | before 2.660962 / after 2.664440 / d% 0.130729 | before 2.6610 / after 2.6644 / d% +0.131% | agree | print (3 dp) | 2.1e-03 |
| Cash, 'delivery ratio' H, Q4 FY 2026 | before 2.895925 / after 2.922184 / d% 0.906762 | before 2.8959 / after 2.9222 / d% +0.907% | agree | print (3 dp) | 2.6e-04 |
| Cash, 'delivery ratio' H, Q1 FY 2027 | before 2.778271 / after 2.783979 / d% 0.205478 | before 2.7783 / after 2.7840 / d% +0.205% | agree | print (3 dp) | 2.3e-03 |
| Cash, 'delivery ratio' H, Q2 FY 2027 | before 2.761772 / after 2.750308 / d% -0.415114 | before 2.7618 / after 2.7503 / d% -0.415% | agree | print (3 dp) | 2.7e-04 |
| Cash, 'delivery ratio' H, Q3 FY 2027 | before 2.811989 / after 2.818824 / d% 0.243047 | before 2.8120 / after 2.8188 / d% +0.243% | agree | print (3 dp) | 1.9e-04 |
| Cash, model gross brokerage Rs Cr, Q3 FY 2027 | before 233.808260 / after 221.237185 / d% -5.376660 | before 233.81 / after 221.24 / d% -5.377% | agree | print (3 dp) | 6.3e-05 |
| F&O, gross Rs per contract, Q1 FY 2025 | before 0.749805 / after 0.738224 / d% -1.544470 | before 0.7498 / after 0.7382 / d% -1.544% | agree | print (3 dp) | 3.0e-04 |
| moved parameters: mine = bridge (9 listed) | only mine: []; only bridge: [] |  | agree | exact |  |

## The keys

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| workbook turnover equals the lake on every day before 2025-06-09 (418 days compared) |  |  | agree | exact |  |
| from 2025-06-09 the workbook value of a day is the lake value of two trading days earlier, on all 340 differing days (first 2025-06-09, last 2026-10-21) |  |  | agree | exact |  |
| lake key = lake NSE cash turnover + lake BSE cash turnover on the same date, every calendar equity day (758 days) |  |  | agree | exact |  |
| state ab cash rows use the lake key: every cash row of Q2 FY27 equals ratio x gross x lake K / sum of lake K |  |  | agree | exact |  |
| every equity calendar day has a lake cash row, status ok, non-zero (no gap, no zero in the key) |  |  | agree | exact |  |
| lake index-option + BSE contracts equal the workbook on all 756 common days with a number | [] |  | agree | exact |  |
| differs only on 2024-05-31 (workbook text cell, lake 568768399.0) |  |  | agree | exact |  |
| lake adds one day the workbook lacks: 2023-09-29 |  |  | agree | exact |  |
| 2024-05-31 now carries revenue in F&O (error row in state a, number in state ab) |  |  | agree | exact |  |

## Quarter ties after re-keying

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| fo Q1 FY 2025 (state ab) | 149.579711 | 149.579711 | agree | rel 1e-6 | 5.7e-10 |
| fo Q2 FY 2025 (state ab) | 154.763515 | 154.763515 | agree | rel 1e-6 | 3.2e-09 |
| fo Q3 FY 2025 (state ab) | 134.975013 | 134.975013 | agree | rel 1e-6 | 2.6e-09 |
| fo Q4 FY 2025 (state ab) | 107.123214 | 107.123214 | agree | rel 1e-6 | 4.4e-09 |
| fo Q1 FY 2026 (state ab) | 108.822813 | 108.822813 | agree | rel 1e-6 | 5.6e-10 |
| fo Q2 FY 2026 (state ab) | 111.504138 | 111.504138 | agree | rel 1e-6 | 3.1e-09 |
| fo Q3 FY 2026 (state ab) | 119.868077 | 119.868077 | agree | rel 1e-6 | 1.7e-09 |
| fo Q4 FY 2026 (state ab) | 116.579231 | 116.579231 | agree | rel 1e-6 | 1.8e-10 |
| fo Q1 FY 2027 (state ab) | 117.799255 | 117.799255 | agree | rel 1e-6 | 1.6e-09 |
| fo Q2 FY 2027 (state ab) | 110.150147 | 110.150147 | agree | rel 1e-6 | 2.5e-09 |
| cash Q1 FY 2025 (state ab) | 164.046384 | 164.046384 | agree | rel 1e-6 | 1.5e-09 |
| cash Q2 FY 2025 (state ab) | 193.281803 | 193.281803 | agree | rel 1e-6 | 2.4e-09 |
| cash Q3 FY 2025 (state ab) | 127.951719 | 127.951719 | agree | rel 1e-6 | 2.1e-09 |
| cash Q4 FY 2025 (state ab) | 91.320249 | 91.320249 | agree | rel 1e-6 | 1.9e-09 |
| cash Q1 FY 2026 (state ab) | 149.422872 | 149.422872 | agree | rel 1e-6 | 1.1e-09 |
| cash Q2 FY 2026 (state ab) | 108.615195 | 108.615195 | agree | rel 1e-6 | 3.0e-09 |
| cash Q3 FY 2026 (state ab) | 104.706628 | 104.706628 | agree | rel 1e-6 | 9.5e-10 |
| cash Q4 FY 2026 (state ab) | 101.850330 | 101.850330 | agree | rel 1e-6 | 2.6e-09 |
| cash Q1 FY 2027 (state ab) | 123.640509 | 123.640509 | agree | rel 1e-6 | 1.8e-09 |
| cash Q2 FY 2027 (state ab) | 132.034689 | 132.034689 | agree | rel 1e-6 | 1.3e-09 |

## Daily revenue rows that changed

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| F&O counts / dates | mine 757/758 changed 61 added 1 dropped 0 first 2024-04-01 last 2024-06-28; bridge 757/758 changed 385 added 1 dropped 0 first 2024-04-01 last 2026-10-21 |  | **DIFFER** | differ |  |
| F&O ratio min | 0.984555 | 0.984555296 | agree | rel 1e-6 | 3.6e-10 |
| F&O ratio max | 0.984555 | 1.000000000 | **DIFFER** | differ | 1.5e-02 |
| Cash counts / dates | mine 634/634 changed 372 added 0 dropped 0 first 2025-04-01 last 2026-09-30; bridge 634/634 changed 372 added 0 dropped 0 first 2025-04-01 last 2026-09-30 |  | agree | exact |  |
| Cash ratio min | 0.186455 | 0.186454599 | agree | rel 1e-6 | 2.5e-09 |
| Cash ratio max | 4.306999 | 4.306998593 | agree | rel 1e-6 | 5.4e-11 |
| Commodities counts / dates | mine 653/653 changed 0 added 0 dropped 0 first  last ; bridge 653/653 changed 0 added 0 dropped 0 first  last  |  | agree | exact |  |
| Commodities ratio min | - |  | agree | blank |  |
| Commodities ratio max | - |  | agree | blank |  |
| MTF counts / dates | mine 495/495 changed 0 added 0 dropped 0 first  last ; bridge 495/495 changed 0 added 0 dropped 0 first  last  |  | agree | exact |  |
| MTF ratio min | - |  | agree | blank |  |
| MTF ratio max | - |  | agree | blank |  |

