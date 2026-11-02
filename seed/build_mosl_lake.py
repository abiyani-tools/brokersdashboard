"""snapshot/mosl_lake_*.json: the four exchange series MOSL's live key reads from the lake, by date (read only).

    python3 seed/build_mosl_lake.py NSE_JSON BSE_JSON OUT_REFRESHED OUT_DB_AS_READ [START]

NSE_JSON / BSE_JSON: ExchangesDash's nse_dashboard_data.json and bse_dashboard_data.json (the files
src/live/refresh_market.py reads). The rows are the ones that job writes to sb_market_daily under source
'exchangesdash_json' (it calls the same lake_rows()). Series (all raw, own date, status as the job stores it):
    nse_fo/io_contracts      NSE index-option contracts       (MOSL F&O key = NSE index options + BSE contracts)
    bse_fo/contracts         BSE contracts                    (equals the workbook's `backtesting F&O!R` on all 757 days)
    nse_cash/turnover_cr     NSE cash turnover, Rs Cr         (the cash key; NOT the workbook's column, two rows off)
    bse_cash/turnover_cr     BSE cash turnover, Rs Cr

Two files are written:
  OUT_REFRESHED   the JSON on the owner's main branch as read on 2 Nov 2026 (io_contracts complete to 30 Oct): what the
                  daily job's refresh step writes, so what tomorrow's live run reads. The default for dry runs and tests.
  OUT_DB_AS_READ  the same, with the three differences the database itself showed on 2 Nov 2026 (SELECTs on
                  sb_market_daily, source 'exchangesdash_json', before today's refresh):
                    nse_fo/io_contracts   0 (status suspect) on 12, 13, 14, 15 Oct 2026 and no row after 15 Oct
                    bse_cash/turnover_cr  0.0 (status ok) on 2026-06-15; the owner's file now has 10,587.06
                  Used to test that E5 flags them. Nothing is written to the database here.
"""
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.live.refresh_market import lake_rows

KEYS = ('nse_fo/io_contracts', 'bse_fo/contracts', 'nse_cash/turnover_cr', 'bse_cash/turnover_cr')
DB_AS_READ = {
    # (key, date): (value, status) or None = no row
    ('nse_fo/io_contracts', '2026-10-12'): (0.0, 'suspect'), ('nse_fo/io_contracts', '2026-10-13'): (0.0, 'suspect'),
    ('nse_fo/io_contracts', '2026-10-14'): (0.0, 'suspect'), ('nse_fo/io_contracts', '2026-10-15'): (0.0, 'suspect'),
    ('bse_cash/turnover_cr', '2026-06-15'): (0.0, 'ok'),
}
DB_LAST = {'nse_fo/io_contracts': '2026-10-15'}        # no row after this date in the database


def series(nse_path, bse_path, start='2023-09-29'):
    data = {'nse': json.load(open(nse_path)), 'bse': json.load(open(bse_path))}
    rows = lake_rows(data, {'nse': 'local', 'bse': 'local'}, dt.datetime.now(dt.timezone.utc).isoformat())
    out = {k: [] for k in KEYS}
    for r in rows:
        k = f"{r['dataset']}/{r['metric']}"
        if k in out and r['trade_date'] >= start:
            out[k].append([r['trade_date'], r['value'], r['status']])
    for k in out:
        out[k].sort()
    return out


def as_read_in_db(s):
    out = {}
    for k, rows in s.items():
        last = DB_LAST.get(k)
        out[k] = [list((d,) + DB_AS_READ.get((k, d), (v, st))) for d, v, st in rows if last is None or d <= last]
    return out


def fixture(s, about):
    return {'_about': about, 'unit': 'io / bse contracts: raw count; turnover: Rs Cr', 'series': s}


def main(nse_path, bse_path, out_ref, out_db, start='2023-09-29'):
    s = series(nse_path, bse_path, start)
    ref = fixture(s, "Lake series for MOSL's live key (see seed/build_mosl_lake.py): ExchangesDash main as read on 2 Nov "
                     "2026 = what the daily refresh writes to sb_market_daily. Read only.")
    db = fixture(as_read_in_db(s), "Same series as the database held them on 2 Nov 2026 before that day's refresh: "
                                   "io_contracts zero (suspect) on 12-15 Oct and no row after, bse_cash turnover 0.0 on "
                                   "2026-06-15. For the E5 tests. Read only.")
    for path, fx in ((out_ref, ref), (out_db, db)):
        with open(path, 'w') as fh:
            json.dump(fx, fh, indent=0)
            fh.write('\n')
        print(path, {k: (len(v), v[0][0], v[-1][0]) for k, v in fx['series'].items()})


if __name__ == '__main__':
    main(*sys.argv[1:])
