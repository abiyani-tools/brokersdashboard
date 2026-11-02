"""MOSL in the live run: dry run and as-of date, E5 on MOSL's own series (zero = suspect), refusal, publish rows,
`--broker all` ordering and the independence of Angel One and Groww."""
import json
import os

import pytest

from src.engine import mosl_switches as MS
from src.live import cli, publish as publish_mod
from src.live.db import KEY_ENV, SupabaseWriter
from src.live.groww_run import groww_inputs
from src.live.loader import MOSL_MARKET_KEYS, select_volumes
from src.live.mosl_run import MoslRefused, live_run_mosl, mosl_inputs
from src.live.publish import PublishRefused, publish, rows_for
from src.live.run import EngineSnapshotReader, report_md
from src.live.snapshot import complete_through, complete_through_mosl, mosl_lake_rows, mosl_lake_series

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SNAP = os.path.join(ROOT, 'snapshot', 'db_snapshot_2026-10-23.json')
REVIEWED = os.path.join(ROOT, 'snapshot', 'facts_reviewed_2026-10-23.json')
MSNAP = os.path.join(ROOT, 'snapshot', 'mosl_snapshot_2026-10-23.json')
LAKE = os.path.join(ROOT, 'snapshot', 'mosl_lake_2026-11-02.json')
LAKE_DB = os.path.join(ROOT, 'snapshot', 'mosl_lake_db_2026-11-02.json')
GDB_INPUTS = os.path.join(ROOT, 'out', 'groww', 'db_inputs.json')
MDB_INPUTS = os.path.join(ROOT, 'out', 'mosl', 'db_inputs.json')
FILES = ['--mosl-snapshot', MSNAP, '--mosl-facts', MS.REVIEWED, '--mosl-lake', LAKE]
SECRET = 'sb_secret_TEST_ONLY_not_a_real_key'


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


def lake_rows(path=LAKE):
    return [dict(trade_date=d, dataset=k.split('/')[0], metric=k.split('/')[1], value=v, status=st,
                 source='exchangesdash_json', unit='count', note=None)
            for k, rows in json.load(open(path))['series'].items() for d, v, st in rows]


def mosl_facts(status='reviewed'):
    return [dict(f, status=status) for f in MS.load_reviewed()]


def db_tables(mosl_status='reviewed', with_inputs=True, lake=LAKE):
    """The sb_* tables as the DB would hold them: Angel One and Groww as in their tests, MOSL's filing facts at
    `mosl_status`, and (with_inputs) the seed facts, assumptions and pins of out/mosl/db_inputs.json."""
    from tests.live.test_groww_live import db_tables as groww_db_tables
    t = groww_db_tables('reviewed')
    t['sb_market_daily'] = list(t['sb_market_daily']) + lake_rows(lake)
    t['sb_disclosure_facts'] = list(t['sb_disclosure_facts']) + [dict(f, fact_id=846 + i) for i, f in enumerate(mosl_facts(mosl_status))]
    if with_inputs:
        r = json.load(open(MDB_INPUTS))
        t['sb_disclosure_facts'] += [dict(f, fact_id=900500 + i, doc_id=None) for i, f in enumerate(r['sb_disclosure_facts'])]
        t['sb_assumptions'] = list(t['sb_assumptions']) + r['sb_assumptions']
        t['sb_parity_pins'] = list(t['sb_parity_pins']) + r['sb_parity_pins']
    return t


@pytest.fixture(scope='module')
def shared():
    return json.load(open(SNAP))


@pytest.fixture(scope='module')
def msnap():
    return json.load(open(MSNAP))


@pytest.fixture(scope='module')
def mosl(shared, msnap):
    return live_run_mosl(shared, msnap, mosl_facts(), lake_rows())


@pytest.fixture
def writer_env(monkeypatch):
    monkeypatch.setenv(KEY_ENV, SECRET)


