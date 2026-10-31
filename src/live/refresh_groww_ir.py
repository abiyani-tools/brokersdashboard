"""Daily archive of Groww's investor-relations home page into sb_broker_daily.

    python3 -m src.live.refresh_groww_ir                     # dry run: fetch, parse, show the rows, write nothing
    python3 -m src.live.refresh_groww_ir --write             # upsert into sb_broker_daily (needs SUPABASE_SERVICE_KEY)
    python3 -m src.live.refresh_groww_ir --html FILE         # parse a saved page instead of fetching (dry run / fixture)
    python3 -m src.live.refresh_groww_ir --fixture PATH      # also write the parsed rows as an engine fixture

Why: https://groww.in/investor-relations embeds seven charts in <script id="__NEXT_DATA__"> (props.pageProps.
initialChartConfigs): users, customer assets (total, MF, stocks), MF SIP inflows, stocks turnover, equity-derivatives
premium turnover, commodity-derivatives notional turnover and MTF net book. Each has the closed quarters and, as its last
point, the current quarter-to-date. The page keeps no daily history, so each day's capture is the only record.

Units. The page's chart values are in its own unit: value / 100 = Rs Mn. That is checked on every run against the page's
own printed "Rs Mn" string for the latest point (currentValue) and against rawCurrentValue, and the run fails if either
disagrees. (It was described as Rs '000; that reading is off by 10: the page's strings, the KPI Handbook ADTO x days and
exchange turnover all agree with / 100.) User counts are stored as printed.

Loud failures. A missing __NEXT_DATA__, a missing or renamed chart id or line, a label that is not 'Qn FYyy' or does not
follow the one before, a non-numeric value, a unit string that is not "Rs Mn", or charts that end on different quarters
raise PageChanged: the job fails and prints a GitHub error annotation. A blocked fetch (HTTP 403 etc.) does the same.
The raw HTML is saved first (--raw-dir, default out/groww_ir/; git-ignored, uploaded as a workflow artifact), so a failed
parse leaves the page to look at.

Which trading day the QTD point runs through is not on the page. After parsing, the run infers it from exchange turnover
(src.engine.groww_ir.infer_covered_through) and stores it in covers_through on the QTD rows when the inference is clear.
Exchange turnover is read from sb_market_daily when SUPABASE_SERVICE_KEY is set, else from the committed fixture.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import sys

from ..engine import groww_ir as IR

URL = 'https://groww.in/investor-relations'
USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/126.0 Safari/537.36')
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
PAGE_TO_MN = 0.01                      # page chart value x 0.01 = Rs Mn
MIN_POINTS = 5
DEFAULT_RAW_DIR = 'out/groww_ir'
DEFAULT_EXCHANGE = 'snapshot/groww_exchange_2026-10-31.json'
PK = ('broker_id', 'snapshot_date', 'metric', 'period_key')

# chart id -> {line key: (metric, kind, expected line name or None)}; kind 'money' (page unit) or 'count'
CHARTS = {
    'users': {'value': (IR.M_USERS, 'count', None)},
    'aum': {'value': (IR.M_ASSETS, 'money', 'Total Assets'), 'value2': (IR.M_ASSETS_MF, 'money', 'MF Assets'),
            'value3': (IR.M_ASSETS_STOCKS, 'money', 'Stocks Assets')},
    'mf_sip': {'value': (IR.M_SIP, 'money', None)},
    'stocks_turnover': {'value': (IR.M_STOCKS, 'money', None)},
    'equity_derivatives': {'value': (IR.M_DERIV, 'money', None)},
    'commodity_derivatives': {'value': (IR.M_COMM, 'money', None)},
    'mtf_net_book': {'value': (IR.M_MTF, 'money', None)},
}
UNIT = {'money': 'Rs Mn', 'count': 'count'}
_MN = re.compile(r'^₹\s*([\d,]+(?:\.\d+)?)\s*Mn$')


class PageChanged(RuntimeError):
    """The page no longer has the structure this parser was written against."""


class FetchFailed(RuntimeError):
    """groww.in could not be fetched (blocked, down, or an error status)."""


def _fail(msg):
    raise PageChanged(msg)


# ── fetch ──
def fetch(session=None, url=URL):
    """(html, fetched_at UTC). Raises FetchFailed on a network error or a non-200 answer."""
    if session is None:
        import requests
        session = requests.Session()
    try:
        resp = session.get(url, headers={'User-Agent': USER_AGENT, 'Accept': 'text/html,application/xhtml+xml',
                                         'Accept-Language': 'en-IN,en;q=0.9'}, timeout=60)
    except Exception as e:                                              # network level: DNS, TLS, timeout
        raise FetchFailed(f'GET {url} failed: {type(e).__name__}: {e}')
    fetched_at = dt.datetime.now(dt.timezone.utc)
    if resp.status_code != 200:
        raise FetchFailed(f'GET {url} returned HTTP {resp.status_code} (blocked or down?); body starts: '
                          f'{resp.text[:120]!r}')
    return resp.text, fetched_at


# ── parse ──
def extract_next_data(html):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        _fail('no <script id="__NEXT_DATA__"> in the page (a block page, or the site no longer uses Next.js)')
    try:
        return json.loads(m.group(1))
    except ValueError as e:
        _fail(f'__NEXT_DATA__ is not JSON: {e}')


def _chart_list(next_data):
    try:
        charts = next_data['props']['pageProps']['initialChartConfigs']
    except (KeyError, TypeError):
        _fail('props.pageProps.initialChartConfigs is missing')
    if not isinstance(charts, list) or not charts:
        _fail('initialChartConfigs is not a non-empty list')
    return charts


def _num(x, where):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0:
        _fail(f'{where}: not a non-negative number: {x!r}')
    return float(x)


def parse_charts(next_data):
    """{chart id: parsed} with the closed and QTD points, validated. Raises PageChanged.

    parsed = {'labels': [page labels], 'points': {line key: [value, ...]}, 'last_label', 'unit_check': ...}"""
    charts = _chart_list(next_data)
    by_id = {}
    for c in charts:
        if not isinstance(c, dict) or 'id' not in c:
            _fail(f'a chart without an id: {str(c)[:100]}')
        by_id[c['id']] = c
    missing = sorted(set(CHARTS) - set(by_id))
    if missing:
        _fail(f'chart id(s) missing: {missing}; the page has {sorted(by_id)}')
    out = {}
    for cid, lines in CHARTS.items():
        c = by_id[cid]
        data = c.get('data')
        if not isinstance(data, list) or len(data) < MIN_POINTS:
            _fail(f'{cid}: data has {len(data) if isinstance(data, list) else "no"} points (expected >= {MIN_POINTS})')
        labels, prev = [], None
        for i, p in enumerate(data):
            lab = IR.period_key(p.get('label') if isinstance(p, dict) else None) if _label_ok(p) else \
                _fail(f'{cid}: point {i} has no valid label: {str(p)[:80]}')
            if prev is not None and lab != IR.next_quarter(prev):
                _fail(f'{cid}: labels not consecutive: {prev} then {lab}')
            labels.append(lab)
            prev = lab
        if cid == 'aum':
            names = {ln.get('dataKey'): ln.get('name') for ln in c.get('lines', []) if isinstance(ln, dict)}
            for key, (_, _, want) in lines.items():
                if names.get(key) != want:
                    _fail(f'{cid}: line {key} is named {names.get(key)!r}, expected {want!r}')
        points = {}
        for key, (metric, kind, _) in lines.items():
            points[key] = []
            for i, p in enumerate(data):
                if key not in p:
                    _fail(f'{cid}: point {labels[i]} has no {key}')
                points[key].append(_num(p[key], f'{cid} {labels[i]} {key}'))
        out[cid] = {'labels': labels, 'points': points}
    last = {cid: v['labels'][-1] for cid, v in out.items()}
    if len(set(last.values())) != 1:
        _fail(f'charts end on different quarters: {last}')
    for cid, lines in CHARTS.items():
        _check_unit(cid, by_id[cid], lines, out[cid]['points'])
    return out


def _label_ok(p):
    return isinstance(p, dict) and isinstance(p.get('label'), str) and re.match(r'^Q[1-4] FY\d{2}$', p['label'])


def _check_unit(cid, chart, lines, points):
    """The unit guard: the latest point against the page's own printed string and rawCurrentValue."""
    raw = chart.get('rawCurrentValue')
    cur = chart.get('currentValue')
    for key, (metric, kind, _) in lines.items():
        if key != 'value':
            continue
        v = points[key][-1]
        if kind == 'count':
            if not isinstance(raw, (int, float)) or raw != v or str(cur).replace(',', '') != str(int(v)):
                _fail(f'{cid}: user count {v} does not match rawCurrentValue {raw!r} / currentValue {cur!r}')
        else:
            m = _MN.match(str(cur or ''))
            if not m:
                _fail(f'{cid}: currentValue {cur!r} is not "₹<n> Mn" (the page changed its unit or format)')
            printed = float(m.group(1).replace(',', ''))
            if abs(v * PAGE_TO_MN - printed) > max(1.0, 1e-6 * printed):
                _fail(f'{cid}: latest value {v} x {PAGE_TO_MN} = {v * PAGE_TO_MN:,.1f} Rs Mn, but the page prints '
                      f'{printed:,.0f} Mn: the chart unit changed')
            if not isinstance(raw, (int, float)) or abs(raw - v * 1e6) > max(1.0, 1e-6 * raw):
                _fail(f'{cid}: rawCurrentValue {raw!r} is not the chart value x 1e6 ({v * 1e6:,.0f})')


