# Motilal Oswal Financial Services Ltd (MOFSL / MOSL; NSE: MOTILALOFS, BSE 532892, ISIN INE338I01027) - disclosure map for a broking ADR model

Prepared 2026-11-02. Symbol verified: `api/corporate-announcements?index=equities&symbol=MOTILALOFS` returns 1,132 rows (2007-10-18 to 2026-10-30, company name "Motilal Oswal Financial Services Limited"). Latest reporting event: Q2 FY27 (qtr ended 2026-09-30), filed 2026-10-29. Inventory with URLs and sha256: `out/mosl/filings_inventory.json` (41 documents). Raw files: `data/raw/disclosures/mosl/`. IR-site index: `out/mosl/ir_site_spreadsheet_investor-relations.json`. Full NSE feed: `out/mosl/nse_announcements_MOTILALOFS_full.json`.

## 1. Where the data lives

| Channel | What it is | On NSE feed? |
|---|---|---|
| **Quarterly Data Book (.xlsx)** | **The operating-metrics source.** 12 sheets: Summary, Consol (group KPIs, ADTO, brokerage by segment, market share, NSE active clients, MTF, ARPU), AMC, PWM, WM, Capital Market, HFC, Treasury, 5 year Trend, BS & Capital Allocation, Reconcilliation to FS, Exchage Format P&L (spellings as in file). Rs Cr unless a label says otherwise. Published on results day. | **No.** Only on the IR site. No NSE row names a data book. |
| IR site `motilaloswal.com/investor-relations` | Page is rendered from `https://www.motilaloswal.com/spreadsheets/investor-relations.json` (79 rows; columns Year, Quarter, Standalone, Consolidated, Earning Presentation, Concall Transcript, Additional Slides, Concall Recording, Data Book). `motilaloswalgroup.com` redirects to `motilaloswal.com`. | n/a |
| NSE `Investor Presentation` (33 rows), `Press Release` (60), `Analysts/Institutional Investor Meet/Con. Call Updates` (197) | Quarterly earnings presentation (50-57 pp) and press release. **From Q3 FY26 the press release and the presentation are one combined PDF**, filed twice (Press Release, and Analysts/Investor Meet) with the same sha256. | Yes |
| NSE `Outcome of Board Meeting` / `Financial Result Updates` / `General Updates` | Consolidated + standalone results (Rs lakh), segment note, limited-review report, plus a results press-release page at the back. Q2 FY27 PDF has an OCR-quality text layer; the IR-site consolidated/standalone PDFs for Q2 FY27 are image-only. | Yes |
| Concall transcripts | IR site only (NSE carries recording links and a few transcripts). Qualitative: MTF market share, yields, "8 headwinded quarters". | Partly |
| NSE Report 1C (active clients by member) | Monthly; MOSL is a row. See section 7. | NSE archives |
| Monthly business / operating update | **None exists.** No such NSE category for MOTILALOFS; no feed row mentions monthly operating data. | - |

### Data book format, URL pattern, history

- Format: **.xlsx**, ~550-620 KB, formulas pasted as values, one workbook per quarter.
- URLs: `https://www.motilaloswal.com/non-campaign/compliance/q{1-4}fy{25|26}-data-book.xlsx`; Q1 FY27 `/non-campaign/compliance/mofsl-q1fy27-data-book.xlsx`; **Q2 FY27 moved folder:** `https://www.motilaloswal.com/non-campaign/download/q2fy27-data-book.xlsx`. So the pattern is not stable: always read the IR JSON `Data Book` column. Pre-FY25 rows have an empty Data Book cell; a stray Q1 FY25 row points at a dead file (`734517138q2fy24-data-sheet.xlsx`, HTTP 404); `q?fy24-data-book.xlsx` redirects (302).
- Available: 10 books, Q1 FY25 to Q2 FY27 (all 10 downloaded). Cadence quarterly; Q1 FY27 and Q2 FY27 HTTP Last-Modified equals the results day (23-Jul-2026, 29-Oct-2026). Older books show Last-Modified of a Jul-2026 site re-upload, so their publication date is taken as the results day.
- History per workbook: annual columns FY21 to last FY, plus a **rolling quarterly window that changes size**: Q1 FY25 book Q1FY23..Q1FY25 (9 qtrs); Q4 FY25 book Q1FY23..Q4FY25 (12); Q1 FY26 book Q1FY23..Q1FY26 (13); Q2 FY26 to Q4 FY26 books Q1FY24..; **Q1 FY27 and Q2 FY27 books Q1FY25..** (9 and 10 qtrs). **Q1FY23-Q4FY24 quarterly values survive only in the older workbooks, so keep every vintage.**
- Row positions move between vintages (e.g. Consol ADTO header row 41 in Q1 FY25, 43 in Q2 FY27); match on labels, not row numbers. Row refs below are the Q2 FY27 book.

