-- Valuation (PLAN 5.8): DB inputs. DRAFT, NOT APPLIED. Target: everjfpbnlbcpuarnhob (brokers-dashboard), sb_* only.
-- Apply AFTER migrations/20261109_sb_valuation_lines.sql. Step by step:
--   1. sb_assumptions: adds the 7 val_* rows of seed/valuation_assumptions.json (weights 20/30/50, regression band 10%,
--      45-day window, series start per broker, P/E band window, Angel results dates). Adds only missing keys.
--   2. sb_assumptions: P/E and Groww growth follow the 09.11 workbook (AB, 9 Nov 2026, point 5):
--      ANGELONE pat_pe 20,24,28 -> 22,27,32; GROWW pat_pe 38,44,50 -> 44.3,50,55.7; GROWW pat_adr_qoq_growth 0.035 -> 0.04.
--      This moves the PAT model's FY28 targets (and so the ADR leg): Angel base about 344.7 -> 387.8, Groww 198.8 -> 229.4
--      (dry run on the 6 Nov runs, out/pat/2026-11-06/).
--   3. sb_disclosure_facts: stages 27 Angel One facts for the P/E series, status 'staged': consolidated quarterly PAT
--      Q4 FY22 - Q4 FY25 (pl_pat) and quarter-end share counts Q3 FY23 - Q2 FY27 on today's Re 1 basis
--      (shares_period_end_cr, a separate metric so the PAT model's shares_outstanding_cr is untouched). Read from the
--      outcome filings (out/pat/facts_angel_pat_history.md). The engine reads reviewed facts only: step 4 after AB's check.
-- Idempotent: running it twice adds nothing.
-- Rollback: delete from sb_assumptions where key like 'val_%';
--           the step-2 UPDATEs with the old values above;
--           delete from sb_disclosure_facts where broker_id = 'ANGELONE' and extracted_by = 'claude'
--             and (metric = 'shares_period_end_cr' or (metric = 'pl_pat' and source_ref like 'outcome_of_board_meeting:%'));

begin;

insert into public.sb_assumptions (broker_id, key, value, value_text, unit, source_ref, note)
select x.broker_id, x.key, x.value, x.value_text, x.unit, x.source_ref, x.note
from jsonb_to_recordset($json$[
{
"broker_id": "*",
"key": "val_weights",
"value": null,
"value_text": "0.2,0.3,0.5",
"unit": "fraction (regression,ratio,adr)",
"source_ref": "excel[New Model - 09.11.26/20260714_brokers dashboard v2.xlsx]:Groww - ADR Model!H71:H73; Angel One - ADR model (A+B)!G70:G72",
"note": "Triangulation weights, used as SUMPRODUCT for both brokers (AB, 9 Nov 2026, point 1: the Angel sheet's plain AVERAGE is replaced)"
},
{
"broker_id": "*",
"key": "val_regression_band",
"value": 0.1,
"value_text": null,
"unit": "fraction",
"source_ref": "excel[New Model - 09.11.26/20260714_brokers dashboard v2.xlsx]:Angel One - ADR model (A+B)!B70; Groww - ADR Model!C71",
"note": "Bear / bull = slope × ADR × (1 ∓ band) + intercept"
},
{
"broker_id": "*",
"key": "val_dma_days",
"value": 45,
"value_text": null,
"unit": "trading days",
"source_ref": "excel[New Model - 09.11.26/20260714_brokers dashboard v2.xlsx]:Angel One Revenue!N48 (=AVERAGE(M4:M48)); Groww Revenue!N48",
"note": "Moving average of daily ADR (broking + MTF) the price is regressed on and divided by"
},
{
"broker_id": "*",
"key": "val_pe_since",
"value": null,
"value_text": "2025-04-01",
"unit": "date",
"source_ref": "excel[New Model - 09.11.26/20260714_brokers dashboard v2.xlsx]:Angel One - ADR model (A+B)!AE80:AF84 (since Apr-25)",
"note": "Start of the second P/E band window; the first is the last 3 years (X80:X84)"
},
{
"broker_id": "ANGELONE",
"key": "val_series_start",
"value": null,
"value_text": "2025-01-01",
"unit": "date",
"source_ref": "excel[New Model - 09.11.26/20260714_brokers dashboard v2.xlsx]:Angel One Revenue!C1 (Start date)",
"note": "First ADR day of the regression / ratio series; the fit starts at the 45th day (2025-03-04 in the workbook)"
},
{
"broker_id": "GROWW",
"key": "val_series_start",
"value": null,
"value_text": "2025-11-12",
"unit": "date",
"source_ref": "excel[New Model - 09.11.26/20260714_brokers dashboard v2.xlsx]:Groww Revenue!B4 (first date)",
"note": "First ADR day of the regression / ratio series (Groww listed 12 Nov 2025); the fit starts at the 45th day (2026-01-14 in the workbook)"
},
{
"broker_id": "ANGELONE",
"key": "val_results_dates",
"value": null,
"value_text": "Q4 FY 2022=2022-04-20;Q3 FY 2023=2023-01-16;Q4 FY 2023=2023-04-17;Q1 FY 2024=2023-07-13;Q2 FY 2024=2023-10-12;Q3 FY 2024=2024-01-15;Q4 FY 2024=2024-04-17;Q1 FY 2025=2024-07-15;Q2 FY 2025=2024-10-14;Q3 FY 2025=2025-01-13;Q4 FY 2025=2025-04-16;Q1 FY 2026=2025-07-16;Q2 FY 2026=2025-10-15;Q3 FY 2026=2026-01-15;Q4 FY 2026=2026-04-16;Q1 FY 2027=2026-07-15;Q2 FY 2027=2026-10-15",
"unit": "date per quarter",
"source_ref": "outcome_of_board_meeting letters, page 1 (\"held today\"), one per quarter: out/pat/facts_angel_pat_history.md",
"note": "Results (board meeting) date of each quarter: from that date its consolidated PAT counts in the trailing 12 months of the P/E series. [SOURCE NEEDED: NSE dissemination timestamps; the letters are same-day]"
}
]$json$::jsonb)
  as x(broker_id text, key text, value numeric, value_text text, unit text, source_ref text, note text)
where not exists (select 1 from public.sb_assumptions a where a.broker_id = x.broker_id and a.key = x.key);

update public.sb_assumptions set value = null, value_text = '22,27,32',
       source_ref = 'excel[New Model - 09.11.26/20260714_brokers dashboard v2.xlsx]:Angel One - ADR model (A+B)!C30:E30', note = 'Input: P/E bear, base, bull (AB, 9 Nov 2026: follow the 09.11 workbook; was 20, 24, 28). Edit in sb_assumptions.'
 where broker_id = 'ANGELONE' and key = 'pat_pe';
update public.sb_assumptions set value = null, value_text = '44.3,50,55.7',
       source_ref = 'excel[New Model - 09.11.26/20260714_brokers dashboard v2.xlsx]:Groww - ADR Model!C31:E31', note = 'Input: P/E bear, base, bull (AB, 9 Nov 2026: follow the 09.11 workbook; was 38, 44, 50). Edit in sb_assumptions.'
 where broker_id = 'GROWW' and key = 'pat_pe';
update public.sb_assumptions set value = 0.04, value_text = null,
       source_ref = 'excel[New Model - 09.11.26/20260714_brokers dashboard v2.xlsx]:Groww - ADR Model!F58 (4%)', note = 'Broking and MTF ADR grow by this each quarter from the ADR window''s level: the current quarter''s remaining days at the window ADR, the next quarter × (1+g), and so on through Q4 FY28. (AB, 9 Nov 2026: follow the 09.11 workbook; was 3.5%.) Input: edit in sb_assumptions.'
 where broker_id = 'GROWW' and key = 'pat_adr_qoq_growth';

insert into public.sb_disclosure_facts (broker_id, period_type, period_key, metric, segment, value, unit,
                                        table_label, source_ref, extracted_by, status, note)
select x.broker_id, x.period_type, x.period_key, x.metric, x.segment, x.value, x.unit, x.table_label,
       x.source_ref, x.extracted_by, x.status, x.note
from jsonb_to_recordset($json$[
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q3 FY 2023",
"metric": "pl_pat",
"segment": "consolidated",
"value": 2279.82,
"unit": "Rs Mn",
"table_label": "Consolidated statement of financial results: Profit for the period / year (XI = VII+X)",
"source_ref": "outcome_of_board_meeting:Results-1.pdf#page=6",
"extracted_by": "claude",
"status": "staged",
"note": null
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q4 FY 2023",
"metric": "pl_pat",
"segment": "consolidated",
"value": 2669.12,
"unit": "Rs Mn",
"table_label": "Consolidated statement of financial results: Profit for the period / year (XI = VII+X)",
"source_ref": "outcome_of_board_meeting:Results_17042023.pdf#page=6",
"extracted_by": "claude",
"status": "staged",
"note": null
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q1 FY 2024",
"metric": "pl_pat",
"segment": "consolidated",
"value": 2208,
"unit": "Rs Mn",
"table_label": "Consolidated statement of financial results: Profit for the period / year (XI = VII+X)",
"source_ref": "outcome_of_board_meeting:Financialresults.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": "Filing prints Rs Mn rounded to integer; 2-dp comparative recorded separately below"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q2 FY 2024",
"metric": "pl_pat",
"segment": "consolidated",
"value": 3045,
"unit": "Rs Mn",
"table_label": "Consolidated statement of financial results: Profit for the period / year (XI = VII+X)",
"source_ref": "outcome_of_board_meeting:outcomeoftheboardmeeting12102023.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": "Filing prints Rs Mn rounded to integer; 2-dp comparative recorded separately below"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q3 FY 2024",
"metric": "pl_pat",
"segment": "consolidated",
"value": 2603,
"unit": "Rs Mn",
"table_label": "Consolidated statement of financial results: Profit for the period / year (XI = VII+X)",
"source_ref": "outcome_of_board_meeting:Quarterly-Results.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": "Filing prints Rs Mn rounded to integer; 2-dp comparative recorded separately below"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q4 FY 2024",
"metric": "pl_pat",
"segment": "consolidated",
"value": 3399.42,
"unit": "Rs Mn",
"table_label": "Consolidated statement of financial results: Profit for the period / year (XI = VII+X)",
"source_ref": "outcome_of_board_meeting:OutcomeBM17042024.pdf#page=6",
"extracted_by": "claude",
"status": "staged",
"note": null
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q1 FY 2025",
"metric": "pl_pat",
"segment": "consolidated",
"value": 2927.26,
"unit": "Rs Mn",
"table_label": "Consolidated statement of financial results: Profit for the period / year (XI = VII+X)",
"source_ref": "outcome_of_board_meeting:OuctomeandFRfinalJUly2024.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": null
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q2 FY 2025",
"metric": "pl_pat",
"segment": "consolidated",
"value": 4233.68,
"unit": "Rs Mn",
"table_label": "Consolidated statement of financial results: Profit for the period / year (XI = VII+X)",
"source_ref": "outcome_of_board_meeting:Outocme_14102024-1.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": null
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q3 FY 2025",
"metric": "pl_pat",
"segment": "consolidated",
"value": 2814.66,
"unit": "Rs Mn",
"table_label": "Consolidated statement of financial results: Profit for the period / year (XI = VII+X)",
"source_ref": "outcome_of_board_meeting:OutcomeofboardmeetingJanuary132025.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": null
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q4 FY 2025",
"metric": "pl_pat",
"segment": "consolidated",
"value": 1745.21,
"unit": "Rs Mn",
"table_label": "Consolidated statement of financial results: Profit for the period / year (VII = V-VI)",
"source_ref": "outcome_of_board_meeting:Results_Angel-One-Limited.pdf#page=6",
"extracted_by": "claude",
"status": "staged",
"note": null
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q4 FY 2022",
"metric": "pl_pat",
"segment": "consolidated",
"value": 2046.94,
"unit": "Rs Mn",
"table_label": "Consolidated statement of financial results: Profit for the period / year (XI = VII+X)",
"source_ref": "outcome_of_board_meeting:OutcomeoftheBoardmeeing200422.pdf#page=14",
"extracted_by": "claude",
"status": "staged",
"note": "Primary: Q4 FY22 own filing, consolidated statement, 31 March 2022 column (text layer of scan; value 2,046.94). Cross-checked: identical figure in the 31 March 2022 comparative column of Results_17042023.pdf p6 (read visually)."
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q3 FY 2023",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 83.357,
"unit": "crore shares",
"table_label": "Consolidated statement p6: basic EPS from total operations (Rs. 27.35) with PAT row XI",
"source_ref": "outcome_of_board_meeting:Results-1.pdf#page=6",
"extracted_by": "claude",
"status": "staged",
"note": "[DERIVED, NOT PERIOD-END: paid-up capital at 31 Dec 2022 is not printed in the Q3 FY23 filing. 2279.82 Mn / basic EPS 27.35 = 83.36 Mn weighted shares (FV Rs 10) = 8.336 crore; EPS rounding gives 83.34-83.37 Mn. Bracket: 31 Mar 2023 paid-up 83.42 Mn (834.20/10). Prefer [SOURCE NEEDED: 31 Dec 2022 paid-up capital or Q3 FY23 shareholding pattern] if exact needed.]"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q4 FY 2023",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 83.42,
"unit": "crore shares",
"table_label": "Consolidated balance sheet: Equity share capital",
"source_ref": "outcome_of_board_meeting:Results_17042023.pdf#page=7",
"extracted_by": "claude",
"status": "staged",
"note": "834.2 Rs Mn / Rs 10 = 83.420 Mn shares = 8.3420 crore as printed; x10 for Re 1 basis"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q1 FY 2024",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 83.819,
"unit": "crore shares",
"table_label": "Statement of consolidated results: Equity share capital (30 June 2023 comparative column)",
"source_ref": "outcome_of_board_meeting:OuctomeandFRfinalJUly2024.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": "comparative-sourced (own Q1 FY24 filing does not print the row); 838.19 Rs Mn / Rs 10 = 83.819 Mn shares = 8.3819 crore as printed; x10 for Re 1 basis"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q2 FY 2024",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 83.894,
"unit": "crore shares",
"table_label": "Statement of consolidated results: Equity share capital (30 Sep 2023 comparative column)",
"source_ref": "outcome_of_board_meeting:Outocme_14102024-1.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": "comparative-sourced; own Q2 FY24 filing p6 prints 839 (rounded); 838.94 Rs Mn / Rs 10 = 83.894 Mn shares = 8.3894 crore as printed; x10 for Re 1 basis"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q3 FY 2024",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 83.951,
"unit": "crore shares",
"table_label": "Statement of consolidated results: Equity share capital (31 Dec 2023 comparative column)",
"source_ref": "outcome_of_board_meeting:OutcomeofboardmeetingJanuary132025.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": "comparative-sourced; own Q3 FY24 filing does not print the row; 839.51 Rs Mn / Rs 10 = 83.951 Mn shares = 8.3951 crore as printed; x10 for Re 1 basis"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q4 FY 2024",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 84.008,
"unit": "crore shares",
"table_label": "Consolidated balance sheet: Equity share capital",
"source_ref": "outcome_of_board_meeting:OutcomeBM17042024.pdf#page=7",
"extracted_by": "claude",
"status": "staged",
"note": "840.08 Rs Mn / Rs 10 = 84.008 Mn shares = 8.4008 crore as printed; x10 for Re 1 basis"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q1 FY 2025",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 90.088,
"unit": "crore shares",
"table_label": "Statement of consolidated results: Equity share capital (Face value Rs. 10 each)",
"source_ref": "outcome_of_board_meeting:OuctomeandFRfinalJUly2024.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": "900.88 Rs Mn / Rs 10 = 90.088 Mn shares = 9.0088 crore as printed; x10 for Re 1 basis"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q2 FY 2025",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 90.151,
"unit": "crore shares",
"table_label": "Statement of consolidated results: Equity share capital (Face value Rs. 10 each)",
"source_ref": "outcome_of_board_meeting:Outocme_14102024-1.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": "901.51 Rs Mn / Rs 10 = 90.151 Mn shares = 9.0151 crore as printed; x10 for Re 1 basis"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q3 FY 2025",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 90.251,
"unit": "crore shares",
"table_label": "Statement of consolidated results: Equity share capital (Face value Rs. 10 each)",
"source_ref": "outcome_of_board_meeting:OutcomeofboardmeetingJanuary132025.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": "902.51 Rs Mn / Rs 10 = 90.251 Mn shares = 9.0251 crore as printed; x10 for Re 1 basis"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q4 FY 2025",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 90.294,
"unit": "crore shares",
"table_label": "Consolidated balance sheet: Equity share capital",
"source_ref": "outcome_of_board_meeting:Results_Angel-One-Limited.pdf#page=7",
"extracted_by": "claude",
"status": "staged",
"note": "902.94 Rs Mn / Rs 10 = 90.294 Mn shares = 9.0294 crore as printed; x10 for Re 1 basis"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q1 FY 2026",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 90.546,
"unit": "crore shares",
"table_label": "Statement of consolidated results: Equity share capital (Face value Rs. 10 each)",
"source_ref": "outcome_of_board_meeting:OutcomeBM16072025.pdf#page=4",
"extracted_by": "claude",
"status": "staged",
"note": "905.46 Rs Mn / Rs 10 = 90.546 Mn shares = 9.0546 crore as printed; x10 for Re 1 basis"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q2 FY 2026",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 90.717,
"unit": "crore shares",
"table_label": "Consolidated balance sheet: Equity share capital",
"source_ref": "outcome_of_board_meeting:Outcome_BM15102025.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": "907.17 Rs Mn / Rs 10 = 90.717 Mn shares = 9.0717 crore as printed; x10 for Re 1 basis"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q3 FY 2026",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 90.855,
"unit": "crore shares",
"table_label": "Statement of consolidated results: Equity share capital (Face value Rs. 10 each)",
"source_ref": "outcome_of_board_meeting:1768483194528-Outcome-of-BM_Jan-2026.pdf#page=6",
"extracted_by": "claude",
"status": "staged",
"note": "matches pre-split issued shares 90,855,479 in same filing Annexure II p12; 908.55 Rs Mn / Rs 10 = 90.855 Mn shares = 9.0855 crore as printed; x10 for Re 1 basis"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q4 FY 2026",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 91.086,
"unit": "crore shares",
"table_label": "Statement of consolidated results: Equity share capital (face value Re. 1 each), year ended 31 March 2026",
"source_ref": "outcome_of_board_meeting:1776349099449-OutcomeofBoardMeeting.pdf#page=6",
"extracted_by": "claude",
"status": "staged",
"note": "first filing printed post-split; 910.86 Rs Mn / Re 1 = 910.86 Mn shares = 91.0860 crore; already post-split; pre-split equivalent 9.1086 crore"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q1 FY 2027",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 91.352,
"unit": "crore shares",
"table_label": "Statement of consolidated results: Equity share capital (face value Re. 1 each), 30 June 2026 column",
"source_ref": "outcome_of_board_meeting:Outcome_Q2FY27_15102026.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": "taken from Q2 FY27 consolidated statement; own Q1 FY27 filing standalone p4 also prints 913.52; 913.52 Rs Mn / Re 1 = 913.52 Mn shares = 91.3520 crore; already post-split; pre-split equivalent 9.1352 crore"
},
{
"broker_id": "ANGELONE",
"period_type": "Q",
"period_key": "Q2 FY 2027",
"metric": "shares_period_end_cr",
"segment": "consolidated",
"value": 91.459,
"unit": "crore shares",
"table_label": "Statement of consolidated results: Equity share capital (face value Re. 1 each)",
"source_ref": "outcome_of_board_meeting:Outcome_Q2FY27_15102026.pdf#page=5",
"extracted_by": "claude",
"status": "staged",
"note": "914.59 Rs Mn / Re 1 = 914.59 Mn shares = 91.4590 crore; already post-split; pre-split equivalent 9.1459 crore"
}
]$json$::jsonb)
  as x(broker_id text, period_type text, period_key text, metric text, segment text, value numeric, unit text,
       table_label text, source_ref text, extracted_by text, status text, note text)
where not exists (select 1 from public.sb_disclosure_facts f
                  where f.broker_id = x.broker_id and f.metric = x.metric and f.period_key = x.period_key
                    and f.segment = x.segment and f.source_ref = x.source_ref);

commit;

-- Step 4 (after AB has checked out/pat/facts_angel_pat_history.md): mark the step-3 facts reviewed.
-- update public.sb_disclosure_facts set status = 'reviewed'
--  where broker_id = 'ANGELONE' and extracted_by = 'claude' and status = 'staged'
--    and (metric = 'shares_period_end_cr' or (metric = 'pl_pat' and source_ref like 'outcome_of_board_meeting:%'));
-- Check: select key, broker_id, value, value_text from sb_assumptions where key like 'val_%' or key in ('pat_pe', 'pat_adr_qoq_growth') order by 1, 2;
