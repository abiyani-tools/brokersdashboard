import json

import pytest

from src.live.db import KEY_ENV, SupabaseWriter
from src.live.loader import select_volumes
from src.live.refresh_market import PK, SOURCE, lake_rows

SECRET = 'sb_secret_TEST_ONLY_not_a_real_key'
SHAS = {'nse': 'abcdef1234', 'bse': '9876543210', 'mcx': '1111111aaa', 'mcx_contracts': '2222222bbb',
        'mtf': '3333333ccc'}

NSE = {'daily_all': [
    {'date': '2023-05-31', 'total_contracts': 1, 'io_contracts': 1, 'so_contracts': 1, 'io_premium': 1,
     'so_premium': 1, 'if_turnover': 1, 'sf_turnover': 1, 'cash_traded_value': 1},
    {'date': '2026-10-22', 'total_contracts': 500, 'io_contracts': 0, 'so_contracts': 30, 'io_premium': 2.5,
     'so_premium': 1.5, 'if_turnover': 10.0, 'sf_turnover': 5.0, 'cash_traded_value': 99.0},
], 'special_sessions': [
    {'date': '2025-10-21', 'total_contracts': 7, 'io_contracts': 5, 'so_contracts': 2, 'io_premium': 0.1,
     'so_premium': 0.1, 'if_turnover': 0.2, 'sf_turnover': 0.3, 'cash_traded_value': 4.0},
]}
BSE = {'daily_all': [
    {'date': '2026-10-22', 'total_contracts': 400, 'options_premium_turnover': 3.0, 'futures_turnover': 0.5,
     'cash_trades': 0, 'cash_traded_value': 8.0},
]}
MCX = {'daily_all': [{'date': '2026-10-22', 'fut_rev': 3.2, 'opt_rev': 15.2}], 'special_sessions': []}
DATA = {'nse': NSE, 'bse': BSE, 'mcx': MCX}


def _by_key(rows):
    return {(r['trade_date'], r['dataset'], r['metric']): r for r in rows}


def test_mapping_matches_the_23_oct_import():
    rows = _by_key(lake_rows(DATA, SHAS, 'now'))
    assert ('2023-05-31', 'nse_fo', 'contracts') not in rows          # before START
    r = rows[('2026-10-22', 'nse_fo', 'fut_turnover_cr')]
    assert r['value'] == 15.0 and r['unit'] == 'Rs Cr' and r['source'] == SOURCE
    assert r['source_ref'].startswith('sucaanalytics-max/ExchangesDash@abcdef1:')
    assert rows[('2026-10-22', 'bse_fo', 'contracts')]['source_ref'].startswith('sucaanalytics-max/ExchangesDash@9876543:')
    assert rows[('2026-10-22', 'nse_fo', 'io_contracts')]['status'] == 'suspect'
    assert rows[('2026-10-22', 'bse_cash', 'trades')]['status'] == 'suspect'
    assert rows[('2026-10-22', 'bse_fo', 'contracts')]['status'] == 'ok'
    assert ('2025-10-21', 'nse_fo', 'contracts') in rows               # special sessions are kept
    # not public yet: NSE cash trades, MCX contracts, MTF book
    assert not [k for k in rows if k[1:] in (('nse_cash', 'trades'), ('mcx', 'contracts'),
                                             ('mtf_industry', 'book_cr'))]


def test_nse_cash_trades_are_picked_up_once_published():
    nse = json.loads(json.dumps(NSE))
    nse['daily_all'][1]['cash_trades'] = 45_000_000
    r = _by_key(lake_rows(dict(DATA, nse=nse), SHAS, 'now'))[('2026-10-22', 'nse_cash', 'trades')]
    assert r['value'] == 45_000_000 and r['status'] == 'ok' and r['unit'] == 'count'


def test_mcx_contracts_and_mtf_book_are_picked_up_once_published():
    mcx = json.loads(json.dumps(MCX))
    mcx['daily_all'][0]['total_contracts'] = 18_289_605
    mcx['special_sessions'] = [{'date': '2024-04-11', 'total_contracts': 1_000}]      # MCX-only session
    sep = [{'date': '2026-10-22', 'total_contracts': 18_300_000}, {'date': '2026-10-23', 'total_contracts': 0}]
    mtf = [{'date': '2026-10-22', 'book_cr': 148_900.5}]
    rows = _by_key(lake_rows(dict(DATA, mcx=mcx, mcx_contracts=sep, mtf=mtf), SHAS, 'now'))
    r = rows[('2026-10-22', 'mcx', 'contracts')]
    assert r['value'] == 18_300_000 and r['source_ref'].startswith('sucaanalytics-max/ExchangesDash@2222222:')
    assert rows[('2024-04-11', 'mcx', 'contracts')]['value'] == 1_000
    assert rows[('2026-10-23', 'mcx', 'contracts')]['status'] == 'suspect'
    m = rows[('2026-10-22', 'mtf_industry', 'book_cr')]
    assert m['value'] == 148_900.5 and m['unit'] == 'Rs Cr' and m['status'] == 'ok'


