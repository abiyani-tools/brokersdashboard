# Independent check of switch (j): MTF basis per Q5 / Q6 for every reported quarter

Script: `out/checks/switch_j_check.py` (stdlib; `python3 -I out/checks/switch_j_check.py`; reads the snapshot JSON and the bridges through `git show angel-mtf-j:<path>`, branch HEAD 1ca68ab). Nothing under `src/engine/` or `src/live/` was read.
Result: **173 checked, 173 agree, 0 disagree.** Tolerance: rel <= 1e-6 or half a unit of the last printed digit of the claim.

## Method (rebuilt from raw inputs)
- Daily industry book: `market_daily` `mtf_industry/book_cr` (507 rows, 2024-10-01 .. 2026-10-19, all `ok`, 5 Muhurat/budget days kept per Q8). Quarter = `calendar.q_fy`.
- Industry average, after = mean of the daily values of the quarter's days; where none exist (Q1, Q2 FY25) = mean of the 3 monthly values. Before = mean of the 3 monthly values (Q2 FY27 already on the daily average since (h)).
- Angel book, after = reviewed `avg_funding_book` (Rs Mn) / 10 where one exists, else the `mtf_angel_book_cr` pin. Before = pin (Q2 FY27: fact 566 / 10 from (h)).
- Share = book / industry average; before keeps the Q3 FY25 `mtf_share_override` 0.0485, after drops it.
- Projected share = mean of the last 6 reported shares = Q1 FY26 .. Q2 FY27.
- Daily MTF revenue = share(q) x book_d x 0.1495 / 246 (Q3 FY27 days use the projected share). ADR = sum of revenue / number of days that have an MTF daily value (FY27 136, Q2 FY27 65, Oct-26 12, FY26 247). MTF net = 0.45 x gross. Consolidated = Broking + MTF; Broking is taken from the bridge tables (unchanged in j, and equal to the (i) "after" value).

## 1. Quarter table (all agree, before -> after)
| Quarter | Book (Rs Cr) | Industry avg (Rs Cr) | Share |
|---|---|---|---|
| Q1 FY25 | 2,630.0 pin | 73,666.7 monthly | 0.0357014 (unchanged) |
| Q2 FY25 | 3,900.0 pin | 91,666.7 monthly | 0.0425455 (unchanged) |
| Q3 FY25 | 4,050.0 pin | 88,666.7 -> 79,351.5 (62 days) | 0.0485 (override) -> 0.0510387 |
| Q4 FY25 | 4,030.0 pin | 78,000.0 -> 75,539.3 (62) | 0.0516667 -> 0.0533497 |
| Q1 FY26 | 4,205.53 -> 4,206.0 (f581) | 78,333.3 -> 74,884.3 (61) | 0.0536876 -> 0.0561667 |
| Q2 FY26 | 5,304.13 -> 5,305.0 (f582) | 97,000.0 -> 92,456.6 (64) | 0.0546817 -> 0.0573783 |
| Q3 FY26 | 5,855.09 pin | 114,333.3 -> 110,826.3 (62) | 0.0512107 -> 0.0528312 |
| Q4 FY26 | 5,796.13 -> 5,849.0 (f580) | 114,666.7 -> 114,169.0 (60) | 0.0505477 -> 0.0512311 |
| Q1 FY27 | 6,133.33 -> 6,137.0 (f498) | 119,000.0 -> 120,750.8 (59) | 0.0515406 -> 0.0508237 |
| Q2 FY27 | 7,453.0 (f566) | 141,829.6 (65) | 0.0525490 (unchanged) |
| Q3 FY27 projected | 7,803.2 -> 7,971.1 | 149,002.5 (12 days) | 0.0523696 -> 0.0534966 (+2.152%) |

Projected share: before = mean(0.0536876, 0.0546817, 0.0512107, 0.0505477, 0.0515406, 0.0525490) = 0.05236955; after = mean(0.0561667, 0.0573783, 0.0528312, 0.0512311, 0.0508237, 0.0525490) = 0.05349665.
Q3 FY25 override: 4,050 / 79,351.48 = 0.05103875 (vs 0.0485, +5.23%); with the monthly average it would have been 0.04568, so the override had been masking a larger gap.

