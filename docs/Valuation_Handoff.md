# Valuation tab (PLAN 5.8) — handoff, 9 Nov 2026

Engine work is committed on branch `feat/valuation` (from main `1b281a0`). The dashboard branch `brokers-valuation`
in `../exchangesdash-valuation` is not committed or pushed yet. **Nothing is applied to any DB.**

## What AB asked for (9 Nov)
- A **Valuation** tab for Angel One and Groww, based on the 09.11 workbook
  (`../New Model - 09.11.26/20260714_brokers dashboard v2.xlsx`, sheets `Angel One - ADR model (A+B)` and `Groww - ADR Model`).
- Net value = triangulation of three methods: **Regression, Ratio, ADR**. The ADR leg comes from the PAT predictor
  (our live PAT model, `sb_pat_lines` FY 2028 `target_today`).
- The charts of those two sheets (Angel 6, Groww 4).
- Mid-build addition: a **timeline input** with 3M, 6M, 1Y, 2Y, 3Y and Since Apr 2025.

## Decisions AB approved ("Yes, go with those", 9 Nov)
1. Weights are 20 / 30 / 50 (regression / ratio / ADR) for both brokers, as a SUMPRODUCT. The Angel sheet's plain AVERAGE is replaced.
   - Angel base: 0.2×316.53 + 0.3×354.05 + 0.5×349.77 = 344.41 (the sheet shows 340.12).
2. The Ratio leg is a current value: ratio × the Q3 FY27 ADR, not discounted. The Angel label "Target Price FY28" is stale.
3. "Current ADR" = the mean daily ADR (broking + MTF) over the days so far in the latest quarter (`SUMMARY - <broker>!C11`).
4. Regression and ratio windows run from the series start to today (Angel series from 2025-01-01, fit from 2025-03-04;
   Groww series from 2025-11-12, fit from 2026-01-14).
   - Plus the timeline windows (see below). "All" is the workbook's window and is the default.
5. Adopt the 09.11 P/E and growth inputs:
   - Angel P/E 20/24/28 → 22/27/32
   - Groww P/E 38/44/50 → 44.3/50/55.7
   - Groww quarterly ADR growth 3.5% → 4%
6. Angel's P/E band charts use our own consolidated TTM P/E: close × quarter-end shares ÷ TTM consolidated PAT, with each
   quarter counting from its results date. It is checked against the vendor column `Angel One Ltd.1!K`.
7. The sell-side consensus block in the Groww sheet (G27:J30) is left out (rule 1).
8. New table `sb_valuation_lines` (migration), a `/api/brokers?view=valuation` API view, and a tab in the ExchangesDash fork.

## Done
### Engine (this repo, branch `feat/valuation`)
- **`src/engine/valuation.py`:**
  - `adr_series`, `build_daily` (45-day average and ratio)
  - `current_adr`
  - `regression` (Excel SLOPE / INTERCEPT / RSQ) and `ratio` (mean, STDEV.P)
  - `triangulate`
  - `ttm_pe`, `pe_quarters` (reads `val_results_dates` and metric `shares_period_end_cr`), `pe_bands` (STDEV.S)
  - `WINDOWS` (all, 3m, 6m, 1y, 2y, 3y, apr25): a window is published only if the data cover it (10-day slack)
  - `build()`, and `lines()` → `sb_valuation_lines` rows. Sections: summary / inputs (per window), common, weights,
    series, pe, pe_bands (per window).
