# PAT model — GROWW (dry run) · ADR run 0f2f11bf as of 2026-11-06

Shares 623.90 Cr · close ₹215.08 (2026-11-06) · other exp ÷ broking 33.61% (quarters Q3 FY 2026, Q4 FY 2026, Q1 FY 2027, Q2 FY 2027)

| Rs Cr | Q1 FY27 A | Q2 FY27 A | Q3 FY27 E | Q4 FY27 E | FY 2027 E | FY 2028 E |
|---|---:|---:|---:|---:|---:|---:|
| Trading days |  |  | 61.7 | 60.3 |  | 247.0 |
| Broking revenue | 1,133.6 | 1,053.7 | 1,217.0 | 1,178.9 | 4,583.2 | 5,268.9 |
| MTF income | 123.9 | 155.6 | 149.9 | 152.8 | 582.2 | 682.8 |
| Float income | 130.1 | 129.4 | 149.5 | 144.8 | 553.7 | 636.8 |
| PL + LAS (lending) | 85.2 | 90.9 | 95.4 | 100.2 | 371.7 | 557.6 |
| Other operating income | 28.6 | 71.9 | 75.5 | 79.3 | 255.3 | 383.0 |
| Other income | 47.2 | 39.0 | 40.4 | 40.4 | 167.0 | 167.0 |
| Total income | 1,548.7 | 1,540.5 | 1,727.6 | 1,696.3 | 6,513.1 | 7,696.0 |
| Finance cost | 7.3 | 4.7 | 1.7 | 1.7 | 15.4 | 15.4 |
| Employee cost (incl. ESOP) | 182.0 | 168.9 | 190.7 | 190.7 | 732.4 | 842.2 |
| Depreciation | 17.6 | 18.2 | 26.9 | 26.9 | 89.6 | 103.1 |
| Other expenses | 348.7 | 364.1 | 409.1 | 396.3 | 1,518.2 | 1,771.0 |
| Total costs | 555.7 | 555.9 | 628.4 | 615.6 | 2,355.6 | 2,731.7 |
| PBT | 992.3 | 983.9 | 1,099.2 | 1,080.7 | 4,156.1 | 4,964.3 |
| Tax | 257.2 | 259.2 | 274.8 | 270.2 | 1,061.4 | 1,241.1 |
| PAT | 735.0 | 724.7 | 824.4 | 810.5 | 3,094.7 | 3,723.2 |
| MTF book (average) | 3,306.0 | 4,152.0 | 4,000.2 | 4,076.6 | 3,883.7 | 4,555.0 |

## Valuation

| | Bear | Base | Bull |
|---|---:|---:|---:|
| FY 2027 EPS | 4.96 | 4.96 | 4.96 |
| FY 2027 P/E | 38.00 | 44.00 | 50.00 |
| FY 2027 Price (P/E × EPS) | 188.49 | 218.25 | 248.01 |
| FY 2027 Discounted | 159.73 | 184.96 | 210.18 |
| FY 2027 Upside vs close | -25.7% | -14.0% | -2.3% |
| FY 2028 EPS | 5.97 | 5.97 | 5.97 |
| FY 2028 P/E | 38.00 | 44.00 | 50.00 |
| FY 2028 Price (P/E × EPS) | 226.77 | 262.57 | 298.38 |
| FY 2028 Discounted | 192.18 | 222.52 | 252.86 |
| FY 2028 Target price today | 174.71 | 202.29 | 229.88 |
| FY 2028 Upside vs close | -18.8% | -5.9% | +6.9% |

## Against the workbook

| | Workbook | Model | Change |
|---|---:|---:|---:|
| FY27 PAT (`Groww - ADR Model!C23`) | 2,726.12 | 3,094.69 | +13.5% |
| FY28 PAT (`!C45`) | 3,761.23 | 3,723.21 | -1.0% |
| FY28 target today (base) (`!D52`) | 205.28 | 202.29 | -1.5% |

## Rules (projected periods)

- FY 2028 · Broking ADR: 45-day broking ADR 18.898 × average of (1 + 3.5%)^2..^5 = 21.332 a day × 247 days
- FY 2028 · Broking revenue: 45-day broking ADR 18.898 × average of (1 + 3.5%)^2..^5 = 21.332 a day × 247 days
- FY 2028 · Depreciation: FY27 × (1 + 15%)
- FY 2028 · Employee cost (incl. ESOP): FY27 × (1 + 15%)
- FY 2028 · Finance cost: FY27 15.4 + 8.0% × new borrowing 0 (book 4,555 − 3,884, less 75% of FY27 PAT 3094.7, not below 0)
- FY 2028 · Float income: FY27 × (1 + 15%)
- FY 2028 · PL + LAS (lending): FY27 × (1 + 50%)
- FY 2028 · MTF income: 45-day MTF ADR 2.449 × average of (1 + 3.5%)^2..^5 = 2.764 a day × 247 days
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
- Q4 FY 2027 · Broking revenue: 60.3 days × 45-day ADR 18.898 × (1 + 3.5%)^1
- Q4 FY 2027 · Depreciation: Q4 FY26 × (1 + 10%)
- Q4 FY 2027 · Employee cost (incl. ESOP): Q4 FY26 × (1 + 10%)
- Q4 FY 2027 · Finance cost: previous 1.7 + 8.0%/4 × new borrowing 0 (book 4,077 − 4,000, less 75% of previous PAT 824.4, not below 0)
- Q4 FY 2027 · Float income: previous quarter × broking growth
- Q4 FY 2027 · PL + LAS (lending): previous quarter × (1 + 5%)
- Q4 FY 2027 · MTF income: 60.3 days × 45-day ADR 2.449 × (1 + 3.5%)^1
- Q4 FY 2027 · Other income: average of the last 4 reported quarters
- Q4 FY 2027 · Other expenses: 33.61% of broking (last 4 reported quarters)
- Q4 FY 2027 · Other operating income: previous quarter × (1 + 5%)
