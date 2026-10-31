"""Groww investor-relations (IR) data for the live switches g-h and g-i, and the helper that pins a quarter-to-date
(QTD) point to the trading day it runs through.

Source: the IR home page (src/live/refresh_groww_ir.py archives it daily into sb_broker_daily). This module only
reads the archived rows (fixture snapshot/groww_ir_*.json, or the table) and the exchange turnover series; it never
fetches anything.

Units. Money is Rs Mn in the archive (the page prints its own unit: page value / 100 = Rs Mn, checked against the
page's own "Rs Mn" strings, the KPI Handbook ADTO x days and exchange turnover). Exchange turnover is Rs Cr
(sb_market_daily), so shares are computed with both sides in Rs Cr (Rs Mn / 10).

Turnover shares (the definition g-h uses):
    cash share        = Groww stocks turnover  /  (NSE cash_traded_value + BSE cash_traded_value)
    F&O share         = Groww equity-derivatives premium turnover
                        /  (NSE index-option premium + NSE stock-option premium + BSE options_premium_turnover)
Both over the same days. In sb_market_daily: nse_cash/turnover_cr, bse_cash/turnover_cr, nse_fo/io_premium_cr,
nse_fo/so_premium_cr, bse_fo/opt_premium_cr (source 'exchangesdash_json').
"""
import datetime as dt
import json
import math
import re
from collections import defaultdict

BROKER = 'GROWW'
SOURCE = 'groww_ir_site'

# metric names in sb_broker_daily
M_USERS = 'ir_users'
M_ASSETS, M_ASSETS_MF, M_ASSETS_STOCKS = 'ir_customer_assets', 'ir_customer_assets_mf', 'ir_customer_assets_stocks'
M_SIP = 'ir_mf_sip'
M_STOCKS, M_DERIV, M_COMM = 'ir_stocks_turnover', 'ir_equity_derivs_premium', 'ir_commodity_derivs_notional'
M_MTF = 'ir_mtf_net_book'
ALL_METRICS = (M_USERS, M_ASSETS, M_ASSETS_MF, M_ASSETS_STOCKS, M_SIP, M_STOCKS, M_DERIV, M_COMM, M_MTF)

SEGMENT_METRIC = {'cash': (M_STOCKS, 'cash'), 'fo': (M_DERIV, 'deriv')}   # segment -> (IR metric, exchange series)

_Q = re.compile(r'^Q([1-4]) FY (\d{4})$')


class IRError(ValueError):
    """The IR data (or the exchange series next to it) cannot support what was asked: an explicit 'insufficient data'."""


# ── quarters ──
def period_key(label):
    """The page's 'Q3 FY27' -> the repo's 'Q3 FY 2027'."""
    m = re.match(r'^Q([1-4]) FY(\d{2})$', label or '')
    if not m:
        raise IRError(f'unexpected quarter label {label!r} (expected like "Q3 FY27")')
    return f'Q{m.group(1)} FY {2000 + int(m.group(2))}'


def _split(q):
    m = _Q.match(q)
    if not m:
        raise IRError(f'not a quarter key: {q!r}')
    return int(m.group(1)), int(m.group(2))


def quarter_bounds(q):
    """(first day, last day) of an Indian-FY quarter, ISO strings. Q1 = Apr-Jun of the FY's first calendar year."""
    n, fy = _split(q)
    year = fy - 1 if n <= 3 else fy
    month = {1: 4, 2: 7, 3: 10, 4: 1}[n]
    start = dt.date(year, month, 1)
    nxt = dt.date(year + (month + 3 > 12), (month + 3 - 1) % 12 + 1, 1)
    return start.isoformat(), (nxt - dt.timedelta(days=1)).isoformat()


def next_quarter(q):
    n, fy = _split(q)
    return f'Q{n + 1} FY {fy}' if n < 4 else f'Q1 FY {fy + 1}'


def prev_quarter(q):
    n, fy = _split(q)
    return f'Q{n - 1} FY {fy}' if n > 1 else f'Q4 FY {fy - 1}'


def quarter_of(d):
    d = dt.date.fromisoformat(d) if isinstance(d, str) else d
    n = (d.month - 4) // 3 + 1 if d.month >= 4 else 4
    return f'Q{n} FY {d.year + 1 if d.month >= 4 else d.year}'


# ── exchange turnover (Rs Cr) ──
TURNOVER_KEYS = {('nse_cash', 'turnover_cr'): 'nse_cash', ('bse_cash', 'turnover_cr'): 'bse_cash',
                 ('nse_fo', 'io_premium_cr'): 'nse_io', ('nse_fo', 'so_premium_cr'): 'nse_so',
                 ('bse_fo', 'opt_premium_cr'): 'bse_opt'}
