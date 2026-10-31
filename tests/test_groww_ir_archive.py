"""Groww IR archive (src/live/refresh_groww_ir.py) and the QTD trading-day inference (src/engine/groww_ir.py).
The page fixture holds the seven charts as saved on 31 Oct 2026 (the full raw pages are not in git)."""
import copy
import datetime as dt
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.engine import groww_ir as IR
from src.live import refresh_groww_ir as R

ROOT = os.path.join(os.path.dirname(__file__), '..')
PAGE = os.path.join(ROOT, 'tests', 'fixtures', 'groww_ir_page_2026-10-31.html')
EXCHANGE = os.path.join(ROOT, 'snapshot', 'groww_exchange_2026-10-31.json')
IR_FIXTURE = os.path.join(ROOT, 'snapshot', 'groww_ir_2026-10-31.json')
FETCHED = dt.datetime(2026, 10, 31, 5, 46, tzinfo=dt.timezone.utc)          # 11:16 IST


def html():
    return open(PAGE, encoding='utf-8').read()


def next_data():
    return json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html(), re.S).group(1))


def with_data(nd):
    return '<script id="__NEXT_DATA__" type="application/json">' + json.dumps(nd) + '</script>'


def chart(nd, cid):
    return next(c for c in nd['props']['pageProps']['initialChartConfigs'] if c['id'] == cid)


def parse(h=None):
    return R.parse_page(h if h is not None else html(), FETCHED)


# ── parse ──
def test_parses_all_seven_charts_into_178_rows():
    rows, meta = parse()
    assert len(rows) == 178 and meta['snapshot_date'] == '2026-10-31'
    assert {r['metric'] for r in rows} == set(IR.ALL_METRICS)
    assert {(r['metric']) for r in rows if r['is_qtd']} == set(IR.ALL_METRICS)
    assert {r['period_key'] for r in rows if r['is_qtd']} == {'Q3 FY 2027'}
    assert all(r['broker_id'] == 'GROWW' and r['source'] == 'groww_ir_site' and r['covers_through'] is None
               for r in rows)
    assert {r['unit'] for r in rows if r['metric'] == 'ir_users'} == {'count'}
    assert {r['unit'] for r in rows if r['metric'] != 'ir_users'} == {'Rs Mn'}
    assert len({tuple(r[k] for k in R.PK[1:]) for r in rows}) == 178              # primary key is unique
    assert all(set(r) == set(rows[0]) for r in rows)                              # same keys: a valid bulk upsert


def test_units_tie_to_the_kpi_handbook_and_the_pages_own_strings():
    rows, _ = parse()
    v = {(r['metric'], r['period_key']): r['value'] for r in rows}
    # KPI Handbook (Q2 FY27): ADTO stocks 144,299.7059 Rs Mn x 65 days, MTF book 43,514 Rs Mn, F&O premium ADTO 123,224.343
    assert v[('ir_stocks_turnover', 'Q2 FY 2027')] == pytest.approx(144299.7059 * 65, rel=2e-4)
    assert v[('ir_equity_derivs_premium', 'Q2 FY 2027')] == pytest.approx(123224.343 * 65, rel=2e-4)
    assert v[('ir_mtf_net_book', 'Q2 FY 2027')] == pytest.approx(43514.0, rel=2e-4)
    # the page prints the QTD point as "Rs 2,731,513 Mn"
    assert v[('ir_stocks_turnover', 'Q3 FY 2027')] == pytest.approx(2731513, abs=1)
    assert v[('ir_users', 'Q3 FY 2027')] == 24101431


# ── the page changes: fail loudly ──
def test_missing_next_data_fails():
    with pytest.raises(R.PageChanged, match='__NEXT_DATA__'):
        parse('<html><body>Access denied</body></html>')


def test_missing_chart_id_fails():
    nd = next_data()
    nd['props']['pageProps']['initialChartConfigs'] = [c for c in nd['props']['pageProps']['initialChartConfigs']
                                                       if c['id'] != 'mtf_net_book']
    with pytest.raises(R.PageChanged, match="missing.*mtf_net_book"):
        parse(with_data(nd))


def test_renamed_chart_id_fails():
    nd = next_data()
    chart(nd, 'stocks_turnover')['id'] = 'cash_turnover'
    with pytest.raises(R.PageChanged, match='stocks_turnover'):
        parse(with_data(nd))


def test_renamed_line_fails():
    nd = next_data()
    chart(nd, 'aum')['lines'][1]['name'] = 'Mutual Fund Assets'
    with pytest.raises(R.PageChanged, match='MF Assets'):
        parse(with_data(nd))


