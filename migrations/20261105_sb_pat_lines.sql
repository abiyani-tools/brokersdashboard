-- PLAN 5.7: sb_pat_lines holds the PAT model's output (src/engine/pat.py), one row per run, period, line and scenario.
-- NOT YET APPLIED. Needs AB's OK (CLAUDE.md rule 7) and a notice to the ExchangesDash owner, whose mirror copies every
-- sb_* table (brokers_mirror_schema.sql there needs the same table).
--
-- What it does, step by step:
--   1. Creates sb_pat_lines. run_id is the broker's ADR run (sb_runs) whose daily ADR the model used, so each PAT
--      figure traces to one published ADR run. No new run rows: the PAT step writes after that run succeeds.
--   2. period_key: 'Q1 FY 2027' … 'Q4 FY 2027', 'FY 2027', 'FY 2028'. line: the model's line keys (broking, mtf,
--      finance, fees_commission, …, pat, eps, target_today, upside). scenario: '' for P&L lines, 'bear' | 'base' |
--      'bull' for valuation lines (they differ only in P/E). regime: 'actual' (filed quarter) or 'projected'.
--      rule: the rule in words, with its inputs (e.g. "previous 147.5 + 9.0%/4 × new borrowing 140 …").
--   3. Public read (anon), like the other output tables; writes only with the service key.
-- Rolling back = drop table public.sb_pat_lines.

begin;

create table public.sb_pat_lines (
  run_id      uuid    not null references public.sb_runs (run_id) on delete cascade,
  broker_id   text    not null references public.sb_brokers (broker_id),
  period_key  text    not null,
  line        text    not null,
  scenario    text    not null default '' check (scenario in ('', 'bear', 'base', 'bull')),
  label       text    not null,
  value       numeric not null,
  unit        text    not null,
  regime      text    not null check (regime in ('actual', 'projected')),
  rule        text    null,
  sort_order  integer not null,
  primary key (run_id, period_key, line, scenario)
);

create index sb_pat_lines_broker on public.sb_pat_lines (broker_id, run_id);

alter table public.sb_pat_lines enable row level security;

create policy public_read on public.sb_pat_lines
  for select to anon, authenticated using (true);

commit;
