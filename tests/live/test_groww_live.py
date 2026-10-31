"""Groww in the live run: dry run, refusal with unreviewed facts, publish rows, `--broker all` ordering."""
import json
import os

import pytest

from src.engine import groww_switches as GS
from src.live import cli, publish as publish_mod
from src.live.db import KEY_ENV, SupabaseWriter
from src.live.groww_run import GrowwRefused, groww_inputs, live_run_groww
from src.live.publish import PublishRefused, publish
from src.live.run import EngineSnapshotReader, live_run, report_md
from src.live.snapshot import build_snapshot

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SNAP = os.path.join(ROOT, 'snapshot', 'db_snapshot_2026-10-23.json')
REVIEWED = os.path.join(ROOT, 'snapshot', 'facts_reviewed_2026-10-23.json')
GSNAP = os.path.join(ROOT, 'snapshot', 'groww_snapshot_2026-10-23.json')
DB_INPUTS = os.path.join(ROOT, 'out', 'groww', 'db_inputs.json')
SECRET = 'sb_secret_TEST_ONLY_not_a_real_key'
PK = {'sb_calibration': ('run_id', 'segment', 'period_key', 'param'),
      'sb_daily_revenue': ('run_id', 'trade_date', 'segment'),
      'sb_summary_cells': ('run_id', 'panel', 'period_type', 'period_key', 'table_name', 'row_label')}


class Resp:
    def __init__(self, status=201):
        self.status_code, self.text = status, ''


class FakeSession:
    def __init__(self):
        self.calls = []

    def post(self, url, data, headers, timeout):
        self.calls.append(('POST', url.rsplit('/', 1)[1], json.loads(data)))
        return Resp()

    def patch(self, url, params, data, headers, timeout):
        self.calls.append(('PATCH', url.rsplit('/', 1)[1], json.loads(data)))
        return Resp(204)


class TablesReader:
    def __init__(self, tables):
        self.tables = tables

    def table(self, name, **eq):
        return [r for r in self.tables[name] if all(str(r.get(k)) == str(v) for k, v in eq.items())]


def groww_facts(status='reviewed'):
    return [dict(f, status=status) for f in GS.load_reviewed()]


def db_tables(groww_status='reviewed', with_inputs=True):
    """The sb_* tables as the DB would hold them: Angel One as in the snapshot, Groww's filing facts at
    `groww_status` and (with_inputs) the seed facts, assumptions and pins of out/groww/db_inputs.json."""
    snap, rev = json.load(open(SNAP)), json.load(open(REVIEWED))['facts']
    t = dict(EngineSnapshotReader(snap, rev).tables)
    t['sb_disclosure_facts'] = list(t['sb_disclosure_facts']) + groww_facts(groww_status)
    t['sb_assumptions'] = list(t['sb_assumptions'])
    if with_inputs:
        r = json.load(open(DB_INPUTS))
        t['sb_disclosure_facts'] += [dict(f, fact_id=900000 + i, doc_id=None) for i, f in enumerate(r['sb_disclosure_facts'])]
        t['sb_assumptions'] += r['sb_assumptions']
        t['sb_parity_pins'] = list(t['sb_parity_pins']) + r['sb_parity_pins']
    return t


@pytest.fixture(scope='module')
def angel():
    return live_run(SNAP, REVIEWED)


@pytest.fixture(scope='module')
def groww(angel):
    return live_run_groww(angel, json.load(open(GSNAP)), GS.load_reviewed())


@pytest.fixture
def writer_env(monkeypatch):
    monkeypatch.setenv(KEY_ENV, SECRET)


# ── the dry run ──
def test_groww_dry_run_from_the_angel_run(angel, groww):
    assert groww['broker'] == 'GROWW' and groww['switches'] == 'abcdefg' and groww['as_of'] == angel['as_of'] == '2026-10-21'
    assert not groww['report'].blocking, groww['report'].summary()
    get = {(r['panel'], r['row_label']): r['value'] for r in groww['rows'] if r['period_type'] in ('FY', 'Q', 'M')}
    assert get[('Consolidated', 'FY 2027')] == pytest.approx(20.007085, abs=5e-7)
    assert get[('Consolidated', 'Q2 FY 2027')] == pytest.approx(18.528112, abs=5e-7)
    assert get[('Consolidated', 'FY 2027 October')] == pytest.approx(23.617623, abs=5e-7)
    keys = [(r['panel'], r['period_type'], r['period_key'], r['table_name'], r['row_label']) for r in groww['rows']]
    assert len(keys) == len(set(keys)) and 'MTF (net)' not in {k[0] for k in keys}      # Groww: gross MTF only
    md = report_md(groww)
    assert md.startswith('# Live run (dry run) · GROWW') and 'borrowed from the Angel One live run' in md


