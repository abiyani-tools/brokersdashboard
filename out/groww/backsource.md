# Groww back-sourcing: workbook inputs vs Groww's own filings

Prepared 2026-10-31. Scope: the 41 `scope: "groww"` rows of `out/groww/workbook_inputs.json` (including the 8 `read_by_model: false` rows), plus two extra rows (MTF yield and day basis) because D7 asks about them. Research only: no database writes, no commits, nothing outside `out/groww/`.

## 1. Result in one view

| Status | Count (41 groww rows) | Meaning |
|---|---|---|
| match | 10 | Same as the filing at the same precision and definition |
| rounded | 11 | Workbook holds Groww's coarse (integer-percent) print or a typed rounding of a figure Groww gives more precisely |
| restated | 10 | Workbook holds the figure as first published; a later filing restates it (revenue-mix classification, or the market-share denominator), or the workbook doubles a new-basis figure back to the legacy basis |
| differs | 8 | Wrong bucket, wrong base, wrong concept, or a different basis than the filing |
| no source | 2 | Typed assumption; no filing can source it |

Extra rows: `mtf_yield` match, `mtf_day_basis` no source.

The four findings that change numbers (details in section 3 and in the table):
1. **D9 base.** The mix % is on consolidated total income. The workbook's Q4 FY26 and Q1 FY27 base (14,684 and 14,730 Rs Mn) is platform revenue from operations excluding Fisdom and AMC, not total income, and is 4.4% and 4.9% smaller than consolidated total income (15,355.35 and 15,486.7). Every Q4 FY26 and Q1 FY27 segment revenue built on it is 4-5% low.
2. **MTF revenue is mis-bucketed for Q4 FY25, Q1 FY26 and Q4 FY26.** The workbook took 5% (the Treasury bucket) for Q4 FY25 and Q1 FY26 where MTF was 2% and 3%, and 5% for Q4 FY26 where MTF is 6.9%. Q4 FY25 is +150%, Q1 FY26 +67%, Q4 FY26 -31%.
3. **Market shares are ADTO shares on a legacy basis.** The workbook series is internally consistent (Q4 FY26 and Q1 FY27 are 2 x the new-basis figure), but no filing prints those values after Q3 FY26.
4. **Stocks (cash) mix is restated in the Q2 FY27 letter** (IPO and BDSA revenue moved to Other operating income): 19.4/18.2/16.4/16.4% become 17.8/16.5/15.6/16.1%. Workbook cash revenue is on the old classification.

## 2. Row-by-row table

Page numbers are PDF pages of the NSE-filed file (cover letter = page 1; printed page = PDF page minus 2 for the letters). Status compares the workbook with the **latest** filing figure on the same definition.

Document key (files in `data/raw/disclosures/groww/`; handbooks in `ir_site/`):
- SL-Q2FY26 `BILLIONBRAINS_21112025104921_Shareholderslettersigned.pdf`; SL-Q3FY26 `BILLIONBRAINS_14012026125814_SHLetterSigned_.pdf` (the 132923 copy has the same sha256); SL-Q4FY26 `BILLIONBRAINS_20042026132113_ShareholdrsLetterSigned.pdf`; SL-Q1FY27 `BILLIONBRAINS_15072026114459_ShareholderLettersigned.pdf`; SL-Q2FY27 `BILLIONBRAINS_14102026130454_ShareholderLetter_Final.pdf`
- RES-Q2FY26 `BILLIONBRAINS_21112025102506_BMoutcomeintimati.pdf` (image only, read visually); RES-Q3FY26 `BILLIONBRAINS_14012026123241_OutcomeSigned.pdf`; RES-Q4FY26 `BILLIONBRAINS_20042026130140_Boardoutcomesigned.pdf`; RES-Q1FY27 `BILLIONBRAINS_15072026112913_outcomefinal.pdf`; RES-Q2FY27 `BILLIONBRAINS_14102026124408_outcomefinalsigned.pdf`
- HB-Q4FY26 `2026_4_Key_Performance_Indicators_Q4_FY26.xlsx`; HB-Q1FY27 `2026_7_Q1_FY27_KPI_Handbook.xlsx`; HB-Q2FY27 `2026_10_Q2_FY27_KPI_Handbook.xlsx`
- TR-Q2FY26 `BILLIONBRAINS_26112025163528_Intimationtranscriptsigned.pdf`; TR-Q1FY27 `BILLIONBRAINS_17072026171936_EC_Trans_SD.pdf`; TR-Q2FY27 `BILLIONBRAINS_16102026165927_EC_Trans_SD.pdf`

