# Independent recompute of MOSL switch m-g (FY24 quarters Q2-Q4 FY24).
# stdlib json/math/csv/re/os + openpyxl (only for the data-book re-reads). Run from the worktree root:
#   python3 out/checks/mosl_switch_g_check.py
# Nothing under src/engine/ or src/live/ is read or imported. No database is touched.
# Inputs: docs/MOSL_ADR_Methodology.md s3-s4 (rules), docs/MOSL_LIVE_SPEC.md (m-g), out/bridges/mosl_g.md (claims),
#   snapshot/mosl_facts_fy24_candidates_2026-11-03.json, snapshot/mosl_facts_reviewed_2026-11-02.json,
#   snapshot/mosl_lake_2026-11-03.json, snapshot/db_snapshot_2026-11-03.json, the Q4 FY26 data book (xlsx).
import json, math, csv, os, re, sys, datetime, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))


def J(p):
    with open(os.path.join(ROOT, p)) as fh:
        return json.load(fh)


FACTS24 = J('snapshot/mosl_facts_fy24_candidates_2026-11-03.json')['facts']
FACTS25 = J('snapshot/mosl_facts_reviewed_2026-11-02.json')['facts']
LAKE = J('snapshot/mosl_lake_2026-11-03.json')['series']
DB = J('snapshot/db_snapshot_2026-11-03.json')
BR = open(os.path.join(ROOT, 'out/bridges/mosl_g.md')).read()

ITEMS = []   # (id, kind, item, mine, bridge, reldiff, tol, verdict, note)


def rel(a, b):
    if a is None or b is None:
        return None
    if a == b:
        return 0.0
    return abs(a - b) / max(abs(a), abs(b), 1e-300)


def add(kind, item, mine, bridge, tol=1e-6, note='', printed=None):
    """Agree = relative diff <= tol, or, when the bridge prints `printed` (a string), the value rounds to what is printed."""
    r = rel(mine, bridge)
    ok = r is not None and r <= tol
    t = tol
    if printed is not None and mine is not None:
        s = printed.replace(',', '').replace('%', '').replace('+', '').strip()
        dec = len(s.split('.')[1]) if '.' in s else 0
        half = 0.5 * 10 ** (-dec)
        if abs(mine - bridge) <= half * (1 + 1e-9):
            ok = True
            t = half
    ITEMS.append([len(ITEMS) + 1, kind, item, mine, bridge, r, t, 'agree' if ok else 'DISAGREE', note])
    return ok


def add_bool(kind, item, mine, bridge, note=''):
    ok = (mine == bridge)
    ITEMS.append([len(ITEMS) + 1, kind, item, mine, bridge, None, None, 'agree' if ok else 'DISAGREE', note])
    return ok


