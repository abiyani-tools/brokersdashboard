# Note for the ExchangesDash owner: new table `sb_valuation_lines` and a Valuation tab

*From Tusk (Abhishek Biyani) · sent 9 Nov 2026 as a comment on sucaanalytics-max/ExchangesDash#75 (the Valuation tab PR), after the migration was applied*

Hi Jay,

This is about a new Brokers tab, **Valuation** (Angel One and Groww), and the table behind it.

1. **The table now exists on our side.** `public.sb_valuation_lines` was created in the brokers-dashboard project
   (`everjfpbnlbcpuarnhob`) by `migrations/20261109_sb_valuation_lines.sql`. Anon has read access, so your publishable key
   can read it. Per your `docs/BROKERS_INTEGRATION.md` rule, the mirror copy can be created now. Here it is, without the
   foreign keys and CHECK constraints, as in your other definitions:

   ```sql
   create table if not exists public.sb_valuation_lines (
     run_id uuid not null,
     broker_id text not null,
     section text not null,
     period_key text not null default '',
     line text not null,
     scenario text not null default '',
     label text not null,
     value numeric not null,
     unit text not null,
     rule text,
     sort_order integer not null,
     primary key (run_id, section, period_key, line, scenario)
   );
   alter table public.sb_valuation_lines enable row level security;
   comment on table public.sb_valuation_lines is 'Copy of brokers-dashboard sb_valuation_lines (scripts/brokers_mirror.py); not edited by hand.';
   ```

2. **Size.** Each weekday's daily job writes the table right after `sb_pat_lines`: about 3,000 rows per run for Angel One
   and 1,100 for Groww (6 Nov dry run). Most of them are the daily series behind the charts; Angel One also has about
   800 P/E rows. It grows with the series, about 5 rows per broker per trading day.
3. **The PR** adds:
   - `dashboard/js/34-brokers-valuation.js`
   - `view=valuation` in `dashboard/api/brokers.js` (built like `view=pat`)
   - one tab entry in `js/30-brokers.js`
   - the script tag in `index.html`
   - three API tests

   No other `sb_*` table changes. Until our first run publishes, the tab says "No valuation published … yet".

Thanks,
Abhishek
