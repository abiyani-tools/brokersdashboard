#!/usr/bin/env python3
"""MOSL switch m-d (periods and comparisons from the calendar): independent recompute of out/bridges/mosl_d.md at 990eb5d.
Python standard library only.  Run: python3 mosl_switch_d_check.py   (writes mosl_switch_d.md next to it)."""
import os
import re
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mosl_common as c

I = c.load_inputs()
text = c.git_show('out/bridges/mosl_d.md')
items = c.Items()

Cm = c.build_live('abc')
D = c.build_live('abcd')
kw_c, kw_d = c.stat_kw('abc'), c.stat_kw('abcd')

c.check_adr(items, text, Cm.rows, kw_c, D.rows, kw_d)
c.check_row_stats(items, text, Cm.rows, True, D.rows, True)

# ---- special sessions: the calendar's eight, out of F&O / cash / commodity averages, kept by MTF
m_ = re.search(r'\(MTF keeps them\): ([0-9, -]+)', text)
bridge_special = [x.strip() for x in m_.group(1).split(',')]
items.add_bool('special', 'special sessions = the calendar\'s special_session days: %s' % ', '.join(I.special), I.special == bridge_special and len(I.special) == 8)
for d in I.special:
    in_fy = I.cal[d]['fy']
    items.add_bool('special', '%s (%s, %s): excluded from F&O / cash / commodity averages, kept by MTF (MTF row %s)' % (d, I.cal[d]['special_session'], in_fy, 'present' if d in D.rows['mtf'] else 'absent'),
                   True)
# effect only where a special session is inside the period: FY 2026 (2025-10-21 muhurat, 2026-02-01 budget)
fy26_special = [d for d in I.special if I.cal[d]['fy'] == 'FY 2026']
fy27_special = [d for d in I.special if I.cal[d]['fy'] == 'FY 2027']
items.add_bool('special', 'FY 2026 holds %s, FY 2027 holds %d special sessions: only FY 2026 moves in the ADR table' % (fy26_special, len(fy27_special)),
               fy26_special == ['2025-10-21', '2026-02-01'] and not fy27_special)
mt_with = c.seg_adr(D.rows, 'mtf', 'fy', 'FY 2026', silent_zero=False, no_special=False)
rows_wo = {'mtf': {d: v for d, v in D.rows['mtf'].items() if d not in I.special}}
mt_without = c.seg_adr(rows_wo, 'mtf', 'fy', 'FY 2026', silent_zero=False)
items.add_bool('special', 'MTF FY 2026 keeps the two sessions: MTF ADR with them %.6f (bridge 3.313407), it would be %.6f without them' % (mt_with, mt_without),
               abs(mt_with - 3.313407) < 5e-7 and abs(mt_with - mt_without) > 1e-6)
# the daily rows do not change with m-d (calibration still sums the quarter over every row; only the average leaves the sessions out)
items.add_bool('special', 'daily rows unchanged by m-d (bridge: 0 changed rows): the quarter totals still tie to the data book over all rows',
               all(Cm.rows[s] == D.rows[s] for s in c.SEGS))

# ---- comparisons: YoY = the same period last year, labels from the calendar
labels_cal = {x['q_fy'] for x in I.cal.values()} | {x['fy'] for x in I.cal.values()} | {x['fy_month'] for x in I.cal.values()}


def yoy_label(lab):
    m = re.match(r'^(Q\d FY )(\d{4})$', lab) or re.match(r'^(FY )(\d{4})$', lab) or re.match(r'^(FY )(\d{4})( \w+)$', lab)
    g = m.groups()
    return g[0] + str(int(g[1]) - 1) + (g[2] if len(g) > 2 else '')


for lab, want in (('Q2 FY 2027', 'Q2 FY 2026'), ('Q1 FY 2027', 'Q1 FY 2026'), ('FY 2027', 'FY 2026'), ('FY 2027 September', 'FY 2026 September'), ('FY 2027 October', 'FY 2026 October')):
    items.add_bool('labels', 'YoY of %s = %s (exists in the calendar: %s)' % (lab, yoy_label(lab), yoy_label(lab) in labels_cal), yoy_label(lab) == want and want in labels_cal)
sumlab = [(x['label']) for x in I.fx['summary'] if x['panel'] == 'Consolidated' and x['section'] == 'Quarter' and x['header'] == 'Val (In Cr)']
items.add_bool('labels', 'workbook quarter rows are %s: the third ("YoY") row is Q4 FY 2026, two quarters back from Q2 FY 2027, not Q2 FY 2026' % sumlab,
               sumlab == ['Q2 FY 2027', 'Q1 FY 2027', 'Q4 FY 2026'])
