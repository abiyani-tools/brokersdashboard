#!/usr/bin/env python3
"""MOSL switch m-f (MTF yield: typed yields kept, 12.94% carried): independent recompute of out/bridges/mosl_f.md at 990eb5d.
Python standard library only.  Run: python3 mosl_switch_f_check.py   (writes mosl_switch_f.md next to it)."""
import os
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mosl_common as c

I = c.load_inputs()
text = c.git_show('out/bridges/mosl_f.md')
items = c.Items()

E = c.build_live('abcde')
F = c.build_live('abcdef')
kw_e, kw_f = c.stat_kw('abcde'), c.stat_kw('abcdef')

c.check_adr(items, text, E.rows, kw_e, F.rows, kw_f)
only_mine, only_br = c.check_params(items, text, E.par, F.par)      # the bridge has no 'moved' table: none may move
c.check_row_stats(items, text, E.rows, True, F.rows, True)

# ---- the yields
typed = [(q, I.wb_fact[('mtf_nii_yield', q)]) for q in c.QS if ('mtf_nii_yield', q) in I.wb_fact]
items.add_bool('yield', 'nine typed yields Q1 FY25 - Q1 FY27 kept: %s' % ', '.join('%.4f' % v for q, v in typed),
               [q for q, v in typed] == c.REPORTED[:9] and all(F.nii[q] == v for q, v in typed))
items.add_bool('yield', 'typed yields lie in the 11.9%% - 15.5%% band of the workbook (Methodology 2b): min %.4f max %.4f' % (min(v for q, v in typed), max(v for q, v in typed)),
               abs(min(v for q, v in typed) - 0.1192) < 5e-5 and abs(max(v for q, v in typed) - 0.1548) < 5e-5)
carry = I.assump['mtf_nii_yield_carry']
items.add_bool('yield', 'carry assumption row mtf_nii_yield_carry = %.17g = 12.94%% (rounded), equal to the last typed Q1 FY27 yield %.17g' % (carry['value'], I.wb_fact[('mtf_nii_yield', 'Q1 FY 2027')]),
               carry['value'] == I.wb_fact[('mtf_nii_yield', 'Q1 FY 2027')] and round(carry['value'] * 100, 2) == 12.94)
items.add_bool('yield', 'carry row is labelled: note starts "[SOURCE NEEDED: MOSL does not publish an MTF yield]", source_ref names assumptions!F14',
               carry['note'].startswith('[SOURCE NEEDED: MOSL does not publish an MTF yield]') and 'F14' in carry['source_ref'])
items.add_bool('yield', 'Q2 FY27 (now reported) and Q3 FY27 (open) both use the carry: %.6f / %.6f' % (F.nii['Q2 FY 2027'], F.nii['Q3 FY 2027']),
               F.nii['Q2 FY 2027'] == carry['value'] == F.nii['Q3 FY 2027'])
items.add_bool('yield', 'no number moves: m-f only turns the workbook\'s unlabelled F15 = F14 into the labelled row (all rows of every segment identical to state e)',
               all(E.rows[s] == F.rows[s] for s in c.SEGS) and not only_mine and not only_br)
items.add_bool('yield', 'day basis stays 247 (assumption row mtf_day_basis = %s; FY26 has %d equity days in the calendar, FY27 will differ)' % (
    I.day_basis, sum(1 for v in I.cal.values() if v['is_equity_day'] and v['fy'] == 'FY 2026')), I.day_basis == 247)

# ---- MTF share of each reported quarter = disclosed closing book / industry book on the quarter's last day with a book
wbc = I.fx['calib']['mtf']
for q in c.REPORTED[2:]:
    cl, cl_d = c.ind_close(q)
    sh = c.mtf_book(q) / cl
    if q == 'Q2 FY 2027':
        items.add_bool('mtf book', '%s: disclosed book %.0f Cr / industry %.2f Cr (%s) = %.5f (the workbook carried %.5f)' % (q, c.mtf_book(q), cl, cl_d, sh, wbc[q]['share']),
                       abs(F.share_mtf[q] - sh) < 1e-15 and abs(sh - 0.0635) < 5e-5 and c.mtf_book(q) == 9600.0 and sh != wbc[q]['share'])
    else:
        items.add_bool('mtf book', '%s: disclosed book %.0f Cr / industry %.2f Cr (%s) = %.5f = the workbook\'s share' % (q, c.mtf_book(q), cl, cl_d, sh),
                       abs(F.share_mtf[q] - sh) < 1e-15 and abs(sh - wbc[q]['share']) < 1e-12 and abs(F.nii[q] - wbc[q]['nii']) < 1e-15)
