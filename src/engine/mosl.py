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

Switch m-g (approved by AB on 3 Nov 2026): the quarters start at Q2 FY24 (M.qs, the first-quarter pins) and the same tables calibrate Q2 - Q4 FY24 from
FY24 facts; no row exists before Q2 FY24 (Q1 FY24 is not calibrated), and MTF still starts Q3 FY25.

Daily rows: {date: {'rev_<unit>': net or None, 'gross_<unit>': gross or None, 'err': '#N/A' | '#VALUE!' | None}}.
A date with no row is a blank cell. summary.build(daily, 'MOSL') turns an 'err' row into the workbook's IFERROR 0.
"""
import json
from collections import Counter, defaultdict

from . import mosl_switches as MS
from .inputs import q_of, quarter_seq

BROKER = 'MOSL'
Q_ALL = ['Q1 FY 2025', 'Q2 FY 2025', 'Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026',
         'Q4 FY 2026', 'Q1 FY 2027', 'Q2 FY 2027', 'Q3 FY 2027']
NA, VALUE = '#N/A', '#VALUE!'

# the shared snapshot's series MOSL reads unchanged (Commodities!F, MTF data (2)!I)
SHARED = {'mcx': ('mcx', 'contracts'), 'mtf_industry': ('mtf_industry', 'book_cr')}


class MoslInputs:
    """MOSL's own inputs from a mosl_snapshot_*.json (facts / assumptions / pins with broker_id = 'MOSL', and the
    exchange series the shared snapshot lacks) plus the shared snapshot's MCX contracts and industry MTF book.

    switches: live switches m-a ... m-f (src/engine/mosl_switches.py); none = parity (the workbook).
    reviewed_facts: the reviewed MOSL fact rows the switches read (needed as soon as one is on).
    lake: {'dataset/metric': {date: (value, status)}} the lake's key series (switch b); as_of: ISO date, the series are
    read up to and including it (None = everything)."""

    def __init__(self, snap, shared, switches=(), reviewed_facts=None, lake=None, as_of=None):
        assert snap.get('broker_id') == BROKER, snap.get('broker_id')
        self.snap = snap
        self.as_of = as_of
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
        if as_of is not None:
            for k in self._mkt:
                self._mkt[k] = {d: v for d, v in self._mkt[k].items() if d <= as_of}
        self.cal = {r['trade_date']: r for r in shared.get('calendar', []) if as_of is None or r['trade_date'] <= as_of}
        self.switches = MS.check(switches)
        self.overlay, self._pin_over = {}, {}
        if self.switches:
            if reviewed_facts is None:
                raise MS.SwitchError('MOSL live switches need the reviewed facts')
            self.overlay = MS.build_overlay(self.switches, reviewed_facts, self._facts)
            self._pin_over = MS.pin_overrides(self.switches)
        if 'f' in self.switches and YIELD_KEY not in self._assume:
            raise MS.SwitchError(f'switch m-f: the sb_assumptions row {YIELD_KEY} ({MS.YIELD_LABEL}) is not in the inputs')
        self._lake = {}
        if 'b' in self.switches:
            if lake is None:
                raise MS.SwitchError("switch m-b needs the lake's daily cash turnover and F&O contracts")
            for key in LAKE_KEYS:
                if key not in lake:
                    raise MS.SwitchError(f'switch m-b: the lake series {key} is missing')
                self._lake[key] = {d: v for d, v in lake[key].items() if as_of is None or d <= as_of}

        if 'g' in self.switches:                          # Q2 FY24 is calibrated on its whole key: the series must reach back to it
            starts = {f'lake {k}': min(v) for k, v in self._lake.items() if v}
            starts.update({f'{ds}:{m}': min(v) for (ds, m), v in self._mkt.items() if (ds, m) == SHARED['mcx'] and v})
            late = {k: d for k, d in starts.items() if d > MS.FY24_FIRST_DAY}
            if late or len(starts) < len(LAKE_KEYS) + 1:
                raise MS.SwitchError(f'switch m-g: the key series must start by {MS.FY24_FIRST_DAY} (Q2 FY24 is calibrated on its '
                                     f'whole quarter); they start {late or sorted(starts)}')

    def on(self, letter):
        return letter in self.switches

    @property
    def qs(self):
        """The quarters the tables span: the workbook's Q1 FY25 - Q3 FY27 in parity; live: to the last data day's."""
        if not self.switches:
            return Q_ALL
        last = max([q_of(d) for s in self._mkt.values() for d in s] + [q_of(d) for s in self._lake.values() for d in s]
                   + [Q_ALL[-1]], key=_qkey)
        return quarter_seq(MS.FY24_FIRST if 'g' in self.switches else Q_ALL[0], last)     # m-g: from Q2 FY24

    def fact(self, metric, period):
        o = self.overlay.get((metric, period))
        if o is not None:
            return o.value
        f = self._facts.get((metric, period))
        if f is None:
            raise KeyError(f'MOSL fact {metric} for {period} is not in the snapshot')
        return f['value']

    def has_fact(self, metric, period):
        return (metric, period) in self._facts or (metric, period) in self.overlay

    def assume(self, key):
        a = self._assume[key]
        return a['value'] if a['value'] is not None else a['value_text']

    def has_assume(self, key):
        return key in self._assume

    def pin(self, key, period=''):
        if (key, period) in self._pin_over:
            return self._pin_over[(key, period)]
        return self._pins[(key, period)]['value_text']

    def series(self, dataset, metric):
        return self._mkt[(dataset, metric)]

    def lake(self, dataset, metric):
        """{date: (value, status)} of a lake key series (switch b)."""
        return self._lake[f'{dataset}/{metric}']


YIELD_KEY = MS.YIELD_ASSUMPTION
LAKE_KEYS = ('nse_fo/io_contracts', 'bse_fo/contracts', 'nse_cash/turnover_cr', 'bse_cash/turnover_cr')


def load_lake(path=None):
    """{'dataset/metric': {date: (value, status)}} from a snapshot/mosl_lake_*.json."""
    fx = json.load(open(path or MS.LAKE_FIXTURE))
    return {k: {d: (v, st) for d, v, st in rows} for k, rows in fx['series'].items()}


def load(shared_snapshot, mosl_snapshot, switches=(), reviewed_path=None, lake_path=None, as_of=None, fy24_path=None):
    """MoslInputs from the shared (Angel) snapshot path and the MOSL snapshot path.
    switches: MOSL live switches; the reviewed facts (and, for m-b, the lake fixture) are read from their default fixtures.
    Switch m-g also reads the FY24 facts (fy24_path; default: the FY24 fixture, reviewed per AB's approval of 3 Nov 2026)."""
    switches = MS.check(switches)
    reviewed = MS.load_reviewed(reviewed_path or MS.REVIEWED) if switches else None
    if 'g' in switches:
        reviewed = reviewed + MS.load_reviewed(fy24_path or MS.FY24_REVIEWED)
    lake = load_lake(lake_path) if 'b' in switches else None
    return MoslInputs(json.load(open(mosl_snapshot)), json.load(open(shared_snapshot)), switches, reviewed, lake, as_of)


def _qkey(q):
    return int(q[-4:]), int(q[1])


def _isnum(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _mean(*xs):
    return sum(xs) / len(xs)


# ── net / gross ratio (assumptions rows 112-114; R and S are formulas) ──
def net_gross(M, seg, q):
    """Reported net / gross brokerage for `seg` ('cash' | 'fo' | 'comm') in quarter q; None where the workbook's
    HLOOKUP finds no column (#N/A). Q2 FY27 = mean(Q4 FY26, Q1 FY27) (R112:R114); F&O Q3 FY27 = Q2 FY27 (S113).
    Live: m-e carries the last reported quarter's ratio into every later quarter (no table range, no averaging)."""
    m = f'net_gross_{seg}'
    if M.has_fact(m, q):
        return M.fact(m, q)
    if M.on('e'):
        last = M.pin(f'{seg}_last_actual_quarter')
        return M.fact(m, last) if _qkey(q) > _qkey(last) else None
    if q == 'Q2 FY 2027':
        return _mean(M.fact(m, 'Q1 FY 2027'), M.fact(m, 'Q4 FY 2026'))
    if q == 'Q3 FY 2027' and seg == 'fo':
        return net_gross(M, 'fo', 'Q2 FY 2027')
    return None


def _usable(x):
    """A lake (value, status) pair that may drive a key: present, status ok, positive (zero on a trading day = suspect)."""
    return x is not None and x[1] == 'ok' and x[0] is not None and x[0] > 0


def _regime(M, seg, q):
    return 'actual' if _qkey(q) <= _qkey(M.pin(f'{seg}_last_actual_quarter')) else 'projected'


# ── F&O: backtesting F&O!P:S, AE:AG, assumptions!B26:L37 ──
def _fo_tables(M, dates, key):
    """(share I, rate L, table) by quarter. key: {date: S or None (#VALUE!)}.
    Switch b reads no premium ADTO (the G / H / K terms cancel: K = share x F), so `table` has F and K only."""
    live_b = M.on('b')
    if not live_b:
        adto_n, adto_b = M.series('nse_fo', 'index_opt_adto'), M.series('bse_fo', 'opt_adto')
    qs = M.qs
    days = Counter(q_of(d) for d in dates)                                   # E = COUNTIF(E:E, quarter)
    S, J, Mm = defaultdict(float), defaultdict(float), defaultdict(float)
    for d in dates:
        q = q_of(d)
        if key[d] is not None:
            S[q] += key[d]
        if not live_b:
            J[q] += adto_n[d] if _isnum(adto_n.get(d)) else 0
            Mm[q] += adto_b[d] if _isnum(adto_b.get(d)) else 0
    first, last = M.pin('fo_table_first_quarter'), M.pin('fo_last_actual_quarter')
    share = {q: M.fact('share_fo', q) for q in qs if M.has_fact('share_fo', q)}
    if not M.has_fact('share_fo', 'Q1 FY 2027'):
        share['Q1 FY 2027'] = _mean(share['Q3 FY 2026'], share['Q4 FY 2026'])    # I35 = AVERAGE(I33:I34)
    if not M.has_fact('share_fo', 'Q2 FY 2027'):
        share['Q2 FY 2027'] = share['Q1 FY 2027']                                # I36 = I35
    share['Q3 FY 2027'] = share['Q2 FY 2027']                                    # I37 = I36
    rate, table = {}, {}
    for q in qs:
        if M.has_fact('gross_fo_cr', q):
            F = S[q] / 1e7                                                   # Cr contracts
            if live_b:
                K = share[q] * F
                table[q] = dict(F=F, K=K)
            else:
                G = (J[q] + Mm[q]) / days[q]                                 # average premium ADTO
                H = G / F
                Jq = share[q] * G
                K = Jq / H
                table[q] = dict(F=F, G=G, H=H, J=Jq, K=K)
            rate[q] = (M.fact('gross_fo_cr', q) / K) * 10                    # L = (C/K)*10
    rate['Q2 FY 2027'] = rate[last]                                          # L36 = L35
    rate['Q3 FY 2027'] = rate['Q2 FY 2027']                                  # L37 = L36
    for q in qs[qs.index('Q3 FY 2027') + 1:]:                                # live: later quarters carry (m-e rule)
        share[q], rate[q] = share[qs[qs.index(q) - 1]], rate[qs[qs.index(q) - 1]]
    zero = {x for x in M.pin('fo_zero_quarters').split(',') if x}
    for q in zero:
        rate[q] = 0.0                                                        # blank L27:L28: VLOOKUP gives 0
    assert first in share and set(share) >= set(rate), (first, sorted(set(rate) - set(share)))
    return share, rate, table


def fo_daily(M):
    live_c = M.on('c')
    if M.on('b'):
        pl, bl = M.lake('nse_fo', 'io_contracts'), M.lake('bse_fo', 'contracts')
        dates = sorted(pl)
        key = {}
        for d in dates:
            if live_c:
                key[d] = pl[d][0] + bl[d][0] if _usable(pl[d]) and _usable(bl.get(d)) else None
            else:
                key[d] = pl[d][0] + bl[d][0] if bl.get(d) is not None else None      # S = R + P, as read
    else:
        p, bse = M.series('nse_fo', 'index_opt_contracts'), M.series('bse_fo', 'opt_contracts_live')
        dates = sorted(p)
        key = {d: (bse[d] + p[d]) if _isnum(p[d]) and _isnum(bse.get(d)) else None for d in dates}   # S = R + P
    share, rate, table = _fo_tables(M, dates, key)
    out = {}
    for d in dates:
        q = q_of(d)
        if q not in share:
            row = dict(rev_mn=None, gross_mn=None, err=NA)                   # VLOOKUP miss (Q3, Q4 FY24)
        elif key[d] is None:
            row = dict(rev_mn=None, gross_mn=None, err=VALUE)                # P169 is text
        else:
            gross = share[q] * (key[d] / 1e7) * rate[q]                      # AF (Rs Mn)
            row = dict(rev_mn=net_gross(M, 'fo', q) * gross, gross_mn=gross, err=None)   # AG
        if live_c and row['err']:
            continue                                                         # m-c: an error row is not a day
        if M.switches:
            row['regime'] = _regime(M, 'fo', q)
        out[d] = row
    return out, dict(share=share, rate=rate, table=table)


# ── Cash: backtesting cash!I:K, Y:AB, assumptions!B45:N54 ──
def cash_daily(M):
    live_c = M.on('c')
    if M.on('b'):
        nl, bl = M.lake('nse_cash', 'turnover_cr'), M.lake('bse_cash', 'turnover_cr')
        dates, K = [], {}
        for d in sorted(nl):
            if live_c:
                if not (_usable(nl[d]) and _usable(bl.get(d))):
                    continue                                                 # m-c: no row for a missing / zero day
            elif bl.get(d) is None:
                raise KeyError(f'MOSL cash key: no BSE cash turnover on {d} (switch m-c would leave the day out)')
            K[d] = nl[d][0] + bl[d][0]
            dates.append(d)
    else:
        ni, bi = M.series('nse_cash', 'turnover_cr_xl'), M.series('bse_cash', 'turnover_cr_xl')
        dates = sorted(ni)
        K = {d: ni[d] + bi[d] for d in dates}                                # K = I + J
    qs = M.qs
    days, tot = Counter(q_of(d) for d in dates), defaultdict(float)
    for d in dates:
        tot[q_of(d)] += K[d]
    first, last = M.pin('cash_table_first_quarter'), M.pin('cash_last_actual_quarter')
    T = {}
    for q in qs[qs.index(first):qs.index(last) + 1]:
        D = days[q]
        C = tot[q] / D                                                       # average NSE + BSE ADTO
        E = M.fact('share_cash', q)
        G = M.fact('adto_cash_mosl', q)
        H = (E * C) / G                                                      # 'delivery ratio' F / G
        T[q] = dict(days=D, share=E, H=H, G=G, key=tot[q],                   # key: the quarter's NSE + BSE turnover, Rs Cr
                    J=M.fact('gross_cash_cr', q) / G if (q != last or M.on('a')) else None)
    if not M.on('a'):
        T[last]['J'] = T[qs[qs.index(last) - 1]]['J']                        # J52 = J51: typed I52 = 228 not used
    for q in qs[qs.index(first):qs.index(last) + 1]:
        T[q]['gross'] = T[q]['J'] * T[q]['G']                                # the quarter's gross, Rs Cr
    i = qs.index(last)
    if M.on('e'):
        unit = T[last]['gross'] / tot[last]                                  # gross per Rs Cr of turnover, last reported
    else:
        nxt = qs[i + 1]                                                      # the estimate quarter
        prev3 = [T[q]['H'] for q in qs[i - 2:i + 1]]
        T[nxt] = dict(days=days[nxt], share=T[last]['share'], H=_mean(*prev3), J=T[last]['J'])
        if i + 2 < len(qs):
            nxt2 = qs[i + 2]                                                 # Q3 FY27 (13 days so far)
            T[nxt2] = dict(days=days[nxt2], share=T[nxt]['share'],
                           H=_mean(*[T[q]['H'] for q in qs[i - 1:i + 2]]), J=T[nxt]['J'])
    ratio_last = M.pin('cash_net_ratio_last_quarter')
    out = {}
    for d in dates:
        q = q_of(d)
        if q not in T and not (M.on('e') and _qkey(q) > _qkey(last)):
            continue                                                         # AB is blank before the first quarter
        if M.on('e') and _qkey(q) > _qkey(last):                             # m-e: carry the last quarter's rate per Rs Cr
            gross = K[d] * unit
            r = net_gross(M, 'cash', q)
            row = dict(rev_cr=r * gross, gross_cr=gross, err=None)
        else:
            t = T[q]
            gross = t['share'] * (K[d] / t['H']) * (t['J'] / t['days'])      # AA (Rs Cr)
            r = net_gross(M, 'cash', q) if (M.on('e') or _qkey(q) <= _qkey(ratio_last)) else None
            row = (dict(rev_cr=r * gross, gross_cr=gross, err=None) if r is not None
                   else dict(rev_cr=None, gross_cr=gross, err=NA))           # AB: HLOOKUP range ends at Q2 FY27
        if live_c and row['err']:
            continue
        if M.switches:
            row['regime'] = _regime(M, 'cash', q)
        out[d] = row
    return out, dict(table=T)


# ── Commodities: Commodities!F, L, M, O, assumptions!B59:L74 ──
def comm_daily(M):
    live_c, live_e = M.on('c'), M.on('e')
    f = M.series('mcx', 'contracts')
    dates = sorted(f)
    qs = M.qs
    last_q, table_last = M.pin('comm_last_actual_quarter'), M.pin('comm_table_last_quarter')
    quarters = qs[:qs.index(table_last) + 1]
    if live_e:                                                               # no table range: to the last data day's quarter
        quarters = qs[:qs.index(max((q_of(d) for d in dates), key=_qkey)) + 1]
    tot = defaultdict(float)
    for d in dates:
        if _isnum(f[d]) and not (live_c and f[d] <= 0):
            tot[q_of(d)] += f[d]
    share = {q: M.fact('share_comm', q) for q in quarters if M.has_fact('share_comm', q)}
    nxt = qs[qs.index(last_q) + 1]
    if live_e:
        for q in quarters[quarters.index(last_q) + 1:]:
            share[q] = share[last_q]                                         # carried with the take rate: revenue per contract
    elif nxt in quarters:
        share[nxt] = _mean(*[share[q] for q in qs[qs.index(last_q) - 3:qs.index(last_q) + 1]])   # L62
    take, contracts = {}, {}
    for q in quarters:
        contracts[q] = tot[q] / 1e6                                          # Mn
        if q == nxt or (live_e and _qkey(q) > _qkey(last_q)):
            take[q] = take[last_q]                                           # L74 = K74
            continue
        take[q] = M.fact('gross_comm_cr', q) * 10 / (share[q] * contracts[q])    # row 74 = row 61 / row 66
    blank_from = M.pin('comm_o_blank_from_date')
    ratio_last = qs.index(table_last)
    out = {}
    for d in dates:
        q = q_of(d)
        if live_c and not (_isnum(f[d]) and f[d] > 0):
            continue                                                         # m-c: no row for a missing / zero day
        if q not in share:
            if d >= blank_from and not live_e:
                continue                                                     # formula not extended: blank
            if live_c:
                continue
            out[d] = dict(rev_mn=None, gross_mn=None, err=NA)                # no column in B59:L74
            continue
        gross = (f[d] / 1e6) * share[q] * take[q]                            # L (Rs Mn)
        r = net_gross(M, 'comm', q) if (live_e or qs.index(q) <= ratio_last) else None
        row = dict(rev_mn=r * gross, gross_mn=gross, err=None)               # O
        if M.switches:
            row['regime'] = _regime(M, 'comm', q)
        out[d] = row
    return out, dict(share=share, take=take, contracts_mn=contracts)


# ── MTF: MTF data (2)!I, V:X, assumptions!B5:F18 ──
def mtf_daily(M):
    live_c, live_e = M.on('c'), M.on('e')
    book = M.series('mtf_industry', 'book_cr')
    dates = sorted(book)
    qs = M.qs
    last_act = M.pin('mtf_last_actual_quarter')
    quarters = qs[qs.index('Q3 FY 2025'):qs.index(last_act) + 1]
    last = {}                                                                # D8:D14: book on the quarter's last date
    for d in dates:
        if _isnum(book[d]):
            last[q_of(d)] = book[d]
    share = {q: M.fact('mtf_book_closing', q) / last[q] for q in quarters}   # E = C / D
    nii = {}
    for q in quarters:
        if M.has_fact('mtf_nii_yield', q):
            nii[q] = M.fact('mtf_nii_yield', q)                              # typed, per quarter
        elif M.on('f'):
            nii[q] = M.assume(MS.YIELD_ASSUMPTION)                           # labelled carry (m-f)
        else:
            nii[q] = nii[quarters[quarters.index(q) - 1]]                    # F15 = F14
    carry_nii = M.assume(MS.YIELD_ASSUMPTION) if M.on('f') else nii[quarters[-1]]
    i = qs.index(quarters[-1])
    for q in (qs[i + 1:] if live_e else qs[i + 1:i + 2]):
        share[q], nii[q] = share[quarters[-1]], carry_nii                    # E15 = E14, F15 = F14
    basis = M.assume('mtf_day_basis')
    stop = None if live_e else M.pin('mtf_last_formula_date')
    out = {}
    for d in dates:
        q = q_of(d)
        if (stop is not None and d > stop) or q not in share:
            continue                                                         # V:X have no formula: blank
        if live_c and not (_isnum(book[d]) and book[d] > 0):
            continue
        w = share[q] * book[d]                                               # W: MOSL daily book (Rs Cr)
        row = dict(nii_cr=w * nii[q] / basis, book_cr=w, err=None)           # X
        if M.switches:
            row['regime'] = 'actual' if _qkey(q) <= _qkey(last_act) else 'projected'
        out[d] = row
    return out, dict(share=share, nii=nii, industry_close=last)


def run(M):
    """{'daily': {fo, cash, comm, mtf}, 'calib': {...}} in parity mode (or with the live switches M carries)."""
    fo, fo_c = fo_daily(M)
    cash, cash_c = cash_daily(M)
    comm, comm_c = comm_daily(M)
    mtf, mtf_c = mtf_daily(M)
    ratio = {q: {s: net_gross(M, s, q) for s in ('cash', 'fo', 'comm')} for q in M.qs}
    calib = dict(fo=fo_c, cash=cash_c, comm=comm_c, mtf=mtf_c, ratio=ratio)
    if M.switches:                                                           # which quarters are reported, per segment
        calib['last_actual'] = dict({s: M.pin(f'{s}_last_actual_quarter') for s in ('fo', 'cash', 'comm')},
                                    mtf=M.pin('mtf_last_actual_quarter'))
    return dict(daily=dict(fo=fo, cash=cash, comm=comm, mtf=mtf), calib=calib)
