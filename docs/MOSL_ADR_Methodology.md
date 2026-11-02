# Motilal Oswal (MOSL) — ADR Methodology & Logic Spec (v1)

**Purpose:** a written-down, code-ready version of the Motilal Oswal ADR (average daily revenue) logic in `20260714_brokers dashboard v2.xlsx`, to be reproduced cell for cell ("parity") by the engine that already implements Angel One (`docs/Angel_One_ADR_Methodology.md`) and Groww (`docs/Groww_ADR_Methodology.md`). The target screen is the sheet **`SUMMARY - Motilal Oswal`** (hidden in the workbook). Read §0.1 first: MOSL is built on a different principle from Angel and Groww, and borrows nothing from Angel.

**Basis:** the workbook as saved (exchange data to **21 Oct 2026**, industry MTF book to **19 Oct 2026**, MOSL facts through the **Q1 FY27 data book**). Every number comes from a cell (`sheet!cell`), read with openpyxl from a copy, formulas and cached values loaded separately. **Verification:**
1. A reference aggregator rebuilds the Summary from the cached daily rows of the four feeder columns (§1) and reproduces **all 264 numeric formula cells** of `SUMMARY - Motilal Oswal` (max abs difference 0.0; tolerance 1e-9). A row-alignment check on the 54 Broking/Consolidated sum cells (135 references) finds no off-by-one reference.
2. A second reference re-derives the four daily columns from the raw exchange columns and the typed inputs (§4): 633 F&O, 496 cash, 646 commodity and 495 MTF numeric rows, max abs difference 0.0, and every error cell (`#N/A`, `#VALUE!`) lands on the same rows.
3. The Q2 FY27 data book (published 29 Oct 2026, read-only copy in `data/raw/disclosures/mosl/`) is used only for the backtest in §5; it is not in the workbook.
I did not re-derive the exchange numbers themselves: they arrive through an external link (§2a).

**Conventions:** Indian FY (Apr–Mar; "FY 2027" = Apr-2026 to Mar-2027). Period labels as in the workbook: `Q2 FY 2027`, `FY 2027 September`. Summary ADR in Rs Cr. The F&O and commodity daily columns are in **Rs Mn** (÷10 → Cr); the cash daily column (`AB`) and the MTF column (`X`) are **already in Rs Cr** (no ÷10). Quarterly revenue inputs are Rs Cr, as in the data book.

**Companion files** (`out/mosl/`): `workbook_inputs.json` (1,226 rows: every hard-coded input the MOSL chain reads, the live data-book links and the typed data-book copy, tagged by `scope`, with the data-book cell where one exists), `summary_expected.json` (the 264 parity fixtures). The reference aggregator is `scratchpad/mosl/parity.py` (Summary from cached daily rows) and `scratchpad/mosl/derive.py` (daily layer from raw inputs), path in §8b.

---

## 0. The idea in one paragraph

MOSL does not publish orders, trades or a monthly business update. It publishes a **quarterly data book** (Excel, 3–4 weeks after quarter end) with **gross and net brokerage by segment** (cash, F&O, commodity, currency), ADTO, market shares and the MTF closing book. So, unlike Angel and Groww, the workbook never has to derive revenue from orders: it takes **each reported quarter's gross segment revenue and spreads it over the days of the quarter in proportion to a daily market-activity key**, then multiplies by the reported **net ÷ gross brokerage ratio** to get net brokerage. The keys are: NSE **index-option** + BSE option contracts (F&O), NSE + BSE cash **turnover** (cash), MCX contracts (commodities). MTF is a separate formula: **MOSL share of the industry closing book × daily industry book × a typed net-interest yield ÷ 247**. The ADR of a period is the simple average of daily revenue over the days of that period.

The formulas carry market-share, ADTO and "delivery ratio" terms, but in a calibrated quarter they **cancel**: F&O `ΣAF = 10 × reported gross revenue`, cash `ΣAA = reported gross revenue`, commodities `ΣL = 10 × reported gross revenue`, exactly (§4). Share and ADTO only matter in estimate quarters, and only for commodities and cash (§6).

