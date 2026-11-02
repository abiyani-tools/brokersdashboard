# Independent check of switch (j): MTF basis per Q5 / Q6 for every reported quarter.
# Stdlib only. Reads snapshot JSON + out/bridges/{i,j}.md (claims) via `git show angel-mtf-j:<path>`
# (falls back to files under the repo root). Does NOT touch src/engine or src/live.
# Run:  python3 -I out/checks/switch_j_check.py   (from the repo root; or set REPO / REF env vars)
import json, os, re, subprocess

REPO = os.environ.get('REPO', '/Users/abhishekbiyani/Documents/brokersdashboard')
REF = os.environ.get('REF', 'angel-mtf-j')


def load(path):
    try:
        return subprocess.check_output(['git', '-C', REPO, 'show', '%s:%s' % (REF, path)]).decode()
    except Exception:
        return open(os.path.join(REPO, path)).read()


d = json.loads(load('snapshot/db_snapshot_2026-10-23.json'))
f = json.loads(load('snapshot/facts_reviewed_2026-10-23.json'))
jmd, imd = load('out/bridges/j.md'), load('out/bridges/i.md')
n = ag = 0
bad = []


def ok_(name, ok, info=''):
    global n, ag
    n += 1
    ag += bool(ok)
    if not ok:
        bad.append(name)
    print('%-58s %s %s' % (name, 'AGREE' if ok else 'DISAGREE', info))


def dp_of(s):
    s = s.replace(',', '').replace('+', '')
    return len(s.split('.')[1]) if '.' in s else 0


def cmp(name, mine, claim_s):
    """claim_s: the printed string. agree if rel<=1e-6 or within half a unit of the last printed digit."""
    c = float(claim_s.replace(',', '').replace('+', ''))
    tol = max(1e-6 * abs(c), 0.5 * 10 ** (-dp_of(claim_s)) * 1.0001)
    ok = abs(mine - c) <= tol
    ok_(name, ok, 'mine %.9g claim %s' % (mine, claim_s))


# ---------------------------------------------------------------- inputs
YLD = [a['value'] for a in d['assumptions'] if a['key'] == 'mtf_yield'][0]
DAYS = [a['value'] for a in d['assumptions'] if a['key'] == 'mtf_day_basis'][0]
NET = [a['value'] for a in d['assumptions'] if a['key'] == 'mtf_net_factor'][0]
cal = {c['trade_date']: c for c in d['calendar']}
daily = {x['trade_date']: x['value'] for x in d['market_daily'] if x['dataset'] == 'mtf_industry' and x['metric'] == 'book_cr'}
assert all(x['status'] == 'ok' for x in d['market_daily'] if x['dataset'] == 'mtf_industry')
monthly = {x['fy_month']: x['value'] for x in d['monthly'] if x['dataset'] == 'mtf_industry'}
pin = {p['period_key']: p['value'] for p in d['pins'] if p['key'] == 'mtf_angel_book_cr'}
ovr = {p['period_key']: p['value'] for p in d['pins'] if p['key'] == 'mtf_share_override'}
rev = {}
for x in f['facts']:
    if x['status'] == 'reviewed' and x['metric'] == 'avg_funding_book' and x['period_type'] == 'Q':
        assert x['period_key'] not in rev
        rev[x['period_key']] = (x['fact_id'], x['value'])
staged_q = {x['period_key']: x for x in d['facts'] if x['metric'] == 'avg_funding_book' and x['period_type'] == 'Q'}

QS = ['Q1 FY 2025', 'Q2 FY 2025', 'Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026',
      'Q4 FY 2026', 'Q1 FY 2027', 'Q2 FY 2027']
MONTHS = {}
for q in QS:
    fy = q.split(' ', 1)[1]
    k = int(q[1])
    ms = {1: ['April', 'May', 'June'], 2: ['July', 'August', 'September'],
          3: ['October', 'November', 'December'], 4: ['January', 'February', 'March']}[k]
    MONTHS[q] = ['%s %s' % (fy, m) for m in ms]

# ---- check 2: pinned quarters genuinely lack a reviewed fact
print('=== reviewed avg_funding_book (Q) facts in the reviewed snapshot ===')
print(rev)
for q in ('Q1 FY 2025', 'Q2 FY 2025', 'Q3 FY 2025', 'Q4 FY 2025', 'Q3 FY 2026'):
    ok_('no reviewed avg_funding_book fact: ' + q, q not in rev, 'staged seed: %s' % (staged_q[q]['value'] if q in staged_q else 'none'))
for q, fid in (('Q1 FY 2026', 581), ('Q2 FY 2026', 582), ('Q4 FY 2026', 580), ('Q1 FY 2027', 498), ('Q2 FY 2027', 566)):
    ok_('reviewed fact %d present for %s' % (fid, q), rev.get(q, (None,))[0] == fid, rev.get(q))

