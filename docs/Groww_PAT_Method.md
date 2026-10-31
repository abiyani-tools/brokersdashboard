# Groww PAT Predictor: how `Groww - ADR Model` turns ADR into PAT, EPS and a target price

**Purpose:** spec for the dashboard's Groww "PAT Predictor" tab. With the sheet's own inputs the tab must reproduce the sheet's cached numbers; the fixture is `out/groww/pat_expected.json`.

**Basis:** `20260714_brokers dashboard v2.xlsx` (read from a copy, openpyxl, formulas and cached values loaded separately). I rebuilt the whole valuation chain in Python from the inputs below and matched every output cell (FY27 and FY28, Bear/Base/Bull, 45 cells) with **max difference 0.0**. Indian FY: FY27 = Apr 2026 to Mar 2027. ADR and revenue in Rs Cr (ADR per trading day). Sheet cell refs are on `Groww - ADR Model` unless a sheet is named.

**What the sheet is.** It is the Angel One `Angel One - ADR model` sheet cloned for Groww (same layout, one extra header row), with the ADR cells repointed to Groww and the other feeds only partly repointed (Issue 1). It is visible, has no dependents anywhere in the workbook, and `B2` is `#VALUE!` (an Excel stock data-type cell that supplies `D2` and `E2`).

---

## 1. The calculation chain

There is **no EPS row and no PAT-margin input**. PAT comes from an explicit income-minus-costs build, and EPS is only implied inside the price formulas (`C28 = C26*C23/$D$2`). The valuation has two horizons: **FY27** (rows 15 to 30) and **FY28** (rows 32 to 53). The headline is the **FY28 "Target price today"** (`C52:E52`) and its upside (`C53:E53`).

Scenario columns: `C` = Bear, `D` = Base, `E` = Bull. The scenarios differ **only in P/E** (38 / 44 / 50). Every other cell in `D` and `E` is `=C` or `=D` of the cell to its left (e.g. `D15 = C15`, `E15 = D15`).

### 1.1 ADR block (rows 4 to 10)

| Cell | Formula | Meaning |
|---|---|---|
| `C8` | `='Groww - Final '!D58` = `D14` = last numeric of `'Groww charts'!AG` / 10 | Broking ADR "45 Day" (A). **Really a 36-trading-day average** (Issue 3) |
| `D8` | `='Groww - Final '!D89` = average of the last 45 rows of `'Groww charts'!AD` (daily MTF revenue, Rs Cr, **gross**) | MTF ADR 45-day (B) |
| `E8` | `=D8+C8` | Total ADR 45-day (A+B) = **17.9887** |
| `C9`, `D9`, `E9` | same pattern: `'Groww - Final '!D59` (last of `AF`/10, **really 15 days**) and `D90` (true last 20 days), sum | 20-day ADR: Broking 16.6441, MTF 2.5826, total 19.2267 |
| `C10`, `D10`, `E10` | `D60` (true last 5 days of `AE`/10) and `D91`, sum | 5-day ADR: 15.7076, 2.5990, 18.3066. **Not used downstream** |

`'Groww charts'!AE` is daily Broking ADR (F&O + Cash + Commodities, Rs Mn) and the series ends **24 Sep 2026** (row 218). The sheet is therefore as of 24 Sep, not 21 Oct like the published Summary.

### 1.2 FY27 block (rows 15 to 30), all three scenarios identical until the P/E

