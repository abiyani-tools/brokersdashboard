# LIVE_SPEC — Angel One ADR engine: parity → live

Status: **SIGNED OFF by AB, 23 Oct 2026** — all seven §7 proposals accepted. E1, E2, E4, E5 and E6 are implemented in
`src/live/` (tests in `tests/live/`). E3 and the §4 switches wait for the engine code. · broker `ANGELONE`
Baseline: parity run `42e5519f-0e19-4834-9a4c-2ce8ccec574a` (as-of 21 Oct 2026, 8,774 / 8,797 exact, 0 unexplained).

This spec was written from the live database (`sb_*` tables, the stored calibration of the parity run) and the plan.
The engine code (`src/engine`, commits `d237013` / `7c745d5`) was not available to this session, so module and
function names are left to `engine-coder`. Every number below was recomputed from DB rows and reproduces the parity
calibration where a parity value exists (F&O take rate 21.4230, cash 16.7752, commodity 22.2949).

Sign-off: AB accepted every proposal in §7 on 23 Oct 2026 (the proposal in italics is the rule in force).

---

## 1. Ground rules

1. **Parity mode never changes.** `mode='parity'` keeps the cell lookups, `sb_parity_pins` and the Excel quirks.
   The parity gate (8,774 exact, 264 / 264 Summary cells) runs on every commit and must stay green.
2. **Live mode = parity + a set of named switches.** Each switch in §4 is a flag (`live.switches = {a, b, …}`); live mode
   turns all of them on. Turning flags on one at a time must reproduce each bridge in §4.
3. **One switch per commit**, each with an ADR bridge for **FY27, Q2 FY27, Oct-26**, per segment
   (F&O, Cash, Commodities, MTF, Broking, Consolidated): old ADR, new ADR, Δ, Δ%.
   `recompute-checker` recomputes the new ADR independently from raw rows; agreement to 1e-6 is the exit test.
4. **Live inputs are only `reviewed` facts, with seeds as fallback**, read through `sb_facts_current` (§2).
5. **No silent defaults.** A missing input raises or produces a flagged "insufficient data" cell; it is never treated as 0
   or dropped.
6. Every live run writes `sb_runs(mode='live', as_of_date, code_version, notes)` and records which switches were on in `notes`.

## 2. Inputs and precedence (E2)

| Input | Live source | Parity source (unchanged) |
|---|---|---|
| Company disclosures (orders, shares, revenue mix, total income, funding book, trading days) | `sb_facts_current` by `metric × period_key` | cell lookups + seeds |
| Exchange volumes (NSE / BSE F&O, NSE / BSE cash, MCX) | `sb_market_daily` rows with `status in ('ok','imputed')`; a `suspect` row fails E5 | Excel columns |
| Industry MTF book | `sb_market_daily` `mtf_industry/book_cr`, daily average over the period | monthly series (`MTF data!D49:D57`) |
| Calendar, special sessions | `sb_calendar` | Excel date rows |
| Fixed assumptions (MTF yield 14.95%, 246-day basis, 45% net factor) | `sb_assumptions` | same |

**Precedence** for facts is the same as the view `sb_facts_current`: drop `rejected`, prefer `reviewed`, then the latest
`created_at`, then the highest `fact_id`. The loader (`live.loader.select_current`) reads `sb_disclosure_facts` and applies
this ordering in code. It adds one more step, decision Q1: among non-reviewed rows of `total_orders`, the F&O-market sheet
wins. The view happens to give the same answer today only because those rows have the higher fact_ids.

**Volumes** (`live.loader.select_volumes`) keep one value per date and input:
- **Without switch (c)**, the volume policy is `excel_first` (parity inputs): the `excel_seed` row, else the lake row.
- **With (c)**, it is `best_ok`: an `ok` lake row, else an `ok` Excel row, else whatever exists, kept with its status.

A selected value that is not `ok` is never replaced by 0; E5 blocks on it.

- After the 2.2 review (23 Oct): 178 reviewed, 477 seeds staged, 509 current rows.
- 62 reviewed rows overlap a seed for the same metric and period, and the reviewed value wins. None of them sets
  `supersedes`; the view does not need it. Facts that are real corrections, not rounding:

