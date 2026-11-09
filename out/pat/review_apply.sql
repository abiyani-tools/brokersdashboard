-- PLAN 5.7: mark the PAT model's staged facts reviewed (DRAFT, 9 Nov 2026). NOT APPLIED: needs AB's OK (CLAUDE.md rule 7).
-- Target: brokers-dashboard (everjfpbnlbcpuarnhob), table sb_disclosure_facts only.
--
-- Evidence: out/pat/review_check/check_report.md. An independent re-read of every staged row from the cited PDF page
-- found 178 MATCH and 20 DERIVED_OK (0 mismatches) out of 198.
-- AB still decides the open points below (search for "AB:"), then reads this file and applies it.
--
-- Step by step:
--   1. Share counts: replace the two derived share counts with the filed equity-capital lines (AB: keep or drop step 1).
--      a. Angel One: 91.4496 Cr (net worth 67,124 ÷ book value 73.4, deck p30) → 91.459 Cr.
--         Source: ANGEL8896_15102026171541_Outcome.pdf p5 (scanned), "Equity share capital (face value Re. 1 each)"
--         914.59 Rs Mn at 30 Sep 2026. 914.59 Mn ÷ Re 1 = 914.59 Mn shares = 91.459 Cr.
--      b. Groww: 623.905 Cr (31 Mar 2026 capital 1,247.81 ÷ 2, p7, period blank) → 624.21 Cr at 30 Sep 2026.
--         Source: BILLIONBRAINS_14102026124408_outcomefinalsigned.pdf p8 balance sheet, "Equity share capital"
--         1,248.42 Rs Cr at 30 September. 1,248.42 ÷ face value 2 = 624.21 Cr. period_key gets 'Q2 FY 2027'.
--         (In the DB its period_key is '' today; the model takes the shares row with the latest period_key.)
--   2. Mark reviewed the 198 PAT facts: segment 'consolidated', extracted_by 'claude', metric pl_* / trading_days /
--      shares_outstanding_cr.
--   3. Mark reviewed the older Angel One facts that the model also reads, which are still staged in the 3 Nov snapshot:
--      the quarterly depository / other revenue mix (Working sheet - Angel One!F19:M19, M21) and the Q3 FY26 funding
--      book (J31). The guard `status = 'staged'` makes this a no-op for rows that are already reviewed.
--      AB: these are Excel-cell facts (rule 1 allows them); review them against the workbook cells named in source_ref.
-- Open points that stay as filed (no SQL), from the check report:
--   - Angel Q3 FY26 pl_pat 2,687 is line X, after a ~12 Rs Mn prior-year tax credit (FY26 "Taxes for earlier years"
--     (12.80), Outcome p5); PBT − tax = 2,675. It only feeds the last-4-quarter ratios, which do not use PAT.
--   - Groww Q2 FY27 pl_pat 724.70 is total profit; profit attributable to shareholders is 725.65 (NCI −0.95).
--     The effect on FY27 EPS is about 0.0015 Rs.
-- Rollback: step 1 = the two UPDATEs with the old values (91.4496 / 623.905, period_key NULL, the old source_ref and
--           table_label in out/pat/db_inputs.sql); steps 2–3 = set status 'staged', reviewed_at NULL for the same rows.

begin;

-- 1a. Angel One shares (AB: keep or drop)
update public.sb_disclosure_facts
   set value = 91.459,
       source_ref = 'results_outcome:ANGEL8896_15102026171541_Outcome.pdf#page=5',
       table_label = 'Equity share capital (face value Re. 1 each) 914.59 Rs Mn at 30 Sep 2026 ÷ Re 1',
       note = 'Filed share capital ÷ face value: 914.59 Mn shares = 91.459 Cr. Replaces 91.4496 (net worth ÷ book value, deck p30).'
 where broker_id = 'ANGELONE' and metric = 'shares_outstanding_cr' and segment = 'consolidated' and extracted_by = 'claude';

-- 1b. Groww shares (AB: keep or drop)
update public.sb_disclosure_facts
   set value = 624.21,
       period_key = 'Q2 FY 2027',
       source_ref = 'results_outcome:BILLIONBRAINS_14102026124408_outcomefinalsigned.pdf#page=8',
       table_label = 'Equity share capital 1,248.42 Rs Cr at 30 Sep 2026 ÷ face value INR 2',
       note = 'Balance sheet share capital ÷ face value: 1,248.42 ÷ 2 = 624.21 Cr. Replaces 623.905 (31 Mar 2026 capital, p7).'
 where broker_id = 'GROWW' and metric = 'shares_outstanding_cr' and segment = 'consolidated' and extracted_by = 'claude';

-- 2. The 198 PAT facts
update public.sb_disclosure_facts
   set status = 'reviewed', reviewed_at = now()
 where broker_id in ('ANGELONE', 'GROWW') and segment = 'consolidated' and extracted_by = 'claude' and status = 'staged'
   and (metric like 'pl\_%' or metric in ('trading_days', 'shares_outstanding_cr'));

-- 3. Older Angel One facts the model reads (ids from snapshot/db_snapshot_2026-11-03.json)
update public.sb_disclosure_facts
   set status = 'reviewed', reviewed_at = now()
 where broker_id = 'ANGELONE' and status = 'staged'
   and fact_id in (60, 61, 62, 63, 64, 65, 66, 68, 71);

commit;

-- Check after applying: expect 198 for the first count and 0 for the second
--   select count(*) filter (where status = 'reviewed'), count(*) filter (where status = 'staged')
--     from sb_disclosure_facts where segment = 'consolidated' and extracted_by = 'claude';
-- Then a dry run with the service key in the shell (writes nothing): python3 run_pat.py --db
