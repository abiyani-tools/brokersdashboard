"""'SUMMARY - Angel One' grid, cell for cell (parity layout).

Statistics follow the workbook formulas exactly:
- FY / quarter / month: AVERAGEIFS over the segment sheet's rows (all numeric rows; commodities incl. zeros)
- 'Avg of last 6 months': (avg quarter A + avg quarter B) / 2
- last 5 / previous 5 / last 45 / last 20 trading days: rows with date >= LARGE(unique dates, N)
- weekday: latest / last 3 / last 10 distinct dates with that weekday
  (commodities filter revenue > 0 for last-N and weekday; MTF weekday uses NET revenue)
- Broking and Consolidated = sums of segment statistics.

Per-broker parity specs (SPECS): labels, comparison columns, panel layout, the daily field and scale each segment
reads, and whether the MTF weekday tables read net. 'MOSL' (SUMMARY - Motilal Oswal) differs from the other two in
its layout (Broking aligned with Consolidated; Commodities left and Cash right in band 3), in reading Cash and MTF
in Rs Cr (no /10) and in its error rows: a daily row with `err` set is a cell holding #N/A / #VALUE!, which makes
AVERAGEIFS (FY / quarter / month) an error and IFERROR turn it into 0, while the last-N and weekday windows drop it.
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

# 'SUMMARY - Groww': the same rows, but the right panels sit in L:T (labels in L / Q, values in M / R), and the
# latest period is the partial Q3 FY27 / October. The F&O panel (L35:L45) and the Cash panel (B61:B71) keep stale
# hand-typed labels; Broking and Consolidated read the default labels (L8:L18) for every segment.
_GROWW_FY = ['FY 2027', 'FY 2026']
_GROWW_STALE_M = ['FY 2026 February', 'FY 2026 January']
GROWW_LABELS = {
    'default': {'fy': _GROWW_FY, 'q': ['Q3 FY 2027', 'Q2 FY 2027', 'Q3 FY 2026'],
                'm': ['FY 2027 October', 'FY 2027 September'], 'avg6': ['Q2 FY 2027', 'Q3 FY 2027']},
    'F&O':     {'fy': _GROWW_FY, 'q': ['Q1 FY 2027', 'Q4 FY 2026', 'Q4 FY 2025'], 'm': _GROWW_STALE_M,
                'avg6': ['Q4 FY 2026', 'Q1 FY 2027']},
    'Cash':    {'fy': _GROWW_FY, 'q': ['Q1 FY 2027', 'Q4 FY 2026', 'Q1 FY 2026'], 'm': _GROWW_STALE_M,
                'avg6': ['Q4 FY 2026', 'Q1 FY 2027']},
}
GROWW_COLS = {'L': ('C', 'D', 'E', 'H', 'I', 'J'), 'R': ('M', 'N', 'O', 'R', 'S', 'T')}

# 'SUMMARY - Motilal Oswal': panels L:T like Groww, but Broking sits on the Consolidated rows and band 3 is swapped
# (Commodities left B58:J81, Cash right L59:T82, one row below). Every panel reads the same typed labels (L7:L17),
# and the "YoY" quarter row is Q4 FY26 (L13). F&O and Commodities are Rs Mn (/10); Cash (AB) and MTF (X) are Rs Cr.
MOSL_LABELS = {
    'default': {'fy': ['FY 2027', 'FY 2026'], 'q': ['Q2 FY 2027', 'Q1 FY 2027', 'Q4 FY 2026'],
                'm': ['FY 2027 September', 'FY 2027 August'], 'avg6': ['Q1 FY 2027', 'Q2 FY 2027']},
}
_MOSL_TOP = ('L', (7, 8), (11, 12, 13), (16, 17, 18), (22, 23, 24, 25), 7)
_MOSL_MTF = ('L', (35, 36), (39, 40, 41), (44, 45, 46), (50, 51, 52, 53), 35)
MOSL_LAYOUT = {
    'Consolidated': _MOSL_TOP,
    'Broking':      ('R',) + _MOSL_TOP[1:],
    'MTF':          _MOSL_MTF,
    'F&O':          ('R',) + _MOSL_MTF[1:],
    'Commodities':  ('L', (63, 64), (67, 68, 69), (72, 73, 74), (78, 79, 80, 81), 63),
    'Cash':         ('R', (64, 65), (68, 69, 70), (73, 74, 75), (79, 80, 81, 82), 64),
}
# segment -> (daily field, divisor, last-N / weekday windows keep revenue > 0 only)
DEFAULT_FIELDS = {'F&O': ('rev_mn', 10, False), 'Cash': ('rev_mn', 10, False),
                  'Commodities': ('rev_mn', 10, True), 'MTF': ('gross_cr', 1, False)}
MOSL_FIELDS = {'F&O': ('rev_mn', 10, False), 'Cash': ('rev_cr', 1, False),
               'Commodities': ('rev_mn', 10, False), 'MTF': ('nii_cr', 1, False)}

# per-broker parity spec: labels, comparison columns, whether the MTF weekday tables read net (Angel) or gross (Groww)
SPECS = {
    'ANGELONE': {'labels': PARITY_LABELS, 'cols': COLS, 'mtf_weekday_net': True},
    'GROWW': {'labels': GROWW_LABELS, 'cols': GROWW_COLS, 'mtf_weekday_net': False},
    'MOSL': {'labels': MOSL_LABELS, 'cols': GROWW_COLS, 'mtf_weekday_net': False, 'layout': MOSL_LAYOUT,
             'fields': MOSL_FIELDS},
}


class Seg:
    """One segment's daily series with the workbook's statistics."""
    def __init__(self, series, scale=1.0, weekday_series=None, positive_only=False, errors=()):
        self.s = {d: v / scale for d, v in series.items() if v is not None}
        self.w = {d: v / scale for d, v in (weekday_series or series).items() if v is not None}
        self.pos = positive_only
        self.err = set(errors)                      # dates whose cell holds #N/A / #VALUE! (MOSL)

    def _avg(self, keyfn, label):
        if self.err and any(keyfn(d) == label for d in self.err):
            return 0.0                              # AVERAGEIFS over an error -> error -> IFERROR(...,0)
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


def build(daily, broker='ANGELONE'):
    spec = SPECS[broker]
    PARITY_LABELS = spec['labels']
    mtf_w = {d: r['net_cr'] for d, r in daily['mtf'].items()} if spec['mtf_weekday_net'] else None
    fields = spec.get('fields', DEFAULT_FIELDS)
    key = {'F&O': 'fo', 'Cash': 'cash', 'Commodities': 'comm', 'MTF': 'mtf'}
    segs = {}
    for name, (field, scale, pos) in fields.items():
        rows = daily[key[name]]
        segs[name] = Seg({d: r[field] for d, r in rows.items()}, scale, positive_only=pos,
                         weekday_series=mtf_w if name == 'MTF' else None,
                         errors=[d for d, r in rows.items() if r.get('err')])
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
    return _to_cells(stats, D, spec['cols'], spec.get('layout', LAYOUT)), stats


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


def _to_cells(stats, D, cols=COLS, layout=LAYOUT):
    cells = {}
    for panel, (side, fyr, qr, mr, wr, wd0) in layout.items():
        v, c1, c2, wv, wc1, wc2 = cols[side]
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