# ---- industry averages
def dayset(q):
    return sorted(dt for dt in daily if cal[dt]['q_fy'] == q)


def mean(a):
    return sum(a) / len(a)


def ind_after(q):
    ds = dayset(q)
    return mean([daily[x] for x in ds]) if ds else mean([monthly[m] for m in MONTHS[q]])


def ind_before(q):
    if q == 'Q2 FY 2027':           # (h) already put Q2 FY27 on the daily average
        return ind_after(q)
    return mean([monthly[m] for m in MONTHS[q]])


def book_before(q):
    return rev[q][1] / 10 if q == 'Q2 FY 2027' else pin[q]


def book_after(q):
    return rev[q][1] / 10 if q in rev else pin[q]


def share_before(q):
    return ovr[q] if q in ovr else book_before(q) / ind_before(q)


def share_after(q):
    return book_after(q) / ind_after(q)


SB = {q: share_before(q) for q in QS}
SA = {q: share_after(q) for q in QS}
LAST6 = QS[-6:]
PB = mean([SB[q] for q in LAST6])
PA = mean([SA[q] for q in LAST6])

# ---- parse j.md quarter table
print('\n=== quarter table (book, industry average, share; before -> after) ===')
rows = {}
for line in jmd.splitlines():
    c = [x.strip() for x in line.strip().strip('|').split('|')]
    if len(c) == 7 and c[0].startswith('Q') and 'FY' in c[0] and '→' in c[1]:
        rows[c[0]] = c
for q in QS:
    r = rows[q.replace('FY 20', 'FY 20')]
    b0, b1 = [s.strip() for s in r[1].split('→')]
    i0, i1 = [s.strip() for s in r[3].split('→')]
    s0, s1 = [s.strip() for s in r[5].split('→')]
    cmp(q + ' book before', book_before(q), b0)
    cmp(q + ' book after', book_after(q), b1)
    cmp(q + ' industry avg before', ind_before(q), i0)
    cmp(q + ' industry avg after', ind_after(q), i1)
    cmp(q + ' share before', SB[q], s0)
    cmp(q + ' share after', SA[q], s1)
    cmp(q + ' delta share %', (SA[q] / SB[q] - 1) * 100, r[6].replace('%', ''))
    print('   %s: days in daily avg %d; book src %s; share %.9f -> %.9f' % (q, len(dayset(q)), 'fact %d' % rev[q][0] if q in rev else 'pin', SB[q], SA[q]))
r = rows['Q3 FY 2027']
cmp('Q3 FY27 projected share before (mean last 6: Q1FY26..Q2FY27)', PB, r[5].split('→')[0].strip())
cmp('Q3 FY27 projected share after', PA, r[5].split('→')[1].strip())
cmp('Q3 FY27 projected delta %', (PA / PB - 1) * 100, r[6].replace('%', ''))
cmp('Q3 FY27 book before (= projected share x industry avg)', PB * ind_after('Q3 FY 2027'), r[1].split('→')[0].strip())
cmp('Q3 FY27 book after', PA * ind_after('Q3 FY 2027'), r[1].split('→')[1].strip())
cmp('Q3 FY27 industry avg (12 daily days to 19 Oct)', ind_after('Q3 FY 2027'), r[3].split('→')[1].strip())
ok_('Q3 FY25 override 0.0485 present in before, dropped after', ovr.get('Q3 FY 2025') == 0.0485 and abs(SB['Q3 FY 2025'] - 0.0485) < 1e-15 and abs(SA['Q3 FY 2025'] - 4050 / ind_after('Q3 FY 2025')) < 1e-15)
ok_('Q3 FY25 industry before = monthly (102000+80000+84000)/3', abs(ind_before('Q3 FY 2025') - 88666.6666667) < 1e-3)
ok_('Q1-Q2 FY25 have no daily data (monthly kept); Q3 FY25+ do', not dayset('Q1 FY 2025') and not dayset('Q2 FY 2025') and all(dayset(q) for q in QS[2:]))
ok_('Q2 FY27 share unchanged (same book fact 566, same daily avg)', abs(SA['Q2 FY 2027'] - SB['Q2 FY 2027']) < 1e-15 and book_after('Q2 FY 2027') == 7453.0)
ok_('Q2 FY27 not among Q5/Q6 movers: before-state (h) already 7453/daily', ind_before('Q2 FY 2027') == ind_after('Q2 FY 2027'))
# sanity: workbook pins reproduce Excel shares for pre-(j) before state (Q49:Q57 = P / D)
ok_('Q1 FY27 before share = 6133.333/119000 (Excel Q57)', abs(SB['Q1 FY 2027'] - 6133.333333333334 / 119000) < 1e-15)

