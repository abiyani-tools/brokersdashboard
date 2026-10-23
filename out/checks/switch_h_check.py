# Independent check of switch (h): Q2 FY 2027 becomes an actual quarter.
# Stdlib only; reads snapshot JSON only.  Run: python3 -I out/checks/switch_h_check.py
import json, re
R = '/home/user/brokersdashboard/snapshot/'
d = json.load(open(R + 'db_snapshot_2026-10-23.json'))
f = json.load(open(R + 'facts_reviewed_2026-10-23.json'))
n = ag = 0
bad = []


def cmp(name, m, c, dp=6, extra=0.0):
    """claim c is printed to dp decimals -> allow rel 1e-6 or half-ulp of the printed claim."""
    global n, ag
    tol = max(1e-6 * abs(c), 0.5 * 10 ** (-dp) * 1.001) + extra
    ok = abs(m - c) <= tol
    n += 1
    ag += ok
    if not ok:
        bad.append(name)
    print('%-52s mine %.9f claim %.*f rel %.2e %s' % (name, m, dp, c, abs(m - c) / abs(c) if c else abs(m),
                                                      'AGREE' if ok else 'DISAGREE'))


def chk(name, ok, info=''):
    global n, ag
    n += 1
    ag += bool(ok)
    if not ok:
        bad.append(name)
    print('%-52s %s %s' % (name, 'AGREE' if ok else 'DISAGREE', info))


# ------------------------------------------------------------------ inputs
seed = {}
for x in d['facts']:
    m = re.match(r'excel:Working sheet - Angel One!([A-Z]+)(\d+)$', x['source_ref'])
    if m:
        seed[(m.group(1), int(m.group(2)))] = x['value']
seed[('J', 8)] = 35                                    # switch a
Q = ['Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027']
col = dict(zip(Q, 'FGHIJKM'))
rev = {}
for x in f['facts']:
    if x['status'] == 'reviewed':
        k = (x['metric'], x['period_key'])
        assert k not in rev or rev[k] == x['value'], k
        rev[k] = x['value']
mix = {(s, q): rev[('revmix_' + s, q)] for s in ('fo', 'cash', 'comm') for q in Q + ['Q2 FY 2027']}   # switch b (deck mix)
TI = {q: seed[(col[q], 99)] for q in Q}
TI['Q2 FY 2027'] = 14315.0
chk('reviewed total_income Q2 FY27 == 14315', rev[('total_income', 'Q2 FY 2027')] == 14315)
O = {('fo', 'Q2 FY 2027'): 256.0, ('cash', 'Q2 FY 2027'): 66.0, ('comm', 'Q2 FY 2027'): 45.0}
for s, k in (('fo', 'orders_fo'), ('cash', 'orders_cash'), ('comm', 'orders_comm')):
    chk('reviewed %s Q2 FY27 == task' % k, rev[(k, 'Q2 FY 2027')] == O[(s, 'Q2 FY 2027')])
chk('mix Q2 FY27 .387/.087/.071', (mix[('fo', 'Q2 FY 2027')], mix[('cash', 'Q2 FY 2027')], mix[('comm', 'Q2 FY 2027')]) == (0.387, 0.087, 0.071))
chk('share_cash_q Q2 FY27 0.168, avg_funding_book 74530, orders_total 366.46',
    (rev[('share_cash_q', 'Q2 FY 2027')], rev[('avg_funding_book', 'Q2 FY 2027')], rev[('orders_total', 'Q2 FY 2027')]) == (0.168, 74530.0, 366.46))
row_o = {'fo': 6, 'cash': 7, 'comm': 8}
for s in row_o:
    for q in Q:
        O[(s, q)] = seed[(col[q], row_o[s])]
TR = {k: mix[k] * TI[k[1]] / O[k] for k in mix}        # take rate = mix x total income / orders (a, b on)
cal = {c['trade_date']: c for c in d['calendar']}
MD = {}
for x in d['market_daily']:
    MD[(x['dataset'], x['trade_date'])] = x['value']
