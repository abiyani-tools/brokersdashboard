# Groww — ADR Methodology & Logic Spec (v1)

**Purpose:** a written-down, code-ready version of the Groww ADR (average daily revenue) logic in `20260714_brokers dashboard v2.xlsx`, to be reproduced cell for cell ("parity") by the engine that already implements the Angel One logic (`docs/Angel_One_ADR_Methodology.md`). The target screen is the sheet **`SUMMARY - Groww`**. Read §0.1 first: it lists every difference from Angel One.

**Basis:** the workbook as saved (exchange data to **21 Oct 2026**, industry MTF book to **19 Oct 2026**). Every number comes from a cell (`sheet!cell`), read with openpyxl from a copy, formulas and cached values loaded separately. **Verification:** I rebuilt the aggregation layer in Python from the cached daily rows of the four feeder columns (§1) and reproduced **all 262 numeric formula cells** of `SUMMARY - Groww` to 1e-9. The daily-layer formulas were traced by hand and recomputed for one day per segment (§4). I did not re-derive the 8,000+ daily cells from raw exchange data (the exchange inputs arrive through an external link, §2a).

**Conventions:** Indian FY (Apr–Mar; "FY 2027" = Apr-2026 to Mar-2027). Period labels as in the workbook: `Q2 FY 2025`, `FY 2027 October`. Summary ADR in Rs Cr. Daily F&O, cash and commodity revenue sit in Rs Mn in the daily sheets (÷10 → Cr). `MTF data (2)!L` is already in Rs Cr (no ÷10). Orders and contracts in Mn.

**Companion files** (`out/groww/`): `workbook_inputs.json` (726 rows: every hard-coded input the Groww chain reads, tagged by `scope`), `summary_expected.json` (262 numeric `SUMMARY - Groww` cells, the parity fixtures), `summary_expected_dash.json` (the 2 in-panel cells that legitimately show "-").

---

## 0. The idea in one paragraph

Groww does not publish daily revenue, **orders, or monthly business updates**: only quarterly results (revenue mix %, total income, MTF revenue) and, as the workbook has it, an ADTO market share per quarter. The workbook therefore rebuilds Groww's daily revenue from:

1. **Daily exchange activity**: NSE + BSE F&O contracts, NSE + BSE cash trades, MCX contracts and the industry MTF book (the same four feeder series as Angel One).
2. **Market orders borrowed from Angel One.** Daily "market orders" = daily contracts (or trades) ÷ **Angel One's** contracts-per-order (or trades-per-order). That ratio is Angel's own monthly/quarterly calibration, so Groww's ADR inherits Angel's reported orders and shares.
3. **Groww's share** (typed ADTO market share per quarter) turns market orders into **derived Groww orders**.
4. **Groww's take rate** = Groww's reported segment revenue (revenue-mix % × total income) ÷ those derived orders, set per reported quarter.

Per segment: **daily revenue = market orders × Groww share × take rate**; MTF is **Groww book (share × industry daily book) × 14.95% ÷ 246**. The ADR of a period is the simple average of daily revenue over the days of that period.

**Two regimes, and Groww has more estimate than Angel:**

| Regime | When (as saved) | What the model does |
|---|---|---|
| **Calibrated (actual)** | F&O: Q2–Q4 FY26. Cash: Q2 FY26–Q1 FY27. MTF share: Q3 FY25–Q1 FY27. Commodities: only Q3 FY26 (one-off) | Take rate (and for cash the share/orders) is solved from Groww's reported revenue, so the quarter ties to reported revenue: cash exactly (0.00%), F&O within ±0.1%, MTF −0.8% to −5.2%, commodities not at all (§5) |
| **Estimate** | F&O Q1 FY27 onward (even though Q1 FY27 is reported). Cash Q2 FY27 onward. Commodities everywhere after Q3 FY26. MTF Q2 FY27 onward (typed shares). Everything before 1 Jul 2025 is **zero** | Carry-forwards, trailing averages and hard-coded growth/share assumptions (§6) |

**Identity worth knowing.** In a calibrated quarter the share cancels: F&O Rev_d ≈ V_d × Rev_q ÷ ΣV_q (× CPO_q/CPO_m ≈ 1), and cash Rev_d = N_d × Rev_q ÷ ΣN_q exactly. So the ADR is reported revenue spread over days in proportion to exchange volume, as for Angel. Share, CPO and TPO only matter in estimate quarters and for commodities.

### 0.1 Differences from the Angel One model (what the coder needs)

