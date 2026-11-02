# MOSL back-sourcing: workbook inputs vs the quarterly data books

Prepared 2026-11-02. Research only: no DB writes, no commits, nothing outside `out/mosl/backsource.md` and `out/mosl/facts_candidates.json`. Companion: `out/mosl/facts_candidates.json` (290 staged facts, all from the latest vintage).

Method. All 10 data books (`data/raw/disclosures/mosl/MOSL_DataBook_*.xlsx`, sha256 checked against `filings_inventory.json`) were read with openpyxl (`data_only=True`, labels matched, not row numbers). **Latest vintage for every quarter Q1 FY25 to Q2 FY27 = the Q2 FY27 book** (29 Oct 2026, `MOSL_DataBook_q2fy27-data-book.xlsx`). Cells below are in that book, sheet `Consol` unless stated. Workbook cells are in `/Users/abhishekbiyani/Documents/brokersdashboard/out/mosl/workbook_inputs.json`. Rs Cr unless stated. Page numbers are PDF pages (pdftotext).

## 1. Result in one view

Scope: the 106 `scope: mosl` inputs the Summary reads (`read_by_summary`) plus the 507 shared industry-book rows (`MTF data (2)!I12:I518`).

| Status | Count | Meaning |
|---|---|---|
| match | **73** | Identical to the Q2 FY27 book cell (57 on `Motilal Oswal assumptions`, 16 on `Working Sheet - MOSL`) |
| rounded | **16** | Typed value is the Q2 FY27 book cell rounded to whole Rs Cr / 3 decimals. Error 0.00% to 0.51% (largest: `K60` commodity gross 55 vs 54.72) |
| restated | **0** | No typed value is stale. But 27 of the 89 traced inputs have a *different first-reported value*; all 27 already hold the post-restatement figure (Q2 FY26 book or later) |
| differs | **0** | |
| no source | **9** (+507) | The nine NII yields `F6:F14`; plus the 507 daily industry MTF book values (not a MOSL disclosure) |
| n/a | 8 | `SUMMARY - Motilal Oswal!L7:L17`, `B36` period labels (typed text, not data). `L13` = `Q4 FY 2026` is the "YoY" label problem (Methodology issue 3) |

Not read by the Summary but typed (extra): `I52` cash gross 228 vs 228.3005 (rounded, not fed: `J52 = J51`), `K63` commodity ADTO 34,937 vs 34,937.03 (rounded). The 165 live-link cells (`C84:Q94`, `C103:Q103`) hold Q1 FY27-book values; against the Q2 FY27 book none of the 207 compared cells moved except F&O ADTO Q1 FY27 (see 2.3), so the links are current.

### 1.1 Restatement facts (which book changed what)
- **Q2 FY26 book (30 Oct 2025) restated Q3 FY25 to Q1 FY26** (and the Q1/Q2 FY25 history): total gross brokerage Q1 FY26 447.15 to 486.72 (+8.9%); cash gross Q1 FY26 216.24 to 252.56 (+16.8%); **cash net Q1 FY26 113.10 to 149.42 (+32.1%)**; cash gross Q3 FY25 222.48 to 232.68 (+4.6%); cash ADTO Q3 FY25 3,230 to 3,395 (+5.1%); cash share Q3 FY25 7.40% (Q3 FY25 book) / 7.35% (Q4 FY25 book) to 7.72%; F&O premium share Q1 FY26 7.88% to 8.71% (+0.8 pp); F&O gross Q1 FY26 183.16 to 186.41 (+1.8%). Commodity gross and net rows never changed (they first appear in the Q2 FY25 book).
- **Q2 FY27 book (29 Oct 2026) restated the WM lending book** (not a Summary input, but it drives the NII-yield proxy): closing lending book Q1 FY26 5,542 to 6,267, Q2 FY26 6,305 to 7,186, Q3 FY26 6,630 to 7,664, Q4 FY26 6,094 to 7,328, Q1 FY27 7,388 to 8,587 (+16.2%); WM "Net Interest Margin on Loans" Q1 FY27 11.41% to 9.67%. In the Q1 FY27 book the WM lending book (7,388) was below the Group MTF book (7,800); in the Q2 FY27 book it is above (8,587), so the restatement looks like it brought the whole MTF book into WM lending (inference; no footnote).
- **Q2 FY27 book vs Q1 FY27 book, Consol sheet:** 207 cells compared, 1 differs: F&O ADTO Q1 FY27 443,891 to 448,098 (+0.95%, `Consol!P45`; not a model input).
- The workbook's typed values equal the Q2 FY26-book vintage (e.g. `C29` = 225 is 224.54 rounded, not 222.68). Use older books only for "as first reported".

## 2. Status table (inputs the Summary reads, 89 data-book-traced)

`assumptions!` = `Motilal Oswal assumptions`. "typed vs book" is the rounding error. "first / now" appears only where an older vintage printed a different number (vintage = the book in which the value first appeared / the book from which the current value applies).

