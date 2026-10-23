"""Calibration tables + projection rules, written to reproduce the workbook exactly (parity mode).

Each function returns {period_key: {param: value, ..., 'regime': 'actual'|'projected', 'rule': str}}.
Cell comments name the workbook cells being reproduced.
"""
from statistics import mean
from .inputs import months_of_quarter, quarter_of_month, month_seq, quarter_seq

# Working-sheet quarter columns (row 2 headers) and the 174-182 quarterly table rows
WS_QCOL = {'Q1 FY 2025': 'D', 'Q2 FY 2025': 'E', 'Q3 FY 2025': 'F', 'Q4 FY 2025': 'G', 'Q1 FY 2026': 'H',
           'Q2 FY 2026': 'I', 'Q3 FY 2026': 'J', 'Q4 FY 2026': 'K', 'Q1 FY 2027': 'M'}
WS_QROW2 = {q: 174 + i for i, q in enumerate(['Q1 FY 2025', 'Q2 FY 2025', 'Q3 FY 2025', 'Q4 FY 2025',
                                              'Q1 FY 2026', 'Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027'])}
WS_MROW0 = 141   # 'FY 2025 April' in Working sheet B141


def qcols(I):
    """Quarter -> Working-sheet column, plus quarters added by live switches (h)."""
    return {**WS_QCOL, **getattr(I, 'extra_qcols', {})}


def qrows2(I):
    """Quarter -> quarterly-table row (174-182), plus quarters added by live switches (h)."""
    return {**WS_QROW2, **getattr(I, 'extra_qrows', {})}


def ws_month_row(fm):
    return WS_MROW0 + month_seq('FY 2025 April', fm).__len__() - 1


# ── take rates: Working sheet rows 61-63 (= rev mix × total income) / rows 6-8 (orders) → rows 76-78 ──
def take_rates(I):
    out = {}
    QC, QR = qcols(I), qrows2(I)
    for q, c in QC.items():
        ti = I.ws(c, 99)
        o = {s: I.ws(c, r) for s, r in (('fo', 6), ('cash', 7), ('comm', 8))}
        mix = {s: I.ws(c, r) for s, r in (('fo', 15), ('cash', 16), ('comm', 17))}
        row = {'total_income': ti}                                      # row 99
        if q in QR:                                                      # I174:I182 = F / C
            r2 = QR[q]
            row['comm_pct'] = I.ws('F', r2) / I.ws('C', r2)
        for s in ('fo', 'cash', 'comm'):
            if ti is not None and mix[s] is not None and o[s]:
                row[f'rev_{s}_mn'] = mix[s] * ti                       # rows 61-63
                row[f'take_rate_{s}'] = mix[s] * ti / o[s]             # rows 76-78
        if None not in o.values():
            row['fo_pct'] = o['fo'] / (o['fo'] + o['cash'] + o['comm'])  # row 10 (segment-sum denominator)
        out[q] = row
    return out


