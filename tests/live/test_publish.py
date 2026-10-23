import json
import os

import pytest

from src.live.db import KEY_ENV, SupabaseWriter
from src.live.integrity import Issue, Report
from src.live.publish import PublishRefused, publish
from src.live.run import live_run
from src.live.snapshot import complete_through, trim

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SNAP = os.path.join(ROOT, 'snapshot', 'db_snapshot_2026-10-23.json')
REVIEWED = os.path.join(ROOT, 'snapshot', 'facts_reviewed_2026-10-23.json')
SECRET = 'sb_secret_TEST_ONLY_not_a_real_key'
PK = {'sb_calibration': ('run_id', 'segment', 'period_key', 'param'),
      'sb_daily_revenue': ('run_id', 'trade_date', 'segment'),
      'sb_summary_cells': ('run_id', 'panel', 'period_type', 'period_key', 'table_name', 'row_label')}


class Resp:
    def __init__(self, status=201, text=''):
        self.status_code, self.text = status, text


class FakeSession:
    def __init__(self, fail_on=None):
        self.calls, self.fail_on = [], fail_on

    def post(self, url, data, headers, timeout):
        table = url.rsplit('/', 1)[1]
        self.calls.append(('POST', table, json.loads(data), headers))
        return Resp(500, 'boom') if table == self.fail_on else Resp(201)

    def patch(self, url, params, data, headers, timeout):
        self.calls.append(('PATCH', url.rsplit('/', 1)[1], json.loads(data), params))
        return Resp(204)


@pytest.fixture(scope='module')
def run():
    return live_run(SNAP, REVIEWED)


@pytest.fixture
def writer_env(monkeypatch):
    monkeypatch.setenv(KEY_ENV, SECRET)


def test_publish_writes_the_run_in_order(run, writer_env):
    s = FakeSession()
    run_id, counts = publish(run, SupabaseWriter(session=s, chunk=1000))
    tables = [c[1] for c in s.calls]
    assert tables[0] == 'sb_runs' and tables[-1] == 'sb_runs'
    assert s.calls[0][2][0]['status'] == 'running' and s.calls[0][2][0]['mode'] == 'live'
    assert s.calls[0][2][0]['as_of_date'] == '2026-10-21'
    assert s.calls[-1][0] == 'PATCH' and s.calls[-1][2]['status'] == 'success' and s.calls[-1][3] == {'run_id': f'eq.{run_id}'}
    assert counts['sb_summary_cells'] == len(run['rows'])
    for table, key in PK.items():                     # rows satisfy each table's primary key
        rows = [r for c in s.calls if c[0] == 'POST' and c[1] == table for r in c[2]]
        assert rows and all(r['run_id'] == run_id for r in rows)
        keys = [tuple(r[k] for k in key) for r in rows]
        assert len(keys) == len(set(keys)), table
    assert {r['regime'] for c in s.calls if c[1] == 'sb_daily_revenue' for r in c[2]} <= {'actual', 'projected'}


def test_publish_chunks_large_tables(run, writer_env):
    s = FakeSession()
    publish(run, SupabaseWriter(session=s, chunk=500))
    sizes = [len(c[2]) for c in s.calls if c[0] == 'POST' and c[1] == 'sb_daily_revenue']
    assert len(sizes) > 1 and max(sizes) <= 500


def test_a_blocking_run_is_not_published(run, writer_env):
    blocked = dict(run, report=Report([Issue('frozen', 'bse_fo:contracts', 'error', (), 'test')]))
    s = FakeSession()
    with pytest.raises(PublishRefused):
        publish(blocked, SupabaseWriter(session=s))
    assert s.calls == []


def test_a_failed_insert_marks_the_run_failed(run, writer_env):
    s = FakeSession(fail_on='sb_daily_revenue')
    with pytest.raises(RuntimeError, match='sb_daily_revenue'):
        publish(run, SupabaseWriter(session=s))
    assert s.calls[-1][0] == 'PATCH' and s.calls[-1][2]['status'] == 'failed'
    assert SECRET not in json.dumps([c[2] for c in s.calls])


def test_complete_through_names_the_limiting_series():
    snap = json.load(open(SNAP))
    assert complete_through(snap)[0] == '2026-10-21'
    snap['market_daily'] = [r for r in snap['market_daily']
                            if not (r['dataset'] == 'nse_cash' and r['trade_date'] > '2026-10-16')]
    assert complete_through(snap) == ('2026-10-16', 'nse_cash:trades')
    t = trim(snap, '2026-10-16')
    assert max(r['trade_date'] for r in t['calendar']) == '2026-10-16'
    assert max(r['trade_date'] for r in t['market_daily']) == '2026-10-16'