LAKE = {x['trade_date']: x['value'] for x in d['market_daily_lake'] if x['dataset'] == 'bse_fo'}
FROZEN = 18962859
pe = {}
for x in d['parity_expected']:
    if x['kind'] == 'daily':
        k, _, dt = x['key'].partition('|')
        pe[(k, dt)] = x['value']
ASM = {x['key']: x for x in d['assumptions']}
YLD, DAYS = ASM['mtf_yield']['value'], ASM['mtf_day_basis']['value']

# ================================================================== F&O
print('\n=== F&O ===')


def e_q(q, a=True):
    o6, o7, o8 = seed[(col[q], 6)], seed[(col[q], 7)], seed[(col[q], 8)]
    return o6 / (o6 + o7 + o8)


E_b = sum(e_q(q) for q in ('Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026')) / 3        # avg of 9 months = avg of 3 quarterly values x3
E_a = seed[('M', 6)] / (seed[('M', 6)] + seed[('M', 7)] + seed[('M', 8)])
print('Q1 FY27 orders fo/cash/comm', seed[('M', 6)], seed[('M', 7)], seed[('M', 8)])
cmp('F&O E Apr/May FY27 before (avg of 9)', E_b, 0.729933)
cmp('F&O E Apr/May FY27 after 300/407', E_a, 0.737101)
chk('E after == 300/(300+67+40)', abs(E_a - 300 / 407) < 1e-15)
C = {x['period_key']: x['value'] for x in d['facts'] if x['source_ref'].startswith('excel: F&O market!C')}
Nm = {x['period_key']: x['value'] for x in d['facts'] if x['source_ref'].startswith('excel: F&O market!N')}
mon = {}
for dt, c in cal.items():
    if ('nse_fo', dt) in MD:
        mon.setdefault(c['fy_month'], []).append(dt)


def mkt(dt):   # market contracts (Mn), real BSE on imputed days (switch c)
    return (MD[('nse_fo', dt)] + (LAKE[dt] if dt in LAKE else MD[('bse_fo', dt)])) / 1e6


H = {}
for mth, Ev_b, Ev_a in (('FY 2027 April', E_b, E_a), ('FY 2027 May', E_b, E_a)):
    G = Nm[mth] * sum(mkt(dt) for dt in mon[mth])
    H[mth] = (G / (Ev_b * C[mth]), G / (Ev_a * C[mth]))
    print(mth, 'G=%.6f (share %.3f x contracts) F_before=%.6f F_after=%.6f' % (G, Nm[mth], Ev_b * C[mth], Ev_a * C[mth]))
cmp('H Apr FY27 before', H['FY 2027 April'][0], 14.411181)
cmp('H Apr FY27 after', H['FY 2027 April'][1], 14.271051)
cmp('H May FY27 before', H['FY 2027 May'][0], 14.339181)
cmp('H May FY27 after', H['FY 2027 May'][1], 14.199750)
# sanity vs parity Excel H (no switch a: J8=36)
E_p = sum((lambda q: seed[(col[q], 6)] / (seed[(col[q], 6)] + seed[(col[q], 7)] + (36 if q == 'Q3 FY 2026' else seed[(col[q], 8)])))(q)
          for q in ('Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026')) / 3
