"""PAT predictor recompute kit: the reference the dashboard page ports line for line (contract of 10 Nov 2026).

The page reads the published sb_pat_lines rows of a broker, lets the reader edit four inputs (QoQ ADR growth g, the
P/E per scenario, the FY28 → FY27 discount and the FY27 → today discount) and recomputes every g-dependent line from
the kit rows (period 'inputs', lines k_* / in_*; per quarter k_step, k_sofar_*, k_rem_days). At the published
defaults recompute() reproduces every published P&L, top-block, build-up and valuation line of pat.build() / rows().

    kit = kit_from_rows(rows)                    # rows as /api/brokers?view=pat returns them
    out = recompute(kit, g, pe, disc, today, gm)  # {(period_key, line, scenario): value}

g is the QoQ growth of broking (and cash) ADR, gm that of MTF ADR (AB, 13 Nov 2026: two inputs instead of one; gm
None = the published in_mtf_qoq_growth, or g for a run published before that row).

Lines that do not depend on g (Angel: distribution, treasury, other and the cost lines other than finance and fees &
commission; Groww: lending, other operating, other, employee, depreciation; FY 2026; trading days; shares; close) are
the published values. No I/O here.
"""
from __future__ import annotations

SCENARIOS = ('bear', 'base', 'bull')
FY27_Q = ('Q1 FY 2027', 'Q2 FY 2027', 'Q3 FY 2027', 'Q4 FY 2027')
FY28_Q = ('Q1 FY 2028', 'Q2 FY 2028', 'Q3 FY 2028', 'Q4 FY 2028')
REVENUE_LINES = {
    'ANGELONE': ('broking', 'depository', 'distribution', 'mtf', 'treasury', 'other'),
    'GROWW': ('broking', 'mtf', 'float', 'lending', 'other_operating', 'other'),
}
COST_LINES = {
    'ANGELONE': ('finance', 'fees_commission', 'employee', 'depreciation', 'other_expenses', 'impairment'),
    'GROWW': ('finance', 'employee', 'depreciation', 'other_expenses'),
}
G_INDEPENDENT = {   # projected-quarter lines taken as published
    'ANGELONE': ('distribution', 'treasury', 'other', 'employee', 'depreciation', 'other_expenses', 'impairment'),
    'GROWW': ('lending', 'other_operating', 'other', 'employee', 'depreciation'),
}
TREASURY = {'ANGELONE': 'treasury', 'GROWW': 'float'}
TOTALS = ('total_income', 'total_costs', 'pbt', 'tax', 'pat')


def qkey(q):
    return int(q[-4:]) * 4 + int(q[1])


def new_borrowing(book, prev_book, retained):
    growth = book - prev_book
    return growth if growth <= 0 else max(growth - retained, 0.0)


def kit_from_rows(rows):
    """The published rows → the kit: every value by (period_key, line, scenario), the inputs, the projected FY27
    quarters (those with k_rem_days), the build-up quarters (those with adr_consol) and the default inputs."""
    V = {(r['period_key'], r['line'], r.get('scenario') or ''): float(r['value']) for r in rows}
    inp = {line: v for (pk, line, s), v in V.items() if pk == 'inputs' and s == ''}
    broker = 'ANGELONE' if 'k_fee_ratio' in inp else 'GROWW'
    proj = sorted({pk for (pk, line, _) in V if line == 'k_rem_days'}, key=qkey)
    buildup = sorted({pk for (pk, line, _) in V if line == 'adr_consol' and pk.startswith('Q')}, key=qkey)
    step = {pk: v for (pk, line, _), v in V.items() if line == 'k_step'}
    pe = [V[('inputs', 'in_pe', s)] for s in SCENARIOS]
    return dict(broker=broker, values=V, inputs=inp, proj=proj, buildup=buildup, step=step,
                defaults=dict(g=inp['in_qoq_growth'], gm=inp.get('in_mtf_qoq_growth', inp['in_qoq_growth']), pe=pe,
                              disc=inp['in_discount_fwd'], today=inp['in_discount_today']))


