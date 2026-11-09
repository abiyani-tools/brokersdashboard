# PAT model — GROWW (dry run) · ADR run 0f2f11bf as of 2026-11-06

Shares 623.90 Cr · close ₹215.08 (2026-11-06) · other exp ÷ broking 33.61% (quarters Q3 FY 2026, Q4 FY 2026, Q1 FY 2027, Q2 FY 2027)

| Rs Cr | Q1 FY27 A | Q2 FY27 A | Q3 FY27 E | Q4 FY27 E | FY 2027 E | FY 2028 E |
|---|---:|---:|---:|---:|---:|---:|
| Trading days |  |  | 61.7 | 60.3 |  | 247.0 |
| Broking revenue | 1,133.6 | 1,053.7 | 1,217.0 | 1,184.6 | 4,588.9 | 5,359.7 |
| MTF income | 123.9 | 155.6 | 149.9 | 153.5 | 582.9 | 694.6 |
| Float income | 130.1 | 129.4 | 149.5 | 145.5 | 554.4 | 637.6 |
| PL + LAS (lending) | 85.2 | 90.9 | 95.4 | 100.2 | 371.7 | 557.6 |
| Other operating income | 28.6 | 71.9 | 75.5 | 79.3 | 255.3 | 383.0 |
| Other income | 47.2 | 39.0 | 40.4 | 40.4 | 167.0 | 167.0 |
| Total income | 1,548.7 | 1,540.5 | 1,727.6 | 1,703.4 | 6,520.2 | 7,799.4 |
| Finance cost | 7.3 | 4.7 | 1.7 | 1.7 | 15.4 | 15.4 |
| Employee cost (incl. ESOP) | 182.0 | 168.9 | 190.7 | 190.7 | 732.4 | 842.2 |
| Depreciation | 17.6 | 18.2 | 26.9 | 26.9 | 89.6 | 103.1 |
| Other expenses | 348.7 | 364.1 | 409.1 | 398.2 | 1,520.1 | 1,801.6 |
| Total costs | 555.7 | 555.9 | 628.4 | 617.5 | 2,357.5 | 2,762.3 |
| PBT | 992.3 | 983.9 | 1,099.2 | 1,085.9 | 4,161.3 | 5,037.1 |
| Tax | 257.2 | 259.2 | 274.8 | 271.5 | 1,062.7 | 1,259.3 |
| PAT | 735.0 | 724.7 | 824.4 | 814.4 | 3,098.6 | 3,777.9 |
| MTF book (average) | 3,306.0 | 4,152.0 | 4,000.2 | 4,096.3 | 3,888.6 | 4,633.5 |

## Valuation

| | Bear | Base | Bull |
|---|---:|---:|---:|
| FY 2027 EPS | 4.97 | 4.97 | 4.97 |
| FY 2027 P/E | 44.30 | 50.00 | 55.70 |
| FY 2027 Price (P/E × EPS) | 220.01 | 248.32 | 276.63 |
| FY 2027 Discounted | 183.35 | 206.94 | 230.53 |
| FY 2027 Upside vs close | -14.8% | -3.8% | +7.2% |
| FY 2028 EPS | 6.06 | 6.06 | 6.06 |
| FY 2028 P/E | 44.30 | 50.00 | 55.70 |
| FY 2028 Price (P/E × EPS) | 268.24 | 302.76 | 337.27 |
| FY 2028 Discounted | 223.54 | 252.30 | 281.06 |
| FY 2028 Target price today | 203.22 | 229.36 | 255.51 |
| FY 2028 Upside vs close | -5.5% | +6.6% | +18.8% |

## Against the workbook

| | Workbook | Model | Change |
|---|---:|---:|---:|
| FY27 PAT (`PAT predictor Q2FY27!AC51`) | 3,021.36 | 3,098.60 | +2.6% |
| FY28 PAT (`Groww - ADR Model!C28`) | 4,115.26 | 3,777.86 | -8.2% |
| FY28 target today (base) (`!D35`) | 220.86 | 229.36 | +3.8% |

## Valuation: three methods (close ₹215.08 on 2026-11-06)

