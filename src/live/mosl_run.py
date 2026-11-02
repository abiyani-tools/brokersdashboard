"""MOSL live run: switches m-a ... m-f on the shared snapshot, with MOSL's own facts and its four lake series.

MOSL publishes no orders, so nothing is borrowed from the Angel One calibration (unlike Groww): a MOSL run needs the shared
snapshot (calendar, MCX contracts, industry MTF book) and MOSL's inputs only. It still reads the same snapshot as the other
brokers; its as-of date is the last day on which *its* inputs are complete (snapshot.complete_through_mosl): NSE index-option
contracts, BSE contracts, NSE / BSE cash turnover and MCX contracts. A zero or a non-ok row on a trading day in any of them
is a blocking E5 error (zero = suspect), so until the lake has the NSE index-option contracts again (ExchangesDash PR #33)
MOSL's as-of date is earlier than Angel One's and Groww's.

Only reviewed MOSL facts move numbers. A run whose required facts are not all 'reviewed' (or whose workbook inputs are not in
the database) is refused with MoslRefused and nothing is computed or published.

    mosl = live_run_mosl(snap, msnap, facts, lake_rows)               # raises MoslRefused
"""
from __future__ import annotations

import datetime as dt

from .groww_run import is_seed
from .integrity import run_checks
from .loader import MOSL_LAKE_KEYS, MOSL_MARKET_KEYS, MOSL_SHARED_KEYS, load_inputs
from .run import EngineSnapshotReader, coverage
from .snapshot import complete_through_mosl, mosl_lake_series

BROKER = 'MOSL'
SWITCHES = 'abcdef'


class MoslRefused(RuntimeError):
    """The MOSL run is not allowed to go live: its facts are not reviewed, or its inputs are not in the database."""

    def __init__(self, reasons):
        self.reasons = list(reasons)
        super().__init__('MOSL live run refused: ' + ' | '.join(self.reasons))


def mosl_inputs(reader, broker=BROKER):
    """(MOSL snapshot, MOSL filing facts) from the sb_* tables: the workbook seed facts, assumptions and pins of `broker`,
    and every other fact that is not rejected (any status: the run decides what it may use)."""
    rows = [dict(f, broker_id=broker) for f in reader.table('sb_disclosure_facts', broker_id=broker)
            if f['status'] != 'rejected']
    snap = dict(broker_id=broker,
                facts=[f for f in rows if is_seed(f)],
                assumptions=[dict(a, broker_id=broker) for a in reader.table('sb_assumptions', broker_id=broker)],
                pins=[dict(p, broker_id=broker) for p in reader.table('sb_parity_pins', broker_id=broker)],
                market_daily=[])                       # the workbook's exchange series are not in the DB: live reads the lake
    return snap, [f for f in rows if not is_seed(f)]


def _ids(rows):
    ids = sorted(f['fact_id'] for f in rows)
    return f'{ids[0]}-{ids[-1]}' if ids else 'none'


def refusal_reasons(switches, msnap, facts):
    """Why a MOSL run may not go live (empty list = fine). Reads nothing but its arguments."""
    from ..engine import mosl_switches as MS
    reasons = []
    counts = (len(msnap['facts']), len(msnap['assumptions']), len(msnap['pins']))
    if not all(counts):
        reasons.append(f'MOSL workbook inputs are not in the database ({counts[0]} seed facts, {counts[1]} '
                       f'assumptions, {counts[2]} pins; the run needs all three)')
    rows = [f for f in facts if f['status'] != 'rejected']
    reviewed = [f for f in rows if f['status'] == 'reviewed']
    staged = [f for f in rows if f['status'] != 'reviewed']
    if not switches:
        return reasons
    if not all(counts):
        if staged:
            reasons.append(f'MOSL filing facts: {len(reviewed)} reviewed, {len(staged)} staged (ids {_ids(staged)}); '
                           'the switches need reviewed facts')
        return reasons
    if 'f' in switches and MS.YIELD_ASSUMPTION not in {a['key'] for a in msnap['assumptions']}:
        reasons.append(f'the sb_assumptions row {MS.YIELD_ASSUMPTION} ({MS.YIELD_LABEL}) is not in the database')
    # which facts the switches would read: build the overlay as if every fact were reviewed, then check each one
    lenient = [dict(f, status='reviewed') for f in rows]
    by_id = {f['fact_id']: f for f in rows}
    seed_facts = {(f['metric'], f['period_key']): f for f in msnap['facts']}
    try:
        overlay = MS.build_overlay(switches, lenient, seed_facts)
    except MS.SwitchError as e:
        reasons.append(f'MOSL filing facts incomplete or inconsistent: {e}')
        return reasons
    need = {i for o in overlay.values() for i in o.fact_ids if isinstance(i, int)}
    bad = [by_id[i] for i in sorted(need) if by_id[i]['status'] != 'reviewed']
    if bad:
        what = ', '.join(f"{f['metric']} {f['period_key']} (fact {f['fact_id']}, {f['status']})" for f in bad[:12])
        reasons.append(f'{len(bad)} of the {len(need)} MOSL facts the switches read are not reviewed: {what}'
                       + (f' ... and {len(bad) - 12} more' if len(bad) > 12 else ''))
    return reasons