COMPONENTS = ('nse_cash', 'bse_cash', 'nse_io', 'nse_so', 'bse_opt')
SOURCE_PREF = ('exchangesdash_json', 'exchangesdash_json@b2049b5', 'excel_seed')   # the daily refresh first


class Turnover:
    """Daily NSE + BSE cash turnover and option-premium turnover, Rs Cr.

    days: {date: {component: value}} with the five COMPONENTS. A day missing a component is kept out of `days` and
    listed in `incomplete`; asking for a total that spans an incomplete day raises (no silent drop)."""

    def __init__(self, parts):
        self.days, self.incomplete = {}, set()
        for d, p in parts.items():
            if all(p.get(c) is not None for c in COMPONENTS):
                self.days[d] = {c: float(p[c]) for c in COMPONENTS}
            else:
                self.incomplete.add(d)
        if not self.days:
            raise IRError('no exchange turnover days')
        self.dates = sorted(self.days)

    @classmethod
    def from_market_rows(cls, rows):
        """sb_market_daily rows (dataset, metric, trade_date, value, source, status). Per day and series the first
        source of SOURCE_PREF that has an 'ok' row wins."""
        best = {}
        for r in rows:
            comp = TURNOVER_KEYS.get((r['dataset'], r['metric']))
            if comp is None or r.get('status', 'ok') != 'ok' or r.get('value') is None:
                continue
            src = r.get('source', '')
            rank = SOURCE_PREF.index(src) if src in SOURCE_PREF else len(SOURCE_PREF)
            k = (str(r['trade_date'])[:10], comp)
            if k not in best or rank < best[k][0]:
                best[k] = (rank, float(r['value']))
        parts = defaultdict(dict)
        for (d, comp), (_, v) in best.items():
            parts[d][comp] = v
        return cls(parts)

    @classmethod
    def from_fixture(cls, obj):
        if isinstance(obj, str):
            obj = json.load(open(obj))
        return cls({r['trade_date']: {c: r.get(c) for c in COMPONENTS} for r in obj['rows']})

    def to_fixture(self, about):
        return {'_about': about, 'unit': 'Rs Cr',
                'rows': [dict(trade_date=d, **self.days[d]) for d in self.dates]}

    def _sum(self, kind, a, b):
        bad = sorted(d for d in self.incomplete if a <= d <= b)
        if bad:
            raise IRError(f'exchange turnover incomplete on {bad[:5]} (a series is missing); cannot total {a}..{b}')
        ds = [d for d in self.dates if a <= d <= b]
        if not ds:
            raise IRError(f'no exchange turnover between {a} and {b} (data covers {self.dates[0]}..{self.dates[-1]})')
        keys = ('nse_cash', 'bse_cash') if kind == 'cash' else ('nse_io', 'nse_so', 'bse_opt')
        return sum(self.days[d][k] for d in ds for k in keys), len(ds)

    def total(self, kind, a, b, complete_to=None):
        """(Rs Cr, days) over a..b. complete_to: the last day the data must reach (a closed quarter's end, give or
        take a weekend and a holiday); raises if the series ends before."""
        if complete_to is not None:
            end = dt.date.fromisoformat(complete_to) - dt.timedelta(days=5)
            if self.dates[-1] < end.isoformat():
                raise IRError(f'exchange turnover ends {self.dates[-1]}, before {complete_to}: {a}..{b} is not covered')
        return self._sum(kind, a, b)