| Workbook cell | Metric | Period | Workbook value | Filing value | Document + page/sheet | Status | Note |
|---|---|---|---|---|---|---|---|
| Working sheet - Groww!H7 | revmix_fo | Q2 FY26 | 0.57 | 57% as printed; 56.9% restated | SL-Q2FY26 p7; SL-Q1FY27 p6; SL-Q2FY27 p6 | rounded | Workbook = Q2 FY26 letter integer print. One-decimal 56.9% is on all later letters. Base = consolidated total income (Fisdom not yet consolidated). |
| Working sheet - Groww!I7 | revmix_fo | Q3 FY26 | 0.53 | 53% as printed; 53.5% later | SL-Q3FY26 p6; SL-Q1FY27 p6; SL-Q2FY27 p6 | rounded | Integer print understates the one-decimal figure by 0.5pp (about Rs63 Mn of F&O revenue on total income 12,610.72). |
| Working sheet - Groww!J7 | revmix_fo | Q4 FY26 | 0.55 | 55% as printed; 54.8% later | SL-Q4FY26 p7; SL-Q1FY27 p6; SL-Q2FY27 p6 | rounded | Letter text (SL-Q4FY26 p6) says 54.6%, chart says 55%, later letters say 54.8%: use 54.8%. Workbook applies it to 14,684 (revenue ex Fisdom/AMC), not total income 15,355.35: F&O Rs 8,076 Mn vs 8,415 Mn on the right base (-4.0%). See D9. |
| Working sheet - Groww!L7 | revmix_fo | Q1 FY27 | 0.52 (not read by model) | 52.0% as printed; 51.9% restated | SL-Q1FY27 p6; SL-Q2FY27 p6 | match | Matches the Q1 FY27 print; Q2 FY27 letter shows 51.9%. Row 120 base issue as above (applied to 14,730 not 15,486.7). |
| Working sheet - Groww!H8 | revmix_cash | Q2 FY26 | 0.19 | Stocks 19% as printed; 19.4% (Q1 FY27 letter); 17.8% (Q2 FY27 letter, new classification) | SL-Q2FY26 p7; SL-Q1FY27 p6; SL-Q2FY27 p6 | restated | Groww bucket is "Stocks" (includes DP/DDPI/pledge fees and, until Q2 FY27, IPO and BDSA revenue). Q2 FY27 reclassification moved IPO/BDSA to Other operating income: 19.4% -> 17.8%. |
| Working sheet - Groww!I8 | revmix_cash | Q3 FY26 | 0.18 | Stocks 18% as printed; 18.2% (Q1 FY27 letter); 16.5% (Q2 FY27 letter) | SL-Q3FY26 p6; SL-Q1FY27 p6; SL-Q2FY27 p6 | restated | Same reclassification. |
| Working sheet - Groww!J8 | revmix_cash | Q4 FY26 | 0.16 | Stocks 16% as printed; 16.4% (Q1 FY27 letter); 15.6% (Q2 FY27 letter) | SL-Q4FY26 p7; SL-Q1FY27 p6; SL-Q2FY27 p6 | restated | Same reclassification. Applied to 14,684 base (D9). |
| Working sheet - Groww!L8 | revmix_cash | Q1 FY27 | 0.164 | Stocks 16.4% as printed; 16.1% (Q2 FY27 letter) | SL-Q1FY27 p6; SL-Q2FY27 p6 | restated | Workbook matches the Q1 FY27 print; restated to 16.1%. Applied to 14,730 base (D9): Rs 2,416 Mn vs 2,540 Mn on total income. |
| Working sheet - Groww!I9 | revmix_comm | Q3 FY26 | 0.04 | 4% as printed; 3.5% later | SL-Q3FY26 p6; SL-Q1FY27 p6; SL-Q2FY27 p6 | rounded | Integer print rounds 3.5% up. Rs 504.43 Mn in the workbook (4% x 12,610.72) vs 441.4 Mn at 3.5%. |
| Working sheet - Groww!J9 | revmix_comm | Q4 FY26 | 0.04 (not read by model) | 4% as printed; 4.5% later | SL-Q4FY26 p7; SL-Q1FY27 p6; SL-Q2FY27 p6 | rounded | 4.5% on total income 15,355.35 = Rs 691.0 Mn vs workbook 587.36 Mn (4% x 14,684). |
| Working sheet - Groww!L9 | revmix_comm | Q1 FY27 | 0.049 (not read by model) | 4.9% | SL-Q1FY27 p6; SL-Q2FY27 p6 | match | Both letters print 4.9%. Rs 721.77 Mn in workbook = 4.9% x 14,730; on total income 758.8 Mn. |
| Working sheet - Groww!G7 | revmix_fo | Q1 FY26 | 0.56 (not read by model) | 56% as printed; 56.4% later | SL-Q2FY26 p7; SL-Q1FY27 p6 | rounded | Q1 FY26 mix is available (one decimal on SL-Q1FY27 p6). Not in the Q2 FY27 restated set. |
| Working sheet - Groww!G8 | revmix_cash | Q1 FY26 | 0.19 (not read by model) | Stocks 19% as printed; 19.3% later | SL-Q2FY26 p7; SL-Q1FY27 p6 | rounded | Old classification only; Q2 FY27 letter starts at Q2 FY26, so no restated Q1 FY26 value exists. |
| Working sheet - Groww!H103 | revenue_from_ops | Q2 FY26 | 10187.42 Rs Mn | 10,187.42 Rs Mn | RES-Q2FY26 p5 (image, read visually); RES-Q3FY26 p6; RES-Q2FY27 p7 (1,018.74 Cr) | match | Q2 FY26 results PDF has no text layer; confirmed visually and against the comparative columns in two later results. |
| Working sheet - Groww!I103 | revenue_from_ops | Q3 FY26 | 12160.72 Rs Mn | 12,160.72 Rs Mn | RES-Q3FY26 p6; RES-Q4FY26 p8 | match |  |
| Working sheet - Groww!H104 | other_income | Q2 FY26 | 520.55 Rs Mn | 520.55 Rs Mn | RES-Q2FY26 p5; RES-Q3FY26 p6; RES-Q2FY27 p7 (52.06 Cr) | match |  |
| Working sheet - Groww!I104 | other_income | Q3 FY26 | 450 Rs Mn | 450.00 Rs Mn | RES-Q3FY26 p6; RES-Q4FY26 p8 | match | Printed as 450.00. |
| Working sheet - Groww!H105 | total_income | Q2 FY26 | 10707.97 Rs Mn (formula) | 10,707.97 Rs Mn | RES-Q2FY26 p5; RES-Q3FY26 p6; RES-Q2FY27 p7 (1,070.80 Cr) | match |  |
| Working sheet - Groww!I105 | total_income | Q3 FY26 | 12610.72 Rs Mn (formula) | 12,610.72 Rs Mn | RES-Q3FY26 p6; RES-Q4FY26 p8 | match |  |
| Working sheet - Groww!G103 | revenue_from_ops | Q1 FY26 | 9043 Rs Mn (not read by model) | 9,043.98 Rs Mn (904.40 Cr in the Q1 FY27 results) | RES-Q2FY26 p5 (30 June 2025 column); RES-Q1FY27 p6 | rounded | Typed 9043 truncates 9,043.98. Q1 FY26 is available in the filings: see Q1 FY26 answer. |
| Working sheet - Groww!G104 | other_income | Q1 FY26 | 442 Rs Mn (not read by model) | 440.73 Rs Mn (44.07 Cr) | RES-Q2FY26 p5; RES-Q1FY27 p6 | differs | 442 is the residual 9,485 - 9,043; the filing prints 440.73 (+1.27 Mn, 0.3%). G105 = 9485 vs 9,484.71 is rounded. |
| Working sheet - Groww!J120 | total_income_ex_fisdom_amc | Q4 FY26 | 14684 Rs Mn | Revenue ex Fisdom and Growwmf 14,684 Mn (platform revenue). Consolidated total income 15,355.35 Mn; revenue from operations 15,053.67 Mn | SL-Q4FY26 p4; HB-Q4FY26 sheet Financial KPIs!K15; RES-Q4FY26 p8 | differs | The number matches the filing exactly but it is not a total-income figure: it is platform revenue from operations ex Fisdom and Growwmf (before other income). Groww does not publish "total income ex Fisdom/AMC". Not the base of the revenue-mix %. See D9. |
| Working sheet - Groww!L120 | total_income_ex_fisdom_amc | Q1 FY27 | 14730 Rs Mn | Platform revenue ex Fisdom and Groww AMC 1,472.72 Cr (letter rounds to 1,473 Cr). Consolidated total income 1,548.67 Cr | SL-Q1FY27 p4; HB-Q1FY27 sheet Financial KPIs!L13; RES-Q1FY27 p6 | differs | Same concept problem; also rounded 14,730 vs 14,727.2. The Q2 FY27 handbook restates Q1 FY27 platform revenue to 1,497.63 Cr (Fisdom now included, only AMC excluded). |
| Working sheet - Groww!H55 | share_fo_adto_q | Q2 FY26 | 0.173 | Retail Derivatives Premium ADTO share 17.3% as printed; 8.6% restated (new basis) | SL-Q2FY26 p5; SL-Q2FY27 p5 | restated | By ADTO. Q2 FY26 letter denominator = exchange turnover; from Q4 FY26 it is exchange turnover x 2, so every figure halves (17.3 -> 8.65, printed 8.6). Workbook stays on the legacy basis. |
| Working sheet - Groww!I55 | share_fo_adto_q | Q3 FY26 | 0.181 | 18.1% as printed (legacy basis) | SL-Q3FY26 p5 | match | No later letter restates Q3 FY26 (the charts only carry year-ago pairs); implied new-basis value 9.05% is not published. |
| Working sheet - Groww!J55 | share_fo_adto_q | Q4 FY26 | 0.212 | 10.6% (new basis) | SL-Q4FY26 p5, p6 and footnote | restated | 0.212 = 2 x 10.6%. Filing prints 10.6%; the legacy-basis equivalent is the workbook's own doubling. Consistent with H55/I55. |
| Working sheet - Groww!L55 | share_fo_adto_q | Q1 FY27 | 0.22 (=11*2%; not read by model) | 11.0% (new basis) | SL-Q1FY27 p5 | restated | Doubling again. Q2 FY27 letter also prints 11.0% (p5). |
| Working sheet - Groww!H56 | share_cash_adto_q | Q2 FY26 | 0.258 | Retail Cash ADTO share 25.8% as printed; 12.9% restated | SL-Q2FY26 p5; SL-Q2FY27 p5 | restated | By ADTO (Stocks turnover). See H55 note. |
| Working sheet - Groww!I56 | share_cash_adto_q | Q3 FY26 | 0.288 | 28.8% as printed (legacy basis) | SL-Q3FY26 p5 | match | Not restated in any later letter. |
| Working sheet - Groww!J56 | share_cash_adto_q | Q4 FY26 | 0.314 | 15.7% (new basis) | SL-Q4FY26 p5 | restated | 0.314 = 2 x 15.7%. |
| Working sheet - Groww!L56 | share_cash_adto_q | Q1 FY27 | 0.302 (=15.1*2%) | 15.1% (new basis) | SL-Q1FY27 p5 | restated | Doubling. Q2 FY27 letter: 15.4% (30.8% legacy). Workbook pins L56 for Q2 and Q3 FY27, so the Q2 FY27 actual is not yet fed. |
| MTF data!H51 | mtf_revenue | Q3 FY25 | 20.1 Rs Cr | Not printed in Rs. Derived: 2% x 10,044.47 = 200.89 Mn = 20.09 Cr | SL-Q2FY26 p7; SL-Q3FY26 p6 (MTF 2%); RES-Q3FY26 p6 (Q3 FY25 total income 10,044.47) | rounded | Groww never prints MTF revenue in Rs; every MTF revenue figure is mix % x total income. Typed 20.1 rounds 20.089. |
| MTF data!H52 | mtf_revenue | Q4 FY25 | 42.5 Rs Cr | Derived: 2% x 8,495.72 = 169.91 Mn = 16.99 Cr | SL-Q3FY26 p6 (MTF 2%, Treasury 5%); SL-Q2FY26 p7; RES-Q4FY26 p8 | differs | Workbook used 5%, which is the Treasury bucket, not MTF. +150%. Book check: 16.99 Cr x 4 / avg book 572 Cr = 11.9% annualised; 42.5 Cr would imply 29.7% on a 14.95% product. |
| MTF data!H53 | mtf_revenue | Q1 FY26 | 47.425 Rs Cr | Derived: 3.0% x 9,484.71 = 284.54 Mn = 28.45 Cr | SL-Q1FY27 p6 (MTF 3.0%, Treasury 4.6%); SL-Q2FY26 p7 (3%); RES-Q2FY26 p5 | differs | Workbook used 5% x 9,485 (Treasury bucket). +66.7%. Book check: 28.45 Cr -> 13.9% annualised on avg book 819 Cr; 47.4 Cr -> 23.2%. |
| MTF data!H54 | mtf_revenue | Q2 FY26 | 53.53985 Rs Cr | Derived: 4.7% x 10,707.97 = 503.28 Mn = 50.33 Cr (letter integer 5%) | SL-Q1FY27 p6; SL-Q2FY27 p6 (MTF 4.7%); SL-Q2FY26 p7 (5%) | rounded | Workbook = 5% x 10,707.97. Overstates by 6.4%. Book check: 14.9% annualised at 4.7%. |
| MTF data!H55 | mtf_revenue | Q3 FY26 | 75.66432 Rs Cr | Derived: 5.6% x 12,610.72 = 706.20 Mn = 70.62 Cr (letter integer 6%) | SL-Q1FY27 p6; SL-Q2FY27 p6 (MTF 5.6%); SL-Q3FY26 p6 (6%) | rounded | Workbook = 6% x 12,610.72. Overstates by 7.1%. |
| MTF data!H56 | mtf_revenue | Q4 FY26 | 73.42 Rs Cr | Derived: 6.9% x 15,355.35 = 1,059.52 Mn = 105.95 Cr | SL-Q1FY27 p6 and p7 text ("MTF +1.1pp QoQ", 8.0 less 6.9); SL-Q2FY27 p6; RES-Q4FY26 p8 | differs | Two errors: (1) SL-Q4FY26 p7 prints MTF 5% and PL+LAS 7% by its legend order, but the next two letters give MTF 6.9% and PL+LAS 5.2% (legend swapped in the Q4 letter); (2) base 14,684 instead of 15,355.35. Workbook is 30.7% low. Book check: 105.95 Cr = 16.5% on avg book, 15.1% on closing book 2,814 Cr; 73.4 Cr = 11.5%. |
| MTF data!H57 | mtf_revenue | Q1 FY27 | 118 Rs Cr (typed; L22/10 = 117.84) | Derived: 8.0% x 15,486.7 = 1,238.94 Mn = 123.89 Cr | SL-Q1FY27 p6; SL-Q2FY27 p6 (8.0%); RES-Q1FY27 p6 | differs | Mix % is right (8.0%); base is 14,730 not total income 15,486.7. -4.8%. |
| MTF data!J58 | mtf_share_override | Q2 FY27 | 0.0288 | Groww MTF book 4,351 Cr = 2.7% of NSE+BSE combined MTF book at quarter end | SL-Q2FY27 p5; HB-Q2FY27 Operational KPIs!E20 | differs | Typed assumption of 2.88% vs the disclosed 2.7%. Not like for like: the workbook divides by an average industry book (scanx), Groww divides closing book by NSE+BSE closing book. Q1 FY27 was 2.7% too (SL-Q1FY27 p5); Q4 FY26 2.6% on the combined basis (2.7% NSE-only). |
| MTF data!J59 | mtf_share_override | Q3 FY27 | 0.032 | none (future period) | - | no source | Typed assumption; no filing can source it yet. |
| MTF data!J60 | mtf_share_override | Q4 FY27 | 0.036 | none (future period) | - | no source | Typed assumption; no filing can source it yet. |
| MTF data (2)!L12 (extra, scope assumption) | mtf_yield | all | 0.1495 | 14.95% fixed MTF pricing | TR-Q2FY26 p6; TR-Q1FY27 p13 | match | Groww's own number, spoken by the CFO on two calls (not in a letter or handbook). Applies to the interest charged; management says average vs closing balance makes realised yield vary slightly. |
| MTF data (2)!L12 (extra, scope assumption) | mtf_day_basis | FY26 / FY27 | 246 | FY26 = 247 trading days (61+64+62+60); FY27 H1 = 125 (60+65) | HB-Q2FY27 Operational KPIs!E36:J36 | no source | Groww publishes trading days per quarter, not a full-year day basis. 246 is not a Groww disclosure; FY26 actual is 247 on the handbook row. |

