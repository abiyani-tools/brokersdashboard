"""Share prices into sb_share_prices (src/live/refresh_prices.py): Yahoo chart replies -> rows, failures, the write."""
import datetime as dt

import pytest

from src.live import db, refresh_prices as R

IST = 19800
D1, D2, D3 = 1793159100, 1793245500, 1793331900        # 09:15 IST on 2026-10-28, 29, 30 (Yahoo stamps the session open)


def result(ts=(D1, D2, D3), close=(100.0, None, 102.5), adj=(99.0, None, 101.5), currency='INR', regular=None):
    return {'meta': {'currency': currency, 'gmtoffset': IST,
                     'currentTradingPeriod': {'regular': regular or {'start': D3 + 86400, 'end': D3 + 86400 + 22500}}},
            'timestamp': list(ts), 'indicators': {'quote': [{'close': list(close)}], 'adjclose': [{'adjclose': list(adj)}]}}


def test_rows_on_ist_dates_and_null_closes_dropped():
    rows = R.price_rows('ANGELONE', 'ANGELONE.NS', result(), 'now')
    assert [(r['trade_date'], r['close'], r['adj_close']) for r in rows] == [('2026-10-28', 100.0, 99.0),
                                                                             ('2026-10-30', 102.5, 101.5)]
    r = rows[0]
    assert (r['broker_id'], r['ticker'], r['source']) == ('ANGELONE', 'ANGELONE.NS', 'yahoo_chart_v8')
    assert r['source_ref'].startswith('https://query1.finance.yahoo.com/v8/finance/chart/ANGELONE.NS?range=10y')


def test_the_bar_of_a_session_still_open_is_not_a_close():
    regular = {'start': D3, 'end': D3 + 22500}                       # 30 Oct, 09:15-15:30 IST
    during = dt.datetime.fromtimestamp(D3 + 3600, dt.timezone.utc)
    after = dt.datetime.fromtimestamp(D3 + 23000, dt.timezone.utc)
    assert [r['trade_date'] for r in R.price_rows('MOSL', 'MOTILALOFS.NS', result(regular=regular), 'now', during)] \
        == ['2026-10-28']
    assert [r['trade_date'] for r in R.price_rows('MOSL', 'MOTILALOFS.NS', result(regular=regular), 'now', after)] \
        == ['2026-10-28', '2026-10-30']


def test_a_changed_reply_is_refused():
    with pytest.raises(R.PriceError, match='currency'):
        R.price_rows('GROWW', 'GROWW.NS', result(currency='USD'), 'now')
    with pytest.raises(R.PriceError, match='closes'):
        R.price_rows('GROWW', 'GROWW.NS', result(close=(1.0,)), 'now')


def test_one_failed_ticker_still_writes_the_others(monkeypatch, capsys):
    def fake_fetch(ticker, session=None):
        if ticker == 'GROWW.NS':
            raise RuntimeError('429 Too Many Requests')
        return result()
    monkeypatch.setattr(R, 'fetch', fake_fetch)
    written = {}

    class W:
        def upsert(self, table, rows, pk):
            written[table] = (rows, pk)
            return len(rows)
    monkeypatch.setattr(db, 'SupabaseWriter', W)
    assert R.main(['--write']) == 1                                  # the step shows as failed ...
    rows, pk = written['sb_share_prices']                            # ... after the other tickers are written
    assert pk == ('broker_id', 'trade_date')
    assert sorted({r['broker_id'] for r in rows}) == ['ANGELONE', 'MOSL'] and len(rows) == 4
    assert 'share price NOT read: GROWW.NS: RuntimeError: 429' in capsys.readouterr().out


def test_dry_run_writes_nothing(monkeypatch):
    monkeypatch.setattr(R, 'fetch', lambda ticker, session=None: result())

    class W:
        def __init__(self):
            raise AssertionError('no writer on a dry run')
    monkeypatch.setattr(db, 'SupabaseWriter', W)
    assert R.main([]) == 0
