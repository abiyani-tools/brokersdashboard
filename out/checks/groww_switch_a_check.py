#!/usr/bin/env python3
"""Groww switch g-a: independent recompute of the bridge out/bridges/groww_a.md.
Only json, math, csv from the stdlib (os/sys for paths). Run: python groww_switch_a_check.py"""
# ---- common model block (stdlib: json, math, csv only; os/sys for paths) ----
import json, math, csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))


def J(p):
    with open(os.path.join(ROOT, p)) as fh:
        return json.load(fh)


DB = J('snapshot/db_snapshot_2026-10-23.json')
FX = J('snapshot/groww_fixtures_2026-10-23.json')
GS = J('snapshot/groww_snapshot_2026-10-23.json')
FR = J('snapshot/groww_facts_reviewed_2026-10-31.json')['facts']
HB = J('snapshot/groww_orders_handbook_2026-10-31.json')['quarters']
FRID = {f['fact_id']: f for f in FR}

# ---------------- calendar ----------------
CAL = {c['trade_date']: c for c in DB['calendar']}
SPECIAL = sorted(d for d, c in CAL.items() if c['special_session'])
FYDAYS = {}
for d, c in CAL.items():
    if c['is_equity_day']:
        FYDAYS[c['fy']] = FYDAYS.get(c['fy'], 0) + 1
QMONTHS = {}
for d in sorted(CAL):
    c = CAL[d]
    QMONTHS.setdefault(c['q_fy'], [])
    if c['fy_month'] not in QMONTHS[c['q_fy']]:
        QMONTHS[c['q_fy']].append(c['fy_month'])

# ---------------- exchange series ----------------
MK = {}
for m in DB['market_daily']:
    MK.setdefault(m['dataset'], {})[m['trade_date']] = m['value']
LAKE = {m['trade_date']: m['value'] for m in DB['market_daily_lake'] if m['dataset'] == 'bse_fo'}
IMPUTED = sorted(m['trade_date'] for m in DB['market_daily'] if m['status'] == 'imputed')


def V(d, lake):
    b = MK['bse_fo'][d]
    if lake and d in LAKE:
        b = LAKE[d]
    return (MK['nse_fo'][d] + b) / 1e6


def N(d):
    return (MK['nse_cash'][d] + MK['bse_cash'][d]) / 1e6


def M(d):
    return MK['mcx'][d] / 1e6


BOOK = MK['mtf_industry']

# ---------------- Angel calibration read from the parity expected values ----------------
CAL_ANG = {}
for p in DB['parity_expected']:
    if p['kind'] == 'calib':
        k, _, s = p['key'].partition('|')
        CAL_ANG.setdefault(k, {})[s] = p['value']
CPO_FO = CAL_ANG['fo_cpo_m']            # monthly contracts per order (Angel)
CPO_COMM = CAL_ANG['comm_cpo_m']        # monthly commodity contracts per order (Angel)
TPO = CAL_ANG['cash_tpo_q']             # quarterly trades per order (Angel)
TR_COMM_ANG_M = CAL_ANG['comm_take_rate_m']
TR_COMM_ANG_Q = CAL_ANG['take_rate_comm_q']
IND_AVG_Q = CAL_ANG['mtf_industry_avg_q']

FO_DAYS = sorted(FX['daily']['backtesting F&O!AD'])
CASH_DAYS = sorted(FX['daily']['backtesting cash!V'])
COMM_DAYS = sorted(FX['daily']['Commodities!K'])
MTF_DAYS = sorted(FX['daily']['MTF data (2)!L'])

QS = ['Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026',
      'Q1 FY 2027', 'Q2 FY 2027', 'Q3 FY 2027']


def qdays(q, days):
    return [d for d in days if CAL[d]['q_fy'] == q]


def mean(x):
    x = list(x)
    return sum(x) / len(x)


# ---------------- facts ----------------
def fact(metric, q, seg=None):
    """value of a reviewed fact; seg=None means the restated/default (segment == '')."""
    for f in FR:
        if f['metric'] == metric and f['period_key'] == q and (f['segment'] or None) == seg:
            return f['value']
    return None


