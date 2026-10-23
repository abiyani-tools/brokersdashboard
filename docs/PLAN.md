# PLAN — Angel One ADR tracker (status 23 Oct 2026)

Legend: `[ ]` to do · `[x]` done · `[~]` waiting on someone · **owner** = agent (see §4) or AB / an outside owner.
Each to-do ends with an **exit test**. A to-do is done only when its test passes.

## 0. State in one screen
| Item | Status |
|---|---|
| Supabase `brokers-dashboard` (`everjfpbnlbcpuarnhob`, Mumbai), `sb_*` schema | live |
| Parity engine (`src/engine`) | 8,774 / 8,797 exact, 0 unexplained, 264 / 264 Summary cells |
| Live input layer (`src/live`) + E3 (`src/engine/summary_periods.py`) | E1–E6 coded and tested (61 passed on 3.9 and 3.13); E3 migration applied |
| Parity run stored | run `42e5519f-0e19-4834-9a4c-2ce8ccec574a` |
| Catch-up facts (Jun–Sep 26, Q1/Q2 FY27, Q3 FY26 fix, Q2 FY27 deck mix) | 178 **reviewed** (fact_ids 478–655, all approved 23 Oct; 477 seeds staged) |
| Review page | "Angel One Figure Review" artifact; decisions in its `reviews` collection |
| Repo | `abiyani-tools/brokersdashboard` (`main`); CI secrets not yet added |
| Blocked on outside owners | NSE cash trades; MTF table access; anon read (RLS) policies on the lake |

## 1. Decisions in force (AB, 22–23 Oct)
D1 summary laid out exactly like the Excel sheet, with FY / quarter / month dropdowns. Comparisons follow the selected period (YoY, QoQ, MoM, 6M ending at the selected month) · D2 cash projection uses the latest **monthly** cash share · D3 commodity take rate = each quarter's own · D4 MTF gross section, net = 45% × gross ([SOURCE NEEDED: basis for 45%]) · D5 daily job on GitHub Actions · D6 review page; live mode uses only `reviewed` facts (seeds as fallback) · D7 catch-up started · special sessions (Muhurat / DR test) excluded from averages in live mode · Angel One first, keyed by broker.

## 2. To-dos by phase

### Phase 2 — finish the catch-up
- [x] **2.1 AB reviews the 178 figures** on the review page. *Owner: AB.* Exit: no figure left "to review".
- [x] **2.2 Apply decisions.** *Done 23 Oct: 178 → reviewed (status only; SQL in `out/apply_review_2026-10-23.sql`).* Read the page's `reviews` collection (ArtifactData list → `out_dir`), run `apply_review.py` (the script does every value change), show AB the SQL, and then ops-runner executes it. *Owner: main → ops-runner.* Exit: count of `reviewed` = count approved; flagged figures still `staged`, with the note attached.
- [x] **2.3 Re-read the flagged figures** *(none flagged)* from the PDF page and stage corrected rows (`supersedes` = old fact_id). *Owner: filing-extractor.* Exit: AB approves the corrections.
- [x] **2.4 Back-source the four revenue-mix differences** *Done 23 Oct: each Excel value = whole-number % of broking × whole-number broking share on the deck of that quarter (rounding, not restatement); `out/checks/2_4_backsource.md`.* (Q3/Q4 FY25 F&O and commodity). Find the Q3 and Q4 FY25 decks on the NSE feed and compare them with the Q2 FY27 deck. *Owner: filing-extractor.* Exit: each Excel value traced to a deck page, or marked as restated.
- [ ] **2.5 P&L lines from the Q2 FY27 results PDF** (scanned pp. 3–15). Not needed for the ADR. *Owner: filing-extractor; low priority.*

