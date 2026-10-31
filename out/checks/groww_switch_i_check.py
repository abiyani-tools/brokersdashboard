#!/usr/bin/env python3
"""Groww switch g-i ("MTF from Groww's own book"): independent recompute of
out/bridges/groww_i.md and the g-i section of out/groww/backtest_ir_switches.md.

Stdlib only (json, math, re, os, subprocess). Nothing from src/engine or src/live is read.
Inputs: snapshot/*.json (+ the saved page out/groww_ir/*.html for the unit check, if present),
the committed bridges / backtest text (read from the working tree, else `git show groww-ir:<path>`).
Run:  python out/checks/groww_switch_i_check.py        (writes out/checks/groww_switch_i_items.csv)
"""
import json, math, os, re, subprocess, sys, csv
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
BRANCH = 'groww-ir'


def text(p):
    fp = os.path.join(ROOT, p)
    if os.path.exists(fp):
        with open(fp, encoding='utf-8') as fh:
            return fh.read()
    return subprocess.check_output(['git', 'show', '%s:%s' % (BRANCH, p)], cwd=ROOT).decode('utf-8')


def J(p):
    return json.loads(text(p))


DB = J('snapshot/db_snapshot_2026-10-23.json')
IR = J('snapshot/groww_ir_2026-10-31.json')['rows']
FR = J('snapshot/groww_facts_reviewed_2026-10-31.json')['facts']
GS = J('snapshot/groww_snapshot_2026-10-23.json')['facts']     # workbook facts: Q2/Q3 FY26 total income only
BR_I = text('out/bridges/groww_i.md')
BR_F = text('out/bridges/groww_f.md')
BR_G = text('out/bridges/groww_g.md')
BT = text('out/groww/backtest_ir_switches.md')

YIELD = 0.1495   # facts 10102/10103 (assumptions mtf_yield)

# ------------------------------------------------------------------ calendar
CAL = {c['trade_date']: c for c in DB['calendar']}
EQ = sorted(d for d, c in CAL.items() if c['is_equity_day'])
FYDAYS = {}
for d in EQ:
    FYDAYS[CAL[d]['fy']] = FYDAYS.get(CAL[d]['fy'], 0) + 1
# FY27 incomplete: g-f convention uses FY26's count (stated in the g-f bridge)
FYBASIS = dict(FYDAYS)
FYBASIS['FY 2027'] = FYDAYS['FY 2026']
ASOF = EQ[-1]
START = '2024-10-01'            # first day of the industry-book series; g-i covers START..ASOF
OWN_DAYS = [d for d in EQ if START <= d <= ASOF]
IND = {m['trade_date']: m['value'] for m in DB['market_daily'] if m['dataset'] == 'mtf_industry'}   # Rs Cr
IND_DAYS = sorted(IND)

QS = ['Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026',
      'Q1 FY 2027', 'Q2 FY 2027', 'Q3 FY 2027']
REPORTED = QS[:-1]
OPEN_Q = QS[-1]


def qend(q):
    """calendar end date of a fiscal quarter label 'Qn FY yyyy'."""
    n = int(q[1]); fy = int(q.split()[-1])
    return {1: date(fy - 1, 6, 30), 2: date(fy - 1, 9, 30), 3: date(fy - 1, 12, 31), 4: date(fy, 3, 31)}[n]


def prevq(q):
    n = int(q[1]); fy = int(q.split()[-1])
    return 'Q4 FY %d' % (fy - 1) if n == 1 else 'Q%d FY %d' % (n - 1, fy)


def D(s):
    y, m, d = s.split('-')
    return date(int(y), int(m), int(d))


def qdays(q, days):
    return [d for d in days if CAL[d]['q_fy'] == q]


# ------------------------------------------------------------------ inputs: own book (page) and disclosed revenue
LEVEL = {}                  # quarter -> Rs Mn
OPENROW = None
for r in IR:
    if r['metric'] == 'ir_mtf_net_book':
        LEVEL[r['period_key']] = r['value']
        if r['is_qtd']:
            OPENROW = r
