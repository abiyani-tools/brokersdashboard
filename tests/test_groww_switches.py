"""Groww parity -> live switches g-a ... g-g (docs/GROWW_LIVE_SPEC.md). Each switch is exact and isolated;
no switches = the workbook (262 / 262). Run: python -m pytest tests/test_groww_switches.py -q"""
import copy
import json
import os
import sys
from statistics import mean

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.engine import daily, groww, groww_bridge as B, groww_switches as GS, parity_groww as PG, summary
from src.engine import summary_periods as SP
from src.engine.inputs import fy_of, load_snapshot, q_of

ROOT = os.path.join(os.path.dirname(__file__), '..')
_cache = {}


def run(sw=''):
    """(I, G, res) for a switch string, cached."""
    if sw not in _cache:
        _cache[sw] = B.run_switches(tuple(sw))
    return _cache[sw]


def daily_of(sw, seg):
    return run(sw)[2]['daily'][seg]


def reviewed():
    return GS.load_reviewed()


def overlay_with(rows, sw='abcdefg'):
    snap = json.load(open(PG.GROWW_SNAPSHOT))
    return groww.GrowwInputs(snap, tuple(sw), rows)


# ── the fixture ──
def test_reviewed_fixture_is_the_103_candidates_as_reviewed():
    rows = reviewed()
    cand = json.load(open(GS.CANDIDATES))['sb_disclosure_facts']
    assert len(rows) == len(cand) == 103 and {r['status'] for r in rows} == {'reviewed'}
    assert sorted(r['fact_id'] for r in rows) == list(range(10001, 10104))
    assert all(r['broker_id'] == 'GROWW' and r['doc_id'] for r in rows)
    assert [(r['metric'], r['period_key'], r['segment'], r['value'], r['unit']) for r in rows] == \
        [(c['metric'], c['period_key'], c['segment'], c['value'], c['unit']) for c in cand]
    assert json.load(open(GS.REVIEWED)) == GS.build_reviewed_fixture()          # reproducible from the candidates


# ── no switches = parity ──
def test_no_switches_is_the_workbook():
    I, G, res = run('')
    assert G.switches == frozenset() and G.overlay == {} and I.switches == frozenset()
    fixtures = json.load(open(PG.GROWW_FIXTURES))
    cells, _ = summary.build(res['daily'], 'GROWW')
    rows = PG.compare_summary(cells, fixtures)
    assert len(rows) == 264 and all(r['ok'] for r in rows)
    assert all(not r['mismatches'] for r in PG.compare_daily(res, fixtures).values())


def test_order_and_unknown_switch():
    assert GS.ORDER == 'abcdefg' and GS.cumulative('d') == (frozenset('abc'), frozenset('abcd'))
    with pytest.raises(GS.SwitchError):
        GS.check('x')
    with pytest.raises(GS.SwitchError):
        groww.GrowwInputs(json.load(open(PG.GROWW_SNAPSHOT)), ('a',))           # switches need the reviewed facts


# ── the same-unit / reviewed rule ──
def _tweak(metric, period, segment, **kw):
    rows = copy.deepcopy(reviewed())
    for r in rows:
        if (r['metric'], r['period_key'], r['segment']) == (metric, period, segment):
            r.update(kw)
    return rows


def test_unit_mismatch_raises():
    with pytest.raises(GS.SwitchError, match='revmix_fo'):
        overlay_with(_tweak('revmix_fo', 'Q4 FY 2026', '', unit='Rs Mn'), 'a')
    with pytest.raises(GS.SwitchError, match='total_income'):
        overlay_with(_tweak('total_income', 'Q4 FY 2026', '', unit='Rs Cr'), 'a')
    with pytest.raises(GS.SwitchError, match='expected fraction'):                # the fact's own unit
        overlay_with(_tweak('share_fo_adto_q', 'Q2 FY 2026', 'denom_exch_x1', unit='Mn'), 'a')
    snap = json.load(open(PG.GROWW_SNAPSHOT))                                     # the workbook input's unit
    for f in snap['facts']:
        if (f['metric'], f['period_key']) == ('revmix_fo', 'Q4 FY 2026'):
            f['unit'] = 'Rs Mn'
    with pytest.raises(GS.SwitchError, match=r"unit of revmix_fo Q4 FY 2026 is 'Rs Mn'"):
        groww.GrowwInputs(snap, ('a',), reviewed())


