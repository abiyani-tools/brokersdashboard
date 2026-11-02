"""ADR bridge for one MOSL switch (docs/MOSL_LIVE_SPEC.md; same format as src/engine/groww_bridge.py).

    python3 -m src.engine.bridge --broker MOSL a        # writes out/bridges/mosl_a.md

Periods: FY 2027 (to date), Q2 FY 2027, Q1 FY 2027, FY 2027 October (to date) and the comparison base FY 2026.
Rs crore per trading day; F&O, Cash and Commodities are net brokerage, MTF is net interest income (NII), Broking =
F&O + Cash + Commodities, Consolidated = Broking + MTF. "Before" = the switches earlier in the order a -> f; "after"
adds this one. Every run reads the series up to BRIDGE_AS_OF (the workbook snapshot's last day, 21 Oct 2026), so
the bridges compare like with like whatever the lake holds after it.
"""
import sys
from collections import defaultdict

from . import mosl, mosl_switches as MS, summary
from . import summary_periods as SP
from .inputs import q_of
from .parity_mosl import MOSL_SNAPSHOT, SHARED_SNAPSHOT

BRIDGE_AS_OF = '2026-10-21'
PERIODS = (('FY', 'FY 2027'), ('Q', 'Q2 FY 2027'), ('Q', 'Q1 FY 2027'), ('M', 'FY 2027 October'), ('FY', 'FY 2026'))
HEADLINE = ('FY 2027', 'Q2 FY 2027', 'Q1 FY 2027', 'FY 2027 October', 'FY 2026')
# periods added to one switch's bridge: m-b moves days inside a quarter, not the quarter's total, so months show it
EXTRA_PERIODS = {'b': (('M', 'FY 2027 September'), ('M', 'FY 2027 August'), ('M', 'FY 2026 September'))}
SEGMENTS = (('fo', 'F&O', 'rev_mn'), ('cash', 'Cash', 'rev_cr'), ('comm', 'Commodities', 'rev_mn'), ('mtf', 'MTF', 'nii_cr'))


def run_switches(switches, shared_snapshot=SHARED_SNAPSHOT, mosl_snapshot=MOSL_SNAPSHOT, as_of=BRIDGE_AS_OF,
                 lake_path=None):
    M = mosl.load(shared_snapshot, mosl_snapshot, tuple(switches), lake_path=lake_path, as_of=as_of)
    return M, mosl.run(M)


# ── summary view ──
def special_dates(M):
    """Special-session dates left out of the F&O, cash and commodity statistics under m-d (MTF keeps them)."""
    return {d for d, r in M.cal.items() if r.get('special_session')} if M.on('d') else set()


def segments(M, res, guarded=False):
    return SP.make_segments(res['daily'], guarded=guarded, calendar=M.cal if guarded else None,
                            exclude=special_dates(M), exclude_segments=MS.D_SEGMENTS, mtf_weekday_net=False,
                            fields=summary.MOSL_FIELDS)


def live_period_rows(M, res):
    """E3 rows for every FY / quarter / month from the calendar, generalised by broker (MOSL: NII, no net MTF panel)."""
    return SP.period_rows(segments(M, res, guarded=True))


def adr(M, res, periods=PERIODS):
    segs = segments(M, res)
    get = {'FY': lambda s, k: s.fy(k), 'Q': lambda s, k: s.q(k), 'M': lambda s, k: s.m(k)}
    return {(p, k, panel): SP._combine(segs, panel, lambda s: get[p](s, k))
            for p, k in periods for panel in SP.PANELS}


def asof_table(M, res):
    """{(panel, table, row label): value}: the week / weekday tables anchored on the last date of the series."""
    segs = segments(M, res)
    last = max(d for s in segs.values() for d in s.s)
    return {(panel, r['table_name'], r['row_label']): r['value']
            for panel in SP.PANELS for r in SP.asof_rows(segs, panel, last) if r['value'] is not None}


