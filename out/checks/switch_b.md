# Check — switch (b): revenue mix to one decimal

Independent recompute by `recompute-checker`, 23 Oct 2026, without `src/engine/` or `src/live/`.
Script: `out/checks/switch_b_check.py` (rerun with `python3 -I out/checks/switch_b_check.py`; it reads only the snapshot JSON files).

**Result: 28 checked, 27 agree at ≤ 1e-6. The one "disagreement" is a rounded claim, not a difference:** the claimed
before cash take rate 16.7752 was written to 4 decimals; the recomputed value 16.775235 rounds to it (rel 2.07e-6).

Method: take rate = mix × total income (row 99) ÷ orders (rows 6–8), recomputed per quarter from the seed cells
before and after, with J8 = 35 in both (switch a on). BEFORE ADRs from the workbook's own daily values
(`parity_expected`), adjusted for switch (a); AFTER = BEFORE × the derived daily ratios; averages as AVERAGEIFS ÷ 10.

Take-rate ratios (after / before):

| Quarter | F&O | Cash |
|---|---|---|
| Q3 FY25 | 0.997151 | 1 |
| Q4 FY25 | 1.002165 | 1 |
| Q1 FY26 | 1.004444 | 0.97 |
| Q2 FY26 | 0.993478 | 1.05 |
| Q3 FY26 | 1.006818 (0.443/0.44) | 0.9625 |
| Q4 FY26 | 0.997872 | 1.042857 |
| Q1 FY27 | (not used: F&O actuals end Q4 FY26) | 0.955556 (19.258657 → 18.402716) |

- F&O projected rate (avg Q2–Q4 FY26): 21.422996 → 21.409331, ratio 0.999362095 (−0.0638%).
- Cash projected rate (avg Q3 FY26–Q1 FY27): 16.775235 → 16.512193.
- Commodity fixed rate: × 0.061/0.06 = 1.016666667 on every day.

ADR, Rs crore per trading day — recomputed values equal the bridge (`out/bridges/b.md`) to ≤ 2.5e-7 relative:

| Period | Segment | Before | After |
|---|---|---:|---:|
| FY 2027 | Commodity | 1.581057 | 1.607408 |
| FY 2027 | F&O | 9.293706 | 9.287777 |
| FY 2027 | Cash | 2.064588 | 2.005320 |
| Q2 FY 2027 | Commodity | 1.642440 | 1.669814 |
| Q2 FY 2027 | F&O | 8.505598 | 8.500172 |
| Q2 FY 2027 | Cash | 1.965533 | 1.934712 |
| Oct 2026 | Commodity | 1.967379 | 2.000169 |
| Oct 2026 | F&O | 6.750116 | 6.745811 |
| Oct 2026 | Cash | 2.163120 | 2.129202 |

Consolidated deltas (unrounded): FY 2027 −0.0388461, Q2 FY 2027 −0.0088720, Oct −0.0054348 Rs crore/day.
385 of 509 cash days change (Q3/Q4 FY25 mix unchanged). MTF does not read the mix rows (not recomputed).