def test_groww_uses_the_calibration_of_that_angel_run(angel, groww):
    """Contracts per order, trades per order and commodity take rates are Angel's own, from the same run."""
    from src.engine.inputs import months_of_quarter
    assert groww['calib']['cash_quarter']['Q2 FY 2027']['tpo'] == angel['calib']['cash_quarter']['Q2 FY 2027']['tpo']
    m = months_of_quarter('Q2 FY 2027')[0]
    d = '2026-07-01'
    assert groww['daily']['fo'][d]['cpo'] == angel['calib']['fo_month'][m]['cpo']
    assert groww['calib']['comm_quarter']['Q2 FY 2027']['take_rate'] == \
        angel['calib']['take_rates']['Q2 FY 2027']['take_rate_comm']


def test_groww_needs_an_angel_run_with_the_same_switch_c(angel):
    with pytest.raises(ValueError, match='g-c'):
        live_run_groww(angel, json.load(open(GSNAP)), GS.load_reviewed(), switches='abdefg')


# ── refusal ──
def test_staged_facts_are_refused_and_nothing_is_computed(angel):
    with pytest.raises(GrowwRefused) as e:
        live_run_groww(angel, json.load(open(GSNAP)), groww_facts('staged'))
    msg = str(e.value)
    assert 'not reviewed' in msg and 'staged' in msg and 'revmix_fo Q2 FY 2026' in msg
    # one reviewed fact missing from an otherwise reviewed set is named too
    facts = groww_facts()
    i = next(i for i, f in enumerate(facts) if f['metric'] == 'total_income' and f['period_key'] == 'Q2 FY 2027')
    facts[i] = dict(facts[i], status='staged')
    with pytest.raises(GrowwRefused, match=r'1 of the \d+ Groww facts .*total_income Q2 FY 2027'):
        live_run_groww(angel, json.load(open(GSNAP)), facts)


def test_a_run_without_the_workbook_inputs_in_the_db_is_refused(angel):
    gs = dict(json.load(open(GSNAP)), facts=[], assumptions=[], pins=[])
    with pytest.raises(GrowwRefused, match='not in the database'):
        live_run_groww(angel, gs, groww_facts())


def test_publish_refuses_a_groww_run_not_built_on_reviewed_facts(groww, writer_env):
    s = FakeSession()
    with pytest.raises(PublishRefused, match='reviewed'):
        publish(dict(groww, facts_reviewed=False), SupabaseWriter(session=s))
    assert s.calls == []


def test_db_run_with_staged_facts_fails_clearly_and_publishes_no_groww(capsys, monkeypatch, tmp_path, writer_env):
    monkeypatch.chdir(tmp_path)
    s = FakeSession()
    reader = TablesReader(db_tables('staged', with_inputs=False))      # today's DB: facts staged, no inputs
    rc = cli.main(['--db', '--publish', '--broker', 'GROWW'], lambda: reader, lambda: SupabaseWriter(session=s))
    out = capsys.readouterr().out
    assert rc == cli.REFUSED_EXIT and 'Groww not published' in out
    assert 'not in the database' in out and 'staged' in out and 'the switches need reviewed facts' in out
    assert s.calls == []                                                  # nothing written, Angel not published either
    assert 'refused' in open(tmp_path / 'out/live/2026-10-21/groww/report.md').read()


# ── the DB path ──
def test_build_snapshot_for_groww_takes_that_brokers_facts_and_the_shared_market_data():
    reader = TablesReader(db_tables('reviewed'))
    snap, reviewed = build_snapshot(reader, broker='GROWW')
    assert len(reviewed) == 103 + 0 and all(f['broker_id'] == 'GROWW' for f in reviewed + snap['facts'])
    assert len(snap['facts']) == 41                                       # the seed facts, not Angel's 477
    assert len(snap['calendar']) > 700 and snap['market_daily']
    gsnap, facts = groww_inputs(reader)
    assert (len(gsnap['facts']), len(gsnap['assumptions']), len(gsnap['pins']), len(facts)) == (41, 14, 10, 103)


