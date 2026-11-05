"""PAT model for Angel One and Groww (PLAN 5.7): quarterly P&L build → FY27E, FY28E → EPS → valuation.

Built on the workbook's `PAT predictor Q2FY27` (quarterly cost and revenue rules) and the `Angel One - ADR
model (A+B)` / `Groww - ADR Model` sheets (FY28 ADR growth, P/E bands, discounting), with the fixes AB
approved on 5 Nov 2026 (docs/PAT_Model.md):
  - reported quarters are the filed figures; the rest of FY27 is projected, so FY27E = reported + projected
  - broking, MTF and cash revenue come from the engine's published daily ADR (window per broker)
  - finance cost follows the MTF book implied by that MTF revenue: previous period + funding rate ×
    (book growth − retained share of the previous period's PAT), the same rule in FY27 and FY28
  - fees & commission expense (Angel) = its ratio to broking revenue (last 4 reported quarters) × projected
    broking revenue, in every forecast period; Groww's other expenses scale with broking the same way
  - Groww's other income is its own filed figure
Every number is in Rs Cr (per-share figures in Rs). Each output line carries its rule in words.

Inputs (all plain data, no I/O here):
  facts:   sb_disclosure_facts rows (pl_* lines, revmix_*, avg_funding_book, total_income, shares_outstanding_cr)
  daily:   sb_daily_revenue rows of the broker's ADR run (trade_date, segment, revenue_cr, regime)
  assume:  {key: row} for the broker, '*' rows included (seed/pat_assumptions.json or sb_assumptions)
  close:   latest share price (Rs) and its date
"""
from __future__ import annotations

import datetime as dt
from collections import defaultdict

FY27_Q = ('Q1 FY 2027', 'Q2 FY 2027', 'Q3 FY 2027', 'Q4 FY 2027')
SCENARIOS = ('bear', 'base', 'bull')
BROKING_SEGS = ('fo', 'cash', 'comm')
REVENUE_LINES = {
    'ANGELONE': ('broking', 'depository', 'distribution', 'mtf', 'treasury', 'other'),
    'GROWW': ('broking', 'mtf', 'float', 'lending', 'other_operating', 'other'),
}
COST_LINES = {
    'ANGELONE': ('finance', 'fees_commission', 'employee', 'depreciation', 'other_expenses', 'impairment'),
    'GROWW': ('finance', 'employee', 'depreciation', 'other_expenses'),
}
LABELS = {
    'broking': 'Broking revenue', 'depository': 'Depository income', 'distribution': 'Distribution income',
    'mtf': 'MTF income', 'treasury': 'Other interest income (treasury)', 'other': 'Other income',
    'float': 'Float income', 'lending': 'PL + LAS (lending)', 'other_operating': 'Other operating income',
    'total_income': 'Total income', 'finance': 'Finance cost', 'fees_commission': 'Fees & commission expense',
    'employee': 'Employee cost (incl. ESOP)', 'depreciation': 'Depreciation', 'other_expenses': 'Other expenses',
    'impairment': 'Impairment', 'total_costs': 'Total costs', 'pbt': 'PBT', 'tax': 'Tax', 'pat': 'PAT',
    'pat_margin': 'PAT margin', 'mtf_book': 'MTF book (average)', 'trading_days': 'Trading days',
    'adr_broking': 'Broking ADR', 'adr_mtf': 'MTF ADR', 'eps': 'EPS', 'pe': 'P/E', 'price_fwd': 'Price (P/E × EPS)',
    'price_disc': 'Discounted', 'target_today': 'Target price today', 'upside': 'Upside vs close',
    'shares': 'Shares outstanding', 'close': 'Share price (close)',
}


class PatInputMissing(RuntimeError):
    pass


# ── periods ──────────────────────────────────────────────────────────────────
def q_of(iso):
    d = dt.date.fromisoformat(iso)
    fy = d.year + 1 if d.month >= 4 else d.year
    return f'Q{(d.month - 4) % 12 // 3 + 1} FY {fy}'


def q_prev(q, n=1):
    k, fy = int(q[1]), int(q[-4:])
    i = fy * 4 + k - 1 - n
    return f'Q{i % 4 + 1} FY {i // 4}'


def q_end(q):
    k, fy = int(q[1]), int(q[-4:])
    m = {1: (fy - 1, 6, 30), 2: (fy - 1, 9, 30), 3: (fy - 1, 12, 31), 4: (fy, 3, 31)}[k]
    return dt.date(*m)


