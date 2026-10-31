# Groww: model-implied vs disclosed total orders

Implied orders = the model's daily Groww orders summed over the quarter: F&O (Angel-calibrated market orders x Groww share) + cash (market trades / Angel trades per order x Groww share) + commodity. Disclosed = total broking orders (Stocks + Derivatives; no segment split), KPI Handbook Operational KPIs row 10, latest handbook (Q2 FY27). Mn orders.

"Parity" = the workbook (no switches). "Live" = switches abcdefg. The shares are on the legacy basis (denominator = exchange turnover) in both, as in the workbook. "Live, new-basis shares" halves the F&O and cash orders: the share on Groww's published basis (denominator = exchange turnover x 2).

| Quarter | Disclosed | Parity: F&O | cash | comm | total | gap | Live: F&O | cash | comm | total | gap | Live, new-basis shares: total | gap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Q3 FY 2025 | 454.2 | — | — | — | — | not live | — | — | — | — | not live | — | — |
| Q4 FY 2025 | 357.7 | — | — | — | — | not live | — | — | — | — | not live | — | — |
| Q1 FY 2026 | 378.6 | — | — | — | — | not live | 165.7 | 98.3 | 0.0 | 264.1 | -30.2% | 132.0 | -65.1% |
| Q2 FY 2026 | 415.7 | 206.1 | 100.7 | 0.0 | 306.8 | -26.2% | 206.1 | 100.7 | 0.0 | 306.8 | -26.2% | 153.4 | -63.1% |
| Q3 FY 2026 | 474.2 | 230.5 | 107.0 | 21.9 | 359.4 | -24.2% | 230.5 | 107.0 | 19.8 | 357.3 | -24.7% | 188.5 | -60.2% |
| Q4 FY 2026 | 587.4 | 306.1 | 122.3 | 26.5 | 455.0 | -22.5% | 306.1 | 122.3 | 33.8 | 462.2 | -21.3% | 248.0 | -57.8% |
| Q1 FY 2027 | 560.2 | 299.4 | 116.3 | 25.4 | 441.1 | -21.3% | 295.9 | 116.3 | 35.3 | 447.4 | -20.1% | 241.4 | -56.9% |
| Q2 FY 2027 | 517.3 | 259.7 | 132.2 | 34.9 | 426.8 | -17.5% | 258.9 | 134.8 | 44.4 | 438.1 | -15.3% | 241.2 | -53.4% |

Q3 FY25 and Q4 FY25: F&O and cash are zero-filled in the workbook and stay so (no backfill before 1 Apr 2025); commodities are blank before 1 Oct 2025, so the commodity column is 0 up to Q2 FY26 and the Q3 FY26 value is the first live quarter. Q3 FY27 is partial (13 trading days) and has no disclosure yet.