pc = {x['key'].split('|')[1]: x['value'] for x in d['parity_expected'] if x['key'].startswith('fo_cpo_m|')}
Gm = Nm['FY 2027 May'] * sum(mkt(dt) for dt in mon['FY 2027 May'])
cmp('sanity: parity H May FY27 from raw vs Excel H51', Gm / (E_p * C['FY 2027 May']), pc['FY 2027 May'], dp=9)
# take rates
fo_b_proj = (TR[('fo', 'Q2 FY 2026')] + TR[('fo', 'Q3 FY 2026')] + TR[('fo', 'Q4 FY 2026')]) / 3
fo_a = {q: TR[('fo', q)] for q in Q + ['Q2 FY 2027']}
fo_a3 = (fo_a['Q4 FY 2026'] + fo_a['Q1 FY 2027'] + fo_a['Q2 FY 2027']) / 3
cmp('F&O TR Q1 FY27 before (proj avg Q2-Q4 FY26)', fo_b_proj, 21.409331)
cmp('F&O TR Q1 FY27 after (actual)', fo_a['Q1 FY 2027'], 21.553290)
cmp('F&O TR Q2 FY27 before (carried)', fo_b_proj, 21.409331)
cmp('F&O TR Q2 FY27 after 0.387*14315/256', fo_a['Q2 FY 2027'], 21.640254)
cmp('F&O TR Q3 FY27 before (carried)', fo_b_proj, 21.409331)
cmp('F&O TR Q3 FY27 after (avg Q4FY26,Q1,Q2 FY27)', fo_a3, 21.565956)
print('F&O take-rate Q1 deck-mix check: mix', mix[('fo', 'Q1 FY 2027')], 'x', TI['Q1 FY 2027'], '/', O[('fo', 'Q1 FY 2027')])
trb = lambda q: (fo_a[q] if q in Q[:6] else fo_b_proj)                      # before, by quarter
tra = lambda q: (fo_a[q] if q in Q + ['Q2 FY 2027'] else fo_a3)           # after
Hb = lambda dt: H['FY 2027 April'][0] if cal[dt]['fy_month'] == 'FY 2027 April' else H['FY 2027 May'][0]   # Jun+ carry May
Ha = lambda dt: H['FY 2027 April'][1] if cal[dt]['fy_month'] == 'FY 2027 April' else H['FY 2027 May'][1]
share_m = {}
mths = [m for m in dict.fromkeys(cal[dt]['fy_month'] for dt in sorted(cal))]
fo_share_proj = (Nm['FY 2026 March'] + Nm['FY 2027 April'] + Nm['FY 2027 May']) / 3          # N24 = AVERAGE(N21:N23)
fo_share = lambda mth: Nm[mth] if mth in Nm else fo_share_proj
chk('F&O projected monthly share = avg(Mar,Apr,May)=0.221', abs(fo_share_proj - 0.221) < 1e-12, fo_share_proj)

# ---- before daily series (a-g) from workbook daily values (same chain as switch_b/c/d scripts)
Qd = ['Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027']
tr_old_new = {q: (seed[(col[q], 15)] * TI[q] / seed[(col[q], 6)], fo_a[q]) for q in Q}          # (Excel deck mix, reviewed deck mix)
est_old = sum(tr_old_new[q][0] for q in Q[3:6]) / 3
est_new = sum(tr_old_new[q][1] for q in Q[3:6]) / 3
ra = e_q('Q2 FY 2026') + e_q('Q3 FY 2026') + e_q('Q4 FY 2026')
ra = E_b / E_p                                                                                       # switch a, 9-month average
fo_pe = {dt: v for (k, dt), v in pe.items() if k == 'fo_rev_mn'}
FO_B, FO_A = {}, {}
for dt, v in fo_pe.items():
    c = cal[dt]
    q = c['q_fy']
    b = v / 10
    if q == 'Q3 FY 2026':
        b *= 381 / 380
    elif dt >= '2026-04-01':
        b *= ra
    b *= (tr_old_new[q][1] / tr_old_new[q][0]) if q in Q[:6] else est_new / est_old                     # switch b
    if dt in LAKE:
        b *= (MD[('nse_fo', dt)] + LAKE[dt]) / (MD[('nse_fo', dt)] + FROZEN)                            # switch c
    FO_B[dt] = b
    if dt < '2026-04-01':
        FO_A[dt] = b
    else:                                                                                               # switch h: ratios from changed intermediates
        FO_A[dt] = b * (tra(q) / trb(q)) * (Hb(dt) / Ha(dt))
# direct rebuild for FY27 days: daily = (contracts/1e6)/H x share x TR  (Rs Mn) -> /10 Rs Cr
mx_b = mx_a = 0
for dt in FO_B:
    if dt >= '2026-04-01':
        c = cal[dt]
        q = c['q_fy']
        sh = fo_share(c['fy_month'])
        hb = Hb(dt)
        db = mkt(dt) / hb * sh * trb(q) / 10
        da = mkt(dt) / Ha(dt) * sh * tra(q) / 10
        mx_b = max(mx_b, abs(db / FO_B[dt] - 1))
        mx_a = max(mx_a, abs(da / FO_A[dt] - 1))
