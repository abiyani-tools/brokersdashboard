"""Motilal Oswal (MOSL) daily revenue by segment, parity mode (docs/MOSL_ADR_Methodology.md, sections 3, 4, 6, 8b).

MOSL publishes no orders, so nothing is borrowed from Angel One or Groww. Each segment spreads the quarter's reported
gross brokerage over the days of the quarter by an exchange key, then applies the reported net / gross ratio:
  F&O          key = NSE index-option contracts + BSE contracts      ->  backtesting F&O!AG   (net, Rs Mn)
  Cash         key = NSE + BSE cash turnover (Rs Cr, as the workbook uses it)  ->  backtesting cash!AB (net, Rs Cr)
  Commodities  key = MCX contracts                                    ->  Commodities!O        (net, Rs Mn)
  MTF          MOSL closing-book share x industry daily book x typed NII yield / 247  ->  MTF data (2)!X (Rs Cr)
All four calibrations are quarterly; the quarter tables are rebuilt here from the typed inputs and the day counts, so
the engine is calendar-driven (the workbook's hand-extended lookup ranges become explicit rules, below).

The literal chain is followed, including the terms that cancel in a calibrated quarter (share, premium ADTO,
'delivery ratio'): F&O sum(AF) = 10 x reported gross, cash sum(AA) = reported gross, commodities sum(L) = 10 x gross.

Workbook quirks kept in parity mode (section 8c):
  - cash take rate J per QUARTER, and Q1 FY27 J = Q4 FY26 J (the typed 228 is ignored);
  - rounded typed inputs; commodity share of Q2 FY27 = mean of the last four typed shares (take rate carried);
  - the cash key (NSE + BSE turnover) is two rows out of date alignment from 9 Jun 2025 (it is the input series);
  - Q2 FY27 is an estimate (carries and trailing averages), Q3 FY27 exists for F&O only (13 days of cash AA
    are computed but AB is #N/A: the net-ratio HLOOKUP range ends at Q2 FY27); commodities Q3 FY27 O is #N/A
    before `comm_o_blank_from_date` and blank from it; MTF has no row after the last formula date;
  - F&O Q3/Q4 FY24 are #N/A (no table row), Q1/Q2 FY25 numeric 0 (blank rate), 31 May 2024 is #VALUE! (text key).

Daily rows: {date: {'rev_<unit>': net or None, 'gross_<unit>': gross or None, 'err': '#N/A' | '#VALUE!' | None}}.
A date with no row is a blank cell. summary.build(daily, 'MOSL') turns an 'err' row into the workbook's IFERROR 0.
"""
import json
from collections import Counter, defaultdict

from .inputs import q_of

BROKER = 'MOSL'
Q_ALL = ['Q1 FY 2025', 'Q2 FY 2025', 'Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026',
         'Q4 FY 2026', 'Q1 FY 2027', 'Q2 FY 2027', 'Q3 FY 2027']
NA, VALUE = '#N/A', '#VALUE!'

# the shared snapshot's series MOSL reads unchanged (Commodities!F, MTF data (2)!I)
SHARED = {'mcx': ('mcx', 'contracts'), 'mtf_industry': ('mtf_industry', 'book_cr')}