| Workbook cell | Input | Quarter | Typed | Data-book cell (Q2 FY27 book) | Status | Note |
|---|---|---|---|---|---|---|
| assumptions!C6 | MTF closing book (Rs Cr) | Q1FY25 | 4,612 | Consol!F70 = 4,612 | match |  |
| assumptions!C7 | MTF closing book (Rs Cr) | Q2FY25 | 4,649 | Consol!G70 = 4,649 | match |  |
| assumptions!C8 | MTF closing book (Rs Cr) | Q3FY25 | 4,961 | Consol!H70 = 4,961 | match |  |
| assumptions!C9 | MTF closing book (Rs Cr) | Q4FY25 | 4,081 | Consol!I70 = 4,081 | match |  |
| assumptions!C10 | MTF closing book (Rs Cr) | Q1FY26 | 5,042 | Consol!K70 = 5,042 | match |  |
| assumptions!C11 | MTF closing book (Rs Cr) | Q2FY26 | 6,147 | Consol!L70 = 6,147 | match |  |
| assumptions!C12 | MTF closing book (Rs Cr) | Q3FY26 | 6,543 | Consol!M70 = 6,543 | match |  |
| assumptions!C13 | MTF closing book (Rs Cr) | Q4FY26 | 5,757 | Consol!N70 = 5,757 | match |  |
| assumptions!C14 | MTF closing book (Rs Cr) | Q1FY27 | 7,800 | Consol!P70 = 7,800 | match |  |
| assumptions!C29 | F&O gross brokerage (Rs Cr) | Q3FY25 | 225 | Consol!H52 = 224.54 | rounded | typed vs book +0.21%; first 222.68 (Q3FY25 book); now 224.54 (from Q2FY26 book) |
| assumptions!C30 | F&O gross brokerage (Rs Cr) | Q4FY25 | 182 | Consol!I52 = 182.31 | rounded | typed vs book -0.17%; first 180.03 (Q4FY25 book); now 182.31 (from Q2FY26 book) |
| assumptions!C31 | F&O gross brokerage (Rs Cr) | Q1FY26 | 186.41 | Consol!K52 = 186.41 | match | first 183.16 (Q1FY26 book); now 186.41 (from Q2FY26 book) |
| assumptions!C32 | F&O gross brokerage (Rs Cr) | Q2FY26 | 188.03 | Consol!L52 = 188.03 | match |  |
| assumptions!C33 | F&O gross brokerage (Rs Cr) | Q3FY26 | 200.93 | Consol!M52 = 200.93 | match |  |
| assumptions!C34 | F&O gross brokerage (Rs Cr) | Q4FY26 | 203 | Consol!N52 = 202.76 | rounded | typed vs book +0.12%;  |
| assumptions!C35 | F&O gross brokerage (Rs Cr) | Q1FY27 | 206 | Consol!P52 = 205.60 | rounded | typed vs book +0.20%;  |
| assumptions!I27 | F&O premium mkt share | Q1FY25 | 0.0966 | Consol!F66 = 0.0966 | match | first 0.0950 (Q1FY25 book); now 0.0966 (from Q2FY26 book) |
| assumptions!I28 | F&O premium mkt share | Q2FY25 | 0.0912 | Consol!G66 = 0.0912 | match | first 0.0902 (Q2FY25 book); now 0.0912 (from Q2FY26 book) |
| assumptions!I29 | F&O premium mkt share | Q3FY25 | 0.0823 | Consol!H66 = 0.0823 | match | first 0.0780 (Q3FY25 book); now 0.0823 (from Q2FY26 book) |
| assumptions!I30 | F&O premium mkt share | Q4FY25 | 0.0818 | Consol!I66 = 0.0818 | match | first 0.0758 (Q4FY25 book); now 0.0818 (from Q2FY26 book) |
| assumptions!I31 | F&O premium mkt share | Q1FY26 | 0.0871 | Consol!K66 = 0.0871 | match | first 0.0788 (Q1FY26 book); now 0.0871 (from Q2FY26 book) |
| assumptions!I32 | F&O premium mkt share | Q2FY26 | 0.0872 | Consol!L66 = 0.0872 | match |  |
| assumptions!I33 | F&O premium mkt share | Q3FY26 | 0.0838 | Consol!M66 = 0.0838 | match |  |
| assumptions!I34 | F&O premium mkt share | Q4FY26 | 0.0700 | Consol!N66 = 0.0703 | rounded | typed vs book -0.48%;  |
| assumptions!I46 | cash gross brokerage (Rs Cr) | Q3FY25 | 233 | Consol!H51 = 232.68 | rounded | typed vs book +0.14%; first 222.48 (Q3FY25 book); now 232.68 (from Q2FY26 book) |
| assumptions!I47 | cash gross brokerage (Rs Cr) | Q4FY25 | 169 | Consol!I51 = 169.41 | rounded | typed vs book -0.24%; first 167.74 (Q4FY25 book); now 169.41 (from Q2FY26 book) |
| assumptions!I48 | cash gross brokerage (Rs Cr) | Q1FY26 | 252.56 | Consol!K51 = 252.56 | match | first 216.24 (Q1FY26 book); now 252.56 (from Q2FY26 book) |
| assumptions!I49 | cash gross brokerage (Rs Cr) | Q2FY26 | 204.69 | Consol!L51 = 204.69 | match |  |
| assumptions!I50 | cash gross brokerage (Rs Cr) | Q3FY26 | 196.85 | Consol!M51 = 196.85 | match |  |
| assumptions!I51 | cash gross brokerage (Rs Cr) | Q4FY26 | 189 | Consol!N51 = 188.74 | rounded | typed vs book +0.14%;  |
| assumptions!E46 | cash mkt share | Q3FY25 | 0.0772 | Consol!H64 = 0.0772 | match | first 0.0740 (Q3FY25 book); now 0.0772 (from Q2FY26 book) |
| assumptions!E47 | cash mkt share | Q4FY25 | 0.0697 | Consol!I64 = 0.0697 | match | first 0.0672 (Q4FY25 book); now 0.0697 (from Q2FY26 book) |
| assumptions!E48 | cash mkt share | Q1FY26 | 0.0734 | Consol!K64 = 0.0734 | match | first 0.0706 (Q1FY26 book); now 0.0734 (from Q2FY26 book) |
| assumptions!E49 | cash mkt share | Q2FY26 | 0.0708 | Consol!L64 = 0.0708 | match |  |
| assumptions!E50 | cash mkt share | Q3FY26 | 0.0694 | Consol!M64 = 0.0694 | match |  |
| assumptions!E51 | cash mkt share | Q4FY26 | 0.0680 | Consol!N64 = 0.0678 | rounded | typed vs book +0.32%;  |
| assumptions!E52 | cash mkt share | Q1FY27 | 0.0680 | Consol!P64 = 0.0678 | rounded | typed vs book +0.32%;  |
| assumptions!G46 | cash ADTO (Rs Cr/day) | Q3FY25 | 3,395 | Consol!H44 = 3,394.6 | rounded | typed vs book +0.01%; first 3,230.4 (Q3FY25 book); now 3,394.6 (from Q2FY26 book) |
| assumptions!G47 | cash ADTO (Rs Cr/day) | Q4FY25 | 2,585 | Consol!I44 = 2,585.5 | rounded | typed vs book -0.02%; first 2,510.6 (Q4FY25 book); now 2,585.5 (from Q2FY26 book) |
| assumptions!G48 | cash ADTO (Rs Cr/day) | Q1FY26 | 3,304.9 | Consol!K44 = 3,304.9 | match | first 3,179.2 (Q1FY26 book); now 3,304.9 (from Q2FY26 book) |
| assumptions!G49 | cash ADTO (Rs Cr/day) | Q2FY26 | 2,776.2 | Consol!L44 = 2,776.2 | match |  |
| assumptions!G50 | cash ADTO (Rs Cr/day) | Q3FY26 | 2,776.4 | Consol!M44 = 2,776.4 | match |  |
| assumptions!G51 | cash ADTO (Rs Cr/day) | Q4FY26 | 2,984 | Consol!N44 = 2,984.0 | rounded | typed vs book -0.00%;  |
| assumptions!G52 | cash ADTO (Rs Cr/day) | Q1FY27 | 3,552 | Consol!P44 = 3,552.5 | rounded | typed vs book -0.01%;  |
| Working Sheet - MOSL!J53 | commodity gross brokerage (Rs Cr) | Q1FY25 | 33.29 | Consol!F53 = 33.29 | match |  |
| Working Sheet - MOSL!K53 | commodity gross brokerage (Rs Cr) | Q2FY25 | 36.71 | Consol!G53 = 36.71 | match |  |
| Working Sheet - MOSL!L53 | commodity gross brokerage (Rs Cr) | Q3FY25 | 39.92 | Consol!H53 = 39.92 | match |  |
| Working Sheet - MOSL!M53 | commodity gross brokerage (Rs Cr) | Q4FY25 | 39.46 | Consol!I53 = 39.46 | match |  |
| Working Sheet - MOSL!O53 | commodity gross brokerage (Rs Cr) | Q1FY26 | 46.52 | Consol!K53 = 46.52 | match |  |
| Working Sheet - MOSL!P53 | commodity gross brokerage (Rs Cr) | Q2FY26 | 50.52 | Consol!L53 = 50.52 | match |  |
| Working Sheet - MOSL!Q53 | commodity gross brokerage (Rs Cr) | Q3FY26 | 84.23 | Consol!M53 = 84.23 | match |  |
| Working Sheet - MOSL!R53 | commodity gross brokerage (Rs Cr) | Q4FY26 | 90.11 | Consol!N53 = 90.11 | match |  |
| assumptions!K60 | commodity gross brokerage (Rs Cr) | Q1FY27 | 55 | Consol!P53 = 54.72 | rounded | typed vs book +0.51%;  |
| Working Sheet - MOSL!J73 | commodity mkt share | Q1FY25 | 0.0777 | Consol!F67 = 0.0777 | match |  |
| Working Sheet - MOSL!K73 | commodity mkt share | Q2FY25 | 0.0727 | Consol!G67 = 0.0727 | match |  |
| Working Sheet - MOSL!L73 | commodity mkt share | Q3FY25 | 0.0808 | Consol!H67 = 0.0808 | match |  |
| Working Sheet - MOSL!M73 | commodity mkt share | Q4FY25 | 0.0875 | Consol!I67 = 0.0875 | match |  |
| Working Sheet - MOSL!O73 | commodity mkt share | Q1FY26 | 0.0869 | Consol!K67 = 0.0869 | match |  |
| Working Sheet - MOSL!P73 | commodity mkt share | Q2FY26 | 0.0853 | Consol!L67 = 0.0853 | match |  |
| Working Sheet - MOSL!Q73 | commodity mkt share | Q3FY26 | 0.0846 | Consol!M67 = 0.0846 | match |  |
| Working Sheet - MOSL!R73 | commodity mkt share | Q4FY26 | 0.1010 | Consol!N67 = 0.1010 | match |  |
| assumptions!K62 | commodity mkt share | Q1FY27 | 0.0770 | Consol!P67 = 0.0772 | rounded | typed vs book -0.28%;  |
| assumptions!G112 | net/gross cash | Q1FY25 | 0.5238 | Consol!F57/Consol!F51 = 0.5238 | match | first 0.5211 (Q2FY25 book); now 0.5238 (from Q2FY26 book) |
| assumptions!H112 | net/gross cash | Q2FY25 | 0.5377 | Consol!G57/Consol!G51 = 0.5377 | match | first 0.5282 (Q2FY25 book); now 0.5377 (from Q2FY26 book) |
| assumptions!I112 | net/gross cash | Q3FY25 | 0.5499 | Consol!H57/Consol!H51 = 0.5499 | match | first 0.5301 (Q3FY25 book); now 0.5499 (from Q2FY26 book) |
| assumptions!J112 | net/gross cash | Q4FY25 | 0.5391 | Consol!I57/Consol!I51 = 0.5391 | match | first 0.5345 (Q4FY25 book); now 0.5391 (from Q2FY26 book) |
| assumptions!L112 | net/gross cash | Q1FY26 | 0.5916 | Consol!K57/Consol!K51 = 0.5916 | match | first 0.5230 (Q1FY26 book); now 0.5916 (from Q2FY26 book) |
| assumptions!M112 | net/gross cash | Q2FY26 | 0.5306 | Consol!L57/Consol!L51 = 0.5306 | match |  |
| assumptions!N112 | net/gross cash | Q3FY26 | 0.5319 | Consol!M57/Consol!M51 = 0.5319 | match |  |
| assumptions!O112 | net/gross cash | Q4FY26 | 0.5396 | Consol!N57/Consol!N51 = 0.5396 | match |  |
| assumptions!Q112 | net/gross cash | Q1FY27 | 0.5416 | Consol!P57/Consol!P51 = 0.5416 | match |  |
| assumptions!G113 | net/gross F&O | Q1FY25 | 0.5694 | Consol!F58/Consol!F52 = 0.5694 | match | first 0.5682 (Q2FY25 book); now 0.5694 (from Q2FY26 book) |
| assumptions!H113 | net/gross F&O | Q2FY25 | 0.5758 | Consol!G58/Consol!G52 = 0.5758 | match | first 0.5736 (Q2FY25 book); now 0.5758 (from Q2FY26 book) |
| assumptions!I113 | net/gross F&O | Q3FY25 | 0.6011 | Consol!H58/Consol!H52 = 0.6011 | match | first 0.5978 (Q3FY25 book); now 0.6011 (from Q2FY26 book) |
| assumptions!J113 | net/gross F&O | Q4FY25 | 0.5876 | Consol!I58/Consol!I52 = 0.5876 | match | first 0.5824 (Q4FY25 book); now 0.5876 (from Q2FY26 book) |
| assumptions!L113 | net/gross F&O | Q1FY26 | 0.5838 | Consol!K58/Consol!K52 = 0.5838 | match | first 0.5764 (Q1FY26 book); now 0.5838 (from Q2FY26 book) |
| assumptions!M113 | net/gross F&O | Q2FY26 | 0.5930 | Consol!L58/Consol!L52 = 0.5930 | match |  |
| assumptions!N113 | net/gross F&O | Q3FY26 | 0.5966 | Consol!M58/Consol!M52 = 0.5966 | match |  |
| assumptions!O113 | net/gross F&O | Q4FY26 | 0.5750 | Consol!N58/Consol!N52 = 0.5750 | match |  |
| assumptions!Q113 | net/gross F&O | Q1FY27 | 0.5730 | Consol!P58/Consol!P52 = 0.5730 | match |  |
| assumptions!G114 | net/gross commodity | Q1FY25 | 0.6028 | Consol!F59/Consol!F53 = 0.6028 | match |  |
| assumptions!H114 | net/gross commodity | Q2FY25 | 0.6372 | Consol!G59/Consol!G53 = 0.6372 | match |  |
| assumptions!I114 | net/gross commodity | Q3FY25 | 0.6271 | Consol!H59/Consol!H53 = 0.6271 | match |  |
| assumptions!J114 | net/gross commodity | Q4FY25 | 0.6410 | Consol!I59/Consol!I53 = 0.6410 | match |  |
| assumptions!L114 | net/gross commodity | Q1FY26 | 0.5975 | Consol!K59/Consol!K53 = 0.5975 | match |  |
| assumptions!M114 | net/gross commodity | Q2FY26 | 0.5711 | Consol!L59/Consol!L53 = 0.5711 | match |  |
| assumptions!N114 | net/gross commodity | Q3FY26 | 0.5513 | Consol!M59/Consol!M53 = 0.5513 | match |  |
| assumptions!O114 | net/gross commodity | Q4FY26 | 0.5646 | Consol!N59/Consol!N53 = 0.5646 | match |  |
| assumptions!Q114 | net/gross commodity | Q1FY27 | 0.6089 | Consol!P59/Consol!P53 = 0.6089 | match |  |

