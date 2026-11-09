# PAT model — GROWW (dry run) · ADR run 549741c7 as of 2026-11-03

Shares 623.90 Cr · close ₹207.23 (2026-11-04) · other exp ÷ broking 33.61% (quarters Q3 FY 2026, Q4 FY 2026, Q1 FY 2027, Q2 FY 2027)

| Rs Cr | Q1 FY27 A | Q2 FY27 A | Q3 FY27 E | Q4 FY27 E | FY 2027 E | FY 2028 E |
|---|---:|---:|---:|---:|---:|---:|
| Trading days |  |  | 61.6 | 60.4 |  | 247.0 |
| Broking revenue | 1,133.6 | 1,053.7 | 1,196.5 | 1,159.2 | 4,543.0 | 5,171.8 |
| MTF income | 123.9 | 155.6 | 150.1 | 153.3 | 582.9 | 684.2 |
| Float income | 130.1 | 129.4 | 146.9 | 142.4 | 548.8 | 631.1 |
| PL + LAS (lending) | 85.2 | 90.9 | 95.4 | 100.2 | 371.7 | 557.6 |
| Other operating income | 28.6 | 71.9 | 75.5 | 79.3 | 255.3 | 383.0 |
| Other income | 47.2 | 39.0 | 40.4 | 40.4 | 167.0 | 167.0 |
| Total income | 1,548.7 | 1,540.5 | 1,704.8 | 1,674.7 | 6,468.7 | 7,594.6 |
| Finance cost | 7.3 | 4.7 | 1.8 | 1.8 | 15.5 | 15.5 |
| Employee cost (incl. ESOP) | 182.0 | 168.9 | 190.7 | 190.7 | 732.4 | 842.2 |
| Depreciation | 17.6 | 18.2 | 26.9 | 26.9 | 89.6 | 103.1 |
| Other expenses | 348.7 | 364.1 | 402.2 | 389.6 | 1,504.7 | 1,738.4 |
| Total costs | 555.7 | 555.9 | 621.6 | 609.0 | 2,342.2 | 2,699.3 |
| PBT | 992.3 | 983.9 | 1,083.2 | 1,065.7 | 4,125.0 | 4,895.4 |
| Tax | 257.2 | 259.2 | 270.8 | 266.4 | 1,053.6 | 1,223.8 |
| PAT | 735.0 | 724.7 | 812.4 | 799.3 | 3,071.4 | 3,671.5 |
| MTF book (average) | 3,306.0 | 4,152.0 | 4,004.2 | 4,091.9 | 3,888.5 | 4,564.1 |

## Valuation

| | Bear | Base | Bull |
|---|---:|---:|---:|
| FY 2027 EPS | 4.92 | 4.92 | 4.92 |
| FY 2027 P/E | 38.00 | 44.00 | 50.00 |
| FY 2027 Price (P/E × EPS) | 187.07 | 216.61 | 246.14 |
| FY 2027 Discounted | 158.53 | 183.56 | 208.60 |
| FY 2027 Upside vs close | -23.5% | -11.4% | +0.7% |
| FY 2028 EPS | 5.88 | 5.88 | 5.88 |
| FY 2028 P/E | 38.00 | 44.00 | 50.00 |
| FY 2028 Price (P/E × EPS) | 223.62 | 258.93 | 294.24 |
| FY 2028 Discounted | 189.51 | 219.43 | 249.35 |
| FY 2028 Target price today | 172.28 | 199.48 | 226.69 |
| FY 2028 Upside vs close | -16.9% | -3.7% | +9.4% |

## Against the workbook

| | Workbook | Model | Change |
|---|---:|---:|---:|
| FY27 PAT (`Groww - ADR Model!C23`) | 2,726.12 | 3,071.41 | +12.7% |
| FY28 PAT (`!C45`) | 3,761.23 | 3,671.53 | -2.4% |
| FY28 target today (base) (`!D52`) | 205.28 | 199.48 | -2.8% |

## Rules (projected periods)

- FY 2028 · Broking ADR: 45-day broking ADR 18.550 × average of (1 + 3.5%)^2..^5 = 20.939 a day × 247 days
- FY 2028 · Broking revenue: 45-day broking ADR 18.550 × average of (1 + 3.5%)^2..^5 = 20.939 a day × 247 days
- FY 2028 · Depreciation: FY27 × (1 + 15%)
- FY 2028 · Employee cost (incl. ESOP): FY27 × (1 + 15%)
- FY 2028 · Finance cost: FY27 15.5 + 8.0% × new borrowing 0 (book 4,564 − 3,889, less 75% of FY27 PAT 3071.4, not below 0)
- FY 2028 · Float income: FY27 × (1 + 15%)
- FY 2028 · PL + LAS (lending): FY27 × (1 + 50%)
- FY 2028 · MTF income: 45-day MTF ADR 2.454 × average of (1 + 3.5%)^2..^5 = 2.770 a day × 247 days
- FY 2028 · Other income: FY27
- FY 2028 · Other expenses: 33.61% of broking
- FY 2028 · Other operating income: FY27 × (1 + 50%)
- Q3 FY 2027 · Broking revenue: engine daily broking to 2026-11-03 (22 days) + 39.6 days × 45-day ADR 18.550
- Q3 FY 2027 · Depreciation: Q4 FY26 × (1 + 10%)
- Q3 FY 2027 · Employee cost (incl. ESOP): Q4 FY26 × (1 + 10%)
- Q3 FY 2027 · Finance cost: previous 4.7 + 8.0%/4 × new borrowing -148 (book 4,004 − 4,152, less 75% of previous PAT 724.7, not below 0)
- Q3 FY 2027 · Float income: previous quarter × broking growth
- Q3 FY 2027 · PL + LAS (lending): previous quarter × (1 + 5%)
- Q3 FY 2027 · MTF income: engine daily MTF to 2026-11-03 (22 days) + 39.6 days × 45-day ADR 2.454
- Q3 FY 2027 · Other income: average of the last 4 reported quarters
- Q3 FY 2027 · Other expenses: 33.61% of broking (last 4 reported quarters)
- Q3 FY 2027 · Other operating income: previous quarter × (1 + 5%)
- Q4 FY 2027 · Broking revenue: 60.4 days × 45-day ADR 18.550 × (1 + 3.5%)^1
- Q4 FY 2027 · Depreciation: Q4 FY26 × (1 + 10%)
- Q4 FY 2027 · Employee cost (incl. ESOP): Q4 FY26 × (1 + 10%)
- Q4 FY 2027 · Finance cost: previous 1.8 + 8.0%/4 × new borrowing 0 (book 4,092 − 4,004, less 75% of previous PAT 812.4, not below 0)
- Q4 FY 2027 · Float income: previous quarter × broking growth
- Q4 FY 2027 · PL + LAS (lending): previous quarter × (1 + 5%)
- Q4 FY 2027 · MTF income: 60.4 days × 45-day ADR 2.454 × (1 + 3.5%)^1
- Q4 FY 2027 · Other income: average of the last 4 reported quarters
- Q4 FY 2027 · Other expenses: 33.61% of broking (last 4 reported quarters)
- Q4 FY 2027 · Other operating income: previous quarter × (1 + 5%)
