# Motilal Oswal (MOSL) — live spec (draft for AB's sign-off, 2 Nov 2026)

Parity is done. On branch `mosl-parity`, the engine reproduces `SUMMARY - Motilal Oswal` exactly: 264/264 cells, and the four daily net-revenue columns with max difference 0. Angel One and Groww are unchanged.

Evidence:
- `docs/MOSL_ADR_Methodology.md`: how the workbook models MOSL; issues in §7.
- `out/mosl/backsource.md`: each input traced to MOSL's quarterly data book.
- `out/mosl/facts_candidates.json`: 290 facts, Q1 FY25 – Q2 FY27, latest data-book vintage.

As for Angel One and Groww:
- each switch is one commit with a parity → live bridge and an independent recompute check;
- only `reviewed` facts move numbers;
- nothing is published until AB signs off.

## How MOSL differs

| | Angel One | Groww | MOSL |
|---|---|---|---|
| Source of truth | monthly business update + quarterly deck | quarterly KPI Handbook + letter | **quarterly data book (xlsx, IR site, results day)** |
| Revenue | orders × take rate | orders (Angel's calibration) × take rate | **disclosed gross brokerage per segment, spread by an exchange-volume key, × net/gross** |
| Borrows from Angel | — | contracts and trades per order | **nothing** |
| F&O key | contracts | contracts | NSE index-option + BSE contracts |
| Cash key | trades | trades | NSE + BSE cash turnover |
| MTF | share × industry book × yield | Groww's own book × 14.95% (g-i) | MOSL book share × industry daily book × NII yield |
| Summary basis | gross MTF | gross MTF | **net brokerage** + MTF |

Because revenue is disclosed every quarter, each reported quarter ties to the data book by construction. The model's job is the day-by-day shape and the unreported (current) quarter.

## Proposed switches

| # | Switch | Parity (workbook) | Live (proposed) | Evidence |
|---|---|---|---|---|
| m-a | **Reported quarters from the data book** | Q2 FY27 is an estimate (cash gross −15.8%, commodity gross +49%, MTF book −9.1% vs actual); Q1 FY27 cash gross not fed (`J52 = J51`) | Every reported quarter (Q1 FY25 – Q2 FY27) is calibrated from reviewed data-book facts (gross per segment, net/gross, MTF book) | backsource.md; Q2 FY27 book of 29 Oct |
| m-b | **Cash key on the right dates** | The NSE / BSE cash turnover key is read two rows off from 9 Jun 2025 (day values move by a median 8%) | The lake's daily cash turnover on its own date | Methodology §7 |
| m-c | **No silent zeros** | The FY27 year to date drops cash and commodities through IFERROR over #N/A (Broking shown 1.805 vs 4.294) | Missing days are excluded and flagged ("insufficient data"), never averaged as 0 | Methodology §7 #1 |
| m-d | **Periods and comparisons from the calendar** | "YoY" compares Q2 FY27 with Q4 FY26; stale labels; band 3 swapped | The same rules as Angel One and Groww (switches g/h, g-g): YoY = the same period last year, labels from the calendar, standard panel order; special sessions out of the F&O / cash / commodity averages | Methodology §7 #3 |
| m-e | **One estimate rule for the open quarter** | Typed / carried, and the Q3 FY27 cash key is latent ×5 | The open quarter (Q3 FY27) carries the last reported quarter's net revenue per unit of key (per contract, per Rs Cr of turnover) and its net/gross. The MTF share is carried from the last reported quarter-end | — |
| m-f | **MTF yield** (decision below) | 9 typed NII yields, no source (Q2 FY27 carried 12.94%) | See decision 3 | backsource.md (NII yield) |

**No BSE-freeze switch is needed.** MOSL's F&O key already reads the live BSE column, not the frozen one.

## Decisions for AB

1. **Approve switches m-a … m-f** (or strike any).
2. **What "MOSL broking" means.** The model uses the data book's consolidated net brokerage (Q2 FY27: 277.4 Cr). That is about retail and PWM; MOSL calls its market share "retail broking". It excludes the Capital Markets segment (institutional broking, 103.4 Cr). Keep it at retail + PWM? (Recommended: yes, as the workbook does, labelled on the dashboard.)
3. **MTF yield.** MOSL publishes no MTF yield or interest line. Options:
   - **(a)** keep the workbook's typed yields, carrying 12.94%;
   - **(b)** use the proxy "WM net interest income × 4 ÷ average lending book" (Q2 FY27: 12.04%). It's within 0.7 pp of the typed yields for Q1 FY26 – Q1 FY27, but 1.3–2.6 pp above them for FY25, and the Q2 FY27 data book restated the lending book by up to 16%;
   - **(c)** ask MOSL IR.

   Recommended: (a) for now, labelled as an assumption, and (c) in parallel.
4. **Facts.** Approve the 290 candidate facts. Nothing is staged in the DB yet. On approval they're staged with their data-book cell references, then marked reviewed, as for Groww.
5. **Dashboard.** MOSL becomes the third option in the Brokers selector, with its own panel set (net brokerage; no MTF (net) panel). ADR only; no PAT tab for now.

## Dependencies

- **NSE index-option contracts** become an engine input for MOSL. In the current ExchangesDash data they are zero on 12–15 Oct and end on 15 Oct. The owner's PR [sucaanalytics-max/ExchangesDash#33](https://github.com/sucaanalytics-max/ExchangesDash/pull/33) takes them from NSE directly. Until it merges, MOSL's live F&O stops at 11 Oct, and E5 will flag the zero days.
- **MCX contracts and NSE cash turnover:** the same limits as the other brokers (as of 21 Oct until PR #33).
- **Each quarter's update:** the data book is published on results day, and the filing watcher (PLAN 4.2) can be extended to fetch it from MOSL's IR JSON (`motilaloswal.com/spreadsheets/investor-relations.json`, column "Data Book"; URL pattern `q{n}fy{yy}-data-book.xlsx`, folder changes, so read the JSON). It stages the facts for AB's review, which keeps the base assumptions current with each quarterly presentation.