# ── the archived IR rows ──
class IR:
    """Archived IR rows (sb_broker_daily shape). The latest snapshot gives every quarter's value and the QTD point;
    the QTD rows of every snapshot give the book archive (g-i).

    rows: dicts with broker_id, snapshot_date, metric, period_key, value (Rs Mn or count), unit, is_qtd and,
    optionally, covers_through and fetched_at."""

    def __init__(self, rows):
        rows = [dict(r, snapshot_date=str(r['snapshot_date'])[:10],
                     covers_through=(str(r['covers_through'])[:10] if r.get('covers_through') else None))
                for r in rows]
        if not rows:
            raise IRError('no archived IR rows')
        for r in rows:
            if r['broker_id'] != BROKER:
                raise IRError(f'not a Groww IR row: {r["broker_id"]} {r["metric"]}')
        self.rows = rows
        self.snapshot_date = max(r['snapshot_date'] for r in rows)
        self._latest = {}
        for r in rows:
            if r['snapshot_date'] == self.snapshot_date:
                k = (r['metric'], r['period_key'])
                if k in self._latest:
                    raise IRError(f'duplicate IR row {k} on {self.snapshot_date}')
                self._latest[k] = r
        for m in (M_STOCKS, M_DERIV, M_MTF):
            if not any(k[0] == m for k in self._latest):
                raise IRError(f'archived IR snapshot {self.snapshot_date} has no {m}')
        qtd = {r['period_key'] for r in self._latest.values() if r['is_qtd']}
        if len(qtd) > 1:
            raise IRError(f'snapshot {self.snapshot_date}: several quarters flagged quarter-to-date: {sorted(qtd)}')
        self.qtd_period = next(iter(qtd)) if qtd else None
        cov = {r['covers_through'] for r in self._latest.values() if r['is_qtd'] and r['covers_through']}
        if len(cov) > 1:
            raise IRError(f'snapshot {self.snapshot_date}: different covers_through dates {sorted(cov)}')
        self.covers_through = next(iter(cov)) if cov else None
        self.fetched_at = next((r.get('fetched_at') for r in self._latest.values() if r.get('fetched_at')), None)

    def has(self, metric, period):
        return (metric, period) in self._latest

    def value(self, metric, period):
        """The latest snapshot's value (Rs Mn, or a count), whether the quarter is closed or QTD."""
        r = self._latest.get((metric, period))
        if r is None:
            raise IRError(f'IR snapshot {self.snapshot_date}: no {metric} for {period}')
        return float(r['value'])

    # MTF net book, Rs Cr ---------------------------------------------------------------
    def book_levels_cr(self):
        """{quarter: Rs Cr}: quarter-end levels of the closed quarters (latest snapshot)."""
        return {k[1]: float(r['value']) / 10.0 for k, r in self._latest.items() if k[0] == M_MTF and not r['is_qtd']}

    def book_latest(self):
        """(quarter, Rs Cr): the QTD point, i.e. the latest level of the open quarter; None if the page's last
        quarter is already closed."""
        for k, r in self._latest.items():
            if k[0] == M_MTF and r['is_qtd']:
                return k[1], float(r['value']) / 10.0
        return None

    def book_archive_cr(self):
        """{day: Rs Cr}: every archived QTD level, keyed by the trading day it runs through (covers_through, else the
        snapshot date). Several snapshots on one day: the latest one."""
        out = {}
        for r in sorted((r for r in self.rows if r['metric'] == M_MTF and r['is_qtd']),
                        key=lambda r: (r['snapshot_date'], r.get('fetched_at') or '')):
            out[r['covers_through'] or r['snapshot_date']] = float(r['value']) / 10.0
        return out


# ── which trading day does the QTD point run through? ──
CONFIDENT_COST, CONFIDENT_MARGIN = 0.10, 0.02


def infer_covered_through(ir, turnover, on_or_before=None):
    """The last trading day Groww's QTD point includes, inferred (the page does not say).

    Method. Groww's turnover share of NSE+BSE exchange turnover moves slowly from quarter to quarter, while the QTD
    numerator is fixed. Cut the exchange series at each candidate trading day d (quarter start .. min(fetch day, last
    exchange day)): share(d) = Groww QTD turnover / exchange turnover over [quarter start, d]. share(d) falls as d
    advances, and only one cut-off makes it match the prior quarter's share on both series:
        cost(d) = |ln(cash share(d) / cash share, prior quarter)| + |ln(F&O share(d) / F&O share, prior quarter)|
    The inferred day is the argmin. `confident` needs cost <= 0.10 and the runner-up at least 0.02 worse; otherwise the
    caller must not use the date.

    Returns {'day', 'cost', 'margin', 'confident', 'prior_shares', 'candidates': [(day, cash share, F&O share, cost)]}.
    """
    q = ir.qtd_period
    if q is None:
        raise IRError('the IR snapshot has no quarter-to-date point')
    prior = prev_quarter(q)
    p_start, p_end = quarter_bounds(prior)
    base = {}
    for seg, (metric, kind) in SEGMENT_METRIC.items():
        tot, _ = turnover.total(kind, p_start, p_end, complete_to=p_end)
        base[seg] = ir.value(metric, prior) / 10.0 / tot
    start, _ = quarter_bounds(q)
    limit = min(on_or_before or ir.snapshot_date, turnover.dates[-1])
    cands = [d for d in turnover.dates if start <= d <= limit]
    if not cands:
        raise IRError(f'no exchange turnover day in {q} up to {limit}')
    num = {seg: ir.value(metric, q) / 10.0 for seg, (metric, _) in SEGMENT_METRIC.items()}
    table = []
    for d in cands:
        sh = {seg: num[seg] / turnover.total(kind, start, d)[0] for seg, (_, kind) in SEGMENT_METRIC.items()}
        cost = sum(abs(math.log(sh[s] / base[s])) for s in sh)
        table.append((d, sh['cash'], sh['fo'], cost))
    ranked = sorted(table, key=lambda t: t[3])
    best = ranked[0]
    margin = ranked[1][3] - best[3] if len(ranked) > 1 else float('inf')
    return {'day': best[0], 'cost': best[3], 'margin': margin,
            'confident': best[3] <= CONFIDENT_COST and margin >= CONFIDENT_MARGIN,
            'prior': prior, 'prior_shares': base, 'candidates': table}


