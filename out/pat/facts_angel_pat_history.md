# Angel One consolidated PAT history (staged, not loaded)

| Quarter | PAT Rs Mn (as printed) | Rs Cr | Results date | Source (page) |
|---|---|---|---|---|
| Q3 FY 2023 | 2,279.82 | 227.98 | 2023-01-16 | Results-1.pdf p6 |
| Q4 FY 2023 | 2,669.12 | 266.91 | 2023-04-17 | Results_17042023.pdf p6 |
| Q1 FY 2024 | 2,208.00 | 220.80 | 2023-07-13 | Financialresults.pdf p5 |
| Q2 FY 2024 | 3,045.00 | 304.50 | 2023-10-12 | outcomeoftheboardmeeting12102023.pdf p5 |
| Q3 FY 2024 | 2,603.00 | 260.30 | 2024-01-15 | Quarterly-Results.pdf p5 |
| Q4 FY 2024 | 3,399.42 | 339.94 | 2024-04-17 | OutcomeBM17042024.pdf p6 |
| Q1 FY 2025 | 2,927.26 | 292.73 | 2024-07-15 | OuctomeandFRfinalJUly2024.pdf p5 |
| Q2 FY 2025 | 4,233.68 | 423.37 | 2024-10-14 | Outocme_14102024-1.pdf p5 |
| Q3 FY 2025 | 2,814.66 | 281.47 | 2025-01-13 | OutcomeofboardmeetingJanuary132025.pdf p5 |
| Q4 FY 2025 | 1,745.21 | 174.52 | 2025-04-16 | Results_Angel-One-Limited.pdf p6 |

FY2025 sum check: 2927.26+4233.68+2814.66+1745.21 = 11720.81 Rs Mn = audited FY25 11,720.81 (diff 0.00); vs stored 11721 diff 0.19 (rounding).

Notes

- Source: Angel One outcome-of-board-meeting PDFs (unaudited results with limited-review for Q1-Q3, audited for Q4), downloaded from the company website w3assets.angelone.in (listed on angelone.in/investor-relations). Saved under data/filings/angelone_hist/ with SHA256SUMS.txt. Each PDF is an image scan; every figure was read visually from the rendered consolidated statement page, not from OCR text.
- Metric = row XI / VII "Profit for the period / year" of the CONSOLIDATED statement (Rs. in million). The statement has no non-controlling-interest split (all profit shown as one line, as in out/pat/facts_angel_pl.json), so attributable = total.
- filing_date = date of the board meeting stated in the company letter to NSE/BSE ("held today i.e. ..."). The exact NSE dissemination timestamp could not be checked: the NSE announcements API is not reachable from this agent (attempt blocked by the auto-mode permission classifier). Letters are same-day, so the date is expected to equal the NSE date. [SOURCE NEEDED: NSE an_dt for each outcome filing, if exact timestamp required]
- Q1-Q3 FY2024 originals print integer Rs Mn (2208, 3045, 2603). Later comparative columns give 2 dp (2208.05, 3044.51, 2603.09/2603.10). No restatement of substance; rounded values agree. Prefer 2-dp comparative if precision is wanted.
- Q3 FY2023 original is 2279.82 and later comparative columns (Q4FY23 filing 2,279.82; Q3FY24 filing 2,280) agree.
- Q2 FY2025 4233.68: the Q2 FY25 filing page text is small; value confirmed against the Q3 FY25 filing comparative column (4,233.68). The continuing-operations row VII is 4,233.80; row XI (total) is 4,233.68 and is used.
- Q4 FY2025 1745.21 is a low quarter vs Q3 (2814.66); it is as printed (row VII, audited, FY25 total 11,720.81).
- FY2025 check: Q1 2927.26 + Q2 4233.68 + Q3 2814.66 + Q4 1745.21 = 11720.81 Rs Mn. Audited FY2025 in the Q4 FY25 filing = 11,720.81 (difference 0.00). Existing out/pat/facts_angel_pl.json FY 2025 pl_pat = 11721 (rounded Rs Mn): difference 0.19 Rs Mn, rounding only.
- TTM P/E series: Q3 FY2023 TTM needs Q4FY22-Q3FY23; Q4 FY2022 (Jan-Mar 2022, 2046.94 Rs Mn per Q4FY23 filing comparative) is not staged as a fact. Q4 FY2023 filing p6 shows it; ask if wanted. First full TTM from data staged here is Q2 FY2024 (Q3FY23..Q2FY24).


## Follow-ups

Q4 FY2022 PAT: 2,046.94 Rs Mn (204.69 Cr), 20 Apr 2022, OutcomeoftheBoardmeeing200422.pdf p14 (primary); Results_17042023.pdf p6 (comparative, same).

### Results dates