1. **Operating ADR** `C15 = E8` (the **45-day** total A+B; `D15=C15`, `E15=D15`). = 17.9887.
2. **Trading days** `C16:E16` = 247 (typed in each cell).
3. **Operating revenue** `C17 = C16*C15` = 247 x 17.9887 = **4,443.22**.
4. **Treasury income** `C18 = 'PAT predictor Q2FY27'!AC48` = **1,149.81** (Groww "Other interest income", FY27E; Appendix A).
5. **Other income** `C19 = 'Angel One - Final'!E100 + E101` = **371.66**. These are Angel One's depository and distribution income, not Groww's (Issue 1).
6. **Total income (less MTF interest)** `C20 = C19 + C17 + C18` = **5,964.68**.
7. **Total costs** `C21 = 'PAT predictor Q2FY27'!AC63 - AC59` = 2,370.20 - 40.34 = **2,329.85** (FY27E total expenses **excluding finance cost**; Appendix B).
8. **PAT** `C23 = (C20 - C21) * 0.75` = **2,726.12** (25% tax typed inside the formula). Margin `C24 = C23/C20` = 45.70%.
9. **EPS (implied)** = `C23 / D2` = 2,726.12 / 621.0962 = **4.3892**.
10. **P/E** `C26:E26` = 38 / 44 / 50.
11. **1-year-forward price** `C28 = C26*C23/$D$2` (= P/E x EPS): 166.79 / **193.13** / 219.46.
12. **Discounted** `C29 = C28/(1+$G$29)`, `G29 = 18%`: 141.35 / **163.67** / 185.98.
13. **Upside** `C30 = C29/$E$2 - 1`, `E2` = CMP 181.52: -22.1% / **-9.8%** / +2.5%.

### 1.3 FY28 ADR bridge (rows 32 to 33)

- `C32 = 27%`, `D32 = 50%` (typed). They sit in the Bear and Base columns but are **not scenarios**: `C32` grows Broking and `D32` grows MTF.
- `C33 = (1+C32)*C9` = 1.27 x 16.6441 = **21.1380** (Broking, grown off the **20-day** ADR).
- `D33 = (1+D32)*D9` = 1.50 x 2.5826 = **3.8739** (MTF, off the 20-day ADR).
- `E33 = D33 + C33` = **25.0119** (FY28 total ADR).

### 1.4 FY28 block (rows 35 to 53)

1. `C37 = E33` (`D37=C37`, `E37=D37`) = 25.0119. `C38 = C16` = 247.
2. **Operating revenue** `C39 = C38*C37` = **6,177.93**.
3. **Treasury** `C40 = C18*(1+15%)` = **1,322.28** (15% typed inside the formula).
4. **Other income** `C41 = 'Angel One - Final'!D131 + D132` = **420.31** (Angel One again).
5. **Total income** `C42 = C41 + C39 + C40` = **7,920.52**.
6. **Total costs** `C43 = 'PAT predictor Q2FY27'!AF63` = **2,905.55** (**includes** finance cost 226.21; Appendix B).
7. **PAT** `C45 = (C42 - C43) * 0.75` = **3,761.23**. Margin `C46` = 47.49%.
8. **EPS (implied)** = `C45 / D2` = **6.0558**.
9. **P/E** `C48 = C26` (38 / 44 / 50).
10. **FY28 price** `C50 = C48*C45/$D$2`: 230.12 / **266.46** / 302.79.
11. **Discounted @ 18%** `C51 = C50/(1+$G$51)`, `G51 = 18%`: 195.02 / 225.81 / 256.60.
12. **Target price today** `C52 = C51/(1+$G$52)`, `G52 = 10%`: **177.29 / 205.28 / 233.27**.
13. **Upside** `C53 = C52/$E$2 - 1`: **-2.3% / +13.1% / +28.5%**.

So FY28 is discounted **twice**, 18% then 10% (a combined factor of 1.298), against one 18% step in the FY27 block.

### 1.5 Memo cells (feed nothing)