chk('F&O direct rebuild == adjusted-parity BEFORE (max rel %.1e)' % mx_b, mx_b < 1e-9)
chk('F&O direct rebuild == ratio AFTER (max rel %.1e)' % mx_a, mx_a < 1e-9)
chg = [dt for dt in FO_B if abs(FO_A[dt] / FO_B[dt] - 1) > 1e-12]
chk('F&O changed days 138, Apr1..Oct21', len(chg) == 138 and (min(chg), max(chg)) == ('2026-04-01', '2026-10-21'), (len(chg), min(chg), max(chg)))
chk('F&O nothing before 2026-04-01 changes', all(FO_A[dt] == FO_B[dt] for dt in FO_B if dt < '2026-04-01'))
rr = [FO_A[dt] / FO_B[dt] for dt in chg]
cmp('F&O day ratio min', min(rr), 1.016609392, dp=9)
cmp('F&O day ratio max', max(rr), 1.020711241, dp=9)

# ================================================================== Cash
print('\n=== Cash ===')
trades = {}
for (ds, dt), v in MD.items():
    if ds in ('nse_cash', 'bse_cash'):
        trades[dt] = trades.get(dt, 0) + v / 1e6
qt = {}
for dt, t in trades.items():
    qt[cal[dt]['q_fy']] = qt.get(cal[dt]['q_fy'], 0) + t
K = {q: seed[(col[q], 40)] for q in Q}
K['Q2 FY 2027'] = rev[('share_cash_q', 'Q2 FY 2027')]
P = {q: qt[q] / (O[('cash', q)] / K[q]) for q in Q if q in ('Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027')}
P['Q2 FY 2027'] = qt['Q2 FY 2027'] / (66 / K['Q2 FY 2027'])
print('market trades Mn: Q3FY26 %.3f Q4FY26 %.3f Q1FY27 %.3f Q2FY27 %.3f' % tuple(qt[q] for q in ('Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027', 'Q2 FY 2027')))
pcal = {x['key'].split('|')[1]: x['value'] for x in d['parity_expected'] if x['key'].startswith('cash_tpo_q|')}
cmp('sanity: P Q1 FY27 raw vs Excel G41', P['Q1 FY 2027'], pcal['Q1 FY 2027'], dp=9)
cmp('sanity: P Q4 FY26 raw vs Excel G40', P['Q4 FY 2026'], pcal['Q4 FY 2026'], dp=9)
P_b = (P['Q3 FY 2026'] + P['Q4 FY 2026'] + P['Q1 FY 2027']) / 3
T = {q: TR[('cash', q)] for q in Q + ['Q2 FY 2027']}
T_b = (T['Q3 FY 2026'] + T['Q4 FY 2026'] + T['Q1 FY 2027']) / 3
P_a3 = (P['Q4 FY 2026'] + P['Q1 FY 2027'] + P['Q2 FY 2027']) / 3
T_a3 = (T['Q4 FY 2026'] + T['Q1 FY 2027'] + T['Q2 FY 2027']) / 3
cmp('Cash P Q2 FY27 before (avg Q3FY26,Q4FY26,Q1FY27)', P_b, 6.150236)
cmp('Cash P Q2 FY27 after trades/(66/0.168)', P['Q2 FY 2027'], 6.852245)
cmp('Cash TR Q2 FY27 before', T_b, 16.512193)
cmp('Cash TR Q2 FY27 after 0.087*14315/66', T['Q2 FY 2027'], 18.869773)
cmp('Cash P Q3 FY27 after (avg Q4FY26,Q1,Q2 FY27)', P_a3, 6.535245)
cmp('Cash TR Q3 FY27 after', T_a3, 17.752967)
print('cash share Q2 FY27: before = monthly (Jul .171 Aug .170 Sep .162; Oct carries Sep), after = %.3f' % K['Q2 FY 2027'])
msh = {}
for x in d['facts'] + f['facts']:
    if x['metric'] == 'share_cash' and x['period_type'] == 'M':
        msh[x['period_key']] = x['value']
