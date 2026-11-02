# Scope: ADR from April 2023 (all three brokers)

Requested by AB on 2 Nov 2026. AB's words: "If we want the ADRs to run even before lets say - from April 2023, can you do
it based on the logic you have and disclosure filings data you already have?" **Proposal only; nothing is approved.**

## Where each series starts today (latest live runs, as of 30 Oct 2026)

| Broker | F&O / cash | Commodities | MTF | What limits the start |
|---|---|---|---|---|
| Angel One | 2024-10-01 | 2024-04-01 | 2024-10-01 | the engine's calibration window starts at the workbook's first F&O day (reviewed facts go back to Q1 FY25 / Apr 2024); MTF needs the industry book |
| Groww | 2025-04-01 (non-zero from that day) | 2025-10-01 | 2024-10-01 | Groww's own quarterly revenue facts start Q3 FY25; F&O / cash also need Angel One's orders calibration for the same months |
| MOSL | 2024-04-01 | 2024-04-01 | 2024-10-01 | data-book facts loaded from Q1 FY25; MTF needs the industry book |

## What already exists for Apr 2023 – Mar 2024

| Input | Status | Source |
|---|---|---|
| NSE / BSE daily volumes | **available, not loaded**: ExchangesDash's JSON has 2023-04-03 onwards; our refresh starts at 2023-09-29 (`START` in `src/live/refresh_market.py`) | the same public JSON the daily job reads |
| MCX daily contracts | available from 2022-01-03 (same JSON) | same |
| `sb_calendar` | starts 2023-09-29; Apr–Sep 2023 days must be added | from the exchanges' trading days in the same JSON |
| Industry MTF book | **missing** before 2024-10-01 (the owner's view starts there, and it currently answers 401) | NSE publishes the daily MTF disclosure for earlier years: the owner could backfill their view |
| MOSL facts FY24 | **in files we already hold**: each data book has quarterly columns Q1 FY23 … (e.g. the Q1 FY25 book has Q1 FY23 – Q1 FY25) | `data/raw/disclosures/mosl/*data-book.xlsx`, same metrics and cells as the 290 reviewed facts |
| Angel One facts FY24 | **not extracted**: 12 monthly business updates (Apr 2023 – Mar 2024) and 4 quarterly decks | NSE announcements feed (the filing-extractor reads these) |
| Groww facts FY24 | quarterly turnover and premium for Q1 FY23 onwards are on the IR page (already archived in `sb_broker_daily`); **revenue is annual only** (prospectus FY24); IR MTF book starts Q1 FY25 | IR archive; RHP |

## Options

**A. Sourced backfill, in three steps** (recommended):
1. **Market data and calendar to 2023-04-03.** Move `START` back, add the Apr–Sep 2023 calendar days, rerun E5 on them. No engine logic changes. *Small.*
2. **MOSL FY24.** Stage about 100 facts (Q1–Q4 FY24, the same metrics as the reviewed 290) from the data books we hold, AB reviews them, then extend MOSL's calibration window to Q1 FY24 with a bridge and an independent check (as for m-a). *Medium.*
3. **Angel One FY24, then Groww.** The filing-extractor reads 16 Angel PDFs (about 150–200 facts for AB to review), and the engine's calibration window becomes a parameter instead of the workbook's first day. Angel One then runs from Apr 2023 (Apr 2024 for F&O / cash needs only the engine change, since the facts exist). Groww follows Angel's months, but its FY24 quarters have no quarterly revenue: the FY24 annual revenue would be split across quarters by its IR turnover. That is an estimate rule and needs AB's sign-off. *Medium to large.*

**MTF in every option.** Before Oct 2024 there's no industry book. Either ask the owner to backfill `codex_public_nse_mtf_daily` to Apr 2023 (needs the 401 fixed first), or publish Consolidated without MTF for those months, labelled. A per-broker alternative (Angel One's own monthly funding book, MOSL's quarterly closing book) changes the MTF method, so it's a separate decision.

**B. Backcast** (quick, all estimate). Apply each broker's first calibrated quarter (rates, shares, take rates) to the FY24 volumes and tag every day 'estimate'. This is quick once step A1 is done, but none of it ties to a filing, and the FY24 YoY comparisons for FY25 would compare against a model, not reported figures. Not recommended, except as a labelled stopgap for Groww's FY24.

## Database changes (the ExchangesDash owner mirrors `sb_*`: tell them first)

There are no schema changes. New rows only:
- `sb_market_daily` and `sb_calendar` for Apr–Sep 2023;
- `sb_disclosure_facts` for the FY24 quarters;
- `sb_assumptions` for any estimate rule (Groww's FY24 split, or option B);
- new runs.

Every published figure keeps its regime tag ('actual' where a quarter ties to a filing, else 'projected' / estimate).

## Recommended order

A1, then A2 and the Angel One F&O / cash extension to Apr 2024 (no new facts needed). Then A3. Ask the owner about the MTF backfill alongside. Each step is a switch with a bridge, an independent check and AB's approval, as for m-a … m-f.