assert OPENROW['period_key'] == OPEN_Q
OPEN_LEVEL = OPENROW['value']      # 40,848.931 Rs Mn (QTD, covers_through 2026-10-30)


def fact(metric, q, seg=''):
    for f in FR:
        if f['metric'] == metric and f['period_key'] == q and (f['segment'] or '') == seg:
            return f
    return None


def tincome(q):
    f = fact('total_income', q)
    if f:
        return f['value'], 'reviewed fact %d' % f['fact_id']
    for g in GS:
        if g['metric'] == 'total_income' and g['period_key'] == q:
            return g['value'], 'workbook snapshot (derived)'
    raise KeyError(q)


def disclosed_cr(q):
    """MTF mix x total income (Rs Mn) / 10 -> Rs Cr; restated mix where it exists, else the original classification."""
    f = fact('revmix_mtf', q) or fact('revmix_mtf', q, 'cls_pre_q2fy27')
    ti, src = tincome(q)
    return f['value'] * ti / 10.0, f['value'], ti, src


DISC = {q: disclosed_cr(q)[0] for q in REPORTED}


# ------------------------------------------------------------------ own book path (Rs Cr)
def book_day(d, level_override=None):
    """Own book (Rs Cr) for an equity day d.
    closed quarter: linear interpolation in calendar days between the two quarter-end levels;
    open quarter  : the latest level held flat."""
    q = CAL[d]['q_fy']
    if q == OPEN_Q:
        return OPEN_LEVEL / 10.0
    e1 = qend(q); e0 = qend(prevq(q))
    f = (D(d) - e0).days / float((e1 - e0).days)
    l0 = LEVEL[prevq(q)]; l1 = LEVEL[q]
    return (l0 + f * (l1 - l0)) / 10.0


def mean(x):
    x = list(x)
    return sum(x) / len(x)


def raw_rev(d):
    """daily revenue at k = 1, Rs Cr"""
    return book_day(d) * YIELD / FYBASIS[CAL[d]['fy']]


K = {}
for q in REPORTED:
    K[q] = DISC[q] / sum(raw_rev(d) for d in qdays(q, OWN_DAYS))
K[OPEN_Q] = 1.0


def own_daily(d):
    return K[CAL[d]['q_fy']] * raw_rev(d)


# ------------------------------------------------------------------ industry-book (g-f) daily, "before"
SHARE = {}
for q in REPORTED:
    rows = qdays(q, IND_DAYS)
    SHARE[q] = DISC[q] / sum(IND[d] * YIELD / FYBASIS[CAL[d]['fy']] for d in rows)
SHARE[OPEN_Q] = SHARE['Q2 FY 2027']      # g-f: the open quarter carries the last reported share


def gf_daily(d):
    q = CAL[d]['q_fy']
    return SHARE[q] * IND[d] * YIELD / FYBASIS[CAL[d]['fy']]


# ------------------------------------------------------------------ period averages (ADR)
def adr(daily, days, sel):
    v = [daily(d) for d in days if sel(d)]
    return mean(v), len(v)


# ------------------------------------------------------------------ bridge parsing helpers
def tables(md):
    """yield (heading, [rows as lists of cells]) for each markdown table; heading = last non-table text line above."""
    out = []
    lines = md.split('\n')
    last = ''
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('|') and i + 1 < len(lines) and re.match(r'^\|[\s:|-]+\|$', lines[i + 1]):
            rows = []
            hdr = [c.strip() for c in ln.strip().strip('|').split('|')]
            j = i + 2
            while j < len(lines) and lines[j].startswith('|'):
                rows.append([c.strip() for c in lines[j].strip().strip('|').split('|')])
                j += 1
            out.append((last, hdr, rows))
            i = j
            continue
        if ln.strip():
            last = ln.strip()
        i += 1
    return out


