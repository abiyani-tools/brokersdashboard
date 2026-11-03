"""Fixtures for MOSL switch m-g (FY24 quarters): market data from 1 June 2023, read only from ExchangesDash's public JSON.

    python3 seed/build_mosl_g_fixtures.py [SHARED_IN [LAKE_OUT [SHARED_OUT]]]

Reads nothing but the owner's public files (src.live.refresh_market.fetch(): nse / bse / mcx dashboard JSON on
raw.githubusercontent.com, each at the latest commit that changed it) and the committed shared snapshot. No database is
read or written. It patches src.live.refresh_market.START to 2023-06-01 (the module is not edited), exactly as the daily
refresh now does after step A1, and writes:

  snapshot/mosl_lake_2026-11-03.json     the four lake series of MOSL's key (lake_rows(), source 'exchangesdash_json') from
                                         2023-06-01, in the format of mosl_lake_2026-11-02.json
  snapshot/db_snapshot_2026-11-03.json   a copy of snapshot/db_snapshot_2026-10-23.json with
                                           - the calendar days 2023-06-01 .. 2023-09-28 added (calendar_rows(), the days
                                             NSE or MCX traded; equity / MCX flags from which file has the day),
                                           - MCX contracts (mcx / contracts) for every MCX day from 2023-06-01 to 2024-03-28
                                             added (the snapshot's series began 2024-04-01),
                                           - is_mcx_day set true on 2023-09-29 .. 2024-03-28 where MCX traded (the database
                                             has these flags since 2 Nov 2026; the snapshot had them false).
                                         Every other row is unchanged.
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from src.live import refresh_market as R            # noqa: E402
import build_mosl_lake as L                         # noqa: E402

START = '2023-06-01'
SHARED_IN = os.path.join(ROOT, 'snapshot', 'db_snapshot_2026-10-23.json')
LAKE_OUT = os.path.join(ROOT, 'snapshot', 'mosl_lake_2026-11-03.json')
SHARED_OUT = os.path.join(ROOT, 'snapshot', 'db_snapshot_2026-11-03.json')
MCX_END = '2024-03-28'            # the snapshot's own MCX series starts 2024-04-01


def build(data, shas, shared):
    """(lake fixture, shared snapshot) from the parsed public JSON `data` (commits `shas`) and the shared snapshot dict."""
    R.START = START
    rows = R.lake_rows(data, shas, '')
    keys = set(L.KEYS)
    series = {k: [] for k in L.KEYS}
    for r in rows:
        k = f"{r['dataset']}/{r['metric']}"
        if k in keys:
            series[k].append([r['trade_date'], r['value'], r['status']])
    for k in series:
        series[k].sort()
    read = ', '.join(f'{k}@{v[:7]}' for k, v in sorted(shas.items()))
    about = ("Lake series for MOSL's live key from 2023-06-01 (see seed/build_mosl_g_fixtures.py): read only from "
             f'ExchangesDash\'s public JSON ({R.REPO}: {read}) through src.live.refresh_market.lake_rows(); '
             "the rows the daily refresh writes to sb_market_daily (source 'exchangesdash_json'). Nothing read from the database.")
    lake = L.fixture(series, about)

    snap = json.loads(json.dumps(shared))
    first = min(r['trade_date'] for r in snap['calendar'])
    added = R.calendar_rows(data, _day_before(START), first)
    snap['calendar'] = added + snap['calendar']
    mcx_days = {r['date'] for r in R._rows(data['mcx'])}
    flipped = []
    for r in snap['calendar']:
        if first <= r['trade_date'] <= MCX_END and r['trade_date'] in mcx_days and not r['is_mcx_day']:
            r['is_mcx_day'] = True
            flipped.append(r['trade_date'])
    have = {r['trade_date'] for r in snap['market_daily'] if r['dataset'] == 'mcx'}
    mcx_rows = [dict(trade_date=r['trade_date'], dataset='mcx', metric='contracts', value=r['value'], status=r['status'],
                     unit='count')
                for r in rows if r['dataset'] == 'mcx' and r['metric'] == 'contracts' and r['trade_date'] <= MCX_END
                and r['trade_date'] not in have]
    snap['market_daily'] = snap['market_daily'] + mcx_rows
    snap['_meta'] = {
        'about': ('db_snapshot_2026-10-23.json plus the market data from 2023-06-01 for the MOSL m-g bridge. Read only '
                  "from ExchangesDash's public JSON (src.live.refresh_market.fetch / calendar_rows / lake_rows); built by "
                  'seed/build_mosl_g_fixtures.py. No database was read.'),
        'source_commits': {k: f'{R.REPO}@{v}' for k, v in sorted(shas.items())},
        'calendar_days_added': [added[0]['trade_date'], added[-1]['trade_date'], len(added)] if added else None,
        'mcx_contract_rows_added': [mcx_rows[0]['trade_date'], mcx_rows[-1]['trade_date'], len(mcx_rows)] if mcx_rows else None,
        'is_mcx_day_set_true': [flipped[0], flipped[-1], len(flipped)] if flipped else None,
    }
    return lake, snap


def _day_before(day):
    return (dt.date.fromisoformat(day) - dt.timedelta(days=1)).isoformat()


def main(shared_in=SHARED_IN, lake_out=LAKE_OUT, shared_out=SHARED_OUT):
    data, shas = R.fetch()
    lake, snap = build(data, shas, json.load(open(shared_in)))
    with open(lake_out, 'w') as fh:
        json.dump(lake, fh, indent=0)
        fh.write('\n')
    with open(shared_out, 'w') as fh:
        json.dump(snap, fh)                       # compact, as db_snapshot_2026-10-23.json
        fh.write('\n')
    print(lake_out, {k: (len(v), v[0][0], v[-1][0]) for k, v in lake['series'].items()})
    print(shared_out, json.dumps(snap['_meta']['calendar_days_added']), json.dumps(snap['_meta']['mcx_contract_rows_added']),
          json.dumps(snap['_meta']['is_mcx_day_set_true']))


if __name__ == '__main__':
    main(*sys.argv[1:])
