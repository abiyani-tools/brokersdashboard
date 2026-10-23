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
        Inputs(snap, 'c', [])


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
