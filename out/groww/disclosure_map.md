# Groww (Billionbrains Garage Ventures Ltd, NSE: GROWW, BSE 544603) - disclosure map for an ADR model

Prepared 2026-10-31. Listing 2025-11-12. Five reporting events since listing: Q2 FY26 (21-Nov-25), Q3 FY26 (14-Jan-26), Q4 FY26 (20-Apr-26), Q1 FY27 (15-Jul-26), Q2 FY27 (14-Oct-26). Inventory with URLs and sha256: `out/groww/filings_inventory.json`. Raw files: `data/raw/disclosures/groww/`.

## 1. Where the data lives (important: not where Angel's is)

| Channel | What it is | On NSE feed? |
|---|---|---|
| NSE `Outcome of Board Meeting` | Results PDF (consolidated + standalone), limited-review report | Yes. Q2 FY26 PDF is image-only (no text layer); the other four have text. |
| NSE `Investor Presentation` / `Analysts/Investor Meet - Presentation` | The quarterly **Shareholders' Letter** (11-14 pp). Groww has no separate investor deck and files **no press release**. | Yes. Q3 FY26 letter was filed twice under two categories (identical sha256). |
| NSE `Updates` / `General Updates` "Key Performance Indicators" | One-page cover note only, pointing to groww.in. | Yes, but contains no numbers. |
| **groww.in/investor-relations/performance/quarterly-results** | **KPI Handbook (.xlsx)** per quarter: the real operating-metrics table, 9 quarters of history each time. | **No.** Only on the IR site. |
| groww.in/investor-relations home page | Live "Our Metrics" widget: quarterly history since Q1 FY22 plus quarter-to-date current figures (embedded JSON, `__NEXT_DATA__`). | No. |
| Earnings-call transcripts (NSE `Analysts/Institutional Investor Meet/Con. Call Updates`) | Verbal order economics. | Yes. |

NSE feed facts: symbol `GROWW` returns 110 announcements (2025-11-12 to 2026-10-16, same with or without date windows); `BILLIONBRAINS` returns nothing. No "Press Release" and no "Monthly Business Updates" category exists for Groww. BSE not tried (Access Denied earlier).

## 2. Metric x source x cadence x first period x pages

Page refs are PDF pages of the NSE-filed file (cover letter = p1). "Handbook" sheet names are as in the xlsx. Letter files: Q2FY26 `...21112025104921_Shareholderslettersigned.pdf`, Q3FY26 `...14012026125814_SHLetterSigned_.pdf`, Q4FY26 `...20042026132113_ShareholdrsLetterSigned.pdf`, Q1FY27 `...15072026114459_ShareholderLettersigned.pdf`, Q2FY27 `...14102026130454_ShareholderLetter_Final.pdf`.