def recompute(kit, g, pe, disc, today, gm=None):
    """Every published line (not the inputs) at broking growth g, MTF growth gm, P/E [bear, base, bull] and the two
    discount rates."""
    b, V, k = kit['broker'], kit['values'], kit['inputs']
    if gm is None:
        gm = k.get('in_mtf_qoq_growth', g)
    pub = lambda pk, line: V[(pk, line, '')]
    out = {key: v for key, v in V.items() if key[0] != 'inputs' and not key[1].startswith(('k_', 'in_'))}
    b0, m0, c0 = k['k_adr_broking0'], k['k_adr_mtf0'], k['k_adr_cash0']
    tax, ret, rate, y = k['k_tax'], k['k_retention'], k['k_funding_rate'], k['k_mtf_yield']

    # projected FY27 quarters, in order
    prev = dict(finance=k.get('k_prev_finance'), mtf_book=k.get('k_prev_mtf_book'), pat=k.get('k_prev_pat'),
                broking=k.get('k_prev_broking'), float=k.get('k_prev_float'))
    for q in kit['proj']:
        f, fm = (1 + g) ** kit['step'][q], (1 + gm) ** kit['step'][q]
        rem = pub(q, 'k_rem_days')
        L = {}
        L['broking'] = pub(q, 'k_sofar_broking') + rem * b0 * f
        L['mtf'] = pub(q, 'k_sofar_mtf') + rem * m0 * fm
        cash = pub(q, 'k_sofar_cash') + rem * c0 * f
        if b == 'ANGELONE':
            L['depository'] = k['k_dep_share_of_cash'] * cash
        else:
            L['float'] = prev['float'] * L['broking'] / prev['broking']
        for line in G_INDEPENDENT[b]:
            L[line] = pub(q, line)
        L['total_income'] = sum(L[x] for x in REVENUE_LINES[b])
        L['mtf_book'] = L['mtf'] / (y / 4)
        L['finance'] = max(prev['finance'] + rate / 4 * new_borrowing(L['mtf_book'], prev['mtf_book'], ret * prev['pat']), 0.0)
        if b == 'ANGELONE':
            L['fees_commission'] = k['k_fee_ratio'] * L['broking']
        else:
            L['other_expenses'] = k['k_oexp_ratio'] * L['broking']
        L['total_costs'] = sum(L[x] for x in COST_LINES[b])
        L['pbt'] = L['total_income'] - L['total_costs']
        L['tax'] = tax * L['pbt']
        L['pat'] = L['pbt'] - L['tax']
        for line, v in L.items():
            out[(q, line, '')] = v
        prev = L

    # FY27 = the four quarters (filed ones as published)
    Y27 = {line: sum(out[(q, line, '')] for q in FY27_Q) for line in REVENUE_LINES[b] + COST_LINES[b] + TOTALS}
    Y27['mtf_book'] = sum(out[(q, 'mtf_book', '')] for q in FY27_Q) / 4

    # FY28
    path = sum((1 + g) ** kit['step'][q] for q in FY28_Q) / 4
    path_m = sum((1 + gm) ** kit['step'][q] for q in FY28_Q) / 4
    b28, m28 = b0 * path, m0 * path_m
    d28 = k['k_fy28_days']
    gd, gt = k['k_dist_growth_fy28'], k['k_treasury_growth_fy28']
    F = dict(adr_broking=b28, adr_mtf=m28, broking=b28 * d28, mtf=m28 * d28)
    if b == 'ANGELONE':
        F['depository'] = Y27['depository'] * F['broking'] / Y27['broking']
        F['distribution'] = Y27['distribution'] * (1 + gd)
        F['treasury'] = Y27['treasury'] * (1 + gt)
    else:
        F['lending'] = Y27['lending'] * (1 + gd)
        F['other_operating'] = Y27['other_operating'] * (1 + gd)
        F['float'] = Y27['float'] * (1 + gt)
    F['other'] = Y27['other']
    F['total_income'] = sum(F[x] for x in REVENUE_LINES[b])
    F['mtf_book'] = F['mtf'] / y
    F['finance'] = max(Y27['finance'] + rate * new_borrowing(F['mtf_book'], Y27['mtf_book'], ret * Y27['pat']), 0.0)
    if b == 'ANGELONE':
        F['fees_commission'] = k['k_fee_ratio'] * F['broking']
        for line in ('employee', 'depreciation', 'other_expenses', 'impairment'):
            F[line] = pub('FY 2028', line)
    else:
        F['other_expenses'] = k['k_oexp_ratio'] * F['broking']
        for line in ('employee', 'depreciation'):
            F[line] = pub('FY 2028', line)
    F['total_costs'] = sum(F[x] for x in COST_LINES[b])
    F['pbt'] = F['total_income'] - F['total_costs']
    F['tax'] = tax * F['pbt']
    F['pat'] = F['pbt'] - F['tax']

    # build-up, top block, margins, valuation
    for q in kit['buildup']:
        out[(q, 'adr_consol', '')] = b0 * (1 + g) ** kit['step'][q] + m0 * (1 + gm) ** kit['step'][q]
    F['adr_consol'] = b28 + m28
    shares, close = pub('FY 2028', 'shares'), pub('FY 2028', 'close')
    for pk, L in (('FY 2027', Y27), ('FY 2028', F)):
        L['pat_margin'] = L['pat'] / L['total_income']
        L['op_revenue'] = L['broking'] + L['mtf']
        L['treasury_rev'] = L[TREASURY[b]]
        L['other_inc'] = L['total_income'] - L['op_revenue'] - L['treasury_rev']
        for line, v in L.items():
            out[(pk, line, '')] = v
        eps = L['pat'] / shares
        for s, x in zip(SCENARIOS, pe):
            price = x * eps
            disc1 = price / (1 + disc)
            target = disc1 / (1 + today) if pk == 'FY 2028' else disc1    # FY 2027: one discount step (as build())
            for line, v in (('eps', eps), ('pe', x), ('price_fwd', price), ('price_disc', disc1),
                            ('target_today', target), ('upside', target / close - 1)):
                out[(pk, line, s)] = v
    return out
