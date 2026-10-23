# Data Lake Review — what exists, what matches the Excel, what's missing (Angel One ADR)

**Reviewed on:** 22 Oct 2026, read-only.
**Repos (public, cloned):**
- `sucaanalytics-max/ExchangesDash` @ `b2049b5` (bot commit 22 Oct 2026 09:35 UTC)
- `sucaanalytics-max/mcx-vercel` @ `4fc70a5` (17 Oct 2026)

**Supabase:**
- **Octo-MCX** (`avqwpebveqetwwzkmtux`): queried directly with the public read key found in the mcx-vercel code.
- **NSE-BSE** (`vuswwmczfrlzjoxfvkzu`): no read key in either repo. Reviewed through the schema SQL and the committed JSON exports. CLAUDE.md says these are "the same rows Supabase holds", but this is **not yet verified against the database itself**.

**Comparison base:** the daily inputs in `20260714_brokers dashboard v2.xlsx`, matched by date.

---

## 1. Inventory

### NSE-BSE project — written by ExchangesDash, GitHub Actions 00:30 / 12:30 / 15:30 UTC Mon–Fri

| Table | Grain | Fields relevant to the Angel ADR |
|---|---|---|
| `nse_daily` | date, from 2023-04-03 | `total_contracts` (F&O), `if/sf/io/so_contracts`, `io_premium`, `so_premium`, `if/sf_turnover`, `cash_traded_value`, `fy`, `fy_quarter`, `fy_month`, `day` |
| `bse_daily` | date, from 2023-04-03 | `total_contracts` (F&O), `options_premium_turnover`, `futures_turnover`, `cash_trades`, `cash_traded_value` |
| `nse_pnl`, `nse_pnl_fy`, `nse_cost_ratios`, `*_aggregates`, `*_pipeline_runs`, `live_samples` | — | Not needed for Angel (exchange P&L, live intraday) |

- Sources: NSE `api/historicalOR/fo/tbg/daily` and `…/cm/tbg/daily` (curl_cffi with Chrome impersonation, run from GitHub runners); BSE `Mkt_Deri_ArchiveSum` and `histoequitymonthdisplay` APIs.
- Period labels already use the Excel's format (`Q3 FY 2027`, `FY 2027 October`), so lookups line up directly.
- The schema SQL is out of date. The JSON carries `if/sf/io/so_contracts`, which `supabase_schema.sql` doesn't list.

### Octo-MCX project — written by mcx-vercel (relay + bhav refresh)

| Table | Rows | Range | Relevant? |
|---|---|---|---|
| `mcx_commodity_daily` | 42,169 | 2022-01-03 → 2026-10-21 | **Yes.** Contracts by commodity × instrument (FUTCOM / OPTFUT / FUTIDX / OPTIDX); the daily sum = MCX contracts |
| `mcx_daily_revenue` | 1,207 | 2022-01-03 → 2026-10-21 | MCX's own revenue (futures notional, options premium); `is_actual = false` before Sep 2024 |
| `mcx_oi_participants`, `mcx_margin_daily`, `mcx_valuation`, `mcx_share_price`, `mcx_*_signals`, `mcx_icomdex_daily`, `mcx_commodity_prices`, `relay_heartbeat`, `codex_*` | — | — | Not needed for Angel |

**No broker data in either project or repo.** There are no Angel/Groww/MOSL disclosures, no MTF data, and no broker tables.

---

## 2. Angel ADR inputs mapped to the data lake

