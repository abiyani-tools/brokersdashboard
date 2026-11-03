"""ADR bridge for one MOSL switch (docs/MOSL_LIVE_SPEC.md; same format as src/engine/groww_bridge.py).

    python3 -m src.engine.bridge --broker MOSL a        # writes out/bridges/mosl_a.md

Periods: FY 2027 (to date), Q2 FY 2027, Q1 FY 2027, FY 2027 October (to date) and the comparison base FY 2026.
Rs crore per trading day; F&O, Cash and Commodities are net brokerage, MTF is net interest income (NII), Broking =
F&O + Cash + Commodities, Consolidated = Broking + MTF. "Before" = the switches earlier in the order a -> f; "after"
adds this one. Every run reads the series up to BRIDGE_AS_OF (the workbook snapshot's last day, 21 Oct 2026), so
the bridges compare like with like whatever the lake holds after it.
"""
import os
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


# ── m-g: FY24 quarters ──
FY24_PANEL_SEGS = (('F&O', 'fo'), ('Cash', 'cash'), ('Commodities', 'comm'))


def _row_key(r):
    return (r['panel'], r['period_type'], r['period_key'], r['table_name'], r['row_label'])


def _is_fy24(period_type, key):
    """Period keys that belong to FY24 (or earlier): FY 2024, Q1-Q4 FY 2024, 'FY 2024 <month>'. The as-of tables are keyed
    by a date and never FY24."""
    if period_type == 'asof':
        return False
    return (key[:7] == 'FY 2024') if period_type in ('FY', 'M') else (key[-7:] == 'FY 2024')


def fy24_effect(M_a, r_a, M_b, r_b):
    """What m-g changes in the live (guarded) summary rows, a-f -> a-g.
    Returns dict(fy25_changed=[(key, field, before, after)], fy25_unchanged=n, fy24_new=[rows only a-g has],
    violations=[...]). A violation is an FY25+ value that changed, or a comparison that changed from a value."""
    ra, rb = ({_row_key(r): r for r in live_period_rows(M, res)} for M, res in ((M_a, r_a), (M_b, r_b)))
    changed, same, violations = [], 0, []
    for k, y in rb.items():
        if _is_fy24(k[1], k[2]):
            continue
        x = ra.get(k)
        if x is None:
            violations.append((k, 'row', None, 'new row'))
            continue
        moved_ = False
        for f in ('value', 'comp_value'):
            if x[f] == y[f]:
                continue
            moved_ = True
            if x[f] is None:
                changed.append((k, f, None, y[f]))
            else:
                violations.append((k, f, x[f], y[f]))
        same += not moved_
    for k in ra:
        if k not in rb:
            violations.append((k, 'row', 'dropped', None))
    return dict(fy25_changed=changed, fy25_unchanged=same, violations=violations,
                fy24_rows=[r for k, r in rb.items() if _is_fy24(k[1], k[2])],
                fy24_only_after=[k for k in rb if _is_fy24(k[1], k[2]) and k not in ra])


