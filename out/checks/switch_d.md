# Check - switch (d): drop special sessions from period averages

Independent recompute, 23 Oct 2026, without `src/engine/` or `src/live/`. Script: `out/checks/switch_d_check.py`
(`python3 -I`; reads only `snapshot/db_snapshot_2026-10-23.json` and `facts_reviewed_2026-10-23.json`).

**Result: 33 checks, 33 agree (max rel diff 2.9e-7, which is 6-dp rounding of the claims). No disagreements.**

## Method
- Daily values: `parity_expected` `fo_rev_mn|`, `cash_rev_mn|`, `comm_rev_mn|` (Rs Mn, /10 -> Rs cr), `mtf_gross_cr|` (Rs cr).
- Before = switches a+b+c as in switch_a/b/c checks: commodity x 36/35 (a) and x 0.061/0.06 (b); F&O Q3 FY26 x 381/380 (a), per-quarter
  take-rate ratios (b) for F&O and cash; (c) F&O x (NSE+BSE real)/(NSE+18,962,859) on 2026-09-29..10-21 only. MTF untouched.
- Special sessions = `calendar.special_session` non-null: 2023-11-12, 2024-03-02, 2024-05-18, 2024-11-01, 2025-10-21.
  Only 2024-11-01 and 2025-10-21 are in the daily series (present for all four segments, including commodity and MTF).
- Average = mean over the period's dates (commodity includes zero days), with and without those dates. Consolidated = F&O+Cash+Comm+MTF averages.

## Day counts (F&O/cash/MTF; commodity), before -> after
FY 2026 247 -> 246 (comm 257 -> 256); Q3 FY 2026 62 -> 61 (comm 64 -> 63); FY 2026 October 21 -> 20 (comm 22 -> 21).
Each period loses exactly 2025-10-21 only; 2024-11-01 is in FY 2025, so no period claimed here is touched by it.

## Results (Rs cr per trading day; all AGREE)
Full per-figure output (mine unrounded vs claim, rel diff) is printed by the script. Examples:
| Figure | Mine before | Mine after | Claim |
|---|---|---|---|
| FY26 Consolidated | 15.555596870 | 15.597885083 | 15.555597 -> 15.597885 |
| FY26 MTF | 3.117216972 | 3.116117010 | 3.117217 -> 3.116117 |
| Q3 FY26 F&O | 9.559821518 | 9.698682389 | 9.559822 -> 9.698682 |
| Q3 FY26 Cash | 1.661333371 | 1.679983120 | 1.661333 -> 1.679983 |
| Oct FY26 Consolidated | 16.293960277 | 16.850336490 | 16.293960 -> 16.850336 |
| Oct FY26 Commodities | 1.305592272 | 1.362590821 | 1.305592 -> 1.362591 |
FY 2027, Q2 FY 2027, FY 2027 October: before == after exactly for all segments (no special session in range); consolidated 17.608086, 16.678121, 20.531603.

Tolerance: rel <= 1e-6, or abs <= 5.5e-7 (half-ulp of the 6-dp table).
