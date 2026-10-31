# Groww — live spec (draft for AB's sign-off, 31 Oct 2026)

Parity is done: the engine reproduces `SUMMARY - Groww` exactly (262/262 cells) on branch `groww-parity`. Evidence: `docs/Groww_ADR_Methodology.md` (§11 has the corrections) and `out/groww/backsource.md` (each input traced to Groww's filings).

This spec proposes the live switches, the Groww counterpart of Angel One's a–i. As for Angel One:
- each switch is one commit with a parity → live bridge and an independent recompute check;
- only `reviewed` facts move numbers;
- nothing is published until you sign off.

## How Groww differs from Angel One

| Area | Angel One | Groww |
|---|---|---|
| Disclosure cadence | Monthly business update plus quarterly deck | **Quarterly only**: Shareholders' Letter, results, and a KPI Handbook .xlsx on the IR site (not on NSE) |
| Orders | By segment, monthly | Total only, quarterly (Stocks + Derivatives; 51.73 Cr in Q2 FY27); no segment split |
| Revenue by segment | Mix % of total income | Mix % of **consolidated total income** (8 buckets), reclassified in Q2 FY27 |
| Market shares | Orders / turnover shares | ADTO shares; the denominator doubled from Q4 FY26 |
| Market orders | Calibrated from Angel's own orders | **Borrowed from Angel One's calibration** (contracts per order, trades per order) |

## Proposed switches

| # | Switch | Parity (workbook) | Live (proposed) | Evidence |
|---|---|---|---|---|
| g-a | **Facts from filings** | 41 typed inputs, 18 of them wrong or rounded | Load the reviewed facts from `out/groww/facts_candidates.json`: mix on consolidated total income (D9); MTF mix 2% / 3% / 6.9% for Q4 FY25 / Q1 FY26 / Q4 FY26; one classification of the stocks mix | backsource.md; Q1 FY27 letter p7 ("MTF +1.1pp QoQ") |
| g-b | **Full FY26** (D2) | F&O / cash 0 for Q3 FY25–Q1 FY26, `#N/A` for Q2 FY25 | Calibrate Q1 FY26 from its reported total income (9,484.71 Mn) and mix, so FY26 has every quarter; no figures before Q1 FY26 | Q2 FY26 results p5; Q1 FY27 letter p6 |
| g-c | **BSE F&O unfrozen** (D11) | 18.96 Mn carried 29 Sep–21 Oct 2026 | Lake values, the same as Angel switch c (already live) | shared |
| g-d | **Every reported quarter calibrates** (D3, D12) | F&O take rate fixed at Q4 FY26; commodities calibrated once (Q3 FY26), using Angel's take rate | F&O, cash and commodities take rate and share calibrated for each reported quarter, Q1 FY27 and Q2 FY27 included | Q2 FY27 actuals in facts_candidates |
| g-e | **One estimate rule** (D4) | Mix of carry, trailing-3, ×1.05 typed growths and typed MTF shares | Unreported quarters carry the last actual share and take rate; no typed growth. Overrides go in `sb_assumptions` with a note | — |
| g-f | **MTF basis** (D7) | Angel's 14.95% yield, 246 days | 14.95% (Groww's stated fixed pricing, calls only) × the actual trading days of each FY; share = the disclosed MTF revenue ÷ the industry book | transcripts Q2 FY26 p6, Q1 FY27 p13 |
| g-g | **Special sessions and periods** | Partial latest period; stale labels | The same live rules as Angel One: special sessions out of the F&O, cash and commodity averages; labels from the calendar; comparisons follow the selected period | Angel switches d, h |

## Kept as they are (D5, D6), labelled in the UI

- **Market orders from Angel One's calibration.** Groww publishes no segment orders, so there is no independent route. The dashboard says so.
- **ADTO shares applied to orders.** The take rate absorbs the difference. The label reads "share by turnover".

## New check (not in the workbook)