| Metric | Source | Cadence | First period | Where |
|---|---|---|---|---|
| **Broking orders, total** (Stocks + Derivatives; glossary: "orders executed in Stocks and Derivatives") | KPI Handbook | Quarterly | Q2 FY25 (history in Q2 FY26 handbook); first published Q2 FY26 | Handbook `Operational KPIs` / `Platform KPIs`, row "Broking Orders". Q2 FY27 handbook gives 9 quarters in Cr. Letter glossary p13 (Q2 FY26 letter) defines it. |
| Orders by segment (F&O / cash / commodity) | **Not disclosed** | - | - | Only one datum: commodity = 4.6% of broking orders in Q3 FY26 (0.3% in Q2 FY26): Q3 FY26 letter p8. Q4 FY26: commodity average daily orders +60.7% QoQ (Q4 letter p8). Analysts back-solve the split from Rs20/order (Q3 FY26 transcript p8-9: ~5.4 Mn derivative + ~2.3 Mn stock orders/day, analyst-derived). |
| Trading days in period | KPI Handbook | Quarterly | Q2 FY25 | bottom row of the KPI sheets |
| Revenue per broking order | Letter Q&A + transcripts | Ad hoc | Q2 FY26 (Rs19.8 vs Rs18.0 in Q2 FY25; avg stock order value Rs59,079) | Q2 FY26 letter p7. Q3 FY26 call: blended Rs19.6 -> Rs19.9 (analyst-quoted, mgmt did not dispute) transcript p9. Q2 FY27 call: F&O and commodity Rs20 flat per order; cash = lower of 10 bps or Rs20, brokerage ~Rs15-16 per cash order (transcript p10). |
| Revenue mix by product, % of **Total Income** (Equity Derivs, Stocks, Commodity, MTF, Float, PL+LAS, Other operating, Other income) | Letter | Quarterly (5-quarter chart each time) | Q2 FY25 (coarser buckets) | Q2 FY26 p7; Q3 FY26 p6; Q4 FY26 p7; Q1 FY27 p6; **Q2 FY27 p6** (latest, restated, one-decimal, 8 buckets; verified visually). Rs values are not published; derive as % x Total Income. |
| Stocks revenue split | Letter text | Q2 FY27 only | Q2 FY27 | brokerage = 70-75% of Stocks revenue, rest DP/DDPI/pledge/auto-square-off: Q2 FY27 letter p7 |
| Total income / Revenue from operations (consolidated, Rs Cr) | Results PDF + Handbook `Summary P&L` | Quarterly | Q2 FY26 (+ comparatives) | Results: Q3 FY26 p6, Q4 FY26 p8, Q1 FY27 p6, Q2 FY27 p7 (Q2 FY26 PDF image-only). Q2 FY27: revenue 1,501.53, total income 1,540.54. |
| Segment revenue in statutory results | **Not disclosed**: "only one reportable segment" | - | - | Results note: Q3 FY26 p7, Q4 FY26 p11, Q1 FY27 p7, Q2 FY27 p10 |
| Platform revenue ex Fisdom/AMC, cost to serve etc. | Handbook `Financial KPIs` | Quarterly | Q2 FY25 | Q2 FY27 handbook: Rs1,497.4 Cr revenue (differs from consolidated 1,501.53 by scope) |
| NSE active clients (and share of NSE total) | Handbook + letter | Quarterly | Q2 FY25 (handbook); share 26.3% in Q2 FY26 letter p5 | Handbook `Platform KPIs` row 5; last in Q1 FY27 handbook (1.305 Cr); Q1 FY27 letter p7 (+115k net adds vs industry -257k). **Dropped from the Q2 FY27 handbook and letter.** |
| Active users / total transacting users / MAU / DAU | Handbook, letter | Quarterly | Q2 FY25 | Letters p4 (all five). Q2 FY27 handbook restates users and assets to include W + Fisdom (e.g. Q1 FY27 TTU 2.24 Cr -> 2.2935 Cr), so splice with care. |
| Broking transacting users | Handbook | Quarterly | Q2 FY25 | `Platform KPIs` row 14; not in Q2 FY27 handbook |
| Market share: stocks (retail cash ADTO), equity-derivs premium ADTO, MTF book, MF SIP | Letter | Quarterly (YoY pair only in letter; handbook has the ADTO level history) | Q2 FY26 | Q2 FY26 p5; Q3 FY26 p5; Q4 FY26 p5; Q1 FY27 p5; Q2 FY27 p5. Definition change in Q4 FY26: retail ADTO share now = Groww / (exchange turnover x 2) (Q4 FY26 letter p5-6, restated Q2 FY26 25.8% -> 12.9%). MTF share denominator became NSE+BSE in Q1 FY27 (letter p5). Commodity retail share (notional ADTO, MCX+NSE) 28.6% in Q1 FY27 only (letter p7). |
| ADTO levels: Stocks, Equity-derivs premium, Commodity notional | Handbook | Quarterly | Stocks/deriv Q2 FY25; commodity Q2 FY26 (Q2 FY27 handbook rows 10, 14, 16) | `Operational KPIs` |
| MTF book, MTF active users | Handbook, letter | Quarterly | Q2 FY25 | Handbook rows 9, 12; Q2 FY26 letter p8. Q2 FY27: Rs4,351 Cr. MTF yield fixed 14.95% (Q1 FY27 transcript p13). |
| Float / PL+LAS / loan books | Handbook (disbursements, GCS books) + mix % | Quarterly | Q2 FY25 | `Operational KPIs` rows 17-20 |
| Customer assets, MF assets, stock assets | Handbook | Quarterly | Q2 FY25 | rows 4, 7, 11 |
| Monthly / QTD turnover and MTF, TTU, assets (live) | IR home page widget | Daily refresh (cache ~35 s), QTD | Q1 FY22 quarterly history; Commodity T/O from Q2 FY26; MTF from Q1 FY25 | `groww.in/investor-relations` -> `__NEXT_DATA__.props.pageProps.initialChartConfigs`. As of 31-Oct-26: Stocks T/O Rs2.73 Tn, Equity-deriv premium T/O Rs3.71 Tn, Commodity notional Rs82.96 Tn, MTF Rs40.85 Bn (QTD, Q3 FY27). |
| NSE active clients by member (Groww Invest Tech Pvt Ltd) | NSE Report 1C workbook | Monthly (file overwritten; sheet "as of" date in name) | FY24 file onwards | See section 4 |

### Quarterly series needed for ADR (from Q2 FY27 handbook, `Operational KPIs`; Cr)

| Quarter | Broking orders (Cr) | Trading days | Orders/day (Mn) |
|---|---|---|---|
| Q2 FY25 | 53.2394 | 64 | 8.32 |
| Q3 FY25 | 45.4209 | 62 | 7.33 |
| Q4 FY25 | 35.7715 | 62 | 5.77 |
| Q1 FY26 | 37.8557 | 61 | 6.21 |
| Q2 FY26 | 41.5707 | 64 | 6.50 |
| Q3 FY26 | 47.4194 | 62 | 7.65 |
| Q4 FY26 | 58.7390 | 60 | 9.79 |
| Q1 FY27 | 56.0156 | 60 | 9.34 |
| Q2 FY27 | 51.7305 | 65 | 7.96 |

