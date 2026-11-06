"""PAT model run (PLAN 5.7): quarterly P&L → FY27E / FY28E → valuation, per broker.

    python3 run_pat.py                    # dry run on local inputs (out/pat/dev, snapshot facts), report to out/pat/<as_of>/
    python3 run_pat.py --broker GROWW
    python3 run_pat.py --db [--publish]   # read the latest live run, facts and assumptions from the DB; --publish writes sb_pat_lines

Local inputs: daily ADR rows and prices in out/pat/dev/<BROKER>_{daily,prices}.json (the published run, read from
/api/brokers), facts from snapshot/ (reviewed) plus the staged P&L extracts in out/pat/facts_*_pl.json, and
assumptions from seed/pat_assumptions.json.
"""
from __future__ import annotations

import argparse
import glob
import json
import os

from src.engine import pat as P

SHEET = {   # workbook headline cells, for the bridge in the report (20260714_brokers dashboard v2.xlsx)
    'ANGELONE': {'FY27 PAT': (870.43, "Angel One - ADR model (A+B)!C22"), 'FY28 PAT': (1387.49, '!C44'),
                 'FY28 target today (base)': (265.39, '!D51')},
    'GROWW': {'FY27 PAT': (2726.12, 'Groww - ADR Model!C23'), 'FY28 PAT': (3761.23, '!C45'),
              'FY28 target today (base)': (205.28, '!D52')},
}


def local_facts(broker):
    facts = []
    if broker == 'ANGELONE':
        rv = json.load(open(sorted(glob.glob('snapshot/facts_reviewed_*.json'))[-1]))
        facts += [dict(f, broker_id='ANGELONE') for f in (rv['facts'] if isinstance(rv, dict) else rv)]
        # quarters the reviewed set lacks (Q3 FY26 funding book, older revenue mix): staged rows from the DB snapshot
        have = {(f['period_key'], f['metric']) for f in facts}
        db = json.load(open(sorted(glob.glob('snapshot/db_snapshot_*.json'))[-1]))['facts']
        facts += [dict(f, broker_id='ANGELONE', note=(f.get('note') or '') + ' [staged]') for f in db
                  if f['metric'].startswith(('revmix_', 'avg_funding_book')) and (f['period_key'], f['metric']) not in have]
    else:
        facts += json.load(open(sorted(glob.glob('snapshot/groww_facts_reviewed_*.json'))[-1]))['facts']
    pl = json.load(open(f'out/pat/facts_{"angel" if broker == "ANGELONE" else "groww"}_pl.json'))
    facts += pl['facts'] + [dict(pl['shares'], period_key=None)]
    return facts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--broker', default='all')
    ap.add_argument('--db', action='store_true')
    ap.add_argument('--publish', action='store_true')
    a = ap.parse_args()
    if a.publish and not a.db:
        raise SystemExit('--publish needs --db')
    if a.db:
        return db_run(['ANGELONE', 'GROWW'] if a.broker == 'all' else [a.broker], a.publish)
    brokers = ['ANGELONE', 'GROWW'] if a.broker == 'all' else [a.broker]
    assumptions = json.load(open('seed/pat_assumptions.json'))['assumptions']
    for b in brokers:
        daily = json.load(open(f'out/pat/dev/{b}_daily.json'))
        px = json.load(open(f'out/pat/dev/{b}_prices.json'))['prices'][-1]
        facts = local_facts(b)
        shares = next(f['value'] for f in facts if f['metric'] == 'shares_outstanding_cr')
        m = P.build(b, facts, daily['rows'], assumptions, dict(price=px['close'], date=px['trade_date']), shares)
        out = f"out/pat/{m['as_of']}"
        os.makedirs(out, exist_ok=True)
        json.dump(P.rows(m, daily['run']['run_id']), open(f'{out}/{b}_pat_lines.json', 'w'), indent=1)
        open(f'{out}/{b}_report.md', 'w').write(report(m, daily['run']['run_id']))
        print(open(f'{out}/{b}_report.md').read())
    preview(brokers, out)


