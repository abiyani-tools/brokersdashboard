# PAT model vs AB's workbook PAT predictor (2026-11-06)

Workbook: `New model - 06.11.26/20260714_brokers dashboard v2 - new.xlsx`, sheet `PAT predictor Q2FY27` (cached values; the sheet `PAT predictor Q3FY27` is half-built: Q2 FY27 columns are 0). Model: `run_pat.py` dry run on the live ADR runs as of 2026-11-06 (`out/pat/2026-11-06/*_report.md`). Rs Cr. Diff = model − workbook. Report only: neither side changed.

## ANGELONE

### FY 2027

| Line | Workbook cell | Workbook | Model | Diff | Diff % |
|---|---|---:|---:|---:|---:|
| Broking revenue | `L42` | 3,267.4 | 3,503.8 | +236.5 | +7.2% |
| Depository income | `L44` | 198.7 | 203.4 | +4.8 | +2.4% |
| Distribution income | `L46` | 192.2 | 259.6 | +67.5 | +35.1% |
| MTF income | `L48` | 1,100.0 | 1,096.6 | -3.4 | -0.3% |
| Other interest income (treasury) | `L50` | 1,060.8 | 929.0 | -131.8 | -12.4% |
| Total income / revenue | `L52` | 5,819.0 | 6,060.2 | +241.1 | +4.1% |
| Finance cost | `L61` | 629.8 | 577.0 | -52.8 | -8.4% |
| Fees & commission | `L62` | 797.4 | 830.5 | +33.1 | +4.2% |
| Impairment | `L63` | 3.2 | 2.1 | -1.1 | -33.6% |
| Employee (incl. ESOP) | `L64` | 1,124.9 | 1,095.0 | -29.9 | -2.7% |
| Depreciation | `L65` | 141.6 | 142.0 | +0.4 | +0.3% |
| Other expenses | `L66` | 1,687.8 | 1,655.1 | -32.7 | -1.9% |
| Total costs | `L67` | 4,384.6 | 4,301.6 | -83.1 | -1.9% |
| PBT | `L69` | 1,434.4 | 1,758.6 | +324.2 | +22.6% |
| PAT | `L53` | 1,063.4 | 1,297.9 | +234.5 | +22.1% |

### FY 2028

| Line | Workbook cell | Workbook | Model | Diff | Diff % |
|---|---|---:|---:|---:|---:|
| Broking revenue | `N42` | 3,730.6 | 4,108.9 | +378.3 | +10.1% |
| Depository income | `N44` | 197.9 | 238.6 | +40.7 | +20.6% |
| Distribution income | `N46` | 239.5 | 311.6 | +72.0 | +30.1% |
| MTF income | `N48` | 1,393.0 | 1,298.6 | -94.4 | -6.8% |
| Other interest income (treasury) | `N50` | 1,184.4 | 1,068.4 | -116.0 | -9.8% |
| Total income / revenue | `N52` | 6,745.4 | 7,093.6 | +348.2 | +5.2% |
| Finance cost | `N61` | 894.0 | 610.7 | -283.3 | -31.7% |
| Fees & commission | `N62` | 922.7 | 962.8 | +40.1 | +4.3% |
| Impairment | `N63` | 3.5 | 2.3 | -1.2 | -33.6% |
| Employee (incl. ESOP) | `N64` | 1,259.9 | 1,226.4 | -33.5 | -2.7% |
| Depreciation | `N65` | 158.6 | 159.1 | +0.5 | +0.3% |
| Other expenses | `N66` | 1,864.0 | 1,820.6 | -43.4 | -2.3% |
| Total costs | `N67` | 5,102.6 | 4,781.9 | -320.7 | -6.3% |
| PBT | `N69` | 1,642.8 | 2,311.7 | +669.0 | +40.7% |
| PAT | `N53` |  | 1,733.8 | | |

### Quarters (total costs, PAT)

| Quarter | WB costs | Model costs | WB PAT | Model PAT |
|---|---:|---:|---:|---:|
| Q1 FY 2027 | 1,109.2 | 1,109.0 | 231.0 | 231.4 |
| Q2 FY 2027 | 1,058.5 | 973.0 | 290.1 | 335.0 |
| Q3 FY 2027 | 1,068.2 | 1,071.8 | 295.0 | 392.7 |
| Q4 FY 2027 | 1,148.8 | 1,147.8 | 247.3 | 338.8 |