def num(s):
    s = s.replace(',', '').replace('%', '').replace('+', '').replace('−', '-').replace('—', '').strip()
    return float(s) if s not in ('', '-') else None


def dec(s):
    """decimals printed in s"""
    s = s.replace(',', '').replace('%', '').replace('+', '').strip()
    return len(s.split('.')[1]) if '.' in s else 0


ITEMS = []     # (id, kind, desc, mine, bridge_str, tol_abs, rel_diff, verdict)


def cmp_item(kind, desc, mine, bridge_str, scale=1.0):
    """compare mine*scale with the printed bridge value to half a unit of its last printed digit"""
    b = num(bridge_str)
    if b is None:
        ITEMS.append((kind, desc, mine, bridge_str, None, None, 'n/a'))
        return
    m = mine * scale
    tol = 0.5 * 10 ** (-dec(bridge_str)) + 1e-12
    diff = abs(m - b)
    rel = diff / abs(b) if b else diff
    ok = diff <= tol
    ITEMS.append((kind, desc, m, bridge_str, tol, rel, 'agree' if ok else 'DISAGREE'))


# ------------------------------------------------------------------ CHECK 1: k and ties (reported quarters)
tie_rows = []
for q in REPORTED:
    tot = sum(own_daily(d) for d in qdays(q, OWN_DAYS))
    rel = abs(tot - DISC[q]) / DISC[q]
    tie_rows.append((q, K[q], DISC[q], tot, rel, len(qdays(q, OWN_DAYS))))
    ITEMS.append(('tie', '%s daily MTF revenue sums to disclosed (rel diff, tol 1e-9)' % q, rel, '0', 1e-9, rel,
                  'agree' if rel <= 1e-9 else 'DISAGREE'))

# bridge per-quarter table
qt = [t for t in tables(BR_I) if 'Own avg book' in t[1]][0]
bq = {}
for r in qt[2]:
    bq[r[0]] = r
for q in QS:
    r = bq[q]
    days = qdays(q, OWN_DAYS)
    own_avg = mean(book_day(d) for d in days)
    ind_rows = qdays(q, IND_DAYS)
    ind_avg = mean(IND[d] for d in ind_rows)
    rev_k1 = sum(raw_rev(d) for d in days)
    cmp_item('qtab', '%s days' % q, len(days), r[2])
    cmp_item('qtab', '%s own avg book Rs Cr' % q, own_avg, r[3])
    cmp_item('qtab', '%s industry avg book Rs Cr' % q, ind_avg, r[4])
    cmp_item('qtab', '%s k' % q, K[q], r[5])
    cmp_item('qtab', '%s quarter revenue at k=1 Rs Cr' % q, rev_k1, r[6])
    if q != OPEN_Q:
        cmp_item('qtab', '%s disclosed Rs Cr' % q, DISC[q], r[7])
    cmp_item('qtab', '%s book after k Rs Cr' % q, K[q] * own_avg, r[8])
    cmp_item('qtab', '%s share of industry (after) %%' % q, 100 * K[q] * own_avg / ind_avg, r[9])

m = re.search(r'interpolated (\d+), latest (\d+)', BR_I)
n_interp = sum(1 for d in OWN_DAYS if CAL[d]['q_fy'] != OPEN_Q)
n_latest = sum(1 for d in OWN_DAYS if CAL[d]['q_fy'] == OPEN_Q)
cmp_item('qtab', 'book basis: interpolated days', n_interp, m.group(1))
cmp_item('qtab', 'book basis: latest-level days', n_latest, m.group(2))
cmp_item('qtab', 'days covered by g-i (509 to as-of %s)' % ASOF, len(OWN_DAYS), '509')

