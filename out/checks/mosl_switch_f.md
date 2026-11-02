# MOSL switch m-f: independent recompute

Script: `out/checks/mosl_switch_f_check.py` (+ `mosl_common.py`), Python standard library only; inputs read with `git show 990eb5d:<path>` (`snapshot/mosl_snapshot_2026-10-23.json` carries the typed yields and the new `mtf_nii_yield_carry` row; reviewed facts carry the disclosed MTF book; industry book from the db snapshot). Nothing under `src/engine/` or `src/live/` was read. Bridge: `out/bridges/mosl_f.md`.

Before = my state a+b+c+d+e, after = a+b+c+d+e+f. MTF revenue = share x industry daily book x yield / 247, share = disclosed closing book / industry book on the quarter's last day with a book (m-a supplies Q2 FY27: 9,600 / 151,133.98 = 6.35%), yield = the workbook's typed value for Q1 FY25 - Q1 FY27 and the 12.94% carry for Q2 and Q3 FY27. The bridge has no "Parameters that moved" table; I check that no parameter of any segment moves between my states e and f.

**Result: 76/76 items agree** (76 to 1e-6 relative or exact; 0 only to the bridge print precision).

ADR before / after values in the bridge table (60 numbers, printed to 6 decimals): max absolute difference 4.85e-07 Cr, max relative difference 6.73e-07 (a 6-decimal print can only resolve 5e-7 Cr).

| Item kind | Checked | Agree | Agree at 1e-6 / exact |
|---|---:|---:|---:|
| ADR | 30 | 30 | 30 |
| Consolidated headline | 5 | 5 | 5 |
| param set | 1 | 1 | 1 |
| daily rows | 12 | 12 | 12 |
| yield | 7 | 7 | 7 |
| mtf book | 12 | 12 | 12 |
| info | 9 | 9 | 9 |

## Headline (Consolidated)

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| FY 2027 | before 8.718295 / after 8.718295 / d% 0.000000 | before 8.718295 / after 8.718295 / d% +0.0000% | agree | rel 1e-6 | 3.9e-08 |
| Q2 FY 2027 | before 8.967060 / after 8.967060 / d% 0.000000 | before 8.967060 / after 8.967060 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| Q1 FY 2027 | before 8.197926 / after 8.197926 / d% 0.000000 | before 8.197926 / after 8.197926 / d% +0.0000% | agree | rel 1e-6 | 5.9e-08 |
| FY 2027 October | before 9.876513 / after 9.876513 / d% 0.000000 | before 9.876513 / after 9.876513 / d% +0.0000% | agree | rel 1e-6 | 3.4e-08 |
| FY 2026 | before 7.662290 / after 7.662290 / d% 0.000000 | before 7.662290 / after 7.662290 / d% +0.0000% | agree | rel 1e-6 | 1.5e-08 |