def fact_id(metric, q, seg=None):
    for f in FR:
        if f['metric'] == metric and f['period_key'] == q and (f['segment'] or None) == seg:
            return f['fact_id']
    return None


WB = {}
for f in GS['facts']:
    WB[(f['metric'], f['period_key'])] = f['value']
MIXSEG = {'fo': 'revmix_fo', 'cash': 'revmix_cash', 'comm': 'revmix_comm'}


def mix_live(seg, q):
    """live mix: restated where it exists, original (cls_pre_q2fy27) otherwise."""
    m = MIXSEG[seg]
    v = fact(m, q)
    if v is None:
        v = fact(m, q, 'cls_pre_q2fy27')
    return v


def share_live(seg, q):
    m = 'share_%s_adto_q' % seg
    for f in FR:
        if f['metric'] == m and f['period_key'] == q:
            if f['segment'] == 'denom_exch_x1':
                return f['value']
    for f in FR:
        if f['metric'] == m and f['period_key'] == q and f['segment'] == 'denom_exch_x2':
            return 2 * f['value']
    return None


def tinc_live(q):
    v = fact('total_income', q)
    if v is None:
        v = WB.get(('total_income', q))
    return v


def mtf_rev_live(q):
    """Rs Cr = MTF mix x consolidated total income (Rs Mn) / 10; restated mix where it exists."""
    m = fact('revmix_mtf', q)
    if m is None:
        m = fact('revmix_mtf', q, 'cls_pre_q2fy27')
    return m * tinc_live(q) / 10.0


