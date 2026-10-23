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
}

IMPLEMENTED = set(CELL_SWITCHES)


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
