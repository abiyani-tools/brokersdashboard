"""MOSL parity -> live switches m-a ... m-f (docs/MOSL_LIVE_SPEC.md). Each switch is exact and isolated; no switches =
the workbook (264 / 264). The recomputes below use the raw series and the reviewed facts, not the engine's own tables.
Run: python -m pytest tests/test_mosl_switches.py -q"""
import copy
import json
import os
import sys
from collections import defaultdict

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.engine import mosl, mosl_bridge as B, mosl_switches as MS, parity_mosl as PM, summary
from src.engine import summary_periods as SP
from src.engine.inputs import q_of, quarter_seq

ROOT = os.path.join(os.path.dirname(__file__), '..')
_cache = {}


def run(sw=''):
    """(M, res) for a switch string, cached."""
    if sw not in _cache:
        _cache[sw] = B.run_switches(tuple(sw))
    return _cache[sw]


def reviewed():
    return MS.load_reviewed()


def facts():
    return {(f['metric'], f['period_key']): f for f in reviewed()}


def qsum(rows, field, q):
    return sum(r[field] for d, r in rows.items() if q_of(d) == q and r[field] is not None)


def overlay_with(rows, sw='a'):
    return mosl.MoslInputs(json.load(open(PM.MOSL_SNAPSHOT)), json.load(open(PM.SHARED_SNAPSHOT)), tuple(sw), rows,
                           lake=mosl.load_lake() if 'b' in sw else None)


# ── the fixture ──
def test_reviewed_fixture_is_the_290_candidates_as_reviewed():
    rows = reviewed()
    cand = json.load(open(MS.CANDIDATES))['sb_disclosure_facts']
    assert len(rows) == len(cand) == 290 and {r['status'] for r in rows} == {'reviewed'}
    assert sorted(r['fact_id'] for r in rows) == list(range(20001, 20291))
    assert all(r['broker_id'] == 'MOSL' and r['doc_id'] for r in rows)
    assert [(r['metric'], r['period_key'], r['segment'], r['value'], r['unit']) for r in rows] == \
        [(c['metric'], c['period_key'], c['segment'], c['value'], c['unit']) for c in cand]
    assert json.load(open(MS.REVIEWED)) == MS.build_reviewed_fixture()          # reproducible from the candidates


# ── no switches = parity ──
def test_no_switches_is_the_workbook():
    M, res = run('')
    assert M.switches == frozenset() and M.overlay == {} and M.qs == mosl.Q_ALL
    fixtures = json.load(open(PM.MOSL_FIXTURES))
    cells, _ = summary.build(res['daily'], 'MOSL')
    rows = PM.compare_summary(cells, fixtures)
    assert len(rows) == 264 and all(r['ok'] for r in rows)
    assert all(not r['mismatches'] for r in PM.compare_daily(res, fixtures).values())
    assert all('regime' not in r for seg in res['daily'].values() for r in seg.values())    # parity rows are unchanged


def test_order_and_unknown_switch():
    assert MS.ORDER == 'abcdef' and MS.cumulative('d') == (frozenset('abc'), frozenset('abcd'))
    with pytest.raises(MS.SwitchError):
        MS.check('x')
    with pytest.raises(MS.SwitchError):
        mosl.MoslInputs(json.load(open(PM.MOSL_SNAPSHOT)), json.load(open(PM.SHARED_SNAPSHOT)), ('a',))   # needs the facts


# ── the same-unit / reviewed rule ──
def _tweak(metric, period, **kw):
    rows = copy.deepcopy(reviewed())
    for r in rows:
        if (r['metric'], r['period_key']) == (metric, period):
            r.update(kw)
    return rows


def test_unit_mismatch_raises():
    with pytest.raises(MS.SwitchError, match='gross_brokerage_fo'):
        overlay_with(_tweak('gross_brokerage_fo', 'Q2 FY 2027', unit='Rs Cr'))
    with pytest.raises(MS.SwitchError, match='adto_cash'):
        overlay_with(_tweak('adto_cash', 'Q1 FY 2027', unit='Rs Mn'))
    with pytest.raises(MS.SwitchError, match='share_comm'):
        overlay_with(_tweak('share_comm', 'Q1 FY 2027', unit='Mn'))
    snap = json.load(open(PM.MOSL_SNAPSHOT))                                      # the workbook input's unit
    for f in snap['facts']:
        if (f['metric'], f['period_key']) == ('gross_fo_cr', 'Q4 FY 2026'):
            f['unit'] = 'Rs Mn'
    with pytest.raises(MS.SwitchError, match=r"unit of gross_fo_cr Q4 FY 2026 is 'Rs Mn'"):
        mosl.MoslInputs(snap, json.load(open(PM.SHARED_SNAPSHOT)), ('a',), reviewed())


def test_unreviewed_fact_raises():
    with pytest.raises(MS.SwitchError, match='not reviewed'):
        overlay_with(_tweak('net_brokerage_cash', 'Q2 FY 2027', status='staged'))
    rows = [r for r in reviewed() if not (r['metric'] == 'gross_brokerage_comm' and r['period_key'] == 'Q2 FY 2027')]
    with pytest.raises(MS.SwitchError, match='no reviewed fact gross_brokerage_comm Q2 FY 2027'):
        overlay_with(rows)


