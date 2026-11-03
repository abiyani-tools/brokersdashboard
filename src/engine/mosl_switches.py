"""MOSL parity -> live switches m-a ... m-f (docs/MOSL_LIVE_SPEC.md, approved by AB on 2 Nov 2026), applied in order a -> f,
and the optional m-g (FY24 quarters; EXTRA, off in the published chain until AB approves it).

Same discipline as Angel's and Groww's switches (src/engine/switches.py, groww_switches.py):
- a switch is a named, independent addition; with none on, MOSL is the workbook (264 / 264 cells);
- a replaced value must resolve to a reviewed fact whose unit is the declared one (and whose engine input has the
  unit the fact is converted to), or SwitchError;
- the facts come from a reviewed-facts fixture (snapshot/mosl_facts_reviewed_*.json), built from
  out/mosl/facts_candidates.json by build_reviewed_fixture() below. The fixture treats the 290 candidates as reviewed
  (AB approved them on 2 Nov 2026); nothing is written to the database.

What each switch does (the engine reads them through MoslInputs.on(letter), src/engine/mosl.py):
  a  every reported quarter Q1 FY25 - Q2 FY27 is calibrated from data-book facts (gross per segment, net / gross, shares,
     cash ADTO, MTF book); Q2 FY27 becomes actual and Q1 FY27 cash gross is fed (J52 = J51 dropped)
  b  keys on their own dates from the lake: cash = NSE + BSE `turnover_cr` (not the workbook column two rows off from
     9 Jun 2025); F&O = NSE `io_contracts` + BSE `contracts` (equal to the workbook's on every common day)
  c  no silent zeros: a missing, non-ok or zero key day gets no row; #N/A / #VALUE! rows are not written
  d  periods and comparisons from the calendar (same live rules as Angel One and Groww): YoY = same period last year,
     labels from the calendar, standard panel order, special sessions out of the F&O / cash / commodity averages
  e  one estimate rule for the open quarter: carry the last reported quarter's net revenue per unit of key (per contract
     for F&O and commodities, per Rs Cr of turnover for cash) and its net / gross; MTF share carried from the last
     reported quarter-end and extended to the last data day
  f  MTF yield: the workbook's typed NII yields kept, the last (12.94%) carried for later quarters from the labelled
     assumption `mtf_nii_yield_carry` ([SOURCE NEEDED: MOSL does not publish an MTF yield])

  g  (AB approved it and the 116 FY24 facts on 3 Nov 2026) MOSL's quarters start at Q2 FY24: F&O, cash and commodities
     calibrate Q2 - Q4 FY24 as m-a does for FY25+, from the 116 FY24 facts (out/mosl/facts_candidates_fy24.json; the
     fixtures snapshot/mosl_facts_fy24_candidates_*.json and mosl_facts_reviewed_2026-11-03.json hold them as reviewed;
     the database gets them from out/mosl/fy24_facts.sql). Q1 FY24 is not calibrated: no revenue row before Q2 FY24,
     and MTF still starts Q3 FY25 (so Consolidated FY24 stays insufficient). The key series must start by 3 Jul 2023

Units. The candidates are in the data book's Rs Mn (x10 of its Rs Cr) and Rs Mn per day; the engine reads Rs Cr and
Rs Cr per day, so each fact is declared with its source unit and divided by 10. Net / gross = net brokerage / gross
brokerage of the same segment and quarter (two facts).
"""
import json
import os
from collections import namedtuple

from .inputs import quarter_seq

ORDER = 'abcdef'                      # the published chain
EXTRA = 'g'                           # m-g: FY24 quarters; off until AB approves it
ALL = ORDER + EXTRA
REQUIRES = {'g': 'ab'}                # g adds FY24 quarters to the calibration a builds, on the lake keys (b) that reach back to Jun 2023

DESCRIPTIONS = {
    'a': 'Reported quarters from the data book: Q1 FY25 - Q2 FY27 calibrated from facts; Q2 FY27 actual; Q1 FY27 cash gross fed',
    'b': 'Keys on the right dates: lake NSE + BSE cash turnover (and the F&O key) on their own dates',
    'c': 'No silent zeros: missing, non-ok and zero key days and error rows are excluded, not averaged as 0',
    'd': 'Periods and comparisons from the calendar; special sessions out of the F&O, cash and commodity averages',
    'e': "One estimate rule: the open quarter carries the last reported quarter's net revenue per unit of key and its net / gross",
    'f': 'MTF yield: typed NII yields kept, the last carried as a labelled assumption (MOSL publishes no MTF yield)',
    'g': 'FY24 quarters: F&O, cash and commodities calibrate Q2 - Q4 FY24 from reviewed data-book facts; MTF still starts Q3 FY25',
}