| Period | Metric | Seed | Reviewed |
|---|---|---|---|
| Q3 FY26 | orders_comm | 36 (fact 25) / 35 (fact 273) | **35** (596) |
| Q4 FY26 | avg_funding_book (Rs Mn) | 58,000 | **58,490** |
| Q1 / Q2 FY26 | avg_funding_book (Rs Mn) | 42,083.3 / 53,076.7 | **42,060 / 53,050** |
| Q2 FY25 – Q1 FY27 | revmix_* | Excel's rounded % | the deck's one-decimal % |
| Q1 / Q2 / Q4 FY26 | client_base, orders_total, gross_client_acq_q | rounded | 2-decimal |

- **Three conflicts have no reviewed value.** Both values are seeds from two Excel sheets:

| Period | total_orders (Mn) | Working sheet | F&O market sheet |
|---|---|---|---|
| FY25 Nov | | 131.28 (C148) | 130.96 (C33) |
| FY25 Jan | | 125.97 (C150) | 125.96 (C35) |
| FY26 Jan | | 146.67 (C162) | 146.70 (C47) |

  Proposal: `filing-extractor` reads the three monthly business updates and stages the disclosed value. Until then live
  uses the F&O-market value (the parity pin `fo_monthly_orders_source`). **[AB: §7 Q1]**

- **Units.** The loader converts on read and asserts units:
  - Rs Mn → Rs Cr = ÷10.
  - Rs Bn → Rs Cr = ×100.
  - Shares are fractions (0.174, not 17.4).

  E5 rejects a share above 1, and a Rs-per-order take rate outside 5–60.

## 3. Engine items E1–E6

**E1 — period ranges from `sb_calendar`.**
- FY, quarter and month ranges come from `sb_calendar` (`fy`, `q_fy`, `fy_month`). Today it covers 29 Sep 2023 – 21 Oct 2026, 785 days.
- A calendar day that has volumes but no calibration for its period (for example November 2026 once added) raises
  `MissingCalibration(period)` in live mode. It is never skipped.
- Exit test: add a synthetic November 2026 row with no inputs; the run fails, naming the period.

**E2 — live loader.**
- `live.loader.load_inputs(reader, broker, as_of, switches)` returns the calendar, the facts (precedence as in §2, with unit
  conversion and the source fact_id of each value), the selected volumes and the raw volumes.
- The parity engine keeps its own loader; the parity path is not touched.
- Exit test (`tests/live/test_loader.py`): it returns the Q2 FY27 inputs (orders_fo 256, orders_cash 66, orders_comm 45,
  total_income 14,315, revmix_fo 0.387 / cash 0.087 / comm 0.071, avg_funding_book 74,530 Rs Mn = 7,453 Cr, share_*_q),
  all from reviewed facts. **Done.**
- Still open: running the parity gate once the engine imports `live/`. The gate must stay unchanged.

**E3 — Summary for every FY / quarter / month (D1).** *Done: `src/engine/summary_periods.py`; migration applied 23 Oct 2026.*
- **One label rule** builds every comparison from the selection:
  - FY → previous FY (YoY).
  - Quarter → previous quarter (QoQ) and the same quarter last FY (YoY).
  - Month → previous month (MoM), the same month last FY (YoY) and "6M".
  - The Week and Weekday tables stay anchored on the last date.
- **The workbook's grid is this rule at two selections:** FY 2027 / Q2 FY 2027 / FY 2027 September for every panel, and
  FY 2027 / Q4 FY 2026 / FY 2026 February for Cash. So the Cash panel's "stale labels" are just a different selection.
- **6M:**
  - Parity: the average of the two quarterly ADRs ending with the month's quarter.
  - Live: the average over the 6 calendar months ending at the month (decision Q2). For Cash in September 2026 that gives
    2.0543 Rs Cr/day, a different number from the two-quarter average.
- **Live statistics are guarded.** A period that has a calendar trading day before a segment's series starts is partial,
  so it gets *insufficient data* (the value is NULL and `note` gives the reason), never a short average. The F&O, Cash and
  MTF series start 1 Oct 2024, so FY 2025 and earlier have no value; Q3 FY 2025 is complete. Commodities start
  1 Apr 2024. An insufficient segment makes Broking and Consolidated insufficient too.
