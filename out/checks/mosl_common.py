#!/usr/bin/env python3
"""Shared independent model for the MOSL switch checks m-a ... m-f (recompute-checker).

Python standard library only (json, math, os, re, subprocess).  Nothing under src/engine or src/live is
imported or read.  Every input is read from the committed tree at commit 990eb5d (branch mosl-parity)
with `git show 990eb5d:<path>`, so a concurrent edit of the working tree does not matter.

The model is rebuilt from the Methodology (docs/MOSL_ADR_Methodology.md sections 3, 4, 6, 8b), the live spec
(docs/MOSL_LIVE_SPEC.md) and the raw inputs: reviewed data-book facts, workbook keys (snapshot), lake keys,
MCX contracts, industry MTF book, calendar.
"""
import json
import math
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
COMMIT = '990eb5d'
START = '2024-04-01'   # first day of Q1 FY25, first quarter with a data-book fact
LAST = '2026-10-21'    # last calendar day in the snapshot (series read to 2026-10-21)
ERR = 'ERR'            # an Excel error value (#N/A, #VALUE!): the row exists but holds an error

QS = ['Q1 FY 2025', 'Q2 FY 2025', 'Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026',
      'Q4 FY 2026', 'Q1 FY 2027', 'Q2 FY 2027', 'Q3 FY 2027']
REPORTED = QS[:10]
OPEN = 'Q3 FY 2027'
SEGS = ['fo', 'cash', 'comm', 'mtf']
PANELS = ['Consolidated', 'Broking', 'MTF', 'F&O', 'Cash', 'Commodities']
PERIODS = [('fy', 'FY 2027'), ('q', 'Q2 FY 2027'), ('q', 'Q1 FY 2027'), ('m', 'FY 2027 October'), ('fy', 'FY 2026')]
PLABEL = {'FY 2027': 'FY 2027', 'Q2 FY 2027': 'Q2 FY 2027', 'Q1 FY 2027': 'Q1 FY 2027',
          'FY 2027 October': 'FY 2027 October', 'FY 2026': 'FY 2026'}


def git_show(path):
    out = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (COMMIT, path)], check=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    return out.decode('utf-8')


_cache = {}


def jload(path):
    if path not in _cache:
        _cache[path] = json.loads(git_show(path))
    return _cache[path]


# ------------------------------------------------------------------ inputs
class Inputs(object):
    pass


def load_inputs():
    if 'inputs' in _cache:
        return _cache['inputs']
    I = Inputs()
    db = jload('snapshot/db_snapshot_2026-10-23.json')
    sn = jload('snapshot/mosl_snapshot_2026-10-23.json')
    fx = jload('snapshot/mosl_fixtures_2026-10-23.json')
    fr = jload('snapshot/mosl_facts_reviewed_2026-11-02.json')
    lk = jload('snapshot/mosl_lake_2026-11-02.json')
    I.db, I.sn, I.fx, I.fr, I.lk = db, sn, fx, fr, lk
    I.cal = {c['trade_date']: c for c in db['calendar'] if c['trade_date'] <= LAST}
    I.special = sorted(d for d, c in I.cal.items() if c['special_session'])
    # reviewed data-book facts, raw units (Rs Mn, Rs Mn/day, fractions)
    I.facts = {}
    I.fact_ids = {}
    for f in fr['facts']:
        assert f['status'] == 'reviewed' and f['broker_id'] == 'MOSL'
        I.facts[(f['metric'], f['period_key'])] = f['value']
        I.fact_ids[(f['metric'], f['period_key'])] = f['fact_id']
    # workbook keys (cached values of backtesting F&O / backtesting cash)
    md = {}
    for r in sn['market_daily']:
        md.setdefault(r['dataset'] + '/' + r['metric'], {})[r['trade_date']] = r['value']
    I.wb_nse_io = md['nse_fo/index_opt_contracts']
    I.wb_bse = md['bse_fo/opt_contracts_live']
    I.wb_nse_cash = md['nse_cash/turnover_cr_xl']
    I.wb_bse_cash = md['bse_cash/turnover_cr_xl']
    I.wb_S = {}
    for d in I.wb_nse_io:
        n = I.wb_nse_io[d]
        I.wb_S[d] = None if n is None else n + I.wb_bse[d]
    I.wb_K = {d: I.wb_nse_cash[d] + I.wb_bse_cash[d] for d in I.wb_nse_cash}
    # lake keys, on their own dates
    ser = lk['series']
    L = {}
    for k, rows in ser.items():
        L[k] = {}
        for d, v, st in rows:
            assert st == 'ok'
            L[k][d] = v
    I.lk_S = {d: L['nse_fo/io_contracts'][d] + L['bse_fo/contracts'][d] for d in L['nse_fo/io_contracts']
              if d in L['bse_fo/contracts']}
    I.lk_K = {d: L['nse_cash/turnover_cr'][d] + L['bse_cash/turnover_cr'][d] for d in L['nse_cash/turnover_cr']
              if d in L['bse_cash/turnover_cr']}
    I.lk_raw = L
    # MCX contracts and industry MTF book (db snapshot)
    I.mcx = {r['trade_date']: r['value'] for r in db['market_daily'] if r['dataset'] == 'mcx'}
    I.ind = {r['trade_date']: r['value'] for r in db['market_daily'] if r['dataset'] == 'mtf_industry'}
    # workbook typed MTF inputs and assumptions
    I.wb_fact = {}
    for f in sn['facts']:
        I.wb_fact[(f['metric'], f['period_key'])] = f['value']
    I.assump = {a['key']: a for a in sn['assumptions']}
    I.pins = {p['key']: p for p in sn['pins']}
    I.day_basis = I.assump['mtf_day_basis']['value']
    I.carry = I.assump['mtf_nii_yield_carry']['value']
    _cache['inputs'] = I
    return I