Net/gross rows (`C112:Q115`, ratio of the `Consol` net and gross rows, e.g. `F57 / F51`): all nine Summary-read quarters (Q1 FY25 to Q1 FY27) per segment are exact; FY columns and currency (row 115) are exact but not read.

### 2.1 The 27 untraced inputs (9 NII yields, 2 industry books, 16 day counts)

| Group | Cells | Source | Status |
|---|---|---|---|
| NII yield (read) | `F6:F14` | **Not in any MOSL filing.** Closest data-book proxy in section 3; no formula reproduces them | no source |
| Industry closing book | `D6:D7` (Q1, Q2 FY25: 70,593.33 / 82,020.37) | Not a MOSL disclosure and not read by the Summary (the daily series starts 1 Oct 2024). The workbook's only named source for the industry book is `MTF data!A5` = `scanx.trade/insight/mtf-insight` (monthly table); the daily series `MTF data (2)!I12:I518` has no named source. Primary source would be exchange-reported MTF outstanding, not verified. | no source [SOURCE NEEDED: daily industry MTF book and the two FY25 closes] |
| Industry book, 30 Sep 2026 | `MTF data (2)!I506` = 151,133.98 | Same unnamed series. MOSL reported share = 9,600 / 151,133.98 = **6.352%** (the model carries 5.776%) | no source |
| Trading days | `M29:M36` (F&O) and `L46:L53` (cash) | **Exchange calendar.** Each typed count equals the number of dated rows per quarter in the workbook's exchange feeder (`backtesting F&O`, `backtesting cash`; these come from the Exchanges dashboard link `[11]`): 62, 62, 61, 64, 62, 60, 60, 65 for Q3 FY25 to Q2 FY27 (16 of 16 equal). They include special sessions (1 Feb 2025 and 1 Feb 2026 are weekend Budget sessions; 1 Nov 2024 and 21 Oct 2025 evening sessions per Methodology 4.5). MCX has more days (64, 65, 64, 65, 64, 64, 64, 66) and the MTF series has 62, 62, 61, 64, 62, 60, **59**, 65 (Q1 FY27 has one fewer). MOSL publishes no day count. Not independently re-checked against NSE holiday circulars. | derived: matches the feeder [SOURCE NEEDED: NSE trading-holiday circulars for an independent check] |

