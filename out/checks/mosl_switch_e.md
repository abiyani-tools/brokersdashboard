# MOSL switch m-e: independent recompute

Script: `out/checks/mosl_switch_e_check.py` (+ `mosl_common.py`), Python standard library only; inputs read with `git show 990eb5d:<path>`. Nothing under `src/engine/` or `src/live/` was read. Bridge: `out/bridges/mosl_e.md`.

Before = my state a+b+c+d, after = a+b+c+d+e. Open quarter Q3 FY27 (1-21 Oct 2026): F&O, cash, commodities earn the last reported quarter's (Q2 FY27) net revenue per unit of their key (per index-option + BSE contract, per Rs Cr of NSE + BSE turnover, per MCX contract) x that day's key; each carries Q2 FY27's net / gross. MTF carries the Q2 FY27 quarter-end share (9,600 / industry book on 30 Sep) and the 12.94% yield, and its rows run to the last day with an industry book (19 Oct). I implemented the F&O rule both ways (workbook carry of share, rate and ratio, and net per contract) and they agree to 1e-12, which is why the F&O column does not move.

**Result: 102/102 items agree** (88 to 1e-6 relative or exact; 14 only to the bridge print precision).

ADR before / after values in the bridge table (60 numbers, printed to 6 decimals): max absolute difference 4.85e-07 Cr, max relative difference 6.73e-07 (a 6-decimal print can only resolve 5e-7 Cr).

| Item kind | Checked | Agree | Agree at 1e-6 / exact |
|---|---:|---:|---:|
| ADR | 30 | 30 | 25 |
| Consolidated headline | 5 | 5 | 4 |
| param | 11 | 11 | 3 |
| param set | 1 | 1 | 1 |
| daily rows | 12 | 12 | 12 |
| rule | 13 | 13 | 13 |
| tie to data book | 30 | 30 | 30 |

## Headline (Consolidated)

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| FY 2027 | before 8.650276 / after 8.718295 / d% 0.786320 | before 8.650276 / after 8.718295 / d% +0.7863% | agree | print (4 dp) | 2.5e-05 |
| Q2 FY 2027 | before 8.967060 / after 8.967060 / d% 0.000000 | before 8.967060 / after 8.967060 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| Q1 FY 2027 | before 8.197926 / after 8.197926 / d% 0.000000 | before 8.197926 / after 8.197926 / d% +0.0000% | agree | rel 1e-6 | 5.9e-08 |
| FY 2027 October | before 2.332592 / after 9.876513 / d% 323.413618 | before 2.332592 / after 9.876513 / d% +323.4136% | agree | rel 1e-6 | 5.6e-08 |
| FY 2026 | before 7.662290 / after 7.662290 / d% 0.000000 | before 7.662290 / after 7.662290 / d% +0.0000% | agree | rel 1e-6 | 1.5e-08 |

