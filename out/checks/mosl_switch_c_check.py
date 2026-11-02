#!/usr/bin/env python3
"""MOSL switch m-c (no silent zeros): independent recompute of out/bridges/mosl_c.md at 990eb5d.
Python standard library only.  Run: python3 mosl_switch_c_check.py   (writes mosl_switch_c.md next to it)."""
import os
import re
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mosl_common as c

I = c.load_inputs()
text = c.git_show('out/bridges/mosl_c.md')
items = c.Items()

B = c.build_live('ab')
Cm = c.build_live('abc')
kw_b, kw_c = c.stat_kw('ab'), c.stat_kw('abc')

c.check_adr(items, text, B.rows, kw_b, Cm.rows, kw_c)
c.check_params(items, text, B.par, Cm.par)
c.check_row_stats(items, text, B.rows, False, Cm.rows, True)

# ---- the days that have no row after m-c (bridge lines "F&O: 124 day(s) have no row ...: first .. last")
names = {'F&O': 'fo', 'Cash': 'cash', 'Commodities': 'comm'}
for m_ in re.finditer(r'^(F&O|Cash|Commodities): (\d+) day\(s\) have no row after m-c.*?: (\d{4}-\d\d-\d\d) \.\. (\d{4}-\d\d-\d\d)', text, re.M):
    seg, n, first, last = m_.group(1), int(m_.group(2)), m_.group(3), m_.group(4)
    s = names[seg]
    gone = sorted(d for d, v in B.rows[s].items() if v == c.ERR or v is None)
    gone = [d for d in gone if d not in Cm.rows[s] or Cm.rows[s][d] in (c.ERR, None)]
    # F&O: error rows are those before Q1 FY25 (no table row); commodities: #N/A and blank Q3 rows; cash: Q3 #N/A rows
    if s == 'comm':
        gone = sorted(d for d in c.days_of(c.OPEN, sorted(Cm.rows['comm'])) if Cm.rows['comm'][d] in (c.ERR, None))
        # the bridge counts only rows that exist in the workbook (7 #N/A rows); the 7 blank rows are not rows at all
        gone = [d for d in gone if Cm.rows['comm'][d] == c.ERR]
    items.add_bool('no-row days', '%s: %d days with no row, %s .. %s' % (seg, n, first, last),
                   len(gone) == n and gone[0] == first and gone[-1] == last, 'mine %d days %s .. %s' % (len(gone), gone[0], gone[-1]))
# ---- no key day is missing, non-ok or zero in the reviewed inputs, so the exclusions above are only the error rows
cal_eq = [d for d, v in I.cal.items() if v['is_equity_day'] and d >= c.START]
cal_mcx = [d for d, v in I.cal.items() if v['is_mcx_day'] and d >= c.START]
items.add_bool('keys', 'lake F&O and cash keys: every equity day from 2024-04-01 (%d days) present, status ok, non-zero (nse io, bse, nse cash, bse cash)' % len(cal_eq),
               all(all(d in I.lk_raw[k] and I.lk_raw[k][d] > 0 for d in cal_eq) for k in I.lk_raw))
items.add_bool('keys', 'MCX key: every MCX calendar day from 2024-04-01 (%d days) present and non-zero' % len(cal_mcx), all(d in I.mcx and I.mcx[d] > 0 for d in cal_mcx))
items.add_bool('keys', 'workbook-keyed cash (state a): every day present and non-zero', all(v > 0 for v in I.wb_K.values()))
items.add_bool('keys', 'industry MTF book: every row present and non-zero (%d rows, %s .. %s)' % (len(I.ind), min(I.ind), max(I.ind)), all(v > 0 for v in I.ind.values()))
# ---- the silent zero itself, and the methodology's corrected figures on the workbook as saved (issue 1)
P = c.build_parity()
C = c.parity_cached_rows()
for seg, per_exp in (('cash', (125, 13)), ('comm', (130, 7)), ('fo', (138, 0)), ('mtf', (124, 0))):
    v, n, e = c.seg_adr(C, seg, 'fy', 'FY 2027', silent_zero=False, with_n=True)
    v0, n0, e0 = c.seg_adr(C, seg, 'fy', 'FY 2027', silent_zero=True, with_n=True)
    errs = sum(1 for d in c.period_dates('fy', 'FY 2027') if C[seg].get(d) == c.ERR)
    items.add_bool('silent zero', 'workbook FY 2027 %s: %d numeric rows, %d error rows (Methodology 1: %d / %d); IFERROR gives %.4f, error rows skipped %.4f'
                   % (seg, n, errs, per_exp[0], per_exp[1], v0, v), n == per_exp[0] and errs == per_exp[1] and (v0 == 0.0) == (errs > 0))