# ---------------- the model, cumulative switches ----------------
def build(flags):
    """flags: set of letters among 'abcdefg'. Returns params and daily revenue series."""
    a, b, c, d_, e, f, g = [x in flags for x in 'abcdefg']
    P = {'fo': {}, 'cash': {}, 'comm': {}, 'mtf': {}, 'rev': {}}
    # --- inputs by quarter
    base = {}
    mix = {'fo': {}, 'cash': {}, 'comm': {}}
    share = {'fo': {}, 'cash': {}}
    qs_fo = ['Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026']
    qs_cash = ['Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027']
    qs_comm = ['Q3 FY 2026']
    if b:
        qs_fo = ['Q1 FY 2026'] + qs_fo
        qs_cash = ['Q1 FY 2026'] + qs_cash
    if d_:
        qs_fo = qs_fo + ['Q1 FY 2027', 'Q2 FY 2027']
        qs_cash = qs_cash + ['Q2 FY 2027']
        qs_comm = ['Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027', 'Q2 FY 2027']
    # revenue base and mixes
    def total_income(q):
        if q in ('Q2 FY 2026', 'Q3 FY 2026'):
            return WB[('total_income', q)]
        if q == 'Q1 FY 2026':
            return fact('total_income', q)
        if q == 'Q2 FY 2027':
            return fact('total_income', q)
        # Q4 FY26, Q1 FY27
        if a:
            return fact('total_income', q)
        return WB[('total_income_ex_fisdom_amc', q)]

    def mixv(seg, q):
        wb = WB.get((MIXSEG[seg], q))
        if q == 'Q1 FY 2026':
            return mix_live(seg, q)           # only used under b
        if q == 'Q2 FY 2027':
            return mix_live(seg, q)           # only used under d
        # Q2 FY26..Q1 FY27
        if a:
            return mix_live(seg, q)
        if d_ and (seg, q) in (('fo', 'Q1 FY 2027'), ('comm', 'Q4 FY 2026'), ('comm', 'Q1 FY 2027')):
            return mix_live(seg, q)
        return wb

    def shr(seg, q):
        wb = WB.get(('share_%s_adto_q' % seg, q))
        if q in ('Q1 FY 2026',) or q == 'Q2 FY 2027':
            return share_live(seg, q)
        if a:
            return share_live(seg, q)
        if d_ and q == 'Q1 FY 2027' and seg == 'fo':
            return share_live(seg, q)
        return wb

    # ---------------- F&O
    fo = {}
    for q in qs_fo:
        rev = mixv('fo', q) * total_income(q)              # Rs Mn
        cpo_q = mean(CPO_FO[m] for m in QMONTHS[q])
        vsum = sum(V(x, c) for x in qdays(q, FO_DAYS))
        s = shr('fo', q)
        orders = vsum / cpo_q * s
        fo[q] = {'rev': rev, 'share': s, 'cpo_q': cpo_q, 'tr': rev / orders, 'cal': True}
    lastq = qs_fo[-1]
    nxt = QS[QS.index(lastq) + 1:]
    sh_prev = fo[lastq]['share']
    first = True
    for q in nxt:
        if q in ('Q3 FY 2025', 'Q4 FY 2025'):
            continue
        if first:
            s = sh_prev * (1.0 if e else 1.05)
            first = False
        else:
            s = sh_prev
        fo[q] = {'share': s, 'tr': fo[lastq]['tr'], 'cal': False}
        sh_prev = s
    P['fo'] = fo
    # ---------------- Cash
    ca = {}
    for q in qs_cash:
        rev = mixv('cash', q) * total_income(q)
        nsum = sum(N(x) for x in qdays(q, CASH_DAYS))
        s = shr('cash', q)
        orders = nsum / TPO[q] * s
        ca[q] = {'rev': rev, 'share': s, 'tpo': TPO[q], 'tr': rev / orders, 'cal': True}
    lastq = qs_cash[-1]
    trs = [ca[q]['tr'] for q in qs_cash]
    for q in QS[QS.index(lastq) + 1:]:
        # estimate quarters: g-e carries the last actual take rate; before g-e, trailing mean of the last 3 actuals
        tr = ca[lastq]['tr'] if e else mean(trs[-3:])
        ca[q] = {'share': ca[lastq]['share'], 'tpo': TPO[q], 'tr': tr, 'cal': False}
    P['cash'] = ca
    # ---------------- Commodities
    cm = {}
    def sum_mkt(q):
        return sum(M(x) / CPO_COMM[CAL[x]['fy_month']] for x in qdays(q, COMM_DAYS))
    if not d_:
        tr_c = mean(TR_COMM_ANG_Q[q] for q in ('Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026'))
        q = 'Q3 FY 2026'
        mx = mixv('comm', q)
        rev = mx * total_income(q)
        s0 = rev / tr_c / sum_mkt(q)
        cm_share = s0 * 1.05
        for qq in ('Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027', 'Q2 FY 2027', 'Q3 FY 2027'):
            cm[qq] = {'share': cm_share, 'tr': tr_c, 'cal': qq == 'Q3 FY 2026', 'share0': s0}
        cm['Q3 FY 2026']['rev'] = rev
    else:
        for q in qs_comm:
            rev = mixv('comm', q) * total_income(q)
            tr = TR_COMM_ANG_Q.get(q) or TR_COMM_ANG_M[QMONTHS[q][0]]   # quarterly Angel take rate where reported; Angel's carried monthly value otherwise
            s = rev / tr / sum_mkt(q)
            cm[q] = {'rev': rev, 'share': s, 'tr': tr, 'cal': True}
        q = 'Q3 FY 2027'
        cm[q] = {'share': cm['Q2 FY 2027']['share'] * (1.0 if e else 1.05),
                 'tr': TR_COMM_ANG_M[QMONTHS[q][0]], 'cal': False}
    P['comm'] = cm
    # ---------------- MTF
    mt = {}
    mq = ['Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027']
    if f:
        mq = mq + ['Q2 FY 2027']
    yld = 0.1495
    def mrev(q):
        if a:
            return mtf_rev_live(q)
        return WB[('mtf_revenue', q)]
    def mtf_daysbasis(day):
        fy = CAL[day]['fy']
        if f:
            n = FYDAYS[fy]
            if fy == 'FY 2027':
                n = FYDAYS['FY 2026']        # incomplete FY: last complete FY count
            return n
        return 246
    for q in mq:
        rev = mrev(q)
        days = qdays(q, MTF_DAYS)
        if f:
            den = sum(BOOK[x] * yld / mtf_daysbasis(x) for x in days)
            s = rev / den
            avgbook = rev / (yld * len(days) / mtf_daysbasis(days[0]))
        else:
            avgbook = rev / (yld / 4.0)
            s = avgbook / IND_AVG_Q[q]
        mt[q] = {'rev': rev, 'share': s, 'book': avgbook, 'cal': True, 'n': len(days)}
    if not f and not e:
        typed = {'Q2 FY 2027': 0.0288, 'Q3 FY 2027': 0.032, 'Q4 FY 2027': 0.036}
        for q, s in typed.items():
            mt[q] = {'share': s, 'cal': False}
    else:
        last = mq[-1]
        for q in ('Q2 FY 2027', 'Q3 FY 2027', 'Q4 FY 2027'):
            if q not in mt:
                mt[q] = {'share': mt[last]['share'], 'cal': False}
        # Q3/Q4 carry from the last actual
        for q in ('Q3 FY 2027', 'Q4 FY 2027'):
            mt[q]['share'] = mt[mq[-1]]['share']
    P['mtf'] = mt
    # ---------------- daily revenue
    R = {'fo': {}, 'cash': {}, 'comm': {}, 'mtf': {}}
    zero_q = ('Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026')
    for x in FO_DAYS:
        q = CAL[x]['q_fy']
        if q in P['fo'] and P['fo'][q].get('tr') is not None:
            p = P['fo'][q]
            R['fo'][x] = V(x, c) / CPO_FO[CAL[x]['fy_month']] * p['share'] * p['tr']
        elif q in zero_q:
            R['fo'][x] = 0.0
        else:
            R['fo'][x] = None
    for x in CASH_DAYS:
        q = CAL[x]['q_fy']
        if q in P['cash']:
            p = P['cash'][q]
            R['cash'][x] = N(x) / p['tpo'] * p['share'] * p['tr']
        elif q in zero_q:
            R['cash'][x] = 0.0
        else:
            R['cash'][x] = None
    for x in COMM_DAYS:
        q = CAL[x]['q_fy']
        p = P['comm'][q]
        R['comm'][x] = M(x) / CPO_COMM[CAL[x]['fy_month']] * p['share'] * p['tr']
    for x in MTF_DAYS:
        q = CAL[x]['q_fy']
        s = P['mtf'][q]['share']
        R['mtf'][x] = s * BOOK[x] * yld / mtf_daysbasis(x)
    return P, R


