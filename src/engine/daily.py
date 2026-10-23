"""Daily Angel One revenue by segment (parity mode) — reproduces backtesting F&O!AA, backtesting cash!S,
Commodities!I, MTF data (2)!O/P."""
from collections import defaultdict
from .inputs import fy_month_of, q_of
from . import calibrate as C


def _sum_by(series, keyfn, dates=None):
    out = defaultdict(float)
    for d, v in series.items():
        if v is not None and (dates is None or d in dates):
            out[keyfn(d)] += v
    return dict(out)


def run(I):
    res = {'calib': {}, 'daily': {}}
    tr = C.take_rates(I)
    res['calib']['take_rates'] = tr

    # ── F&O ──
    nse = I.series('nse_fo', 'contracts'); bse = I.series('bse_fo', 'contracts')
    bse_status = I.status('bse_fo', 'contracts')
    # monthly market contracts (' F&O market'!J) come from the exchange sheets, so imputed BSE days use
    # the real exchange value when we have it (lake); the daily column V keeps the workbook's value.
    bse_for_month = {d: (I.lake[('bse_fo', 'contracts')].get(d, v) if bse_status.get(d) == 'imputed' else v)
                     for d, v in bse.items()}
    mkt_m = defaultdict(float)
    for d in nse:
        mkt_m[fy_month_of(d)] += nse[d] + bse_for_month.get(d, 0)
    fo_m, fo_trq = C.calib_fo(I, dict(mkt_m), tr)
    res['calib']['fo_month'], res['calib']['fo_take_rate'] = fo_m, fo_trq
    fo = {}
    for d in sorted(nse):
        m, q = fy_month_of(d), q_of(d)
        if m not in fo_m or q not in fo_trq:
            continue
        V = (nse[d] + bse[d]) / 1e6                       # V, Mn contracts
        X = V / fo_m[m]['cpo']                            # market orders
        Z = X * fo_m[m]['share']                          # Angel F&O orders (Mn)
        fo[d] = {'orders_mn': Z, 'rev_mn': Z * fo_trq[q][0], 'cpo': fo_m[m]['cpo'], 'share': fo_m[m]['share'],
                 'regime': 'actual' if fo_m[m]['regime'] == 'actual' and fo_trq[q][1] == 'actual' else 'projected'}
    res['daily']['fo'] = fo

    # ── Cash ──
    nt = I.series('nse_cash', 'trades'); bt = I.series('bse_cash', 'trades')
    trades = {d: (nt[d] + bt.get(d, 0)) / 1e6 for d in nt}  # N, Mn trades
    cash_q = C.calib_cash(I, _sum_by(trades, q_of), tr)
    res['calib']['cash_quarter'] = cash_q
    cash = {}
    for d in sorted(trades):
        q = q_of(d)
        if q not in cash_q:
            continue
        c = cash_q[q]
        R = trades[d] * c['share'] / c['tpo']
        cash[d] = {'orders_mn': R, 'rev_mn': R * c['take_rate'], 'tpo': c['tpo'], 'share': c['share'],
                   'regime': c['regime']}
    res['daily']['cash'] = cash

    # ── Commodities ──
    mcx = I.series('mcx', 'contracts')
    comm_m, comm_tr, comm_tr_q = C.calib_comm(I, _sum_by(mcx, fy_month_of))
    res['calib']['comm_month'], res['calib']['comm_take_rate'] = comm_m, (comm_tr, comm_tr_q)
    comm = {}
    for d in sorted(mcx):
        m = fy_month_of(d)
        if m not in comm_m:
            continue
        G = (mcx[d] / 1e6) / comm_m[m]['cpo']
        H = G * comm_m[m]['share']
        comm[d] = {'orders_mn': H, 'rev_mn': H * comm_tr, 'cpo': comm_m[m]['cpo'], 'share': comm_m[m]['share'],
                   'regime': comm_m[m]['regime']}
    res['daily']['comm'] = comm

    # ── MTF ──
    book = I.series('mtf_industry', 'book_cr')
    from statistics import mean as _mean
    byq = {}
    for dd, v in book.items():
        byq.setdefault(q_of(dd), []).append(v)
    mtf_q = C.calib_mtf(I, {q: _mean(v) for q, v in byq.items()})
    res['calib']['mtf_quarter'] = mtf_q
    y, basis, net = I.assume['mtf_yield'][0], I.assume['mtf_day_basis'][0], I.assume['mtf_net_factor'][0]
    mtf = {}
    for d in sorted(book):
        q = q_of(d)
        sh = mtf_q[q]['share']
        N = sh * book[d]
        O = N * (y / basis)
        mtf[d] = {'share': sh, 'angel_book_cr': N, 'gross_cr': O, 'net_cr': O * net, 'regime': mtf_q[q]['regime']}
    res['daily']['mtf'] = mtf
    return res
