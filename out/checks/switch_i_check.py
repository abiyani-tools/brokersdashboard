# Independent check of switch (i): monthly inputs extended to Sep-2026 (F&O share/orders, commodity orders/share).
# Stdlib only; reads snapshot JSON only.  Run: python3 -I out/checks/switch_i_check.py
import json, re
R = '/home/user/brokersdashboard/snapshot/'
d = json.load(open(R + 'db_snapshot_2026-10-23.json'))
f = json.load(open(R + 'facts_reviewed_2026-10-23.json'))
n = ag = 0
bad = []


def cmp(name, m, c, dp=6):
    global n, ag
    tol = max(1e-6 * abs(c), 0.5 * 10 ** (-dp) * 1.001)
    ok = abs(m - c) <= tol
    n += 1; ag += ok
    if not ok: bad.append(name)
    print('%-50s mine %.9f claim %.*f rel %.2e %s' % (name, m, dp, c, abs(m - c) / abs(c) if c else abs(m), 'AGREE' if ok else 'DISAGREE'))


def chk(name, ok, info=''):
    global n, ag
    n += 1; ag += bool(ok)
    if not ok: bad.append(name)
    print('%-50s %s %s' % (name, 'AGREE' if ok else 'DISAGREE', info))


# ---------------------------------------------------------------- inputs
seed = {}
for x in d['facts']:
    m = re.match(r'excel:Working sheet - Angel One!([A-Z]+)(\d+)$', x['source_ref'])
    if m: seed[(m.group(1), int(m.group(2)))] = x['value']
seed[('J', 8)] = 35                                       # switch a
Q = ['Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027']
col = dict(zip(Q, 'FGHIJKM'))
rev = {}
for x in f['facts']:
    if x['status'] == 'reviewed': rev[(x['metric'], x['period_key'], x['period_type'])] = x['value']
rq = lambda m, k: rev[(m, k, 'Q')]
rm = lambda m, k: rev[(m, k, 'M')]
mix = {(s, q): rq('revmix_' + s, q) for s in ('fo', 'comm') for q in Q + ['Q2 FY 2027']}   # switch b
TI = {q: seed[(col[q], 99)] for q in Q}; TI['Q2 FY 2027'] = 14315.0
O = {('fo', 'Q2 FY 2027'): 256.0, ('comm', 'Q2 FY 2027'): 45.0}
for s, r in (('fo', 6), ('comm', 8)):
    for q in Q: O[(s, q)] = seed[(col[q], r)]
TR = {k: mix[k] * TI[k[1]] / O[k] for k in mix}           # take rate (Rs Mn per Mn orders)
cal = {c['trade_date']: c for c in d['calendar']}
MD = {(x['dataset'], x['trade_date']): x['value'] for x in d['market_daily']}
LAKE = {x['trade_date']: x['value'] for x in d['market_daily_lake'] if x['dataset'] == 'bse_fo'}
chk('15 lake days, all 2026', len(LAKE) == 15)
pe = {}
for x in d['parity_expected']:
    if x['kind'] == 'daily':
        k, _, dt = x['key'].partition('|'); pe[(k, dt)] = x['value']
mkt = lambda dt: (MD[('nse_fo', dt)] + (LAKE[dt] if dt in LAKE else MD[('bse_fo', dt)])) / 1e6
MONTHS = ['FY 2027 ' + m for m in ('April', 'May', 'June', 'July', 'August', 'September', 'October')]
adr_days = lambda D, fld, key: [v for dt, v in D.items() if cal[dt][fld] == key]
adr = lambda D, fld, key: sum(adr_days(D, fld, key)) / len(adr_days(D, fld, key))

# reviewed monthly facts used by (i)
TO = {m: rm('total_orders', m) for m in MONTHS[2:6]}
SH = {m: rm('share_fo', m) for m in MONTHS[2:6]}
chk('reviewed total_orders Jun..Sep', [TO[m] for m in MONTHS[2:6]] == [140.04, 134.68, 109.5, 122.29], TO)
chk('reviewed share_fo Jun..Sep', [round(SH[m], 6) for m in MONTHS[2:6]] == [0.221, 0.222, 0.217, 0.225], SH)
# workbook seeds (months already in workbook, not changed)
C = {x['period_key']: x['value'] for x in d['facts'] if x['source_ref'].startswith('excel: F&O market!C')}
N = {x['period_key']: x['value'] for x in d['facts'] if x['source_ref'].startswith('excel: F&O market!N')}
chk('workbook F&O C and N end at FY2027 May', 'FY 2027 May' in C and 'FY 2027 June' not in C and 'FY 2027 May' in N and 'FY 2027 June' not in N)
chk('Working sheet C167 (June) 140.04 == reviewed', abs(rm('total_orders', 'FY 2027 June') - 140.04) < 1e-12)

