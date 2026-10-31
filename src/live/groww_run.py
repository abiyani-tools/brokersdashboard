"""Groww live run: the Angel One live run's calibration + Groww's own facts, switches g-a ... g-g.

Groww publishes no orders, so its model borrows Angel One's calibration (contracts per order, trades per order,
commodity market orders and take rates). A Groww run is therefore built *from an Angel live run* (the same
snapshot, the same as-of date, the same switches on the shared exchange series), never from a separate one.

Only reviewed Groww facts move numbers. A run whose required facts are not all 'reviewed' (or whose workbook
inputs are not in the database) is refused with GrowwRefused and nothing is computed or published.

    angel = live_run_snapshot(snap, reviewed)
    groww = live_run_groww(angel, groww_snapshot, groww_facts)       # raises GrowwRefused
"""
from __future__ import annotations

import datetime as dt

from .integrity import run_checks
from .loader import load_inputs
from .run import EngineSnapshotReader, coverage

BROKER = 'GROWW'
SWITCHES = 'abcdefg'


class GrowwRefused(RuntimeError):
    """The Groww run is not allowed to go live: its facts are not reviewed, or its inputs are not in the database."""

    def __init__(self, reasons):
        self.reasons = list(reasons)
        super().__init__('Groww live run refused: ' + ' | '.join(self.reasons))


def is_seed(fact):
    """A workbook input (source_ref 'excel:...'): the parity baseline, read whatever its status (as for Angel One)."""
    return str(fact.get('source_ref') or '').startswith('excel:')


def groww_inputs(reader, broker=BROKER):
    """(Groww snapshot, Groww filing facts) from the sb_* tables: the workbook seed facts, assumptions and pins of
    `broker`, and every other fact that is not rejected (any status: the run decides what it may use)."""
    rows = [dict(f, broker_id=broker) for f in reader.table('sb_disclosure_facts', broker_id=broker)
            if f['status'] != 'rejected']
    snap = dict(broker_id=broker,
                facts=[f for f in rows if is_seed(f)],
                assumptions=[dict(a, broker_id=broker) for a in reader.table('sb_assumptions', broker_id=broker)],
                pins=[dict(p, broker_id=broker) for p in reader.table('sb_parity_pins', broker_id=broker)])
    return snap, [f for f in rows if not is_seed(f)]


def _ids(rows):
    ids = sorted(f['fact_id'] for f in rows)
    return f'{ids[0]}-{ids[-1]}' if ids else 'none'


def refusal_reasons(switches, gsnap, facts):
    """Why a Groww run may not go live (empty list = fine). Reads nothing but its arguments."""
    from ..engine import groww_switches as GS
    reasons = []
    counts = (len(gsnap['facts']), len(gsnap['assumptions']), len(gsnap['pins']))
    if not all(counts):
        reasons.append(f'Groww workbook inputs are not in the database ({counts[0]} seed facts, {counts[1]} '
                       f'assumptions, {counts[2]} pins; the run needs all three)')
    rows = [f for f in facts if f['status'] != 'rejected']
    reviewed = [f for f in rows if f['status'] == 'reviewed']
    staged = [f for f in rows if f['status'] != 'reviewed']
    if not switches:
        return reasons
    if not all(counts):
        if staged:
            reasons.append(f'Groww filing facts: {len(reviewed)} reviewed, {len(staged)} staged (ids {_ids(staged)}); '
                           'the switches need reviewed facts')
        return reasons
    # which facts the switches would read: build the overlay as if every fact were reviewed, then check each one
    lenient = [dict(f, status='reviewed') for f in rows]
    by_id = {f['fact_id']: f for f in rows}
    seed_facts = {(f['metric'], f['period_key']): f for f in gsnap['facts']}
    seed_assume = {a['key']: a for a in gsnap['assumptions']}
    try:
        overlay = GS.build_overlay(switches, lenient, seed_facts, seed_assume)
    except GS.SwitchError as e:
        reasons.append(f'Groww filing facts incomplete or inconsistent: {e}')
        return reasons
    need = {i for o in overlay.values() for i in o.fact_ids if isinstance(i, int)}
    bad = [by_id[i] for i in sorted(need) if by_id[i]['status'] != 'reviewed']
    if bad:
        what = ', '.join(f"{f['metric']} {f['period_key']}" + (f" [{f['segment']}]" if f.get('segment') else '')
                         + f" (fact {f['fact_id']}, {f['status']})" for f in bad[:12])
        reasons.append(f'{len(bad)} of the {len(need)} Groww facts the switches read are not reviewed: {what}'
                       + (f' ... and {len(bad) - 12} more' if len(bad) > 12 else ''))
    return reasons


class GrowwSnapshotReader(EngineSnapshotReader):
    """sb_* view for E5: the shared exchange data and calendar of the Angel snapshot, with Groww's own facts."""

    def __init__(self, snap, reviewed, gsnap, facts):
        super().__init__(snap, reviewed)
        self.tables['sb_disclosure_facts'] = [dict(f, broker_id=BROKER) for f in list(gsnap['facts']) + list(facts)]


