"""E3 — the Summary for any selected FY / quarter / month (decision D1, LIVE_SPEC §3).

One rule makes every comparison label from the selection:
  FY      : FY, previous FY                                   → YoY
  quarter : quarter, previous quarter, same quarter last FY   → QoQ, YoY
  month   : month, previous month, same month last FY, 6M     → MoM, YoY, vs 6M
The workbook's layout is this rule at two fixed selections: (FY 2027, Q2 FY 2027, FY 2027 September) for every
panel, and (FY 2027, Q4 FY 2026, FY 2026 February) for Cash, whose labels are stale in the workbook.
The parity "6M" is the average of two quarterly ADRs (the month's quarter and the one before);
live "6M" is the average over the six calendar months ending at the selected month (decision Q2).

Week / weekday tables are anchored on the last date (as_of), not on a selection.

Guarded statistics (live) return Insufficient instead of the workbook's IFERROR 0: a period with no rows,
a period that starts before a segment's series does (partial history), or a window with too few dates.
summary.py (parity) is not changed.
"""
from statistics import mean

from .inputs import MONTHS, fy_month_of, fy_of, months_of_quarter, q_of, quarter_of_month
from .summary import WEEKDAYS, Seg
from ..live.guards import Insufficient, is_insufficient

PARITY_SELECTIONS = {
    'default': ('FY 2027', 'Q2 FY 2027', 'FY 2027 September'),
    'Cash': ('FY 2027', 'Q4 FY 2026', 'FY 2026 February'),
}
SEGMENT_PANELS = ('F&O', 'Cash', 'Commodities', 'MTF', 'MTF (net)')
PANELS = ('Consolidated', 'Broking', 'MTF', 'F&O', 'Cash', 'Commodities')


def panels_of(segs):
    """The panels to show: the six workbook panels, plus 'MTF (net)' under switch g."""
    return PANELS + (('MTF (net)',) if 'MTF (net)' in segs else ())


# ── label arithmetic ──
def prev_fy(fy):
    return f"FY {int(fy[3:]) - 1}"


def prev_q(q):
    n, y = int(q[1]), int(q[-4:])
    return f"Q{n - 1} FY {y}" if n > 1 else f"Q4 FY {y - 1}"


def q_last_year(q):
    return f"{q[:6]}{int(q[-4:]) - 1}"


def month_shift(m, k):
    """'FY 2027 September', -1 → 'FY 2027 August'; months run April..March within an FY."""
    idx = int(m[3:7]) * 12 + MONTHS.index(m[8:]) + k
    return f"FY {idx // 12} {MONTHS[idx % 12]}"


def six_months(m):
    return [month_shift(m, -k) for k in range(5, -1, -1)]


def labels_for(fy, q, m):
    qm = quarter_of_month(m)
    return {'fy': [fy, prev_fy(fy)], 'q': [q, prev_q(q), q_last_year(q)], 'm': [m, month_shift(m, -1)],
            'm_ly': month_shift(m, -12), 'six': six_months(m), 'avg6': [prev_q(qm), qm]}


def period_start(label):
    """First calendar date (ISO) of an 'FY 2027' / 'Q2 FY 2027' / 'FY 2027 September' period."""
    if label.startswith('Q'):
        label = months_of_quarter(label)[0]
    fy = int(label[3:7])
    if len(label) == 7:                                   # 'FY 2027'
        return f"{fy - 1}-04-01"
    mon = MONTHS.index(label[8:])                        # 0 = April
    year, month = (fy - 1, mon + 4) if mon <= 8 else (fy, mon - 8)
    return f"{year}-{month:02d}-01"


# ── guarded statistics ──
class GuardedSeg(Seg):
    """Seg with live-mode guards. `trading_days` = the calendar's trading days for this segment (ISO strings)."""

    def __init__(self, name, series, trading_days, scale=1.0, weekday_series=None, positive_only=False):
        super().__init__(series, scale, weekday_series, positive_only)
        self.name = name
        self.first = min(self.s) if self.s else None
        self.days = sorted(trading_days)

    def _partial(self, label):
        start = period_start(label)
        if not self.days or start < self.days[0]:
            return f"calendar starts {self.days[0] if self.days else '-'}, after {label} began"
        missed = [d for d in self.days if start <= d < self.first and keyfn_for(label)(d) == label] \
            if self.first else []
        if self.first is None or missed:
            return f"{self.name} series starts {self.first}, after {label} began"
        return None

    def _avg(self, keyfn, label):
        why = self._partial(label)
        if why:
            return Insufficient(f"{self.name} {label}: {why}")
        vals = [v for d, v in self.s.items() if keyfn(d) == label]
        return mean(vals) if vals else Insufficient(f"{self.name} {label}: no trading days")

    def avg6(self, a, b):
        x, y = self.q(a), self.q(b)
        bad = _first_insufficient(x, y)
        return bad if bad is not None else (x + y) / 2

    def months(self, labels):
        for lab in labels:
            why = self._partial(lab)
            if why:
                return Insufficient(f"{self.name} 6M to {labels[-1]}: {why}")
        vals = [v for d, v in self.s.items() if fy_month_of(d) in labels]
        return mean(vals) if vals else Insufficient(f"{self.name} 6M to {labels[-1]}: no trading days")

    def lastn(self, n):
        have = len(self._filtered(self.s))
        return super().lastn(n) if have >= n else Insufficient(f"{self.name} last {n} days: {have} days")

    def prev5(self):
        have = len(self._filtered(self.s))
        return super().prev5() if have >= 10 else Insufficient(f"{self.name} previous 5 days: {have} days")

    def weekday(self, k, n):
        import datetime as dt
        have = sum(1 for d in self._filtered(self.w) if dt.date.fromisoformat(d).weekday() == k)
        if have < n:
            return Insufficient(f"{self.name} {WEEKDAYS[k]} x{n}: {have} dates")
        return super().weekday(k, n)