def test_groww_from_db_tables_equals_groww_from_files(angel, groww, monkeypatch, tmp_path):
    from src.live.run import live_run_snapshot
    from src.live.snapshot import complete_through, trim
    reader = TablesReader(db_tables('reviewed'))
    snap, reviewed = build_snapshot(reader)
    snap = trim(snap, complete_through(snap)[0])
    a = live_run_snapshot(snap, reviewed)
    gsnap, facts = groww_inputs(reader)
    g = live_run_groww(a, gsnap, facts)
    assert a['rows'] == angel['rows'] and g['daily'] == groww['daily'] and g['rows'] == groww['rows']


# ── publishing ──
def test_publish_writes_groww_rows_with_the_brokers_id(groww, writer_env):
    s = FakeSession()
    run_id, counts = publish(groww, SupabaseWriter(session=s, chunk=100000), notes_extra='Angel One calibration from run X')
    first = s.calls[0]
    assert first[1] == 'sb_runs' and first[2][0]['broker_id'] == 'GROWW' and first[2][0]['mode'] == 'live'
    assert 'GROWW switches g-abcdefg' in first[2][0]['notes'] and 'Angel One calibration from run X' in first[2][0]['notes']
    assert s.calls[-1][0] == 'PATCH' and s.calls[-1][2]['status'] == 'success'
    for table, key in PK.items():
        rows = [r for c in s.calls if c[0] == 'POST' and c[1] == table for r in c[2]]
        assert rows and {r['broker_id'] for r in rows} == {'GROWW'} and {r['run_id'] for r in rows} == {run_id}, table
        keys = [tuple(r[k] for k in key) for r in rows]
        assert len(keys) == len(set(keys)), table
    daily = [r for c in s.calls if c[1] == 'sb_daily_revenue' for r in c[2]]
    assert {r['regime'] for r in daily} <= {'actual', 'projected'}
    assert {r['segment'] for r in daily} == {'fo', 'cash', 'comm', 'mtf_gross'}                # no net MTF for Groww
    assert min(r['trade_date'] for r in daily if r['segment'] == 'fo') == '2025-04-01'          # before first live: no rows
    calib = [r for c in s.calls if c[1] == 'sb_calibration' for r in c[2]]
    assert {r['period_type'] for r in calib} == {'Q'} and {r['regime'] for r in calib} <= {'actual', 'projected'}
    assert {(r['segment'], r['param']) for r in calib} >= {('fo', 'take_rate_used'), ('cash', 'share'), ('mtf', 'share'),
                                                          ('comm', 'take_rate_used')}
    assert counts['sb_summary_cells'] == len(groww['rows'])


def test_angel_rows_still_carry_angelone(angel, writer_env):
    s = FakeSession()
    publish(angel, SupabaseWriter(session=s, chunk=100000))
    for c in s.calls:
        if c[0] == 'POST':
            assert {r['broker_id'] for r in c[2]} == {'ANGELONE'}, c[1]


# ── the command line ──
def test_parse():
    o = cli.parse(['--broker', 'groww', '--db'])
    assert o['broker'] == 'GROWW' and o['db'] and not o['publish']
    assert cli.parse(['--broker=all'])['broker'] == 'ALL' and cli.parse([])['broker'] == 'ANGELONE'
    o = cli.parse(['a.json', 'b.json', '--groww-facts', 'g.json'])
    assert (o['snapshot'], o['reviewed'], o['groww_facts']) == ('a.json', 'b.json', 'g.json')
    with pytest.raises(SystemExit):
        cli.parse(['--broker', 'zerodha'])


