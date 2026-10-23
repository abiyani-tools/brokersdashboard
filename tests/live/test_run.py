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
    with pytest.raises(MissingCalibration, match='fo FY 2027 October'):
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
