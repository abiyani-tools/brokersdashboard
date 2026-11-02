-- sb_calendar: mark MCX open on the 121 days it traded between 29 Sep 2023 and 28 Mar 2024.
-- APPLIED 2 Nov 2026 with AB's OK ("Yes, apply it"): 121 rows, 2023-09-29 .. 2024-03-28. The ExchangesDash owner mirrors sb_*.
--
-- Why: the calendar seeded from the workbook marks is_mcx_day = false on every day from 2023-09-29 to 2024-03-28,
-- although MCX traded (ExchangesDash's mcx_dashboard_data has contracts > 0 on each; E5 has been reporting it as
-- "value on a day sb_calendar marks closed"). Commodity revenue starts 2024-04-01, so no figure uses those days today.
-- But step A1 (market data from 1 June 2023) adds earlier days with the right flag, and the guard for the Commodities
-- "Avg of last 6 months" would then see a calendar that starts in June 2023 and average April 2024 alone for
-- FY 2025 April - August (5 cells per broker). With the flags right, those cells stay "insufficient data".
-- Simulated (committed snapshots, June 2023 start + this fix): every published value of Angel One and MOSL identical;
-- only "insufficient data" note wording changes; MCX 2024-01-01 (morning session only) becomes a known E5 event
-- (src/live/integrity.py KNOWN_ISSUES, deployed in 7c6a269).
--
-- Touches is_mcx_day only, and only on days with MCX contracts > 0 in the data (not from a list). The 4 days that stay
-- false have no MCX contracts: 2023-11-12 (muhurat), 2024-01-20 (Saturday session), 2024-03-02 and 2024-05-18 (DR tests).
-- Rollback: the same days back to false (the list is the RETURNING output, saved in the run notes).

update sb_calendar c set is_mcx_day = true
where not c.is_mcx_day
  and c.trade_date in (select distinct trade_date from sb_market_daily
                       where dataset = 'mcx' and metric = 'contracts' and source = 'exchangesdash_json' and value > 0)
returning c.trade_date;
-- expect 121 rows, 2023-09-29 .. 2024-03-28
