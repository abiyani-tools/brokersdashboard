# Request for the ExchangesDash owner: data for a "Brokers" view

*From Tusk (Abhishek Biyani) · 31 Oct 2026*

## Why we're asking

We've built a broker revenue tracker (average daily revenue, Angel One first, more stockbrokers later). It runs off exchange volumes: NSE/BSE F&O contracts, NSE/BSE cash trades, MCX contracts and the industry MTF book.

**The goal is to integrate it into ExchangesDash as a "Brokers" view, with all exchange data flowing from your data lake**, so there's one source for the exchange numbers and one dashboard.

Today our job reads your public JSON in `dashboard/data` from GitHub, read only. It never writes to your Supabase projects or repos. Three daily series we need aren't in your lake's public output. Because of them our numbers are stuck at **21 Oct 2026**:

| # | Series | Where it is today | What we need from the lake |
|---|---|---|---|
| 1 | NSE cash: number of trades | not collected (only `cash_traded_value`) | a daily field, published in `nse_dashboard_data.json` |
| 2 | MCX: total contracts traded per day | Octo-MCX `mcx_commodity_daily`, not public | a daily field in a public JSON |
| 3 | Industry MTF book (Rs Cr) | `codex_nse_mtf_daily`; anon gets "permission denied" | a daily public JSON (or anon read) |

**If the fields are named as below, our job picks them up the same evening, with no change on our side.**

Please don't change any existing revenue logic.

---

## 1. NSE cash number of trades — blocking

**Source (already in your pipeline).** `scripts/nse_pipeline.py` → `parse_cm_record()` reads `https://www.nseindia.com/api/historicalOR/cm/tbg/daily` but keeps only `CDT_TRADES_VALUES`. The same response already carries the fields we need. We checked a live response on 31 Oct 2026; each row looks like this:

```json
{"F_TIMESTAMP": "30-Oct-2026", "CDT_NOS_OF_SECURITY_TRADES": 3641,
 "CDT_NOS_OF_TRADES": 43793587, "CDT_TRADES_QTY": 64151.92, "CDT_TRADES_VALUES": 120852.45}
```

**Please:**
1. Confirm which pipeline writes `nse_daily` today, and change that one. It could be this repo (`ENABLE_SUPABASE_WRITES` / `PIPELINE_SOURCE`), `Research-Tusk/nse-cloud-pipeline`, or the codex_* release pipeline.
2. Keep `CDT_NOS_OF_TRADES`, `CDT_NOS_OF_SECURITY_TRADES` and `CDT_TRADES_QTY` alongside the value.
3. Store them in nullable columns on `nse_daily`, with the same names as `bse_daily`: `cash_trades BIGINT`, `cash_securities INT`, `cash_quantity BIGINT`. Update `supabase_schema.sql` and `NSE_COLUMNS` in `excel_sync.py`.
4. Publish `cash_trades` (raw count) on every row of `daily_all` and `special_sessions` in `dashboard/data/nse_dashboard_data.json`, and in the `_eff` variant.
5. Backfill from 2023-04-03 to today, month by month, using the same endpoint (`?month=Oct&year=26`).
6. Add a unit test for the parser.

**Acceptance (`cash_trades`, raw count):**

| Date | Value | Date | Value |
|---|---:|---|---:|
| 2023-10-03 | 25,766,997 | 2026-10-21 | 45,566,881 |
| 2024-10-01 | 35,848,491 | 2026-10-22 | 42,604,615 |
| 2025-06-09 | 36,138,088 | 2026-10-23 | 53,501,357 |
| 2026-05-14 | 41,039,788 | 2026-10-30 | 43,793,587 |

---

## 2. MCX total contracts per day — blocking

**What.** The day's total contracts traded on MCX, across all commodities and instruments (FUTCOM, OPTFUT, FUTIDX, OPTIDX). That's `sum(contracts)` per `trading_date` in Octo-MCX `mcx_commodity_daily`, from bhavcopy (sources `mcx_historical` / `dhan_live`), as a raw count.

**Publish (either option works):**
- add `total_contracts` to each row of `daily_all` and `special_sessions` in `dashboard/data/mcx_dashboard_data.json`, which has revenue only today; or
- a separate file `dashboard/data/mcx_contracts_daily.json` with rows `{"date": "YYYY-MM-DD", "total_contracts": N}`.

Cover 2023-09-29 onwards, including MCX-only sessions.

