"""Valuation for Angel One and Groww (PLAN 5.8): three methods, triangulated into one value per scenario.

Built on the 09.11 workbook (New Model - 09.11.26/20260714_brokers dashboard v2.xlsx), sheets
`Angel One - ADR model (A+B)` rows 40-73 and `Groww - ADR Model` rows 41-74, with AB's choices of 9 Nov 2026:

  1. Regression: share price = intercept + slope × 45-day average ADR, a plain least-squares fit (Excel SLOPE /
     INTERCEPT / RSQ) over every day that has both a 45-day average and a close, from the broker's series start.
     Base = slope × current ADR + intercept; bear / bull move the slope term by ∓ the band (10%).
  2. Ratio: price ÷ 45-day average ADR on the same days; its mean and population standard deviation (STDEV.P).
     Bear / base / bull = (mean − 1 SD, mean, mean + 1 SD) × current ADR. A current value, not discounted (AB, point 2).
  3. ADR: the PAT model's FY 2028 "target price today" (src/engine/pat.py, sb_pat_lines) for each scenario.
  Net = weighted sum, 20% / 30% / 50% for both brokers (AB, point 1; the 09.11 Angel sheet takes a plain average).

"Current ADR" = the mean daily ADR (broking + MTF, Rs Cr / day) over the trading days so far in the latest quarter:
the workbook's `SUMMARY - <broker>!C11` (AB, point 3). ADR is the engine's sb_daily_revenue summed over fo, cash,
comm and the MTF segment, the same total the workbook's `<broker> Revenue!M` holds.

Angel One also gets the consolidated trailing-12-month P/E series behind the workbook's two P/E band charts
(last 3 years, and since 1 Apr 2025; mean ± 1 / 2 sample SD, STDEV.S): close × shares ÷ the sum of the last four
filed quarters' consolidated PAT, a quarter counting from its results date (AB, point 6).

Everything here is plain data in, plain data out (no I/O). Rs Cr, per-share figures in Rs.
"""
from __future__ import annotations

import datetime as dt
import math

SCENARIOS = ('bear', 'base', 'bull')
METHODS = ('regression', 'ratio', 'adr')
LABELS = {
    'regression': 'Regression', 'ratio': 'Ratio analysis', 'adr': 'ADR (PAT model)', 'net': 'Net value (weighted)',
    'upside': 'Upside vs close', 'weight': 'Weight', 'adr_now': 'Current ADR (quarter to date)',
    'slope': 'Slope', 'intercept': 'Intercept', 'r2': 'R²', 'fit_days': 'Days in the fit', 'fit_from': 'Fit from',
    'ratio_mean': 'Price ÷ 45-day ADR: mean', 'ratio_sd': 'Price ÷ 45-day ADR: SD', 'close': 'Share price (close)',
    'band': 'Regression bear / bull band', 'pe_mean': 'P/E mean', 'pe_sd': 'P/E SD', 'pe_current': 'P/E current',
}


class ValuationInputMissing(RuntimeError):
    pass


def q_of(iso):
    d = dt.date.fromisoformat(iso)
    fy = d.year + 1 if d.month >= 4 else d.year
    return f'Q{(d.month - 4) % 12 // 3 + 1} FY {fy}'


# ── statistics, as Excel computes them ───────────────────────────────────────
def mean(xs):
    return sum(xs) / len(xs)


def stdev_p(xs):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def stdev_s(xs):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def ols(xs, ys):
    """Excel SLOPE, INTERCEPT and RSQ of ys on xs."""
    mx, my = mean(xs), mean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    slope = sxy / sxx
    return slope, my - slope * mx, sxy * sxy / (sxx * syy)


