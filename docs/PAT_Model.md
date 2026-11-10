# PAT model (PLAN 5.7): Angel One and Groww

Design approved by AB on 5 Nov 2026. Code: `src/engine/pat.py` (model), `run_pat.py` (runner), `src/extract/pl_angel.py` /
`pl_groww.py` (filed P&L), `seed/pat_assumptions.json` → `seed/build_pat_db_rows.py` (DB rows), `tests/test_pat.py`;
`src/engine/pat_kit.py` (the page's recompute, reference) and `tests/test_pat_kit.py` (10 Nov 2026, section 5).
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
   | Broking, MTF (and Angel's cash, for depository) | engine daily revenue to the run's date + remaining days × the start ADR (step 0, the **start rule** below); each later quarter × (1 + quarterly ADR growth g: Angel 3%, Groww 4%) |
   | **Start rule** (AB, 10 Nov 2026) | start ADR (broking, MTF gross, cash) = the current quarter's engine revenue so far ÷ its engine days so far (QTD); if the current quarter has fewer than 5 engine days, the previous quarter's full-quarter ADR. Replaces the 20-day (Angel) / 45-day (Groww) window; `pat_adr_window_fy27` is no longer read. The 45-day average is published as a reference row only |
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
4. **Valuation** (FY27 and FY28): EPS = PAT ÷ shares; price = P/E × EPS (`pat_pe`: Angel 22 / 27 / 32, Groww
   44.3 / 50 / 55.7); discounted by `pat_discount_fwd` (20%); FY28 a second step to today (`pat_discount_today`, 10%);
   upside vs the latest close. The FY 2028 base target today is the ADR leg of the valuation (`src/engine/valuation.py`).

Output rows also carry the divisor and price behind the valuation (lines `shares` and `close`, per valuation year), so
the dashboard needs no other table. Dashboard: ExchangesDash Brokers → PAT Predictor (`js/33-brokers-pat.js`, view
`/api/brokers?view=pat`); from 10 Nov 2026 the page recomputes from the published rows (section 5).

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
| FY28 ADR = 20- or 45-day ADR × (1 + 27%) broking, × (1 + 35% / 50%) MTF | quarterly ADR growth (Angel 3%, Groww 4%) compounding from the current quarter's QTD ADR through Q4 FY28 |
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

To go live: (1) ✅ apply `migrations/20261105_sb_pat_lines.sql` (6 Nov), (2) ✅ apply `out/pat/db_inputs.sql` (6 Nov),
(3) review the staged facts: evidence `out/pat/review_check/check_report.md`, SQL `out/pat/review_apply.sql` (draft), (4) merge PR #6,
(5) notify the ExchangesDash owner (`docs/Prompt_for_ExchangesDash_owner_sb_pat_lines.md`; dashboard tab already merged, #57 / #58),
(6) the daily job then publishes after each ADR run. Workbook cross-check: `out/pat/<as_of>/workbook_crosscheck.md`.

## 5. PAT Predictor page: ADR build-up, top block, inputs and the recompute kit (10 Nov 2026)

AB's restructure of the Brokers → PAT Predictor tab: (1) ADR build-up from the current quarter's consolidated ADR with
one input, the QoQ growth g; (2) the FY 2028 PAT predictor (Bear / Base / Bull differ only in P/E) with editable inputs;
(3) the quarterly and 3-year P&L. Edits on the page are not saved; the engine publishes the defaults. Contract:
`pat_contract/CONTRACT.md` (session scratchpad, 10 Nov 2026).

**Consolidated ADR** = broking ADR + MTF gross ADR. **Build-up** (`adr_consol`, Rs Cr / day): each quarter from the
current one to Q4 FY 2028 = (b0 + m0) × (1 + g)^step, where step = quarters after the current one (`k_step`); the current
quarter (step 0) is its QTD ADR (start rule, section 1). FY 2028 `adr_consol` = (b0 + m0) × the average of
(1 + g)^step over Q1–Q4 FY 2028 = FY28 broking ADR + FY28 MTF ADR.

**Top block** (FY 2026, FY 2027, FY 2028; adds up to total income exactly):

| Line | Angel One | Groww |
|---|---|---|
| `op_revenue` Operating revenue | broking + MTF | broking + MTF |
| `treasury_rev` Treasury revenue | `treasury` (other interest income) | `float` |
| `other_inc` Other income | total income − operating − treasury = depository + distribution + other | = PL + LAS + other operating + other income |

FY 2028 operating revenue = FY 2028 `adr_consol` × FY28 trading days, the same number as broking + MTF in the P&L.

**New `sb_pat_lines` rows** (no column change; scenario '' unless stated):

| period_key | line | value |
|---|---|---|
| `FY 2026` | every P&L line the quarters carry, `pat_margin` | sum of the filed Q1–Q4 FY 2026 (MTF book: average); regime actual, rule `filed: Q1–Q4 FY 2026` |
| `FY 2026` / `FY 2027` / `FY 2028` | `op_revenue`, `treasury_rev`, `other_inc` | the top block |
| current quarter … `Q4 FY 2028`, `FY 2028` | `adr_consol` | the build-up (sort 800) |
| each build-up and projected FY27 quarter | `k_step` | step (power of 1 + g) |
| `inputs` | `adr_45dma` | mean of the last 45 engine days of broking + MTF (reference only) |
| `inputs` | `in_qoq_growth`; `in_pe` (scenario bear / base / bull); `in_discount_fwd`, `in_discount_today` | the page's input defaults (`pat_adr_qoq_growth`, `pat_pe`, `pat_discount_fwd`, `pat_discount_today`) |
| `inputs` | `k_tax`, `k_retention`, `k_funding_rate`, `k_mtf_yield`, `k_fy28_days`, `k_dist_growth_fy28`, `k_treasury_growth_fy28` | the assumptions build() used |
| `inputs` | `k_adr_broking0`, `k_adr_mtf0`, `k_adr_cash0` | the start ADRs (b0, m0, c0) |
| `inputs` | Angel `k_dep_share_of_cash`, `k_fee_ratio`; Groww `k_oexp_ratio` | as build() |
| `inputs` | `k_prev_finance`, `k_prev_mtf_book`, `k_prev_pat`, `k_prev_broking` (+ Groww `k_prev_float`) | the quarter before the first projected quarter |
| each projected FY27 quarter | `k_sofar_broking`, `k_sofar_mtf`, `k_sofar_cash`, `k_rem_days` | engine revenue already in the quarter; remaining days given to it |

`k_*`, `in_*` and `adr_45dma` rows have sort_order ≥ 1000, so the page never lists them as P&L lines.

**Recompute kit** (`src/engine/pat_kit.py`): `kit_from_rows(rows)` reads the published rows (as the API returns them);
`recompute(kit, g, pe, disc, today)` returns every published line (P&L of the projected quarters, FY 2027, FY 2028,
top block, build-up, valuation of FY 2027 and FY 2028) for the reader's inputs, following the contract's pseudocode
line for line: projected quarters in order (broking / MTF / cash = so far + remaining days × start ADR × (1 + g)^step;
Angel depository = share × cash, Groww float = previous float × broking growth; finance from the MTF book with the
retained-PAT rule; Angel fees & commission and Groww other expenses × broking; g-independent lines as published), FY27
= the four quarters, FY28 as section 1, then top block and valuation. The JavaScript page ports it; at the published
defaults it must reproduce every published line (`tests/test_pat_kit.py`: abs 1e-6 at the defaults, at g ± 0.01 against
a rebuild of `build()`, and at other P/E and discount rates, for both brokers and for the < 5-day fallback). FY 2027's
valuation has one discount step (target = discounted price), as build() publishes it.