def insufficient(M, res):
    """Live (guarded) summary rows that are flagged 'insufficient data': [(panel, period, why)]."""
    out, seen = [], set()
    for r in live_period_rows(M, res):
        if r['note'] and r['value'] is None and r['period_type'] != 'asof' and r['row_label'] == r['period_key'] \
                and (r['panel'], r['period_key']) not in seen:
            seen.add((r['panel'], r['period_key']))
            out.append((r['panel'], r['period_key'], r['note']))
    return out


# ── parameters ──
def params(M, res):
    """{(segment, quantity, quarter): value}: model quarter totals, rates, shares, net / gross, MTF share and yield."""
    c, d, out = res['calib'], res['daily'], {}
    gross, net = defaultdict(float), defaultdict(float)
    for seg, name, field, gfield, scale in (('fo', 'F&O', 'rev_mn', 'gross_mn', 10.0), ('cash', 'Cash', 'rev_cr', 'gross_cr', 1.0),
                                            ('comm', 'Commodities', 'rev_mn', 'gross_mn', 10.0)):
        for day, r in d[seg].items():
            if r[gfield] is not None:
                gross[(name, q_of(day))] += r[gfield] / scale
            if r[field] is not None:
                net[(name, q_of(day))] += r[field] / scale
    for (name, q), v in gross.items():
        out[(name, 'model gross brokerage Rs Cr', q)] = v
        out[(name, 'model net brokerage Rs Cr', q)] = net[(name, q)]
    for q, v in c['fo']['rate'].items():
        out[('F&O', 'gross Rs per contract', q)] = v / 10
    for q, v in c['fo']['share'].items():
        out[('F&O', 'premium share (cancels)', q)] = v
    for q, t in c['cash']['table'].items():
        for k, name in (('share', 'share (cancels)'), ('H', "'delivery ratio' H"), ('J', 'gross per Rs of reported ADTO J')):
            if t.get(k) is not None:
                out[('Cash', name, q)] = t[k]
    for q, v in c['comm']['take'].items():
        out[('Commodities', 'gross Rs per MOSL contract', q)] = v
    for q, v in c['comm']['share'].items():
        out[('Commodities', 'share', q)] = v
    for q, v in c['mtf']['share'].items():
        out[('MTF', 'share of industry book', q)] = v
    for q, v in c['mtf']['nii'].items():
        out[('MTF', 'NII yield', q)] = v
    for q, r in c['ratio'].items():
        for s, name in (('fo', 'F&O'), ('cash', 'Cash'), ('comm', 'Commodities')):
            if r[s] is not None:
                out[(name, 'net / gross', q)] = r[s]
    return out


def _qsort(key):
    seg, what, q = key
    return (seg, what, (int(q[-4:]), int(q[1])))


def moved(a, b, rel=1e-9):
    keys = sorted(set(a) | set(b), key=_qsort)
    return [(k, a.get(k), b.get(k)) for k in keys
            if a.get(k) is None or b.get(k) is None or abs(a[k] - b[k]) > rel * max(1.0, abs(a[k]))]


def daily_changes(res_a, res_b):
    """Per segment: rows in both runs whose value changed, the range of after / before ratios, rows only the
    'after' run has (added) and rows only the 'before' run has (dropped, with how many were error rows)."""
    out = {}
    for seg, name, key in SEGMENTS:
        a, b = res_a['daily'][seg], res_b['daily'][seg]
        both = sorted(set(a) & set(b))
        ratios = [b[d][key] / a[d][key] for d in both
                  if a[d][key] and b[d][key] is not None and b[d][key] != a[d][key]]
        changed = [d for d in both if b[d][key] != a[d][key]]
        dropped = sorted(set(a) - set(b))
        out[name] = dict(days_before=len(a), days_after=len(b), changed=len(changed),
                         first=changed[0] if changed else None, last=changed[-1] if changed else None,
                         rmin=min(ratios) if ratios else None, rmax=max(ratios) if ratios else None,
                         added=sorted(set(b) - set(a)), dropped=dropped,
                         dropped_err=sum(1 for d in dropped if a[d].get('err')))
    return out