### Phase 3 — live engine (Opus designs, engine-coder implements, recompute-checker verifies)
- [x] **3.0 Spec first.** *Signed off 23 Oct; all seven §7 proposals accepted.* The main session writes `docs/LIVE_SPEC.md`: each switch from parity to live, its rule, its inputs, and the expected direction of the ADR change. *Owner: main (Opus).* Exit: AB signs off.
- [x] **E1 Derive period ranges from `sb_calendar`.** A day with no calibration raises or is flagged, never dropped. Exit: a test where November exists in the calendar fails loudly without inputs.
- [x] **E2 Live loader** by `metric × period` from reviewed facts, with seeds as fallback; cell lookups kept for parity only. Exit: the loader returns Q2 FY27 inputs; the parity test is unchanged.
- [x] **E3 Summary for every FY / quarter / month** (D1). *Code + exit test done; migration `20261023_sb_summary_cells_period` applied 23 Oct.* Store the rows in `sb_summary_cells` with `period_key`. Comparisons follow the selected period. Exit: the parity labels reproduce today's 264 cells.
- [x] **E4 Guards for short history** (last-45, weekday, division by zero) → "insufficient data". Exit: unit tests.
- [x] **E5 Integrity checks** before every run: missing days, frozen series, jumps of 5× / 0.2×, unit sanity. A failure blocks publishing. Exit: the known lake gaps (BSE cash 15 Jun 2026; NSE IO/SO 12–15 Oct; MCX 27–28 May) are caught.
- [~] **E6 DB reader** *(coded; the CI-vs-snapshot test runs once the secrets exist)* using `SUPABASE_SERVICE_KEY` from the environment (never hard-coded). Exit: a run from CI equals a run from the snapshot.
- [ ] **3.1 Switches, one commit each, each with an ADR bridge** (FY27, Q2 FY27, Oct-26, per segment):
  - [x] (a) J8 = 35: commodity +2.857% on every day; F&O +0.087% from Apr-26 (J8 is in the Q3 FY26 F&O share of orders); Consolidated FY27 +0.30%. Bridge `out/bridges/a.md`, check `out/checks/switch_a.md` (22/22 agree).
  - [x] (b) one-decimal revenue mix (21 cells, Q3 FY25–Q1 FY27): F&O −0.064%, cash −1.57% projected (FY27 −2.87%: Q1 FY27 actual 9% → 8.6%), commodity +1.667%; Consolidated FY27 −0.23%. `out/bridges/b.md`, check `out/checks/switch_b.md`.
  - [x] (c) BSE contracts unfrozen (15 imputed days, 29 Sep–21 Oct, from the lake): F&O Oct-26 6.7458 → 11.6734 (+73.0%), FY27 +5.36%; Consolidated Oct-26 +31.6%. `out/bridges/c.md`, check `out/checks/switch_c.md` (13/13 agree).
  - [x] (d) special sessions excluded from averages (F&O, cash, commodity; MTF keeps them — AB 23 Oct): FY27 / Q2 FY27 / Oct-26 unchanged; Oct-25 Consolidated +3.42% (Oct-26 YoY +26.0% → +21.8%), Q3 FY26 +1.10%. `out/bridges/d.md`, check `out/checks/switch_d.md`.
  - [x] (e) D2 monthly cash share on projected cash days (Jul 0.171, Aug 0.170, Sep 0.162; Oct uses Sep): cash Oct-26 −6.90%, Q2 FY27 −3.67%, FY27 −2.36%; Consolidated Oct-26 −0.72%. `out/bridges/e.md`, check `out/checks/switch_e.md` (20/20).
  - [x] (f) D3 quarterly commodity take rate (Q2 FY25 24.39 … Q1 FY27 22.94; Q2–Q3 FY27 carry Q1 FY27): commodity FY27 / Q2 FY27 / Oct-26 −1.61%, FY26 −1.64%; Consolidated FY27 −0.15%. Q1 FY25: *sourced 23 Oct from the Q1 FY27 deck p.31 (facts 656–661, reviewed; F&O / cash / commodity published as whole numbers only); Q1 FY25 now uses its own rate (Commodities Q1 FY25 0.638 → 0.651 Rs cr/day).* `out/bridges/f.md`, check `out/checks/switch_f.md` (33/33).
  - [x] (g) D4 MTF gross / net: MTF gross in every table (the workbook's weekday tables used net), plus an 'MTF (net)' panel at 45% × gross; Consolidated stays gross. FY/Q/M unchanged; weekday Consolidated +~2.6 Rs Cr/day. `out/bridges/g.md`, check `out/checks/switch_g.md` (29/29). Gross headline confirmed by AB, 23 Oct.
  - [x] (h) Q2 FY27 actuals in, projections rolled to Q3 FY27 (synthetic Q2 FY27 column from reviewed facts; last-actual pins → Q2 FY27; MTF Q2 book 7,453 Cr / daily industry avg): F&O FY27 +1.84%, cash +1.37%, commodity −0.92%, MTF +0.35%; Consolidated FY27 +1.18%, Q2 FY27 +1.40%, Oct-26 +1.02%. `out/bridges/h.md`, check `out/checks/switch_h.md` (101/101).
  - [x] (i) F&O and commodity monthly inputs to Sep-26 (cash is covered by e, h): F&O FY27 −1.83%, commodity Oct-26 −7.22%; Consolidated FY27 −1.30%, Oct-26 −1.67%. `out/bridges/i.md`, check `out/checks/switch_i.md` (69/69).
  - Exit for each: recompute-checker's independent numbers agree to 1e-6.
- [ ] **3.2 Out-of-sample log.** For every new quarter, store the model estimate vs reported orders and revenue by segment (as in Build Plan §2c). Exit: a table `sb_backtest` or a JSON file plus a page on the dashboard.

### Phase 4 — daily automation
- [~] **4.0 GitHub repo.** *Pushed to `abiyani-tools/brokersdashboard` on 23 Oct; AB still adds the secrets `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`.* AB creates a private repo under `abiyani-tools`. Then attach it (add_repo, access "push"), push, and AB adds the secrets. *Owner: AB, then ops-runner.*
- [~] **4.1 `daily.yml`:** *Publishing and the schedule switched on 23 Oct with AB's OK: weekdays 14:17 UTC (19:47 IST) the job checks the secrets, runs the parity gate, then `run_live.py --db --publish` — DB → snapshot, trimmed to the last day on which every engine input is complete (the limiting series goes into `sb_runs.notes`), E5 → engine a–i → E1 coverage → Summary rows → `sb_runs` ('running' → 'success' / 'failed'), `sb_calibration`, `sb_daily_revenue`, `sb_summary_cells`. A blocking E5 run is not published. Never run against the real DB from the cloud session (no key there); the first real run is the workflow's. Exit: 10 trading days unattended with no silent gaps. Known limit: NSE cash trades end 21 Oct in the lake, so runs stay as of 21 Oct until the ExchangesDash owner adds them.*
- [~] **4.2 Filing watcher:** *Built 23 Oct (`run_watch.py`, `src/extract/watch_filings.py`, `angel_press.py`; workflow `filings.yml` at 09:00 and 19:30 IST). It queries the NSE corporate-announcements API for ANGELONE, keeps `desc` in Monthly Business Updates / Press Release / Investor Presentation / Outcome of Board Meeting (results only), skips URLs or sha256 already in `sb_documents`, downloads, parses (monthly tables; press-release orders and gross revenues; decks and results are registered and flagged for the filing-extractor), compares prior-period columns with reviewed facts, and stages facts with page refs. Notice: `out/filings/<date>/summary.md` + the job summary + artifact. NSE answered from GitHub Actions on 23 Oct (API and a 13 MB PDF), so no Mac job is needed; the Mac command is in `run_watch.py` if CI is ever blocked. Rolled-back DB dry run: 3 docs + 39 facts inserted and rolled back (sequence now at 700). Scheduled runs stay dry until AB sets the repo variable `FILINGS_WRITE=true`. Waiting on AB: OK for the first real insert (the only filing missing today is the 15 Jul Q1 FY27 results outcome, 0 facts).* Exit: the October 2026 business update is staged automatically. Expected 3–6 Nov (the last four came on 3 Jul, 5 Aug, 4 Sep and 6 Oct, 07:37–08:05 IST); NSE does not pre-announce it, so the date can't be checked in advance. The 09:00 IST run catches it.

### Phase 5 — dashboard
- [ ] **5.1 "Brokers" toggle in ExchangesDash.** That repo belongs to sucaanalytics-max and is read-only for us: build it on a fork or branch and send a PR or a prompt to the owner. The page reads `sb_summary_cells`, `sb_daily_revenue` and `sb_calibration` with the publishable key. Layout = the Summary sheet: Consolidated, Broking, MTF, F&O, Cash and Commodities panels; FY / Q / M dropdowns; Actual / Estimate tags. *Owner: dashboard-builder.* Exit: a screenshot diff against the Excel for the parity run.
- [ ] **5.2 Estimate-vs-reported page** from 3.2.
- [ ] **5.3 Second broker** (Groww / Motilal): copy the fact metrics, add `broker_id` rows, write a broker-specific calibration module. *Main (Opus) decides the method.*

### Waiting on outside owners (prompts in `docs/`)
- [~] NSE cash trades into the lake. Without them the cash ADR can't move past 21 Oct 2026. `Prompt_for_ExchangesDash_owner.md`
- [~] Read access to the MTF table (`codex_nse_mtf_daily`), with the check values in `Prompt_for_MTF_pipeline_owner.md`.
- [~] Anon read (RLS) policies on the lake tables; fix lake gaps and junk 1999 rows.

## 3. How to run work cheaply (token rules)
1. **Never re-read raw sources in later steps.** Extractors write `data/extracted/*.json`; checkers write `out/checks/*.md`. The main session reads only those summaries.
2. **Subagents keep bulk out of context.** PDFs, SQL dumps over 200 rows, and lake pagination run in subagents and come back as a ≤ 30-line result plus a file path.
3. **Use the snapshot, not the DB, for engine work** (`snapshot/db_snapshot_*.json`). Refresh it only when the inputs change.
4. **Run tests narrowly** (`pytest -q -k <name>`) while iterating; run the full gate before each commit.
5. **Use the Batch API / scheduled jobs** for anything not time-sensitive, such as backfills or re-parsing history.
6. **One switch per commit**, so a failing bridge points to a single cause.

## 4. Agent roster and model routing
Route by the kind of work, not by its importance. **No financial extraction or unit work ever runs on Haiku** (a 10× unit error on Haiku was measured in AB's own benchmark).

| Agent | Model / effort | Does | Never does |
|---|---|---|---|
| **main session** | Opus / high | Specs, deciding what a number means, projection rules, bridges, sign-off packs for AB, writing agent prompts | Bulk PDF reading, routine SQL |
| `filing-extractor` | Sonnet / medium | NSE feed → PDFs → facts JSON with page refs; sum-checks; staging | Approving facts; editing engine code |
| `recompute-checker` | Sonnet / medium | Independent recompute of any derived number or bridge from raw inputs, without reading the engine's code path | Fixing the engine (it only reports) |
| `engine-coder` | Sonnet / medium | Implements E1–E6 and the switches to the spec; keeps the parity gate green | Choosing rules not in the spec |
| `lake-auditor` | Sonnet / low | Read-only checks on the data lake (gaps, freezes, units), owner prompts | Any write to the lake |
| `dashboard-builder` | Sonnet / medium | ExchangesDash toggle (Next.js), reading `sb_*` with the publishable key | Computing ADR in the front end |
| `ops-runner` | Haiku / low | Pushes, workflow files, file moves; runs SQL that was already generated by a script and approved by AB | Generating or editing any number, unit or formula (hand back to Sonnet) |

**Hand-off contract for every subagent:** the input is a task, file paths and an exit test. The output is a file in `out/` plus a reply of ≤ 30 lines: what was done, numbers with sources, failures, and open `[SOURCE NEEDED]` items.

## 5. Next session — start here
1. Branch `claude/jolly-knuth-ws84jt` is ahead of `main` (fast-forward). `python3 -m pytest tests/ -q` → 78 passed, 1 skipped.
2. `python3 run_live.py` (dry run) must exit 0; report in `out/live/<as_of>/report.md`. After merging to `main`, run `daily` from the Actions tab (manual) to try the DB path with the secrets.
3. Closed 23 Oct (from AB's Mac): Q1 FY25 revenue mix (facts 656–661) · 2.4 back-sourcing · first published live runs (`sb_runs` fec7b8c4, 84f2ffa4) · MCX 2025-01-01 explained (morning session only) · E5 skips days the calendar marks closed. Open: 4.1 ten-day watch, 4.2 (built; first real insert and `FILINGS_WRITE` wait on AB), 3.2 / 5.2, 5.1.
4. Cumulative parity → live bridge: `out/bridges/summary.md` (Consolidated FY27 17.10 → 17.51, Q2 FY27 16.56 → 16.50, Oct-26 15.55 → 20.22).
5. Watch the first `daily` runs (Actions → daily; artifact `live-run`), then confirm the rows in `sb_runs` (mode 'live').