def test_unreviewed_fact_raises():
    with pytest.raises(GS.SwitchError, match='not reviewed'):
        overlay_with(_tweak('revmix_mtf', 'Q4 FY 2026', '', status='staged'), 'a')
    rows = [r for r in reviewed() if not (r['metric'] == 'revmix_fo' and r['period_key'] == 'Q3 FY 2026' and r['segment'] == '')]
    with pytest.raises(GS.SwitchError, match='no reviewed fact revmix_fo Q3 FY 2026'):
        overlay_with(rows, 'a')


# ── g-a: facts from filings ──
def test_a_vintages_restated_where_it_exists():
    G = run('a')[1]
    o = G.overlay
    assert o[('revmix_cash', 'Q3 FY 2026')].value == 0.165 and o[('revmix_cash', 'Q3 FY 2026')].vintage == 'restated'
    assert o[('revmix_cash', 'Q2 FY 2026')].value == 0.178                      # not the original 0.194
    assert o[('revmix_comm', 'Q3 FY 2026')].value == 0.035
    for q, mix in (('Q3 FY 2025', 0.02), ('Q4 FY 2025', 0.02), ('Q1 FY 2026', 0.03)):   # MTF: no restatement exists
        assert o[('mtf_revenue', q)].vintage.startswith('original')
    assert o[('mtf_revenue', 'Q4 FY 2026')].vintage == 'restated'


def test_a_mtf_mix_fixes_and_arithmetic():
    o = run('a')[1].overlay
    assert o[('mtf_revenue', 'Q4 FY 2025')].value == pytest.approx(0.02 * 8495.72 / 10, rel=1e-12)     # 16.99 Cr, was 42.5
    assert o[('mtf_revenue', 'Q1 FY 2026')].value == pytest.approx(0.03 * 9484.71 / 10, rel=1e-12)     # 28.45 Cr, was 47.425
    assert o[('mtf_revenue', 'Q4 FY 2026')].value == pytest.approx(0.069 * 15355.35 / 10, rel=1e-12)   # 105.95 Cr, was 73.42
    assert o[('mtf_revenue', 'Q4 FY 2026')].unit == 'Rs Cr' and o[('mtf_revenue', 'Q4 FY 2026')].seed == 73.42
    # Q2 / Q3 FY26 total income is the workbook seed (equal to the filing): recorded as such
    assert any(str(i).startswith('seed:') for i in o[('mtf_revenue', 'Q2 FY 2026')].fact_ids)


def test_a_mix_on_consolidated_total_income():
    G = run('a')[1]
    rev = groww.segment_revenue(G)
    assert rev['fo']['Q4 FY 2026'] == pytest.approx(0.548 * 15355.35, rel=1e-13)
    assert rev['cash']['Q1 FY 2027'] == pytest.approx(0.161 * 15486.7, rel=1e-13)
    assert rev['fo']['Q2 FY 2026'] == pytest.approx(0.569 * (10187.42 + 520.55), rel=1e-13)
    P = groww.segment_revenue(run('')[1])
    assert P['fo']['Q4 FY 2026'] == pytest.approx(0.55 * 14684, rel=1e-13)       # parity unchanged


def test_a_shares_keep_their_workbook_value():
    """The legacy-basis shares of the filings equal the workbook's inputs (the doubling the workbook applies)."""
    P, A = run('')[1], run('a')[1]
    for q in ('Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026'):
        assert A.fact('share_fo_adto_q', q) == P.fact('share_fo_adto_q', q)
    for q in ('Q2 FY 2026', 'Q3 FY 2026', 'Q4 FY 2026', 'Q1 FY 2027'):
        assert A.fact('share_cash_adto_q', q) == P.fact('share_cash_adto_q', q)