def g_detail(M, res, quarters=MS.FY24_QUARTERS):
    """Per FY24 quarter and segment: the calibration quantities and the quarter's revenue, ADR and its arithmetic.
    Returns {(segment, quarter): dict}; revenue in Rs Cr (net = net / gross x gross), days = rows the quarter has."""
    c, d = res['calib'], res['daily']
    adr_q = adr(M, res, tuple(('Q', q) for q in quarters))
    out = {}
    for q in quarters:
        r = c['ratio'][q]
        fo, cash = c['fo']['table'][q], c['cash']['table'][q]
        gross_fact = {s: M.fact(f'gross_{s}_cr', q) for s in ('fo', 'cash', 'comm')}
        keys = {'fo': (fo['F'], 'Cr contracts (NSE index options + BSE)'),
                'cash': (cash['key'], 'Rs Cr turnover (NSE + BSE)'),
                'comm': (c['comm']['contracts_mn'][q], 'Mn contracts (MCX)')}
        share = {'fo': c['fo']['share'][q], 'cash': cash['share'], 'comm': c['comm']['share'][q]}
        rate = {'fo': c['fo']['rate'][q] / 10, 'cash': cash['J'], 'comm': c['comm']['take'][q]}      # Rs per contract; cash: gross per Rs of ADTO
        for name, seg in FY24_PANEL_SEGS:
            rows = {dd: x for dd, x in d[seg].items() if q_of(dd) == q}
            field, scale = ('rev_cr', 1.0) if seg == 'cash' else ('rev_mn', 10.0)
            rev = sum(x[field] for x in rows.values()) / scale                       # the quarter's net revenue, every day
            sp = special_dates(M)                                                    # m-d: special sessions out of the ADR
            adr_rev = sum(x[field] for dd, x in rows.items() if dd not in sp) / scale
            n = sum(1 for dd in rows if dd not in sp)
            n_special = len(rows) - n
            out[(name, q)] = dict(share=share[seg], key=keys[seg][0], key_unit=keys[seg][1], rate=rate[seg], ng=r[seg],
                                  gross=gross_fact[seg], revenue=rev, days=n, n_special=n_special, adr_revenue=adr_rev, adr=adr_rev / n, adr_engine=adr_q[('Q', q, name)],
                                  seg=seg, G=cash['G'] if seg == 'cash' else None, H=cash['H'] if seg == 'cash' else None)
        out[('Broking', q)] = dict(adr=sum(out[(n_, q)]['adr'] for n_, _ in FY24_PANEL_SEGS),
                                   adr_engine=adr_q[('Q', q, 'Broking')])
    return out


def g_arith(name, q, x):
    """One line of arithmetic for a segment-quarter (Rs Cr)."""
    if x['seg'] == 'fo':
        K = x['share'] * x['key']
        return (f"{name} {q}: K = share x key = {x['share']:.6f} x {x['key']:,.4f} = {K:,.4f} Cr contracts; "
                f"rate = gross / K = {x['gross']:,.4f} / {K:,.4f} = {x['rate']:.4f} Rs per contract; net = {x['ng']:.6f} x "
                f"{x['gross']:,.4f} = {x['ng'] * x['gross']:,.4f} Rs Cr; ADR = {x['adr_revenue']:,.4f} / {x['days']} days = {x['adr']:.6f}")
    if x['seg'] == 'cash':
        return (f"{name} {q}: gross per Rs of reported ADTO J = gross / ADTO = {x['gross']:,.4f} / {x['G']:,.4f} = {x['rate']:.6f}; "
                f"day gross = share x (key_d / H) x (J x ADTO / days) with H = share x avg key / ADTO = {x['H']:.4f}; "
                f"quarter key = {x['key']:,.2f} Rs Cr over {x['days']} days; net = {x['ng']:.6f} x {x['gross']:,.4f} = "
                f"{x['ng'] * x['gross']:,.4f}; ADR = {x['adr_revenue']:,.4f} / {x['days']} days = {x['adr']:.6f}")
    return (f"{name} {q}: take = gross x 10 / (share x contracts) = {x['gross']:,.4f} x 10 / ({x['share']:.6f} x {x['key']:,.4f}) "
            f"= {x['rate']:.4f} Rs per contract; net = {x['ng']:.6f} x {x['gross']:,.4f} = {x['ng'] * x['gross']:,.4f}; "
            f"ADR = {x['adr_revenue']:,.4f} / {x['days']} days = {x['adr']:.6f}")