## ADR by period and panel

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| FY 2027, Consolidated | before 8.650276 / after 8.718295 / delta 0.068019 / d% 0.786320 | before 8.650276 / after 8.718295 / delta +0.068019 / d% +0.7863% | agree | print (4 dp) | 2.5e-05 |
| FY 2027, Broking | before 4.438283 / after 4.440500 / delta 0.002218 / d% 0.049964 | before 4.438283 / after 4.440500 / delta +0.002218 / d% +0.0500% | agree | print (4 dp) | 7.2e-04 |
| FY 2027, MTF | before 4.211993 / after 4.277794 / delta 0.065801 / d% 1.562236 | before 4.211993 / after 4.277794 / delta +0.065801 / d% +1.5622% | agree | print (4 dp) | 2.3e-05 |
| FY 2027, F&O | before 1.871544 / after 1.871544 / delta 0.000000 / d% 0.000000 | before 1.871544 / after 1.871544 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.0e-07 |
| FY 2027, Cash | before 2.045402 / after 2.035185 / delta -0.010216 / d% -0.499469 | before 2.045402 / after 2.035185 / delta -0.010216 / d% -0.4995% | agree | print (4 dp) | 6.2e-05 |
| FY 2027, Commodities | before 0.521337 / after 0.533771 / delta 0.012434 / d% 2.384961 | before 0.521337 / after 0.533771 / delta +0.012434 / d% +2.3850% | agree | print (4 dp) | 2.5e-05 |
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
| FY 2027 October, Consolidated | before 2.332592 / after 9.876513 / delta 7.543921 / d% 323.413618 | before 2.332592 / after 9.876513 / delta +7.543921 / d% +323.4136% | agree | rel 1e-6 | 6.0e-08 |
| FY 2027 October, Broking | before 2.332592 / after 4.918772 / delta 2.586180 / d% 110.871491 | before 2.332592 / after 4.918772 / delta +2.586180 / d% +110.8715% | agree | rel 1e-6 | 1.3e-07 |
| FY 2027 October, MTF | before 0.000000 / after 4.957741 / delta 4.957741 / d% - | before 0.000000 / after 4.957741 / delta +4.957741 / d%  | agree | rel 1e-6 | 2.3e-08 |
| FY 2027 October, F&O | before 2.332592 / after 2.332592 / delta 0.000000 / d% 0.000000 | before 2.332592 / after 2.332592 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 4.9e-08 |
| FY 2027 October, Cash | before 0.000000 / after 1.936953 / delta 1.936953 / d% - | before 0.000000 / after 1.936953 / delta +1.936953 / d%  | agree | rel 1e-6 | 1.2e-07 |
| FY 2027 October, Commodities | before 0.000000 / after 0.649226 / delta 0.649226 / d% - | before 0.000000 / after 0.649226 / delta +0.649226 / d%  | agree | rel 1e-6 | 6.7e-07 |
| FY 2026, Consolidated | before 7.662290 / after 7.662290 / delta 0.000000 / d% 0.000000 | before 7.662290 / after 7.662290 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.5e-08 |
| FY 2026, Broking | before 4.348883 / after 4.348883 / delta 0.000000 / d% 0.000000 | before 4.348883 / after 4.348883 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 7.2e-08 |
| FY 2026, MTF | before 3.313407 / after 3.313407 / delta 0.000000 / d% 0.000000 | before 3.313407 / after 3.313407 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 5.9e-08 |
| FY 2026, F&O | before 1.857828 / after 1.857828 / delta 0.000000 / d% 0.000000 | before 1.857828 / after 1.857828 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 1.1e-09 |
| FY 2026, Cash | before 1.888062 / after 1.888062 / delta 0.000000 / d% 0.000000 | before 1.888062 / after 1.888062 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 3.9e-08 |
| FY 2026, Commodities | before 0.602993 / after 0.602993 / delta 0.000000 / d% 0.000000 | before 0.602993 / after 0.602993 / delta +0.000000 / d% +0.0000% | agree | rel 1e-6 | 6.4e-07 |

## Parameters that moved

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| Cash, 'delivery ratio' H, Q3 FY 2027 | before 2.818824 / after - / d% - | before 2.8188 / after — / d%  | agree | print (4 dp) | 8.4e-06 |
| Cash, gross per Rs of reported ADTO J, Q3 FY 2027 | before 0.063638 / after - / d% - | before 0.0636 / after — / d%  | agree | print (4 dp) | 5.9e-04 |
| Cash, model gross brokerage Rs Cr, Q3 FY 2027 | before - / after 45.349735 / d% - | before — / after 45.3497 / d%  | agree | rel 1e-6 | 7.8e-07 |
| Cash, model net brokerage Rs Cr, Q3 FY 2027 | before - / after 25.180392 / d% - | before — / after 25.1804 / d%  | agree | rel 1e-6 | 3.2e-07 |
| Cash, net / gross, Q3 FY 2027 | before - / after 0.555249 / d% - | before — / after 0.5552 / d%  | agree | print (4 dp) | 8.8e-05 |
| Cash, share (cancels), Q3 FY 2027 | before 0.079747 / after - / d% - | before 0.0797 / after — / d%  | agree | print (4 dp) | 5.9e-04 |
| Commodities, gross Rs per MOSL contract, Q3 FY 2027 | before - / after 5.441486 / d% - | before — / after 5.4415 / d%  | agree | print (4 dp) | 2.6e-06 |
| Commodities, model gross brokerage Rs Cr, Q3 FY 2027 | before - / after 15.291603 / d% - | before — / after 15.2916 / d%  | agree | rel 1e-6 | 2.1e-07 |
| Commodities, model net brokerage Rs Cr, Q3 FY 2027 | before - / after 9.089170 / d% - | before — / after 9.0892 / d%  | agree | print (4 dp) | 3.3e-06 |
| Commodities, net / gross, Q3 FY 2027 | before - / after 0.594390 / d% - | before — / after 0.5944 / d%  | agree | print (4 dp) | 1.7e-05 |
| Commodities, share, Q3 FY 2027 | before - / after 0.078503 / d% - | before — / after 0.0785 / d%  | agree | print (4 dp) | 3.3e-05 |
| moved parameters: mine = bridge (11 listed) | only mine: []; only bridge: [] |  | agree | exact |  |

