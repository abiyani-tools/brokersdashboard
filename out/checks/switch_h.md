# Independent check of switch (h): Q2 FY 2027 becomes an actual quarter

Script: `out/checks/switch_h_check.py` (stdlib, snapshot JSON only; `python3 -I`). Result: **101 checked, 101 agree, 0 disagree.**
Tolerance: rel <= 1e-6 or half a unit in the last printed decimal of the claim (claims are rounded).

Method: BEFORE (a-g) = workbook daily values adjusted by the a-g chain (a: J8=35; b: deck mix; c: real BSE on 15 frozen days; e: monthly cash share; f: per-quarter commodity rate; g: gross MTF), reusing the switch_a..g scripts. AFTER = per-day ratios from the changed intermediates. F&O, cash and MTF AFTER and BEFORE were also rebuilt directly from raw market_daily (contracts/trades/book) and match the ratio path (max rel 7e-16).

## Intermediates (all agree)
- F&O E Apr/May FY27: before = mean of Q2, Q3 (J8=35), Q4 FY26 orders share = 0.729933; after = 300/(300+67+40) = 0.737101.
- F&O H = G/F, G = share x sum(NSE+BSE contracts)/1e6, F = E x C.
  - April: G = 0.223 x 6403.5 = 1427.98168, C = 135.75. H = 1427.98168/(0.729933 x 135.75) = 14.411181 -> /(0.737101 x 135.75) = 14.271051.
  - May: G = 1364.32737, C = 130.35. H = 14.339181 -> 14.199750. Jun-Oct carry May.
  - Sanity: with J8=36 the same raw rebuild gives the Excel H51 14.351720077 exactly.
- F&O take rate: mix x TI / orders. Q1 FY27 0.451 x 14337/300 = 21.553290 (before: avg Q2-Q4 FY26 = 21.409331). Q2 0.387 x 14315/256 = 21.640254. Q3 = mean(Q4 FY26 21.550176, 21.553290, 21.640254) = 21.565956.
- Cash: market trades Q3 FY26 2116.998, Q4 FY26 2401.643, Q1 FY27 2536.789, Q2 FY27 2691.953 Mn. P_q = trades/(orders/K).
  - Q2 before P = mean(Q3, Q4 FY26, Q1 FY27) = 6.150236; after = 2691.953/(66/0.168) = 6.852245. TR before 16.512193; after 0.087 x 14315/66 = 18.869773. Share 0.174 (monthly .171/.170/.162 under e) -> 0.168.
  - Q3: P = mean(Q4 FY26, Q1, Q2 FY27) = 6.535245; TR = 17.752967; Oct keeps monthly share 0.162 (Sep carried, no Oct fact).
- Commodity: Q2 own = 0.071 x 14315/45 = 22.585889; before Q2/Q3 used Q1 FY27 22.9392; ratio 0.984597932.
- MTF: industry mean of 65 daily values Jul 1-Sep 30 = 141829.592; share = 7453/141829.592 = 0.0525490 (before 0.0522225 = mean of Q4 FY25..Q1 FY27 shares). Q3 = mean(0.0536876, 0.0546817, 0.0512107, 0.0505477, 0.0515406, 0.0525490) = 0.0523696. Pinned Angel books / monthly-series averages reproduce the Excel Q49:Q57 shares exactly.

## Day counts and ratios (agree)
F&O 138 days Apr 1-Oct 21, ratio 1.016609392..1.020711241. Cash 78 days Jul 1-Oct 21, ratio 1.007706248..1.063689928. Commodity 80 days, ratio 0.984597932. MTF 77 days Jul 1-Oct 19, ratio 1.002815870..1.006251610. Nothing dated before 2026-04-01 changes; FY 2026 and Q3 FY 2026 ADRs unchanged.

## ADR, Rs Cr/day (mine matches every claim, before and after; 3 periods x 5 panels x before/after = 30 values)
| Period | Segment | mine before | mine after |
|---|---|---:|---:|
| FY 2027 | F&O | 9.785974 | 9.965732 |
| FY 2027 | Cash | 1.958058 | 1.984881 |
| FY 2027 | Commodities | 1.581557 | 1.567012 |
| FY 2027 | MTF | 4.209385 | 4.224009 |
| FY 2027 | Consolidated | 17.534973 | 17.741633 |
| Q2 FY 2027 | F&O / Cash / Comm / MTF | 8.572370 / 1.863740 / 1.642960 / 4.501224 | 8.749915 / 1.916008 / 1.617655 / 4.529364 |
| Q2 FY 2027 | Consolidated | 16.580294 | 16.812941 |
| FY 2027 Oct | F&O / Cash / Comm / MTF | 11.673365 / 1.982360 / 1.968001 / 4.728868 | 11.874226 / 2.005758 / 1.937690 / 4.742184 |
| FY 2027 Oct | Consolidated | 20.352594 | 20.559858 |
Day bases: FY27 F&O/cash 138, commodity 144, MTF 136; Q2 65/65/66/65; Oct 13/13/14/12.

## Process note
First run of my script showed 8 disagreements (FY27 and Q2 commodity and consolidated). Cause was my own bug: the BEFORE commodity series used the Q2 own rate (the dict already held the new Q2 fact). Fixed so BEFORE carries the Q1 FY27 rate; all then agree. No engine discrepancy.

Observation (not a disagreement): the claimed commodity ratio 22.585889/22.9392 is computed from rounded inputs (0.984597937 vs exact 0.984597932), immaterial.
