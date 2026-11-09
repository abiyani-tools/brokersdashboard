# Note for the ExchangesDash owner: `sb_pat_lines` now exists on the brokers side

*From Tusk (Abhishek Biyani) · draft 9 Nov 2026, not sent*

Hi Jay,

This is about the PAT Predictor tab merged in #57 / #58 and the mirror definition of `sb_pat_lines` in `brokers_mirror_schema.sql`.

1. **The table exists on our side.** `public.sb_pat_lines` was created on 6 Nov 2026 in the brokers-dashboard project
   (`everjfpbnlbcpuarnhob`) by `migrations/20261105_sb_pat_lines.sql`. Its columns, types and primary key
   (`run_id, period_key, line, scenario`) match your mirror definition exactly. Anon has read access, so your publishable key can read it.
   Your `docs/BROKERS_INTEGRATION.md` says to create the copy only once the table exists here. It does now, so
   `create table if not exists public.sb_pat_lines …` can be run in your project before the next mirror run.
2. **It is empty for now.** Rows arrive once our PAT step is merged (brokersdashboard PR #6) and the staged filing
   facts are reviewed. After that, each weekday's daily job writes about 155 rows per broker (Angel One, Groww) right after
   that day's ADR run. Until then, `/api/brokers?view=pat` correctly returns "No PAT lines published for the latest live runs yet".
3. **No other change.** No columns change on the other `sb_*` tables, and the dashboard needs no code change.

Thanks,
Abhishek