# ── the bridge ──
def bridge(letter, shared_snapshot=None, mosl_snapshot=MOSL_SNAPSHOT, lake_path=None):
    """shared_snapshot / lake_path default to the parity fixtures; m-g (market data from 1 June 2023) defaults to
    snapshot/db_snapshot_2026-11-03.json and snapshot/mosl_lake_2026-11-03.json."""
    if letter == 'g':
        shared_snapshot, lake_path = shared_snapshot or MS.SHARED_FIXTURE_G, lake_path or MS.LAKE_FIXTURE_G
    shared_snapshot = shared_snapshot or SHARED_SNAPSHOT
    before, after = MS.cumulative(letter)
    M_a, r_a = run_switches(before, shared_snapshot, mosl_snapshot, lake_path=lake_path)
    M_b, r_b = run_switches(after, shared_snapshot, mosl_snapshot, lake_path=lake_path)
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
    g = None
    if letter == 'g':
        eff = fy24_effect(M_a, r_a, M_b, r_b)
        assert not eff['violations'], eff['violations'][:5]                          # no FY25+ value may change
        assert all(r['value'] is None for r in eff['fy24_rows'] if r['period_key'] == 'FY 2024' or r['row_label'] == 'Q1 FY 2024'
                   or (r['panel'] == 'Consolidated' and r['row_label'] == r['period_key'])), 'FY 2024 / Q1 FY24 / Consolidated FY24'
        M_o, r_o = run_switches(before, SHARED_SNAPSHOT, mosl_snapshot)              # a-f on the 23 Oct / 2 Nov fixtures
        t_o, t_n = adr(M_o, r_o), t_a
        g = dict(effect=eff, detail=g_detail(M_b, r_b), shared=shared_snapshot, lake=lake_path,
                 fixture_effect=[(k, panel, t_o[(p, k, panel)], t_n[(p, k, panel)]) for p, k in PERIODS for panel in SP.PANELS
                                 if abs(t_o[(p, k, panel)] - t_n[(p, k, panel)]) > 1e-9 * max(1.0, abs(t_o[(p, k, panel)]))],
                 quarters=M_b.qs[:3], first_rows={q: {s: min(d for d in r_b['daily'][s] if q_of(d) == q) for s in ('fo', 'cash', 'comm')}
                                                  for q in M_b.qs[:3]},
                 no_row_dates=sorted(d for d in M_b.cal if d < '2023-07-01'))
    return dict(letter=letter, g=g, before=sorted(before), after=sorted(after), rows=rows, yoy=yoy,
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
              'a period with no value at all is flagged insufficient in the live rows. The ADR tables below are the unguarded '
              'statistics (a segment with no value in a month adds 0 to the sum, as FY 2027 October does for cash and commodities '
              'until m-e); the live rows flag such a period as insufficient instead.', '']
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
    if b['letter'] == 'g':
        L += _g_markdown(b)
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