## 3. NII yield: can it be derived from the data book?

**No, not exactly.** The data book has no MTF interest income, MTF NII or MTF yield line (`Consol` row 70 is the closing MTF book only; the Q1 FY27 transcript p14 says "healthy yields and spreads" with no number; the Q4 FY26 and Q1 FY27 decks and transcripts give no MTF yield). The workbook applies the typed yield as `daily MOSL MTF book x yield / 247` (Methodology 4.4).

Closest data-book analogue (Proxy A): **WM net interest income x 4 / WM average lending assets**, `WM!row 8` and `WM!row 46`, latest vintage. WM lending is MTF + LAS + other loans, and WM NII is net of allocated funding cost, so this is a blended yield, not an MTF yield. I also searched all quarterly rows of all sheets (394 rows) as numerator / denominator pairs, with x1, x4 and 365/days annualisation, for a ratio that reproduces the nine typed values to within 10%: none exists. The best single-row pair is spurious.

| Quarter | Typed (assumptions) | WM NII (Rs Cr) `WM!row 8` | WM avg lending assets (Rs Cr) `WM!row 46` | **Proxy A** = NII x 4 / avg lending | A - typed (pp) | A / typed - 1 | Proxy B = NII x 4 / closing lending | Proxy C = NII x 4 / closing MTF book | Reported "Net Interest Margin on Loans" `WM!row 62` |
|---|---|---|---|---|---|---|---|---|---|
| Q1FY25 (F6) | 11.92% | 185.04 | 5,585 | 13.25% | +1.33 | +11.2% | 11.97% | 16.05% | 8.89% |
| Q2FY25 (F7) | 13.26% | 222.91 | 5,913 | 15.08% | +1.82 | +13.7% | 15.80% | 19.18% | 9.87% |
| Q3FY25 (F8) | 13.73% | 213.81 | 5,479 | 15.61% | +1.89 | +13.7% | 16.10% | 17.24% | 10.52% |
| Q4FY25 (F9) | 14.48% | 211.37 | 4,965 | 17.03% | +2.55 | +17.6% | 18.32% | 20.72% | 11.38% |
| Q1FY26 (F10) | 14.51% | 206.70 | 5,441 | 15.19% | +0.68 | +4.7% | 13.19% | 16.40% | 9.82% |
| Q2FY26 (F11) | 15.48% | 252.35 | 6,726 | 15.01% | -0.48 | -3.1% | 14.05% | 16.42% | 11.03% |
| Q3FY26 (F12) | 14.54% | 257.90 | 7,425 | 13.89% | -0.64 | -4.4% | 13.46% | 15.77% | 10.18% |
| Q4FY26 (F13) | 13.06% | 248.37 | 7,496 | 13.25% | +0.19 | +1.5% | 13.56% | 17.26% | 9.46% |
| Q1FY27 (F14) | 12.94% | 264.34 | 7,957 | 13.29% | +0.35 | +2.7% | 12.31% | 13.56% | 9.67% |
| **Q2FY27 (F15 carries F14 = 12.94%)** | 12.94% (carry) | 282.60 | 9,392 | 12.04% | -0.90 vs carry | -7.0% | 11.09% | 11.78% | 9.35% |