| # | Area | Angel One (engine today) | Groww (this workbook) |
|---|---|---|---|
| 1 | **Own disclosures** | Monthly business update (orders, shares, funding book) and quarterly deck (orders, mix, income) | **Quarterly only**: revenue-mix %, total income, MTF revenue, and an **ADTO** share. No reported orders, no monthly data, no avg funding book. The workbook names no source for any of it |
| 2 | **Where "market orders" come from** | Angel orders ÷ Angel share (own disclosure) | Contracts or trades ÷ **Angel's** contracts/order (monthly, `' F&O market'!H`), trades/order (quarterly, `'cash market'!G35:G43`), commodity contracts/order (monthly, `Commodities!Z`). Groww depends on every Angel input and Angel estimate |
| 3 | **Segments** | F&O, Cash, Commodities, MTF | Same four, but **Groww F&O and Cash have no ADR before 1 Jul 2025** and **Commodities only from 1 Oct 2025** (launch). F&O/Cash days before 1 Jul 2025 are **numeric 0** in the sheet; commodity days before 1 Oct 2025 are **blank** |
| 4 | **Calibration cadence** | F&O monthly, Commodities monthly, Cash quarterly, MTF quarterly | **F&O quarterly** (take rate, share) on top of Angel's monthly CPO; **Cash quarterly**; **Commodities one-off** (Q3 FY26, never refreshed); **MTF quarterly** share |
| 5 | **Take-rate construction** | `mix × total income ÷ reported orders` (`Working sheet!rows 76–78`) | Orders are **derived** (`market orders × ADTO share`): `take rate = mix × base ÷ derived orders`. F&O at `backtesting F&O!AJ46:AL46`, cash at `Working sheet - Groww!H72:J72, L72`. Commodities: take rate **borrowed** (mean of Angel's last 3 quarterly commodity take rates, `Commodities!S5`) and orders derived from it |
| 6 | **Share definition** | Share of orders, as Angel reports it | **ADTO share** (`Working sheet - Groww!A54`) applied to order counts (units mismatch, issue #6) |
| 7 | **MTF basis** | Angel book share × industry book; **gross** `O` and **net** `P` (×0.45); weekday tables use net (issue #2 of the Angel doc) | Groww share × industry book; **gross only** (`MTF data (2)!L`). Weekday tables use `L` too: **no gross/net mismatch**. Share comes from reported MTF revenue ÷ (0.1495/4) ÷ industry quarterly average; Q2–Q4 FY27 shares are **typed** (`MTF data!J58:J60`). Yield 14.95% and 246 days are **Angel's constants** |
| 8 | **Summary layout** | Right panels in cols **M–U**; latest period = last **complete** (Q2 FY27, September) | Right panels in cols **L–T** (labels in L, values in M); latest period = **current partial** (Q3 FY27 = 13 equity days, October) |
| 9 | **Stale labels** | Cash panel only (`B65:B72`) | **F&O panel** (`L39:L41`, `L44:L45`) **and Cash panel** (`B65:B67`, `B70:B71`) hold hand-typed labels from older periods; Consolidated, Broking, MTF, Commodities link to the current labels |
| 10 | **Comparatives** | FY26 full year | **FY26 F&O and Cash ADR average in 61 zero days** (Apr–Jun 2025), understating FY26 by ~20–25% and overstating every FY YoY (issue #1). Commodities FY26 averages only the 128 live days |
| 11 | **Estimate rules** | carry / trailing-3 / trailing-9 | F&O: carry last take rate; share = last × 1.05 (typed 5%); cash: trailing-3 for take rate and trades/order, carry share; commodities: fixed share ×1.05 and fixed take rate; MTF: typed shares |
| 12 | **Latest actuals not wired** | Q1 FY27 F&O not fed (Angel issue #4) | **Q1 FY27 F&O is not fed** (+3.1% vs reported); **Q1 FY27 commodities not fed** (−14.7%); cash and MTF share are fed |

---

## 1. Output to replicate: `SUMMARY - Groww`

Three bands of two panels. Every panel has the same five tables; values are ADR in Rs Cr.

| Band (rows) | Left panel (cols B–J) | Right panel (cols **L–T**) |
|---|---|---|
| 3–26 | **Consolidated** = Broking + MTF (title `B3`) | **Broking** = F&O + Cash + Commodities (`L3:L4`) |
| 30–53 | **MTF** (`B31`: "MTF based on Trading days") | **F&O** (`L31`) |
| 56–79 | **Cash** (`B57`) | **Commodities** (`L57`) |

Row blocks inside a panel (band 2 and 3 are aligned; in band 1 the Broking panel sits one row below the Consolidated one):

| Table | Band 1 left / right (rows) | Band 2 | Band 3 | Comparison columns |
|---|---|---|---|---|
| Financial Year (2 rows) | 7–8 / 8–9 | 35–36 | 61–62 | YoY = cur/prev − 1 |
| Quarter (3 rows) | 11–13 / 12–14 | 39–41 | 65–67 | QoQ (vs row 2), YoY (vs row 3) |
| Month (2 rows + "Avg Of Last 6 Months") | 16–18 / 17–19 | 44–46 | 70–72 | MoM, "Mo 6M" = month ÷ 6M avg − 1 |
| Week (4 rows: last 5, previous 5, last 45, last 20 trading days) | 22–25 / 23–26 | 50–53 | 76–79 | WoW = L5/P5 − 1; "Wo 10W" = L5/L45 − 1 (ratios on the first row only) |
| Weekday Mon–Fri (3 rows each: latest, avg last 3, avg last 10) in cols G–J / Q–T | 7–25 / 8–26 | 35–53 | 61–79 | "Do 3D" = latest/avg3 − 1, "Do 10D" = latest/avg10 − 1 |

**Labels (as saved).** FY: `FY 2027`, `FY 2026`. Quarter: `Q3 FY 2027` (QTD), `Q2 FY 2027`, `Q3 FY 2026` (the "YoY" row). Month: `FY 2027 October`, `FY 2027 September`. They are typed once, in `L8:L9`, `L12:L14`, `L17:L18`, and linked from there into Consolidated (`B7:B17`), MTF (`B35:B45`) and Commodities (`L65:L71`). The F&O panel keeps its own typed labels (`L35:L36` current; **`L39:L41` = Q1 FY27, Q4 FY26, Q4 FY25 and `L44:L45` = Feb/Jan 2026 are stale**); the Cash panel too (`B61:B62` current; **`B65:B67`, `B70:B71` stale**).

**Aggregation formulas (as in Excel):**
- FY / Quarter / Month value = `AVERAGEIFS(daily revenue, period-key column, label) / 10`, wrapped in `IFERROR(…,0)`. MTF has no `/10`. Key columns: F&O/Cash `D` (FY), `E` (Q FY), `G` (FY Month); Commodities `C` (FY), `M` (Q FY), `E` (FY Month); MTF `E`, `F`, `H`. **Zero rows are averaged; blank rows are not.**
- "Avg Of Last 6 Months" = mean of the **two quarter-average ADRs** in the table, written as `(AVERAGEIFS(Q row 2) + AVERAGEIFS(Q row 1))/2/10`. In Broking and Consolidated it points at `L13`, `L12` (Q2 FY27 and the 13-day Q3 FY27), not at six months. Not day-weighted. In the F&O and Cash panels it points at their own stale labels (`L40`, `L39`; `B66`, `B65`).
- Last-N-trading-days: `LET` over the series' own date column, keeping only rows where date and value are numeric; unique dates; `cutoff = LARGE(unique dates, N)`; average of all rows with date ≥ cutoff (N = 5, 20, 45). Previous 5 = dates between `LARGE(…,10)` and `LARGE(…,6)`. Dates come from each feeder sheet, so windows can cover different days per segment (MTF ends 19 Oct).
- Weekday: filter unique numeric dates with `WEEKDAY(date,2)=k`, sort descending; "latest" = first; "last 3/10" = first 3/10 dates; average of the value on those dates.
- **Consolidated and Broking cells are sums of segment ADRs**, each computed separately, not averages of summed daily revenue. Broking `M8 = F&O + Cash + M61` (Commodities); Consolidated `C7 = M8 + C35` (MTF). Weekday: `R8 = R35 + H61 + R61`, `H7 = R8 + H35`. Week: `M23 = M50 + C76 + M76`, `C22 = M23 + C50`. The sum rows (`M8:M9, M12:M14, M17:M19, M23:M26`, `R8:R26`, and Consolidated) do **not** read the F&O/Cash panel labels, so the stale labels there do not feed the totals.
- Ratio cells: `IFERROR(a/b − 1, "-")`. Division by 0 gives the text "-" (cells `O39`, `E65`; `L/M145,149,153,157,161` are stray).
- Stray cells: `K144:M163` hold typed zeros and "-" with no panel (15 numeric cells). Excluded from the fixtures.

**Parity values for testing the build** (workbook as saved):

| ADR, Rs Cr | F&O | Cash | Commodities | **Broking** | MTF (gross) | **Consolidated** |
|---|---|---|---|---|---|---|
| FY 2027 YTD (`M35`,`C61`,`M61`,`M8`,`C35`,`C7`) | 11.4745 | 4.1344 | 1.1677 | **16.7766** | 2.2867 | **19.0633** |
| FY 2026 (`M36`,`C62`,`M62`,`M9`,`C36`,`C8`) | 8.4453 | 2.6939 | 0.9157 | **12.0549** | 0.9852 | **13.0401** |
| Q3 FY 2027 QTD / `FY 2027 October` (`M12`,`C11`) | 8.364 | 4.565 | 1.5795 | **14.5088** | 2.8977 | **17.4065** |
| Q2 FY 2027 (`M13`,`C12`) | 10.540 | 4.148 | 1.2798 | **15.9675** | 2.4824 | **18.4499** |
| FY 2027 September (`M18`,`C17`) | – | – | 1.4783 | **16.2716** | 2.5988 | **18.8703** |

Arithmetic check, FY 2027: 11.4745 + 4.1344 + 1.1677 = 16.7766, and 16.7766 + 2.2867 = 19.0633. Day counts behind FY 2027: F&O 138, Cash 138, Commodities 144 (MCX days), MTF 136. Q3 FY27 QTD: 13 / 13 / 14 / 12 days.

### 1.1 What reads the ADR downstream (not part of the parity target)

| Sheet | Role | Notes |
|---|---|---|
| `Groww charts` (hidden) | Daily series per segment: `AA`=`'backtesting F&O'!AD`, `AB`=`'backtesting cash'!V`, `AC`=`Commodities!K`, `AD`=`'MTF data (2)'!L` via `VLOOKUP`; `AE` = A+B+C; `AF/AG/AH` = "20/45/90 DMA" | Series ends **24 Sep 2026** (rows to 218). The DMA windows are truncated near the end (e.g. `AF218 = AVERAGE(AE204:AE218)` = 15 rows, `AG` 36 rows, `AH` 81 rows). Not in `SUMMARY - Groww` |
| `Groww - Final ` (visible) | Quarterly / annual predictor: "Last 45/20/5 day ADR" from `Groww charts!AG/AF/AE` ÷ 10; take rates `backtesting F&O!AP56`, `cash market!K41`, **`'Angel One - Final'!D26`** (Angel's commodity take rate 21.51, while the ADR chain uses 24.20); `PAT predictor *` sheets | Rows 163+ display cells of `SUMMARY - Brokers` (hidden multi-broker copy of this summary) |
| `Groww - ADR Model` (visible) | Valuation. `C8:E10` read `Groww - Final !D58:D60, D89:D91`; `J7:K7` re-average `MTF data (2)!L`; **`K6 = 12.05` typed** (FY26 broking ADR); other income from **`'Angel One - Final'!E100:E101`, `D131:D132`** | `B2` is `#VALUE!` (stock data type) |
| `PE chart - Groww`, `Groww - comparables` | Typed PE series and a text peer table | No ADR logic |

Not precedents of `SUMMARY - Groww`: `Summary MTF` (empty), `Monthly Market share` (NSE active clients by broker, typed; Groww rows 5, 27), `backtesting MCX` (older Groww commodity backtest, columns `O:P`; broken, `#REF!` from external link [3]; it re-uses `Commodities!S8:S9`), `Revenue and Orders`, `Motilal Oswal assumptions` (reached only by whole-column `SUMIF`s in `cash market` rows 68–72, scratch).

---

## 2. Inputs used

Legend: **Used** = read by the Groww ADR chain · **Not read** = present but not read · **Borrowed** = read, taken from Angel One or shared · **Absent** = not in the workbook.

### 2a. Exchange data (daily): identical feeder sheets to Angel One

All five series arrive by external link `[11]` = `…/Direct Equity/Exchanges-capital markets plays/Dashboard/20260121_Exchanges_Dashboard.xlsx` (SharePoint), sheets `NSE F&O`, `BSE F&O`, `NSE Cash`, `BSE Cash`, `MCX Data Clean`. Groww's columns in each feeder sheet differ from Angel's.

| Input | Status | Where | Note |
|---|---|---|---|
| Date, Q FY, FY, FY Month | Used | `backtesting F&O!B,D,E,G` (rows 4–761); `backtesting cash!B,D,E,G` (3–760); `Commodities!B,C,E,M` (derived from date by formula); `MTF data (2)!B,E,F,H` | |
| NSE total F&O contracts (index+stock options **and** futures) | Used | `backtesting F&O!T` = ext `NSE F&O` col U ÷ 1e6 | Same definition as Angel |
| BSE F&O contracts | Used | `backtesting F&O!U` = ext `BSE F&O` col I ÷ 1e6 | **Frozen 29 Sep–21 Oct 2026** (`U747:U761 = previous row` = 18.963 Mn). Shared defect with Angel (issue #2) |
| NSE trades, BSE trades | Used | `backtesting cash!L,M` → `N` | |
| MCX contracts | Used | `Commodities!F` | |
| Premium/notional ADTOs | Not read | `backtesting F&O!I:N`, `backtesting cash!I:K` | Display / MOSL only |

Groww-only daily columns (the values the Summary reads): F&O `AD` (rows 189–761; numeric from 1 Jul 2025), Cash `V` (188–760; numeric from 1 Jul 2025), Commodities `K` (390–661, from 1 Oct 2025), MTF `L` (12–518, 1 Oct 2024–19 Oct 2026).

### 2b. MTF data

| Input | Status | Where | Note |
|---|---|---|---|
| Industry total MTF book, **daily** (Rs Cr) | Used, borrowed | `MTF data (2)!I12:I518` (hard-coded, 507 values) | [SOURCE NEEDED: workbook does not name the daily source] |
| Industry MTF book, **monthly** (rounded) | Used, borrowed | `MTF data!E23:E43` (Oct-24 → Jun-26, typed); quarterly average `I` → `D51:D57` | The only source the workbook names is a URL in `MTF data!A5`: `https://scanx.trade/insight/mtf-insight` (monthly table). Q2 FY27 denominator `D58` = average of the daily series |
| Groww MTF revenue per quarter (Rs Cr) | Used | `MTF data!H51:H57` (typed copies of `Working sheet - Groww!E22:L22 / 10`) | `H51=20.1`, `H52=42.5`, `H57=118` are rounded vs 20.089, 42.479, 117.84 |
| Groww MTF share, Q2–Q4 FY27 | Used | `MTF data!J58=0.0288`, `J59=0.032`, `J60=0.036` | Typed; no basis, no source |
| Yield, day basis | Used | Literal `0.1495/246` inside `MTF data (2)!L12:L518`; `0.1495/4` inside `MTF data!I50:I57` | Angel's constants. Groww yield [SOURCE NEEDED] |
| Groww closing book, avg-book columns, 45% net factor | Not read | `MTF data!O,F,G`, `MTF data (2)!P` | Not used for Groww |

### 2c. Groww's own disclosures (`Working sheet - Groww`)

No cell comment, hyperlink or label names a source for any Groww figure. [SOURCE NEEDED: Groww quarterly results / investor presentation, page and table, for every row below.] Column map: `H`=Q2 FY26, `I`=Q3 FY26, `J`=Q4 FY26, `L`=Q1 FY27 (`G`=Q1 FY26 is mostly blank; `C:F` are older, `C` is a mislabeled copy of Q1 FY26 values).

| Metric (loader name) | Periods read | Cells | Value(s) |
|---|---|---|---|
| `revmix_fo` | Q2, Q3, Q4 FY26 | `H7, I7, J7` | 57%, 53%, 55% (whole %). `L7` = 52% **not read** |
| `revmix_cash` (incl. depository income) | Q2, Q3, Q4 FY26, Q1 FY27 | `H8, I8, J8, L8` | 19%, 18%, 16%, 16.4% |
| `revmix_comm` | Q3 FY26 only | `I9` | 4%. `J9` = 4%, `L9` = 4.9% **not read** |
| `revenue_from_ops`, `other_income` (→ total income) | Q2, Q3 FY26 | `H103:I104` (`H105`, `I105` sum) | 10,187.42 + 520.55 = **10,707.97**; 12,160.72 + 450 = **12,610.72** Rs Mn |
| `total_income_ex_fisdom_amc` ("Reported except Fisdom/AMC") | Q4 FY26, Q1 FY27 | `J120`, `L120` | **14,684**, **14,730** Rs Mn. These replace total income as the base for `J17`, `L18` |
| `share_fo_adto_q` (ADTO share) | Q2, Q3, Q4 FY26 | `H55:J55` | 0.173, 0.181, 0.212. `L55 = 11*2%` = 0.22 **not read** |
| `share_cash_adto_q` | Q2, Q3, Q4 FY26, Q1 FY27 | `H56:J56`, `L56` | 0.258, 0.288, 0.314, **0.302** (`L56` is the formula `=15.1*2%`) |
| Q1 FY26 (`G7`, `G8`, `G103:G105`; share `G55`, `G56` blank) | not read | | F&O 56%, cash 19%, total income 9,485 present; shares missing |

Derived (formulas): segment revenue `H17=H7*$H$105`, `I17=I7*$I$105`, `J17=J7*J$120`, `L18=L8*L$120`, commodity `I19=I9*$I$105` (Rs Mn); `H17:J17` = 6,103.54 / 6,683.68 / 8,076.20; cash `H18:J18, L18` = 2,034.51 / 2,269.93 / 2,349.44 / 2,415.72; commodity Q3 FY26 504.43.

### 2d. Angel One inputs the Groww chain reads (shared, already in the engine's Angel facts)

| Angel input | Where (read by Groww) | Feeds |
|---|---|---|
| Monthly total orders, Oct-24…May-26 | `' F&O market'!C32:C51` (typed) | F&O CPO `H32:H51` → Groww `X` (market orders) |
| F&O % of total orders, per quarter | `Working sheet - Angel One!F10:K10` (formulas of orders `F6:K8`) | `' F&O market'!E32:E49` |
| Monthly Angel F&O share, Oct-24…May-26 | `' F&O market'!N4:N23` (typed) | `O` contracts → CPO |
| Quarterly cash orders / cash share | `Working sheet - Angel One!F7:K7, M7`; `F40:K40, M40` | `cash market!N, K` → trades/order `P` |
| Monthly commodity orders and share | `Working sheet - Angel One!C141:C167` (`J141:J167`), `F165:F167`; `Commodities!AA14:AA37` (typed) | `Commodities!X, Z` (market orders, CPO) |
| Angel commodity take rate, Q1–Q3 FY26 | `Working sheet - Angel One!H78:J78` ← rows `17, 63, 94–99` | `Commodities!S5` (Groww commodity take rate) |

---

## 3. Take rate / revenue per order

Groww's orders are derived, so the take rate is **revenue ÷ derived orders**, not `mix × income ÷ reported orders`.

```
SegRev_q (Rs Mn)  = RevMix%_seg,q × Base_q          Base = total income (Q2, Q3 FY26; row 105)
                                                           or "Reported except Fisdom/AMC" (Q4 FY26, Q1 FY27; row 120)
F&O:   MktContracts_q = Σ_d V_d (Mn)               (AJ42:AL42)
       CPO_q          = mean of the 3 monthly Angel CPOs      (' F&O market'!J43, J46, J49)
       GrowwOrders_q  = MktContracts_q / CPO_q × Share_fo,q   (AJ45:AL45)
       TakeRate_fo,q  = SegRev_q / GrowwOrders_q              (AJ46:AL46 → AM56:AO56)
Cash:  MktOrders_q    = Σ trades_q / TPO_q        TPO_q = Angel's trades/order  (cash market!G35:G41, = P)
       GrowwOrders_q  = MktOrders_q × Share_cash,q            (Working sheet - Groww!H67:J67, L67)
       TakeRate_cash,q= SegRev_q / GrowwOrders_q              (H72:J72, L72 → cash market!K38:K41)
Comm:  TakeRate_comm  = mean(Angel commodity take rates Q1, Q2, Q3 FY26)   (Commodities!S5)
```

| Rs per order | Q2 FY26 | Q3 FY26 | Q4 FY26 | Q1 FY27 | Q2 FY27 | Q3 FY27 |
|---|---|---|---|---|---|---|
| F&O (`backtesting F&O!AM56:AR56`) | 29.633 | 28.977 | 26.378 | 26.378 (carry) | 26.378 | 26.378 |
| Cash (`cash market!K38:K43`) | 20.200 | 21.211 | 19.208 | 20.774 | 20.398 (avg of last 3) | 20.398 |
| Commodity (`Commodities!S5`) | – | – | – | – | 24.204 for every day from 1 Oct 2025 | |

Worked example, Q4 FY26 F&O: Rev = 0.55 × 14,684 = 8,076.20 Rs Mn; market contracts 20,278.12 Mn ÷ CPO 14.0411 = 1,444.20 Mn market orders × 0.212 = 306.17 Mn Groww orders; take rate = 8,076.20 ÷ 306.17 = **Rs 26.378** (`AL46`). Cash Q1 FY27: 0.164 × 14,730 = 2,415.72; market trades 2,536.79 Mn ÷ TPO 6.5881 = 385.06 Mn × 0.302 = 116.29 Mn orders; take rate = **Rs 20.774** (`L72`).

**Precision note.** Mix % is whole-percent for Q2 FY26–Q4 FY26 (one decimal for Q1 FY27 in `L8`, `L9`). ±0.5 pp moves the take rate by about ±0.9% for F&O (55%), ±3% for cash (16%) and ±12% for commodities (4%).

**Take rates are not comparable with Angel's** (Groww F&O ≈ 26–30 vs Angel ≈ 21.5): the denominator is derived orders on Angel's contracts/order, with an ADTO share. Treat them as calibration constants, not economics.

---

## 4. Segment logic

### 4.1 F&O broking: `backtesting F&O` (quarterly take rate/share, monthly Angel CPO)

**Daily** (rows 189–761; Groww columns `AB:AD`):

```
V  MktContracts_d (Mn) = T (NSE total) + U (BSE)                     U frozen from 29 Sep (issue #2)
W  CPO_m               = VLOOKUP(FY Month, ' F&O market'!$B$31:$H$56, 7)    Angel's monthly contracts/order
X  MktOrders_d         = V / W
AB Share_q             = HLOOKUP(Q FY, $AJ$48:$AR$57, 10)            row 57; zero for Q3 FY25–Q1 FY26 (empty)
AC GrowwOrders_d       = X × AB
AD Rev_d (Rs Mn)       = AC × HLOOKUP(Q FY, $AI$48:$AR$57, 9)         row 56 take rate; ADR = AD / 10
```

**Quarterly table `AM48:AR57`** (rows 55 CPO, 56 take rate, 57 share):

| | Q2 FY26 | Q3 FY26 | Q4 FY26 | Q1 FY27 | Q2 FY27 | Q3 FY27 |
|---|---|---|---|---|---|---|
| Share (row 57) | 0.173 (`'Working sheet - Groww'!H55`) | 0.181 | 0.212 | **0.2226** = `AO57*(1+AS57)`, `AS57 = 5%` | carry | carry |
| Take rate (row 56) | 29.633 (`=AJ46`) | 28.977 | 26.378 | 26.378 (`=AO56`) | carry | carry |
| CPO (row 55, take-rate step only) | 12.698 | 13.256 | 14.041 | 14.743 (`=AP50 = AO50*1.05`, unused by the daily chain) | | |

Row 55 of Q1 FY27+ is not read by any daily cell. Daily CPO is always the **monthly** Angel value: through May 2026 calibrated (e.g. May 2026 = 14.3517), June–Oct 2026 = 14.3517 carried (`' F&O market'!H52:H56 = H51`). The take-rate step uses the **quarterly mean** of three monthly CPOs; that is why quarters tie to ±0.1% and not exactly.

**Worked example, 14 May 2026 (row 652, Q1 FY27 estimate):** V = 64.913 + 590.772 (expiry day) = 655.685 Mn; W = 14.3517; X = 45.687; AB = 0.2226; AC = 10.170 Mn orders; AD = 10.170 × 26.378 = 268.26 Rs Mn → **Rs 26.83 Cr**.

### 4.2 Cash: `backtesting cash` (quarterly)

```
N  Trades_d (Mn)  = L (NSE) + M (BSE)
P  TPO_q          = VLOOKUP(Q FY, 'cash market'!$F$34:$J$44, 2)     Angel's quarterly market trades / market orders
T  Share_q        = VLOOKUP(Q FY, 'cash market'!$F$33:$L$44, 7)     Groww ADTO share (col L)
U  GrowwOrders_d  = N × T / P
V  Rev_d (Rs Mn)  = U × VLOOKUP(Q FY, 'cash market'!$F$34:$L$44, 6) take rate (col K); ADR = V / 10
```

Lookup table `cash market!F35:L43`:

| Q FY | Trades/order `G` | Take rate `K` | Share `L` | Source |
|---|---|---|---|---|
| Q2 FY26 | 5.7792 | 20.200 | 0.258 | actual |
| Q3 FY26 | 5.6972 | 21.211 | 0.288 | actual |
| Q4 FY26 | 6.1654 | 19.208 | 0.314 | actual |
| Q1 FY27 | 6.5881 | 20.774 | 0.302 | actual (share = formula `15.1*2%`) |
| Q2 FY27 | 6.1502 = AVERAGE(G39:G41) | 20.398 = AVERAGE(K39:K41) | 0.302 = `L41` | estimate |
| Q3 FY27 | = `G42` | = `K42` | = `L42` | estimate |

Calibrated identity: **U = N × Groww orders_q ÷ Σtrades_q**, so the quarter ties exactly. Q3 FY25–Q1 FY26 rows find no table row (or an empty share) and give 0 (or `#N/A` for Q2 FY25). **Worked example, 14 May 2026 (row 651):** N = 41.040 + 4.423 = 45.462 Mn; P = 6.5881; T = 0.302; U = 2.0840 Mn; V = 2.0840 × 20.774 = 43.29 Rs Mn → **Rs 4.33 Cr**.

### 4.3 Commodities: `Commodities` (monthly Angel CPO, one-off Groww calibration)

**Calibration, once, on Q3 FY26** (`S3:S9`):

```
S3 = Working sheet - Groww!I19              Groww Q3 FY26 commodity revenue = 504.43 Rs Mn
S5 = mean(Angel!H78, I78, J78)              take rate 24.204   (Angel's Q1–Q3 FY26 commodity take rates)
S6 = S3 / S5                                Groww orders 20.841 Mn
S7 = SUM(X32:X34)                           market orders Oct–Dec 2025 = 65.833 Mn   (X = Angel monthly orders / Angel monthly share)
S8 = S6 / S7                                Groww "share" 0.31657
S9 = 5%  (typed)                            growth
```

**Daily** (from row 390 = 1 Oct 2025; before that `J:K` are empty):

```
G  MktOrders_d (Mn)   = (F/1e6) / VLOOKUP(FY Month, $U$13:$Z$46, 6)      Angel's monthly commodity contracts/order (Z)
J  GrowwOrders_d      = G × $S$8 × (1 + $S$9)                            = G × 0.33240
K  Rev_d (Rs Mn)      = J × $S$5                                         one fixed take rate for all days; ADR = K / 10
```

Monthly CPO `Z`: calibrated Oct-25…Jun-26 from Angel's orders and shares (Oct-25 8.357 … Jun-26 14.838); estimate `Z41 = AVERAGE(Z38:Z40)` (Jul-26, 12.702), `Z42 = AVERAGE(Z39:Z41)` (Aug-26, 13.024), `Z43 = Z42`, `Z44 = Z43` (Sep, Oct).

**Worked example, 14 May 2026 (row 548):** F = 53.827 Mn contracts; G = 4.6672; J = 4.6672 × 0.33240 = 1.5514 Mn; K = 1.5514 × 24.204 = 37.55 Rs Mn → **Rs 3.75 Cr**.

Commodities is **never recalibrated** to Groww's reported commodity revenue (Q4 FY26 587.36, Q1 FY27 721.77 in `Working sheet - Groww!J19, L19`). The 5% growth is applied inside the calibration quarter, so even Q3 FY26 over-shoots by exactly 5%.

### 4.4 MTF: `MTF data (2)` + `MTF data` (quarterly share, daily book)

```
GrowwAvgBook_q (Rs Cr) = MTFRev_q (Rs Cr) / (0.1495/4)                   MTF data!I51:I57
IndAvgBook_q           = AVERAGE of 3 monthly industry books              MTF data!D51:D57 (Q2 FY27: average of the daily series, D58)
J  Share_q             = GrowwAvgBook_q / IndAvgBook_q                    MTF data!J51:J57; typed J58:J60 for Q2–Q4 FY27
K  GrowwBook_d (Rs Cr) = J × I (industry daily book)
L  Rev_d (Rs Cr)       = K × 0.1495 / 246                                 Summary reads L directly (gross)
```

| Q FY | Share `J` | Source |
|---|---|---|
| Q3 FY25 | 0.006065 | from H51 = 20.1 |
| Q4 FY25 | 0.014579 | H52 = 42.5 |
| Q1 FY26 | 0.016199 | H53 = 47.425 |
| Q2 FY26 | 0.014768 | H54 = 53.53985 |
| Q3 FY26 | 0.017707 | H55 = 75.66432 |
| Q4 FY26 | 0.017132 | H56 = 73.42 |
| Q1 FY27 | 0.026531 | H57 = 118 |
| Q2 / Q3 / Q4 FY27 | 0.0288 / 0.032 / 0.036 | **typed** |

**Worked example, 14 May 2026 (row 410):** I = 121,761.47 Cr; J = 0.026531; K = 3,230.46 Cr; L = 3,230.46 × 0.1495 / 246 = **Rs 1.963 Cr**.

### 4.5 Groww-specific mechanics the engine must replicate

1. **Zero days.** `backtesting F&O!AB:AD` and `backtesting cash!T:V` are numeric **0** for 1 Jul 2024–30 Jun 2025 wherever the quarterly table has no entry, and `#N/A` for Q2 FY 2025 (Jul–Sep 2024). `AVERAGEIFS` over FY 2026 therefore averages in the 61 days of Q1 FY26. Commodities `K` is blank before 1 Oct 2025, so its FY26 average covers only the 128 live days. Window statistics (`LET`) drop the `#N/A` rows but keep the zeros.
2. **Silent zeros.** Every FY/Q/month cell is wrapped in `IFERROR(…,0)`. A lookup that misses (a period beyond the typed tables) returns 0 in the Summary, not an error. Parity mode must give 0 only where the workbook does; live mode should raise.
3. **Roll horizon.** The typed lookup tables end at Q3 FY27 (`backtesting F&O` col `AR`; `cash market!F43`), `' F&O market'!B56` and `Commodities!U44` = Oct 2026, `MTF data!C60` = Q4 FY27. Dates after those fail in the sheet. The engine must be calendar-driven, not table-bound.
4. **Mixed bases in one Summary.** F&O and cash ADR use equity trading days (138 in FY27), commodities MCX days (144), MTF the days present in the industry series (136, ends 19 Oct).

---

## 5. Backtest / reconciliation

The workbook has no formal backtest block for Groww (Angel has `backtesting F&O!AP4:AS9`). The nearest are `Working sheet - Groww!H66:J73` (orders and take rates), `backtesting F&O!AJ37:AL46` and `MTF data!M55:M57`. I compared Σ daily revenue per quarter with reported revenue (`Working sheet - Groww` rows 17–19, 22):

| Segment (Rs Mn) | Q1 FY26 | Q2 FY26 | Q3 FY26 | Q4 FY26 | Q1 FY27 |
|---|---|---|---|---|---|
| F&O: model / reported | 0 / 5,311.6 (not modelled) | +0.07% | −0.09% | −0.02% | **+3.10%** (7,896.8 vs 7,659.6) |
| Cash | 0 / 1,802.2 (not modelled) | 0.00% | 0.00% | 0.00% | 0.00% |
| Commodities | n/a | n/a | **+5.00%** (529.7 vs 504.4) | **+9.38%** (642.5 vs 587.4) | **−14.71%** (615.6 vs 721.8) |
| MTF (model ×10 vs `row 22`) | −5.18% (449.7 vs 474.2) | −0.81% | −2.28% | −2.86% | −2.52% |

**Read-out.** Cash ties by construction. F&O ties to ±0.1% only in the three quarters used to set the take rate; the first quarter after (Q1 FY27, already reported) is off by +3.1% because it is projected, not fed. Commodities has no calibration after Q3 FY26 and the error grows. MTF is a share-times-book model on a 14.95%/246-day basis, so it runs 1–5% low. As with Angel, the tie-out in calibrated quarters shows the arithmetic, not predictive power. The dashboard should store a **pre-report estimate snapshot** per quarter (Groww's Q2 FY27 numbers are the next test).

---

## 6. Estimate-regime rules currently in the workbook

| Segment | Parameter | Rule in Excel | Cells |
|---|---|---|---|
| F&O | Contracts/order (monthly) | Angel's calibrated month through May-26; **Jun–Oct 2026 = May carried** | `' F&O market'!H52:H56 = H51` |
| F&O | Groww share | Q4 FY26 × 1.05 (typed 5%), then carried; **the reported Q1 FY27 share 0.22 is ignored** | `backtesting F&O!AP57 = AO57*(1+AS57)`, `AQ57:AR57` |
| F&O | Take rate | Q4 FY26 carried; **reported Q1 FY27 revenue 7,659.6 ignored** | `AP56 = AO56`, `AQ56`, `AR56` |
| Cash | Trades/order | Mean of last 3 quarters, then carried | `cash market!G42 = AVERAGE(G39:G41)`, `G43 = G42` |
| Cash | Take rate | Mean of last 3 quarters, then carried | `K42`, `K43` |
| Cash | Share | Last quarter carried (0.302, which is below Q4 FY26's 0.314) | `L42 = L41`, `L43 = L42` |
| Commodities | Contracts/order | Rolling mean of last 3 months, then carried | `Commodities!Z41:Z44` |
| Commodities | Share, take rate | Q3 FY26 calibration × 1.05 and Angel mean Q1–Q3 FY26, **for every day** | `S5, S8, S9` |
| MTF | Share | Typed 0.0288 (Q2), 0.032 (Q3), 0.036 (Q4 FY27) | `MTF data!J58:J60` |
| MTF | Industry avg book, Q2 FY27 | Average of the daily series | `MTF data!D58` |
| F&O (BSE) | Daily BSE contracts | Previous day carried when missing | `backtesting F&O!U747:U761` |
| All | Days before 1 Jul 2025 (F&O, Cash), 1 Oct 2025 (Commodities) | 0 / blank | §4.5 |

The rules differ across segments (carry vs trailing-3 vs ×1.05 vs typed). See decision D4.

---

## 7. Issues found (ranked by impact on the ADR)

1. **HIGH: FY 2026 comparatives are zero-filled for F&O and Cash.**
   - `backtesting F&O!AD` and `backtesting cash!V` are 0 for the 61 days of Q1 FY26 (Apr–Jun 2025); `AVERAGEIFS(…, FY 2026)` includes them.
   - FY26 F&O ADR shown **8.445**; Groww's own reported revenue gives 26,175.0 Mn ÷ 247 days ÷ 10 = **10.597** (`'Working sheet - Groww'!K17`). Q2–Q4 only: 11.215. Cash shown **2.694** vs **3.423** reported-basis. Consolidated FY26 shown **13.040**; with reported F&O/Cash it is about **15.92**.
   - Effect: FY YoY shown F&O +35.9%, Cash +53.5%, Broking +39.2%, Consolidated **+46.2%** (`D7`) vs about **+8%, +21%, +12%, +20%** respectively on a reported basis. Q1 FY26 quarter comparisons show 0 or "-".
   - Commodities FY26 is averaged over live days only, so the three segments use three different treatments of "not yet live".
   - Inputs exist to fix it: `G7`, `G8`, `G105` give Q1 FY26 F&O 5,311.6 and cash 1,802.2 Rs Mn.
2. **HIGH: BSE F&O contracts frozen for 15 trading days** (`backtesting F&O!U747:U761` = 18.963 Mn, the 28 Sep value). Shared with Angel (same cell). September's actual BSE average in this workbook is 102.3 Mn/day. Groww's Oct-26 F&O ADR is **8.36 Cr** as built; at September's BSE volume it would be **about 11.8 Cr** (illustration only). Every window touching those dates (last 5/20/45, weekdays, QTD, October) is distorted. Latest Thursday F&O (`R47`) 4.72 vs 10-Thursday average 13.30 is partly this.
3. **HIGH: Commodities are not calibrated to Groww's reported revenue.** Share fixed at 0.3324 and take rate at 24.20 for all days; model vs reported **+5.0%, +9.4%, −14.7%** (Q3 FY26, Q4 FY26, Q1 FY27). The commodity take rate is **Angel's**, not Groww's, and the reported Q4 FY26 / Q1 FY27 commodity revenue (`J19`, `L19`) is never read.
4. **MED: Q1 FY27 F&O is projected although reported.** Model 7,896.8 vs 7,659.6 Mn (+3.1%): share 0.2226 (= 0.212 × 1.05) vs reported 0.22 (`L55`), take rate carried 26.378 vs implied. Cash and MTF share were fed through; F&O and commodities were not.
5. **MED: Groww's market orders are Angel's.** CPO, TPO and commodity CPO are Angel's calibrations. Any Angel estimate, error or duplicate input moves Groww: June 2026 Angel orders (140.04) never reached `' F&O market'!C52`, so F&O CPO is May's from June on; Angel's Q3 FY26 commodity orders are 36 in `Working sheet - Angel One!J8` and 35 in `F180` (Angel doc issue #5; Groww's commodity calibration reads the monthly split built from `I174:I182`, i.e. the 35). Not an Excel bug, but a coupling the engine must expose.
6. **MED: ADTO share applied to order counts.** `Working sheet - Groww!A54` is "Market share by ADTO". The model multiplies it by market **orders** (contracts ÷ CPO, trades ÷ TPO). A turnover share is not an order share. The error is absorbed by the take rate in calibrated quarters (the take rate is solved from the same derived orders), so it matters in estimate quarters and in comparisons with Angel.
7. **MED: Typed assumptions with no source or stated basis.** `AS57` 5% F&O share growth; `Commodities!S9` 5%; `MTF data!J58:J60` (0.0288/0.032/0.036); `MTF data!B61` 38% growth (feeds `D59:D61`, display only); `Working sheet - Groww!L55 =11*2%`, `L56 =15.1*2%` (formula constants; `L56` pins the cash share for Q2 and Q3 FY27, and is **below** Q4 FY26's 0.314), `I23 =378-290` (not read by the ADR). [SOURCE NEEDED: basis for each.]
8. **MED: MTF conventions.** Groww yield taken as Angel's 14.95% [SOURCE NEEDED: Groww MTF yield]; 246-day basis vs 247 actual days in FY26 (and 138 so far in FY27); share built from the rounded monthly industry series but applied to the daily series (Angel doc issue #6); `MTF data!H51, H52, H57` typed rounded (up to 0.14%); the daily industry book ends 19 Oct (2 days short of equity data) so MTF windows cover different dates from F&O/Cash. Quarter tie-out −0.8% to −5.2%.
9. **MED: Roll horizon and silent zeros.** Typed lookup tables end at Q3 FY27 / Oct 2026 (§4.5.3); beyond that the Summary shows 0 through `IFERROR`. The next roll (Nov 2026) breaks `Commodities!G`, `' F&O market'!W`, and the F&O/cash take-rate lookups for Q4 FY27 dates.
10. **LOW/MED: Stale hand-typed labels** in the F&O panel (`L39:L41`, `L44:L45`) and Cash panel (`B65:B67`, `B70:B71`): those panels' quarter/month tables and their "Avg Of Last 6 Months" (`M46` 13.31, `C72` 3.97) describe Q1 FY27 / Q4 FY26 / Jan–Feb 2026 and do not foot to the Broking figures beside them. The totals are not affected. `L8:L9`, `L12:L14`, `L17:L18` must be rolled by hand.
11. **LOW: Latest quarter and month are partial.** Q3 FY27 is 13 days and October 13 days. QoQ −9.1%, MoM −10.8% (Broking) compare a partial period with full ones. "Avg Of Last 6 Months" averages the partial Q3 with the full Q2.
12. **LOW: Two revenue bases in `Working sheet - Groww`.** Q2/Q3 FY26 mix is applied to total income (row 105, includes Fisdom/AMC); Q4 FY26/Q1 FY27 to "Reported except Fisdom/AMC" (row 120). If the disclosed % are on one basis, the other columns are off by the Fisdom/AMC share (about 2–5%).
13. **LOW: `Working sheet - Groww` column `C` (Q1FY25) duplicates Q1 FY26 values** (`C103 = 9,043.98` = `K103 − sum(H:J)`), and `G103:G104` are typed rounded. Not read. Header mislabel.
14. **LOW: Take rate computed twice** (`Working sheet - Groww!H71, I71` and `backtesting F&O!AJ46:AL46`; equal today, `J71` blank). The Summary reads the second.
15. **LOW: Downstream sheets** (not parity): `Groww charts` series ends 24 Sep and its "20/45/90 DMA" windows shrink to 15/36/81 rows at the end; `Groww - Final` takes the commodity take rate from Angel (`'Angel One - Final'!D26` 21.51 vs 24.20); `Groww - ADR Model` takes other income from Angel's sheet and `K6` typed.
16. **LOW: Different day bases** across segments (F&O/Cash 138, Commodities 144, MTF 136 in FY27), as for Angel.

Angel-doc issues that do **not** apply to Groww: the net/gross MTF mismatch (Groww uses gross everywhere); the double-entry of Groww's own monthly inputs (there are none).

---

## 8. Recommended logic for the engine

### 8a. Data model additions (reuse the Angel tables; add `broker_id = 'GROWW'`)

| Table | Grain | New fields / metrics |
|---|---|---|
| `groww_quarterly` (facts) | q_fy | `revmix_fo`, `revmix_cash`, `revmix_comm`, `total_income` (Rs Mn), `total_income_ex_fisdom_amc`, `share_fo_adto_q`, `share_cash_adto_q`, `mtf_revenue` (Rs Cr), source_doc, page |
| `assumptions` | key | `share_growth_fo` 5%, `share_growth_comm` 5%, `mtf_share_override` by quarter, `mtf_yield` 0.1495, `mtf_day_basis` 246, `comm_take_rate_basis` (mean of Angel Q1–Q3 FY26), `first_live_date` per segment (F&O/Cash 2025-07-01, Commodities 2025-10-01) |
| calendar | date | add `is_live_fo`, `is_live_cash`, `is_live_comm` |

Metric names align with the Angel loader (`revmix_*`, `total_income`, `orders_*`, `share_*`); Groww-only names: `share_*_adto_q`, `total_income_ex_fisdom_amc`, `mtf_revenue`. Facts must carry document and page; every row in `workbook_inputs.json` with a `[SOURCE NEEDED]` note needs a filing-extractor pass.

### 8b. Compute pipeline (parity mode)

```python
# --- Angel-borrowed calibration (already in the engine; do not re-implement)
cpo_fo[m]    = angel.fo_contracts_per_order[m]      # monthly; Jun-Oct 2026 = May carried
tpo_cash[q]  = angel.cash_trades_per_order[q]       # quarterly; Q2 FY27 = mean(last 3), Q3 FY27 = carry
mkt_ord_comm[m], cpo_comm[m] = angel.comm_market_orders[m], angel.comm_cpo[m]
tr_comm_angel[q] = angel.take_rate_comm[q]

# --- Groww quarterly parameters
base[q] = total_income[q]                    if q in (Q2 FY26, Q3 FY26) else total_income_ex_fisdom[q]   # Q4 FY26, Q1 FY27
rev[seg, q] = revmix[seg, q] * base[q]       # Rs Mn

# F&O take rate, Q2-Q4 FY26 only; Q1 FY27+ carries Q4 FY26
for q in (Q2 FY26, Q3 FY26, Q4 FY26):
    cpo_q = mean(cpo_fo[m] for m in months(q))
    orders = sum(V[d] for d in days(q)) / cpo_q * share_fo[q]
    tr_fo[q] = rev['fo', q] / orders
tr_fo[Q1 FY27 ...] = tr_fo[Q4 FY26]
share_fo[Q1 FY27 ...] = share_fo[Q4 FY26] * (1 + share_growth_fo)

# Cash take rate, Q2 FY26-Q1 FY27; estimate = trailing 3
for q in (Q2 FY26 .. Q1 FY27):
    orders = (sum(trades[d] for d in days(q)) / tpo_cash[q]) * share_cash[q]
    tr_cash[q] = rev['cash', q] / orders
tr_cash[Q2 FY27] = mean(tr_cash[Q3 FY26], tr_cash[Q4 FY26], tr_cash[Q1 FY27]); carry for Q3 FY27
share_cash[Q2 FY27 ...] = share_cash[Q1 FY27]

# Commodities: one-off
tr_comm   = mean(tr_comm_angel[Q1 FY26], [Q2 FY26], [Q3 FY26])
orders0   = rev['comm', Q3 FY26] / tr_comm
share0    = orders0 / sum(mkt_ord_comm[m] for m in (Oct, Nov, Dec 2025))
share_eff = share0 * (1 + share_growth_comm)

# MTF share
for q in (Q3 FY25 .. Q1 FY27):
    share_mtf[q] = (mtf_revenue[q] / (mtf_yield / 4)) / mean(industry_book_monthly[m] for m in months(q))
share_mtf[Q2..Q4 FY27] = mtf_share_override[q]

# --- daily revenue
for d in days:
    fo_rev_mn[d]   = V[d] / cpo_fo[month(d)] * share_fo[q(d)] * tr_fo[q(d)]      if d >= 2025-07-01 else 0.0
    cash_rev_mn[d] = N[d] / tpo_cash[q(d)]   * share_cash[q(d)] * tr_cash[q(d)]  if d >= 2025-07-01 else 0.0
    comm_rev_mn[d] = (mcx[d]/1e6 / cpo_comm[month(d)]) * share_eff * tr_comm      if d >= 2025-10-01 else None   # blank, not 0
    mtf_rev_cr[d]  = share_mtf[q(d)] * industry_book[d] * mtf_yield / mtf_day_basis                              # gross only

# --- summary (identical aggregator for every panel)
adr(seg, period) = mean(rev[seg, d] for d in period, zeros included, None excluded) / (1 if seg == 'mtf' else 10)
windows: last N trading days per segment from that segment's own numeric dates; weekday stats per segment
Broking = F&O + Cash + Commodities;  Consolidated = Broking + MTF       # sums of segment ADRs
unknown period -> parity: 0 (IFERROR);  live: raise
```

Test hooks: `summary_expected.json` (262 cells, ±1e-9) and the four feeder columns' cached daily values. My reference aggregator (`/private/tmp/claude-501/-Users-abhishekbiyani-Documents-broker-dashboard/4f78fff7-ca02-4af2-8c4c-b57322f6b69d/scratchpad/groww/parity.py`) reproduces all 262 from the cached daily rows; the engine's daily layer should reproduce the daily rows (`backtesting F&O!AD`, `backtesting cash!V`, `Commodities!K`, `MTF data (2)!L`) before the Summary is compared.

### 8c. Parity mode vs corrected mode

Keep a **parity mode** that reproduces every quirk above: zero-fill before 1 Jul 2025, the 5% typed growths, Q1 FY27 F&O not fed, fixed commodity calibration, the 18.963 BSE freeze, stale panel labels, partial latest period. Each correction is one named switch with a before → after bridge (as for Angel): (a) exclude or backfill Q1 FY26 (decision D2), (b) feed Q1 FY27 F&O and commodity actuals (D3), (c) BSE F&O from the lake (shared with Angel switch), (d) one estimate rule per parameter (D4), (e) MTF yield and day basis (D7), (f) labels from the calendar, last complete period plus QTD row (D8).

---

## 9. Decisions needed from AB

| # | Decision | Excel today | Suggested |
|---|---|---|---|
| D1 | Parity first, then corrected switches? | | Yes |
| D2 | Pre-Jul-2025 F&O/Cash days (FY26 comparatives) | Zero-filled; FY26 ADR −20/25% | Switch: backfill Q1 FY26 from reported revenue (`G7`, `G8`, `G105`) spread by volume, so FY26 is a full year; keep zero-fill in parity |
| D3 | Feed Q1 FY27 actuals into F&O and Commodities, and recalibrate commodities each quarter | F&O +3.1%, Commodities −14.7%, Q3 FY26 +5.0% | Yes: each reported quarter calibrates take rate (F&O, commodities) like cash; drop the 5% share growth inside reported quarters |
| D4 | Estimate rules | Mixed: carry, trailing-3, ×1.05, typed | One rule per parameter type in `assumptions`, same as Angel D6 |
| D5 | Dependence on Angel's market orders | Groww CPO/TPO = Angel's | Keep for parity; show the dependency in the UI; consider an independent industry-orders estimate later |
| D6 | ADTO share applied to orders | As is | Confirm Groww's disclosed share is by ADTO; if so keep (take rate absorbs it) and label |
| D7 | MTF: yield, day basis, Q2–Q4 FY27 shares | 14.95% (Angel's), 246, typed 2.88/3.20/3.60% | Source Groww's yield; day basis = actual FY days; replace typed shares by "last actual share carried" and show the typed value as an override |
| D8 | "Latest" quarter/month | Current partial (13 days) | Last complete period, plus a QTD/MTD row (same as Angel D5) |
| D9 | Base for revenue mix (row 105 vs row 120) | Q2/Q3 on total income, Q4/Q1 on ex-Fisdom/AMC | Confirm which base the disclosed % use; apply one |
| D10 | Source of record for Groww's facts | None named in the workbook | Run filing-extractor on Groww's results for Q1 FY26–Q1 FY27 (and Q2 FY27 when out); until then every Groww fact is `[SOURCE NEEDED]` |
| D11 | BSE F&O freeze (29 Sep–21 Oct) | Frozen | Fix at source (the lake); shared with Angel |
| D12 | Commodities take rate | Angel's Q1–Q3 FY26 mean (24.20) | Groww-specific once calibrated per quarter (D3) |
| D13 | Roll horizon | Typed tables end Oct 2026 | Calendar-driven engine; no table-bound lookups |

---

## 10. Cell map (for reference)

| Item | Cells |
|---|---|
| Summary panels | Consolidated `B3:J26`, Broking `L3:T26`, MTF `B30:J53`, F&O `L30:T53`, Cash `B56:J79`, Commodities `L56:T79`; stray `K144:M163` |
| Summary labels (typed) | `L8:L9`, `L12:L14`, `L17:L18`; F&O `L35:L36, L39:L41, L44:L45`; Cash `B61:B62, B65:B67, B70:B71` |
| F&O daily | `backtesting F&O!B4:AD761` (Groww `AB:AD` rows 189–761; numeric from row 438 = 1 Jul 2025); BSE freeze `U747:U761` |
| F&O quarterly table | `backtesting F&O!AI48:AR57` (rows 55 CPO, 56 take rate, 57 share), growth `AS50, AS55, AS57`; take-rate derivation `AI36:AL46` |
| F&O monthly CPO (Angel) | `' F&O market'!B31:H56` (`H` = contracts/order, `J` quarterly mean) |
| Cash daily | `backtesting cash!B3:V760` (Groww `T:V`, rows 188–760; numeric from row 437) |
| Cash calibration | `cash market!B4:P26`, lookup `F34:L43` (`G` TPO, `K` take rate, `L` share) |
| Groww cash orders / take rate | `Working sheet - Groww!H63:L72` |
| Commodities daily | `Commodities!B2:K661` (Groww `J:K` from row 390 = 1 Oct 2025) |
| Commodities calibration | `Commodities!R2:S9` (Groww), `U13:AB44` (Angel monthly CPO) |
| MTF daily | `MTF data (2)!B12:L518` (Groww `J:L`; industry book `I`) |
| MTF calibration | `MTF data!C48:J60` (Groww share `J`), monthly industry `E12:E44`, quarterly avg `I` |
| Groww disclosures | `Working sheet - Groww` rows 7–9 (mix), 17–19, 22 (segment revenue, Rs Mn), 55–56 (ADTO shares), 103–105, 120 (income), 63–72 (derived orders and take rates) |
| Angel inputs read | `' F&O market'!C32:C51, N4:N23`; `Working sheet - Angel One` rows 6–10, 17, 40, 63, 78, 94–99, 141–167, 174–182; `Commodities!AA14:AA37` |
| External exchange file | `20260121_Exchanges_Dashboard.xlsx` (link `[11]`), sheets `NSE F&O`, `BSE F&O`, `NSE Cash`, `BSE Cash`, `MCX Data Clean` |
| Downstream | `Groww charts!AA:AL`, `Groww - Final `, `Groww - ADR Model`, `SUMMARY - Brokers` |

---

## 11. Corrections after the parity build and back-sourcing (31 Oct 2026)

The engine reproduces `SUMMARY - Groww` (262/262 cells, 1e-9) and the four feeder columns (≤ 1.1e-13); see branch `groww-parity`, `run_parity.py --broker GROWW`. Building it and tracing the inputs to Groww's filings (`out/groww/backsource.md`) corrected this document in places:

**Spec errors (the code follows the sheet, not these lines)**
- §1: `M12`, `M13`, `M18` (F&O) and the `C65`-style cells (cash) are Broking figures. The F&O and Cash panels carry stale labels (Q1 FY27, Q4 FY26, Feb / Jan 2026), so 8.364, 10.540 and 4.565 are not shown in those panels.
- §0.1 #3 and §8b: F&O and cash are `#N/A` for Q2 FY25 (1 Jul–30 Sep 2024) and numeric 0 for Q3 FY25–Q1 FY26 only, as §4.5.1 says, not 0 for every day before 1 Jul 2025.
- §1: the commodity window and weekday formulas count only `value > 0` days (no numeric effect here).

**Inputs vs filings (41 Groww inputs: 10 match, 11 rounded, 10 restated, 8 differ, 2 no source)**
- D9: the revenue mix is a % of **consolidated total income**. The workbook's row 120 (used for Q4 FY26 and Q1 FY27) is platform revenue ex Fisdom/AMC, so those quarters' segment revenue is 4–5% low.
- D6: the shares are by ADTO (cash = stocks ADTO, F&O = equity-derivatives premium ADTO). Groww doubled the denominator from Q4 FY26; the workbook re-doubles to stay on the old basis, which is consistent.
- D7: the 14.95% MTF rate is stated on calls only (Q2 FY26 transcript p6, Q1 FY27 p13); the book-yield check gives 14.2–16.5%. The 246-day basis has no source (FY26 had 247 trading days).
- MTF revenue is wrong in three quarters: Q4 FY25 and Q1 FY26 use 5% (the Treasury bucket) where MTF was 2% and 3%; Q4 FY26 uses 73.4 Cr where 6.9% × 15,355 = 105.95 Cr (the Q4 FY26 letter's chart transposes the PL+LAS and MTF labels; the Q1 FY27 letter's "MTF +1.1pp QoQ" confirms 6.9%).
- The stocks mix was restated in the Q2 FY27 letter's reclassification (e.g. 19.4 → 17.8).
- Q1 FY26 is available (total income 9,484.71 Mn, Q2 FY26 results p5; mix on the Q1 FY27 letter p6), so FY26 can be a full year (D2).
- The Q2 FY27 actuals and 103 candidate facts with page refs are in `out/groww/facts_candidates.json`.