class MoslInputs:
    """MOSL's own inputs from a mosl_snapshot_*.json (facts / assumptions / pins with broker_id = 'MOSL', and the
    exchange series the shared snapshot lacks) plus the shared snapshot's MCX contracts and industry MTF book."""

    def __init__(self, snap, shared):
        assert snap.get('broker_id') == BROKER, snap.get('broker_id')
        self.snap = snap
        self._facts = {}
        for f in snap['facts']:
            assert f['broker_id'] == BROKER, f
            assert (f['metric'], f['period_key']) not in self._facts, f
            self._facts[(f['metric'], f['period_key'])] = f
        self._assume = {}
        for a in snap['assumptions']:
            assert a['broker_id'] == BROKER, a
            self._assume[a['key']] = a
        self._pins = {}
        for p in snap['pins']:
            assert p['broker_id'] == BROKER, p
            self._pins[(p['key'], p['period_key'])] = p
        self._mkt = defaultdict(dict)                     # (dataset, metric) -> {date: value (None = text cell)}
        for m in snap['market_daily']:
            self._mkt[(m['dataset'], m['metric'])][m['trade_date']] = m['value']
        for m in shared['market_daily']:
            if (m['dataset'], m['metric']) in SHARED.values() and m['status'] in ('ok', 'imputed'):
                self._mkt[(m['dataset'], m['metric'])][m['trade_date']] = m['value']

    def fact(self, metric, period):
        f = self._facts.get((metric, period))
        if f is None:
            raise KeyError(f'MOSL fact {metric} for {period} is not in the snapshot')
        return f['value']

    def has_fact(self, metric, period):
        return (metric, period) in self._facts

    def assume(self, key):
        a = self._assume[key]
        return a['value'] if a['value'] is not None else a['value_text']

    def pin(self, key, period=''):
        return self._pins[(key, period)]['value_text']

    def series(self, dataset, metric):
        return self._mkt[(dataset, metric)]


def load(shared_snapshot, mosl_snapshot):
    """MoslInputs from the shared (Angel) snapshot path and the MOSL snapshot path."""
    return MoslInputs(json.load(open(mosl_snapshot)), json.load(open(shared_snapshot)))


def _qkey(q):
    return int(q[-4:]), int(q[1])