# ── the daily series ─────────────────────────────────────────────────────────
def adr_series(daily, start=None):
    """[(date, total ADR)] from sb_daily_revenue rows: fo + cash + comm + MTF on every day the required segments all
    have a row (commodities count as zero before their first day). MTF is mtf_gross (Angel, Groww) or mtf_nii."""
    by = {}
    for r in daily:
        if r.get('revenue_cr') is not None:
            by.setdefault(r['segment'], {})[r['trade_date']] = float(r['revenue_cr'])
    mtf = 'mtf_nii' if 'mtf_nii' in by else 'mtf_gross'
    need = ('fo', 'cash', mtf)
    if any(s not in by for s in need):
        raise ValuationInputMissing(f'daily ADR rows missing for {[s for s in need if s not in by]}')
    days = sorted(set.intersection(*(set(by[s]) for s in need)))
    comm = by.get('comm', {})
    first_comm = min(comm) if comm else None
    out = []
    for d in days:
        if start and d < start:
            continue
        if first_comm and d >= first_comm and d not in comm:
            continue
        out.append((d, sum(by[s][d] for s in need) + comm.get(d, 0.0)))
    return out


def build_daily(adr, prices, dma_days=45):
    """Rows {date, adr, dma, price, ratio}: dma from the dma_days-th day of the ADR series (AVERAGE(M4:M48) is the
    first, as in the workbook); price is the close of that date (None when there is none)."""
    px = {p['trade_date']: float(p['close']) for p in prices if p.get('close') is not None}
    rows = []
    for i, (d, v) in enumerate(adr):
        dma = mean([x for _, x in adr[i - dma_days + 1:i + 1]]) if i >= dma_days - 1 else None
        p = px.get(d)
        rows.append(dict(date=d, adr=v, dma=dma, price=p, ratio=p / dma if (p and dma) else None))
    return rows


def current_adr(adr):
    """Mean daily ADR over the days of the latest quarter in the series (SUMMARY!C11)."""
    q = q_of(adr[-1][0])
    xs = [v for d, v in adr if q_of(d) == q]
    return mean(xs), q, len(xs)


# ── the three methods ────────────────────────────────────────────────────────
def regression(rows, adr_now, band):
    fit = [r for r in rows if r['dma'] is not None and r['price']]
    if len(fit) < 30:
        raise ValuationInputMissing(f'only {len(fit)} days with a 45-day ADR and a close')
    slope, icpt, r2 = ols([r['dma'] for r in fit], [r['price'] for r in fit])
    vals = dict(bear=slope * adr_now * (1 - band) + icpt, base=slope * adr_now + icpt, bull=slope * adr_now * (1 + band) + icpt)
    return dict(slope=slope, intercept=icpt, r2=r2, n=len(fit), fit_from=fit[0]['date'], fit_to=fit[-1]['date'], values=vals)


def ratio(rows, adr_now):
    rs = [r['ratio'] for r in rows if r['ratio'] is not None]
    if len(rs) < 30:
        raise ValuationInputMissing(f'only {len(rs)} days with a price ÷ ADR ratio')
    m, sd = mean(rs), stdev_p(rs)
    return dict(mean=m, sd=sd, n=len(rs), values=dict(bear=(m - sd) * adr_now, base=m * adr_now, bull=(m + sd) * adr_now))


def triangulate(values, weights):
    """values: {method: {scenario: price}}; weights: {method: w}. Weighted sum per scenario (SUMPRODUCT)."""
    tw = sum(weights.values())
    if abs(tw - 1) > 1e-9:
        raise ValuationInputMissing(f'valuation weights add up to {tw}, not 1')
    return {s: sum(weights[m] * values[m][s] for m in METHODS) for s in SCENARIOS}


# ── P/E bands (Angel One, Groww) ─────────────────────────────────────────────
def fiscal_order(quarter):
    """'Q3 FY 2025' -> (2025, 3), so quarters sort in time order; anything else sorts as itself."""
    p = str(quarter).split()
    return (int(p[2]), int(p[0][1:])) if len(p) == 3 and p[0][:1] == 'Q' and p[1] == 'FY' else (0, str(quarter))


