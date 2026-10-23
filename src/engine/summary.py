"""'SUMMARY - Angel One' grid, cell for cell (parity layout).

Statistics follow the workbook formulas exactly:
- FY / quarter / month: AVERAGEIFS over the segment sheet's rows (all numeric rows; commodities incl. zeros)
- 'Avg of last 6 months': (avg quarter A + avg quarter B) / 2
- last 5 / previous 5 / last 45 / last 20 trading days: rows with date >= LARGE(unique dates, N)
- weekday: latest / last 3 / last 10 distinct dates with that weekday
  (commodities filter revenue > 0 for last-N and weekday; MTF weekday uses NET revenue)
- Broking and Consolidated = sums of segment statistics.
"""
import datetime as dt
from statistics import mean
from .inputs import fy_of, q_of, fy_month_of

WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

# Parity labels = the workbook's hard-coded period labels (SUMMARY!M8:M18, B61:B71 etc.)
PARITY_LABELS = {
    'default': {'fy': ['FY 2027', 'FY 2026'], 'q': ['Q2 FY 2027', 'Q1 FY 2027', 'Q2 FY 2026'],
                'm': ['FY 2027 September', 'FY 2027 August'], 'avg6': ['Q1 FY 2027', 'Q2 FY 2027']},
    'Cash':    {'fy': ['FY 2027', 'FY 2026'], 'q': ['Q4 FY 2026', 'Q3 FY 2026', 'Q4 FY 2025'],
                'm': ['FY 2026 February', 'FY 2026 January'], 'avg6': ['Q3 FY 2026', 'Q4 FY 2026']},
}

# panel -> (side, fy rows, q rows, m rows, week rows, weekday first row)
LAYOUT = {
    'Consolidated': ('L', (7, 8), (11, 12, 13), (16, 17, 18), (22, 23, 24, 25), 7),
    'Broking':      ('R', (8, 9), (12, 13, 14), (17, 18, 19), (23, 24, 25, 26), 8),
    'MTF':          ('L', (35, 36), (39, 40, 41), (44, 45, 46), (50, 51, 52, 53), 35),
    'F&O':          ('R', (35, 36), (39, 40, 41), (44, 45, 46), (50, 51, 52, 53), 35),
    'Cash':         ('L', (61, 62), (65, 66, 67), (70, 71, 72), (76, 77, 78, 79), 61),
    'Commodities':  ('R', (61, 62), (65, 66, 67), (70, 71, 72), (76, 77, 78, 79), 61),
}
COLS = {'L': ('C', 'D', 'E', 'H', 'I', 'J'), 'R': ('N', 'O', 'P', 'S', 'T', 'U')}


class Seg:
    """One segment's daily series with the workbook's statistics."""
    def __init__(self, series, scale=1.0, weekday_series=None, positive_only=False):
        self.s = {d: v / scale for d, v in series.items() if v is not None}
        self.w = {d: v / scale for d, v in (weekday_series or series).items() if v is not None}
        self.pos = positive_only

    def _avg(self, keyfn, label):
        vals = [v for d, v in self.s.items() if keyfn(d) == label]
        return mean(vals) if vals else 0.0          # IFERROR(...,0)

    def fy(self, l): return self._avg(fy_of, l)
    def q(self, l): return self._avg(q_of, l)
    def m(self, l): return self._avg(fy_month_of, l)
    def avg6(self, a, b): return (self.q(a) + self.q(b)) / 2

    def _filtered(self, s):
        return {d: v for d, v in s.items() if (v > 0 if self.pos else True)}

    def lastn(self, n):
        s = self._filtered(self.s); u = sorted(s, reverse=True)
        cutoff = u[n - 1]
        return mean(v for d, v in s.items() if d >= cutoff)

    def prev5(self):
        s = self._filtered(self.s); u = sorted(s, reverse=True)
        hi, lo = u[5], u[9]
        return mean(v for d, v in s.items() if lo <= d <= hi)

    def weekday(self, k, n):
        s = self._filtered(self.w)
        ds = sorted((d for d in s if dt.date.fromisoformat(d).weekday() == k), reverse=True)[:n]
        return mean(s[d] for d in ds)


