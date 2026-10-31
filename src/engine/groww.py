"""Groww daily revenue by segment, parity mode (docs/Groww_ADR_Methodology.md, section 8b).

Groww publishes no orders, so the workbook borrows Angel One's market calibration (contracts per order by
month, trades per order by quarter, commodity market orders and contracts per order, commodity take rates)
and adds Groww's own quarterly inputs (revenue mix, total income, ADTO shares, MTF revenue). This module
reads Angel's calibration from the Angel engine run (`daily.run`) and re-implements none of it.

Reproduces: backtesting F&O!AD, backtesting cash!V, Commodities!K, MTF data (2)!L.

Workbook quirks kept in parity mode (section 8c): zero-fill before 1 Jul 2025 (numeric 0 for Q3 FY25-Q1 FY26,
#N/A for Q2 FY25), blank commodities before 1 Oct 2025, fixed commodity calibration, typed 5% growths, the
Q1 FY27 F&O not fed, the BSE freeze (it is in the input series), MTF gross only.

Live switches g-a ... g-g (docs/GROWW_LIVE_SPEC.md, src/engine/groww_switches.py) are read from GrowwInputs.switches;
each changes inputs (an overlay of reviewed facts, pins, assumptions) or a rule behind `G.on(letter)`. With none on,
every line below is the parity code path.
"""
import json
from collections import defaultdict
from statistics import mean

from .inputs import Inputs, fy_month_of, fy_of, months_of_quarter, q_of, quarter_seq
from . import daily as ANGEL
from . import groww_switches as GS

BROKER = 'GROWW'


class GrowwInputs:
    """Groww's own inputs from a groww_snapshot_*.json (facts / assumptions / pins with broker_id = 'GROWW').

    switches: Groww live switches g-a ... g-g (src/engine/groww_switches.py); none = parity (the workbook).
    reviewed_facts: the reviewed Groww fact rows the switches read (needed as soon as one is on)."""

    def __init__(self, snap, switches=(), reviewed_facts=None):
        assert snap.get('broker_id') == BROKER, snap.get('broker_id')
        self.snap = snap
        self._facts = {}
        for f in snap['facts']:
            assert f['broker_id'] == BROKER, f
            self._facts[(f['metric'], f['period_key'])] = f
        self._assume = {}
        for a in snap['assumptions']:
            assert a['broker_id'] == BROKER, a
            self._assume[a['key']] = a
        self._pins = {}
        for p in snap['pins']:
            assert p['broker_id'] == BROKER, p
            self._pins[(p['key'], p['period_key'])] = p
        self.switches = GS.check(switches)
        self.overlay, self._pin_over, self._assume_over = {}, {}, {}
        if self.switches:
            if reviewed_facts is None:
                raise GS.SwitchError('Groww live switches need the reviewed facts')
            self.overlay = GS.build_overlay(self.switches, reviewed_facts, self._facts, self._assume)
            self._pin_over = GS.pin_overrides(self.switches)
            self._assume_over = GS.assume_overrides(self.switches)

    def fact(self, metric, period):
        o = self.overlay.get((metric, period))
        if o is not None:
            return o.value
        f = self._facts.get((metric, period))
        if f is None:
            raise KeyError(f'Groww fact {metric} for {period} is not in the snapshot')
        return f['value']

    def assume(self, key):
        if key in self._assume_over:
            return self._assume_over[key]
        if key == 'mtf_yield' and ('mtf_yield', GS.YIELD_PERIOD) in self.overlay:
            return self.overlay[('mtf_yield', GS.YIELD_PERIOD)].value
        a = self._assume[key]
        return a['value'] if a['value'] is not None else a['value_text']

    def pin(self, key, period=''):
        if (key, period) in self._pin_over:
            return self._pin_over[(key, period)]
        return self._pins[(key, period)]['value_text']

    def on(self, letter):
        return letter in self.switches


def load(angel_snapshot, groww_snapshot, switches=(), reviewed_path=None):
    """(Inputs, GrowwInputs) from the Angel snapshot and the Groww snapshot paths.

    switches: Groww switches. g-c is Angel switch c on the shared exchange series (its market_overrides); the Angel
    calibration Groww borrows is otherwise Angel's parity run."""
    switches = GS.check(switches)
    reviewed = GS.load_reviewed(reviewed_path or GS.REVIEWED) if switches else None
    I = Inputs(json.load(open(angel_snapshot)), ('c',) if 'c' in switches else ())
    return I, GrowwInputs(json.load(open(groww_snapshot)), switches, reviewed)


def _qkey(q):
    return int(q[-4:]), int(q[1])