def adr(R, seg, key, label, skip=()):
    sel = []
    for x, v in R[seg].items():
        if x in skip or v is None:
            continue
        c = CAL[x]
        if (key == 'fy' and c['fy'] == label) or (key == 'q' and c['q_fy'] == label) or (key == 'm' and c['fy_month'] == label):
            sel.append(v)
    if not sel:
        return 0.0
    return mean(sel) / (1.0 if seg == 'mtf' else 10.0)


PERIODS = [('FY 2027', 'fy'), ('Q2 FY 2027', 'q'), ('FY 2027 October', 'm'), ('FY 2026', 'fy'), ('FY 2026 October', 'm')]


def summary(flags):
    P, R = build(flags)
    skip = set(SPECIAL) if 'g' in flags else set()
    out = {}
    for lab, key in PERIODS:
        seg = {}
        seg['F&O'] = adr(R, 'fo', key, lab, skip)
        seg['Cash'] = adr(R, 'cash', key, lab, skip)
        seg['Commodities'] = adr(R, 'comm', key, lab, skip)
        seg['MTF'] = adr(R, 'mtf', key, lab)
        seg['Broking'] = seg['F&O'] + seg['Cash'] + seg['Commodities']
        seg['Consolidated'] = seg['Broking'] + seg['MTF']
        for k, v in seg.items():
            out[(lab, k)] = v
    return P, R, out


# ---------------- bridge parsing (plain string handling) ----------------
def num(s):
    s = s.strip().replace(',', '').replace('%', '').replace('+', '')
    if s in ('—', '', '-'):
        return None
    return float(s)


