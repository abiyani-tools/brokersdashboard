import datetime as dt
import os

import pytest

from src.live.integrity import KNOWN_ISSUES, series_issues
from src.live.loader import Volume
from src.live.periods import Calendar, MissingCalibration
from src.live.run import coverage, live_run

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SNAP = os.path.join(ROOT, 'snapshot', 'db_snapshot_2026-10-23.json')
REVIEWED = os.path.join(ROOT, 'snapshot', 'facts_reviewed_2026-10-23.json')


def _cal(days, special=()):
    return [{'trade_date': d, 'is_equity_day': True, 'is_mcx_day': True,
             'special_session': 'muhurat' if d in special else None} for d in days]


def test_coverage_makes_a_dropped_day_loud():
    days = ['2026-10-19', '2026-10-20', '2026-10-21']
    daily = {s: {d: {} for d in days} for s in ('fo', 'cash', 'comm', 'mtf')}
    assert coverage(_cal(days), daily, '2026-10-21')
    del daily['fo']['2026-10-20']
    with pytest.raises(MissingCalibration, match='fo 2026-10-20'):
        coverage(_cal(days), daily, '2026-10-21')
    # an MTF day whose input is missing (E5 warning) is tolerated; any other MTF gap is not
    daily['fo']['2026-10-20'] = {}
    del daily['mtf']['2026-10-19']
    assert coverage(_cal(days), daily, '2026-10-21', {'mtf': {'2026-10-19'}})


def test_special_sessions_are_not_jump_tested():
    start = dt.date(2026, 6, 1)
    days = [start + dt.timedelta(i) for i in range(45) if (start + dt.timedelta(i)).weekday() < 5][:30]
    cal = Calendar.from_rows(_cal([d.isoformat() for d in days], special={days[20].isoformat()}))
    vals = [100 + i % 7 for i in range(30)]
    vals[20] = 5                                          # a thin Muhurat-like session
    series = [Volume(d, 'nse_cash:trades', float(v), 'ok', 'x') for d, v in zip(days, vals)]
    assert not [i for i in series_issues('nse_cash:trades', series, cal, days[-1], 'error') if i.check == 'jump']


def test_known_issues_state_a_reason():
    assert all(len(reason) > 40 for reason in KNOWN_ISSUES.values())


@pytest.fixture(scope='module')
def run():
    return live_run(SNAP, REVIEWED)


def test_live_dry_run_on_the_snapshot(run):
    rep = run['report']
    assert not rep.blocking, rep.summary()
    assert run['switches'] == 'abcdefghi' and run['as_of'] == '2026-10-21'
    # known exceptions are reported, not dropped
    assert {i.dates[0].isoformat() for i in rep.find('jump', 'mcx:contracts', 'info') if not i.source} == {'2025-01-01', '2025-02-01'}
    # the IO / SO split is audit-only: no blocking 'missing' for it
    assert not rep.find(key='nse_fo:io_contracts', severity='error')
    keys = [(r['panel'], r['period_type'], r['period_key'], r['table_name'], r['row_label']) for r in run['rows']]
    assert len(keys) == len(set(keys)) and 'MTF (net)' in {k[0] for k in keys}


def test_live_headline_equals_the_cumulative_bridge(run):
    get = {(r['panel'], r['row_label']): r['value'] for r in run['rows'] if r['period_type'] in ('FY', 'Q', 'M')}
    assert get[('Consolidated', 'FY 2027')] == pytest.approx(17.510302, abs=5e-7)
    assert get[('Consolidated', 'Q2 FY 2027')] == pytest.approx(16.495983, abs=5e-7)
    assert get[('Consolidated', 'FY 2027 October')] == pytest.approx(20.216017, abs=5e-7)


def test_new_month_after_the_workbook_grid_is_calibrated_in_live_mode(tmp_path):
    """E1 for the daily job: November 2026 days (after the workbook's Oct-26 grid) get revenue, not dropped."""
    import json
    from src.engine import daily
    from src.engine.inputs import load_snapshot
    snap = json.load(open(SNAP))
    new = ['2026-11-02', '2026-11-03']
    for d in new:
        snap['calendar'].append({'trade_date': d, 'fy': 'FY 2027', 'q_fy': 'Q3 FY 2027', 'fy_month': 'FY 2027 November',
                                 'weekday': 'Monday' if d.endswith('02') else 'Tuesday', 'is_equity_day': True,
                                 'is_mcx_day': True, 'special_session': None, 'note': 'synthetic (test)'})
    last = {(r['dataset'], r['metric']): r for r in snap['market_daily'] if r['trade_date'] == '2026-10-19'}
    for d in new:                                         # test-only volumes: copy 19 Oct
        snap['market_daily'] += [dict(r, trade_date=d) for r in last.values()]
    p = tmp_path / 'snap_nov.json'
    p.write_text(json.dumps(snap))
    run = live_run(str(p), REVIEWED)
    assert run['as_of'] == '2026-11-03'                    # coverage passed: no day dropped
    for seg in ('fo', 'cash', 'comm', 'mtf'):
        assert all(d in run['daily'][seg] and run['daily'][seg][d]['regime'] == 'projected' for d in new), seg
    assert 'FY 2027 November' in {r['period_key'] for r in run['rows'] if r['period_type'] == 'M'}
    # parity mode keeps the workbook's grid (ends October 2026)
    assert '2026-11-02' not in daily.run(load_snapshot(str(p)))['daily']['fo']


def test_snapshot_built_from_sb_tables_gives_the_same_engine_run():
    """The DB path (sb_* tables -> build_snapshot -> engine) equals the snapshot-file path."""
    import json
    from src.engine import daily
    from src.engine.inputs import Inputs
    from src.live.run import EngineSnapshotReader
    from src.live.snapshot import build_snapshot
    snap = json.load(open(SNAP))
    reviewed = json.load(open(REVIEWED))['facts']
    built, rev = build_snapshot(EngineSnapshotReader(snap, reviewed))
    assert len(rev) == 178 and len(built['facts']) == 477
    for sw in ('', 'abcdefghi'):
        a = daily.run(Inputs(snap, sw, reviewed if sw else None))['daily']
        b = daily.run(Inputs(built, sw, rev if sw else None))['daily']
        assert a == b, sw