def _le(a, b):
    return _qkey(a) <= _qkey(b)


# ── quarterly parameters ──
LIVE_SEGMENTS = ('fo', 'cash', 'comm')


def _base_kind(G, q):
    try:
        return G.pin('revenue_base', q)
    except KeyError:
        if not G.switches:
            raise
        return 'total_income'                  # live: a quarter without a pin (Q2 FY27) is on total income


def _base(G, q):
    which = _base_kind(G, q)
    if which == 'total_income':
        if ('total_income', q) in G.overlay:
            return G.fact('total_income', q)                                       # consolidated total income, filed
        return G.fact('revenue_from_ops', q) + G.fact('other_income', q)           # H105 = H103 + H104
    return G.fact(which, q)


def segment_revenue(G):
    """rev[seg][q] in Rs Mn = revenue-mix % x base (Working sheet - Groww rows 17-19, 22).
    Base = total income (Q2, Q3 FY26: row 105 = 103 + 104) or income excluding Fisdom/AMC (Q4 FY26, Q1 FY27: row 120).
    Live: every quarter with a mix and a base (consolidated total income once switch g-a is on)."""
    rev = defaultdict(dict)
    if not G.switches:
        plan = (('Q2 FY 2026', ('fo', 'cash')), ('Q3 FY 2026', ('fo', 'cash', 'comm')),
                ('Q4 FY 2026', ('fo', 'cash')), ('Q1 FY 2027', ('cash',)))
    else:
        last = max((q for m, q in list(G._facts) + list(G.overlay) if m.startswith('revmix_')), key=_qkey)
        plan = [(q, LIVE_SEGMENTS) for q in quarter_seq('Q1 FY 2026', last)]
    for q, segs in plan:
        for s in segs:
            if not G.switches:
                rev[s][q] = G.fact(f'revmix_{s}', q) * _base(G, q)
            else:
                try:
                    rev[s][q] = G.fact(f'revmix_{s}', q) * _base(G, q)
                except KeyError:
                    continue                                                       # no mix or no base: not usable
    return rev


def fo_parameters(I, G, angel, V_by_q, last_q):
    """backtesting F&O!AM48:AR57: share (row 57) and take rate (row 56) by quarter. Calibrated Q2-Q4 FY26,
    then the last take rate carried and the last share x (1 + typed growth), then carried.
    Live: g-b starts at Q1 FY26, g-d runs to the last reported quarter, g-e drops the typed growth."""
    rev = segment_revenue(G)['fo']
    cpo_m = {m: r['cpo'] for m, r in angel['calib']['fo_month'].items()}
    growth = 0.0 if G.on('e') else G.assume('share_growth_fo')
    first, last = G.pin('fo_first_calibrated_quarter'), G.pin('fo_last_actual_quarter')
    out = {}
    for q in quarter_seq(first, last_q):
        if _le(q, last):
            cpo_q = mean(cpo_m[m] for m in months_of_quarter(q))                  # ' F&O market'!J43, J46, J49
            share = G.fact('share_fo_adto_q', q)
            orders = V_by_q[q] / cpo_q * share                                    # AJ45:AL45
            out[q] = {'share': share, 'take_rate': rev[q] / orders, 'cpo_q': cpo_q, 'orders_mn': orders,
                      'rev_mn': rev[q], 'regime': 'actual', 'rule': 'take rate = revenue / (contracts / CPO x share)'}
        else:
            prev = out[quarter_seq(first, q)[-2]]
            share = prev['share'] * (1 + growth) if prev['regime'] == 'actual' else prev['share']
            out[q] = {'share': share, 'take_rate': prev['take_rate'], 'regime': 'projected',
                      'rule': 'share = last actual x (1 + growth) then carried; take rate carried'}
    return out


def cash_parameters(I, G, angel, N_by_q, last_q):
    """cash market!F35:L43: trades per order G (Angel's), take rate K, share L by quarter.
    Calibrated Q2 FY26-Q1 FY27; then the mean of the last 3 quarters (take rate), carried (share), then carried.
    Live: g-b starts at Q1 FY26, g-d runs to the last reported quarter, g-e carries the last actual take rate."""
    rev = segment_revenue(G)['cash']
    tpo = {q: r['tpo'] for q, r in angel['calib']['cash_quarter'].items()}
    first, last = G.pin('cash_first_calibrated_quarter'), G.pin('cash_last_actual_quarter')
    out, hist = {}, []
    for q in quarter_seq(first, last_q):
        if _le(q, last):
            share = G.fact('share_cash_adto_q', q)
            orders = N_by_q[q] / tpo[q] * share                                   # Working sheet - Groww H67:L67
            tr = rev[q] / orders                                                  # H72:L72
            out[q] = {'share': share, 'take_rate': tr, 'tpo': tpo[q], 'orders_mn': orders, 'rev_mn': rev[q],
                      'regime': 'actual'}
            hist.append(tr)
        else:
            prev = out[quarter_seq(first, q)[-2]]
            if G.on('e'):
                tr = prev['take_rate']                                            # one rule: carry the last actual
            else:
                tr = mean(hist[-3:]) if prev['regime'] == 'actual' else prev['take_rate']   # K42 = AVERAGE(K39:K41), K43 = K42
            out[q] = {'share': prev['share'], 'take_rate': tr, 'tpo': tpo[q], 'regime': 'projected'}
    return out