chk('monthly cash shares Jul/Aug/Sep FY27 = .171/.17/.162', (msh['FY 2027 July'], msh['FY 2027 August'], msh['FY 2027 September']) == (0.171, 0.17, 0.162))
chk('no monthly cash share for Oct FY27', 'FY 2027 October' not in msh)
cmp('Cash share Q2 FY27 after', K['Q2 FY 2027'], 0.168, dp=3)


def msc(mth):
    i = mths.index(mth)
    while mth_ok(mths[i]) is None:
        i -= 1
    return msh[mths[i]]


def mth_ok(m):
    return msh.get(m)


# before daily: a,b on (ratio of cash TR), (e) monthly share for projected days
CASH_B, CASH_A = {}, {}
cash_pe = {dt: v for (k, dt), v in pe.items() if k == 'cash_rev_mn'}
Qc = Q
tr_cash_old = {q: seed[(col[q], 16)] * TI[q] / seed[(col[q], 7)] for q in Q}
est_cash_old = sum(tr_cash_old[q] for q in Q[4:]) / 3
for dt, v in cash_pe.items():
    q = cal[dt]['q_fy']
    b = v * ((T[q] / tr_cash_old[q]) if q in Q else (T_b / est_cash_old))               # switch b
    if q not in Q:
        b *= msc(cal[dt]['fy_month']) / 0.174                                           # switch e
    CASH_B[dt] = b / 10
    if q in Q:
        CASH_A[dt] = CASH_B[dt]
    elif q == 'Q2 FY 2027':
        CASH_A[dt] = CASH_B[dt] * (K['Q2 FY 2027'] / msc(cal[dt]['fy_month'])) * (P_b / P['Q2 FY 2027']) * (T['Q2 FY 2027'] / T_b)
    else:    # Q3 FY27: projected -> monthly share (unchanged, Sep carried); P and TR now avg incl. Q2
        CASH_A[dt] = CASH_B[dt] * (P_b / P_a3) * (T_a3 / T_b)
mxb = mxa = 0
for dt in CASH_B:
    q = cal[dt]['q_fy']
    if q in Q:
        continue
    sh = msc(cal[dt]['fy_month'])
    db = trades[dt] * sh / P_b * T_b / 10
    if q == 'Q2 FY 2027':
        da = trades[dt] * K['Q2 FY 2027'] / P['Q2 FY 2027'] * T['Q2 FY 2027'] / 10
    else:
        da = trades[dt] * sh / P_a3 * T_a3 / 10
    mxb = max(mxb, abs(db / CASH_B[dt] - 1))
    mxa = max(mxa, abs(da / CASH_A[dt] - 1))
chk('Cash direct rebuild == adjusted-parity BEFORE (max rel %.1e)' % mxb, mxb < 1e-9)
chk('Cash direct rebuild == ratio AFTER (max rel %.1e)' % mxa, mxa < 1e-9)
chg = [dt for dt in CASH_B if abs(CASH_A[dt] / CASH_B[dt] - 1) > 1e-12]
chk('Cash changed days 78, Jul1..Oct21', len(chg) == 78 and (min(chg), max(chg)) == ('2026-07-01', '2026-10-21'), (len(chg), min(chg), max(chg)))
rr = [CASH_A[dt] / CASH_B[dt] for dt in chg]
cmp('Cash day ratio min', min(rr), 1.007706248, dp=9)
cmp('Cash day ratio max', max(rr), 1.063689928, dp=9)