pa = c.panel_adr(C, 'fy', 'FY 2027', silent_zero=False)
for lab, mine, doc in (('cash', pa['Cash'], '1.840'), ('commodities', pa['Commodities'], '0.648'), ('Broking', pa['Broking'], '4.294'), ('Consolidated', pa['Consolidated'], '8.281')):
    items.add('silent zero', 'Methodology issue 1, FY 2027 %s with the error days skipped (workbook as saved)' % lab, mine, doc)
pb = c.panel_adr(C, 'fy', 'FY 2027', silent_zero=True)
items.add('silent zero', 'Methodology issue 1, FY 2027 Broking as the workbook shows it (silent zeros)', pb['Broking'], '1.805')
# ---- days used per period after m-c (the average runs over the days that have a value)
for seg, per, exp in (('cash', 'FY 2027', 125), ('comm', 'FY 2027', 130), ('mtf', 'FY 2027', 124), ('fo', 'FY 2027', 138), ('cash', 'FY 2027 October', 0), ('comm', 'FY 2027 October', 0), ('fo', 'FY 2027 October', 13)):
    v, n, e = c.seg_adr(Cm.rows, seg, c.kind_of(per), per, silent_zero=False, with_n=True)
    items.add_bool('days used', '%s %s after m-c: %d days with a value (expected %d)' % (seg, per, n, exp), n == exp)
items.add_bool('days used', 'FY 2027 October: cash and commodities have no value at all (flagged insufficient in the live rows, 0 added in the unguarded table)',
               c.seg_adr(Cm.rows, 'cash', 'm', 'FY 2027 October', silent_zero=False, with_n=True)[1] == 0 and c.seg_adr(Cm.rows, 'comm', 'm', 'FY 2027 October', silent_zero=False, with_n=True)[1] == 0)
# ---- unchanged states
for per in ('Q2 FY 2027', 'Q1 FY 2027', 'FY 2026'):
    pb_, pc_ = c.panel_adr(B.rows, c.kind_of(per), per, **kw_b), c.panel_adr(Cm.rows, c.kind_of(per), per, **kw_c)
    items.add_bool('unchanged', '%s: no error row in the period, so m-c leaves every panel unchanged' % per, all(abs(pb_[k] - pc_[k]) < 1e-12 for k in pb_))

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mosl_switch_c.md')
    intro = ['Script: `out/checks/mosl_switch_c_check.py` (+ `mosl_common.py`), Python standard library only; inputs read with `git show 990eb5d:<path>`. Nothing under `src/engine/` or `src/live/` was read. Bridge: `out/bridges/mosl_c.md`.',
             '',
             'Before = my state a+b, after = a+b+c: an FY / quarter / month average runs over the days that have a value; error rows (`#N/A`, `#VALUE!`), blank rows and key-less rows are left out instead of turning the whole average into the workbook\'s IFERROR 0. The "ADR" table is the unguarded statistic (a segment with no value in a period adds 0 to the sum; the live rows flag that period as insufficient), as the bridge says. **Not rechecked:** the bridge\'s count of 28 / 18 periods flagged insufficient and the weekly / weekday tables: the flagging rules are engine logic the spec does not define; only the ADR, parameter, row and day-count numbers are.']
    cols = ['Item', 'Mine', 'Bridge', 'Verdict', 'Criterion', 'Max rel diff']
    sections = [('Headline (Consolidated)', ['Consolidated headline'], cols),
                ('ADR by period and panel', ['ADR'], cols),
                ('Parameters that moved', ['param', 'param set'], cols),
                ('Days with no row; keys without gaps or zeros', ['no-row days', 'keys'], cols),
                ('The silent zero in the workbook (Methodology issue 1) and the days used', ['silent zero', 'days used', 'unchanged'], cols),
                ('Daily revenue rows that changed', ['daily rows'], cols)]
    n, a = c.write_md(out, 'MOSL switch m-c: independent recompute', intro, items, sections, explain={})
    print('m-c: %d/%d items agree' % (a, n))
    for r in items.rows:
        if not r[4]:
            print('DIFFER', r[0], r[1], r[2], r[3], r[5])