| Quarter | Date | Source |
|---|---|---|
| Q4 FY 2022 | 2022-04-20 | OutcomeoftheBoardmeeing200422.pdf#page=1 |
| Q1 FY 2026 | 2025-07-16 | OutcomeBM16072025.pdf#page=1 |
| Q2 FY 2026 | 2025-10-15 | Outcome_BM15102025.pdf#page=1 |
| Q3 FY 2026 | 2026-01-15 | 1768483194528-Outcome-of-BM_Jan-2026.pdf#page=1 |
| Q4 FY 2026 | 2026-04-16 | 1776349099449-OutcomeofBoardMeeting.pdf#page=1 |
| Q1 FY 2027 | 2026-07-15 | 1784121905252-OutcomeoftheBoardmeeting_15072026signed.pdf#page=1 |
| Q2 FY 2027 | 2026-10-15 | Outcome_Q2FY27_15102026.pdf#page=1 |

### Shares (crore)

| Quarter end | Capital Rs Mn | FV printed | As printed (cr) | Current basis Re 1 (cr) | Source |
|---|---|---|---|---|---|
| 2022-12-31 | None | 10 | 8.3357 | 83.357 | Results-1.pdf#page=6 |
| 2023-03-31 | 834.2 | 10 | 8.342 | 83.42 | Results_17042023.pdf#page=7 |
| 2023-06-30 | 838.19 | 10 | 8.3819 | 83.819 | OuctomeandFRfinalJUly2024.pdf#page=5 |
| 2023-09-30 | 838.94 | 10 | 8.3894 | 83.894 | Outocme_14102024-1.pdf#page=5 |
| 2023-12-31 | 839.51 | 10 | 8.3951 | 83.951 | OutcomeofboardmeetingJanuary132025.pdf#page=5 |
| 2024-03-31 | 840.08 | 10 | 8.4008 | 84.008 | OutcomeBM17042024.pdf#page=7 |
| 2024-06-30 | 900.88 | 10 | 9.0088 | 90.088 | OuctomeandFRfinalJUly2024.pdf#page=5 |
| 2024-09-30 | 901.51 | 10 | 9.0151 | 90.151 | Outocme_14102024-1.pdf#page=5 |
| 2024-12-31 | 902.51 | 10 | 9.0251 | 90.251 | OutcomeofboardmeetingJanuary132025.pdf#page=5 |
| 2025-03-31 | 902.94 | 10 | 9.0294 | 90.294 | Results_Angel-One-Limited.pdf#page=7 |
| 2025-06-30 | 905.46 | 10 | 9.0546 | 90.546 | OutcomeBM16072025.pdf#page=4 |
| 2025-09-30 | 907.17 | 10 | 9.0717 | 90.717 | Outcome_BM15102025.pdf#page=5 |
| 2025-12-31 | 908.55 | 10 | 9.0855 | 90.855 | 1768483194528-Outcome-of-BM_Jan-2026.pdf#page=6 |
| 2026-03-31 | 910.86 | 1 | 91.086 | 91.086 | 1776349099449-OutcomeofBoardMeeting.pdf#page=6 |
| 2026-06-30 | 913.52 | 1 | 91.352 | 91.352 | Outcome_Q2FY27_15102026.pdf#page=5 |
| 2026-09-30 | 914.59 | 1 | 91.459 | 91.459 | Outcome_Q2FY27_15102026.pdf#page=5 |

### Split

- event: Sub-division of equity shares
- ratio: 1 existing share of Rs 10 -> 10 shares of Re 1 (10-for-1; no bonus)
- board_approval_date: 2026-01-15
- postal_ballot_notice_date: 2026-01-15 (e-voting cut-off Wed 14 Jan 2026)
- pre_split_issued_paid_up_shares: 90855479
- post_split_shares_same_date: 908554790
- record_date: [SOURCE NEEDED: record date / effective date of split (not in the Jan 2026 or Apr 2026 outcome letters; announcements page and NSE not reachable)]
- latest_possible_effective_date: before 2026-04-16 (Q4 FY26 filing prints EPS as Post split, face value Re 1, with 31 Mar 2025 and FY25 comparatives restated)
- sources: ['outcome_of_board_meeting:1768483194528-Outcome-of-BM_Jan-2026.pdf#page=1,#page=12 (Annexure II)', 'outcome_of_board_meeting:1776349099449-OutcomeofBoardMeeting.pdf#page=6', 'postal_ballot_notice:Jan2026_postal_ballot_notice.pdf; prior_intimation:Jan2026_prior_intimation.pdf (7 Jan 2026)']
- other_corporate_actions_in_window: No bonus issue found in any filing read. Other share-count changes: QIP of 58,70,818 shares allotted 2 Apr 2024 (Q1 FY25 jump 840.08 -> 900.88 Rs Mn), plus ESOP/RSU allotments. A 10-for-1 factor applies to every period-end before the split.