mon = {}
for dt, c in cal.items():
    if ('nse_fo', dt) in MD: mon.setdefault(c['fy_month'], []).append(dt)
mc = {m: sum(mkt(dt) for dt in mon[m]) for m in MONTHS}            # market F&O contracts, Mn

# ================================================================== F&O
print('\n=== F&O ===')
E1 = seed[('M', 6)] / (seed[('M', 6)] + seed[('M', 7)] + seed[('M', 8)])   # Q1 FY27 300/407 (Apr, May, Jun)
E2 = rq('orders_fo', 'Q2 FY 2027') / (rq('orders_fo', 'Q2 FY 2027') + rq('orders_cash', 'Q2 FY 2027') + rq('orders_comm', 'Q2 FY 2027'))  # 256/367
cmp('E Q1 FY27 300/407', E1, 0.737101); cmp('E Q2 FY27 256/367', E2, 0.697548)
Ea = {'FY 2027 April': E1, 'FY 2027 May': E1, 'FY 2027 June': E1, 'FY 2027 July': E2, 'FY 2027 August': E2, 'FY 2027 September': E2}
C_i = dict(C); C_i.update(TO)
N_i = dict(N); N_i.update(SH)
H_b, H_a = {}, {}                       # contracts per order, before (a-h) and after (a-i)
for m in MONTHS[:2]:
    H_b[m] = H_a[m] = N[m] * mc[m] / (Ea[m] * C[m])
for m in MONTHS[2:6]:
    G = N_i[m] * mc[m]; F = Ea[m] * C_i[m]; H_a[m] = G / F
    print(m, 'G = %.3f x %.4f = %.4f; F = %.6f x %.2f = %.4f; H = %.5f' % (N_i[m], mc[m], G, Ea[m], C_i[m], F, H_a[m]))
H_a['FY 2027 October'] = H_a['FY 2027 September']
for m in MONTHS[2:]: H_b[m] = H_b['FY 2027 May']
for m, c in (('FY 2027 June', 14.642), ('FY 2027 July', 15.80632), ('FY 2027 August', 13.38654), ('FY 2027 September', 14.46973), ('FY 2027 October', 14.46973)):
    cmp('H after ' + m, H_a[m], c, dp=3 if m.endswith('June') else 5)
for m in ('FY 2027 June', 'FY 2027 October'): cmp('H before ' + m, H_b[m], 14.19975, dp=5)
chk('H before Jul/Aug/Sep all carry 14.19975', all(abs(H_b[m] - 14.19975) < 5e-6 for m in MONTHS[3:]))
sh_b = {m: (N[m] if m in N else 0.221) for m in MONTHS}
chk('share before Jun..Oct = avg(Mar,Apr,May)=0.221', abs((N['FY 2026 March'] + N['FY 2027 April'] + N['FY 2027 May']) / 3 - 0.221) < 1e-12)
sh_a = dict(N_i); sh_a['FY 2027 October'] = (N_i['FY 2027 July'] + N_i['FY 2027 August'] + N_i['FY 2027 September']) / 3
cmp('F&O Oct share after mean(.222,.217,.225)', sh_a['FY 2027 October'], 0.221333)
cmp('F&O Oct share before', sh_b['FY 2027 October'], 0.221, dp=3)
# take rates (unchanged by i, as established in switch h)
fo_tr = {q: TR[('fo', q)] for q in Q + ['Q2 FY 2027']}
fo_q3 = (fo_tr['Q4 FY 2026'] + fo_tr['Q1 FY 2027'] + fo_tr['Q2 FY 2027']) / 3
trq = lambda q: fo_tr[q] if q in fo_tr else fo_q3
FO_B, FO_A = {}, {}
for (k, dt) in pe:
    if k == 'fo_rev_mn' and dt >= '2026-04-01':
        c = cal[dt]; m = c['fy_month']
        FO_B[dt] = mkt(dt) / H_b[m] * sh_b[m] * trq(c['q_fy']) / 10
        FO_A[dt] = mkt(dt) / H_a[m] * sh_a[m] * trq(c['q_fy']) / 10