## 3. Answers to the open questions

**D9. Base of the revenue-mix %: total income, consolidated.** The chart is titled "Total Income mix, by Products (% Share)" and the letters introduce it as the consolidated total-income split (SL-Q3FY26 p6 Q1; SL-Q4FY26 p6 Q2; SL-Q1FY27 p6; SL-Q2FY27 p6). The restated chart has an "Other Income" bucket, so the base must include other income, and it must be the consolidated figure (Fisdom and AMC included). Arithmetic test: Other Income % in the Q2 FY27 letter (SL-Q2FY27 p6) against reported other income / consolidated total income: Q2 FY26 52.06/1,070.80 = 4.86% (letter 4.9); Q3 FY26 45.00/1,261.07 = 3.57% (3.6); Q4 FY26 30.17/1,535.54 = 1.96% (2.0); Q1 FY27 47.25/1,548.67 = 3.05% (3.1); Q2 FY27 39.01/1,540.54 = 2.53% (2.5). All five tie. Dividing by platform revenue ex Fisdom/AMC instead gives 3.8% (Q3), 2.05% (Q4) and 3.21% (Q1 FY27), which do not tie (letter 3.6/2.0/3.1). The workbook's row 120 (14,684 / 14,730) is also not "income": it is revenue from operations ex Fisdom and Growwmf/AMC (SL-Q4FY26 p4; HB-Q4FY26 Financial KPIs!K15; SL-Q1FY27 p4 rounds 1,472.72 Cr to 1,473 Cr). Fix: use row 105 style total income for every quarter (Q4 FY26 15,355.35; Q1 FY27 15,486.7; Q2 FY27 15,405.4 Rs Mn). Effect on the workbook segments: Q4 FY26 F&O 8,076 -> 8,415 Mn (+4.2%); Q1 FY27 F&O 7,660 -> 8,038 Mn (+4.9% at 51.9%); MTF Q1 FY27 118 -> 123.9 Cr. Q2 FY26 and Q3 FY26 were already on the right base.