def q_of(d):
    return load_inputs().cal[d]['q_fy']


def days_of(q, dates):
    c = load_inputs().cal
    return [d for d in dates if c[d]['q_fy'] == q]


# ---- facts in the units of the workbook (Rs Cr)
def gross(seg, q):
    I = load_inputs()
    return I.facts[('gross_brokerage_' + {'fo': 'fo', 'cash': 'cash', 'comm': 'comm'}[seg], q)] / 10.0


def net(seg, q):
    I = load_inputs()
    return I.facts[('net_brokerage_' + {'fo': 'fo', 'cash': 'cash', 'comm': 'comm'}[seg], q)] / 10.0


def ratio(seg, q):
    return net(seg, q) / gross(seg, q)


def share(seg, q):
    I = load_inputs()
    return I.facts[('share_' + {'fo': 'fo_premium', 'cash': 'cash', 'comm': 'comm'}[seg], q)]


def adto_cash(q):
    return load_inputs().facts[('adto_cash', q)] / 10.0   # Rs Mn/day -> Rs Cr/day


def mtf_book(q):
    return load_inputs().facts[('mtf_book', q)] / 10.0    # Rs Mn -> Rs Cr


# ------------------------------------------------------------------ state model
class Model(object):
    def __init__(self, name):
        self.name = name
        self.rows = {s: {} for s in SEGS}   # date -> net revenue Rs Cr (float) | ERR | None (blank)
        self.par = {}                         # (segment label, quantity, quarter) -> value (None = no value)
        self.share_mtf = {}
        self.nii = {}
        self.extra = {}


def sset(m, seg, q, quantity, val):
    m.par[(seg, quantity, q)] = val


def ind_close(q):
    """Industry book on the last day of quarter q that has a book."""
    I = load_inputs()
    ds = [d for d in I.ind if I.cal.get(d, {}).get('q_fy') == q]
    return I.ind[max(ds)], max(ds)


def mtf_share(q):
    return mtf_book(q) / ind_close(q)[0]