## 2. Filings found (last 8 quarters, Q3 FY25 to Q2 FY27)

| Quarter (results date on NSE) | Data book (IR) | Presentation (IR) | NSE press release / presentation | Results |
|---|---|---|---|---|
| Q3 FY25 (2025-01-28) | yes | yes (54 pp) | PR + pres separately | not downloaded (only latest requested) |
| Q4 FY25 (2025-04-25) | yes | yes (56 pp) + Additional Slides | PR + pres separately | - |
| Q1 FY26 (2025-07-24) | yes | yes (55 pp) | PR + pres separately | - |
| Q2 FY26 (2025-10-30) | yes | yes (56 pp) | PR + pres separately | - |
| Q3 FY26 (2026-01-27) | yes | yes (55 pp) | combined PR+pres | - |
| Q4 FY26 (2026-04-29) | yes | yes (57 pp) | combined PR+pres | - |
| Q1 FY27 (2026-07-23) | yes | yes (55 pp) | combined PR+pres | - |
| Q2 FY27 (2026-10-29) | yes | yes (50 pp) | combined PR+pres | NSE financials (24 pp) + Outcome (23 MB) + IR consolidated/standalone PDFs |

Also downloaded: Q1 FY25 and Q2 FY25 data books (they are the oldest vintages), Q4 FY26 and Q1 FY27 concall transcripts, NSE Report 1C workbooks FY24-FY27.

## 3. Metric x source x cadence x first period x refs (broking business)

Terminology: MOSL has **no "broking segment"**. Retail broking sits inside the statutory segment **Wealth Management (WM)** with distribution and lending (deck footnote, Q2 FY27 p18: "includes retail broking, capital market lending & distribution"). Institutional broking sits in **Capital Markets (IE & IB)**. HNI/UHNI broking sits in **Asset & Private Wealth Management**. Sheet "Consol" carries group-wide broking KPIs that are not split by segment.

