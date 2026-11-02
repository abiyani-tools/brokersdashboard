# Live run (dry run) · MOSL — as of 2026-10-21

Switches: m-abcdef · E5: pass (0 blocking, 1 warnings, 5 info) · E1 coverage: pass · Summary rows: 1566

Nothing was written to the database.

## Headline (Rs crore per trading day; net brokerage + MTF NII)

| Period | Panel | ADR | vs previous | YoY |
|---|---|---:|---:|---:|
| FY 2027 | Broking | 4.4405 | — | +2.1% |
| FY 2027 | Cash | 2.0352 | — | +7.8% |
| FY 2027 | Commodities | 0.5338 | — | -11.5% |
| FY 2027 | Consolidated | 8.7183 | — | +13.8% |
| FY 2027 | F&O | 1.8715 | — | +0.7% |
| FY 2027 | MTF | 4.2778 | — | +29.1% |
| FY 2027 October | Broking | 4.9188 | +14.5% | +7.3% |
| FY 2027 October | Cash | 1.9370 | -2.4% | +10.6% |
| FY 2027 October | Commodities | 0.6492 | +6.8% | -7.7% |
| FY 2027 October | Consolidated | 9.8765 | +6.9% | +19.7% |
| FY 2027 October | F&O | 2.3326 | +36.8% | +9.5% |
| FY 2027 October | MTF | 4.9577 | +0.4% | +35.4% |
| Q2 FY 2027 | Broking | 4.2480 | -6.5% | +9.4% |
| Q2 FY 2027 | Cash | 2.0313 | -1.4% | +19.7% |
| Q2 FY 2027 | Commodities | 0.5221 | +0.3% | +17.6% |
| Q2 FY 2027 | Consolidated | 8.9671 | +9.4% | +20.1% |
| Q2 FY 2027 | F&O | 1.6946 | -13.7% | -2.7% |
| Q2 FY 2027 | MTF | 4.7191 | +29.2% | +31.7% |

MOSL needs nothing from the Angel One calibration. As of 2026-10-21 (limited by mcx:contracts): 110 inputs come from 110 reviewed data-book facts; the rest are the workbook's. Basis: net brokerage of retail + PWM (Consolidated net brokerage; excludes Capital Markets) plus MTF net interest income. MTF yield: the workbook's typed values, carried at 12.94% ([SOURCE NEEDED: MOSL does not publish an MTF yield]).

## E5 integrity report

```
E5: 0 blocking, 1 warning, 5 info
INFO    jump     mcx:contracts 2025-01-01: 406,749 outside 0.2×2,205,346 .. 5.0×7,748,851 — known: 406,749 contracts against a trailing 20-day minimum of 2,205,346: New Year's Day, MCX traded the morning session only (evening session from 5 pm closed; Zerodha bulletin 31 Dec 2024). Genuine thin day, not a data error; not marked special in sb_calendar, so it stays in the commodity averages
WARNING missing  mtf_industry:book_cr 2026-04-08: no value on a trading day
INFO    status   bse_fo:contracts [excel_seed] 2026-09-29..2026-10-21 (15 days): status imputed
INFO    frozen   bse_fo:contracts [excel_seed] 2026-09-28..2026-10-21 (16 days): 18,962,859 repeated 16 days
INFO    jump     mcx:contracts [excel_seed] 2025-01-01: 406,749 outside 0.2×2,205,346 .. 5.0×7,748,851
INFO    missing  mtf_industry:book_cr [excel_seed] 2026-04-08: no value on a trading day
```
