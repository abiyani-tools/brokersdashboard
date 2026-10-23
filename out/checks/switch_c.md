# Check - switch (c): real BSE F&O contracts for the 15 frozen days

Independent recompute, 23 Oct 2026, without `src/engine/` or `src/live/`. Script: `out/checks/switch_c_check.py`
(`python3 -I out/checks/switch_c_check.py`; reads only `snapshot/db_snapshot_2026-10-23.json` and `facts_reviewed_2026-10-23.json`).

**Result: 13 checks, 13 agree (ADRs and deltas at rel <= 7e-8 vs the 6-decimal claims; ratios at <= 1e-10). No disagreements.**

## Method
- Before = workbook daily F&O revenue (`parity_expected` `fo_rev_mn|date`, Rs Mn) x (a) [Q3 FY26 x 381/380; Apr 2026 onward x 1.000874473]
  x (b) [per-quarter F&O take-rate ratio; Apr 2026 onward x 0.999362095], as in switch_a.md / switch_b_check.py.
- Day ratio = (NSE + BSE_real) / (NSE + 18,962,859), NSE from `market_daily` nse_fo/contracts, BSE_real from `market_daily_lake`.
- After = before x ratio on those 15 days, else unchanged. ADR = AVERAGEIFS / 10 (Rs Mn -> Rs crore).
- Note: the ratio assumes the workbook's daily F&O revenue is proportional to NSE+BSE contracts that day (as given in the task); not re-derived from column V.

## Input checks
- `market_daily` has exactly 15 bse_fo rows with status 'imputed' (2026-09-29 .. 2026-10-21), all = 18,962,859; no other dataset has non-'ok' rows.
- `market_daily_lake` has the same 15 dates; all 15 values match the list given (e.g. 09-29 27,311,202; 10-01 512,976,127; 10-08 459,891,587; 10-09 18,761,074; 10-21 188,513,714).
- 2 of the 15 changed days fall in September (09-29, 09-30); the other 13 are in October, which equals the 13 October trading days in the period.

## Daily ratios (all computed)
| Date | NSE | BSE real | Ratio |
|---|---:|---:|---:|
| 2026-09-29 | 391,345,011 | 27,311,202 | 1.020346534 |
| 2026-09-30 | 70,406,273 | 152,837,325 | 2.497994475 |
| 2026-10-01 | 93,623,700 | 512,976,127 | 5.387852976 |
| 2026-10-05 | 200,466,714 | 26,843,978 | 1.035916394 |
| 2026-10-06 | 324,591,448 | 27,015,960 | 1.023440547 |
| 2026-10-07 | 73,324,482 | 162,293,562 | 2.553091697 |
| 2026-10-08 | 81,469,428 | 459,891,587 | 5.390308547 (max) |
| 2026-10-09 | 131,595,782 | 18,761,074 | 0.998659758 (min; real < frozen) |
| 2026-10-12 | 188,020,446 | 26,038,276 | 1.034183515 |
| 2026-10-13 | 437,742,373 | 40,228,045 | 1.046562169 |
| 2026-10-14 | 85,522,676 | 174,459,443 | 2.488211588 |
| 2026-10-15 | 96,381,541 | 493,485,755 | 5.113965619 |
| 2026-10-16 | 174,991,899 | 24,749,231 | 1.029833617 |
| 2026-10-19 | 430,513,108 | 32,609,976 | 1.030362284 |
| 2026-10-21 | 92,942,397 | 188,513,714 | 2.515128610 |

## F&O ADR, Rs crore/day (recomputed unrounded)
| Period | days | Before mine / claim | After mine / claim | Delta mine / claim |
|---|---:|---|---|---|
| FY 2027 | 138 | 9.287777389 / 9.287777 | 9.785973717 / 9.785974 | 0.4981963 / 0.498196 |
| Q2 FY 2027 | 65 | 8.500172103 / 8.500172 | 8.572370393 / 8.572370 | 0.0721983 / 0.072198 |
| Oct 2026 (to 21 Oct) | 13 | 6.745810534 / 6.745811 | 11.673364713 / 11.673365 | 4.9275542 / 4.927554 |

## Scope
- Exactly 15 F&O days change; 0 of the other 494 F&O days change (509 days total).
- Cash, commodity, MTF: the switch only alters the F&O day factor, so their deltas are zero by construction; I did not re-run those segments.
  Consolidated deltas therefore equal the F&O deltas (checked as F&O deltas above).
