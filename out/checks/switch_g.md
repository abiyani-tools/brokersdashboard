# Switch (g) independent check
Inputs: snapshot/db_snapshot_2026-10-23.json only (parity_expected mtf_gross_cr / mtf_net_cr daily, calendar, assumptions.mtf_net_factor=0.45). Script: out/checks/switch_g_check.py (python3 -I).
Formulas: period ADR = mean of daily MTF (Rs cr) over calendar-matched MTF dates (FY2026 sets drop 2025-10-21, switch d). Weekday latest/avg3/avg10 = last 1/3/10 MTF dates with that weekday (latest MTF date 2026-10-19, a Monday). Net = 0.45 x gross.
Tolerance: rel <= 1e-6 or abs <= 5.5e-7 (6dp rounding).
Result: 29 checks, 29 agree, 0 disagree.
- net == 0.45 x gross on all 507 dates (max rel err 0).
- 6 periods: gross, net, and 0.45 x claimed gross all match (e.g. FY 2027 4.209385080 / 1.894223286; FY 2026 ex-2025-10-21 3.116117010 / 1.402252655).
- Monday latest/avg3/avg10 and Tuesday latest, both bases, match.
- Consolidated delta: Monday 2.593309 and Thursday 2.595848 equal MTF gross-net delta on 2026-10-19 / 2026-10-15.
- 2025-10-21 is in no weekday window, so d does not affect those.
Not checked: other segments' unchanged values, and the week tables (not recomputed here).