# daily MTF rows: unchanged against the workbook's cached rows through Q1 FY27, +9.9741% in Q2 FY27 (new share, same yield)
Cc = c.parity_cached_rows()['mtf']
mx = max(abs(F.rows['mtf'][d] - Cc[d]) / Cc[d] for d in Cc if c.q_of(d) != 'Q2 FY 2027')
items.add_bool('mtf book', 'MTF daily rows Q3 FY25 - Q1 FY27 equal the workbook\'s cached rows (max rel diff %.1e): typed yields and book shares kept' % mx, mx < 1e-12)
rr = [F.rows['mtf'][d] / Cc[d] for d in Cc if c.q_of(d) == 'Q2 FY 2027']
ta = c.find_table(c.git_show('out/bridges/mosl_a.md'), ['Segment', 'Days before'])
mtf_row = [r for r in ta['rows'] if r[0] == 'MTF'][0]
items.add('mtf book', 'MTF daily rows Q2 FY27 vs the workbook: ratio new share / carried share over %d days (bridge m-a MTF ratio min)' % len(rr), min(rr), mtf_row[6])
items.add('mtf book', 'same ratio, max (bridge m-a MTF ratio max)', max(rr), mtf_row[7])
items.add_bool('mtf book', 'Q2 FY27 MTF ratio is one number for all %d days (spread %.1e)' % (len(rr), max(rr) - min(rr)), max(rr) - min(rr) < 1e-12)
# MTF ADR of each reported quarter (information: no bridge number) and the Q2 FY27 / Q1 FY27 movement the carry hides
for q in ('Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027', 'Q2 FY 2027', 'Q3 FY 2027'):
    v, n, e = c.seg_adr(F.rows, 'mtf', 'q', q, silent_zero=False, with_n=True)
    items.add_bool('info', 'MTF ADR %s = %.6f Cr over %d days (share %.5f x yield %.5f / 247 x book)' % (q, v, n, F.share_mtf[q], F.nii[q]), n > 0)

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mosl_switch_f.md')
    intro = ['Script: `out/checks/mosl_switch_f_check.py` (+ `mosl_common.py`), Python standard library only; inputs read with `git show 990eb5d:<path>` (`snapshot/mosl_snapshot_2026-10-23.json` carries the typed yields and the new `mtf_nii_yield_carry` row; reviewed facts carry the disclosed MTF book; industry book from the db snapshot). Nothing under `src/engine/` or `src/live/` was read. Bridge: `out/bridges/mosl_f.md`.',
             '',
             'Before = my state a+b+c+d+e, after = a+b+c+d+e+f. MTF revenue = share x industry daily book x yield / 247, share = disclosed closing book / industry book on the quarter\'s last day with a book (m-a supplies Q2 FY27: 9,600 / 151,133.98 = 6.35%), yield = the workbook\'s typed value for Q1 FY25 - Q1 FY27 and the 12.94% carry for Q2 and Q3 FY27. The bridge has no "Parameters that moved" table; I check that no parameter of any segment moves between my states e and f.']
    cols = ['Item', 'Mine', 'Bridge', 'Verdict', 'Criterion', 'Max rel diff']
    sections = [('Headline (Consolidated)', ['Consolidated headline'], cols),
                ('ADR by period and panel', ['ADR'], cols),
                ('Yields', ['yield', 'param set'], cols),
                ('MTF share from the disclosed book', ['mtf book'], cols),
                ('MTF ADR by reported quarter (information)', ['info'], cols),
                ('Daily revenue rows that changed', ['daily rows'], cols)]
    n, a = c.write_md(out, 'MOSL switch m-f: independent recompute', intro, items, sections, explain={})
    print('m-f: %d/%d items agree' % (a, n))
    for r in items.rows:
        if not r[4]:
            print('DIFFER', r[0], r[1], r[2], r[3], r[5])