- **Output:** `period_rows()` gives 1,566 rows for the parity daily series (6 panels × every FY / quarter / month, plus
  the as-of tables), each with a unique key. `publish.period_summary_rows()` writes them, and `publish.summary_rows()` now
  tags parity rows with their selection.
- **Exit test (`tests/test_summary_periods.py`), passing:** the general rule at the parity selections reproduces the
  workbook's 264 Summary cells exactly (rel 1e-9). The live comparisons match an independent recompute from the daily
  series.
- **Migration** `migrations/20261023_sb_summary_cells_period.sql`, **applied 23 Oct 2026** with AB's OK:
  - It adds `period_type`, `period_key` and `note`.
  - It fills them for the 210 stored parity rows.
  - It widens the primary key to (run_id, panel, period_type, period_key, table_name, row_label). The old key would collide
    on labels like "Avg of last 6 months".

  Verified after applying: 210 rows (FY 12, Q 24, M 24, asof 150), no NULL periods, values unchanged (sum 1,485.349792).

**E4 — short-history guards.**
- Last-45-day, last-3 and last-10 averages, weekday tables and every ratio return "insufficient data" with a reason when
  n is below the window or the denominator is 0.
- Exit test: unit tests for n = 0, 1 and window−1, and a zero denominator.

**E5 — integrity checks before every live run** (`live.integrity.run_checks`). It runs in two layers:
- **Selected layer:** the series the engine will use. An issue here is an *error* and blocks publishing (no
  `sb_summary_cells` write); the report goes to `sb_runs.notes`.
- **Audit layer:** each source on its own. Its issues are *info*, so a lake gap stays visible even when the other source
  covers the day.

The checks:
- **Missing day:** a calendar equity or MCX day with no value for an input the ADR uses.
- **Status and zero:** a non-`ok` status, or zero on a trading day.
- **Frozen series:** the same non-zero value on 3 or more consecutive trading days.
- **Jump:** a day's value above 5× the **max**, or below 0.2× the **min**, of the trailing 20 non-zero values (with at
  least 10 of them). *Changed from "5× the median":* expiry days run 15–20× a normal day (BSE F&O 1 Oct 513M vs 27M), so a
  median rule would block every expiry. The max/min rule still catches ×100 or ÷1000 unit errors, and finds no false jump
  in six months of real data.
- **Unit sanity:** as in §2. A take rate outside 5–60 Rs/order, or "insufficient", is an error.
- **Seed conflicts** settled by the Q1 rule are *warnings*.
- **Industry MTF book:** a missing day is a *warning*, and the last 3 trading days may be missing (publication lag),
  because the quarterly average is taken over the days reported. The only gap today is 8 Apr 2026.

The exit test passes (`tests/live/test_integrity.py`) on lake data from 1 Apr to 21 Oct 2026:
- **Without switch (c)**, two errors block: BSE F&O contracts frozen at 18,962,859 from 28 Sep to 21 Oct (16 days), and
  15 `imputed` days, both from the Excel copy.
- **With (c)**, nothing blocks: the lake has the real BSE values, so open question 3 is settled.
- **Either way**, the audit reports every known gap:
  - BSE cash 0 on 15 Jun (lake).
  - NSE IO and SO 0 on 12–15 Oct (lake).
  - MCX 0 on 27–28 May (`octo_mcx`).
  - IO and SO missing from the lake on 16, 19 and 21 Oct.
  - The frozen BSE values in the Excel copy.

  In every one of these cases, the other source holds an `ok` value for those days.

The calendar's equity days match every trading-day count Angel One discloses: Q1 FY27 60, Q2 FY27 65, and Jun / Jul /
Aug / Sep 21 / 23 / 21 / 21.

`nse_cash/turnover_cr` and `bse_cash/turnover_cr` are `suspect` on 340 days (an Excel row offset). They are not used by
the ADR, so E5 checks only the datasets the ADR reads.