def build_live(flags):
    """The live model after the switches in `flags` (a subset of 'abcdef', applied cumulatively)."""
    I = load_inputs()
    f = set(flags)
    m = Model(''.join(sorted(f)))
    S = I.lk_S if 'b' in f else I.wb_S
    K = I.lk_K if 'b' in f else I.wb_K
    fo_dates = sorted(d for d in S if d <= LAST and d in I.cal)
    cash_dates = sorted(d for d in K if START <= d <= LAST and d in I.cal)
    comm_dates = sorted(d for d in I.mcx if START <= d <= LAST)
    # ---------------- F&O
    sums = {}
    for d in fo_dates:
        if d < START:
            m.rows['fo'][d] = ERR            # no table row before Q1 FY25: #N/A
    L_fo = {}
    for q in REPORTED:
        days = days_of(q, [d for d in fo_dates if d >= START])
        good = [d for d in days if S.get(d) is not None]
        F = sum(S[d] for d in good) / 1e7
        sh = share('fo', q)
        G = gross('fo', q)
        rt = ratio('fo', q)
        L = G / (sh * F) * 10.0                # workbook L: Rs Mn per Cr contracts
        L_fo[q] = (sh, L, rt)
        sg = 0.0
        sn_ = 0.0
        for d in days:
            if d in good:
                af = sh * S[d] / 1e7 * L        # Rs Mn gross
                m.rows['fo'][d] = rt * af / 10.0
                sg += af / 10.0
                sn_ += rt * af / 10.0
            else:
                m.rows['fo'][d] = ERR
        sums[('fo', q)] = sum(S[d] for d in good)
        sset(m, 'F&O', q, 'premium share (cancels)', sh)
        sset(m, 'F&O', q, 'gross Rs per contract', L / 10.0)
        sset(m, 'F&O', q, 'model gross brokerage Rs Cr', sg)
        sset(m, 'F&O', q, 'model net brokerage Rs Cr', sn_)
    # open quarter: carry
    sh, L, rt = L_fo['Q2 FY 2027']
    days = days_of(OPEN, fo_dates)
    sg = sn_ = 0.0
    for d in days:
        af = sh * S[d] / 1e7 * L
        v = rt * af / 10.0
        if 'e' in f:
            # m-e: net revenue per index-option + BSE contract of the last reported quarter x the day's key
            v2 = net('fo', 'Q2 FY 2027') / sums[('fo', 'Q2 FY 2027')] * S[d]
            assert abs(v2 - v) <= 1e-12 * abs(v), (d, v, v2)
        m.rows['fo'][d] = v
        sg += af / 10.0
        sn_ += v
    sset(m, 'F&O', OPEN, 'premium share (cancels)', sh)
    sset(m, 'F&O', OPEN, 'gross Rs per contract', L / 10.0)
    sset(m, 'F&O', OPEN, 'net / gross', rt)
    sset(m, 'F&O', OPEN, 'model gross brokerage Rs Cr', sg)
    sset(m, 'F&O', OPEN, 'model net brokerage Rs Cr', sn_)
    for q in REPORTED:
        sset(m, 'F&O', q, 'net / gross', ratio('fo', q))
    # ---------------- cash
    Hq, Jq = {}, {}
    sums_k = {}
    for q in REPORTED:
        days = days_of(q, cash_dates)
        D = len(days)
        C = sum(K[d] for d in days) / D
        sh = share('cash', q)
        G = adto_cash(q)
        H = sh * C / G
        J = gross('cash', q) / G
        rt = ratio('cash', q)
        Hq[q], Jq[q] = H, J
        sums_k[q] = sum(K[d] for d in days)
        sg = sn_ = 0.0
        for d in days:
            aa = sh * K[d] / H * J / D
            m.rows['cash'][d] = rt * aa
            sg += aa
            sn_ += rt * aa
        sset(m, 'Cash', q, "'delivery ratio' H", H)
        sset(m, 'Cash', q, 'gross per Rs of reported ADTO J', J)
        sset(m, 'Cash', q, 'model gross brokerage Rs Cr', sg)
        sset(m, 'Cash', q, 'model net brokerage Rs Cr', sn_)
        sset(m, 'Cash', q, 'net / gross', rt)
        sset(m, 'Cash', q, 'share (cancels)', sh)
    days = days_of(OPEN, cash_dates)
    if 'e' not in f:
        H3 = (Hq['Q4 FY 2026'] + Hq['Q1 FY 2027'] + Hq['Q2 FY 2027']) / 3.0
        J3 = Jq['Q2 FY 2027']
        sh3 = share('cash', 'Q2 FY 2027')
        D = len(days)                      # days so far (the workbook's D54)
        sg = 0.0
        for d in days:
            m.rows['cash'][d] = ERR        # AB #N/A: the net-ratio HLOOKUP range ends at Q2 FY27
            sg += sh3 * K[d] / H3 * J3 / D
        sset(m, 'Cash', OPEN, "'delivery ratio' H", H3)
        sset(m, 'Cash', OPEN, 'gross per Rs of reported ADTO J', J3)
        sset(m, 'Cash', OPEN, 'share (cancels)', sh3)
        sset(m, 'Cash', OPEN, 'model gross brokerage Rs Cr', None if 'c' in f else sg)
        sset(m, 'Cash', OPEN, 'model net brokerage Rs Cr', None if 'c' in f else 0.0)
    else:
        npk = net('cash', 'Q2 FY 2027') / sums_k['Q2 FY 2027']      # net Rs Cr per Rs Cr of NSE+BSE turnover
        rt = ratio('cash', 'Q2 FY 2027')
        sn_ = 0.0
        for d in days:
            m.rows['cash'][d] = npk * K[d]
            sn_ += npk * K[d]
        sset(m, 'Cash', OPEN, 'net / gross', rt)
        sset(m, 'Cash', OPEN, 'model gross brokerage Rs Cr', sn_ / rt)
        sset(m, 'Cash', OPEN, 'model net brokerage Rs Cr', sn_)
    # ---------------- commodities
    take_q, sh_q, contr = {}, {}, {}
    sums_f = {}
    for q in REPORTED:
        days = days_of(q, comm_dates)
        cm = sum(I.mcx[d] for d in days) / 1e6
        sh = share('comm', q)
        tk = gross('comm', q) * 10.0 / (sh * cm)
        rt = ratio('comm', q)
        take_q[q], sh_q[q] = tk, sh
        sums_f[q] = sum(I.mcx[d] for d in days)
        sg = sn_ = 0.0
        for d in days:
            lm = I.mcx[d] / 1e6 * sh * tk      # Rs Mn gross
            m.rows['comm'][d] = rt * lm / 10.0
            sg += lm / 10.0
            sn_ += rt * lm / 10.0
        sset(m, 'Commodities', q, 'gross Rs per MOSL contract', tk)
        sset(m, 'Commodities', q, 'model gross brokerage Rs Cr', sg)
        sset(m, 'Commodities', q, 'model net brokerage Rs Cr', sn_)
        sset(m, 'Commodities', q, 'net / gross', rt)
        sset(m, 'Commodities', q, 'share', sh)
    days = days_of(OPEN, comm_dates)
    if 'e' not in f:
        blank_from = I.pins['comm_o_blank_from_date']['value_text']
        for d in days:
            m.rows['comm'][d] = ERR if d < blank_from else None
    else:
        npk = net('comm', 'Q2 FY 2027') / sums_f['Q2 FY 2027']
        rt = ratio('comm', 'Q2 FY 2027')
        sn_ = 0.0
        for d in days:
            v = npk * I.mcx[d]
            m.rows['comm'][d] = v
            sn_ += v
        sset(m, 'Commodities', OPEN, 'gross Rs per MOSL contract', take_q['Q2 FY 2027'])
        sset(m, 'Commodities', OPEN, 'share', sh_q['Q2 FY 2027'])
        sset(m, 'Commodities', OPEN, 'net / gross', rt)
        sset(m, 'Commodities', OPEN, 'model gross brokerage Rs Cr', sn_ / rt)
        sset(m, 'Commodities', OPEN, 'model net brokerage Rs Cr', sn_)
    # ---------------- MTF
    typed = {q: I.wb_fact[('mtf_nii_yield', q)] for q in QS if ('mtf_nii_yield', q) in I.wb_fact}
    nii = dict(typed)
    nii['Q2 FY 2027'] = I.carry if 'f' in f else typed['Q1 FY 2027']      # F15 = F14 in the workbook
    nii[OPEN] = I.carry if 'f' in f else typed['Q1 FY 2027']
    shr = {q: mtf_share(q) for q in REPORTED[2:]}    # Q1, Q2 FY25: no daily industry book (series starts 2024-10-01)
    shr[OPEN] = shr['Q2 FY 2027']
    m.share_mtf, m.nii = shr, nii
    last = LAST if 'e' in f else '2026-09-30'
    for d in sorted(I.ind):
        c = I.cal[d]
        q = c['q_fy']
        if d < '2024-10-01' or d > last or q not in shr or q in ('Q1 FY 2025', 'Q2 FY 2025'):
            continue
        m.rows['mtf'][d] = shr[q] * I.ind[d] * nii[q] / I.day_basis
    for q in QS[2:]:
        sset(m, 'MTF', q, 'share of industry book', shr[q])
        sset(m, 'MTF', q, 'NII yield', nii[q])
    return m