# ── m-a: reported quarters from the data book ──
def test_a_every_reported_quarter_ties_to_the_data_book():
    """Independent recompute: the quarter's daily gross sums to the fact (Rs Mn / 10 = Rs Cr), and the net to the net fact."""
    M, res = run('a')
    F = facts()
    for q in MS.REPORTED:
        fo, cash, comm = res['daily']['fo'], res['daily']['cash'], res['daily']['comm']
        assert qsum(fo, 'gross_mn', q) / 10 == pytest.approx(F[('gross_brokerage_fo', q)]['value'] / 10, rel=1e-9), q
        assert qsum(fo, 'rev_mn', q) == pytest.approx(F[('net_brokerage_fo', q)]['value'], rel=1e-9), q
        assert qsum(cash, 'gross_cr', q) == pytest.approx(F[('gross_brokerage_cash', q)]['value'] / 10, rel=1e-9), q
        assert qsum(cash, 'rev_cr', q) == pytest.approx(F[('net_brokerage_cash', q)]['value'] / 10, rel=1e-9), q
        assert qsum(comm, 'gross_mn', q) == pytest.approx(F[('gross_brokerage_comm', q)]['value'], rel=1e-9), q
        assert qsum(comm, 'rev_mn', q) == pytest.approx(F[('net_brokerage_comm', q)]['value'], rel=1e-9), q


def test_a_q2_fy27_is_actual_and_q1_fy27_cash_is_fed():
    M, res = run('a')
    F = facts()
    assert all(r['regime'] == 'actual' for d, r in res['daily']['fo'].items() if q_of(d) == 'Q2 FY 2027')
    assert all(r['regime'] == 'actual' for d, r in res['daily']['comm'].items() if q_of(d) == 'Q2 FY 2027')
    assert all(r['regime'] == 'projected' for d, r in res['daily']['fo'].items() if q_of(d) == 'Q3 FY 2027')
    # Q1 FY27 cash: the data book's 228.30 is fed (the workbook ties to 224.98: J52 = J51)
    assert qsum(res['daily']['cash'], 'gross_cr', 'Q1 FY 2027') == pytest.approx(228.3005, abs=1e-3)
    assert qsum(run('')[1]['daily']['cash'], 'gross_cr', 'Q1 FY 2027') == pytest.approx(224.98, abs=1e-2)
    # MTF: the closing book is the reported one (workbook carried 5.776% -> 8,729 vs 9,600 reported)
    m = res['calib']['mtf']
    assert m['share']['Q2 FY 2027'] * m['industry_close']['Q2 FY 2027'] == pytest.approx(9600.0, rel=1e-12)
    assert m['share']['Q2 FY 2027'] == pytest.approx(0.0635, abs=5e-5)


def test_a_q2_fy27_gap_to_the_workbook_estimate_is_the_documented_one():
    """Methodology section 5: Q2 FY27 broking net 261.76 estimated vs 276.64 reported (-5.4%)."""
    before, after = run('')[1]['daily'], run('a')[1]['daily']
    net = lambda r: (qsum(r['fo'], 'rev_mn', 'Q2 FY 2027') / 10 + qsum(r['cash'], 'rev_cr', 'Q2 FY 2027')
                     + qsum(r['comm'], 'rev_mn', 'Q2 FY 2027') / 10)
    assert net(before) == pytest.approx(261.76, abs=0.05) and net(after) == pytest.approx(276.64, abs=0.05)


def test_a_q3_fy27_keeps_the_workbook_estimate_rules():
    _, res = run('a')
    d = res['daily']
    oct_cash = [x for x in d['cash'] if q_of(x) == 'Q3 FY 2027']
    assert len(oct_cash) == 13 and all(d['cash'][x]['err'] == '#N/A' for x in oct_cash)
    assert d['comm']['2026-10-12']['err'] == '#N/A' and '2026-10-13' not in d['comm']
    assert max(d['mtf']) == '2026-09-30'
    assert d['fo']['2026-10-21']['regime'] == 'projected' and d['fo']['2026-10-21']['rev_mn'] > 0


def test_a_zero_quarters_are_calibrated_and_earlier_days_are_unchanged():
    before, after = run('')[1]['daily'], run('a')[1]['daily']
    assert before['fo']['2024-04-01']['rev_mn'] == 0.0 and after['fo']['2024-04-01']['rev_mn'] > 0       # Q1 FY25: blank rate
    assert min(before['cash']) == '2024-10-01' and min(after['cash']) == '2024-04-01'                   # cash from Q1 FY25
    assert before['fo']['2023-10-03']['err'] == '#N/A' and after['fo']['2023-10-03']['err'] == '#N/A'  # no fact before Q1 FY25
    assert after['fo']['2024-05-31']['err'] == '#VALUE!'                                                # the workbook's text cell


