# broker_db — Angel One ADR engine (parity mode)

Rebuilds the Angel One ADR calculation in `20260714_brokers dashboard v2.xlsx` from the `brokers-dashboard` Supabase project (ref `everjfpbnlbcpuarnhob`). The first goal is **exact parity** with the workbook. The methodology is in `Angel_One_ADR_Methodology.md`.

## Status — 23 Oct 2026

**Parity: 8,774 of 8,797 workbook values reproduced exactly** (tolerance: one part in a billion). **0 are unexplained.** The 23 out-of-scope values are listed below.

| Output | Matched |
|---|---|
| `SUMMARY - Angel One` cells (all 6 panels × FY / Quarter / Month / Week / Weekday) | 264 / 264 |
| Daily F&O, cash, commodity revenue and orders; daily MTF gross/net | 8,066 / 8,066 |
| Calibration: revenue per order, F&O contracts/order, cash trades/order, commodity contracts/order, shares, MTF share | 444 / 467 |

**Out of scope (23).** These cells don't feed the ADR and can't be rebuilt from stored inputs:
- `Commodities!AB26:AB44` (19): a monthly commodity revenue-per-order column the workbook calculates but never uses, since daily revenue uses the fixed `AI11`. `AB26:AB34` are typed-in rounded values.
- `MTF data!D59:D60`, `P59:P60` (4): Q3–Q4 FY27 MTF book estimates that rely on a 38% FY27 growth assumption (`MTF data!B61`) not stored in the DB.

**Run stored in the DB:** run `42e5519f-0e19-4834-9a4c-2ce8ccec574a` (mode `parity`, as of 2026-10-21). It holds 357 calibration rows, 2,692 daily revenue rows and 210 summary rows, all readable with the publishable key.

## Layout

```
src/engine/inputs.py     load a DB snapshot; FY / quarter / month labels
src/engine/calibrate.py  take rates; F&O, cash, commodity and MTF calibration + the workbook's projection rules
src/engine/daily.py      daily revenue per segment
src/engine/summary.py    the Summary grid (cell for cell, incl. the workbook's quirks)
src/engine/summary_periods.py  E3: the Summary for every FY / quarter / month (live, guarded)
src/live/                live-mode inputs: periods (E1), loader (E2), guards (E4), integrity (E5), db readers (E6)
src/live/run.py          live dry run: E5 → engine (switches a–i) → E1 coverage → E3 rows (`python3 run_live.py`)
src/engine/switches.py   the parity → live switches a–i; src/engine/bridge.py the ADR bridge per switch
migrations/              SQL migrations for the sb_* tables
src/engine/parity.py     compare with sb_parity_expected; documented out-of-scope list
src/engine/publish.py    rows for sb_runs / sb_calibration / sb_daily_revenue / sb_summary_cells
seed/build_fixtures.py   builds the parity fixtures + data-lake rows (already loaded)
tests/test_parity.py     the parity gate (pytest)
snapshot/                JSON export of the DB inputs used for this run
run_parity.py            prints the parity report
```

Run it with `python3 run_parity.py`, or `python3 -m pytest tests/ -q`.

## Workbook quirks reproduced on purpose (parity mode only)

- The commodity take rate is fixed at Q3 FY26 for every date.
- Weekday tables use net MTF revenue; all other tables use gross.
- The cash panel's stale labels: Q4 FY26 / Q3 FY26 / Q4 FY25, Feb / Jan FY26.
- The "6-month" figure is the average of two quarterly ADRs.
- BSE F&O contracts are frozen 29 Sep–21 Oct 2026 in the daily column, while the monthly contracts/order uses the real exchange totals.
- F&O inputs are cut off at Q4 FY26 / May-26, while cash uses Q1 FY27.
- The MTF Angel book uses the workbook's own values.

Live mode removes these, one documented switch at a time.

## Next

1. Live mode: use every reviewed disclosure, data-lake exchange data (BSE contracts unfrozen), and one projection rule per parameter.
2. Disclosure pipeline: Angel monthly update and quarterly results → `sb_disclosure_facts`, with review.
3. Daily refresh job (GitHub Actions, with the service key as a secret) + the "Brokers" toggle in ExchangesDash.