**Implied vs disclosed total orders.** The model's Groww orders (F&O + cash + commodity) can be compared each quarter with Groww's disclosed total orders (KPI Handbook). That gives Groww an out-of-sample test like Angel One's (PLAN 3.2). A persistent gap would show where the borrowed Angel calibration doesn't fit Groww.

## Monthly signal (optional, later)

Groww has no monthly update. Two fetchable monthly series could inform intra-quarter estimates. Neither is needed for the switches above.
- **NSE Report 1C** (broker-wise active clients, about the 7th of each month). It is overwritten in place, so it must be archived monthly.
- **Month-end snapshots of the IR site's quarter-to-date widget** (stocks turnover, derivatives premium turnover, MTF book).

## Decisions for AB

1. Approve the switch list g-a … g-g (or strike any).
2. g-a: review and approve the candidate facts, as you did for Angel One's 178. Nothing is staged in the database yet.
3. g-b: is FY26 starting at Q1 FY26 (1 Apr 2025) right, or should FY26 comparisons start from Q2 FY26?
4. g-f: keep 14.95% for MTF, or use a filed number if you have one?
5. Dashboard: a broker selector in the Brokers view (agreed). Show the implied-vs-disclosed orders check there too?

## Live run and daily job (built 31 Oct 2026)

- `python3 run_live.py --broker GROWW|ANGELONE|all` (default ANGELONE, unchanged). Groww borrows Angel One's calibration, so every choice runs the Angel One live run first and builds Groww from that same run (snapshot, as-of date, switch c). Groww's report and Summary rows go to `out/live/<as_of>/groww/`.
- From the DB, `build_snapshot(reader, broker='GROWW')` loads that broker's facts with the shared calendar and exchange data; `groww_inputs(reader)` gives the Groww engine its seed facts (`source_ref` `excel:...`), `sb_assumptions` and `sb_parity_pins` (`broker_id='GROWW'`), and the filing facts of any status.
- Only `reviewed` facts move numbers. A Groww run whose required facts are not all `reviewed`, or whose workbook inputs are not in the database, is refused (`GrowwRefused`): nothing is computed or published. `publish()` also refuses a Groww run not built on reviewed facts.
- Groww's workbook inputs (41 seed facts, 14 assumptions, 10 pins) belong in the database like Angel One's. `out/groww/db_inputs.json` and `out/groww/db_inputs.sql` hold the rows (not applied; AB approves). Until then Groww runs from the snapshot file.
- `publish()` writes `broker_id` on `sb_runs` and on `sb_calibration`, `sb_daily_revenue` and `sb_summary_cells` (all key by `run_id`, so brokers never collide). Groww daily rows exclude days before a segment went live and carry gross MTF only; regimes are `actual` / `projected` (the tables' check constraints). The dashboard's `/api/brokers?broker=GROWW` finds the latest `mode='live'` run for the broker.
- `daily.yml` runs `--broker all`: Angel One is published first. A refused Groww run is a warning annotation (exit 0); any other Groww error fails the job after Angel One has published.

## Groww IR archive (built 31 Oct 2026; migration not applied)

groww.in/investor-relations shows the closed quarters and the current quarter-to-date for seven series (users, customer assets, MF SIP inflows, stocks turnover, equity-derivatives premium turnover, commodity-derivatives notional, MTF net book) and overwrites the quarter-to-date every day. `src/live/refresh_groww_ir.py` archives each day's page into `sb_broker_daily` (migration `out/groww/migration_sb_broker_daily.sql`, for AB to apply). `daily.yml` runs it before the live run with `continue-on-error: true`: a blocked fetch or a changed page shows as a red step with an error annotation and a warning in the job summary, never silently. The raw page is the workflow artifact `groww-ir-raw`, not in git.

- Units: the page's chart values are in its own unit, value / 100 = Rs Mn (checked on every run against the page's printed "Rs Mn" string and `rawCurrentValue`; the run fails if they disagree). Money is stored in Rs Mn, user counts as printed.
- Which trading day the QTD point runs through is not on the page. `src/engine/groww_ir.py: infer_covered_through` cuts the exchange cash and option-premium turnover at each candidate day and picks the cut-off at which Groww's share of NSE+BSE turnover matches the prior quarter's share on both series. It is stored in `covers_through` on the QTD rows when the inference is clear (31 Oct 2026 page: 30 Oct), and can always be re-derived from the stored rows plus `sb_market_daily`.