def test_a_overlay_is_declared_in_the_data_books_units():
    M = run('a')[0]
    o = M.overlay[('gross_fo_cr', 'Q2 FY 2027')]
    assert o.unit == 'Rs Cr' and o.value == pytest.approx(188.46755, abs=1e-4) and o.seed is None
    n = M.overlay[('net_gross_cash', 'Q2 FY 2027')]
    assert n.value == pytest.approx(1320.35 / 2377.94, abs=1e-5) and len(n.fact_ids) == 2
    same = M.overlay[('gross_fo_cr', 'Q1 FY 2026')]
    assert not same.changed and same.value == same.seed                      # identical to the workbook: seed value kept
    assert len(M.overlay) == 8 * 10 + 3 * 10


# ── m-b: keys on the right dates (the lake) ──
def lake():
    return json.load(open(MS.LAKE_FIXTURE))['series']


def test_b_cash_day_is_the_lake_turnover_on_its_own_date():
    """Independent recompute: a calibrated quarter's daily cash gross = quarter gross x K_d / sum K, K = lake NSE + BSE."""
    _, res = run('ab')
    L = lake()
    nse, bse = {d: v for d, v, s in L['nse_cash/turnover_cr']}, {d: v for d, v, s in L['bse_cash/turnover_cr']}
    F = facts()
    for q in ('Q4 FY 2025', 'Q1 FY 2026', 'Q2 FY 2026', 'Q2 FY 2027'):
        days = [d for d in res['daily']['cash'] if q_of(d) == q]
        tot = sum(nse[d] + bse[d] for d in days)
        gross = F[('gross_brokerage_cash', q)]['value'] / 10
        for d in days[::7]:
            assert res['daily']['cash'][d]['gross_cr'] == pytest.approx(gross * (nse[d] + bse[d]) / tot, rel=1e-9), d


def test_b_the_workbook_column_was_two_rows_off_from_9_jun_2025():
    a, b = run('a')[1]['daily']['cash'], run('ab')[1]['daily']['cash']
    assert a['2025-03-20']['gross_cr'] == pytest.approx(b['2025-03-20']['gross_cr'], rel=1e-12)         # a quarter before 9 Jun: same
    assert a['2025-06-10']['gross_cr'] != pytest.approx(b['2025-06-10']['gross_cr'], rel=1e-3)           # after: own date
    moved = [abs(b[d]['gross_cr'] / a[d]['gross_cr'] - 1) for d in a if d >= '2025-06-09']
    assert sorted(moved)[len(moved) // 2] > 0.05                                                         # median day moves > 5%
    for q in MS.REPORTED[2:]:                                                                            # quarter totals tie
        assert qsum(a, 'gross_cr', q) == pytest.approx(qsum(b, 'gross_cr', q), rel=1e-9) or q == 'Q3 FY 2027'


def test_b_f_and_o_key_equals_the_workbooks_except_the_text_cell():
    snap = json.load(open(PM.MOSL_SNAPSHOT))
    wb = {m['trade_date']: m['value'] for m in snap['market_daily'] if m['metric'] == 'index_opt_contracts'}
    L = lake()
    lk = {d: v for d, v, s in L['nse_fo/io_contracts']}
    assert [d for d in wb if wb[d] is not None and wb[d] != lk[d]] == []
    a, b = run('a')[1]['daily']['fo'], run('ab')[1]['daily']['fo']
    assert a['2024-05-31']['err'] == '#VALUE!' and b['2024-05-31']['err'] is None and b['2024-05-31']['rev_mn'] > 0
    assert '2023-09-29' in b and '2023-09-29' not in a and b['2023-09-29']['err'] == '#N/A'
    for d in a:                                                       # every other F&O day is bit-identical
        if d not in ('2024-05-31', '2024-04-01') and q_of(d) != 'Q1 FY 2025' and a[d]['rev_mn'] is not None:
            assert b[d]['rev_mn'] == pytest.approx(a[d]['rev_mn'], rel=1e-12), d


def test_b_moves_days_not_quarter_totals():
    t_a, t_b = (B.adr(*run(s), periods=B.PERIODS) for s in ('a', 'ab'))
    for k in t_a:
        assert t_b[k] == pytest.approx(t_a[k], rel=1e-9), k


def test_b_needs_the_lake_series():
    with pytest.raises(MS.SwitchError, match='lake'):
        mosl.MoslInputs(json.load(open(PM.MOSL_SNAPSHOT)), json.load(open(PM.SHARED_SNAPSHOT)), ('a', 'b'), reviewed())
    L = mosl.load_lake()
    del L['nse_cash/turnover_cr']
    with pytest.raises(MS.SwitchError, match='nse_cash/turnover_cr'):
        mosl.MoslInputs(json.load(open(PM.MOSL_SNAPSHOT)), json.load(open(PM.SHARED_SNAPSHOT)), ('a', 'b'), reviewed(), L)
    L = mosl.load_lake()
    del L['bse_cash/turnover_cr']['2025-06-10']
    M = mosl.MoslInputs(json.load(open(PM.MOSL_SNAPSHOT)), json.load(open(PM.SHARED_SNAPSHOT)), ('a', 'b'), reviewed(), L)
    with pytest.raises(KeyError, match='2025-06-10'):                  # a missing day is loud, never a silent drop
        mosl.run(M)