def _g_markdown(b):
    g = b['g']
    eff, det = g['effect'], g['detail']
    qs = MS.FY24_QUARTERS
    L = ['## m-g: FY24 quarters', '',
         "MOSL's quarters now start at Q2 FY24 (Jul 2023). F&O, cash and commodities calibrate Q2 - Q4 FY24 exactly as m-a does "
         "for FY25+: rate = reported gross brokerage / (share x the quarter's key), revenue = rate x share x the day's key x "
         "net / gross. The facts are the 116 FY24 facts (AB approved them with the switch on 3 Nov 2026); the FY24 gross and net "
         "brokerage Rs Mn are divided by 10 to Rs Cr. Market data from 1 June 2023 "
         f"({os.path.basename(g['shared'])}, {os.path.basename(g['lake'])}; read only from ExchangesDash's public JSON). "
         f"No revenue row exists before Q2 FY24 (the {len(g['no_row_dates'])} calendar days from {g['no_row_dates'][0]} to "
         f"{g['no_row_dates'][-1]} have none). First revenue day per segment: "
         + '; '.join(f"{n} {g['first_rows'][qs[0]][sg]}" for n, sg in FY24_PANEL_SEGS) + '. MTF is unchanged: NII still starts '
         'Q3 FY25 (no industry book before Oct 2024), so Consolidated FY24 stays insufficient.', '',
         'Per segment and quarter (Rs crore; ADR = net revenue / trading days with a row, special sessions left out by m-d: net revenue below counts every day, ADR does not):', '',
         '| Segment | Quarter | Share | Quarter key | Rate | Net / gross | Gross Rs Cr | Net revenue Rs Cr | Days | ADR |',
         '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name, _ in FY24_PANEL_SEGS:
        for q in qs:
            x = det[(name, q)]
            rate = f"{x['rate']:.4f}" if x['seg'] != 'cash' else f"{x['rate']:.6f}"
            L.append(f"| {name} | {q} | {x['share']:.6f} | {x['key']:,.2f} ({x['key_unit']}) | {rate} | {x['ng']:.6f} | "
                     f"{x['gross']:,.4f} | {x['revenue']:,.4f} | {x['days']} | {_f6(x['adr'])} |")
    L += ['', "Rate: F&O and commodities in Rs per contract (gross / (share x key)); cash is gross per Rs of the data book's "
          'ADTO (J). Arithmetic:', '']
    for name, _ in FY24_PANEL_SEGS:
        for q in qs:
            L.append('- ' + g_arith(name, q, det[(name, q)]))
    L += ['', 'Broking ADR (F&O + Cash + Commodities, Rs crore per trading day):', '',
          '| Quarter | F&O | Cash | Commodities | Broking |', '|---|---:|---:|---:|---:|']
    for q in qs:
        assert abs(det[('Broking', q)]['adr'] - det[('Broking', q)]['adr_engine']) < 1e-12, q
        L.append(f"| {q} | " + ' | '.join(_f6(det[(n, q)]['adr']) for n, _ in FY24_PANEL_SEGS)
                 + f" | {_f6(det[('Broking', q)]['adr'])} |")
    L += ['']
    insuff = [r for r in eff['fy24_rows'] if r['value'] is None and r['row_label'] == r['period_key']
              and r['period_type'] in ('FY', 'Q')]
    q1 = [r for r in eff['fy24_rows'] if r['row_label'] == 'Q1 FY 2024' and r['value'] is None]
    L += ['Still "insufficient data" after m-g (live rows):', '']
    for r in sorted(insuff, key=lambda r: (r['period_key'], r['panel'])):
        L.append(f"- {r['panel']} {r['period_key']}: {r['note']}")
    L.append(f"- Q1 FY 2024 (the base of Q2 FY24's QoQ): {len(q1)} panels, e.g. {q1[0]['note'] if q1 else '-'}")
    L += ['', "FY25+ cells (every FY / quarter / month / week row of FY 2025 onward, all panels): "
          f"{len(eff['fy25_changed'])} change from \"insufficient data\" to a value, {eff['fy25_unchanged']} are unchanged, "
          f"{len(eff['violations'])} change a value that was already there (asserted 0).", '']
    grouped = {}
    for k, f, _, y in eff['fy25_changed']:
        grouped.setdefault((k[1], k[2], k[4], f), []).append(k[0])
    L += ['| Period | Row | Field | Panels (insufficient data -> value) |', '|---|---|---|---|']
    for (pt, pk, rl, f), panels in sorted(grouped.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
        L.append(f"| {pk} | {rl.replace(' | ', ' / ')} | {'value' if f == 'value' else 'comparison'} | {', '.join(sorted(panels))} |")
    L += ['', 'A "value" row is the FY24 base of a FY25 comparison (e.g. the "Q2 FY 2024" row inside Q2 FY25); a "comparison" '
          'row is the YoY, QoQ, MoM or vs-6M figure itself.', '']
    if g['fixture_effect']:
        L += ['Data effect, not the switch: a-f on these fixtures (market data from 1 Jun 2023, MCX days flagged, owner '
              'corrections to two 2025 NSE cash turnover days) against a-f on the 23 Oct / 2 Nov fixtures:', '',
              '| Period | Panel | a-f, old fixtures | a-f, new fixtures |', '|---|---|---:|---:|']
        for k, panel, x, y in g['fixture_effect']:
            L.append(f'| {k} | {panel} | {_f6(x)} | {_f6(y)} |')
        L.append('')
    else:
        L += ['a-f on these fixtures equals a-f on the 23 Oct / 2 Nov fixtures (to 1e-9) in every bridge period and panel: the data effect is nil at the period level.', '']
    return L


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
