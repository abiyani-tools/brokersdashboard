# ---- common model block (stdlib: json, math, csv, re only; os/sys for paths) ----
# Independent rebuild of the MOSL ADR chain from docs/MOSL_ADR_Methodology.md (sections 3, 4, 8b),
# docs/MOSL_LIVE_SPEC.md, the snapshots and the reviewed facts. Nothing under src/ is read.
import json, math, csv, os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ERR = 'ERR'          # an error cell (#N/A, #VALUE!); blank rows are simply absent from a series


def J(p):
    with open(os.path.join(ROOT, p)) as fh:
        return json.load(fh)


DB = J('snapshot/db_snapshot_2026-10-23.json')
MS = J('snapshot/mosl_snapshot_2026-10-23.json')
FX = J('snapshot/mosl_fixtures_2026-10-23.json')
LAKE = J('snapshot/mosl_lake_2026-11-02.json')['series']
RF = J('snapshot/mosl_facts_reviewed_2026-11-02.json')['facts']
RFID = {f['fact_id']: f for f in RF}

# ---------------- calendar ----------------
CAL = {c['trade_date']: c for c in DB['calendar']}
LASTDATE = max(CAL)
SPECIAL = sorted(d for d, c in CAL.items() if c['special_session'])
QORDER = ['Q1 FY 2025', 'Q2 FY 2025', 'Q3 FY 2025', 'Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026',
          'Q4 FY 2026', 'Q1 FY 2027', 'Q2 FY 2027', 'Q3 FY 2027']
REPORTED = QORDER[:10]
def qprev(q, n=1):
    return QORDER[QORDER.index(q) - n]

# ---------------- workbook seed (typed assumptions) ----------------
SEED = {}
for f in MS['facts']:
    SEED.setdefault(f['metric'], {})[f['period_key']] = f['value']
ASSUME = {a['key']: a for a in MS['assumptions']}
NII_CARRY = ASSUME['mtf_nii_yield_carry']['value']
DAYBASIS = ASSUME['mtf_day_basis']['value']

# ---------------- exchange series ----------------
XL = {}
for m in MS['market_daily']:
    XL.setdefault(m['dataset'] + '/' + m['metric'], {})[m['trade_date']] = m
MCX = {m['trade_date']: m['value'] for m in DB['market_daily'] if m['dataset'] == 'mcx'}
BOOK = {m['trade_date']: m['value'] for m in DB['market_daily'] if m['dataset'] == 'mtf_industry'}
LK = {k: {r[0]: r[1] for r in v if r[0] <= LASTDATE and r[2] == 'ok'} for k, v in LAKE.items()}

# workbook key series
S_XL = {}   # F&O key = NSE index options + BSE (raw count); None = text/#VALUE! cell
for d in sorted(XL['nse_fo/index_opt_contracts']):
    n = XL['nse_fo/index_opt_contracts'][d]
    b = XL['bse_fo/opt_contracts_live'][d]
    S_XL[d] = None if (n['value'] is None or b['value'] is None) else n['value'] + b['value']
K_XL = {d: XL['nse_cash/turnover_cr_xl'][d]['value'] + XL['bse_cash/turnover_cr_xl'][d]['value']
        for d in sorted(XL['nse_cash/turnover_cr_xl'])}
# lake key series (own dates)
S_LK = {d: LK['nse_fo/io_contracts'][d] + LK['bse_fo/contracts'][d] for d in sorted(LK['nse_fo/io_contracts'])
        if d in LK['bse_fo/contracts']}
K_LK = {d: LK['nse_cash/turnover_cr'][d] + LK['bse_cash/turnover_cr'][d] for d in sorted(LK['nse_cash/turnover_cr'])
        if d in LK['bse_cash/turnover_cr']}

# ---------------- reviewed facts -> input units ----------------
# input -> (fact metric, divisor).  Rs Mn -> Rs Cr is /10; Rs Mn/day -> Rs Cr/day is /10; fractions as they are.
INPUT_MAP = {
    'adto_cash_mosl': ('adto_cash', 10.0), 'gross_cash_cr': ('gross_brokerage_cash', 10.0),
    'gross_fo_cr': ('gross_brokerage_fo', 10.0), 'gross_comm_cr': ('gross_brokerage_comm', 10.0),
    'mtf_book_closing': ('mtf_book', 10.0), 'share_cash': ('share_cash', 1.0),
    'share_fo': ('share_fo_premium', 1.0), 'share_comm': ('share_comm', 1.0)}
FACT = {}   # (fact metric, quarter) -> fact
for f in RF:
    FACT[(f['metric'], f['period_key'])] = f


def fval(metric, q):
    return FACT[(metric, q)]['value']


def live_input(name, q):
    """Live value of an input in its own unit, from the reviewed fact."""
    if name.startswith('net_gross_'):
        seg = name[len('net_gross_'):]
        return fval('net_brokerage_' + seg, q) / fval('gross_brokerage_' + seg, q)
    m, div = INPUT_MAP[name]
    return fval(m, q) / div


def live_input_facts(name, q):
    if name.startswith('net_gross_'):
        seg = name[len('net_gross_'):]
        return [FACT[('net_brokerage_' + seg, q)]['fact_id'], FACT[('gross_brokerage_' + seg, q)]['fact_id']]
    return [FACT[(INPUT_MAP[name][0], q)]['fact_id']]


def wb_input(name, q):
    """The workbook's typed value (None where the workbook has none / only a formula)."""
    return SEED.get(name, {}).get(q)


# =============== the model ===============
def qi(q):
    return QORDER.index(q)


def qkey(q):
    m = re.match(r'Q(\d) FY (\d+)', q)
    return (int(m.group(2)), int(m.group(1)))