@pytest.mark.parametrize('key,old_source', [('nse_fo:contracts', 'exchangesdash_json@b2049b5'),
                                            ('mcx:contracts', 'octo_mcx@2026-10-22')])
def test_refreshed_rows_win_over_the_one_off_imports(key, old_source):
    ds, metric = key.split(':')
    old = dict(trade_date='2026-10-15', dataset=ds, metric=metric, source=old_source, value=1.0, status='ok')
    new = dict(old, source=SOURCE, value=2.0)
    for policy in ('best_ok', 'excel_first'):
        vols = select_volumes([old, new], policy, keys=[key])
        assert [v.value for v in vols[key]] == [2.0]


class GH:
    """GitHub stand-in: commits API and raw files; `missing` paths have no commits."""

    def __init__(self, files, missing=()):
        self.files, self.missing = files, set(missing)

    def get(self, url, params=None, headers=None, timeout=None):
        if 'api.github.com' in url:
            path = params['path']
            return FakeGet([] if path in self.missing else [{'sha': 'f' * 40}])
        return FakeGet(self.files[url.split('/' + 'f' * 40 + '/', 1)[1]])


class FakeGet:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        pass

    def json(self):
        return self.body


def test_fetch_skips_optional_files_the_repo_does_not_have():
    from src.live.refresh_market import FILES, fetch
    gh = GH({FILES['nse']: NSE, FILES['bse']: BSE, FILES['mcx']: MCX},
            missing=(FILES['mcx_contracts'], FILES['mtf']))
    data, shas = fetch(gh)
    assert set(data) == set(shas) == {'nse', 'bse', 'mcx'}
    with pytest.raises(RuntimeError):
        fetch(GH({}, missing=(FILES['nse'],)))


class Resp:
    def __init__(self, status=201, text=''):
        self.status_code, self.text = status, text


class Session:
    def __init__(self):
        self.calls = []

    def post(self, url, params, data, headers, timeout):
        self.calls.append((url, params, json.loads(data), headers))
        return Resp(201)


