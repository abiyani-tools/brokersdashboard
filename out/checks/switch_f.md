# Switch (f) check: per-quarter commodity take rate (independent rebuild)

Script: out/checks/switch_f_check.py (stdlib, `python3 -I`, reads only snapshot/db_snapshot_2026-10-23.json and snapshot/facts_reviewed_2026-10-23.json).

## Formulas (units)
- rate_q (Rs Mn per Mn orders) = revmix_comm_q (fraction, reviewed) x row99_q (Rs Mn) / row8_q (Mn orders); J8 = 35 (a).
  - Q2 FY25: 0.037 x 15160 / 23 = 24.3878; Q3 FY25: 0.044 x 12638 / 23 = 24.1770; Q4 FY25: 0.052 x 10578 / 22 = 25.0025
  - Q1 FY26: 0.055 x 11430.92 / 27 = 23.2852; Q2 FY26: 0.056 x 12041.98 / 29 = 23.2535; Q3 FY26: 0.061 x 13376.97 / 35 = 23.3141
  - Q4 FY26: 0.065 x 14672.46 / 43 = 22.1793; Q1 FY27: 0.064 x 14337 / 40 = 22.9392
- BEFORE daily (Rs cr) = comm_rev_mn (parity_expected) / 10 x 36/35 x 0.061/0.06. AFTER = BEFORE x rate_q / 23.314148. Q1 FY25 days use Q2 FY25 rate; Q2/Q3 FY27 use Q1 FY27 rate.
- ADR = AVERAGEIFS over all commodity days (zeros included) of the period; FY 2026 bases drop special sessions (d).

## Result
33 checks, 33 agree (after tolerance fix below). 660 commodity days, 596 change; only Q3 FY26 is unchanged. FY27/Q2 FY27/Oct FY27 all scale by 22.9392/23.314148 = 0.983918 (-1.6080%; claim -1.6082% matches within its rounding).

| Period | before | after | claim before | claim after |
|---|---|---|---|---|
| FY 2027 | 1.607408 | 1.581557 | 1.607408 | 1.581557 |
| Q2 FY 2027 | 1.669814 | 1.642960 | same | same |
| FY 2027 Oct | 2.000169 | 1.968001 | same | same |
| FY 2026 | 1.220379 | 1.200323 | same | same |
| Q3 FY26, FY26 Oct | unchanged 1.293745, 1.362591 | | | |

## Notes
- Rate claims are 4 dp, so the tolerance is the half-ulp of the claim (rel <= 5e-6), not 1e-6.
- First run flagged two "cons delta" lines (Q2 FY27, FY26). These are rounding artifacts of the claim (delta = difference of two 6dp-rounded numbers, up to 1e-6 error). Unrounded deltas: Q2 FY27 -0.0268546, FY26 -0.0200553; I set the delta tolerance to 1.05e-6 absolute. Not an engine disagreement.
- F&O, cash and MTF are not touched by the script (not rebuilt here); consolidated delta = commodity delta by construction.