# ---------------------------------------------------------------- parity (workbook as saved)
def build_parity():
    """The workbook's four daily series rebuilt from raw keys and the workbook's typed calibration."""
    I = load_inputs()
    fx = I.fx
    cb = fx['calib']
    m = Model('parity')
    S, K = I.wb_S, I.wb_K
    gro = {}
    # F&O: AF = share * S/1e7 * rate (Rs Mn); AG = net/gross * AF.  Rows: #N/A before Q1 FY25, 0 for Q1-Q2 FY25
    for d in sorted(S):
        q = I.cal[d]['q_fy']
        if d < START:
            m.rows['fo'][d] = ERR
            continue
        c = cb['fo'][q]
        r = cb['ratio'][q]['fo']
        if S[d] is None:
            m.rows['fo'][d] = ERR
            continue
        rate = c['rate'] or 0.0
        af = c['share'] * S[d] / 1e7 * rate
        gro[('fo', d)] = af / 10.0
        m.rows['fo'][d] = r * af / 10.0
    # cash: AA = share * K / H * J / D ; AB = ratio * AA from 2024-10-01 ; blank before
    for d in sorted(K):
        if d < '2024-10-01' or d > LAST or d not in I.cal:
            continue
        q = I.cal[d]['q_fy']
        c = cb['cash'][q]
        aa = c['share'] * K[d] / c['H'] * c['J'] / c['days']
        gro[('cash', d)] = aa
        m.rows['cash'][d] = ERR if q == OPEN else cb['ratio'][q]['cash'] * aa
    # commodities
    blank_from = I.pins['comm_o_blank_from_date']['value_text']
    for d in sorted(I.mcx):
        if d < START or d > LAST:
            continue
        q = I.cal[d]['q_fy']
        if q == OPEN:
            m.rows['comm'][d] = ERR if d < blank_from else None
            continue
        c = cb['comm'][q]
        lm = I.mcx[d] / 1e6 * c['share'] * c['take']
        gro[('comm', d)] = lm / 10.0
        m.rows['comm'][d] = cb['ratio'][q]['comm'] * lm / 10.0
    # MTF
    for d in sorted(I.ind):
        if d < '2024-10-01' or d > '2026-09-30':
            continue
        q = I.cal[d]['q_fy']
        c = cb['mtf'][q]
        m.rows['mtf'][d] = c['share'] * I.ind[d] * c['nii'] / I.day_basis
    m.extra['gross'] = gro
    # ---- parity parameters (the workbook's typed calibration, quarter by quarter)
    for q in QS:
        days_fo = [d for d in S if I.cal.get(d, {}).get('q_fy') == q and d >= START and S[d] is not None]
        c = cb['fo'][q]
        if q != 'Q3 FY 2027' or True:
            sset(m, 'F&O', q, 'premium share (cancels)', c['share'])
            sset(m, 'F&O', q, 'gross Rs per contract', (c['rate'] or 0.0) / 10.0)
            sset(m, 'F&O', q, 'net / gross', cb['ratio'][q]['fo'])
            g = sum(gro[('fo', d)] for d in days_fo)
            sset(m, 'F&O', q, 'model gross brokerage Rs Cr', g)
            sset(m, 'F&O', q, 'model net brokerage Rs Cr', g * cb['ratio'][q]['fo'])
    for q in QS[2:]:
        c = cb['cash'][q]
        dc = [d for d in I.wb_K if I.cal.get(d, {}).get('q_fy') == q and '2024-10-01' <= d <= LAST]
        g = sum(gro[('cash', d)] for d in dc)
        sset(m, 'Cash', q, "'delivery ratio' H", c['H'])
        sset(m, 'Cash', q, 'gross per Rs of reported ADTO J', c['J'])
        sset(m, 'Cash', q, 'model gross brokerage Rs Cr', g)
        sset(m, 'Cash', q, 'model net brokerage Rs Cr', 0.0 if q == OPEN else g * cb['ratio'][q]['cash'])
        sset(m, 'Cash', q, 'share (cancels)', c['share'])
    for q in REPORTED:
        sset(m, 'Cash', q, 'net / gross', cb['ratio'][q]['cash'])   # row 112; Q3 FY27 has none (#N/A)
        c = cb['comm'][q]
        dc = [d for d in I.mcx if I.cal.get(d, {}).get('q_fy') == q and START <= d <= LAST]
        g = sum(gro[('comm', d)] for d in dc)
        sset(m, 'Commodities', q, 'gross Rs per MOSL contract', c['take'])
        sset(m, 'Commodities', q, 'model gross brokerage Rs Cr', g)
        sset(m, 'Commodities', q, 'model net brokerage Rs Cr', g * cb['ratio'][q]['comm'])
        sset(m, 'Commodities', q, 'net / gross', cb['ratio'][q]['comm'])
        sset(m, 'Commodities', q, 'share', c['share'])
    for q in QS[2:10]:
        c = cb['mtf'][q]
        sset(m, 'MTF', q, 'share of industry book', c['share'])
        sset(m, 'MTF', q, 'NII yield', c['nii'])
    return m


