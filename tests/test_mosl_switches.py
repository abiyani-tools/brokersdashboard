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


# ── m-c: no silent zeros ──
def test_c_error_rows_are_not_days_and_nothing_else_moves():
    _, a = run('ab')
    _, b = run('abc')
    for seg in ('fo', 'cash', 'comm', 'mtf'):
        assert not any(r.get('err') for r in b['daily'][seg].values())
        assert set(b['daily'][seg]) == {d for d, r in a['daily'][seg].items() if not r.get('err')}
        for d, r in b['daily'][seg].items():                          # every surviving day is bit-identical
            assert r == a['daily'][seg][d]
    errs = {seg: sorted(d for d, r in a['daily'][seg].items() if r.get('err')) for seg in ('fo', 'cash', 'comm')}
    assert len(errs['fo']) == 124 and errs['cash'][0] == '2026-10-01' and len(errs['cash']) == 13
    assert len(errs['comm']) == 7 and errs['comm'][-1] == '2026-10-12'


def test_c_fy27_cash_and_commodities_are_averages_of_the_days_that_have_a_value_not_zero():
    M, res = run('abc')
    segs = B.segments(M, res)
    before = B.segments(*run('ab'))
    assert before['Cash'].fy('FY 2027') == 0.0 and before['Commodities'].fy('FY 2027') == 0.0       # IFERROR 0 (issue 1)
    cash = [r['rev_cr'] for d, r in res['daily']['cash'].items() if d >= '2026-04-01']
    comm = [r['rev_mn'] / 10 for d, r in res['daily']['comm'].items() if d >= '2026-04-01']
    assert len(cash) == 125 and len(comm) == 130              # April - September: October has no cash or commodity row until m-e
    assert segs['Cash'].fy('FY 2027') == pytest.approx(sum(cash) / len(cash), rel=1e-12)
    assert segs['Commodities'].fy('FY 2027') == pytest.approx(sum(comm) / len(comm), rel=1e-12)
    t = B.adr(M, res)
    assert t[('FY', 'FY 2027', 'Broking')] == pytest.approx(
        t[('FY', 'FY 2027', 'F&O')] + t[('FY', 'FY 2027', 'Cash')] + t[('FY', 'FY 2027', 'Commodities')], rel=1e-12)
    assert t[('FY', 'FY 2027', 'Consolidated')] > 8.0                # the workbook shows 5.79


def test_c_a_period_with_no_value_is_flagged_insufficient_not_zero():
    M, res = run('abc')
    rows = B.live_period_rows(M, res)
    cash_oct = [r for r in rows if r['panel'] == 'Cash' and r['period_key'] == 'FY 2027 October'
                and r['row_label'] == 'FY 2027 October']
    assert len(cash_oct) == 1 and cash_oct[0]['value'] is None and 'no trading days' in cash_oct[0]['note']
    cons = [r for r in rows if r['panel'] == 'Consolidated' and r['row_label'] == 'FY 2027 October'][0]
    assert cons['value'] is None                                      # a sum with an insufficient part is insufficient


DB_LAKE = os.path.join(ROOT, 'snapshot', 'mosl_lake_db_2026-11-02.json')


def test_c_zero_and_non_ok_lake_days_get_no_row():
    """The database as read on 2 Nov 2026: io_contracts zero (suspect) on 12-15 Oct, BSE cash 0.0 (ok) on 15 Jun 2026."""
    _, no_c = B.run_switches('ab', lake_path=DB_LAKE)
    _, with_c = B.run_switches('abc', lake_path=DB_LAKE)
    assert no_c['daily']['cash']['2026-06-15']['gross_cr'] > 0                 # b alone: the zero is averaged in as NSE only
    assert '2026-06-15' not in with_c['daily']['cash']
    for d in ('2026-10-12', '2026-10-13', '2026-10-14', '2026-10-15'):
        assert d in no_c['daily']['fo'] and d not in with_c['daily']['fo']
    assert max(with_c['daily']['fo']) == '2026-10-09' and max(no_c['daily']['fo']) == '2026-10-15'
    # the reported quarter still ties to the data book without the dropped day
    F = facts()
    assert qsum(with_c['daily']['cash'], 'gross_cr', 'Q1 FY 2027') == pytest.approx(
        F[('gross_brokerage_cash', 'Q1 FY 2027')]['value'] / 10, rel=1e-9)


# ── m-d: periods and comparisons from the calendar ──
def _means(rows, field, scale, in_period, skip=()):
    v = [r[field] / scale for d, r in rows.items() if in_period(d) and d not in skip]
    return sum(v) / len(v)


