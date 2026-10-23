"""Parity → live switches (LIVE_SPEC §4). Each switch is exact and isolated; no switches = parity."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.engine.inputs import load_snapshot, Inputs
from src.engine import calibrate, daily, switches as SW

ROOT = os.path.join(os.path.dirname(__file__), '..')
SNAP = os.path.join(ROOT, 'snapshot', 'db_snapshot_2026-10-23.json')
REVIEWED = os.path.join(ROOT, 'snapshot', 'facts_reviewed_2026-10-23.json')


@pytest.fixture(scope='module')
def parity():
    return load_snapshot(SNAP)


@pytest.fixture(scope='module')
def with_a():
    return load_snapshot(SNAP, 'a', REVIEWED)


def test_reviewed_snapshot_is_the_178_reviewed_facts():
    facts = json.load(open(REVIEWED))['facts']
    assert len(facts) == 178 and {f['status'] for f in facts} == {'reviewed'}
    assert sorted(f['fact_id'] for f in facts) == list(range(478, 656))


def test_no_switches_is_parity(parity):
    assert parity.switches == frozenset() and parity.overrides == {}
    assert parity.ws('J', 8) == 36


def test_switch_a_replaces_j8_with_the_reviewed_fact(parity, with_a):
    assert with_a.overrides == {('Working sheet - Angel One', 'J', 8): (35, 596, 'a')}
    assert with_a.ws('J', 8) == 35
    # Commodities!AI11 = J17 × J99 / J8: the fixed take rate rises by exactly 36/35
    tr_parity, q = daily.run(parity)['calib']['comm_take_rate']
    tr_a, _ = daily.run(with_a)['calib']['comm_take_rate']
    assert q == 'Q3 FY 2026'
    assert tr_parity == pytest.approx(22.29495, rel=1e-6)
    assert tr_a / tr_parity == pytest.approx(36 / 35, rel=1e-12)
    # row 10: Q3 FY26 F&O share of orders = 277 / (277 + 68 + J8)
    assert calibrate.take_rates(with_a)['Q3 FY 2026']['fo_pct'] == pytest.approx(277 / 380, rel=1e-12)
    assert calibrate.take_rates(parity)['Q3 FY 2026']['fo_pct'] == pytest.approx(277 / 381, rel=1e-12)


def test_switch_a_moves_only_commodity_and_fo(parity, with_a):
    a, b = daily.run(parity)['daily'], daily.run(with_a)['daily']
    for seg, key in (('cash', 'rev_mn'), ('mtf', 'gross_cr')):
        assert all(a[seg][d][key] == b[seg][d][key] for d in a[seg])
    assert all(b['comm'][d]['rev_mn'] / a['comm'][d]['rev_mn'] == pytest.approx(36 / 35, rel=1e-12)
               for d in a['comm'] if a['comm'][d]['rev_mn'])
    # F&O: Q3 FY26 days rise by 381/380 (their own F&O %), Q4 FY26 days do not move
    assert b['fo']['2025-11-03']['rev_mn'] / a['fo']['2025-11-03']['rev_mn'] == pytest.approx(381 / 380, rel=1e-12)
    assert b['fo']['2026-02-02']['rev_mn'] == a['fo']['2026-02-02']['rev_mn']


def test_a_switch_needs_a_reviewed_fact():
    snap = json.load(open(SNAP))
    reviewed = [f for f in json.load(open(REVIEWED))['facts'] if f['fact_id'] != 596]
    with pytest.raises(SW.SwitchError, match='no reviewed fact'):
        Inputs(snap, 'a', reviewed)


def test_unknown_and_unimplemented_switches_are_refused():
    snap = json.load(open(SNAP))
    with pytest.raises(SW.SwitchError, match='unknown'):
        Inputs(snap, 'z', [])
    with pytest.raises(SW.SwitchError, match='not implemented'):
        Inputs(snap, 'f', [])


def test_cumulative_order():
    assert SW.cumulative('a') == (frozenset(), frozenset('a'))
    assert SW.cumulative('c') == (frozenset('ab'), frozenset('abc'))


@pytest.fixture(scope='module')
def with_ab():
    return load_snapshot(SNAP, 'ab', REVIEWED)


def test_switch_b_replaces_the_21_revenue_mix_cells(with_ab):
    b = {c: v for c, v in with_ab.overrides.items() if v[2] == 'b'}
    assert len(b) == 21 and {c[2] for c in b} == {15, 16, 17} and {c[1] for c in b} == set('FGHIJKM')
    assert with_ab.ws('J', 17) == 0.061 and with_ab.ws('M', 16) == 0.086 and with_ab.ws('F', 15) == 0.525


def test_switch_b_daily_ratios_are_the_mix_ratios(with_a, with_ab):
    a, b = daily.run(with_a)['daily'], daily.run(with_ab)['daily']
    ratio = lambda seg, d, k='rev_mn': b[seg][d][k] / a[seg][d][k]
    # commodity: fixed Q3 FY26 take rate, J17 0.06 -> 0.061, on every day
    assert all(ratio('comm', d) == pytest.approx(0.061 / 0.06, rel=1e-12) for d in a['comm'] if a['comm'][d]['rev_mn'])
    # F&O Q3 FY26 days use their own quarter's take rate: J15 0.44 -> 0.443
    assert ratio('fo', '2025-11-03') == pytest.approx(0.443 / 0.44, rel=1e-12)
    # cash Q1 FY27 is an actual quarter: M16 0.09 -> 0.086
    assert ratio('cash', '2026-05-04') == pytest.approx(0.086 / 0.09, rel=1e-12)
    # cash projected quarters: average of the last three quarters' take rates (Q3 FY26..Q1 FY27)
    assert ratio('cash', '2026-08-03') == pytest.approx(16.5122 / 16.7752, rel=1e-4)
    assert all(a['mtf'][d]['gross_cr'] == b['mtf'][d]['gross_cr'] for d in a['mtf'])


@pytest.fixture(scope='module')
def with_abc():
    return load_snapshot(SNAP, 'abc', REVIEWED)


def test_switch_c_unfreezes_bse_contracts_from_the_lake(with_ab, with_abc):
    days = with_abc.market_overrides[('bse_fo', 'contracts')]
    assert len(days) == 15 and min(days) == '2026-09-29' and max(days) == '2026-10-21'
    assert days['2026-10-01'] == (512976127, 'ok')
    assert all(with_ab.series('bse_fo', 'contracts')[d] == 18962859 for d in days)
    assert with_abc.status('bse_fo', 'contracts')['2026-10-01'] == 'ok'
    assert with_ab.status('bse_fo', 'contracts')['2026-10-01'] == 'imputed'


def test_switch_c_scales_each_day_by_its_market_volume(with_ab, with_abc):
    a, b = daily.run(with_ab)['daily']['fo'], daily.run(with_abc)['daily']['fo']
    nse = with_ab.series('nse_fo', 'contracts')
    old, new = with_ab.series('bse_fo', 'contracts'), with_abc.series('bse_fo', 'contracts')
    changed = {d for d in a if b[d]['rev_mn'] != a[d]['rev_mn']}
    assert changed == set(with_abc.market_overrides[('bse_fo', 'contracts')])
    for d in changed:   # same contracts/order, share and take rate: revenue ∝ NSE + BSE contracts
        assert b[d]['rev_mn'] / a[d]['rev_mn'] == pytest.approx((nse[d] + new[d]) / (nse[d] + old[d]), rel=1e-12)


def test_switch_d_drops_special_sessions_from_averages_only():
    from statistics import mean
    from src.engine import bridge as B
    from src.engine.inputs import fy_month_of
    I_c = load_snapshot(SNAP, 'abc', REVIEWED)
    I_d = load_snapshot(SNAP, 'abcd', REVIEWED)
    assert SW.excluded_dates(I_c) == set()
    assert SW.excluded_dates(I_d) == {'2023-11-12', '2024-03-02', '2024-05-18', '2024-11-01', '2025-10-21'}
    t_c, r_c = B.adr(I_c)
    t_d, r_d = B.adr(I_d)
    assert r_c['daily'] == r_d['daily']                       # daily rows (and totals) untouched
    fo = {d: r['rev_mn'] / 10 for d, r in r_d['daily']['fo'].items() if fy_month_of(d) == 'FY 2026 October'}
    assert t_c[('M', 'FY 2026 October', 'F&O')] == pytest.approx(mean(fo.values()), rel=1e-12)
    assert t_d[('M', 'FY 2026 October', 'F&O')] == pytest.approx(
        mean(v for d, v in fo.items() if d != '2025-10-21'), rel=1e-12)
    for k in ('FY 2027', 'Q2 FY 2027', 'FY 2027 October'):   # no special session in FY27 to date
        p = 'FY' if k == 'FY 2027' else ('Q' if k.startswith('Q') else 'M')
        assert t_c[(p, k, 'Consolidated')] == t_d[(p, k, 'Consolidated')]


def test_switch_e_projected_cash_days_use_the_monthly_share():
    I_d = load_snapshot(SNAP, 'abcd', REVIEWED)
    I_e = load_snapshot(SNAP, 'abcde', REVIEWED)
    a, b = daily.run(I_d)['daily']['cash'], daily.run(I_e)['daily']['cash']
    changed = sorted(d for d in a if b[d]['rev_mn'] != a[d]['rev_mn'])
    assert changed[0] == '2026-07-01' and changed[-1] == '2026-10-21' and len(changed) == 78
    assert all(a[d]['regime'] == 'projected' for d in changed)
    want = {'07': 0.171, '08': 0.17, '09': 0.162, '10': 0.162}   # Oct: latest disclosed month (Sep)
    for d in changed:
        assert b[d]['share'] == pytest.approx(want[d[5:7]], rel=1e-12)
        assert b[d]['rev_mn'] / a[d]['rev_mn'] == pytest.approx(want[d[5:7]] / 0.174, rel=1e-12)
    assert SW.monthly_share(I_e.facts, 'share_cash', 'FY 2027 October') == (0.162, 'FY 2027 September', 561)
