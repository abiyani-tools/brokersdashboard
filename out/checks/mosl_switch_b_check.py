#!/usr/bin/env python3
"""MOSL switch m-b (cash key on the right dates): independent recompute of out/bridges/mosl_b.md at 990eb5d.
Python standard library only.  Run: python3 mosl_switch_b_check.py   (writes mosl_switch_b.md next to it)."""
import os
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mosl_common as c

I = c.load_inputs()
text = c.git_show('out/bridges/mosl_b.md')
items = c.Items()

A = c.build_live('a')
B = c.build_live('ab')
kw_a, kw_b = c.stat_kw('a'), c.stat_kw('ab')

c.check_adr(items, text, A.rows, kw_a, B.rows, kw_b)
c.check_params(items, text, A.par, B.par)
c.check_row_stats(items, text, A.rows, False, B.rows, False)

# ---- the key itself: lake NSE + BSE cash turnover on its own date vs the workbook's columns
lk, wb = I.lk_K, I.wb_K
ds = sorted(d for d in lk if d in I.cal)
idx = {d: i for i, d in enumerate(ds)}
diff = [d for d in ds if d in wb and abs(wb[d] - lk[d]) > 1e-6]
items.add_bool('cash key', 'workbook turnover equals the lake on every day before 2025-06-09 (%d days compared)' % len([d for d in ds if d in wb and d < '2025-06-09']),
               not [d for d in diff if d < '2025-06-09'])
items.add_bool('cash key', 'from 2025-06-09 the workbook value of a day is the lake value of two trading days earlier, on all %d differing days (first %s, last %s)' % (len(diff), diff[0], diff[-1]),
               all(abs(wb[d] - lk[ds[idx[d] - 2]]) <= 1e-6 for d in diff) and diff[0] == '2025-06-09')
items.add_bool('cash key', 'lake key = lake NSE cash turnover + lake BSE cash turnover on the same date, every calendar equity day (%d days)' % len(ds),
               all(abs(lk[d] - (I.lk_raw['nse_cash/turnover_cr'][d] + I.lk_raw['bse_cash/turnover_cr'][d])) < 1e-9 for d in ds))
items.add_bool('cash key', 'state ab cash rows use the lake key: every cash row of Q2 FY27 equals ratio x gross x lake K / sum of lake K',
               all(abs(B.rows['cash'][d] - c.net('cash', 'Q2 FY 2027') * lk[d] / sum(lk[x] for x in c.days_of('Q2 FY 2027', ds))) < 1e-9
                   for d in c.days_of('Q2 FY 2027', ds)))
items.add_bool('cash key', 'every equity calendar day has a lake cash row, status ok, non-zero (no gap, no zero in the key)',
               all(d in lk and lk[d] > 0 for d in [x for x, v in I.cal.items() if v['is_equity_day']]))
# ---- the F&O key from the lake
wbS, lkS = I.wb_S, I.lk_S
common = [d for d in wbS if d in lkS and wbS[d] is not None]
bad = [d for d in common if wbS[d] != lkS[d]]
items.add_bool('F&O key', 'lake index-option + BSE contracts equal the workbook on all %d common days with a number' % len(common), not bad, str(bad))
items.add_bool('F&O key', 'differs only on 2024-05-31 (workbook text cell, lake %s)' % (lkS['2024-05-31'],), wbS['2024-05-31'] is None and '2024-05-31' in lkS)
items.add_bool('F&O key', 'lake adds one day the workbook lacks: ' + ', '.join(d for d in lkS if d not in wbS and d in I.cal), [d for d in lkS if d not in wbS and d in I.cal] == ['2023-09-29'])
items.add_bool('F&O key', '2024-05-31 now carries revenue in F&O (error row in state a, number in state ab)',
               A.rows['fo']['2024-05-31'] == c.ERR and isinstance(B.rows['fo']['2024-05-31'], float))
# ---- every quarter still ties to the data book net brokerage after the re-keying
for seg in ('fo', 'cash'):
    for q in c.REPORTED:
        days = [d for d in c.days_of(q, sorted(B.rows[seg])) if isinstance(B.rows[seg][d], float)]
        items.add('tie to data book', '%s %s (state ab)' % (seg, q), sum(B.rows[seg][d] for d in days), '%.6f' % (I.facts[('net_brokerage_' + seg, q)] / 10.0))

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mosl_switch_b.md')
    intro = ['Script: `out/checks/mosl_switch_b_check.py` (+ `mosl_common.py`), Python standard library only; inputs read with `git show 990eb5d:<path>` (reviewed facts; workbook keys `snapshot/mosl_snapshot_2026-10-23.json`; lake keys `snapshot/mosl_lake_2026-11-02.json` = ExchangesDash main as read 2 Nov 2026; MCX, calendar, industry book `snapshot/db_snapshot_2026-10-23.json`). Nothing under `src/engine/` or `src/live/` was read. Bridge: `out/bridges/mosl_b.md`.',
             '',
             'Before = my state a (m-a recomputed), after = a + b: the cash key is the lake `nse_cash/turnover_cr` + `bse_cash/turnover_cr` on its own date and the F&O key the lake `nse_fo/io_contracts` + `bse_fo/contracts`; the quarter totals stay the data-book net brokerage, only the day shape moves. Months of the bridge (FY 2027 September, FY 2027 August, FY 2026 September) are checked as well.']
    cols = ['Item', 'Mine', 'Bridge', 'Verdict', 'Criterion', 'Max rel diff']
    sections = [('Headline (Consolidated)', ['Consolidated headline'], cols),
                ('ADR by period and panel (before, after, delta, delta %)', ['ADR'], cols),
                ('Parameters that moved', ['param', 'param set'], cols),
                ('The keys', ['cash key', 'F&O key'], cols),
                ('Quarter ties after re-keying', ['tie to data book'], cols),
                ('Daily revenue rows that changed', ['daily rows'], cols)]
    expl = {'F&O counts / dates': 'Not a value difference. Rows whose value moves by more than 1e-9 relative: 61 (Q1 FY25, 2024-04-01 .. 2024-06-28, the 31 May 2024 row appears and the quarter total is spread over one more day: ratio 0.984555296, equal to the bridge min). The bridge counts 385 as changed: the other 324 rows are unchanged in my model even under exact float inequality (same keys: the lake equals the workbook on all 756 common days), so they can only be ulp-level arithmetic noise in the bridge (its ratio max prints 1.000000000). No ADR, parameter or other count is affected.',
            'F&O ratio max': 'Same cause: the bridge max ratio 1.000000000 comes from those noise rows; my changed rows are all Q1 FY25 with ratio 0.984555296.'}
    n, a = c.write_md(out, 'MOSL switch m-b: independent recompute', intro, items, sections, explain=expl)
    print('m-b: %d/%d items agree' % (a, n))
    for r in items.rows:
        if not r[4]:
            print('DIFFER', r[0], r[1], r[2], r[3], r[5])