def comm_parameters(I, G, angel):
    """Commodities!S3:S9, once: Groww Q3 FY26 commodity revenue / Angel's mean take rate = Groww orders;
    / Angel's market orders Oct-Dec 2025 = Groww 'share'; x (1 + typed growth) for every day."""
    qc = G.pin('comm_calibration_quarter')
    rev = segment_revenue(G)['comm'][qc]                                          # S3 = I19 = I9 x I105
    tr_q = angel['calib']['take_rates']
    take_rate = mean(tr_q[q]['take_rate_comm'] for q in G.assume('comm_take_rate_basis').split(','))   # S5
    orders = rev / take_rate                                                      # S6
    mkt = sum(angel['calib']['comm_month'][m]['mkt_orders'] for m in months_of_quarter(qc))   # S7 = SUM(X32:X34)
    share0 = orders / mkt                                                         # S8
    growth = G.assume('share_growth_comm')                                        # S9
    return {'take_rate': take_rate, 'share0': share0, 'growth': growth, 'share': share0 * (1 + growth),
            'rev_mn': rev, 'orders_mn': orders, 'mkt_orders_mn': mkt, 'quarter': qc}


def comm_parameters_quarterly(I, G, angel, mkt_orders_by_q, last_q):
    """g-d: each reported commodity quarter calibrates on its own revenue (mix x total income).
    Groww discloses no commodity orders, so the take rate is Angel's own for that quarter (the latest earlier one for a
    quarter Angel has none for); orders = revenue / take rate; share = orders / the quarter's market orders (the sum of
    the daily market orders, contracts / Angel's contracts per order). Unreported quarters: last actual share
    x (1 + typed growth) (none under g-e), take rate carried."""
    rev = segment_revenue(G)['comm']
    tr_q = angel['calib']['take_rates']
    first, last = G.pin('comm_first_calibrated_quarter'), G.pin('comm_last_actual_quarter')
    growth = 0.0 if G.on('e') else G.assume('share_growth_comm')
    out, rate, rate_from = {}, None, None
    for q in quarter_seq(first, last_q):
        if _le(q, last):
            r = tr_q.get(q, {}).get('take_rate_comm')
            if r is not None:
                rate, rate_from = r, q
            elif rate is None:
                raise ValueError(f'Groww commodities: no Angel take rate for {q} or any earlier quarter')
            orders = rev[q] / rate
            out[q] = {'take_rate': rate, 'take_rate_from': rate_from, 'rev_mn': rev[q], 'orders_mn': orders,
                      'mkt_orders_mn': mkt_orders_by_q[q], 'share': orders / mkt_orders_by_q[q], 'regime': 'actual'}
        else:
            prev = out[quarter_seq(first, q)[-2]]
            share = prev['share'] * (1 + growth) if prev['regime'] == 'actual' else prev['share']
            out[q] = {'take_rate': prev['take_rate'], 'take_rate_from': prev['take_rate_from'], 'share': share,
                      'regime': 'projected'}
    return out


def fy_trading_days(cal):
    """{fy: (trading days, complete, counted FY)} from the calendar's equity days. An FY the calendar does not cover
    end to end (FY27 so far) uses the latest complete FY's count and says so."""
    first, last = min(cal), max(cal)
    days = defaultdict(int)
    for d, r in cal.items():
        if r['is_equity_day']:
            days[r['fy']] += 1
    done = {fy: (n, True, fy) for fy, n in days.items()
            if f'{int(fy[3:]) - 1}-04-01' >= first and f'{fy[3:]}-03-31' <= last}
    latest = max(done, key=lambda f: int(f[3:]))
    return {fy: done.get(fy, (done[latest][0], False, latest)) for fy in days}