def test_d_special_sessions_leave_the_fo_cash_and_commodity_averages_but_not_mtf():
    M, res = run('abcd')
    special = {d for d, r in M.cal.items() if r.get('special_session')}
    assert {'2024-11-01', '2025-02-01', '2025-10-21', '2026-02-01'} <= special
    segs = B.segments(M, res)
    fy26 = lambda d: d.startswith(('2025-04', '2025-05', '2025-06', '2025-07', '2025-08', '2025-09', '2025-1', '2026-01',
                                   '2026-02', '2026-03'))
    d = res['daily']
    assert segs['F&O'].fy('FY 2026') == pytest.approx(_means(d['fo'], 'rev_mn', 10, fy26, special), rel=1e-12)
    assert segs['Cash'].fy('FY 2026') == pytest.approx(_means(d['cash'], 'rev_cr', 1, fy26, special), rel=1e-12)
    assert segs['MTF'].fy('FY 2026') == pytest.approx(_means(d['mtf'], 'nii_cr', 1, fy26), rel=1e-12)   # MTF keeps them
    plain = B.segments(*run('abc'))
    assert plain['F&O'].fy('FY 2026') != segs['F&O'].fy('FY 2026')


def test_d_only_the_periods_with_a_special_session_move():
    t_c, t_d = B.adr(*run('abc')), B.adr(*run('abcd'))
    for k in t_c:
        moved = t_d[k] != pytest.approx(t_c[k], rel=1e-12)
        assert moved == (k[1] == 'FY 2026' and k[2] != 'MTF'), k                  # FY27 has no special session yet


def test_d_yoy_is_the_same_period_last_year_not_the_workbooks_typed_row():
    M, res = run('abcd')
    rows = B.live_period_rows(M, res)
    get = lambda panel, label: next(r for r in rows if (r['panel'], r['period_key'], r['row_label']) ==
                                    (panel, 'Q2 FY 2027', label))
    yoy = get('Consolidated', 'Q2 FY 2027 | YoY')
    assert yoy['comparison'] == 'YoY'
    ly = get('Consolidated', 'Q2 FY 2026')                                           # the comparator row is labelled Q2 FY26
    assert yoy['comp_value'] == pytest.approx(yoy['value'] / ly['value'] - 1, rel=1e-12)
    assert get('Consolidated', 'Q1 FY 2027')['value'] is not None                    # QoQ comparator
    t = B.adr(M, res, (('Q', 'Q2 FY 2027'), ('Q', 'Q2 FY 2026'), ('Q', 'Q4 FY 2026')))
    assert yoy['value'] == pytest.approx(t[('Q', 'Q2 FY 2027', 'Consolidated')], rel=1e-12)
    assert ly['value'] == pytest.approx(t[('Q', 'Q2 FY 2026', 'Consolidated')], rel=1e-12)
    # the workbook's "YoY" (vs Q4 FY26) would have said something else
    wb = t[('Q', 'Q2 FY 2027', 'Consolidated')] / t[('Q', 'Q4 FY 2026', 'Consolidated')] - 1
    assert yoy['comp_value'] != pytest.approx(wb, abs=0.01)


def test_d_standard_panels_labels_from_the_calendar_and_no_net_mtf():
    M, res = run('abcd')
    rows = B.live_period_rows(M, res)
    panels = list(dict.fromkeys(r['panel'] for r in rows))
    assert panels == list(SP.PANELS) and 'MTF (net)' not in panels
    keys = {(r['panel'], r['period_type'], r['period_key'], r['table_name'], r['row_label']) for r in rows}
    assert len(keys) == len(rows)
    assert {r['period_key'] for r in rows if r['period_type'] == 'FY'} >= {'FY 2026', 'FY 2027'}
    assert 'FY 2027 October' in {r['period_key'] for r in rows if r['period_type'] == 'M'}
    # the same generator as Angel One and Groww (one code path): E3 rows built from the calendar
    assert rows == SP.period_rows(B.segments(M, res, guarded=True))


def test_d_parity_summary_still_reads_the_workbook_layout():
    cells, _ = summary.build(run('')[1]['daily'], 'MOSL')
    assert len(cells) == 264
    assert summary.SPECS['MOSL']['labels']['default']['q'][2] == 'Q4 FY 2026'          # parity keeps the typed row


# ── m-e: one estimate rule for the open quarter ──
def _per_unit(rows, field, key, q):
    """net revenue per unit of key over a quarter: sum(net) / sum(key)."""
    days = [d for d in rows if q_of(d) == q]
    return sum(rows[d][field] for d in days) / sum(key[d] for d in days)


def _keys():
    L = lake()
    g = lambda k: {d: v for d, v, s in L[k]}
    io, bse, nc, bc = (g(k) for k in ('nse_fo/io_contracts', 'bse_fo/contracts', 'nse_cash/turnover_cr', 'bse_cash/turnover_cr'))
    shared = json.load(open(PM.SHARED_SNAPSHOT))
    mcx = {m['trade_date']: m['value'] for m in shared['market_daily'] if (m['dataset'], m['metric']) == ('mcx', 'contracts')}
    return ({d: io[d] + bse[d] for d in io}, {d: nc[d] + bc[d] for d in nc}, mcx)