# ---------------------------------------------------------------- daily MTF revenue and ADR
def share_for(dt, S, P):
    q = cal[dt]['q_fy']
    return S[q] if q in S else P         # Q3 FY27 onward = projected


def rev_day(dt, S, P):
    return share_for(dt, S, P) * daily[dt] * YLD / DAYS


def adr(sel, S, P, mult=1.0):
    ds = [dt for dt in daily if sel(cal[dt])]
    return sum(rev_day(dt, S, P) for dt in ds) / len(ds) * mult, len(ds)


PER = {'FY 2027': lambda c: c['fy'] == 'FY 2027', 'Q2 FY 2027': lambda c: c['q_fy'] == 'Q2 FY 2027',
       'FY 2027 October': lambda c: c['fy_month'] == 'FY 2027 October', 'FY 2026': lambda c: c['fy'] == 'FY 2026',
       'Q3 FY 2026': lambda c: c['q_fy'] == 'Q3 FY 2026', 'FY 2026 October': lambda c: c['fy_month'] == 'FY 2026 October',
       'Q1 FY 2027': lambda c: c['q_fy'] == 'Q1 FY 2027'}


def parse_adr(md):
    out = {}
    for line in md.splitlines():
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) == 6 and c[1] in ('Consolidated', 'Broking', 'MTF', 'MTF (net)', 'F&O', 'Cash', 'Commodities'):
            out[(c[0], c[1])] = c[2:]
    return out


J, I = parse_adr(jmd), parse_adr(imd)
print('\n=== ADR (Rs Cr / trading day, MTF gross) ===')
cons = {}
for per, sel in PER.items():
    mb, nb = adr(sel, SB, PB)
    ma, na = adr(sel, SA, PA)
    cl = J[(per, 'MTF')]
    cmp('%s MTF ADR before (%d days)' % (per, nb), mb, cl[0])
    cmp('%s MTF ADR after' % per, ma, cl[1])
    cmp('%s MTF ADR delta' % per, ma - mb, cl[2])
    cmp('%s MTF ADR delta %%' % per, (ma / mb - 1) * 100, cl[3].replace('%', ''))
    cn = J[(per, 'MTF (net)')]
    cmp('%s MTF net after = 0.45 x gross' % per, NET * ma, cn[1])
    # Broking unchanged: before == after in j, and equal to (i) after.
    bk = J[(per, 'Broking')]
    ok_('%s Broking unchanged j (before==after) and == (i) after' % per,
        bk[0] == bk[1] and float(bk[2]) == 0 and ((per, 'Broking') not in I or I[(per, 'Broking')][1] == bk[0]),
        '%s%s' % (bk[:2], '' if (per, 'Broking') in I else ' ((i) has no row for this period)'))
    brk = float(bk[0])
    cc = J[(per, 'Consolidated')]
    cmp('%s Consolidated before = Broking + MTF' % per, brk + mb, cc[0])
    cmp('%s Consolidated after = Broking + MTF' % per, brk + ma, cc[1])
    cmp('%s Consolidated delta' % per, ma - mb, cc[2])
    cmp('%s Consolidated delta %%' % per, ((brk + ma) / (brk + mb) - 1) * 100, cc[3].replace('%', ''))
    # before-state MTF must equal (i) 'after' MTF where (i) reports it
    if (per, 'MTF') in I:
        cmp('%s MTF before == bridge (i) after' % per, mb, I[(per, 'MTF')][1])
    cons[per] = (brk + mb, brk + ma)
    print('   %s: MTF %.9f -> %.9f ; Consolidated %.9f -> %.9f' % (per, mb, ma, brk + mb, brk + ma))

# ---------------------------------------------------------------- daily rows changed
print('\n=== daily rows ===')
ch = [dt for dt in daily if abs(rev_day(dt, SA, PA) - rev_day(dt, SB, PB)) > 1e-12]
rat = [rev_day(dt, SA, PA) / rev_day(dt, SB, PB) for dt in daily]
m = re.search(r'\| MTF \| (\d+) \| (\d+) \| (\S+) \| (\S+) \| (\S+) \| (\S+) \|', jmd)
ok_('MTF daily rows 507', len(daily) == int(m.group(1)), len(daily))
ok_('MTF daily rows changed 442 (all but Q2 FY27 = 65 days)', len(ch) == int(m.group(2)) and len(daily) - len(dayset('Q2 FY 2027')) == 442, len(ch))
ok_('first / last changed date', (min(ch), max(ch)) == (m.group(3), m.group(4)), (min(ch), max(ch)))
cmp('ratio min', min(rat), m.group(5))
cmp('ratio max', max(rat), m.group(6))

print('\n%d checked, %d agree, %d disagree' % (n, ag, n - ag))
if bad:
    print('DISAGREE:', bad)