# ------------------------------------------------------------------ CHECK 2 / 3: ADRs and consolidated
SEL = {
    'FY 2027': lambda d: CAL[d]['fy'] == 'FY 2027',
    'Q2 FY 2027': lambda d: CAL[d]['q_fy'] == 'Q2 FY 2027',
    'FY 2027 October': lambda d: CAL[d]['fy_month'] == 'FY 2027 October',
    'FY 2026': lambda d: CAL[d]['fy'] == 'FY 2026',
    'FY 2026 October': lambda d: CAL[d]['fy_month'] == 'FY 2026 October',
}
MY = {}     # (period) -> dict(before, after, n_before, n_after)
for p, sel in SEL.items():
    b, nb = adr(gf_daily, IND_DAYS, sel)
    a, na = adr(own_daily, OWN_DAYS, sel)
    MY[p] = dict(before=b, after=a, nb=nb, na=na)

# main ADR table of g-i bridge
adr_t = [t for t in tables(BR_I) if t[1][:3] == ['Period', 'Panel', 'Before'] and 'Δ' in t[1]][0]
BR_ROWS = {(r[0], r[1]): r for r in adr_t[2]}
BROKING = {p: num(BR_ROWS[(p, 'Broking')][2]) for p in SEL}        # unchanged by g-i, taken from the bridge (input)
BROKING_AFTER = {p: num(BR_ROWS[(p, 'Broking')][3]) for p in SEL}
for p in SEL:
    ITEMS.append(('input', 'Broking %s: bridge before == after (g-i leaves Broking alone)' % p, BROKING[p], '%.6f' % BROKING_AFTER[p],
                  1e-12, abs(BROKING[p] - BROKING_AFTER[p]), 'agree' if abs(BROKING[p] - BROKING_AFTER[p]) < 1e-12 else 'DISAGREE'))
    r = BR_ROWS[(p, 'MTF')]
    cmp_item('ADR', 'MTF %s before (g-f path)' % p, MY[p]['before'], r[2])
    cmp_item('ADR', 'MTF %s after (g-i)' % p, MY[p]['after'], r[3])
    cmp_item('ADR', 'MTF %s delta' % p, MY[p]['after'] - MY[p]['before'], r[4])
    cmp_item('ADR', 'MTF %s delta %%' % p, 100 * (MY[p]['after'] / MY[p]['before'] - 1), r[5])
    rc = BR_ROWS[(p, 'Consolidated')]
    cb = BROKING[p] + MY[p]['before']
    ca = BROKING[p] + MY[p]['after']
    cmp_item('ADR', 'Consolidated %s before' % p, cb, rc[2])
    cmp_item('ADR', 'Consolidated %s after' % p, ca, rc[3])
    cmp_item('ADR', 'Consolidated %s delta' % p, ca - cb, rc[4])
    cmp_item('ADR', 'Consolidated %s delta %%' % p, 100 * (ca / cb - 1), rc[5])

# headline Consolidated table (first table of the bridge)
head_t = [t for t in tables(BR_I) if t[1] == ['Period', 'Before', 'After', 'Δ %']]
for hd, hh, rows in head_t[:1]:        # first table = abcdefgh -> abcdefghi
    for r in rows:
        p = r[0]
        if p in MY:
            cb = BROKING[p] + MY[p]['before']; ca = BROKING[p] + MY[p]['after']
            cmp_item('headline', '%s Consolidated before' % p, cb, r[1])
            cmp_item('headline', '%s Consolidated after' % p, ca, r[2])
            cmp_item('headline', '%s Consolidated delta %%' % p, 100 * (ca / cb - 1), r[3])