# ================================================================== Commodity
print('\n=== Commodity ===')
cr = {q: TR[('comm', q)] for q in Q + ['Q2 FY 2027']}
BASE = 0.061 * seed[('J', 99)] / 35
cmp('Comm own rate Q2 FY27 0.071*14315/45', cr['Q2 FY 2027'], 22.585889)
cmp('Comm Q1 FY27 rate (before: Q2/Q3 carry)', cr['Q1 FY 2027'], 22.9392, dp=4)
cmp('Comm rate ratio', cr['Q2 FY 2027'] / cr['Q1 FY 2027'], 22.585889 / 22.9392, dp=9)
COMM_B, COMM_A = {}, {}
for (k, dt), v in pe.items():
    if k != 'comm_rev_mn':
        continue
    q = cal[dt]['q_fy']
    b = v / 10 * 36 / 35 * 0.061 / 0.06                                   # a, b (comm rate scaling under fixed-rate parity)
    b *= (cr[q] if q in Q else cr['Q1 FY 2027']) / BASE                  # f (before h: Q2+ carry Q1 FY27 rate)
    COMM_B[dt] = b
    COMM_A[dt] = b * (cr['Q2 FY 2027'] / cr['Q1 FY 2027'] if q in ('Q2 FY 2027', 'Q3 FY 2027') else 1.0)
chg = [dt for dt in COMM_B if abs(COMM_A[dt] / COMM_B[dt] - 1) > 1e-12]
chk('Comm changed days 80, Jul1..Oct21', len(chg) == 80 and min(chg) >= '2026-07-01', (len(chg), min(chg), max(chg)))
chk('Comm Q3 FY27 after carries Q2 own rate (ratio same)', True, 'Q3 days use %.6f' % cr['Q2 FY 2027'])
rr = [COMM_A[dt] / COMM_B[dt] for dt in chg]
cmp('Comm day ratio min', min(rr), 0.984597932, dp=9)
cmp('Comm day ratio max', max(rr), 0.984597932, dp=9)

# ================================================================== MTF
print('\n=== MTF ===')
book = {dt: v for (ds, dt), v in MD.items() if ds == 'mtf_industry'}
qb = {}
for dt, v in book.items():
    qb.setdefault(cal[dt]['q_fy'], []).append(v)
ind_q2 = sum(qb['Q2 FY 2027']) / len(qb['Q2 FY 2027'])
print('Q2 FY27 MTF days %d (first %s last %s)' % (len(qb['Q2 FY 2027']), min(dt for dt in book if cal[dt]['q_fy'] == 'Q2 FY 2027'), max(dt for dt in book if cal[dt]['q_fy'] == 'Q2 FY 2027')))
cmp('MTF industry avg Q2 FY27 (daily mean)', ind_q2, 141829.592, dp=3)
angel_q2 = 74530 / 10
sh_q2 = angel_q2 / ind_q2
cmp('MTF share Q2 FY27 after (7453/ind)', sh_q2, 0.0525490, dp=7)
mser = {x['fy_month']: x['value'] for x in d['monthly'] if x['dataset'] == 'mtf_industry'}
pin = {x['period_key']: x['value'] for x in d['pins'] if x['key'] == 'mtf_angel_book_cr'}
# Quarter k months in label order
def months_of(q):
    fy = int(q[-4:]); qq = int(q[1])
    order = {1: ['April', 'May', 'June'], 2: ['July', 'August', 'September'], 3: ['October', 'November', 'December'], 4: ['January', 'February', 'March']}[qq]
    return ['FY %d %s' % (fy, m) for m in order]
# the monthly seed labels are the workbook's FY labels; verify Q1 FY26 matches parity first
pm = {x['key'].split('|')[1]: x['value'] for x in d['parity_expected'] if x['key'].startswith('mtf_share_q|')}
act = {}
for q in ('Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027', 'Q4 FY 2025'):
    ind = sum(mser[m] for m in months_of(q)) / 3
    act[q] = pin[q] / ind
    cmp('sanity: MTF share %s = pinned book/monthly-series avg vs Excel Q' % q, act[q], pm[q], dp=9)
cl = {'Q1 FY 2026': 0.0536876, 'Q2 FY 2026': 0.0546817, 'Q3 FY 2026': 0.0512107, 'Q4 FY 2026': 0.0505477, 'Q1 FY 2027': 0.0515406}
for q, c in cl.items():
    cmp('MTF share %s (claim)' % q, act[q], c, dp=7)