## GROWW

### FY 2027

| Line | Workbook cell | Workbook | Model | Diff | Diff % |
|---|---|---:|---:|---:|---:|
| Broking revenue | `AC42` | 4,278.8 | 4,583.2 | +304.4 | +7.1% |
| MTF income | `AC46` | 655.6 | 582.2 | -73.4 | -11.2% |
| Total income / revenue | `AC50` | 6,411.8 | 6,513.1 | +101.3 | +1.6% |
| Finance cost | `AC59` | 40.1 | 15.4 | -24.8 | -61.7% |
| Employee (incl. ESOP) | `AC60` | 754.2 | 732.4 | -21.9 | -2.9% |
| Depreciation | `AC61` | 98.3 | 89.6 | -8.7 | -8.8% |
| Other expenses | `AC62` | 1,477.3 | 1,518.2 | +40.9 | +2.8% |
| Total costs | `AC63` | 2,370.0 | 2,355.6 | -14.4 | -0.6% |
| PBT | `AC65` | 4,041.8 | 4,156.1 | +114.3 | +2.8% |
| Tax | `AC66` | 1,010.4 | 1,061.4 | +50.9 | +5.0% |
| PAT | `AC51` | 3,021.4 | 3,094.7 | +73.3 | +2.4% |

### FY 2028

| Line | Workbook cell | Workbook | Model | Diff | Diff % |
|---|---|---:|---:|---:|---:|
| Broking revenue | `AF42` | 4,820.8 | 5,268.9 | +448.1 | +9.3% |
| MTF income | `AF46` | 983.4 | 682.8 | -300.6 | -30.6% |
| Total income / revenue | `AF50` | 7,632.5 | 7,696.0 | +63.6 | +0.8% |
| Finance cost | `AF59` | 226.0 | 15.4 | -210.6 | -93.2% |
| Employee (incl. ESOP) | `AF60` | 867.4 | 842.2 | -25.1 | -2.9% |
| Depreciation | `AF61` | 113.1 | 103.1 | -10.0 | -8.8% |
| Other expenses | `AF62` | 1,698.9 | 1,771.0 | +72.2 | +4.2% |
| Total costs | `AF63` | 2,905.3 | 2,731.7 | -173.6 | -6.0% |
| PBT | `AF65` |  | 4,964.3 | | |
| Tax | `AF66` |  | 1,241.1 | | |
| PAT | `AF51` |  | 3,723.2 | | |

### Quarters (total costs, PAT)

| Quarter | WB costs | Model costs | WB PAT | Model PAT |
|---|---:|---:|---:|---:|
| Q1 FY 2027 | 555.7 | 555.7 | 735.0 | 735.0 |
| Q2 FY 2027 | 605.1 | 555.9 | 738.5 | 724.7 |
| Q3 FY 2027 | 604.4 | 628.4 | 761.6 | 824.4 |
| Q4 FY 2027 | 604.8 | 615.6 | 786.2 | 810.5 |


## FY28 valuation: model vs the 06.11 workbook

AB, 9 Nov 2026: P/E and discounts now follow the 06.11 workbook (`seed/pat_assumptions.json`, DB update `out/pat/assumptions_2026-11-09.sql`); P/E and quarterly ADR growth stay editable inputs. The ADR starting point still differs.

The `pat_*` source cells name the 14 Jul workbook (`../20260714_brokers dashboard v2.xlsx`), where every one was re-read and matches.
AB's 06.11 workbook rebuilt the FY28 block of `Angel One - ADR model (A+B)` and `Groww - ADR Model`; these values now differ:

