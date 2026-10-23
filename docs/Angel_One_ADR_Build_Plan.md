# Angel One ADR Tracker — Build Plan v2 (verified 23 Oct 2026)

v1 (22 Oct) was written before we found the data lake and before the engine existed. v2 records:
- what is now built and verified;
- the errors found in v1 and in the workbook;
- the revised plan to a live dashboard.

Companion docs: `Angel_One_ADR_Methodology.md` (formulas), `Data_Lake_Review_Angel_ADR.md` (sources), `Engine_Parity_Status.md` (engine).

---

## 1. Where we are

| Item | Status | Evidence |
|---|---|---|
| Supabase `brokers-dashboard` (ref `everjfpbnlbcpuarnhob`, Mumbai), `sb_*` schema | Built (by another session); audited | 477 facts, 11,011 daily rows, 33 monthly rows, 785 calendar days: every value equals its Excel cell |
| Data-lake copies alongside the Excel values | Loaded and reconciled | All differences explained (Data Lake Review §2d) |
| Engine, parity mode | Built | **8,774 / 8,797 workbook values exact**; 23 out of scope (documented); 0 unexplained; 264 / 264 Summary cells |
| First run stored | Done | run `42e5519f…`, readable with the publishable key |
| Temporary loaders | Removed | none left in `pg_proc` |

---

## 2. Verification against primary filings (new)

### 2a. Back-sourcing: Excel inputs vs Angel's own PDFs — 20 checked, 20 match

| Filing | Values checked | Result |
|---|---|---|
| Business update, 4 Sep 2026 | Aug-25 orders 109.86, F&O share 22.1%, cash 18.6%, commodity 67.6%, funding book ₹52.91 bn; Jul-26 commodity share 48.0%; Aug-26 43.7% | all match |
| Business update, 6 Oct 2026 | Sep-25 orders 127.57, F&O 21.8%, cash 19.0%, commodity 64.3%, book ₹55.53 bn | all match |
| Press release, 15 Jul 2026 (Q1 FY27) | orders F&O 300, cash 67, commodity 40; shares 22.2 / 17.4 / 52.3 / 20.2%; total income ₹14,337 mn | all match |

### 2b. A typo in the workbook (resolved open point v1 §11.5)

The Q3 FY26 press release (15 Jan 2026) prints **Commodity orders 35, Total 380**. `Working sheet!J8` = 36 is a typo. Consequences:

| Affected | Workbook | Corrected |
|---|---|---|
| Q3 FY26 commodity take rate, `J78` = 0.06 × 13,376.97 / orders | ₹22.29 (÷36) | **₹22.93** (÷35) |
| `Commodities!AI11`, the fixed rate used for **every** commodity day | ₹22.29 | ₹22.93 → all commodity ADR **+2.86%** (36 / 35) |
| Q3 FY26 F&O % of orders (`J10`) | 277 / 381 = 0.7270 | 277 / 380 = 0.7289 |