`I4:K4` trading days 246 / 249 / 247 (typed); `K6 = 12.05` (typed, FY26 Broking ADR); `I7 = 'PAT predictor Q2FY27'!C120` = (282.1 - 136.7)/246 = 0.5911 (**Angel One's FY24 MTF ADR**); `J7`, `K7` = `AVERAGEIFS('MTF data (2)'!L, E, "FY 2025"/"FY 2026")` = 0.4809 / 0.9852; `K8 = K6+K7` = 13.0352; `L7 = K7/J7-1` = 104.9%; `M7 = RRI(2,I7,K7)` = 29.1%; `C57 = 0.28806` (typed "45 DMA vs Price R square"); `G15 = 0`. None of these reaches PAT, EPS or the target.

### 1.6 Reference implementation (matches the sheet to 0.0)

```
adr27 = C8 + D8                       # 45-day Broking + MTF
for pe in (C26, D26, E26):
    pat27 = (days*adr27 + C18 + C19 - C21) * 0.75
    eps27 = pat27 / D2;  price27 = pe*eps27;  disc27 = price27/(1+G29);  up27 = disc27/E2 - 1
    adr28 = (1+C32)*C9 + (1+D32)*D9   # 20-day
    pat28 = (days*adr28 + C18*1.15 + C41 - C43) * 0.75
    eps28 = pat28 / D2;  price28 = pe*eps28
    tp = price28/(1+G51)/(1+G52);  up28 = tp/E2 - 1
```

---

## 2. Inputs

Type: **(a)** ADR / Summary value from the published Groww run; **(b)** a Groww figure or aggregate we may already have; **(c)** a typed assumption. "Source" says where it comes from in the workbook; `[SOURCE NEEDED]` means the workbook has no source (a typed number, or a live Excel field). Fixture values are in `pat_expected.json`.

### 2.1 (a) ADR from the published run (4 core + 5 memo or unused)

The published Summary column is **Val (In Cr)**, Week table. Parity-run values as of the 21 Oct 2026 data (from `out/groww/summary_expected.json`) are in the last column; the workbook's own values are older (series ends 24 Sep).

| Cell | Label | Workbook | Unit | Published Summary cell (panel, period) | Parity run | Source in workbook |
|---|---|---|---|---|---|---|
| `C8` | Broking ADR 45-day | 15.4793 | Rs Cr/day | `SUMMARY - Groww!M25`, **Broking** panel, "last 45 trading days" | 15.3652 | `'Groww - Final '!D58` <- `'Groww charts'!AG` /10 |
| `D8` | MTF ADR 45-day | 2.5094 | Rs Cr/day | `SUMMARY - Groww!C52`, **MTF (gross)** panel, "last 45 trading days" | 2.6550 | `'Groww - Final '!D89` <- `'Groww charts'!AD` |
| `C9` | Broking ADR 20-day | 16.6441 | Rs Cr/day | `SUMMARY - Groww!M26`, Broking, "last 20 trading days" | 15.1985 | `'Groww - Final '!D59` |
| `D9` | MTF ADR 20-day | 2.5826 | Rs Cr/day | `SUMMARY - Groww!C53`, MTF, "last 20 trading days" | 2.7876 | `'Groww - Final '!D90` |
| `C10` | Broking ADR 5-day (unused) | 15.7076 | Rs Cr/day | `M23`, Broking, "Last 5 Trading Days" | 14.4506 | `'Groww - Final '!D60` |
| `D10` | MTF ADR 5-day (unused) | 2.5990 | Rs Cr/day | `C50`, MTF, "Last 5 Trading Days" | 2.8856 | `'Groww - Final '!D91` |
| `K6` | Broking ADR FY26 (memo) | 12.05 | Rs Cr/day | `M9`, Broking, FY 2026 (12.0549) | 12.0549 | typed |
| `K7` | MTF ADR FY26 (memo) | 0.9852 | Rs Cr/day | `C36`, MTF, FY 2026 | 0.9852 | `AVERAGEIFS('MTF data (2)'!L)` |
| `J7` | MTF ADR FY25 (memo) | 0.4809 | Rs Cr/day | **not published** (MTF panel shows FY 2027 and FY 2026 only) | n/a | `AVERAGEIFS('MTF data (2)'!L)` |

The consolidated 45-day ADR on the Summary (`C24`, 18.0202) equals Broking + MTF (15.3652 + 2.6550), the same A+B the sheet builds in `E8`. The dashboard takes MTF **gross**; the engine's separate "MTF (net)" panel is not used (Section 4).

### 2.2 (b) Groww figures / aggregates (6)

| Cell | Label | Value | Unit | What it is | Source / match with `groww_facts_reviewed_2026-10-31.json` |
|---|---|---|---|---|---|
| `D2` | Shares outstanding | 621.0962 | crore shares (6,210,962,000 / 10^7) | live Excel Stocks field `_FV(B2,"Shares outstanding")` | `[SOURCE NEEDED]`; **no shares fact** in the reviewed JSON |
| `C18` | FY27 Treasury (other interest) income | 1,149.8082 | Rs Cr | = Q1 FY27 actual 275.451 + Q2E 290 + Q3E 291.45 + Q4E 292.907 (Appendix A) | Partly: Q1 FY27 uses mix % x revenue (8.1% float + 5.5% PL+LAS + 3.0% treasury + 2.1% other) x 14,730 Mn. Facts (restated mix, share of total income 15,486.7 Mn): float 8.4%, PL+LAS 5.5%, other income 3.1%, other operating 2.1% = 19.1% = 2,958 Mn vs 2,754.5 Mn in the sheet (+7%, restated classification and different base). Q2 FY27 **actual** (float 8.4% + PL+LAS 5.9% + other income 2.5% + other operating 4.8% of 15,405.4 Mn = 3,328 Mn = 332.8 Cr) is above the typed Q2E 290. `[SOURCE NEEDED]` for the Q2E-Q4E path |
| `C19` | FY27 Other income | 371.658 | Rs Cr | **Angel One** depository + distribution (bug, Issue 1) | Wrong entity. Groww's own distribution (Fisdom/AMC) is `'PAT predictor Q2FY27'!AC44` = 327.57; Q1 FY27 76 Cr = facts `total_income` 15,486.7 minus `platform_revenue_ex_fisdom_amc` 14,727.2 = 759.5 Mn (matches 760) |
| `C21` | FY27 total costs ex finance cost | 2,329.8525 | Rs Cr | Q1 FY27 actual + Q2-Q4E (Appendix B) | Q1 FY27 lines are typed in `'Working sheet - Groww'!L107:L110` (finance 73.1, employee 1,820, depreciation 176.3, other 3,487.4 Mn). **No cost facts** in the reviewed JSON: `[SOURCE NEEDED]` |
| `C41` | FY28 Other income | 420.3099 | Rs Cr | **Angel One** `'Angel One - Final'!D131+D132` (bug) | as `C19`. Groww's own FY28 distribution is `'Groww - Final '!E132` = 506.15 |
| `C43` | FY28 total costs incl finance cost | 2,905.5452 | Rs Cr | FY27 lines x 1.15 plus a finance cost build (Appendix B) | `[SOURCE NEEDED]` |

Other Groww facts available but **not used by this sheet**: Q2 FY27 actual total income 15,405.4 Mn and H1 FY27 actual 30,892.1 Mn = 3,089 Cr (already 51.8% of the sheet's FY27 total income 5,964.7), MTF book 43,514 Mn, trading days 65 (matches the workbook's `E27`). The sheet has **no Q2 FY27 actuals** (Issue 2).

### 2.3 (c) Typed assumptions (all `[SOURCE NEEDED]`; the workbook gives no source or rationale)

| Cell | Label | Value | Unit |
|---|---|---|---|
| `C16`, `D16`, `E16` | Trading days FY27 (and FY28, `C38 = C16`) | 247, 247, 247 | days (three separate typed cells) |
| `C26`, `D26`, `E26` | P/E Bear / Base / Bull | 38 / 44 / 50 | x |
| `G29` | Discount rate, FY27 price to today | 18% | fraction |
| `C32` | FY28 growth on Broking 20-day ADR | 27% | fraction |
| `D32` | FY28 growth on MTF 20-day ADR | 50% | fraction |
| `G51` | Discount rate, FY28 price to FY27-end | 18% | fraction |
| `G52` | Discount rate, FY27-end to today | 10% | fraction |
| `E2` | **CMP** | 181.52 | Rs/share |
| inside `C23:E23`, `C45:E45` | Retention after tax = 1 - 25% | 0.75 | fraction |
| inside `C40` | FY28 treasury growth over FY27 | 15% | fraction |

`E2` is the live Excel Stocks price at the last save (the typed price series in `'Groww charts'!C` ends 2 Sep 2026 at 189.88). The dashboard needs a live CMP. Unused typed cells: `I4:K4`, `K6`, `C57` (R-square 0.28806), `G15` (0).

**Input counts.** On the sheet: **(a) 4 core ADR cells** (`C8`, `D8`, `C9`, `D9`) plus 5 memo or unused ADR cells; **(b) 6** (`D2`, `C18`, `C19`, `C21`, `C41`, `C43`); **(c) 13 cells** (3 days, 3 P/E, `G29`, `G51`, `G52`, `C32`, `D32`, `E2`) **plus 2 constants hidden in formulas** (0.75 and 15%), plus 5 unused typed cells. `pat_expected.json` carries 35 input entries (all of the above), 85 sheet output entries (every formula cell plus 6 derived EPS values) and 31 `layer: "upstream"` entries (Appendix A and B feeders, for dashboards that rebuild C18, C21, C43 rather than freeze them).

---

## 3. Scenarios and sensitivity

- **Bear / Base / Bull** (`C:E`, rows 14 to 53): **only the P/E changes** (38 / 44 / 50). ADR, days, treasury, other income, costs, growth and discount rates are the same in all three. PAT and EPS are therefore identical across scenarios, and target price scales linearly with P/E.
- **Two horizons:** FY27 (1-year-forward, one 18% discount) and FY28 (18% then 10%).
- **No sensitivity grid.** There is no P/E x ADR table in the sheet. Only the three scenarios and the 5/20/45-day ADR reference rows exist.
- The sheet's PE series (`PE chart - Groww`, hidden) is **not linked**: 59 typed TTM P/E points (12 Nov 2025 to 4 Feb 2026), average 65.8x, -1SD 61.5x, last 69.9x. The typed 38 / 44 / 50 are 22 to 30 turns below it.

**Fixture 1 (workbook inputs):** the table below, also in `pat_expected.json`.

| | Bear | Base | Bull |
|---|---|---|---|
| FY27 PAT (Rs Cr) / EPS (Rs) | 2,726.12 / 4.389 | 2,726.12 / 4.389 | 2,726.12 / 4.389 |
| FY27 discounted price / upside | 141.35 / -22.1% | 163.67 / -9.8% | 185.98 / +2.5% |
| FY28 PAT (Rs Cr) / EPS (Rs) | 3,761.23 / 6.056 | 3,761.23 / 6.056 | 3,761.23 / 6.056 |
| FY28 price / **target today** | 230.12 / **177.29** | 266.46 / **205.28** | 302.79 / **233.27** |
| **Upside vs CMP 181.52** | **-2.3%** | **+13.1%** | **+28.5%** |

**Fixture 2 (computed by me, not a workbook value): same sheet inputs but ADR from the published parity run** (`C8 = 15.3652`, `D8 = 2.6550`, `C9 = 15.1985`, `D9 = 2.7876`). FY27 ADR 18.0202, PAT 2,731.96, EPS 4.399, FY27 discounted price 164.02 (Base), upside -9.6%. FY28 ADR 23.4836, PAT 3,478.12, EPS 5.600, **target 163.94 / 189.83 / 215.72**, **upside -9.7% / +4.6% / +18.8%**. The Base FY28 target is 7.5% below the sheet's 205.28 purely from the ADR basis (the FY28 bridge compounds the 20-day Broking ADR, which drops from 16.64 to 15.20).

---

## 4. Differences from Angel One's PAT logic

Angel's dashboard tab follows the workbook's `PAT` sheet (column E): `E4` revenue/day (Summary 45-day Broking) x `E5` days (249) = broking revenue; `E7` "other revenue" typed from the predictor; PAT = margin (`E10`, from the predictor) x total revenue; EPS = PAT / 91; P/E 22.5; target = P/E x EPS / 1.18; upside vs CMP. One horizon, no scenarios.

| Topic | Angel One (`PAT` col E) | Groww (`Groww - ADR Model`) |
|---|---|---|
| Source sheet | `PAT` | `Groww - ADR Model` (the Angel ADR-model clone) |
| ADR input | Broking 45-day only (`SUMMARY - Brokers!M80`, 15.37) | Broking **and** MTF 45-day and 20-day (4 values), summed as A+B |
| MTF | inside "other revenue" (typed) | **MTF is part of the operating ADR** (gross MTF ADR, `D8`) |
| Other revenue | typed block: MTF + other interest + distribution + depository | Two typed blocks: **Treasury** (`C18`, float + PL+LAS + treasury + other) and **Other income** (`C19`, distribution/wealth, currently Angel's number) |
| Non-broking lines | Depository, distribution, MTF, other interest | **No depository.** Distribution = Fisdom/AMC ("Wealth"); float, PL+LAS, treasury and other income are rolled into one "Other interest income" |
| PAT | margin x revenue (margin typed from the predictor, ~19%) | **(total income - costs) x 0.75**; costs are explicit lines (Appendix B) so the margin is an output (45.7% FY27, 47.5% FY28) |
| EPS | PAT / 91 (typed, `E12`) | PAT / **621.0962 crore shares** (live Excel field, `D2`); not shown in the sheet |
| P/E, discount | 22.5x, 18%, one step | 38 / 44 / 50x scenarios; FY27 18% one step; FY28 18% then 10% |
| Horizon | FY27 | FY27 and FY28 (FY28 is the headline) |
| ADR basis | published Summary 45-day | parity workbook ADR, with a truncated 36-day "45 DMA" (Issue 3) |
| Gross vs net MTF | Angel's sheet uses **net** MTF ADR (`'MTF data (2)'!P`, "B - C") and strips finance cost out of costs | Groww's `'MTF data (2)'!L` is **gross**, but costs still strip finance cost in FY27 (the Angel treatment), so MTF funding cost drops out of FY27 (Issue 4) |

---

## 5. Issues

Ranked by impact on the target price.

1. **"Other Income" is Angel One's, not Groww's (`C19`, `C41`).** `C19 = 'Angel One - Final'!E100+E101` is Angel One's depository (4 x 43.011) plus distribution (43.011 growing 10% per quarter): 3% each of Angel's Q1 FY27 base of 14,337 Mn (`'Working sheet - Angel One'!M99`). `C41 = 'Angel One - Final'!D131+D132` applies Angel's 15% / 20% growth rates. Groww has no depository income. Its own distribution (Fisdom/AMC) is 327.57 for FY27 (`'PAT predictor Q2FY27'!AC44`) and 506.15 for FY28 (`'Groww - Final '!E132`). Swapping them in (my calculation) moves Base FY27 PAT from 2,726.12 to 2,693.06 and FY28 PAT from 3,761.23 to 3,825.62, taking the Base FY28 target from 205.28 to 208.80. The dashboard should show Groww's own line and flag the sheet value. It is also a hidden coupling: any change to Angel One's inputs moves Groww's valuation.
2. **FY27 uses estimates for the quarters already reported.** Q1 FY27 is actual; Q2 FY27 onward are estimates (treasury Q2E typed 290, costs rolled from Q4 FY26 x 1.1), although Q2 FY27 actuals exist (total income 15,405.4 Mn). H1 FY27 actual total income is 3,089 Cr, already 51.8% of the sheet's FY27 total income 5,964.7 (which also omits Groww's own distribution).
3. **ADR as-of date and windows.** `'Groww charts'!AE:AG` end **24 Sep 2026**; the published Summary runs to 21 Oct (Broking) and 19 Oct (MTF). The "45 DMA" `AG218` is `AVERAGE(AE183:AE218)` = **36 rows**, and the "20 DMA" `AF218` is `AVERAGE(AE204:AE218)` = **15 rows** (windows shrink near the end of the sheet). The MTF 45/20-day cells use true 45/20 rows. So `C8`, `C9` are not 45- and 20-day averages, and the sheet is not like-for-like with the dashboard's published 45-day figure (Fixture 2: Base FY28 target 189.83 instead of 205.28).
4. **MTF treatment is inconsistent between FY27 and FY28.** MTF revenue is gross (`D8`, 14.95% x book). FY27 costs `C21 = AC63 - AC59` remove finance cost (copied from Angel, where MTF is net), so about 40.3 Cr of funding cost is dropped; including it cuts Base FY27 PAT from 2,726.12 to 2,695.86. FY28 costs `C43 = AF63` **include** finance cost 226.21. The label "Total Income (less MTF interest)" is Angel's and does not apply.
5. **FY28 ADR bridge compounds the 20-day ADR, FY27 uses the 45-day.** `C33 = (1+C32)*C9` (Angel's sheet uses `C8`). FY28 ADR 25.01 vs FY27 17.99 is +39%. Growth rates 27% / 50% are typed with no source. The cells sit under "Bear"/"Base" headings but are Broking/MTF growth.
6. **FY28 costs are not tied to the sheet's FY28 ADR.** `C43 = AF63`: cost lines are FY27 x (1 + 15%, typed `AG60:AG62`); finance cost `AF59 = AF74*8.5% + AC59`, driven by `'Groww - Final '!E133` (FY28 MTF income 983.37 = 1.5 x the MTF-data FY27 total), not by this sheet's FY28 MTF revenue (3.8739 x 247 = 956.9). Rates in the chain differ: 8.5% (`AF59`), 8% (`Y77:AB77`), 14.99% (`AF70`, `AC70`), 15% (`'MTF data'!H59`), 14.95% (ADR engine). Excluding finance cost in FY28 as in FY27 would lift the Base FY28 target to 214.54.
7. **Discount rates differ from `Groww - Final`.** `Groww - Final ` discounts FY27 at 13.5% (`G119`) and FY28 at 18% then 13.5% (`I150`, `I151`); this sheet uses 18% (FY27) and 18% then 10% (FY28). Same P/E 44, similar PAT, but targets of 205.28 (this sheet) vs 187.25 (`Groww - Final !E151`). `E6` of `Groww - Final ` is labelled "ADR Model" but is its own FY27 Base target (174.90, -3.6%), not this sheet. The workbook holds three Groww PAT numbers for FY27: **2,726.12** (this sheet), **2,802.08** (`Groww - Final !E112`) and **3,007.85** (`'PAT predictor Q2FY27'!AC51`).
8. **CMP and shares are live Excel fields, stale in the file.** `E2 = 181.52` and `D2 = 621.0962` come from `_FV(B2,...)`. The cached price has no date, and the typed price series ends 2 Sep 2026. The dashboard needs its own live CMP and share count `[SOURCE NEEDED]`. Upside is only meaningful against a fresh CMP.
9. **Typed P/E with no link to history.** 38 / 44 / 50 vs the hidden `PE chart - Groww` average of 65.8x (stale, ends 4 Feb 2026) and `Groww - comparables` (text only, no numbers used).
10. **Hardcodes inside formulas:** 0.75 (tax), 15% (`C40`). The three trading-day cells (`C16:E16`) are typed separately; `C38:E38` link to them. `G29` and `G51` are separate cells that both hold 18%.
11. **Wrong-entity memo cells.** `I7` (FY24 MTF ADR 0.5911) and `M7` (CAGR 29.1%) come from Angel One's `'PAT predictor Q2FY27'!C118:C120`; `K6` is a rounded typed 12.05 (Summary 12.0549); `J7` (FY25) is not in the published Summary. The "FY24 MTF ADR" does not exist for Groww. Do not show these on the tab.
12. **Label noise.** `B2` is `#VALUE!`; `H7` says "MTF ADR (B-C)" for a gross MTF ADR; "Bear/Base/Bull" over ADR rows implies ADR scenarios that do not exist; there is no EPS row.

### Dashboard notes (for the builder)

- Compute EPS as PAT / shares and show it; the sheet has none.
- Treat `C18`, `C21`, `C43`, `D2`, `E2` and the typed block as labelled assumptions with their workbook cell. `C19` and `C41` should be shown as Groww's own distribution (or as an assumption flagged as the sheet's Angel One value) with the sheet value kept for parity.
- Keep `G29`, `G51`, `G52` as three separate inputs; keep the 20-day and 45-day ADRs as separate inputs (FY27 = 45-day, FY28 = 20-day).
- Parity check: with the workbook inputs, FY28 Base target 205.28 and upside +13.09% (Fixture 1). With the live ADR the numbers move (Fixture 2); say so on the tab.

---

## Appendix A: Treasury income `C18 = 'PAT predictor Q2FY27'!AC48`

`AC48 = SUM(Y48:AB48)` = 275.451 + 290.000 + 291.450 + 292.907 = **1,149.808** (Rs Cr). "Other interest income" in this workbook is Groww's float + PL+LAS + treasury + other income lines.

| Quarter | Cell | Formula | Value | Note |
|---|---|---|---|---|
| Q1 FY27 (actual) | `Y48` = `'PAT predictor Q1FY27'!Z10` = `'Working sheet - Groww'!L32/10` | (`L20` float 8.1% + `L21` PL+LAS 5.5% + `L23` treasury 3.0% + `L25` other 2.1%) x `L120` 14,730 Mn | 275.451 | mix % typed (`L10`, `L11`, `L13`, `L14`), revenue typed |
| Q2 FY27E | `Z48 = M36` | typed | 290 | no source |
| Q3 FY27E | `AA48` | `Z48 + (AA42-Z42)/Z42 * Z48` | 291.45 | grows with broking revenue (0.5%/qtr, typed `AG9`) |
| Q4 FY27E | `AB48` | same | 292.907 | |

Broking revenue path (`Z42 = M30` = 1,055.15 Q2E, from daily `backtesting` sheets x days-in-quarter, then x 1.005 per quarter) only drives the growth step; it does not use this sheet's ADR.

## Appendix B: Costs

`C21 = AC63 - AC59` (ex finance), `C43 = AF63`. All in Rs Cr.

| Line | Q1 FY27 actual (`Y`) | Q2-Q4 FY27E rule | FY27E (`AC`) | FY28E (`AF`) |
|---|---|---|---|---|
| Finance cost | 7.31 (`'Working sheet - Groww'!L107/10`) | Q2 = Y + extra-capital x 8%/4, then rolling (`Y77:AB77`) | 40.344 (**removed** in `C21`) | 226.215 = `AF74*8.5% + AC59` |
| Employee | 182.0 | Q2 = Q4 FY26 173.4 x 1.1 = 190.74, flat | 754.22 | 867.353 (`AC60 x 1.15`, typed `AG60`) |
| Depreciation | 17.63 | Q2 = Q4 FY26 24.455 x 1.1 = 26.90, flat | 98.3315 | 113.081 (x 1.15) |
| Other expenses | 348.74 | `Z62 = (AC62 - Y62)/3`, `AC62 = X62 x 1.13` (FY26 sum 1,307.346 x 1.13) | 1,477.301 | 1,698.896 (x 1.15) |
| **Total** | 555.68 | | **2,370.196** (ex finance 2,329.852) | **2,905.545** |

`AF74` = extra MTF capital = `AF70 - AC70` = 6,560.15 - 4,373.44 = 2,186.72, where `AF70 = AF46/14.99%`, `AC70 = AC46/14.99%`, `AF46 = 'Groww - Final '!E133` = 983.367 and `AC46` = 655.578 (Q1 117.84 + `'MTF data'!E64` 158.87 + `D70` 178.29 + `D71` 200.58). `MTF data` rows use typed industry MTF book points (`E29:E43`), a 38% growth (`B61`) and Groww shares of 3.2% / 3.6% (`J59`, `J60`) at 15% (`H59`, `H60`).
