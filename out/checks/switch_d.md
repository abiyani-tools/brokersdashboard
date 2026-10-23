# Check - switch (d), revised rule: drop special sessions from trading segments only

Independent recompute, 23 Oct 2026, without `src/engine/` or `src/live/`. Script: `out/checks/switch_d_check.py` (`python3 -I`, stdlib only).
Reads `snapshot/db_snapshot_2026-10-23.json`, plus `facts_reviewed_2026-10-23.json` for the reviewed revenue-mix values behind switch (b). That is unchanged from the earlier check, and (b) cannot be rebuilt from the snapshot alone.

**Result: 34 checks, 34 agree (max rel diff 2.9e-7, which is 6-dp rounding of the claims). No disagreements.**

## What changed vs the earlier check
- (d) applies to F&O, cash and commodity only. MTF is averaged over all dates in both before and after, so MTF is identical before and after.
- Calendar special sessions are now 2023-11-12, 2024-03-02, 2024-05-18, 2024-11-01, 2025-02-01 (budget), 2025-10-21.
- In the daily series: 2024-11-01, 2025-02-01 and 2025-10-21 (all four segments). Only 2025-10-21 falls in a claimed period.
- 2025-02-01 is FY 2025 / Q4 FY 2025 / FY 2025 February. It touches none of the claimed periods (confirmed; the script prints the special dates found in each period: only 2025-10-21).

## Method
- Daily values: `parity_expected` `fo_rev_mn|`, `cash_rev_mn|`, `comm_rev_mn|` (Rs Mn, /10 -> Rs cr), `mtf_gross_cr|` (Rs cr).
- Before = a+b+c: commodity x 36/35 (a) and x 0.061/0.06 (b); F&O Q3 FY26 x 381/380 (a); per-quarter take-rate ratios (b) for F&O and cash;
  (c) F&O x (NSE+BSE real)/(NSE+18,962,859) on the 2026-09-29..10-21 dates only. MTF untouched.
- Average = mean over the period's dates (commodity includes zero days). Consolidated = F&O + Cash + Comm + MTF.
- After = same, but the special-session dates are dropped from F&O, cash and commodity.

## Day counts (F&O/cash; comm; MTF), before -> after
FY 2026 247 -> 246 (comm 257 -> 256; MTF 247 -> 247). Q3 FY 2026 62 -> 61 (comm 64 -> 63; MTF 62). FY 2026 October 21 -> 20 (comm 22 -> 21; MTF 21).

## Results (Rs cr per trading day; all AGREE; mine unrounded)
| Period | Segment | Mine before | Mine after | Claim before -> after |
|---|---|---|---|---|
| FY 2026 | F&O | 9.513241390 | 9.547485020 | 9.513241 -> 9.547485 |
| FY 2026 | Cash | 1.709085761 | 1.713904408 | 1.709086 -> 1.713904 |
| FY 2026 | Comm | 1.216052747 | 1.220378645 | 1.216053 -> 1.220379 |
| FY 2026 | MTF | 3.117216972 | 3.117216972 | 3.117217 -> 3.117217 |
| FY 2026 | Consolidated | 15.555596870 | 15.598985046 | 15.555597 -> 15.598985 |
| Q3 FY 2026 | F&O | 9.559821518 | 9.698682389 | 9.559822 -> 9.698682 |
| Q3 FY 2026 | Cash | 1.661333371 | 1.679983120 | 1.661333 -> 1.679983 |
| Q3 FY 2026 | Comm | 1.275227320 | 1.293744853 | 1.275227 -> 1.293745 |
| Q3 FY 2026 | MTF | 3.449134382 | 3.449134382 | 3.449134 -> 3.449134 |
| Q3 FY 2026 | Consolidated | 15.945516591 | 16.121544744 | 15.945517 -> 16.121545 |
| FY 2026 October | F&O | 9.933100923 | 10.375290552 | 9.933101 -> 10.375291 |
| FY 2026 October | Cash | 1.684168126 | 1.742191597 | 1.684168 -> 1.742192 |
| FY 2026 October | Comm | 1.305592272 | 1.362590821 | 1.305592 -> 1.362591 |
| FY 2026 October | MTF | 3.371098956 | 3.371098956 | 3.371099 -> 3.371099 |
| FY 2026 October | Consolidated | 16.293960277 | 16.851171925 | 16.293960 -> 16.851172 |

FY 2027, Q2 FY 2027, FY 2027 October: before == after exactly for every segment (consolidated 17.608086, 16.678121, 20.531603).
Tolerance: rel <= 1e-6, or abs <= 5.5e-7 (half-ulp of the 6-dp table).