### Notes

- Source: Angel One outcome-of-board-meeting PDFs (unaudited results with limited-review for Q1-Q3, audited for Q4), downloaded from the company website w3assets.angelone.in (listed on angelone.in/investor-relations). Saved under data/filings/angelone_hist/ with SHA256SUMS.txt. Each PDF is an image scan; every figure was read visually from the rendered consolidated statement page, not from OCR text.
- Metric = row XI / VII "Profit for the period / year" of the CONSOLIDATED statement (Rs. in million). The statement has no non-controlling-interest split (all profit shown as one line, as in out/pat/facts_angel_pl.json), so attributable = total.
- filing_date = date of the board meeting stated in the company letter to NSE/BSE ("held today i.e. ..."). The exact NSE dissemination timestamp could not be checked: the NSE announcements API is not reachable from this agent (attempt blocked by the auto-mode permission classifier). Letters are same-day, so the date is expected to equal the NSE date. [SOURCE NEEDED: NSE an_dt for each outcome filing, if exact timestamp required]
- Q1-Q3 FY2024 originals print integer Rs Mn (2208, 3045, 2603). Later comparative columns give 2 dp (2208.05, 3044.51, 2603.09/2603.10). No restatement of substance; rounded values agree. Prefer 2-dp comparative if precision is wanted.
- Q3 FY2023 original is 2279.82 and later comparative columns (Q4FY23 filing 2,279.82; Q3FY24 filing 2,280) agree.
- Q2 FY2025 4233.68: the Q2 FY25 filing page text is small; value confirmed against the Q3 FY25 filing comparative column (4,233.68). The continuing-operations row VII is 4,233.80; row XI (total) is 4,233.68 and is used.
- Q4 FY2025 1745.21 is a low quarter vs Q3 (2814.66); it is as printed (row VII, audited, FY25 total 11,720.81).
- FY2025 check: Q1 2927.26 + Q2 4233.68 + Q3 2814.66 + Q4 1745.21 = 11720.81 Rs Mn. Audited FY2025 in the Q4 FY25 filing = 11,720.81 (difference 0.00). Existing out/pat/facts_angel_pl.json FY 2025 pl_pat = 11721 (rounded Rs Mn): difference 0.19 Rs Mn, rounding only.
- TTM P/E series: Q3 FY2023 TTM needs Q4FY22-Q3FY23; Q4 FY2022 (Jan-Mar 2022, 2046.94 Rs Mn per Q4FY23 filing comparative) is not staged as a fact. Q4 FY2023 filing p6 shows it; ask if wanted. First full TTM from data staged here is Q2 FY2024 (Q3FY23..Q2FY24).
- FOLLOW-UP 1: Q4 FY2022 consolidated PAT 2046.94 Rs Mn staged from its own filing (OutcomeoftheBoardmeeing200422.pdf p14) and also as comparative-sourced from Results_17042023.pdf p6; both agree.
- FOLLOW-UP 2: dates are the board-meeting dates in each outcome letter ("held today i.e. ..."). Q4 FY2026 results were 16 Apr 2026 (outcome 1776349099449-OutcomeofBoardMeeting.pdf); the 15 Jul 2026 deck cited in facts_angel_pl.json for Q4 FY26 is a later presentation, not the results date.
- FOLLOW-UP 3 method: shares = equity share capital (Rs Mn) / face value printed; consolidated and standalone capital are identical. value = crore shares on the face value printed in that period; value_current_basis = crore shares on Re 1 face value = capital Rs Mn / 10 (equity capital in Rs is unchanged by a split). Mar 2026 onward filings already print Re 1.
- Rs Mn capital is rounded to 2 dp in filings; Q2 FY24 own filing printed 839 (rounded) so the 838.94 comparative is used. Q3 FY2023 (31 Dec 2022) is the only quarter with no printed paid-up capital; it is EPS-weighted-share derived and flagged.
- Share facts use quarter-end paid-up capital. TTM P/E check vs vendor: vendor series may use weighted or diluted shares or market cap from NSE; this series is basic paid-up only (ESOP/RSU dilution excluded: 2.64 crore RSUs, 0.89 mn PSUs, 0.79 mn options outstanding at 30 Jun 2026 per Q1 FY27 standalone notes, page 5 of the Jul 2026 letter).
- Existing facts_angel_pl.json holds Q1 FY26 = 1145, Q3 FY26 = 2687 (derived) in Rs Mn. Filings print 1,144.68 (Q1 FY26 p4), 2,117.30 (Q2 FY26 per Q2 FY27 p5), 2,686.64 (Q3 FY26 p6 of Jan 2026 letter; so Q3 need not be derived), 3,202.37 (Q4 FY26 p6). Differences are rounding only. Flagged, not overwritten.