def test_a_take_rates_and_daily_ratios():
    P, A = run('')[2]['calib'], run('a')[2]['calib']
    assert A['fo_quarter']['Q4 FY 2026']['take_rate'] / P['fo_quarter']['Q4 FY 2026']['take_rate'] == \
        pytest.approx(0.548 * 15355.35 / (0.55 * 14684), rel=1e-12)
    assert A['fo_quarter']['Q2 FY 2026']['share'] == P['fo_quarter']['Q2 FY 2026']['share']
    pc, ac = daily_of('', 'comm'), daily_of('a', 'comm')
    assert all(ac[d]['rev_mn'] / pc[d]['rev_mn'] == pytest.approx(0.035 / 0.04, rel=1e-12) for d in pc)
    # F&O days of Q2 FY26 move only by the mix change; Q4 FY26 and the carried quarters by base and mix
    pf, af = daily_of('', 'fo'), daily_of('a', 'fo')
    assert af['2025-08-01']['rev_mn'] / pf['2025-08-01']['rev_mn'] == pytest.approx(0.569 / 0.57, rel=1e-12)
    assert af['2026-08-03']['rev_mn'] / pf['2026-08-03']['rev_mn'] == pytest.approx(0.548 * 15355.35 / (0.55 * 14684), rel=1e-12)


def test_a_mtf_share_from_the_fixed_revenue():
    P, A = run('')[2]['calib']['mtf_quarter'], run('a')[2]['calib']['mtf_quarter']
    assert A['Q4 FY 2025']['groww_book_cr'] == pytest.approx((0.02 * 8495.72 / 10) / (0.1495 / 4), rel=1e-12)
    assert A['Q4 FY 2025']['share'] / P['Q4 FY 2025']['share'] == pytest.approx((0.02 * 8495.72 / 10) / 42.5, rel=1e-12)
    assert A['Q2 FY 2027']['share'] == P['Q2 FY 2027']['share']                  # still typed


# ── g-b: Q1 FY26 calibrated ──
# ── g-c: BSE F&O unfrozen ──
# ── g-d: every reported quarter calibrates ──
# ── g-e: one estimate rule ──
# ── g-f: MTF basis ──
# ── g-g: special sessions, periods ──
# ── the orders check ──
# ── bridges ──
@pytest.mark.parametrize('x', list('a'))
def test_each_bridge_builds_and_adds_up(x):
    b = B.bridge(x)
    txt = B.markdown(b)
    assert f'g-{x}' in txt and 'Consolidated' in txt and b['before'] == sorted(GS.cumulative(x)[0])
    cons = {r['period']: r for r in b['rows'] if r['panel'] == 'Consolidated'}
    # Consolidated = Broking + MTF in both runs
    for r in b['rows']:
        if r['panel'] == 'Consolidated':
            br = next(q for q in b['rows'] if (q['period'], q['panel']) == (r['period'], 'Broking'))
            mt = next(q for q in b['rows'] if (q['period'], q['panel']) == (r['period'], 'MTF'))
            assert r['after'] == pytest.approx(br['after'] + mt['after'], rel=1e-12)
            assert r['before'] == pytest.approx(br['before'] + mt['before'], rel=1e-12)
    assert set(cons) == {'FY 2027', 'Q2 FY 2027', 'FY 2027 October', 'FY 2026', 'FY 2026 October'}


def test_bridges_chain_end_to_end():
    """Each bridge's 'after' is the next one's 'before': the effects add up from parity to all seven switches."""
    prev = None
    for x in 'a':
        b = B.bridge(x)
        if prev is not None:
            assert {(r['period'], r['panel']): r['before'] for r in b['rows']} == \
                {(r['period'], r['panel']): r['after'] for r in prev['rows']}
        prev = b
    parity = B.adr(*run(''))
    first = B.bridge('a')
    assert first['rows'][0]['before'] == parity[('FY', 'FY 2027', 'Consolidated')]


def test_cli_dispatches_by_broker(tmp_path, monkeypatch):
    from src.engine import bridge
    monkeypatch.chdir(tmp_path)
    bridge.main(['bridge.py', '--broker', 'GROWW', 'a'])
    assert (tmp_path / 'out' / 'bridges' / 'groww_a.md').exists() and not (tmp_path / 'out' / 'bridges' / 'a.md').exists()
    with pytest.raises(SystemExit):
        bridge.main(['bridge.py', '--broker', 'NOPE', 'a'])


def test_angel_is_untouched():
    from src.engine import parity
    I = load_snapshot(PG.ANGEL_SNAPSHOT)
    res = daily.run(I)
    cells, _ = summary.build(res['daily'])
    rows = parity.compare(res, cells, I.snap['parity_expected'])
    rep = parity.report(rows)
    assert sum(v[0] for v in rep.values()) == 8797 and sum(v[1] for v in rep.values()) == 8774
