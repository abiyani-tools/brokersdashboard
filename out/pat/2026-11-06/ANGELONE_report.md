# PAT model — ANGELONE (dry run) · ADR run 435538e3 as of 2026-11-06

Shares 91.45 Cr · close ₹331 (2026-11-06) · fees ÷ broking 23.43% (quarters Q3 FY 2026, Q4 FY 2026, Q1 FY 2027, Q2 FY 2027)

| Rs Cr | Q1 FY27 A | Q2 FY27 A | Q3 FY27 E | Q4 FY27 E | FY 2027 E | FY 2028 E |
|---|---:|---:|---:|---:|---:|---:|
| Trading days |  |  | 61.7 | 60.3 |  | 247.0 |
| Broking revenue | 861.7 | 780.2 | 931.3 | 930.7 | 3,503.8 | 4,108.9 |
| Depository income | 43.0 | 57.3 | 51.5 | 51.7 | 203.4 | 238.6 |
| Distribution income | 43.0 | 68.7 | 72.1 | 75.8 | 259.6 | 311.6 |
| MTF income | 230.0 | 279.3 | 293.1 | 294.1 | 1,096.6 | 1,298.6 |
| Other interest income (treasury) | 236.9 | 230.7 | 230.7 | 230.7 | 929.0 | 1,068.4 |
| Other income | 19.1 | 15.4 | 16.6 | 16.6 | 67.7 | 67.7 |
| Total income | 1,433.7 | 1,431.5 | 1,595.4 | 1,599.6 | 6,060.2 | 7,093.6 |
| Finance cost | 129.2 | 147.5 | 150.2 | 150.2 | 577.0 | 610.7 |
| Fees & commission expense | 203.1 | 191.1 | 218.2 | 218.1 | 830.5 | 962.8 |
| Employee cost (incl. ESOP) | 268.6 | 255.5 | 285.4 | 285.4 | 1,095.0 | 1,226.4 |
| Depreciation | 35.1 | 34.8 | 35.3 | 36.8 | 142.0 | 159.1 |
| Other expenses | 472.6 | 344.3 | 381.8 | 456.4 | 1,655.1 | 1,820.6 |
| Impairment | 0.6 | -0.2 | 0.9 | 0.9 | 2.1 | 2.3 |
| Total costs | 1,109.0 | 973.0 | 1,071.8 | 1,147.8 | 4,301.6 | 4,781.9 |
| PBT | 324.7 | 458.5 | 523.6 | 451.8 | 1,758.6 | 2,311.7 |
| Tax | 93.3 | 123.5 | 130.9 | 112.9 | 460.6 | 577.9 |
| PAT | 231.4 | 335.0 | 392.7 | 338.8 | 1,297.9 | 1,733.8 |
| MTF book (average) | 6,137.0 | 7,453.0 | 7,822.4 | 7,848.9 | 7,315.3 | 8,662.9 |

## Valuation

| | Bear | Base | Bull |
|---|---:|---:|---:|
| FY 2027 EPS | 14.19 | 14.19 | 14.19 |
| FY 2027 P/E | 22.00 | 27.00 | 32.00 |
| FY 2027 Price (P/E × EPS) | 312.25 | 383.21 | 454.18 |
| FY 2027 Discounted | 260.21 | 319.34 | 378.48 |
| FY 2027 Upside vs close | -21.4% | -3.5% | +14.3% |
| FY 2028 EPS | 18.96 | 18.96 | 18.96 |
| FY 2028 P/E | 22.00 | 27.00 | 32.00 |
| FY 2028 Price (P/E × EPS) | 417.10 | 511.89 | 606.69 |
| FY 2028 Discounted | 347.58 | 426.58 | 505.57 |
| FY 2028 Target price today | 315.98 | 387.80 | 459.61 |
| FY 2028 Upside vs close | -4.5% | +17.2% | +38.9% |

## Against the workbook

| | Workbook | Model | Change |
|---|---:|---:|---:|
| FY27 PAT (`PAT predictor Q2FY27!L53`) | 1,063.41 | 1,297.95 | +22.1% |
| FY28 PAT (`Angel One - ADR model (A+B)!C27`) | 1,564.86 | 1,733.79 | +10.8% |
| FY28 target today (base) (`!D34`) | 310.91 | 387.80 | +24.7% |

## Valuation: three methods (close ₹331.00 on 2026-11-06)

| ₹ per share | Weight | Bear | Base | Bull |
|---|---:|---:|---:|---:|
| Regression | 20% | 293.07 | 312.26 | 331.45 |
| Ratio analysis | 30% | 300.73 | 345.55 | 390.36 |
| ADR (PAT model) | 50% | 315.98 | 387.80 | 459.61 |
| **Net value** | | **306.82** | **360.01** | **413.20** |
| Upside vs close | | -7.3% | +8.8% | +24.8% |