def ttm_pe(prices, quarters, shares_cr):
    """[{date, close, shares, ttm_pat, pe}]: quarters = [(results_date, quarter, pat_cr[, shares_cr])]. On each date
    the last four quarters whose results date is on or before it; the share count is the latest of those quarters'
    (on today's split basis, as the closes are), else shares_cr. Dates before four quarters are known are left out."""
    # by results date, then by fiscal quarter: quarters can share a date (Groww's pre-listing quarters, all on the listing day)
    qs = sorted(quarters, key=lambda q: (q[0], fiscal_order(q[1])))
    out = []
    for p in prices:
        d = p['trade_date']
        known = [q for q in qs if q[0] <= d]
        if len(known) < 4 or p.get('close') is None:
            continue
        last4 = known[-4:]
        pat = sum(q[2] for q in last4)
        if pat <= 0:
            continue
        sh = next((q[3] for q in reversed(known) if len(q) > 3 and q[3]), shares_cr)
        out.append(dict(date=d, close=float(p['close']), shares=sh, ttm_pat=pat, quarters=[q[1] for q in last4],
                        pe=float(p['close']) * sh / pat))
    return out


def pe_quarters(facts, A):
    """[(results_date, quarter, pat_cr, shares_cr)] from consolidated quarterly pl_pat facts and the quarter-end
    share count (metric shares_period_end_cr, on today's Re 1 face-value basis), dated by the val_results_dates assumption ("Q3 FY 2023=2023-01-16;
    …"). Quarters without a results date are left out. [] when the broker has no results dates."""
    txt = A('val_results_dates', '')
    if not txt:
        return []
    dates = dict(x.strip().split('=') for x in str(txt).split(';') if x.strip())
    pat, shares = {}, {}
    for f in facts:
        if f.get('period_type') != 'Q' or f.get('segment', 'consolidated') != 'consolidated':
            continue
        if f['metric'] == 'pl_pat':
            pat[f['period_key']] = f['value'] / 10 if f['unit'] == 'Rs Mn' else f['value']
        elif f['metric'] == 'shares_period_end_cr' and f.get('period_key'):
            shares[f['period_key']] = f['value']
    return sorted((dates[q], q, v, shares.get(q)) for q, v in pat.items() if q in dates)


def pe_bands(series, since):
    xs = [r for r in series if r['date'] >= since]
    if len(xs) < 2:
        return None
    pes = [r['pe'] for r in xs]
    m, sd = mean(pes), stdev_s(pes)
    return dict(since=xs[0]['date'], to=xs[-1]['date'], n=len(xs), mean=m, sd=sd, current=xs[-1]['pe'])


# ── the whole thing ──────────────────────────────────────────────────────────
# Timeline windows (AB, 9 Nov 2026): the regression and ratio legs, and the P/E bands, are fitted over each window;
# 'all' is the workbook's own window (the whole series from val_series_start), the default.
WINDOWS = (('all', 'All', None), ('3m', '3M', 3), ('6m', '6M', 6), ('1y', '1Y', 12), ('2y', '2Y', 24), ('3y', '3Y', 36),
           ('apr25', 'Since Apr 2025', 'pe_since'))
COVER_SLACK_DAYS = 10   # a window counts as covered when its first fitted day is at most this many days after its start


def months_back(iso, n):
    d = dt.date.fromisoformat(iso)
    y, m = divmod(d.year * 12 + d.month - 1 - n, 12)
    m += 1
    last = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1)).day
    return dt.date(y, m, min(d.day, last)).isoformat()


def window_starts(as_of, series_start, pe_since):
    out = {}
    for key, _, n in WINDOWS:
        out[key] = series_start if n is None else pe_since if n == 'pe_since' else months_back(as_of, n)
    return out


def covered(first_day, start):
    return dt.date.fromisoformat(first_day) <= dt.date.fromisoformat(start) + dt.timedelta(days=COVER_SLACK_DAYS)