**D6. The shares are by ADTO (turnover), not orders.** The letter charts are "Retail Cash ADTO" (Stocks ADTO, Rs Cr; handbook glossary: cumulative Stocks turnover / trading days) and "Retail Derivatives Premium ADTO" (handbook glossary: notional turnover for futures plus premium turnover for options / trading days): SL-Q2FY26 p5, SL-Q3FY26 p5, SL-Q4FY26 p5, SL-Q1FY27 p5, SL-Q2FY27 p5; HB-Q2FY27 Glossary rows for items 10 and 14. Management confirmed on the Q2 FY27 call that ADTO is reported "to calculate the market share" and that revenue is linked to orders, not ADTV (TR-Q2FY27 p10). Segment definition: cash = Stocks (equities, ETFs, rights, preference shares, InvITs, REITs, warrants, PTCs; excludes Fisdom stocks); F&O = equity derivatives only (commodity is separate and shown as a notional ADTO share, 28.6% in Q1 FY27 only, SL-Q1FY27 p5 and p7). Denominator: exchange turnover through Q3 FY26; exchange turnover x 2 from Q4 FY26 ("each trade has two parties"), which halves every figure (SL-Q4FY26 p5 footnote and p6; Q2 FY26 restated 25.8 -> 12.9 and 17.3 -> 8.6 on SL-Q2FY27 p5). The filings do not define "retail" beyond the label. The MTF share changed denominator in Q1 FY27 to combined NSE+BSE MTF books (SL-Q1FY27 p5 footnote: Q4 FY26 2.6% vs 2.7% NSE-only). The workbook keeps the legacy basis by doubling Q4 FY26 and Q1 FY27 (J55/J56 are 2 x 10.6% and 2 x 15.7%; L55/L56 are `=11*2%` and `=15.1*2%`), which is consistent. Both bases must be labelled; ADTO share is not an order share.