# ── the dry run, its as-of date and what limits it ──
def test_mosl_dry_run_headline_and_as_of(mosl):
    assert mosl['broker'] == 'MOSL' and mosl['switches'] == 'abcdef' and mosl['as_of'] == '2026-10-21'
    assert mosl['limiting'] == 'mcx:contracts' and not mosl['report'].blocking, mosl['report'].summary()
    get = {(r['panel'], r['row_label']): r['value'] for r in mosl['rows'] if r['period_type'] in ('FY', 'Q', 'M')}
    assert get[('Consolidated', 'FY 2027')] == pytest.approx(8.718295, abs=5e-7)
    assert get[('Consolidated', 'Q2 FY 2027')] == pytest.approx(8.967060, abs=5e-7)
    assert get[('Consolidated', 'FY 2027 October')] == pytest.approx(9.876513, abs=5e-7)
    keys = [(r['panel'], r['period_type'], r['period_key'], r['table_name'], r['row_label']) for r in mosl['rows']]
    assert len(keys) == len(set(keys)) and 'MTF (net)' not in {k[0] for k in keys}
    md = report_md(mosl)
    assert md.startswith('# Live run (dry run) · MOSL') and 'Switches: m-abcdef' in md and 'net brokerage + MTF NII' in md
    assert 'SOURCE NEEDED: MOSL does not publish an MTF yield' in md


def test_mosl_matches_the_bridge_chain(mosl):
    """The live run is the engine chain a-f on the same series: the rows equal the bridge's after-f numbers."""
    from src.engine import mosl_bridge as B
    t = B.adr(*B.run_switches('abcdef'))
    get = {(r['period_key'], r['panel']): r['value'] for r in mosl['rows'] if r['row_label'] == r['period_key']}
    for (p, k, panel), v in t.items():
        if (k, panel) in get and get[(k, panel)] is not None:
            assert get[(k, panel)] == pytest.approx(v, rel=1e-12), (k, panel)


def test_mosl_as_of_is_the_last_day_its_own_inputs_are_complete(shared):
    """Database as read on 2 Nov 2026: io_contracts zero on 12-15 Oct and absent after. MOSL stops at the last ok day."""
    lake = mosl_lake_series(lake_rows(LAKE_DB))
    assert complete_through_mosl(shared, lake) == ('2026-10-09', 'nse_fo:io_contracts')
    assert complete_through_mosl(shared, mosl_lake_series(lake_rows(LAKE))) == ('2026-10-21', 'mcx:contracts')
    assert complete_through(shared)[0] == '2026-10-21'                       # Angel One's own rule is unchanged


def test_e5_flags_the_zero_io_days_and_the_missing_days_instead_of_averaging_them(shared, msnap):
    run = live_run_mosl(shared, msnap, mosl_facts(), lake_rows(LAKE_DB), as_of='2026-10-21')
    assert run['report'].blocking
    io = {i.check: i for i in run['report'].find(key='nse_fo:io_contracts', severity='error')}
    assert [d.isoformat() for d in io['zero'].dates] == ['2026-10-12', '2026-10-13', '2026-10-14', '2026-10-15']
    assert [d.isoformat() for d in io['status'].dates] == ['2026-10-12', '2026-10-13', '2026-10-14', '2026-10-15']
    assert [d.isoformat() for d in io['missing'].dates][0] == '2026-10-16' and len(io['missing'].dates) == 3   # 16, 19, 21
    assert 'not evaluated' in run['coverage']
    for d in ('2026-10-12', '2026-10-13', '2026-10-14', '2026-10-15', '2026-10-16'):
        assert d not in run['daily']['fo']                                  # no row, never a zero
    # the database's own zero on BSE cash (2026-06-15, status ok) is flagged too: turnover zero is suspect for MOSL
    zeros = run['report'].find(check='zero', key='bse_cash:turnover_cr', severity='error')
    assert [d.isoformat() for i in zeros for d in i.dates] == ['2026-06-15']
    assert '2026-06-15' not in run['daily']['cash']


def test_dry_run_as_of_the_db_state_is_blocked_by_the_bse_cash_zero(shared, msnap):
    run = live_run_mosl(shared, msnap, mosl_facts(), lake_rows(LAKE_DB))
    assert run['as_of'] == '2026-10-09' and run['limiting'] == 'nse_fo:io_contracts' and run['report'].blocking
    assert [i.key for i in run['report'].errors] == ['bse_cash:turnover_cr']