def decimals(s):
    s = s.strip().replace(',', '').replace('%', '')
    return len(s.split('.')[1]) if '.' in s else 0


def tables(path):
    cur = None
    out = []
    for l in open(path):
        l = l.strip()
        if l.startswith('|'):
            cells = [c.strip() for c in l.strip('|').split('|')]
            if cur is None:
                cur = {'hdr': cells, 'rows': []}
                out.append(cur)
            elif not l.replace('|', '').replace(':', '').replace('-', '').strip():
                pass
            else:
                cur['rows'].append(cells)
        else:
            cur = None
    return out


def cmp1(mine, printed):
    """compare a float with a printed string. returns (rel diff, ok, exact)."""
    t = num(printed)
    if t is None or mine is None:
        ok = (t is None and mine is None)
        return (0.0 if ok else float('inf')), ok, ok
    dec = decimals(printed)
    tol = 0.5 * 10 ** (-dec) * (1 + 1e-9)
    rel = abs(mine - t) / abs(t) if t else abs(mine - t)
    return rel, (abs(mine - t) <= tol or rel <= 1e-6), rel <= 1e-6


SEGMAP = {'F&O': 'fo', 'Cash': 'cash', 'Commodities': 'comm', 'MTF': 'mtf'}


def getp(P, seg, qty, q):
    d = P[SEGMAP[seg]].get(q)
    if d is None:
        return None
    if qty.startswith('revenue'):
        return d.get('rev')
    if qty.startswith('take rate'):
        return d.get('tr')
    if qty.startswith('Groww average book'):
        return d.get('book')
    if qty.startswith('share'):
        return d.get('share')
    raise ValueError(qty)


def dpct(b, a):
    if b is None or a is None or b == 0:
        return None
    return (a / b - 1) * 100


ITEMS = []     # (kind, label, detail, ok, exact, maxrel)


def add(kind, label, detail, ok, exact, rel):
    ITEMS.append((kind, label, detail, bool(ok), bool(exact), rel))


def check_adr(path, flags, prev):
    P, R, S = summary(set(flags))
    P0, R0, S0 = summary(set(prev))
    lines = ['| Period | Panel | My before | Bridge before | My after | Bridge after | Max rel diff | Verdict |', '|---|---|---:|---:|---:|---:|---:|---|']
    for t in tables(path):
        if t['hdr'][:2] == ['Period', 'Panel']:
            for r in t['rows']:
                k = (r[0], r[1])
                rb, okb, exb = cmp1(S0[k], r[2])
                ra, oka, exa = cmp1(S[k], r[3])
                # printed delta %
                dd = dpct(S0[k], S[k])
                rd, okd, exd = cmp1(dd if dd is not None else 0.0, r[5])
                ok = okb and oka and okd
                ex = exb and exa
                mr = max(rb, ra)
                add('ADR', '%s | %s' % k, '', ok, ex, mr)
                lines.append('| %s | %s | %.6f | %s | %.6f | %s | %.1e | %s |' % (r[0], r[1], S0[k], r[2], S[k], r[3], mr, 'agree' if ok else 'DIFFER'))
    return P, R, S, P0, R0, S0, lines


def check_params(path, P, P0):
    lines = ['| Segment | Quantity | Quarter | My before | Bridge before | My after | Bridge after | My d% | Bridge d% | Verdict |', '|---|---|---|---:|---:|---:|---:|---:|---:|---|']
    for t in tables(path):
        if t['hdr'][:3] == ['Segment', 'Quantity', 'Quarter']:
            for r in t['rows']:
                mb = getp(P0, r[0], r[1], r[2])
                ma = getp(P, r[0], r[1], r[2])
                rb, okb, exb = cmp1(mb, r[3])
                ra, oka, exa = cmp1(ma, r[4])
                dd = dpct(mb, ma)
                if r[5].strip() == '':
                    okd = dd is None
                    rdd = 'blank'
                else:
                    _, okd, _ = cmp1(dd if dd is not None else 0.0, r[5])
                    rdd = r[5]
                ok = okb and oka and okd
                ex = exb and exa
                mr = max(rb, ra) if (rb != float('inf') and ra != float('inf')) else float('inf')
                add('param', '%s | %s | %s' % (r[0], r[1], r[2]), '', ok, ex, mr)
                f = lambda v: '—' if v is None else '%.6g' % v
                lines.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                    r[0], r[1], r[2], f(mb), r[3], f(ma), r[4], f(dd), rdd, 'agree' if ok else 'DIFFER'))
    return lines