Revenue mix, % of Total Income, Q2 FY27 letter p6: Eq Derivs 56.9 / 53.5 / 54.8 / 51.9 / 44.8; Stocks 17.8 / 16.5 / 15.6 / 16.1 / 17.4; Commodity 0.2 / 3.5 / 4.5 / 4.9 / 6.2; MTF 4.7 / 5.6 / 6.9 / 8.0 / 10.1; Float 7.4 / 7.0 / 7.9 / 8.4 / 8.4; PL+LAS 6.2 / 5.9 / 5.2 / 5.5 / 5.9; Other operating 1.9 / 4.3 / 3.3 / 2.1 / 4.8; Other income 4.9 / 3.6 / 2.0 / 3.1 / 2.5 (Q2 FY26 ... Q2 FY27). Columns sum to 99.9-100.2 (rounding).

## 3. Checks run (precision rules)

- Letter vs handbook, Q2 FY27: Stocks ADTO 14,430 vs 14,429.97; Eq-deriv premium ADTO 12,322 vs 12,322.43; MTF book 4,351 vs 4,351.4. Pass.
- Orders across handbook vintages: Q1 FY27 56.023 (Jul handbook) vs 56.0156 (Oct); Q4 FY26 58.743 vs 58.739; Q2 FY26 415.764 Mn vs 415.707 Mn. Max drift 0.02%: orders are lightly restated each quarter; use the latest handbook.
- Total income Q2 FY27: letter chart Rs1,541 Cr vs results p7 1,540.54. Pass.
- NSE Active Clients cross-check vs NSE Report 1C: Q4 FY26 handbook 12.939 Mn = FY26 workbook 12,939,127. Q1 FY27 1.305 Cr ties to third-party report of 13,053,752 (June). Sep-26 workbook: 13,448,194 / 46,120,857 total = 29.16%. Pass.
- Segment-orders-sum-to-total and F&O + cash + commodity mix = broking share: not testable (no segment orders; broking is not a separate mix line).
- Q2 FY26 results PDF has no text layer; its figures were not read from it (comparatives taken from the Q2 FY27 results/handbook: revenue 1,018.74, total income 1,070.80 Cr). OCR not available here.
- The company's "AI Earnings Pack" md (IR site) cites the Q2 FY27 revenue mix on PDF p5; the mix chart is actually on PDF p6 (printed page 04). I used p6.

## 4. Not disclosed by Groww (vs Angel One) and monthly alternatives

Angel One gives monthly: orders by segment, market shares, client base. Groww gives **none of these monthly**.

- No monthly business update of any kind (Q2 FY27 transcript p10: CFO only said August was the lowest month of the quarter).
- No orders by segment (only total), no segment revenue (single reportable segment), no revenue in Rs by product (only % of total income), no brokerage-only revenue line, no client count by segment in the filings (NSE active clients only up to Q1 FY27; Groww dropped it in Q2 FY27).
- Mix is % of total income, and the classification changed in Q2 FY27 (Treasury -> Other income; IPO and BSDA revenue from Stocks -> Other operating income; delayed payment charges -> Float), so older letters' mix is not comparable; use the Q2 FY27 restated 5-quarter set.
- No ARPU/take-rate table; only the commentary points above.

Monthly-or-better series that can stand in:
1. **NSE Report 1C (active clients by member, monthly).** `https://nsearchives.nseindia.com/miscellaneous/ArbitrationReports/isc_report1C_<FY>.xls` (FY26: `2526`, FY27: `2627`). Fetched OK with a browser UA and NSE cookie. Row "Groww Invest Tech Private Limited" (col J "NO. OF ACTIVE CLIENTS" in the FY27 layout; col D "UCC OF ACTIVE CLIENTS" in FY24-FY26 files); Angel One is in the same sheet. Updated about the 7th of the following month ("Last Updated on 30-September-2026", saved 2026-10-07). **The file is overwritten in place with one sheet, so history must be archived by us each month**; the FY files only hold the year-end figure (FY26 12,939,127; FY25 12,921,210; FY24 9,544,603). The NSE page is `nseindia.com/invest/arbitration-status` (JS app; the xls link is not in the HTML, found via a third-party tracker). Third-party trackers (onetradejournal.com, entrackr, Inc42, Outlook Business) publish monthly series back to 2025; unverified secondary.
2. **Groww IR home page live metrics** (`groww.in/investor-relations`, plain HTTPS GET, no auth, 35 s cache). Gives QTD Stocks turnover, Equity-derivative premium turnover, Commodity notional turnover, MTF net book, transacting users, assets, SIP inflows as of today, plus quarterly history. Not monthly natively, but a month-end snapshot job gives monthly turnover by differencing QTD values (turnover only; **no orders**, so ADR-by-order needs orders/day derived from quarterly orders). Platform-level figures; users and assets exclude W/Fisdom.
3. NSE/BSE exchange-wide ADTO by segment (not Groww-specific): use with Groww's quarterly market share to interpolate months. Not tested here.

Net: a monthly orders series for Groww is not obtainable. Best proxy for monthly ADR: quarterly orders (handbook) x monthly turnover shape (IR widget snapshots) x per-order yield assumptions (Rs20 F&O/commodity, ~Rs15-16 cash), with NSE Report 1C as the monthly client-base series.
