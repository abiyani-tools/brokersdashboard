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
- Q4 FY26 is a definition break in the disclosed share (Groww doubled the denominator; the engine's legacy value is 2 x the printed one, which assumes the break was exactly 2x). Neither method can see it: both miss by -15% / -9% there. Without it: share 4.1% vs 3.3%, revenue 5.2% vs 5.2%.
- n = 4 quarters per segment: the differences are inside the noise of the disclosed share (printed to 3 decimals) and of mix x total income. g-h does NOT clearly beat carry; it helps cash and hurts F&O. Its live effect today is small (Q3 FY27 ratio cash 0.981, F&O 1.002). Adopting it is AB's call.

