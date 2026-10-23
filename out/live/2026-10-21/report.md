# Live run (dry run) — as of 2026-10-21

Switches: abcdefghi · E5: pass (0 blocking, 4 warnings, 5 info) · E1 coverage: pass · Summary rows: 1827

Nothing was written to the database.

## Headline (Rs crore per trading day; MTF gross)

| Period | Panel | ADR | vs previous | YoY |
|---|---|---:|---:|---:|
| FY 2027 | Broking | 13.2863 | — | +6.6% |
| FY 2027 | Cash | 1.9849 | — | +15.8% |
| FY 2027 | Commodities | 1.5178 | — | +26.1% |
| FY 2027 | Consolidated | 17.5103 | — | +12.3% |
| FY 2027 | F&O | 9.7836 | — | +2.4% |
| FY 2027 | MTF | 4.2240 | — | +35.5% |
| FY 2027 | MTF (net) | 1.9008 | — | +35.5% |
| FY 2027 October | Broking | 15.4738 | +25.2% | +14.8% |
| FY 2027 October | Cash | 2.0058 | -0.9% | +15.1% |
| FY 2027 October | Commodities | 1.7978 | +16.6% | +31.9% |
| FY 2027 October | Consolidated | 20.2160 | +18.2% | +20.0% |
| FY 2027 October | F&O | 11.6703 | +32.8% | +12.5% |
| FY 2027 October | MTF | 4.7422 | +0.0% | +40.7% |
| FY 2027 October | MTF (net) | 2.1340 | +0.0% | +40.7% |
| Q2 FY 2027 | Broking | 11.9666 | -16.0% | +6.6% |
| Q2 FY 2027 | Cash | 1.9160 | -6.8% | +21.2% |
| Q2 FY 2027 | Commodities | 1.5400 | +7.4% | +48.3% |
| Q2 FY 2027 | Consolidated | 16.4960 | -8.5% | +15.4% |
| Q2 FY 2027 | F&O | 8.5106 | -20.9% | -1.1% |
| Q2 FY 2027 | MTF | 4.5294 | +19.8% | +47.4% |
| Q2 FY 2027 | MTF (net) | 2.0382 | +19.8% | +47.4% |

## E5 integrity report

```
E5: 0 blocking, 4 warning, 5 info
INFO    jump     mcx:contracts 2025-01-01: 406,749 outside 0.2×2,205,346 .. 5.0×7,748,851 — known: 406,749 contracts against a trailing 20-day minimum of 2,205,346; not a special session in sb_calendar; cause not yet sourced (lake-auditor to check against MCX)
WARNING missing  mtf_industry:book_cr 2026-04-08: no value on a trading day
WARNING conflict total_orders FY 2025 January -: seed values disagree; using fact 415 (excel: F&O market!C35) by rule
WARNING conflict total_orders FY 2025 November -: seed values disagree; using fact 413 (excel: F&O market!C33) by rule
WARNING conflict total_orders FY 2026 January -: seed values disagree; using fact 427 (excel: F&O market!C47) by rule
INFO    status   bse_fo:contracts [excel_seed] 2026-09-29..2026-10-21 (15 days): status imputed
INFO    frozen   bse_fo:contracts [excel_seed] 2026-09-28..2026-10-21 (16 days): 18,962,859 repeated 16 days
INFO    jump     mcx:contracts [excel_seed] 2025-01-01: 406,749 outside 0.2×2,205,346 .. 5.0×7,748,851
INFO    missing  mtf_industry:book_cr [excel_seed] 2026-04-08: no value on a trading day
```