# ── the bridge ──
def bridge(letter, shared_snapshot=SHARED_SNAPSHOT, mosl_snapshot=MOSL_SNAPSHOT):
    before, after = MS.cumulative(letter)
    M_a, r_a = run_switches(before, shared_snapshot, mosl_snapshot)
    M_b, r_b = run_switches(after, shared_snapshot, mosl_snapshot)
    periods = PERIODS + EXTRA_PERIODS.get(letter, ())
    t_a, t_b = adr(M_a, r_a, periods), adr(M_b, r_b, periods)
    rows = []
    for p, k in periods:
        for panel in SP.PANELS:
            x, y = t_a[(p, k, panel)], t_b[(p, k, panel)]
            rows.append(dict(period=k, panel=panel, before=x, after=y, delta=y - x, pct=(y / x - 1) if x else None))
    yoy = []
    if letter == 'd':                         # the Q2 FY27 "YoY": the workbook's typed Q4 FY26 row vs the same quarter last year
        sa, sb = segments(M_a, r_a), segments(M_b, r_b)
        for panel in SP.PANELS:
            q = SP._combine(sb, panel, lambda s: s.q('Q2 FY 2027'))
            wb = SP._combine(sb, panel, lambda s: s.q('Q4 FY 2026'))
            ly = SP._combine(sb, panel, lambda s: s.q('Q2 FY 2026'))
            q0 = SP._combine(sa, panel, lambda s: s.q('Q2 FY 2027'))
            wb0 = SP._combine(sa, panel, lambda s: s.q('Q4 FY 2026'))
            yoy.append(dict(panel=panel, workbook=(q0 / wb0 - 1) if wb0 else None, live=(q / ly - 1) if ly else None,
                            q_after=q, q4_after=wb, q2ly_after=ly))
    return dict(letter=letter, before=sorted(before), after=sorted(after), rows=rows, yoy=yoy,
                facts={k: o for k, o in M_b.overlay.items() if o.switch == letter and o.changed},
                same={k: o for k, o in M_b.overlay.items() if o.switch == letter and not o.changed},
                asof=_asof_diff(asof_table(M_a, r_a), asof_table(M_b, r_b)),
                params=moved(params(M_a, r_a), params(M_b, r_b)), days=daily_changes(r_a, r_b),
                excluded=sorted(special_dates(M_b) - special_dates(M_a)),
                insufficient_before=insufficient(M_a, r_a) if 'c' in before else None,
                insufficient_after=insufficient(M_b, r_b) if 'c' in after else None,
                dropped={name: d['dropped'] for name, d in daily_changes(r_a, r_b).items() if d['dropped']},
                as_of=BRIDGE_AS_OF)


def _asof_diff(a, b):
    return [(k, a.get(k), b.get(k)) for k in dict.fromkeys(list(a) + list(b))
            if a.get(k) is None or b.get(k) is None or abs(a[k] - b[k]) > 1e-12 * max(1.0, abs(a[k]))]


def _f6(x, sign=''):
    return '—' if x is None else f'{x:{sign}.6f}'


def _num(x):
    if x is None:
        return '—'
    return f'{x:,.4f}' if abs(x) < 100 else f'{x:,.2f}'