def build(daily):
    segs = {
        'F&O': Seg({d: r['rev_mn'] for d, r in daily['fo'].items()}, 10),
        'Cash': Seg({d: r['rev_mn'] for d, r in daily['cash'].items()}, 10),
        'Commodities': Seg({d: r['rev_mn'] for d, r in daily['comm'].items()}, 10, positive_only=True),
        'MTF': Seg({d: r['gross_cr'] for d, r in daily['mtf'].items()}, 1,
                   weekday_series={d: r['net_cr'] for d, r in daily['mtf'].items()}),
    }
    D = PARITY_LABELS['default']
    stats = {}

    def seg_block(name, lab):
        g = segs[name]
        return {
            'fy': [g.fy(x) for x in lab['fy']],
            'q': [g.q(x) for x in lab['q']],
            'm': [g.m(x) for x in lab['m']] + [g.avg6(*lab['avg6'])],
            'w': [g.lastn(5), g.prev5(), g.lastn(45), g.lastn(20)],
            'wd': [[g.weekday(k, 1), g.weekday(k, 3), g.weekday(k, 10)] for k in range(5)],
        }

    for name in segs:
        stats[name] = seg_block(name, PARITY_LABELS.get(name, D))
    # Broking sums segment stats computed on the DEFAULT labels (cash too: SUMMARY!N8 uses M8, not B61)
    parts = [seg_block(n, D) for n in ('F&O', 'Cash', 'Commodities')]
    stats['Broking'] = _sum_blocks(parts)
    stats['Consolidated'] = _sum_blocks([stats['Broking'], seg_block('MTF', D)])
    return _to_cells(stats, D), stats


def _sum_blocks(blocks):
    out = {}
    for k in ('fy', 'q', 'm', 'w'):
        out[k] = [sum(b[k][i] for b in blocks) for i in range(len(blocks[0][k]))]
    out['wd'] = [[sum(b['wd'][k][j] for b in blocks) for j in range(3)] for k in range(5)]
    return out


def _cmp(a, b):
    try:
        return a / b - 1
    except ZeroDivisionError:
        return None


def _to_cells(stats, D):
    cells = {}
    for panel, (side, fyr, qr, mr, wr, wd0) in LAYOUT.items():
        v, c1, c2, wv, wc1, wc2 = COLS[side]
        st = stats[panel]
        for rows, key in ((fyr, 'fy'), (qr, 'q'), (mr, 'm'), (wr, 'w')):
            vals = st[key]
            for r, x in zip(rows, vals):
                cells[f'{v}{r}'] = (panel, key, x)
            cells[f'{c1}{rows[0]}'] = (panel, key + '_cmp1', _cmp(vals[0], vals[1]))
            if key != 'fy':
                cells[f'{c2}{rows[0]}'] = (panel, key + '_cmp2', _cmp(vals[0], vals[2]))
        for k in range(5):
            r0 = wd0 + 4 * k
            latest, a3, a10 = st['wd'][k]
            cells[f'{wv}{r0}'] = (panel, f'{WEEKDAYS[k]} latest', latest)
            cells[f'{wv}{r0 + 1}'] = (panel, f'{WEEKDAYS[k]} avg3', a3)
            cells[f'{wv}{r0 + 2}'] = (panel, f'{WEEKDAYS[k]} avg10', a10)
            cells[f'{wc1}{r0}'] = (panel, f'{WEEKDAYS[k]} vs avg3', _cmp(latest, a3))
            cells[f'{wc2}{r0}'] = (panel, f'{WEEKDAYS[k]} vs avg10', _cmp(latest, a10))
    return cells
