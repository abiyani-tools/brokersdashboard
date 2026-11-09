# PAT staged facts: independent check (198 rows)

Method: own pdftotext -layout parser (not src/extract/pl_*.py) on the cited page of each PDF. Header columns were read by me and hard-coded per page; every row's number count equalled the header's column count (otherwise it would have been NOT_FOUND). Groww filings of Jan-26 (p6) and Apr-26 (p8) print INR Millions; the staged rows carry unit "Rs Mn" for those and "Rs Cr" for Jul-26 / Oct-26 filings, which is correct as filed. One image (Groww Jan p6) and one scanned page (Angel Outcome p5, zoomed) were looked at by eye.

## Counts
| Status | n |
|---|---|
| MATCH | 178 (Angel 90, Groww 88) |
| DERIVED_OK | 20 (18 Angel Q3 FY26 rows + 2 shares rows) |
| MISMATCH / DERIVED_MISMATCH / NOT_FOUND | 0 |
| Total | 198 |

No non-MATCH rows. Findings worth AB's attention are in "Observations" below; none changes a staged value.

## 1-2. Value, row, column, unit, period mapping
Column maps used (header text -> period_key, Indian FY):
- Angel Oct-26 deck p29: Q2 FY27 | Q1 FY27 | Q2 FY26 | FY26 | FY25 (Rs Mn)
- Angel Jul-26 deck (AOLupdate) p29: Q1 FY27 | Q4 FY26 | Q1 FY26 | FY26 | FY25
- Groww Oct-26 p7 (Rs Cr): 30 Sep 2026 = Q2 FY27 | 30 Jun 2026 = Q1 FY27 | 30 Sep 2025 = Q2 FY26 | 6M | 6M | FY26
- Groww Jul-26 p6 (Rs Cr): 30 Jun 2026 = Q1 FY27 | 31 Mar 2026 = Q4 FY26 | 30 Jun 2025 = Q1 FY26 | FY26
- Groww Jan-26 p6 (Rs Mn): 31 Dec 2025 = Q3 FY26 | 30 Sep 2025 = Q2 FY26 | 31 Dec 2024 = Q3 FY25 | 9M | 9M | FY25
- Groww Apr-26 p8 (Rs Mn): 31 Mar 2026 = Q4 FY26 | 31 Dec 2025 = Q3 FY26 | 31 Mar 2025 = Q4 FY25 | FY26 | FY25
All 178 non-derived rows equal the printed figure (tolerance 0.005 for Groww 2-dp figures, 0.5 for Angel integers; actual differences were 0). Signs as filed: Angel impairment Q1 FY26 -5, Q2 FY26 -8, Q2 FY27 -2; Groww Q3 FY25 employee benefits (3,175.56) and total expenses (177.27) Rs Mn are negative as filed (Note 6 on p7 of the Jan filing: long-term incentive plan cancelled in Dec-24 quarter and reversed; text line read: "The said long term incentive plan was been cancelled during the three months period ended 31 December 2024. Accordingly, the Group has reversed the long term incentive of INR 1,061.69 million and INR 4,246.76 million...").
Row choices to be aware of:
- Angel pl_pat = line X "Profit for the period / year (VIII-IX=X)" (after "Tax For Previous Years"); pl_tax = line VII only. pl_pbt = line VI (after associate).
- Groww pl_pbt = "Profit before tax for the period/year" (after associate loss), pl_pat = "Profit for the period/year" (total, incl. non-controlling interest). Q2 FY27: total 724.70; attributable to shareholders 725.65 (NCI -0.95). Other quarters have no NCI.