| Metric | Source | Cadence | First period | Where (Q2 FY27 data book unless stated) |
|---|---|---|---|---|
| **Orders / trades / trade count** | **Not disclosed anywhere** | - | - | No order or trade count in data books, decks, results or transcripts reviewed. |
| **ADTO by segment, Rs Cr/day**: Cash, F&O notional, F&O premium, Commodity, Currency | Data book | Quarterly | Cash, F&O notional, F&O premium: Q1FY23 (F&O premium from Q1FY24); Commodity + Currency: first book carrying them is Q2 FY25 (history Q1FY23) | `Consol` rows 44-48 (annual FY21-FY26 in cols B-E/J/O). Q2 FY27: cash 3,736.7; F&O 449,327.9; F&O premium 4,923.3; commodity 43,478.4; currency 535.8. Deck glossary (Q2 FY27 p48) defines ADTO only. |
| **Market share: overall (Cash+F&O+Commodity)**, cash, F&O premium, commodity | Data book; deck headline; transcripts | Quarterly | Cash Q1FY23; F&O premium Q1FY24; **overall + commodity first in the Q4 FY26 book (history from Q1FY24)** | `Consol` rows 63 (overall), 64, 66, 67. Q2 FY27: overall 7.94%, cash 7.97%, F&O premium 8.77%, commodity 7.85%. Deck p30 "Consolidated Market share: 7.9% in Q2FY27". F&O **notional** market share (row 65) ends in the Q3 FY26 book (blank for quarters in later books). Denominator exchange/turnover basis is not footnoted. |
| **Retail vs institutional ADTO / market share** | **Not disclosed** | - | - | The ADTO/market-share rows are labelled "Consolidated"; the Q1 FY27 transcript p4 calls the market share "overall retail broking market share, including commodities". Capital Markets (institutional) sheet has no volume metric. Whether institutional turnover is excluded is **unverified**. |
| **Active clients: NSE active clients (lakh)** | Data book | Quarterly | Q1FY23 | `Consol` row 69. Q2 FY27 9.08987 lakh = **908,987, ties exactly to NSE Report 1C at 30-Sep-2026**. |
| Group customers (mn), AUA (Rs bn) | Data book | Quarterly | Q1FY23 | `Consol` rows 22-23. Q2 FY27 16.21 mn customers, Rs 8,800.8 bn AUA. Customers is a group-wide count (all products). |
| "~10.3 Mn Broking Clients", "~5.9 Mn" WM clients | Deck narrative | Quarterly (deck) | - | Q2 FY27 deck p10. Registered/ever clients, not active. |
| **Gross brokerage by segment, Rs Cr**: Cash, F&O, Commodity, Currency, Total | Data book | Quarterly | **Q2 FY25 book (history from Q1FY23)**; not in the Q1 FY25 book | `Consol` rows 50-54. Q2 FY27 total 485.50 = 237.79 + 188.47 + 57.97 + 1.27. |
| **Net brokerage by segment, Rs Cr** (after commission paid to franchisees and external wealth managers) | Data book | Quarterly | Q1FY23 (cash/F&O/total); commodity/currency from Q2 FY25 book | `Consol` rows 56-60. Q2 FY27 277.41. |
| **Brokerage revenue by business** (net of sharing): WM / PWM / Capital Markets | Data book | Quarterly | Q1FY23 (FY21 annual) | WM `WM` row 9 (Q2 FY27 204.76); PWM `PWM` row 8 (70.03); Capital Markets `Capital Market` row 7 "Net Brokerage & other allied income" (103.41; **institutional**). Deck Q2 FY27 p32 chart: WM brokerage 205 vs 184 YoY. **These three do not sum to Consol net brokerage** (378.2 vs 277.4): intercompany/definition gap, unreconciled. |
| **Broking share of group net revenue (%)** | Data book | Quarterly | Q1FY23 | `Consol` row 29 "-Broking" (21.07% Q2 FY27). Note 21.07% x group net revenue 1,756.64 = 370.2, which is not the Consol net brokerage (277.4); basis unclear, do not use as a revenue input. |
| **Broking ARPU, Rs** ("on gross brokerage") | Data book | Quarterly | Q1FY23 | `Consol` row 72. Q2 FY27 21,040. Definition not footnoted. FY25 ties to FY gross brokerage / average of opening and closing NSE active clients (about 0.15% off), but quarterly values do **not** reproduce as annualised gross brokerage / NSE active clients (e.g. Q4 FY25 22,826 vs 15,447 implied). |
| **MTF book, Rs Cr** | Data book; transcripts | Quarterly (closing) | **Q4 FY26 book (history from Q1FY24; annual FY21+)** | `Consol` row 70. Q2 FY27 9,600 (Q1 FY27 7,800). Deck p10-11 mention MTF qualitatively. Q1 FY27 transcript p4: MTF market share about 6.5%; p14: "book has grown 54% YoY", "healthy yields and spreads" (no number). |
| **Lending book (MTF + LAS + other), Rs Cr**, WM and PWM | Data book | Quarterly | Q1FY23 | `WM` rows 18, 38, 46 (average); `PWM` rows 45, 60. Q2 FY27 WM closing 10,197 (incl. MTF 9,600 per Consol). Deck Q2 FY27 p32: lending book 10,197 vs 7,186 YoY. |
| **MTF / lending interest income and NII** | Data book | Quarterly | Q1FY23 (NII); interest income and finance cost from Q1FY25 | **MTF interest income is not separate.** WM NII `WM` row 8 (282.60 Q2 FY27); WM interest income and finance cost `Reconcilliation to FS` rows 4-5 (526.05, -243.45; matches statutory WM interest income 52,658 lakh in results p10 within basis differences). `WM` row 62 "Net Interest Margin on Loans" (9.35% Q2 FY27, annualised; does not reproduce as NII x 4 / average lending assets, which gives 12.0%). |
| **Distribution income** | Data book | Quarterly | Q1FY23 | `WM` row 7 (62.30 Q2 FY27), `PWM` row 6 (132.26). Distribution assets `WM` row 17 (47,911.8). Deck p32: Q2 FY26 had Rs 27 Cr secondary-transaction revenue vs nil in Q2 FY27. |
| **Total income, broking-bearing segments** | Data book; statutory results | Quarterly | Q1FY23 (data book); Q1 FY25 comparatives (results) | `WM` row 3 gross revenue 1,108.66 (statutory WM revenue 1,110.33, results p10); net revenue row 6 (590.25). `Capital Market` row 3 gross 216.96 = statutory Capital Markets 21,696 lakh (ties). Group `Consol` row 3 gross 2,562.20, row 6 net 1,756.64. |
| **Total income, consolidated group** | Results (NSE); Exchage Format P&L | Quarterly | all | NSE financials Q2 FY27 p6: revenue from operations 3,04,167 lakh, total income 3,04,376 lakh. Includes treasury fair-value gains (83,305 lakh); `Consol` data-book gross revenue excludes the "Fund Base"/treasury line. `Exchage Format P&L` sheet repeats p6 in lakh. |
| **Statutory brokerage line** | Standalone results (NSE) | Quarterly | all | NSE financials Q2 FY27 p13: "Brokerage and fees income" 60,502 lakh (Q2 FY27), 53,568 (Q2 FY26). Standalone parent only, includes fees; reviewed, not a segment cut. |
| **Segment reporting (statutory, Ind AS 108)** | Consolidated results note | Quarterly | all | NSE financials Q2 FY27 p10-11: five segments (Wealth Management, Capital Markets, Asset & Private Wealth Management, Home Finance, Treasury Investments), with external vs interest revenue, interest expense, D&A, PBT, assets, liabilities. AMC is **inside** Asset & PWM; the data book splits AMC and PWM separately. Standalone: no segment note (p17 note 7). |
| **Yield / take-rate** | Not disclosed as such | - | - | Only ARPU (above) and gross vs net brokerage (net/gross 56-59%). Revenue per Rs of turnover is derivable (brokerage / ADTO x trading days) but needs an exchange trading-day count that MOSL does not publish. Retention on AUM rows `WM` rows 60-62. |
| VAR (variable additional returns, AMC/Alternates) | Data book | Quarterly | Q1FY24 | `Consol` row 74. Not broking. |
| Client assets, net flows | Data book | Quarterly | Q1FY23 | `WM` rows 15-18, 55-57. |

