Context: Tusk is building a stockbroker ADR tracker (Angel One first; Groww, Motilal Oswal later). Part
of each broker's daily revenue is MTF interest, which we model as:
  broker MTF book = broker share × industry MTF book, and
  daily MTF revenue = broker MTF book × yield / trading days.
We therefore need a reliable **daily industry MTF book** (total MTF outstanding across the market).
Our understanding is that your automated "MTF2" scraper pulls this from the NSE website and writes it
to the NSE-BSE Supabase project (vuswwmczfrlzjoxfvkzu). We only need to read it; we won't write to your
project.

What we found
- There is a table public.codex_nse_mtf_daily in vuswwmczfrlzjoxfvkzu. With the anon key it returns
  "permission denied for table codex_nse_mtf_daily" (42501).
- We couldn't find the code that writes it in sucaanalytics-max/ExchangesDash,
  Research-Tusk/nse-cloud-pipeline (all 5 branches) or sucaanalytics-max/mcx-vercel.
- We understand the codex_* tables are a parallel experiment, so we'd like to confirm this one is
  maintained.

Please answer / do the following

1. Where it runs
   - Which repo, job and schedule writes codex_nse_mtf_daily (or any other MTF table)? Please share
     the repo link, or read access to it.
   - Is this table the long-term home for the data? If codex_* may be retired, could the MTF data
     move to (or be mirrored in) a stable table, e.g. public.nse_mtf_daily?

2. What the data is
   - Exact NSE source: report or page name, URL or API endpoint, and file name pattern.
   - Columns, with units: is the industry book in Rs crore or Rs lakh? Is it the end-of-day net
     outstanding, or beginning-of-day plus fresh exposure minus liquidated? Is it scrip-wise
     or total only?
   - History start date, publication lag (T+1?), and how missing or holiday days are handled.
     We need missing days to stay empty or flagged, not carried forward from the previous day.
   - Does the scraper also hold a monthly industry series, or broker-level MTF data?

3. Check against our workbook
   Our brokers workbook ('MTF data (2)' column I, Rs crore, 507 trading days from 2024-10-01 to
   2026-10-19) was filled from the same NSE source. Please confirm your table returns these values:
     2024-10-01  81,823.53
     2025-04-01  69,043.81
     2025-10-01 1,06,409.32
     2026-05-14 1,21,761.47
     2026-10-19 1,48,568.87
   We also use a monthly series ('MTF data' column E, rounded, e.g. Oct-24 102,000; Mar-26 111,000;
   Jul-26 136,000 Rs crore). If that comes from your scraper or another source, please tell us which.

4. Read access (read-only)
     grant select on public.codex_nse_mtf_daily to anon;
     alter table public.codex_nse_mtf_daily enable row level security;
     create policy "public_read" on public.codex_nse_mtf_daily for select to anon using (true);
   (Or the equivalent for whichever stable table you choose in point 1.)

Thanks. Once read access is in place we'll check every overlapping day against the workbook and
send you any differences we find.