def build_rows(parsed, fetched_at, snapshot_date, html_sha, broker=IR.BROKER):
    """sb_broker_daily rows (covers_through None; set on the QTD rows by add_covers_through)."""
    last_q = next(iter(parsed.values()))['labels'][-1]
    q_end = IR.quarter_bounds(last_q)[1]
    is_open = q_end >= snapshot_date                  # the last point is quarter-to-date while the quarter runs
    rows = []
    for cid, lines in CHARTS.items():
        labels = parsed[cid]['labels']
        for key, (metric, kind, _) in lines.items():
            for i, lab in enumerate(labels):
                v = parsed[cid]['points'][key][i]
                rows.append(dict(
                    broker_id=broker, fetched_at=fetched_at.isoformat(timespec='seconds'),
                    snapshot_date=snapshot_date, metric=metric, period_key=lab,
                    value=round(v * PAGE_TO_MN, 6) if kind == 'money' else v, unit=UNIT[kind],
                    is_qtd=bool(is_open and i == len(labels) - 1), source=IR.SOURCE, covers_through=None,
                    source_ref=f'{URL}@sha256:{html_sha[:12]}#initialChartConfigs[id={cid}].data'
                               f'[label={lab}].{key}'))
    return rows


def check_period_plausible(rows, snapshot_date):
    """The page's last quarter must be the one the fetch day is in, or the one just before (not rolled yet)."""
    last = max((r['period_key'] for r in rows), key=lambda q: (IR._split(q)[1], IR._split(q)[0]))
    cur = IR.quarter_of(snapshot_date)
    if last not in (cur, IR.prev_quarter(cur)):
        _fail(f'the latest quarter on the page is {last}; a fetch on {snapshot_date} ({cur}) should show {cur} '
              f'(or {IR.prev_quarter(cur)} just after a quarter end)')