def mtf_parameters(I, G, last_q, book=None, fy_days=None):
    """MTF data!I51:J60: Groww average book = revenue / (yield / 4); share = book / industry average of the
    monthly series; typed shares from Q2 FY27.
    g-e: unreported quarters carry the last actual share (no typed share). g-f: see mtf_parameters_by_revenue."""
    if G.on('f'):
        return mtf_parameters_by_revenue(I, G, last_q, book, fy_days)
    y, qf = G.assume('mtf_yield'), G.assume('mtf_quarter_fraction')
    last = G.pin('mtf_last_actual_quarter')
    out = {}
    for q in quarter_seq('Q3 FY 2025', last_q):
        if _le(q, last):
            ind = mean(I.monthly[('mtf_industry', 'book_cr', m)] for m in months_of_quarter(q))   # D51:D57
            book_cr = G.fact('mtf_revenue', q) / (y / qf)                                         # I51:I57
            out[q] = {'industry_avg_cr': ind, 'groww_book_cr': book_cr, 'share': book_cr / ind, 'regime': 'actual',
                      'revenue_cr': G.fact('mtf_revenue', q)}
        elif G.on('e'):
            prev = out[quarter_seq('Q3 FY 2025', q)[-2]]
            out[q] = {'share': prev['share'], 'regime': 'carried'}
        else:
            out[q] = {'share': G.fact('mtf_share_override', q), 'regime': 'typed'}               # J58:J60
    return out


def mtf_parameters_by_revenue(I, G, last_q, book, fy_days):
    """g-f: the quarter's disclosed revenue is spread over its own days: share = revenue / (yield x days in quarter /
    days in FY) / industry average book (daily series), so the model's quarter total equals the disclosed revenue.
    Unreported quarters: the typed share (parity) or, under g-e, the last actual share carried."""
    y = G.assume('mtf_yield')
    last = G.pin('mtf_last_actual_quarter')
    byq = defaultdict(list)
    for d, v in book.items():
        byq[q_of(d)].append(v)
    out = {}
    for q in quarter_seq('Q3 FY 2025', last_q):
        if _le(q, last):
            n, D, ind = len(byq[q]), fy_days[_fy_of_quarter(q)][0], mean(byq[q])
            book_cr = G.fact('mtf_revenue', q) / (y * n / D)
            out[q] = {'industry_avg_cr': ind, 'groww_book_cr': book_cr, 'share': book_cr / ind, 'regime': 'actual',
                      'days_in_quarter': n, 'days_in_fy': D, 'revenue_cr': G.fact('mtf_revenue', q)}
        elif G.on('e'):
            prev = out[quarter_seq('Q3 FY 2025', q)[-2]]
            out[q] = {'share': prev['share'], 'regime': 'carried'}
        else:
            out[q] = {'share': G.fact('mtf_share_override', q), 'regime': 'typed'}
    return out


def _fy_of_quarter(q):
    """'Q3 FY 2026' -> 'FY 2026'"""
    return q[3:]