class MoslSnapshotReader(EngineSnapshotReader):
    """sb_* view for E5: the shared calendar and MCX / MTF series of the snapshot, MOSL's own facts and lake rows."""

    def __init__(self, snap, msnap, facts, lake_rows):
        super().__init__(snap, ())
        self.tables['sb_disclosure_facts'] = [dict(f, broker_id=BROKER) for f in list(msnap['facts']) + list(facts)]
        self.tables['sb_market_daily'] = list(self.tables['sb_market_daily']) + [
            dict(r, source=r.get('source', 'exchangesdash_json')) for r in lake_rows]


# E5 reads each series as the engine does: the lake's own rows for MOSL's four, workbook-first for the shared two
E5_POLICY = {**{k: 'lake_ok' for k in MOSL_LAKE_KEYS}, **{k: 'excel_first' for k in MOSL_SHARED_KEYS}}


def live_run_mosl(snap, msnap, facts, lake_rows, switches=SWITCHES, as_of=None):
    """MOSL's live run on the shared snapshot `snap` (untrimmed: MOSL takes its own as-of date).

    msnap: MOSL snapshot (seed facts, assumptions, pins); facts: MOSL filing facts of any status; lake_rows: sb_market_daily
    rows of the four lake series. as_of: default = the last day on which MOSL's inputs are complete.
    Raises MoslRefused (nothing computed) unless every fact the switches read is reviewed."""
    from ..engine import mosl as MO
    from ..engine import mosl_switches as MS
    from ..engine.mosl_bridge import live_period_rows

    switches = MS.check(switches)
    reasons = refusal_reasons(switches, msnap, facts)
    if reasons:
        raise MoslRefused(reasons)
    lake = mosl_lake_series(lake_rows)
    limiting = ''
    if as_of is None:
        as_of, limiting = complete_through_mosl(snap, lake)
    reviewed = [f for f in facts if f['status'] == 'reviewed']
    try:
        M = MO.MoslInputs(msnap, snap, switches, reviewed, lake, as_of)
        res = MO.run(M)
    except MS.SwitchError as e:
        raise MoslRefused([str(e)])
    except KeyError as e:
        raise MoslRefused([f'a MOSL input is missing: {e}'])

    reader = MoslSnapshotReader({**snap, 'calendar': [r for r in snap['calendar'] if r['trade_date'] <= as_of]},
                                msnap, reviewed, lake_rows)
    inputs = load_inputs(reader, BROKER, dt.date.fromisoformat(as_of), (), policy=E5_POLICY, keys=MOSL_MARKET_KEYS)
    report = run_checks(inputs, keys=MOSL_MARKET_KEYS)

    book = M.series('mtf_industry', 'book_cr')
    mtf_gaps = {r['trade_date'] for r in snap['calendar']
                if r['is_equity_day'] and r['trade_date'] <= as_of and r['trade_date'] not in book}
    cov = 'pass'
    if report.blocking:
        cov = 'not evaluated (E5 blocks: a day it flags has no row, so E1 would only repeat it)'
    else:
        coverage([r for r in snap['calendar'] if r['trade_date'] <= as_of], res['daily'], as_of, {'mtf': mtf_gaps})

    rows = live_period_rows(M, res)
    used = sorted({i for o in M.overlay.values() for i in o.fact_ids if isinstance(i, int)})
    note = (f"MOSL needs nothing from the Angel One calibration. As of {as_of}"
            + (f' (limited by {limiting})' if limiting else '')
            + f": {len(M.overlay)} inputs come from {len(used)} reviewed data-book facts; the rest are the workbook's. "
              'Basis: net brokerage of retail + PWM (Consolidated net brokerage; excludes Capital Markets) plus MTF net interest '
              f'income. MTF yield: the workbook\'s typed values, carried at {M.assume(MS.YIELD_ASSUMPTION):.2%} '
              f'({MS.YIELD_LABEL}).')
    last = {s: M.pin(f'{s}_last_actual_quarter') for s in ('fo', 'cash', 'comm')}
    last['mtf'] = M.pin('mtf_last_actual_quarter')
    return dict(as_of=as_of, switches=''.join(sorted(M.switches)), report=report, daily=res['daily'],
                calib=dict(res['calib'], last_actual=last), rows=rows, overrides=M.overlay, broker=BROKER,
                facts_reviewed=True, fact_ids=used, note=note, limiting=limiting, coverage=cov)
