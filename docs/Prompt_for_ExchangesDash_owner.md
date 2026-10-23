Context: Tusk is building a broker ADR tracker (Angel One first, more stockbrokers later). It reads
NSE/BSE daily data from the NSE-BSE Supabase project (vuswwmczfrlzjoxfvkzu) and MCX contracts from
the Octo-MCX project. It will appear as a "Brokers" toggle in ExchangesDash (separate PR later).
We need the following. Please don't change any existing revenue logic.

1. NSE cash number of trades (the main ask)
   - First confirm which pipeline currently writes nse_daily: this repo (ENABLE_SUPABASE_WRITES /
     PIPELINE_SOURCE), Research-Tusk/nse-cloud-pipeline, or the codex_* release pipeline. Make the
     change in the active writer(s).
   - scripts/nse_pipeline.py → parse_cm_record() keeps only CDT_TRADES_VALUES from
     https://www.nseindia.com/api/historicalOR/cm/tbg/daily. Also keep the number of trades
     (and, if present, number of securities traded and traded quantity) from the same response.
     Confirm the exact JSON keys from a live response (likely CDT_NOS_OF_TRADES /
     CDT_NOS_OF_SECURITY_TRADES / CDT_TRADES_QTY).
   - Add nullable columns to nse_daily: cash_trades BIGINT, cash_securities INT, cash_quantity BIGINT
     (same names as bse_daily). Update supabase_schema.sql, the JSON exports (daily_all,
     special_sessions, codex artifacts) and NSE_COLUMNS in excel_sync.py.
   - Backfill from 2023-04-03 to today, month by month, using the same endpoint.
   - Acceptance: nse_daily.cash_trades equals 25,766,997 on 2023-10-03; 35,848,491 on 2024-10-01;
     36,138,088 on 2025-06-09; 41,039,788 on 2026-05-14; 45,566,881 on 2026-10-21
     (from our NSE-sourced workbook). Add a unit test for the parser.

2. Data gaps found while reconciling (please verify and re-fetch; don't carry values forward)
   The GitHub JSON (dashboard/data) and the Supabase codex_artifacts snapshot (release published
   2026-10-22 05:10 UTC) disagree, and each has gaps the other doesn't:
   - BSE total_contracts = 0 for 62 trading days, 2026-06-01 → 2026-09-04, in codex_artifacts
     bse_dashboard (the GitHub JSON has values; e.g. 2026-06-04 = 565,266,960).
   - BSE cash_trades = 0 on 2026-07-28, 29, 30, 31 in codex_artifacts (GitHub JSON: 4,244,709 /
     3,916,621 / 4,211,764 / 3,676,075).
   - BSE cash_trades = 0 on 2026-06-15 in the GitHub JSON (codex_artifacts: 4,083,815).
   - nse_daily io_contracts and so_contracts = 0 on 2026-10-12, 13, 14, 15 although total_contracts
     is populated (check if/sf_contracts too).
   - BSE options_premium_turnover on 2026-04-02 = 85,211.36; our workbook has 85,205.45.
     Please confirm which is right.
   - Please confirm that nse_daily / bse_daily (the tables, not just the JSON) are complete for
     these dates, and which of the GitHub JSON, codex_artifacts and the tables is the source
     of record.
   - Confirm the Muhurat / DR-test sessions (2023-11-12, 2024-03-02, 2024-05-18, 2024-11-01,
     2025-10-21) are stored in nse_daily / bse_daily (we need them).

3. Octo-MCX (mcx-vercel), if you also own it
   - mcx_commodity_daily: 2026-05-27 and 2026-05-28 have only zero-contract rows (source dhan_live).
     Please re-fetch from bhavcopy.
   - MCX-only sessions on exchange holidays are missing: 2024-04-11, 04-17, 05-01, 05-23,
     06-17, 07-17.
   - Test rows dated 1999-01-01…04 (sources t, writetest, before) in mcx_commodity_daily and
     1900-01-01 / 1999-01-01 in mcx_daily_revenue. Please delete them, or tell us to filter them out.

4. Industry MTF book (needed for the MTF part of the ADR)
   - The NSE-BSE project has a table codex_nse_mtf_daily, but anon gets "permission denied", and
     its writer isn't in ExchangesDash, nse-cloud-pipeline or mcx-vercel. Which repo/job writes it
     (the "MTF2" scraper)? Is it the source of the daily industry MTF book in our brokers workbook
     (MTF data (2)!I, Rs Cr, from 2024-10-01)? Since codex_* is an experiment, please confirm this
     table will keep being updated, or move it to a stable table.
   - Please grant read-only access:
       grant select on public.codex_nse_mtf_daily to anon;
       create policy "public_read" on public.codex_nse_mtf_daily for select to anon using (true);
   - If the scraper also has a monthly series of the industry book, please point us to it.

5. Read access
   - With the anon key, nse_daily, bse_daily, nse_pnl and the other ExchangesDash tables return
     0 rows (RLS has no anon SELECT policy). Please add a read-only policy for anon on nse_daily
     and bse_daily, e.g.:
       create policy "public_read" on public.nse_daily for select to anon using (true);
       create policy "public_read" on public.bse_daily for select to anon using (true);
     No write access needed.
   - Naming: the project already has broker_* tables (sell-side research report library). Our
     stockbroker tables will use a different prefix (e.g. sb_ / retail_broker_) and will live in a
     separate Supabase project unless you prefer otherwise.
   - Any constraints we should follow for a "Brokers" toggle PR in dashboard/ (it will load a
     separate broker JSON through an /api proxy, like live.js).
