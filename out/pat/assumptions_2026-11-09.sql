-- PAT valuation inputs follow AB's 06.11 workbook (AB, 9 Nov 2026). DRAFT, NOT APPLIED. Target: everjfpbnlbcpuarnhob, sb_assumptions.
-- Values change: pat_discount_fwd (all) 0.18 -> 0.20; ANGELONE pat_discount_today 0.09 -> 0.10; ANGELONE pat_pe 18,22.5,27 -> 20,24,28.
-- Source refs and notes only: GROWW pat_pe (38,44,50), GROWW pat_discount_today (0.10), pat_adr_qoq_growth (3% / 3.5%).
-- P/E and quarterly ADR growth stay inputs: change them here (sb_assumptions), never in code.
-- Rollback: the same UPDATEs with the old values (git show 4976866:seed/pat_assumptions.json).

begin;

update public.sb_assumptions set value = 0.2, value_text = null,
       source_ref = 'excel[New model - 06.11.26/20260714_brokers dashboard v2 - new.xlsx]:Angel One - ADR model (A+B)!G33; Groww - ADR Model!G34 (20%)', note = '1-year discount on a forward price (AB, 9 Nov 2026: follow the 06.11 workbook; was 18%)'
 where broker_id = '*' and key = 'pat_discount_fwd';
update public.sb_assumptions set value = 0.03, value_text = null,
       source_ref = 'AB instruction, 5 Nov 2026; same value in excel[New model - 06.11.26/20260714_brokers dashboard v2 - new.xlsx]:Angel One - ADR model (A+B)!E57 (3%)', note = 'Broking and MTF ADR grow by this each quarter from the ADR window''s level: the current quarter''s remaining days at the window ADR, the next quarter × (1+g), and so on through Q4 FY28. Input: edit in sb_assumptions.'
 where broker_id = 'ANGELONE' and key = 'pat_adr_qoq_growth';
update public.sb_assumptions set value = null, value_text = '20,24,28',
       source_ref = 'excel[New model - 06.11.26/20260714_brokers dashboard v2 - new.xlsx]:Angel One - ADR model (A+B)!C30:E30', note = 'Input: P/E bear, base, bull (AB, 9 Nov 2026: follow the 06.11 workbook; was 18, 22.5, 27). Edit in sb_assumptions.'
 where broker_id = 'ANGELONE' and key = 'pat_pe';
update public.sb_assumptions set value = 0.1, value_text = null,
       source_ref = 'excel[New model - 06.11.26/20260714_brokers dashboard v2 - new.xlsx]:Angel One - ADR model (A+B)!G34 (10%)', note = 'Second discount from the FY28 price to today (AB, 9 Nov 2026: follow the 06.11 workbook; was 9%)'
 where broker_id = 'ANGELONE' and key = 'pat_discount_today';
update public.sb_assumptions set value = 0.035, value_text = null,
       source_ref = 'AB instruction, 5 Nov 2026; same value in excel[New model - 06.11.26/20260714_brokers dashboard v2 - new.xlsx]:Groww - ADR Model!F58 (3.5%)', note = 'Broking and MTF ADR grow by this each quarter from the ADR window''s level: the current quarter''s remaining days at the window ADR, the next quarter × (1+g), and so on through Q4 FY28. Input: edit in sb_assumptions.'
 where broker_id = 'GROWW' and key = 'pat_adr_qoq_growth';
update public.sb_assumptions set value = null, value_text = '38,44,50',
       source_ref = 'excel[New model - 06.11.26/20260714_brokers dashboard v2 - new.xlsx]:Groww - ADR Model!C31:E31 (=Groww - ADR Model!D207:F207; unchanged)', note = 'Input: P/E bear, base, bull. Edit in sb_assumptions.'
 where broker_id = 'GROWW' and key = 'pat_pe';
update public.sb_assumptions set value = 0.1, value_text = null,
       source_ref = 'excel[New model - 06.11.26/20260714_brokers dashboard v2 - new.xlsx]:Groww - ADR Model!G35 (10%, unchanged)', note = null
 where broker_id = 'GROWW' and key = 'pat_discount_today';

commit;

-- Check: select broker_id, key, value, value_text from sb_assumptions where key in ('pat_pe','pat_discount_fwd','pat_discount_today','pat_adr_qoq_growth') order by 1, 2;
