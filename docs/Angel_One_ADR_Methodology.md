# Angel One — ADR Methodology & Logic Spec (v1)

**Purpose:** a written-down, code-ready version of the Angel One ADR (average daily revenue) logic in `20260714_brokers dashboard v2.xlsx`. Use it to build the online Brokers Dashboard in Claude Code. The first screen should reproduce the sheet **`SUMMARY - Angel One`**.

**Basis:** the workbook as saved (daily data runs to **21 Oct 2026**), plus `Data inputs for Broker.docx`. Every number below comes from a cell in the workbook (sheet!cell). I recomputed each derived number from its inputs in Python, and they all match the workbook's cached values unless a difference is flagged.

**Conventions:** Indian FY (Apr–Mar; "FY 2027" = Apr-2026 to Mar-2027). Rs crore (Cr) for ADR. Rs million (Mn) inside the daily sheets (÷10 → Cr). Orders and contracts are in millions (Mn) unless stated.

---

## 0. The idea in one paragraph

Angel One does not publish daily revenue. The model rebuilds it from three things:

1. **Daily exchange activity**: F&O contracts, cash trades, MCX contracts and the industry MTF book.
2. **Calibration ratios** from Angel's own monthly and quarterly disclosures: orders, market share, revenue mix and funding book.
3. **Revenue per order ("take rate")** for each segment and quarter.

For each segment: **daily Angel orders = daily market activity × Angel share ÷ (activity per order)**, then **daily revenue = daily Angel orders × take rate**. MTF works the same way: **Angel book = share × industry book**, then **revenue = book × yield ÷ trading days**. The ADR for a period is the simple average of daily revenue over the trading days in that period.

**Two regimes. Knowing which one applies matters for the code.**

| Regime | When | What the model really does |
|---|---|---|
| **Calibrated (actual)** | Angel has reported orders for that month (F&O, commodities) or quarter (cash, MTF) | The market-share term cancels. Daily orders are simply **reported orders for the period spread across days in proportion to exchange volume**. Quarterly sums tie to reported revenue by construction. |
| **Estimate** | Period not yet reported by Angel | Market share, activity per order and take rate come from **assumption rules** (carry forward or trailing averages, §6). This is where the tracker earns its keep, and where errors live. |

---

## 1. Output to replicate: `SUMMARY - Angel One`

Three bands of two panels each. Every panel has the same five tables. All values are ADR in Rs Cr.

| Band (rows) | Left panel (cols B–J) | Right panel (cols M–U) |
|---|---|---|
| 3–26 | **Consolidated** = Broking + MTF | **Broking** = F&O + Cash + Commodities |
| 30–53 | **MTF** | **F&O** |
| 56–79 | **Cash** | **Commodities** |

Tables in each panel:

| Table | Rows shown | Comparison columns |
|---|---|---|
| **Financial Year** | Current FY (YTD), previous FY | YoY = cur/prev − 1 |
| **Quarter** | Latest quarter, previous quarter, same quarter last year | QoQ, YoY |
| **Month** | Latest month, previous month, "Avg of last 6 months" | MoM, "Mo 6M" = month / 6-mo avg − 1 |
| **Week** | Last 5 trading days, previous 5 trading days (days 6–10), last 45 trading days, last 20 trading days | WoW = L5/P5 − 1; "Wo 10W" = L5/L45 − 1 |
| **Weekday** (Mon–Fri) | Latest occurrence of that weekday, avg of last 3 such weekdays, avg of last 10 | "Do 3D" = latest/avg3 − 1, "Do 10D" = latest/avg10 − 1 |

**Aggregation formulas (as in Excel):**
- FY / Quarter / Month value = `AVERAGE(daily revenue where period key = X) / 10`. In Excel this is `AVERAGEIFS(...)/10`; the MTF sheet is already in Cr, so it has no /10.
- "Avg of last 6 months" = simple average of the latest two **quarter** ADRs, e.g. `SUMMARY!N19`, `C46`, `C72`, `N72`. It is not day-weighted.
- Last-N-trading-days = average of daily revenue for dates ≥ the N-th largest distinct date in that segment's sheet (`LARGE(unique dates, N)`). Previous 5 = dates between the 10th and 6th largest.
- Weekday = filter distinct dates with `WEEKDAY(date,2)=k`, take the latest 1 / 3 / 10, and average daily revenue on those dates.
- Consolidated and Broking cells are **sums of the segment ADRs**, not averages of summed daily revenue. Example: `SUMMARY!N8 = F&O FY ADR + Cash FY ADR + Commodities FY ADR` and `C7 = N8 + C35 (MTF)`.