- Current ADR 19.99 Cr / day: mean of 25 days of Q3 FY 2027 (broking + MTF)
- Regression: price = 9.599 × 45-day ADR + 120.35, R² 0.238, 413 days 2025-03-04 to 2026-11-06
- Ratio: price ÷ 45-day ADR mean 17.283, SD 2.242 (STDEV.P), 413 days
- ADR: the FY 2028 target price today above
- P/E band 3m: mean 25.37, SD 1.30, current 26.20 (2026-08-06 to 2026-11-06, 64 days)
- P/E band 6m: mean 28.59, SD 3.92, current 26.20 (2026-05-06 to 2026-11-06, 128 days)
- P/E band 1y: mean 29.18, SD 3.23, current 26.20 (2025-11-06 to 2026-11-06, 248 days)
- P/E band 2y: mean 24.73, SD 5.69, current 26.20 (2024-11-06 to 2026-11-06, 494 days)
- P/E band 3y: mean 23.65, SD 5.33, current 26.20 (2023-11-06 to 2026-11-06, 739 days)
- P/E band apr25: mean 26.51, SD 4.77, current 26.20 (2025-04-01 to 2026-11-06, 396 days)

## Rules (projected periods)

- FY 2028 · Broking ADR: 20-day broking ADR 14.992 × average of (1 + 3.0%)^2..^5 = 16.635 a day × 247 days
- FY 2028 · Broking revenue: 20-day broking ADR 14.992 × average of (1 + 3.0%)^2..^5 = 16.635 a day × 247 days
- FY 2028 · Depository income: FY27 × broking growth
- FY 2028 · Depreciation: FY27 × (1 + 12%)
- FY 2028 · Distribution income: FY27 × (1 + 20%)
- FY 2028 · Employee cost (incl. ESOP): FY27 × (1 + 12%)
- FY 2028 · Fees & commission expense: 23.43% of broking
- FY 2028 · Finance cost: FY27 577.0 + 9.0% × new borrowing 374 (book 8,663 − 7,315, less 75% of FY27 PAT 1297.9, not below 0)
- FY 2028 · Impairment: FY27 × (1 + 10%)
- FY 2028 · MTF income: 20-day MTF ADR 4.738 × average of (1 + 3.0%)^2..^5 = 5.257 a day × 247 days
- FY 2028 · Other income: FY27
- FY 2028 · Other expenses: FY27 × (1 + 10%)
- FY 2028 · Other interest income (treasury): FY27 × (1 + 15%)
- Q3 FY 2027 · Broking revenue: engine daily broking to 2026-11-06 (25 days) + 36.7 days × 20-day ADR 14.992
- Q3 FY 2027 · Depository income: 40% × cash broking 128.7
- Q3 FY 2027 · Depreciation: same quarter last year × (1 + 12%)
- Q3 FY 2027 · Distribution income: previous quarter × (1 + 5%)
- Q3 FY 2027 · Employee cost (incl. ESOP): FY26 quarterly average × (1 + 7%)
- Q3 FY 2027 · Fees & commission expense: 23.43% of broking (last 4 reported quarters)
- Q3 FY 2027 · Finance cost: previous 147.5 + 9.0%/4 × new borrowing 118 (book 7,822 − 7,453, less 75% of previous PAT 335.0, not below 0)
- Q3 FY 2027 · Impairment: FY26 quarterly average × (1 + 10%)
- Q3 FY 2027 · MTF income: engine daily MTF to 2026-11-06 (25 days) + 36.7 days × 20-day ADR 4.738
- Q3 FY 2027 · Other income: average of the last 4 reported quarters
- Q3 FY 2027 · Other expenses: same quarter last year × (1 + 10%)
- Q3 FY 2027 · Other interest income (treasury): previous quarter × (1 + 0%)
- Q4 FY 2027 · Broking revenue: 60.3 days × 20-day ADR 14.992 × (1 + 3.0%)^1
- Q4 FY 2027 · Depository income: 40% × cash broking 129.2
- Q4 FY 2027 · Depreciation: same quarter last year × (1 + 12%)
- Q4 FY 2027 · Distribution income: previous quarter × (1 + 5%)
- Q4 FY 2027 · Employee cost (incl. ESOP): FY26 quarterly average × (1 + 7%)
- Q4 FY 2027 · Fees & commission expense: 23.43% of broking (last 4 reported quarters)
- Q4 FY 2027 · Finance cost: previous 150.2 + 9.0%/4 × new borrowing 0 (book 7,849 − 7,822, less 75% of previous PAT 392.7, not below 0)
- Q4 FY 2027 · Impairment: FY26 quarterly average × (1 + 10%)
- Q4 FY 2027 · MTF income: 60.3 days × 20-day ADR 4.738 × (1 + 3.0%)^1
- Q4 FY 2027 · Other income: average of the last 4 reported quarters
- Q4 FY 2027 · Other expenses: same quarter last year × (1 + 10%)
- Q4 FY 2027 · Other interest income (treasury): previous quarter × (1 + 0%)
