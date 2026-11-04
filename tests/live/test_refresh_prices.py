"""Share prices into sb_share_prices (src/live/refresh_prices.py): Yahoo chart replies -> rows, failures, the write."""
import datetime as dt

import pytest

from src.live import db, refresh_prices as R

IST = 19800
D1, D2, D3 = 1793159100, 1793245500, 1793331900        # 09:15 IST on 2026-10-28, 29, 30 (Yahoo stamps the session open)


def result(ts=(D1, D2, D3), close=(100.0, None, 102.5), adj=(99.0, None, 101.5), volume=(10, 0, 12), currency='INR',
           regular=None, splits=None):
    end = max(ts) + 86400
    out = {'meta': {'currency': currency, 'gmtoffset': IST,
                    'currentTradingPeriod': {'regular': regular or {'start': end, 'end': end + 22500}}},
           'timestamp': list(ts), 'indicators': {'quote': [{'close': list(close), 'volume': list(volume)}],
                                                 'adjclose': [{'adjclose': list(adj)}]}}
    if splits:   # [(ex timestamp, numerator, denominator)], as Yahoo's events=split
        out['events'] = {'splits': {str(t): {'date': t, 'numerator': n, 'denominator': d, 'splitRatio': f'{n:g}:{d:g}'}
                                    for t, n, d in splits}}
    return out


D4, D5 = D3 + 3 * 86400, D3 + 4 * 86400                 # 09:15 IST on 2026-11-02, 03
SPLIT_EX = D5 + 30 * 86400                              # a 4:1 split (3:1 bonus) whose ex-date is after these days


def test_closes_yahoo_left_on_the_pre_split_basis_are_rescaled():
    # MOTILALOFS.NS: 4:1 bonus ex 2024-06-10, Yahoo restated only from 2024-01-01 (1,240.85 then 315.01)
    rows = R.price_rows('MOSL', 'MOTILALOFS.NS', result(
        ts=(D1, D2, D3, D4), close=(1210.85, 1240.85, 315.0125, 309.95), adj=(1182.3, 1211.632, 307.595, 302.65),
        volume=(1, 1, 1, 1), splits=[(SPLIT_EX, 4.0, 1.0)]), 'now')
    assert [r['close'] for r in rows] == [302.7125, 310.2125, 315.0125, 309.95]
    assert [r['adj_close'] for r in rows] == [295.575, 302.908, 307.595, 302.65]
    assert rows[0]['source_ref'].endswith('| close and adj_close / 4: split 4:1 ex 2026-12-03, '
                                          'which Yahoo left unadjusted before 2026-10-30')
    assert '|' not in rows[2]['source_ref']                           # rows from the seam on are untouched


def test_a_split_yahoo_restated_in_full_changes_nothing():
    # ANGELONE.NS: 10:1 split ex 2026-02-26, the whole history restated by Yahoo
    rows = R.price_rows('ANGELONE', 'ANGELONE.NS', result(
        ts=(D1, D2, D3), close=(248.99, 246.5, 250.0), adj=(245.2, 242.8, 250.0), volume=(1, 1, 1),
        splits=[(D2, 10.0, 1.0)]), 'now')
    assert [r['close'] for r in rows] == [248.99, 246.5, 250.0]
    assert all('|' not in r['source_ref'] for r in rows)


def test_a_basis_break_no_split_explains_is_refused():
    with pytest.raises(R.PriceError, match='one-day move over 50%.*2026-10-28 1240.85 -> 2026-10-29 315.01'):
        R.price_rows('MOSL', 'MOTILALOFS.NS', result(close=(1240.85, 315.0125, 309.95), adj=(1, 1, 1),
                                                     volume=(1, 1, 1)), 'now')


def test_a_split_that_fits_two_falls_is_refused():
    with pytest.raises(R.PriceError, match='fits 2 one-day falls'):
        R.price_rows('MOSL', 'MOTILALOFS.NS', result(
            ts=(D1, D2, D3, D4, D5), close=(1000.0, 250.0, 1000.0, 250.0, 251.0), adj=(1, 1, 1, 1, 1),
            volume=(1, 1, 1, 1, 1), splits=[(SPLIT_EX, 4.0, 1.0)]), 'now')


def test_split_events_are_requested():
    assert R.PARAMS['events'] == 'split'


def test_rows_on_ist_dates_and_null_closes_dropped():
    rows = R.price_rows('ANGELONE', 'ANGELONE.NS', result(), 'now')
    assert [(r['trade_date'], r['close'], r['adj_close']) for r in rows] == [('2026-10-28', 100.0, 99.0),
                                                                             ('2026-10-30', 102.5, 101.5)]
    r = rows[0]
    assert (r['broker_id'], r['ticker'], r['source']) == ('ANGELONE', 'ANGELONE.NS', 'yahoo_chart_v8')
    assert r['source_ref'].startswith('https://query1.finance.yahoo.com/v8/finance/chart/ANGELONE.NS?range=10y')


def test_a_bar_with_no_volume_is_a_holiday_not_a_price():
    # Yahoo's 2026-01-15 (exchange holiday): the last close repeated with volume 0
    rows = R.price_rows('GROWW', 'GROWW.NS', result(close=(164.34, 164.34, 173.23), adj=(164.34, 164.34, 173.23),
                                                    volume=(5, 0, 7)), 'now')
    assert [r['trade_date'] for r in rows] == ['2026-10-28', '2026-10-30']


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
