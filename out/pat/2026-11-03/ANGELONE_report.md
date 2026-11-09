# PAT model — ANGELONE (dry run) · ADR run 60065c7b as of 2026-11-03

Shares 91.45 Cr · close ₹312.1 (2026-11-04) · fees ÷ broking 23.43% (quarters Q3 FY 2026, Q4 FY 2026, Q1 FY 2027, Q2 FY 2027)

| Rs Cr | Q1 FY27 A | Q2 FY27 A | Q3 FY27 E | Q4 FY27 E | FY 2027 E | FY 2028 E |
|---|---:|---:|---:|---:|---:|---:|
| Trading days |  |  | 61.6 | 60.4 |  | 247.0 |
| Broking revenue | 861.7 | 780.2 | 937.3 | 942.2 | 3,521.3 | 4,152.2 |
| Depository income | 43.0 | 57.3 | 50.5 | 50.7 | 201.5 | 237.6 |
| Distribution income | 43.0 | 68.7 | 72.1 | 75.8 | 259.6 | 311.6 |
| MTF income | 230.0 | 279.3 | 294.0 | 296.4 | 1,099.7 | 1,306.3 |
| Other interest income (treasury) | 236.9 | 230.7 | 230.7 | 230.7 | 929.0 | 1,068.4 |
| Other income | 19.1 | 15.4 | 16.6 | 16.6 | 67.7 | 67.7 |
| Total income | 1,433.7 | 1,431.5 | 1,601.2 | 1,612.4 | 6,078.7 | 7,143.7 |
| Finance cost | 129.2 | 147.5 | 150.6 | 150.6 | 578.0 | 613.8 |
| Fees & commission expense | 203.1 | 191.1 | 219.6 | 220.8 | 834.6 | 972.9 |
| Employee cost (incl. ESOP) | 268.6 | 255.5 | 285.4 | 285.4 | 1,095.0 | 1,226.4 |
| Depreciation | 35.1 | 34.8 | 35.3 | 36.8 | 142.0 | 159.1 |
| Other expenses | 472.6 | 344.3 | 381.8 | 456.4 | 1,655.1 | 1,820.6 |
| Impairment | 0.6 | -0.2 | 0.9 | 0.9 | 2.1 | 2.3 |
| Total costs | 1,109.0 | 973.0 | 1,073.7 | 1,150.9 | 4,306.6 | 4,795.1 |
| PBT | 324.7 | 458.5 | 527.5 | 461.4 | 1,772.1 | 2,348.6 |
| Tax | 93.3 | 123.5 | 131.9 | 115.4 | 464.0 | 587.2 |
| PAT | 231.4 | 335.0 | 395.6 | 346.1 | 1,308.1 | 1,761.5 |
| MTF book (average) | 6,137.0 | 7,453.0 | 7,843.9 | 7,909.8 | 7,335.9 | 8,714.8 |

## Valuation

| | Bear | Base | Bull |
|---|---:|---:|---:|
| FY 2027 EPS | 14.30 | 14.30 | 14.30 |
| FY 2027 P/E | 18.00 | 22.50 | 27.00 |
| FY 2027 Price (P/E × EPS) | 257.47 | 321.84 | 386.21 |
| FY 2027 Discounted | 218.20 | 272.74 | 327.29 |
| FY 2027 Upside vs close | -30.1% | -12.6% | +4.9% |
| FY 2028 EPS | 19.26 | 19.26 | 19.26 |
| FY 2028 P/E | 18.00 | 22.50 | 27.00 |
| FY 2028 Price (P/E × EPS) | 346.71 | 433.39 | 520.06 |
| FY 2028 Discounted | 293.82 | 367.28 | 440.73 |
| FY 2028 Target price today | 269.56 | 336.95 | 404.34 |
| FY 2028 Upside vs close | -13.6% | +8.0% | +29.6% |

## Against the workbook