**E6 — DB reader.**
- Reads with `SUPABASE_SERVICE_KEY` from the environment and fails if the variable is unset. It is never hard-coded and never logged.
- The snapshot reader stays the default for tests.
- Exit test: a CI run against the DB equals a run from `snapshot/db_snapshot_*.json` taken the same minute.

## 4. Switches (PLAN 3.1)

Take rate (Rs per order) = total_income (Rs Mn) × revmix_segment ÷ orders_segment (Mn). This is the engine's rule
(`sb_calibration.rule` = "rev mix x total income / orders") and reproduces every stored parity take rate.
The Δ figures below are for the **input**; the ADR bridge in the commit shows the ADR effect per period.

| # | Switch | Live rule | Inputs | Expected direction (input, recomputed here) |
|---|---|---|---|---|
| a | **J8 = 35** — *done 23 Oct* | Working sheet J8 (Q3 FY26 commodity orders) := reviewed fact 596 (35), everywhere J8 is read | orders_comm Q3 FY26 | Commodity take rate 22.2949 → **22.9319 (+2.857%)**, every commodity day × 36/35. J8 is also in Q3 FY26's F&O share of orders (277/381 → 277/380): Oct–Dec 2025 F&O days × 381/380, and FY27 F&O × 1.000874 through the 9-month average. Consolidated FY27 17.0967 → 17.1487 (**+0.30%**), Q2 FY27 +0.32%, Oct-26 +0.39%. `out/bridges/a.md`; independent check `out/checks/switch_a.md` 22/22 agree |
| b | **One-decimal revenue mix** — *done 23 Oct* | Working sheet rows 15–17 (F&O, cash, commodity share of total income) for Q3 FY25 … Q1 FY27 := reviewed deck values (21 cells, facts 606–644) | revmix_fo / cash / comm | On top of (a): F&O projected take rate 21.4230 → 21.4093 (**−0.064%**); cash projected 16.7752 → 16.5122 (**−1.57%**), and Q1 FY27 actual cash days × 0.086/0.09 (FY27 cash **−2.87%**); commodity × 0.061/0.06 (**+1.667%**). Consolidated FY27 17.1487 → 17.1099 (**−0.23%**), Q2 FY27 −0.05%, Oct-26 −0.03%. `out/bridges/b.md`; check `out/checks/switch_b.md` (agrees; one 4-decimal claim rounds) |
| c | **BSE contracts unfrozen** — *done 23 Oct* | The 15 days the workbook carries 18,962,859 forward in the daily column (29 Sep – 21 Oct 2026, status `imputed`) take the lake's real BSE F&O totals (`market_daily_lake`). Contracts per order, share and take rate are unchanged, so each day scales by (NSE + BSE real) ÷ (NSE + 18,962,859). The live E5 policy `best_ok` (§2) selects the same values from `sb_market_daily` | `bse_fo/contracts` | On top of (a, b): F&O Oct-26 6.7458 → **11.6734 (+73.0%)**, Q2 FY27 +0.85% (29–30 Sep), FY27 +5.36%; Consolidated Oct-26 15.6040 → 20.5316 (**+31.6%**), FY27 +2.91%. Daily ratios 0.9987 (9 Oct) to 5.39 (8 Oct). `out/bridges/c.md`; check `out/checks/switch_c.md` (13/13 agree) |
| d | **Special sessions excluded** — *done 23 Oct* | Dates with `special_session` (Muhurat, DR test) are dropped from every average, last-N and weekday statistic, for all four segments; daily rows and totals keep them. In the daily series: 2024-11-01, 2025-10-21 | `sb_calendar.special_session` | FY27, Q2 FY27, Oct-26 **unchanged**. Comparison bases rise: Oct-25 Consolidated 16.2940 → 16.8503 (**+3.41%**), so Oct-26 YoY +26.0% → **+21.8%**; Q3 FY26 +1.11%; FY26 +0.27%. FY26 MTF −0.035% (the Muhurat MTF value is above average). *Open: MTF could keep these days (interest, not a session).* `out/bridges/d.md`; check `out/checks/switch_d.md` (33/33) |
| e | **D2 monthly cash share** — *done 23 Oct* | Projected cash days (quarters after the last actual cash quarter) use the monthly `share_cash` of their own month, else of the latest earlier month; actual quarters keep the quarterly share their trades/order is built on | share_cash (M): Jul-26 0.171, Aug 0.170, Sep 0.162 | Cash Oct-26 2.1292 → 1.9824 (**−6.90%** = 0.162/0.174), Q2 FY27 −3.67%, FY27 −2.36%; 78 days change; Consolidated Oct-26 −0.72%, FY27 −0.27%. When (h) makes Q2 FY27 actual, Jul–Sep move to the quarterly 0.168. `out/bridges/e.md`; check `out/checks/switch_e.md` (20/20) |
| f | **D3 quarterly commodity take rate** — *done 23 Oct* | Each quarter's commodity days use that quarter's rate (mix × total income ÷ commodity orders, cells after a, b); Q2 FY25 uses the reviewed revmix_comm 0.037 (no cell); quarters after the last rate carry it (Q4); Q1 FY25 has no disclosed mix → earliest rate (Q2 FY25), days marked projected, [SOURCE NEEDED: Q1 FY25 revenue mix] | rows 8, 17, 99 per quarter | Rates (Rs/order): Q2 FY25 24.39, Q3 FY25 24.18, Q4 FY25 25.00, Q1 FY26 23.29, Q2 FY26 23.25, Q3 FY26 23.31, Q4 FY26 22.18, Q1 FY27 22.94. On top of (a–e): commodity FY27, Q2 FY27, Oct-26 × 22.9392/23.3141 (**−1.61%**), FY26 −1.64%, Q3 FY26 and Oct-25 unchanged; 596 of 660 days change; Consolidated FY27 −0.15%, Oct-26 −0.16%. `out/bridges/f.md`; check `out/checks/switch_f.md` (33/33) |
| g | **D4 MTF gross / net** — *done 23 Oct* | MTF is gross (book × 14.95% / 246 per day) in every table, and an 'MTF (net)' panel shows net = 45% × gross [SOURCE NEEDED: basis for 45%]. Consolidated stays on gross. *Correction:* this row earlier said the headline "stays net, as in parity"; in parity the FY / quarter / month tables and Consolidated are gross and only the weekday tables use net (a workbook quirk this switch removes) | `sb_assumptions` mtf_* | FY / Q / M **unchanged**; MTF (net) FY27 1.8942 (= 0.45 × 4.2094). Weekday tables: MTF net → gross (× 1/0.45; Monday 2.1218 → 4.7151), so Consolidated weekday rows rise by the same Δ (~2.6). Week tables unchanged. *Open: AB to confirm gross headline.* `out/bridges/g.md`; check `out/checks/switch_g.md` (29/29) |
| h | **Q2 FY27 actuals in; projections roll to Q3 FY27** — *done 23 Oct* | A synthetic Q2 FY27 Working-sheet column from reviewed facts (orders 256/66/45, mix .387/.087/.071, cash share .168, total income 14,315; quarterly table 366.46 / 45); last-actual pins for F&O, cash, MTF → Q2 FY27, so the workbook's projection rules roll forward. MTF Q2 FY27: Angel book = disclosed average funding book 7,453 Cr (Q5), industry = daily lake average 141,830 Cr (Q6); projected MTF share = mean of the last 6 reported quarters (Excel Q58) | facts 563–595, 648–655 | F&O take rate Q1 21.553 / Q2 21.640 actual, Q3 21.566 (3-quarter mean); Apr–May F&O % 0.7371 → contracts/order 14.339 → 14.200: F&O FY27 **+1.84%**, Q2 +2.07%, Oct +1.72%. Cash Q2 FY27 actual (tpo 6.852, take rate 18.870): FY27 **+1.37%**, Q2 +2.80%, Oct +1.18%. Commodity Q2 own rate 22.586: **−1.54%** from Jul. MTF Q2 share 0.05255, Q3 0.05237: Q2 +0.63%, Oct +0.28%. Consolidated FY27 17.535 → 17.742 (**+1.18%**), Q2 FY27 +1.40%, Oct-26 +1.02%. Nothing before Apr-26 moves. `out/bridges/h.md`; check `out/checks/switch_h.md` (101/101) |
| i | **Inputs cut off at the latest disclosed month** — *built 23 Oct; independent check pending* | Monthly F&O share and total orders (workbook to May-26), commodity total orders (Jun-26) and commodity share (Aug-26) extended with reviewed monthly facts to Sep-26; months the workbook has are unchanged. Cash is covered by (e) and (h) | share_fo, total_orders, share_comm (M) | F&O Jun–Sep contracts/order actual (14.64, 15.81, 13.39, 14.47; was 14.20 carried), Oct share 0.2213: F&O FY27 **−1.83%**, Q2 −2.73%, Oct −1.72%. Commodity Jul–Sep actual (comm % 45/366.46), Sep share 0.417, Oct contracts/order 13.395: FY27 −3.14%, Q2 −4.80%, Oct **−7.22%**. Consolidated FY27 17.742 → 17.510 (**−1.30%**), Oct-26 −1.67%. `out/bridges/i.md` |