## 4. Quarterly series for an ADR model (Q2 FY27 data book values, the latest vintage)

| Metric | Q3FY25 | Q4FY25 | Q1FY26 | Q2FY26 | Q3FY26 | Q4FY26 | Q1FY27 | Q2FY27 |
|---|---|---|---|---|---|---|---|---|
| Gross brokerage total, Rs Cr | 497.8 | 392.0 | 486.7 | 444.2 | 483.4 | 483.1 | 490.6 | 485.5 |
| - Cash | 232.7 | 169.4 | 252.6 | 204.7 | 196.9 | 188.7 | 228.3 | 237.8 |
| - F&O | 224.5 | 182.3 | 186.4 | 188.0 | 200.9 | 202.8 | 205.6 | 188.5 |
| - Commodity | 39.9 | 39.5 | 46.5 | 50.5 | 84.2 | 90.1 | 54.7 | 58.0 |
| - Currency | 0.66 | 0.78 | 1.23 | 0.96 | 1.37 | 1.50 | 1.98 | 1.27 |
| Net brokerage total, Rs Cr | 288.3 | 224.2 | 286.7 | 249.5 | 271.7 | 270.2 | 275.9 | 277.4 |
| ADTO cash, Rs Cr | 3,395 | 2,585 | 3,305 | 2,776 | 2,776 | 2,984 | 3,552 | 3,737 |
| ADTO F&O notional, Rs Cr | 456,606 | 298,509 | 282,953 | 290,970 | 357,456 | 409,512 | 448,098 | 449,328 |
| ADTO F&O premium, Rs Cr | 5,450 | 4,740 | 5,602 | 4,847 | 5,360 | 5,441 | 5,447 | 4,923 |
| ADTO commodity, Rs Cr | 8,348 | 9,616 | 12,659 | 15,452 | 27,419 | 30,637 | 34,937 | 43,478 |
| Market share overall | 8.05% | 8.27% | 8.45% | 8.36% | 8.30% | 9.20% | 7.62% | 7.94% |
| Market share cash | 7.72% | 6.97% | 7.34% | 7.08% | 6.94% | 6.78% | 6.78% | 7.97% |
| Market share F&O premium | 8.23% | 8.18% | 8.71% | 8.72% | 8.38% | 7.03% | 7.61% | 8.77% |
| Market share commodity | 8.08% | 8.75% | 8.69% | 8.53% | 8.46% | 10.10% | 7.72% | 7.85% |
| NSE active clients, lakh | 10.30 | 10.15 | 9.97 | 9.38 | 9.11 | 9.02 | 8.99 | 9.09 |
| MTF book, Rs Cr | 4,961 | 4,081 | 5,042 | 6,147 | 6,543 | 5,757 | 7,800 | 9,600 |
| Broking ARPU, Rs | 25,833 | 22,826 | 21,322 | 18,958 | 18,608 | 19,796 | 20,062 | 21,040 |
| WM brokerage (net), Rs Cr | 225.0 | 161.1 | 193.3 | 183.8 | 212.0 | 215.0 | 205.1 | 204.8 |
| WM distribution income, Rs Cr | 87.8 | 181.9 | 128.4 | 93.4 | 61.3 | 105.3 | 63.7 | 62.3 |
| WM NII, Rs Cr | 213.8 | 211.4 | 206.7 | 252.3 | 257.9 | 248.4 | 264.3 | 282.6 |
| WM closing lending book, Rs Cr | 5,313 | 4,616 | 6,267 | 7,186 | 7,664 | 7,328 | 8,587 | 10,197 |
| Capital Markets net brokerage & allied, Rs Cr | 74.7 | 72.9 | 122.7 | 77.1 | 89.0 | 94.5 | 83.0 | 103.4 |
| PWM brokerage, Rs Cr | 59.3 | 49.9 | 52.5 | 56.1 | 59.6 | 64.8 | 63.1 | 70.0 |