def parity_cached_rows():
    """The workbook's cached daily columns (AG/10, AB, O/10, X) as rows: Rs Cr, ERR for '#...', as saved."""
    fx = load_inputs().fx['daily']
    out = {s: {} for s in SEGS}
    spec = {'fo': ('backtesting F&O!AG', 0.1), 'cash': ('backtesting cash!AB', 1.0),
            'comm': ('Commodities!O', 0.1), 'mtf': ('MTF data (2)!X', 1.0)}
    for s, (k, sc) in spec.items():
        for d, v in fx[k].items():
            out[s][d] = ERR if isinstance(v, str) else v * sc
    return out


# ---------------------------------------------------------------- statistics
def period_dates(kind, label):
    c = load_inputs().cal
    key = {'fy': 'fy', 'q': 'q_fy', 'm': 'fy_month'}[kind]
    return [d for d in sorted(c) if c[d][key] == label]


def seg_adr(rows, seg, kind, label, flags=(), silent_zero=True, no_special=False, with_n=False):
    """ADR of one segment: simple average of the daily revenue over the period's rows.

    silent_zero (workbook, before m-c): a matched error row makes AVERAGEIFS an error, IFERROR -> 0; blank rows
    are skipped; no numeric row -> #DIV/0 -> 0.   After m-c: error and blank rows are left out.
    no_special (m-d): special sessions are left out of the F&O, cash and commodity averages (MTF keeps them).
    """
    I = load_inputs()
    dates = period_dates(kind, label)
    vals, err = [], False
    for d in dates:
        if d not in rows[seg]:
            continue
        v = rows[seg][d]
        if no_special and seg != 'mtf' and I.cal[d]['special_session']:
            continue
        if v is None:
            continue
        if v == ERR:
            err = True
            continue
        vals.append(v)
    if silent_zero and err:
        res = 0.0
    elif not vals:
        res = 0.0
    else:
        res = sum(vals) / len(vals)
    return (res, len(vals), err) if with_n else res


def panel_adr(rows, kind, label, **kw):
    r = {s: seg_adr(rows, s, kind, label, **kw) for s in SEGS}
    out = {'F&O': r['fo'], 'Cash': r['cash'], 'Commodities': r['comm'], 'MTF': r['mtf']}
    out['Broking'] = r['fo'] + r['cash'] + r['comm']
    out['Consolidated'] = out['Broking'] + r['mtf']
    return out


STATE_KW = {
    # flags -> kwargs of the statistics
}


def stat_kw(flags):
    f = set(flags)
    return {'silent_zero': 'c' not in f, 'no_special': 'd' in f}