chk('F&O FY27 days 138', len(FO_B) == 138, len(FO_B))
chg = [dt for dt in FO_B if abs(FO_A[dt] / FO_B[dt] - 1) > 1e-12]
chk('F&O changed days 99, 2026-06-01..2026-10-21', len(chg) == 99 and (min(chg), max(chg)) == ('2026-06-01', '2026-10-21'), (len(chg), min(chg), max(chg)))
rr = [FO_A[dt] / FO_B[dt] for dt in chg]
cmp('F&O day ratio min', min(rr), 0.902424); cmp('F&O day ratio max', max(rr), 1.041549)
# sanity: before-state F&O ADR vs switch h claims (a-h)
cmp('sanity F&O FY27 before == h after', adr(FO_B, 'fy', 'FY 2027'), 9.965732)
cmp('sanity F&O Q2 before == h after', adr(FO_B, 'q_fy', 'Q2 FY 2027'), 8.749915)
cmp('sanity F&O Oct before == h after', adr(FO_B, 'fy_month', 'FY 2027 October'), 11.874226)

# ================================================================== Commodity
print('\n=== Commodity ===')
mcx = {dt: v for (ds, dt), v in MD.items() if ds == 'mcx'}
mcm = {}
for dt, v in mcx.items(): mcm[cal[dt]['fy_month']] = mcm.get(cal[dt]['fy_month'], 0) + v / 1e6
pcs = {x['key'].split('|')[1]: x['value'] for x in d['parity_expected'] if x['key'].startswith('comm_share_m|')}
CS = {'FY 2027 April': pcs['FY 2027 April'], 'FY 2027 May': pcs['FY 2027 May'], 'FY 2027 June': rm('share_comm', 'FY 2027 June'),
      'FY 2027 July': 0.48, 'FY 2027 August': 0.437}             # workbook AA38..AA42 (Apr/May via Excel's AA, Jun reviewed == Excel .52)
chk('June comm share reviewed == workbook AA40 .52', abs(CS['FY 2027 June'] - pcs['FY 2027 June']) < 1e-12)
chk('workbook Jul/Aug comm share == reviewed', rm('share_comm', 'FY 2027 July') == 0.48 and abs(rm('share_comm', 'FY 2027 August') - 0.437) < 1e-12)
CS_i = dict(CS); CS_i['FY 2027 September'] = rm('share_comm', 'FY 2027 September')
cmp('reviewed Sep comm share', CS_i['FY 2027 September'], 0.417, dp=3)
pct1 = seed[('M', 8)] / rq('orders_total', 'Q1 FY 2027')                 # Working sheet I182 = 40/406.14
pct2 = rq('orders_comm', 'Q2 FY 2027') / rq('orders_total', 'Q2 FY 2027')  # 45/366.46
cmp('comm% Q2 FY27 45/366.46', pct2, 45 / 366.46, dp=9)
pq = {x['key'].split('|')[1]: x['value'] for x in d['parity_expected'] if x['key'].startswith('comm_pct_q|')}
cmp('sanity comm% Q1 FY27 vs Excel I182', pct1, pq['Q1 FY 2027'], dp=9)
TOc = {'FY 2027 April': C['FY 2027 April'], 'FY 2027 May': C['FY 2027 May'], 'FY 2027 June': TO['FY 2027 June'], 'FY 2027 July': TO['FY 2027 July'],
       'FY 2027 August': TO['FY 2027 August'], 'FY 2027 September': TO['FY 2027 September']}
pcm = {x['key'].split('|')[1]: x['value'] for x in d['parity_expected'] if x['key'].startswith('comm_cpo_m|')}
Z = {}
for m in MONTHS[:6]:
    pc = pct1 if m in MONTHS[:3] else pct2
    Y = TOc[m] * pc; X = Y / CS_i.get(m, 0.417); Z[m] = mcm[m] / X