## The estimate rule

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| fo: each of the 13 Q3 FY27 days = 6.751634e-09 Rs Cr per index-option + BSE contract x that day's key (net 110.1501 Cr over 65 Q2 days) |  |  | agree | exact |  |
| fo: Q3 FY27 net / gross carried from Q2 FY27 = 0.5845 |  |  | agree | exact |  |
| cash: each of the 13 Q3 FY27 days = 1.576230e-05 Rs Cr per Rs Cr of NSE + BSE turnover x that day's key (net 132.0347 Cr over 65 Q2 days) |  |  | agree | exact |  |
| cash: Q3 FY27 net / gross carried from Q2 FY27 = 0.5552 |  |  | agree | exact |  |
| comm: each of the 14 Q3 FY27 days = 2.539060e-08 Rs Cr per MCX contract x that day's key (net 34.4559 Cr over 66 Q2 days) |  |  | agree | exact |  |
| comm: Q3 FY27 net / gross carried from Q2 FY27 = 0.5944 |  |  | agree | exact |  |
| days in the open quarter: F&O 13, cash 13, commodities 14, MTF 12 (bridge: 13 / 13 / 14 / 12; MTF stops with the industry book on 2026-10-19) |  |  | agree | exact |  |
| MTF share carried from the last reported quarter-end: 9600 Cr / industry 151133.98 Cr on 2026-09-30 = 0.06352 (6.35%) |  |  | agree | exact |  |
| MTF yield carried: Q3 FY27 0.129383 = Q1 FY27 typed 0.129383 |  |  | agree | exact |  |
| MTF 2026-10-19 = 4.943314 Cr = share x book 148568.87 x yield / 247 |  |  | agree | exact |  |
| Cash net per day: Q3 1.9370 vs Q2 2.0313 Cr (same order: the day count is no longer 5x) |  |  | agree | exact |  |
| F&O net per day: Q3 2.3326 vs Q2 1.6946 Cr (same order: the day count is no longer 5x) |  |  | agree | exact |  |
| Commodities net per day: Q3 0.6492 vs Q2 0.5221 Cr (same order: the day count is no longer 5x) |  |  | agree | exact |  |

