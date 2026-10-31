"""Backtests of the Groww IR switches (out/groww/backtest_ir_switches.md).

    python3 -m src.engine.groww_ir_backtest            # rewrites out/groww/backtest_ir_switches.md

g-i  predicts each reported quarter's MTF revenue from Groww's own book (quarter-end levels from the IR page) and
     from g-f's industry-book method, and compares both with the disclosed MTF revenue. Q3 FY25 .. Q2 FY27.

g-h  predicts each reported quarter's F&O and cash share, and its segment revenue, from the previous reported quarter,
     by (i) carry (g-e) and (ii) the g-h ratio, and compares both with the disclosed values. Quarters Q3 FY26 .. Q2 FY27.
"""
import json
import os
import sys
from statistics import mean

from . import groww, groww_bridge as B, groww_ir as IR, groww_switches as GS
from .inputs import quarter_seq

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'out', 'groww', 'backtest_ir_switches.md')
H_QUARTERS = quarter_seq('Q3 FY 2026', 'Q2 FY 2027')
SEG = (('fo', 'F&O', 'fo_quarter'), ('cash', 'Cash', 'cash_quarter'))


def _ir_and_turnover():
    ir = IR.IR(json.load(open(GS.IR_FIXTURE))['rows'])
    return ir, IR.Turnover.from_fixture(GS.EXCHANGE_FIXTURE)


def backtest_h():
    """Rows per segment and quarter: disclosed share and revenue, the carry (g-e) and g-h predictions and their errors.

    Disclosed share = the share the engine calibrates on (ADTO share, legacy basis: the printed value, or 2 x the
    printed new-basis value); disclosed revenue = revenue-mix x total income. Predicted revenue = the previous quarter's
    take rate x the quarter's market orders (disclosed orders / disclosed share, i.e. the engine's market-order base)
    x the predicted share. Only the share differs between the two methods."""
    I, G, res = B.run_switches(tuple('abcdefg'))
    ir, turnover = _ir_and_turnover()
    calib = res['calib']
    rows = []
    for seg, name, table in SEG:
        t = calib[table]
        for q in H_QUARTERS:
            p = quarter_seq('Q2 FY 2026', q)[-2]
            a, b = t[q], t[p]
            assert a['regime'] == b['regime'] == 'actual'
            r = IR.qtd_share_ratio(ir, turnover, seg, q, p)
            mkt = a['orders_mn'] / a['share']                         # market orders of quarter q (Mn)
            disc_share, disc_rev = a['share'], a['rev_mn']
            carry_share = b['share']
            h_share = b['share'] * r['ratio']
            rows.append(dict(segment=name, quarter=q, prev=p, ratio=r['ratio'], disclosed_share=disc_share,
                             carry_share=carry_share, h_share=h_share, disclosed_rev=disc_rev,
                             carry_rev=b['take_rate'] * mkt * carry_share, h_rev=b['take_rate'] * mkt * h_share,
                             take_rate_prev=b['take_rate']))
    for r in rows:
        for k in ('carry', 'h'):
            r[f'{k}_share_err'] = r[f'{k}_share'] / r['disclosed_share'] - 1
            r[f'{k}_rev_err'] = r[f'{k}_rev'] / r['disclosed_rev'] - 1
    return rows


def _stats(rows, key):
    e = [r[key] for r in rows]
    return dict(mean=mean(e), mae=mean(abs(x) for x in e), max=max(abs(x) for x in e),
                wins=None)


BASIS_BREAK = 'Q4 FY 2026'      # Groww doubled the share denominator here: the disclosed legacy share jumps for both methods


def summary_h(rows):
    out = {}
    groups = [(n, lambda r, n=n: r['segment'] == n) for n in sorted({r['segment'] for r in rows})]
    groups += [('All', lambda r: True), (f'All ex {BASIS_BREAK[:2]} FY26', lambda r: r['quarter'] != BASIS_BREAK)]
    for name, keep in groups:
        sel = [r for r in rows if keep(r)]
        out[name] = {}
        for what in ('share', 'rev'):
            c, h = _stats(sel, f'carry_{what}_err'), _stats(sel, f'h_{what}_err')
            h['wins'] = sum(abs(r[f'h_{what}_err']) < abs(r[f'carry_{what}_err']) for r in sel)
            out[name][what] = {'carry': c, 'h': h, 'n': len(sel)}
    return out