Parity mode keeps 36 (it's what the workbook did). Live mode uses 35.

### 2c. First out-of-sample test: the workbook's Q2 FY27 estimates vs what Angel then reported

| Orders (Mn), Q2 FY27 | Model (projected) | Reported | Error |
|---|---|---|---|
| Total (Jul + Aug + Sep monthly updates: 134.68 + 109.50 + 122.29) | 381.3 | 366.5 | **+4.0%** |
| F&O | 257.8 | 256 | **+0.7%** |
| Cash | 76.2 | 66 | **+15.4%** |
| Commodity | 47.3 | 45 | **+5.0%** |

The segment split (256 / 66 / 45) is now confirmed from the primary filing: the Q2 FY27 press release (filed 15 Oct 2026, page 2). 256 + 66 + 45 = 367 vs 366.46 in the September update's quarterly table (+0.15%, rounding). The monthly totals are from the primary business updates.

**Shares the model used vs reported:**

| Segment | Used | Reported |
|---|---|---|
| F&O | 22.1% carried | Jul 22.2%, Aug 21.7%, Sep 22.5% |
| Cash | 17.4% carried | Jul 17.1%, Aug 17.0%, Sep 16.2% |
| Commodity | Sep carried at 43.7% | Sep 41.7% |

**Read-out:** the F&O method holds up well. Cash is the weak spot: a falling share plus a trades-per-order ratio averaged over a different regime. The Q2 FY27 revenue mix is now captured from the deck (slide 30: F&O 38.7%, cash 8.7%, commodity 7.1% of ₹14,315 Mn consolidated gross revenues), staged for review. The revenue-side accuracy test runs once those figures are approved.

---

## 3. Errors and gaps found in plan v1

| # | v1 said | Reality / fix |
|---|---|---|
| 1 | Stack: DuckDB on the Mac | **Supabase** (`brokers-dashboard`); the dashboard is a toggle in ExchangesDash (Vercel); the daily job can run on GitHub Actions like ExchangesDash |
| 2 | Filing name pattern `…_Intimation_of_Business_Update.pdf` | Names vary (e.g. `…_IntimationBU.pdf` on 5 Aug 2026, `…_Intimation_of_Business_updates.pdf` on 6 Oct 2026). **Detect by announcement subject/category in the NSE feed, not by file name**; keep `w3assets.angelone.in` as the fallback |
| 3 | Phase 3: build exchange collectors | NSE/BSE F&O contracts, BSE cash trades and MCX contracts already exist in the data lake and match. **Still missing: NSE cash trades** (owner prompt sent) and the **industry MTF book** (`codex_nse_mtf_daily`, access pending) |
| 4 | "Commodities use only MCX days with contracts > 0" | Precisely: FY / quarter / month averages include every MCX row; the > 0 filter applies only to last-N and weekday stats |
| 5 | "~200 Summary cells" | 264 |
| 6 | Revenue mix from "the investor presentation" | Confirmed: the press release has no mix (Q1 FY27 checked). The deck is required each quarter |
| 7 | Funding book check "quarterly ≈ average of monthly" | The Q3 FY26 press release gives a **period-end** book (₹58.6 bn, Dec-25), not an average. Store `funding_book_end` and `funding_book_avg` separately |
| 8 | Workbook is current | It is **one quarter behind**: Jul/Aug/Sep-26 monthly updates and Q2 FY27 results (16 Oct 2026) are published but not captured |

---

## 4. Engine code review — what must change for live mode

| # | Issue | Risk | Fix |
|---|---|---|---|
| E1 | Period ranges are hard-coded (`FY 2027 October`, `Q3/Q4 FY 2027`). Days in months beyond the table are **silently skipped** | **High:** November would simply vanish | Derive ranges from the calendar; a day with no calibration must raise or be flagged, never dropped |
| E2 | Inputs are looked up by Excel cell (`Working sheet!H6` …) | **High:** new facts (Q2 FY27) have no cell | Live loader by `metric × period` from `sb_facts_current`; cell lookups stay for parity only |
| E3 | Summary period labels are hard-coded (`PARITY_LABELS`) | Medium | Live labels from the data date + decision Q4 below |
| E4 | No guards for short history (last-45 with < 45 days, weekday with no dates, divide-by-zero) | Medium | Explicit "insufficient data" results |
| E5 | Integrity checks (missing days, freezes, 5×/0.2× jumps) are not implemented yet | Medium | Run before every engine run; block publishing on a failure |
| E6 | Engine reads a manual JSON export | Medium | A direct reader using a service key held as a GitHub secret (never in code) |
| E7 | The parity test compares the workbook with itself (inputs and outputs both come from the Excel) | Note | It proves the reproduction, not correctness. §2b–2c is the correctness evidence; keep doing the pre-report snapshot check each quarter |

---

## 5. Revised phases

| Phase | Deliverable | Exit test |
|---|---|---|
| **1. Parity** | Engine reproduces the workbook | ✅ done |
| **2. Catch up the facts** | Ingest Jul/Aug/Sep-26 monthly updates and Q2 FY27 (press release + deck + results) from primary PDFs; fix J8 (35); back-source every seeded fact | Every engine input traced to a PDF + page; mismatch log reviewed by AB |
| **3. Live engine** | E1–E6; live loader; one projection rule per parameter; special sessions excluded; data-lake exchange data (BSE unfrozen) | Each switch from parity to live shown as an ADR bridge (e.g. BSE unfrozen; Oct F&O 6.74 → about 11.67 under parity rules) |
| **4. Daily automation** | GitHub Actions: data-lake pull → integrity checks → engine → write `sb_*` outputs; filing watcher for Angel announcements → parse → staged facts → AB review | Two weeks of unattended runs without silent gaps |
| **5. Dashboard** | "Brokers" toggle in ExchangesDash reading `sb_summary_cells` / `sb_daily_revenue` (publishable key), with Actual/Estimate tags and the estimate-vs-reported page | Visual check vs Excel (parity run) and vs live run |

**Blocked on the data-lake owner:** NSE cash trades (the cash ADR can't move past 21 Oct 2026 without it) and MTF book access (same for MTF). Everything else can proceed.

---

## 6. Decisions (AB, 23 Oct 2026)

| # | Decision | What it means for the build |
|---|---|---|
| D1 | **The dashboard summary is laid out exactly like the `SUMMARY - Angel One` sheet**, with a **dropdown for each FY, quarter and month** | The engine stores ADRs for **every** FY, quarter and month (not just the workbook's hard-coded labels) in `sb_summary_cells` / a period table. Comparisons follow the selected period: YoY = same period last year; QoQ / MoM = prior period; 6-month = the six months ending at the selected month |
| D2 | **Cash projection uses the latest monthly cash market share from Angel's disclosures** | Replaces "carry last quarter's share". The engine uses the monthly `share_cash` for each month (the actual month when disclosed, else the latest one) |
| D3 | **Commodity take rate = each quarter's own** | Replaces the fixed Q3 FY26 rate (`AI11`); projected quarters use the projection rule |
| D4 | **MTF: a Gross section; Net = 45% of gross** | Every panel shows MTF gross; net is a separate line at 45% × gross (the weekday-only net quirk goes away in live mode). The 45% factor's basis is still [SOURCE NEEDED: basis for 45% net factor] |
| D5 | **Daily job on GitHub Actions** in a new repo under `abiyani-tools`; AB adds the Supabase service key as a repository secret | Repo + workflow skeleton created; the daily run is switched on once live mode passes its checks |
| D6 | **Review page**: each extracted figure beside its PDF page, with approve / flag | Staged facts become `reviewed` only through this page; the engine's live mode uses reviewed facts (plus seeds where nothing is reviewed yet) |
| D7 | **Catch-up started 23 Oct 2026** | 11 filings and 178 facts staged (Jun–Sep 2026 monthly, Q1/Q2 FY27, Q3 FY26 correction, Q2 FY27 deck revenue mix to one decimal for 9 quarters, 11 back-sourcing corrections) |
| — | Special sessions (Muhurat / DR test) are excluded from averages in live mode | (AB, 22 Oct) |
| — | Angel One first; every table keyed by broker for Groww / Motilal later | (AB, 22 Oct) |

### Catch-up evidence (23 Oct 2026)

- **Parser checks:** average daily orders × trading days ties to total orders within 0.1% in all six tables (Jun, Jul, Aug, Sep, Q1 FY27, Q2 FY27).
- **Back-sourcing of the filings' comparison columns against the seeded Excel values:** 101 / 112 exact. The 11 differences are Excel rounding or averaging and are staged as corrections:
  - quarterly funding book: Q4 FY26 ₹58.49 bn vs 58; Q1 FY26 42.06 vs 42.08; Q2 FY26 53.05 vs 53.08;
  - quarterly total orders: 343.11 vs 343; 360.43 vs 360;
  - client base and gross acquisition (display only).
- **Q2 FY27 deck, slide 30:** broking mix to one decimal for 9 quarters. In every quarter F&O + cash + commodity equals the slide's own gross-broking share (e.g. Q2 FY27: 38.7 + 8.7 + 7.1 = 54.5%). The basis ties to consolidated gross revenues (54.5% × ₹14,315 Mn ≈ ₹7,804 Mn gross broking on slide 26).
- **Revenue mix vs the Excel:** 30 deck values have an Excel counterpart. 4 match exactly, and 22 differ only because the Excel used whole percentages (e.g. Q1 FY27 F&O 45.1% vs 45%). Four differ by more than rounding: Q3 FY25 F&O 52.5% vs Excel 52.65% and commodity 4.4% vs 4.55%; Q4 FY25 F&O 46.3% vs 46.2% and commodity 5.2% vs 5.4%. The Excel values may come from an earlier deck (possibly restated): [SOURCE NEEDED: the Q3/Q4 FY25 decks the Excel used]. Live mode will use the one-decimal values from the latest deck once approved.
- **Review page (D6) published 23 Oct 2026:** "Angel One Figure Review" artifact. Decisions are stored with the page; `src/extract/apply_review.py` turns them into SQL. Approved → `status = 'reviewed'`; flagged → stays `staged` with the reviewer's note appended.
- **Q1 FY27 investor presentation was filed twice** (18:03 and an "update" at 18:49 IST). The later one is authoritative.
- **Q2 FY27 results were filed 15 Oct 2026**, not 16 Oct as press coverage said. The results PDF is mostly scanned (pp. 3–15). P&L lines aren't needed for the ADR and will be read later.