| Excel input | Data-lake field | Match with Excel (by date) | Notes |
|---|---|---|---|
| NSE total F&O contracts (`backtesting F&O!T`) | `nse_daily.total_contracts` | **752 / 752 exact** | ✅ |
| NSE index/stock option contracts (`P`, `Q`) | `nse_daily.io_contracts`, `so_contracts` | 744 / 748 | Lake shows **0 for 12–15 Oct 2026** (the total is still right). Not used by the Angel ADR |
| BSE F&O contracts (`U`) | `bse_daily.total_contracts` | 737 / 752 | **All 15 differences are the Excel's frozen 29 Sep–21 Oct 2026 values. The lake has the real figures** (e.g. 1 Oct 513.0 Mn, 15 Oct 493.5 Mn vs the Excel's 18.96) |
| NSE / BSE option premium (`J`, `M`) | `io_premium`, `bse.options_premium_turnover` | 752/752; 751/752 | BSE 2 Apr 2026: 85,211.36 (lake) vs 85,205.45 (Excel) |
| BSE cash trades (`backtesting cash!M`) | `bse_daily.cash_trades` | 752 / 753 | Lake has **0 on 15 Jun 2026** (the Excel has 4.08 Mn) |
| **NSE cash trades** (`backtesting cash!L`) | — | **not stored** | ❌ The NSE pipeline calls the CM endpoint but keeps only `CDT_TRADES_VALUES` (traded value). The trade count most likely comes back in the same response (field name to confirm) |
| NSE cash turnover (`backtesting cash!I`) | `nse_daily.cash_traded_value` | 415 / 753 | The 338 mismatches start 9 Jun 2025 and are the **Excel's 2-row misalignment** (Excel 11 Jun = lake 9 Jun). Not used by the Angel ADR |
| MCX contracts (`Commodities!F`) | Σ `mcx_commodity_daily.contracts` per date | **652 / 654 exact** | Lake has **0 on 27–28 May 2026** (only zero-contract `dhan_live` rows). 6 MCX-only sessions from 2024 (11 Apr, 17 Apr, 1 May, 23 May, 17 Jun, 17 Jul) are **missing** from the lake |
| Industry MTF book, daily (`MTF data (2)!I`) | — | **not in lake** | ❌ |
| Industry MTF book, monthly (`MTF data!E`) | — | **not in lake** | ❌ |
| Angel monthly business update fields | — | **not in lake** | ❌ New store needed (build plan §2a) |
| Angel quarterly fields | — | **not in lake** | ❌ New store needed (build plan §2b) |

### Convention differences to handle for exact parity

- **Special sessions:** ExchangesDash moves the Muhurat and DR-test sessions (12 Nov 2023, 2 Mar 2024, 18 May 2024, 1 Nov 2024, 21 Oct 2025) out of `daily_all` into `special_sessions`. The Excel **includes** them in the Angel averages. Parity mode must merge them back.
- **Duplicate row in the Excel:** `backtesting F&O` has 1 Feb 2024 twice. That affects FY 2024 only, which isn't shown on the Summary.
- **Junk rows in Octo-MCX:** `mcx_commodity_daily` has test rows dated 1999-01-01…04 (sources `t`, `writetest`, `before`). `mcx_daily_revenue` has 1900-01-01 and 1999-01-01. Filter these out.

### Impact of switching F&O to lake BSE contracts (all other Excel inputs unchanged)

| F&O ADR, Rs Cr | Excel | With lake BSE contracts |
|---|---|---|
| FY 2027 September | 8.3943 | 8.6177 |
| FY 2027 October (to 21 Oct) | 6.7442 | **11.6706** |
| FY 2027 YTD | 9.2856 | 9.7837 |

Computed as Excel daily revenue × (NSE + lake BSE) / (NSE + Excel BSE), which holds because daily F&O revenue is proportional to market contracts.

---

## 2b. Direct check of the NSE-BSE Supabase project with the anon key (22 Oct 2026)

**What the anon key can and can't read:**
- Tables that exist but return **0 rows** to anon (row-level security, no read policy): `nse_daily`, `bse_daily`, `nse_pnl`, `nse_pnl_fy`, `nse_cost_ratios`, `*_aggregates`, `*_pipeline_runs`, `broker_sweep_*`, `broker_qa_runs`, `broker_url_rules`, `broker_subject_rules`, `broker_improvement_log`, `rl_documents`, `rl_runs`.
- Tables that refuse anon outright ("permission denied"): `codex_releases`, `codex_mcx_daily`, `codex_raw_observations`, `codex_data_quality_results`.
- **Tables that are readable:**
  - `codex_artifacts`: published dashboard snapshots for NSE, BSE and MCX, each carrying `daily_all`. Latest release published 2026-10-22 05:10 UTC, as of 21 Oct.
  - `codex_latest_live`, `codex_live_snapshots`: intraday data.
  - `broker_brokers` (16), `broker_reports` (1,822), `broker_companies` (665).

**`broker_*` is a sell-side research-report library**: 16 research houses (Motilal Oswal, Kotak, Emkay, …), filed from OneDrive/Outlook. It isn't stockbroker data. Our stockbroker tables need a different prefix to avoid confusion.

**`codex_*` looks like a second, release-based pipeline** publishing the same dashboards. Its BSE data differs from the GitHub JSON:

| Field | GitHub JSON | `codex_artifacts` | Excel |
|---|---|---|---|
| BSE F&O contracts, 1 Jun–4 Sep 2026 (62 days) | values | **0** | = GitHub |
| BSE cash trades, 28–31 Jul 2026 | values | **0** | = GitHub |
| BSE cash trades, 15 Jun 2026 | **0** | 4,083,815 | = codex |
| Muhurat / DR-test sessions | separate `special_sessions` | included in `daily_all` (880 vs 875 rows) | included |
| NSE `if/sf/io/so_contracts` | present | **absent** | — |
| NSE cash trades | absent | absent | present |