def _p(x, d=1):
    return f'{100 * x:+.{d}f}%'


def _a(x, d=1):
    return f'{100 * x:.{d}f}%'


def markdown_h(rows):
    s = summary_h(rows)
    L = ['## g-h: quarter-to-date turnover share, backtest on reported quarters', '',
         'Each reported quarter Q3 FY26 .. Q2 FY27 is predicted from the previous reported quarter, by (i) carry (g-e: '
         'the previous share) and (ii) g-h (previous share x the change in Groww\'s share of NSE+BSE turnover):', '',
         '    share_pred = share_prev x (Groww turnover share in q / Groww turnover share in prev)',
         '    Groww turnover share = Groww turnover / exchange turnover over the same days (whole quarters here)',
         '    cash: IR stocks turnover vs NSE cash_traded_value + BSE cash_traded_value',
         '    F&O : IR equity-derivatives premium turnover vs NSE index + stock option premium + BSE options_premium_turnover',
         '', 'Revenue prediction = previous quarter\'s take rate x the quarter\'s market orders x predicted share (the '
         'engine\'s own order model; the take rate is unchanged, calibrated on the previous reported quarter). So the '
         'share error and the revenue error of a method are the same number up to the take-rate drift between the two '
         'quarters. "Disclosed" = the share the engine calibrates on (ADTO share, legacy basis, 3 decimals as printed: '
         'a +-0.0005 rounding is +-0.2-0.5% of the share) and the revenue mix x total income of the filing.', '',
         'Data: IR page history (snapshot/groww_ir_2026-10-31.json, built from the saved page of 31 Oct 2026), exchange '
         'turnover (snapshot/groww_exchange_2026-10-31.json = sb_market_daily \'exchangesdash_json\'), facts '
         '(snapshot/groww_facts_reviewed_2026-10-31.json), engine run g-a..g-g.', '',
         '| Segment | Quarter | Prev | Ratio | Disclosed share | Carry share | err | g-h share | err | Disclosed rev Rs Mn | '
         'Carry rev | err | g-h rev | err |', '|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        L.append(f"| {r['segment']} | {r['quarter']} | {r['prev']} | {r['ratio']:.4f} | {r['disclosed_share']:.4f} | "
                 f"{r['carry_share']:.4f} | {_p(r['carry_share_err'])} | {r['h_share']:.4f} | {_p(r['h_share_err'])} | "
                 f"{r['disclosed_rev']:,.0f} | {r['carry_rev']:,.0f} | {_p(r['carry_rev_err'])} | "
                 f"{r['h_rev']:,.0f} | {_p(r['h_rev_err'])} |")
    L += ['', 'Summary (relative error vs disclosed; n = quarters):', '',
          '| Segment | n | Share: carry mean | carry mean abs | carry max abs | g-h mean | g-h mean abs | g-h max abs | '
          'g-h closer in | Revenue: carry mean abs | carry max abs | g-h mean abs | g-h max abs | g-h closer in |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name, v in s.items():
        sh, rv = v['share'], v['rev']
        L.append(f"| {name} | {sh['n']} | {_p(sh['carry']['mean'])} | {_a(sh['carry']['mae'])} | {_a(sh['carry']['max'])} | "
                 f"{_p(sh['h']['mean'])} | {_a(sh['h']['mae'])} | {_a(sh['h']['max'])} | {sh['h']['wins']}/{sh['n']} | "
                 f"{_a(rv['carry']['mae'])} | {_a(rv['carry']['max'])} | {_a(rv['h']['mae'])} | "
                 f"{_a(rv['h']['max'])} | {rv['h']['wins']}/{rv['n']} |")
    allr, ex = s['All'], s[f'All ex {BASIS_BREAK[:2]} FY26']
    sh, rv, shx, rvx = allr['share'], allr['rev'], ex['share'], ex['rev']
    L += ['', 'Reading (plain):', '',
          f"- Share, all 8: carry mean abs {_a(sh['carry']['mae'])} vs g-h {_a(sh['h']['mae'])}; revenue {_a(rv['carry']['mae'])} "
          f"vs {_a(rv['h']['mae'])}. Max abs share error {_a(sh['carry']['max'])} vs {_a(sh['h']['max'])}.",
          f"- Cash: g-h is better (share {_a(s['Cash']['share']['carry']['mae'])} -> {_a(s['Cash']['share']['h']['mae'])}, "
          f"revenue {_a(s['Cash']['rev']['carry']['mae'])} -> {_a(s['Cash']['rev']['h']['mae'])}). F&O: g-h is not better "
          f"(share {_a(s['F&O']['share']['carry']['mae'])} -> {_a(s['F&O']['share']['h']['mae'])}, revenue "
          f"{_a(s['F&O']['rev']['carry']['mae'])} -> {_a(s['F&O']['rev']['h']['mae'])}).",
          f"- Q4 FY26 is a definition break in the disclosed share (Groww doubled the denominator; the engine's legacy "
          f"value is 2 x the printed one, which assumes the break was exactly 2x). Neither method can see it: both miss the "
          f"share by 7-15% there (F&O -15%, cash -7 to -8%). Without it: share {_a(shx['carry']['mae'])} vs {_a(shx['h']['mae'])}, revenue "
          f"{_a(rvx['carry']['mae'])} vs {_a(rvx['h']['mae'])}.",
          '- n = 4 quarters per segment: the differences are inside the noise of the disclosed share (printed to 3 '
          'decimals) and of mix x total income. g-h does NOT clearly beat carry; it helps cash and hurts F&O. '
          "Its live effect today is small (Q3 FY27 ratio cash 0.981, F&O 1.002). Adopting it is AB's call.", '']
    return L


# ── g-i ──
I_QUARTERS = quarter_seq('Q3 FY 2025', 'Q2 FY 2027')
MIX_ROUNDED = ('Q3 FY 2025', 'Q4 FY 2025')   # MTF revenue mix printed as a whole percent (2%): +-25% of the figure


def backtest_i():
    """Rows per reported quarter: disclosed MTF revenue (Rs Cr) and three predictions.

    own_qe     Groww's quarter-end net book x 14.95% x (days in quarter / FY trading days)       [g-i's input, simplest]
    own_path   the g-i rule at k = 1: sum over the quarter's days of the interpolated own book x 14.95% / FY days
    own_open   the previous quarter-end level held flat x 14.95% x days / FY days: the open-quarter rule ('latest level')
               as it would stand on day 1 of the quarter, the only variant that does not know the quarter's own end level
    own_k      own_path x k of the previous reported quarter (k = disclosed / own_path), i.e. the calibration carried
    industry   g-f's method: previous quarter's share of the industry book carried (g-e) x this quarter's industry
               average book x 14.95% x (days in quarter / FY trading days); needs a previous quarter (not Q3 FY25)
    Disclosed = MTF revenue mix x total income (the g-a fact, Rs Cr)."""
    I, G, res = run_chain()
    y = G.assume('mtf_yield')
    ir = IR.IR(json.load(open(GS.IR_FIXTURE))['rows'])
    fy_days = groww.fy_trading_days(I.cal)
    days = sorted(d for d, r in I.cal.items() if r['is_equity_day'] and d >= '2024-10-01')
    own = IR.own_book_path(ir, days)
    industry = I.series('mtf_industry', 'book_cr')
    levels = ir.book_levels_cr()
    byq, indq = {}, {}
    for d in days:
        byq.setdefault(IR.quarter_of(d), []).append(d)
    for d, v in industry.items():
        indq.setdefault(IR.quarter_of(d), []).append(v)
    rows, prev = [], None
    for q in I_QUARTERS:
        ds = byq[q]
        D = fy_days[q[3:]][0]
        disclosed = G.fact('mtf_revenue', q)
        own_path = sum(own[d][0] for d in ds) * y / D
        r = dict(quarter=q, disclosed=disclosed, book_end=levels[q], days=len(ds), fy_days=D,
                 own_qe=levels[q] * y * len(ds) / D, own_path=own_path,
                 own_open=levels[IR.prev_quarter(q)] * y * len(ds) / D,
                 own_k=None, industry=None, k=disclosed / own_path)
        if prev is not None:
            r['own_k'] = own_path * prev['k']
            n_p, n_q = len(indq[prev['quarter']]), len(indq[q])
            share_prev = prev['disclosed'] / (y * n_p / prev['fy_days']) / mean(indq[prev['quarter']])
            r['industry'] = share_prev * mean(indq[q]) * y * n_q / D
        rows.append(r)
        prev = r
    for r in rows:
        for k in ('own_qe', 'own_path', 'own_open', 'own_k', 'industry'):
            r[f'{k}_err'] = None if r[k] is None else r[k] / r['disclosed'] - 1
    return rows


def run_chain():
    return B.run_switches(tuple('abcdefg'))


def _s(rows, key, keep=lambda r: True):
    e = [r[key] for r in rows if r[key] is not None and keep(r)]
    return dict(n=len(e), mean=mean(e), mae=mean(abs(x) for x in e), max=max(abs(x) for x in e))


def summary_i(rows):
    """{label: {method: stats}} for the quarters every method can predict (Q4 FY25 .. Q2 FY27), for all 8 quarters the
    own-book methods can, and without the two quarters whose disclosed figure comes from a whole-percent mix."""
    common = lambda r: r['industry'] is not None
    ex = lambda r: r['quarter'] not in MIX_ROUNDED
    both = lambda r: common(r) and ex(r)
    out = {'Q4 FY25..Q2 FY27 (7, every method)': {m: _s(rows, f'{m}_err', common)
                                                  for m in ('industry', 'own_qe', 'own_path', 'own_open', 'own_k')},
           'Q1 FY26..Q2 FY27 (6, mix to 0.1pp)': {m: _s(rows, f'{m}_err', both)
                                                 for m in ('industry', 'own_qe', 'own_path', 'own_open', 'own_k')},
           'Q3 FY25..Q2 FY27 (8, own book only)': {m: _s(rows, f'{m}_err')
                                                   for m in ('own_qe', 'own_path', 'own_open')}}
    return out


def markdown_i(rows):
    s = summary_i(rows)
    L = ['## g-i: MTF from Groww\'s own book, backtest on reported quarters', '',
         'Disclosed MTF revenue = revenue mix x total income (Rs Cr). Predictions, each without looking at the disclosed '
         'revenue of the quarter predicted:', '',
         '- **own book, quarter-end** = Groww MTF net book at the quarter end (IR page) x 14.95% x days in quarter / trading '
         'days of the FY.',
         '- **own book, g-i path (k = 1)** = the g-i rule: daily book interpolated linearly between quarter-end levels '
         '(calendar days), x 14.95% / FY trading days, summed over the quarter.',
         '- **own book, previous quarter-end level held flat** = the open-quarter rule ("latest level, held flat") as it would '
         'stand on day 1 of the quarter: the only own-book variant that does not know the quarter\'s own end level (the page '
         'keeps no intra-quarter history, so a mid-quarter version cannot be tested).',
         '- **own book, path x previous k** = the path above times k of the previous reported quarter (k = disclosed / '
         'path), i.e. the g-f-style calibration carried one quarter. Not what g-i does for the open quarter (k = 1); shown for '
         'comparison.',
         '- **industry book (g-f / g-e)** = the previous quarter\'s share of the industry book carried x this quarter\'s '
         'industry average book x 14.95% x days / FY days. This is how g-f + g-e price an unreported quarter.', '',
         'Trading days of the FY are the calendar\'s equity days (g-f convention; FY27 uses FY26\'s count until the FY is '
         'complete). Q3 FY25 and Q4 FY25 disclose the MTF mix as a whole percent (2%), so their "disclosed" revenue is '
         'known only to about +-25%. The industry book series starts 1 Oct 2024, so the industry method needs a previous '
         'quarter and starts at Q4 FY25. Q1 and Q2 FY25 have no disclosed MTF revenue (no MTF mix before Q3 FY25).', '',
         '| Quarter | Days | Own book at qtr end Rs Cr | Disclosed Rs Cr | Own qtr-end | err | Own path (k=1) | err | '
         'Own path x prev k | err | Prev qtr-end held flat | err | Industry (g-f) | err | k (disclosed / path) |',
         '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    f = lambda x: '—' if x is None else f'{x:,.2f}'
    e = lambda x: '—' if x is None else _p(x)
    for r in rows:
        L.append(f"| {r['quarter']} | {r['days']} | {r['book_end']:,.1f} | {r['disclosed']:,.2f} | {f(r['own_qe'])} | "
                 f"{e(r['own_qe_err'])} | {f(r['own_path'])} | {e(r['own_path_err'])} | {f(r['own_k'])} | "
                 f"{e(r['own_k_err'])} | {f(r['own_open'])} | {e(r['own_open_err'])} | {f(r['industry'])} | {e(r['industry_err'])} | {r['k']:.3f} |")
    L += ['', 'Summary (relative error vs disclosed):', '',
          '| Quarters | Method | n | Mean (signed) | Mean abs | Max abs |', '|---|---|---:|---:|---:|---:|']
    names = {'industry': 'industry book (g-f)', 'own_qe': 'own book, quarter-end', 'own_path': 'own book, g-i path (k=1)',
             'own_open': 'own book, previous quarter-end held flat', 'own_k': 'own book, path x previous k'}
    for label, d in s.items():
        for m, v in d.items():
            L.append(f"| {label} | {names[m]} | {v['n']} | {_p(v['mean'])} | {_a(v['mae'])} | {_a(v['max'])} |")
    c = s['Q4 FY25..Q2 FY27 (7, every method)']
    c6 = s['Q1 FY26..Q2 FY27 (6, mix to 0.1pp)']
    L += ['', 'Reading (plain):', '',
          f"- On the 7 quarters every method can predict: industry book (g-f) mean abs {_a(c['industry']['mae'])} / max "
          f"{_a(c['industry']['max'])}; Groww's own book on the g-i path {_a(c['own_path']['mae'])} / {_a(c['own_path']['max'])}; "
          f"own book at quarter end {_a(c['own_qe']['mae'])} / {_a(c['own_qe']['max'])}. On the 6 quarters with a mix known to "
          f"0.1pp: industry {_a(c6['industry']['mae'])} / {_a(c6['industry']['max'])}, own path {_a(c6['own_path']['mae'])} / "
          f"{_a(c6['own_path']['max'])}.",
          f"- Caution: the quarter-end and path variants use the quarter's own end level, which the open quarter does not "
          f"have. The variant that does not (previous quarter-end level held flat: the live open-quarter rule as on day 1) "
          f"has mean abs error {_a(c['own_open']['mae'])} / max {_a(c['own_open']['max'])} on the 7 quarters, signed mean "
          f"{_p(c['own_open']['mean'])}: with a book growing 10-70% a quarter it under-states, as the industry method does "
          f"({_p(c['industry']['mean'])} signed). Mid-quarter the live rule uses the latest archived level, which is closer "
          "than day 1; that cannot be backtested (the page keeps no intra-quarter history).",
          '- The own-book methods carry no calibration and are not fitted on the revenue they predict; the industry '
          "method carries a share fitted on the previous quarter. The quarter-end level overstates a quarter's average "
          'book when the book is rising (hence the positive signed mean); interpolating between quarter ends removes most '
          'of that, at the price of needing the quarter\'s end level.',
          '- k (last column) is the residual between "own book x 14.95%" and the disclosed revenue: it is the calibration '
          'g-i keeps in reported quarters, so reported-quarter totals still tie to the disclosure exactly. It ranges '
          f"{min(r['k'] for r in rows):.2f}-{max(r['k'] for r in rows):.2f}; the Q3-Q4 FY25 values include the whole-percent "
          'mix rounding.', '']
    return L


def main(argv=None):
    rows_h, rows_i = backtest_h(), backtest_i()
    text = '\n'.join(['# Groww IR switches: backtests', ''] + markdown_h(rows_h) + [''] + markdown_i(rows_i)) + '\n'
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as fh:
        fh.write(text)
    print(text)
    print(f'written {os.path.relpath(OUT)}')


if __name__ == '__main__':
    main(sys.argv[1:])