def test_upsert_merges_on_the_primary_key(monkeypatch):
    monkeypatch.setenv(KEY_ENV, SECRET)
    s = Session()
    rows = lake_rows(DATA, SHAS, 'now')
    n = SupabaseWriter(session=s, chunk=5).upsert('sb_market_daily', rows, PK)
    assert n == len(rows) and len(s.calls) == -(-len(rows) // 5)
    url, params, part, headers = s.calls[0]
    assert url.endswith('/rest/v1/sb_market_daily')
    assert params == {'on_conflict': 'trade_date,dataset,metric,source'}
    assert 'resolution=merge-duplicates' in headers['Prefer']
    assert SECRET not in repr(SupabaseWriter(session=s))


def test_snapshot_keeps_one_lake_row_per_day():
    import os
    from src.live.run import EngineSnapshotReader
    from src.live.snapshot import build_snapshot
    root = os.path.join(os.path.dirname(__file__), '..', '..')
    snap = json.load(open(os.path.join(root, 'snapshot', 'db_snapshot_2026-10-23.json')))
    rd = EngineSnapshotReader(snap)
    rd.tables['sb_market_daily'] = rd.tables['sb_market_daily'] + [
        dict(trade_date='2026-10-01', dataset='bse_fo', metric='contracts', source=s, value=v, status='ok')
        for s, v in ((SOURCE, 2.0), ('exchangesdash_json@b2049b5', 1.0), ('zzz_later_source', 3.0))]
    built, _ = build_snapshot(rd)
    day = [r for r in built['market_daily_lake'] if (r['trade_date'], r['dataset'], r['metric'])
           == ('2026-10-01', 'bse_fo', 'contracts')]
    assert [(r['source'], r['value']) for r in day] == [(SOURCE, 2.0)]


def test_calendar_is_extended_from_the_exchanges_trading_days():
    from src.live.refresh_market import calendar_rows
    nse = {'daily_all': [{'date': d} for d in ('2026-10-21', '2026-10-22', '2026-10-23')],
           'special_sessions': [{'date': '2026-11-08'}]}
    mcx = {'daily_all': [{'date': d} for d in ('2026-10-21', '2026-10-22', '2026-10-24')]}
    rows = {r['trade_date']: r for r in calendar_rows({'nse': nse, 'mcx': mcx}, '2026-10-21')}
    assert sorted(rows) == ['2026-10-22', '2026-10-23', '2026-10-24', '2026-11-08']
    assert (rows['2026-10-23']['is_equity_day'], rows['2026-10-23']['is_mcx_day']) == (True, False)
    assert (rows['2026-10-24']['is_equity_day'], rows['2026-10-24']['is_mcx_day']) == (False, True)
    r = rows['2026-11-08']
    assert r['special_session'] == 'special' and r['weekday'] == 'Sunday'
    assert (r['fy'], r['q_fy'], r['fy_month']) == ('FY 2027', 'Q3 FY 2027', 'FY 2027 November')


def test_as_of_is_capped_by_the_calendar():
    import os
    from src.live.snapshot import complete_through
    root = os.path.join(os.path.dirname(__file__), '..', '..')
    snap = json.load(open(os.path.join(root, 'snapshot', 'db_snapshot_2026-10-23.json')))
    snap['calendar'] = [r for r in snap['calendar'] if r['trade_date'] <= '2026-10-16']
    assert complete_through(snap) == ('2026-10-16', 'sb_calendar')


def test_industry_mtf_book_from_the_owners_view(monkeypatch):
    from src.live.refresh_market import MTF_SOURCE, fetch_mtf_book, mtf_rows
    monkeypatch.delenv('NSE_LAKE_ANON_KEY', raising=False)
    rows, msg = fetch_mtf_book()
    assert rows == [] and 'skipped' in msg                          # no key: nothing read, run goes on
    view = [{'reporting_date': '2023-05-31', 'closing_outstanding_cr': 1.0},
            {'reporting_date': '2024-10-01', 'closing_outstanding_cr': 81823.53},
            {'reporting_date': '2026-10-29', 'closing_outstanding_cr': 0}]
    out = {r['trade_date']: r for r in mtf_rows(view, 'now')}
    assert sorted(out) == ['2024-10-01', '2026-10-29']               # before START dropped
    r = out['2024-10-01']
    assert (r['dataset'], r['metric'], r['unit'], r['source'], r['value']) == \
        ('mtf_industry', 'book_cr', 'Rs Cr', MTF_SOURCE, 81823.53)
    assert out['2026-10-29']['status'] == 'suspect'


def test_a_failed_mtf_view_still_writes_the_exchangesdash_rows(monkeypatch, capsys):
    """2 Nov 2026: the owner's view answered 401 and the whole refresh stopped, so the lake rows were never upserted."""
    from src.live import db, refresh_market as R
    monkeypatch.setattr(R, 'fetch', lambda: (DATA, SHAS))

    def boom():
        raise RuntimeError('401 Client Error: Unauthorized')
    monkeypatch.setattr(R, 'fetch_mtf_book', boom)
    written = {}

    class W:
        def upsert(self, table, rows, pk):
            written[table] = rows
            return len(rows)

        def insert(self, table, rows):
            written[table] = rows

    class Rd:
        def table(self, name):
            return [{'trade_date': '2099-01-01'}]
    monkeypatch.setattr(db, 'SupabaseWriter', W)
    monkeypatch.setattr(db, 'SupabaseReader', Rd)
    assert R.main(['--write']) == 1                                        # the step shows as failed ...
    assert len(written['sb_market_daily']) == len(lake_rows(DATA, SHAS, 'now'))   # ... after the lake rows are written
    assert 'industry MTF book: NOT read (RuntimeError: 401' in capsys.readouterr().out


def test_industry_mtf_book_pages_through_the_view(monkeypatch):
    from src.live.refresh_market import fetch_mtf_book
    monkeypatch.setenv('NSE_LAKE_ANON_KEY', 'anon_TEST_ONLY')
    days = [{'reporting_date': f'2025-01-{i:02d}', 'closing_outstanding_cr': 1000 + i} for i in range(1, 6)]

    class S:
        def __init__(self):
            self.calls = []

        def get(self, url, params, headers, timeout):
            self.calls.append(params['offset'])
            return FakeGet(days[params['offset']:params['offset'] + params['limit']])
    s = S()
    rows, msg = fetch_mtf_book(s, page=2)
    assert len(rows) == 5 and s.calls == [0, 2, 4] and 'last 2025-01-05' in msg


def test_calendar_is_backfilled_to_start(monkeypatch):
    """A1 (2 Nov 2026): the refresh adds the days from START up to the calendar's first day, nothing before START."""
    from src.live import db, refresh_market as R
    monkeypatch.setattr(R, 'START', '2023-06-01')
    nse = {'daily_all': [{'date': d} for d in ('2023-05-31', '2023-06-01', '2023-06-02', '2023-09-29', '2026-10-22')]}
    mcx = {'daily_all': [{'date': d} for d in ('2023-06-01', '2023-06-03', '2023-09-29', '2026-10-22')]}
    data = {'nse': nse, 'bse': {'daily_all': []}, 'mcx': mcx}
    early = R.calendar_rows(data, R._day_before(R.START), '2023-09-29')
    assert [r['trade_date'] for r in early] == ['2023-06-01', '2023-06-02', '2023-06-03']
    assert [(r['is_equity_day'], r['is_mcx_day']) for r in early] == [(True, True), (True, False), (False, True)]
    assert early[0]['fy_month'] == 'FY 2024 June'


def test_new_years_day_2024_on_mcx_is_a_known_thin_day():
    from src.live.integrity import KNOWN_ISSUES, Issue, _known
    import datetime as dt
    i = _known(Issue('jump', 'mcx:contracts', 'error', (dt.date(2024, 1, 1),), '206,227 outside ...'))
    assert i.severity == 'info' and 'evening session from 5 pm closed' in i.detail
    assert ('jump', 'mcx:contracts', '2025-01-01') in KNOWN_ISSUES