| ₹ per share | Weight | Bear | Base | Bull |
|---|---:|---:|---:|---:|
| Regression | 20% | 192.20 | 201.05 | 209.90 |
| Ratio analysis | 30% | 200.82 | 221.01 | 241.19 |
| ADR (PAT model) | 50% | 203.22 | 229.36 | 255.51 |
| **Net value** | | **200.29** | **221.19** | **242.09** |
| Upside vs close | | -6.9% | +2.8% | +12.6% |

- Current ADR 23.31 Cr / day: mean of 25 days of Q3 FY 2027 (broking + MTF)
- Regression: price = 3.796 × 45-day ADR + 112.54, R² 0.074, 200 days 2026-01-14 to 2026-11-06
- Ratio: price ÷ 45-day ADR mean 9.480, SD 0.866 (STDEV.P), 200 days
- ADR: the FY 2028 target price today above

## Rules (projected periods)

- FY 2028 · Broking ADR: 45-day broking ADR 18.898 × average of (1 + 4.0%)^2..^5 = 21.699 a day × 247 days
- FY 2028 · Broking revenue: 45-day broking ADR 18.898 × average of (1 + 4.0%)^2..^5 = 21.699 a day × 247 days
- FY 2028 · Depreciation: FY27 × (1 + 15%)
- FY 2028 · Employee cost (incl. ESOP): FY27 × (1 + 15%)
- FY 2028 · Finance cost: FY27 15.4 + 8.0% × new borrowing 0 (book 4,634 − 3,889, less 75% of FY27 PAT 3098.6, not below 0)
- FY 2028 · Float income: FY27 × (1 + 15%)
- FY 2028 · PL + LAS (lending): FY27 × (1 + 50%)
- FY 2028 · MTF income: 45-day MTF ADR 2.449 × average of (1 + 4.0%)^2..^5 = 2.812 a day × 247 days
- FY 2028 · Other income: FY27
- FY 2028 · Other expenses: 33.61% of broking
- FY 2028 · Other operating income: FY27 × (1 + 50%)
- Q3 FY 2027 · Broking revenue: engine daily broking to 2026-11-06 (25 days) + 36.7 days × 45-day ADR 18.898
- Q3 FY 2027 · Depreciation: Q4 FY26 × (1 + 10%)
- Q3 FY 2027 · Employee cost (incl. ESOP): Q4 FY26 × (1 + 10%)
- Q3 FY 2027 · Finance cost: previous 4.7 + 8.0%/4 × new borrowing -152 (book 4,000 − 4,152, less 75% of previous PAT 724.7, not below 0)
- Q3 FY 2027 · Float income: previous quarter × broking growth
- Q3 FY 2027 · PL + LAS (lending): previous quarter × (1 + 5%)
- Q3 FY 2027 · MTF income: engine daily MTF to 2026-11-06 (25 days) + 36.7 days × 45-day ADR 2.449
- Q3 FY 2027 · Other income: average of the last 4 reported quarters
- Q3 FY 2027 · Other expenses: 33.61% of broking (last 4 reported quarters)
- Q3 FY 2027 · Other operating income: previous quarter × (1 + 5%)
- Q4 FY 2027 · Broking revenue: 60.3 days × 45-day ADR 18.898 × (1 + 4.0%)^1
- Q4 FY 2027 · Depreciation: Q4 FY26 × (1 + 10%)
- Q4 FY 2027 · Employee cost (incl. ESOP): Q4 FY26 × (1 + 10%)
- Q4 FY 2027 · Finance cost: previous 1.7 + 8.0%/4 × new borrowing 0 (book 4,096 − 4,000, less 75% of previous PAT 824.4, not below 0)
- Q4 FY 2027 · Float income: previous quarter × broking growth
- Q4 FY 2027 · PL + LAS (lending): previous quarter × (1 + 5%)
- Q4 FY 2027 · MTF income: 60.3 days × 45-day ADR 2.449 × (1 + 4.0%)^1
- Q4 FY 2027 · Other income: average of the last 4 reported quarters
- Q4 FY 2027 · Other expenses: 33.61% of broking (last 4 reported quarters)
- Q4 FY 2027 · Other operating income: previous quarter × (1 + 5%)
