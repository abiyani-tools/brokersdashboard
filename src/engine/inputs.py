"""Load engine inputs from a brokers-dashboard DB snapshot (JSON export of the sb_* tables).

Every value the engine uses is looked up by the Excel cell it was seeded from (source_ref), so parity
mode uses exactly the input the workbook used. Live mode will swap these lookups for reviewed facts.
"""
import json, re, datetime as dt
from collections import defaultdict


def _ref(ref):
    """'excel:Working sheet - Angel One!H6' -> ('Working sheet - Angel One', 'H', 6)"""
    m = re.match(r"(?:excel:)?\s*'?(.+?)'?!\$?([A-Z]+)\$?(\d+)$", (ref or '').strip())
    if not m:
        return None
    return m.group(1).strip(), m.group(2), int(m.group(3))


class Inputs:
    def __init__(self, snap, switches=(), reviewed_facts=None):
        """switches: live switches to apply (src/engine/switches.py); none = parity mode.
        reviewed_facts: sb_disclosure_facts rows with status 'reviewed' (needed by cell switches)."""
        self.snap = snap
        # calendar
        self.cal = {r['trade_date']: r for r in snap['calendar']}
        # facts by (sheet, col, row) and by (metric, period, sheet)
        self.cell = {}
        self.fact = defaultdict(dict)
        for f in snap['facts']:
            r = _ref(f['source_ref'])
            if r:
                self.cell[r] = f['value']
            self.fact[(f['metric'], r[0] if r else None)][f['period_key']] = f['value']
        # market daily (excel_seed): {(dataset, metric): {date: (value, status)}}
        self.mkt = defaultdict(dict)
        for m in snap['market_daily']:
            self.mkt[(m['dataset'], m['metric'])][m['trade_date']] = (m['value'], m['status'])
        self.lake = defaultdict(dict)          # optional second source, for imputed days
        for m in snap.get('market_daily_lake', []):
            self.lake[(m['dataset'], m['metric'])][m['trade_date']] = m['value']
        # monthly market series
        self.monthly = {(m['dataset'], m['metric'], m['fy_month']): m['value'] for m in snap['monthly']}
        # pins and assumptions
        self.pins = {(p['key'], p['period_key']): (p['value'], p['value_text']) for p in snap['pins']}
        self.assume = {a['key']: (a['value'], a['value_text']) for a in snap['assumptions']}
        # live switches: cell overrides from reviewed facts (empty in parity mode)
        from . import switches as SW
        self.switches = SW.check(switches)
        self.overrides = {}
        if self.switches:
            from ..live.loader import Facts
            facts = Facts.from_rows(list(snap['facts']) + list(reviewed_facts or []))
            seed_units = {_ref(f['source_ref']): f['unit'] for f in snap['facts'] if _ref(f['source_ref'])}
            self.overrides = SW.cell_overrides(self.switches, facts, seed_units)

    # ── helpers ──
    def ws(self, col, row):
        """Value seeded from 'Working sheet - Angel One'!<col><row>."""
        key = ('Working sheet - Angel One', col, row)
        if key in self.overrides:
            return self.overrides[key][0]
        return self.cell.get(key)

    def pin(self, key, period=''):
        return self.pins.get((key, period), (None, None))

    def series(self, dataset, metric):
        return {d: v for d, (v, s) in self.mkt[(dataset, metric)].items()}

    def status(self, dataset, metric):
        return {d: s for d, (v, s) in self.mkt[(dataset, metric)].items()}


def load_snapshot(path, switches=(), reviewed_path=None):
    reviewed = json.load(open(reviewed_path))['facts'] if reviewed_path else None
    return Inputs(json.load(open(path)), switches, reviewed)


# ── calendar labels (same strings as the workbook) ──
MONTHS = ['April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December',
          'January', 'February', 'March']


def fy_of(d):
    d = dt.date.fromisoformat(d) if isinstance(d, str) else d
    return f"FY {d.year + 1 if d.month >= 4 else d.year}"


def fy_month_of(d):
    d = dt.date.fromisoformat(d) if isinstance(d, str) else d
    return f"{fy_of(d)} {d.strftime('%B')}"


def q_of(d):
    d = dt.date.fromisoformat(d) if isinstance(d, str) else d
    q = (d.month - 4) // 3 + 1 if d.month >= 4 else 4
    return f"Q{q} {fy_of(d)}"


def months_of_quarter(q):
    """'Q1 FY 2027' -> ['FY 2027 April', 'FY 2027 May', 'FY 2027 June']"""
    n, fy = int(q[1]), q[3:]
    return [f"{fy} {m}" for m in MONTHS[(n - 1) * 3:(n - 1) * 3 + 3]]


def quarter_of_month(fm):
    """'FY 2027 May' -> 'Q1 FY 2027'"""
    fy, mon = fm[:7], fm[8:]
    return f"Q{MONTHS.index(mon) // 3 + 1} {fy}"


def month_seq(start, end):
    """FY-month labels from start to end inclusive."""
    out, fy, i = [], int(start[3:7]), MONTHS.index(start[8:])
    while True:
        lab = f"FY {fy} {MONTHS[i]}"
        out.append(lab)
        if lab == end:
            return out
        i += 1
        if i == 12:
            i, fy = 0, fy + 1


def quarter_seq(start, end):
    out, n, fy = [], int(start[1]), int(start[6:])
    while True:
        lab = f"Q{n} FY {fy}"
        out.append(lab)
        if lab == end:
            return out
        n += 1
        if n == 5:
            n, fy = 1, fy + 1