**D7. MTF yield: yes, disclosed, but only as a spoken statement, and no MTF revenue in Rs.** Groww's MTF pricing is a fixed 14.95%: CFO Ishan Bansal on the Q2 FY26 call (TR-Q2FY26 p6: "Our pricing is simple. It is 14.95%") and on the Q1 FY27 call (TR-Q1FY27 p13: "our pricing is fixed actually, it is 14.95%... roughly the number is around 14.95%", with a small closing-vs-average-balance delta). It is not in a letter, handbook or results note. Groww does not publish MTF interest income in Rs: only MTF as % of total income (letter p6/p7 charts) and the MTF book at quarter end (handbook Operational KPIs row 12, `MTF Book`). Cross-check: derived MTF revenue (mix x total income) x 4 / average of opening and closing book gives 14.9% (Q2 FY26), 14.2% (Q3), 16.5% (Q4), 15.0% (Q1 FY27) and 15.3% (Q2 FY27), consistent with 14.95%. So Angel's 14.95% coincides with Groww's own figure; the workbook's constant is right, its source label should be Groww's call transcripts. The day basis 246 has no Groww source (FY26 had 247 trading days on HB-Q2FY27 Operational KPIs row 36). The typed MTF share overrides (J58:J60) have no source; the disclosed Q2 FY27 share is 2.7% of NSE+BSE closing book (SL-Q2FY27 p5).