def weekdays(a, b):
    """Weekdays in (a, b] (dates)."""
    n, d = 0, a + dt.timedelta(days=1)
    while d <= b:
        n += d.weekday() < 5
        d += dt.timedelta(days=1)
    return n


# ── assumptions ──────────────────────────────────────────────────────────────
class Assume:
    def __init__(self, rows, broker):
        self.rows = {}
        for r in rows:
            if r['broker_id'] in ('*', broker):
                if r['key'] not in self.rows or r['broker_id'] == broker:
                    self.rows[r['key']] = r

    def __call__(self, key, default=None):
        r = self.rows.get(key)
        if r is None:
            if default is None:
                raise PatInputMissing(f'assumption {key} not set')
            return default
        return r['value'] if r.get('value') is not None else r.get('value_text')

    def ref(self, key):
        r = self.rows.get(key)
        return r and r.get('source_ref')

    def pe(self):
        return [float(x) for x in str(self('pat_pe')).split(',')]


# ── reported quarters from facts ─────────────────────────────────────────────
def _cr(f):
    return f['value'] / 10 if f['unit'] == 'Rs Mn' else f['value']


def fact_table(facts, broker):
    """{(period_key, metric): value} in Rs Cr (fractions stay fractions); the latest reviewed / staged row wins."""
    t = {}
    for f in facts:
        if f.get('broker_id', broker) != broker or f.get('period_key') is None:
            continue
        v = f['value'] if f['unit'] in ('fraction', 'days', 'crore shares', 'count') else _cr(f)
        t[(f['period_key'], f['metric'])] = v
    return t


def reported_quarter(t, broker, q, yield_):
    """The filed P&L of quarter q split into the model's lines, or None if q is not reported."""
    g = lambda m: t.get((q, m))
    ti = g('pl_total_income')
    if ti is None:
        return None
    mix = lambda m: t.get((q, m))
    # commodity broking counts as 0 before a broker reported it (Groww: from Q2 FY26)
    broking_share = mix('revmix_broking') or (
        mix('revmix_fo') + mix('revmix_cash') + (mix('revmix_comm') or 0.0)
        if mix('revmix_fo') is not None and mix('revmix_cash') is not None else None)
    if broking_share is None:
        raise PatInputMissing(f'{broker} {q}: no broking revenue mix')
    L = {'broking': broking_share * ti, 'total_income': ti}
    if broker == 'ANGELONE':
        book = g('avg_funding_book')                                  # Rs Cr (filed in Rs Mn)
        if book is None:
            raise PatInputMissing(f'{broker} {q}: no average client funding book')
        L['mtf'] = book * yield_ / 4
        L['treasury'] = g('pl_interest_income') - L['mtf']
        for line, m in (('depository', 'revmix_dep'), ('distribution', 'revmix_dist')):
            L[line] = (mix(m) or 0.0) * ti
        L['other'] = ti - L['broking'] - L['depository'] - L['distribution'] - g('pl_interest_income')
        L['fees_commission'] = g('pl_fee_commission_expense')
        L['impairment'] = g('pl_impairment')
        L['employee'] = g('pl_employee') + (g('pl_esop') or 0.0)
    else:
        for line, m in (('mtf', 'revmix_mtf'), ('float', 'revmix_float'), ('lending', 'revmix_plas')):
            if mix(m) is None:
                raise PatInputMissing(f'{broker} {q}: no {m}')
            L[line] = mix(m) * ti
        L['other'] = g('pl_other_income')
        L['other_operating'] = 0.0          # the residual, set below
        L['employee'] = g('pl_employee')
    L.update(finance=g('pl_finance_cost'), depreciation=g('pl_depreciation'), other_expenses=g('pl_other_expenses'),
             total_costs=g('pl_total_expenses'), pbt=g('pl_pbt'), tax=g('pl_tax'), pat=g('pl_pat'))
    L['mtf_book'] = L['mtf'] / (yield_ / 4)
    if broker == 'GROWW':   # Groww's mix is of total income: keep the lines adding up to it
        L['other_operating'] += ti - sum(L[k] for k in REVENUE_LINES['GROWW'])
    return L


