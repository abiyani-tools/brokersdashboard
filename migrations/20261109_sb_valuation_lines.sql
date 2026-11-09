-- PLAN 5.8: sb_valuation_lines holds the valuation (src/engine/valuation.py): three methods (regression, ratio, ADR via
-- the PAT model), their weighted net value, and the daily series behind the Valuation tab's charts.
-- NOT YET APPLIED. Needs AB's OK (CLAUDE.md rule 7) and a notice to the ExchangesDash owner, whose mirror copies every
-- sb_* table (brokers_mirror_schema.sql there needs the same table).
--
-- What it does, step by step:
--   1. Creates sb_valuation_lines. run_id is the broker's ADR run (sb_runs) whose daily ADR the valuation used, the
--      same run the PAT step wrote sb_pat_lines for. No new run rows.
--   2. section:
--        'summary'  : line regression | ratio | adr | net | upside per scenario (bear / base / bull), per timeline window
--                     (period_key 'all' = the workbook's window, '3m', '6m', '1y', '2y', '3y', 'apr25'; a window the
--                     data do not cover is not written)
--        'inputs'   : per window: slope, intercept, R², days in the fit, ratio mean and SD (scenario '')
--        'common'   : close, current ADR, regression band (period_key '')
--        'weights'  : the weight of each method (period_key = regression | ratio | adr)
--        'series'   : one row per trade date (period_key 'YYYY-MM-DD') and line adr | dma | price | ratio | implied
--        'pe'       : Angel One's consolidated TTM P/E per trade date (line 'pe')
--        'pe_bands' : P/E mean, SD and current per window (period_key '3m' … '3y', 'apr25')
--      rule: the arithmetic in words, e.g. "9.613 × 20.38 + 120.65".
--   3. Public read (anon), like the other output tables; writes only with the service key.
-- Size per run (6 Nov dry run): Angel One 3,017 rows (2,071 series, 817 P/E), Groww 1,072; the job deletes nothing (like sb_pat_lines).
-- Rolling back = drop table public.sb_valuation_lines.

begin;

create table public.sb_valuation_lines (
  run_id      uuid    not null references public.sb_runs (run_id) on delete cascade,
  broker_id   text    not null references public.sb_brokers (broker_id),
  section     text    not null check (section in ('summary', 'inputs', 'common', 'weights', 'series', 'pe', 'pe_bands')),
  period_key  text    not null default '',
  line        text    not null,
  scenario    text    not null default '' check (scenario in ('', 'bear', 'base', 'bull')),
  label       text    not null,
  value       numeric not null,
  unit        text    not null,
  rule        text    null,
  sort_order  integer not null,
  primary key (run_id, section, period_key, line, scenario)
);

create index sb_valuation_lines_broker on public.sb_valuation_lines (broker_id, run_id);

alter table public.sb_valuation_lines enable row level security;

create policy public_read on public.sb_valuation_lines
  for select to anon, authenticated using (true);

commit;