# ---------------------------------------------------------------- bridge parsing and comparison
def num(s):
    """Parse a bridge cell: returns (value, decimals, is_pct) or (None, 0, False) for blank / dash."""
    s = s.strip().replace(',', '')
    if s in ('', '-', '—'):
        return None, 0, False
    pct = s.endswith('%')
    if pct:
        s = s[:-1]
    s = s.lstrip('+')
    if s.startswith('−'):
        s = '-' + s[1:]
    dp = len(s.split('.')[1]) if '.' in s else 0
    return float(s), dp, pct


def tables(text):
    """All markdown tables of a bridge: list of (header list, rows list of cell lists)."""
    out = []
    cur = None
    for line in text.split('\n'):
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if cur is None:
                cur = {'head': cells, 'rows': []}
            elif all(set(c) <= set('-: ') for c in cells):
                continue
            else:
                cur['rows'].append(cells)
        else:
            if cur is not None:
                out.append(cur)
                cur = None
    if cur is not None:
        out.append(cur)
    return out


def find_table(text, first_cols):
    for t in tables(text):
        if t['head'][:len(first_cols)] == first_cols:
            return t
    return None


class Items(object):
    """Collects compared items; each is agree / differ with the criterion that decided it."""

    def __init__(self):
        self.rows = []
        self.meta = {'adr_n': 0, 'adr_max_rel': 0.0, 'adr_max_abs': 0.0}

    def add(self, kind, label, mine, bridge_str, scale=1.0, note=''):
        """Compare my number (already in the bridge's unit; `scale` multiplies it, e.g. 100 for a % column) with
        the bridge's printed string."""
        bv, dp, pct = num(bridge_str) if isinstance(bridge_str, str) else (bridge_str, 6, False)
        if mine is None or bv is None:
            ok = (mine is None and bv is None)
            how = 'blank' if ok else 'differ'
            self.rows.append((kind, label, mine, bridge_str, ok, how, None, note))
            return ok
        x = mine * scale
        diff = abs(x - bv)
        rel = diff / abs(bv) if bv != 0 else (0.0 if diff == 0 else float('inf'))
        if rel <= 1e-6:
            ok, how = True, 'rel 1e-6'
        elif diff <= 0.5 * 10 ** (-dp) * (1 + 1e-9):
            ok, how = True, 'print (%d dp)' % dp
        else:
            ok, how = False, 'differ'
        self.rows.append((kind, label, x, bridge_str, ok, how, rel, note))
        return ok

    def add_bool(self, kind, label, ok, detail=''):
        self.rows.append((kind, label, detail, '', bool(ok), 'exact' if ok else 'differ', None, ''))
        return ok

    def count(self):
        n = len(self.rows)
        a = sum(1 for r in self.rows if r[4])
        rel = sum(1 for r in self.rows if r[4] and r[5] in ('rel 1e-6', 'exact', 'blank'))
        return n, a, rel

    def by_kind(self):
        d = {}
        for r in self.rows:
            k = d.setdefault(r[0], [0, 0, 0])
            k[0] += 1
            k[1] += 1 if r[4] else 0
            k[2] += 1 if (r[4] and r[5] in ('rel 1e-6', 'exact', 'blank')) else 0
        return d


def fmt(x, nd=6):
    if x is None:
        return '-'
    if isinstance(x, str):
        return x
    return ('%.' + str(nd) + 'f') % x


def write_md(path, title, intro, items, sections, extra_lines=(), explain=None):
    """Write the working file: header, result line, per-kind table, then the item sections."""
    n, a, rel = items.count()
    L = ['# ' + title, '']
    L.extend(intro)
    L.append('')
    L.append('**Result: %d/%d items agree** (%d to 1e-6 relative or exact; %d only to the bridge print precision).'
             % (a, n, rel, a - rel))
    if a != n:
        L.append('')
        L.append('**%d item(s) DIFFER** (listed below with cause).' % (n - a))
    L.append('')
    if items.meta['adr_n']:
        L.append('ADR before / after values in the bridge table (%d numbers, printed to 6 decimals): max absolute difference %.2e Cr, max relative difference %.2e (a 6-decimal print can only resolve 5e-7 Cr).'
                 % (items.meta['adr_n'], items.meta['adr_max_abs'], items.meta['adr_max_rel']))
        L.append('')
    L.append('| Item kind | Checked | Agree | Agree at 1e-6 / exact |')
    L.append('|---|---:|---:|---:|')
    for k, v in items.by_kind().items():
        L.append('| %s | %d | %d | %d |' % (k, v[0], v[1], v[2]))
    L.append('')
    L.extend(extra_lines)
    bad = [r for r in items.rows if not r[4]]
    if bad:
        L.append('## Differences and their cause')
        L.append('')
        for r in bad:
            L.append('- `%s` (%s; bridge value %s). %s' % (r[1], r[2], r[3] if r[3] != '' else '-', (explain or {}).get(r[1], 'UNEXPLAINED')))
        L.append('')
    for head, kinds, cols in sections:
        L.append('## ' + head)
        L.append('')
        L.append('| ' + ' | '.join(cols) + ' |')
        L.append('|' + '|'.join(['---'] * len(cols)) + '|')
        for r in items.rows:
            if r[0] in kinds:
                L.append('| %s | %s | %s | %s | %s | %s |' % (
                    r[1], fmt(r[2], 6) if not isinstance(r[2], str) else r[2], r[3],
                    'agree' if r[4] else '**DIFFER**', r[5], ('%.1e' % r[6]) if r[6] is not None else ''))
        L.append('')
    with open(path, 'w') as fh:
        fh.write('\n'.join(L) + '\n')
    return n, a