# ── ADR from the engine's daily rows ─────────────────────────────────────────
class Adr:
    def __init__(self, daily, mtf_segment='mtf_gross'):
        by = defaultdict(dict)
        for r in daily:
            if r.get('revenue_cr') is not None:
                by[r['segment']][r['trade_date']] = r['revenue_cr']
        need = list(BROKING_SEGS) + [mtf_segment]
        missing = [s for s in need if not by[s]]
        if missing:
            raise PatInputMissing(f'daily ADR rows missing for {missing}')
        self.days = sorted(set(by['fo']) & set(by['cash']) & set(by[mtf_segment]))
        self.seg = {'broking': {d: sum(by[s].get(d, 0.0) for s in BROKING_SEGS) for d in self.days},
                    'cash': {d: by['cash'][d] for d in self.days},
                    'mtf': {d: by[mtf_segment][d] for d in self.days}}
        self.as_of = self.days[-1]

    def window(self, what, n):
        ds = self.days[-n:]
        return sum(self.seg[what][d] for d in ds) / len(ds)

    def in_quarter(self, what, q):
        ds = [d for d in self.days if q_of(d) == q]
        return sum(self.seg[what][d] for d in ds), len(ds)


def new_borrowing(book, prev_book, retained):
    """Borrowing needed for the MTF book: growth not covered by retained PAT (a surplus pays no interest back,
    so it stops at 0); a shrinking book repays borrowing one for one."""
    growth = book - prev_book
    return growth if growth <= 0 else max(growth - retained, 0.0)