def check_inputs(path, flags):
    lines = ['| Input | Period | My workbook | Bridge workbook | My live | Bridge live | Fact ids ok | Vintage ok | Verdict |', '|---|---|---:|---:|---:|---:|---|---|---|']
    for t in tables(path):
        if t['hdr'][:2] == ['Input', 'Period']:
            for r in t['rows']:
                m, q = r[0], r[1]
                if m == 'mtf_revenue':
                    wb = WB.get(('mtf_revenue', q))
                    live = mtf_rev_live(q)
                elif m.startswith('revmix'):
                    wb = WB.get((m, q))
                    live = mix_live(m[7:], q)
                elif m.startswith('share_'):
                    wb = WB.get((m, q))
                    live = share_live(m.split('_')[1], q)
                elif m == 'total_income':
                    wb = None
                    live = fact('total_income', q)
                elif m == 'mtf_yield':
                    wb = DB_ASSUME['mtf_yield']
                    live = fact('mtf_yield', q)
                else:
                    raise ValueError(m)
                rw, okw, exw = cmp1(wb, r[2])
                rl, okl, exl = cmp1(live, r[3])
                # fact ids
                ids = []
                for tok in r[4].replace(';', ',').split(','):
                    tok = tok.strip()
                    if tok.isdigit():
                        ids.append(int(tok))
                idok = all(i in FRID and FRID[i]['period_key'] == q for i in ids)
                if m == 'mtf_revenue':
                    want = set(['revmix_mtf']) if 'seed:' in r[4] else set(['revmix_mtf', 'total_income'])
                    idok = idok and set(FRID[i]['metric'] for i in ids) == want
                elif m == 'total_income':
                    idok = idok and all(FRID[i]['metric'] == 'total_income' for i in ids)
                else:
                    idok = idok and all(FRID[i]['metric'] == m for i in ids)
                # facts of the same metric: value consistent with live
                vint = r[5]
                vok = True
                if m.startswith('revmix'):
                    restated = fact(m, q) is not None
                    vok = (restated and vint.startswith('restated')) or ((not restated) and vint.startswith('original'))
                elif m == 'mtf_revenue':
                    restated = fact('revmix_mtf', q) is not None
                    vok = (restated and vint.startswith('restated')) or ((not restated) and vint.startswith('original'))
                ok = okw and okl and idok and vok
                add('input', '%s | %s' % (m, q), '', ok, exw and exl, max(rw, rl) if rw != float('inf') and rl != float('inf') else float('inf'))
                f = lambda v: '—' if v is None else '%.6g' % v
                lines.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (m, q, f(wb), r[2], f(live), r[3], 'yes' if idok else 'NO', 'yes' if vok else 'NO', 'agree' if ok else 'DIFFER'))
    return lines


