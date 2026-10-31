"""ADR bridge for one Groww switch (docs/GROWW_LIVE_SPEC.md; same format as src/engine/bridge.py for Angel One).

    python3 -m src.engine.bridge --broker GROWW a        # writes out/bridges/groww_a.md

Periods: FY 2027 (to date), Q2 FY 2027, FY 2027 October (to date), and the comparison bases FY 2026 and FY 2026 October.
Rs crore per trading day; MTF is gross. "Before" = the switches earlier in the order a -> g; "after" adds this one.
"""
import os
import sys

from . import groww, groww_switches as GS
from . import summary_periods as SP
from .bridge import daily_changes
from .parity_groww import ANGEL_SNAPSHOT, GROWW_SNAPSHOT

PERIODS = (('FY', 'FY 2027'), ('Q', 'Q2 FY 2027'), ('M', 'FY 2027 October'),
           ('FY', 'FY 2026'), ('M', 'FY 2026 October'))
HEADLINE = ('FY 2027', 'Q2 FY 2027', 'FY 2027 October', 'FY 2026')
SEGMENTS = (('fo', 'F&O', 'rev_mn'), ('cash', 'Cash', 'rev_mn'), ('comm', 'Commodities', 'rev_mn'),
            ('mtf', 'MTF', 'gross_cr'))


def run_switches(switches, angel_snapshot=ANGEL_SNAPSHOT, groww_snapshot=GROWW_SNAPSHOT):
    I, G = groww.load(angel_snapshot, groww_snapshot, switches)
    return I, G, groww.run(I, G)


def segments(I, G, res, guarded=False):
    return SP.make_segments(res['daily'], guarded=guarded, calendar=I.cal if guarded else None, mtf_weekday_net=False)


def adr(I, G, res):
    segs = segments(I, G, res)
    get = {'FY': lambda s, k: s.fy(k), 'Q': lambda s, k: s.q(k), 'M': lambda s, k: s.m(k)}
    return {(p, k, panel): SP._combine(segs, panel, lambda s: get[p](s, k))
            for p, k in PERIODS for panel in SP.PANELS}


# ── parameters ──
def params(G, res):
    """{(segment, quantity, quarter): value}: segment revenue, take rates, shares, MTF revenue and shares."""
    c, out = res['calib'], {}
    actual = {'fo': [q for q, p in c['fo_quarter'].items() if p['regime'] == 'actual'],
              'cash': [q for q, p in c['cash_quarter'].items() if p['regime'] == 'actual'],
              'comm': [q for q, p in c['comm_quarter'].items() if p['regime'] == 'actual'] if 'comm_quarter' in c
              else [c['comm']['quarter']]}
    for seg, name in (('fo', 'F&O'), ('cash', 'Cash'), ('comm', 'Commodities')):
        for q in actual[seg]:                                   # the revenue each calibration is built on
            out[(name, 'revenue Rs Mn', q)] = c['revenue'][seg][q]
    for name, table in (('F&O', c['fo_quarter']), ('Cash', c['cash_quarter'])):
        for q, p in table.items():
            out[(name, 'take rate Rs/order', q)] = p['take_rate']
            out[(name, 'share (ADTO, legacy basis)', q)] = p['share']
    if 'comm_quarter' in c:
        for q, p in c['comm_quarter'].items():
            out[('Commodities', 'take rate Rs/order', q)] = p['take_rate']
            out[('Commodities', 'share of Angel market orders', q)] = p['share']
    else:
        for q in c['fo_quarter']:
            if (int(q[-4:]), int(q[1])) >= (2026, 3):
                out[('Commodities', 'take rate Rs/order', q)] = c['comm']['take_rate']
                out[('Commodities', 'share of Angel market orders', q)] = c['comm']['share']
    for q, p in c['mtf_quarter'].items():
        out[('MTF', 'share of industry book', q)] = p['share']
        if 'revenue_cr' in p:
            out[('MTF', 'revenue Rs Cr', q)] = p['revenue_cr']
        if 'groww_book_cr' in p:
            out[('MTF', 'Groww average book Rs Cr', q)] = p['groww_book_cr']
    out[('MTF', 'yield', 'all')] = G.assume('mtf_yield')
    return out


def _qsort(key):
    seg, what, q = key
    return (seg, what, (int(q[-4:]), int(q[1])) if q != 'all' else (0, 0))


def moved(a, b, rel=1e-12):
    keys = sorted(set(a) | set(b), key=_qsort)
    return [(k, a.get(k), b.get(k)) for k in keys
            if a.get(k) is None or b.get(k) is None or abs(a[k] - b[k]) > rel * max(1.0, abs(a[k]))]


