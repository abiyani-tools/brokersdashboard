"""Parity → live switches (LIVE_SPEC §4), one per letter, applied in order a → i.

A cell switch replaces workbook cells (as read through Inputs.ws) with reviewed disclosure facts.
Every replacement must resolve to a fact with status 'reviewed' and the same unit as the seed it
replaces; anything else raises. With no switches on, Inputs behaves exactly as in parity mode.
"""
WS = 'Working sheet - Angel One'
ORDER = 'abcdefghi'

# switch -> {(sheet, col, row): (metric, period_key)}
CELL_SWITCHES = {
    # (a) Q3 FY26 commodity orders: the workbook's J8 = 36; the Q3 FY26 press release says 35 (fact 596).
    #     J8 feeds the commodity take rate (Commodities!AI11 = J17 × J99 / J8) and the F&O share of
    #     orders for Q3 FY26 (row 10 = J6 / (J6 + J7 + J8)).
    'a': {(WS, 'J', 8): ('orders_comm', 'Q3 FY 2026')},
    # (b) revenue mix to the deck's one decimal (Working sheet rows 15-17 = F&O, cash, commodity share
    #     of total income) for Q3 FY25 .. Q1 FY27. Q2 FY27 enters with switch (h).
    'b': {(WS, col, row): (metric, q)
          for q, col in (('Q3 FY 2025', 'F'), ('Q4 FY 2025', 'G'), ('Q1 FY 2026', 'H'), ('Q2 FY 2026', 'I'),
                         ('Q3 FY 2026', 'J'), ('Q4 FY 2026', 'K'), ('Q1 FY 2027', 'M'))
          for row, metric in ((15, 'revmix_fo'), (16, 'revmix_cash'), (17, 'revmix_comm'))},
}

# switch -> exchange series whose imputed (carried-forward) days take the lake's value instead.
MARKET_SWITCHES = {
    # (c) BSE F&O contracts: the workbook carries 18,962,859 forward from 29 Sep to 21 Oct 2026 in the
    #     daily column (backtesting F&O!V); the lake (exchangesdash_json) has the real daily totals.
    #     The monthly contracts per order already uses the real totals in parity, so only the daily
    #     market volume (V) changes.
    'c': {('bse_fo', 'contracts')},
}

# switch -> rule applied when averaging daily revenue (summary statistics only; daily rows are kept)
SUMMARY_SWITCHES = {
    # (d) special sessions (sb_calendar.special_session: Muhurat, DR test) are dropped from every average,
    #     last-N and weekday statistic, for all segments; they stay in the daily rows and in totals.
    'd': 'exclude_special_sessions',
    # (g) decision D4: MTF shown gross in every table (the workbook's weekday tables use net) plus an
    #     'MTF (net)' panel at net = 45% × gross [SOURCE NEEDED: basis for 45%]. Consolidated stays gross.
    'g': 'mtf_gross_and_net',
}

# switch -> projection rule replaced in the daily model
PROJECTION_SWITCHES = {
    # (e) decision D2: projected cash days use the monthly cash share (sb_disclosure_facts share_cash, period M)
    #     of their own month, or of the latest earlier month that has one, instead of carrying the last
    #     actual quarter's share. Actual quarters keep the quarterly share their trades/order is built on.
    'e': 'cash_share_monthly',
    # (f) decision D3: each quarter's commodity days use that quarter's own take rate (mix × total income ÷
    #     commodity orders) instead of the fixed Q3 FY26 rate (Commodities!AI11). Quarters after the last
    #     one with a rate carry the latest (decision Q4). A quarter before the first one with a rate
    #     (Q1 FY25: no revenue mix disclosed) uses the earliest rate, flagged as projected.
    'f': 'comm_take_rate_quarterly',
}

