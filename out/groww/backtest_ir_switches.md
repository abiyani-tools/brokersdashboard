# Groww IR switches: backtests

## g-h: quarter-to-date turnover share, backtest on reported quarters

Each reported quarter Q3 FY26 .. Q2 FY27 is predicted from the previous reported quarter, by (i) carry (g-e: the previous share) and (ii) g-h (previous share x the change in Groww's share of NSE+BSE turnover):

    share_pred = share_prev x (Groww turnover share in q / Groww turnover share in prev)
    Groww turnover share = Groww turnover / exchange turnover over the same days (whole quarters here)
    cash: IR stocks turnover vs NSE cash_traded_value + BSE cash_traded_value
    F&O : IR equity-derivatives premium turnover vs NSE index + stock option premium + BSE options_premium_turnover

Revenue prediction = previous quarter's take rate x the quarter's market orders x predicted share (the engine's own order model; the take rate is unchanged, calibrated on the previous reported quarter). So the share error and the revenue error of a method are the same number up to the take-rate drift between the two quarters. "Disclosed" = the share the engine calibrates on (ADTO share, legacy basis, 3 decimals as printed: a +-0.0005 rounding is +-0.2-0.5% of the share) and the revenue mix x total income of the filing.

Data: IR page history (snapshot/groww_ir_2026-10-31.json, built from the saved page of 31 Oct 2026), exchange turnover (snapshot/groww_exchange_2026-10-31.json = sb_market_daily 'exchangesdash_json'), facts (snapshot/groww_facts_reviewed_2026-10-31.json), engine run g-a..g-g.

| Segment | Quarter | Prev | Ratio | Disclosed share | Carry share | err | g-h share | err | Disclosed rev Rs Mn | Carry rev | err | g-h rev | err |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| F&O | Q3 FY 2026 | Q2 FY 2026 | 1.0138 | 0.1810 | 0.1730 | -4.4% | 0.1754 | -3.1% | 6,747 | 6,521 | -3.3% | 6,611 | -2.0% |
| F&O | Q4 FY 2026 | Q3 FY 2026 | 0.9917 | 0.2120 | 0.1810 | -14.6% | 0.1795 | -15.3% | 8,415 | 7,646 | -9.1% | 7,583 | -9.9% |
| F&O | Q1 FY 2027 | Q4 FY 2026 | 1.0640 | 0.2200 | 0.2120 | -3.6% | 0.2256 | +2.5% | 8,038 | 7,836 | -2.5% | 8,337 | +3.7% |
| F&O | Q2 FY 2027 | Q1 FY 2027 | 1.0487 | 0.2200 | 0.2200 | +0.0% | 0.2307 | +4.9% | 6,902 | 7,032 | +1.9% | 7,374 | +6.9% |
| Cash | Q3 FY 2026 | Q2 FY 2026 | 1.0873 | 0.2880 | 0.2580 | -10.4% | 0.2805 | -2.6% | 2,081 | 1,814 | -12.8% | 1,973 | -5.2% |
| Cash | Q4 FY 2026 | Q3 FY 2026 | 1.0091 | 0.3140 | 0.2880 | -8.3% | 0.2906 | -7.4% | 2,395 | 2,181 | -8.9% | 2,201 | -8.1% |
| Cash | Q1 FY 2027 | Q4 FY 2026 | 1.0114 | 0.3020 | 0.3140 | +4.0% | 0.3176 | +5.2% | 2,493 | 2,368 | -5.0% | 2,395 | -3.9% |
| Cash | Q2 FY 2027 | Q1 FY 2027 | 1.0329 | 0.3080 | 0.3020 | -1.9% | 0.3119 | +1.3% | 2,681 | 2,834 | +5.7% | 2,927 | +9.2% |

Summary (relative error vs disclosed; n = quarters):

| Segment | n | Share: carry mean | carry mean abs | carry max abs | g-h mean | g-h mean abs | g-h max abs | g-h closer in | Revenue: carry mean abs | carry max abs | g-h mean abs | g-h max abs | g-h closer in |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Cash | 4 | -4.2% | 6.2% | 10.4% | -0.9% | 4.1% | 7.4% | 3/4 | 8.1% | 12.8% | 6.6% | 9.2% | 3/4 |
| F&O | 4 | -5.7% | 5.7% | 14.6% | -2.8% | 6.5% | 15.3% | 2/4 | 4.2% | 9.1% | 5.6% | 9.9% | 1/4 |
| All | 8 | -4.9% | 5.9% | 14.6% | -1.8% | 5.3% | 15.3% | 5/8 | 6.2% | 12.8% | 6.1% | 9.9% | 4/8 |
| All ex Q4 FY26 | 6 | -2.7% | 4.1% | 10.4% | +1.4% | 3.3% | 5.2% | 4/6 | 5.2% | 12.8% | 5.2% | 9.2% | 3/6 |

Reading (plain):

- Share, all 8: carry mean abs 5.9% vs g-h 5.3%; revenue 6.2% vs 6.1%. Max abs share error 14.6% vs 15.3%.
- Cash: g-h is better (share 6.2% -> 4.1%, revenue 8.1% -> 6.6%). F&O: g-h is not better (share 5.7% -> 6.5%, revenue 4.2% -> 5.6%).
- Q4 FY26 is a definition break in the disclosed share (Groww doubled the denominator; the engine's legacy value is 2 x the printed one, which assumes the break was exactly 2x). Neither method can see it: both miss the share by 7-15% there (F&O -15%, cash -7 to -8%). Without it: share 4.1% vs 3.3%, revenue 5.2% vs 5.2%.
- n = 4 quarters per segment: the differences are inside the noise of the disclosed share (printed to 3 decimals) and of mix x total income. g-h does NOT clearly beat carry; it helps cash and hurts F&O. Its live effect today is small (Q3 FY27 ratio cash 0.981, F&O 1.002). Adopting it is AB's call.


## g-i: MTF from Groww's own book, backtest on reported quarters

Disclosed MTF revenue = revenue mix x total income (Rs Cr). Predictions, each without looking at the disclosed revenue of the quarter predicted:

- **own book, quarter-end** = Groww MTF net book at the quarter end (IR page) x 14.95% x days in quarter / trading days of the FY.
- **own book, g-i path (k = 1)** = the g-i rule: daily book interpolated linearly between quarter-end levels (calendar days), x 14.95% / FY trading days, summed over the quarter.
- **own book, previous quarter-end level held flat** = the open-quarter rule ("latest level, held flat") as it would stand on day 1 of the quarter: the only own-book variant that does not know the quarter's own end level (the page keeps no intra-quarter history, so a mid-quarter version cannot be tested).
- **own book, path x previous k** = the path above times k of the previous reported quarter (k = disclosed / path), i.e. the g-f-style calibration carried one quarter. Not what g-i does for the open quarter (k = 1); shown for comparison.
- **industry book (g-f / g-e)** = the previous quarter's share of the industry book carried x this quarter's industry average book x 14.95% x days / FY days. This is how g-f + g-e price an unreported quarter.

Trading days of the FY are the calendar's equity days (g-f convention; FY27 uses FY26's count until the FY is complete). Q3 FY25 and Q4 FY25 disclose the MTF mix as a whole percent (2%), so their "disclosed" revenue is known only to about +-25%. The industry book series starts 1 Oct 2024, so the industry method needs a previous quarter and starts at Q4 FY25. Q1 and Q2 FY25 have no disclosed MTF revenue (no MTF mix before Q3 FY25).

| Quarter | Days | Own book at qtr end Rs Cr | Disclosed Rs Cr | Own qtr-end | err | Own path (k=1) | err | Own path x prev k | err | Prev qtr-end held flat | err | Industry (g-f) | err | k (disclosed / path) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Q3 FY 2025 | 62 | 542.4 | 20.09 | 20.19 | +0.5% | 17.34 | -13.7% | — | — | 14.48 | -27.9% | — | — | 1.158 |
| Q4 FY 2025 | 62 | 601.9 | 16.99 | 22.41 | +31.9% | 21.26 | +25.1% | 24.63 | +45.0% | 20.19 | +18.8% | 19.12 | +12.5% | 0.799 |
| Q1 FY 2026 | 61 | 1,035.8 | 28.45 | 38.24 | +34.4% | 30.53 | +7.3% | 24.40 | -14.3% | 22.22 | -21.9% | 16.71 | -41.3% | 0.932 |
| Q2 FY 2026 | 64 | 1,668.3 | 50.33 | 64.62 | +28.4% | 52.35 | +4.0% | 48.80 | -3.0% | 40.12 | -20.3% | 36.86 | -26.8% | 0.961 |
| Q3 FY 2026 | 62 | 2,307.4 | 70.62 | 86.59 | +22.6% | 74.90 | +6.1% | 72.00 | +1.9% | 62.61 | -11.3% | 58.44 | -17.2% | 0.943 |
| Q4 FY 2026 | 60 | 2,814.3 | 105.95 | 102.20 | -3.5% | 92.88 | -12.3% | 87.58 | -17.3% | 83.80 | -20.9% | 70.40 | -33.6% | 1.141 |
| Q1 FY 2027 | 60 | 3,774.8 | 123.89 | 137.08 | +10.6% | 119.99 | -3.2% | 136.87 | +10.5% | 102.20 | -17.5% | 110.19 | -11.1% | 1.033 |
| Q2 FY 2027 | 65 | 4,351.6 | 155.59 | 171.20 | +10.0% | 159.87 | +2.7% | 165.07 | +6.1% | 148.51 | -4.6% | 160.32 | +3.0% | 0.973 |

Summary (relative error vs disclosed):

| Quarters | Method | n | Mean (signed) | Mean abs | Max abs |
|---|---|---:|---:|---:|---:|
| Q4 FY25..Q2 FY27 (7, every method) | industry book (g-f) | 7 | -16.3% | 20.8% | 41.3% |
| Q4 FY25..Q2 FY27 (7, every method) | own book, quarter-end | 7 | +19.2% | 20.2% | 34.4% |
| Q4 FY25..Q2 FY27 (7, every method) | own book, g-i path (k=1) | 7 | +4.3% | 8.7% | 25.1% |
| Q4 FY25..Q2 FY27 (7, every method) | own book, previous quarter-end held flat | 7 | -11.1% | 16.5% | 21.9% |
| Q4 FY25..Q2 FY27 (7, every method) | own book, path x previous k | 7 | +4.1% | 14.0% | 45.0% |
| Q1 FY26..Q2 FY27 (6, mix to 0.1pp) | industry book (g-f) | 6 | -21.1% | 22.2% | 41.3% |
| Q1 FY26..Q2 FY27 (6, mix to 0.1pp) | own book, quarter-end | 6 | +17.1% | 18.3% | 34.4% |
| Q1 FY26..Q2 FY27 (6, mix to 0.1pp) | own book, g-i path (k=1) | 6 | +0.8% | 5.9% | 12.3% |
| Q1 FY26..Q2 FY27 (6, mix to 0.1pp) | own book, previous quarter-end held flat | 6 | -16.1% | 16.1% | 21.9% |
| Q1 FY26..Q2 FY27 (6, mix to 0.1pp) | own book, path x previous k | 6 | -2.7% | 8.9% | 17.3% |
| Q3 FY25..Q2 FY27 (8, own book only) | own book, quarter-end | 8 | +16.9% | 17.8% | 34.4% |
| Q3 FY25..Q2 FY27 (8, own book only) | own book, g-i path (k=1) | 8 | +2.0% | 9.3% | 25.1% |
| Q3 FY25..Q2 FY27 (8, own book only) | own book, previous quarter-end held flat | 8 | -13.2% | 17.9% | 27.9% |

Reading (plain):

- On the 7 quarters every method can predict: industry book (g-f) mean abs 20.8% / max 41.3%; Groww's own book on the g-i path 8.7% / 25.1%; own book at quarter end 20.2% / 34.4%. On the 6 quarters with a mix known to 0.1pp: industry 22.2% / 41.3%, own path 5.9% / 12.3%.
- Caution: the quarter-end and path variants use the quarter's own end level, which the open quarter does not have. The variant that does not (previous quarter-end level held flat: the live open-quarter rule as on day 1) has mean abs error 16.5% / max 21.9% on the 7 quarters, signed mean -11.1%: with a book growing 10-70% a quarter it under-states, as the industry method does (-16.3% signed). Mid-quarter the live rule uses the latest archived level, which is closer than day 1; that cannot be backtested (the page keeps no intra-quarter history).
- The own-book methods carry no calibration and are not fitted on the revenue they predict; the industry method carries a share fitted on the previous quarter. The quarter-end level overstates a quarter's average book when the book is rising (hence the positive signed mean); interpolating between quarter ends removes most of that, at the price of needing the quarter's end level.
- k (last column) is the residual between "own book x 14.95%" and the disclosed revenue: it is the calibration g-i keeps in reported quarters, so reported-quarter totals still tie to the disclosure exactly. It ranges 0.80-1.16; the Q3-Q4 FY25 values include the whole-percent mix rounding.