## 3. Derived rows (Angel Q3 FY26, 18 rows) = FY26 (Oct deck) - Q1 FY26 (Jul deck) - Q2 FY26 (Oct deck) - Q4 FY26 (Jul deck), re-done from the PDFs; all 18 agree with the note and the staged value. Rs Mn:
| metric | FY26 | Q1 | Q2 | Q4 | Q3 |
|---|---|---|---|---|---|
| interest income | 16,317 | 3,564 | 3,794 | 4,550 | 4,409 |
| fees and commission income | 34,842 | 7,780 | 8,167 | 10,000 | 8,895 |
| fv gain | 207 | 62 | 57 | 45 | 43 |
| revenue from ops | 51,366 | 11,405 | 12,018 | 14,594 | 13,349 |
| other income | 156 | 26 | 24 | 78 | 28 |
| total income | 51,522 | 11,431 | 12,042 | 14,672 | 13,377 |
| finance costs | 4,367 | 829 | 932 | 1,336 | 1,270 |
| fee & comm expense | 7,202 | 1,689 | 1,700 | 1,988 | 1,825 |
| impairment | 31 | -5 | -8 | 27 | 17 |
| employee | 8,839 | 2,274 | 2,275 | 2,050 | 2,240 |
| ESOP | 1,832 | 465 | 470 | 393 | 504 |
| depreciation | 1,250 | 299 | 307 | 329 | 315 |
| other expenses | 15,282 | 4,235 | 3,427 | 4,149 | 3,471 |
| total expenses | 38,803 | 9,787 | 9,102 | 10,273 | 9,641 |
| PBT | 12,718 | 1,644 | 2,940 | 4,399 | 3,735 |
| tax | 3,579 | 500 | 823 | 1,196 | 1,060 |
| PAT (line X) | 9,151 | 1,145 | 2,117 | 3,202 | 2,687 |
| trading days | 246 | 61 | 64 | 60 | 61 |
Caveat: Q3 is a difference of rounded integers, so each line carries up to about +/-2 Rs Mn rounding error (see check 4).

## 4. Internal consistency (from staged facts; difference = left - right)
Angel (Rs Mn): interest+fees+fv-RevOps | RevOps+OthInc-TI | sum of 7 expense lines-TE | TI-TE-PBT | PBT-tax-PAT
- Q1 FY26: 1 | 0 | -1 | 0 | -1
- Q2 FY26: 0 | 0 | 1 | 0 | 0
- Q3 FY26 (derived): -2 | 0 | 1 | 1 | **-12**
- Q4 FY26: 1 | 0 | -1 | 0 | 1
- Q1 FY27: 0 | 0 | 2 | 0 | 0
- Q2 FY27: -1 | 1 | 0 | 0 | 0
All are within the filing's own rounding ("Numbers are rounded off to the nearest number"), except Q3 FY26 PBT-tax-PAT = 3,735 - 1,060 - 2,687 = -12 (above 0.5). Reason: PAT is line X (after prior-year tax IX); FY26 IX = -13 (PBT-tax = 9,138 vs line X 9,151), and Q1/Q2/Q4 IX are about 0/0/+1, so almost the whole -13 falls in Q3. Not an error, but PAT != PBT - tax in Q3 FY26 and the prior-year tax line is not staged. Also share of associate (line V, -0 to -1) is not staged; TI-TE-PBT is within 1 everywhere, so it is immaterial.
Cross-check against the Angel Outcome PDF p5 (scanned, unrounded, Rs Mn): Q2 FY27 revenue from ops 14,269.89, TI 14,315.36, TE 9,730.37, PBT 4,584.96, PAT 3,349.72; Q1 FY27 PBT 3,246.71, PAT 2,313.98; Q2 FY26 PBT 2,939.98, PAT 2,117.30. All round to the deck figures staged.

Groww (Rs Mn for Q3 FY25, Q4 FY25, Q3 FY26; Rs Cr for the rest): RevOps+OthInc-TI = 0 and sum of 4 expense lines-TE = 0 in all 8 quarters; PBT-tax-PAT = 0 in all 8. TI-TE-PBT must equal the share of associate loss; printed associate losses are (units as filed): Q3 FY25 6.05 Mn (computed 6.05), Q4 FY25 5.18 Mn (5.18), Q1 FY26 0.63 Cr (0.63), Q2 FY26 0.52 Cr (0.52), Q3 FY26 6.65 Mn (6.65), Q4 FY26 0.66 Cr (0.66), Q1 FY27 0.72 Cr (0.72), Q2 FY27 0.75 Cr (0.75). All agree; note the facts carry no associate row, so PBT cannot be rebuilt from the staged facts alone (differences above 0.5 of the unit: 6.05, 5.18, 6.65 Rs Mn rows, fully explained by this line).

## 5. Overlapping filings (all printed columns of all six statement pages compared, Groww converted Mn/10)
120 (broker, period, metric) combinations appear in more than one filing: Angel Q1 FY27, FY26, FY25 (Jul vs Oct deck); Groww Q1 FY27 (Jul vs Oct), Q2 FY26 (Oct vs Jan), Q3 FY26 (Jan vs Apr), Q4 FY26 (Jul vs Apr), FY26, FY25. No revisions. Three Groww pairs differ by 0.006 to 0.01 Cr only because Rs Mn figures are printed to 2 dp (e.g. Q4 FY26 PAT 686.36 Cr in Jul vs 6,863.54 Mn = 686.354 Cr in Apr; FY26 PAT 2,083.01 vs 20,830.00 Mn; FY26 PBT 2,821.42 vs 28,214.11 Mn). Rounding, not restatement. The staged Q4 FY26 PAT is the Jul-26 Cr figure.