def check_daily(path, R, R0):
    """'Daily revenue rows that changed' table."""
    lines = ['| Segment | Days | Changed (mine / bridge) | First | Last | Ratio min (mine / bridge) | Ratio max (mine / bridge) | Verdict |', '|---|---:|---|---|---|---|---|---|']
    names = {'F&O': 'fo', 'Cash': 'cash', 'Commodities': 'comm', 'MTF': 'mtf'}
    for t in tables(path):
        if t['hdr'][:3] == ['Segment', 'Days', 'Changed']:
            for r in t['rows']:
                s = names[r[0]]
                days = [x for x in R[s]]
                nd = len(days)
                ch = []
                ratios = []
                for x in days:
                    a, b = R0[s][x], R[s][x]
                    if a is None or b is None:
                        continue
                    if abs(a - b) > 1e-12 * max(abs(a), abs(b), 1e-300):
                        ch.append(x)
                        if a != 0:
                            ratios.append(b / a)
                first = ch[0] if ch else ''
                last = ch[-1] if ch else ''
                okc = (len(ch) == int(r[2])) and first == r[3] and last == r[4]
                ok = okc
                mn = mx = None
                if r[5].strip():
                    c1 = ratios and abs(min(ratios) - float(r[5])) <= 0.5e-9 * 1.001
                    c2 = ratios and abs(max(ratios) - float(r[6])) <= 0.5e-9 * 1.001
                    ok = ok and bool(c1) and bool(c2)
                else:
                    ok = ok and not ratios
                ok = ok and nd == int(r[1])
                add('daily', r[0], '', ok, ok, 0.0)
                lines.append('| %s | %d | %d / %s | %s | %s | %s / %s | %s / %s | %s |' % (
                    r[0], nd, len(ch), r[2], first, last,
                    ('%.9f' % min(ratios)) if ratios else '', r[5], ('%.9f' % max(ratios)) if ratios else '', r[6], 'agree' if ok else 'DIFFER'))
    return lines


DB_ASSUME = {a['key']: a['value'] for a in DB['assumptions'] if a['broker_id'] == '*' and a['value'] is not None}


def counts():
    out = {}
    for k, l, d, ok, ex, rel in ITEMS:
        o = out.setdefault(k, [0, 0, 0])
        o[0] += 1
        o[1] += 1 if ok else 0
        o[2] += 1 if (ok and ex) else 0
    return out


