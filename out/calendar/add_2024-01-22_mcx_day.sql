-- sb_calendar: add 2024-01-22 as an MCX-only trading day. NOT APPLIED (blocked by the permission check on 3 Nov 2026;
-- needs AB's explicit OK).
-- MCX traded (1,552,107 contracts in ExchangesDash's mcx JSON); NSE and BSE were closed for the Ram Mandir
-- consecration holiday. It is the only day with MCX contracts and no sb_calendar row (checked 3 Nov 2026).
-- Revenue already counts the day (MOSL commodities Q4 FY24 ties to its reported net brokerage with it); the row only
-- makes the calendar complete for the guards and E5.

insert into sb_calendar (trade_date, fy, q_fy, fy_month, weekday, is_equity_day, is_mcx_day, special_session, note)
select '2024-01-22', 'FY 2024', 'Q4 FY 2024', 'FY 2024 January', 'Monday', false, true, null,
       'MCX traded, NSE / BSE closed (Ram Mandir consecration holiday); added with AB''s OK (MCX contracts 1,552,107 in ExchangesDash''s JSON)'
where not exists (select 1 from sb_calendar where trade_date = '2024-01-22')
returning trade_date, is_equity_day, is_mcx_day;