def test_e_open_quarter_carries_the_last_reported_quarters_net_revenue_per_unit_of_key():
    _, res = run('abcde')
    fo_k, cash_k, mcx = _keys()
    d = res['daily']
    for seg, field, key in (('fo', 'rev_mn', fo_k), ('cash', 'rev_cr', cash_k), ('comm', 'rev_mn', mcx)):
        q2 = _per_unit(d[seg], field, key, 'Q2 FY 2027')
        days = [x for x in d[seg] if q_of(x) == 'Q3 FY 2027']
        assert len(days) >= 13, seg
        for x in days:
            assert d[seg][x][field] == pytest.approx(q2 * key[x], rel=1e-9), (seg, x)
            assert d[seg][x]['regime'] == 'projected'
    F = facts()
    for seg, gf in (('cash', 'gross_cr'), ('fo', 'gross_mn'), ('comm', 'gross_mn')):                # and its net / gross
        for x in [x for x in d[seg] if q_of(x) == 'Q3 FY 2027'][:3]:
            n, g = F[(f'net_brokerage_{seg}', 'Q2 FY 2027')]['value'], F[(f'gross_brokerage_{seg}', 'Q2 FY 2027')]['value']
            fld = 'rev_cr' if seg == 'cash' else 'rev_mn'
            assert d[seg][x][fld] / d[seg][x][gf] == pytest.approx(n / g, rel=1e-9)


def test_e_no_error_rows_and_no_typed_values_in_the_open_quarter():
    _, res = run('abcde')
    d = res['daily']
    assert not any(r.get('err') for seg in d.values() for r in seg.values())
    assert len([x for x in d['cash'] if q_of(x) == 'Q3 FY 2027']) == 13 and len([x for x in d['comm'] if q_of(x) == 'Q3 FY 2027']) == 14
    m = res['calib']['mtf']
    assert m['share']['Q3 FY 2027'] == m['share']['Q2 FY 2027'] and m['nii']['Q3 FY 2027'] == m['nii']['Q2 FY 2027']
    assert max(d['mtf']) == '2026-10-19' and len([x for x in d['mtf'] if q_of(x) == 'Q3 FY 2027']) == 12   # to the last book day
    book = {x: r['book_cr'] for x, r in d['mtf'].items()}
    ind = {m_['trade_date']: m_['value'] for m_ in json.load(open(PM.SHARED_SNAPSHOT))['market_daily']
           if (m_['dataset'], m_['metric']) == ('mtf_industry', 'book_cr')}
    assert book['2026-10-15'] == pytest.approx(m['share']['Q2 FY 2027'] * ind['2026-10-15'], rel=1e-12)


def test_e_reported_quarters_are_untouched():
    a, b = run('abcd')[1]['daily'], run('abcde')[1]['daily']
    for seg in a:
        for d, r in a[seg].items():
            if q_of(d) != 'Q3 FY 2027':
                assert b[seg][d] == r, (seg, d)


def test_e_alone_carries_q1_fy27_into_q2_fy27_and_the_ratio_without_averaging():
    M, res = run('e')
    F = facts()
    for seg in ('fo', 'cash', 'comm'):
        assert M.pin(f'{seg}_last_actual_quarter') == 'Q1 FY 2027'
    r = {s: mosl.net_gross(M, s, 'Q2 FY 2027') for s in ('fo', 'cash', 'comm')}
    assert r['cash'] == M.fact('net_gross_cash', 'Q1 FY 2027') != (M.fact('net_gross_cash', 'Q1 FY 2027')
                                                                  + M.fact('net_gross_cash', 'Q4 FY 2026')) / 2
    assert r['comm'] == M.fact('net_gross_comm', 'Q1 FY 2027') and r['fo'] == M.fact('net_gross_fo', 'Q1 FY 2027')
    cash = res['daily']['cash']
    assert all(q_of(d) != 'Q3 FY 2027' or cash[d]['err'] is None for d in cash)
    assert set(d for d in cash if q_of(d) in ('Q2 FY 2027', 'Q3 FY 2027')) and all(
        cash[d]['regime'] == 'projected' for d in cash if q_of(d) in ('Q2 FY 2027', 'Q3 FY 2027'))


def test_e_rolls_into_the_next_quarter_without_a_table():
    """A day in Q4 FY27 (an extended lake) is carried from Q2 FY27 too: no range, no typed column."""
    L = mosl.load_lake()
    for k, s in L.items():
        s['2027-01-05'] = s['2026-10-21']
    M = mosl.MoslInputs(json.load(open(PM.MOSL_SNAPSHOT)), json.load(open(PM.SHARED_SNAPSHOT)), tuple('abcde'), reviewed(), L,
                        '2027-01-05')
    res = mosl.run(M)
    assert M.qs[-1] == 'Q4 FY 2027'
    fo_k, cash_k, _ = _keys()
    q2 = _per_unit(res['daily']['fo'], 'rev_mn', fo_k, 'Q2 FY 2027')
    k = L['nse_fo/io_contracts']['2027-01-05'][0] + L['bse_fo/contracts']['2027-01-05'][0]
    assert res['daily']['fo']['2027-01-05']['rev_mn'] == pytest.approx(q2 * k, rel=1e-9)
    q2c = _per_unit(res['daily']['cash'], 'rev_cr', cash_k, 'Q2 FY 2027')
    kc = L['nse_cash/turnover_cr']['2027-01-05'][0] + L['bse_cash/turnover_cr']['2027-01-05'][0]
    assert res['daily']['cash']['2027-01-05']['rev_cr'] == pytest.approx(q2c * kc, rel=1e-9)
