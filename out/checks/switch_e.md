# Check — switch (e): projected cash days use the monthly cash share

Independent recompute by `recompute-checker`, 23 Oct 2026, without `src/engine/` or `src/live/`.
Script: `out/checks/switch_e_check.py` (stdlib only, reads the snapshot JSON; `python3 -I out/checks/switch_e_check.py`).

**Result: 20 checked, 20 agree** (rel ≤ 1e-6; largest 2.5e-7, from the claims' 6-decimal rounding).

Method: BEFORE cash daily = the workbook's `cash_rev_mn|date` (parity_expected), adjusted for switch (b)
(quarterly cash take-rate ratios; Q2 FY27 onward × 16.512193/16.775235; Q1 FY27 × 0.086/0.09). (a), (c) do not
touch cash and (d) does not touch FY 2027. Each projected day × monthly share ÷ 0.174.

- Monthly facts: FY 2027 July 0.171 (fact 544), August 0.17 (527), September 0.162 (561); no FY 2027 October
  `share_cash` exists, so October uses September's 0.162.
- Days changed: exactly 78, 2026-07-01 .. 2026-10-21.

| Cash ADR (Rs crore/day) | Before | After |
|---|---:|---:|
| FY 2027 | 2.005320 | 1.958058 |
| Q2 FY 2027 | 1.934712 | 1.863740 |
| FY 2027 October | 2.129202 | 1.982360 (−6.896552%) |

Consolidated deltas equal the cash deltas: FY 2027 −0.047262, Q2 FY 2027 −0.070972, October −0.146841.
FY 2026, Q3 FY 2026, FY 2026 October cash unchanged (1.709086, 1.661333, 1.684168).
Limit: F&O, commodity and MTF are unchanged by construction (only cash days are modified); not recomputed.