for m in MONTHS[:3]: cmp('sanity Z %s vs Excel Z' % m[8:], Z[m], pcm[m], dp=9)
Zb = dict((m, Z[m]) for m in MONTHS[:3])
Zb['FY 2027 July'] = sum(Z[m] for m in MONTHS[:3]) / 3
Zb['FY 2027 August'] = (Z['FY 2027 May'] + Z['FY 2027 June'] + Zb['FY 2027 July']) / 3
Zb['FY 2027 September'] = Zb['FY 2027 October'] = Zb['FY 2027 August']
cmp('Z before July', Zb['FY 2027 July'], 12.70223, dp=5); cmp('sanity Z before July vs Excel Z41', Zb['FY 2027 July'], pcm['FY 2027 July'], dp=9)
cmp('Z before Aug', Zb['FY 2027 August'], 13.0244, dp=4); cmp('sanity Z before Aug vs Excel Z42', Zb['FY 2027 August'], pcm['FY 2027 August'], dp=9)
cmp('Z before Sep', Zb['FY 2027 September'], 13.0244, dp=4); cmp('Z before Oct', Zb['FY 2027 October'], 13.0244, dp=4)
Za = dict(Z)
Za['FY 2027 October'] = (Z['FY 2027 July'] + Z['FY 2027 August'] + Z['FY 2027 September']) / 3
for m, c in (('July', 11.91392), ('August', 13.65102), ('September', 14.62069), ('October', 13.39521)):
    cmp('Z after ' + m, Za['FY 2027 ' + m], c, dp=5)
for m in MONTHS[3:]: print(m, 'MCX %.4f Mn; total orders %s' % (mcm[m], TOc.get(m)))
CSb = dict(CS); CSb['FY 2027 September'] = CSb['FY 2027 October'] = 0.437
CSa = dict(CS_i); CSa['FY 2027 October'] = CSa['FY 2027 September']
cmp('share Sep before', CSb['FY 2027 September'], 0.437, dp=3); cmp('share Sep after', CSa['FY 2027 September'], 0.417, dp=3)
cmp('share Oct before', CSb['FY 2027 October'], 0.437, dp=3); cmp('share Oct after', CSa['FY 2027 October'], 0.417, dp=3)
# take rate (switch f/h): per quarter own rate for Q1, Q2; Q3 carries Q2
cr = {q: TR[('comm', q)] for q in ('Q1 FY 2027', 'Q2 FY 2027')}
ctr = lambda q: cr['Q1 FY 2027'] if q == 'Q1 FY 2027' else cr['Q2 FY 2027']
CM_B, CM_A = {}, {}
for (k, dt) in pe:
    if k == 'comm_rev_mn' and dt >= '2026-04-01':
        c = cal[dt]; m = c['fy_month']
        CM_B[dt] = mcx[dt] / 1e6 / Zb[m] * CSb[m] * ctr(c['q_fy']) / 10
        CM_A[dt] = mcx[dt] / 1e6 / Za[m] * CSa[m] * ctr(c['q_fy']) / 10
chg = [dt for dt in CM_B if abs(CM_A[dt] / CM_B[dt] - 1) > 1e-12]
chk('Comm changed days 80, 2026-07-01..2026-10-21', len(chg) == 80 and (min(chg), max(chg)) == ('2026-07-01', '2026-10-21'), (len(chg), min(chg), max(chg)))
rr = [CM_A[dt] / CM_B[dt] for dt in chg]
cmp('Comm day ratio min', min(rr), 0.850050); cmp('Comm day ratio max', max(rr), 1.066167)
cmp('sanity Comm FY27 before == h after', adr(CM_B, 'fy', 'FY 2027'), 1.567012)

# ================================================================== ADR
print('\n=== ADR (Rs Cr/day) ===')
CONS_B = {'fy': 17.741633, 'q_fy': 16.812941, 'fy_month': 20.559858}   # a-h consolidated (verified in switch h)
CL = {('FY 2027', 'fy'): ((9.965732, 9.783595), (1.567012, 1.517817), (17.741633, 17.510302)),
      ('Q2 FY 2027', 'q_fy'): ((8.749915, 8.510622), (1.617655, 1.539989), (16.812941, 16.495983)),
      ('FY 2027 October', 'fy_month'): ((11.874226, 11.670252), (1.937690, 1.797823), (20.559858, 20.216017))}
for (p, fl), (fo, cm, co) in CL.items():
    fb, fa, cb, ca = adr(FO_B, fl, p), adr(FO_A, fl, p), adr(CM_B, fl, p), adr(CM_A, fl, p)
    cmp('F&O %s before' % p, fb, fo[0]); cmp('F&O %s after' % p, fa, fo[1])
    cmp('Comm %s before' % p, cb, cm[0]); cmp('Comm %s after' % p, ca, cm[1])
    # cash, MTF unchanged -> consolidated(after) = consolidated(a-h) + dFO + dComm
    cmp('Consol %s before (a-h, switch h)' % p, CONS_B[fl], co[0])
    cmp('Consol %s after = before + dFO + dComm' % p, CONS_B[fl] + (fa - fb) + (ca - cb), co[1])
print('\nchecked %d agree %d' % (n, ag))
print('DISAGREE:', bad)
