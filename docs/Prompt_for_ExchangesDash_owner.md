Hi, a request from Tusk (Abhishek Biyani). We run a broker revenue tracker (Angel One first) that reads your
public ExchangesDash data, read only. Every weekday our job copies dashboard/data/nse_dashboard_data.json and
bse_dashboard_data.json from your GitHub repo. We never write to your Supabase projects or repos.

Our estimates are stuck at 21 Oct 2026 because two daily series are missing from your public data. Item 3 is
needed soon after. Items 1–3 below are the whole ask; item 4 lists smaller data fixes for whenever you have
time. Please don't change any existing revenue logic.

| # | Series | Today | What we need |
|---|---|---|---|
| 1 | NSE cash: number of trades | not collected (only cash_traded_value) | a daily field in nse_dashboard_data.json |
| 2 | MCX: total contracts traded per day | in Octo-MCX (mcx_commodity_daily), not public | a daily field in a public JSON |
| 3 | Industry MTF book (Rs Cr) | in codex_nse_mtf_daily, anon gets "permission denied" | a daily public JSON, or anon read |

If the fields are named as below, our job picks them up with no change on our side.

----------------------------------------------------------------------------------------------------------
1. NSE cash number of trades  (blocking)
----------------------------------------------------------------------------------------------------------
- Where: scripts/nse_pipeline.py → parse_cm_record() keeps only CDT_TRADES_VALUES from
  https://www.nseindia.com/api/historicalOR/cm/tbg/daily. The same response carries the number of trades
  (and number of securities traded, traded quantity). Please confirm the exact keys from a live response
  (likely CDT_NOS_OF_TRADES / CDT_NOS_OF_SECURITY_TRADES / CDT_TRADES_QTY).
- First confirm which pipeline actually writes nse_daily today (this repo with ENABLE_SUPABASE_WRITES /
  PIPELINE_SOURCE, Research-Tusk/nse-cloud-pipeline, or the codex_* release pipeline) and change that one.
- Store: nullable columns on nse_daily, same names as bse_daily:
  cash_trades BIGINT, cash_securities INT, cash_quantity BIGINT. Update supabase_schema.sql and
  NSE_COLUMNS in excel_sync.py.
- Publish: add cash_trades (raw count) to every row of daily_all and special_sessions in
  dashboard/data/nse_dashboard_data.json (and the _eff variant).
- Backfill: 2023-04-03 to today, month by month, same endpoint.
- Acceptance (raw counts, from our NSE-sourced workbook):
    2023-10-03  25,766,997      2025-06-09  36,138,088      2026-10-21  45,566,881
    2024-10-01  35,848,491      2026-05-14  41,039,788
  Please add a unit test for the parser.

----------------------------------------------------------------------------------------------------------
2. MCX total contracts per day  (blocking)
----------------------------------------------------------------------------------------------------------
- What: the day's total contracts traded on MCX across all commodities and instruments (FUTCOM, OPTFUT,
  FUTIDX, OPTIDX), i.e. sum(contracts) per trading_date in Octo-MCX mcx_commodity_daily, from bhavcopy
  (sources mcx_historical / dhan_live). Raw count.
- Publish: add total_contracts to each daily row of dashboard/data/mcx_dashboard_data.json (it has revenue
  only today), from 2023-09-29 onwards, including MCX-only sessions. If it's easier, a separate file
  dashboard/data/mcx_contracts_daily.json with rows {date, total_contracts} works too. Alternatively,
  grant anon SELECT on mcx_commodity_daily in the Octo-MCX project.
- Please also fix, in mcx_commodity_daily:
    - 2026-05-27 and 2026-05-28 have only zero-contract rows (source dhan_live): re-fetch from bhavcopy.
    - MCX-only sessions on exchange holidays are missing: 2024-04-11, 04-17, 05-01, 05-23, 06-17, 07-17.
    - Test rows dated 1999-01-01…04 (sources t, writetest, before); and 1900-01-01 / 1999-01-01 in
      mcx_daily_revenue: please delete them.
- Acceptance (raw counts; these match your mcx_commodity_daily today):
    2024-10-01   6,093,508      2026-05-14  53,827,133      2026-10-21  18,289,605
    2025-06-09   4,815,253      2026-10-19  12,615,403

----------------------------------------------------------------------------------------------------------
3. Industry MTF book  (needed next; ours stops at 19 Oct 2026)
----------------------------------------------------------------------------------------------------------
- codex_nse_mtf_daily in the NSE-BSE project looks like the daily industry MTF book (Rs Cr, from
  2024-10-01), but anon gets "permission denied" and its writer isn't in ExchangesDash, nse-cloud-pipeline
  or mcx-vercel. Which repo/job writes it (the "MTF2" scraper), and will it keep running? codex_* reads as
  an experiment; if so, please move it to a stable table.
- Publish: dashboard/data/nse_mtf_daily.json with rows {date, book_cr}, from 2024-10-01. Or grant read:
    grant select on public.codex_nse_mtf_daily to anon;
    create policy "public_read" on public.codex_nse_mtf_daily for select to anon using (true);
- Acceptance (Rs Cr, from our workbook): 2024-10-01 81,823.53 · 2025-06-09 80,962.95 ·
  2026-05-14 121,761.47 · 2026-10-19 148,568.87.
- If there's also a monthly series of the industry book, please point us to it.

----------------------------------------------------------------------------------------------------------
4. Smaller data fixes (non-blocking; please verify and re-fetch, don't carry values forward)
----------------------------------------------------------------------------------------------------------
- nse_daily io_contracts and so_contracts are 0 on 2026-10-12…15 although total_contracts is populated,
  and the JSON has no io/so_contracts after 2026-10-15. Please check if/sf_contracts too.
- BSE cash_trades = 0 on 2026-06-15 in the GitHub JSON (codex_artifacts has 4,083,815). codex_artifacts in
  turn has 0 on 2026-07-28…31 (JSON: 4,244,709 / 3,916,621 / 4,211,764 / 3,676,075) and BSE
  total_contracts = 0 for 2026-06-01 → 2026-09-04 (JSON has values). Which source is the record?
- BSE options_premium_turnover on 2026-04-02: 85,211.36 in your data vs 85,205.45 in our workbook.
- Please confirm the special sessions are in nse_daily / bse_daily and the JSON: Muhurat 2023-11-12,
  2024-11-01, 2025-10-21; DR tests 2024-03-02, 2024-05-18; Budget days 2025-02-01, 2026-02-01 (the
  JSON's special_sessions lists the first five only).

----------------------------------------------------------------------------------------------------------
Notes
----------------------------------------------------------------------------------------------------------
- We read dashboard/data from raw.githubusercontent.com (latest commit per file). Please tell us before
  renaming those files or making the repo private.
- Our tables use the sb_ prefix in a separate Supabase project; nothing is added to yours.
- Later we'd like to send a self-contained "Brokers" PR to ExchangesDash: four new files (api/brokers.js,
  js/30-brokers.js, js/31-brokers-pat.js, brokers.css), a few lines in index.html, 00-core.js and
  01-data.js, and one Vercel env var (BROKERS_SUPABASE_KEY, a publishable key). All 99 of your tests pass
  with it applied. Any constraints we should follow?

Thank you!