## Quarter ties (state abcde)

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| fo Q1 FY 2025 (state abcde) | 149.579711 | 149.579711 | agree | rel 1e-6 | 5.7e-10 |
| fo Q2 FY 2025 (state abcde) | 154.763515 | 154.763515 | agree | rel 1e-6 | 3.2e-09 |
| fo Q3 FY 2025 (state abcde) | 134.975013 | 134.975013 | agree | rel 1e-6 | 2.6e-09 |
| fo Q4 FY 2025 (state abcde) | 107.123214 | 107.123214 | agree | rel 1e-6 | 4.4e-09 |
| fo Q1 FY 2026 (state abcde) | 108.822813 | 108.822813 | agree | rel 1e-6 | 5.6e-10 |
| fo Q2 FY 2026 (state abcde) | 111.504138 | 111.504138 | agree | rel 1e-6 | 3.1e-09 |
| fo Q3 FY 2026 (state abcde) | 119.868077 | 119.868077 | agree | rel 1e-6 | 1.7e-09 |
| fo Q4 FY 2026 (state abcde) | 116.579231 | 116.579231 | agree | rel 1e-6 | 1.8e-10 |
| fo Q1 FY 2027 (state abcde) | 117.799255 | 117.799255 | agree | rel 1e-6 | 1.6e-09 |
| fo Q2 FY 2027 (state abcde) | 110.150147 | 110.150147 | agree | rel 1e-6 | 2.5e-09 |
| cash Q1 FY 2025 (state abcde) | 164.046384 | 164.046384 | agree | rel 1e-6 | 1.5e-09 |
| cash Q2 FY 2025 (state abcde) | 193.281803 | 193.281803 | agree | rel 1e-6 | 2.4e-09 |
| cash Q3 FY 2025 (state abcde) | 127.951719 | 127.951719 | agree | rel 1e-6 | 2.1e-09 |
| cash Q4 FY 2025 (state abcde) | 91.320249 | 91.320249 | agree | rel 1e-6 | 1.9e-09 |
| cash Q1 FY 2026 (state abcde) | 149.422872 | 149.422872 | agree | rel 1e-6 | 1.1e-09 |
| cash Q2 FY 2026 (state abcde) | 108.615195 | 108.615195 | agree | rel 1e-6 | 3.0e-09 |
| cash Q3 FY 2026 (state abcde) | 104.706628 | 104.706628 | agree | rel 1e-6 | 9.5e-10 |
| cash Q4 FY 2026 (state abcde) | 101.850330 | 101.850330 | agree | rel 1e-6 | 2.6e-09 |
| cash Q1 FY 2027 (state abcde) | 123.640509 | 123.640509 | agree | rel 1e-6 | 1.8e-09 |
| cash Q2 FY 2027 (state abcde) | 132.034689 | 132.034689 | agree | rel 1e-6 | 1.3e-09 |
| comm Q1 FY 2025 (state abcde) | 20.069437 | 20.069437 | agree | rel 1e-6 | 2.1e-08 |
| comm Q2 FY 2025 (state abcde) | 23.392304 | 23.392304 | agree | rel 1e-6 | 1.3e-09 |
| comm Q3 FY 2025 (state abcde) | 25.031958 | 25.031958 | agree | rel 1e-6 | 8.1e-09 |
| comm Q4 FY 2025 (state abcde) | 25.296819 | 25.296819 | agree | rel 1e-6 | 8.2e-09 |
| comm Q1 FY 2026 (state abcde) | 27.797930 | 27.797930 | agree | rel 1e-6 | 1.7e-08 |
| comm Q2 FY 2026 (state abcde) | 28.849019 | 28.849019 | agree | rel 1e-6 | 6.2e-09 |
| comm Q3 FY 2026 (state abcde) | 46.436481 | 46.436481 | agree | rel 1e-6 | 4.7e-09 |
| comm Q4 FY 2026 (state abcde) | 50.873132 | 50.873132 | agree | rel 1e-6 | 2.9e-09 |
| comm Q1 FY 2027 (state abcde) | 33.317873 | 33.317873 | agree | rel 1e-6 | 4.1e-09 |
| comm Q2 FY 2027 (state abcde) | 34.455949 | 34.455949 | agree | rel 1e-6 | 2.2e-09 |

## Daily revenue rows that changed

| Item | Mine | Bridge | Verdict | Criterion | Max rel diff |
|---|---|---|---|---|---|
| F&O counts / dates | mine 634/634 changed 0 added 0 dropped 0 first  last ; bridge 634/634 changed 0 added 0 dropped 0 first  last  |  | agree | exact |  |
| F&O ratio min | - |  | agree | blank |  |
| F&O ratio max | - |  | agree | blank |  |
| Cash counts / dates | mine 621/634 changed 0 added 13 dropped 0 first  last ; bridge 621/634 changed 0 added 13 dropped 0 first  last  |  | agree | exact |  |
| Cash ratio min | - |  | agree | blank |  |
| Cash ratio max | - |  | agree | blank |  |
| Commodities counts / dates | mine 646/660 changed 0 added 14 dropped 0 first  last ; bridge 646/660 changed 0 added 14 dropped 0 first  last  |  | agree | exact |  |
| Commodities ratio min | - |  | agree | blank |  |
| Commodities ratio max | - |  | agree | blank |  |
| MTF counts / dates | mine 495/507 changed 0 added 12 dropped 0 first  last ; bridge 495/507 changed 0 added 12 dropped 0 first  last  |  | agree | exact |  |
| MTF ratio min | - |  | agree | blank |  |
| MTF ratio max | - |  | agree | blank |  |