HERE = os.path.dirname(__file__)
CANDIDATES = os.path.join(HERE, '..', '..', 'out', 'mosl', 'facts_candidates.json')
REVIEWED = os.path.join(HERE, '..', '..', 'snapshot', 'mosl_facts_reviewed_2026-11-02.json')
LAKE_FIXTURE = os.path.join(HERE, '..', '..', 'snapshot', 'mosl_lake_2026-11-02.json')
FY24_CANDIDATES = os.path.join(HERE, '..', '..', 'out', 'mosl', 'facts_candidates_fy24.json')
FY24_REVIEWED = os.path.join(HERE, '..', '..', 'snapshot', 'mosl_facts_fy24_candidates_2026-11-03.json')
REVIEWED_ALL = os.path.join(HERE, '..', '..', 'snapshot', 'mosl_facts_reviewed_2026-11-03.json')
LAKE_DB_FIXTURE_G = os.path.join(HERE, '..', '..', 'snapshot', 'mosl_lake_db_2026-11-03.json')
LAKE_FIXTURE_G =os.path.join(HERE, '..', '..', 'snapshot', 'mosl_lake_2026-11-03.json')
SHARED_FIXTURE_G = os.path.join(HERE, '..', '..', 'snapshot', 'db_snapshot_2026-11-03.json')
LAKE_DB_FIXTURE = os.path.join(HERE, '..', '..', 'snapshot', 'mosl_lake_db_2026-11-02.json')

Q = quarter_seq
REPORTED = Q('Q1 FY 2025', 'Q2 FY 2027')          # every quarter the Q2 FY27 data book reports (latest vintage)

# engine input -> (candidate metric, candidate unit, engine unit, divisor). Value = fact / divisor.
FACT_INPUTS = {
    'gross_fo_cr': ('gross_brokerage_fo', 'Rs Mn', 'Rs Cr', 10.0),
    'gross_cash_cr': ('gross_brokerage_cash', 'Rs Mn', 'Rs Cr', 10.0),
    'gross_comm_cr': ('gross_brokerage_comm', 'Rs Mn', 'Rs Cr', 10.0),
    'share_fo': ('share_fo_premium', 'fraction', 'fraction', 1.0),
    'share_cash': ('share_cash', 'fraction', 'fraction', 1.0),
    'share_comm': ('share_comm', 'fraction', 'fraction', 1.0),
    'adto_cash_mosl': ('adto_cash', 'Rs Mn/day', 'Rs Cr/day', 10.0),
    'mtf_book_closing': ('mtf_book', 'Rs Mn', 'Rs Cr', 10.0),
}
# net / gross = net_brokerage_<seg> / gross_brokerage_<seg>, both Rs Mn
RATIO_INPUTS = {'net_gross_fo': 'fo', 'net_gross_cash': 'cash', 'net_gross_comm': 'comm'}

FY24_QUARTERS = Q('Q2 FY 2024', 'Q4 FY 2024')     # g: the FY24 quarters that are calibrated (Q1 FY24 is not)
FY24_FIRST = FY24_QUARTERS[0]
FY24_FACT_INPUTS = tuple(m for m in FACT_INPUTS if m != 'mtf_book_closing')   # MTF NII still starts Q3 FY25

# a: all of them, every reported quarter; g: the FY24 quarters, without the MTF book
FACT_SWITCHES = {'a': [('fact', m, REPORTED) for m in FACT_INPUTS] + [('ratio', m, REPORTED) for m in RATIO_INPUTS],
                 'g': [('fact', m, FY24_QUARTERS) for m in FY24_FACT_INPUTS]
                 + [('ratio', m, FY24_QUARTERS) for m in RATIO_INPUTS]}

# switch -> pin values it sets (the workbook's table ends and "last actual" markers)
PIN_SWITCHES = {
    'a': {('fo_last_actual_quarter', ''): 'Q2 FY 2027', ('cash_last_actual_quarter', ''): 'Q2 FY 2027',
          ('comm_last_actual_quarter', ''): 'Q2 FY 2027', ('mtf_last_actual_quarter', ''): 'Q2 FY 2027',
          ('fo_zero_quarters', ''): '', ('cash_table_first_quarter', ''): 'Q1 FY 2025'},
    'g': {('fo_table_first_quarter', ''): FY24_FIRST, ('cash_table_first_quarter', ''): FY24_FIRST},
}

YIELD_ASSUMPTION = 'mtf_nii_yield_carry'
YIELD_LABEL = '[SOURCE NEEDED: MOSL does not publish an MTF yield]'

D_SEGMENTS = ('fo', 'cash', 'comm')       # d: special sessions leave these averages; MTF keeps them
IMPLEMENTED = set(ALL)            


class SwitchError(ValueError):
    pass