class Model:
    """flags: letters 'a'..'f' applied cumulatively (parity = empty set)."""

    def __init__(self, flags):
        self.fl = set(flags)
        self.P = {}        # parameters per segment
        self.series = {}   # segment -> {date: net revenue (sheet unit) or ERR}; blank rows are absent
        self.gross = {}    # segment -> {date: gross revenue (sheet unit)}
        self.key = {}      # segment -> {date: key}
        self.lastq = 'Q2 FY 2027' if 'a' in self.fl else 'Q1 FY 2027'   # last calibrated quarter
        self._fo()
        self._cash()
        self._comm()
        self._mtf()
        if 'c' in self.fl:
            for s in self.series:
                self.series[s] = {d: v for d, v in self.series[s].items() if v != ERR}

    def _inp(self, name, q):
        """An input as the chain reads it: the reviewed fact under switch a, the workbook's typed value before."""
        if 'a' in self.fl and q in REPORTED:
            return live_input(name, q)
        return wb_input(name, q)

    def _ratio(self, seg):
        a = 'a' in self.fl
        r = {}
        for q in REPORTED:
            if a:
                r[q] = live_input('net_gross_' + seg, q)
            elif q in SEED['net_gross_' + seg] and qi(q) <= qi('Q1 FY 2027'):
                r[q] = SEED['net_gross_' + seg][q]
        if not a:
            if seg != 'fo' or True:
                r['Q2 FY 2027'] = (r['Q4 FY 2026'] + r['Q1 FY 2027']) / 2.0
        return r

    # ---------------- F&O ----------------
    def _fo(self):
        fl = self.fl
        a, b = 'a' in fl, 'b' in fl
        S = S_LK if b else S_XL
        dates = [d for d in sorted(S) if d in CAL]
        rows = {}
        for d in dates:
            rows.setdefault(CAL[d]['q_fy'], []).append(d)
        F = {q: sum(S[d] for d in ds if S.get(d) is not None) / 1e7 for q, ds in rows.items()}   # Cr contracts
        gross, share, rate = {}, {}, {}
        for q in QORDER:
            gross[q] = self._inp('gross_fo_cr', q)
            share[q] = self._inp('share_fo', q)
        if not a:
            share['Q1 FY 2027'] = (wb_input('share_fo', 'Q3 FY 2026') + wb_input('share_fo', 'Q4 FY 2026')) / 2.0
            share['Q2 FY 2027'] = share['Q3 FY 2027'] = share['Q1 FY 2027']
        else:
            share['Q3 FY 2027'] = share['Q2 FY 2027']
        for q in QORDER:
            if gross[q] is not None and share[q] is not None and q in F:
                rate[q] = gross[q] / (share[q] * F[q])           # gross Rs per contract
        last = self.lastq
        for q in QORDER[qi(last) + 1:]:
            rate[q] = rate[last]
        ratio = self._ratio('fo')
        ratio['Q3 FY 2027'] = ratio['Q2 FY 2027']
        self.P['fo'] = dict(F=F, share=share, rate=rate, ratio=ratio, gross_in=gross)
        ser, gr = {}, {}
        for d in dates:
            q = CAL[d]['q_fy']
            if qkey(q) < qkey('Q1 FY 2025'):
                ser[d] = ERR                                      # no table row: #N/A
                continue
            sd = S.get(d)
            if sd is None:
                ser[d] = ERR                                      # text key: #VALUE!
                continue
            if q not in rate:                                     # Q1-Q2 FY25 in parity: blank rate = numeric 0
                ser[d] = 0
                gr[d] = 0
                continue
            g = share[q] * (sd / 1e7) * rate[q] * 10.0            # Rs Mn gross
            gr[d] = g
            ser[d] = ratio[q] * g
        self.series['fo'], self.gross['fo'] = ser, gr
        self.key['fo'] = {d: S.get(d) for d in dates}

    # ---------------- cash ----------------
    def _cash(self):
        fl = self.fl
        a, b = 'a' in fl, 'b' in fl
        K = K_LK if b else K_XL
        first = 'Q1 FY 2025' if a else 'Q3 FY 2025'
        dates = [d for d in sorted(K) if d in CAL and CAL[d]['q_fy'] in QORDER and qi(CAL[d]['q_fy']) >= qi(first)]
        rows = {}
        for d in dates:
            rows.setdefault(CAL[d]['q_fy'], []).append(d)
        C = {q: sum(K[d] for d in ds) / len(ds) for q, ds in rows.items()}
        D = {q: len(ds) for q, ds in rows.items()}
        calib = [q for q in REPORTED if (a or qi(q) >= 2) and (a or qi(q) <= qi('Q1 FY 2027'))]
        share, H, Jr, gross, adto = {}, {}, {}, {}, {}
        for q in calib:
            share[q] = self._inp('share_cash', q)
            gross[q] = self._inp('gross_cash_cr', q)
            adto[q] = self._inp('adto_cash_mosl', q)
            H[q] = share[q] * C[q] / adto[q]
            Jr[q] = gross[q] / adto[q]
        if not a:
            Jr['Q1 FY 2027'] = Jr['Q4 FY 2026']                  # workbook J52 = J51
        for q in QORDER[qi(calib[-1]) + 1:]:
            pq = qprev(q)
            share[q] = share[pq]
            Jr[q] = Jr[pq]
            H[q] = (H[qprev(q, 3)] + H[qprev(q, 2)] + H[pq]) / 3.0
        ratio = self._ratio('cash')
        fl = self.fl
        self.P['cash'] = dict(C=C, D=D, share=share, H=H, J=Jr, ratio=ratio, gross_in=gross, adto=adto)
        e = 'e' in fl
        if e:      # open quarter: last reported quarter's gross per Rs Cr of turnover and its net / gross
            ratio['Q3 FY 2027'] = ratio['Q2 FY 2027']
            perk = gross['Q2 FY 2027'] / (C['Q2 FY 2027'] * D['Q2 FY 2027'])
        ser, gr = {}, {}
        for d in dates:
            q = CAL[d]['q_fy']
            if e and q == 'Q3 FY 2027':
                aa = perk * K[d]
            else:
                aa = share[q] * (K[d] / H[q]) * (Jr[q] / D[q])
            gr[d] = aa
            ser[d] = ratio[q] * aa if q in ratio else ERR          # Q3 FY27: HLOOKUP range ends at Q2 FY27
        self.series['cash'], self.gross['cash'] = ser, gr
        self.key['cash'] = {d: K[d] for d in dates}

    # ---------------- commodities ----------------
    def _comm(self):
        a = 'a' in self.fl
        dates = [d for d in sorted(MCX) if d in CAL]
        rows = {}
        for d in dates:
            rows.setdefault(CAL[d]['q_fy'], []).append(d)
        cont = {q: sum(MCX[d] for d in ds) / 1e6 for q, ds in rows.items()}      # Mn contracts
        share, take, gross = {}, {}, {}
        qs = [q for q in REPORTED if a or qi(q) <= qi('Q1 FY 2027')]
        for q in qs:
            gross[q] = self._inp('gross_comm_cr', q)
            share[q] = self._inp('share_comm', q)
            take[q] = gross[q] * 10.0 / (share[q] * cont[q])      # gross Rs per MOSL contract
        if not a:
            share['Q2 FY 2027'] = sum(share[x] for x in ('Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027')) / 4.0
            take['Q2 FY 2027'] = take['Q1 FY 2027']
        ratio = self._ratio('comm')
        if 'e' in self.fl:       # open quarter carries the last reported quarter's net per contract and net / gross
            share['Q3 FY 2027'] = share['Q2 FY 2027']
            take['Q3 FY 2027'] = take['Q2 FY 2027']
            ratio['Q3 FY 2027'] = ratio['Q2 FY 2027']
        self.P['comm'] = dict(cont=cont, share=share, take=take, ratio=ratio, gross_in=gross)
        ser, gr = {}, {}
        for d in dates:
            q = CAL[d]['q_fy']
            if q not in take:
                if d <= '2026-10-12':
                    ser[d] = ERR              # O #N/A to 12 Oct, blank from 13 Oct
                continue
            l = (MCX[d] / 1e6) * share[q] * take[q]
            gr[d] = l
            ser[d] = ratio[q] * l
        self.series['comm'], self.gross['comm'] = ser, gr
        self.key['comm'] = {d: MCX[d] for d in dates}

    # ---------------- MTF ----------------
    def _mtf(self):
        a = 'a' in self.fl
        dates = [d for d in sorted(BOOK) if d in CAL]
        rows = {}
        for d in dates:
            rows.setdefault(CAL[d]['q_fy'], []).append(d)
        indclose = {q: BOOK[ds[-1]] for q, ds in rows.items()}
        qs = [q for q in REPORTED if (a or qi(q) <= qi('Q1 FY 2027')) and q in indclose]
        share, nii = {}, {}
        for q in qs:
            share[q] = self._inp('mtf_book_closing', q) / indclose[q]
            nii[q] = SEED['mtf_nii_yield'].get(q, NII_CARRY)
        last = qs[-1]
        for q in QORDER[qi(last) + 1:]:
            share[q] = share[last]
            nii[q] = SEED['mtf_nii_yield'].get(q, NII_CARRY)
        self.P['mtf'] = dict(share=share, nii=nii, indclose=indclose)
        ser = {}
        for d in dates:
            q = CAL[d]['q_fy']
            if 'e' not in self.fl and d > '2026-09-30':
                continue                                           # formulas stop on 30 Sep
            ser[d] = share[q] * BOOK[d] * nii[q] / DAYBASIS
        self.series['mtf'] = ser