**Is Q1 FY26 (Apr-Jun 2025) available? Yes, enough to make FY26 a full year.**
- Total income 9,484.71, revenue from operations 9,043.98, other income 440.73 Rs Mn: RES-Q2FY26 p5 (30 June 2025 column, audited), repeated as 948.47 / 904.40 / 44.07 Cr in RES-Q1FY27 p6; also 9,485 Mn on SL-Q2FY26 p4 and 948.47 Cr in HB-Q1FY27 Financial KPIs!H6. Nine-month check: RES-Q3FY26 p6 9M revenue 31,392.12 - 12,160.72 - 10,187.42 = 9,043.98. FY26 total income: 9,484.71 + 10,707.97 + 12,610.72 + 15,355.35 = 48,158.75 Mn vs 48,158.76 printed (RES-Q4FY26 p8): ties.
- Revenue mix: SL-Q1FY27 p6 (one decimal, old classification): F&O 56.4, Stocks 19.3, Float 9.9, MTF 3.0, PL+LAS 6.6, Treasury 4.6 (sums to 99.8; commodity and other income not shown); SL-Q2FY26 p7 (integers 56/19/10/7/5/3). Not available on the Q2 FY27 restated classification (that set starts at Q2 FY26).
- Operating data: Broking orders 37.8557 Cr, 61 trading days, Stocks ADTO Rs 10,673.99 Cr, Equity-derivatives premium ADTO 9,276.73 Cr, MTF book 1,035.77 Cr (HB-Q2FY27 Operational KPIs column J). Market shares for Q1 FY26 exist only on the new basis: Stocks 11.8%, derivatives 7.2% (SL-Q1FY27 p5), i.e. 23.6% and 14.4% on the legacy basis.
- Limits: there is no Groww Q1 FY26 letter (pre-listing; listing was 12 Nov 2025). Segment revenue in Rs is never published; it is mix x total income. The prospectus (not downloaded) may hold more, but the filings above already cover D2.