# "g-i on top of g-a..g-g alone" table: Broking = g-f bridge Broking (g-f's after has no g-h; it equals abcdefg Broking
# only through FY27 / Q2 / Oct values below, which the g-f bridge prints)
alt = [t for t in tables(BR_I) if 'without g-h' in t[0] or 'g-a..g-g alone' in t[0]]
ff = {(r[0], r[1]): r for r in [t for t in tables(BR_F) if t[1][:3] == ['Period', 'Panel', 'Before']][0][2]}
gg = {(r[0], r[1]): r for r in [t for t in tables(BR_G) if t[1][:3] == ['Period', 'Panel', 'Before']][0][2]}
if alt:
    for r in alt[0][2]:
        p = r[0]
        if p in MY:
            brk_f = num(gg[(p, 'Broking')][3])       # g-g bridge, 'after' = switches abcdefg (Broking before g-h/g-i)
            cb = brk_f + MY[p]['before']; ca = brk_f + MY[p]['after']
            cmp_item('alt', '(no g-h) %s Consolidated before' % p, cb, r[1])
            cmp_item('alt', '(no g-h) %s Consolidated after' % p, ca, r[2])
            cmp_item('alt', '(no g-h) %s Consolidated delta %%' % p, 100 * (ca / cb - 1), r[3])

# MTF 'before' also equals the g-f bridge's MTF after
for p in ('FY 2027', 'Q2 FY 2027', 'FY 2027 October', 'FY 2026', 'FY 2026 October'):
    if (p, 'MTF') in ff:
        cmp_item('ADR', 'MTF %s before vs g-f bridge MTF after' % p, MY[p]['before'], ff[(p, 'MTF')][3])

# parameters that moved: Groww average book Q1 FY27 before (g-f: 3,469.39 = 59 industry rows), Q3 FY27 after
pm = [t for t in tables(BR_I) if t[1][:3] == ['Segment', 'Quantity', 'Quarter']][0][2]
for r in pm:
    if r[1] == 'Groww average book Rs Cr' and r[2] == 'Q1 FY 2027':
        rows = qdays('Q1 FY 2027', IND_DAYS)
        before_book = DISC['Q1 FY 2027'] / (YIELD * len(rows) / FYBASIS['FY 2027'])   # g-f: share x avg industry book
        cmp_item('param', 'Q1 FY27 Groww avg book before (disclosed / (yield x rows / FY days))', before_book, r[3])
        after_book = K['Q1 FY 2027'] * mean(book_day(d) for d in qdays('Q1 FY 2027', OWN_DAYS))
        cmp_item('param', 'Q1 FY27 Groww avg book after (k x own avg)', after_book, r[4])
    if r[1] == 'Groww average book Rs Cr' and r[2] == 'Q3 FY 2027':
        cmp_item('param', 'Q3 FY27 Groww avg book after', OPEN_LEVEL / 10.0, r[4])
    if r[1].startswith('g-i calibration k'):
        cmp_item('param', 'k %s' % r[2], K[r[2]], r[4])

# daily-rows-changed table: ratio min/max of after/before on the 507 overlapping days
ch = [t for t in tables(BR_I) if t[1][:3] == ['Segment', 'Days', 'Changed']][0][2]
mtf_row = [r for r in ch if r[0].startswith('MTF')][0]
ratios = [own_daily(d) / gf_daily(d) for d in IND_DAYS]
changed = sum(1 for d in IND_DAYS if abs(own_daily(d) - gf_daily(d)) > 1e-15)
cmp_item('daily', 'MTF rows in before series', len(IND_DAYS), mtf_row[1])
cmp_item('daily', 'MTF rows changed', changed, mtf_row[2])
cmp_item('daily', 'MTF ratio min', min(ratios), mtf_row[5])
cmp_item('daily', 'MTF ratio max', max(ratios), mtf_row[6])
added = [d for d in OWN_DAYS if d not in IND]
ITEMS.append(('daily', 'days added by g-i (not in industry series)', len(added), '2: ' + ', '.join(added), None, None,
              'agree' if added == ['2026-04-08', '2026-10-21'] else 'DISAGREE'))
first_last = (IND_DAYS[0], IND_DAYS[-1])
ITEMS.append(('daily', 'MTF first/last changed day', 0, '%s / %s' % first_last, None, None,
              'agree' if (mtf_row[3], mtf_row[4]) == first_last else 'DISAGREE'))

