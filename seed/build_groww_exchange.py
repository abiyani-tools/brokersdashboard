"""snapshot/groww_exchange_<date>.json: daily NSE + BSE cash turnover and option-premium turnover (Rs Cr) for g-h.

    python3 seed/build_groww_exchange.py NSE_JSON BSE_JSON OUT [START]

NSE_JSON / BSE_JSON: ExchangesDash's nse_dashboard_data.json and bse_dashboard_data.json (the files
src/live/refresh_market.py reads). The rows are the ones that job writes to sb_market_daily under source
'exchangesdash_json' (it calls the same lake_rows()), so the fixture equals the table: it was cross-checked
against SELECT sums by quarter on 31 Oct 2026. Read only; nothing is written to the database.
"""
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.engine.groww_ir import Turnover
from src.live.refresh_market import lake_rows


def main(nse_path, bse_path, out, start='2024-04-01'):
    data = {'nse': json.load(open(nse_path)), 'bse': json.load(open(bse_path))}
    shas = {'nse': 'local', 'bse': 'local'}
    rows = [r for r in lake_rows(data, shas, dt.datetime.now(dt.timezone.utc).isoformat())
            if r['trade_date'] >= start and r['status'] == 'ok']
    t = Turnover.from_market_rows(rows)
    fx = t.to_fixture(
        'Exchange turnover in Rs Cr: nse_cash/turnover_cr (cash_traded_value), bse_cash/turnover_cr, '
        'nse_fo/io_premium_cr, nse_fo/so_premium_cr, bse_fo/opt_premium_cr. ExchangesDash JSON, the rows of '
        "sb_market_daily source 'exchangesdash_json'. Built by seed/build_groww_exchange.py; read only.")
    with open(out, 'w') as fh:
        json.dump(fx, fh, indent=0)
        fh.write('\n')
    print(f'{out}: {len(t.dates)} days {t.dates[0]}..{t.dates[-1]}, incomplete days {sorted(t.incomplete)}')


if __name__ == '__main__':
    main(*sys.argv[1:])