# ---------------------------------------------------------------- generic comparisons against a bridge
def kind_of(label):
    if re.match(r'^FY \d{4}$', label):
        return 'fy'
    if re.match(r'^Q\d FY \d{4}$', label):
        return 'q'
    return 'm'


def add_multi(items, kind, label, pairs, note=''):
    """One item made of several numbers; agrees only if every number agrees (worst criterion reported)."""
    worst = 'rel 1e-6'
    ok = True
    mine_s, br_s = [], []
    maxrel = 0.0
    for name, mine, bstr, scale in pairs:
        bv, dp, pct = num(bstr)
        if mine is None or bv is None:
            good = (mine is None and bv is None)
            how = 'blank'
            rel = 0.0
            x = None
        else:
            x = mine * scale
            diff = abs(x - bv)
            rel = diff / abs(bv) if bv != 0 else (0.0 if diff == 0 else float('inf'))
            if rel <= 1e-6:
                good, how = True, 'rel 1e-6'
            elif diff <= 0.5 * 10 ** (-dp) * (1 + 1e-9):
                good, how = True, 'print (%d dp)' % dp
            else:
                good, how = False, 'differ'
        if not good:
            ok = False
            worst = 'differ'
        elif how.startswith('print') and worst != 'differ':
            worst = how
        maxrel = max(maxrel, rel if rel != float('inf') else 1.0)
        mine_s.append('%s %s' % (name, '-' if x is None else ('%.6f' % x if abs(x) < 1e4 else '%.2f' % x)))
        br_s.append('%s %s' % (name, bstr))
    items.rows.append((kind, label, ' / '.join(mine_s), ' / '.join(br_s), ok, worst, maxrel, note))
    return ok


def check_adr(items, text, rows_b, kw_b, rows_a, kw_a, kind='ADR'):
    """Every row of the bridge's ADR table: before, after, delta, delta %."""
    t = find_table(text, ['Period', 'Panel', 'Before', 'After'])
    cache = {}
    for r in t['rows']:
        per, panel, b, a, dl, dp_ = r[:6]
        k = kind_of(per)
        if (per, 'b') not in cache:
            cache[(per, 'b')] = panel_adr(rows_b, k, per, **kw_b)
            cache[(per, 'a')] = panel_adr(rows_a, k, per, **kw_a)
        mb, ma = cache[(per, 'b')][panel], cache[(per, 'a')][panel]
        for mine_, str_ in ((mb, b), (ma, a)):
            bv_ = num(str_)[0]
            items.meta['adr_n'] += 1
            items.meta['adr_max_abs'] = max(items.meta['adr_max_abs'], abs(mine_ - bv_))
            if bv_ != 0:
                items.meta['adr_max_rel'] = max(items.meta['adr_max_rel'], abs(mine_ - bv_) / abs(bv_))
        pct = (ma / mb - 1.0) if mb != 0 else None
        add_multi(items, kind, '%s, %s' % (per, panel),
                  [('before', mb, b, 1), ('after', ma, a, 1), ('delta', ma - mb, dl, 1), ('d%', pct, dp_, 100)])
    h = find_table(text, ['Period', 'Before', 'After', 'Δ %'])
    if h is not None:
        for r in h['rows']:
            per, b, a, dp_ = r[:4]
            k = kind_of(per)
            mb = cache.get((per, 'b'), panel_adr(rows_b, k, per, **kw_b))['Consolidated']
            ma = cache.get((per, 'a'), panel_adr(rows_a, k, per, **kw_a))['Consolidated']
            add_multi(items, 'Consolidated headline', per,
                      [('before', mb, b, 1), ('after', ma, a, 1), ('d%', ma / mb - 1.0, dp_, 100)])


def check_params(items, text, par_b, par_a, kind='param', tol=1e-6):
    """Every row of 'Parameters that moved', and that the set of moved parameters is the same."""
    t = find_table(text, ['Segment', 'Quantity', 'Quarter'])
    listed = set()
    if t is not None:
        for r in t['rows']:
            seg, qty, q, b, a, dp_ = r[:6]
            key = (seg, qty, q)
            listed.add(key)
            mb, ma = par_b.get(key), par_a.get(key)
            pct = None
            if mb not in (None, 0) and ma is not None:
                pct = ma / mb - 1.0
            add_multi(items, kind, '%s, %s, %s' % key, [('before', mb, b, 1), ('after', ma, a, 1), ('d%', pct, dp_, 100)])
    # completeness: my moved set vs the bridge's listed set
    mine = set()
    for key in set(par_b) | set(par_a):
        vb, va = par_b.get(key), par_a.get(key)
        if (vb is None) != (va is None):
            mine.add(key)
        elif vb is not None and abs(va - vb) > tol * max(abs(vb), 1e-12):
            mine.add(key)
    only_mine = sorted(mine - listed)
    only_br = sorted(listed - mine)
    items.add_bool('param set', 'moved parameters: mine = bridge (%d listed)' % len(listed),
                   not only_mine and not only_br,
                   'only mine: %s; only bridge: %s' % (only_mine, only_br))
    return only_mine, only_br