# ── the model ────────────────────────────────────────────────────────────────
def build(broker, facts, daily, assumptions, close, shares=None):
    A = Assume(assumptions, broker)
    y = A('pat_mtf_yield')
    t = fact_table(facts, broker)
    adr = Adr(daily)
    rules = {}                                     # (period, line) → rule text
    Q = {}                                         # period → lines
    hist = {}
    skipped = {}
    for back in range(8, 0, -1):                   # reported quarters before FY27 (for averages and same-quarter-LY)
        q = q_prev('Q1 FY 2027', back)
        try:
            r = reported_quarter(t, broker, q, y)
        except PatInputMissing as e:               # an older quarter without a full split: not used
            skipped[q] = str(e)
            continue
        if r:
            hist[q] = r
    for q in FY27_Q:
        r = reported_quarter(t, broker, q, y)
        if r:
            hist[q] = r
            Q[q] = dict(r, regime='actual')
            for k in r:
                rules[(q, k)] = 'filed'
    reported = [q for q in sorted(hist, key=lambda q: (q[-4:], q[1]))]
    last4 = reported[-4:]
    if len(last4) < 4:
        raise PatInputMissing(f'{broker}: fewer than 4 reported quarters')
    ratio = lambda num: sum(hist[q][num] for q in last4) / sum(hist[q]['broking'] for q in last4)
    fee_ratio = ratio('fees_commission') if broker == 'ANGELONE' else None
    oexp_ratio = ratio('other_expenses') if broker == 'GROWW' else None
    prev_fy = [q_prev('Q1 FY 2027', k) for k in (4, 3, 2, 1)]          # Q1..Q4 FY26
    if not all(q in hist for q in prev_fy):
        raise PatInputMissing(f'{broker}: FY26 quarters incomplete: {[q for q in prev_fy if q not in hist]}')
    other_avg = sum(hist[q]['other'] for q in last4) / 4

    # FY27 trading days left (workbook 247 basis), split by weekdays
    fy_days = A('pat_fy27_trading_days')
    traded = sum(1 for d in adr.days if d >= '2026-04-01')
    left = max(fy_days - traded, 0)
    asof = dt.date.fromisoformat(adr.as_of)
    proj_q = [q for q in FY27_Q if q not in Q]
    wd = {q: weekdays(max(asof, q_end(q_prev(q))), q_end(q)) for q in proj_q}
    tot_wd = sum(wd.values()) or 1
    w27 = int(A('pat_adr_window_fy27'))
    adr_b, adr_m, adr_c = adr.window('broking', w27), adr.window('mtf', w27), adr.window('cash', w27)
    # quarterly ADR growth path: the current quarter's remaining days at the window ADR, then × (1 + g) a quarter
    g_q = A('pat_adr_qoq_growth')
    first_proj = q_of(adr.as_of) if q_of(adr.as_of) in FY27_Q else None
    step = lambda q: 0 if first_proj is None else (int(q[-4:]) * 4 + int(q[1])) - (int(first_proj[-4:]) * 4 + int(first_proj[1]))

    tax, ret, rate = A('pat_tax_rate'), A('pat_retention'), A('pat_funding_rate')
    for q in proj_q:
        p = Q.get(q_prev(q)) or hist[q_prev(q)]
        ly = hist[q_prev(q, 4)]
        rem = left * wd[q] / tot_wd
        so_far = {k: adr.in_quarter(k, q) for k in ('broking', 'mtf', 'cash')}
        L = {'trading_days': so_far['broking'][1] + rem}
        f = (1 + g_q) ** step(q)
        L['broking'] = so_far['broking'][0] + rem * adr_b * f
        L['mtf'] = so_far['mtf'][0] + rem * adr_m * f
        cash = so_far['cash'][0] + rem * adr_c * f
        grow = f' × (1 + {g_q:.1%})^{step(q)}' if step(q) else ''
        done = f'engine daily {{}} to {adr.as_of} ({so_far["broking"][1]} days) + ' if so_far['broking'][1] else ''
        rules[(q, 'broking')] = done.format('broking') + f'{rem:.1f} days × {w27}-day ADR {adr_b:.3f}{grow}'
        rules[(q, 'mtf')] = done.format('MTF') + f'{rem:.1f} days × {w27}-day ADR {adr_m:.3f}{grow}'
        if broker == 'ANGELONE':
            L['depository'] = A('pat_dep_share_of_cash') * cash
            rules[(q, 'depository')] = f'{A("pat_dep_share_of_cash"):.0%} × cash broking {cash:.1f}'
            L['distribution'] = p['distribution'] * (1 + A('pat_dist_cqgr'))
            rules[(q, 'distribution')] = f'previous quarter × (1 + {A("pat_dist_cqgr"):.0%})'
            L['treasury'] = p['treasury'] * (1 + A('pat_treasury_cqgr'))
            rules[(q, 'treasury')] = f'previous quarter × (1 + {A("pat_treasury_cqgr"):.0%})'
        else:
            for k in ('lending', 'other_operating'):
                L[k] = p[k] * (1 + A('pat_dist_cqgr'))
                rules[(q, k)] = f'previous quarter × (1 + {A("pat_dist_cqgr"):.0%})'
            L['float'] = p['float'] * L['broking'] / p['broking']
            rules[(q, 'float')] = 'previous quarter × broking growth'
        L['other'] = other_avg
        rules[(q, 'other')] = 'average of the last 4 reported quarters'
        L['total_income'] = sum(L[k] for k in REVENUE_LINES[broker])
        # costs
        L['mtf_book'] = L['mtf'] / (y / 4)
        extra = new_borrowing(L['mtf_book'], p['mtf_book'], ret * p['pat'])
        L['finance'] = max(p['finance'] + rate / 4 * extra, 0.0)
        rules[(q, 'finance')] = (f'previous {p["finance"]:.1f} + {rate:.1%}/4 × new borrowing {extra:,.0f} (book {L["mtf_book"]:,.0f} '
                                 f'− {p["mtf_book"]:,.0f}, less {ret:.0%} of previous PAT {p["pat"]:.1f}, not below 0)')
        if broker == 'ANGELONE':
            L['fees_commission'] = fee_ratio * L['broking']
            rules[(q, 'fees_commission')] = f'{fee_ratio:.2%} of broking (last 4 reported quarters)'
            L['employee'] = sum(hist[x]['employee'] for x in prev_fy) / 4 * (1 + A('pat_employee_growth'))
            rules[(q, 'employee')] = f'FY26 quarterly average × (1 + {A("pat_employee_growth"):.0%})'
            L['depreciation'] = ly['depreciation'] * (1 + A('pat_depreciation_growth'))
            rules[(q, 'depreciation')] = f'same quarter last year × (1 + {A("pat_depreciation_growth"):.0%})'
            L['other_expenses'] = ly['other_expenses'] * (1 + A('pat_other_exp_growth'))
            rules[(q, 'other_expenses')] = f'same quarter last year × (1 + {A("pat_other_exp_growth"):.0%})'
            L['impairment'] = sum(hist[x]['impairment'] for x in prev_fy) / 4 * (1 + A('pat_impairment_growth'))
            rules[(q, 'impairment')] = f'FY26 quarterly average × (1 + {A("pat_impairment_growth"):.0%})'
        else:
            q4 = hist[prev_fy[-1]]
            L['employee'] = q4['employee'] * (1 + A('pat_employee_growth'))
            rules[(q, 'employee')] = f'Q4 FY26 × (1 + {A("pat_employee_growth"):.0%})'
            L['depreciation'] = q4['depreciation'] * (1 + A('pat_depreciation_growth'))
            rules[(q, 'depreciation')] = f'Q4 FY26 × (1 + {A("pat_depreciation_growth"):.0%})'
            L['other_expenses'] = oexp_ratio * L['broking']
            rules[(q, 'other_expenses')] = f'{oexp_ratio:.2%} of broking (last 4 reported quarters)'
        L['total_costs'] = sum(L[k] for k in COST_LINES[broker])
        L['pbt'] = L['total_income'] - L['total_costs']
        L['tax'] = tax * L['pbt']
        L['pat'] = L['pbt'] - L['tax']
        L['regime'] = 'projected'
        Q[q] = L

    # FY27 = the four quarters
    fy27 = {k: sum(Q[q][k] for q in FY27_Q) for k in REVENUE_LINES[broker] + COST_LINES[broker] +
            ('total_income', 'total_costs', 'pbt', 'tax', 'pat')}
    fy27['mtf_book'] = sum(Q[q]['mtf_book'] for q in FY27_Q) / 4
    fy27['regime'] = 'projected' if proj_q else 'actual'

    # FY28: the four quarters continue the quarterly ADR growth path (days split equally); every cost linked as in FY27
    d28 = A('pat_fy28_trading_days')
    fy28_q = ('Q1 FY 2028', 'Q2 FY 2028', 'Q3 FY 2028', 'Q4 FY 2028')
    k28 = [step(q) if first_proj else 0 for q in fy28_q]
    path = sum((1 + g_q) ** k for k in k28) / 4                     # average growth factor over FY28
    b28, m28 = adr_b * path, adr_m * path
    F = {'trading_days': d28, 'adr_broking': b28, 'adr_mtf': m28, 'broking': b28 * d28, 'mtf': m28 * d28}
    expo = f'(1 + {g_q:.1%})^{k28[0]}..^{k28[-1]}'
    rules[('FY 2028', 'broking')] = (f'{w27}-day broking ADR {adr_b:.3f} × average of {expo} = {b28:.3f} a day × {d28} days')
    rules[('FY 2028', 'mtf')] = (f'{w27}-day MTF ADR {adr_m:.3f} × average of {expo} = {m28:.3f} a day × {d28} days')
    rules[('FY 2028', 'adr_broking')] = rules[('FY 2028', 'broking')]
    gd, gt = A('pat_dist_growth_fy28'), A('pat_treasury_growth_fy28')
    if broker == 'ANGELONE':
        F['depository'] = fy27['depository'] * F['broking'] / fy27['broking']
        rules[('FY 2028', 'depository')] = 'FY27 × broking growth'
        F['distribution'] = fy27['distribution'] * (1 + gd)
        rules[('FY 2028', 'distribution')] = f'FY27 × (1 + {gd:.0%})'
        F['treasury'] = fy27['treasury'] * (1 + gt)
        rules[('FY 2028', 'treasury')] = f'FY27 × (1 + {gt:.0%})'
    else:
        for k in ('lending', 'other_operating'):
            F[k] = fy27[k] * (1 + gd)
            rules[('FY 2028', k)] = f'FY27 × (1 + {gd:.0%})'
        F['float'] = fy27['float'] * (1 + gt)
        rules[('FY 2028', 'float')] = f'FY27 × (1 + {gt:.0%})'
    F['other'] = fy27['other']
    rules[('FY 2028', 'other')] = 'FY27'
    F['total_income'] = sum(F[k] for k in REVENUE_LINES[broker])
    F['mtf_book'] = F['mtf'] / y
    extra = new_borrowing(F['mtf_book'], fy27['mtf_book'], ret * fy27['pat'])
    F['finance'] = max(fy27['finance'] + rate * extra, 0.0)
    rules[('FY 2028', 'finance')] = (f'FY27 {fy27["finance"]:.1f} + {rate:.1%} × new borrowing {extra:,.0f} (book {F["mtf_book"]:,.0f} '
                                     f'− {fy27["mtf_book"]:,.0f}, less {ret:.0%} of FY27 PAT {fy27["pat"]:.1f}, not below 0)')
    if broker == 'ANGELONE':
        F['fees_commission'] = fee_ratio * F['broking']
        rules[('FY 2028', 'fees_commission')] = f'{fee_ratio:.2%} of broking'
        for k, g in (('employee', 'pat_employee_growth_fy28'), ('depreciation', 'pat_depreciation_growth_fy28'),
                     ('other_expenses', 'pat_other_exp_growth_fy28'), ('impairment', 'pat_impairment_growth')):
            F[k] = fy27[k] * (1 + A(g))
            rules[('FY 2028', k)] = f'FY27 × (1 + {A(g):.0%})'
    else:
        for k, g in (('employee', 'pat_employee_growth_fy28'), ('depreciation', 'pat_depreciation_growth_fy28')):
            F[k] = fy27[k] * (1 + A(g))
            rules[('FY 2028', k)] = f'FY27 × (1 + {A(g):.0%})'
        F['other_expenses'] = oexp_ratio * F['broking']
        rules[('FY 2028', 'other_expenses')] = f'{oexp_ratio:.2%} of broking'
    F['total_costs'] = sum(F[k] for k in COST_LINES[broker])
    F['pbt'] = F['total_income'] - F['total_costs']
    F['tax'] = tax * F['pbt']
    F['pat'] = F['pbt'] - F['tax']
    F['regime'] = 'projected'
    fy27.update(adr_broking=adr_b, adr_mtf=adr_m)

    # valuation
    shares_cr = shares if shares is not None else t.get((None, 'shares_outstanding_cr'))
    if not shares_cr:
        raise PatInputMissing(f'{broker}: shares outstanding not set')
    pe = A.pe()
    disc, today = A('pat_discount_fwd'), A('pat_discount_today')
    val = {}
    for period, L in (('FY 2027', fy27), ('FY 2028', F)):
        L['pat_margin'] = L['pat'] / L['total_income']
        eps = L['pat'] / shares_cr
        for s, x in zip(SCENARIOS, pe):
            price = x * eps
            d1 = price / (1 + disc)
            tgt = d1 / (1 + today) if period == 'FY 2028' else d1
            val[(period, s)] = dict(eps=eps, pe=x, price_fwd=price, price_disc=d1, target_today=tgt,
                                    upside=tgt / close['price'] - 1)
    return dict(broker=broker, as_of=adr.as_of, quarters=Q, fy27=fy27, fy28=F, valuation=val, rules=rules,
                shares_cr=shares_cr, close=close, ratios=dict(fees_to_broking=fee_ratio, other_exp_to_broking=oexp_ratio,
                last4=last4), skipped=skipped, assumptions={k: (A(k), A.ref(k)) for k in A.rows})