def db_inputs(reader, broker):
    """The latest successful live ADR run of the broker and everything the model reads (reviewed facts only)."""
    runs = [r for r in reader.table('sb_runs', broker_id=broker, mode='live') if r['status'] == 'success']
    if not runs:
        raise P.PatInputMissing(f'{broker}: no successful live run')
    run = max(runs, key=lambda r: r['started_at'])
    daily = reader.table('sb_daily_revenue', run_id=run['run_id'])
    facts = [f for f in reader.table('sb_disclosure_facts', broker_id=broker) if f['status'] == 'reviewed']
    assumptions = [a for b in ('*', broker) for a in reader.table('sb_assumptions', broker_id=b) if a['key'].startswith('pat_')]
    prices = sorted(reader.table('sb_share_prices', broker_id=broker), key=lambda r: r['trade_date'])
    if not prices:
        raise P.PatInputMissing(f'{broker}: no share prices')
    # prefer the filed consolidated P&L lines over older rows of the same metric (e.g. Angel's workbook-seeded pl_*)
    pl = {(f['period_key'], f['metric']) for f in facts if f['metric'].startswith('pl_') and f.get('segment') == 'consolidated'}
    facts = [f for f in facts if not (f['metric'].startswith('pl_') and f.get('segment') != 'consolidated'
                                      and (f['period_key'], f['metric']) in pl)]
    shares = [f for f in facts if f['metric'] == 'shares_outstanding_cr']
    if not shares:
        raise P.PatInputMissing(f'{broker}: shares outstanding not reviewed')
    return run, daily, facts, assumptions, prices[-1], max(shares, key=lambda f: f['period_key'])['value']


def db_run(brokers, publish):
    from src.live.db import SupabaseReader, SupabaseWriter
    reader = SupabaseReader()
    writer = SupabaseWriter() if publish else None
    failed = []
    for b in brokers:
        try:
            run, daily, facts, assumptions, px, shares = db_inputs(reader, b)
            m = P.build(b, facts, daily, assumptions, dict(price=float(px['close']), date=px['trade_date']), float(shares))
        except P.PatInputMissing as e:
            print(f'::warning title=PAT {b} skipped::{e}')
            failed.append(b)
            continue
        out = f"out/pat/{m['as_of']}"
        os.makedirs(out, exist_ok=True)
        rows = P.rows(m, run['run_id'])
        open(f'{out}/{b}_report.md', 'w').write(report(m, run['run_id']))
        if writer:
            writer.upsert('sb_pat_lines', rows, on_conflict=('run_id', 'period_key', 'line', 'scenario'))
            print(f"{b}: {len(rows)} sb_pat_lines rows for run {run['run_id'][:8]}")
        else:
            print(f"{b}: dry run, {len(rows)} rows (nothing written)")
    if failed and len(failed) == len(brokers):
        raise SystemExit(f'PAT model skipped for every broker: {failed}')