Revenue fields also differ between the two (different take-rate rules). That isn't relevant for Angel, which uses volumes only.

**Implication:** neither copy is complete on its own. The tracker should read the base tables `nse_daily` / `bse_daily` once anon read access is granted, or the GitHub JSON as a fallback. Every gap gets flagged rather than filled.

## 2c. Follow-ups (22 Oct 2026)

- **`codex_*` is a parallel experiment** (confirmed by AB). It is not a source for the tracker.
- **MTF:** `Research-Tusk/nse-cloud-pipeline`, all 5 branches, has no MTF code. The NSE-BSE project does have `codex_nse_mtf_daily`, but anon is refused ("permission denied") and its writer isn't in any repo reviewed. The owner prompt asks for the writer, its continuity and read access.
- **New Supabase project for the stockbroker tables:** `brokers-dashboard`, ref `everjfpbnlbcpuarnhob`, region ap-south-1 (Mumbai), org abiyani-tools's Org. Created 22 Oct 2026 and empty so far.

## 2d. `brokers-dashboard` database — state at 22 Oct 2026, 22:45 IST

**Built by another session.** Migration `sb_core_schema` plus a token-gated loader, run at about 15:50 IST. Tables: `sb_brokers`, `sb_calendar`, `sb_documents`, `sb_disclosure_facts`, `sb_market_daily`, `sb_market_monthly`, `sb_assumptions`, `sb_parity_pins`, `sb_runs`, `sb_calibration`, `sb_daily_revenue`, `sb_summary_cells`. The broker id is `ANGELONE`.

**Audited against the Excel. Every value matches the cell it cites:**
- 477 disclosure facts
- 11,011 daily market rows; the dates also match their Excel rows
- 33 monthly MTF rows
- 11 parity pins with values
- 785 calendar days (labels, weekdays, 5 special sessions)

**Added this session:**
- `sb_parity_expected`, the Excel outputs to reproduce: 8,066 daily, 467 calibration and 264 Summary cells. A spot check: FY27 ADRs recomputed from it equal the Summary cells (F&O 9.285586, Cash 2.064588, Commodities 1.537138, MTF 4.209385). The Q4 FY26 F&O take rate recomputed from the facts is 21.550176, matching the Excel.
- Data-lake rows in `sb_market_daily`:
  - source `exchangesdash_json@b2049b5` for NSE/BSE;
  - source `octo_mcx@2026-10-22` for MCX;
  - suspect zeros flagged.

  Contracts and trades are stored as raw counts, the same unit as the Excel rows.
- **In-database reconciliation of Excel vs data lake, overlapping days:**

  | Metric | Matching days | Differences |
  |---|---|---|
  | NSE F&O contracts | 757 / 757 | — |
  | BSE F&O contracts | 742 / 757 | the 15 frozen Excel days |
  | BSE cash trades | 757 / 758 | 15 Jun 2026, lake 0 |
  | MCX contracts | 652 / 654 | 27–28 May 2026, lake 0 |
  | NSE index/stock option contracts | 749 / 753 and 750 / 754 | 12–15 Oct 2026, lake 0 |
  | BSE premium and futures turnover | 756 / 757 | 2 Apr 2026 |
  | NSE cash turnover | 419 / 758 | Excel 2-row shift from 9 Jun 2025 |
  | BSE cash turnover | 418 / 758 | **same 2-row shift** (new finding; 339/340 match at lag 2); excel_seed rows now flagged `suspect` |

- **Access:** the public key reads only `sb_brokers` and `sb_calendar`. Output tables are empty but readable once runs exist. All inputs, facts, pins and fixtures are private.
- My temporary loader is dropped. The other session's `sb_tmp_seed_load` still exists, but the public key is refused ("permission denied"). **Pending AB's OK to drop it.**
- **Schema note:** `sb_market_daily` has no unit column. Contracts and trades are raw counts, turnover is Rs Cr, the MTF book is Rs Cr. Adding a `unit` column is recommended.

## 3. What this changes in the build plan

1. **Exchange data needn't be rebuilt.** NSE F&O, BSE F&O, BSE cash trades and MCX contracts already exist and match. The plan's Phase 3 shrinks to:
   - adding **NSE cash trades**;
   - an **industry MTF book** collector;
   - handling the gaps above (data quality flags, not carry-forward).
2. **Where the pipeline runs:** ExchangesDash fetches NSE from GitHub Actions with curl_cffi, so the broker pipeline can follow that pattern (Actions → Supabase → static dashboard on Vercel) rather than a Mac-only job.
3. **New storage is still needed** for Angel disclosures, MTF and NSE trades. Where it goes depends on write access (question 1 below).