## ADR by period and panel

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| FY 2027, Consolidated | before 8.718295 / after 8.718295 / delta 0.000000 / d% 0.000000 | before 8.718295 / after 8.718295 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 3.9e-08 |
| FY 2027, Broking | before 4.440500 / after 4.440500 / delta 0.000000 / d% 0.000000 | before 4.440500 / after 4.440500 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 9.3e-08 |
| FY 2027, MTF | before 4.277794 / after 4.277794 / delta 0.000000 / d% 0.000000 | before 4.277794 / after 4.277794 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 5.7e-08 |
| FY 2027, F&O | before 1.871544 / after 1.871544 / delta 0.000000 / d% 0.000000 | before 1.871544 / after 1.871544 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.0e-07 |
| FY 2027, Cash | before 2.035185 / after 2.035185 / delta 0.000000 / d% 0.000000 | before 2.035185 / after 2.035185 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 2.1e-07 |
| FY 2027, Commodities | before 0.533771 / after 0.533771 / delta 0.000000 / d% 0.000000 | before 0.533771 / after 0.533771 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.1e-07 |
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
| FY 2027 October, Consolidated | before 9.876513 / after 9.876513 / delta 0.000000 / d% 0.000000 | before 9.876513 / after 9.876513 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 3.4e-08 |
| FY 2027 October, Broking | before 4.918772 / after 4.918772 / delta 0.000000 / d% 0.000000 | before 4.918772 / after 4.918772 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.5e-08 |
| FY 2027 October, MTF | before 4.957741 / after 4.957741 / delta 0.000000 / d% 0.000000 | before 4.957741 / after 4.957741 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 2.3e-08 |
| FY 2027 October, F&O | before 2.332592 / after 2.332592 / delta 0.000000 / d% 0.000000 | before 2.332592 / after 2.332592 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| FY 2027 October, Cash | before 1.936953 / after 1.936953 / delta 0.000000 / d% 0.000000 | before 1.936953 / after 1.936953 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.2e-07 |
| FY 2027 October, Commodities | before 0.649226 / after 0.649226 / delta 0.000000 / d% 0.000000 | before 0.649226 / after 0.649226 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 6.7e-07 |
| FY 2026, Consolidated | before 7.662290 / after 7.662290 / delta 0.000000 / d% 0.000000 | before 7.662290 / after 7.662290 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.5e-08 |
| FY 2026, Broking | before 4.348883 / after 4.348883 / delta 0.000000 / d% 0.000000 | before 4.348883 / after 4.348883 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 7.2e-08 |
| FY 2026, MTF | before 3.313407 / after 3.313407 / delta 0.000000 / d% 0.000000 | before 3.313407 / after 3.313407 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 5.9e-08 |
| FY 2026, F&O | before 1.857828 / after 1.857828 / delta 0.000000 / d% 0.000000 | before 1.857828 / after 1.857828 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.1e-09 |
| FY 2026, Cash | before 1.888062 / after 1.888062 / delta 0.000000 / d% 0.000000 | before 1.888062 / after 1.888062 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 3.9e-08 |
| FY 2026, Commodities | before 0.602993 / after 0.602993 / delta 0.000000 / d% 0.000000 | before 0.602993 / after 0.602993 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 6.4e-07 |

## Yields

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| moved parameters: mine = bridge (0 listed) | only mine: []; only bridge: [] |  | agree | exact |  |
| nine typed yields Q1 FY25 - Q1 FY27 kept: 0.1192, 0.1326, 0.1373, 0.1448, 0.1451, 0.1548, 0.1454, 0.1306, 0.1294 |  |  | agree | exact |  |
| typed yields lie in the 11.9% - 15.5% band of the workbook (Methodology 2b): min 0.1192 max 0.1548 |  |  | agree | exact |  |
| carry assumption row mtf_nii_yield_carry = 0.12938330773959208 = 12.94% (rounded), equal to the last typed Q1 FY27 yield 0.12938330773959208 |  |  | agree | exact |  |
| carry row is labelled: note starts "[SOURCE NEEDED: MOSL does not publish an MTF yield]", source_ref names assumptions!F14 |  |  | agree | exact |  |
| Q2 FY27 (now reported) and Q3 FY27 (open) both use the carry: 0.129383 / 0.129383 |  |  | agree | exact |  |
| no number moves: m-f only turns the workbook's unlabelled F15 = F14 into the labelled row (all rows of every segment identical to state e) |  |  | agree | exact |  |
| day basis stays 247 (assumption row mtf_day_basis = 247; FY26 has 247 equity days in the calendar, FY27 will differ) |  |  | agree | exact |  |