def check(switches):
    switches = frozenset(switches)
    unknown = switches - set(ALL)
    if unknown:
        raise SwitchError(f'unknown MOSL switch(es) {sorted(unknown)}')
    missing = switches - IMPLEMENTED
    if missing:
        raise SwitchError(f'MOSL switch(es) {sorted(missing)} not implemented yet')
    for sw in sorted(switches & set(REQUIRES)):
        if not set(REQUIRES[sw]) <= switches:
            raise SwitchError(f'MOSL switch m-{sw} needs m-{REQUIRES[sw]}')
    return switches


def cumulative(letter):
    i = ALL.index(letter)
    return frozenset(ALL[:i]), frozenset(ALL[:i + 1])


Override = namedtuple('Override', 'value fact_ids switch unit vintage seed changed note')


class FactIndex:
    """Reviewed MOSL facts by (metric, period). Anything not 'reviewed' is refused."""

    def __init__(self, rows):
        self.rows = {}
        for r in rows:
            if r.get('broker_id') != 'MOSL':
                raise SwitchError(f'not a MOSL fact: {r.get("broker_id")} {r.get("metric")}')
            key = (r['metric'], r['period_key'], r.get('segment') or '')
            if key in self.rows:
                raise SwitchError(f'duplicate fact {key}')
            self.rows[key] = r

    def get(self, switch, metric, period, unit):
        r = self.rows.get((metric, period, ''))
        if r is None:
            raise SwitchError(f'switch m-{switch}: no reviewed fact {metric} {period}')
        if r['status'] != 'reviewed':
            raise SwitchError(f'switch m-{switch}: {metric} {period} is {r["status"]}, not reviewed (fact {r["fact_id"]})')
        if r['unit'] != unit:
            raise SwitchError(f'switch m-{switch}: {metric} {period} is in {r["unit"]!r}, expected {unit!r} (fact {r["fact_id"]})')
        return r


def _same(a, b):
    return a is not None and abs(a - b) <= 1e-9 * max(1.0, abs(b))


def build_overlay(switches, reviewed_rows, seed_facts):
    """{(metric, period): Override} for the switches that are on.

    seed_facts: {(metric, period): fact row of the MOSL snapshot} (the workbook inputs being replaced).
    Raises SwitchError for a missing / unreviewed fact, a unit that differs from the declared source unit, or an engine
    input whose seed unit is not the unit the fact is converted to. A replacement equal to the seed within 1e-9
    (relative) keeps the seed value, so identical inputs stay bit-identical."""
    idx = FactIndex(reviewed_rows)
    out = {}

    def put(sw, metric, period, value, fact_ids, unit, vintage, note=''):
        seed = seed_facts.get((metric, period))
        if seed is not None and seed['unit'] != unit:
            raise SwitchError(f'switch m-{sw}: unit of {metric} {period} is {seed["unit"]!r}, replacement is in {unit!r}')
        seed_v = seed['value'] if seed is not None else None
        same = _same(seed_v, value)
        out[(metric, period)] = Override(seed_v if same else value, tuple(fact_ids), sw, unit, vintage, seed_v,
                                         not same, note)

    for sw in sorted(check(switches)):
        for kind, metric, quarters in FACT_SWITCHES.get(sw, []):
            for q in quarters:
                if kind == 'fact':
                    cand, src_unit, unit, div = FACT_INPUTS[metric]
                    f = idx.get(sw, cand, q, src_unit)
                    put(sw, metric, q, f['value'] / div, [f['fact_id']], unit, 'data book, latest vintage',
                        f'{f["value"]:,.4f} {src_unit}' + (f' / {div:g}' if div != 1.0 else ''))
                else:
                    seg = RATIO_INPUTS[metric]
                    n = idx.get(sw, f'net_brokerage_{seg}', q, 'Rs Mn')
                    g = idx.get(sw, f'gross_brokerage_{seg}', q, 'Rs Mn')
                    put(sw, metric, q, n['value'] / g['value'], [n['fact_id'], g['fact_id']], 'fraction',
                        'data book, latest vintage', f'{n["value"]:,.2f} / {g["value"]:,.2f} Rs Mn')
    return out


def pin_overrides(switches):
    out = {}
    for sw in sorted(switches):
        out.update(PIN_SWITCHES.get(sw, {}))
    return out


# ── the reviewed-facts fixture ──
FIRST_FACT_ID = 20001


