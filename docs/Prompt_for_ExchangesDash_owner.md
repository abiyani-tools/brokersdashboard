Context: Tusk runs a broker ADR tracker (Angel One first, more stockbrokers later). It reads NSE/BSE daily
data published by ExchangesDash and MCX contracts from Octo-MCX, and publishes daily to its own Supabase
project. It will later appear as a "Brokers" toggle in ExchangesDash (separate PR). We only read your
data; please don't change any existing revenue logic.

Updated 31 Oct 2026. Item 1 is what blocks us: our estimates can't move past 21 Oct 2026 without it.

1. NSE cash number of trades (the main ask)
   - Your public JSON (dashboard/data/nse_dashboard_data*.json) has cash_traded_value but no number of
     trades. BSE already has cash_trades / cash_securities / cash_quantity; we need the same for NSE.
   - First confirm which pipeline currently writes nse_daily: this repo (ENABLE_SUPABASE_WRITES /
     PIPELINE_SOURCE), Research-Tusk/nse-cloud-pipeline, or the codex_* release pipeline. Make the
     change in the active writer(s).
   - scripts/nse_pipeline.py → parse_cm_record() keeps only CDT_TRADES_VALUES from
     https://www.nseindia.com/api/historicalOR/cm/tbg/daily. Also keep the number of trades (and, if
     present, number of securities traded and traded quantity) from the same response. Confirm the exact
     JSON keys from a live response (likely CDT_NOS_OF_TRADES / CDT_NOS_OF_SECURITY_TRADES /
     CDT_TRADES_QTY).
   - Add nullable columns to nse_daily: cash_trades BIGINT, cash_securities INT, cash_quantity BIGINT
     (same names as bse_daily). Carry them into the JSON exports (nse_dashboard_data*.json, daily_all,
     special_sessions, codex artifacts), supabase_schema.sql and NSE_COLUMNS in excel_sync.py.
   - Backfill from 2023-04-03 to today, month by month, using the same endpoint.
   - Acceptance: cash_trades = 25,766,997 on 2023-10-03; 35,848,491 on 2024-10-01; 36,138,088 on
     2025-06-09; 41,039,788 on 2026-05-14; 45,566,881 on 2026-10-21 (from our NSE-sourced workbook).
     Please add a unit test for the parser.

2. Industry MTF book (needed for the MTF part of the ADR; ours also stops at 19 Oct)
   - The NSE-BSE project has codex_nse_mtf_daily, but anon gets "permission denied", and its writer isn't
     in ExchangesDash, nse-cloud-pipeline or mcx-vercel. Which repo/job writes it (the "MTF2" scraper)?
     Is it the daily industry MTF book (Rs Cr, from 2024-10-01)? Since codex_* is an experiment, please
     confirm it will keep being updated, or move it to a stable table.
   - Please either grant read-only access:
       grant select on public.codex_nse_mtf_daily to anon;
       create policy "public_read" on public.codex_nse_mtf_daily for select to anon using (true);
     or add the daily book to a public JSON in dashboard/data.
   - If the scraper also has a monthly series of the industry book, please point us to it.

3. Octo-MCX (mcx-vercel), if you own it
   - We need daily MCX total contracts (all commodities). mcx_dashboard_data.json has revenue only. Please
     add total contracts per day to a public JSON, or grant anon read on mcx_commodity_daily.
   - mcx_commodity_daily: 2026-05-27 and 2026-05-28 have only zero-contract rows (source dhan_live).
     Please re-fetch from bhavcopy.
   - MCX-only sessions on exchange holidays are missing: 2024-04-11, 04-17, 05-01, 05-23, 06-17, 07-17.
   - Test rows dated 1999-01-01…04 (sources t, writetest, before) in mcx_commodity_daily and
     1900-01-01 / 1999-01-01 in mcx_daily_revenue: please delete them, or tell us to filter them out.

4. Data gaps found while reconciling (please verify and re-fetch; don't carry values forward)
   - nse_daily io_contracts and so_contracts = 0 on 2026-10-12, 13, 14, 15 although total_contracts is
     populated (please check if/sf_contracts too).
   - BSE total_contracts = 0 for 62 trading days, 2026-06-01 → 2026-09-04, in codex_artifacts
     bse_dashboard (the GitHub JSON has values; e.g. 2026-06-04 = 565,266,960).
   - BSE cash_trades = 0 on 2026-07-28, 29, 30, 31 in codex_artifacts (GitHub JSON: 4,244,709 /
     3,916,621 / 4,211,764 / 3,676,075), and 0 on 2026-06-15 in the GitHub JSON (codex_artifacts:
     4,083,815).
   - BSE options_premium_turnover on 2026-04-02 = 85,211.36; our workbook has 85,205.45. Which is right?
   - Which of the GitHub JSON, codex_artifacts and the nse_daily / bse_daily tables is the source of
     record?
   - Please confirm the Muhurat / DR-test / Budget-day sessions (2023-11-12, 2024-03-02, 2024-05-18,
     2024-11-01, 2025-02-01, 2025-10-21, 2026-02-01) are stored in nse_daily / bse_daily.

5. Read access and the later "Brokers" PR
   - With the anon key, nse_daily, bse_daily and the other ExchangesDash tables return 0 rows (RLS has
     no anon SELECT policy). We read the public JSON in dashboard/data today, so this is only needed if
     you'd rather we read the tables:
       create policy "public_read" on public.nse_daily for select to anon using (true);
       create policy "public_read" on public.bse_daily for select to anon using (true);
     No write access needed.
   - We read dashboard/data from raw.githubusercontent.com. Please let us know before renaming those
     files or making the repo private.
   - Our tables use the sb_ prefix and live in a separate Supabase project; nothing is added to yours.
   - The Brokers view will be a self-contained PR: four new files (api/brokers.js, js/30-brokers.js,
     js/31-brokers-pat.js, brokers.css) plus a few lines in index.html, 00-core.js and 01-data.js, and one
     Vercel env var (BROKERS_SUPABASE_KEY, a publishable key). All 99 of your tests pass with it applied.
     Any constraints we should follow?