| | Workbook | Model | Change |
|---|---:|---:|---:|
| FY27 PAT (`Angel One - ADR model (A+B)!C22`) | 870.43 | 1,308.09 | +50.3% |
| FY28 PAT (`!C44`) | 1,387.49 | 1,761.46 | +27.0% |
| FY28 target today (base) (`!D51`) | 265.39 | 336.95 | +27.0% |

## Rules (projected periods)

- FY 2028 · Broking ADR: 20-day broking ADR 15.150 × average of (1 + 3.0%)^2..^5 = 16.811 a day × 247 days
- FY 2028 · Broking revenue: 20-day broking ADR 15.150 × average of (1 + 3.0%)^2..^5 = 16.811 a day × 247 days
- FY 2028 · Depository income: FY27 × broking growth
- FY 2028 · Depreciation: FY27 × (1 + 12%)
- FY 2028 · Distribution income: FY27 × (1 + 20%)
- FY 2028 · Employee cost (incl. ESOP): FY27 × (1 + 12%)
- FY 2028 · Fees & commission expense: 23.43% of broking
- FY 2028 · Finance cost: FY27 578.0 + 9.0% × new borrowing 398 (book 8,715 − 7,336, less 75% of FY27 PAT 1308.1, not below 0)
- FY 2028 · Impairment: FY27 × (1 + 10%)
- FY 2028 · MTF income: 20-day MTF ADR 4.766 × average of (1 + 3.0%)^2..^5 = 5.289 a day × 247 days
- FY 2028 · Other income: FY27
- FY 2028 · Other expenses: FY27 × (1 + 10%)
- FY 2028 · Other interest income (treasury): FY27 × (1 + 15%)
- Q3 FY 2027 · Broking revenue: engine daily broking to 2026-11-03 (22 days) + 39.6 days × 20-day ADR 15.150
- Q3 FY 2027 · Depository income: 40% × cash broking 126.2
- Q3 FY 2027 · Depreciation: same quarter last year × (1 + 12%)
- Q3 FY 2027 · Distribution income: previous quarter × (1 + 5%)
- Q3 FY 2027 · Employee cost (incl. ESOP): FY26 quarterly average × (1 + 7%)
- Q3 FY 2027 · Fees & commission expense: 23.43% of broking (last 4 reported quarters)
- Q3 FY 2027 · Finance cost: previous 147.5 + 9.0%/4 × new borrowing 140 (book 7,844 − 7,453, less 75% of previous PAT 335.0, not below 0)
- Q3 FY 2027 · Impairment: FY26 quarterly average × (1 + 10%)
- Q3 FY 2027 · MTF income: engine daily MTF to 2026-11-03 (22 days) + 39.6 days × 20-day ADR 4.766
- Q3 FY 2027 · Other income: average of the last 4 reported quarters
- Q3 FY 2027 · Other expenses: same quarter last year × (1 + 10%)
- Q3 FY 2027 · Other interest income (treasury): previous quarter × (1 + 0%)
- Q4 FY 2027 · Broking revenue: 60.4 days × 20-day ADR 15.150 × (1 + 3.0%)^1
- Q4 FY 2027 · Depository income: 40% × cash broking 126.9
- Q4 FY 2027 · Depreciation: same quarter last year × (1 + 12%)
- Q4 FY 2027 · Distribution income: previous quarter × (1 + 5%)
- Q4 FY 2027 · Employee cost (incl. ESOP): FY26 quarterly average × (1 + 7%)
- Q4 FY 2027 · Fees & commission expense: 23.43% of broking (last 4 reported quarters)
- Q4 FY 2027 · Finance cost: previous 150.6 + 9.0%/4 × new borrowing 0 (book 7,910 − 7,844, less 75% of previous PAT 395.6, not below 0)
- Q4 FY 2027 · Impairment: FY26 quarterly average × (1 + 10%)
- Q4 FY 2027 · MTF income: 60.4 days × 20-day ADR 4.766 × (1 + 3.0%)^1
- Q4 FY 2027 · Other income: average of the last 4 reported quarters
- Q4 FY 2027 · Other expenses: same quarter last year × (1 + 10%)
- Q4 FY 2027 · Other interest income (treasury): previous quarter × (1 + 0%)