def build(broker, daily, prices, pat_targets, A, pe_quarters=None, shares_cr=None):
    """A: assumption reader (src.engine.pat.Assume) with the val_* keys. pat_targets: {scenario: FY 2028 target
    price today} from the PAT model. Returns the model dict that lines() flattens: one valuation per covered window."""
    start = str(A('val_series_start'))
    dma_days = int(A('val_dma_days'))
    band = float(A('val_regression_band'))
    pe_since = str(A('val_pe_since'))
    w = {m: float(x) for m, x in zip(METHODS, str(A('val_weights')).split(','))}
    adr = adr_series(daily, start)
    if len(adr) < dma_days + 30:
        raise ValuationInputMissing(f'{broker}: {len(adr)} ADR days from {start}')
    rows = build_daily(adr, prices, dma_days)
    adr_now, q, qdays = current_adr(adr)
    if set(pat_targets) != set(SCENARIOS):
        raise ValuationInputMissing(f'{broker}: PAT model targets missing ({sorted(pat_targets)})')
    px = sorted((p for p in prices if p.get('close') is not None), key=lambda p: p['trade_date'])[-1]
    close = dict(price=float(px['close']), date=px['trade_date'])
    as_of = adr[-1][0]
    starts = window_starts(as_of, start, pe_since)
    fitted = [r for r in rows if r['dma'] is not None and r['price']]
    windows = {}
    for key, label, _ in WINDOWS:
        sub = [r for r in rows if r['date'] >= starts[key]]
        if key != 'all' and (not fitted or not covered(fitted[0]['date'], starts[key])):
            continue   # the data start after the window does: it would repeat 'all'
        try:
            reg, rat = regression(sub, adr_now, band), ratio(sub, adr_now)
        except ValuationInputMissing:
            if key == 'all':
                raise
            continue
        vals = dict(regression=reg['values'], ratio=rat['values'], adr=dict(pat_targets))
        net = triangulate(vals, w)
        windows[key] = dict(label=label, start=starts[key], regression=reg, ratio=rat, values=vals, net=net,
                            upside={s: net[s] / close['price'] - 1 for s in SCENARIOS})
    base = windows['all']
    for r in rows:   # the implied price on the workbook's own fit ('<broker> Revenue'!AK)
        r['implied'] = base['regression']['slope'] * r['dma'] + base['regression']['intercept'] if r['dma'] is not None else None
    pe = None
    if pe_quarters and shares_cr:
        series = ttm_pe(prices, pe_quarters, shares_cr)
        if series:
            last = series[-1]['date']
            bands = {}
            for key, _, n in WINDOWS:
                # 'all' is the whole P/E series (Groww's workbook chart: 'Groww charts'!G3:G203, from the listing).
                # Under All the page shows the workbook's 3y and apr25 bands where the series covers them (Angel One),
                # else this one (Groww, listed 12 Nov 2025)
                since = series[0]['date'] if n is None else pe_since if n == 'pe_since' else months_back(last, n)
                b = pe_bands(series, since) if covered(series[0]['date'], since) else None
                if b:
                    bands[key] = b
            pe = dict(series=series, windows=bands)
    return dict(broker=broker, as_of=as_of, adr_now=adr_now, adr_quarter=q, adr_quarter_days=qdays, band=band,
                weights=w, close=close, windows=windows, rows=rows, pe=pe, start=start, dma_days=dma_days,
                # the workbook window, flat, for the report and callers that want one answer
                regression=base['regression'], ratio=base['ratio'], values=base['values'], net=base['net'],
                upside=base['upside'])



