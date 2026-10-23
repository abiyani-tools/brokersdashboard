-- E3 (LIVE_SPEC §3): sb_summary_cells holds the Summary for every FY / quarter / month.
-- APPLIED 23 Oct 2026 on everjfpbnlbcpuarnhob (apply_migration 'sb_summary_cells_period'), with AB's OK.
-- Verified: 210 rows (FY 12, Q 24, M 24, asof 150), no NULL periods, values unchanged (sum 1485.349792).
--
-- What it does, step by step:
--   1. Adds period_type ('FY' | 'Q' | 'M' | 'asof'), period_key (the selected period, or the as-of date for the
--      Week / Weekday tables) and note (why a value is NULL: "insufficient data: …").
--   2. Fills the two new columns for the 210 rows already stored (parity run 42e5519f…, as of 2026-10-21).
--      The Cash panel was built for Q4 FY 2026 / FY 2026 February (the workbook's stale labels); every other
--      panel for FY 2027 / Q2 FY 2027 / FY 2027 September.
--   3. Makes the two columns NOT NULL and widens the primary key with them. Today's key
--      (run_id, panel, table_name, row_label) would collide as soon as two periods share a row label such as
--      "Avg of last 6 months".
--   4. Adds an index for the dashboard's lookup (run, period).
-- Nothing is deleted. Values are not changed. Rolling back = drop the new key, restore the old one, drop the columns.

begin;

alter table public.sb_summary_cells
  add column if not exists period_type text,
  add column if not exists period_key  text,
  add column if not exists note        text;

update public.sb_summary_cells
   set period_type = case table_name
                       when 'Financial Year' then 'FY'
                       when 'Quarter'        then 'Q'
                       when 'Month'          then 'M'
                       else 'asof' end,
       period_key  = case table_name
                       when 'Financial Year' then 'FY 2027'
                       when 'Quarter'        then case when panel = 'Cash' then 'Q4 FY 2026' else 'Q2 FY 2027' end
                       when 'Month'          then case when panel = 'Cash' then 'FY 2026 February' else 'FY 2027 September' end
                       else '2026-10-21' end
 where run_id = '42e5519f-0e19-4834-9a4c-2ce8ccec574a';

-- fails (and rolls back) if any other run left rows without a period
alter table public.sb_summary_cells
  alter column period_type set not null,
  alter column period_key  set not null,
  add constraint sb_summary_cells_period_type_chk check (period_type in ('FY', 'Q', 'M', 'asof'));

alter table public.sb_summary_cells drop constraint sb_summary_cells_pkey;
alter table public.sb_summary_cells
  add constraint sb_summary_cells_pkey primary key (run_id, panel, period_type, period_key, table_name, row_label);

create index if not exists sb_summary_cells_run_period_idx
  on public.sb_summary_cells (run_id, period_type, period_key);

commit;

-- Check after applying (expect 210 rows: FY 12, Q 24, M 24, asof 150):
--   select period_type, count(*) from sb_summary_cells group by 1 order by 1;