**Q2 FY27 actuals (letter and results of 14 Oct 2026).** See section 5. Headlines: consolidated total income Rs 1,540.54 Cr (+44% YoY), revenue from operations 1,501.53 Cr, other income 39.01 Cr; mix F&O 44.8%, Stocks 17.4%, Commodity 6.2%, MTF 10.1%; Stocks ADTO 14,430 Cr (15.4% share), Equity-derivatives premium ADTO 12,322 Cr (11.0%), MTF book 4,351 Cr (2.7%); broking orders 51.7305 Cr over 65 trading days.

## 4. Checks run and other observations

- Mix columns sum (restated set, SL-Q2FY27 p6): Q2 FY26 100.0, Q3 99.9, Q4 100.2, Q1 FY27 100.0, Q2 FY27 100.1: within rounding. Original-vintage set (SL-Q1FY27 p6): 99.8 (Q1 FY26), 99.4 (Q2 FY26, comm 0.2 and a tiny other income not labelled), 99.9, 100.1, 100.0.
- Q2 FY27 letter vs handbook: Stocks ADTO 14,430 vs 14,429.97; premium ADTO 12,322 vs 12,322.43; MTF book 4,351 vs 4,351.4. Pass. Letter p3 total income 1,541 vs results p7 1,540.54. Pass.
- Q2 FY27 other income: results PDF p7 prints 39.01 Cr, handbook Summary P&L!C6 prints 39.02 (total income 1,540.54 in both). Use the results PDF. Six-month: 86.26 (results) vs 86.24 (handbook).
- Orders are lightly restated by handbook vintage (up to 0.02%); use the latest handbook (map section 3).
- SL-Q4FY26: p6 text says F&O mix rose from 53.5% to 54.6%, p7 chart prints 55%, later letters print 54.8%. Use 54.8%.
- SL-Q4FY26 p7 legend order (Float, PL+LAS, MTF, Treasury) does not match the next letters' segment order for Q4 FY26 (MTF 6.9, PL+LAS 5.2). The evidence for 6.9%: SL-Q1FY27 p7 text "MTF (+1.1pp QoQ)" (8.0 - 6.9); the book-yield check in the table; the Q3 FY26 and Q4 FY25/Q1 FY26 columns of the Q4 letter agree with the later letters. Treat the Q4 letter's Q4 FY26 PL+LAS and MTF labels as transposed.
- Fisdom: consolidated from Q3 FY26 (acquired 3 Oct 2025; SL-Q2FY26 p9, SL-Q3FY26 p3). Q2 FY26 mix and income have no Fisdom, so the Q2 to Q3 FY26 step in total income includes acquisition revenue. Fisdom revenue is not disclosed separately; the platform "ex Fisdom" figure gives the gap (Q4 FY26: 15,053.67 consolidated revenue minus 14,684 = 369.7 Mn for Fisdom plus Growwmf).
- Q2 FY27 letter p4 platform revenue (1,497 Cr; handbook 1,497.4) excludes Groww AMC only; Fisdom is now included (SL-Q2FY27 p9). A Q2 FY27 "ex Fisdom/AMC" figure no longer exists, which is a second reason to drop row 120.
- Groww files no monthly data, no orders by segment, and no segment revenue (map sections 2 and 4); the revenue-per-order commentary (Rs 20 per order for F&O and commodity, cash about Rs 15-16; TR-Q2FY27 p10) is spoken, not tabulated.