Cumulative effect of all nine: `out/bridges/summary.md` (Consolidated FY27 17.10 → 17.51, Q2 FY27 16.56 → 16.50,
Oct-26 15.55 → 20.22).

Order of commits: a → b → c → d → e → f → g → h → i, the plan's order. Each bridge is taken against the previous commit,
so the effects add up to parity → full live without double counting. (f) and (h) both touch commodity; (f) changes the rule
and (h) only adds the Q2 FY27 quarter.

## 5. Bridge format (per commit)

The file is `out/bridges/<switch>.md` and also goes in the commit body. It has:
1. **Header:** the rule changed and the fact_ids used.
2. **Table:** periods (FY27 YTD, Q2 FY27, Oct-26 MTD) × segments (F&O, Cash, Commodities, MTF net, Broking, Consolidated),
   with old, new, Δ and Δ%.
3. **Check:** the `recompute-checker` line with its independent number and the max abs diff (must be ≤ 1e-6).

## 6. Not in scope of this spec

The following are not covered here:
- Daily automation (Phase 4).
- The dashboard (Phase 5).
- A second broker.
- 2.4, back-sourcing the Q3 / Q4 FY25 mix. (b) already uses the deck's restated values, and 2.4 decides whether the Excel's
  values were restated or mistyped.