| Regime | When (as saved) | What the model does |
|---|---|---|
| **Calibrated (actual)** | Q3 FY25 to Q1 FY27 for F&O, cash, commodities (cash Q1 FY27 only partly, issue #7); MTF share Q3 FY25 to Q1 FY27 | Quarter ties to reported gross revenue (typed values, some rounded) to within about 0.5%; cash Q1 FY27 −1.5% |
| **Estimate** | **Q2 FY27 (Jul–Sep 2026) for all four segments** (reported on 29 Oct 2026, not yet in the workbook); Q3 FY27 (1–21 Oct) for F&O only | Carry-forwards and trailing averages of typed assumptions (§6) |
| **Not modelled** | F&O Q1–Q2 FY25: numeric 0; before that `#N/A`. Cash and MTF before 1 Oct 2024: `#N/A` / blank. Cash, commodities, MTF in Q3 FY27: `#N/A` or blank | See issue #1 |

**The headline quarter of the Summary (Q2 FY27) is a pure estimate**, and the comparatives (Q1 FY27, Q4 FY26) are calibrated.

### 0.1 Differences from the Angel One and Groww models (what the coder needs)

| # | Area | Angel One (engine today) | Groww | **MOSL (this workbook)** |
|---|---|---|---|---|
| 1 | **Own disclosures** | Monthly update (orders, shares, book) + quarterly deck | Quarterly only: mix %, total income, ADTO share, MTF revenue | **Quarterly data book only**, with **gross and net brokerage per segment**, ADTO, shares, MTF closing book. No orders, no trades, no monthly data. [Disclosure map: `out/mosl/disclosure_map.md`] |
| 2 | **Orders and Angel calibration** | Own reported orders | Contracts / trades ÷ **Angel's** contracts-per-order (monthly) and trades-per-order (quarterly) | **No orders at all, and no Angel borrowing.** The precedent closure of the 264 Summary cells never touches ` F&O market`, `cash market`, `MTF data`, `Working sheet - Angel One`, `Working sheet - Groww`, the Angel CPO table `Commodities!U:AA` or Angel's share columns. MOSL has its own quarterly calibration; the engine's Angel calibration is **not reused** |
| 3 | **Revenue basis** | Mix × total income ÷ orders = take rate | Same, with derived orders | **Reported gross brokerage, then × reported net/gross ratio.** The Summary shows **net** brokerage for F&O, cash, commodities (`AG`, `AB`, `O`); MTF is **NII-based** (`X`), not a gross interest or revenue line |
| 4 | **Activity key** | All F&O contracts (NSE total + BSE); cash trades; MCX contracts | Same as Angel | F&O: **NSE index options + BSE contracts only** (`backtesting F&O!S = R + P`; excludes NSE stock options and futures). Cash: **NSE + BSE turnover (ADTO, Rs Cr)**, not trades. Commodities: MCX contracts |
| 5 | **Calibration cadence** | F&O monthly, commodities monthly, cash and MTF quarterly | F&O quarterly on Angel's monthly CPO; cash quarterly; commodities one-off | **Everything quarterly**; no monthly parameters |
| 6 | **MTF** | Angel share × book; yield 14.95%; /246; gross and net 0.45 | Groww share; 14.95%; /246 | MOSL **closing-book** share (reported book ÷ industry book on the quarter's last data date) × daily industry book × **typed quarterly NII yield (11.9–15.5%)** ÷ **247**. Daily series ends 30 Sep (Q3 FY27 blank) |
| 7 | **Summary layout** | Right panels M–U; Cash left, Commodities right in band 3 | Right panels L–T; Broking panel one row below Consolidated | Right panels **L–T**; **band 3 is swapped: Commodities left (`B58:J81`), Cash right (`L59:T82`)**; Broking aligned with Consolidated (same rows); Cash panel one row below Commodities. Latest period = last complete (Q2 FY27, September) as for Angel |
| 8 | **Labels** | Cash panel stale | F&O and Cash panels stale | No stale panel labels (all link to `L7:L17`), **but the "YoY" quarter row is Q4 FY26 for a Q2 FY27 headline** (`L13`), so "YoY" is a two-quarter comparison (issue #3) |
| 9 | **Pre-launch days** | Fully backfilled | F&O/Cash zero before 1 Jul 2025 | Full FY26 in all four segments: **no zero-fill problem in FY26**. Zeros only for F&O Q1–Q2 FY25 |
| 10 | **Latest period handling** | Last complete period | Current partial period | Last complete period for labels, **but the data run to different dates**: F&O 21 Oct; cash, commodities, MTF 30 Sep. **FY27 YTD silently drops cash and commodities** (issue #1) |
| 11 | **Special sessions** | Included in parity | Included | Included (1 Nov 2024, 1 Feb 2025, 21 Oct 2025, 1 Feb 2026 carry revenue) |
| 12 | **Hidden multi-broker panel** | Net/gross MTF mismatch (H8) | not audited | The MOSL panel of `SUMMARY - Brokers` is ~17% below reported (H7, verified, issue #2) |

---

## 1. Output to replicate: `SUMMARY - Motilal Oswal`

Three bands of two panels. Every panel has the same five tables; values are ADR in Rs Cr.

| Band (rows) | Left panel (cols B–J) | Right panel (cols **L–T**) |
|---|---|---|
| 3–25 | **Consolidated** = Broking + MTF (`B3`) | **Broking** = F&O + Cash + Commodities (`L3`) |
| 30–53 | **MTF** (`B31` "MTF Book") | **F&O** (`L31`) |
| 58–81 | **Commodities** (`B59`) | **Cash** (`L60`) |

| Table | Consolidated / Broking rows | MTF / F&O rows | Commodities rows | Cash rows | Comparison columns |
|---|---|---|---|---|---|
| Financial Year (2) | 7–8 | 35–36 | 63–64 | 64–65 | YoY = cur/prev − 1 |
| Quarter (3) | 11–13 | 39–41 | 67–69 | 68–70 | QoQ (vs row 2), "YoY" (vs row 3) |
| Month (2 + avg) | 16–18 | 44–46 | 72–74 | 73–75 | MoM, "Mo 6M" = month ÷ avg − 1 |
| Week (4) | 22–25 | 50–53 | 78–81 | 79–82 | WoW = L5/P5 − 1; "Wo 10W" = L5/L45 − 1 (first row only) |
| Weekday Mon–Fri (3 rows each) | G–J / Q–T, 7–25 | 35–53 | 63–81 | 64–82 | "Do 3D", "Do 10D" |

Per panel: 3 FY + 5 Quarter + 5 Month + 6 Week + 25 Weekday = **44 numeric cells; 6 panels = 264**. Fixtures: `out/mosl/summary_expected.json`. No cell evaluates to the text "-" (no division by zero reaches a ratio).

**Labels (as saved).** FY `FY 2027`, `FY 2026`. Quarter `Q2 FY 2027`, `Q1 FY 2027`, **`Q4 FY 2026`** (the "YoY" row). Month `FY 2027 September`, `FY 2027 August`. They are typed once, in `L7:L8`, `L11:L13`, `L16:L17`, and linked into every panel (`B7:B17`, `L35:L45`, `B35`, `B39:B45`, `B63:B73`, `L64:L74`). The only other typed label is `B36` (`FY 2026`, MTF panel).

**Aggregation formulas (as in Excel):**
- FY / Quarter / Month = `IFERROR(AVERAGEIFS(daily, key, label)/10, 0)`. F&O and Commodities carry the `/10`; **Cash and MTF do not**. Key columns: F&O `D, E, G` (of `backtesting F&O`), Cash `D, E, G` (`backtesting cash`), Commodities `C, M, E`, MTF `E, F, H` (`MTF data (2)`, rows 12–1000). Daily value columns: F&O `AG`, Cash `AB`, Commodities `O`, MTF `X`.
- **AVERAGEIFS semantics that matter:** blank cells are skipped; **a matched cell holding `#N/A` makes the whole average an error, which `IFERROR` turns into 0**; zeros are averaged.
- "Avg Of Last 6 Months" = mean of the **two quarter ADRs** (Q1 and Q2 FY27 rows), not six months and not day-weighted: `(AVERAGEIFS(Q1)+AVERAGEIFS(Q2))/2` (`/10` for F&O, commodities). Broking `M18 = M46 + M75 + C74`, Consolidated `C18 = M18 + C46`.
- Last-N-trading-days: `LET` on the segment's **own** date and value columns, keeping rows where both are numeric (zeros kept, errors dropped); `cutoff = LARGE(unique dates, N)`, average of all rows with date ≥ cutoff (N = 5, 20, 45). Previous 5 = dates between `LARGE(…,10)` and `LARGE(…,6)`.
- Weekday: unique numeric dates with `WEEKDAY(date,2)=k`, sorted descending; "latest" = first, "last 3 / 10" = first 3 / 10 dates; average of the value on those dates. No `> 0` filter.
- **Consolidated and Broking cells are sums of segment ADRs**, not averages of summed daily revenue: `M7 = M35 + M64 + C63` (F&O + Cash + Commodities), `C7 = M7 + C35` (MTF); weekday `R7 = R35 + R64 + H63`, `H7 = R7 + H35`; week `M22 = M50 + M79 + C78`, `C22 = M22 + C50`.
- Stray cells: `K144:K163` hold 15 typed zeros and a header with no panel. Excluded from the fixtures.

**Parity values for testing the build** (workbook as saved; Rs Cr per day):

| Period (cells: F&O, Cash, Comm, Broking, MTF, Consolidated) | F&O | Cash | Commodities | **Broking** | MTF | **Consolidated** |
|---|---|---|---|---|---|---|
| FY 2027 YTD (`M35`,`M64`,`C63`,`M7`,`C35`,`C7`) | 1.8054 | **0 (silent)** | **0 (silent)** | **1.8054** | 3.9876 | **5.7931** |
| FY 2026 (`M36`,`M65`,`C64`,`M8`,`C36`,`C8`) | 1.8499 | 1.8815 | 0.5991 | **4.3304** | 3.3134 | **7.6438** |
| Q2 FY 2027 (`M39`,`M68`,`C67`,`M11`,`C39`,`C11`) | 1.5818 | 1.6647 | 0.7687 | **4.0152** | 4.2911 | **8.3063** |
| Q1 FY 2027 (`M40`,`M69`,`C68`,`M12`,`C40`,`C12`) | 1.9672 | 2.0307 | 0.5233 | **4.5211** | 3.6533 | **8.1744** |
| Q4 FY 2026 (`M41`,`M70`,`C69`,`M13`,`C41`,`C13`) | 1.9453 | 1.6998 | 0.7949 | **4.4400** | 3.2819 | **7.7219** |
| FY 2027 September (`M44`,`M73`,`C72`,`M16`,`C44`,`C16`) | 1.5914 | 1.6208 | 0.8948 | **4.1070** | 4.4923 | **8.5993** |
| FY 2027 August (`M45`,`M74`,`C73`,`M17`,`C45`,`C17`) | 1.3591 | 1.6553 | 0.7478 | **3.7622** | 4.2846 | **8.0468** |
| Avg of last 6 months (`M46`,`M75`,`C74`,`M18`,`C46`,`C18`) | 1.7745 | 1.8477 | 0.6460 | **4.2682** | 3.9722 | **8.2404** |
| Last 5 trading days (`M50`,`M79`,`C78`,`M22`,`C50`,`C22`) | 2.1958 | 1.5336 | 0.7968 | **4.5263** | 4.5556 | **9.0819** |
| Previous 5 (`M51`,`M80`,`C79`,`M23`,`C51`,`C23`) | 1.9952 | 1.5821 | 1.4633 | **5.0406** | 4.4888 | **9.5293** |
| Last 45 (`M52`,`M81`,`C80`,`M24`,`C52`,`C24`) | 1.7154 | 1.6393 | 0.7995 | **4.1542** | 4.3724 | **8.5266** |
| Last 20 (`M53`,`M82`,`C81`,`M25`,`C53`,`C25`) | 1.9921 | 1.6246 | 0.9419 | **4.5585** | 4.4948 | **9.0533** |

Day counts behind FY 2027: F&O 138 rows (all numeric), Cash 138 rows (**125 numeric**, 13 `#N/A`), Commodities 144 rows (**130 numeric**: 7 `#N/A`, 7 blank), MTF 136 rows (**124 numeric**, 12 blank). Q2 FY27: 65 / 65 / **66 (MCX)** / 65 days. Q1 FY27: 60 / 60 / 64 / **59** days. **The last-N and weekday windows end on different dates per segment**: F&O to 21 Oct 2026, Cash, Commodities and MTF to 30 Sep 2026, so "Last 5 trading days" of Broking adds F&O for 15–21 Oct to the other three segments for 24–30 Sep.

Arithmetic check, Q2 FY27: 1.5818 + 1.6647 + 0.7687 = 4.0152; 4.0152 + 4.2911 = 8.3063.

### 1.1 What reads the ADR downstream (not part of the parity target)

| Sheet | Role | Notes |
|---|---|---|
| `MOSL charts` (hidden) | Daily `C = VLOOKUP(…,'backtesting F&O'!B:AG,32)/10`, `D = …cash!B:AB,27` (no /10), `E = …Commodities!B:O,14)/10`, `I = 'MTF data (2)'!B:X,23`, `F = C+D+E`, 45-DMA, `J = I + F`, stock price (`STOCKHISTORY`), R² | Consistent with the Summary (net columns, right units). Starts at `backtesting F&O!B253` (1 Oct 2024) |
| `Motilal Oswal Charts` (hidden) | Older series: `AB = VLOOKUP(…,'backtesting F&O'!$B:$AF,31)` (**gross** `AF`, Rs Mn), `AC = VLOOKUP(…,'backtesting cash'!$B:$AA,24)`, `AD = …Commodities!$B:$L,11` (**gross** `L`, Rs Mn), `W = AB+AC+AD` | **The cash lookup index is 24, which returns column `Y` (MOSL market share, 0.068–0.077), not `AA` (index 26)**, so the "ADR" is F&O gross + a share + commodity gross. Series ends 8 Jun 2026 (row 418), so `Motilal Oswal - Final!D14:D15` (`Y419`, `X419`) = 0 |
| `Motilal Oswal - Final` (hidden) | Predictor / valuation | A half-converted copy of `Groww - Final`: reads **Groww's** shares (`'Working sheet - Groww'!H55:J56`), **Angel's** commodity take rate (`'Angel One - Final'!D26`), `PAT predictor Q1FY27` and `Motilal Oswal Charts!Y419` (= 0); 5 `#REF!` chains. Not a MOSL ADR consumer |
| `SUMMARY - Brokers`, `(A+B)`, panel `AG59:AO` | Hidden multi-broker copy | **~17% below reported (issue #2)** |
| `PAT predictor Q1FY27!N23:Q30`, `Q2FY27!N23:Q31` | Gross sums × net/gross ratio `Working Sheet - MOSL!T62:T64` (= `AVERAGE(S,N,I)`, the annual FY26, FY25, FY24 ratios) | Different ratio from the Summary chain; Q2 FY27 projected broking 265.0 vs Summary-implied 261.8 vs reported 276.6. Typed "Actual reported" `N30:P30` = 124 / 118 / 33 (F&O and cash look swapped, issue #12) |
| `cash market` rows 57–72 | Scratch SUMIFs on the assumptions sheet | Not read by the MOSL Summary |

Not precedents of `SUMMARY - Motilal Oswal`: `MTF data` (monthly industry table), ` F&O market`, `cash market`, `Working sheet - Angel One`, `Working sheet - Groww`, `Monthly Market share`, `Revenue and Orders`, the Angel/Groww columns of `Commodities`, `backtesting F&O` columns `T:AD` (Angel, Groww) and `backtesting cash` `L:X`.

---

## 2. Inputs used

Legend: **Used** = read by the MOSL ADR chain · **Not read** = present but not read · **Absent** = not in the workbook · **Shared** = a shared feeder sheet.

### 2a. Exchange data (daily): shared feeder sheets

All arrive by external link `[11]` = `…/Direct Equity/Exchanges-capital markets plays/Dashboard/20260121_Exchanges_Dashboard.xlsx` (SharePoint), cached in the feeder sheets. MOSL reads **different columns** from Angel and Groww:

| Input | Status | Where | Note |
|---|---|---|---|
| Date, FY, Q FY, FY Month | Used | `backtesting F&O!B,D,E,G` (rows 4–761); `backtesting cash!B,D,E,G` (3–760); `Commodities!B,C,E,M` (2–661; `M` = `"Q"&…` formula); `MTF data (2)!B,E,F,H` (12–518) | |
| NSE index-option contracts | Used | `backtesting F&O!P` = ext `NSE F&O` col M | |
| BSE contracts ("BSE Opt contracts") | Used | `backtesting F&O!R` = ext `BSE F&O` col I | Same source column as the frozen `U` (Angel/Groww), but `R` is **not frozen**: live through 21 Oct. MOSL is immune to the 29 Sep–21 Oct BSE freeze |
| **Total option contracts (the F&O key)** | Used | `backtesting F&O!S = R + P` (Rs: raw counts) | Excludes NSE stock options (`Q`) and futures. BSE is **46–50%** of `S` in Q4 FY26–Q3 FY27, and BSE > NSE on 27 of 65 days in Q2 FY27 (Sensex expiry days reach 339–513 Mn contracts) |
| NSE / BSE option ADTO (premium turnover) | Used (cancels) | `backtesting F&O!J` (NSE index options), `M` (BSE options), ext `NSE F&O` col O, `BSE F&O` col M | Feeds `assumptions!G` only; no effect on the output |
| NSE + BSE cash turnover ("ADTO") | Used | `backtesting cash!K = I + J` (Rs Cr), ext `NSE Cash` col L, `BSE Cash` col L | **Two-row date misalignment from 9 Jun 2025** (issue #5): display-only for Angel/Groww, **the cash key for MOSL** |
| MCX total contracts | Used | `Commodities!F` = ext `MCX Data Clean` col J | |
| `backtesting F&O!P169` | Used | typed `' '` (text) on 31 May 2024 | `S169 = #VALUE!` (Q1 FY25; outside every Summary period) |
| `backtesting F&O` columns `I, K, L, N:O, Q, T:AD`; `backtesting cash` columns `H, L:X` | Not read | | Angel / Groww / display (NSE total F&O, trades, stock options, futures) |

### 2b. MTF data

| Input | Status | Where | Note |
|---|---|---|---|
| Industry total MTF book, **daily** (Rs Cr) | Used, shared | `MTF data (2)!I12:I518` (507 typed values, 1 Oct 2024 → 19 Oct 2026) | [SOURCE NEEDED: workbook does not name the daily source; `MTF data!A5` names `scanx.trade/insight/mtf-insight` for the monthly table] |
| Industry closing book at quarter end | Used | `assumptions!D8:D14` = `MAXIFS` date of the quarter with a book, then `XLOOKUP`; `D6:D7` typed (Q1, Q2 FY25: 70,593.33 / 82,020.37, **unsourced, not read**) | `D15 = 'MTF data (2)'!I501` (23 Sep, stale) feeds only display `C15`/`R103` |
| MOSL closing MTF book (Rs Cr) | Used | `assumptions!C6:C14` (data book `Consol!F70:P70`, exact) | Q2 FY27 reported 9,600 is **not** in the workbook |
| **NII yield** | Used | `assumptions!F6:F14` (typed; 0.1192 … 0.1294; `F15 = F14`) | **[SOURCE NEEDED: not a line in the data book; no data-book cell equals any of the nine values]** |
| Day basis | Used | literal `/247` inside `MTF data (2)!X12:X506` | FY26 had 247 trading days; FY27 will differ |
| Groww / Angel books, 45% net, 14.95%, 246 | Not read | `MTF data (2)!J:P`, `MTF data!…` | |

### 2c. MOSL's own disclosures: the quarterly data book

**Source of record:** the MOSL quarterly **data book** (`.xlsx`, sheet **`Consol`**), published on `motilaloswal.com` three to four weeks after the quarter (Q1 FY27 on 23 Jul 2026, Q2 FY27 on 29 Oct 2026; no monthly update exists). The workbook links one copy live: external link `[12]` = `mofsl-q1fy27-data-book (3).xlsx` (a local Downloads copy), sheet `Consol`, columns `B..E` = FY21..FY24, `F..I` = Q1..Q4 FY25, `J` = FY25, `K..N` = Q1..Q4 FY26, `O` = FY26, `P` = Q1 FY27. In the Q2 FY27 book the same rows hold `Q` = Q2 FY27 (match on labels; row positions move between vintages). `Consol` rows used: 44–48 ADTO, 50–54 gross brokerage, 56–60 net brokerage, 63–67 market share, 69 NSE active clients, 70 MTF book, 72 ARPU, 74 VAR.

**Period of each assumption cell** (the workbook's own labels):
- MTF block: rows 6–14 = `Q1 FY 2025` … `Q1 FY 2027` (label in `B`); `B15` Q2 FY27 (estimate), `B16:B18` empty headers.
- F&O block: rows 27–37 = `Q1 FY 2025` … `Q3 FY 2027` (label in `B`).
- Cash block: rows 46–54 = `Q3 FY 2025` … `Q3 FY 2027` (label in `B`).
- Commodities block: columns `C..L` of row 59 = `Q1 FY 2025` … `Q2 FY 2027`.
- Net/gross and external-link rows: columns `C..F` = FY21..FY24, `G..J` = Q1..Q4 FY25, `K` = FY25, `L..O` = Q1..Q4 FY26, `P` = FY26, `Q` = Q1 FY27, `R` = Q2 FY27, `S` = Q3 FY27 (header rows 110–111 and 82–83).

**Register of every MOSL assumption cell** (sheet `Motilal Oswal assumptions` unless stated). "Read" = a precedent of the Summary. The per-cell list, with value, unit, period, label and the data-book cell, is `out/mosl/workbook_inputs.json` (`databook_ref`, `databook_match` = exact / rounded / link / none).

*Typed numeric cells: 135.* **108 match the data book (90 exact, 18 rounded to 3–4 digits), 27 do not.**

| Cells | Label in the sheet | Metric | Periods | Data-book cell | Match | Read |
|---|---|---|---|---|---|---|
| `C6:C14` | MOSL- closing book | `mtf_book_closing` (Rs Cr) | Q1 FY25 .. Q1 FY27 | `Consol!F70:P70` | exact 9 | 9/9 |
| `D6:D7` | Market - closing | `mtf_industry_book_close` | Q1, Q2 FY25 | none (industry; unsourced) | none | 0/2 |
| `F6:F14` | NII | `mtf_nii_yield` | Q1 FY25 .. Q1 FY27 | **none** | none | 9/9 |
| `C29:C35` | MOSL F&O revenue | `gross_fo_cr` (Rs Cr) | Q3 FY25 .. Q1 FY27 | `Consol!H52:P52` | exact 3, **rounded 4** (`C29`=225, `C30`=182, `C34`=203, `C35`=206) | 7/7 |
| `I27:I34` | MOSL mkt share | `share_fo` (F&O premium) | Q1 FY25 .. Q4 FY26 | `Consol!F66:N66` | exact 7, rounded 1 (`I34`=0.07 vs 0.0703) | 8/8 |
| `M29:M36`, `L46:L53` | Total trading days | `trading_days_total` | Q3 FY25 .. Q2 FY27 | none (calendar counts) | none | 0/16 |
| `E46:E52` | MOSL mkt share | `share_cash` | Q3 FY25 .. Q1 FY27 | `Consol!H64:P64` | exact 5, rounded 2 (`E51`, `E52` = 0.068 vs 0.0678) | 7/7 |
| `G46:G52` | MOSL reported | `adto_cash_mosl` (Rs Cr/day) | Q3 FY25 .. Q1 FY27 | `Consol!H44:P44` | exact 3, rounded 4 | 7/7 |
| `I46:I52` | MOSL reported rev | `gross_cash_cr` (Rs Cr) | Q3 FY25 .. Q1 FY27 | `Consol!H51:P51` | exact 3, rounded 4 (`I46`=233, `I47`=169, `I51`=189, `I52`=228) | 6/7 (**`I52` not read**) |
| `K60` | Revenue | `gross_comm_cr` | Q1 FY27 | `Consol!P53` | rounded (55 vs 54.72) | 1/1 |
| `K62` | Market Share | `share_comm` | Q1 FY27 | `Consol!P67` | rounded (0.077 vs 0.0772) | 1/1 |
| `K63` | ADTO | `adto_comm_mosl` | Q1 FY27 | `Consol!P47` | rounded | 0/1 |
| `C112:Q112` | Net/Gross, Cash (row 97 pasted) | `net_gross_cash` | FY21 .. Q1 FY27 | `Consol!57 ÷ 51` | exact 15 | 9/15 |
| `C113:Q113` | Net/Gross, F&O | `net_gross_fo` | same | `Consol!58 ÷ 52` | exact 15 | 9/15 |
| `C114:Q114` | Net/Gross, Commodity | `net_gross_comm` | same | `Consol!59 ÷ 53` | exact 15 | 9/15 |
| `C115:Q115` | Net/Gross, Currency | `net_gross_currency` | same | `Consol!60 ÷ 54` | exact 15 | 0/15 |

*Live external links to the data book: 165 cells* (`C84:Q88` gross total/cash/F&O/commodity/currency = `Consol!B50:P54`; `C90:Q94` net = `Consol!B56:P60`; `C103:Q103` MTF book = `Consol!B70:P70`; 11 rows × 15 columns). None is a precedent of the Summary (display and the PAT predictor).

**So 300 numeric cells sit on the assumptions sheet and 273 of them trace to the data book (165 live links + 90 exact + 18 rounded); the other 27 (9 NII yields, 2 industry books, 16 day counts) do not.** In addition, `Working Sheet - MOSL` holds **411 typed numeric cells copied from the data book** (rows 44–80, columns `B:S`; 319 equal the data book exactly, the other 92 are FY24-quarter columns the Q1 FY27 book no longer shows); the Summary reads only `J53:R53` (commodity gross revenue, Q1 FY25–Q4 FY26, 8 cells) and `J73:R73` (commodity share, 8 cells). Rows 62–65 (`=net/gross`) are formulas.

Formula cells in the chain (not inputs): F&O `F, G, H, J, K, L` (rows 29–37), `I35:I37`; cash `C, D, F, H, J` (46–54) with `E53:E54`, `H53:H54`, `J52:J54`; commodity rows 60–74 `C:L`; `R112:R114`, `S113`.

**Used by the chain but typed as a constant inside a formula:** `247` (`MTF data (2)!X`), `1e7` (`backtesting F&O!AF`), `10` (`assumptions!L29:L35`), `60` (`D35`, `D36`, display).

### 2d. Angel One / Groww inputs the MOSL chain reads

**None.** Precedent closure of all 264 cells (30,454 cells, 29,226 formulas, 1,228 constants) touches six sheets only: `backtesting F&O`, `backtesting cash`, `Commodities` (columns `B:F, L, M, O`), `MTF data (2)` (`B,D–H,I,V,W,X`), `Motilal Oswal assumptions`, `Working Sheet - MOSL`. The "contracts / order" column `Commodities!N` (which does use Angel's monthly CPO table `U13:Z43`) exists beside the MOSL columns but feeds only the display rows `assumptions!C68:K72`, never the daily chain.

---

## 3. Take rate / revenue per unit of activity

MOSL's revenue is **reported**, so the calibration constant is the revenue per unit of the activity key, per quarter. Units below are as the sheet defines them.

```
Gross_q (Rs Cr)           = typed C (F&O), I (cash), K60 / Working Sheet row 53 (commodity)     [data book Consol rows 52 / 51 / 53]
F&O:   F_q   = Σ_d S_d / 1e7              (Cr index-option + BSE contracts in the quarter)
       K_q   = share_q × F_q               (MOSL contracts; share_q typed, cancels)
       L_q   = Gross_q / K_q × 10          (Rs Mn per Cr contracts; "Rs per contract" in the label is ×10; true Rs/contract = L/10)
Cash:  C_q   = mean_d(K_d)  (avg NSE+BSE ADTO);  F_q = share_q × C_q ;  H_q = F_q / G_q  (G = MOSL reported cash ADTO)
       J_q   = I_q / G_q    (reported gross revenue per unit of reported ADTO; per QUARTER, not per day)
Comm:  contracts_q = Σ_d F_d / 1e6 (Mn);  MOSLc_q = share_q × contracts_q ;  take_q = Gross_q × 10 / MOSLc_q   (Rs per MOSL contract)
MTF:   share_q = MOSL closing book / industry closing book (last data date of q);  NII_q typed
Net:   ratio_q = Net_q / Gross_q  per segment (typed row 112 cash, 113 F&O, 114 commodity)
```

| | Q3 FY25 | Q4 FY25 | Q1 FY26 | Q2 FY26 | Q3 FY26 | Q4 FY26 | Q1 FY27 | Q2 FY27 | Q3 FY27 |
|---|---|---|---|---|---|---|---|---|---|
| F&O, Rs per MOSL contract (`L/10`) | 0.745 | 1.673 | 1.749 | 1.477 | 1.466 | 1.476 | 1.428 | 1.428 (carry) | 1.428 |
| F&O index-option contracts `F`, Cr | 3,670.7 | 1,330.1 | 1,224.2 | 1,460.0 | 1,635.2 | 1,964.9 | 1,876.2 | 1,631.5 | 449.1 (13 d) |
| F&O share `I` (typed, cancels) | 0.0823 | 0.0818 | 0.0871 | 0.0872 | 0.0838 | 0.0700 | 0.0769 (avg `I33:I34`) | carry | carry |
| F&O net/gross | 0.6011 | 0.5876 | 0.5838 | 0.5930 | 0.5966 | 0.5750 | 0.5730 | 0.5740 (avg Q4, Q1) | carry |
| Cash take rate `J` (per quarter) | 0.06863 | 0.06538 | 0.07642 | 0.07373 | 0.07090 | 0.06334 | **0.06334 (= `J51`)** | 0.06334 | 0.06334 |
| Cash `J/D`, bps of reported ADTO per day | 11.07 | 10.55 | 12.53 | 11.52 | 11.44 | 10.56 | 10.56 | 9.74 (D=65) | 48.7 (D=13) |
| Cash "delivery ratio" `H` | 2.5235 | 2.7199 | 2.5730 | 2.6548 | 2.6610 | 2.9053 | 2.7875 | 2.7846 (avg of 3) | 2.8258 |
| Cash share `E` | 0.0772 | 0.0697 | 0.0734 | 0.0708 | 0.0694 | 0.0680 | 0.0680 | 0.0680 | 0.0680 |
| Cash net/gross | 0.5499 | 0.5391 | 0.5916 | 0.5306 | 0.5319 | 0.5396 | 0.5416 | 0.5406 (avg Q4, Q1) | `#N/A` (range ends at `R`) |
| Commodity share (row 62) | 0.0808 | 0.0875 | 0.0869 | 0.0853 | 0.0846 | 0.1010 | 0.0770 | **0.0870 (avg of last 4)** | none |
| Commodity take, Rs per MOSL contract (row 74) | 18.57 | 17.53 | 17.55 | 16.79 | 17.02 | 12.65 | **7.33** | 7.33 (carry) | none |
| Commodity net/gross | 0.6271 | 0.6410 | 0.5975 | 0.5711 | 0.5513 | 0.5646 | 0.6089 | 0.5867 (avg Q4, Q1) | none |
| MTF share (closing) | 0.05989 | 0.05995 | 0.05957 | 0.06181 | 0.05745 | 0.05435 | 0.05776 | 0.05776 (carry) | none |
| MTF NII yield `F` | 0.1373 | 0.1448 | 0.1451 | 0.1548 | 0.1454 | 0.1306 | 0.1294 | 0.1294 (carry) | none |

(Commodity Q1 FY25 take 22.12, Q2 FY25 19.44; MTF/other columns for FY25 H1 are not used by the Summary periods.)

Worked example, **Q4 FY26 cash**: G = 2,984; I = 189 (typed, data book 188.74); J = 189 / 2,984 = 0.063338. Days 60 and average ADTO 127,489 (Rs Cr/day, `C51`) give F = 0.068 × 127,489 = 8,669, H = 8,669 / 2,984 = 2.9053. A day with ADTO K has AA = 0.068 × K / 2.9053 × 0.063338 / 60 and Σ AA = G × J = 189. **Q1 FY27 F&O**: C35 = 206 (typed; data book 205.60), F = 1,876.18 Cr contracts, I = 0.07691, K = 144.30 Cr contracts, L = 206 / 144.30 × 10 = 14.276; Σ AF = 0.07691 × 1,876.18 × 14.276 = 2,060 Rs Mn = 10 × 206.

**Precision note.** The typed gross revenues for Q3 FY25, Q4 FY25, Q4 FY26, Q1 FY27 (F&O), Q3 FY25–Q1 FY27 (cash, except Q1–Q3 FY26) and Q1 FY27 (commodity) are rounded to whole Rs Cr (up to ±0.5% for the smaller lines); shares for Q4 FY26/Q1 FY27 to three decimals (cash 0.068 vs 0.0678, commodity 0.077 vs 0.0772, F&O 0.07 vs 0.0703). Rounding matters little in calibrated quarters (the quarter ties within 0.5%) but flows into the estimate quarters through the carried parameters.

---

## 4. Segment logic and calibration cadence

All four calibrations are **quarterly**; there is no monthly parameter. Daily rows carry the quarter's parameters by `Q FY` label.

### 4.1 F&O broking: `backtesting F&O` columns `AE:AG` (rows 4–761)

```
S   = R + P                                       index-option (NSE) + BSE contracts, raw count   (R = BSE col I, P = NSE index options)
AE  = VLOOKUP(Q FY, assumptions!$B$26:$L$36, 8)    share I   (rows ≥ 747: $B$26:$L$37; typed-by-hand extension for Q3 FY27)
AF  = AE × (S / 1e7) × VLOOKUP(Q FY, same range, 11)   L_q   → Rs Mn  (gross)
AG  = HLOOKUP(Q FY, assumptions!$B$111:$R$113, 3) × AF  net/gross F&O   (rows ≥ 746: $B$111:$S$113)
Summary: AVERAGEIFS(AG, key, label) / 10  → Rs Cr
```
Quarter table (`assumptions!B26:L37`): `E` days = `COUNTIF`; `F = SUMIF(S)/1e7`; `G = (SUMIF(J)+SUMIF(M))/E` (avg premium ADTO); `H = G/F`; `J = I × G`; `K = J/H`; `L = (C/K) × 10`; `I35 = AVERAGE(I33:I34)`, `I36 = I35`, `I37 = I36`; `L36 = L35`, `L37 = L36`.
**Identity:** `AF = I × S/1e7 × (10 C / (I F)) = 10 C × S/F`, so the share cancels and **Σ_q AF = 10 × reported gross F&O revenue** for every calibrated quarter, and for estimate quarters `AF = 10 × C_Q1FY27 × S_d / F_Q1FY27`: revenue per index-option contract held at the Q1 FY27 level.
Rows 4–127 (Q3, Q4 FY24) are `#N/A` (no table row); rows 128–252 (Q1, Q2 FY25) are numeric **0** (blank `L27`, `L28`; row 169 is `#VALUE!`); the first non-zero day is 1 Oct 2024 (row 253).
**Worked example, 14 May 2026 (row 652, Q1 FY27):** S = 644,612,887; I = 0.076911; L = 14.2759; AF = 0.076911 × 64.4613 × 14.2759 = 70.777 Rs Mn; net/gross 0.572963; **AG = 40.553 Rs Mn → Rs 4.055 Cr**.

### 4.2 Cash: `backtesting cash` columns `Y:AB` (rows 3–760; numeric from row 252 = 1 Oct 2024)

```
K   = I + J                                         NSE + BSE turnover (Rs Cr), cached from link [11]
Y   = VLOOKUP(Q FY, assumptions!$B$45:$J$54, 4)     share E
Z   = VLOOKUP(Q FY, assumptions!$B$45:$H$54, 7)     "delivery ratio" H   (=F/G)
AA  = Y × (K / Z) × ( VLOOKUP(.., $B$45:$J$54, 9) / VLOOKUP(.., $B$45:$D$54, 3) )     = E × K/H × J/D        Rs Cr (gross)
AB  = HLOOKUP(Q FY, assumptions!$C$111:$R$112, 2) × AA      (rows 252–760; range ENDS at R = Q2 FY27)
Summary: AVERAGEIFS(AB, key, label)   — no /10
```
Lookup ranges were extended by hand row by row (`$B$45:$J$52` for rows ≤ 681, `…53` ≤ 745, `…54` after): **the engine must be calendar-driven**.
**Identity:** `Σ_d AA = (ΣK/H_q) × E × J/D = G × J = I` (reported gross cash revenue) in every quarter where `J = I/G`: the share cancels, revenue is spread over days in proportion to ADTO. **Q1 FY27 is the exception:** `J52 = J51`, so `Σ AA = G52 × J51 = 224.98` instead of the typed 228 (−1.5% vs 228.30 in the data book). **Estimate quarters:** `E53 = E52`, `H53 = AVERAGE(H50:H52)`, `J53 = J52`, `D53` = days so far (65), so `Σ AA = E × (ΣK/D) × J / H = 0.068 × 129,408 × 0.063338 / 2.7846 = 200.16`: the take rate `J` is **per quarter**, so a 65-day quarter earns the same total as a 60-day one (issue #6).
**Q3 FY27 (rows 748–760, 13 days):** `AA` is computed (`D54` = 13 days so far gives **AA760 = 15.46 vs ≈ 3 in Q2**, a ×5 inflation) but `AB` is `#N/A` because the `HLOOKUP` range stops at column R. The inflation is hidden by the `#N/A`.
**Worked example, 14 May 2026 (row 651):** K = 154,990.89; E = 0.068; H = 2.78748; J = 0.0633378; D = 60 → AA = 0.068 × 154,990.89 / 2.78748 × 0.0633378 / 60 = **3.9913 Cr**; × 0.541569 = **AB 2.1616 Cr**.

### 4.3 Commodities: `Commodities` columns `L, M, O` (rows 2–661)

```
M   = "Q" & quarter-of-FY & " " & FY (formula on the date)
L   = (F/1e6) × HLOOKUP(M, assumptions!$B$59:$K$74 (rows ≤ 581; $B$59:$L$74 after), 4) × HLOOKUP(M, same, 16)     share (row 62) × take (row 74)   → Rs Mn (gross)
O   = HLOOKUP(M, assumptions!$C$111:$R$114, 4) × L        net/gross commodity (row 114)         (rows 2–654)
Summary: AVERAGEIFS(O, key, label) / 10
```
Quarter table (`assumptions!C59:L78`): `C60:J60 = 'Working Sheet - MOSL'!J53:R53` (gross revenue Cr), `K60 = 55` typed; `C62:J62 = 'Working Sheet - MOSL'!J73:R73` (share), `K62 = 0.077` typed, **`L62 = AVERAGE(H62:K62)`**; `C65 = SUMIF(Commodities!M, q, F)/1e6`; `66 = share × contracts`; `C74 = revenue(Mn)/row 66`; **`L74 = K74`**.
**Identity:** in calibrated quarters `Σ L = 10 × reported gross` (the share cancels); in Q2 FY27 `L = F × 0.0870 × 7.3265`, so the share does **not** cancel: the carried take rate was solved with the Q1 FY27 share 0.0770, applied with the four-quarter average 0.0870 (+13%).
Columns `G:K` (Angel / Groww) and `N` (Angel contracts per order) are not read. **Q3 FY27:** `M = 'Q3 FY 2027'` has no column in `B59:L74`, so `L` is `#N/A` for rows 648–661; `O` is `#N/A` for rows 648–654 and **blank for rows 655–661** (formula not extended).
**Worked example, 14 May 2026 (row 548):** F = 53,827,133; share 0.077; take 7.326509; L = 53.827 × 0.077 × 7.3265 = 30.366 Rs Mn; × 0.608897 = **O 18.490 Rs Mn → Rs 1.849 Cr**.

### 4.4 MTF: `MTF data (2)` columns `V:X` (rows 12–506)

```
V   = VLOOKUP(FY Quarter, assumptions!$B$5:$E$15, 4)         share E = C / D   (MOSL closing book ÷ industry closing book)
W   = V × I                                                  MOSL daily book (Rs Cr)
X   = W × VLOOKUP(FY Quarter, assumptions!$B$5:$F$18, 5) / 247    NII yield F, per trading day     → Rs Cr (Summary reads X directly)
```
`D8:D14` = industry book on the last quarter date that has one (`MAXIFS` + `XLOOKUP`), `C` = reported closing book, `E15 = E14`, `F15 = F14` (Q2 FY27 carries). Rows 507–518 (1–19 Oct 2026, 12 days) have **no formulas**; `V` and `X` are blank, so the MTF series (and every MTF window) ends on 30 Sep while `I` runs to 19 Oct. No gross/net layer: MOSL MTF is **NII-based** and `X` is read as is.
**Share definition:** closing-book ratio on a single date, applied to the whole quarter's daily book. At Q2 FY27 the carried share 5.776% gives a 30 Sep MOSL book of 8,729 vs 9,600 reported (−9.1%; reported share 6.35%).
**Worked example, 14 May 2026 (row 410):** I = 121,761.47; V = 7,800 / 135,044.20 = 0.0577589; W = 7,032.80; X = 7,032.80 × 0.129383 / 247 = **Rs 3.6839 Cr**.

### 4.5 MOSL-specific mechanics the engine must replicate

1. **Silent zeros.** Every FY / quarter / month cell is `IFERROR(…,0)`. `AVERAGEIFS` returns an error if **any matched cell is an error**, so FY 2027 cash (13 `#N/A` rows) and FY 2027 commodities (7 `#N/A` rows) are **0**, not an average of the numeric days. Parity mode must give 0 only where the workbook does; live mode should raise (issue #1).
2. **Different feeder end dates**: F&O to 21 Oct; cash, commodities, MTF numeric to 30 Sep. FY 2027 F&O includes 13 October days; FY 2027 MTF is April–September. Window statistics follow each segment's own dates.
3. **Roll horizon.** Typed tables end at Q3 FY27 (`assumptions` row 37 F&O, 54 cash) or Q2 FY27 (`L59`, `R111:R114`, `B15`); F&O was extended by hand (`$L$37`, `$S$113`) from row 747/746; for cash the share/ratio/rate lookups were extended to row 54 and commodity `L` to column L, but the **net-ratio lookups (cash `AB`, commodities `O`) stop at column R**. The next roll breaks `AE`/`AF` (Q4 FY27), `Y:AB` and `L`.
4. **Row alignment is not uniform**: cash panel one row below commodities; weekday blocks follow the same offset. Parity needs the label-based lookup, not row arithmetic.
5. **Special sessions** (1 Nov 2024, 1 Feb 2025, 21 Oct 2025, 1 Feb 2026) carry full revenue and enter every average; Angel/Groww parity does the same.
6. **Trading-day bases differ by segment** (F&O 65, commodities 66, MTF 65 in Q2 FY27; MTF 59 vs 60 in Q1 FY27).

---

## 5. Backtest / reconciliation

The workbook has no formal MOSL backtest block (Angel has `backtesting F&O!AP4:AS9`; MOSL has only the display checks `assumptions!K46:K53` "calculated" vs "reported rev" and `C76:L76`). I compared Σ daily model with the data book (`Consol`, Q2 FY27 book, columns `H…Q`), gross and net, Rs Cr:

| Segment, model vs reported (net, Rs Cr) | Q3 FY25 | Q4 FY25 | Q1 FY26 | Q2 FY26 | Q3 FY26 | Q4 FY26 | **Q1 FY27** | **Q2 FY27 (estimate)** |
|---|---|---|---|---|---|---|---|---|
| F&O | 135.25 / 134.98 (+0.21%) | 106.94 / 107.12 (−0.17%) | 108.82 / 108.82 (0.00%) | 111.50 / 111.50 | 119.87 / 119.87 | 116.72 / 116.58 (+0.12%) | 118.03 / 117.80 (+0.20%) | **102.81 / 110.15 (−6.66%)** |
| Cash | 128.13 / 127.95 (+0.14%) | 91.10 / 91.32 (−0.24%) | 149.42 / 149.42 | 108.62 / 108.62 | 104.71 / 104.71 | 101.99 / 101.85 (+0.14%) | 121.84 / 123.64 (**−1.46%**) | **108.21 / 132.03 (−18.05%)** |
| Commodity | 25.03 / 25.03 | 25.30 / 25.30 | 27.80 / 27.80 | 28.85 / 28.85 | 46.44 / 46.44 | 50.87 / 50.87 | 33.49 / 33.32 (+0.51%) | **50.74 / 34.46 (+47.25%)** |
| **Total broking** | | | | | | | 273.36 / 274.76 (−0.51%) | **261.76 / 276.64 (−5.38%)** |

Gross, Q2 FY27: F&O 179.13 vs 188.47 (−4.95%), cash 200.16 vs 237.79 (−15.83%), commodities 86.47 vs 57.97 (+49.17%). MTF closing book: model 8,729 vs reported 9,600 (−9.1%); the data book has no MTF revenue, so the NII ADR has no reported comparator.

**Read-out.**
- Calibrated quarters tie by construction (to rounding), so the table above is the arithmetic, not predictive power.
- **The Q2 FY27 numbers are the first pre-report test of the estimate rules, and the workbook's headline quarter misses by −5.4% (net).** Reasons: cash share carried at 6.80% (reported 7.97%) and the per-quarter take rate not scaled for 65 vs 60 days (issue #6); commodity take rate carried at 7.33 (Q1 FY27) when the reported quarter implies about 5.4 Rs/contract (57.97 Cr over 0.0785 × 1,357 Mn contracts), together with a share of 8.70% (reported 7.85%); F&O index-option volume fell 13% quarter on quarter while reported revenue fell 8%.
- On reported net revenue, Q2 FY27 Broking ADR is 110.15/65 + 132.03/65 + 34.46/66 = 1.695 + 2.031 + 0.522 = **4.248**, against 4.015 in the workbook (−5.5%).
- Store a **pre-report estimate snapshot** per quarter (as for Groww); Q3 FY27's will be the next test.

---

## 6. Estimate-regime rules currently in the workbook

| Segment | Parameter | Rule in Excel | Cells |
|---|---|---|---|
| F&O | Share (cancels) | Q1 FY27 = mean of last two typed shares; then carry | `assumptions!I35 = AVERAGE(I33:I34)`, `I36 = I35`, `I37 = I36` |
| F&O | Revenue per contract | Q1 FY27 calibrated to the **rounded typed 206**; Q2, Q3 FY27 carry | `C35`, `L35`, `L36 = L35`, `L37 = L36` |
| F&O | Net/gross | Q2 FY27 = mean(Q4 FY26, Q1 FY27); Q3 carry | `R113 = AVERAGE(Q113,O113)`, `S113 = R113` |
| Cash | Share | Typed 0.068 for Q1 FY27; then carry | `E52` (typed), `E53 = E52`, `E54 = E53` |
| Cash | "Delivery ratio" H | Trailing 3 quarters (Q3 FY27 includes the Q2 estimate) | `H53 = AVERAGE(H50:H52)`, `H54 = AVERAGE(H51:H53)` |
| Cash | Take rate J | **Q1 FY27 = Q4 FY26** (typed `I52 = 228` ignored); then carry; per quarter, not per day | `J52 = J51`, `J53 = J52`, `J54 = J53`; `D53`, `D54` = days so far |
| Cash | Net/gross | Q2 FY27 = mean(Q4 FY26, Q1 FY27); **Q3 FY27 absent** | `R112 = AVERAGE(Q112,O112)`; range `$C$111:$R$112` |
| Commodities | Share | **Mean of the last four quarters** (Q2 FY26 … Q1 FY27) | `L62 = AVERAGE(H62:K62)` |
| Commodities | Take rate | Carry Q1 FY27 | `L74 = K74` |
| Commodities | Net/gross | Mean(Q4 FY26, Q1 FY27); **Q3 FY27 absent** | `R114` |
| MTF | Share, NII | Carry Q1 FY27 | `E15 = E14`, `F15 = F14` |
| MTF | Day basis | Literal 247 | `MTF data (2)!X12:X506` |
| Display only | Net/gross trailing-4 | `R97:R100 = AVERAGE(Q97, M97:O97)` | Differs from the trailing-2 `R112:R114` used by the chain |
| Display only | F&O Q2 FY27 projection | `D36 = (K36·L36/10)·(60/E36)` = 165.35 vs the daily chain's 179.13 (the factor `60/65` is a copy of Q1's 60 days) | `D36`, `O36`, `R86` |

The rules differ across segments and parameters (carry vs trailing-2/3/4). See decision D9.

---

## 7. Issues found (ranked by impact on the ADR)

1. **HIGH: FY 2027 YTD mixes four bases and shows cash and commodities as 0.**
   - Q3 FY27 days: `backtesting cash!AB748:AB760` are `#N/A` (the `HLOOKUP` range `$C$111:$R$112` ends at Q2 FY27), `Commodities!O648:O654` `#N/A` and `O655:O661` blank. `AVERAGEIFS` over a range that holds an error returns the error and `IFERROR` makes it 0. F&O includes 13 October days; MTF is April–September.
   - Shown: `M64` (cash) 0, `C63` (commodities) 0, Broking `M7` **1.805** (F&O only), Consolidated `C7` **5.793**. With the error days skipped: cash 1.840, commodities 0.648, Broking **4.294**, Consolidated **8.281**.
   - Effect: FY YoY shown Broking `N7` −58.3% (vs −0.85% corrected), Consolidated `D7` −24.2% (vs **+8.3%**), cash `N64` and commodities `D63` = −100%.
   - This **extends H7**, which names the cash zero only; commodities fail the same way.
2. **HIGH: the MOSL panel of `SUMMARY - Brokers` is about 17% below reported (audit H7, verified).**
   - Cells: `AH63` (FY27) 3.599 vs `SUMMARY - Motilal Oswal!M7` 1.805; Q1 FY27 `AH67` 3.808 vs `M12` 4.521 vs reported net 274.76 Cr / 60 days = 4.579 (**−16.8%**; the audit's −16.9% uses the rounded 275). The MOSL sheet is −1.3% to reported.
   - Causes, all confirmed: (a) the Brokers panel reads **gross** F&O `AF` and gross cash `AA`; (b) it **divides cash `AA` by 10** though `AA` is already in Rs Cr; (c) commodities `AH145`, `AH149` are **typed 0**; (d) stale labels (`AG68` and `AG69` both read `Q4 FY 2026`).
   - Q1 FY27 bridge, Rs Cr/day: F&O gross 3.433 vs net 1.967 (+1.466); cash 0.375 vs 2.031 (−1.656); commodities 0 vs 0.523 (−0.523); total −0.713.
   - The silent zero H7 describes is the same mechanism as issue #1 (`AB760` `#N/A`). H7's "reported cash 118" is not the data book: net cash is **123.64** (F&O 117.80), see #12.
3. **HIGH: the "YoY" quarter row is Q4 FY26, not Q2 FY26.** `L13` is typed `Q4 FY 2026`, so `E11`, `O11`, `E39` … compare Q2 FY27 with a quarter two back. Broking "YoY" shows **−9.6%** (true YoY vs Q2 FY26: **+3.4%**); Consolidated +7.6% (true +11.3%); F&O −18.7% (true −9.2%); commodities −3.3% (true **+73%**); MTF +30.7% (true +19.8%).
4. **HIGH: the headline quarter is a pure estimate and misses by 5.4% (§5).** Q2 FY27: cash −18%, commodities +47%, F&O −7%; MTF book −9%. The data book was published on 29 Oct 2026; the workbook still estimates.
5. **MED: the cash allocation key is two trading days out of alignment since 9 Jun 2025.**
   - Evidence in the workbook: correlation of `K` (turnover) with trades is 0.84 at lag 0 before 9 Jun 2025 but 0.82 at lag 2 (0.48 at lag 0) after; `docs/Mistakes_Register.md` X-03 and `Data_Lake_Review_Angel_ADR.md` §2 document the same shift (Excel 11 Jun = lake 9 Jun). The register calls it display-only: true for Angel and Groww, **not for MOSL, whose cash daily allocation key is `K`**.
   - Effect (re-aligned, approximate, last two days held): period averages move ≤ 0.8% (FY27 −0.4%, Q2 FY27 −0.8%), but **day-level values differ by a median 8%, 90th percentile 26%**, and the "last 5 days" cash ADR moves from 1.534 to about 1.72. Weekday and last-N statistics are affected, quarter ties are not.
6. **MED: cash estimate is not scaled for the number of days, and Q3 FY27 is latent ×5.** `J` is revenue ÷ ADTO per quarter, so Q2 FY27 (65 days) earns the same total as a 60-day quarter (−7.7% on days alone). In the partial quarter `D54` = 13 gives `AA` = 15.46 vs about 3.0: extending the `HLOOKUP` range without fixing `D` would multiply Q3 FY27 cash by about 5.
7. **MED: Q1 FY27 reported values are not fed, and typed inputs are rounded.** Cash `J52 = J51` (reported 228 / 228.30 ignored): −1.46% and the Q4 FY26 take rate is carried forward; F&O 206 (205.60, +0.20%), commodity 55 (54.72, +0.51%), Q4 FY26 F&O 203 (202.76), cash 189 (188.74); shares 0.07 / 0.068 / 0.077 vs 0.0703 / 0.0678 / 0.0772. The rounded commodity share enters the Q2 FY27 average.
8. **MED: the F&O activity key is index options + BSE only, and BSE is about half of it.** Revenue of all F&O (incl. stock options and futures) is allocated by `S`; BSE is 46–50% of `S` and BSE expiry days carry 340–513 Mn contracts. Q2 FY27 daily F&O net ranges 4.7–39.9 Rs Mn (median 11.5, CV 0.57); 1 Oct 2026 is 37.8. Weekday, last-5 and last-20 F&O statistics are dominated by expiry-day mix, not by revenue.
9. **MED: MTF is thinly sourced.** The nine NII yields (`F6:F14`, 11.9–15.5%) have no source and equal no data-book cell; the share is a one-day closing-book ratio applied to a whole quarter; 247 is a literal; the series stops 30 Sep while the industry book runs to 19 Oct; Q1 FY27 has 59 days vs 60 equity days; Q2 FY27 share is carried (model book −9.1%). `D6:D7` and the daily industry book are unsourced. [SOURCE NEEDED]
10. **MED: non-contemporaneous windows.** Broking and Consolidated "last 5 / 20 / 45 days" and weekday cells add segments measured over different dates (F&O to 21 Oct, others to 30 Sep). "Last 5 days" Broking 4.526 is not a coherent week.
11. **LOW/MED: "Avg Of Last 6 Months"** is the mean of two quarter ADRs (Q1, Q2 FY27), not six months and not day-weighted: Broking 4.268 vs the month-weighted figure; "Mo 6M" ratios inherit it.
12. **LOW: downstream and typed-data defects.**
    - `PAT predictor Q1FY27!N30:O30` are typed 124 / 118 as "Actual reported" F&O / cash; the data book has net F&O 117.80 and net cash 123.64, so the two look **swapped** (sum 275 unaffected).
    - `PAT predictor` uses `Working Sheet - MOSL!T62:T64 = AVERAGE(S,N,I)` (the **annual** FY26, FY25, FY24 net ratios) instead of the quarterly ratio the Summary chain uses.
    - `Motilal Oswal - Final` is a Groww/Angel hybrid with `#REF!`; `Motilal Oswal Charts!AC` returns the MOSL cash market share instead of cash revenue (lookup index 24 vs 26) and mixes gross Rs Mn lines.
    - `assumptions!D36/O36` (60/65 factor), `D15 = I501` (23 Sep), `backtesting F&O!P169` typed `' '`.
13. **LOW: stray cells and conventions.** `K144:K163` typed zeros (15 cells); F&O Q1–Q2 FY25 numeric 0; special sessions included; trading-day bases differ (F&O 138, cash 125 numeric, commodities 130 numeric, MTF 124 numeric in FY27); the Q1/Q2 FY25 shares in the F&O table are never read.

Angel-doc and Groww-doc issues that do **not** apply to MOSL: BSE F&O freeze (MOSL reads `R`, live), Angel orders/CPO coupling, ADTO-share applied to orders, FY26 zero-fill, stale panel labels, MTF gross/net mismatch in the Summary (the Brokers panel has its own, issue #2).

---

## 8. Recommended logic for the engine

### 8a. Data model additions (reuse the Angel tables; add `broker_id = 'MOTILALOFS'`)

| Table | Grain | New fields / metrics |
|---|---|---|
| `mosl_quarterly` (facts, from the data book `Consol`) | q_fy | `gross_cash_cr, gross_fo_cr, gross_comm_cr, net_cash_cr, net_fo_cr, net_comm_cr` (Rs Cr); `adto_cash_mosl` (Rs Cr/day); `share_cash, share_fo, share_comm` (fractions, F&O = premium share); `mtf_book_closing` (Rs Cr); `source_doc, page/cell` (e.g. `Consol!Q52`) |
| `assumptions` | key | `mtf_nii_yield` by quarter [SOURCE NEEDED], `mtf_day_basis` 247, `comm_share_rule` (avg last 4), `net_gross_rule` (avg last 2), `cash_hr_rule` (trailing 3), `first_live` per segment (F&O 2024-04-01 zero, 2024-10-01 numeric; cash and MTF 2024-10-01; commodities 2024-04-01) |
| `sb_market_daily` (new metrics; Angel needs total F&O, MOSL needs the split) | date | `nse_fo/index_opt_contracts`, `bse_fo/contracts` (live, **not** the frozen copy), `nse_cash/turnover_cr`, `bse_cash/turnover_cr` (**correctly aligned**, issue #5), `mcx/contracts`, `mtf_industry/book_cr`; premium ADTO is not needed for the output |
| calendar | date | `is_live_fo, is_live_cash, is_live_comm, is_live_mtf`; `special_session` (as Angel) |

Metric names match the Angel/Groww loader where the meaning matches (`share_*`, `mtf_industry:book_cr`, `mtf_book_closing`, `gross_*`/`net_*`); MOSL-only: `adto_cash_mosl`, `mtf_nii_yield`, `net_gross_*`. Every fact carries document and cell; every `[SOURCE NEEDED]` in `workbook_inputs.json` needs a filing-extractor pass (NII yield, industry book before 1 Oct 2024, daily industry book).

### 8b. Compute pipeline (parity mode)

```python
# ---- MOSL borrows NOTHING from Angel: no contracts/order, trades/order, orders, Angel share, Angel take rate.
# ---- Reuse from the engine: calendar, sb_market_daily loader, Summary aggregator (windows, weekday, sums), parity harness.

# ---- quarterly calibration (all quarters in the data-book facts; typed/rounded values in parity mode)
for q in Q3FY25 .. Q1FY27:
    # F&O
    F[q]  = sum(idxopt[d] for d in days(q)) / 1e7                    # idxopt = NSE index options + BSE contracts (raw count)
    G[q]  = (sum(nse_idxopt_adto[d]) + sum(bse_opt_adto[d])) / n_days(q); H = G / F
    K     = share_fo[q] * G / H                                      # = share * F ; share cancels
    L_fo[q] = gross_fo[q] / K * 10                                   # Rs Mn per Cr contracts
    # cash
    C = sum(adto[d] for d in days(q)) / n_days(q); Fc = share_cash[q] * C; H_c[q] = Fc / adto_mosl[q]
    J[q] = gross_cash[q] / adto_mosl[q]                              # parity: Q1FY27 uses J[Q4FY26] (J52 = J51); gross_cash[Q1FY27]=228 is NOT used
    # commodities
    cont = sum(mcx[d] for d in days(q)) / 1e6
    take_c[q] = gross_comm[q] * 10 / (share_comm[q] * cont)          # Rs per MOSL contract
    # MTF
    share_mtf[q] = mtf_book_closing[q] / ind_book[last_date_with_book(q)]
share_fo[Q1FY27] = mean(share_fo[Q3FY26], share_fo[Q4FY26]); share_fo[Q2FY27..] = share_fo[Q1FY27]
L_fo[Q2FY27..] = L_fo[Q1FY27]
share_cash[Q2FY27..] = share_cash[Q1FY27]; H_c[Q2FY27] = mean(H_c[Q3FY26..Q1FY27]); J[Q2FY27..] = J[Q1FY27]
share_comm[Q2FY27] = mean(share_comm[Q2FY26..Q1FY27]); take_c[Q2FY27] = take_c[Q1FY27]
share_mtf[Q2FY27] = share_mtf[Q1FY27]; nii[Q2FY27] = nii[Q1FY27]
ratio_x[Q2FY27] = mean(ratio_x[Q4FY26], ratio_x[Q1FY27]) for x in (fo, cash, comm); ratio_fo[Q3FY27] = ratio_fo[Q2FY27]

# ---- daily revenue
fo_net_mn[d]   = ratio_fo[q] * share_fo[q] * idxopt[d]/1e7 * L_fo[q]                 # Rs Mn   (zero for Q1-Q2 FY25; none before)
cash_net_cr[d] = ratio_cash[q] * share_cash[q] * adto[d] / H_c[q] * J[q] / n_days_so_far(q)   # Rs Cr; PARITY: n_days_so_far = COUNTIF of rows in the sheet;
                                                                                              # no value for Q3 FY27 (lookup range ends at R)
comm_net_mn[d] = ratio_comm[q] * (mcx[d]/1e6) * share_comm[q] * take_c[q]                    # Rs Mn   (none for Q3 FY27)
mtf_nii_cr[d]  = share_mtf[q] * ind_book[d] * nii[q] / 247                                   # Rs Cr   (none after 30 Sep)

# ---- Summary (one aggregator for every panel)
adr(seg, period) = mean(rev[seg, d] for d in period, zeros included, blanks excluded)
                   / (10 if seg in (fo, comm) else 1);  if any matched row is an error value -> parity: 0 (IFERROR); live: raise
windows (last 5/20/45, previous 5, weekday latest/last3/last10): per segment, over that segment's own numeric dates
Broking = F&O + Cash + Commodities ;  Consolidated = Broking + MTF                          # sums of segment ADRs, label-aligned
```

Test hooks: `out/mosl/summary_expected.json` (264 cells, tolerance 1e-9) and the four cached daily columns (`backtesting F&O!AG`, `backtesting cash!AB`, `Commodities!O`, `MTF data (2)!X`; plus gross `AF`, `AA`, `L`). The reference aggregator **`/private/tmp/claude-501/-Users-abhishekbiyani-Documents-broker-dashboard/4f78fff7-ca02-4af2-8c4c-b57322f6b69d/scratchpad/mosl/parity.py`** reproduces all 264 from the cached daily rows; **`…/scratchpad/mosl/derive.py`** reproduces the four daily columns from raw exchange columns and the typed inputs (max abs diff 0.0). Build the daily layer first, then the Summary. Closed forms (share cancels) agree with the literal chain to 4e-16 relative for F&O (tested); the parity run should still follow the literal chain above.

### 8c. Parity mode vs corrected mode

Keep a **parity mode** that reproduces every quirk: silent zeros, the FY27 YTD basis, `J52 = J51`, rounded typed inputs, the Q4 FY26 "YoY" row, the misaligned cash key, the per-quarter cash take rate, 247, the typed NII yield, per-segment windows. Each correction is one named switch with a before → after bridge (as for Angel): (a) **FY/quarter statistics only over fully covered periods, or Q3 FY27 fed**, so FY27 YTD is on one basis (D3); (b) **feed reported quarters** (Q1 FY27 cash `J`, unrounded data-book values, and Q2 FY27 now) (D5); (c) **YoY comparator = same quarter last year** (D4); (d) **cash key re-aligned** from the lake (D6); (e) cash estimate scaled by days (D9); (f) commodity share/take-rate rule (D9); (g) MTF yield sourced and day basis (D8); (h) **common window end date** across segments (D11); (i) special sessions out of the statistics, as Angel switch d.

---

## 9. Decisions needed from AB

| # | Decision | Excel today | Suggested |
|---|---|---|---|
| D1 | Parity first, then corrected switches? | | Yes |
| D2 | MOSL revenue basis | Net brokerage in the Summary; Brokers panel gross F&O/cash | Net for the Summary (what the data book calls net brokerage); show gross beside it; confirm the basis used for the cross-broker comparison with Angel/Groww (their series are total-income based) |
| D3 | FY27 YTD with uncovered days (cash, commodities, MTF in Q3 FY27) | 0 (silent) / mixed | Parity: keep. Live: extend the estimate rules to Q3 FY27, or flag the period as partial and show only covered segments; never 0 |
| D4 | "YoY" quarter row | Q4 FY26 (typed) | True same-quarter-last-year (Q2 FY26), driven from the calendar |
| D5 | Load the Q2 FY27 data book (29 Oct 2026) and recalibrate; use unrounded values and feed Q1 FY27 cash | Rounded typed values; Q1 FY27 cash not fed | Yes: Q2 FY27 becomes calibrated; one filing-extractor pass over `Consol` rows 44–74; keep the pre-report snapshot for the bridge |
| D6 | Cash turnover key alignment | Two rows off since 9 Jun 2025 | Take NSE and BSE turnover from the lake aligned to date; keep the Excel series for parity |
| D7 | F&O activity key | NSE index options + BSE contracts | Keep for parity; test premium turnover or all-F&O contracts, and expiry-day weighting, as corrected switches |
| D8 | MTF: NII yield source, day basis | Typed 11.9–15.5%, no source; 247 | Source the yield (results / presentation, not the data book); day basis = trading days of the FY; show the industry book end date |
| D9 | Estimate rules | Carry, trailing-2/3/4, share-average, per-quarter cash rate | One rule per parameter type in `assumptions` (as Angel D6), cash scaled by days, commodity share carried not averaged; label every quarter "estimate" until the data book is loaded (3–4 weeks after quarter end) |
| D10 | "Latest" period | Last complete quarter / month; FY27 YTD includes October for F&O | Last complete period plus a QTD/MTD row; one end date per period |
| D11 | Windows across segments | Each segment's own dates | Common end date (the earliest segment end) for Broking and Consolidated |
| D12 | Source of record for MOSL facts | Link `[12]` to a Downloads copy of the Q1 FY27 book | Data books from `motilaloswal.com` per quarter (URLs not stable, match on labels, row positions move); restatements checked (Q1 FY26 total gross revenue 2,016.4 → 2,018.2; brokerage rows unchanged) |
| D13 | Roll horizon | Typed tables end Q2/Q3 FY27 | Calendar-driven engine; no table-bound lookups |
| D14 | `Motilal Oswal - Final`, `Motilal Oswal Charts`, `SUMMARY - Brokers` MOSL panel | Hybrid / mixed units / 17% low | Out of scope for parity; rebuild from the corrected series, repair or retire |

---

## 10. Cell map (for reference)

| Item | Cells |
|---|---|
| Summary panels | Consolidated `B3:J25`, Broking `L3:T25`, MTF `B30:J53`, F&O `L30:T53`, Commodities `B58:J81`, Cash `L59:T82`; stray `K144:K163` |
| Summary labels (typed) | `L7:L8`, `L11:L13`, `L16:L17`; MTF `B36` |
| F&O daily | `backtesting F&O!B4:AG761` (MOSL `AE:AG`; `#N/A` rows 4–127, numeric 0 rows 128–252, first non-zero row 253 = 1 Oct 2024; Q3 FY27 rows 749–761); key `S = R + P` |
| F&O quarterly | `assumptions!B26:L37` (revenue `C`, share `I`, contracts `F`, ADTO `G`, rate `L`), net/gross `B111:S113` (chain reads `G:R`, `S113`) |
| Cash daily | `backtesting cash!B3:AB760` (MOSL `K, Y:AB`; numeric from row 252; Q3 FY27 rows 748–760 `#N/A`) |
| Cash quarterly | `assumptions!B45:N54` (share `E`, reported ADTO `G`, reported revenue `I`, `H`, `J`, `K` check), net/gross `C111:R112` |
| Commodities daily | `Commodities!B2:O661` (MOSL `L, M, O`; Q3 FY27 rows 648–661) |
| Commodities quarterly | `assumptions!B59:L78` (revenue 60, share 62, contracts 65–66, take 74), `Working Sheet - MOSL!J53:R53`, `J73:R73`, net/gross row 114 |
| MTF daily | `MTF data (2)!B12:X518` (MOSL `V:X` rows 12–506; industry book `I`) |
| MTF quarterly | `assumptions!B5:F18` (closing book `C`, industry `D`, share `E`, NII `F`) |
| Data book | external link `[12]`, sheet `Consol`; `assumptions!C84:Q94, C103:Q103` (live links); `Working Sheet - MOSL!B1:S80` (typed copy, 411 numeric cells in rows 44–80) |
| Exchange link | `[11]` `20260121_Exchanges_Dashboard.xlsx`, sheets `NSE F&O`, `BSE F&O`, `NSE Cash`, `BSE Cash`, `MCX Data Clean` |
| Downstream | `MOSL charts`, `Motilal Oswal Charts`, `Motilal Oswal - Final`, `PAT predictor Q1FY27!N21:Q30`, `PAT predictor Q2FY27!N21:Q31`, `SUMMARY - Brokers!AG59:AO` and `(A+B)` |
| Parallel work | Data-book download, disclosure map and filings inventory: `out/mosl/disclosure_map.md`, `filings_inventory.json`; raw books `data/raw/disclosures/mosl/` |