# switch -> a quarter the workbook has no column for, built from reviewed facts, and the pins it moves
H_COL, H_ROW2 = 'Q2FY27', 183          # synthetic Working-sheet column / quarterly-table row (not Excel cells)
QUARTER_SWITCHES = {
    # (h) Q2 FY27 actuals in; projections roll to Q3 FY27. Cells: orders (6-8), revenue mix (15-17),
    #     cash share (40), total income (99), quarterly table C (total orders) and F (commodity orders).
    #     The last-actual-quarter pins move to Q2 FY27. MTF Q2 FY27: Angel book = disclosed average funding
    #     book (Rs Mn ÷ 10, decision Q5); industry average = daily lake average, as the monthly series ends
    #     in May 2026 (decision Q6).
    'h': {
        'quarter': 'Q2 FY 2027', 'col': H_COL, 'row2': H_ROW2,
        'cells': {(WS, H_COL, 6): ('orders_fo', 'Mn'), (WS, H_COL, 7): ('orders_cash', 'Mn'),
                  (WS, H_COL, 8): ('orders_comm', 'Mn'), (WS, H_COL, 15): ('revmix_fo', 'fraction'),
                  (WS, H_COL, 16): ('revmix_cash', 'fraction'), (WS, H_COL, 17): ('revmix_comm', 'fraction'),
                  (WS, H_COL, 40): ('share_cash_q', 'fraction'), (WS, H_COL, 99): ('total_income', 'Rs Mn'),
                  (WS, 'C', H_ROW2): ('orders_total', 'Mn'), (WS, 'F', H_ROW2): ('orders_comm', 'Mn')},
        'pins': {'fo_pct_last_actual_quarter': 'Q2 FY 2027', 'fo_take_rate_last_actual_quarter': 'Q2 FY 2027',
                 'cash_last_actual_quarter': 'Q2 FY 2027', 'mtf_last_actual_quarter': 'Q2 FY 2027'},
    },
}

# switch -> monthly input series extended with reviewed monthly facts for months the workbook does not have
MONTHLY_SWITCHES = {
    # (i) F&O and commodity monthly inputs run to the latest disclosed month (Sep 2026) instead of the
    #     workbook's cut-offs (F&O share and total orders: May-26; commodity total orders: Jun-26; commodity
    #     share: Aug-26). Months the workbook already has are not changed. Cash is covered by (e) and (h).
    'i': ('share_fo', 'total_orders', 'share_comm'),
}

IMPLEMENTED = (set(CELL_SWITCHES) | set(MARKET_SWITCHES) | set(SUMMARY_SWITCHES) | set(PROJECTION_SWITCHES)
               | set(QUARTER_SWITCHES) | set(MONTHLY_SWITCHES))


class SwitchError(ValueError):
    pass


def check(switches):
    switches = set(switches)
    unknown = switches - set(ORDER)
    if unknown:
        raise SwitchError(f'unknown switch(es) {sorted(unknown)}')
    missing = switches - IMPLEMENTED
    if missing:
        raise SwitchError(f'switch(es) {sorted(missing)} not implemented yet')
    return frozenset(switches)


def cumulative(letter):
    """Switches on before and after `letter` when applied in order (for a bridge)."""
    i = ORDER.index(letter)
    return frozenset(ORDER[:i]), frozenset(ORDER[:i + 1])


def cell_overrides(switches, facts, seed_units):
    """{(sheet, col, row): (value, fact_id, switch)} for the switches that are on.

    facts: src.live.loader.Facts (precedence: reviewed first).
    seed_units: {(sheet, col, row): unit of the seed fact for that cell}.
    """
    out = {}
    for sw in sorted(switches):
        for cell, (metric, period) in CELL_SWITCHES.get(sw, {}).items():
            if not facts.has(metric, period):
                raise SwitchError(f'switch {sw}: no reviewed fact {metric} {period}')
            f = facts.fact(metric, period)
            if f.status != 'reviewed':
                raise SwitchError(f'switch {sw}: {metric} {period} has no reviewed fact (got {f.status} {f.fact_id})')
            if seed_units.get(cell) != f.unit:
                raise SwitchError(f'switch {sw}: unit of {cell} is {seed_units.get(cell)!r}, fact {f.fact_id} is {f.unit!r}')
            out[cell] = (f.value, f.fact_id, sw)
        q = QUARTER_SWITCHES.get(sw)
        if q:
            for cell, (metric, unit) in q['cells'].items():
                if not facts.has(metric, q['quarter']):
                    raise SwitchError(f'switch {sw}: no reviewed fact {metric} {q["quarter"]}')
                f = facts.fact(metric, q['quarter'])
                if f.status != 'reviewed':
                    raise SwitchError(f'switch {sw}: {metric} {q["quarter"]} has no reviewed fact')
                if f.unit != unit:
                    raise SwitchError(f'switch {sw}: {metric} {q["quarter"]} is in {f.unit!r}, expected {unit!r}')
                out[cell] = (f.value, f.fact_id, sw)
    return out