def _isnum(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _mean(*xs):
    return sum(xs) / len(xs)


# ── net / gross ratio (assumptions rows 112-114; R and S are formulas) ──
def net_gross(M, seg, q):
    """Reported net / gross brokerage for `seg` ('cash' | 'fo' | 'comm') in quarter q; None where the workbook's
    HLOOKUP finds no column (#N/A). Q2 FY27 = mean(Q4 FY26, Q1 FY27) (R112:R114); F&O Q3 FY27 = Q2 FY27 (S113)."""
    m = f'net_gross_{seg}'
    if M.has_fact(m, q):
        return M.fact(m, q)
    if q == 'Q2 FY 2027':
        return _mean(M.fact(m, 'Q1 FY 2027'), M.fact(m, 'Q4 FY 2026'))
    if q == 'Q3 FY 2027' and seg == 'fo':
        return net_gross(M, 'fo', 'Q2 FY 2027')
    return None


# ── F&O: backtesting F&O!P:S, AE:AG, assumptions!B26:L37 ──
def _fo_tables(M, dates, key):
    """(share I, rate L, table) by quarter. key: {date: S or None (#VALUE!)}."""
    adto_n, adto_b = M.series('nse_fo', 'index_opt_adto'), M.series('bse_fo', 'opt_adto')
    days = Counter(q_of(d) for d in dates)                                   # E = COUNTIF(E:E, quarter)
    S, J, Mm = defaultdict(float), defaultdict(float), defaultdict(float)
    for d in dates:
        q = q_of(d)
        if key[d] is not None:
            S[q] += key[d]
        J[q] += adto_n[d] if _isnum(adto_n.get(d)) else 0
        Mm[q] += adto_b[d] if _isnum(adto_b.get(d)) else 0
    first, last = M.pin('fo_table_first_quarter'), M.pin('fo_last_actual_quarter')
    share = {q: M.fact('share_fo', q) for q in Q_ALL if M.has_fact('share_fo', q)}
    share['Q1 FY 2027'] = _mean(share['Q3 FY 2026'], share['Q4 FY 2026'])    # I35 = AVERAGE(I33:I34)
    share['Q2 FY 2027'] = share['Q1 FY 2027']                                # I36 = I35
    share['Q3 FY 2027'] = share['Q2 FY 2027']                                # I37 = I36
    rate, table = {}, {}
    for q in Q_ALL:
        if M.has_fact('gross_fo_cr', q):
            F = S[q] / 1e7                                                   # Cr contracts
            G = (J[q] + Mm[q]) / days[q]                                     # average premium ADTO
            H = G / F
            Jq = share[q] * G
            K = Jq / H
            rate[q] = (M.fact('gross_fo_cr', q) / K) * 10                    # L = (C/K)*10
            table[q] = dict(F=F, G=G, H=H, J=Jq, K=K)
    rate['Q2 FY 2027'] = rate[last]                                          # L36 = L35
    rate['Q3 FY 2027'] = rate['Q2 FY 2027']                                  # L37 = L36
    zero = set(M.pin('fo_zero_quarters').split(','))
    for q in zero:
        rate[q] = 0.0                                                        # blank L27:L28: VLOOKUP gives 0
    assert first in share and set(share) >= set(rate), (first, sorted(set(rate) - set(share)))
    return share, rate, table


def fo_daily(M):
    p, bse = M.series('nse_fo', 'index_opt_contracts'), M.series('bse_fo', 'opt_contracts_live')
    dates = sorted(p)
    key = {d: (bse[d] + p[d]) if _isnum(p[d]) and _isnum(bse.get(d)) else None for d in dates}   # S = R + P
    share, rate, table = _fo_tables(M, dates, key)
    out = {}
    for d in dates:
        q = q_of(d)
        if q not in share:
            out[d] = dict(rev_mn=None, gross_mn=None, err=NA)                # VLOOKUP miss (Q3, Q4 FY24)
        elif key[d] is None:
            out[d] = dict(rev_mn=None, gross_mn=None, err=VALUE)             # P169 is text
        else:
            gross = share[q] * (key[d] / 1e7) * rate[q]                      # AF (Rs Mn)
            out[d] = dict(rev_mn=net_gross(M, 'fo', q) * gross, gross_mn=gross, err=None)   # AG
    return out, dict(share=share, rate=rate, table=table)


# ── Cash: backtesting cash!I:K, Y:AB, assumptions!B45:N54 ──
def cash_daily(M):
    ni, bi = M.series('nse_cash', 'turnover_cr_xl'), M.series('bse_cash', 'turnover_cr_xl')
    dates = sorted(ni)
    K = {d: ni[d] + bi[d] for d in dates}                                    # K = I + J
    days, tot = Counter(q_of(d) for d in dates), defaultdict(float)
    for d in dates:
        tot[q_of(d)] += K[d]
    first, last = M.pin('cash_table_first_quarter'), M.pin('cash_last_actual_quarter')
    T = {}
    for q in Q_ALL[Q_ALL.index(first):Q_ALL.index(last) + 1]:
        D = days[q]
        C = tot[q] / D                                                       # average NSE + BSE ADTO
        E = M.fact('share_cash', q)
        G = M.fact('adto_cash_mosl', q)
        H = (E * C) / G                                                      # 'delivery ratio' F / G
        T[q] = dict(days=D, share=E, H=H, J=M.fact('gross_cash_cr', q) / G if q != last else None)
    T[last]['J'] = T[Q_ALL[Q_ALL.index(last) - 1]]['J']                      # J52 = J51: typed I52 = 228 not used
    nxt = Q_ALL[Q_ALL.index(last) + 1]                                       # Q2 FY27 (estimate)
    nxt2 = Q_ALL[Q_ALL.index(last) + 2]                                      # Q3 FY27 (13 days so far)
    prev3 = [T[q]['H'] for q in Q_ALL[Q_ALL.index(last) - 2:Q_ALL.index(last) + 1]]
    T[nxt] = dict(days=days[nxt], share=T[last]['share'], H=_mean(*prev3), J=T[last]['J'])
    T[nxt2] = dict(days=days[nxt2], share=T[nxt]['share'],
                   H=_mean(*[T[q]['H'] for q in Q_ALL[Q_ALL.index(last) - 1:Q_ALL.index(last) + 2]]), J=T[nxt]['J'])
    ratio_last = M.pin('cash_net_ratio_last_quarter')
    out = {}
    for d in dates:
        q = q_of(d)
        if q not in T:
            continue                                                         # AB is blank before the first quarter
        t = T[q]
        gross = t['share'] * (K[d] / t['H']) * (t['J'] / t['days'])          # AA (Rs Cr)
        r = net_gross(M, 'cash', q) if _qkey(q) <= _qkey(ratio_last) else None
        out[d] = (dict(rev_cr=r * gross, gross_cr=gross, err=None) if r is not None
                  else dict(rev_cr=None, gross_cr=gross, err=NA))            # AB: HLOOKUP range ends at Q2 FY27
    return out, dict(table=T)


# ── Commodities: Commodities!F, L, M, O, assumptions!B59:L74 ──
def comm_daily(M):
    f = M.series('mcx', 'contracts')
    dates = sorted(f)
    last_q, table_last = M.pin('comm_last_actual_quarter'), M.pin('comm_table_last_quarter')
    quarters = Q_ALL[:Q_ALL.index(table_last) + 1]
    tot = defaultdict(float)
    for d in dates:
        if _isnum(f[d]):
            tot[q_of(d)] += f[d]
    share = {q: M.fact('share_comm', q) for q in quarters if M.has_fact('share_comm', q)}
    nxt = Q_ALL[Q_ALL.index(last_q) + 1]
    share[nxt] = _mean(*[share[q] for q in Q_ALL[Q_ALL.index(last_q) - 3:Q_ALL.index(last_q) + 1]])   # L62
    take, contracts = {}, {}
    for q in quarters:
        if q == nxt:
            take[q] = take[last_q]                                           # L74 = K74
            contracts[q] = tot[q] / 1e6
            continue
        contracts[q] = tot[q] / 1e6                                          # Mn
        take[q] = M.fact('gross_comm_cr', q) * 10 / (share[q] * contracts[q])    # row 74 = row 61 / row 66
    blank_from = M.pin('comm_o_blank_from_date')
    ratio_last = Q_ALL.index(table_last)
    out = {}
    for d in dates:
        q = q_of(d)
        if q not in share:
            if d >= blank_from:
                continue                                                     # formula not extended: blank
            out[d] = dict(rev_mn=None, gross_mn=None, err=NA)                # no column in B59:L74
            continue
        gross = (f[d] / 1e6) * share[q] * take[q]                            # L (Rs Mn)
        r = net_gross(M, 'comm', q) if Q_ALL.index(q) <= ratio_last else None
        out[d] = dict(rev_mn=r * gross, gross_mn=gross, err=None)            # O
    return out, dict(share=share, take=take, contracts_mn=contracts)


# ── MTF: MTF data (2)!I, V:X, assumptions!B5:F18 ──
def mtf_daily(M):
    book = M.series('mtf_industry', 'book_cr')
    dates = sorted(book)
    quarters = Q_ALL[Q_ALL.index('Q3 FY 2025'):Q_ALL.index(M.pin('mtf_last_actual_quarter')) + 1]
    last = {}                                                                # D8:D14: book on the quarter's last date
    for d in dates:
        if _isnum(book[d]):
            last[q_of(d)] = book[d]
    share = {q: M.fact('mtf_book_closing', q) / last[q] for q in quarters}   # E = C / D
    nii = {q: M.fact('mtf_nii_yield', q) for q in quarters}
    nxt = Q_ALL[Q_ALL.index(quarters[-1]) + 1]
    share[nxt], nii[nxt] = share[quarters[-1]], nii[quarters[-1]]            # E15 = E14, F15 = F14
    basis = M.assume('mtf_day_basis')
    stop = M.pin('mtf_last_formula_date')
    out = {}
    for d in dates:
        q = q_of(d)
        if d > stop or q not in share:
            continue                                                         # V:X have no formula: blank
        w = share[q] * book[d]                                               # W: MOSL daily book (Rs Cr)
        out[d] = dict(nii_cr=w * nii[q] / basis, book_cr=w, err=None)        # X
    return out, dict(share=share, nii=nii, industry_close=last)


def run(M):
    """{'daily': {fo, cash, comm, mtf}, 'calib': {...}} in parity mode."""
    fo, fo_c = fo_daily(M)
    cash, cash_c = cash_daily(M)
    comm, comm_c = comm_daily(M)
    mtf, mtf_c = mtf_daily(M)
    ratio = {q: {s: net_gross(M, s, q) for s in ('cash', 'fo', 'comm')} for q in Q_ALL}
    return dict(daily=dict(fo=fo, cash=cash, comm=comm, mtf=mtf),
                calib=dict(fo=fo_c, cash=cash_c, comm=comm_c, mtf=mtf_c, ratio=ratio))
