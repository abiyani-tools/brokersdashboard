# Groww — live spec (draft for AB's sign-off, 31 Oct 2026)

Parity is done: the engine reproduces `SUMMARY - Groww` exactly (262/262 cells) on branch `groww-parity`. Evidence: `docs/Groww_ADR_Methodology.md` (§11 has the corrections) and `out/groww/backsource.md` (each input traced to Groww's filings).

This spec proposes the live switches, the Groww counterpart of Angel One's a–i. As for Angel One:
- each switch is one commit with a parity → live bridge and an independent recompute check;
- only `reviewed` facts move numbers;
- nothing is published until you sign off.

## How Groww differs from Angel One

| Area | Angel One | Groww |
|---|---|---|
| Disclosure cadence | Monthly business update plus quarterly deck | **Quarterly only**: Shareholders' Letter, results, and a KPI Handbook .xlsx on the IR site (not on NSE) |
| Orders | By segment, monthly | Total only, quarterly (Stocks + Derivatives; 51.73 Cr in Q2 FY27); no segment split |
| Revenue by segment | Mix % of total income | Mix % of **consolidated total income** (8 buckets), reclassified in Q2 FY27 |
| Market shares | Orders / turnover shares | ADTO shares; the denominator doubled from Q4 FY26 |
| Market orders | Calibrated from Angel's own orders | **Borrowed from Angel One's calibration** (contracts per order, trades per order) |

## Proposed switches

| # | Switch | Parity (workbook) | Live (proposed) | Evidence |
|---|---|---|---|---|
| g-a | **Facts from filings** | 41 typed inputs, 18 of them wrong or rounded | Load the reviewed facts from `out/groww/facts_candidates.json`: mix on consolidated total income (D9); MTF mix 2% / 3% / 6.9% for Q4 FY25 / Q1 FY26 / Q4 FY26; one classification of the stocks mix | backsource.md; Q1 FY27 letter p7 ("MTF +1.1pp QoQ") |
| g-b | **Full FY26** (D2) | F&O / cash 0 for Q3 FY25–Q1 FY26, `#N/A` for Q2 FY25 | Calibrate Q1 FY26 from its reported total income (9,484.71 Mn) and mix, so FY26 has every quarter; no figures before Q1 FY26 | Q2 FY26 results p5; Q1 FY27 letter p6 |
| g-c | **BSE F&O unfrozen** (D11) | 18.96 Mn carried 29 Sep–21 Oct 2026 | Lake values, the same as Angel switch c (already live) | shared |
| g-d | **Every reported quarter calibrates** (D3, D12) | F&O take rate fixed at Q4 FY26; commodities calibrated once (Q3 FY26), using Angel's take rate | F&O, cash and commodities take rate and share calibrated for each reported quarter, Q1 FY27 and Q2 FY27 included | Q2 FY27 actuals in facts_candidates |
| g-e | **One estimate rule** (D4) | Mix of carry, trailing-3, ×1.05 typed growths and typed MTF shares | Unreported quarters carry the last actual share and take rate; no typed growth. Overrides go in `sb_assumptions` with a note | — |
| g-f | **MTF basis** (D7) | Angel's 14.95% yield, 246 days | 14.95% (Groww's stated fixed pricing, calls only) × the actual trading days of each FY; share = the disclosed MTF revenue ÷ the industry book | transcripts Q2 FY26 p6, Q1 FY27 p13 |
| g-g | **Special sessions and periods** | Partial latest period; stale labels | The same live rules as Angel One: special sessions out of the F&O, cash and commodity averages; labels from the calendar; comparisons follow the selected period | Angel switches d, h |

## Kept as they are (D5, D6), labelled in the UI

- **Market orders from Angel One's calibration.** Groww publishes no segment orders, so there is no independent route. The dashboard says so.
- **ADTO shares applied to orders.** The take rate absorbs the difference. The label reads "share by turnover".

## New check (not in the workbook)

**Implied vs disclosed total orders.** The model's Groww orders (F&O + cash + commodity) can be compared each quarter with Groww's disclosed total orders (KPI Handbook). That gives Groww an out-of-sample test like Angel One's (PLAN 3.2). A persistent gap would show where the borrowed Angel calibration doesn't fit Groww.

## Monthly signal (optional, later)

Groww has no monthly update. Two fetchable monthly series could inform intra-quarter estimates. Neither is needed for the switches above.
- **NSE Report 1C** (broker-wise active clients, about the 7th of each month). It is overwritten in place, so it must be archived monthly.
- **Month-end snapshots of the IR site's quarter-to-date widget** (stocks turnover, derivatives premium turnover, MTF book).

## Decisions for AB

1. Approve the switch list g-a … g-g (or strike any).
2. g-a: review and approve the candidate facts, as you did for Angel One's 178. Nothing is staged in the database yet.
3. g-b: is FY26 starting at Q1 FY26 (1 Apr 2025) right, or should FY26 comparisons start from Q2 FY26?
4. g-f: keep 14.95% for MTF, or use a filed number if you have one?
5. Dashboard: a broker selector in the Brokers view (agreed). Show the implied-vs-disclosed orders check there too?