def build_reviewed_fixture(candidates_path=CANDIDATES):
    """snapshot/mosl_facts_reviewed_*.json from the candidates: same shape as groww_facts_reviewed_*.json.
    fact_id = 20001 + position in the candidate file; status 'reviewed'; doc_id from the documents map (sha256)."""
    cand = json.load(open(candidates_path))
    docs = cand['documents']
    rows = []
    for i, c in enumerate(cand['sb_disclosure_facts']):
        r = dict(c)
        r['fact_id'] = FIRST_FACT_ID + i
        fname = c['source_ref'].split(':', 1)[1].split('#')[0] if ':' in c['source_ref'] else ''
        r['doc_id'] = docs.get(fname, {}).get('sha256')
        r['status'] = 'reviewed'
        r['reviewed_at'] = '2026-11-02T00:00:00+00:00'
        r['created_at'] = '2026-11-02T00:00:00+00:00'
        rows.append(r)
    return {'_about': (f'LOCAL FIXTURE, not the database: the {len(rows)} MOSL candidate facts of out/mosl/'
                       'facts_candidates.json treated as reviewed (AB approved the MOSL live switches and the facts on '
                       '2 Nov 2026). Built by src.engine.mosl_switches.build_reviewed_fixture(); fact_id = 20001 + '
                       'position; doc_id = sha256 of the data book named in source_ref.'),
            'facts': rows}


def load_reviewed(path=REVIEWED):
    return json.load(open(path))['facts']


# ── the FY24 fixture (reviewed per AB's approval of 3 Nov 2026) ──
FY24_FIRST_FACT_ID = 20291                  # after the 290 reviewed fixture facts (20001 - 20290)
FY24_REVIEWED_AT = '2026-11-03T00:00:00+00:00'
FY24_META = ("the 116 FY24 candidates marked reviewed per AB's approval of 3 Nov 2026 (\"Approve, go live\": switch m-g and "
             'the 116 facts). Local fixture, not the database: the rows reach the database only when out/mosl/fy24_facts.sql '
             'is applied.')
FY24_FIRST_DAY = '2023-07-03'               # the first trading day of Q2 FY24: every key series must reach back to it


def build_fy24_fixture(candidates_path=FY24_CANDIDATES):
    """snapshot/mosl_facts_fy24_candidates_*.json: the 116 FY24 candidates with status 'reviewed' (AB, 3 Nov 2026), the same
    shape as the reviewed fixture. fact_id = 20291 + position."""
    cand = json.load(open(candidates_path))
    docs = cand['documents']
    rows = []
    for i, c in enumerate(cand['sb_disclosure_facts']):
        r = dict(c)
        r['fact_id'] = FY24_FIRST_FACT_ID + i
        fname = c['source_ref'].split(':', 1)[1].split('#')[0] if ':' in c['source_ref'] else ''
        r['doc_id'] = docs.get(fname, {}).get('sha256')
        r['status'] = 'reviewed'
        r['reviewed_at'] = FY24_REVIEWED_AT
        rows.append(r)
    return {'_meta': FY24_META + f' Built by src.engine.mosl_switches.build_fy24_fixture() from out/mosl/'
                     f'facts_candidates_fy24.json ({len(rows)} facts); fact_id = {FY24_FIRST_FACT_ID} + position; '
                     'doc_id = sha256 of the data book named in source_ref.',
            'facts': rows}


def build_reviewed_all_fixture():
    """snapshot/mosl_facts_reviewed_2026-11-03.json: the 290 reviewed facts plus the 116 FY24 facts (406 in all), the
    file-mode default of the live run (switches a-g)."""
    a, b = build_reviewed_fixture(), build_fy24_fixture()
    return {'_about': a['_about'] + ' Plus ' + b['_meta'] + ' (facts 20291 - 20406).', 'facts': a['facts'] + b['facts']}


def fy24_inputs():
    """[(candidate metric, period)] the m-g switch reads: every one must be 'reviewed' before it may go live."""
    out = set()
    for kind, metric, quarters in FACT_SWITCHES['g']:
        for q in quarters:
            if kind == 'fact':
                out.add((FACT_INPUTS[metric][0], q))
            else:
                out |= {(f'net_brokerage_{RATIO_INPUTS[metric]}', q), (f'gross_brokerage_{RATIO_INPUTS[metric]}', q)}
    return sorted(out, key=lambda x: (x[0], int(x[1][-4:]), int(x[1][1])))


if __name__ == '__main__':
    fx = build_reviewed_fixture()
    with open(REVIEWED, 'w') as fh:
        json.dump(fx, fh, indent=1)
        fh.write('\n')
    print(f'written {os.path.relpath(REVIEWED)} ({len(fx["facts"])} facts)')
    fx = build_fy24_fixture()
    with open(FY24_REVIEWED, 'w') as fh:
        json.dump(fx, fh, indent=1)
        fh.write('\n')
    print(f'written {os.path.relpath(FY24_REVIEWED)} ({len(fx["facts"])} facts)')
    fx = build_reviewed_all_fixture()
    with open(REVIEWED_ALL, 'w') as fh:
        json.dump(fx, fh, indent=1)
        fh.write('\n')
    print(f'written {os.path.relpath(REVIEWED_ALL)} ({len(fx["facts"])} facts)')