def keyfn_for(label):
    if label.startswith('Q'):
        return q_of
    return fy_of if len(label) == 7 else fy_month_of


def _first_insufficient(*xs):
    return next((x for x in xs if is_insufficient(x)), None)


def _sum(xs):
    bad = _first_insufficient(*xs)          # Insufficient is falsy: never use `or` here
    return bad if bad is not None else sum(xs)


def _cmp(a, b, what):
    bad = _first_insufficient(a, b)
    if bad is not None:
        return bad
    return a / b - 1 if b else Insufficient(f"{what}: base is 0")


# ── segments from the engine's daily output ──
def make_segments(daily, guarded=False, calendar=None, exclude=(), mtf_split=False):
    """Same series and scaling as summary.build. guarded=True needs `calendar` ({iso: sb_calendar row}).
    exclude: dates left out of every statistic (switch d: special sessions).
    mtf_split (switch g, decision D4): MTF is gross in every table (the workbook's weekday tables use net),
    and a separate 'MTF (net)' panel shows net = 45% × gross. Consolidated stays on gross."""
    exclude = set(exclude)
    if exclude:
        daily = {seg: {d: r for d, r in rows.items() if d not in exclude} for seg, rows in daily.items()}
    spec = {
        'F&O': ({d: r['rev_mn'] for d, r in daily['fo'].items()}, 10, None, False, 'is_equity_day'),
        'Cash': ({d: r['rev_mn'] for d, r in daily['cash'].items()}, 10, None, False, 'is_equity_day'),
        'Commodities': ({d: r['rev_mn'] for d, r in daily['comm'].items()}, 10, None, True, 'is_mcx_day'),
        'MTF': ({d: r['gross_cr'] for d, r in daily['mtf'].items()}, 1,
                None if mtf_split else {d: r['net_cr'] for d, r in daily['mtf'].items()}, False, 'is_equity_day'),
    }
    if mtf_split:
        spec['MTF (net)'] = ({d: r['net_cr'] for d, r in daily['mtf'].items()}, 1, None, False, 'is_equity_day')
    out = {}
    for name, (s, scale, w, pos, flag) in spec.items():
        if guarded:
            days = [d for d, r in calendar.items() if r[flag] and d not in exclude]
            out[name] = GuardedSeg(name, s, days, scale, w, pos)
        else:
            out[name] = Seg(s, scale, w, pos)
    return out


def _combine(segs, panel, fn):
    if panel in SEGMENT_PANELS:
        return fn(segs[panel])
    broking = _sum([fn(segs[p]) for p in ('F&O', 'Cash', 'Commodities')])
    return broking if panel == 'Broking' else _sum([broking, fn(segs['MTF'])])


# ── the parity grid from the general rule (E3 exit test) ──
def parity_stats(segs):
    """stats in summary.build's shape, built from labels_for at the parity selections."""
    def block(seg, lab):
        return {'fy': [seg.fy(x) for x in lab['fy']], 'q': [seg.q(x) for x in lab['q']],
                'm': [seg.m(x) for x in lab['m']] + [seg.avg6(*lab['avg6'])],
                'w': [seg.lastn(5), seg.prev5(), seg.lastn(45), seg.lastn(20)],
                'wd': [[seg.weekday(k, 1), seg.weekday(k, 3), seg.weekday(k, 10)] for k in range(5)]}
    D = labels_for(*PARITY_SELECTIONS['default'])
    stats = {n: block(segs[n], labels_for(*PARITY_SELECTIONS.get(n, PARITY_SELECTIONS['default'])))
             for n in ('F&O', 'Cash', 'Commodities', 'MTF')}
    parts = [block(segs[n], D) for n in ('F&O', 'Cash', 'Commodities')]

    def add(blocks):
        out = {k: [sum(b[k][i] for b in blocks) for i in range(len(blocks[0][k]))] for k in ('fy', 'q', 'm', 'w')}
        out['wd'] = [[sum(b['wd'][k][j] for b in blocks) for j in range(3)] for k in range(5)]
        return out
    stats['Broking'] = add(parts)
    stats['Consolidated'] = add([stats['Broking'], block(segs['MTF'], D)])
    return stats