def ir_inputs(reader, broker=BROKER):
    """(IR rows, exchange turnover) for g-h / g-i from the DB: the latest archived snapshot of sb_broker_daily plus the
    QTD rows of earlier days (the MTF book archive), and the exchange turnover of sb_market_daily. Raises IRError
    when the table is empty."""
    from ..engine import groww_ir as IR
    try:
        qtd = reader.table('sb_broker_daily', broker_id=broker, is_qtd=True)
    except KeyError:                       # a snapshot or test reader without the table
        raise IR.IRError('sb_broker_daily is not in this reader')
    if not qtd:
        raise IR.IRError('sb_broker_daily has no archived Groww IR rows (is the migration applied and the archive running?)')
    latest = max(str(r['snapshot_date'])[:10] for r in qtd)
    rows = reader.table('sb_broker_daily', broker_id=broker, snapshot_date=latest) + \
        [r for r in qtd if str(r['snapshot_date'])[:10] != latest]
    return IR.IR(rows), IR.Turnover.from_market_rows(reader.table('sb_market_daily'))


def live_run_groww(angel_run, gsnap, facts, switches=SWITCHES, ir=None, turnover=None):
    """Groww's live run from an Angel live run (its snapshot, reviewed facts, as-of date and calibration).

    gsnap: Groww snapshot (seed facts, assumptions, pins); facts: Groww filing facts of any status.
    switches: the published chain is SWITCHES ('abcdefg'); g-h / g-i (src/engine/groww_ir.py) are added only by the
    caller, with `ir` (groww_ir.IR) and, for g-h, `turnover` (groww_ir.Turnover).
    Raises GrowwRefused (nothing computed) unless every fact the switches read is reviewed."""
    from ..engine import groww as GW
    from ..engine import groww_switches as GS
    from ..engine.groww_bridge import live_period_rows
    from ..engine.inputs import Inputs

    if angel_run.get('broker', 'ANGELONE') != 'ANGELONE':
        raise ValueError('a Groww run needs an Angel One live run to borrow its calibration from')
    switches = GS.check(switches)
    if ('c' in switches) != ('c' in angel_run['switches']):
        raise ValueError(f"g-c is Angel switch c on the shared exchange series: Groww switches {sorted(switches)} "
                         f"and the Angel run's {angel_run['switches']!r} must agree on it")
    reasons = refusal_reasons(switches, gsnap, facts)
    if reasons:
        raise GrowwRefused(reasons)

    snap, a_reviewed, as_of = angel_run['snapshot'], angel_run['reviewed'], angel_run['as_of']
    if max(r['trade_date'] for r in snap['calendar']) != as_of:
        raise ValueError(f"Angel run as of {as_of} does not match its snapshot")
    reviewed = [f for f in facts if f['status'] == 'reviewed']
    I = Inputs(snap, ('c',) if 'c' in switches else (), a_reviewed if 'c' in switches else None)
    try:
        G = GW.GrowwInputs(gsnap, switches, reviewed, ir, turnover)
        res = GW.run(I, G, angel=dict(calib=angel_run['calib'], daily=angel_run['daily']))
    except GS.SwitchError as e:
        raise GrowwRefused([str(e)])
    except KeyError as e:
        raise GrowwRefused([f'a Groww input is missing: {e}'])

    c = res['calib']
    rates = {(s, q): p['take_rate'] for s, t in (('fo', c['fo_quarter']), ('cash', c['cash_quarter']),
                                                 ('comm', c.get('comm_quarter', {}))) for q, p in t.items()}
    inputs = load_inputs(GrowwSnapshotReader(snap, a_reviewed, gsnap, reviewed), BROKER,
                         dt.date.fromisoformat(as_of), angel_run['switches'])
    report = run_checks(inputs, take_rates=rates)

    book = I.series('mtf_industry', 'book_cr')
    mtf_gaps = {r['trade_date'] for r in snap['calendar'] if r['is_equity_day'] and r['trade_date'] not in book}
    cov_daily = {seg: {d: r for d, r in rows.items() if r['regime'] != 'not_live'} for seg, rows in res['daily'].items()}
    coverage(snap['calendar'], cov_daily, as_of, {'mtf': mtf_gaps})

    rows = live_period_rows(I, G, res)
    used = sorted({i for o in G.overlay.values() for i in o.fact_ids if isinstance(i, int)})
    note = (f"Calibration (contracts per order, trades per order, commodity market orders and take rates) is borrowed "
            f"from the Angel One live run of the same snapshot, as of {as_of}. {len(G.overlay)} Groww inputs come from "
            f"{len(used)} reviewed facts; the rest are the workbook's.")
    if G.switches & set(GS.EXTRA):
        note += (f" Optional IR switches {''.join(sorted(G.switches & set(GS.EXTRA)))} are on "
                 f"(archived Groww IR page, snapshot {ir.snapshot_date}).")
    return dict(as_of=as_of, switches=''.join(sorted(G.switches)), report=report, daily=res['daily'], calib=res['calib'],
                rows=rows, overrides=G.overlay, broker=BROKER, facts_reviewed=True, fact_ids=used, note=note)