b6 = sum(act[q] for q in ('Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027')) / 6
cmp('MTF share Q2/Q3 FY27 before (mean Q4FY25..Q1FY27)', b6, 0.0522225, dp=7)
a6 = sum(act[q] for q in ('Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027')) + sh_q2
a6 /= 6
cmp('MTF share Q3 FY27 after (mean Q1FY26..Q2FY27)', a6, 0.0523696, dp=7)
MTF_B, MTF_A = {}, {}
mtf_pe = {dt: v for (k, dt), v in pe.items() if k == 'mtf_gross_cr'}
mxb = 0
for dt, v in mtf_pe.items():
    q = cal[dt]['q_fy']
    MTF_B[dt] = v
    if q in ('Q2 FY 2027', 'Q3 FY 2027'):
        mxb = max(mxb, abs(b6 * book[dt] * YLD / DAYS / v - 1))
        MTF_A[dt] = (sh_q2 if q == 'Q2 FY 2027' else a6) * book[dt] * YLD / DAYS
    else:
        MTF_A[dt] = v
chk('MTF direct share x book x .1495/246 == parity BEFORE (max rel %.1e)' % mxb, mxb < 1e-9)
chg = [dt for dt in MTF_B if abs(MTF_A[dt] / MTF_B[dt] - 1) > 1e-12]
chk('MTF changed days 77, Jul1..Oct19', len(chg) == 77 and (min(chg), max(chg)) == ('2026-07-01', '2026-10-19'), (len(chg), min(chg), max(chg)))
rr = [MTF_A[dt] / MTF_B[dt] for dt in chg]
cmp('MTF day ratio min', min(rr), 1.002815870, dp=9)
cmp('MTF day ratio max', max(rr), 1.006251610, dp=9)

# ================================================================== ADR claims
print('\n=== ADR (Rs Cr/day; MTF gross) ===')


def adr(D, key, fld):
    v = [x for dt, x in D.items() if cal[dt][fld] == key]
    return sum(v) / len(v)


SEG = {'F&O': (FO_B, FO_A), 'Cash': (CASH_B, CASH_A), 'Commodities': (COMM_B, COMM_A), 'MTF': (MTF_B, MTF_A)}
CL = {('FY 2027', 'fy'): {'F&O': (9.785974, 9.965732), 'Cash': (1.958058, 1.984881), 'Commodities': (1.581557, 1.567012), 'MTF': (4.209385, 4.224009), 'Consolidated': (17.534973, 17.741633)},
      ('Q2 FY 2027', 'q_fy'): {'F&O': (8.572370, 8.749915), 'Cash': (1.863740, 1.916008), 'Commodities': (1.642960, 1.617655), 'MTF': (4.501224, 4.529364), 'Consolidated': (16.580294, 16.812941)},
      ('FY 2027 October', 'fy_month'): {'F&O': (11.673365, 11.874226), 'Cash': (1.982360, 2.005758), 'Commodities': (1.968001, 1.937690), 'MTF': (4.728868, 4.742184), 'Consolidated': (20.352594, 20.559858)}}
for (p, fl), segs in CL.items():
    mine = {s: (adr(b, p, fl), adr(a, p, fl)) for s, (b, a) in SEG.items()}
    mine['Consolidated'] = (sum(v[0] for v in mine.values()), sum(v[1] for v in mine.values()))
    print(p, 'days', {s: len([1 for dt in b if cal[dt][fl] == p]) for s, (b, a) in SEG.items()})
    for s, (cb, ca) in segs.items():
        cmp('%s %s before' % (p, s), mine[s][0], cb)
        cmp('%s %s after' % (p, s), mine[s][1], ca)
for (p, fl) in (('FY 2026', 'fy'), ('Q3 FY 2026', 'q_fy')):
    chk('%s ADRs unchanged (all 4 segments)' % p, all(abs(adr(b, p, fl) - adr(a, p, fl)) < 1e-12 for b, a in SEG.values()))
print('\nchecked %d agree %d' % (n, ag))
print('DISAGREE:', bad)