# ── F&O: ' F&O market' rows 4-28 (market) and 31-56 (Angel), backtesting F&O!AI48:AR52 (take rate) ──
def calib_fo(I, daily_contracts_by_month, tr):
    months = month_seq('FY 2025 October', 'FY 2027 October')            # rows 4-28 / 32-56
    share_src = I.fact[('share_fo', 'F&O market')]                       # N4:N23 hardcoded
    orders_src = I.fact[('total_orders', 'F&O market')]                  # C32:C51 hardcoded
    if I.switches:                                                       # live (i): to the latest disclosed month
        from .switches import extend_monthly
        share_src = extend_monthly(I, 'share_fo', share_src)
        orders_src = extend_monthly(I, 'total_orders', orders_src)
    last_fo_pct_q = I.pin('fo_pct_last_actual_quarter')[1]                # Q4 FY 2026
    last_tr_q = I.pin('fo_take_rate_last_actual_quarter')[1]              # Q4 FY 2026
    out, shares, fo_pct_hist = {}, [], []
    prev = None
    for m in months:
        q = quarter_of_month(m)
        r = {'mkt_contracts': daily_contracts_by_month.get(m)}           # J
        # share N: actual; first unreported = avg of last 3 actual (N24); then carry (N25:N28)
        if m in share_src:
            r['share'], r['share_rule'] = share_src[m], 'actual'
        elif prev and prev['share_rule'] == 'actual':
            r['share'], r['share_rule'] = mean(shares[-3:]), 'avg_last_3_actual_months'
        else:
            r['share'], r['share_rule'] = prev['share'], 'carry'
        if r['share_rule'] == 'actual':
            shares.append(r['share'])
        # F&O % of orders, E: quarter actual up to the pin; then avg of last 9 monthly values (E50); then carry
        if q in tr and 'fo_pct' in tr[q] and _q_le(q, last_fo_pct_q):
            r['fo_pct'], r['fo_pct_rule'] = tr[q]['fo_pct'], 'actual'
            fo_pct_hist.append(r['fo_pct'])
        elif prev and prev['fo_pct_rule'] == 'actual':
            r['fo_pct'], r['fo_pct_rule'] = mean(fo_pct_hist[-9:]), 'avg_last_9_months'
        else:
            r['fo_pct'], r['fo_pct_rule'] = prev['fo_pct'], 'carry'
        # orders C, F; Angel contracts O/G; contracts per order H
        if m in orders_src:
            r['total_orders'] = orders_src[m]
            r['fo_orders'] = r['fo_pct'] * r['total_orders']                     # F = E × C
            r['angel_contracts_mn'] = r['share'] * r['mkt_contracts'] / 1e6      # G = O/1e6, O = N × J
            r['cpo'], r['regime'], r['rule'] = r['angel_contracts_mn'] / r['fo_orders'], 'actual', 'H = G / F'
        else:
            r['cpo'], r['regime'], r['rule'] = prev['cpo'], 'projected', 'carry_last_actual_month (H52:H56)'
        out[m] = r
        prev = r
    # take rate by quarter (AJ51:AR51): actual through the pin, then avg of last 3, then carry
    trq, hist = {}, []
    for q in quarter_seq('Q3 FY 2025', 'Q3 FY 2027'):
        if _q_le(q, last_tr_q):
            trq[q] = (tr[q]['take_rate_fo'], 'actual')
            hist.append(tr[q]['take_rate_fo'])
        elif trq and list(trq.values())[-1][1] == 'actual':
            trq[q] = (mean(hist[-3:]), 'avg_last_3_quarters')
        else:
            trq[q] = (list(trq.values())[-1][0], 'carry')
    return out, trq


def _q_le(a, b):
    ka = (int(a[-4:]), int(a[1]))
    kb = (int(b[-4:]), int(b[1]))
    return ka <= kb


# ── Cash: 'cash market' quarter-end rows + lookup F35:J43 ──
def calib_cash(I, daily_trades_by_quarter, tr):
    last_q = I.pin('cash_last_actual_quarter')[1]                       # Q1 FY 2027
    out, hist = {}, []
    for q in quarter_seq('Q3 FY 2025', 'Q3 FY 2027'):
        r = {'mkt_trades_mn': daily_trades_by_quarter.get(q)}           # M (trades, Mn)
        if _q_le(q, last_q):
            c = qcols(I)[q]
            r['orders'] = I.ws(c, 7)                                     # N
            r['share'] = I.ws(c, 40)                                     # K
            r['mkt_orders'] = r['orders'] / r['share']                   # O
            r['tpo'] = r['mkt_trades_mn'] / r['mkt_orders']              # P = M / O
            r['take_rate'] = tr[q]['take_rate_cash']                     # R = row 77
            r['regime'], r['rule'] = 'actual', 'P = M / (N / K)'
            hist.append(r)
        elif out[list(out)[-1]]['regime'] == 'actual':
            r['tpo'] = mean(h['tpo'] for h in hist[-3:])                 # G42 = AVERAGE(G39:G41)
            r['take_rate'] = mean(h['take_rate'] for h in hist[-3:])     # I42
            r['share'] = hist[-1]['share']                               # J42 = J41
            r['regime'], r['rule'] = 'projected', 'avg_last_3_quarters (tpo, take rate); share carried'
        else:
            p = out[list(out)[-1]]
            r.update(tpo=p['tpo'], take_rate=p['take_rate'], share=p['share'])
            r['regime'], r['rule'] = 'projected', 'carry'
        out[q] = r
    return out