def lines(model, run_id):
    """sb_valuation_lines rows. section 'summary' / 'inputs': period_key = the window ('all', '3m', … 'apr25');
    'common': inputs that do not depend on the window; 'weights': period_key = the method; 'series' / 'pe':
    period_key = trade date; 'pe_bands': period_key = the window."""
    b, out, order = model['broker'], [], 0

    def add(section, line, value, unit, scenario='', period_key='', rule=None, label=None):
        nonlocal order
        order += 1
        out.append(dict(run_id=run_id, broker_id=b, section=section, period_key=period_key, line=line, scenario=scenario,
                        label=label or LABELS.get(line, line), value=float(value), unit=unit, rule=rule, sort_order=order))
    a = model['adr_now']
    add('common', 'close', model['close']['price'], 'Rs', rule=f"close on {model['close']['date']} (sb_share_prices)")
    add('common', 'adr_now', a, 'Rs Cr / day',
        rule=f"mean daily ADR (broking + MTF) over {model['adr_quarter_days']} days of {model['adr_quarter']}")
    add('common', 'band', model['band'], 'fraction', rule='bear / bull move slope × ADR by this')
    for m in METHODS:
        add('weights', 'weight', model['weights'][m], 'fraction', period_key=m, label=f"Weight: {LABELS[m]}")
    for wk, W in model['windows'].items():
        reg, rat = W['regression'], W['ratio']
        rules = {
            'regression': {
                'bear': f"{reg['slope']:.3f} × {a:.2f} × (1 − {model['band']:.0%}) + {reg['intercept']:.2f}",
                'base': f"{reg['slope']:.3f} × {a:.2f} + {reg['intercept']:.2f}",
                'bull': f"{reg['slope']:.3f} × {a:.2f} × (1 + {model['band']:.0%}) + {reg['intercept']:.2f}"},
            'ratio': {
                'bear': f"({rat['mean']:.3f} − {rat['sd']:.3f}) × {a:.2f}", 'base': f"{rat['mean']:.3f} × {a:.2f}",
                'bull': f"({rat['mean']:.3f} + {rat['sd']:.3f}) × {a:.2f}"},
            'adr': {s: 'PAT model FY 2028 target price today (sb_pat_lines)' for s in SCENARIOS},
        }
        for m in METHODS:
            for s in SCENARIOS:
                add('summary', m, W['values'][m][s], 'Rs', s, wk, rule=rules[m][s])
        for s in SCENARIOS:
            add('summary', 'net', W['net'][s], 'Rs', s, wk,
                rule=' + '.join(f"{model['weights'][m]:.0%} × {W['values'][m][s]:.2f}" for m in METHODS))
            add('summary', 'upside', W['upside'][s], 'fraction', s, wk,
                rule=f"{W['net'][s]:.2f} ÷ {model['close']['price']:.2f} − 1")
        span = f"{reg['fit_from']} to {reg['fit_to']}"
        add('inputs', 'slope', reg['slope'], 'Rs per Rs Cr / day', period_key=wk, rule=f"SLOPE(price, {model['dma_days']}-day ADR), {span}")
        add('inputs', 'intercept', reg['intercept'], 'Rs', period_key=wk, rule=f'INTERCEPT(price, 45-day ADR), {span}')
        add('inputs', 'r2', reg['r2'], 'fraction', period_key=wk, rule=f'RSQ(price, 45-day ADR), {span}')
        add('inputs', 'fit_days', reg['n'], 'days', period_key=wk, rule=f"{span} ({W['label']}; window from {W['start']})")
        add('inputs', 'ratio_mean', rat['mean'], 'x', period_key=wk, rule=f"AVERAGE over {rat['n']} days, {span}")
        add('inputs', 'ratio_sd', rat['sd'], 'x', period_key=wk, rule=f'STDEV.P, {span}')
    for r in model['rows']:
        if r['dma'] is None:
            continue
        for k, unit in (('adr', 'Rs Cr / day'), ('dma', 'Rs Cr / day'), ('price', 'Rs'), ('ratio', 'x'), ('implied', 'Rs')):
            if r.get(k) is not None:
                out.append(dict(run_id=run_id, broker_id=b, section='series', period_key=r['date'], line=k, scenario='',
                                label=k, value=float(r[k]), unit=unit, rule=None, sort_order=0))
    if model['pe']:
        for k, w in model['pe']['windows'].items():
            for line in ('pe_mean', 'pe_sd', 'pe_current'):
                add('pe_bands', line, w[line[3:]], 'x', period_key=k,
                    rule=f"{w['since']} to {w['to']}, {w['n']} days" + (' (STDEV.S)' if line == 'pe_sd' else ''))
        for r in model['pe']['series']:
            out.append(dict(run_id=run_id, broker_id=b, section='pe', period_key=r['date'], line='pe', scenario='',
                            label='Consolidated TTM P/E', value=r['pe'], unit='x',
                            rule=f"close {r['close']:.2f} × {r['shares']:.3f} Cr shares ÷ TTM PAT {r['ttm_pat']:.1f} ({', '.join(r['quarters'])})",
                            sort_order=0))
    return out
