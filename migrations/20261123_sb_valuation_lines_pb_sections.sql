-- 23 Nov 2026: let sb_valuation_lines hold Motilal Oswal's P/B lines (engine PR #18, merged 20 Nov 2026).
--
-- Why: valuation.pb_lines writes three new sections, 'pb' (the daily P/B series), 'pb_bands' (mean / SD / current per
-- window) and 'pb_book' (each quarter's net worth, shares and BVPS). The table's section check, from
-- migrations/20261109_sb_valuation_lines.sql, allows only 'summary', 'inputs', 'common', 'weights', 'series', 'pe'
-- and 'pe_bands', so the daily job's PAT step failed on 23 Nov 2026 (run 45113555717): "upsert into sb_valuation_lines
-- (rows 0..499) failed: HTTP 400 ... violates check constraint sb_valuation_lines_section_check" for MOSL's first
-- pb_bands row. Angel One's and Groww's lines published; MOSL's P/B lines were not written.
--
-- What this does: replaces the section check with the same list plus 'pb', 'pb_bands' and 'pb_book'. No data changes,
-- no other column changes. The ExchangesDash mirror's copy of this table has no checks, so nothing is needed there.
--
-- Undo (only once no pb rows remain):
--   delete from public.sb_valuation_lines where section in ('pb', 'pb_bands', 'pb_book');
--   alter table public.sb_valuation_lines drop constraint sb_valuation_lines_section_check;
--   alter table public.sb_valuation_lines add constraint sb_valuation_lines_section_check
--     check (section in ('summary', 'inputs', 'common', 'weights', 'series', 'pe', 'pe_bands'));

alter table public.sb_valuation_lines drop constraint sb_valuation_lines_section_check;
alter table public.sb_valuation_lines add constraint sb_valuation_lines_section_check
  check (section in ('summary', 'inputs', 'common', 'weights', 'series', 'pe', 'pe_bands', 'pb', 'pb_bands', 'pb_book'));
