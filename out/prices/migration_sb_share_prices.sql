-- sb_share_prices: one row per broker x trading day, the listed share's daily close (for the dashboard's price vs
-- ADR-DMA charts and regression). Written by the daily job (src/live/refresh_prices.py); independent of engine runs.
-- Approved by AB on 2 Nov 2026 ("Yes, build it here"); applied the same day.
--
-- Columns, and why each exists:
--   broker_id   FK sb_brokers. Every sb_ table is keyed by broker.
--   trade_date  the session's date in IST (Yahoo's bar timestamp + the exchange's gmtoffset).
--   ticker      the Yahoo symbol read (ANGELONE.NS, MOTILALOFS.NS, GROWW.NS); stored so a symbol change is visible.
--   close       Yahoo chart 'close', Rs: split- and bonus-adjusted, NOT dividend-adjusted. The charts and the
--               regression use this column.
--   adj_close   Yahoo 'adjclose', Rs: also dividend-adjusted. Kept for reference only (it moves the past on every
--               ex-dividend date, which has nothing to do with ADR).
--   source      'yahoo_chart_v8'. Which job wrote it.
--   source_ref  the request URL: every number traces to where it was read (CLAUDE.md rule 1).
--   fetched_at  when the job read it.
--
-- Primary key (broker_id, trade_date). Each daily run re-reads the full history and upserts every row, because Yahoo
-- restates all past closes after a split or bonus: a partial upsert would leave old rows on the old basis.
--
-- Access, as for sb_broker_daily: RLS on, a single public_read policy (SELECT for anon and authenticated); writes go
-- through the service key; write privileges revoked from anon / authenticated.
--
-- Rollback (nothing else depends on the table):   drop table public.sb_share_prices;

create table public.sb_share_prices (
  broker_id   text        not null references public.sb_brokers (broker_id),
  trade_date  date        not null,
  ticker      text        not null,
  close       numeric     not null check (close > 0),
  adj_close   numeric     null check (adj_close is null or adj_close > 0),
  source      text        not null,
  source_ref  text        not null,
  fetched_at  timestamptz not null,
  primary key (broker_id, trade_date)
);

alter table public.sb_share_prices enable row level security;

create policy public_read on public.sb_share_prices
  for select to anon, authenticated using (true);

revoke insert, update, delete, truncate, references, trigger on public.sb_share_prices from anon, authenticated;