def test_a_zero_turnover_is_suspect_even_though_its_status_is_ok(shared, msnap):
    rows = lake_rows(LAKE)
    for r in rows:
        if (r['metric'], r['trade_date']) == ('turnover_cr', '2026-08-03') and r['dataset'] == 'nse_cash':
            r['value'] = 0.0
    run = live_run_mosl(shared, msnap, mosl_facts(), rows)
    assert run['report'].blocking and run['report'].find(check='zero', key='nse_cash:turnover_cr', severity='error')
    assert '2026-08-03' not in run['daily']['cash']


def test_the_workbook_copy_of_a_mosl_series_is_never_read():
    rows = lake_rows() + [dict(trade_date='2026-06-10', dataset='nse_cash', metric='turnover_cr', value=1.0, status='ok',
                               source='excel_seed')]
    from src.live.loader import _volume
    vols = select_volumes([_volume(r) for r in rows], 'lake_ok', ['nse_cash:turnover_cr'])
    v = {x.date.isoformat(): x for x in vols['nse_cash:turnover_cr']}['2026-06-10']
    assert v.source == 'exchangesdash_json' and v.value > 100
    assert MOSL_MARKET_KEYS == ('nse_fo:io_contracts', 'bse_fo:contracts', 'nse_cash:turnover_cr', 'bse_cash:turnover_cr',
                                'mcx:contracts', 'mtf_industry:book_cr')


# ── refusal ──
def test_staged_facts_are_refused_and_nothing_is_computed(shared, msnap):
    with pytest.raises(MoslRefused) as e:
        live_run_mosl(shared, msnap, mosl_facts('staged'), lake_rows())
    assert 'not reviewed' in str(e.value) and 'adto_cash Q1 FY 2025' in str(e.value)
    facts = mosl_facts()
    i = next(i for i, f in enumerate(facts) if f['metric'] == 'mtf_book' and f['period_key'] == 'Q2 FY 2027')
    facts[i] = dict(facts[i], status='staged')
    with pytest.raises(MoslRefused, match=r'1 of the \d+ MOSL facts .*mtf_book Q2 FY 2027'):
        live_run_mosl(shared, msnap, facts, lake_rows())


def test_a_run_without_the_workbook_inputs_in_the_db_is_refused(shared, msnap):
    with pytest.raises(MoslRefused, match='not in the database'):
        live_run_mosl(shared, dict(msnap, facts=[], assumptions=[], pins=[]), mosl_facts(), lake_rows())


def test_a_run_without_the_labelled_yield_assumption_is_refused(shared, msnap):
    ms = dict(msnap, assumptions=[a for a in msnap['assumptions'] if a['key'] != MS.YIELD_ASSUMPTION])
    with pytest.raises(MoslRefused, match='mtf_nii_yield_carry'):
        live_run_mosl(shared, ms, mosl_facts(), lake_rows())


# ── the DB path ──
def test_mosl_inputs_from_the_db_tables_and_the_db_seed_rows_equal_the_snapshot(shared, msnap):
    reader = TablesReader(db_tables())
    snap, facts = mosl_inputs(reader)
    assert (len(snap['facts']), len(snap['assumptions']), len(snap['pins']), len(facts)) == (101, 12, 11, 290)
    assert all(f['broker_id'] == 'MOSL' for f in snap['facts'] + facts)
    run = live_run_mosl(shared, snap, facts, mosl_lake_rows(reader.table('sb_market_daily')))
    again = live_run_mosl(shared, msnap, mosl_facts(), lake_rows())
    assert run['rows'] == again['rows'] and run['daily'] == again['daily']