**Parity values for testing the build** (workbook as saved):

| ADR, Rs Cr | F&O | Cash | Commodities | **Broking** | MTF (gross) | **Consolidated** |
|---|---|---|---|---|---|---|
| FY 2027 YTD (`N35`,`C61`,`N61`,`N8`,`C35`,`C7`) | 9.2856 | 2.0646 | 1.5371 | **12.8873** | 4.2094 | **17.0967** |
| FY 2026 | 9.5021 | 1.7019 | 1.1629 | **12.3669** | 3.1172 | **15.4841** |
| Q2 FY 2027 | 8.4982 | 1.9655 | 1.5968 | **12.0605** | 4.5012 | **16.5617** |
| FY 2027 September | 8.3943 | 2.0766 | 1.7903 | **12.2612** | 4.7123 | **16.9735** |

Arithmetic check for FY 2027: 9.2856 + 2.0646 + 1.5371 = 12.8873, and 12.8873 + 4.2094 = 17.0967 ✓. Day counts behind FY 2027: F&O 138, Cash 138, Commodities 144 (MCX days), MTF 136 (MTF data ends 19 Oct).

---

## 2. Did the Excel use what the Word doc asks for?

Legend: ✅ captured and used in ADR · ⚠️ captured but not used in ADR (or used differently) · ❌ not captured · ➕ used in Excel but not listed in the doc

### 2a. Exchange data (daily)

