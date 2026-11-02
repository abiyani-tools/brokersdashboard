"""Daily share prices of the listed brokers into sb_share_prices (the dashboard's price vs ADR-DMA charts).

    python3 -m src.live.refresh_prices            # dry run: fetch, show what would be written
    python3 -m src.live.refresh_prices --write    # upsert into sb_share_prices (needs SUPABASE_SERVICE_KEY)

Source: Yahoo's chart API (query1.finance.yahoo.com/v8/finance/chart/<ticker>, no key), one call per ticker, the full
history every run. Yahoo restates every past close after a split or bonus, so each run upserts all rows: a partial
upsert would leave the old rows on the old basis (a step in the series).

Columns: `close` is Yahoo's chart close (split- and bonus-adjusted, not dividend-adjusted): the charts use it.
`adj_close` is Yahoo's adjclose (also dividend-adjusted), kept for reference. Bars with no close, or volume 0 (no trade:
Yahoo repeats the last close on an exchange holiday), are dropped: no row, never a repeated price. The bar of a session
still open (today before the close) is dropped: intraday it is the last trade, not a close.

A ticker that fails (HTTP error, an empty or changed reply) is reported and skipped; the others are still written, and
the command exits 1 so the job step shows as failed (the step is continue-on-error: prices never stop the ADR run).
Table: out/prices/migration_sb_share_prices.sql.
"""
from __future__ import annotations

import datetime as dt
import os
import sys

TICKERS = {'ANGELONE': 'ANGELONE.NS', 'MOSL': 'MOTILALOFS.NS', 'GROWW': 'GROWW.NS'}
URL = 'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
PARAMS = {'range': '10y', 'interval': '1d'}
SOURCE = 'yahoo_chart_v8'
PK = ('broker_id', 'trade_date')


class PriceError(RuntimeError):
    """Yahoo's reply cannot be read as a daily price series."""


def fetch(ticker, session=None):
    """Yahoo's chart reply (the 'result' object) for one ticker."""
    if session is None:
        import requests
        session = requests.Session()
    r = session.get(URL.format(ticker=ticker), params=PARAMS, headers={'User-Agent': 'Mozilla/5.0'}, timeout=60)
    r.raise_for_status()
    chart = r.json().get('chart') or {}
    if chart.get('error') or not chart.get('result'):
        raise PriceError(f'{ticker}: no chart result ({chart.get("error")})')
    return chart['result'][0]


def price_rows(broker, ticker, result, fetched_at, now=None):
    """sb_share_prices rows from one chart result. now: the current instant (UTC), to drop a session still open."""
    meta = result.get('meta') or {}
    if meta.get('currency') != 'INR':
        raise PriceError(f'{ticker}: currency {meta.get("currency")!r}, expected INR')
    ts = result.get('timestamp') or []
    ind = result.get('indicators') or {}
    closes = ((ind.get('quote') or [{}])[0]).get('close') or []
    volumes = ((ind.get('quote') or [{}])[0]).get('volume') or [None] * len(ts)
    adj = ((ind.get('adjclose') or [{}])[0]).get('adjclose') or [None] * len(ts)
    if not ts or len(closes) != len(ts) or len(adj) != len(ts) or len(volumes) != len(ts):
        raise PriceError(f'{ticker}: {len(ts)} timestamps, {len(closes)} closes, {len(adj)} adjusted closes, '
                         f'{len(volumes)} volumes')
    offset = meta.get('gmtoffset', 19800)
    session_ = (meta.get('currentTradingPeriod') or {}).get('regular') or {}
    now = (now or dt.datetime.now(dt.timezone.utc)).timestamp()
    still_open = session_.get('start') is not None and session_['start'] <= now < session_.get('end', 0)
    ref = f'{URL.format(ticker=ticker)}?range={PARAMS["range"]}&interval={PARAMS["interval"]}'
    out = {}
    for t, c, a, v in zip(ts, closes, adj, volumes):
        if c is None or c <= 0 or v == 0:      # volume 0: no trade (Yahoo repeats the last close on a holiday, 2026-01-15)
            continue
        if still_open and t >= session_['start']:
            continue                                                  # today's session is still open: not a close
        d = dt.datetime.fromtimestamp(t + offset, dt.timezone.utc).date().isoformat()
        out[d] = dict(broker_id=broker, trade_date=d, ticker=ticker, close=round(float(c), 4),
                      adj_close=round(float(a), 4) if a is not None and a > 0 else None,
                      source=SOURCE, source_ref=ref, fetched_at=fetched_at)
    return [out[d] for d in sorted(out)]


def main(argv=None, session=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    fetched_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    rows, failed = [], []
    for broker, ticker in TICKERS.items():
        try:
            part = price_rows(broker, ticker, fetch(ticker, session), fetched_at)
        except Exception as e:
            failed.append(f'{ticker}: {type(e).__name__}: {e}')
            continue
        rows += part
        print(f'{broker:9} {ticker:14} {len(part):5} days {part[0]["trade_date"]} .. {part[-1]["trade_date"]}, '
              f'last close {part[-1]["close"]}' if part else f'{broker:9} {ticker:14} no rows')
    for f in failed:
        msg = f'share price NOT read: {f}; the other tickers are still written'
        if os.environ.get('GITHUB_ACTIONS'):
            print(f'::warning title=Share price not read::{msg}')
        print(msg)
    rc = 1 if failed else 0
    if '--write' not in argv:
        print('dry run: nothing written (pass --write to upsert into sb_share_prices)')
        return rc
    if rows:
        from .db import SupabaseWriter
        n = SupabaseWriter().upsert('sb_share_prices', rows, PK)
        print(f'upserted {n} rows into sb_share_prices')
    return rc


if __name__ == '__main__':
    sys.exit(main())