## 7. Decisions needed from AB

- [x] **Q1** — The three seed-vs-seed monthly total_orders conflicts. Use the F&O-market value until `filing-extractor` stages the
  disclosed values? *(proposed: yes)*
- [x] **Q2** — Live "6M" = revenue ÷ trading days over 6 calendar months ending at the selected month. The Excel averages the two
  quarter ADRs instead. *(proposed: calendar 6M)*
- [x] **Q3** — Switch (c) needs real BSE F&O contracts for 29 Sep – 21 Oct. Take them from the ExchangesDash lake, or keep
  `imputed` and let E5 block? *(proposed: lake; block if absent)*
- [x] **Q4** — D3 for a quarter not yet reported: carry the latest reported quarter's commodity take rate (after (h): Q2 FY27 = 22.586, applied to Q3 FY27)?
  *(proposed: yes)*
- [x] **Q5** — MTF Angel book: in live mode use the disclosed average funding book. The Excel back-solves the book from interest
  income ÷ 3.75% (`MTF data!P53:P57`). The two differ by ≤ 0.9% (Q4 FY26 5,796 vs 5,849 Cr; Q1 FY27 6,133 vs 6,137 Cr).
  *(proposed: disclosed book)*
- [x] **Q6** — The industry MTF average in live mode = the daily lake average for the quarter (Q1 FY27 120,751 Cr). Parity uses the
  monthly series (119,000 Cr). *(proposed: daily lake)*
- [x] **Q7** — Q2 FY27 changed the revenue-mix layout: depository 4.0% and other 1.0% are now separate lines, and broking = 54.5%
  = F&O 38.7 + cash 8.7 + commodity 7.1. The F&O take rate stays consistent (21.64 own-quarter, vs 21.51–21.55 in Q4 FY26 /
  Q1 FY27), so the F&O share is not inflated by the new lines. Accept the deck's segment shares as-is? *(proposed: yes)*
- [x] **Sign-off** — AB, 23 Oct 2026: "go with your proposals on all seven, start E1–E6".