# ------------------------------------------------------------------ CHECK 2b: open-quarter stand-alone numbers
open_daily = OPEN_LEVEL / 10.0 * YIELD / FYBASIS['FY 2027']
OPEN_INFO = dict(level_rsmn=OPEN_LEVEL, level_cr=OPEN_LEVEL / 10.0, per_day=open_daily, days=len(qdays(OPEN_Q, OWN_DAYS)),
                 quarter_total=open_daily * len(qdays(OPEN_Q, OWN_DAYS)))

# ------------------------------------------------------------------ CHECK 4: backtest
def path_sum(q):
    return sum(raw_rev(d) for d in qdays(q, OWN_DAYS))


def qend_pred(q):
    return LEVEL[q] / 10.0 * YIELD * len(qdays(q, OWN_DAYS)) / FYBASIS[CAL[qdays(q, OWN_DAYS)[0]]['fy']]


def flat_pred(q):
    return LEVEL[prevq(q)] / 10.0 * YIELD * len(qdays(q, OWN_DAYS)) / FYBASIS[CAL[qdays(q, OWN_DAYS)[0]]['fy']]


def ind_pred_days(q):
    """literal reading of the backtest text: previous share carried x industry AVERAGE book x 14.95% x calendar days / FY days"""
    rows = qdays(q, IND_DAYS)
    return SHARE[prevq(q)] * mean(IND[d] for d in rows) * YIELD * len(qdays(q, OWN_DAYS)) / FYBASIS[CAL[rows[0]]['fy']]


def ind_pred(q):
    """what g-f actually does: previous share x sum over the quarter's industry-book ROWS of book x 14.95% / FY days
    (a day without an industry row, 2026-04-08, earns nothing: 59 rows in Q1 FY27, not 60)"""
    rows = qdays(q, IND_DAYS)
    return SHARE[prevq(q)] * sum(IND[d] * YIELD / FYBASIS[CAL[d]['fy']] for d in rows)


PATH = {q: path_sum(q) for q in REPORTED}
KP = {q: DISC[q] / PATH[q] for q in REPORTED}
METH = {}
for q in REPORTED:
    METH[q] = {
        'own qtr-end': qend_pred(q),
        'own path k=1': PATH[q],
        'own path x prev k': PATH[q] * KP[prevq(q)] if prevq(q) in KP else None,
        'prev qtr-end flat': flat_pred(q),
        'industry': ind_pred(q) if prevq(q) in SHARE and qdays(q, IND_DAYS) and prevq(q) in REPORTED else None,
    }
IND_DAYS_VARIANT = {q: ind_pred_days(q) for q in REPORTED[1:]}
ERR = {q: {k: (None if v is None else v / DISC[q] - 1) for k, v in METH[q].items()} for q in REPORTED}

bt_rows = None
for t in tables(BT):
    if t[1][:3] == ['Quarter', 'Days', 'Own book at qtr end Rs Cr']:
        bt_rows = {r[0]: r for r in t[2]}
col = {'qtr-end level': 2, 'disclosed': 3, 'own qtr-end': 4, 'own path k=1': 6, 'own path x prev k': 8,
       'prev qtr-end flat': 10, 'industry': 12, 'k': 14}
for q in REPORTED:
    r = bt_rows[q]
    cmp_item('bt', '%s days' % q, len(qdays(q, OWN_DAYS)), r[1])
    cmp_item('bt', '%s own book at qtr end Rs Cr' % q, LEVEL[q] / 10.0, r[2])
    cmp_item('bt', '%s disclosed' % q, DISC[q], r[3])
    cmp_item('bt', '%s k (disclosed / path)' % q, KP[q], r[14])
    for meth, c in (('own qtr-end', 4), ('own path k=1', 6), ('own path x prev k', 8), ('prev qtr-end flat', 10), ('industry', 12)):
        if METH[q][meth] is None:
            ITEMS.append(('bt', '%s %s n/a' % (q, meth), 0, r[c], None, None, 'agree' if r[c].strip() in ('—', '') else 'DISAGREE'))
            continue
        cmp_item('bt', '%s %s prediction' % (q, meth), METH[q][meth], r[c])
        cmp_item('bt', '%s %s error %%' % (q, meth), 100 * ERR[q][meth], r[c + 1])

