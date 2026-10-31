"""Groww parity -> live switches g-a ... g-g (docs/GROWW_LIVE_SPEC.md), applied in order a -> g.

Same discipline as Angel's switches (src/engine/switches.py):
- a switch is a named, independent addition; with none on, Groww is the workbook (262 / 262 cells);
- a replaced value must resolve to a reviewed fact in the same unit as the input it replaces, or SwitchError;
- the facts come from a reviewed-facts fixture (snapshot/groww_facts_reviewed_*.json), built from
  out/groww/facts_candidates.json by build_reviewed_fixture() below. The fixture treats the candidates as reviewed
  (AB approved the switches on 31 Oct 2026); nothing is written to the database.

Classification vintages in the candidates (`segment`):
- revenue mix (revmix_*): '' = restated in the Q2 FY27 letter, 'cls_pre_q2fy27' = original. The restated value is
  used wherever it exists; the original only where no restatement exists (Q3 FY25, Q4 FY25, Q1 FY26).
- market share (share_*_adto_q): the workbook is on the legacy basis (denominator = exchange turnover; Groww doubled
  the denominator from Q4 FY26). The legacy value is the printed 'denom_exch_x1' where it exists, else 2 x the printed
  'denom_exch_x2' (the doubling the workbook itself applies).
"""
import json
import os
from collections import namedtuple

from .inputs import quarter_seq

ORDER = 'abcdefg'

DESCRIPTIONS = {
    'a': 'Facts from filings: mix on consolidated total income, MTF revenue = MTF mix x total income',
    'b': 'Full FY26: Q1 FY26 calibrated, F&O and cash live from 1 Apr 2025',
    'c': 'BSE F&O unfrozen (Angel switch c: lake values on imputed days)',
    'd': 'Every reported quarter calibrates take rate and share (F&O, cash, commodities), to Q2 FY27',
    'e': 'One estimate rule: unreported quarters carry the last actual share and take rate; no typed growth',
    'f': 'MTF basis: 14.95% x actual FY trading days; share = disclosed MTF revenue / industry book',
    'g': 'Special sessions out of F&O, cash and commodity averages; labels and comparisons from the calendar',
}

HERE = os.path.dirname(__file__)
CANDIDATES = os.path.join(HERE, '..', '..', 'out', 'groww', 'facts_candidates.json')
REVIEWED = os.path.join(HERE, '..', '..', 'snapshot', 'groww_facts_reviewed_2026-10-31.json')

MIX_ORIGINAL = 'cls_pre_q2fy27'
SHARE_X1, SHARE_X2 = 'denom_exch_x1', 'denom_exch_x2'
UNIT_ALIASES = {}

# ── what each switch replaces ──
# ('mix', metric, [quarters])      revenue mix, restated vintage first
# ('fact', metric, [quarters], unit)  the latest-basis fact (segment '')
# ('share', metric, [quarters])    market share on the legacy basis
# ('mtf_rev', [quarters])          MTF revenue (Rs Cr) = MTF mix x total income (Rs Mn), derived
Q = lambda a, b: quarter_seq(a, b)
FACT_SWITCHES = {
    # a: only inputs the parity model reads; Q4 FY26 and Q1 FY27 bases move from the ex-Fisdom/AMC figure to total income
    'a': [('mix', 'revmix_fo', Q('Q2 FY 2026', 'Q4 FY 2026')),
          ('mix', 'revmix_cash', Q('Q2 FY 2026', 'Q1 FY 2027')),
          ('mix', 'revmix_comm', ['Q3 FY 2026']),
          ('fact', 'total_income', ['Q4 FY 2026', 'Q1 FY 2027'], 'Rs Mn'),
          ('share', 'share_fo_adto_q', Q('Q2 FY 2026', 'Q4 FY 2026')),
          ('share', 'share_cash_adto_q', Q('Q2 FY 2026', 'Q1 FY 2027')),
          ('mtf_rev', Q('Q3 FY 2025', 'Q1 FY 2027'))],
    'b': [('mix', 'revmix_fo', ['Q1 FY 2026']), ('mix', 'revmix_cash', ['Q1 FY 2026']),
          ('fact', 'total_income', ['Q1 FY 2026'], 'Rs Mn'),
          ('share', 'share_fo_adto_q', ['Q1 FY 2026']), ('share', 'share_cash_adto_q', ['Q1 FY 2026'])],
    'c': [],
    'd': [('mix', 'revmix_fo', ['Q1 FY 2027', 'Q2 FY 2027']), ('mix', 'revmix_cash', ['Q2 FY 2027']),
          ('mix', 'revmix_comm', ['Q4 FY 2026', 'Q1 FY 2027', 'Q2 FY 2027']),
          ('fact', 'total_income', ['Q2 FY 2027'], 'Rs Mn'),
          ('share', 'share_fo_adto_q', Q('Q1 FY 2027', 'Q2 FY 2027')),
          ('share', 'share_cash_adto_q', ['Q2 FY 2027'])],
    'e': [],
}