def test_dry_run_from_files_writes_groww_beside_angel(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    rc = cli.main(['--broker', 'GROWW', SNAP, REVIEWED, '--groww-snapshot', GSNAP, '--groww-facts', GS.REVIEWED])
    out = capsys.readouterr().out
    assert rc == 0 and '· GROWW' in out and 'Nothing was written to the database' in out
    assert (tmp_path / 'out/live/2026-10-21/groww/summary_rows.json').exists()
    assert not (tmp_path / 'out/live/2026-10-21/report.md').exists()      # --broker GROWW does not write Angel's report


def test_broker_all_runs_angel_then_groww_from_it_then_publishes_both_in_order(monkeypatch, tmp_path, writer_env):
    from src.live import groww_run, run as run_mod
    monkeypatch.chdir(tmp_path)
    events, seen = [], {}
    real_angel, real_groww, real_publish = run_mod.live_run_snapshot, groww_run.live_run_groww, publish_mod.publish

    def angel_(*a, **k):
        r = real_angel(*a, **k)
        seen['angel'] = r
        events.append('angel run')
        return r

    def groww_(angel_run, *a, **k):
        assert angel_run is seen['angel']                                  # built from that very Angel run
        events.append('groww run')
        return real_groww(angel_run, *a, **k)

    def publish_(run, writer, notes_extra=''):
        events.append('publish ' + run.get('broker', 'ANGELONE'))
        if run['broker'] == 'GROWW':
            assert 'Angel One calibration from run' in notes_extra
        return real_publish(run, writer, notes_extra)

    monkeypatch.setattr(run_mod, 'live_run_snapshot', angel_)
    monkeypatch.setattr(groww_run, 'live_run_groww', groww_)
    monkeypatch.setattr(publish_mod, 'publish', publish_)
    s = FakeSession()
    reader = TablesReader(db_tables('reviewed'))
    rc = cli.main(['--db', '--publish', '--broker', 'all'], lambda: reader, lambda: SupabaseWriter(session=s, chunk=100000))
    assert rc == 0 and events == ['angel run', 'groww run', 'publish ANGELONE', 'publish GROWW']
    runs = [c[2][0] for c in s.calls if c[0] == 'POST' and c[1] == 'sb_runs']
    assert [r['broker_id'] for r in runs] == ['ANGELONE', 'GROWW'] and len({r['run_id'] for r in runs}) == 2
    assert [c[2]['status'] for c in s.calls if c[0] == 'PATCH'] == ['success', 'success']
    # each child row follows its own run row
    order = [(c[1], c[2][0].get('broker_id') if c[0] == 'POST' else None) for c in s.calls if c[0] == 'POST']
    assert order.index(('sb_runs', 'GROWW')) > max(i for i, (t, b) in enumerate(order) if b == 'ANGELONE')
    assert (tmp_path / 'out/live/2026-10-21/groww/report.md').read_text().startswith('# Live run · GROWW')


def test_broker_all_publishes_angel_when_groww_is_refused(monkeypatch, tmp_path, capsys, writer_env):
    monkeypatch.chdir(tmp_path)
    s = FakeSession()
    reader = TablesReader(db_tables('staged'))
    rc = cli.main(['--db', '--publish', '--broker', 'all'], lambda: reader, lambda: SupabaseWriter(session=s, chunk=100000))
    out = capsys.readouterr().out
    assert rc == 0                                                         # a warning, not a failure
    assert 'WARNING Groww not published' in out and 'staged' in out
    runs = [c[2][0] for c in s.calls if c[0] == 'POST' and c[1] == 'sb_runs']
    assert [r['broker_id'] for r in runs] == ['ANGELONE']
    assert [c[2]['status'] for c in s.calls if c[0] == 'PATCH'] == ['success']


def test_broker_all_in_github_actions_emits_a_warning_annotation(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    reader = TablesReader(db_tables('staged'))
    assert cli.main(['--db', '--broker', 'all'], lambda: reader) == 0
    assert '::warning title=Groww not published::' in capsys.readouterr().out


def test_a_groww_error_other_than_a_refusal_fails_the_job_after_angel_published(monkeypatch, tmp_path, writer_env):
    from src.live import groww_run
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(groww_run, 'live_run_groww', lambda *a, **k: 1 / 0)
    s = FakeSession()
    reader = TablesReader(db_tables('reviewed'))
    rc = cli.main(['--db', '--publish', '--broker', 'all'], lambda: reader, lambda: SupabaseWriter(session=s, chunk=100000))
    assert rc == 1
    assert [c[2][0]['broker_id'] for c in s.calls if c[0] == 'POST' and c[1] == 'sb_runs'] == ['ANGELONE']