def series_of(rows_seg, drop_err):
    return {d: v for d, v in rows_seg.items() if v is not None and not (drop_err and v == ERR)}


def rows_stats(b, a, tol=1e-9):
    """The bridge's 'Daily revenue rows that changed' statistics for one segment."""
    changed, ratios = [], []
    for d, vb in b.items():
        if d not in a:
            continue
        va = a[d]
        if vb == ERR or va == ERR:
            if vb != va:
                changed.append(d)
            continue
        if abs(va - vb) > tol * max(abs(vb), 1e-300):
            changed.append(d)
            if vb != 0:
                ratios.append(va / vb)
    added = [d for d in a if d not in b]
    dropped = [d for d in b if d not in a]
    return {'before': len(b), 'after': len(a), 'changed': len(changed), 'first': min(changed) if changed else '',
            'last': max(changed) if changed else '', 'rmin': min(ratios) if ratios else None,
            'rmax': max(ratios) if ratios else None, 'added': len(added), 'dropped': len(dropped)}


def check_row_stats(items, text, rows_b, drop_b, rows_a, drop_a, kind='daily rows'):
    t = find_table(text, ['Segment', 'Days before'])
    names = {'F&O': 'fo', 'Cash': 'cash', 'Commodities': 'comm', 'MTF': 'mtf'}
    out = []
    for r in t['rows']:
        seg, db_, da_, ch, first, last, rmin, rmax, add, drp = r[:10]
        s = rows_stats(series_of(rows_b[names[seg]], drop_b), series_of(rows_a[names[seg]], drop_a))
        ok = (s['before'] == int(db_) and s['after'] == int(da_) and s['changed'] == int(ch) and
              s['added'] == int(add) and s['dropped'] == int(drp) and s['first'] == first and s['last'] == last)
        det = 'mine %d/%d changed %d added %d dropped %d first %s last %s' % (
            s['before'], s['after'], s['changed'], s['added'], s['dropped'], s['first'], s['last'])
        ok1 = items.add_bool(kind, '%s counts / dates' % seg, ok, det + '; bridge %s/%s changed %s added %s dropped %s first %s last %s' % (db_, da_, ch, add, drp, first, last))
        for nm, mv, bs in (('ratio min', s['rmin'], rmin), ('ratio max', s['rmax'], rmax)):
            items.add(kind, '%s %s' % (seg, nm), mv, bs)
        out.append((seg, s))
    return out


# ---------------------------------------------------------------- data book (xlsx read with zipfile + xml, stdlib)
DATABOOK = os.path.join(ROOT, 'data', 'raw', 'disclosures', 'mosl', 'MOSL_DataBook_q2fy27-data-book.xlsx')
DB_COLS = {'Q1 FY 2025': 'F', 'Q2 FY 2025': 'G', 'Q3 FY 2025': 'H', 'Q4 FY 2025': 'I', 'Q1 FY 2026': 'K', 'Q2 FY 2026': 'L',
           'Q3 FY 2026': 'M', 'Q4 FY 2026': 'N', 'Q1 FY 2027': 'P', 'Q2 FY 2027': 'Q'}


def databook_consol(path=DATABOOK):
    """Rows of the data book sheet 'Consol' as {row: {column letter: value}} (numbers as float, text as str).
    Returns None when the file is not there (data/raw is gitignored, it is not part of the commit)."""
    import zipfile
    import xml.etree.ElementTree as ET
    if not os.path.exists(path):
        return None
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    z = zipfile.ZipFile(path)
    ss = [''.join(t.text or '' for t in si.iter('{%s}t' % ns['m']))
          for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', ns)]
    wbx = z.read('xl/workbook.xml').decode()
    rid = re.search(r'<sheet name="Consol"[^>]*r:id="(rId\d+)"', wbx).group(1)
    rels = z.read('xl/_rels/workbook.xml.rels').decode()
    target = re.search(r'<Relationship [^>]*Id="%s"[^>]*Target="([^"]+)"' % rid, rels)
    if target is None:
        target = re.search(r'<Relationship [^>]*Target="([^"]+)"[^>]*Id="%s"' % rid, rels)
    sheet = ET.fromstring(z.read('xl/' + target.group(1).lstrip('/').replace('xl/', '')))
    rows = {}
    for row in sheet.find('m:sheetData', ns):
        r = int(row.get('r'))
        for cell in row:
            v = cell.find('m:v', ns)
            if v is None:
                continue
            col = re.match(r'[A-Z]+', cell.get('r')).group()
            rows.setdefault(r, {})[col] = ss[int(v.text)] if cell.get('t') == 's' else float(v.text)
    return rows