for q in REPORTED[1:]:
    rel = abs(IND_DAYS_VARIANT[q] / METH[q]['industry'] - 1)
    ITEMS.append(('info', '%s industry prediction, literal "x days" reading vs rows used by the bridge' % q,
                  IND_DAYS_VARIANT[q], '%.2f' % METH[q]['industry'], None, rel, 'same' if rel < 1e-9 else 'DIFFERS (explained: 60 days vs 59 rows)'))

# summary
sets = [
    ('Q4 FY25..Q2 FY27 (7, every method)', REPORTED[1:], ['industry', 'own qtr-end', 'own path k=1', 'prev qtr-end flat', 'own path x prev k']),
    ('Q1 FY26..Q2 FY27 (6, mix to 0.1pp)', REPORTED[2:], ['industry', 'own qtr-end', 'own path k=1', 'prev qtr-end flat', 'own path x prev k']),
    ('Q3 FY25..Q2 FY27 (8, own book only)', REPORTED, ['own qtr-end', 'own path k=1', 'prev qtr-end flat']),
]
names = {'industry': 'industry book (g-f)', 'own qtr-end': 'own book, quarter-end', 'own path k=1': 'own book, g-i path (k=1)',
         'prev qtr-end flat': 'own book, previous quarter-end held flat', 'own path x prev k': 'own book, path x previous k'}
bt_sum = {}
for t in tables(BT):
    if t[1] == ['Quarters', 'Method', 'n', 'Mean (signed)', 'Mean abs', 'Max abs']:
        for r in t[2]:
            bt_sum[(r[0], r[1])] = r
SUMMARY = []
for label, qs, ms in sets:
    for m in ms:
        e = [ERR[q][m] for q in qs]
        sm, sa, mx = 100 * mean(e), 100 * mean(abs(x) for x in e), 100 * max(abs(x) for x in e)
        SUMMARY.append((label, m, len(e), sm, sa, mx))
        r = bt_sum[(label, names[m])]
        cmp_item('bt-sum', '%s | %s n' % (label, m), len(e), r[2])
        cmp_item('bt-sum', '%s | %s mean signed %%' % (label, m), sm, r[3])
        cmp_item('bt-sum', '%s | %s mean abs %%' % (label, m), sa, r[4])
        cmp_item('bt-sum', '%s | %s max abs %%' % (label, m), mx, r[5])

# ------------------------------------------------------------------ CHECK 5: units
page_vals = {}
html = None
for cand in ('out/groww_ir/investor-relations_2026-10-31.html',):
    fp = os.path.join(ROOT, cand)
    if os.path.exists(fp):
        html = open(fp, encoding='utf-8', errors='replace').read().replace('\\"', '"')
UNIT = {}
if html:
    i = html.find('"id":"mtf_net_book"')
    seg = html[i:i + 1800]
    for lab, v in re.findall(r'\{"label":"(Q\d FY\d\d)","value":([0-9.]+)\}', seg):
        page_vals[lab] = float(v)
    UNIT['page_Q2FY27_raw'] = page_vals.get('Q2 FY27')
    UNIT['page_Q3FY27_raw'] = page_vals.get('Q3 FY27')
    mm = re.search(r'"currentValue":"([^"]+)","rawCurrentValue":(\d+)', seg)
    UNIT['display_current'] = mm.group(1) if mm else None
    UNIT['rawCurrentValue'] = float(mm.group(2)) if mm else None
    for lab, v in page_vals.items():
        ql = 'Q%s FY 20%s' % (lab[1], lab[-2:])
        ok = abs(v / 100.0 - LEVEL[ql]) < 1e-6
        ITEMS.append(('units', 'page %s raw %.1f / 100 == snapshot Rs Mn %.3f' % (lab, v, LEVEL[ql]), v / 100.0, '%.3f' % LEVEL[ql],
                      1e-6, abs(v / 100.0 - LEVEL[ql]), 'agree' if ok else 'DISAGREE'))