- **`tests/test_valuation.py` and `tests/fixtures/valuation_wb_0911.json`** (the workbook's own daily ADR, prices and cells).
  The engine reproduces the workbook exactly:
  - regression slope / intercept / R², every day's 45-day ADR, ratio and implied price
  - ratio mean / SD
  - Groww's net E74:G74
  - Angel's P/E band means and SDs
  - 7 tests pass.
- **`run_pat.py`:**
  - calls the valuation after the PAT model (`valuation()`, `local_history()` for Angel's P/E history)
  - `--publish` also upserts `sb_valuation_lines`, and only warns if the table is missing
  - the report gets a "Valuation: three methods" section
  - `db_inputs` now returns the whole price list and reads `val_*` assumptions
- **`tests/test_pat.py`:** updated for Groww's 4% growth and the new `db_inputs` return value.
- **Seeds:**
  - `seed/pat_assumptions.json`: point 5 changes, sourced to the 09.11 workbook.
  - New `seed/valuation_assumptions.json`: 7 `val_*` keys (weights, band, DMA days, P/E window start, series start per
    broker, Angel results dates).
- **`migrations/20261109_sb_valuation_lines.sql`:** DRAFT, NOT APPLIED.
- **`out/valuation/db_inputs.sql`:** DRAFT, NOT APPLIED.
  - Step 1: `val_*` assumptions.
  - Step 2: P/E and Groww growth updates.
  - Step 3: 27 staged Angel facts: pl_pat Q4 FY22 to Q4 FY25, and `shares_period_end_cr` Q3 FY23 to Q2 FY27 on the Re 1 basis.
  - Step 4 (commented out): mark those facts reviewed. The engine reads reviewed facts only.
- **Angel P/E history** from the filing-extractor: `out/pat/facts_angel_pat_history.json` / `.md`, with PDFs and SHA256SUMS in
  `data/filings/angelone_hist/`.
  - 1:10 split approved 15 Jan 2026, effective by 16 Apr 2026. `[SOURCE NEEDED: split record date]`.
  - Q3 FY23 share count is derived from EPS (weighted average, not period end).
  - FY25 quarterly sum = audited figure.
- **Dry run** (`python3 run_pat.py`, 6 Nov live runs, local inputs `out/pat/dev/`): `out/pat/2026-11-06/*_report.md` and
  `*_valuation_lines.json`. Window "All", ₹ per share:

  | | Regression | Ratio | ADR (PAT) | **Net (20/30/50)** | Close | Upside |
  |---|---:|---:|---:|---:|---:|---:|
  | Angel base | 312.26 | 345.55 | 387.80 | **360.01** (bear 306.82, bull 413.20) | 331.00 | +8.8% |
  | Groww base | 201.05 | 221.01 | 229.36 | **221.19** (bear 200.29, bull 242.09) | 215.08 | +2.8% |

  - Angel net by window: 3M 359.7, 6M 372.7, 1Y 357.7, Since Apr 2025 359.4. 2Y / 3Y are not covered by ADR; only P/E covers them.
  - Groww: All 221.2, 3M 226.3, 6M 223.6.

### Workbook → live bridge (to show AB)
- **Angel regression** live: 9.599 × ADR + 120.35, R² 0.238. Workbook: 9.613 / 120.65 / 0.259. Close.
- **Groww regression** live: 3.796 × ADR + 112.54, R² 0.074. Workbook: 7.827 / 36.78 / 0.216.
  - The cause is that the live engine's Groww ADR runs 5–7% above the workbook's between Feb and Jun 2026 (live switches).
    Prices match day for day. The fit is weak, so small ADR differences move the slope a lot.
- **ADR leg** moves with the new P/E:
  - Angel base 344.68 → 387.80
  - Groww 198.80 → 229.36
- **Angel derived P/E vs vendor:** median −0.05%.
  - 3Y band: mean 23.65 vs 23.74, SD 5.33 vs 5.09.
  - Since Apr 25: mean 26.51 vs 26.58, SD 4.77 vs 4.34.
  - The remaining gaps sit in the ~week before each results date: the vendor takes in the new quarter about a week early.
    We keep the filed dates.

### Dashboard (ExchangesDash fork; worktree `../exchangesdash-valuation`, branch `brokers-valuation` from upstream/main `d4c5103e`, uncommitted)
- `dashboard/api/brokers.js`: `view=valuation` → `valuationLines()` (like `patLines`).
- `tests/test_brokers_api.py`: 3 ValuationView tests (13/13 API tests pass).
- New `dashboard/js/34-brokers-valuation.js`:
  - KPIs and the timeline selector. Windows the data don't cover are disabled. A window covered only by P/E keeps the All fit and shows a note.
  - Three-methods table with weights, net and upside; hover shows the arithmetic. An inputs panel.
  - Charts:
    - price vs 45-day ADR (dual axis)
    - scatter with fit
    - price ÷ 45-day ADR with ±1/2 SD bands
    - actual vs regression-implied price
    - Angel's P/E bands: 3Y and Since Apr 25 under All; otherwise the chosen window
- `js/30-brokers.js`: tab `val` "Valuation" for brokers with `pat: true`. `index.html`: script tag.
- **Not touched:** `brokers_mirror_schema.sql`. Its rule is to add a table only once it exists on the brokers side.
  The mirror owner gets a note (still to write: `docs/Prompt_for_ExchangesDash_owner_sb_valuation_lines.md`).
- **Preview:**
  - `.claude/launch.json` config `brokers-valuation-preview` (port 8795) runs a scratch copy of the replica's
    `dev/serve.mjs` that answers `view=valuation` from `out/pat/2026-11-06/*_valuation_lines.json`.
  - The wrapper is saved at `out/valuation/dev/serve-val.mjs`, and `.claude/launch.json` points there.
  - Verified in the browser for Angel and Groww: all windows, no console errors, and no sideways page scroll at 375 px.

## Gates (re-run 9 Nov, 23:19, after the timeline and the window tests)
- brokersdashboard `pytest tests/`: **406 passed, 1 skipped**; `run_parity.py`: **8774/8797 exact, 23 out of scope, 0 unexplained**.
- ExchangesDash worktree: `unittest discover -s tests` **323 tests OK**; `node --check` on every `dashboard/js` / `api` file OK.
- Done since the pause: window tests in `tests/test_valuation.py` (8 pass); mirror note
  `docs/Prompt_for_ExchangesDash_owner_sb_valuation_lines.md` (draft, not sent); row counts per run (Angel 3,017, Groww 1,072).

## Next steps (in order)
1. ~~Re-run the gates~~, ~~window tests~~, ~~mirror note~~: done 9 Nov 23:19.
2. Show AB, step by step (rule 7), then on his OK:
   - (a) commit here, run the gate, push, PR
   - (b) apply `migrations/20261109_sb_valuation_lines.sql`
   - (c) apply `out/valuation/db_inputs.sql` steps 1–3; step 4 after AB checks `out/pat/facts_angel_pat_history.md`
   - (d) commit and push the ExchangesDash branch `brokers-valuation` and open a PR upstream
5. PLAN.md: tick 5.8 when the tab is live.