def finish(tag, title, lines_by_section, extra_notes, outdir):
    cs = counts()
    base = globals().get('OUTBASE', 'groww_switch_%s' % tag)
    tot = sum(v[0] for v in cs.values())
    agr = sum(v[1] for v in cs.values())
    ex = sum(v[2] for v in cs.values())
    md = ['# Groww %s: independent recompute' % ('switch ' + title if tag != 'orders' else title), '',
          'Script: `out/checks/%s` (stdlib json/math/csv). Inputs: db snapshot, Groww fixtures/snapshot, reviewed facts, Angel calibration read from `parity_expected`. No engine code read.' % globals().get('SCRIPTNAME', 'groww_switch_%s_check.py' % tag), '',
          '**Result: %d/%d items agree** (%d to 1e-6 relative; %d agree only to the bridge print precision).' % (agr, tot, ex, agr - ex), '',
          '| Item kind | Checked | Agree | Agree at 1e-6 |', '|---|---:|---:|---:|']
    for k, v in cs.items():
        md.append('| %s | %d | %d | %d |' % (k, v[0], v[1], v[2]))
    md.append('')
    for sec, lines in lines_by_section:
        md.append('## ' + sec)
        md.append('')
        md.extend(lines)
        md.append('')
    md.append('## Notes')
    md.append('')
    md.extend(extra_notes)
    md.append('')
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, base + '.md'), 'w') as fh:
        fh.write('\n'.join(md))
    with open(os.path.join(outdir, base + '_items.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['kind', 'item', 'agree', 'agree_1e-6', 'max_rel_diff'])
        for k, l, d, ok, ex_, rel in ITEMS:
            w.writerow([k, l, ok, ex_, rel])
    print('switch %s: %d/%d agree (%d at 1e-6)' % (tag, agr, tot, ex))
    for k, v in cs.items():
        print('  %-6s %d/%d' % (k, v[1], v[0]))
    bad = [(k, l) for k, l, d, ok, ex_, rel in ITEMS if not ok]
    for b in bad:
        print('  DIFFER', b)
    return agr, tot


def ties(P, R, P0, seg_list):
    """self-consistency: sum of daily revenue in a newly calibrated quarter vs the quarter's reported revenue."""
    lines = ['| Segment | Quarter | Reported revenue | Sum of daily revenue | Rel diff | Tolerance | Verdict |', '|---|---|---:|---:|---:|---:|---|']
    daysmap = {'fo': FO_DAYS, 'cash': CASH_DAYS, 'comm': COMM_DAYS}
    for s in seg_list:
        for q, p in P[s].items():
            if 'rev' not in p:
                continue
            old = P0[s].get(q)
            if old is not None and old.get('rev') == p['rev'] and old.get('tr') == p['tr'] and old.get('share') == p['share']:
                continue
            Rs = R[s]
            tot = sum(Rs[x] for x in qdays(q, daysmap[s]) if Rs[x] is not None)
            rel = abs(tot / p['rev'] - 1)
            fac = 1.05 if (s == 'comm' and 'd' not in FLAGS) else 1.0   # parity commodity share carries the typed 5% growth
            rel = abs(tot / (p['rev'] * fac) - 1)
            tol = 5e-3 if s == 'fo' else 1e-9
            ok = rel <= tol
            add('tie', '%s | %s' % (s, q), '', ok, ok, rel)
            lines.append('| %s | %s | %.4f | %.4f | %.2e | %.0e | %s |' % (s, q, p['rev'], tot, rel, tol, 'agree' if ok else 'DIFFER'))
    return lines

TAG = 'a'
FLAGS = 'a'
PREV = ''
BR = os.path.join(ROOT, 'out', 'bridges', 'groww_%s.md' % TAG)
SEC = []
P, R, S, P0, R0, S0, l = check_adr(BR, FLAGS, PREV)
SEC.append(('ADR, Rs crore per trading day (consolidated and panels)', l))
SEC.append(('Parameters that moved', check_params(BR, P, P0)))
SEC.append(('Inputs replaced (reviewed facts)', check_inputs(BR, FLAGS)))
SEC.append(('Daily revenue rows that changed', check_daily(BR, R, R0)))
NOTES = []

SEC.append(('Tie-out of newly calibrated quarters (self-consistency, not in the bridge)', ties(P, R, P0, ['fo', 'cash', 'comm'])))

NOTES.extend(["Method. Parity is first rebuilt from raw inputs (exchange volumes, Angel monthly contracts/order, quarterly trades/order, commodity contracts/order, Angel commodity take rates, industry MTF book) and reproduces the 573/573/272/507 daily Groww rows of `groww_fixtures_2026-10-23.json` to 1e-15 relative; this is the 'Before' column of g-a.", "Formulas. Segment revenue (Rs Mn) = revenue mix x consolidated total income. F&O take rate = revenue / (sum of NSE+BSE contracts / quarterly mean of the three monthly Angel contracts-per-order x ADTO share). Cash take rate = revenue / (sum of trades / Angel trades-per-order x share). Commodity share = revenue / Angel take rate / sum of market orders over Oct-Dec 2025, times 1.05 (growth kept until g-d). MTF average book = revenue / (0.1495/4), share = book / Angel industry quarterly average. Daily revenue = market orders x share x take rate (MTF: share x daily book x 0.1495/246). Carry rules for unreported quarters are the workbook's (F&O take rate carried, share x1.05 once; cash take rate trailing 3).", "Spec vs switch: the spec says 'one classification of the stocks mix'. The switch uses the restated classification (Q2 FY27 letter p6) wherever it exists and the original classification where it does not (Q1 FY26 under g-b; MTF Q3 FY25 to Q1 FY26). The restatement moved cash by about -1.6pp in Q2 FY26 (0.194 to 0.178), so the Q1 FY26 cash mix (0.193) sits on a classification about 8% richer than its neighbours. Disclosed in the bridge vintage column but not 'one classification'.", 'Spec vs switch: the spec names MTF mixes for Q4 FY25, Q1 FY26 and Q4 FY26 only. The switch also replaces Q3 FY25 (2%), Q2 FY26 (4.7%), Q3 FY26 (5.6%) and Q1 FY27 (8.0%; 118.00 to 123.89 Cr). Values agree with the facts file; the extra quarters are an enlargement of scope, not an error.', 'MTF Q2 FY27 ADR is unchanged at g-a because its share is still the typed 0.0288 (the share is not re-derived from revenue until g-f).'])
finish(TAG, 'g-' + TAG, SEC, NOTES, HERE)