def test_bad_or_gappy_labels_fail():
    nd = next_data()
    chart(nd, 'users')['data'][5]['label'] = 'Quarter 3'
    with pytest.raises(R.PageChanged, match='label'):
        parse(with_data(nd))
    nd = next_data()
    del chart(nd, 'users')['data'][5]
    with pytest.raises(R.PageChanged, match='not consecutive'):
        parse(with_data(nd))


def test_charts_ending_on_different_quarters_fail():
    nd = next_data()
    chart(nd, 'mf_sip')['data'].pop()
    with pytest.raises(R.PageChanged, match='different quarters'):
        parse(with_data(nd))


def test_non_numeric_value_fails():
    nd = next_data()
    chart(nd, 'mf_sip')['data'][3]['value'] = '13,023'
    with pytest.raises(R.PageChanged, match='not a non-negative number'):
        parse(with_data(nd))


def test_unit_change_fails():
    nd = next_data()
    c = chart(nd, 'stocks_turnover')
    c['currentValue'] = '₹2.73 Tn'                                    # the page changes its display unit
    with pytest.raises(R.PageChanged, match='Mn'):
        parse(with_data(nd))
    nd = next_data()
    for p in chart(nd, 'stocks_turnover')['data']:                    # every value x10 but the page string unchanged
        p['value'] *= 10
    with pytest.raises(R.PageChanged, match='unit changed'):
        parse(with_data(nd))


def test_stale_page_fails():
    with pytest.raises(R.PageChanged, match='should show'):
        R.parse_page(html(), dt.datetime(2027, 5, 15, 5, 0, tzinfo=dt.timezone.utc))   # Q1 FY28 day, page still Q3 FY27


# ── fetch ──
class _Resp:
    def __init__(self, code, text=''):
        self.status_code, self.text = code, text


class _Session:
    def __init__(self, resp=None, exc=None):
        self.resp, self.exc, self.calls = resp, exc, []

    def get(self, url, headers=None, timeout=None):
        self.calls.append((url, headers))
        if self.exc:
            raise self.exc
        return self.resp


def test_fetch_sends_a_browser_user_agent_and_returns_the_page():
    s = _Session(_Resp(200, 'ok'))
    text, at = R.fetch(s)
    assert text == 'ok' and at.tzinfo is not None
    assert s.calls[0][0] == 'https://groww.in/investor-relations' and 'Mozilla' in s.calls[0][1]['User-Agent']


@pytest.mark.parametrize('sess', [_Session(_Resp(403, 'Forbidden')), _Session(exc=OSError('network is unreachable'))])
def test_blocked_fetch_is_a_loud_failure(sess, capsys, monkeypatch, tmp_path):
    with pytest.raises(R.FetchFailed):
        R.fetch(sess)
    real = R.fetch
    monkeypatch.setattr(R, 'fetch', lambda: real(sess))
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    assert R.main(['--raw-dir', str(tmp_path)]) == 1                   # non-zero exit: the job step turns red
    out = capsys.readouterr().out
    assert 'FETCH FAILED' in out and '::error title=groww.in not fetched' in out


def test_page_change_is_a_loud_failure_and_keeps_the_raw_page(tmp_path, capsys, monkeypatch):
    bad = tmp_path / 'p.html'
    bad.write_text('<html>blocked</html>')
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    assert R.main(['--html', str(bad), '--fetched-at', '2026-10-31T05:46:00Z', '--raw-dir', str(tmp_path / 'raw')]) == 1
    out = capsys.readouterr().out
    assert 'PAGE STRUCTURE CHANGED' in out and '::error title=groww.in page structure changed' in out
    assert os.listdir(tmp_path / 'raw') == ['investor-relations_2026-10-31.html']


# ── the trading day the QTD point runs through ──
def test_the_31_oct_snapshot_runs_through_30_oct():
    rows, _ = parse()
    inf = IR.infer_covered_through(IR.IR(rows), IR.Turnover.from_fixture(EXCHANGE))
    assert inf['day'] == '2026-10-30' and inf['confident'] and inf['margin'] > 0.03
    assert inf['prior'] == 'Q2 FY 2027'
    # Q2 FY27 shares on the stated definition: 11.2% of NSE+BSE cash, 17.5% of NSE+BSE option premium
    assert inf['prior_shares']['cash'] == pytest.approx(0.1120, abs=5e-4)
    assert inf['prior_shares']['fo'] == pytest.approx(0.1748, abs=5e-4)
    by = {c[0]: c for c in inf['candidates']}
    assert by['2026-10-30'][1] == pytest.approx(0.110, abs=5e-4) and by['2026-10-30'][2] == pytest.approx(0.175, abs=5e-4)
    assert len(inf['candidates']) == 20                                     # 20 trading days in Oct 2026 to the 30th


