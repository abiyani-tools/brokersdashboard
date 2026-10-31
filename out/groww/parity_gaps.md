# Groww parity: gaps

Status (branch `groww-parity`): **no gaps**. `python3 run_parity.py --broker GROWW` reproduces

- all 262 numeric `SUMMARY - Groww` cells within 1e-9, and the 2 cells that show "-" (`O39`, `E65`: division by 0);
- the daily rows of the four feeder columns (`backtesting F&O!AD` 573 days, `backtesting cash!V` 573, `Commodities!K` 272, `MTF data (2)!L` 507), max abs diff 1.1e-13 (Rs Mn) / 0 (MTF);
- the 48 cached quarterly parameters (take rates, shares, orders per contract / trade, commodity calibration S3:S9, MTF shares J51:J60).

Not covered by the parity test (by design, not failures):

1. Exchange volumes (NSE / BSE F&O, NSE / BSE trades, MCX contracts) and the industry MTF book are read from the Angel snapshot, as the workbook shares those cells; the arrival of those values from the external link `[11]` is not re-derived.
2. The 15 stray typed cells `K144:M163` belong to no panel and are excluded (as in `summary_expected.json`).
3. Downstream sheets (`Groww charts`, `Groww - Final `, `Groww - ADR Model`) are not part of the target.
4. Groww's quarterly facts (revenue mix, income, ADTO shares, MTF revenue) are workbook values with `[SOURCE NEEDED]`; none is traced to a filing yet.