hb = fact('mtf_book', 'Q2 FY 2027')['value']        # KPI handbook closing funded book, Rs Mn
q2 = LEVEL['Q2 FY 2027']
UNIT['handbook_Q2FY27'] = hb
UNIT['snapshot_Q2FY27'] = q2
UNIT['rel_diff_vs_handbook'] = abs(q2 - hb) / hb
ITEMS.append(('units', 'Q2 FY27 own book (page/100, Rs Mn) vs KPI-handbook 43,514 (tol 0.1%)', q2, '%.0f' % hb, 0.001 * hb,
              abs(q2 - hb) / hb, 'agree' if abs(q2 - hb) / hb < 1e-3 else 'DISAGREE'))
h1 = fact('mtf_book', 'Q1 FY 2026')['value']
ITEMS.append(('units', 'Q1 FY26 own book (Rs Mn) vs facts handbook 10,357.69 (tol 0.1%)', LEVEL['Q1 FY 2026'], '%.2f' % h1, 0.001 * h1,
              abs(LEVEL['Q1 FY 2026'] - h1) / h1, 'agree' if abs(LEVEL['Q1 FY 2026'] - h1) / h1 < 1e-3 else 'DISAGREE'))

# ------------------------------------------------------------------ output
def main():
    ITEMS_C = [it for it in ITEMS if it[0] != 'info']
    n = len(ITEMS_C)
    agree = sum(1 for it in ITEMS_C if it[6] == 'agree')
    print('items: %d  agree: %d  disagree: %d' % (n, agree, n - agree))
    for it in ITEMS:
        if it[6] != 'agree' and (it[0] != 'info' or it[6].startswith('DIFFERS')):
            print('  %-8s %s | mine=%s bridge=%s' % (it[0], it[1], it[2], it[3]))
    kinds = {}
    for it in ITEMS:
        kinds.setdefault(it[0], [0, 0])
        kinds[it[0]][0] += 1
        kinds[it[0]][1] += 1 if it[6] == 'agree' else 0
    print('by kind:', {k: '%d/%d' % (v[1], v[0]) for k, v in kinds.items()})
    print('k:', {q: round(K[q], 6) for q in QS})
    print('open quarter: level %.3f Rs Mn = %.4f Cr; daily %.6f Cr x %d days = %.4f Cr' % (
        OPEN_INFO['level_rsmn'], OPEN_INFO['level_cr'], OPEN_INFO['per_day'], OPEN_INFO['days'], OPEN_INFO['quarter_total']))
    for p in SEL:
        print('%-18s MTF before %.6f after %.6f (days %d/%d)  Cons before %.6f after %.6f  d%% %.4f' % (
            p, MY[p]['before'], MY[p]['after'], MY[p]['nb'], MY[p]['na'], BROKING[p] + MY[p]['before'],
            BROKING[p] + MY[p]['after'], 100 * (MY[p]['after'] / MY[p]['before'] - 1)))
    for s in SUMMARY:
        print('%-40s %-20s n=%d mean %+.2f%% abs %.2f%% max %.2f%%' % s)
    print('units:', UNIT)
    with open(os.path.join(HERE, 'groww_switch_i_items.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['kind', 'item', 'mine', 'bridge_printed', 'tolerance_abs', 'rel_diff', 'verdict'])
        for it in ITEMS:
            w.writerow(it)
    return 0 if agree == n else 1


if __name__ == '__main__':
    sys.exit(main())