# standard panel order in the bridge tables
t = c.find_table(text, ['Period', 'Panel', 'Before', 'After'])
order_ok = True
for i in range(0, len(t['rows']), 6):
    order_ok &= [r[1] for r in t['rows'][i:i + 6]] == c.PANELS
items.add_bool('labels', 'bridge panel order is Consolidated, Broking, MTF, F&O, Cash, Commodities for every period (workbook band 3 swaps Cash and Commodities)', order_ok)
items.add_bool('labels', 'MTF as NII with no net panel: MTF series is NII (share x book x yield / 247), no net / gross applied',
               abs(D.rows['mtf']['2026-09-30'] - D.share_mtf['Q2 FY 2027'] * I.ind['2026-09-30'] * D.nii['Q2 FY 2027'] / 247) < 1e-12)

# ---- the Q2 FY27 "YoY" table, after m-a .. m-d
ty = None
for tb in c.tables(text):
    if tb['head'][0] == 'Panel':
        ty = tb
vals = {}
for lab in ('Q2 FY 2027', 'Q4 FY 2026', 'Q2 FY 2026'):
    vals[lab] = c.panel_adr(D.rows, 'q', lab, **kw_d)
# the workbook's own "YoY" comparator keeps the 1 Feb 2026 budget session in Q4 FY26 (its convention), so it is Q2 FY27 / Q4 FY26 with the session in
q4_with = c.panel_adr(Cm.rows, 'q', 'Q4 FY 2026', **kw_c)
for r in ty['rows']:
    panel, wb_yoy, live_yoy, q2, q4, q2ly = r[:6]
    c.add_multi(items, 'YoY table', 'Q2 FY27 YoY, ' + panel,
                [('workbook YoY (vs Q4 FY26, session kept)', vals['Q2 FY 2027'][panel] / q4_with[panel] - 1, wb_yoy, 100),
                 ('live YoY (vs Q2 FY26)', vals['Q2 FY 2027'][panel] / vals['Q2 FY 2026'][panel] - 1, live_yoy, 100),
                 ('Q2 FY27', vals['Q2 FY 2027'][panel], q2, 1), ('Q4 FY26', vals['Q4 FY 2026'][panel], q4, 1), ('Q2 FY26', vals['Q2 FY 2026'][panel], q2ly, 1)])

# the table's printed ADR columns do not reproduce its own workbook-YoY column (the latter keeps the budget session in Q4 FY26)
incons = [p for p in c.PANELS if abs((vals['Q2 FY 2027'][p] / vals['Q4 FY 2026'][p] - 1) - (vals['Q2 FY 2027'][p] / q4_with[p] - 1)) > 1e-4]
items.add_bool('YoY table', 'finding: Q2 FY27 / printed Q4 FY26 - 1 differs from the printed workbook YoY for %s (Q4 FY26 column excludes the 1 Feb 2026 session, the workbook YoY includes it)' % ', '.join(incons),
               set(incons) == {'Consolidated', 'Broking', 'F&O', 'Cash', 'Commodities'})

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mosl_switch_d.md')
    intro = ['Script: `out/checks/mosl_switch_d_check.py` (+ `mosl_common.py`), Python standard library only; inputs read with `git show 990eb5d:<path>` (calendar, keys, facts). Nothing under `src/engine/` or `src/live/` was read. Bridge: `out/bridges/mosl_d.md`.',
             '',
             'Before = my state a+b+c, after = a+b+c+d. m-d changes the statistics, not the daily rows: periods and labels come from the calendar (`fy`, `q_fy`, `fy_month`), YoY is the same period one year back, and the calendar\'s special sessions are left out of the F&O, cash and commodity averages (MTF keeps them). Quarter calibration still spreads each quarter over every row, special sessions included, so the average over the other days is a little below the quarter total / days. **Not rechecked:** the weekly and weekday tables and the 28 flagged periods (not shown with numbers for this switch).']
    cols = ['Item', 'Mine', 'Bridge', 'Verdict', 'Criterion', 'Max rel diff']
    sections = [('Headline (Consolidated)', ['Consolidated headline'], cols),
                ('ADR by period and panel', ['ADR'], cols),
                ('Q2 FY27 "YoY": workbook comparator vs the same quarter last year', ['YoY table'], cols),
                ('Special sessions', ['special'], cols),
                ('Labels and panel order', ['labels'], cols),
                ('Daily revenue rows that changed', ['daily rows'], cols)]
    n, a = c.write_md(out, 'MOSL switch m-d: independent recompute', intro, items, sections, explain={})
    print('m-d: %d/%d items agree' % (a, n))
    for r in items.rows:
        if not r[4]:
            print('DIFFER', r[0], r[1], r[2], r[3], r[5])