# ── daily revenue ──
def run(I, G, angel=None):
    """Groww's calibration and daily revenue. `angel` = daily.run(I) (Angel's calibration is reused as is).
    I may carry Angel switch c (g-c) and nothing else."""
    if I.switches - {'c'}:
        raise ValueError('Groww needs an Inputs object without live switches (g-c alone may be on)')
    if ('c' in I.switches) != G.on('c'):
        raise ValueError('g-c is Angel switch c on the exchange series: load both with the same switches')
    angel = angel or ANGEL.run(I)
    zero_q = G.assume('zero_fill_quarters').split(',')
    live_fo, live_cash, live_comm = (G.assume(f'first_live_date_{s}') for s in ('fo', 'cash', 'comm'))

    nse, bse = I.series('nse_fo', 'contracts'), I.series('bse_fo', 'contracts')
    fo_days = sorted(d for d in nse if d >= '2024-07-01')                         # rows 189-761
    V = {d: (nse[d] + bse[d]) / 1e6 for d in fo_days}                             # V, Mn contracts
    nt, bt = I.series('nse_cash', 'trades'), I.series('bse_cash', 'trades')
    cash_days = sorted(d for d in nt if d >= '2024-07-01')                        # rows 188-760
    N = {d: (nt[d] + bt.get(d, 0)) / 1e6 for d in cash_days}                      # N, Mn trades
    mcx = I.series('mcx', 'contracts')
    book = I.series('mtf_industry', 'book_cr')

    last_q = max((q_of(d) for d in list(fo_days) + list(cash_days) + list(mcx) + list(book)), key=_qkey)
    V_q, N_q = defaultdict(float), defaultdict(float)
    for d, v in V.items():
        V_q[q_of(d)] += v
    for d, v in N.items():
        N_q[q_of(d)] += v
    fo_q = fo_parameters(I, G, angel, V_q, last_q)
    cash_q = cash_parameters(I, G, angel, N_q, last_q)
    cpo_fo = {m: r['cpo'] for m, r in angel['calib']['fo_month'].items()}
    comm_m = angel['calib']['comm_month']
    fy_days = fy_trading_days(I.cal) if G.on('f') else None
    mtf_q = mtf_parameters(I, G, last_q, book, fy_days)
    if G.on('d'):
        mkt_q = defaultdict(float)
        for d in mcx:
            if d >= live_comm:
                mkt_q[q_of(d)] += (mcx[d] / 1e6) / comm_m[fy_month_of(d)]['cpo']    # the quarter's market orders
        comm = comm_parameters_quarterly(I, G, angel, mkt_q, last_q)
    else:
        comm = comm_parameters(I, G, angel)

    def stub(d, q, live, table, what):
        """Days before first live: None (#N/A) before the zero-fill quarters, 0.0 inside them. Raises if a
        live day has no parameters (the sheet would show an error that IFERROR turns into 0)."""
        if d < live:
            if q in zero_q:
                return 0.0
            if _qkey(q) < _qkey(zero_q[0]):
                return None
        if q not in table:
            raise ValueError(f'Groww {what}: no parameters for {q} ({d}); the workbook shows an error here')
        return 'live'

    fo = {}
    for d in fo_days:
        q = q_of(d)
        mode = stub(d, q, live_fo, fo_q, 'F&O')
        if mode == 'live':
            m = fy_month_of(d)
            X = V[d] / cpo_fo[m]                                                  # market orders
            AC = X * fo_q[q]['share']                                             # Groww orders
            fo[d] = {'orders_mn': AC, 'rev_mn': AC * fo_q[q]['take_rate'], 'cpo': cpo_fo[m],
                     'share': fo_q[q]['share'], 'regime': fo_q[q]['regime']}
        else:
            fo[d] = {'orders_mn': mode, 'rev_mn': mode, 'regime': 'not_live'}
    cash = {}
    for d in cash_days:
        q = q_of(d)
        mode = stub(d, q, live_cash, cash_q, 'cash')
        if mode == 'live':
            c = cash_q[q]
            U = N[d] * c['share'] / c['tpo']                                      # Groww orders
            cash[d] = {'orders_mn': U, 'rev_mn': U * c['take_rate'], 'tpo': c['tpo'], 'share': c['share'],
                       'regime': c['regime']}
        else:
            cash[d] = {'orders_mn': mode, 'rev_mn': mode, 'regime': 'not_live'}
    comm_d = {}
    for d in sorted(mcx):
        if d < live_comm:
            continue                                                              # blank, not 0
        m = fy_month_of(d)
        G_ = (mcx[d] / 1e6) / comm_m[m]['cpo']                                    # Commodities!G
        if G.on('d'):
            cq = comm[q_of(d)]
            J = G_ * cq['share']
            comm_d[d] = {'orders_mn': J, 'rev_mn': J * cq['take_rate'], 'cpo': comm_m[m]['cpo'],
                         'share': cq['share'], 'regime': cq['regime']}
        else:
            J = G_ * comm['share']
            comm_d[d] = {'orders_mn': J, 'rev_mn': J * comm['take_rate'], 'cpo': comm_m[m]['cpo'],
                         'regime': comm_m[m]['regime']}
    y, basis = G.assume('mtf_yield'), G.assume('mtf_day_basis')
    mtf = {}
    for d in sorted(book):
        q = q_of(d)
        if q not in mtf_q:
            raise ValueError(f'Groww MTF: no share for {q} ({d})')
        D = fy_days[fy_of(d)][0] if G.on('f') else basis                          # g-f: the FY's actual trading days
        K = mtf_q[q]['share'] * book[d]                                           # Groww book, Rs Cr
        mtf[d] = {'share': mtf_q[q]['share'], 'groww_book_cr': K, 'gross_cr': K * (y / D),
                  'regime': mtf_q[q]['regime']}
    calib = {'fo_quarter': fo_q, 'cash_quarter': cash_q, 'mtf_quarter': mtf_q, 'revenue': segment_revenue(G)}
    calib['comm_quarter' if G.on('d') else 'comm'] = comm
    if G.on('f'):
        calib['fy_days'] = fy_days
    return {'calib': calib, 'daily': {'fo': fo, 'cash': cash, 'comm': comm_d, 'mtf': mtf}}