# ── publishing ──
def test_publish_writes_mosl_rows_with_the_brokers_id(mosl, writer_env):
    s = FakeSession()
    run_id, counts = publish(mosl, SupabaseWriter(session=s, chunk=100000), notes_extra='MOSL complete through 2026-10-21')
    first = s.calls[0]
    assert first[1] == 'sb_runs' and first[2][0]['broker_id'] == 'MOSL' and first[2][0]['mode'] == 'live'
    assert 'MOSL switches m-abcdef' in first[2][0]['notes'] and first[2][0]['as_of_date'] == '2026-10-21'
    assert s.calls[-1][0] == 'PATCH' and s.calls[-1][2]['status'] == 'success'
    pk = {'sb_calibration': ('run_id', 'segment', 'period_key', 'param'),
          'sb_daily_revenue': ('run_id', 'trade_date', 'segment'),
          'sb_summary_cells': ('run_id', 'panel', 'period_type', 'period_key', 'table_name', 'row_label')}
    for table, key in pk.items():
        rows = [r for c in s.calls if c[0] == 'POST' and c[1] == table for r in c[2]]
        assert rows and {r['broker_id'] for r in rows} == {'MOSL'} and {r['run_id'] for r in rows} == {run_id}, table
        keys = [tuple(r[k] for k in key) for r in rows]
        assert len(keys) == len(set(keys)), table
    daily = [r for c in s.calls if c[1] == 'sb_daily_revenue' for r in c[2]]
    assert {r['segment'] for r in daily} == {'fo', 'cash', 'comm', 'mtf_nii'} and {r['regime'] for r in daily} <= {'actual', 'projected'}
    d = {(r['trade_date'], r['segment']): r for r in daily}
    assert d[('2026-10-21', 'fo')]['revenue_cr'] == pytest.approx(mosl['daily']['fo']['2026-10-21']['rev_mn'] / 10)
    assert d[('2026-10-21', 'cash')]['revenue_cr'] == pytest.approx(mosl['daily']['cash']['2026-10-21']['rev_cr'])
    assert d[('2026-10-21', 'fo')]['regime'] == 'projected' and d[('2026-09-30', 'fo')]['regime'] == 'actual'
    assert all(r['orders_mn'] is None for r in daily)
    calib = [r for c in s.calls if c[1] == 'sb_calibration' for r in c[2]]
    assert {(r['segment'], r['param']) for r in calib} >= {('fo', 'gross_rs_per_contract'), ('cash', 'take_rate_used'),
                                                          ('comm', 'take_rate_used'), ('mtf', 'nii_yield'), ('fo', 'net_gross')}
    assert counts['sb_summary_cells'] == len(mosl['rows'])


def test_publish_refuses_a_run_not_built_on_reviewed_facts_or_blocked_by_e5(mosl, shared, msnap, writer_env):
    s = FakeSession()
    with pytest.raises(PublishRefused, match='reviewed'):
        publish(dict(mosl, facts_reviewed=False), SupabaseWriter(session=s))
    blocked = live_run_mosl(shared, msnap, mosl_facts(), lake_rows(LAKE_DB))
    with pytest.raises(PublishRefused, match='E5'):
        publish(blocked, SupabaseWriter(session=s))
    assert s.calls == []


def test_rows_for_other_brokers_are_unchanged(mosl):
    assert rows_for(mosl, 'x')['sb_daily_revenue'][0]['broker_id'] == 'MOSL'


# ── the command line ──
def test_parse():
    o = cli.parse(['--broker', 'mosl', '--db', '--mosl-lake', 'l.json'])
    assert o['broker'] == 'MOSL' and o['db'] and o['mosl_lake'] == 'l.json'
    assert cli.parse([])['mosl_snapshot'].endswith('mosl_snapshot_2026-10-23.json')
    assert cli.parse(['--broker=all'])['broker'] == 'ALL'
    with pytest.raises(SystemExit):
        cli.parse(['--broker', 'zerodha'])


