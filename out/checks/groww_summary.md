# Groww live switches g-a ... g-g: independent recompute summary

Checker: recompute-checker, branch `groww-parity`, HEAD `0dc69a0`. No file under `src/engine/` or `src/live/` was read. Per-switch working: `out/checks/groww_switch_<x>.md`, scripts `out/checks/groww_switch_<x>_check.py`; orders check: `out/checks/groww_orders_check.md` and `groww_orders_check.py`. Each script (Python stdlib: json, math, csv; os for paths) rebuilds the model from the snapshots, parses the matching bridge in `out/bridges/` and writes its own md and an items csv.

**Total: 443/443 items agree.** No disagreement with any bridge.

| Switch | Agree / checked | Agree at 1e-6 relative | By item kind |
|---|---:|---:|---|
| g-a Facts from filings | 112/112 | 69 | ADR 30/30, param 46/46, input 24/24, daily 4/4, tie 8/8 |
| g-b Full FY26 | 47/47 | 46 | ADR 30/30, param 6/6, input 5/5, daily 4/4, tie 2/2 |
| g-c BSE F&O unfrozen | 50/50 | 50 | ADR 30/30, daily 4/4, lake 16/16 |
| g-d Every reported quarter calibrates | 80/80 | 66 | ADR 30/30, param 26/26, input 10/10, daily 4/4, tie 7/7, input-x 3/3 |
| g-e One estimate rule | 39/39 | 35 | ADR 30/30, param 5/5, daily 4/4 |
| g-f MTF basis | 66/66 | 49 | ADR 30/30, param 18/18, input 2/2, daily 4/4, tie 8/8, days 4/4 |
| g-g Special sessions and periods | 36/36 | 36 | ADR 30/30, daily 4/4, special 2/2 |
| Orders check (Q1 FY26 to Q2 FY27) | 13/13 | 5 | orders 8/8, q2fy27 5/5 |

How "agree" is judged: within 1e-6 relative, or within half of the last digit the bridge prints (several bridge parameters are printed to 4 decimals, e.g. MTF shares 0.0061, so 1e-6 cannot be tested on them; their printed delta % column, which carries 5 or more significant digits, is checked as well). All 210 ADR cells of the seven bridges (5 periods x 6 panels x 7 switches, before and after columns) agree within 6e-7 relative, which is the print rounding of six decimals.

## How the recompute was built

1. Parity rebuilt from raw inputs: NSE+BSE F&O contracts, NSE+BSE trades, MCX contracts and the industry MTF book (db snapshot); Angel's monthly F&O contracts-per-order, quarterly trades-per-order, monthly commodity contracts-per-order and commodity take rates (read from `parity_expected` in the db snapshot); the workbook's Groww inputs (`groww_snapshot`); formulas per Methodology sections 3, 4 and 8b. It reproduces the 573 / 573 / 272 / 507 daily Groww rows of the fixtures to 1e-15 relative and the g-a "Before" column (the workbook summary).
2. Each switch applied cumulatively as the spec and bridge describe: a (reviewed facts), b (Q1 FY26 calibrated), c (lake BSE F&O), d (each reported quarter calibrates), e (carry rule), f (14.95% x FY days, share from disclosed revenue), g (special sessions out of the F&O, cash and commodity averages).
3. Compared with every ADR table, parameter table, inputs-replaced table and daily-rows-changed table, plus switch-specific extras (the 15 lake values, FY day counts, the eight special sessions, tie-outs of daily sums to reported revenue, the commodity market-order denominator against Angel's monthly orders).

First-pass mismatches during the build were all slips in my own recompute (rounded monthly Angel commodity take rate used instead of the quarterly one, a fact-id rule that ignored seed-sourced total income, and the parity commodity tie ignoring the typed 5% growth); none was in a bridge.

## Inputs taken as given (not independently re-derived)

- Angel's calibration values (contracts-per-order by month, trades-per-order by quarter, commodity CPO and take rates) as stored in the db snapshot `parity_expected`. The Angel estimates for Jun-Oct 2026 (carried May F&O CPO 14.35172; Jul-Sep commodity CPO 12.70 to 13.02) are Angel's, not Groww's.
- The industry daily MTF book and exchange daily volumes (db snapshot).
- Reviewed facts read visually from letter charts (restated mixes, new-basis ADTO shares): values and page refs taken from the facts file. Total income (Q2 FY27 1,540.54 Cr, Q1 FY27 1,548.67 Cr) and the orders and trading-day rows were confirmed against `2026_10_Q2_FY27_KPI_Handbook.xlsx`.
- g-g clauses on labels from the calendar, comparisons following the selected period and the "insufficient period" flag: the bridge shows no number for them, so only the special-session ADR effect was checked.

## Orders check (Q2 FY27)

Disclosed total 517.305 Mn (handbook 51.7305 Cr x 10, fact 10095; confirmed in the xlsx). My model: F&O 258.9, cash 134.8, commodity 44.4, total 438.1 Mn, gap -15.3%. All eight quarters of the bridge table agree. Excluding commodity the Q2 FY27 gap is -23.9%: the handbook glossary defines Broking Orders as orders in Stocks and Derivatives and lists Equity and Commodity Derivatives as separate product lines, so whether the disclosed total contains commodity orders is not settled. With the new-basis (halved) shares the gap is -53.4%, so the legacy basis is the closer one.

## Where a switch did something different from the spec (details in each switch md)

- g-a: the spec says one classification of the stocks mix; the switch uses restated mixes where they exist and original ones for Q1 FY26 (and MTF Q3 FY25 to Q1 FY26), so FY26 holds two vintages (sensitivity: FY26 cash ADR -1.8% if Q1 FY26 cash were restated like its neighbours). It also replaces MTF revenue for Q3 FY25, Q2 FY26, Q3 FY26 and Q1 FY27, beyond the three quarters the spec names.
- g-d: the commodity take rate stays Angel's quarterly rate (Q2 FY27 is Angel's carried estimate) and the share absorbs the calibration, whereas the spec and D12 speak of a Groww take rate. The F&O take rate uses the monthly-mean CPO, not the workbook's unused quarterly 14.743.
- g-f: FY 2027 uses FY 2026's 247 days (FY incomplete), not "actual trading days of each FY"; the share is a calibration that ties each quarter's revenue and sits on the daily industry book average (this accounts for +12% in the Q3 FY25 share). Q1 FY27 has 59 industry-book days against 60 trading days.
- g-g: take rates are still calibrated with special-session days in the sums, so excluding those days from the averages leaves, for example, Q4 FY26 F&O about 1.2% of quarter revenue off a tie (2026-02-01).
- g-e: as specified; the "overrides in sb_assumptions" clause is not exercised and cannot be checked from the bridge.
