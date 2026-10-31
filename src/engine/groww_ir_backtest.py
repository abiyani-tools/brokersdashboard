"""Backtests of the Groww IR switches (out/groww/backtest_ir_switches.md).

    python3 -m src.engine.groww_ir_backtest            # rewrites out/groww/backtest_ir_switches.md

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


def main(argv=None):
    rows_h = backtest_h()
    text = '\n'.join(['# Groww IR switches: backtests', ''] + markdown_h(rows_h)) + '\n'
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as fh:
        fh.write(text)
    print(text)
    print(f'written {os.path.relpath(OUT)}')


if __name__ == '__main__':
    main(sys.argv[1:])
