"""ADR bridge for one switch (LIVE_SPEC §5): average daily revenue before → after, per segment.

Periods: FY 2027 (to date), Q2 FY 2027, FY 2027 October (to date), and the comparison bases FY 2026,
Q3 FY 2026 and FY 2026 October. Rs crore per trading day; MTF is gross.
"Before" = the switches earlier in the order a → i; "after" adds this one, so bridges add up.

    python3 -m src.engine.bridge a            # writes out/bridges/a.md
"""
import os
import sys

from . import daily, switches as SW
from .inputs import load_snapshot
from .summary_periods import _combine, asof_rows, make_segments, panels_of

SNAP = 'snapshot/db_snapshot_2026-10-23.json'
REVIEWED = 'snapshot/facts_reviewed_2026-10-23.json'
PERIODS = (('FY', 'FY 2027'), ('Q', 'Q2 FY 2027'), ('M', 'FY 2027 October'),
           # comparison bases (YoY / QoQ) that a switch can move without touching the current periods
           ('FY', 'FY 2026'), ('Q', 'Q3 FY 2026'), ('M', 'FY 2026 October'))
SEGMENTS = (('fo', 'F&O', 'rev_mn'), ('cash', 'Cash', 'rev_mn'), ('comm', 'Commodities', 'rev_mn'), ('mtf', 'MTF', 'gross_cr'))


def adr(I):
    res = daily.run(I)
    segs = make_segments(res['daily'], exclude=SW.excluded_dates(I), mtf_split='g' in I.switches)
    get = {'FY': lambda s, k: s.fy(k), 'Q': lambda s, k: s.q(k), 'M': lambda s, k: s.m(k)}
    table = {(p, k, panel): _combine(segs, panel, lambda s: get[p](s, k))
             for p, k in PERIODS for panel in panels_of(segs)}
    last = max(d for s in segs.values() for d in s.s)
    asof = {(r['panel'], r['table_name'], r['row_label']): r['value']
            for panel in panels_of(segs) for r in asof_rows(segs, panel, last)}
    return table, res, asof


def daily_changes(res_a, res_b):
    """Per segment: days whose revenue changed, and the range of after/before ratios."""
    out = {}
    for seg, name, key in SEGMENTS:
        a, b = res_a['daily'][seg], res_b['daily'][seg]
        if set(a) != set(b):
            raise AssertionError(f'{name}: the switch changed which days exist')
        ratios = [b[d][key] / a[d][key] for d in a if a[d][key] and b[d][key] != a[d][key]]
        changed = sorted(d for d in a if b[d][key] != a[d][key])
        out[name] = dict(days=len(a), changed=len(changed), first=changed[0] if changed else None,
                         last=changed[-1] if changed else None,
                         rmin=min(ratios) if ratios else None, rmax=max(ratios) if ratios else None)
    return out


def bridge(letter, snap=SNAP, reviewed=REVIEWED):
    before, after = SW.cumulative(letter)
    I_a = load_snapshot(snap, before, reviewed if before else None)
    I_b = load_snapshot(snap, after, reviewed)
    t_a, r_a, s_a = adr(I_a)
    t_b, r_b, s_b = adr(I_b)
    rows = []
    panels = list(dict.fromkeys([k[2] for k in t_a] + [k[2] for k in t_b]))
    for p, k in PERIODS:
        for panel in panels:
            x, y = t_a.get((p, k, panel)), t_b.get((p, k, panel))
            rows.append(dict(period=k, panel=panel, before=x, after=y,
                             delta=None if x is None or y is None else y - x,
                             pct=(y / x - 1) if x and y is not None else None))
    asof = [dict(key=key, before=s_a.get(key), after=s_b.get(key)) for key in dict.fromkeys(list(s_a) + list(s_b))
            if s_a.get(key) != s_b.get(key)]
    return dict(letter=letter, before=sorted(before), after=sorted(after), rows=rows,
                overrides={c: v for c, v in I_b.overrides.items() if v[2] == letter},
                market={k: I_b.market_overrides.get(k, {}) for k in SW.MARKET_SWITCHES.get(letter, ())},
                market_before={k: {d: I_a.mkt[k][d] for d in I_b.market_overrides.get(k, {})}
                               for k in SW.MARKET_SWITCHES.get(letter, ())},
                days=daily_changes(r_a, r_b), asof=asof,
                excluded=SW.excluded_dates(I_b) - SW.excluded_dates(I_a))


def markdown(b):
    L = [f"# Bridge — switch ({b['letter']})", '',
         f"Before: switches {''.join(b['before']) or 'none (parity)'} · after: {''.join(b['after'])}", '']
    if b['overrides']:
        L += ['Cells replaced:', '']
        for (sheet, col, row), (v, fid, _) in b['overrides'].items():
            L.append(f"- `{sheet}!{col}{row}` → {v:g} (fact {fid}, reviewed)")
        L.append('')
    for key, days in b.get('market', {}).items():
        L += [f"Exchange series replaced on imputed days: `{key[0]}/{key[1]}` ({len(days)} days, lake value)", '',
              '| Date | Before (status) | After (lake) |', '|---|---:|---:|']
        for d, (v, _) in sorted(days.items()):
            v0, st0 = b['market_before'][key][d]
            L.append(f"| {d} | {v0:,.0f} ({st0}) | {v:,.0f} |")
        L.append('')
    if b.get('excluded'):
        L += ['Days left out of every average: ' + ', '.join(sorted(b['excluded'])), '']
    L += ['ADR, Rs crore per trading day (MTF gross):', '',
          '| Period | Panel | Before | After | Δ | Δ % |', '|---|---|---:|---:|---:|---:|']
    for r in b['rows']:
        pct = '' if r['pct'] is None else f"{100 * r['pct']:+.4f}%"
        f6 = lambda x, sign='': '—' if x is None else f"{x:{sign}.6f}"
        L.append(f"| {r['period']} | {r['panel']} | {f6(r['before'])} | {f6(r['after'])} | {f6(r['delta'], '+')} | {pct} |")
    if b.get('asof'):
        L += ['', 'Week / weekday tables (as of the last date) that changed:', '',
              '| Panel | Table | Row | Before | After |', '|---|---|---|---:|---:|']
        for r in b['asof']:
            (panel, table, label), x, y = r['key'], r['before'], r['after']
            f6 = lambda v: '—' if v is None else f'{v:.6f}'
            L.append(f"| {panel} | {table} | {label} | {f6(x)} | {f6(y)} |")
    L += ['', 'Daily revenue rows that changed:', '', '| Segment | Days | Changed | First | Last | Ratio min | Ratio max |',
          '|---|---:|---:|---|---|---:|---:|']
    for name, d in b['days'].items():
        f = (lambda x: '' if x is None else f'{x:.9f}')
        L.append(f"| {name} | {d['days']} | {d['changed']} | {d['first'] or ''} | {d['last'] or ''} | {f(d['rmin'])} | {f(d['rmax'])} |")
    return '\n'.join(L) + '\n'


def main(argv):
    letter = argv[1]
    b = bridge(letter)
    os.makedirs('out/bridges', exist_ok=True)
    path = f'out/bridges/{letter}.md'
    with open(path, 'w') as fh:
        fh.write(markdown(b))
    print(markdown(b))
    print(f'written {path}')


if __name__ == '__main__':
    main(sys.argv)
