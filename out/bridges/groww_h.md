# Bridge — Groww switch (g-h)

Quarter-to-date turnover share: an unreported quarter's F&O and cash share = last reported share x (Groww QTD share of NSE+BSE turnover / its share in the last reported quarter), take rate carried.

Before: switches abcdefg · after: abcdefgh

Consolidated ADR, Rs crore per trading day (MTF gross):

| Period | Before | After | Δ % |
|---|---:|---:|---:|
| FY 2027 | 20.005274 | 19.999737 | -0.0277% |
| Q2 FY 2027 | 18.582719 | 18.582719 | +0.0000% |
| FY 2027 October | 23.298092 | 23.239322 | -0.2523% |
| FY 2026 | 16.075454 | 16.075454 | +0.0000% |

g-h arithmetic (Groww turnover share = Groww turnover / NSE+BSE exchange turnover over the same days; cash: stocks turnover vs NSE + BSE cash_traded_value, F&O: equity-derivatives premium vs NSE index + stock option premium + BSE options_premium_turnover; both sides Rs Cr):

| Segment | Quarter | Groww Rs Cr | Exchange Rs Cr | Days | Share | Last reported: Groww | Exchange | Share | Ratio | Share before | Share after |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Cash | Q3 FY 2027 (to 2026-10-30) | 273,151.3 | 2,486,622.4 | 20 | 10.985% | 938,087.0 (Q2 FY 2027) | 8,376,614.1 | 11.199% | 0.980887 | 0.3080 | 0.3021 |
| F&O | Q3 FY 2027 (to 2026-10-30) | 371,260.7 | 2,120,151.7 | 20 | 17.511% | 800,978.9 (Q2 FY 2027) | 4,582,986.3 | 17.477% | 1.001935 | 0.2200 | 0.2204 |

The QTD point runs through 2026-10-30 (stored; inferred from the turnover series, see src/engine/groww_ir.py). The model's Q3 FY 2027 has 13 trading days (the snapshot's as-of date), so the ratio built on 20 days is applied to those 13. Take rates are unchanged (calibrated on reported quarters); reported quarters are untouched.

ADR, Rs crore per trading day (MTF gross):

| Period | Panel | Before | After | Δ | Δ % |
|---|---|---:|---:|---:|---:|
| FY 2027 | Consolidated | 20.005274 | 19.999737 | -0.005536 | -0.0277% |
| FY 2027 | Broking | 17.728318 | 17.722781 | -0.005536 | -0.0312% |
| FY 2027 | MTF | 2.276956 | 2.276956 | +0.000000 | +0.0000% |
| FY 2027 | F&O | 12.187676 | 12.190311 | +0.002635 | +0.0216% |
| FY 2027 | Cash | 4.176738 | 4.168567 | -0.008172 | -0.1956% |
| FY 2027 | Commodities | 1.363903 | 1.363903 | +0.000000 | +0.0000% |
| Q2 FY 2027 | Consolidated | 18.582719 | 18.582719 | +0.000000 | +0.0000% |
| Q2 FY 2027 | Broking | 16.188957 | 16.188957 | +0.000000 | +0.0000% |
| Q2 FY 2027 | MTF | 2.393762 | 2.393762 | +0.000000 | +0.0000% |
| Q2 FY 2027 | F&O | 10.617876 | 10.617876 | +0.000000 | +0.0000% |
| Q2 FY 2027 | Cash | 4.123907 | 4.123907 | +0.000000 | +0.0000% |
| Q2 FY 2027 | Commodities | 1.447174 | 1.447174 | +0.000000 | +0.0000% |
| FY 2027 October | Consolidated | 23.298092 | 23.239322 | -0.058770 | -0.2523% |
| FY 2027 October | Broking | 20.783268 | 20.724498 | -0.058770 | -0.2828% |
| FY 2027 October | MTF | 2.514824 | 2.514824 | +0.000000 | +0.0000% |
| FY 2027 October | F&O | 14.458817 | 14.486792 | +0.027975 | +0.1935% |
| FY 2027 October | Cash | 4.538468 | 4.451722 | -0.086746 | -1.9113% |
| FY 2027 October | Commodities | 1.785983 | 1.785983 | +0.000000 | +0.0000% |
| FY 2026 | Consolidated | 16.075454 | 16.075454 | +0.000000 | +0.0000% |
| FY 2026 | Broking | 15.041634 | 15.041634 | +0.000000 | +0.0000% |
| FY 2026 | MTF | 1.033820 | 1.033820 | +0.000000 | +0.0000% |
| FY 2026 | F&O | 10.813984 | 10.813984 | +0.000000 | +0.0000% |
| FY 2026 | Cash | 3.330972 | 3.330972 | +0.000000 | +0.0000% |
| FY 2026 | Commodities | 0.896679 | 0.896679 | +0.000000 | +0.0000% |
| FY 2026 October | Consolidated | 17.199648 | 17.199648 | +0.000000 | +0.0000% |
| FY 2026 October | Broking | 16.086385 | 16.086385 | +0.000000 | +0.0000% |
| FY 2026 October | MTF | 1.113263 | 1.113263 | +0.000000 | +0.0000% |
| FY 2026 October | F&O | 11.855821 | 11.855821 | +0.000000 | +0.0000% |
| FY 2026 October | Cash | 3.519421 | 3.519421 | +0.000000 | +0.0000% |
| FY 2026 October | Commodities | 0.711143 | 0.711143 | +0.000000 | +0.0000% |

Parameters that moved:

| Segment | Quantity | Quarter | Before | After | Δ % |
|---|---|---|---:|---:|---:|
| Cash | share (ADTO, legacy basis) | Q3 FY 2027 | 0.3080 | 0.3021 | -1.911% |
| F&O | share (ADTO, legacy basis) | Q3 FY 2027 | 0.2200 | 0.2204 | +0.193% |

Daily revenue rows that changed:

| Segment | Days | Changed | First | Last | Ratio min | Ratio max |
|---|---:|---:|---|---|---:|---:|
| F&O | 573 | 13 | 2026-10-01 | 2026-10-21 | 1.001934828 | 1.001934828 |
| Cash | 573 | 13 | 2026-10-01 | 2026-10-21 | 0.980886609 | 0.980886609 |
| Commodities | 272 | 0 |  |  |  |  |
| MTF | 507 | 0 |  |  |  |  |