These values were read from the files and not otherwise adjusted. Trading days per quarter are not in any MOSL filing.

## 5. Checks run (precision rules)

- Gross brokerage segments (cash + F&O + commodity + currency) = total gross brokerage; net likewise: **pass, difference 0.000 in all 8 quarters** (Q2 FY27 485.50 and 277.41).
- NSE active clients vs NSE Report 1C: Q2 FY27 9.08987 lakh vs 908,987 at 30-Sep-2026; Q4 FY26 9.02 vs 901,790 (FY26 file); Q4 FY25 10.15 vs 1,014,875 (FY25 file): **pass**.
- Data book vs deck: Q2 FY27 overall market share 7.94% vs deck p30 7.9%; Q1 FY27 7.62% vs transcript p4 7.6%; WM brokerage/distribution/NII/other 204.8/62.3/282.6/40.6 vs deck p32 chart 205/62/283/41 and total 590: **pass**.
- Capital Markets gross revenue Q2 FY27 216.96 vs statutory segment revenue 21,696 lakh: **pass**. WM gross revenue 1,108.66 vs statutory 1,110.33 (0.15% off) and Q2 FY26 969.75 vs 978.06 (0.9% off): management vs statutory basis, noted not forced.
- **Restatement flag.** Values for the same quarter differ across vintages. Q2 FY26 data book (Oct-2025) restated history: Q1 FY26 cash gross brokerage 216.2 (Q1 FY26 book) to 252.6; Q3 FY25 total gross brokerage 485.7 to 497.8; Q1 FY26 F&O premium ADTO 5,058 to 5,602; Q1 FY26 F&O premium market share 7.9% to 8.7% (the Q1 FY26 deck p18 prints cash 7.1% and F&O premium 7.9%; current book 7.34% and 8.71%). Books from Q2 FY26 onward are stable against each other (0.0% drift except F&O ADTO Q1 FY27 0.9%). Use the latest vintage; use an older book only for "as first reported".
- Not testable: orders x days = total orders and segment-orders-sum (no orders disclosed). ARPU and NIM-on-loans definitions could not be reproduced (section 3).
- The data book `Consol` ADTO and market-share labels do not say whether institutional flows are included; recorded as unverified rather than assumed.

## 6. What MOSL discloses that Angel One and Groww do not, and the reverse