# ── the bridge ──
def bridge(letter, angel_snapshot=ANGEL_SNAPSHOT, groww_snapshot=GROWW_SNAPSHOT):
    before, after = GS.cumulative(letter)
    I_a, G_a, r_a = run_switches(before, angel_snapshot, groww_snapshot)
    I_b, G_b, r_b = run_switches(after, angel_snapshot, groww_snapshot)
    t_a, t_b = adr(I_a, G_a, r_a), adr(I_b, G_b, r_b)
    rows = []
    for p, k in PERIODS:
        for panel in SP.PANELS:
            x, y = t_a[(p, k, panel)], t_b[(p, k, panel)]
            rows.append(dict(period=k, panel=panel, before=x, after=y, delta=y - x, pct=(y / x - 1) if x else None))
    market = {}
    if letter == 'c':
        key = ('bse_fo', 'contracts')
        ov = I_b.market_overrides.get(key, {})
        market = {d: (I_a.mkt[key][d], v) for d, v in ov.items()}
    return dict(letter=letter, before=sorted(before), after=sorted(after), rows=rows,
                facts={k: o for k, o in G_b.overlay.items() if o.switch == letter and o.changed},
                same={k: o for k, o in G_b.overlay.items() if o.switch == letter and not o.changed},
                params=moved(params(G_a, r_a), params(G_b, r_b)), days=daily_changes(r_a, r_b), market=market)


def _f6(x, sign=''):
    return '—' if x is None else f'{x:{sign}.6f}'


def _num(x):
    if x is None:
        return '—'
    return f'{x:,.4f}' if abs(x) < 100 else f'{x:,.2f}'


def markdown(b):
    L = [f"# Bridge — Groww switch (g-{b['letter']})", '',
         f"{GS.DESCRIPTIONS[b['letter']]}.", '',
         f"Before: switches {''.join(b['before']) or 'none (parity)'} · after: {''.join(b['after'])}", '']
    head = {(r['period'], r['panel']): r for r in b['rows']}
    L += ['Consolidated ADR, Rs crore per trading day (MTF gross):', '',
          '| Period | Before | After | Δ % |', '|---|---:|---:|---:|']
    for k in HEADLINE:
        r = head[(k, 'Consolidated')]
        pct = '' if r['pct'] is None else '{:+.4f}%'.format(100 * r['pct'])
        L.append(f"| {k} | {_f6(r['before'])} | {_f6(r['after'])} | {pct} |")
    L.append('')
    if b['facts'] or b['same']:
        mix_vint = sorted({o.vintage for k, o in {**b['facts'], **b['same']}.items() if k[0].startswith('revmix')
                           or k[0] == 'mtf_revenue'})
        if mix_vint:
            L += ['Classification vintage of the revenue mix: restated (Q2 FY27 letter, p6) wherever it exists, '
                  'the original classification only where no restatement exists. Vintage per input is in the table.', '']
        L += ['Inputs replaced (reviewed facts; same unit as the workbook input):', '',
              '| Input | Period | Workbook | Live | Facts | Vintage |', '|---|---|---:|---:|---|---|']
        for (metric, period), o in sorted({**b['facts'], **b['same']}.items(),
                                          key=lambda kv: (kv[0][0], int(kv[0][1][-4:]), int(kv[0][1][1]))):
            ids = ', '.join(str(i) for i in o.fact_ids)
            tag = '' if o.changed else ' (same value, source confirmed)'
            L.append(f"| {metric} | {period} | {_num(o.seed)} | {_num(o.value)} | {ids} | {o.vintage}{tag}"
                     f"{' — ' + o.note if o.note else ''} |")
        L.append('')
    for d, (v0, v1) in sorted(b.get('market', {}).items()):
        if d == min(b['market']):
            L += [f"Exchange series replaced on imputed days: `bse_fo/contracts` ({len(b['market'])} days, lake value)", '',
                  '| Date | Before | After (lake) |', '|---|---:|---:|']
        L.append(f"| {d} | {v0[0]:,.0f} ({v0[1]}) | {v1[0]:,.0f} |")
    if b.get('market'):
        L.append('')
    L += ['ADR, Rs crore per trading day (MTF gross):', '',
          '| Period | Panel | Before | After | Δ | Δ % |', '|---|---|---:|---:|---:|---:|']
    for r in b['rows']:
        pct = '' if r['pct'] is None else f"{100 * r['pct']:+.4f}%"
        L.append(f"| {r['period']} | {r['panel']} | {_f6(r['before'])} | {_f6(r['after'])} | {_f6(r['delta'], '+')} | {pct} |")
    if b['params']:
        L += ['', 'Parameters that moved:', '', '| Segment | Quantity | Quarter | Before | After | Δ % |',
              '|---|---|---|---:|---:|---:|']
        for (seg, what, q), x, y in b['params']:
            pct = '' if not x or y is None else f'{100 * (y / x - 1):+.3f}%'
            L.append(f"| {seg} | {what} | {q} | {_num(x)} | {_num(y)} | {pct} |")
    L += ['', 'Daily revenue rows that changed:', '',
          '| Segment | Days | Changed | First | Last | Ratio min | Ratio max |', '|---|---:|---:|---|---|---:|---:|']
    for name, d in b['days'].items():
        f = (lambda x: '' if x is None else f'{x:.9f}')
        L.append(f"| {name} | {d['days']} | {d['changed']} | {d['first'] or ''} | {d['last'] or ''} | "
                 f"{f(d['rmin'])} | {f(d['rmax'])} |")
    return '\n'.join(L) + '\n'


def main(argv):
    arg = argv[1]
    os.makedirs('out/bridges', exist_ok=True)
    text = markdown(bridge(arg))
    path = f'out/bridges/groww_{arg}.md'
    with open(path, 'w') as fh:
        fh.write(text)
    print(text)
    print(f'written {path}')


if __name__ == '__main__':
    main(sys.argv)