def rows(model, run_id):
    """sb_pat_lines rows: one per (period, line, scenario)."""
    out, order = [], 0
    b = model['broker']
    lines = (('trading_days', 'adr_broking', 'adr_mtf') + REVENUE_LINES[b] + ('total_income', 'mtf_book') +
             COST_LINES[b] + ('total_costs', 'pbt', 'tax', 'pat', 'pat_margin'))
    periods = [(q, model['quarters'][q]) for q in FY27_Q] + [('FY 2027', model['fy27']), ('FY 2028', model['fy28'])]
    for line in lines:
        order += 1
        for pk, L in periods:
            if line not in L or L[line] is None:
                continue
            unit = 'fraction' if line == 'pat_margin' else 'days' if line == 'trading_days' else 'Rs Cr'
            if line.startswith('adr_'):
                unit = 'Rs Cr / day'
            out.append(dict(run_id=run_id, broker_id=b, period_key=pk, line=line, label=LABELS[line], scenario='',
                            value=float(L[line]), unit=unit, regime=L['regime'], rule=model['rules'].get((pk, line)),
                            sort_order=order))
    for (pk, s), v in model['valuation'].items():
        for k, x in v.items():
            out.append(dict(run_id=run_id, broker_id=b, period_key=pk, line=k, label=LABELS[k], scenario=s, value=float(x),
                            unit={'pe': 'x', 'upside': 'fraction'}.get(k, 'Rs'), regime='projected',
                            rule=None, sort_order=900 + list(LABELS).index(k)))
    # the divisor and the price behind the valuation lines, once per valuation period
    for pk in sorted({pk for pk, _ in model['valuation']}):
        out.append(dict(run_id=run_id, broker_id=b, period_key=pk, line='shares', label=LABELS['shares'], scenario='',
                        value=float(model['shares_cr']), unit='crore shares', regime='actual',
                        rule='shares outstanding (filings)', sort_order=990))
        out.append(dict(run_id=run_id, broker_id=b, period_key=pk, line='close', label=LABELS['close'], scenario='',
                        value=float(model['close']['price']), unit='Rs', regime='actual',
                        rule=f"close on {model['close']['date']} (sb_share_prices)", sort_order=991))
    return out