# switch -> pin / assumption values it sets
PIN_SWITCHES = {
    'a': {('revenue_base', 'Q4 FY 2026'): 'total_income', ('revenue_base', 'Q1 FY 2027'): 'total_income'},
    'b': {('fo_first_calibrated_quarter', ''): 'Q1 FY 2026', ('cash_first_calibrated_quarter', ''): 'Q1 FY 2026',
          ('revenue_base', 'Q1 FY 2026'): 'total_income'},
    'd': {('fo_last_actual_quarter', ''): 'Q2 FY 2027', ('cash_last_actual_quarter', ''): 'Q2 FY 2027',
          ('comm_first_calibrated_quarter', ''): 'Q3 FY 2026', ('comm_last_actual_quarter', ''): 'Q2 FY 2027'},
}
ASSUME_SWITCHES = {
    # F&O and cash are live from the first day of Q1 FY26; only Q3 FY25 and Q4 FY25 stay zero-filled
    'b': {'first_live_date_fo': '2025-04-01', 'first_live_date_cash': '2025-04-01',
          'zero_fill_quarters': 'Q3 FY 2025,Q4 FY 2025'},
}

MARKET_SWITCHES = {'c': {('bse_fo', 'contracts')}}   # reuses Angel switch c's market_overrides

IMPLEMENTED = set('abcde')


class SwitchError(ValueError):
    pass


def check(switches):
    switches = frozenset(switches)
    unknown = switches - set(ORDER)
    if unknown:
        raise SwitchError(f'unknown Groww switch(es) {sorted(unknown)}')
    missing = switches - IMPLEMENTED
    if missing:
        raise SwitchError(f'Groww switch(es) {sorted(missing)} not implemented yet')
    return switches


def cumulative(letter):
    i = ORDER.index(letter)
    return frozenset(ORDER[:i]), frozenset(ORDER[:i + 1])


Override = namedtuple('Override', 'value fact_ids switch unit vintage seed changed note')


class FactIndex:
    """Reviewed Groww facts by (metric, period, segment). Anything not 'reviewed' is refused."""

    def __init__(self, rows):
        self.rows = {}
        for r in rows:
            if r.get('broker_id') != 'GROWW':
                raise SwitchError(f'not a Groww fact: {r.get("broker_id")} {r.get("metric")}')
            key = (r['metric'], r['period_key'], r.get('segment') or '')
            if key in self.rows:
                raise SwitchError(f'duplicate fact {key}')
            self.rows[key] = r

    def get(self, switch, metric, period, segment=''):
        r = self.rows.get((metric, period, segment))
        if r is None:
            raise SwitchError(f'switch g-{switch}: no reviewed fact {metric} {period}' + (f' [{segment}]' if segment else ''))
        if r['status'] != 'reviewed':
            raise SwitchError(f'switch g-{switch}: {metric} {period} is {r["status"]}, not reviewed (fact {r["fact_id"]})')
        return r

    def has(self, metric, period, segment=''):
        return (metric, period, segment) in self.rows


def _unit_ok(seed_unit, unit):
    return UNIT_ALIASES.get(seed_unit, seed_unit) == UNIT_ALIASES.get(unit, unit)


def _same(a, b):
    return a is not None and abs(a - b) <= 1e-12 * max(1.0, abs(b))


