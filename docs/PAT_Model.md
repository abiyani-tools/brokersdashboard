# PAT model (PLAN 5.7): Angel One and Groww

Design approved by AB on 5 Nov 2026. Code: `src/engine/pat.py` (model), `run_pat.py` (runner), `src/extract/pl_angel.py` /
`pl_groww.py` (filed P&L), `seed/pat_assumptions.json` → `seed/build_pat_db_rows.py` (DB rows), `tests/test_pat.py`.
Output table: `sb_pat_lines` (`migrations/20261105_sb_pat_lines.sql`). Rs Cr throughout; Indian FY.

## 1. What it does

1. **Reported quarters** are the filed consolidated P&L, split into the model's lines:
   - Angel One (investor presentation P&L table, Rs Mn): broking = (F&O + cash + commodity revenue mix) × total income;
     depository and distribution from the revenue mix; MTF = average client funding book × yield ÷ 4; treasury =
     interest income − MTF; other = the rest. Employee cost includes the ESOP expense line (as the workbook does).
   - Groww (results statement): broking, MTF, float, PL + LAS from its revenue mix × total income; other operating =
     the residual; other income as filed. No depository or fees & commission line exists.
2. **Projected quarters (rest of FY27)**, sequentially:

   | Line | Rule |
   |---|---|
   | Broking, MTF (and Angel's cash, for depository) | engine daily revenue to the run's date + remaining days × the broker's ADR (Angel 20-day, Groww 45-day); each later quarter × (1 + quarterly ADR growth: Angel 3%, Groww 3.5%) |
   | Remaining days | 247 − FY27 days already traded, split across the quarters by weekdays (workbook's 247) |
   | Depository (Angel) | 40% × cash broking |
   | Distribution (Angel); PL + LAS, other operating (Groww) | previous quarter × (1 + 5%) |
   | Treasury (Angel) | previous quarter (flat) · Float (Groww): previous quarter × broking growth |
   | Other income | average of the last 4 reported quarters |
   | **MTF book** | MTF income ÷ (yield ÷ 4) |
   | **Finance cost** | previous + funding rate ÷ 4 × new borrowing; new borrowing = book growth less 75% of the previous quarter's PAT, not below 0 (a shrinking book repays borrowing); cost not below 0 |
   | **Fees & commission (Angel)** | (fees ÷ broking over the last 4 reported quarters) × projected broking |
   | **Other expenses (Groww)** | (other expenses ÷ broking over the last 4 reported quarters) × projected broking |
   | Employee | Angel: FY26 quarterly average × 1.07 · Groww: Q4 FY26 × 1.10 |
   | Depreciation | Angel: same quarter last year × 1.12 · Groww: Q4 FY26 × 1.10 |
   | Other expenses (Angel) | same quarter last year × 1.10 |
   | Impairment (Angel) | FY26 quarterly average × 1.10 |
   | Tax | 25% of PBT |

3. **FY27E** = the four quarters. **FY28E**: broking and MTF ADR continue the quarterly growth path (Q1 FY28 is two
   quarters after the current one, so × (1 + g)^2 … Q4 FY28 × (1 + g)^5; FY28 ADR = the average of the four) × 247 days
   (AB, 5 Nov 2026; replaces the workbook's FY28 growth of 27% broking / 35% or 50% MTF); depository with broking; distribution / lending / other
   operating × (1 + 20% / 50%); treasury / float × 1.15; finance cost, fees & commission and Groww's other expenses
   by the same linked rules as FY27; employee, depreciation, other expenses as the workbook (× 1.12 / 1.15 / 1.10).
4. **Valuation** (FY27 and FY28): EPS = PAT ÷ shares; price = P/E × EPS (Angel 18 / 22.5 / 27, Groww 38 / 44 / 50);
   discounted 18%; FY28 a second step to today (Angel 9%, Groww 10%); upside vs the latest close.

Output rows also carry the divisor and price behind the valuation (lines `shares` and `close`, per valuation year), so
the dashboard needs no other table. Dashboard: ExchangesDash Brokers → PAT Predictor (`js/33-brokers-pat.js`, view
`/api/brokers?view=pat`), which shows these rows as published.

Every parameter is an `sb_assumptions` row (key `pat_*`) naming its workbook cell; change it there, not in code.
Every output row carries its rule in words with the numbers it used.

## 2. Fixes against the workbook

| Workbook | Model |
|---|---|
| FY27 = today's ADR × 247 days (`ADR model` sheets), H1 actuals ignored | FY27 = reported Q1–Q2 + projected Q3–Q4 |
| Costs typed from the `PAT predictor` FY27 / FY28 totals | rebuilt quarter by quarter from the filed lines with the same rules |
| Fees & commission = FY26 ratio to broking × (broking + distribution); FY28 by growth | ratio to broking (last 4 quarters) × projected broking, every period |
| Finance cost: Angel Q2 built off Q4 FY26 (skips Q1); FY28 ignores retained profit; Groww FY27 excludes it, FY28 includes it at 8.5% | one rule for both brokers and both years (above) |
| Groww other income = Angel One's depository + distribution | Groww's own filed other income |
| Groww other expenses: FY26 × 1.13 | scale with broking revenue (no fees & commission line to link) |
| FY28 ADR = 20- or 45-day ADR × (1 + 27%) broking, × (1 + 35% / 50%) MTF | quarterly ADR growth (Angel 3%, Groww 3.5%) compounding from today's ADR through Q4 FY28 |
| ADR to 24–25 Sep, CMP and shares from Excel's stock data type | the latest published ADR run, `sb_share_prices`, shares from the filings |

## 3. Data

- **Facts** (`sb_disclosure_facts`, segment `consolidated`, status `staged` until AB reviews; `out/pat/facts_review.md`):
  - Groww: results statements Q3 FY25 – Q2 FY27 (overlapping filings agree to ±0.06 Cr). Shares = paid-up capital ÷
    face value (1,247.81 ÷ 2 = 623.905 Cr, Q2 FY27 filing).
  - Angel One: presentation P&L tables (Q1 FY27 and Q2 FY27 decks); Q3 FY26 = FY26 − Q1 − Q2 − Q4 (derived). Shares =
    net worth ÷ book value per share (67,124 Mn ÷ 73.4 = 91.45 Cr) **[DERIVED: replace with the shareholding-pattern
    count]**. Revenue mix and funding book: the existing facts (Q3 FY26 funding book and older mix rows are staged).
- **Not modelled:** Groww's share of its associate's loss (≈ Rs 0.7 Cr a quarter) and Angel's prior-year tax lines.

## 4. Running

```
python3 -m src.extract.pl_angel > out/pat/facts_angel_pl.json
python3 -m src.extract.pl_groww > out/pat/facts_groww_pl.json
python3 run_pat.py                      # dry run on local inputs (out/pat/dev: the published run from /api/brokers)
python3 seed/build_pat_db_rows.py       # → out/pat/db_inputs.sql (assumptions + staged facts) and facts_review.md
python3 run_pat.py --db [--publish]     # CI: latest live run, reviewed facts, sb_pat_lines
```

To go live: (1) apply `migrations/20261105_sb_pat_lines.sql`, (2) apply `out/pat/db_inputs.sql`, (3) review the staged
facts, (4) notify the ExchangesDash owner (mirror schema), (5) the daily job then publishes after each ADR run.
