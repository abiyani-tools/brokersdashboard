"""Compare an engine run with sb_parity_expected (the workbook's own results)."""
import re
from collections import defaultdict
from .inputs import fy_month_of


# Workbook cells that do not feed the ADR and cannot be rebuilt from stored inputs (documented, not faked)
OUT_OF_SCOPE = {
    'comm_take_rate_m': 'Commodities!AB is calculated but unused (daily revenue uses the fixed AI11); '
                        'AB26:AB34 are typed-in rounded values that were not seeded as facts',
    'mtf_industry_avg_q|Q3 FY 2027': "MTF data!D59 uses a 38% FY27 industry-growth assumption ('MTF data'!B61) "
                                     'not stored in the DB; display only',
    'mtf_industry_avg_q|Q4 FY 2027': 'as D59 (D60); display only',
    'mtf_angel_book_q|Q3 FY 2027': 'P59 = Q59 x D59; depends on the same assumption; display only',
    'mtf_angel_book_q|Q4 FY 2027': 'P60 = Q60 x D60; display only',
}


def _scope(key):
    for k, why in OUT_OF_SCOPE.items():
        if key == k or key.split('|')[0] == k:
            return why
    return None


def compare(res, cells, expected, rel=1e-9, abs_=1e-9):
    got = {}
    d = res['daily']
    for date, r in d['fo'].items():
        got[f'fo_orders_mn|{date}'] = r['orders_mn']; got[f'fo_rev_mn|{date}'] = r['rev_mn']
        got[f'fo_cpo|{date}'] = r['cpo']; got[f'fo_share|{date}'] = r['share']
    for date, r in d['cash'].items():
        got[f'cash_orders_mn|{date}'] = r['orders_mn']; got[f'cash_rev_mn|{date}'] = r['rev_mn']
        got[f'cash_tpo|{date}'] = r['tpo']; got[f'cash_share|{date}'] = r['share']
    for date, r in d['comm'].items():
        got[f'comm_orders_mn|{date}'] = r['orders_mn']; got[f'comm_rev_mn|{date}'] = r['rev_mn']
        got[f'comm_cpo|{date}'] = r['cpo']
    for date, r in d['mtf'].items():
        got[f'mtf_share|{date}'] = r['share']; got[f'mtf_angel_book_cr|{date}'] = r['angel_book_cr']
        got[f'mtf_gross_cr|{date}'] = r['gross_cr']; got[f'mtf_net_cr|{date}'] = r['net_cr']
    c = res['calib']
    for m, r in c['fo_month'].items():
        for k, n in (('share', 'fo_share_m'), ('mkt_contracts', 'fo_mkt_contracts_m'), ('total_orders', 'total_orders_m'),
                     ('fo_pct', 'fo_pct_m'), ('fo_orders', 'fo_orders_m'), ('angel_contracts_mn', 'angel_contracts_mn'),
                     ('cpo', 'fo_cpo_m')):
            if r.get(k) is not None:
                got[f'{n}|{m}'] = r[k]
    for q, (v, _) in c['fo_take_rate'].items():
        got[f'fo_take_rate_q|{q}'] = v
    for q, r in c['cash_quarter'].items():
        for k, n in (('tpo', 'cash_tpo_q'), ('mkt_trades_mn', 'cash_mkt_trades_q'), ('take_rate', 'cash_take_rate_q'),
                     ('share', 'cash_share_q')):
            if r.get(k) is not None:
                got[f'{n}|{q}'] = r[k] * (1e6 if k == 'mkt_trades_mn' else 1)
    for m, r in c['comm_month'].items():
        for k, n in (('mcx_contracts', 'mcx_contracts_m'), ('mkt_orders', 'comm_mkt_orders_m'),
                     ('comm_orders', 'comm_orders_m'), ('cpo', 'comm_cpo_m'), ('share', 'comm_share_m')):
            if r.get(k) is not None:
                got[f'{n}|{m}'] = r[k]
    got['comm_take_rate_fixed'] = c['comm_take_rate'][0]
    for q, r in c['mtf_quarter'].items():
        for k, n in (('industry_avg_cr', 'mtf_industry_avg_q'), ('angel_book_cr', 'mtf_angel_book_q'), ('share', 'mtf_share_q')):
            if r.get(k) is not None:
                got[f'{n}|{q}'] = r[k]
    for q, r in c['take_rates'].items():
        for k, n in (('total_income', 'total_income_q'), ('comm_pct', 'comm_pct_q'), ('fo_pct', 'fo_pct_q'), ('rev_fo_mn', 'fo_rev_q_mn'), ('rev_cash_mn', 'cash_rev_q_mn'),
                     ('rev_comm_mn', 'comm_rev_q_mn'), ('take_rate_fo', 'take_rate_fo_q'),
                     ('take_rate_cash', 'take_rate_cash_q'), ('take_rate_comm', 'take_rate_comm_q')):
            if k in r:
                got[f'{n}|{q}'] = r[k]
    for cell, (_, _, v) in cells.items():
        got[f'summary|{cell}'] = v

    rows = []
    for e in expected:
        key = e['key'] if e['kind'] != 'summary' else 'summary|' + e['excel_ref'].split('!')[1]
        g = got.get(key, 'MISSING')
        ok = (g != 'MISSING' and g is not None and e['value'] is not None
              and abs(g - e['value']) <= max(abs_, rel * abs(e['value'])))
        rows.append({'kind': e['kind'], 'key': e['key'], 'excel_ref': e['excel_ref'], 'expected': e['value'],
                     'got': g, 'ok': ok, 'out_of_scope': None if ok else _scope(e['key'])})
    return rows


def report(rows):
    by = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        name = r['kind'] + ':' + (r['key'].split('|')[0] if r['kind'] != 'summary' else r['key'].split('|')[0])
        by[name][0] += 1
        by[name][1] += r['ok']
        by[name][2] += bool(r.get('out_of_scope'))
    return dict(by)