### Running the archive from AB's Mac

If groww.in blocks GitHub's runners, or a day was missed, run it locally (the page is public; no login):

```
cd /Users/abhishekbiyani/Documents/brokersdashboard
python3 -m src.live.refresh_groww_ir                 # dry run: fetch, parse, print rows and the inferred trading day
export SUPABASE_URL=...  SUPABASE_SERVICE_KEY=...    # from your own secret store; never paste a key into a chat
python3 -m src.live.refresh_groww_ir --write         # upsert into sb_broker_daily (reads exchange turnover from the DB)
```

The raw page lands in `out/groww_ir/` (git-ignored); keep it. A second run on the same IST day replaces that day's rows. The page cannot be back-filled: a day missed is a day without a quarter-to-date value (the quarterly history on any later page still has the closed quarters). To run it every evening on the Mac, a `launchd` job (or `cron`: `15 20 * * 1-5`) calling the two commands above is enough; run it after 19:50 IST so the exchange files for the day are in the DB.

## Optional IR switches g-h and g-i (built 31 Oct 2026; off until AB signs off)

They read the archived IR page (`snapshot/groww_ir_2026-10-31.json` built from the saved page, or the table `sb_broker_daily`) and, for g-h, the exchange turnover (`snapshot/groww_exchange_2026-10-31.json`, or `sb_market_daily`). They are not in the published chain (`SWITCHES = 'abcdefg'`). In the live CLI: `--groww-extra h|i|hi` (or env `GROWW_EXTRA`); `--publish` with them on is refused. Bridges: `out/bridges/groww_h.md`, `groww_i.md`. Backtests: `out/groww/backtest_ir_switches.md`.

- **g-h** (needs g-d, g-e): an unreported quarter's F&O and cash share = last reported share x (Groww QTD turnover share / Groww turnover share in the last reported quarter); Groww turnover share = Groww turnover / NSE+BSE exchange turnover over the same days (cash: stocks turnover vs `cash_traded_value`; F&O: equity-derivatives premium vs NSE index + stock option premium + BSE `options_premium_turnover`). The QTD days are quarter start .. the trading day the page runs through (`covers_through`, inferred). Take rate unchanged. Backtest: it helps cash and does not help F&O; overall not a clear win over g-e's carry.
- **g-i** (needs g-f): daily MTF revenue = Groww's MTF net book x 14.95% / FY trading days (the g-f convention), the book from the IR page: an archived level for the day, else (closed quarter) linear interpolation in calendar days between the two quarter-end levels, else (open quarter) the latest level held flat. It covers every calendar equity day, so it also fills the days the industry-book series lacks. Interaction with g-f: a reported quarter's book is scaled by k = disclosed MTF revenue / (sum of own book x 14.95% / FY days), so reported quarters still tie to the disclosed revenue exactly (g-f's calibration, with Groww's book as the daily shape); the open quarter has no disclosed revenue, k = 1. Backtest: the g-i path (k = 1) is closer to the disclosed revenue than g-f's industry-book method (mean abs error 8.7% vs 20.8% over Q4 FY25..Q2 FY27); the open-quarter rule on day 1 (previous quarter-end level held flat) is not (16.5%, understates like the industry method).

## Sign-off, 31 Oct 2026

AB approved:
- **g-i (MTF from Groww's own book): ON** in the published run, after the independent check (`out/checks/groww_switch_i.md`, 349/349 agree). If the IR archive is missing on a given day, the run publishes g-a…g-g, with a warning and a note in `sb_runs.notes`.
- **g-h (quarter-to-date turnover share): OFF.** Its backtest showed no clear gain over carry. Revisit once the daily archive has a few quarters.

`src/live/cli.py` `SIGNED_OFF_EXTRA = 'i'`; `--groww-extra none` turns the IR switches off for a run.