def test_dry_run_from_files_writes_mosl_under_its_own_as_of(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    rc = cli.main(['--broker', 'MOSL', SNAP, REVIEWED] + FILES)
    out = capsys.readouterr().out
    assert rc == 0 and '· MOSL' in out and 'Nothing was written to the database' in out
    assert 'MOSL complete through 2026-10-21 (limited by mcx:contracts)' in out
    assert 'Angel One live run' not in out                                  # MOSL needs no Angel run
    assert (tmp_path / 'out/live/2026-10-21/mosl/summary_rows.json').exists()
    assert not (tmp_path / 'out/live/2026-10-21/report.md').exists()


def test_db_state_dry_run_has_an_earlier_as_of_and_is_blocked(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    rc = cli.main(['--broker', 'MOSL', SNAP, REVIEWED, '--mosl-snapshot', MSNAP, '--mosl-facts', MS.REVIEWED, '--mosl-lake', LAKE_DB])
    out = capsys.readouterr().out
    assert rc == 1 and 'as of 2026-10-09' in out and 'E5: BLOCKING' in out and 'WARNING MOSL not published' in out
    assert (tmp_path / 'out/live/2026-10-09/mosl/report.md').exists()


def test_broker_all_runs_angel_groww_then_mosl_and_publishes_in_that_order(monkeypatch, tmp_path, writer_env):
    from src.live import groww_run, mosl_run, run as run_mod
    monkeypatch.chdir(tmp_path)
    events = []
    real_angel, real_groww, real_mosl, real_publish = (run_mod.live_run_snapshot, groww_run.live_run_groww,
                                                       mosl_run.live_run_mosl, publish_mod.publish)

    def angel_(*a, **k):
        events.append('angel run')
        return real_angel(*a, **k)

    def groww_(*a, **k):
        events.append('groww run')
        return real_groww(*a, **k)

    def mosl_(*a, **k):
        events.append('mosl run')
        return real_mosl(*a, **k)

    def publish_(run, writer, notes_extra=''):
        events.append('publish ' + run.get('broker', 'ANGELONE'))
        return real_publish(run, writer, notes_extra)

    monkeypatch.setattr(run_mod, 'live_run_snapshot', angel_)
    monkeypatch.setattr(groww_run, 'live_run_groww', groww_)
    monkeypatch.setattr(mosl_run, 'live_run_mosl', mosl_)
    monkeypatch.setattr(publish_mod, 'publish', publish_)
    s = FakeSession()
    reader = TablesReader(db_tables())
    rc = cli.main(['--db', '--publish', '--broker', 'all'], lambda: reader, lambda: SupabaseWriter(session=s, chunk=100000))
    assert rc == 0 and events == ['angel run', 'groww run', 'mosl run', 'publish ANGELONE', 'publish GROWW', 'publish MOSL']
    runs = [c[2][0] for c in s.calls if c[0] == 'POST' and c[1] == 'sb_runs']
    assert [r['broker_id'] for r in runs] == ['ANGELONE', 'GROWW', 'MOSL'] and len({r['run_id'] for r in runs}) == 3
    assert [c[2]['status'] for c in s.calls if c[0] == 'PATCH'] == ['success'] * 3
    assert 'MOSL complete through 2026-10-21' in runs[2]['notes']
    assert (tmp_path / 'out/live/2026-10-21/mosl/report.md').read_text().startswith('# Live run · MOSL')


def test_broker_all_publishes_angel_and_groww_when_mosl_is_refused(monkeypatch, tmp_path, capsys, writer_env):
    monkeypatch.chdir(tmp_path)
    s = FakeSession()
    reader = TablesReader(db_tables('staged'))                              # MOSL facts staged
    rc = cli.main(['--db', '--publish', '--broker', 'all'], lambda: reader, lambda: SupabaseWriter(session=s, chunk=100000))
    out = capsys.readouterr().out
    assert rc == 0 and 'WARNING MOSL not published' in out and 'not reviewed' in out
    assert [c[2][0]['broker_id'] for c in s.calls if c[0] == 'POST' and c[1] == 'sb_runs'] == ['ANGELONE', 'GROWW']
    assert [c[2]['status'] for c in s.calls if c[0] == 'PATCH'] == ['success', 'success']
    assert 'refused' in (tmp_path / 'out/live/2026-10-21/mosl/report.md').read_text()


def test_broker_all_without_mosl_inputs_in_the_db_is_a_warning_too(monkeypatch, tmp_path, capsys, writer_env):
    """Today's database: 290 reviewed filing facts, no workbook inputs."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    s = FakeSession()
    reader = TablesReader(db_tables('reviewed', with_inputs=False))
    rc = cli.main(['--db', '--publish', '--broker', 'all'], lambda: reader, lambda: SupabaseWriter(session=s, chunk=100000))
    out = capsys.readouterr().out
    assert rc == 0 and '::warning title=MOSL not published::' in out and 'not in the database' in out
    assert [c[2][0]['broker_id'] for c in s.calls if c[0] == 'POST' and c[1] == 'sb_runs'] == ['ANGELONE', 'GROWW']


def test_mosl_alone_refused_is_a_failure(monkeypatch, tmp_path, capsys, writer_env):
    monkeypatch.chdir(tmp_path)
    s = FakeSession()
    reader = TablesReader(db_tables('reviewed', with_inputs=False))
    rc = cli.main(['--db', '--publish', '--broker', 'MOSL'], lambda: reader, lambda: SupabaseWriter(session=s, chunk=100000))
    assert rc == cli.REFUSED_EXIT and s.calls == []


def test_mosl_alone_publishes_only_mosl_and_runs_no_angel_calibration(monkeypatch, tmp_path, writer_env):
    from src.live import run as run_mod
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(run_mod, 'live_run_snapshot', lambda *a, **k: pytest.fail('MOSL does not need an Angel One run'))
    s = FakeSession()
    reader = TablesReader(db_tables())
    rc = cli.main(['--db', '--publish', '--broker', 'MOSL'], lambda: reader, lambda: SupabaseWriter(session=s, chunk=100000))
    assert rc == 0
    assert [c[2][0]['broker_id'] for c in s.calls if c[0] == 'POST' and c[1] == 'sb_runs'] == ['MOSL']


def test_a_blocked_mosl_run_is_not_published_and_the_others_are(monkeypatch, tmp_path, capsys, writer_env):
    """The database as read on 2 Nov: MOSL is blocked by E5 (rc 1); Angel One and Groww still publish."""
    monkeypatch.chdir(tmp_path)
    s = FakeSession()
    reader = TablesReader(db_tables(lake=LAKE_DB))
    rc = cli.main(['--db', '--publish', '--broker', 'all'], lambda: reader, lambda: SupabaseWriter(session=s, chunk=100000))
    out = capsys.readouterr().out
    assert rc == 1 and 'WARNING MOSL not published' in out and 'MOSL complete through 2026-10-09' in out
    assert [c[2][0]['broker_id'] for c in s.calls if c[0] == 'POST' and c[1] == 'sb_runs'] == ['ANGELONE', 'GROWW']


def test_a_mosl_error_other_than_a_refusal_fails_the_job_after_the_others_published(monkeypatch, tmp_path, writer_env):
    from src.live import mosl_run
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(mosl_run, 'live_run_mosl', lambda *a, **k: 1 / 0)
    s = FakeSession()
    reader = TablesReader(db_tables())
    rc = cli.main(['--db', '--publish', '--broker', 'all'], lambda: reader, lambda: SupabaseWriter(session=s, chunk=100000))
    assert rc == 1
    assert [c[2][0]['broker_id'] for c in s.calls if c[0] == 'POST' and c[1] == 'sb_runs'] == ['ANGELONE', 'GROWW']


# ── Angel One and Groww are unchanged by MOSL's arrival ──
def test_angel_and_groww_dry_run_output_is_byte_identical_to_before_mosl(monkeypatch, tmp_path):
    """md5 of the four files `run_live.py --broker all` wrote before MOSL was wired in (2 Nov 2026). The reports are
    compared as bytes; the summary rows with every float rounded to 12 significant digits, because Python 3.12's sum()
    is compensated and moves the last bit of some rows (<= 3e-16 relative) against 3.9's. Both versions give these pins."""
    import hashlib
    for d in ('snapshot',):
        os.symlink(os.path.join(ROOT, d), tmp_path / d)
    monkeypatch.chdir(tmp_path)
    cli.main(['--broker', 'all'])
    out = tmp_path / 'out' / 'live' / '2026-10-21'

    def rounded(x):
        if isinstance(x, float):
            return float(f'{x:.12g}')
        if isinstance(x, list):
            return [rounded(v) for v in x]
        if isinstance(x, dict):
            return {k: rounded(v) for k, v in x.items()}
        return x

    def digest(f):
        raw = open(out / f, 'rb').read()
        if f.endswith('.json'):
            raw = json.dumps(rounded(json.loads(raw)), sort_keys=True).encode()
        return hashlib.md5(raw).hexdigest()
    got = {f: digest(f) for f in ('summary_rows.json', 'report.md', 'groww/summary_rows.json', 'groww/report.md')}
    assert got == {'summary_rows.json': 'ab06a0b196b3c03dac61e636c7f72dac', 'report.md': 'c586391fe3aacaf5d0673ed9cca799c4',
                   'groww/summary_rows.json': '60a939b904526f53ba5f7039cf3895a6',
                   'groww/report.md': '1cb10c582088dc06a3dcfce9de0cd0e2'}