def markdown(b):
    L = [f"# Bridge — MOSL switch (m-{b['letter']})", '',
         f"{MS.DESCRIPTIONS[b['letter']]}.", '',
         f"Before: switches {''.join(b['before']) or 'none (parity)'} · after: {''.join(b['after'])} · series read to {b['as_of']}", '']
    head = {(r['period'], r['panel']): r for r in b['rows']}
    L += ['Consolidated ADR, Rs crore per trading day (net brokerage + MTF NII):', '',
          '| Period | Before | After | Δ % |', '|---|---:|---:|---:|']
    for k in HEADLINE:
        r = head[(k, 'Consolidated')]
        pct = '' if r['pct'] is None else '{:+.4f}%'.format(100 * r['pct'])
        L.append(f"| {k} | {_f6(r['before'])} | {_f6(r['after'])} | {pct} |")
    L.append('')
    if b['facts'] or b['same']:
        L += [f"Inputs replaced by reviewed data-book facts: {len(b['facts'])} change the workbook's value, {len(b['same'])} "
              "already equal it (source confirmed, not listed). Each fact is converted from its unit (Rs Mn, Rs Mn per day) "
              "to the input's (Rs Cr, Rs Cr per day); net / gross = net brokerage / gross brokerage of the same quarter.", '',
              '| Input | Period | Workbook | Live | Facts | Basis |', '|---|---|---:|---:|---|---|']
        for (metric, period), o in sorted(b['facts'].items(),
                                          key=lambda kv: (kv[0][0], int(kv[0][1][-4:]), int(kv[0][1][1]))):
            ids = ', '.join(str(i) for i in o.fact_ids)
            L.append(f"| {metric} | {period} | {_num(o.seed)} | {_num(o.value)} | {ids} | {o.note} |")
        L.append('')
    if b['letter'] == 'a':
        L += ['Pins moved by m-a: fo_last_actual_quarter, cash_last_actual_quarter, comm_last_actual_quarter, '
              'mtf_last_actual_quarter = Q2 FY 2027; fo_zero_quarters = none (Q1, Q2 FY25 were numeric 0); '
              'cash_table_first_quarter = Q1 FY 2025. The cash take rate of Q1 FY27 is now its own (J = gross / reported ADTO, '
              'the workbook\'s J52 = J51 is dropped) and the typed Q1 FY27 gross 228.30 is fed. '
              'Q3 FY27 keeps the workbook\'s estimate rules until m-e (cash #N/A, commodities #N/A / blank, F&O carried).', '']
    if b['letter'] == 'b':
        L += ["Cash key: the lake's `nse_cash/turnover_cr` + `bse_cash/turnover_cr` on their own dates (ExchangesDash, "
              "snapshot/mosl_lake_2026-11-02.json) instead of the workbook's columns, which sit two rows off from 9 Jun 2025 "
              '(Methodology issue 5). The F&O key is read from the lake too (`nse_fo/io_contracts` + `bse_fo/contracts`): '
              'it equals the workbook\'s on all 756 common days, differs only on 31 May 2024 (the workbook has a text cell, '
              'the lake a number), and the lake adds the 2023-09-29 row. No premium ADTO is read (it cancels).', '']
    if b['letter'] == 'c':
        for name, ds in b['dropped'].items():
            L += [f'{name}: {len(ds)} day(s) have no row after m-c (error rows the workbook shows as #N/A / #VALUE! or blank, '
                  f"or a missing / non-ok / zero key): {_span(ds)}", '']
        L += ['Before m-c an FY / quarter / month statistic that contained one error day was the workbook\'s IFERROR 0 '
              '(Methodology issue 1). After it the error days are left out and the average runs over the days that have a value; '
              'a period with no value at all is flagged insufficient in the live rows.', '']
    if b['letter'] == 'd':
        if b['excluded']:
            L += ['Special sessions left out of the F&O, cash and commodity averages (MTF keeps them): '
                  + ', '.join(b['excluded']), '']
        L += ['Labels and comparisons come from the calendar (E3, summary_periods, generalised by broker): YoY = the same period '
              'last year, quarter / month labels from the selection, the standard panel order Consolidated, Broking, MTF, F&O, '
              "Cash, Commodities (the workbook's band 3 swaps Cash and Commodities), MTF as NII with no net panel.", '',
              "Q2 FY27 \"YoY\", after m-a..m-d. The workbook's row is typed `Q4 FY 2026` (L13), two quarters back:", '',
              '| Panel | Workbook "YoY" (vs Q4 FY26) | Live YoY (vs Q2 FY26) | Q2 FY27 | Q4 FY26 | Q2 FY26 |',
              '|---|---:|---:|---:|---:|---:|']
        for r in b['yoy']:
            f = lambda x: '—' if x is None else f'{100 * x:+.1f}%'
            L.append(f"| {r['panel']} | {f(r['workbook'])} | {f(r['live'])} | {_f6(r['q_after'])} | {_f6(r['q4_after'])} | "
                     f"{_f6(r['q2ly_after'])} |")
        L.append('')
    if b['letter'] == 'e':
        L += ["Open quarter (Q3 FY27, 1-21 Oct): F&O and commodities earn the last reported quarter's net revenue per contract; "
              "cash earns its net revenue per Rs Cr of NSE + BSE turnover; each with the last reported net / gross. "
              'MTF carries the last reported quarter-end share and yield, and its rows now run to the last day of data '
              '(the workbook\'s formulas stop on 30 Sep). No typed values.', '']
    if b['letter'] == 'f':
        L += [f"The MTF NII yield is the workbook's typed value for each quarter Q1 FY25 - Q1 FY27 (kept; {MS.YIELD_LABEL}). "
              'Quarters after the last typed one carry it from the assumption row `mtf_nii_yield_carry` (12.94%, the workbook\'s '
              'F14). The numbers do not move because the carried value equals the workbook\'s own carry; what changes is that '
              'the yield is now a labelled assumption row in sb_assumptions, which the run refuses without. The day basis '
              '(247) is unchanged.', '']
    if b['insufficient_after'] is not None:
        L += [f"Periods flagged insufficient in the live rows after this switch: {len(b['insufficient_after'])}"
              + (f" (before: {len(b['insufficient_before'])})" if b['insufficient_before'] is not None else '') + '.', '']
        for panel, period, why in b['insufficient_after'][:8]:
            L.append(f'- {panel} {period}: {why}')
        if b['insufficient_after']:
            L.append('')
    L += ['ADR, Rs crore per trading day (net brokerage + MTF NII):', '',
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
    if b['asof']:
        L += ['', f"Week / weekday tables (as of the last date) that changed: {len(b['asof'])} rows over all panels; "
              'the Consolidated panel:', '', '| Panel | Table | Row | Before | After |', '|---|---|---|---:|---:|']
        for (panel, table, label), x, y in b['asof']:
            if panel == 'Consolidated':
                L.append(f"| {panel} | {table} | {label} | {_f6(x)} | {_f6(y)} |")
    L += ['', 'Daily revenue rows that changed:', '',
          '| Segment | Days before | Days after | Changed | First | Last | Ratio min | Ratio max | Added | Dropped |',
          '|---|---:|---:|---:|---|---|---:|---:|---:|---:|']
    for name, d in b['days'].items():
        f = (lambda x: '' if x is None else f'{x:.9f}')
        L.append(f"| {name} | {d['days_before']} | {d['days_after']} | {d['changed']} | {d['first'] or ''} | "
                 f"{d['last'] or ''} | {f(d['rmin'])} | {f(d['rmax'])} | {len(d['added'])} | {len(d['dropped'])} |")
    return '\n'.join(L) + '\n'


def _span(ds):
    return f'{ds[0]}' if len(ds) == 1 else f'{ds[0]} .. {ds[-1]}'


def main(argv):
    import os
    letter = argv[1]
    os.makedirs('out/bridges', exist_ok=True)
    text = markdown(bridge(letter))
    path = f'out/bridges/mosl_{letter}.md'
    with open(path, 'w') as fh:
        fh.write(text)
    print(text)
    print(f'written {path}')


if __name__ == '__main__':
    main(sys.argv)