def parse_page(html, fetched_at):
    """(rows, meta) for a page fetched at `fetched_at` (UTC datetime). Raises PageChanged."""
    sha = hashlib.sha256(html.encode('utf-8')).hexdigest()
    parsed = parse_charts(extract_next_data(html))
    snapshot_date = fetched_at.astimezone(IST).date().isoformat()
    rows = build_rows(parsed, fetched_at, snapshot_date, sha)
    check_period_plausible(rows, snapshot_date)
    extra = sorted({c.get('id') for c in _chart_list(extract_next_data(html))} - set(CHARTS))
    return rows, {'snapshot_date': snapshot_date, 'fetched_at': fetched_at.isoformat(timespec='seconds'),
                  'sha256': sha, 'extra_chart_ids': extra}


# ── trading day covered by the QTD point ──
def load_turnover(source):
    """Turnover from 'db' (sb_market_daily, service key), or a fixture path."""
    if source == 'db':
        from .db import SupabaseReader
        return IR.Turnover.from_market_rows(SupabaseReader().table('sb_market_daily'))
    return IR.Turnover.from_fixture(source)


def add_covers_through(rows, turnover):
    """(inference or None, note). Sets covers_through on the QTD rows when the inference is confident."""
    ir = IR.IR(rows)
    if ir.qtd_period is None:
        return None, 'the page shows closed quarters only: no quarter-to-date point'
    try:
        inf = IR.infer_covered_through(ir, turnover)
    except IR.IRError as e:
        return None, f'covers_through not inferred: {e}'
    if not inf['confident']:
        return inf, (f'covers_through NOT stored: best cut-off {inf["day"]} is not clear (cost {inf["cost"]:.3f}, '
                     f'margin {inf["margin"]:.3f})')
    for r in rows:
        if r['is_qtd']:
            r['covers_through'] = inf['day']
    return inf, f'covers_through {inf["day"]} stored on the {sum(1 for r in rows if r["is_qtd"])} QTD rows'