def resolve_covered_through(ir, turnover):
    """The stored covers_through if the archive has it, else the inferred day (raises if the inference is not
    confident: no QTD-based estimate rather than a guessed day)."""
    if ir.covers_through:
        return ir.covers_through, 'stored'
    inf = infer_covered_through(ir, turnover)
    if not inf['confident']:
        raise IRError(f'cannot pin the {ir.qtd_period} QTD point to a trading day: best cut-off {inf["day"]} has '
                      f'cost {inf["cost"]:.3f}, margin {inf["margin"]:.3f} (needs <= {CONFIDENT_COST}, >= '
                      f'{CONFIDENT_MARGIN})')
    return inf['day'], 'inferred'


# ── g-h: the QTD turnover-share ratio ──
def qtd_share_ratio(ir, turnover, segment, q, last_reported):
    """The g-h multiplier for quarter q (an unreported quarter) and segment ('cash' | 'fo'), with its arithmetic:

        ratio = (Groww turnover / exchange turnover over q's days so far)
              / (Groww turnover / exchange turnover over last_reported's days)

    q's days: quarter start .. the day the QTD point runs through (the QTD quarter), or the whole quarter (a closed
    quarter the page already shows). None if the IR snapshot has no value for q."""
    metric, kind = SEGMENT_METRIC[segment]
    if not ir.has(metric, q):
        return None
    ls, le = quarter_bounds(last_reported)
    t_last, n_last = turnover.total(kind, ls, le, complete_to=le)
    s_last = ir.value(metric, last_reported) / 10.0 / t_last
    qs, qe = quarter_bounds(q)
    if q == ir.qtd_period:
        end, how = resolve_covered_through(ir, turnover)
        if end > turnover.dates[-1]:
            raise IRError(f'covers_through {end} is after the exchange series ({turnover.dates[-1]})')
        t_q, n_q = turnover.total(kind, qs, end)
    else:
        end, how = qe, 'closed quarter'
        t_q, n_q = turnover.total(kind, qs, qe, complete_to=qe)
    s_q = ir.value(metric, q) / 10.0 / t_q
    return {'segment': segment, 'quarter': q, 'last_reported': last_reported, 'ratio': s_q / s_last,
            'share_q': s_q, 'share_last': s_last, 'groww_q_cr': ir.value(metric, q) / 10.0,
            'groww_last_cr': ir.value(metric, last_reported) / 10.0, 'exch_q_cr': t_q, 'exch_last_cr': t_last,
            'days_q': n_q, 'days_last': n_last, 'through': end, 'through_how': how}


# ── g-i: Groww's own MTF book, day by day ──
def own_book_path(ir, days):
    """{day: (Rs Cr, how)} for the given trading days, by the rule (first match):
      archived      the day has an archived QTD level (sb_broker_daily, keyed by the day it runs through);
      latest        the day is in the page's open (QTD) quarter: the latest level, held flat;
      interpolated  the day is in a closed quarter: linear in calendar days between the two quarter-end levels.
    Raises IRError if a quarter-end level the rule needs is missing."""
    levels = ir.book_levels_cr()
    archive = ir.book_archive_cr()
    latest = ir.book_latest()
    out = {}
    for d in days:
        if d in archive:
            out[d] = (archive[d], 'archived')
            continue
        q = quarter_of(d)
        if latest is not None and q == latest[0]:
            out[d] = (latest[1], 'latest')
            continue
        if q not in levels:
            raise IRError(f'MTF book: no quarter-end level for {q} (day {d}); the IR page has {sorted(levels)[:1]}..'
                          f'{sorted(levels)[-1:]}' + (f' and a QTD point for {latest[0]}' if latest else ''))
        p = prev_quarter(q)
        if p not in levels:
            raise IRError(f'MTF book: no quarter-end level for {p}, needed to interpolate {q} (day {d})')
        e0 = dt.date.fromisoformat(quarter_bounds(p)[1])
        e1 = dt.date.fromisoformat(quarter_bounds(q)[1])
        w = (dt.date.fromisoformat(d) - e0).days / (e1 - e0).days
        out[d] = (levels[p] + (levels[q] - levels[p]) * w, 'interpolated')
    return out