def preview(brokers, out):
    """out/pat/preview/index.html: the reports as one local page (serve with: python3 -m http.server 8792 -d out/pat/preview)."""
    import html
    import re

    def inline(t):
        t = html.escape(t)
        return re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', re.sub(r'`([^`]+)`', r'<code>\1</code>', t))

    def md(s):
        res, tbl = [], []

        def flush():
            if tbl:
                rows = [r.strip().strip('|').split('|') for r in tbl if not re.match(r'^\|[-:| ]+\|$', r.strip())]
                head = ''.join(f'<th>{inline(c.strip())}</th>' for c in rows[0])
                body = ''.join('<tr>' + ''.join(f'<td>{inline(c.strip())}</td>' for c in r) + '</tr>' for r in rows[1:])
                res.append(f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>')
                tbl.clear()
        for line in s.splitlines():
            if line.startswith('|'):
                tbl.append(line)
                continue
            flush()
            if line.startswith('## '):
                res.append(f'<h2>{inline(line[3:])}</h2>')
            elif line.startswith('# '):
                res.append(f'<h1>{inline(line[2:])}</h1>')
            elif line.startswith('- '):
                res.append(f'<li>{inline(line[2:])}</li>')
            elif line.strip():
                res.append(f'<p>{inline(line)}</p>')
        flush()
        return '\n'.join(res)
    css = ("body{font-family:-apple-system,Helvetica,Arial,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;color:#16181D}"
           "h1{font-size:20px;border-bottom:2px solid #16181D;padding-bottom:6px}h2{font-size:15px;margin-top:28px;text-transform:uppercase}"
           "table{border-collapse:collapse;font-size:13px;margin:8px 0}th,td{border-bottom:1px solid #e3e3df;padding:5px 10px;text-align:right}"
           "th:first-child,td:first-child{text-align:left}th{background:#f4f4f1}li{font-size:12.5px;color:#3B3E46}"
           "code{font-size:12px;background:#f1f1ee;padding:1px 4px}nav a{margin-right:16px;font-weight:600}.note{font-size:12px;color:#62656D}")
    names = {'ANGELONE': 'Angel One', 'GROWW': 'Groww'}
    secs = [f'<section id="{b}">{md(open(f"{out}/{b}_report.md").read())}</section>' for b in brokers]
    nav = ''.join(f'<a href="#{b}">{names[b]}</a>' for b in brokers)
    os.makedirs('out/pat/preview', exist_ok=True)
    open('out/pat/preview/index.html', 'w').write(
        f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>PAT model preview (dry run)</title><style>{css}</style></head>'
        f'<body><nav>{nav}</nav><p class="note">Local preview of the PAT model dry run (branch feat/pat-model, nothing published). '
        f'A = filed quarter, E = estimate. Rs Cr unless stated.</p>{"<hr>".join(secs)}</body></html>')


def report(m, run_id):
    b, f27, f28 = m['broker'], m['fy27'], m['fy28']
    cols = list(P.FY27_Q) + ['FY 2027', 'FY 2028']
    per = {**m['quarters'], 'FY 2027': f27, 'FY 2028': f28}
    L = [f"# PAT model — {b} (dry run) · ADR run {run_id[:8]} as of {m['as_of']}", '',
         f"Shares {m['shares_cr']:.2f} Cr · close ₹{m['close']['price']} ({m['close']['date']}) · "
         + (f"fees ÷ broking {m['ratios']['fees_to_broking']:.2%}" if m['ratios']['fees_to_broking']
            else f"other exp ÷ broking {m['ratios']['other_exp_to_broking']:.2%}")
         + f" (quarters {', '.join(m['ratios']['last4'])})", '',
         '| Rs Cr | ' + ' | '.join(c.replace(' FY 20', ' FY') + (' A' if per[c]['regime'] == 'actual' else ' E') for c in cols) + ' |',
         '|---|' + '---:|' * len(cols)]
    for line in ('trading_days',) + P.REVENUE_LINES[b] + ('total_income',) + P.COST_LINES[b] + ('total_costs', 'pbt', 'tax', 'pat', 'mtf_book'):
        L.append(f'| {P.LABELS[line]} | ' + ' | '.join('' if per[c].get(line) is None else f'{per[c][line]:,.1f}' for c in cols) + ' |')
    L += ['', '## Valuation', '', '| | Bear | Base | Bull |', '|---|---:|---:|---:|']
    for pk in ('FY 2027', 'FY 2028'):
        for k in ('eps', 'pe', 'price_fwd', 'price_disc', 'target_today', 'upside'):
            if pk == 'FY 2027' and k == 'target_today':
                continue
            v = [m['valuation'][(pk, s)][k] for s in P.SCENARIOS]
            fmt = (lambda x: f'{x:+.1%}') if k == 'upside' else (lambda x: f'{x:,.2f}')
            L.append(f'| {pk} {P.LABELS[k]} | ' + ' | '.join(fmt(x) for x in v) + ' |')
    L += ['', '## Against the workbook', '', '| | Workbook | Model | Change |', '|---|---:|---:|---:|']
    mine = {'FY27 PAT': f27['pat'], 'FY28 PAT': f28['pat'], 'FY28 target today (base)': m['valuation'][('FY 2028', 'base')]['target_today']}
    for k, (v, cell) in SHEET[b].items():
        L.append(f'| {k} (`{cell}`) | {v:,.2f} | {mine[k]:,.2f} | {mine[k] / v - 1:+.1%} |')
    L += ['', '## Rules (projected periods)', '']
    for (pk, line), r in sorted(m['rules'].items()):
        if r != 'filed':
            L.append(f'- {pk} · {P.LABELS[line]}: {r}')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    main()