# ── report ──
def report(rows, meta, inf, note):
    lines = [f'{URL}  fetched {meta["fetched_at"]} (IST date {meta["snapshot_date"]}), sha256 {meta["sha256"][:12]}',
             f'{len(rows)} rows: {len({r["metric"] for r in rows})} metrics, '
             f'{len({r["period_key"] for r in rows})} quarters, {sum(r["is_qtd"] for r in rows)} quarter-to-date']
    if meta['extra_chart_ids']:
        lines.append(f'note: charts on the page that are not archived: {meta["extra_chart_ids"]}')
    qtd = {r['metric']: r for r in rows if r['is_qtd']}
    for m in IR.ALL_METRICS:
        closed = [r for r in rows if r['metric'] == m and not r['is_qtd']]
        last = closed[-1] if closed else None
        q = qtd.get(m)
        lines.append(f'  {m:32} {len([r for r in rows if r["metric"] == m]):3} pts  '
                     + (f'last closed {last["period_key"]} {last["value"]:,.1f} {last["unit"]}' if last else '')
                     + (f'   QTD {q["period_key"]} {q["value"]:,.1f}' if q else ''))
    if inf:
        lines.append(f'QTD runs through: {inf["day"]}  (cost {inf["cost"]:.4f}, margin to next best '
                     f'{inf["margin"]:.4f}, {"confident" if inf["confident"] else "NOT confident"}; prior quarter '
                     f'{inf["prior"]} shares: cash {inf["prior_shares"]["cash"]:.4f}, F&O {inf["prior_shares"]["fo"]:.4f})')
        near = sorted(inf['candidates'], key=lambda t: t[3])[:3]
        for d, sc, sf, cost in near:
            lines.append(f'    cut-off {d}: cash share {sc:.4f}, F&O share {sf:.4f}, cost {cost:.4f}')
    lines.append(note)
    return '\n'.join(lines)


