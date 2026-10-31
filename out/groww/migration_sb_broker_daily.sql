-- sb_broker_daily: one row per broker x snapshot day x metric x period, from a daily capture of a broker's own
-- public figures (first user: Groww's investor-relations home page, src/live/refresh_groww_ir.py).
-- NOT APPLIED. For AB to approve (CLAUDE.md rule 7: migrations are explained before they run).
--
-- Why a table at all: the page keeps no daily history. It shows the closed quarters plus the quarter-to-date, and
-- overwrites the quarter-to-date every day (and restates history without notice). Whatever is not archived the day it
-- is shown is gone.
--
-- Columns, and why each exists:
--   broker_id       FK sb_brokers. Every sb_ table is keyed by broker.
--   fetched_at      the exact instant of the fetch. The page changes intraday (users, customer assets), so a day's
--                   value is only meaningful with its capture time. Also the audit trail for a re-fetch the same day.
--   snapshot_date   IST calendar date of fetched_at. The archive's day key: one capture per metric and period per day.
--   metric          what the number is (ir_stocks_turnover, ir_mtf_net_book, ir_users ...).
--   period_key      the repo's label, 'Q3 FY 2027' (same string as sb_disclosure_facts.period_key).
--   value           the number. Money in Rs Mn (converted from the page's own unit on load), counts as printed.
--   unit            'Rs Mn' | 'count'. Stored, not implied, so a unit slip is visible in the data.
--   is_qtd          true on the page's last point when that quarter is still open (quarter-to-date: partial, changes
--                   daily); false on closed quarters. A QTD value must never be read as a quarter total.
--   source          'groww_ir_site'. Which capture job wrote it (a second job or a manual import gets its own name).
--   source_ref      URL + content hash + the path of the number inside the page: traces each row to the saved HTML.
--   covers_through  OPTIONAL. The last trading day the QTD point includes. The page does not say; it is inferred from
--                   exchange turnover (src/engine/groww_ir.py, infer_covered_through) and stored only on is_qtd rows,
--                   and only when the inference is clear. NULL = not inferred; it can always be re-derived later from
--                   the stored QTD rows plus sb_market_daily, so nothing is lost if it is NULL.
--
-- Primary key (broker_id, snapshot_date, metric, period_key): a second capture on the same IST day replaces the first
-- (upsert), so the archive keeps the last capture of each day.
--
-- Access, as for the other output tables (sb_calibration, sb_daily_revenue ...): RLS on, a single public_read policy
-- (SELECT for anon and authenticated). Writes go through the service key, which bypasses RLS. Beyond the other tables I
-- also revoke the write privileges from anon / authenticated, so "anon read only" holds at the privilege level too.
--
-- Rollback (nothing else depends on the table):   drop table public.sb_broker_daily;

begin;

create table public.sb_broker_daily (
  broker_id      text        not null references public.sb_brokers (broker_id),
  fetched_at     timestamptz not null,
  snapshot_date  date        not null,
  metric         text        not null,
  period_key     text        not null,
  value          numeric     not null,
  unit           text        not null check (unit in ('Rs Mn', 'count')),
  is_qtd         boolean     not null,
  source         text        not null,
  source_ref     text        not null,
  covers_through date        null check (covers_through is null or is_qtd),
  primary key (broker_id, snapshot_date, metric, period_key)
);

alter table public.sb_broker_daily enable row level security;

create policy public_read on public.sb_broker_daily
  for select to anon, authenticated using (true);

revoke insert, update, delete, truncate, references, trigger on public.sb_broker_daily from anon, authenticated;

commit;