def quarter_columns(switches):
    """Extra {quarter: column} and {quarter: quarterly-table row} added by quarter switches."""
    cols, rows = {}, {}
    for sw in sorted(switches):
        q = QUARTER_SWITCHES.get(sw)
        if q:
            cols[q['quarter']], rows[q['quarter']] = q['col'], q['row2']
    return cols, rows


def pin_overrides(switches):
    out = {}
    for sw in sorted(switches):
        out.update(QUARTER_SWITCHES.get(sw, {}).get('pins', {}))
    return out


def market_overrides(switches, mkt, lake):
    """{(dataset, metric): {date: (value, 'ok')}} replacing imputed days with the lake's value.

    mkt: {(dataset, metric): {date: (value, status)}}; lake: {(dataset, metric): {date: value}}.
    An imputed day with no lake value is left as it is (status 'imputed'), for E5 to block on.
    """
    out = {}
    for sw in sorted(switches):
        for key in MARKET_SWITCHES.get(sw, ()):
            out[key] = {d: (lake[key][d], 'ok') for d, (v, st) in mkt[key].items()
                        if st == 'imputed' and d in lake.get(key, {})}
    return out


def excluded_dates(I):
    """Dates left out of averages under the summary switches that are on (ISO strings)."""
    if 'd' in I.switches:
        return {d for d, r in I.cal.items() if r.get('special_session')}
    return set()


def monthly_share(facts, metric, month, back=12):
    """(value, month used, fact_id) for the share of `month`, or of the latest earlier month (≤ `back` back)."""
    from .inputs import MONTHS
    fy, i = int(month[3:7]), MONTHS.index(month[8:])
    for k in range(back + 1):
        idx = fy * 12 + i - k
        m = f"FY {idx // 12} {MONTHS[idx % 12]}"
        if facts.has(metric, m):
            f = facts.fact(metric, m)
            return f.value, m, f.fact_id
    raise SwitchError(f'no {metric} for {month} or the {back} months before it')


def quarter_comm_rates(I, tr):
    """{quarter: (Rs/order, 'actual')} for every quarter with a commodity take rate.

    tr = calibrate.take_rates(I) (cells, so switches a, b apply). A quarter whose mix cell is empty but
    which has a reviewed revmix_comm fact (Q2 FY25) uses that fact with the quarter's income and orders.
    """
    from .calibrate import qcols
    out = {}
    for q, col in qcols(I).items():
        r = tr.get(q, {})
        if 'take_rate_comm' in r:
            out[q] = (r['take_rate_comm'], 'actual')
            continue
        ti, orders = I.ws(col, 99), I.ws(col, 8)
        if I.facts is not None and I.facts.has('revmix_comm', q) and ti and orders:
            f = I.facts.fact('revmix_comm', q)
            if f.status == 'reviewed':
                out[q] = (f.value * ti / orders, 'actual')
    return out


def comm_rate_for(rates, q):
    """(rate, regime, source quarter) for quarter q under switch f."""
    key = lambda x: (int(x[-4:]), int(x[1]))
    if q in rates:
        return rates[q][0], 'actual', q
    have = sorted(rates, key=key)
    earlier = [x for x in have if key(x) < key(q)]
    src = earlier[-1] if earlier else have[0]
    return rates[src][0], 'projected', src


def extend_monthly(I, metric, series, also_present=()):
    """Copy of `series` ({fy_month: value}) plus reviewed monthly facts of `metric` for months not in it
    (nor in any of `also_present`), when a monthly switch covering `metric` is on."""
    out = dict(series)
    if not any(metric in MONTHLY_SWITCHES.get(sw, ()) for sw in I.switches) or I.facts is None:
        return out
    taken = set(out).union(*[set(x) for x in also_present])
    for (m, period, seg), f in I.facts.current.items():
        if m == metric and f.period_type == 'M' and f.status == 'reviewed' and not seg and period not in taken:
            out[period] = f.value
    return out