def _annotate(level, title, text):
    if os.environ.get('GITHUB_ACTIONS'):
        print(f'::{level} title={title}::{text.replace(chr(10), " ")}')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--write', action='store_true', help='upsert into sb_broker_daily (default: dry run)')
    ap.add_argument('--html', help='parse this saved page instead of fetching')
    ap.add_argument('--fetched-at', help='ISO time of the capture of --html (default: the file modification time)')
    ap.add_argument('--raw-dir', default=DEFAULT_RAW_DIR, help='where the raw HTML is saved (not committed)')
    ap.add_argument('--exchange', default='auto', help="exchange turnover: 'db', a fixture path, or auto (db if "
                    "SUPABASE_SERVICE_KEY is set, else " + DEFAULT_EXCHANGE + ')')
    ap.add_argument('--fixture', help='also write the parsed rows (with covers_through) as an engine fixture JSON')
    args = ap.parse_args(sys.argv[1:] if argv is None else argv)

    try:
        if args.html:
            html = open(args.html, encoding='utf-8').read()
            fetched_at = (dt.datetime.fromisoformat(args.fetched_at.replace('Z', '+00:00')) if args.fetched_at else
                          dt.datetime.fromtimestamp(os.path.getmtime(args.html), dt.timezone.utc))
            if fetched_at.tzinfo is None:
                fetched_at = fetched_at.replace(tzinfo=dt.timezone.utc)
        else:
            html, fetched_at = fetch()
    except FetchFailed as e:
        print(f'FETCH FAILED: {e}')
        _annotate('error', 'groww.in not fetched', str(e))
        return 1
    os.makedirs(args.raw_dir, exist_ok=True)                            # raw page first: evidence if parsing fails
    raw_path = os.path.join(args.raw_dir, f'investor-relations_{fetched_at.astimezone(IST).date().isoformat()}.html')
    with open(raw_path, 'w', encoding='utf-8') as fh:
        fh.write(html)
    try:
        rows, meta = parse_page(html, fetched_at)
    except PageChanged as e:
        print(f'PAGE STRUCTURE CHANGED: {e}\n(raw page saved to {raw_path})')
        _annotate('error', 'groww.in page structure changed', str(e))
        return 1

    source = args.exchange
    if source == 'auto':
        source = 'db' if os.environ.get('SUPABASE_SERVICE_KEY') else DEFAULT_EXCHANGE
    try:
        inf, note = add_covers_through(rows, load_turnover(source))
        note += f' (exchange turnover from {source})'
    except Exception as e:                                               # the archive must not depend on this
        inf, note = None, f'covers_through not inferred ({source}): {type(e).__name__}: {e}'
    print(report(rows, meta, inf, note))
    print(f'raw page: {raw_path}')
    if inf is None or not inf['confident']:
        _annotate('warning', 'Groww IR: covers_through not stored', note)
    if args.fixture:
        with open(args.fixture, 'w') as fh:
            json.dump({'_about': (f'Groww IR archive rows of one capture ({meta["fetched_at"]}, IST date '
                                  f'{meta["snapshot_date"]}), exactly as src/live/refresh_groww_ir.py would write them '
                                  'to sb_broker_daily. Money in Rs Mn. Built from the saved page '
                                  f'(sha256 {meta["sha256"][:12]}); covers_through inferred from exchange turnover.'),
                       'snapshot_date': meta['snapshot_date'], 'fetched_at': meta['fetched_at'],
                       'html_sha256': meta['sha256'], 'rows': rows}, fh, indent=1)
            fh.write('\n')
        print(f'fixture written: {args.fixture}')
    if not args.write:
        print('dry run: nothing written (pass --write to upsert into sb_broker_daily)')
        return 0
    from .db import SupabaseWriter
    n = SupabaseWriter().upsert('sb_broker_daily', rows, PK)
    print(f'upserted {n} rows into sb_broker_daily')
    return 0


if __name__ == '__main__':
    sys.exit(main())