Reading it:
- Typed vs Proxy A: correlation 0.58, mean absolute difference 1.10 pp. **From Q1 FY26 to Q1 FY27 they agree within 0.7 pp (+4.7% to -4.4% relative; mean abs 0.47 pp). Q1 to Q4 FY25 the typed yield is 1.3 to 2.6 pp lower than Proxy A** (mean abs 1.9 pp), so the typed series is not the same definition across the nine quarters.
- Vintage matters: on the Q1 FY27 book the Q1 FY27 proxy would be 15.69% (NII 264.34 x 4 / 6,741), on the Q2 FY27 book 13.29% (average lending restated to 7,957). Typed 12.94% sits next to the restated figure.
- The workbook's modelled MTF NII (sum of daily `X`) is 77% to 91% of reported WM NII in Q3 FY25 to Q1 FY27 and **99% in Q2 FY27** (278.9 vs 282.6), because Q2 FY27 carries the Q1 FY27 yield 12.94% on a 65-day quarter. MTF cannot be 99% of WM NII (MTF is 94% of the lending book), so the carried yield looks high for Q2 FY27.
- **Q2 FY27 on Proxy A: 12.04%** (282.602 x 4 / 9,392.072; 11.94% on a 365/92 annualisation; 11.09% on the closing lending book of 10,197) against the carried 12.94% (-0.90 pp).
- Reported "Net Interest Margin on Loans" (`WM!row 62`, 8.9% to 11.4%) is not NII x 4 / average lending (the book's definition is not footnoted; with Proxy A at 12.0% the gap is 2.7 pp) and is 3 to 4.7 pp below the typed yield.
- Recommendation: treat the yield as an assumption, label it `proxy`, and either ask IR for MTF NII/yield or use Proxy A on the latest vintage with the vintage stated. Do not present the typed values as sourced.

## 4. Q2 FY27 actuals (data book of 29 Oct 2026)

Every metric the model uses. QoQ = vs Q1 FY27, YoY = vs Q2 FY26, both from the same (Q2 FY27) book.

| Metric | Data-book cell | Q2 FY27 | Q1 FY27 | Q2 FY26 | QoQ | YoY |
|---|---|---|---|---|---|---|
| Gross brokerage total | Consol!Q50 | 485.50 | 490.59 | 444.19 | -1.0% | +9.3% |
| Cash | Consol!Q51 | 237.79 | 228.30 | 204.69 | +4.2% | +16.2% |
| F&O | Consol!Q52 | 188.47 | 205.60 | 188.03 | -8.3% | +0.2% |
| Commodity | Consol!Q53 | 57.97 | 54.72 | 50.52 | +5.9% | +14.7% |
| Currency | Consol!Q54 | 1.27 | 1.98 | 0.96 | -35.5% | +32.8% |
| Net brokerage total | Consol!Q56 | 277.41 | 275.85 | 249.54 | +0.6% | +11.2% |
| Cash | Consol!Q57 | 132.03 | 123.64 | 108.62 | +6.8% | +21.6% |
| F&O | Consol!Q58 | 110.15 | 117.80 | 111.50 | -6.5% | -1.2% |
| Commodity | Consol!Q59 | 34.46 | 33.32 | 28.85 | +3.4% | +19.4% |
| Currency | Consol!Q60 | 0.77 | 1.09 | 0.57 | -29.4% | +35.9% |
| ADTO cash (Rs Cr/day) | Consol!Q44 | 3,736.7 | 3,552.5 | 2,776.2 | +5.2% | +34.6% |
| ADTO F&O notional (Rs Cr/day) | Consol!Q45 | 449,327.9 | 448,098.0 | 290,970.0 | +0.3% | +54.4% |
| ADTO F&O premium (Rs Cr/day) | Consol!Q46 | 4,923.3 | 5,446.7 | 4,847.0 | -9.6% | +1.6% |
| ADTO commodity (Rs Cr/day) | Consol!Q47 | 43,478.4 | 34,937.0 | 15,452.3 | +24.4% | +181.4% |
| ADTO currency (Rs Cr/day) | Consol!Q48 | 535.8 | 695.0 | 255.4 | -22.9% | +109.7% |
| Market share overall | Consol!Q63 | 7.94% | 7.62% | 8.36% | +0.32 pp | -0.43 pp |
| Market share cash | Consol!Q64 | 7.97% | 6.78% | 7.08% | +1.20 pp | +0.89 pp |
| Market share F&O premium | Consol!Q66 | 8.77% | 7.61% | 8.72% | +1.16 pp | +0.04 pp |
| Market share commodity | Consol!Q67 | 7.85% | 7.72% | 8.53% | +0.13 pp | -0.68 pp |
| MTF closing book (Rs Cr) | Consol!Q70 | 9,600 | 7,800 | 6,147 | +23.1% | +56.2% |
| NSE active clients (lakh) | Consol!Q69 | 9.08987 | 8.98736 | 9.37568 | +1.1% | -3.0% |
| Broking ARPU (Rs) | Consol!Q72 | 21,040 | 20,062 | 18,958 | +4.9% | +11.0% |
| WM net interest income (Rs Cr) | WM!Q8 | 282.60 | 264.34 | 252.35 | +6.9% | +12.0% |
| WM brokerage income (net) (Rs Cr) | WM!Q9 | 204.76 | 205.11 | 183.82 | -0.2% | +11.4% |
| WM distribution income (Rs Cr) | WM!Q7 | 62.30 | 63.70 | 93.39 | -2.2% | -33.3% |
| WM lending book, closing (Rs Cr) | WM!Q18 | 10,197.00 | 8,587.14 | 7,185.78 | +18.7% | +41.9% |
| WM lending assets, average (Rs Cr) | WM!Q46 | 9,392.07 | 7,957.49 | 6,726.36 | +18.0% | +39.6% |

Net / gross by segment, Q2 FY27 (Consol, ratio of rows 56-60 to 50-54): total 57.14%, cash 55.52%, F&O 58.45%, commodity 59.44%, currency 60.72%. Segment sums tie exactly (cash + F&O + commodity + currency = total, gross and net, 0.000 difference in all 10 quarters). Q2 FY27 trading days (workbook feeder): 65 F&O, 65 cash, 66 MCX, 65 MTF. Industry MTF book 30 Sep 2026: 151,133.98 (`MTF data (2)!I506`), MOSL share 6.352%.

**Cross-checks (Q2 FY27)**
- Overall market share 7.94% (`Consol!Q63`) vs "7.9%" in the deck p30 (`MOSL_IR_EarningPresentation_Q2FY27_mofsl-q2fy27-investor-presentation.pdf`) and the combined press release p3 (`NSE_MOTILALOFS_29102026174459_*.pdf`): pass.
- MTF 9,600 vs "9,600+" and +56% YoY (press release p3; data book +56.2%): pass. Loan book 10,197 and +42% YoY (data book +41.9%): pass. WM brokerage 204.76 vs 205 in deck p32 and +11% YoY (data book +11.4%); ARPU +11% (data book +11.0%): pass.
- NSE active clients 9.08987 lakh = 908,987, ties to NSE Report 1C at 30 Sep 2026 (disclosure map section 5): pass.
- Comparison columns: Q1 FY27 and earlier values in the Q2 FY27 book equal the Q1 FY27 book except F&O ADTO Q1 FY27 (+0.95%, recorded, not overwritten).
- Not testable: orders x days (no orders disclosed).

**Workbook estimate vs actual, Q2 FY27** (estimate side from Methodology sections 3, 5 and 6; actual from the table above)

| Parameter | Workbook (estimate) | Actual (data book) | Gap |
|---|---|---|---|
| F&O gross brokerage (model sum) | 179.13 | 188.47 | -4.95% |
| Cash gross brokerage | 200.16 | 237.79 | -15.83% |
| Commodity gross brokerage | 86.47 | 57.97 | +49.17% |
| Broking net (F&O + cash + commodity) | 261.76 | 276.64 | -5.38% |
| Cash market share (carried `E52`) | 6.80% | 7.97% | -1.17 pp |
| Commodity share (avg of last 4) | 8.70% | 7.85% | +0.85 pp |
| F&O premium share (`I35` carry) | 7.69% | 8.77% | -1.08 pp |
| Net/gross F&O / cash / commodity (trailing-2) | 57.40% / 54.06% / 58.67% | 58.44% / 55.52% / 59.44% | +1.0 / +1.5 / +0.8 pp |
| MTF closing book (model, share 5.776%) | 8,729 | 9,600 | -9.1% |
| NII yield (carried) | 12.94% | proxy 12.04% (not reported) | -0.90 pp |

## 5. Answers

### (a) Do ADTO and market share include institutional flows?

**Not stated in the data book; the evidence says retail (plus PWM), but the denominator basis is not footnoted, so it stays unverified.**
- The ADTO and market-share rows (`Consol` rows 44-48, 63-67) carry no footnote. The Capital Market (institutional) sheet has no volume metric at all.
- Management calls the figure retail: Q1 FY27 call, `MOSL_IR_Transcript_Q1FY27.pdf` p4: "overall retail broking market share, including commodities" 7.6% in Q1 FY27 (data book `Consol!P63` 7.62%); Q4 FY26 call, `MOSL_IR_Transcript_Q4FY26.pdf` p4: the same wording for 8.6% in FY26 (data book `Consol!O63` 8.61%). The decks print it as "Consolidated Market share (Cash + F&O + Commodity)" on the Wealth Management slide (Q2 FY27 deck p30), and the deck footnote defines Wealth Management as including retail broking (Q2 FY27 deck p18).
- Consistency test on the numerator: Consol net brokerage ties to WM + PWM brokerage (answer b), not to Capital Markets; Q2 FY27 cash gross brokerage 237.79 / (ADTO 3,736.7 x 65 days) = 9.8 bps of ADTO, a retail full-service rate.
- Denominator test (ADTO / share vs the workbook's exchange feeder, NSE + BSE):

| Quarter | Cash: ADTO / share (Rs Cr/day) | NSE+BSE cash turnover | Ratio | F&O premium: ADTO / share | NSE index options + BSE options premium | Ratio |
|---|---|---|---|---|---|---|
| Q3 FY25 | 43,947 | 110,915 | 0.40 | 66,239 | 62,937 | 1.05 |
| Q4 FY25 | 37,117 | 100,935 | 0.37 | 57,959 | 55,206 | 1.05 |
| Q1 FY26 | 45,018 | 115,833 | 0.39 | 64,353 | 62,920 | 1.02 |
| Q2 FY26 | 39,199 | 104,067 | 0.38 | 55,570 | 55,373 | 1.00 |
| Q3 FY26 | 40,030 | 106,517 | 0.38 | 63,946 | 66,266 | 0.97 |
| Q4 FY26 | 44,024 | 127,489 | 0.35 | 77,364 | 96,617 | 0.80 |
| Q1 FY27 | 52,408 | 145,605 | 0.36 | 71,562 | 86,050 | 0.83 |
| Q2 FY27 | 46,857 | 129,408 | 0.36 | 56,156 | 63,326 | 0.89 |

The cash share is **not** MOSL ADTO / total exchange cash turnover: the implied denominator is 35-40% of it (a client-category subset is consistent with this, but the filings do not say so). The F&O premium denominator tracks total exchange option premium (0.8 to 1.05x), which is not a retail subset. So the share definition may differ by segment. Do not use the share to infer institutional exposure. [SOURCE NEEDED: IR footnote on the market-share denominator and on whether Capital Markets turnover is in ADTO]. The model's cash "delivery ratio" (Methodology 3: 2.5 to 2.9) is the same quantity as the inverse of the 0.35-0.40 ratio here.

### (b) Which brokerage is the revenue base: 277.4 or 378.2?

**The model's base is the consolidated net brokerage line family (`Consol` rows 50-60: gross by segment x net/gross ratio, Q2 FY27 277.41). The 378.2 is a different, wider quantity that includes institutional broking; it is not used.**

| Q2 FY27 | Rs Cr | Cell |
|---|---|---|
| WM brokerage income (net of commission sharing) | 204.76 | `WM!Q9` |
| PWM brokerage income | 70.03 | `PWM!Q8` |
| Capital Market "Net Brokerage & other allied income" (institutional broking and allied income) | 103.41 | `Capital Market!Q7` |
| Sum of three segment lines | **378.21** | |
| WM + PWM | 274.80 | |
| `Consol` net brokerage (row 56) | **277.41** | `Consol!Q56` |
| Gap: three lines minus Consol | 100.80 | = 97.5% of the Capital Market line |
| Gap: Consol minus (WM + PWM) | +2.62 (+0.9%) | unreconciled |

Across the ten quarters Consol net brokerage minus (WM + PWM): Q1 FY25 +5.0, Q2 FY25 +6.7, Q3 FY25 +4.0, Q4 FY25 +13.2, **Q1 FY26 +40.8**, Q2 FY26 +9.6, Q3 FY26 +0.1, Q4 FY26 -9.7, Q1 FY27 +7.6, Q2 FY27 +2.6 (+14% to -3.6% of Consol). So Consol net brokerage is approximately retail (WM) plus HNI (PWM) broking and **excludes the Capital Markets line**; the residual is unexplained (the data book does not reconcile it; the Q1 FY26 gap coincides with the cash restatement). Separately, the `Consol` revenue-mix "-Broking" % x net revenue gives 370.19 in Q2 FY27 (21.07% x 1,756.64), close to the three-line sum (378.21, 2.1% below; 0.6% to 6.8% below it in the other nine quarters). That suggests the "-Broking" revenue line includes Capital Markets, so the book carries two broking notions and only the net-brokerage rows line up with ADTO / share (inference). Do not use the mix % as a revenue input (disclosure map section 3).

Detail for the model: Q2 FY27 net brokerage by segment is cash 132.03 + F&O 110.15 + commodity 34.46 + currency 0.77 = 277.41. The Summary's Broking covers F&O + cash + commodity only (276.64 for Q2 FY27); currency (0.77; 1.09 in Q1 FY27) is not modelled. Gross segments sum to 485.50; gross less net is 208.09 (42.9%), the commission shared out (see c). Implication for cross-broker comparison: MOSL's 277.4 is net of sharing and excludes institutional broking, so it is not like-for-like with a total-income or gross-brokerage basis.

### (c) The net / gross ratio (56-59%)

**Definition: `Consol` Net Brokerage (rows 56-60) divided by Gross Brokerage (rows 50-54), per segment. No filing defines "net" or "gross" for brokerage.** The data book labels the rows only ("Gross Brokerage", "Net Brokerage", "Broking ARPU in Rs. (on Gross brokerage)"): no footnote on `Consol`, no cell comments, nothing on the Summary tab, and none in the 8 earnings decks or the two available transcripts (Q4 FY26, Q1 FY27). The inference (consistent with, not proven by, the filings): net = gross brokerage less the commission paid to franchisees and external wealth managers. Support: deck revenue-by-channel slides note "External channel includes Franchisees" (Q3 FY25 deck p20, Q4 FY25 p20, Q1 FY26 p21); `WM!Q32` shows external wealth managers = 52.9% of WM revenue in Q2 FY27; the WM `Less - Commission Expenses` line is 270.39 (includes distribution commissions, so it cannot be tied to the 208.09 gross-net gap). The workbook applies the ratio per segment (row 112 cash, 113 F&O, 114 commodity).

Values (latest vintage; total range 54.8% to 58.9%, 56-59% for the last eight quarters; FY26 56.8% = `Consol!O56 / O50`):

| Quarter | Total | Cash | F&O | Commodity | Currency |
|---|---|---|---|---|---|
| Q1FY25 | 54.8% | 52.4% | 56.9% | 60.3% | 54.1% |
| Q2FY25 | 55.9% | 53.8% | 57.6% | 63.7% | 51.7% |
| Q3FY25 | 57.9% | 55.0% | 60.1% | 62.7% | 55.6% |
| Q4FY25 | 57.2% | 53.9% | 58.8% | 64.1% | 54.9% |
| Q1FY26 | 58.9% | 59.2% | 58.4% | 59.8% | 55.1% |
| Q2FY26 | 56.2% | 53.1% | 59.3% | 57.1% | 59.3% |
| Q3FY26 | 56.2% | 53.2% | 59.7% | 55.1% | 53.7% |
| Q4FY26 | 55.9% | 54.0% | 57.5% | 56.5% | 56.8% |
| Q1FY27 | 56.2% | 54.2% | 57.3% | 60.9% | 55.4% |
| Q2FY27 | 57.1% | 55.5% | 58.4% | 59.4% | 60.7% |

Cash is the most volatile (53.1% to 59.2%; Q1 FY26 59.2% is the restated quarter), F&O the steadiest (56.9% to 60.1%). The workbook's Q2 FY27 estimate (trailing-2) was 57.40% / 54.06% / 58.67% for F&O / cash / commodity against 58.44% / 55.52% / 59.44% actual.

## 6. Notes and open items
- No number was estimated. Open `[SOURCE NEEDED]`: MTF NII or yield (any), daily industry MTF book and its Q1/Q2 FY25 closes, the market-share denominator definition, an NSE holiday-circular check of the day counts, a reconciliation of Consol net brokerage to WM + PWM.
- Units in `facts_candidates.json`: money in Rs Mn (Rs Cr x 10), ADTO Rs Mn per day, shares as fractions, NSE active clients in Mn (the book prints lakh). Facts are staged, `extracted_by 'claude'`, doc_id null; `share_fo_premium` is the F&O **premium** share (the F&O notional share row 65 is blank from Q1 FY25).
- Workbook rounding feeds forward: the rounded commodity share (7.7% for Q1 FY27) enters the Q2 FY27 four-quarter average, and cash gross Q1 FY27 (228) is not fed at all (Methodology issue 7).