MOSL discloses more than Angel/Groww on:
- **Gross and net brokerage in Rs Cr by segment** (cash / F&O / commodity / currency), with the commission-sharing wedge (net/gross 56-59%). Groww gives only % of total income; Angel's monthly update gives orders, market share and client base.
- **ADTO in Rs Cr by segment** (notional and premium for F&O) with **market share by segment** (and an overall figure), with 9-13 quarters per book and FY21 annual history.
- Segment P&L at five statutory segments (Groww reports one reportable segment), balance sheet per segment, interest income and finance cost per segment.
- Distribution income and distribution assets, lending book and NII, closing client assets and net flows.
- Retail/institutional/HNI separation **by business line** (Wealth Management, Capital Markets, PWM), though not by volume.
- Statutory standalone "Brokerage and fees income" line.

MOSL does not disclose, while Angel and/or Groww do:
- **Orders/trades** (Angel: monthly orders by segment; Groww: quarterly broking orders). This is the biggest gap for an orders-based ADR model.
- A monthly business update (Angel). MOSL has none.
- Retail vs institutional volume split; client counts by segment; client additions; unique clients or MAU/DAU (Groww).
- MTF interest income and MTF yield (Groww states 14.95% on its call); MOSL gives the book and qualitative "healthy yields" only.
- Revenue per order / take-rate table (Groww gives revenue per order commentary).
- F&O **notional** market share has been dropped since the Q4 FY26 book (premium turnover remains).

Net: a **revenue-per-turnover ADR** is feasible for MOSL (brokerage Rs Cr / ADTO) but not a revenue-per-order ADR.

## 7. Monthly or intra-quarter series

- **MOSL itself: none** (no monthly business update, no monthly data book, no QTD widget).
- **NSE Report 1C (active clients by member)**: `https://nsearchives.nseindia.com/miscellaneous/ArbitrationReports/isc_report1C_2627.xls`, fetched OK (HTTP 200, Last-Modified 2026-10-07, sheet `isc_report1C_2627_300926`, header "Last Updated on 30-September-2026"). MOSL row is **"Motilal Oswal Financial Services Limited"** (row 12, sr. 4): Sep-2026 active clients **908,987**; col D "NO. OF UCCs AT THE BEGINNING OF THE YEAR" 5,440,425 (total UCCs, not active); col J = active clients (FY27 layout). Older FY files (`2526`, `2425`, `2324`) hold only year-end actives in col D "UCC OF ACTIVE CLIENTS": FY26 901,790; FY25 1,014,875; FY24 879,631 (row 156, as "MOTILAL OSWAL FINANCIAL SERVICES LIMITED"; a second entity "Motilal Oswal Capital Markets Private Limited" shows "-"). Updated about the 7th of the following month. **The file is overwritten in place, so archive each month ourselves.** Same series that feeds the data book "NSE Active clients" row, so it gives month-end values that interpolate within a quarter and tie to the quarter-end data book figure. Four files saved in `data/raw/disclosures/mosl/nse_report_1C/`.
- Exchange-wide monthly turnover by segment (NSE/BSE/MCX) x MOSL's quarterly market share could shape intra-quarter ADTO and brokerage (e.g. interpolate gross brokerage by segment using turnover shape and the quarter's gross brokerage / ADTO ratio). Not tested here; no MOSL-specific broker-wise turnover is published by NSE.
- Depository (CDSL/NSDL) monthly demat counts by DP could give a second client-growth series. Not tested.

## 8. Other notes

- IR-site `Year/Quarter` labels contain mis-tagged rows (e.g. a second "24-25 Q1" row carries Q4 FY25 documents and the Q1 FY25 data book; rows for Q2 FY27 appear twice, one without the data book). Use the file name, not the label.
- Q1 FY25 and Q2 FY25 books omit some metrics later added (gross brokerage by segment, commodity/currency ADTO, MTF, commodity and overall market share), see section 3 first-period column.
- Q2 FY27 results text layer is OCR quality (e.g. "Singfii"); numbers quoted above from it were read from clean lines and cross-checked to the data book's `Exchage Format P&L` sheet (same figures in lakh). IR-site consolidated/standalone Q2 FY27 PDFs have no text layer and were not read.
- MOSL's group "Total Gross Revenue" in the data book excludes the treasury "Fund Base" line, while the statutory total income includes it (Q2 FY27 2,562.2 Cr vs 3,043.8 Cr).
- Files: `out/mosl/filings_inventory.json`, `out/mosl/disclosure_map.md`, `out/mosl/ir_site_spreadsheet_investor-relations.json`, `out/mosl/nse_announcements_MOTILALOFS_full.json`, `data/raw/disclosures/mosl/`.