**Please also fix in `mcx_commodity_daily`:**
- 2026-05-27 and 2026-05-28 have only zero-contract rows (source `dhan_live`). Please re-fetch them from bhavcopy.
- MCX-only sessions on exchange holidays are missing: 2024-04-11, 04-17, 05-01, 05-23, 06-17 and 07-17.
- Test rows dated 1999-01-01…04 (sources `t`, `writetest`, `before`), plus 1900-01-01 and 1999-01-01 in `mcx_daily_revenue`. Please delete them.

**Acceptance (raw count; these match your `mcx_commodity_daily` today):**

| Date | Value |
|---|---:|
| 2024-10-01 | 6,093,508 |
| 2025-06-09 | 4,815,253 |
| 2026-05-14 | 53,827,133 |
| 2026-10-19 | 12,615,403 |
| 2026-10-21 | 18,289,605 |

---

## 3. Industry MTF book — needed next (ours stops at 19 Oct 2026)

`codex_nse_mtf_daily` in the NSE-BSE project looks like the daily industry MTF book (Rs Cr, from 2024-10-01). But anon gets "permission denied", and its writer isn't in ExchangesDash, nse-cloud-pipeline or mcx-vercel.

**Please tell us:**
- which repo or job writes it (the "MTF2" scraper?);
- whether it will keep running. codex_* reads like an experiment; if so, please move it to a stable table;
- whether there's also a monthly series of the industry book.

**Publish:** `dashboard/data/nse_mtf_daily.json` with rows `{"date": "YYYY-MM-DD", "book_cr": N}`, from 2024-10-01. Or grant read access:

```sql
grant select on public.codex_nse_mtf_daily to anon;
create policy "public_read" on public.codex_nse_mtf_daily for select to anon using (true);
```

**Acceptance (Rs Cr):**

| Date | Value |
|---|---:|
| 2024-10-01 | 81,823.53 |
| 2025-06-09 | 80,962.95 |
| 2026-05-14 | 121,761.47 |
| 2026-10-19 | 148,568.87 |

---

## 4. Integrating the Brokers view into ExchangesDash

Once items 1–3 are live, we'd like to send a self-contained PR:

- **New files (four):** `dashboard/api/brokers.js`, `dashboard/js/30-brokers.js`, `dashboard/js/31-brokers-pat.js`, `dashboard/brokers.css`.
- **Small edits to three files:**
  - `index.html`: the Brokers button, tab sections and script tags;
  - `js/00-core.js`: a Brokers entry in the tab lists, plus a two-line hand-off in `switchExchange`;
  - `js/01-data.js`: the freshness check skips the Brokers view.
- **One Vercel env var:** `BROKERS_SUPABASE_KEY` (a publishable, read-only key).
- **Tests:** all 99 of your tests pass with it applied.

**Where the broker tables should live.** Our broker-side tables use the `sb_` prefix: disclosures, calendar, runs, and the published summary, daily revenue and calibration. Today they sit in a separate Supabase project. To keep everything in one lake we could move them into your NSE-BSE project, still under `sb_`. Your existing `broker_*` tables (the research-report library) would be untouched, and the daily job would write only to `sb_` tables. Which would you prefer: a separate project read through the `/api/brokers` proxy, or `sb_` tables in your project?

**Questions:**
- Any constraints we should follow for the PR (structure, naming, tests, deploy flags)?
- We read `dashboard/data` from raw.githubusercontent.com. Please tell us before renaming those files or making the repo private.

---

## 5. Smaller data fixes (non-blocking)

Please verify and re-fetch these; don't carry values forward.

- **NSE option contracts:** `nse_daily` has `io_contracts` and `so_contracts` = 0 on 2026-10-12…15, although `total_contracts` is populated, and the JSON has no `io/so_contracts` after 2026-10-15. Please check `if/sf_contracts` too.
- **BSE cash trades:** 0 on 2026-06-15 in the GitHub JSON (codex_artifacts has 4,083,815). codex_artifacts has 0 on 2026-07-28…31, where the JSON has 4,244,709 / 3,916,621 / 4,211,764 / 3,676,075.
- **BSE F&O contracts:** codex_artifacts has 0 for 2026-06-01 → 2026-09-04, where the JSON has values. Which source is the record?
- **BSE options premium on 2026-04-02:** 85,211.36 in your data vs 85,205.45 in our workbook.
- **Special sessions:** please confirm these are in `nse_daily` / `bse_daily` and in the JSON. The JSON's `special_sessions` lists the first five only.
  - Muhurat: 2023-11-12, 2024-11-01, 2025-10-21
  - DR tests: 2024-03-02, 2024-05-18
  - Budget days: 2025-02-01, 2026-02-01

Thank you!