## 6. Shares
- Angel One: Oct deck p30 prints "Networth 67,124 (Sep '26) / 61,489 (Mar '26)" and "Book Value: Rs 73.4 as on September 30, 2026" (footnote 6: book value = period-ending networth / period-ending number of equity shares). 67,124 / 73.4 = 914.496 Rs Mn shares = 91.4496 Cr. Arithmetic agrees (DERIVED_OK).
  - Better source: Outcome.pdf p5 (scanned image, read at 250 dpi) prints "Equity share capital (face value Re. 1 each) 914.59" Rs Mn at 30 Sep 2026 (913.52 at 30 Jun 2026; 907.17 at 30 Sep 2025; 910.86 at 31 Mar 2026) = 914.59 Mn shares = **91.459 Cr**. The staged 91.4496 is 0.0094 Cr (0.010%) lower; book value is rounded to 0.1, so the derived number is good only to about +/-0.06 Cr. Suggest AB replaces it with 91.459 (this is the sourced figure) or at least knows the gap.
  - EPS cross-check: Outcome p5 basic EPS Q2 FY27 3.67 with PAT 3,349.72 gives weighted 912.7 Mn = 91.27 Cr (weighted, so a bit lower than period-end). Oct deck p27 TTM PAT Rs 11.6 Bn / TTM EPS 12.7 = 91.3 Cr. Consistent with 91.4-91.5 Cr.
- Groww: Oct-26 filing p7 prints "Paid up equity share capital (Face Value : INR 2/- per share) 1,247.81" Rs Cr, in the Year ended 31 March 2026 column only. 1,247.81 / 2 = 623.905 Cr (DERIVED_OK). Apr-26 filing p8 prints 12,478.06 Rs Mn at 31 Mar 2026 (= 623.903 Cr). But the Oct-26 balance sheet (p8) prints "Equity share capital 1,248.42  1,247.81" (30 Sep 2026, 31 Mar 2026) = 624.21 Cr at 30 Sep 2026. So 623.905 is the 31 Mar 2026 count, not the latest; the fact has period_key blank.
  - EPS cross-check (Oct p7, basic EPS Q2 FY27 1.17, profit attributable to shareholders 725.65 Rs Cr): 725.65 / 1.17 = 620.2 Cr weighted (range 617.6 to 622.9 for EPS rounding). Q1 FY27: 735.04 / 1.19 = 617.7 Cr. These sit 0.3% to 1% below paid-up 623.9, so weighted-average count is not exactly equal to issued count (reason not stated in the filing; do not treat as an error).
  - No PDF prints a plain number-of-shares line for either broker apart from the Groww IPO note (663,230,051 shares issued in IPO; 100,000,000 allotted to the employee trust in Q4 FY26, Apr-26 p11) and the Angel equity share capital line above.

## 7. Angel trading_days
Printed as "# of Trading Days" on p29 of both decks (row above Interest Income): Q1 FY26 61, Q2 FY26 64, Q4 FY26 60, Q1 FY27 60, Q2 FY27 65, FY26 246, FY25 247. Q3 FY26 = 246-61-64-60 = 61 (derived, consistent). All six staged rows agree.

## Observations (no mismatch, for AB's decision)
1. Angel Q3 FY26 PAT staged 2,687 is line X (includes about +12 Rs Mn prior-year tax credit); PBT - tax = 2,675. Both are right for their definitions; decide which the PAT model should use.
2. Angel shares: a filed count exists (Outcome p5 914.59 Rs Mn at Re. 1 = 91.459 Cr); staged 91.4496 is derived from a rounded book value.
3. Groww shares: staged count is as at 31 Mar 2026 (623.905); Sep-26 balance sheet gives 624.21 Cr.
4. Groww pl_pat in Q2 FY27 is the total (724.70) not shareholders' share (725.65); matters if EPS is computed from it.
5. Groww Q3 FY25 expenses/PBT are distorted by the reversal of the long-term incentive (negative employee cost); correct as filed.
6. Staged Rs Mn / Rs Cr units differ across Groww quarters (Q3 FY25, Q4 FY25, Q3 FY26 in Mn); any consumer must convert (Mn / 10 = Cr).
