# Groww switch g-i ("MTF from Groww's own book"): independent recompute

Script: `out/checks/groww_switch_i_check.py` (stdlib only; rerun with the Python 3.9 venv; also writes `groww_switch_i_items.csv`).
Checked against branch `groww-ir` HEAD `0b0e70d` (files identical on `main`). Nothing under `src/engine/` or `src/live/` was read.
Inputs: `snapshot/groww_ir_2026-10-31.json` (own book), `snapshot/groww_facts_reviewed_2026-10-31.json` (MTF mix, total income),
`snapshot/groww_snapshot_2026-10-23.json` (workbook total income for Q2/Q3 FY26 only: status "derived", not in the reviewed-facts file),
`snapshot/db_snapshot_2026-10-23.json` (calendar, industry MTF book), bridges g-f/g-g/g-i, the backtest text, `docs/GROWW_LIVE_SPEC.md` (g-i paragraph),
and the saved page `out/groww_ir/investor-relations_2026-10-31.html` for the unit check only.
Broking is taken from the bridge as an input (g-i leaves it alone; the bridge's own before/after Broking are identical in every row).

## Result: 349/349 comparisons agree with the committed bridge and backtest

Tolerance: half a unit of the last printed digit of the bridge value. 33 of the 45 ADR comparisons also agree to 1e-6 relative; the rest are limited only by the 6-decimal print (worst 5e-4 relative on a small delta column). The 8 tie-outs agree to ~5e-16.

| Check | Items | Agree |
|---|---:|---:|
| 1. k and tie-out of every reported quarter | 8 tie + 8 k (+ per-quarter table cells) | all |
| 2. Open quarter and MTF panel ADR | 45 (MTF and Consolidated, 5 periods) | all |
| 3. Consolidated before/after, both tables | 12 headline + 12 "without g-h" | all |
| 4. Backtest (7 quarters x 5 methods, 4 summaries x 3 windows) | 110 + 52 | all |
| 5. Units | 13 | all |
| Per-quarter table, parameters moved, daily rows | 74 + 12 + 6 | all |

One wording-level difference, not a numeric disagreement with any shipped figure: see "Notes" item 1 (Q1 FY27 industry-book backtest uses 59 rows, the text says "days").

## 1. k per reported quarter and tie-out

Disclosed MTF revenue (Rs Cr) = MTF mix x total income (Rs Mn) / 10; restated mix where it exists, original classification only for Q3 FY25, Q4 FY25, Q1 FY26.
Daily book = linear interpolation in calendar days between the two quarter-end levels (page values / 100 / 10 = Rs Cr); FY trading days = calendar equity days (FY25 249, FY26 247, FY27 247 = FY26's count, FY27 incomplete).
k = disclosed / sum over the quarter's equity days of (book x 14.95% / FY days).

| Quarter | Days | Mix | Total income Rs Mn | Disclosed Rs Cr | My k | Sum of daily at k | Rel diff |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q3 FY25 (extra) | 62 | 0.020 | 10,044.47 | 20.088940 | 1.158422 | 20.088940 | 3.5e-16 |
| Q4 FY25 | 62 | 0.020 | 8,495.72 | 16.991440 | 0.799157 | 16.991440 | 4.2e-16 |
| Q1 FY26 | 61 | 0.030 | 9,484.71 | 28.454130 | 0.932048 | 28.454130 | 5.0e-16 |
| Q2 FY26 | 64 | 0.047 | 10,707.97 | 50.327459 | 0.961304 | 50.327459 | 2.8e-16 |
| Q3 FY26 | 62 | 0.056 | 12,610.72 | 70.620032 | 0.942918 | 70.620032 | 0.0 |
| Q4 FY26 | 60 | 0.069 | 15,355.35 | 105.951915 | 1.140698 | 105.951915 | 2.7e-16 |
| Q1 FY27 | 60 | 0.080 | 15,486.70 | 123.893600 | 1.032540 | 123.893600 | 2.3e-16 |
| Q2 FY27 | 65 | 0.101 | 15,405.40 | 155.594540 | 0.973276 | 155.594540 | 5.5e-16 |

All k values equal the bridge's (4 d.p.), as do own average book, industry average book, quarter revenue at k=1, "book after k" and share of industry (74 table cells). The tie is by construction (k is the ratio), so it tests the arithmetic and the day sets (each quarter's days match: 62/62/61/64/62/60/60/65); the substantive content is the k values and the inputs behind them.

## 2. Open quarter (Q3 FY27) and MTF panel

Rule: k = 1, level = QTD 40,848.931 Rs Mn (page raw 4,084,893.1; covers_through 2026-10-30) held flat on every open-quarter day.
Daily = 4,084.8931 Cr x 14.95% / 247 = **2.472435 Cr/day**; 13 equity days (1-21 Oct 2026) = 32.1417 Cr. Bridge: avg book 4,084.89, quarter revenue at k=1 32.14. Agree.

MTF panel ADR (Rs Cr/day):

| Period | Days before / after | My before | Bridge before | My after | Bridge after | Verdict |
|---|---|---:|---:|---:|---:|---|
| FY 2027 | 136 / 138 | 2.276956 | 2.276956 | 2.258187 | 2.258187 | agree |
| FY 2027 October | 12 / 13 | 2.514824 | 2.514824 | 2.472435 | 2.472435 | agree |
| Q2 FY 2027 | 65 / 65 | 2.393762 | 2.393762 | 2.393762 | 2.393762 | agree (unchanged: ties) |
| FY 2026 | 247 / 247 | 1.033820 | 1.033820 | 1.033820 | 1.033820 | agree |
| FY 2026 October | 21 / 21 | 1.113263 | 1.113263 | 1.018575 | 1.018575 | agree |

"Before" is rebuilt independently as the g-f path (share_q x industry book x 14.95% / FY days, share calibrated per reported quarter, Q3 FY27 carries the Q2 FY27 share): it reproduces the g-f bridge's MTF figures too. The before series has 507 rows (no industry book on 2026-04-08 and 2026-10-21); g-i adds those two days (509). Before: FY27 average over 136 days, Oct over 12; after: 138 and 13. Part of the change is therefore a day-set change, not only a level change (small: Oct 21 earns the same 2.47 as its neighbours).

## 3. Consolidated = Broking + MTF (Broking from the bridge, unchanged)

| Period | Broking | My before | Bridge | My after | Bridge | My d% | Bridge d% |
|---|---:|---:|---:|---:|---:|---:|---:|
| FY 2027 | 17.722781 | 19.999737 | 19.999737 | 19.980968 | 19.980968 | -0.0938% | -0.0938% |
| FY 2027 October | 20.724498 | 23.239322 | 23.239322 | 23.196933 | 23.196933 | -0.1824% | -0.1824% |
| Q2 FY 2027 | 16.188957 | 18.582719 | 18.582719 | 18.582719 | 18.582719 | 0.0000% | 0.0000% |
| FY 2026 | 15.041634 | 16.075454 | 16.075454 | 16.075454 | 16.075454 | 0.0000% | 0.0000% |

The "g-i on top of g-a..g-g alone (without g-h)" table also agrees (Broking from the g-g bridge: FY27 17.728318, Oct 20.783268, FY26 15.041634...): FY27 20.005274 -> 19.986505 (-0.0938%), Oct 23.298092 -> 23.255703 (-0.1819%). FY27 consolidated moves -0.019 Cr/day (-0.09%), October -0.042 Cr/day (-0.18%); MTF panel itself moves -0.82% (FY27) and -1.69% (Oct).

## 4. Backtest recompute (error = prediction / disclosed - 1)

Methods as in the backtest text. Every per-quarter prediction and error agrees with the table to its print precision. Summary (mine, identical to the doc):

| Window | Method | n | Mean signed | Mean abs | Max abs |
|---|---|---:|---:|---:|---:|
| Q4 FY25..Q2 FY27 | industry book (g-f) | 7 | -16.3% | 20.8% | 41.3% |
| | own book, quarter-end | 7 | +19.2% | 20.2% | 34.4% |
| | own book, g-i path (k=1) | 7 | +4.3% | 8.7% | 25.1% |
| | own book, prev quarter-end held flat | 7 | -11.1% | 16.5% | 21.9% |
| | own book, path x previous k | 7 | +4.1% | 14.0% | 45.0% |
| Q1 FY26..Q2 FY27 | industry / path / flat | 6 | -21.1% / +0.8% / -16.1% | 22.2% / 5.9% / 16.1% | 41.3% / 12.3% / 21.9% |
| Q3 FY25..Q2 FY27 (own only) | quarter-end / path / flat | 8 | +16.9% / +2.0% / -13.2% | 17.8% / 9.3% / 17.9% | 34.4% / 25.1% / 27.9% |

Per quarter, own path k=1: -13.7, +25.1, +7.3, +4.0, +6.1, -12.3, -3.2, +2.7 %; prev-quarter-end flat: -27.9, +18.8, -21.9, -20.3, -11.3, -20.9, -17.5, -4.6 %; industry (Q4 FY25 on): +12.5, -41.3, -26.8, -17.2, -33.6, -11.1, +3.0 %.

## 5. Units

Page chart values / 100 = Rs Mn, confirmed three ways: (a) saved page text shows the open-quarter book as "₹40,849 Mn" while the raw chart value is 4,084,893.1 (ratio 100.0); `rawCurrentValue` is 4,084,893,128,700 (another 100x, so it is not the displayed unit); (b) all 11 quarterly page values / 100 equal the snapshot's Rs Mn exactly; (c) Q2 FY27: page 4,351,632.8 / 100 = 43,516.328 Rs Mn vs the KPI-handbook `mtf_book` fact 43,514 Rs Mn (printed 4,351.4 Cr): +0.005%. Q1 FY26 10,358 vs 10,357.69. The QTD change on the page, 2,667 Mn (-6.1%), equals 43,516.3 - 40,848.9.

## Notes and concerns for switching g-i on

1. Backtest wording vs implementation (the only difference found). The text defines the industry-book method as "x days"; the bridge number for Q1 FY27 (110.19, -11.1%) uses the 59 industry rows, not the 60 calendar days (2026-04-08 has no industry row). Under "x days" it would be 112.06 (-9.6%), giving a mean abs error 20.6% (not 20.8%) over 7 quarters, mean signed -16.1% (not -16.3%); max abs 41.3% unchanged. No conclusion changes; the 59-row version is what g-f actually does. Other quarters are identical.
2. Open-quarter rule is the weak spot. The backtest that corresponds to it (previous quarter-end held flat, i.e. day 1) understates every quarter bar one (signed -11.1%, abs 16.5%, max 21.9%), only modestly better than the industry method (mean abs 16.5% vs 20.8%, max 21.9% vs 41.3%) and not near the headline; the headline 8.7% vs 20.8% compares a method that uses the quarter's own end level (hindsight) with one that does not. The spec paragraph states this caveat; AB should read the 16.5% as the honest figure for the open quarter. Today's case runs the other way: the QTD book is 6.1% below the Q2 end. The 40,849 level is the 30 Oct level applied flat to 1-21 Oct; if the fall since 30 Sep was roughly linear, the 1-21 Oct average book was about 42,500, so Q3 FY27 MTF revenue and Oct ADR may be about 4% understated (illustration, not a measured figure). It improves only if daily archived levels accumulate after today.
3. k = 1 in the open quarter ignores the observed k spread (0.80-1.16; 0.93-1.14 over the last six quarters, 0.97-1.03 in the last two). Q3-Q4 FY25 k (1.158, 0.799) mostly reflects the whole-percent mix (+-25%). That is residual uncertainty of roughly +-5-15% around the open-quarter level.
4. Day basis: FY27 uses FY26's 247 days. This does not touch reported quarters but sets the open-quarter level (a 245-day FY27 would raise it 0.8%).
5. Total income for Q2 and Q3 FY26 (and so their disclosed MTF revenue and k) comes from the workbook snapshot facts (status "derived", formula, =row 103 + 104), not from the reviewed-facts file. It matches the g-f bridge, but it is the least-reviewed input.
6. Unit risk: the page's raw values are 100x the displayed Rs Mn. A silent change by Groww in units would scale the MTF line by 100x or 0.01x; the switch is off by default and the share of industry (2.7-2.8%) is an easy sanity guard.
7. Day-set change: g-i adds 2026-04-08 and 2026-10-21 and the MTF averages in the "before" use 136 (FY27) and 12 (Oct) days; this is part of the Δ and is disclosed in the bridge.
8. The interpolation is linear in calendar days between quarter-end levels; the page has no intra-quarter history, so the shape inside a closed quarter cannot be validated. It only affects the daily shape, not any reported quarter's total.