## 2. Pinned quarters genuinely lack a reviewed fact
- Reviewed snapshot (`facts_reviewed_2026-10-23.json`, 178 reviewed rows): `avg_funding_book` Q-facts are 498 (Q1 FY27), 566 (Q2 FY27), 580 (Q4 FY26), 581 (Q1 FY26), 582 (Q2 FY26). None for Q1-Q4 FY25 or Q3 FY26.
- Live DB (project everjfpbnlbcpuarnhob, read-only SELECT): `avg_funding_book` has 9 reviewed rows (5 quarterly above + 4 monthly Jun-Sep FY27) and 14 staged. For period_type Q, the DB holds exactly facts 581, 498, 582, 566, 580 as reviewed, plus staged seeds 69, 73, 70, 71, 72. Q3 FY26 has only staged seed 71 (58,590 Mn); Q1-Q4 FY25 have no row at all, not even staged. Confirmed.

## 3. ADR (Rs Cr per trading day, MTF gross); mine equals every claim
| Period | MTF before | MTF after | Consolidated before | Consolidated after | Delta | Delta % |
|---|---:|---:|---:|---:|---:|---:|
| FY27 (136 d) | 4.224009 | 4.210191 | 17.510302 | 17.496484 | -0.013818 | -0.0789% |
| Q1 FY27 (59 d) | 3.782210 | 3.729600 | 18.024754 | 17.972143 | -0.052611 | -0.2919% |
| Q2 FY27 (65 d) | 4.529364 | 4.529364 | 16.495983 | 16.495983 | 0 | 0 |
| Oct-26 (12 d) | 4.742184 | 4.844245 | 20.216018 | 20.318079 | +0.102061 | +0.5049% |
| FY26 (247 d) | 3.117217 | 3.223252 | 15.586082 | 15.692117 | +0.106035 | +0.6803% |
| Q3 FY26 (62 d) | 3.449134 | 3.558279 | 16.121544 | 16.230689 | +0.109144 | +0.6770% |
| Oct-25 (21 d) | 3.371099 | 3.477774 | 16.851172 | 16.957847 | +0.106675 | +0.6330% |
MTF net (45% x gross) also agrees (FY27 1.894586, Oct-26 2.179910, FY26 1.450464). The "before" MTF values equal bridge (i)'s "after" MTF for every period (i) reports. Broking before = after in every row and equals (i)'s after; Consolidated delta = MTF delta exactly. Q1 FY27 has no row in (i), so only the before = after identity was tested there.
FY27 MTF moves -0.33% (Q1 FY27 days fall with share -1.39%, Q2 flat, Oct and the projected days rise with +2.15%). Daily rows: 507 MTF rows, 442 changed (all but the 65 Q2 FY27 days), first 2024-10-01, last 2026-10-19, ratio min 0.986089985 (Q1 FY27) and max 1.052345 (Q3 FY25).

## 4. Q2 FY27 unchanged, and why
Its book is fact 566 (74,530 Mn = 7,453 Cr) and its industry average is the 65-day daily mean (141,829.59), both already in place from switch (h). j changes only (i) books that were pins -> reviewed facts, (ii) industry averages that were monthly -> daily, (iii) the Q3 FY25 override. None applies to Q2 FY27, so the share (0.0525490), every Q2 FY27 daily row and the Q2 FY27 ADR are identical. The projected share moves because it averages Q1 FY26..Q1 FY27 shares that do move, not because Q2 FY27 moved.

## Observations (none is a disagreement)
1. Q3 FY26 stays on the back-solved pin 5,855.094 (= interest / 3.75%), while the only fact for it is the staged seed 58,590 Mn (5,859.0). For Q4 FY26, Q1 FY26 and Q2 FY26 the disclosed book differed from the back-solve (up to +0.9%), so Q3 FY26 is probably off by a similar small amount until its disclosed book is reviewed. It affects Q3 FY26 share (0.0528312) and the projected share (about 1/6 weight): a +0.07% book change gives +0.01% on the projection, and FY26 / Q3 FY26 MTF ADR moves by the same fraction.
2. Q1-Q4 FY25 books are round hard-coded pins (2,630 / 3,900 / 4,050 / 4,030) with no fact in the DB at all. They do not feed the projected share (last 6 = Q1 FY26 onward) or any reported ADR period; Q1-Q2 FY25 shares have no daily rows.
3. The daily series has no value for 2026-04-08 (an equity day in `calendar`). It is excluded from both the Q1 FY27 industry average (59 days) and the ADR denominator; j does not change that. The bridge, spec and my script all treat it the same way.
4. The industry average for Q3 FY27 is partial (12 days to 19 Oct) but only affects the displayed projected book, not the ADR (revenue uses share x daily book).
