#!/usr/bin/env python3
"""MOSL switch m-e (one estimate rule for the open quarter): independent recompute of out/bridges/mosl_e.md at 990eb5d.
Python standard library only.  Run: python3 mosl_switch_e_check.py   (writes mosl_switch_e.md next to it)."""
import os
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mosl_common as c

I = c.load_inputs()
text = c.git_show('out/bridges/mosl_e.md')
items = c.Items()

D = c.build_live('abcd')
E = c.build_live('abcde')
kw_d, kw_e = c.stat_kw('abcd'), c.stat_kw('abcde')

c.check_adr(items, text, D.rows, kw_d, E.rows, kw_e)
c.check_params(items, text, D.par, E.par)
c.check_row_stats(items, text, D.rows, True, E.rows, True)

Q2, Q3 = 'Q2 FY 2027', 'Q3 FY 2027'
lk = I.lk_K
days = {s: [d for d in sorted(E.rows[s]) if c.q_of(d) == Q3 and isinstance(E.rows[s][d], float)] for s in c.SEGS}
keys = {'fo': I.lk_S, 'cash': I.lk_K, 'comm': I.mcx}
# ---- the rule: Q3 daily net = (last reported quarter's net / its key total) x the day's key
for seg in ('fo', 'cash', 'comm'):
    qd = [d for d in sorted(keys[seg]) if d in I.cal and c.q_of(d) == Q2 and d >= c.START and (seg != 'comm' or d in I.mcx)]
    per_unit = c.net(seg, Q2) / sum(keys[seg][d] for d in qd)
    unit = {'fo': 'Rs Cr per index-option + BSE contract', 'cash': 'Rs Cr per Rs Cr of NSE + BSE turnover', 'comm': 'Rs Cr per MCX contract'}[seg]
    ok = all(abs(E.rows[seg][d] - per_unit * keys[seg][d]) <= 1e-12 * abs(E.rows[seg][d]) for d in days[seg])
    items.add_bool('rule', '%s: each of the %d Q3 FY27 days = %.6e %s x that day\'s key (net %.4f Cr over %d Q2 days)' % (seg, len(days[seg]), per_unit, unit, c.net(seg, Q2), len(qd)), ok)
    items.add_bool('rule', '%s: Q3 FY27 net / gross carried from Q2 FY27 = %.4f' % (seg, c.ratio(seg, Q2)),
                   abs(E.par[({'fo': 'F&O', 'cash': 'Cash', 'comm': 'Commodities'}[seg], 'net / gross', Q3)] - c.ratio(seg, Q2)) < 1e-12)
items.add_bool('rule', 'days in the open quarter: F&O %d, cash %d, commodities %d, MTF %d (bridge: 13 / 13 / 14 / 12; MTF stops with the industry book on %s)' % (
    len(days['fo']), len(days['cash']), len(days['comm']), len(days['mtf']), max(days['mtf'])),
    (len(days['fo']), len(days['cash']), len(days['comm']), len(days['mtf'])) == (13, 13, 14, 12) and max(days['mtf']) == '2026-10-19'
    and max(days['fo']) == '2026-10-21' and max(days['comm']) == '2026-10-21')
# ---- MTF: share carried from the last reported quarter end, yield carried
cl, cl_d = c.ind_close(Q2)
sh = c.mtf_book(Q2) / cl
items.add_bool('rule', 'MTF share carried from the last reported quarter-end: %.0f Cr / industry %.2f Cr on %s = %.5f (6.35%%)' % (c.mtf_book(Q2), cl, cl_d, sh),
               abs(E.share_mtf[Q3] - sh) < 1e-15 and abs(sh - 0.0635) < 5e-5 and cl_d == '2026-09-30')
items.add_bool('rule', 'MTF yield carried: Q3 FY27 %.6f = Q1 FY27 typed %.6f' % (E.nii[Q3], I.wb_fact[('mtf_nii_yield', 'Q1 FY 2027')]), E.nii[Q3] == I.wb_fact[('mtf_nii_yield', 'Q1 FY 2027')])
d0 = '2026-10-19'
items.add_bool('rule', 'MTF %s = %.6f Cr = share x book %.2f x yield / 247' % (d0, E.rows['mtf'][d0], I.ind[d0]), abs(E.rows['mtf'][d0] - sh * I.ind[d0] * E.nii[Q3] / 247) < 1e-12)
# ---- nothing typed, nothing latent: Q3 FY27 gross brokerage per day is of the size of Q2 (the workbook's cash estimate was x5)
for seg, nm in (('cash', 'Cash'), ('fo', 'F&O'), ('comm', 'Commodities')):
    q2d = len([d for d in keys[seg] if d in I.cal and c.q_of(d) == Q2 and (seg != 'comm' or d in I.mcx)])
    q3_per_day = E.par[(nm, 'model net brokerage Rs Cr', Q3)] / len(days[seg])
    q2_per_day = c.net(seg, Q2) / q2d
    items.add_bool('rule', '%s net per day: Q3 %.4f vs Q2 %.4f Cr (same order: the day count is no longer 5x)' % (nm, q3_per_day, q2_per_day), 0.5 < q3_per_day / q2_per_day < 1.5)
# ---- the quarter ties still hold in the final state of m-e
for seg in ('fo', 'cash', 'comm'):
    for q in c.REPORTED:
        dd = [d for d in c.days_of(q, sorted(E.rows[seg])) if isinstance(E.rows[seg][d], float)]
        items.add('tie to data book', '%s %s (state abcde)' % (seg, q), sum(E.rows[seg][d] for d in dd), '%.6f' % (I.facts[('net_brokerage_' + seg, q)] / 10.0))

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mosl_switch_e.md')
    intro = ['Script: `out/checks/mosl_switch_e_check.py` (+ `mosl_common.py`), Python standard library only; inputs read with `git show 990eb5d:<path>`. Nothing under `src/engine/` or `src/live/` was read. Bridge: `out/bridges/mosl_e.md`.',
             '',
             'Before = my state a+b+c+d, after = a+b+c+d+e. Open quarter Q3 FY27 (1-21 Oct 2026): F&O, cash, commodities earn the last reported quarter\'s (Q2 FY27) net revenue per unit of their key (per index-option + BSE contract, per Rs Cr of NSE + BSE turnover, per MCX contract) x that day\'s key; each carries Q2 FY27\'s net / gross. MTF carries the Q2 FY27 quarter-end share (9,600 / industry book on 30 Sep) and the 12.94% yield, and its rows run to the last day with an industry book (19 Oct). I implemented the F&O rule both ways (workbook carry of share, rate and ratio, and net per contract) and they agree to 1e-12, which is why the F&O column does not move.']
    cols = ['Item', 'Mine', 'Bridge', 'Verdict', 'Criterion', 'Max rel diff']
    sections = [('Headline (Consolidated)', ['Consolidated headline'], cols),
                ('ADR by period and panel', ['ADR'], cols),
                ('Parameters that moved', ['param', 'param set'], cols),
                ('The estimate rule', ['rule'], cols),
                ('Quarter ties (state abcde)', ['tie to data book'], cols),
                ('Daily revenue rows that changed', ['daily rows'], cols)]
    n, a = c.write_md(out, 'MOSL switch m-e: independent recompute', intro, items, sections, explain={})
    print('m-e: %d/%d items agree' % (a, n))
    for r in items.rows:
        if not r[4]:
            print('DIFFER', r[0], r[1], r[2], r[3], r[5])
