"""Live run (PLAN 4.1, dry run): E5 checks → engine with the live switches → E1 coverage → E3 Summary rows.

Nothing is written to the database here; publishing needs AB's OK and goes through engine/publish.py.

    python3 run_live.py                      # snapshot + reviewed facts, all switches, as of the last date
"""
from __future__ import annotations

import datetime as dt
import json
import os

from .integrity import Report, run_checks
from .loader import load_inputs
from .periods import MissingCalibration

ALL_SWITCHES = 'abcdefghi'
BROKER = 'ANGELONE'
# segment -> (daily key, value field, calendar flag, trading days allowed missing at the end)
SEGMENTS = {'fo': ('rev_mn', 'is_equity_day', 0), 'cash': ('rev_mn', 'is_equity_day', 0),
            'comm': ('rev_mn', 'is_mcx_day', 0), 'mtf': ('gross_cr', 'is_equity_day', 3)}


class MissingDailyRows(MissingCalibration):
    """Trading days with no daily revenue row: the day's input or its period's calibration is missing."""

    def __init__(self, missing):
        self.missing = missing
        parts = [f"{seg} {ds[0]}..{ds[-1]} ({len(ds)} days)" if len(ds) > 1 else f"{seg} {ds[0]}"
                 for seg, ds in sorted(missing.items())]
        Exception.__init__(self, 'no daily revenue for trading days (input or calibration missing): ' + '; '.join(parts))
        self.periods = parts


class EngineSnapshotReader:
    """sb_* table view of an engine snapshot (+ reviewed facts), for the live loader and E5."""

    def __init__(self, snap, reviewed=()):
        lake = [dict(r, status='ok') for r in snap.get('market_daily_lake', [])]
        self.tables = {
            'sb_calendar': snap['calendar'],
            'sb_disclosure_facts': [dict(f, broker_id=BROKER) for f in list(snap['facts']) + list(reviewed)],
            'sb_market_daily': [dict(r, source=r.get('source', 'excel_seed')) for r in snap['market_daily']] + lake,
            'sb_market_monthly': snap.get('monthly', []),
            'sb_parity_pins': snap.get('pins', []),
            'sb_assumptions': snap.get('assumptions', []),
        }

    def table(self, name, **eq):
        return [r for r in self.tables[name] if all(str(r.get(k)) == str(v) for k, v in eq.items())]


def coverage(calendar_rows, daily, as_of, input_gaps=None):
    """Trading days (up to as_of, from each segment's first day) with no daily row → MissingCalibration.

    The engine skips a day whose month or quarter has no calibration; this makes that loud (E1).
    input_gaps: {segment: dates whose input row is missing}, tolerated only where E5 rates the gap a
    warning (the industry MTF book: the quarterly average is over the days reported).
    """
    missing = {}
    for seg, (_, flag, lag) in SEGMENTS.items():
        rows = daily[seg]
        if not rows:
            raise MissingDailyRows({seg: ['all']})
        first = min(rows)
        days = sorted(r['trade_date'] for r in calendar_rows if r[flag] and first <= r['trade_date'] <= as_of)
        days = days[:len(days) - lag] if lag else days
        gone = [d for d in days if d not in rows and d not in (input_gaps or {}).get(seg, ())]
        if gone:
            missing[seg] = gone
    if missing:
        raise MissingDailyRows(missing)
    return True


def live_run(snapshot_path, reviewed_path, switches=ALL_SWITCHES, as_of=None):
    snap = json.load(open(snapshot_path))
    reviewed = json.load(open(reviewed_path))['facts'] if reviewed_path else []
    return live_run_snapshot(snap, reviewed, switches, as_of)


def live_run_snapshot(snap, reviewed, switches=ALL_SWITCHES, as_of=None):
    from ..engine import daily as D
    from ..engine import switches as SW
    from ..engine.inputs import Inputs
    from ..engine.summary_periods import make_segments, period_rows

    I = Inputs(snap, switches, reviewed)
    as_of = as_of or max(r['trade_date'] for r in I.snap['calendar'])

    res = D.run(I)
    tr = res['calib']['take_rates']
    rates = {(s, q): r[f'take_rate_{s}'] for q, r in tr.items() for s in ('fo', 'cash', 'comm') if f'take_rate_{s}' in r}

    inputs = load_inputs(EngineSnapshotReader(I.snap, reviewed), BROKER, dt.date.fromisoformat(as_of), switches)
    report = run_checks(inputs, take_rates=rates)

    book = I.series('mtf_industry', 'book_cr')
    mtf_gaps = {r['trade_date'] for r in I.snap['calendar'] if r['is_equity_day'] and r['trade_date'] not in book}
    coverage(I.snap['calendar'], res['daily'], as_of, {'mtf': mtf_gaps})

    segs = make_segments(res['daily'], guarded=True, calendar=I.cal, exclude=SW.excluded_dates(I),
                         mtf_split='g' in I.switches, exclude_segments=SW.D_SEGMENTS)
    rows = period_rows(segs)
    return dict(as_of=as_of, switches=''.join(sorted(I.switches)), report=report, daily=res['daily'],
                calib=res['calib'], rows=rows, overrides=I.overrides)


def headline(rows, keys=(('FY', 'FY 2027'), ('Q', 'Q2 FY 2027'), ('M', 'FY 2027 October'))):
    """{(period_key, panel): (value, comparison, comp_value)} for the selection rows themselves."""
    out = {}
    for r in rows:
        if (r['period_type'], r['period_key']) in keys and r['row_label'] in (r['period_key'], r['period_key'] + ' | YoY'):
            out.setdefault((r['period_key'], r['panel']), {})[r['comparison']] = (r['value'], r['comp_value'], r['note'])
    return out


def report_md(run, db_status=None):
    """db_status: what happened in the database (None = a dry run, nothing written)."""
    rep: Report = run['report']
    title = 'Live run (dry run)' if db_status is None else 'Live run'
    L = [f"# {title} — as of {run['as_of']}", '',
         f"Switches: {run['switches']} · E5: {'BLOCKING' if rep.blocking else 'pass'} "
         f"({len(rep.errors)} blocking, {len(rep.find(severity='warning'))} warnings, "
         f"{len(rep.find(severity='info'))} info) · E1 coverage: pass · Summary rows: {len(run['rows'])}", '',
         db_status or 'Nothing was written to the database.', '', '## Headline (Rs crore per trading day; MTF gross)', '',
         '| Period | Panel | ADR | vs previous | YoY |', '|---|---|---:|---:|---:|']
    h = headline(run['rows'])
    pct = lambda x: '—' if x is None else f'{100 * x:+.1f}%'
    for (k, panel), c in sorted(h.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        first = next(iter(c.values()))
        prev = c.get('QoQ', c.get('MoM', (None, None, None)))[1] if 'YoY' in c and len(c) > 1 else None
        yoy = c.get('YoY', (None, None, None))[1]
        val = '—' if first[0] is None else f'{first[0]:.4f}'
        L.append(f"| {k} | {panel} | {val} | {pct(prev)} | {pct(yoy)} |")
    L += ['', '## E5 integrity report', '', '```', rep.summary(), '```', '']
    return '\n'.join(L)


def write(run, out_dir, db_status=None):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'report.md'), 'w') as fh:
        fh.write(report_md(run, db_status))
    with open(os.path.join(out_dir, 'summary_rows.json'), 'w') as fh:
        json.dump(run['rows'], fh)
    return out_dir
