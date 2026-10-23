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

IMPLEMENTED = set(CELL_SWITCHES) | set(MARKET_SWITCHES)


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
            f = facts.fact(metric, period)
            if f.status != 'reviewed':
                raise SwitchError(f'switch {sw}: {metric} {period} has no reviewed fact (got {f.status} {f.fact_id})')
            if seed_units.get(cell) != f.unit:
                raise SwitchError(f'switch {sw}: unit of {cell} is {seed_units.get(cell)!r}, fact {f.fact_id} is {f.unit!r}')
            out[cell] = (f.value, f.fact_id, sw)
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