# ── live rows for every FY / quarter / month ──
def _row(panel, ptype, pkey, table, label, value, comparison=None, comp=None):
    reasons = dict.fromkeys(str(x) for x in (value, comp) if is_insufficient(x))
    note = '; '.join(reasons) if reasons else None
    return dict(panel=panel, period_type=ptype, period_key=pkey, table_name=table, row_label=label,
                value=None if is_insufficient(value) else value, comparison=comparison,
                comp_value=None if is_insufficient(comp) else comp, note=note)


def period_rows(segs, six='calendar'):
    """Rows for every FY, quarter and month present in the daily series, for every panel."""
    dates = sorted({d for s in segs.values() for d in s.s})
    fys = sorted({fy_of(d) for d in dates})
    qs = sorted({q_of(d) for d in dates}, key=lambda q: (int(q[-4:]), int(q[1])))
    ms = sorted({fy_month_of(d) for d in dates}, key=lambda m: (int(m[3:7]), MONTHS.index(m[8:])))
    rows = []
    for panel in panels_of(segs):
        v = lambda fn: _combine(segs, panel, fn)
        for fy in fys:
            a, b = v(lambda s: s.fy(fy)), v(lambda s: s.fy(prev_fy(fy)))
            rows += [_row(panel, 'FY', fy, 'Financial Year', fy, a, 'YoY', _cmp(a, b, f'{fy} YoY')),
                     _row(panel, 'FY', fy, 'Financial Year', prev_fy(fy), b)]
        for q in qs:
            pq, ly = prev_q(q), q_last_year(q)
            a, b, c = v(lambda s: s.q(q)), v(lambda s: s.q(pq)), v(lambda s: s.q(ly))
            rows += [_row(panel, 'Q', q, 'Quarter', q, a, 'QoQ', _cmp(a, b, f'{q} QoQ')),
                     _row(panel, 'Q', q, 'Quarter', q + ' | YoY', a, 'YoY', _cmp(a, c, f'{q} YoY')),
                     _row(panel, 'Q', q, 'Quarter', pq, b), _row(panel, 'Q', q, 'Quarter', ly, c)]
        for m in ms:
            lab = labels_for(fy_of_month(m), quarter_of_month(m), m)
            pm, ly = lab['m'][1], lab['m_ly']
            a, b, c = v(lambda s: s.m(m)), v(lambda s: s.m(pm)), v(lambda s: s.m(ly))
            six_v = v(lambda s: s.months(lab['six'])) if six == 'calendar' else v(lambda s: s.avg6(*lab['avg6']))
            rows += [_row(panel, 'M', m, 'Month', m, a, 'MoM', _cmp(a, b, f'{m} MoM')),
                     _row(panel, 'M', m, 'Month', m + ' | YoY', a, 'YoY', _cmp(a, c, f'{m} YoY')),
                     _row(panel, 'M', m, 'Month', m + ' | vs 6M', a, 'Mo 6M', _cmp(a, six_v, f'{m} vs 6M')),
                     _row(panel, 'M', m, 'Month', pm, b), _row(panel, 'M', m, 'Month', ly, c),
                     _row(panel, 'M', m, 'Month', 'Avg of last 6 months', six_v)]
        rows += asof_rows(segs, panel, dates[-1])
    return rows


def fy_of_month(m):
    return m[:7]


def asof_rows(segs, panel, as_of):
    """Week and weekday tables (labels as in publish.summary_rows), anchored on as_of."""
    v = lambda fn: _combine(segs, panel, fn)
    w = [v(lambda s: s.lastn(5)), v(lambda s: s.prev5()), v(lambda s: s.lastn(45)), v(lambda s: s.lastn(20))]
    r = lambda *a: _row(panel, 'asof', as_of, *a)
    rows = [r('Week', 'Last 5 trading days', w[0], 'WoW', _cmp(w[0], w[1], 'WoW')),
            r('Week', 'Last 5 trading days | vs 45D', w[0], 'vs last 45 days', _cmp(w[0], w[2], 'vs 45D')),
            r('Week', 'Previous 5 trading days', w[1]), r('Week', 'Last 45 trading days', w[2]),
            r('Week', 'Last 20 trading days', w[3])]
    for k, d in enumerate(WEEKDAYS):
        latest, a3, a10 = (v(lambda s, n=n: s.weekday(k, n)) for n in (1, 3, 10))
        rows += [r('Weekday', d, latest, 'vs avg of last 3', _cmp(latest, a3, f'{d} vs 3')),
                 r('Weekday', d + ' | vs 10', latest, 'vs avg of last 10', _cmp(latest, a10, f'{d} vs 10')),
                 r('Weekday', f'Average of last 3 {d}s', a3), r('Weekday', f'Average of last 10 {d}s', a10)]
    return rows