def test_inference_does_not_look_past_the_fetch_day():
    rows, _ = parse()
    inf = IR.infer_covered_through(IR.IR(rows), IR.Turnover.from_fixture(EXCHANGE), on_or_before='2026-10-29')
    assert inf['day'] <= '2026-10-29'


def test_inference_is_refused_when_no_cutoff_fits():
    rows, _ = parse()
    rows = [dict(r, value=r['value'] * 3 if r['metric'] == 'ir_stocks_turnover' and r['is_qtd'] else r['value'])
            for r in rows]
    inf = IR.infer_covered_through(IR.IR(rows), IR.Turnover.from_fixture(EXCHANGE))
    assert not inf['confident']
    with pytest.raises(IR.IRError, match='cannot pin'):
        IR.resolve_covered_through(IR.IR(rows), IR.Turnover.from_fixture(EXCHANGE))


def test_add_covers_through_marks_only_qtd_rows():
    rows, _ = parse()
    inf, note = R.add_covers_through(rows, IR.Turnover.from_fixture(EXCHANGE))
    assert inf['day'] == '2026-10-30' and 'stored' in note
    assert {r['covers_through'] for r in rows if r['is_qtd']} == {'2026-10-30'}
    assert all(r['covers_through'] is None for r in rows if not r['is_qtd'])


def test_turnover_refuses_incomplete_days():
    t = IR.Turnover({'2026-10-01': dict(nse_cash=1, bse_cash=1, nse_io=1, nse_so=1, bse_opt=1),
                     '2026-10-05': dict(nse_cash=1, bse_cash=1, nse_io=1, nse_so=1, bse_opt=None)})
    assert t.incomplete == {'2026-10-05'}
    with pytest.raises(IR.IRError, match='incomplete'):
        t.total('cash', '2026-10-01', '2026-10-30')


def test_fixture_in_the_repo_is_what_the_archive_writes():
    fx = json.load(open(IR_FIXTURE))
    rows, meta = parse()
    inf, _ = R.add_covers_through(rows, IR.Turnover.from_fixture(EXCHANGE))
    strip = lambda rs: [{k: v for k, v in r.items() if k != 'source_ref'} for r in rs]      # the hash is of the full page
    assert strip(fx['rows']) == strip(rows) and fx['snapshot_date'] == '2026-10-31'


def test_quarter_helpers():
    assert IR.period_key('Q3 FY27') == 'Q3 FY 2027' and IR.quarter_bounds('Q3 FY 2027') == ('2026-10-01', '2026-12-31')
    assert IR.quarter_bounds('Q4 FY 2026') == ('2026-01-01', '2026-03-31')
    assert IR.quarter_bounds('Q1 FY 2027') == ('2026-04-01', '2026-06-30')
    assert IR.next_quarter('Q4 FY 2026') == 'Q1 FY 2027' and IR.prev_quarter('Q1 FY 2027') == 'Q4 FY 2026'
    assert IR.quarter_of('2026-03-31') == 'Q4 FY 2026' and IR.quarter_of('2026-04-01') == 'Q1 FY 2027'


# ── the write path and the migration ──
class _Writer:
    def __init__(self):
        self.calls = []

    def upsert(self, table, rows, on_conflict):
        self.calls.append((table, rows, on_conflict))
        return len(rows)


def test_write_upserts_on_the_primary_key(monkeypatch, tmp_path):
    w = _Writer()
    monkeypatch.setattr('src.live.db.SupabaseWriter', lambda: w)
    assert R.main(['--html', PAGE, '--fetched-at', '2026-10-31T05:46:00Z', '--raw-dir', str(tmp_path),
                   '--exchange', EXCHANGE, '--write']) == 0
    (table, rows, key), = w.calls
    assert table == 'sb_broker_daily' and key == ('broker_id', 'snapshot_date', 'metric', 'period_key')
    assert len(rows) == 178 and sum(r['covers_through'] == '2026-10-30' for r in rows) == 9


def test_dry_run_writes_nothing(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr('src.live.db.SupabaseWriter', lambda: pytest.fail('dry run must not write'))
    assert R.main(['--html', PAGE, '--fetched-at', '2026-10-31T05:46:00Z', '--raw-dir', str(tmp_path),
                   '--exchange', EXCHANGE]) == 0
    assert 'dry run: nothing written' in capsys.readouterr().out


def test_migration_file_is_the_agreed_table():
    sql = open(os.path.join(ROOT, 'out', 'groww', 'migration_sb_broker_daily.sql')).read()
    for want in ('create table public.sb_broker_daily', 'references public.sb_brokers', 'timestamptz',
                 'snapshot_date  date', 'period_key     text', 'is_qtd         boolean',
                 'primary key (broker_id, snapshot_date, metric, period_key)', 'enable row level security',
                 'for select to anon, authenticated using (true)', 'drop table public.sb_broker_daily'):
        assert want in sql, want