# ── Commodities: Commodities!U14:AB44, take rate AI11 ──
def calib_comm(I, mcx_by_month):
    months = month_seq('FY 2025 April', 'FY 2027 October')             # rows 14-44
    aa_src = I.fact[('share_comm', 'Commodities')]                       # AA hardcoded (14-37, 41, 42)
    ws_f = I.fact[('share_comm', 'Working sheet - Angel One')]          # AA38:AA40 = WS F165:F167
    ws_c = I.fact[('total_orders', 'Working sheet - Angel One')]        # WS C141:C167
    if I.switches:                                                       # live (i): to the latest disclosed month
        from .switches import extend_monthly
        aa_src = extend_monthly(I, 'share_comm', aa_src, also_present=(ws_f,))
        ws_c = extend_monthly(I, 'total_orders', ws_c)
    out, prev, cpos = {}, None, []
    for m in months:
        q = quarter_of_month(m)
        r = {'mcx_contracts': mcx_by_month.get(m)}                       # W
        # share AA
        if m in aa_src:
            r['share'], r['share_rule'] = aa_src[m], 'actual'
        elif m in ws_f:
            r['share'], r['share_rule'] = ws_f[m], 'actual (WS F)'
        else:
            r['share'], r['share_rule'] = prev['share'], 'carry'
        # Angel commodity orders Y = WS C (monthly total) × WS I (quarter commodity %, = F/C rows 174-182)
        if m in ws_c and q in qrows2(I):
            row2 = qrows2(I)[q]
            comm_pct = I.ws('F', row2) / I.ws('C', row2)
            r['comm_pct'] = comm_pct
            r['comm_orders'] = ws_c[m] * comm_pct                        # Y (= WS J)
            r['mkt_orders'] = r['comm_orders'] / r['share']              # X = Y / AA
            r['cpo'] = (r['mcx_contracts'] / 1e6) / r['mkt_orders']      # Z = (W/1e6) / X
            r['regime'], r['rule'] = 'actual', 'Z = (W/1e6) / (Y/AA)'
            cpos.append(r['cpo'])
        else:
            nproj = sum(1 for v in out.values() if v['regime'] == 'projected')
            if nproj == 0:
                r['cpo'], r['rule'] = mean(cpos[-3:]), 'avg_last_3_actual (Z41)'
            elif nproj == 1:
                r['cpo'], r['rule'] = mean(cpos[-2:] + [prev['cpo']]), 'avg(last_2_actual, 1st projection) (Z42)'
            else:
                r['cpo'], r['rule'] = prev['cpo'], 'carry (Z43:Z44)'
            r['regime'] = 'projected'
        out[m] = r
        prev = r
    # AI11 = Working sheet J78 = take rate of the pinned quarter
    fixed_q = I.pin('comm_take_rate_fixed_quarter')[1]                   # 'Q3 FY 2026'
    c = WS_QCOL[fixed_q]
    take_rate = I.ws(c, 17) * I.ws(c, 99) / I.ws(c, 8)
    return out, take_rate, fixed_q


# ── MTF: 'MTF data'!C48:Q60 ──
def calib_mtf(I, daily_book_by_quarter=None):
    daily_book_by_quarter = daily_book_by_quarter or {}
    out, hist = {}, []
    last_q = I.pin('mtf_last_actual_quarter')[1]                        # Q1 FY 2027
    for q in quarter_seq('Q1 FY 2025', 'Q4 FY 2027'):
        r = {}
        mo = [I.monthly.get(('mtf_industry', 'book_cr', m)) for m in months_of_quarter(q)]
        if None not in mo:
            r['industry_avg_cr'] = mean(mo)                                # D = AVERAGE of monthly series
        if _q_le(q, last_q):
            ov = I.pin('mtf_share_override', q)[0]
            book = I.pin('mtf_angel_book_cr', q)[0]
            if book is None and getattr(I, 'facts', None) is not None:      # live (h): disclosed book, Q5
                f = I.facts.fact('avg_funding_book', q)
                book = f.value / 10 if f.unit == 'Rs Mn' else None             # Rs Mn -> Rs Cr
            if 'industry_avg_cr' not in r and q in daily_book_by_quarter:      # live (h): daily lake avg, Q6
                r['industry_avg_cr'] = daily_book_by_quarter[q]
            r['angel_book_cr'] = book                                      # P (pinned: as the workbook used it)
            r['share'] = ov if ov is not None else book / r['industry_avg_cr']   # Q = P / D (Q51 hard-coded)
            r['regime'], r['rule'] = 'actual', 'override' if ov is not None else 'Q = P / D'
            if _q_le('Q4 FY 2025', q):
                hist.append(r['share'])                                    # Q52:Q57 feed Q58
        elif out[list(out)[-1]]['regime'] == 'actual':
            # Q58 = AVERAGE(Q52:Q57): the last 6 reported quarters (sb_assumptions rule_mtf_share)
            r['share'], r['regime'], r['rule'] = mean(hist[-6:]), 'projected', 'avg_last_6_reported_quarters (Q58)'
            if q in daily_book_by_quarter:                                   # D58 = AVERAGEIF(daily book), P58 = Q58*D58
                r['industry_avg_cr'] = daily_book_by_quarter[q]
                r['angel_book_cr'] = r['share'] * r['industry_avg_cr']
        else:
            r['share'], r['regime'], r['rule'] = out[list(out)[-1]]['share'], 'projected', 'carry'
        out[q] = r
    return out