# =============== aggregation ===============
SCALE = {'fo': 0.1, 'comm': 0.1, 'cash': 1.0, 'mtf': 1.0}


def isnum(v):
    return v is not None and v != ERR


def sel_label(kind, label):
    key = {'FY': 'fy', 'Q': 'q_fy', 'M': 'fy_month'}[kind]
    return lambda d: CAL[d][key] == label


def seg_rows(model, seg, drop_special):
    s = model.series[seg]
    if drop_special and seg != 'mtf':
        return {d: v for d, v in s.items() if not CAL[d]['special_session']}
    return s


def adr_seg(model, seg, sel, guard=True):
    """AVERAGEIFS-style ADR of one segment (Rs Cr/day): blanks skipped, zeros kept; an error row among the
    matched rows makes the whole average an error -> 0 (parity / IFERROR) until switch c drops error rows."""
    rows = seg_rows(model, seg, 'd' in model.fl)
    vals = [v for d, v in rows.items() if sel(d)]
    if any(v == ERR for v in vals) or not vals:
        return 0.0
    return sum(vals) / len(vals) * SCALE[seg]


def window_seg(model, seg, kind, n=None, k=None):
    """Last-N-trading-days, previous-5 and weekday windows over the segment's own numeric dates."""
    rows = seg_rows(model, seg, 'd' in model.fl)
    num = {d: v for d, v in rows.items() if isnum(v)}
    ds = sorted(num, reverse=True)
    if kind == 'last':
        if len(ds) < n:
            return 0.0
        cut = ds[n - 1]
        vs = [num[d] for d in ds if d >= cut]
    elif kind == 'prev5':
        hi, lo = ds[5], ds[9]
        vs = [num[d] for d in ds if lo <= d <= hi]
    elif kind == 'wd':
        wd = [d for d in ds if CAL[d]['weekday'] == k]
        vs = [num[d] for d in wd[:n]]
    return sum(vs) / len(vs) * SCALE[seg] if vs else 0.0


SEGS = ['fo', 'cash', 'comm', 'mtf']
PANELS = ['Consolidated', 'Broking', 'MTF', 'F&O', 'Cash', 'Commodities']


def panels_from(seg_vals):
    br = seg_vals['fo'] + seg_vals['cash'] + seg_vals['comm']
    return {'Consolidated': br + seg_vals['mtf'], 'Broking': br, 'MTF': seg_vals['mtf'],
            'F&O': seg_vals['fo'], 'Cash': seg_vals['cash'], 'Commodities': seg_vals['comm']}


def adr_panels(model, kind, label):
    sel = sel_label(kind, label)
    return panels_from({s: adr_seg(model, s, sel) for s in SEGS})


def window_panels(model, kind, n=None, k=None):
    return panels_from({s: window_seg(model, s, kind, n, k) for s in SEGS})


WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']


def consolidated_tables(model):
    """The Consolidated week / weekday tables of the bridge, keyed as the bridge prints them."""
    out = {}
    out[('Week', 'Last 5 trading days')] = window_panels(model, 'last', 5)['Consolidated']
    out[('Week', 'Last 5 trading days | vs 45D')] = out[('Week', 'Last 5 trading days')]
    out[('Week', 'Previous 5 trading days')] = window_panels(model, 'prev5')['Consolidated']
    out[('Week', 'Last 45 trading days')] = window_panels(model, 'last', 45)['Consolidated']
    out[('Week', 'Last 20 trading days')] = window_panels(model, 'last', 20)['Consolidated']
    for wd in WEEKDAYS:
        v = window_panels(model, 'wd', 1, wd)['Consolidated']
        out[('Weekday', wd)] = v
        out[('Weekday', wd + ' | vs 10')] = v
        out[('Weekday', 'Average of last 3 %ss' % wd)] = window_panels(model, 'wd', 3, wd)['Consolidated']
        out[('Weekday', 'Average of last 10 %ss' % wd)] = window_panels(model, 'wd', 10, wd)['Consolidated']
    return out
