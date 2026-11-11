-- Groww P/E bands on the Valuation tab (AB, 11 Nov 2026: "add the PE chart with +1, +2, -1, -2 SDs as we have for Angel One").
-- DRAFT until applied. Target: everjfpbnlbcpuarnhob, sb_assumptions. One new row, no schema change; same value as seed/valuation_assumptions.json.
-- With it, run_pat.py builds Groww's consolidated TTM P/E series (src/engine/valuation.py pe_quarters / ttm_pe) and publishes
-- sections 'pe' and 'pe_bands' of sb_valuation_lines for Groww, which the Valuation tab draws.
-- Rollback: delete from public.sb_assumptions where broker_id = 'GROWW' and key = 'val_results_dates';

insert into public.sb_assumptions (broker_id, key, value, value_text, unit, source_ref, note)
values ('GROWW', 'val_results_dates', null,
        'Q3 FY 2025=2025-11-12;Q4 FY 2025=2025-11-12;Q1 FY 2026=2025-11-12;Q2 FY 2026=2025-11-21;Q3 FY 2026=2026-01-14;Q4 FY 2026=2026-04-20;Q1 FY 2027=2026-07-15;Q2 FY 2027=2026-10-14',
        'date per quarter',
        'outcome of board meeting letters, page 1 ("held today"): BILLIONBRAINS_21112025102506_BMoutcomeintimati.pdf (November 21, 2025), _14012026123241_OutcomeSigned.pdf (January 14, 2026), _20042026130140_Boardoutcomesigned.pdf (April 20, 2026), _15072026112913_outcomefinal.pdf (July 15, 2026), _14102026124408_outcomefinalsigned.pdf (October 14, 2026); the quarters before the listing on the listing day, 2025-11-12',
        'Results date of each quarter: from that date its consolidated PAT counts in the trailing 12 months of the P/E series (the Angel One rule). Q3 FY25 to Q1 FY26 ended before Groww listed (12 Nov 2025) and count from the listing day, as in the workbook''s ''Groww charts''!G (which brings each later quarter in at its quarter end instead). Q3 FY25 PAT (Rs 757 Cr) includes a negative employee cost; it leaves the TTM on 14 Jan 2026.')
on conflict do nothing;