## 5. Q2 FY27 actuals ready to stage

All proposed in `out/groww/facts_candidates.json` (103 facts, `status 'staged'`, `extracted_by 'claude'` for all: letter charts were read visually, results and transcript text via pdftotext, handbook cells via a zip/XML read of the .xlsx; none was produced by `angel_monthly.py`). Money is stored in Rs Mn (Rs Cr x 10; the printed Cr value is in each note), orders in Mn, shares and mix as fractions.

| Metric | Value | Unit as staged | Printed | Document + page/sheet | Note |
|---|---|---|---|---|---|
| total_income | 15405.4 | Rs Mn | 1,540.54 Cr | RES-Q2FY27 p7 | consolidated |
| revenue_from_ops | 15015.3 | Rs Mn | 1,501.53 Cr | RES-Q2FY27 p7 | |
| other_income | 390.1 | Rs Mn | 39.01 Cr | RES-Q2FY27 p7 | handbook shows 39.02 |
| platform_revenue_ex_amc | 14974 | Rs Mn | 1,497.4 Cr | HB-Q2FY27 Financial KPIs!E5 (letter p4 prints 1,497) | excludes Groww AMC only; Fisdom included |
| revmix_fo | 0.448 | fraction | 44.8% | SL-Q2FY27 p6 | share of total income |
| revmix_cash (Stocks) | 0.174 | fraction | 17.4% | SL-Q2FY27 p6 | new classification (ex IPO/BDSA); brokerage 70-75% of Stocks revenue (p7) |
| revmix_comm | 0.062 | fraction | 6.2% | SL-Q2FY27 p6 | |
| revmix_mtf | 0.101 | fraction | 10.1% | SL-Q2FY27 p6 | derived MTF revenue 10.1% x 1,540.54 = 155.6 Cr (do not stage; show arithmetic) |
| revmix_float / plas / other_operating / other_income | 0.084 / 0.059 / 0.048 / 0.025 | fraction | 8.4 / 5.9 / 4.8 / 2.5% | SL-Q2FY27 p6 | |
| share_fo_adto_q | 0.110 | fraction | 11.0% | SL-Q2FY27 p5 | new basis (denominator exchange x 2); legacy-equivalent 0.220 |
| share_cash_adto_q | 0.154 | fraction | 15.4% | SL-Q2FY27 p5 | new basis; legacy-equivalent 0.308 |
| mtf_share | 0.027 | fraction | 2.7% | SL-Q2FY27 p5 | NSE+BSE combined closing book |
| adto_stocks | 144299.7059 | Rs Mn | 14,429.97059 Cr | HB-Q2FY27 Operational KPIs!E18 | letter prints 14,430 |
| adto_fo_premium | 123224.343 | Rs Mn | 12,322.4343 Cr | HB-Q2FY27 Operational KPIs!E23 | letter prints 12,322 |
| adto_comm_notional | 2835818.725 | Rs Mn | 283,581.8725 Cr | HB-Q2FY27 Operational KPIs!E26 | |
| mtf_book | 43514 | Rs Mn | 4,351.4 Cr | HB-Q2FY27 Operational KPIs!E20 | closing |
| orders_total | 517.305 | Mn | 51.7305 Cr | HB-Q2FY27 Operational KPIs!E10 | Stocks + derivatives; no segment split |
| trading_days | 65 | days | 65 | HB-Q2FY27 Operational KPIs!E36 | |

Also proposed (same file): the restated 5-quarter mix set (Q2 FY26 to Q1 FY27, SL-Q2FY27 p6), the Q1 FY26 and Q4 FY25/Q3 FY25 original-classification MTF and mix values, total income for Q3 FY25, Q4 FY25, Q1 FY26, Q4 FY26 and Q1 FY27 (the corrected bases), Q1 FY26 revenue and other income, platform revenue ex Fisdom/AMC for Q4 FY26 and Q1 FY27 (relabelled), market shares with the basis in `segment`, and the 14.95% MTF yield from the two transcripts.

Not yet available for staging: segment orders, MTF revenue in Rs, a Q2 FY27 NSE active-client count (dropped by Groww from the Q2 FY27 handbook and letter), and any Q3 FY27 figure.