| Item | Model (`sb_assumptions` / run) | 06.11 workbook | Cell |
|---|---|---|---|
| Angel P/E bear / base / bull | 20 / 24 / 28 (`pat_pe`; was 18 / 22.5 / 27) | 20 / 24 / 28 | `Angel One - ADR model (A+B)!C30:E30` |
| Angel forward discount | 20% (`pat_discount_fwd`; was 18%) | 20% | `!G33` |
| Angel discount to today | 10% (`pat_discount_today`; was 9%) | 10% | `!G34` |
| Groww P/E | 38 / 44 / 50 | 38 / 44 / 50 (same) | `Groww - ADR Model!C31:E31` |
| Groww forward discount | 20% (`pat_discount_fwd`; was 18%) | 20% | `!G34` |
| Groww discount to today | 10% | 10% (same) | `!G35` |
| FY28 ADR starting point | 20-day (Angel) / 45-day (Groww) ADR from the engine, then × 1.03 / 1.035 a quarter | `SUMMARY - <broker>!C11` "Q3 FY27 (Estimate)" (Angel 20.376, Groww 23.543 Rs Cr a day), then the same quarterly growth | Angel `!D57:D63`, Groww `!E58:E64` |
| FY28 operating ADR (broking + MTF) | Angel 21.892, Groww 24.096 | Angel 22.609, Groww 26.575 | Angel `!D63`, Groww `!E64` |
| FY28 income outside the ADR (treasury + other) | Angel 1,686.1 (treasury 1,068.4 + depository 238.6 + distribution 311.6 + other 67.7); Groww 1,744.3 (float 636.8 + PL+LAS 557.6 + other operating 383.0 + other 167.0) | Angel 1,604.7 (treasury 1,184.38 + other 420.31, typed); Groww 1,828.4 (treasury 1,322.28 + other 506.15 = `Groww - Final !E132`) | Angel `!C22:C23`, Groww `!C23:C24` |
| FY28 total income | Angel 7,093.6; Groww 7,696.0 | Angel 7,189.1; Groww 8,392.4 | Angel `!C24`, Groww `!C25` |
| FY28 total costs | Angel 4,781.9; Groww 2,731.7 | Angel 5,102.6; Groww 2,905.3 | `PAT predictor Q2FY27!N67`, `!AF63` |
| Shares (Cr) | Angel 91.450; Groww 623.905 (filings, staged) | Angel 91.512; Groww 621.096 (Excel stock data type) | `!D2` |
| FY28 PAT | Angel 1,733.8; Groww 3,723.2 | Angel 1,564.9; Groww 4,115.3 | Angel `!C27`, Groww `!C28` |
| FY28 target today bear / base / bull (Rs) | Angel 287.26 / 344.71 / 402.16; Groww 171.79 / 198.92 / 226.05 (was Angel 265.33 / 331.66 / 397.99; Groww 174.71 / 202.29 / 229.88) | Angel 259.09 / 310.91 / 362.73; Groww 190.74 / 220.86 / 250.98 | Angel `!C34:E34`, Groww `!C35:E35` |

## What drives the gaps

1. **FY28 finance cost** (Angel −283 Cr, Groww −211 Cr) is most of the cost gap. The model funds MTF book growth with borrowing *less 75% of retained PAT* for both brokers (`docs/PAT_Model.md` §2). The workbook's Angel FY28 (`N61`) ignores retained profit; Groww FY28 (`AF59` = `AF74*8.5%+AC59`) adds 8.5% on the FY28 increment. Groww's retained PAT (≈ 2,300 Cr) exceeds its book growth (≈ 670 Cr), so the model adds no new borrowing at all.
2. **Q2 FY27 is filed in the model, estimated in the workbook.** Angel Q2 costs are 973.0 filed against 1,058.5 in `I67`, and PAT is 335.0 against 290.1 in `I53`. Groww Q2 costs are 555.9 against 605.1 in `Z63`, and PAT is 724.7 against 738.5 in `Z51`. The workbook's Q3/Q4 build on its own Q2 estimates.
3. **Revenue split.** The model's Angel treasury is interest income minus MTF, with other income on its own line. The workbook's `Other interest income` (row 50) includes other income, so the treasury line differs while Q1 FY27 total income agrees (1,433.7 both). The Groww workbook has no float, PL + LAS or other-operating lines, so only broking, MTF and totals are compared.
4. **FY28 MTF income** is lower in the model (Angel −94, Groww −301 Cr). The model grows MTF ADR at 3% / 3.5% a quarter from today's ADR. The workbook's PAT predictor FY28 uses its earlier growth assumptions (`N48`, `AF46`).
5. **Valuation inputs**: P/E and discounts now match (9 Nov). The workbook still starts the ADR path from its Q3 FY27 estimate instead of the 20/45-day ADR.

Apart from P/E and discounts (AB, 9 Nov 2026), neither side is changed.