| Doc item | Status | Where in Excel | Note |
|---|---|---|---|
| Date, Quarter, Month, FY, Day, Quarter FY, FY Month | ✅ | `backtesting F&O!B:H`, `backtesting cash!B:H` (pulled from the external file `20260121_Exchanges_Dashboard.xlsx`); `Commodities!B:E,M` and `MTF data (2)!B:H` (derived from date by formula) | — |
| NSE Index Options ADTO (premium) | ⚠️ | `backtesting F&O!J` | Not used for Angel (used in the MOSL model) |
| NSE Stock Options ADTO (premium) | ⚠️ | `backtesting F&O!K` | Same |
| BSE Index / Stock Options ADTO (premium) | ⚠️ | `backtesting F&O!M` | One combined BSE options premium figure, not split; not used for Angel |
| NSE Stock Options contracts | ⚠️ | `backtesting F&O!Q` | Pulled, but the Angel ADR uses **NSE total F&O contracts** (`T`, = external `NSE F&O` col U "Total Contracts"), which includes index and stock futures |
| NSE Index Options contracts | ⚠️ | `backtesting F&O!P` | Same as above |
| BSE Stock / Index Options contracts | ✅ (combined) | `backtesting F&O!U` (= external `BSE F&O` col I) | One combined number, not split. **Frozen 29 Sep–21 Oct 2026** (issue #1) |
| NSE Cash ADTO, BSE Cash ADTO | ⚠️ | `backtesting cash!I,J` | Not used in Angel ADR. NSE ADTO row-misaligned from 9 Jun 2025 (issue #11) |
| NSE trades, BSE trades | ✅ | `backtesting cash!L,M` | Drive the cash ADR |
| MCX date fields | ✅ | `Commodities!B:E,M` | — |
| MCX contracts | ✅ | `Commodities!F` | — |
| ➕ NSE index and stock **futures** contracts | ➕ | inside `backtesting F&O!T` | **Add to the doc**, or define the input as "NSE total F&O contracts" |

### 2b. MTF data (daily)

| Doc item | Status | Where | Note |
|---|---|---|---|
| Date fields | ✅ | `MTF data (2)!B:H` | — |
| Total market MTF book | ✅ | `MTF data (2)!I` (Rs Cr, hard-coded daily) | [SOURCE NEEDED: the workbook does not name the source of the daily industry MTF book] |
| ➕ Monthly industry MTF book | ➕ | `MTF data!E12:E44` (rounded figures) | Used as the **denominator of Angel's MTF share** (issue #6) |

### 2c. Angel One — monthly business update

| Doc item | Status | Where | Note |
|---|---|---|---|
| F&O market share (month) | ✅ | `' F&O market'!N4:N23` (Oct-24 → May-26); also `Working sheet - Angel One!D141:D167` (to Jun-26) | Entered twice. Jun-26 onward in the F&O sheet is a placeholder (avg, then carry 0.221) |
| Cash market share (month) | ⚠️ | `Working sheet!E141:E167` | **Not used.** Cash ADR uses the **quarterly** share (`Working sheet!row 40`) |
| Commodity market share (month) | ✅ | `Commodities!AA14:AA42` (to Aug-26) | Sep and Oct carried forward |
| Average client funding book (month) | ⚠️ | `Working sheet!P3:P11` (Apr–Dec 2025 only) | Averaged to quarter; the ADR uses the quarterly book |
| Total number of orders (month) | ✅ | `' F&O market'!C32:C51` (to May-26) and `Working sheet!C141:C167` (to Jun-26) | Entered twice and **3 months disagree** (issue #5) |
| Average daily orders | ❌ | — | Not captured anywhere |
| Quarterly record of the above | ✅ | `Working sheet!rows 39–42` (shares), `rows 6–8` (orders) | — |

Jul–Sep 2026 monthly updates: only the commodity share (Jul 0.48, Aug 0.437, `Commodities!AA41:AA42`) has been entered. Total orders and F&O share for those months are not in the workbook. [SOURCE NEEDED: Angel One monthly business updates Jul, Aug, Sep 2026 — total orders, F&O/cash/commodity share, avg funding book]

### 2d. Angel One — quarterly presentation

| Doc item | Status | Where | Note |
|---|---|---|---|
| Average client funding book | ✅ | `Working sheet!row 31 / 116`, used in `MTF data!P` | — |
| Total number of users | ⚠️ | `Working sheet!J174:J182` (client base) | Not used in ADR |
| Consolidated P&L | ✅ | `Working sheet!rows 94–111` | — |
| Revenue break-up % (F&O, Cash, Commodity, Distribution, …) | ✅ | `Working sheet!rows 15–19` (Interest/Other only for Q1 FY27, `M20:M21`) | Q3–Q4 FY25 entered as (segment % of broking) × (broking % of total), e.g. `F15 = 81%×65%` |
| MTF (from avg funding book), Treasury (interest − MTF) | ✅ | `Working sheet!row 32` (14.99%/4), `row 33` (Q1 FY27 only), `rows 125–126` | Not used by the daily MTF ADR, which uses 14.95%/246 (issue #7) |
| Quarterly market share F&O / Cash / Commodity | ✅ | `Working sheet!rows 39–41` | — |
| No. of orders F&O / Cash / Commodity | ✅ | `Working sheet!rows 6–8`; duplicated in `rows 174–182` | Duplicates disagree (issue #5) |

---

## 3. Shared building block — take rate (revenue per order)

Source: `Working sheet - Angel One`.

```
SegRev_q (Rs Mn)        = RevMix%_seg,q × TotalIncome_q            rows 61–63 = rows 15–17 × row 99
TakeRate_seg,q (Rs/ord) = SegRev_q / Orders_seg,q (Mn)             rows 76–78 = rows 61–63 / rows 6–8
```

| Rs per order | Q3 FY25 | Q4 FY25 | Q1 FY26 | Q2 FY26 | Q3 FY26 | Q4 FY26 | Q1 FY27 |
|---|---|---|---|---|---|---|---|
| F&O (`row 76`) | 21.53 | 21.25 | 21.34 | 21.47 | 21.25 | 21.55 | 21.51 |
| Cash (`row 77`) | 11.08 | 11.85 | 15.24 | 13.20 | 15.74 | 15.33 | 19.26 |
| Commodity (`row 78`) | 25.00 | 25.96 | 25.40 | 24.91 | 22.29 | 20.47 | 21.51 |

Worked example, Q4 FY26 F&O: 0.47 × 14,672.46 = 6,896.06 Rs Mn; ÷ 320 Mn orders = **Rs 21.55/order** ✓ (`K76`).

**Precision note:** the revenue mix % is entered as whole percentages. A ±0.5 pp rounding moves the take rate by about ±1.1% for F&O (45% base), ±5.6% for cash (9%) and ±8.3% for commodities (6%). The jump in the cash take rate to 19.26 in Q1 FY27 (9% mix vs 7% in Q4 FY26) may be partly rounding. Take the cash and commodity take rates as indicative.

---

## 4. Segment logic

### 4.1 F&O broking — sheet `backtesting F&O` (calibrated **monthly**)

**Monthly calibration** (`' F&O market'`):

```
MktContracts_m (Mn)  = Σ NSE total F&O contracts + Σ BSE F&O contracts, for the month   (J,K rows 4–28)
AngelContracts_m     = FOShare_m × MktContracts_m                                       (O = N × J)
FOOrders_m (Mn)      = TotalOrders_m × FO%_q(m)                                         (F32:F51 = E × C)
                       where FO%_q = FO orders_q / Total orders_q  (Working sheet row 10)
CPO_m (contracts/order) = AngelContracts_m / FOOrders_m                                 (H32:H51 = G / F)
```

**Daily** (`backtesting F&O`, from 1 Oct 2024 = row 253 onward):

```
V  MktContracts_d (Mn) = T (NSE total) + U (BSE)
W  CPO_m               = lookup(FY Month → ' F&O market'!H)
X  MktOrders_d         = V / W
Y  FOShare_m           = lookup(FY Month → ' F&O market'!N)
Z  AngelFOOrders_d     = X × Y
AA Rev_d (Rs Mn)       = Z × TakeRate_FO,q   (lookup Q FY → backtesting F&O!AI48:AR57, row "take rate" = row 51)
ADR (Rs Cr)            = AA / 10
```

In the calibrated regime the share cancels: **Z = V_d × FOOrders_m / MktContracts_m**.

**Worked example, 14 May 2026 (row 652, calibrated month):**
- V = 64.913 (NSE) + 590.772 (BSE, an expiry day) = 655.685 Mn contracts
- W = 1,364.327 / 95.064 = 14.3517
  - 1,364.327 = 0.224 × 6,090.747
  - 95.064 = 0.72930 × 130.35
- X = 655.685 / 14.3517 = 45.687
- Z = 45.687 × 0.224 = 10.234 Mn orders
- Check: 655.685 × 95.064 / 6,090.747 = 10.234 ✓
- AA = 10.234 × 21.423 = 219.24 Rs Mn → **Rs 21.92 Cr**
- Monthly check: Σ Z for May-26 = 95.064 = `' F&O market'!F51` ✓

### 4.2 Cash broking — sheet `backtesting cash` (calibrated **quarterly**)

**Quarterly calibration** (`cash market`, quarter-end rows 6, 9, 12, …, 24; lookup table `F34:J43`):

```
MktTrades_q (Mn)   = Σ (NSE + BSE trades) in quarter                     (M)
MktOrders_q        = CashOrders_q / CashShare_q                          (O = N / K)
TPO_q (trades/order) = MktTrades_q / MktOrders_q                         (P)
TakeRate_cash,q    = Working sheet row 77                                (R)
```

**Daily:**

```
N  Trades_d (Mn)   = NSE trades + BSE trades
R  CashOrders_d    = N × CashShare_q / TPO_q
S  Rev_d (Rs Mn)   = R × TakeRate_cash,q
```

Calibrated identity: **R = Trades_d × CashOrders_q / MktTrades_q**.

**Worked example, 14 May 2026 (row 651, Q1 FY27 calibrated):**
- N = 41.040 + 4.423 = 45.462 Mn trades
- TPO = 2,536.789 / (67 / 0.174) = 6.5881
- R = 45.462 × 0.174 / 6.5881 = 1.2007 Mn
- Check: 45.462 × 67 / 2,536.789 = 1.2007 ✓
- S = 1.2007 × 19.2587 = 23.12 Rs Mn → **Rs 2.31 Cr**

### 4.3 Commodities — sheet `Commodities` (calibrated **monthly**)

**Monthly calibration** (`Commodities!U13:AB44`):

```
CommOrders_m (Mn)  = TotalOrders_m × Comm%_q(m)       (Y = Working sheet J141:J167 = C × I174:I182)
MktOrders_m        = CommOrders_m / CommShare_m       (X = Y / AA)
CPO_m              = MCXContracts_m / MktOrders_m     (Z = W / X)
```

**Daily:**

```
G  MktOrders_d     = (MCX contracts_d / 1e6) / CPO_m
H  CommOrders_d    = G × CommShare_m
I  Rev_d (Rs Mn)   = H × $AI$11      ← one fixed take rate = Working sheet J78 = Rs 22.29 (Q3 FY26) for ALL days
```

**Worked example, 14 May 2026 (row 548):**
- G = 53.827 / 11.5332 = 4.6672
- H = 4.6672 × 0.486 = 2.2682 Mn
- I = 2.2682 × 22.295 = 50.57 Rs Mn → **Rs 5.06 Cr**
- Using that quarter's take rate instead (21.51, `AB39`) would give Rs 4.88 Cr (issue #3).

### 4.4 MTF — sheet `MTF data (2)` (calibrated **quarterly**)

```
AngelShare_q   = AngelAvgBook_q / IndustryAvgBook_q        ('MTF data'!Q49:Q57 = P / D; D from the monthly series)
N  AngelBook_d (Rs Cr) = AngelShare_q × IndustryBook_d (I)
O  GrossRev_d (Rs Cr)  = N × 14.95% / 246
P  NetRev_d            = O × 0.45
```

**Worked example, 14 May 2026 (row 410):**
- N = 0.051541 × 121,761.47 = 6,275.66 Cr
- O = 6,275.66 × 0.1495 / 246 = **Rs 3.81 Cr gross**
- P = 1.72 net

---

## 5. Backtest / reconciliation, and what it proves

Model quarterly revenue (Σ daily, Rs Mn) vs revenue derived from the presentation (`Working sheet!rows 61–63`):

| Quarter | F&O | Cash | Commodities (as built, fixed take rate) | Commodities with quarterly take rate |
|---|---|---|---|---|
| Q3 FY25 | +0.16% | 0.00% | −10.8% | 0.00% |
| Q4 FY25 | +0.09% | 0.00% | −14.1% | +0.10% |
| Q1 FY26 | +0.03% | 0.00% | −12.2% | +0.03% |
| Q2 FY26 | +0.12% | 0.00% | −10.4% | +0.12% |
| Q3 FY26 | −0.24% | 0.00% | −2.8% | −2.76% (35 vs 36 orders, issue #5) |
| Q4 FY26 | +0.16% | 0.00% | +8.9% | 0.00% |
| Q1 FY27 | −0.59% | 0.00% | +3.7% | 0.00% |

The F&O figures match `backtesting F&O!AP4:AS9`. MTF: modelled vs reported Angel MTF interest is −1.1% to −5.5% (`'MTF data'!U51:U57`).

**Read-out:** in calibrated periods the tie-out holds **by construction**, because reported orders are being redistributed. It confirms the arithmetic, not the model's predictive power. The real test is the estimate regime: compare the model's estimate for a quarter (frozen before Angel reports) with the eventual actual. The dashboard should store that "pre-report estimate" snapshot for each quarter.

---

## 6. Estimate-regime rules currently in the workbook

| Segment | Parameter | Rule in Excel | Cells |
|---|---|---|---|
| F&O | Contracts/order (monthly) | Last actual month carried forward | `' F&O market'!H52:H56 = H51` |
| F&O | Market share (monthly) | Avg of last 3 months, then carried | `N24 = AVERAGE(N21:N23)`; `N25:N28` carry |
| F&O | F&O % of total orders | Avg of last 9 months | `E50 = AVERAGE(E41:E49)` |
| F&O | Take rate | Avg of last 3 reported quarters, carried | `backtesting F&O!AP51 = AVERAGE(AM51:AO51)` |
| Cash | Trades/order | Avg of last 3 quarters | `cash market!G42` |
| Cash | Take rate | Avg of last 3 quarters | `I42` |
| Cash | Share | Last quarter carried | `J42 = J41` |
| Commodity | Contracts/order | Rolling avg of last 3 months, then carried | `Commodities!Z41:Z44` |
| Commodity | Share | Actual where entered (Jul/Aug-26), then carried | `AA41:AA44` |
| Commodity | Take rate | Fixed Q3 FY26 for all periods | `AI11` |
| MTF | Share | Avg of Q4 FY25–Q1 FY27, carried | `'MTF data'!Q58:Q60` |
| F&O (BSE) | Daily BSE contracts | Previous day carried when missing | `backtesting F&O!U747:U761` |

The segments use different rules (carry vs 3-period vs 9-month averages). See decision D6.

---

## 7. Issues found (ranked by impact on the ADR)

1. **HIGH — BSE F&O contracts frozen for 15 trading days.**
   - `backtesting F&O!U747:U761` (29 Sep–21 Oct 2026) = previous row, i.e. stuck at **18.96 Mn**, the 28 Sep value. September's actual BSE average was 111.11 Mn/day, with Thursday expiries above 330 Mn.
   - The October F&O ADR of **Rs 6.74 Cr is understated**. Illustration only: at September's average BSE volume it would be about Rs 9.78 Cr.
   - Every window touching those dates is distorted: last 5/20/45 days and weekday stats. Example: latest Thursday F&O 3.81 vs 10-Thursday average 10.72.
2. **HIGH — MTF basis mismatch inside the Summary.**
   - The weekday tables (`SUMMARY!H35:H53`) use **net** MTF (`MTF data (2)!P` = 45% of gross). FY/Quarter/Month/Week tables use **gross** (`O`).
   - So the consolidated weekday ADR mixes bases. Latest Monday consolidated = 19.82. On a gross basis it would be 17.6951 + 4.7151 = **22.41**.
3. **HIGH/MED — Commodity take rate fixed at Q3 FY26 (Rs 22.29) for all dates.**
   - A per-quarter column (`Commodities!AB`) is built but not used. This causes the −14% to +9% quarterly mis-ties in §5.
   - With quarterly take rates: FY27 YTD commodity ADR 1.537 → **1.483**; FY26 1.163 → **1.195**.
4. **MED — Q1 FY27 actuals not fed through to F&O.**
   - The Q1 FY27 presentation is in `Working sheet!col M`, but the F&O take rate still uses the trailing average (21.42 vs actual 21.51).
   - The Apr/May-26 F&O % uses the 9-month average (0.7293) vs actual 0.7371.
   - June-26 total orders (140.04, `Working sheet!C167`) were not copied to `' F&O market'!C52`, so June onward uses the carried contracts/order.
   - Q1 FY27 F&O ties −0.59% (the others are within ±0.24%).
5. **MED — Double-entered inputs that disagree.**
   - Monthly orders `' F&O market'!C` vs `Working sheet!C`: Nov-24 130.96 vs 131.28; Jan-25 125.96 vs 125.97; Jan-26 146.70 vs 146.67.
   - Quarterly orders `rows 6–8` vs `174–182`: Q3 FY26 commodity 36 vs 35, total 381 vs 380; Q4 FY26 total 430 vs 430.66.
   - The monthly F&O share is also held in two places.
6. **MED — MTF share denominator ≠ series it is applied to.**
   - The share uses the quarterly average of a rounded **monthly** industry series. It is then multiplied by the **daily** series.
   - Q3 FY25: 88,667 vs 79,351 (daily average), so the daily Angel book under-ties. Q3 FY25 share is also hard-coded at 0.0485, while 4,050 / 88,667 = 0.0457.
7. **MED — MTF yield conventions are inconsistent and undocumented.**
   - 14.95% / 246 trading days (daily sheet) vs 14.99% / 4 (Working sheet).
   - 45% net factor: [SOURCE NEEDED: basis for the 45% net MTF margin].
8. **LOW — Cash panel on Summary is stale.**
   - Labels are hard-coded at Q4 FY26 / Q3 FY26 / Q4 FY25 and Feb-26 / Jan-26 (`SUMMARY!B65:B72`). Its 6-month average uses Q3+Q4 FY26.
   - The Consolidated/Broking totals are **not** affected; they compute cash directly.
9. **LOW — Period labels hard-coded** (`M8`, `M12:M14`, `M17:M18`, …). They must be rolled by hand. The 13 October days are not shown in the Quarter/Month tables.
10. **LOW — Hard-coded lookup ranges extended by hand** (`B31:H55` vs `H56`; `AI48:AQ57` vs `AR57`). This is fragile.
11. **LOW — `backtesting cash!I`** (NSE cash ADTO) reads the external row 2 rows above the date row from 9 Jun 2025 onward. Display only; it does not affect the ADR.
12. **LOW — `backtesting F&O!O`** ("NSE Fut contracts") = index-futures **turnover** + stock-futures **contracts**. Not used for Angel.
13. **LOW — Labels and definitions.** "Wo 10W" compares against 45 trading days (about 9 weeks). The 6-month average is not day-weighted.
14. **LOW — Different day bases.** Commodities averages over MCX days (144 in FY27), equity segments over equity days (138), MTF over 136 days (ends 19 Oct). The "last N days" windows are taken separately per sheet, so they may not cover the same dates.

---

## 8. Recommended logic for the dashboard build

### 8a. Data model (single source of truth for each input)

| Table | Grain | Fields |
|---|---|---|
| `calendar` | date | date, fy, q_fy, fy_month, weekday, is_equity_day, is_mcx_day |
| `exchange_fo_daily` | date | nse_fo_contracts_total, bse_fo_contracts, (premium ADTOs for display) |
| `exchange_cash_daily` | date | nse_trades, bse_trades, (nse_adto, bse_adto for display) |
| `mcx_daily` | date | mcx_contracts |
| `mtf_industry_daily` | date | industry_mtf_book_cr |
| `angel_monthly` | fy_month | total_orders_mn, fo_share, cash_share, comm_share, avg_funding_book_cr, avg_daily_orders, source_doc, page |
| `angel_quarterly` | q_fy | orders_fo/cash/comm_mn, rev_mix_fo/cash/comm/dist/dep/int/oth, total_income_mn, avg_funding_book_cr, share_fo/cash/comm, users_mn, source_doc, page |
| `assumptions` | key | mtf_yield, mtf_day_basis, mtf_net_factor, estimate rules per parameter |

Every value in `angel_*` carries a document name and page/table reference, in line with the house sourcing rule. Missing values stay null and are never filled silently. The UI then shows each period as **Actual** or **Estimate** and names the rule used.

### 8b. Compute pipeline (pseudo-code)

```python
# 1. take rates per quarter
tr[seg, q] = rev_mix[seg, q] * total_income[q] / orders[seg, q]          # Rs/order

# 2. F&O
mkt_c[d]  = nse_fo_contracts_total[d] + bse_fo_contracts[d]
if month m reported:
    fo_orders[m] = total_orders[m] * fo_pct[q(m)]       # fo_pct = orders_fo/total_orders of that quarter
    angel_fo_orders[d] = mkt_c[d] * fo_orders[m] / sum(mkt_c over m)
else:
    cpo[m]   = estimate_rule('fo_cpo', m)
    share[m] = estimate_rule('fo_share', m)
    angel_fo_orders[d] = mkt_c[d] / cpo[m] * share[m]
fo_rev_cr[d] = angel_fo_orders[d] * tr['fo', q(d)] / 10

# 3. Cash (quarterly calibration)
if quarter q reported:  cash_orders[d] = trades[d] * orders_cash[q] / sum(trades over q)
else:                   cash_orders[d] = trades[d] * share_est[q] / tpo_est[q]
cash_rev_cr[d] = cash_orders[d] * tr['cash', q(d)] / 10

# 4. Commodities (monthly calibration)
comm_orders[m] = total_orders[m] * comm_pct[q(m)]
if reported: comm_orders_d = mcx[d] * comm_orders[m] / sum(mcx over m)
else:        comm_orders_d = mcx[d] / cpo_est[m] * share[m]
comm_rev_cr[d] = comm_orders_d * tr['comm', q(d)] / 10      # quarterly TR (Excel: fixed Q3FY26)

# 5. MTF
if quarter reported: angel_book[d] = industry_book[d] * avg_book_angel[q] / mean(industry_book over q)
else:                angel_book[d] = industry_book[d] * share_est[q]
mtf_gross_cr[d] = angel_book[d] * mtf_yield / mtf_day_basis    # Excel: 0.1495 / 246
mtf_net_cr[d]   = mtf_gross_cr[d] * mtf_net_factor             # Excel: 0.45

# 6. Summary stats per segment, then Broking = FO + Cash + Comm, Consolidated = Broking + MTF (one basis)
```

Build a **"parity mode"** that reproduces the Excel exactly, including its quirks: fixed commodity take rate, net MTF on weekdays, and the monthly-series MTF denominator. Test it against the §1 parity table before switching to corrected logic. That way any difference after the switch can be traced to a specific fix.

---

## 9. Decisions needed from you before coding

| # | Decision | Excel today | Suggested |
|---|---|---|---|
| D1 | Build parity mode first, then corrected? | — | Yes |
| D2 | Commodity take rate | Fixed Q3 FY26 | Quarterly, like F&O and cash |
| D3 | MTF in consolidated: gross or net? | Gross except weekday tables (net) | One basis everywhere; show the other as a toggle |
| D4 | Cash share: monthly (as in doc) or quarterly (as in Excel)? | Quarterly | Quarterly for calibration (orders are quarterly); use monthly share only in the estimate regime |
| D5 | "Latest" quarter/month: last complete or current partial? | Hand-set labels (last complete) | Last complete, plus a QTD/MTD row |
| D6 | Estimate rules | Mixed (§6) | One rule per parameter type, set in `assumptions` |
| D7 | F&O contract definition | NSE total (incl. futures) + BSE combined | Keep it; update the Word doc to say "NSE total F&O contracts" |
| D8 | FY YoY | FY-to-date vs full prior FY | Also show same-period-last-year |
| D9 | Day basis for sums across segments | Each segment's own days | Common equity calendar for windows; MCX-only days kept within commodities |

---

## 10. Cell map (for reference)

| Item | Cells |
|---|---|
| Summary panels | Consolidated `B3:J26`, Broking `M3:U26`, MTF `B30:J53`, F&O `M30:U53`, Cash `B56:J79`, Commodities `M56:U79` |
| F&O daily | `backtesting F&O!B4:AA761` (ADR from row 253 = 1 Oct 2024) |
| F&O monthly calibration | `' F&O market'!B4:O28`, `B31:J56` |
| F&O take-rate table | `backtesting F&O!AI48:AR52` (row 51 = take rate) |
| Cash daily | `backtesting cash!B3:S760` (ADR from 1 Oct 2024) |
| Cash calibration | `cash market!B4:R26`, lookup `F34:J43` |
| Commodities daily | `Commodities!B2:I661` (from 1 Apr 2024) |
| Commodities calibration | `Commodities!U13:AB44`; take rate `AI11` |
| MTF daily | `MTF data (2)!B12:P518` (from 1 Oct 2024) |
| MTF calibration | `MTF data!C48:Q61` |
| Angel disclosures | `Working sheet - Angel One` rows 6–12 (orders), 15–21 (rev mix), 31 (funding book), 39–42 (shares), 61–63 (seg revenue), 76–78 (take rates), 94–111 (P&L), 141–169 (monthly), 174–182 (quarterly orders and users) |
| External exchange file | `20260121_Exchanges_Dashboard.xlsx` (SharePoint), sheets `NSE F&O`, `BSE F&O`, `NSE Cash`, `BSE Cash`, `MCX Data Clean` |