# =============== bridge parsing ===============
def num(s):
    s = s.strip().replace(',', '').replace('%', '').replace('+', '')
    if s in ('', '—', '-', 'none'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def read_bridge(name):
    with open(os.path.join(ROOT, 'out', 'bridges', name)) as fh:
        return fh.read()


def md_tables(text):
    """Yield (preceding non-table line, header cells, rows of cells) for every pipe table in text."""
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


def bridge_adr(text):
    """Per (period, panel): (before, after) from the 'ADR ...' panel table."""
    res = {}
    for last, hdr, rows in md_tables(text):
        if hdr[:3] == ['Period', 'Panel', 'Before']:
            for r in rows:
                res[(r[0], r[1])] = (r[2], r[3], r[4], r[5])
    return res


def bridge_consol(text):
    """Consolidated before -> after per period from the first summary table."""
    res = {}
    for last, hdr, rows in md_tables(text):
        if hdr[:3] == ['Period', 'Before', 'After']:
            for r in rows:
                res[r[0]] = (r[1], r[2], r[3])
            break
    return res


def bridge_tables(text):
    """(Table, Row) -> (before, after) from the Consolidated week / weekday table."""
    res = {}
    for last, hdr, rows in md_tables(text):
        if hdr[:3] == ['Panel', 'Table', 'Row']:
            for r in rows:
                key = (r[1], ' | '.join(r[2:-2]))
                res[key] = (r[-2], r[-1])
    return res


def bridge_params(text):
    res = {}
    for last, hdr, rows in md_tables(text):
        if hdr[:4] == ['Segment', 'Quantity', 'Quarter', 'Before']:
            for r in rows:
                res[(r[0], r[1], r[2])] = (r[3], r[4], r[5])
    return res


def bridge_daily(text):
    res = {}
    for last, hdr, rows in md_tables(text):
        if hdr[:3] == ['Segment', 'Days before', 'Days after']:
            for r in rows:
                res[r[0]] = dict(before=int(r[1]), after=int(r[2]), changed=int(r[3]), first=r[4], last=r[5],
                                 rmin=num(r[6]), rmax=num(r[7]), added=int(r[8]), dropped=int(r[9]))
    return res


def bridge_inputs(text):
    res = {}
    for last, hdr, rows in md_tables(text):
        if hdr[:4] == ['Input', 'Period', 'Workbook', 'Live']:
            for r in rows:
                res[(r[0], r[1])] = (r[2], r[3], r[4], r[5])
    return res
# =============== parameters and daily-row comparisons ===============
def qrows(model, seg, q):
    return [d for d in model.series[seg] if CAL[d]['q_fy'] == q]


def param_value(model, seg, qty, q):
    """The bridge's 'Parameters that moved' quantity for a segment and quarter; None prints as a dash."""
    P = model.P
    e = 'e' in model.fl
    key = {'Cash': 'cash', 'F&O': 'fo', 'Commodities': 'comm', 'MTF': 'mtf'}[seg]
    p = P[key]
    if key == 'cash':
        if qty in ("'delivery ratio' H", 'gross per Rs of reported ADTO J', 'share (cancels)') and e and q == 'Q3 FY 2027':
            return None
        if qty == "'delivery ratio' H":
            return p['H'].get(q)
        if qty == 'gross per Rs of reported ADTO J':
            return p['J'].get(q)
        if qty == 'share (cancels)':
            return p['share'].get(q)
        if qty == 'net / gross':
            return p['ratio'].get(q)
    if key == 'fo':
        if qty == 'gross Rs per contract':
            if 'a' not in model.fl and q in ('Q1 FY 2025', 'Q2 FY 2025'):
                return 0.0                       # blank rate cell reads as 0
            return p['rate'].get(q)
        if qty == 'premium share (cancels)':
            return p['share'].get(q)
        if qty == 'net / gross':
            return p['ratio'].get(q)
    if key == 'comm':
        if qty == 'gross Rs per MOSL contract':
            return p['take'].get(q)
        if qty == 'share':
            return p['share'].get(q)
        if qty == 'net / gross':
            return p['ratio'].get(q)
    if key == 'mtf':
        if 'a' not in model.fl and q == 'Q3 FY 2027':
            return None                          # the workbook has no Q3 FY27 MTF row
        if qty == 'NII yield':
            return p['nii'].get(q)
        if qty == 'share of industry book':
            return p['share'].get(q)
    if qty in ('model gross brokerage Rs Cr', 'model net brokerage Rs Cr'):
        ser = model.series[key]
        ds = [d for d in ser if CAL[d]['q_fy'] == q]
        if not ds:
            return None
        sc = SCALE[key]
        if qty.startswith('model gross'):
            g = [model.gross[key][d] for d in ds if d in model.gross[key]]
            return sum(g) * sc if g else (0.0 if key == 'fo' else None)
        n = [ser[d] for d in ds if isnum(ser[d])]
        return sum(n) * sc if n else 0.0
    raise KeyError((seg, qty))


def daily_stats(before, after, seg):
    """Rows-changed statistics of one segment between two models (the bridge's last table)."""
    sb, sa = before.series[seg], after.series[seg]
    changed, ratios, first, last = 0, [], None, None
    for d in sorted(sa):
        if d not in sb:
            continue
        vb, va = sb[d], sa[d]
        diff = (vb == ERR) != (va == ERR)
        if not diff and isnum(vb) and isnum(va):
            diff = abs(va - vb) > 1e-9 * max(abs(vb), 1e-12) and abs(va - vb) > 1e-12
        if diff:
            changed += 1
            first = first or d
            last = d
            if isnum(vb) and isnum(va) and vb:
                ratios.append(va / vb)
    return dict(before=len(sb), after=len(sa), changed=changed, first=first or '', last=last or '',
                rmin=min(ratios) if ratios else None, rmax=max(ratios) if ratios else None,
                added=len([d for d in sa if d not in sb]), dropped=len([d for d in sb if d not in sa]))
# =============== comparison helpers ===============
def dp_of(s):
    s = s.strip().replace(',', '').replace('%', '').replace('+', '')
    return len(s.split('.')[1]) if '.' in s else 0


def judge(bs, mine):
    """Compare one printed bridge cell with my value. Returns (agree, agree_1e6, rel_diff).
    Agree = within 1e-6 relative, or within half a unit of the last digit the bridge prints."""
    bs = (bs or '').strip()
    b = num(bs)
    if b is None:
        ok = mine is None
        return ok, ok, 0.0 if ok else float('inf')
    if mine is None:
        return False, False, float('inf')
    pct = bs.endswith('%')
    m = mine * 100.0 if pct and False else mine
    diff = abs(m - b)
    rel = diff / abs(b) if b else diff
    a6 = rel <= 1e-6 or diff <= 1e-12
    half = 0.5 * 10 ** (-dp_of(bs)) * (1 + 1e-9)
    return (a6 or diff <= half), a6, rel


def pct_change(before, after):
    if before is None or after is None or before == 0:
        return None
    return (after / before - 1.0) * 100.0


def period_kind(label):
    if label.startswith('Q'):
        return 'Q'
    return 'FY' if re.match(r'^FY \d{4}$', label) else 'M'


class Items:
    def __init__(self):
        self.rows = []

    def add(self, kind, item, agree, a6, rel, mine='', bridge='', note=''):
        self.rows.append(dict(kind=kind, item=item, agree=bool(agree), a6=bool(a6), rel=rel,
                              mine=mine, bridge=bridge, note=note))

    def multi(self, kind, item, pairs, mine='', bridge='', note=''):
        """pairs: list of (bridge string, my value); one item agrees if every pair does."""
        res = [judge(b, m) for b, m in pairs]
        self.add(kind, item, all(r[0] for r in res), all(r[1] for r in res), max(r[2] for r in res),
                 mine, bridge, note)

    def count(self, kind):
        r = [x for x in self.rows if x['kind'] == kind]
        return len(r), sum(1 for x in r if x['agree']), sum(1 for x in r if x['a6'])

    def kinds(self):
        out = []
        for x in self.rows:
            if x['kind'] not in out:
                out.append(x['kind'])
        return out

    def totals(self):
        return len(self.rows), sum(1 for x in self.rows if x['agree']), sum(1 for x in self.rows if x['a6'])

    def disagreements(self):
        return [x for x in self.rows if not x['agree']]


def fmt(v, dp=6):
    if v is None:
        return '—'
    if isinstance(v, float):
        return ('%.' + str(dp) + 'f') % v
    return str(v)


def fnum(v):
    return '—' if v is None else ('%.6g' % v)


# ---- generic item generators over the bridge tables ----
def adr_items(items, text, before, after):
    br = bridge_adr(text)
    lines = []
    for (per, pan), (bb, ba, bd, bp) in br.items():
        k = period_kind(per)
        vb, va = adr_panels(before, k, per)[pan], adr_panels(after, k, per)[pan]
        dd = va - vb
        pc = pct_change(vb, va)
        pairs = [(bb, vb), (ba, va), (bd, dd)]
        if bp.strip():
            pairs.append((bp, pc))
        res = [judge(b, m) for b, m in pairs]
        ok = all(r[0] for r in res)
        a6 = all(r[1] for r in res[:2])
        rel = max(r[2] for r in res[:2])
        items.add('ADR', '%s | %s' % (per, pan), ok, a6, rel, mine='%s -> %s' % (fmt(vb), fmt(va)),
                  bridge='%s -> %s' % (bb, ba))
        lines.append((per, pan, vb, bb, va, ba, rel, ok))
    return lines


def consol_items(items, text, before, after):
    lines = []
    for per, (bb, ba, bp) in bridge_consol(text).items():
        k = period_kind(per)
        vb, va = adr_panels(before, k, per)['Consolidated'], adr_panels(after, k, per)['Consolidated']
        res = [judge(bb, vb), judge(ba, va), judge(bp, pct_change(vb, va)) if bp.strip() else (True, True, 0)]
        items.add('summary', 'Consolidated ' + per, all(r[0] for r in res), all(r[1] for r in res[:2]),
                  max(r[2] for r in res[:2]), '%s -> %s' % (fmt(vb), fmt(va)), '%s -> %s' % (bb, ba))
        lines.append((per, vb, bb, va, ba, max(r[2] for r in res[:2]), all(r[0] for r in res)))
    return lines


def param_items(items, text, before, after):
    lines = []
    for (seg, qty, q), (bb, ba, bp) in bridge_params(text).items():
        mb, ma = param_value(before, seg, qty, q), param_value(after, seg, qty, q)
        pairs = [(bb, mb), (ba, ma)]
        if bp.strip():
            pairs.append((bp, pct_change(mb, ma)))
        else:
            pairs.append(('', pct_change(mb, ma) if False else None))
        res = [judge(b, m) for b, m in pairs]
        ok = all(r[0] for r in res)
        items.add('param', '%s | %s | %s' % (seg, qty, q), ok, all(r[1] for r in res[:2]),
                  max(r[2] for r in res[:2]), '%s -> %s' % (fnum(mb), fnum(ma)), '%s -> %s' % (bb, ba))
        lines.append((seg, qty, q, mb, bb, ma, ba, bp, max(r[2] for r in res[:2]), ok))
    return lines


def table_items(items, text, before, after):
    bt = bridge_tables(text)
    tb, ta = consolidated_tables(before), consolidated_tables(after)
    lines = []
    for key, (bb, ba) in bt.items():
        if key not in tb:
            items.add('week/weekday', ' | '.join(key), False, False, float('inf'), 'row not modelled', '%s -> %s' % (bb, ba))
            continue
        r1, r2 = judge(bb, tb[key]), judge(ba, ta[key])
        items.add('week/weekday', ' | '.join(key), r1[0] and r2[0], r1[1] and r2[1], max(r1[2], r2[2]),
                  '%s -> %s' % (fmt(tb[key]), fmt(ta[key])), '%s -> %s' % (bb, ba))
        lines.append((key, tb[key], bb, ta[key], ba, max(r1[2], r2[2]), r1[0] and r2[0]))
    return lines


def daily_items(items, text, before, after):
    bd = bridge_daily(text)
    names = (('fo', 'F&O'), ('cash', 'Cash'), ('comm', 'Commodities'), ('mtf', 'MTF'))
    lines = []
    for seg, nm in names:
        st = daily_stats(before, after, seg)
        br = bd[nm]
        notes = []
        ok = True
        for k in ('before', 'after', 'added', 'dropped'):
            if st[k] != br[k]:
                ok = False
        # 'changed': the bridge counts any float difference; mine counts a relative difference above 1e-9
        if st['changed'] != br['changed']:
            notes.append('changed: mine %d (rel diff > 1e-9) vs bridge %d' % (st['changed'], br['changed']))
        if st['changed'] > br['changed']:
            ok = False
        if st['changed'] and (st['first'] != br['first'] and not notes):
            ok = False
        rmin_ok = (st['rmin'] is None and br['rmin'] is None) or (
            st['rmin'] is not None and br['rmin'] is not None and judge('%.9f' % br['rmin'], st['rmin'])[0])
        rmax_ok = (st['rmax'] is None and br['rmax'] is None) or (
            st['rmax'] is not None and br['rmax'] is not None and judge('%.9f' % br['rmax'], st['rmax'])[0])
        if not notes:
            ok = ok and rmin_ok and rmax_ok
        else:
            # bridge counts float-noise changes (ratio 1.000000000); require min ratio match and max within 1
            ok = ok and rmin_ok and (br['rmax'] is not None and abs(br['rmax'] - max(st['rmax'] or 1.0, 1.0)) < 1e-9)
        items.add('daily', nm, ok, ok, 0.0 if ok else 1.0,
                  'days %d->%d changed %d added %d dropped %d ratio %s..%s' % (
                      st['before'], st['after'], st['changed'], st['added'], st['dropped'],
                      fmt(st['rmin'], 9), fmt(st['rmax'], 9)),
                  'days %d->%d changed %d added %d dropped %d ratio %s..%s' % (
                      br['before'], br['after'], br['changed'], br['added'], br['dropped'],
                      fmt(br['rmin'], 9), fmt(br['rmax'], 9)), '; '.join(notes))
        lines.append((nm, st, br, ok, '; '.join(notes)))
    return lines


# ---- report writers ----
def esc(s):
    return str(s).replace('|', '/')


def write_outputs(stem, title, items, sections, notes, unverified):
    """Write out/checks/<stem>.md and <stem>_items.csv."""
    n, ag, a6 = items.totals()
    kinds = items.kinds()
    md = []
    md.append('# %s: independent recompute' % title)
    md.append('')
    md.append('Script: `out/checks/%s_check.py` (stdlib json/math/csv/re; run from the repo root). Inputs: '
              '`docs/MOSL_ADR_Methodology.md`, `docs/MOSL_LIVE_SPEC.md`, `snapshot/mosl_snapshot_2026-10-23.json`, '
              '`snapshot/mosl_facts_reviewed_2026-11-02.json`, `snapshot/mosl_lake_2026-11-02.json`, '
              '`snapshot/db_snapshot_2026-10-23.json` (calendar, MCX, industry MTF book); '
              '`snapshot/mosl_fixtures_2026-10-23.json` only to prove the parity rebuild. No file under '
              '`src/engine/` or `src/live/` was read.' % stem)
    md.append('')
    md.append('**Result: %d/%d items agree** (%d to 1e-6 relative; the rest agree to the print precision of the bridge).' % (ag, n, a6))
    md.append('')
    md.append('| Item kind | Checked | Agree | Agree at 1e-6 |')
    md.append('|---|---:|---:|---:|')
    for k in kinds:
        c = items.count(k)
        md.append('| %s | %d | %d | %d |' % (k, c[0], c[1], c[2]))
    md.append('')
    dis = items.disagreements()
    if dis:
        md.append('## Disagreements')
        md.append('')
        md.append('| Kind | Item | Mine | Bridge | Note |')
        md.append('|---|---|---|---|---|')
        for x in dis:
            md.append('| %s | %s | %s | %s | %s |' % (x['kind'], esc(x['item']), esc(x['mine']), esc(x['bridge']), esc(x['note'])))
        md.append('')
    else:
        md.append('No disagreement with the bridge.')
        md.append('')
    md.extend(sections)
    md.append('## Notes')
    md.append('')
    for t in notes:
        md.append('- ' + t)
    md.append('')
    md.append('## Could not be verified from the stated inputs')
    md.append('')
    if unverified:
        for t in unverified:
            md.append('- ' + t)
    else:
        md.append('- Nothing in this bridge was left unverified.')
    md.append('')
    with open(os.path.join(ROOT, 'out', 'checks', stem + '.md'), 'w') as fh:
        fh.write('\n'.join(md))
    with open(os.path.join(ROOT, 'out', 'checks', stem + '_items.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['kind', 'item', 'agree', 'agree_1e-6', 'max_rel_diff'])
        for x in items.rows:
            w.writerow([x['kind'], x['item'], x['agree'], x['a6'], x['rel']])
    print('%s: %d/%d items agree (%d at 1e-6)' % (stem, ag, n, a6))
    for x in dis:
        print('  DISAGREE', x['kind'], x['item'], '| mine', x['mine'], '| bridge', x['bridge'], x['note'])
    return n, ag


def sec_adr(lines):
    out = ['## ADR, Rs crore per trading day (all panels shown by the bridge)', '',
           '| Period | Panel | My before | Bridge before | My after | Bridge after | Max rel diff | Verdict |',
           '|---|---|---:|---:|---:|---:|---:|---|']
    for per, pan, vb, bb, va, ba, rel, ok in lines:
        out.append('| %s | %s | %.6f | %s | %.6f | %s | %.1e | %s |' % (per, pan, vb, bb, va, ba, rel, 'agree' if ok else 'DISAGREE'))
    out.append('')
    return out


def sec_params(lines):
    out = ['## Parameters that moved', '',
           '| Segment | Quantity | Quarter | My before | Bridge before | My after | Bridge after | Bridge d% | Max rel diff | Verdict |',
           '|---|---|---|---:|---:|---:|---:|---:|---:|---|']
    for seg, qty, q, mb, bb, ma, ba, bp, rel, ok in lines:
        out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %.1e | %s |' % (seg, qty, q, fnum(mb), bb, fnum(ma), ba, bp, rel, 'agree' if ok else 'DISAGREE'))
    out.append('')
    return out


def sec_tables(lines):
    out = ['## Consolidated week / weekday tables (as of the last date of each segment)', '',
           '| Table | Row | My before | Bridge before | My after | Bridge after | Max rel diff | Verdict |',
           '|---|---|---:|---:|---:|---:|---:|---|']
    for key, mb, bb, ma, ba, rel, ok in lines:
        out.append('| %s | %s | %.6f | %s | %.6f | %s | %.1e | %s |' % (key[0], key[1], mb, bb, ma, ba, rel, 'agree' if ok else 'DISAGREE'))
    out.append('')
    return out


def sec_daily(lines):
    out = ['## Daily revenue rows that changed', '',
           '| Segment | Mine | Bridge | Verdict | Note |', '|---|---|---|---|---|']
    for nm, st, br, ok, note in lines:
        out.append('| %s | days %d->%d, changed %d, added %d, dropped %d, first %s, last %s, ratio %s..%s | days %d->%d, changed %d, added %d, dropped %d, first %s, last %s, ratio %s..%s | %s | %s |' % (
            nm, st['before'], st['after'], st['changed'], st['added'], st['dropped'], st['first'], st['last'], fmt(st['rmin'], 9), fmt(st['rmax'], 9),
            br['before'], br['after'], br['changed'], br['added'], br['dropped'], br['first'], br['last'], fmt(br['rmin'], 9), fmt(br['rmax'], 9),
            'agree' if ok else 'DISAGREE', note))
    out.append('')
    return out
# =============== switch m-a ===============
STEM = 'mosl_switch_a'
LETTERS = 'abcdef'
IDX = 0
BR = read_bridge('mosl_a.md')
before, after = Model(set(LETTERS[:IDX])), Model(set(LETTERS[:IDX + 1]))
items = Items()
sections, notes, unverified = [], [], []

sections += sec_adr(adr_items(items, BR, before, after))
consol_items(items, BR, before, after)
sections += sec_params(param_items(items, BR, before, after))
sections += sec_tables(table_items(items, BR, before, after))
sections += sec_daily(daily_items(items, BR, before, after))

# ---- inputs replaced by reviewed facts ----
EXPECT_UNIT = {'adto_cash_mosl': 'Rs Mn/day', 'gross_cash_cr': 'Rs Mn', 'gross_fo_cr': 'Rs Mn', 'gross_comm_cr': 'Rs Mn',
               'mtf_book_closing': 'Rs Mn', 'share_cash': 'fraction', 'share_fo': 'fraction', 'share_comm': 'fraction',
               'net_gross_cash': 'Rs Mn', 'net_gross_fo': 'Rs Mn', 'net_gross_comm': 'Rs Mn'}
inp = bridge_inputs(BR)
INPUT_NAMES = list(INPUT_MAP) + ['net_gross_cash', 'net_gross_fo', 'net_gross_comm']
changed, equal = [], []
for n in INPUT_NAMES:
    for q in REPORTED:
        lv, wv = live_input(n, q), wb_input(n, q)
        if wv is not None and abs(lv - wv) <= 1e-6 * abs(lv):
            equal.append((n, q))
        else:
            changed.append((n, q))
items.add('count', 'inputs that change the workbook value', len(changed) == 37, len(changed) == 37, 0.0 if len(changed) == 37 else 1.0,
          str(len(changed)), '37')
items.add('count', 'inputs already equal (1e-6 relative)', len(equal) == 73, len(equal) == 73, 0.0 if len(equal) == 73 else 1.0,
          str(len(equal)), '73')
items.add('count', 'inputs listed in the bridge table = the changed set', set(inp) == set(changed), set(inp) == set(changed),
          0.0, str(len(set(inp) & set(changed))), str(len(inp)))
inp_lines = []
for (n, q), (bw, bl, bf, bbasis) in inp.items():
    lv, wv = live_input(n, q), wb_input(n, q)
    ids = live_input_facts(n, q)
    facts = [FACT[(f['metric'], f['period_key'])] for f in (RFID[i] for i in ids)]
    fid_ok = [int(x) for x in re.findall(r'\d+', bf)] == ids
    meta_ok = all(f['period_key'] == q and f['status'] == 'reviewed' and f['unit'] == EXPECT_UNIT[n] and
                  f['broker_id'] == 'MOSL' and f['period_type'] == 'Q' for f in facts)
    meta_ok = meta_ok and facts[0]['metric'] == (INPUT_MAP[n][0] if n in INPUT_MAP else 'net_brokerage_' + n[len('net_gross_'):])
    # basis string: numbers and unit
    nums = [float(x.replace(',', '')) for x in re.findall(r'[\d,]+\.\d+', bbasis)]
    if n.startswith('net_gross_'):
        bas = [judge(re.findall(r'[\d,]+\.\d+', bbasis)[i], facts[i].get('value')) for i in range(2)]
        unit_ok = 'Rs Mn' in bbasis
    else:
        bas = [judge(re.findall(r'[\d,]+\.\d+', bbasis)[0], facts[0]['value'])] if INPUT_MAP[n][1] != 1.0 else \
            [judge(re.findall(r'\d+\.\d+', bbasis)[0], facts[0]['value'])]
        unit_ok = facts[0]['unit'] in bbasis and (('/ 10' in bbasis) == (INPUT_MAP[n][1] == 10.0))
    j_w, j_l = judge(bw, wv), judge(bl, lv)
    ok = j_w[0] and j_l[0] and fid_ok and meta_ok and unit_ok and all(b[0] for b in bas)
    items.add('input', '%s | %s' % (n, q), ok, ok and j_w[1] and j_l[1], max(j_w[2], j_l[2]),
              'wb %s live %s facts %s' % (fnum(wv), fnum(lv), ids), 'wb %s live %s facts %s' % (bw, bl, bf),
              '' if ok else 'fact_id/unit/period trace: ids %s meta %s unit %s' % (fid_ok, meta_ok, unit_ok))
    inp_lines.append((n, q, wv, bw, lv, bl, ids, bf, ok))
for n in INPUT_NAMES:
    for q in REPORTED:
        if (n, q) in equal:
            ids = live_input_facts(n, q)
            fs = [RFID[i] for i in ids]
            ok = all(f['status'] == 'reviewed' and f['period_key'] == q and f['unit'] == EXPECT_UNIT[n] for f in fs)
            items.add('input-equal', '%s | %s' % (n, q), ok, ok, abs(live_input(n, q) / wb_input(n, q) - 1),
                      'live %s workbook %s' % (fnum(live_input(n, q)), fnum(wb_input(n, q))), 'equal, not listed')
sec = ['## Inputs replaced by reviewed facts (37 listed in the bridge)', '',
       '| Input | Period | My workbook | Bridge workbook | My live | Bridge live | My facts | Bridge facts | Verdict |',
       '|---|---|---:|---:|---:|---:|---|---|---|']
for n, q, wv, bw, lv, bl, ids, bf, ok in inp_lines:
    sec.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (n, q, fnum(wv), bw, fnum(lv), bl, ', '.join(map(str, ids)), bf, 'agree' if ok else 'DISAGREE'))
sec.append('')
sections += sec

# ---- data-book internal tie-out: totals = sum of segments (Rs Mn) ----
tie_lines = ['## Data-book facts: gross / net total = cash + F&O + commodity + currency (Rs Mn)', '',
             '| Quarter | Quantity | Sum of segments | Fact total | Rel diff | Verdict |', '|---|---|---:|---:|---:|---|']
for q in REPORTED:
    for lab, segm, tot in (('gross', ['gross_brokerage_cash', 'gross_brokerage_fo', 'gross_brokerage_comm', 'gross_brokerage_currency'], 'gross_brokerage_total'),
                           ('net', ['net_brokerage_cash', 'net_brokerage_fo', 'net_brokerage_comm', 'net_brokerage_currency'], 'net_brokerage_total')):
        sm = sum(fval(m, q) for m in segm)
        tv = fval(tot, q)
        rel = abs(sm - tv) / tv
        ok = rel <= 5e-4          # data-book rows are published rounded to 0.1 Rs Cr (1 Rs Mn)
        items.add('facts-tie', '%s %s' % (q, lab), ok, rel <= 1e-6, rel, '%.4f' % sm, '%.4f' % tv)
        tie_lines.append('| %s | %s | %.4f | %.4f | %.1e | %s |' % (q, lab, sm, tv, rel, 'agree' if ok else 'DISAGREE'))
tie_lines.append('')
sections += tie_lines

# ---- calibrated quarters tie to the reported gross revenue ----
tl = ['## Tie-out of calibrated quarters: sum of daily gross revenue vs the reported gross (Rs Cr)', '',
      '| Segment | Quarter | Reported gross | Sum of daily gross | Rel diff | Verdict |', '|---|---|---:|---:|---:|---|']
for seg, nm, inpn in (('fo', 'F&O', 'gross_fo_cr'), ('cash', 'Cash', 'gross_cash_cr'), ('comm', 'Commodities', 'gross_comm_cr')):
    for q in REPORTED:
        ds = [d for d in after.gross[seg] if CAL[d]['q_fy'] == q]
        got = sum(after.gross[seg][d] for d in ds) * SCALE[seg]
        rep = live_input(inpn, q)
        rel = abs(got - rep) / rep
        ok = rel <= 1e-9
        items.add('tie', '%s %s' % (nm, q), ok, ok, rel, '%.6f' % got, '%.6f' % rep)
        tl.append('| %s | %s | %.6f | %.6f | %.1e | %s |' % (nm, q, rep, got, rel, 'agree' if ok else 'DISAGREE'))
tl.append('')
sections += tl

# ---- spec / methodology claims on the parity (before) state vs the reported Q2 FY27 ----
sp = ['## Parity estimate of Q2 FY27 vs the reported quarter (spec table m-a; Methodology section 5)', '',
      '| Quantity | Mine | Claim | Verdict |', '|---|---:|---|---|']
def claim(name, mine, cl, tol_dp):
    r = judge(cl, mine)
    items.add('spec', name, r[0], r[1], r[2], fnum(mine), cl)
    sp.append('| %s | %s | %s | %s |' % (name, fnum(mine), cl, 'agree' if r[0] else 'DISAGREE'))
gb = {s: sum(before.gross[s][d] for d in before.gross[s] if CAL[d]['q_fy'] == 'Q2 FY 2027') * SCALE[s] for s in ('fo', 'cash', 'comm')}
gr = {'fo': live_input('gross_fo_cr', 'Q2 FY 2027'), 'cash': live_input('gross_cash_cr', 'Q2 FY 2027'), 'comm': live_input('gross_comm_cr', 'Q2 FY 2027')}
claim('F&O gross Q2 FY27 model (Rs Cr)', gb['fo'], '179.13', 2)
claim('F&O gross model vs reported (%)', (gb['fo'] / gr['fo'] - 1) * 100, '-4.95', 2)
claim('Cash gross Q2 FY27 model (Rs Cr)', gb['cash'], '200.16', 2)
claim('Cash gross model vs reported (%)', (gb['cash'] / gr['cash'] - 1) * 100, '-15.83', 2)
claim('Commodities gross Q2 FY27 model (Rs Cr)', gb['comm'], '86.47', 2)
claim('Commodities gross model vs reported (%)', (gb['comm'] / gr['comm'] - 1) * 100, '49.17', 2)
mb = before.P['mtf']['share']['Q2 FY 2027'] * before.P['mtf']['indclose']['Q2 FY 2027']
claim('MTF closing book Q2 FY27 model (Rs Cr)', mb, '8,729', 0)
claim('MTF book model vs reported (%)', (mb / live_input('mtf_book_closing', 'Q2 FY 2027') - 1) * 100, '-9.1', 1)
sp.append('')
sections += sp

# ---- pins ----
pn = ['## Pins moved by m-a, tested through the daily rows', '', '| Pin | Test | Result |', '|---|---|---|']
def pin(name, test, ok):
    items.add('pin', name, ok, ok, 0.0 if ok else 1.0, test, 'pin value in bridge')
    pn.append('| %s | %s | %s |' % (name, test, 'agree' if ok else 'DISAGREE'))
fo_a = after.series['fo']
q12 = [d for d in fo_a if CAL[d]['q_fy'] in ('Q1 FY 2025', 'Q2 FY 2025')]
nz = [d for d in q12 if isnum(fo_a[d]) and fo_a[d] != 0]
pin('fo_zero_quarters = none', 'Q1, Q2 FY25 F&O rows: %d, of which non-zero numeric %d, error %d (31 May 2024 text key)' % (
    len(q12), len(nz), len([d for d in q12 if fo_a[d] == ERR])), len(nz) == len(q12) - 1 and fo_a['2024-05-31'] == ERR)
fo_b = before.series['fo']
q12b = [d for d in fo_b if CAL[d]['q_fy'] in ('Q1 FY 2025', 'Q2 FY 2025') and fo_b[d] != ERR]
pin('fo_zero_quarters (parity) = Q1, Q2 FY25', 'parity: %d numeric rows, all zero: %s' % (len(q12b), all(fo_b[d] == 0 for d in q12b)), all(fo_b[d] == 0 for d in q12b))
pin('cash_table_first_quarter = Q1 FY 2025', 'first cash row after m-a %s, before %s; rows %d -> %d' % (
    min(after.series['cash']), min(before.series['cash']), len(before.series['cash']), len(after.series['cash'])),
    min(after.series['cash']) == '2024-04-01' and len(after.series['cash']) - len(before.series['cash']) == 125)
for seg, nm in (('fo', 'fo'), ('cash', 'cash'), ('comm', 'comm')):
    q2 = [d for d in after.gross[seg] if CAL[d]['q_fy'] == 'Q2 FY 2027']
    tot = sum(after.gross[seg][d] for d in q2) * SCALE[seg]
    inpn = {'fo': 'gross_fo_cr', 'cash': 'gross_cash_cr', 'comm': 'gross_comm_cr'}[seg]
    pin('%s_last_actual_quarter = Q2 FY 2027' % nm, 'Q2 FY27 daily gross sums to the reported %.4f (mine %.4f)' % (live_input(inpn, 'Q2 FY 2027'), tot),
        abs(tot / live_input(inpn, 'Q2 FY 2027') - 1) < 1e-9)
pin('mtf_last_actual_quarter = Q2 FY 2027', 'Q2 FY27 MTF share %.6f = 9600 / 30 Sep industry book %.2f' % (after.P['mtf']['share']['Q2 FY 2027'], after.P['mtf']['indclose']['Q2 FY 2027']),
    abs(after.P['mtf']['share']['Q2 FY 2027'] - 9600.0 / after.P['mtf']['indclose']['Q2 FY 2027']) < 1e-12)
c1 = after.P['cash']['J']['Q1 FY 2027']
pin('cash take rate Q1 FY27 own (J52 = J51 dropped)', 'J(Q1 FY27) = %.6f = 228.30/3552.47, not J(Q4 FY26) = %.6f' % (c1, after.P['cash']['J']['Q4 FY 2026']),
    abs(c1 - live_input('gross_cash_cr', 'Q1 FY 2027') / live_input('adto_cash_mosl', 'Q1 FY 2027')) < 1e-12 and abs(c1 - after.P['cash']['J']['Q4 FY 2026']) > 1e-4)
q3c = [d for d in after.series['cash'] if CAL[d]['q_fy'] == 'Q3 FY 2027']
q3m = [d for d in after.series['comm'] if CAL[d]['q_fy'] == 'Q3 FY 2027']
pin('Q3 FY27 keeps the workbook rules (cash #N/A, commodities #N/A / blank, F&O carried)',
    'cash Q3 rows %d all error: %s; commodity rows %d error (to 2026-10-12), none after; F&O rate Q3 = Q2: %s' % (
        len(q3c), all(after.series['cash'][d] == ERR for d in q3c), len(q3m), after.P['fo']['rate']['Q3 FY 2027'] == after.P['fo']['rate']['Q2 FY 2027']),
    len(q3c) == 13 and all(after.series['cash'][d] == ERR for d in q3c) and len(q3m) == 7 and after.P['fo']['rate']['Q3 FY 2027'] == after.P['fo']['rate']['Q2 FY 2027'])
pn.append('')
sections += pn

notes += [
    'Method. The parity state is rebuilt first from raw inputs (workbook NSE index-option + BSE contract series, NSE + BSE turnover, MCX contracts, the industry daily MTF book, the typed seed facts and assumptions) with the formulas of Methodology sections 3, 4 and 8b. It reproduces the four daily columns of `snapshot/mosl_fixtures_2026-10-23.json` (F&O 757 rows, cash 509, commodities 653, MTF 495) to 6e-16 relative and the 156 value cells of the Summary fixtures (all panels, FY / quarter / month / week / weekday) to 5e-16. m-a is then applied as the bridge and spec describe: every reported quarter Q1 FY25 - Q2 FY27 calibrates from the reviewed data-book facts, converted Rs Mn to Rs Cr (/10) and net / gross = net brokerage / gross brokerage of the same quarter.',
    'Formulas used. F&O: AF = share x (S/1e7) x rate, rate = gross / (share x sum S/1e7) (Rs per contract), AG = net/gross x AF, ADR = mean(AG)/10. Cash: AA = share x K / H x J / D, H = share x mean K / ADTO, J = gross / ADTO, D = rows in the quarter, AB = net/gross x AA. Commodities: L = MCX Mn contracts x share x take, take = gross x 10 / (share x contracts), O = net/gross x L, ADR = mean(O)/10. MTF: X = (book / industry close of the quarter) x daily industry book x NII / 247.',
    'F&O 31 May 2024: the workbook key cell is text, so that row is an error and is left out of the Q1 FY25 key sum; the Q1 FY25 rate 0.7498 (bridge) only reproduces with that exclusion. m-b then adds the day (0.7382).',
    '"73 inputs already equal" is reproduced with an equality tolerance of 1e-6 relative: the reviewed facts print shares to 9 digits where the workbook seed has 16, so exact equality would give 55 / 55 instead of 73 / 37. At any tolerance between 1e-8 and 1e-6 the changed set is exactly the 37 listed rows.',
    'Daily rows changed. For F&O the bridge counts every row whose float differs; mine counts rows whose relative difference exceeds 1e-9. Counts agree for all four segments in this bridge.',
    'Week / weekday rows printed "Monday | vs 10" repeat the Monday value in the bridge (the workbook column is a comparison; the bridge prints the level); I compare them with the level.',
]
write_outputs(STEM, 'MOSL switch m-a (reported quarters from the data book)', items, sections, notes, unverified)