def num(s):
    s = s.strip().replace(',', '').replace('%', '').replace('+', '')
    if s in ('', '—', '-'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def md_tables(text):
    lines = text.split('\n')
    out, i, last = [], 0, ''
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('|') and i + 1 < len(lines) and re.match(r'^\|[\s:|-]+\|$', lines[i + 1]):
            hdr = [c.strip() for c in ln.strip().strip('|').split('|')]
            rows = []
            i += 2
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            out.append((last, hdr, rows))
            continue
        if ln.strip():
            last = ln.strip()
        i += 1
    return out


TABLES = md_tables(BR)


def table(first_hdrs):
    for last, hdr, rows in TABLES:
        if hdr[:len(first_hdrs)] == first_hdrs:
            return rows
    raise KeyError(first_hdrs)


# ------------------------------------------------------------------ calendar and series
CAL = {c['trade_date']: c for c in DB['calendar']}
LASTCAL = max(CAL)                       # 2026-10-21
MONTHS = ['April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'January',
          'February', 'March']


def fy_of(d):
    y, m = int(d[:4]), int(d[5:7])
    return y + 1 if m >= 4 else y


def qlabel(d):
    if d in CAL:
        return CAL[d]['q_fy']
    m = int(d[5:7])
    qn = ((m - 4) % 12) // 3 + 1
    return 'Q%d FY %d' % (qn, fy_of(d))


def mlabel(d):
    if d in CAL:
        return CAL[d]['fy_month']
    return 'FY %d %s' % (fy_of(d), MONTHS[(int(d[5:7]) - 4) % 12])


def is_special(d):
    return bool(d in CAL and CAL[d]['special_session'])


LK = {k: {r[0]: r[1] for r in v if r[2] == 'ok'} for k, v in LAKE.items()}
# F&O key: NSE index options + BSE contracts (raw count); cash key: NSE + BSE turnover (Rs Cr)
S = {d: LK['nse_fo/io_contracts'][d] + LK['bse_fo/contracts'][d] for d in LK['nse_fo/io_contracts']
     if d in LK['bse_fo/contracts'] and d in CAL and d <= LASTCAL}
K = {d: LK['nse_cash/turnover_cr'][d] + LK['bse_cash/turnover_cr'][d] for d in LK['nse_cash/turnover_cr']
     if d in LK['bse_cash/turnover_cr'] and d in CAL and d <= LASTCAL}
MCX = {m['trade_date']: m['value'] for m in DB['market_daily'] if m['dataset'] == 'mcx' and m['status'] == 'ok'}
NSEOPT = {d: LK['nse_fo/io_contracts'][d] for d in S}
BSEOPT = {d: LK['bse_fo/contracts'][d] for d in S}

# ------------------------------------------------------------------ facts
FACT = {}
for f in FACTS24 + FACTS25:
    FACT[(f['metric'], f['period_key'])] = f
Q24 = ['Q2 FY 2024', 'Q3 FY 2024', 'Q4 FY 2024']
Q25 = ['Q1 FY 2025', 'Q2 FY 2025', 'Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026',
       'Q4 FY 2026', 'Q1 FY 2027', 'Q2 FY 2027']
SEG = ['fo', 'cash', 'comm']
SEGNAME = {'fo': 'F&O', 'cash': 'Cash', 'comm': 'Commodities'}
GM = {'fo': 'gross_brokerage_fo', 'cash': 'gross_brokerage_cash', 'comm': 'gross_brokerage_comm'}
NM = {'fo': 'net_brokerage_fo', 'cash': 'net_brokerage_cash', 'comm': 'net_brokerage_comm'}
SH = {'fo': 'share_fo_premium', 'cash': 'share_cash', 'comm': 'share_comm'}


def fv(m, q):
    return FACT[(m, q)]['value']


def inputs(seg, q):
    """gross Rs Cr, net/gross, share, ADTO (cash, Rs Cr/day) from the facts (Rs Mn / 10)."""
    g = fv(GM[seg], q) / 10.0
    n = fv(NM[seg], q) / 10.0
    return dict(gross=g, net=n, ratio=n / g, share=fv(SH[seg], q),
                adto=(fv('adto_cash', q) / 10.0 if seg == 'cash' else None))


# ------------------------------------------------------------------ the model (a-g rules, FY24 + FY25+)
def qdays(series_dates):
    rows = {}
    for d in sorted(series_dates):
        rows.setdefault(qlabel(d), []).append(d)
    return rows


FODAYS = qdays(S)
CASHDAYS = qdays(K)
MCXDAYS = qdays([d for d in MCX if d <= LASTCAL])

PAR = {}      # (seg, q) -> parameters
NETD = {'fo': {}, 'cash': {}, 'comm': {}}    # daily net revenue, Rs Cr
GRD = {'fo': {}, 'cash': {}, 'comm': {}}     # daily gross revenue, Rs Cr


def build(quarters, openq=None):
    for q in quarters:
        # F&O: rate = gross / (share x key); gross_d = share x S_d/1e7 x rate; net = ratio x gross
        ds = FODAYS[q]
        i = inputs('fo', q)
        F = sum(S[d] for d in ds) / 1e7
        rate = i['gross'] / (i['share'] * F)
        PAR[('fo', q)] = dict(share=i['share'], key=F, rate=rate, ratio=i['ratio'], gross=i['gross'], net=i['net'], days=len(ds),
                              kk=i['share'] * F)
        for d in ds:
            g = i['share'] * (S[d] / 1e7) * rate
            GRD['fo'][d] = g
            NETD['fo'][d] = i['ratio'] * g
        # cash: H = share x mean(K)/ADTO, J = gross/ADTO, gross_d = share x K_d / H x J / D
        ds = CASHDAYS[q]
        i = inputs('cash', q)
        C = sum(K[d] for d in ds) / len(ds)
        H = i['share'] * C / i['adto']
        Jr = i['gross'] / i['adto']
        PAR[('cash', q)] = dict(share=i['share'], key=sum(K[d] for d in ds), H=H, J=Jr, ratio=i['ratio'], gross=i['gross'],
                                net=i['net'], days=len(ds), adto=i['adto'], C=C, kk=i['share'] * sum(K[d] for d in ds),
                                rate=i['gross'] / (i['share'] * sum(K[d] for d in ds)))
        for d in ds:
            g = i['share'] * (K[d] / H) * (Jr / len(ds))
            GRD['cash'][d] = g
            NETD['cash'][d] = i['ratio'] * g
        # commodities: take = gross x 10 / (share x Mn contracts); L = Mn contracts_d x share x take (Rs Mn) /10
        ds = MCXDAYS[q]
        i = inputs('comm', q)
        cont = sum(MCX[d] for d in ds) / 1e6
        take = i['gross'] * 10.0 / (i['share'] * cont)
        PAR[('comm', q)] = dict(share=i['share'], key=cont, rate=take, ratio=i['ratio'], gross=i['gross'], net=i['net'],
                                days=len(ds), kk=i['share'] * cont)
        for d in ds:
            gmn = (MCX[d] / 1e6) * i['share'] * take          # Rs Mn
            GRD['comm'][d] = gmn / 10.0
            NETD['comm'][d] = i['ratio'] * gmn / 10.0


def open_quarter(q, last):
    """m-e: the open quarter carries the last reported quarter's gross per unit of key and net/gross."""
    p = PAR[('fo', last)]
    for d in FODAYS.get(q, []):
        # gross_d = share x S_d/1e7 x rate with rate = gross/(share x F): the share cancels
        GRD['fo'][d] = p['gross'] * (S[d] / 1e7) / p['key']
        NETD['fo'][d] = p['ratio'] * GRD['fo'][d]
    p = PAR[('cash', last)]
    perk = p['gross'] / p['key']
    for d in CASHDAYS.get(q, []):
        GRD['cash'][d] = perk * K[d]
        NETD['cash'][d] = p['ratio'] * GRD['cash'][d]
    p = PAR[('comm', last)]
    for d in MCXDAYS.get(q, []):
        GRD['comm'][d] = p['gross'] * MCX[d] / 1e6 / p['key']
        NETD['comm'][d] = p['ratio'] * GRD['comm'][d]


build(Q24 + Q25)
open_quarter('Q3 FY 2027', 'Q2 FY 2027')


# ------------------------------------------------------------------ ADR aggregation (special sessions out, errors out)
def seg_adr(seg, pred):
    vs = [v for d, v in NETD[seg].items() if pred(d) and not is_special(d)]
    return sum(vs) / len(vs) if vs else None, len(vs)


def adr_label(kind, label):
    f = {'Q': qlabel, 'M': mlabel, 'FY': lambda d: 'FY %d' % fy_of(d)}[kind]
    return lambda d: f(d) == label


def broking(pred):
    t = 0.0
    for s in SEG:
        a, n = seg_adr(s, pred)
        if a is None:
            return None
        t += a
    return t


def window_months(end_month_label, n=6):
    """The n calendar months ending at the month: a date predicate."""
    m = re.match(r'FY (\d+) (\w+)', end_month_label)
    fy, mon = int(m.group(1)), MONTHS.index(m.group(2))     # 0 = April
    idx = (fy - 1) * 12 + mon                                 # month index counted from April of FY1
    lo = idx - (n - 1)

    def pred(d):
        k = (fy_of(d) - 1) * 12 + (int(d[5:7]) - 4) % 12
        return lo <= k <= idx
    return pred


# ================================================================== CHECK 0: data-book re-reads
def find_book():
    cands = [os.path.join(ROOT, 'data/raw/disclosures/mosl/MOSL_DataBook_q4fy26-data-book.xlsx')]
    p = ROOT
    for _ in range(6):
        p = os.path.dirname(p)
        cands.append(os.path.join(p, 'data/raw/disclosures/mosl/MOSL_DataBook_q4fy26-data-book.xlsx'))
    for c in cands:
        if os.path.exists(c):
            return c
    return None


BOOKPATH = find_book()
REREADS = []
if BOOKPATH:
    import openpyxl
    wb = openpyxl.load_workbook(BOOKPATH, data_only=True)
    nre = 0
    for f in FACTS24:
        m = re.match(r'data_book:(.+?)#sheet=(.+)!([A-Z]+\d+)$', f['source_ref'])
        v = wb[m.group(2)][m.group(3)].value
        mult = 10.0 if f['unit'] in ('Rs Mn', 'Rs Mn/day') else (0.1 if f['unit'] == 'Mn' else 1.0)   # clients: lakh -> Mn
        mine = v * mult
        tol = 1e-8 if f['unit'] == 'fraction' else 1e-9            # fractions are stored to 9 decimals
        ok = rel(mine, f['value']) <= tol
        REREADS.append((f['fact_id'], f['metric'], f['period_key'], m.group(2) + '!' + m.group(3), v, mine, f['value'], ok))
        ITEMS.append([len(ITEMS) + 1, 'databook', '%s %s %s!%s (fact %d)' % (f['metric'], f['period_key'], m.group(2), m.group(3), f['fact_id']),
                      mine, f['value'], rel(mine, f['value']), tol, 'agree' if ok else 'DISAGREE',
                      'book cell %r x %g' % (v, mult)])
else:
    ITEMS.append([len(ITEMS) + 1, 'databook', 'data book not found', None, None, None, None, 'DISAGREE', 'xlsx missing'])

# ================================================================== CHECK 1: segment x quarter table
rows = table(['Segment', 'Quarter', 'Share', 'Quarter key'])
SEGKEY = {'F&O': 'fo', 'Cash': 'cash', 'Commodities': 'comm'}
ADRQ = {}        # (seg, q) -> (adr, ndays)
NETQ = {}
for r in rows:
    seg, q = SEGKEY[r[0]], r[1]
    p = PAR[(seg, q)]
    printed = dict(share=r[2], key=r[3].split(' ')[0], rate=r[4], ratio=r[5], gross=r[6], net=r[7], days=r[8], adr=r[9])
    tag = '%s %s' % (r[0], q)
    add('segment', tag + ' share', p['share'], num(r[2]), printed=r[2])
    add('segment', tag + ' quarter key', p['key'], num(printed['key']), printed=printed['key'])
    # rate: F&O Rs/contract, Cash gross per Rs of ADTO (J), Commodities Rs/contract
    mine_rate = p['J'] if seg == 'cash' else p['rate']
    add('segment', tag + (' rate (J = gross/ADTO)' if seg == 'cash' else ' rate'), mine_rate, num(r[4]), printed=r[4])
    add('segment', tag + ' net/gross', p['ratio'], num(r[5]), printed=r[5])
    add('segment', tag + ' gross Rs Cr', p['gross'], num(r[6]), printed=r[6])
    # quarter net revenue (every day) = sum of the daily net rows; must equal the net-brokerage fact
    nsum = sum(NETD[seg][d] for d in NETD[seg] if qlabel(d) == q)
    netfact = fv(NM[seg], q) / 10.0
    add('segment', tag + ' net revenue (sum of daily rows)', nsum, num(r[7]), printed=r[7])
    add('tie', tag + ' sum of daily net = net-brokerage fact / 10', nsum, netfact, tol=1e-12)
    gsum = sum(GRD[seg][d] for d in GRD[seg] if qlabel(d) == q)
    add('tie', tag + ' sum of daily gross = gross-brokerage fact / 10', gsum, p['gross'], tol=1e-12)
    a, n = seg_adr(seg, adr_label('Q', q))
    ADRQ[(seg, q)] = (a, n)
    NETQ[(seg, q)] = nsum
    add_bool('segment', tag + ' trading days in ADR', n, int(num(r[8])))
    add('segment', tag + ' ADR', a, num(r[9]), printed=r[9])

# arithmetic lines of the bridge: K, special-session numerators, H, contracts
txt = BR
for seg, name in (('fo', 'F&O'), ('cash', 'Cash'), ('comm', 'Commodities')):
    for q in Q24:
        m = re.search(r'- %s %s: (.*)' % (re.escape(name), re.escape(q)), txt)
        line = m.group(1)
        p = PAR[(seg, q)]
        if seg == 'fo':
            mk = re.search(r'= ([\d.]+) Cr contracts; rate = gross / K = ([\d.]+) / ([\d.]+) = ([\d.]+) Rs per contract; net = ([\d.]+) x ([\d.]+) = ([\d.]+) Rs Cr; ADR = ([\d.]+) / (\d+) days', line)
            add('arith', '%s %s K = share x key' % (name, q), p['kk'], float(mk.group(1)), printed=mk.group(1))
            add('arith', '%s %s ADR numerator (net, special sessions out)' % (name, q),
                sum(v for d, v in NETD[seg].items() if qlabel(d) == q and not is_special(d)), float(mk.group(8)), printed=mk.group(8))
        elif seg == 'cash':
            mk = re.search(r'H = share x avg key / ADTO = ([\d.]+); quarter key = ([\d,.]+) Rs Cr over (\d+) days; net = ([\d.]+) x ([\d.]+) = ([\d.]+); ADR = ([\d.]+) / (\d+) days', line)
            add('arith', '%s %s H' % (name, q), p['H'], float(mk.group(1)), printed=mk.group(1))
            nspec = sum(1 for d in CASHDAYS[q] if is_special(d))
            add_bool('arith', '%s %s days printed after "over" = days minus special sessions (the key total itself includes them)' % (name, q), p['days'] - nspec, int(mk.group(3)),
                     'bridge wording: "quarter key = X Rs Cr over N days"; X includes the %d special day(s), N does not' % nspec)
            add('arith', '%s %s ADR numerator' % (name, q),
                sum(v for d, v in NETD[seg].items() if qlabel(d) == q and not is_special(d)), float(mk.group(7)), printed=mk.group(7))
            mg = re.search(r'gross / ADTO = ([\d.]+) / ([\d,.]+) = ([\d.]+)', line)
            add('arith', '%s %s ADTO Rs Cr/day' % (name, q), p['adto'], num(mg.group(2)), printed=mg.group(2))
        else:
            mk = re.search(r'= ([\d.]+) x 10 / \(([\d.]+) x ([\d.]+)\) = ([\d.]+) Rs per contract; net = ([\d.]+) x ([\d.]+) = ([\d.]+); ADR = ([\d.]+) / (\d+) days', line)
            add('arith', '%s %s Mn contracts' % (name, q), p['key'], float(mk.group(3)), printed=mk.group(3))
            add('arith', '%s %s take Rs/contract' % (name, q), p['rate'], float(mk.group(4)), printed=mk.group(4))

# Broking table
for r in table(['Quarter', 'F&O', 'Cash', 'Commodities', 'Broking']):
    q = r[0]
    for j, s in enumerate(SEG):
        add('broking', '%s %s ADR' % (SEGNAME[s], q), ADRQ[(s, q)][0], num(r[1 + j]), printed=r[1 + j])
    add('broking', 'Broking %s ADR (sum of segment ADRs)' % q, sum(ADRQ[(s, q)][0] for s in SEG), num(r[4]), printed=r[4])

# the three Broking quarters are also checked against the net-brokerage facts by identity (days-weighted)
for q in Q24:
    tot = sum(fv(NM[s], q) / 10.0 for s in SEG)
    mine = sum(NETQ[(s, q)] for s in SEG)
    add('tie', 'Broking %s: sum of daily net revenue = cash+F&O+comm net brokerage facts' % q, mine, tot, tol=1e-12)

# ================================================================== June 2023 / Q1 FY24 / FY 2024 / Consolidated
june = [d for d in CAL if CAL[d]['q_fy'] == 'Q1 FY 2024']
rev_before_q2 = [(s, d) for s in SEG for d in NETD[s] if d < '2023-07-01']
add_bool('absent', 'June 2023 revenue rows (all three segments)', len(rev_before_q2), 0)
add_bool('absent', 'calendar days 2023-06-01..2023-06-30 (the 21 days that get no row)', len(june), 21)
firsts = {s: min(NETD[s]) for s in SEG}
for s, b in (('fo', 'F&O'), ('cash', 'Cash'), ('comm', 'Commodities')):
    add_bool('first-day', 'first revenue day %s' % b, firsts[s], '2023-07-03')
first_cal = min(CAL)
add_bool('absent', 'calendar starts after Q1 FY24 began (so Q1 FY24 / FY 2024 / FY 2024 months before Jul incomplete)', first_cal, '2023-06-01')
add_bool('absent', 'Q1 FY24 not computed: no facts-based quarter in my model', ('fo', 'Q1 FY 2024') in PAR, False)
add_bool('absent', 'FY 2024 not computed: needs Q1 FY24 days (my model has no Q1 FY24 days)',
         any(qlabel(d) == 'Q1 FY 2024' for s in SEG for d in NETD[s]), False)
mtf = [m for m in DB['market_daily'] if m['dataset'] == 'mtf_industry']
add_bool('absent', 'industry MTF book starts after Q4 FY24 (no MTF base, so Consolidated FY24 insufficient)',
         min(m['trade_date'] for m in mtf) > '2024-03-31', True, 'first MTF industry row %s' % min(m['trade_date'] for m in mtf))

# daily rows added
dr = {r[0]: r for r in table(['Segment', 'Days before', 'Days after'])}
mydays = {}
for s, b in (('fo', 'F&O'), ('cash', 'Cash'), ('comm', 'Commodities')):
    mydays[s] = sum(1 for d in NETD[s] if '2023-07-01' <= d <= '2024-03-31')
    add_bool('daily', '%s daily rows added (Q2-Q4 FY24)' % b, mydays[s], int(dr[b][8]))
    add_bool('daily', '%s days after = days before + added (bridge before %s)' % (b, dr[b][1]), int(dr[b][1]) + mydays[s], int(dr[b][2]))
    add_bool('daily', '%s first day' % b, firsts[s], '2023-07-03')
    add_bool('daily', '%s no day before 2023-07-03 (June rows)' % b, sum(1 for d in NETD[s] if d < '2023-07-03'), 0)

# ================================================================== parameter table
for r in table(['Segment', 'Quantity', 'Quarter', 'Before']):
    seg, qty, q, after = SEGKEY.get(r[0], r[0]), r[1], r[2], num(r[4])
    if q not in Q24:
        continue
    p = PAR[(seg, q)]
    if seg == 'cash':
        v = {"'delivery ratio' H": p['H'], 'gross per Rs of reported ADTO J': p['J'], 'share (cancels)': p['share'],
             'net / gross': p['ratio'], 'model gross brokerage Rs Cr': sum(GRD['cash'][d] for d in GRD['cash'] if qlabel(d) == q),
             'model net brokerage Rs Cr': NETQ[('cash', q)]}[qty]
    elif seg == 'fo':
        v = {'gross Rs per contract': p['rate'], 'premium share (cancels)': p['share'], 'net / gross': p['ratio'],
             'model gross brokerage Rs Cr': sum(GRD['fo'][d] for d in GRD['fo'] if qlabel(d) == q),
             'model net brokerage Rs Cr': NETQ[('fo', q)]}[qty]
    else:
        v = {'gross Rs per MOSL contract': p['rate'], 'share': p['share'], 'net / gross': p['ratio'],
             'model gross brokerage Rs Cr': sum(GRD['comm'][d] for d in GRD['comm'] if qlabel(d) == q),
             'model net brokerage Rs Cr': NETQ[('comm', q)]}[qty]
    add('param', '%s %s %s' % (r[0], qty, q), v, after, printed=r[4])

# inputs replaced by facts
for r in table(['Input', 'Period', 'Workbook', 'Live']):
    name, q, live = r[0], r[1], num(r[3])
    if q not in Q24:
        continue
    if name.startswith('net_gross_'):
        s = name[len('net_gross_'):]
        mine = fv(NM[s], q) / fv(GM[s], q)
        ids = '%d, %d' % (FACT[(NM[s], q)]['fact_id'], FACT[(GM[s], q)]['fact_id'])
    else:
        metric = {'adto_cash_mosl': 'adto_cash', 'gross_cash_cr': GM['cash'], 'gross_fo_cr': GM['fo'], 'gross_comm_cr': GM['comm'],
                  'share_cash': SH['cash'], 'share_fo': SH['fo'], 'share_comm': SH['comm']}[name]
        div = 1.0 if name.startswith('share') else 10.0
        mine = fv(metric, q) / div
        ids = str(FACT[(metric, q)]['fact_id'])
    add('input', '%s %s live' % (name, q), mine, live, printed=r[3])
    add_bool('input', '%s %s fact ids' % (name, q), ids, r[5].strip().split(' ')[0] if False else r[4])
    add_bool('input', '%s %s workbook has no value (dash)' % (name, q), r[2], '—')

# ================================================================== CHECK 2: FY25+ unchanged, and the 152 new cells
# 2a. FY25+ values from the FY25+ facts alone (FY24 facts and days play no part) against the bridge's ADR table.
adrtab = {(r[0], r[1]): r for r in table(['Period', 'Panel', 'Before'])}
mtf_bridge = {}
for (per, pan), r in adrtab.items():
    if pan == 'MTF':
        mtf_bridge[per] = num(r[3])


def period_pred(per):
    if re.match(r'^FY \d+$', per):
        return adr_label('FY', per)
    if re.match(r'^Q\d FY \d+$', per):
        return adr_label('Q', per)
    return adr_label('M', per)


for (per, pan), r in adrtab.items():
    pred = period_pred(per)
    segv = {s: seg_adr(s, pred)[0] for s in SEG}
    if pan in ('MTF',):
        continue
    mine = {'Broking': sum(segv.values()), 'F&O': segv['fo'], 'Cash': segv['cash'], 'Commodities': segv['comm'],
            'Consolidated': sum(segv.values()) + mtf_bridge[per]}[pan]
    add('fy25+', '%s %s ADR after (FY25+ facts only; MTF taken from the bridge for Consolidated)' % (per, pan), mine, num(r[3]), printed=r[3])
    add_bool('fy25+', '%s %s: bridge before = after (0 change)' % (per, pan), num(r[2]) == num(r[3]), True)

# 2b. the 152 new cells. Cells that depend on a FY24 base, derived from the rules (not from the bridge):
#   FY25 month  -> YoY base = same month FY24 (exists from Jul 2023); MoM base for April = Mar 2024; 6M window ending Apr..Aug
#   FY25 quarter-> YoY base = same quarter FY24 (Q2-Q4); QoQ base for Q1 FY25 = Q4 FY24
FY25M = ['FY 2025 ' + m for m in MONTHS]
have24 = lambda lab: any(mlabel(d) == lab for s in SEG for d in NETD[s] if '2023-07-01' <= d <= '2024-03-31')


def month_complete(lab):
    """A month is usable only if every calendar day of it is at or after the first revenue day (Jul 2023)."""
    ds = [d for d, c in CAL.items() if c['fy_month'] == lab]
    return bool(ds) and min(ds) >= '2023-07-01'


new = []     # (period, row, field)
for lab in FY25M:
    mo = lab.split(' ')[2]
    prev = 'FY 2024 ' + mo
    if mo == 'April':
        new += [(lab, 'FY 2024 March', 'value'), (lab, lab, 'comparison')]            # MoM
    if mo != 'April' and mo not in ('May', 'June') and month_complete(prev):
        new += [(lab, prev, 'value'), (lab, lab + ' / YoY', 'comparison')]
    # 6M window ending at the month needs every one of 6 calendar months to be complete
    mi = MONTHS.index(mo)
    win = []
    for k in range(5, -1, -1):
        j = mi - k
        fy = 2025 + (j // 12 if j >= 0 else -1) if False else None
    # window months as labels
    wl = []
    for k in range(5, -1, -1):
        j = MONTHS.index(mo) - k
        fy = 2025 if j >= 0 else 2024
        wl.append('FY %d %s' % (fy, MONTHS[j % 12]))
    # 6M exists today when all window months are FY25+ (Sep 2024 onwards); new when it reaches back to FY24 months that now exist
    reach_fy24 = [w for w in wl if w.startswith('FY 2024')]
    if reach_fy24 and all(month_complete(w) for w in reach_fy24):
        new += [(lab, 'Avg of last 6 months', 'value'), (lab, lab + ' / vs 6M', 'comparison')]
for q, base, kind in (('Q1 FY 2025', 'Q4 FY 2024', 'QoQ'), ('Q2 FY 2025', 'Q2 FY 2024', 'YoY'), ('Q3 FY 2025', 'Q3 FY 2024', 'YoY'),
                      ('Q4 FY 2025', 'Q4 FY 2024', 'YoY')):
    new += [(q, base, 'value'), (q, q if kind == 'QoQ' else q + ' / YoY', 'comparison')]
mine_set = set(new)
bridge_rows = None
for last, hdr, rws in TABLES:
    if hdr[:3] == ['Period', 'Row', 'Field']:
        bridge_rows = rws
bridge_set = set((r[0], r[1], r[2]) for r in bridge_rows)
add_bool('cells', 'new-cell rows derived from the rules vs the bridge table (count)', len(mine_set), len(bridge_set))
add_bool('cells', 'new-cell rows: sets equal (my-only %d, bridge-only %d)' % (len(mine_set - bridge_set), len(bridge_set - mine_set)),
         mine_set == bridge_set, True, 'my-only %s; bridge-only %s' % (sorted(mine_set - bridge_set)[:5], sorted(bridge_set - mine_set)[:5]))
add_bool('cells', 'cells = rows x 4 panels (Broking, Cash, Commodities, F&O)', len(bridge_set) * 4, 152)
add_bool('cells', 'every bridge row lists the four panels',
         all(r[3] == 'Broking, Cash, Commodities, F&O' for r in bridge_rows), True)

# 2c. recompute every new comparison value (and its bases) from my own FY24 and FY25 ADRs
PANELS = ['Broking', 'F&O', 'Cash', 'Commodities']


def panel_adr(pan, pred):
    if pan == 'Broking':
        return broking(pred)
    return seg_adr({'F&O': 'fo', 'Cash': 'cash', 'Commodities': 'comm'}[pan], pred)[0]


def cell_value(period, row, field, pan):
    """value of a bridge cell, recomputed."""
    if field == 'value':
        if row == 'Avg of last 6 months':
            return panel_adr(pan, window_months(period))
        if row.startswith('Q'):
            return panel_adr(pan, adr_label('Q', row))
        return panel_adr(pan, adr_label('M', row))
    cur = panel_adr(pan, period_pred(period))
    if row.endswith('/ YoY'):
        if period.startswith('Q'):
            m = re.match(r'Q(\d) FY (\d+)', period)
            base = adr_label('Q', 'Q%s FY %d' % (m.group(1), int(m.group(2)) - 1))
        else:
            m = re.match(r'FY (\d+) (\w+)', period)
            base = adr_label('M', 'FY %d %s' % (int(m.group(1)) - 1, m.group(2)))
    elif row.endswith('/ vs 6M'):
        base = window_months(period)
    elif period == 'Q1 FY 2025':
        base = adr_label('Q', 'Q4 FY 2024')              # QoQ
    elif period == 'FY 2025 April':
        base = adr_label('M', 'FY 2024 March')           # MoM
    else:
        raise ValueError((period, row))
    return cur / panel_adr(pan, base) - 1.0


CELLVALS = {}
for (period, row, field) in sorted(bridge_set):
    for pan in PANELS:
        v = cell_value(period, row, field, pan)
        CELLVALS[(period, row, field, pan)] = v
        # internal consistency: Broking cell = sum of segment cells for value rows
        ITEMS.append([len(ITEMS) + 1, 'newcell', '%s | %s | %s | %s' % (period, row, field, pan), v, None, None, None,
                      'recomputed' if v is not None else 'NO VALUE', '%s' % ('Rs Cr/day' if field == 'value' else 'ratio')])
for (period, row, field) in sorted(bridge_set):
    if field == 'value':
        s = sum(CELLVALS[(period, row, field, p)] for p in ('F&O', 'Cash', 'Commodities'))
        add('newcell-tie', '%s | %s | Broking value = F&O + Cash + Commodities' % (period, row), CELLVALS[(period, row, field, 'Broking')], s, tol=1e-12)
add_bool('newcell', 'all 152 recomputed cells are numbers (no insufficient data left)', all(v is not None and math.isfinite(v) for v in CELLVALS.values()), True)

# ================================================================== CHECK 3: sanity of the rates
SANITY = []
for q in Q24 + Q25[:4]:
    ds = FODAYS[q]
    nse = sum(NSEOPT[d] for d in ds) / 1e7
    bse = sum(BSEOPT[d] for d in ds) / 1e7
    p = PAR[('fo', q)]
    SANITY.append(dict(q=q, gross=p['gross'], share=p['share'], key=p['key'], nse=nse, bse=bse, bse_pct=bse / (nse + bse), rate=p['rate'],
                       rate_nse_only=p['gross'] / (p['share'] * nse), days=len(ds), gross_per_day=p['gross'] / len(ds)))
BSEPCT = {s['q']: s['bse_pct'] for s in SANITY}


# ================================================================== write the items csv and the summary
def fmt(x):
    if x is None:
        return ''
    if isinstance(x, float):
        return repr(x)
    return str(x)


os.makedirs(os.path.join(ROOT, 'out/checks'), exist_ok=True)
with open(os.path.join(ROOT, 'out/checks/mosl_switch_g_items.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['id', 'kind', 'item', 'mine', 'bridge', 'rel_diff', 'tolerance', 'verdict', 'note'])
    for it in ITEMS:
        w.writerow([fmt(x) for x in it])

kinds = {}
for it in ITEMS:
    k = kinds.setdefault(it[1], [0, 0, 0])
    k[0] += 1
    if it[7] == 'agree':
        k[1] += 1
    elif it[7] == 'recomputed':
        k[2] += 1
n_comp = [it for it in ITEMS if it[7] in ('agree', 'DISAGREE')]
n_agree = sum(1 for it in n_comp if it[7] == 'agree')
n_rec = sum(1 for it in ITEMS if it[7] == 'recomputed')
print('items with a claim to compare: %d, agree %d, disagree %d; recomputed-only new cells %d' % (len(n_comp), n_agree, len(n_comp) - n_agree, n_rec))
for k, v in kinds.items():
    print('  %-12s n=%-4d agree=%-4d recomputed=%d' % (k, v[0], v[1], v[2]))
for it in ITEMS:
    if it[7] == 'DISAGREE':
        print('DISAGREE', it[1], it[2], 'mine', it[3], 'bridge', it[4], 'rel', it[5], it[8])

if '--tables' in sys.argv:
    print('\n10 data-book re-reads')
    for r in REREADS[:0]:
        pass
    pick = [r for r in REREADS if r[1] in ('gross_brokerage_fo', 'net_brokerage_fo', 'gross_brokerage_cash', 'net_brokerage_cash',
                                           'gross_brokerage_comm', 'net_brokerage_comm', 'adto_cash', 'share_fo_premium', 'share_cash',
                                           'share_comm') and r[2] in ('Q2 FY 2024', 'Q3 FY 2024')][:10]
    for r in pick:
        print(r)
    print('\nrate sanity')
    for s in SANITY:
        print(s)
    print('\nnew cell sample')
    for k in [k for k in CELLVALS if k[3] == 'Broking']:
        print(k, CELLVALS[k])

if '--md' in sys.argv:
    print('\n| Period | Row | Field | Broking | F&O | Cash | Commodities |\n|---|---|---|---:|---:|---:|---:|')
    for (period, row, field) in sorted(bridge_set):
        vals = [CELLVALS[(period, row, field, p)] for p in ('Broking', 'F&O', 'Cash', 'Commodities')]
        f = (lambda v: '%.6f' % v) if field == 'value' else (lambda v: '%+.2f%%' % (v * 100))
        print('| %s | %s | %s | %s |' % (period, row, field, ' | '.join(f(v) for v in vals)))
    a, b = SANITY[1 - 1], SANITY[3]
    print('\nlog decomposition of the F&O rate fall, %s -> %s' % (a['q'], b['q']))
    tot = math.log(a['rate'] / b['rate'])
    parts = {'BSE share of key (key / NSE key)': math.log((1 / (1 - b['bse_pct'])) / (1 / (1 - a['bse_pct']))),
             'NSE index-option contracts': math.log(b['nse'] / a['nse']), 'MOSL premium share': math.log(b['share'] / a['share']),
             'gross brokerage (offsets)': -math.log(b['gross'] / a['gross'])}
    print('total ln(rate ratio) %.4f' % tot)
    for k, v in parts.items():
        print('  %-36s %+.4f  (%.0f%%)' % (k, v, 100 * v / tot))
    print('  sum %.4f' % sum(parts.values()))
    print('\n| Quarter | Gross Rs Cr | Premium share | Key Cr contracts | NSE io | BSE | BSE % | Rate | Rate NSE-only | gross/day |\n|---|---|---|---|---|---|---|---|---|---|')
    for s in SANITY:
        print('| %s | %.2f | %.4f | %.1f | %.1f | %.1f | %.1f%% | %.4f | %.4f | %.3f |' % (s['q'], s['gross'], s['share'], s['key'], s['nse'], s['bse'], 100 * s['bse_pct'], s['rate'], s['rate_nse_only'], s['gross_per_day']))
    print('\nQ4 comm days incl 2024-01-22 not in calendar:', '2024-01-22' in MCXDAYS['Q4 FY 2024'], len(MCXDAYS['Q4 FY 2024']))
    n = NETQ[('comm', 'Q4 FY 2024')]
    print('Q4 FY24 comm ADR with that day %.6f, without (60 days) %.6f' % (n / 61, n / 60))
    d = '2024-01-22'
    print('that day net', NETD['comm'][d], 'mcx', MCX[d])