def build_overlay(switches, reviewed_rows, seed_facts, seed_assume):
    """{(metric, period): Override} for the switches that are on.

    seed_facts: {(metric, period): fact row of the Groww snapshot} (the workbook inputs being replaced).
    Raises SwitchError for a missing / unreviewed fact, or a unit that differs from the seed's or the declared one.
    A replacement equal to the seed within 1e-12 keeps the seed value (so identical inputs stay bit-identical).
    """
    idx = FactIndex(reviewed_rows)
    out = {}

    def put(sw, metric, period, value, fact_ids, unit, vintage, note=''):
        seed = seed_facts.get((metric, period))
        if seed is not None:
            if not _unit_ok(seed['unit'], unit):
                raise SwitchError(f'switch g-{sw}: unit of {metric} {period} is {seed["unit"]!r}, fact {fact_ids} is {unit!r}')
            seed_v = seed['value']
        else:
            seed_v = None
        same = _same(seed_v, value)
        out[(metric, period)] = Override(seed_v if same else value, tuple(fact_ids), sw, unit, vintage, seed_v,
                                         not same, note)

    for sw in sorted(check(switches)):
        for spec in FACT_SWITCHES.get(sw, []):
            kind = spec[0]
            if kind == 'mix':
                _, metric, quarters = spec
                for q in quarters:
                    if idx.has(metric, q, ''):
                        f, vintage = idx.get(sw, metric, q, ''), 'restated'
                    else:
                        f, vintage = idx.get(sw, metric, q, MIX_ORIGINAL), 'original (no restatement exists)'
                    if f['unit'] != 'fraction':
                        raise SwitchError(f'switch g-{sw}: {metric} {q} is in {f["unit"]!r}, expected fraction')
                    put(sw, metric, q, f['value'], [f['fact_id']], 'fraction', vintage)
            elif kind == 'fact':
                _, metric, quarters, unit = spec
                for q in quarters:
                    f = idx.get(sw, metric, q, '')
                    if f['unit'] != unit:
                        raise SwitchError(f'switch g-{sw}: {metric} {q} is in {f["unit"]!r}, expected {unit!r}')
                    put(sw, metric, q, f['value'], [f['fact_id']], unit, 'latest')
            elif kind == 'share':
                _, metric, quarters = spec
                for q in quarters:
                    if idx.has(metric, q, SHARE_X1):
                        f = idx.get(sw, metric, q, SHARE_X1)
                        value, vintage = f['value'], 'legacy, as printed'
                    else:
                        f = idx.get(sw, metric, q, SHARE_X2)
                        value, vintage = 2 * f['value'], 'legacy = 2 x printed new basis'
                    if f['unit'] != 'fraction':
                        raise SwitchError(f'switch g-{sw}: {metric} {q} is in {f["unit"]!r}, expected fraction')
                    put(sw, metric, q, value, [f['fact_id']], 'fraction', vintage)
            elif kind == 'mtf_rev':
                _, quarters = spec
                for q in quarters:
                    mix = idx.get(sw, 'revmix_mtf', q, '') if idx.has('revmix_mtf', q, '') \
                        else idx.get(sw, 'revmix_mtf', q, MIX_ORIGINAL)
                    vintage = 'restated' if mix['segment'] == '' else 'original (no restatement exists)'
                    if mix['unit'] != 'fraction':
                        raise SwitchError(f'switch g-{sw}: revmix_mtf {q} is in {mix["unit"]!r}, expected fraction')
                    if idx.has('total_income', q, ''):
                        tf = idx.get(sw, 'total_income', q, '')
                        ti, ti_unit, ti_ids = tf['value'], tf['unit'], [tf['fact_id']]
                    else:                                                  # Q2 / Q3 FY26: the seed equals the filing
                        s = seed_facts.get(('total_income', q))
                        if s is None:
                            raise SwitchError(f'switch g-{sw}: no total income for {q}')
                        ti, ti_unit, ti_ids = s['value'], s['unit'], [f'seed:{s["source_ref"]}']
                    if ti_unit != 'Rs Mn':
                        raise SwitchError(f'switch g-{sw}: total_income {q} is in {ti_unit!r}, expected Rs Mn')
                    rev_cr = mix['value'] * ti / 10.0                      # Rs Mn -> Rs Cr
                    seed_unit = (seed_facts.get(('mtf_revenue', q)) or {}).get('unit', 'Rs Cr')
                    if seed_unit != 'Rs Cr':
                        raise SwitchError(f'switch g-{sw}: unit of mtf_revenue {q} is {seed_unit!r}, expected Rs Cr')
                    put(sw, 'mtf_revenue', q, rev_cr, [mix['fact_id']] + ti_ids, 'Rs Cr', vintage,
                        f'{mix["value"]:.3f} x {ti:,.2f} Rs Mn / 10')
    return out


def pin_overrides(switches):
    out = {}
    for sw in sorted(switches):
        out.update(PIN_SWITCHES.get(sw, {}))
    return out


def assume_overrides(switches):
    out = {}
    for sw in sorted(switches):
        out.update(ASSUME_SWITCHES.get(sw, {}))
    return out


# ── the reviewed-facts fixture ──
FIRST_FACT_ID = 10001


def build_reviewed_fixture(candidates_path=CANDIDATES):
    """snapshot/groww_facts_reviewed_*.json from the candidates: same shape as facts_reviewed_2026-10-23.json.
    fact_id = 10001 + position in the candidate file; status 'reviewed'; doc_id from the documents map (sha256)."""
    cand = json.load(open(candidates_path))
    docs = cand['documents']
    rows = []
    for i, c in enumerate(cand['sb_disclosure_facts']):
        r = dict(c)
        r['fact_id'] = FIRST_FACT_ID + i
        fname = c['source_ref'].split(':', 1)[1].split('#')[0] if ':' in c['source_ref'] else ''
        r['doc_id'] = docs.get(fname, {}).get('sha256')
        r['status'] = 'reviewed'
        r['reviewed_at'] = '2026-10-31T00:00:00+00:00'
        r['created_at'] = '2026-10-31T00:00:00+00:00'
        rows.append(r)
    return {'_about': (f'LOCAL FIXTURE, not the database: the {len(rows)} Groww candidate facts of out/groww/'
                       'facts_candidates.json treated as reviewed (AB approved the Groww live switches on 31 Oct 2026). '
                       'Built by src.engine.groww_switches.build_reviewed_fixture(); fact_id = 10001 + position; '
                       'doc_id = sha256 of the filing named in source_ref.'),
            'facts': rows}


def load_reviewed(path=REVIEWED):
    return json.load(open(path))['facts']


if __name__ == '__main__':
    fx = build_reviewed_fixture()
    with open(REVIEWED, 'w') as fh:
        json.dump(fx, fh, indent=1)
        fh.write('\n')
    print(f'written {os.path.relpath(REVIEWED)} ({len(fx["facts"])} facts)')