## MTF share from the disclosed book

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| Q3 FY 2025: disclosed book 4961 Cr / industry 82835.99 Cr (2024-12-31) = 0.05989 = the workbook's share |  |  | agree | exact |  |
| Q4 FY 2025: disclosed book 4081 Cr / industry 68069.53 Cr (2025-03-28) = 0.05995 = the workbook's share |  |  | agree | exact |  |
| Q1 FY 2026: disclosed book 5042 Cr / industry 84645.85 Cr (2025-06-30) = 0.05957 = the workbook's share |  |  | agree | exact |  |
| Q2 FY 2026: disclosed book 6147 Cr / industry 99445.95 Cr (2025-09-30) = 0.06181 = the workbook's share |  |  | agree | exact |  |
| Q3 FY 2026: disclosed book 6543 Cr / industry 113898.69 Cr (2025-12-31) = 0.05745 = the workbook's share |  |  | agree | exact |  |
| Q4 FY 2026: disclosed book 5757 Cr / industry 105919.61 Cr (2026-03-30) = 0.05435 = the workbook's share |  |  | agree | exact |  |
| Q1 FY 2027: disclosed book 7800 Cr / industry 135044.20 Cr (2026-06-30) = 0.05776 = the workbook's share |  |  | agree | exact |  |
| Q2 FY 2027: disclosed book 9600 Cr / industry 151133.98 Cr (2026-09-30) = 0.06352 (the workbook carried 0.05776) |  |  | agree | exact |  |
| MTF daily rows Q3 FY25 - Q1 FY27 equal the workbook's cached rows (max rel diff 3.7e-16): typed yields and book shares kept |  |  | agree | exact |  |
| MTF daily rows Q2 FY27 vs the workbook: ratio new share / carried share over 65 days (bridge m-a MTF ratio min) | 1.099741 | 1.099741078 | agree | rel 1e-6 | 4.0e-10 |
| same ratio, max (bridge m-a MTF ratio max) | 1.099741 | 1.099741078 | agree | rel 1e-6 | 4.0e-10 |
| Q2 FY27 MTF ratio is one number for all 65 days (spread 6.7e-16) |  |  | agree | exact |  |

## MTF ADR by reported quarter (information)

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| MTF ADR Q3 FY 2025 = 2.640826 Cr over 62 days (share 0.05989 x yield 0.13726 / 247 x book) |  |  | agree | exact |  |
| MTF ADR Q4 FY 2025 = 2.654670 Cr over 62 days (share 0.05995 x yield 0.14478 / 247 x book) |  |  | agree | exact |  |
| MTF ADR Q1 FY 2026 = 2.621197 Cr over 61 days (share 0.05957 x yield 0.14515 / 247 x book) |  |  | agree | exact |  |
| MTF ADR Q2 FY 2026 = 3.582451 Cr over 64 days (share 0.06181 x yield 0.15483 / 247 x book) |  |  | agree | exact |  |
| MTF ADR Q3 FY 2026 = 3.747215 Cr over 62 days (share 0.05745 x yield 0.14538 / 247 x book) |  |  | agree | exact |  |
| MTF ADR Q4 FY 2026 = 3.281906 Cr over 60 days (share 0.05435 x yield 0.13063 / 247 x book) |  |  | agree | exact |  |
| MTF ADR Q1 FY 2027 = 3.653339 Cr over 59 days (share 0.05776 x yield 0.12938 / 247 x book) |  |  | agree | exact |  |
| MTF ADR Q2 FY 2027 = 4.719079 Cr over 65 days (share 0.06352 x yield 0.12938 / 247 x book) |  |  | agree | exact |  |
| MTF ADR Q3 FY 2027 = 4.957741 Cr over 12 days (share 0.06352 x yield 0.12938 / 247 x book) |  |  | agree | exact |  |

## Daily revenue rows that changed

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| F&O counts / dates | mine 634/634 changed 0 added 0 dropped 0 first  last ; bridge 634/634 changed 0 added 0 dropped 0 first  last  |  | agree | exact |  |
| F&O ratio min | - |  | agree | blank |  |
| F&O ratio max | - |  | agree | blank |  |
| Cash counts / dates | mine 634/634 changed 0 added 0 dropped 0 first  last ; bridge 634/634 changed 0 added 0 dropped 0 first  last  |  | agree | exact |  |
| Cash ratio min | - |  | agree | blank |  |
| Cash ratio max | - |  | agree | blank |  |
| Commodities counts / dates | mine 660/660 changed 0 added 0 dropped 0 first  last ; bridge 660/660 changed 0 added 0 dropped 0 first  last  |  | agree | exact |  |
| Commodities ratio min | - |  | agree | blank |  |
| Commodities ratio max | - |  | agree | blank |  |
| MTF counts / dates | mine 507/507 changed 0 added 0 dropped 0 first  last ; bridge 507/507 changed 0 added 0 dropped 0 first  last  |  | agree | exact |  |
| MTF ratio min | - |  | agree | blank |  |
| MTF ratio max | - |  | agree | blank |  |

