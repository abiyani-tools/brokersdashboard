"""Groww parity gate: the engine must reproduce the workbook's feeder columns and SUMMARY - Groww.

Fixtures come from seed/build_groww.py (cached workbook values). Run: python -m pytest tests/test_groww_parity.py -q
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.engine import daily, groww, parity_groww as PG, summary
from src.engine.inputs import fy_month_of, load_snapshot, q_of

TOL = 1e-9


@pytest.fixture(scope='module')
def fixtures():
    return json.load(open(PG.GROWW_FIXTURES))


@pytest.fixture(scope='module')
def run():
    I, G, res, cells = PG.run_all()
    return I, G, res, cells


# ── daily rows of the four feeder columns ──
@pytest.mark.parametrize('col, days', [('backtesting F&O!AD', 573), ('backtesting cash!V', 573),
                                       ('Commodities!K', 272), ('MTF data (2)!L', 507)])
def test_feeder_column_matches_workbook(run, fixtures, col, days, capsys):
    _, _, res, _ = run
    r = PG.compare_daily(res, fixtures)[col]
    assert r['days'] == days
    assert not r['mismatches'], r['mismatches'][:5]
    assert r['max_abs_diff'] <= TOL
    with capsys.disabled():
        print(f'\n  {col}: {days} days, max abs diff {r["max_abs_diff"]:.3g}')


def test_quirks_zero_fill_na_and_blank(run):
    _, _, res, _ = run
    fo, cash, comm = res['daily']['fo'], res['daily']['cash'], res['daily']['comm']
    for seg in (fo, cash):
        assert seg['2024-07-01']['rev_mn'] is None and seg['2024-09-30']['rev_mn'] is None      # Q2 FY25: #N/A
        assert seg['2024-10-01']['rev_mn'] == 0.0 and seg['2025-06-30']['rev_mn'] == 0.0        # Q3 FY25-Q1 FY26: 0
        assert seg['2025-07-01']['rev_mn'] > 0
    assert min(comm) == '2025-10-01'                                                           # blank before launch
    assert '2025-09-30' not in comm


def test_bse_freeze_is_in_the_inputs_not_fixed(run):
    I, _, res, _ = run
    st = I.status('bse_fo', 'contracts')
    assert all(st[d] == 'imputed' for d in ('2026-09-29', '2026-10-21'))
    assert res['daily']['fo']['2026-10-21']['rev_mn'] > 0          # computed from the frozen BSE value, as in Excel


# ── quarterly parameters ──
def test_quarterly_parameters_match_workbook(run, fixtures):
    _, _, res, _ = run
    bad = [r for r in PG.compare_calibration(res, fixtures) if not r[3]]
    assert not bad, bad


@pytest.mark.parametrize('seg, q, field, want', [
    ('fo_quarter', 'Q2 FY 2026', 'take_rate', 29.633), ('fo_quarter', 'Q3 FY 2026', 'take_rate', 28.977),
    ('fo_quarter', 'Q4 FY 2026', 'take_rate', 26.378), ('fo_quarter', 'Q1 FY 2027', 'take_rate', 26.378),
    ('fo_quarter', 'Q1 FY 2027', 'share', 0.2226), ('fo_quarter', 'Q3 FY 2027', 'share', 0.2226),
    ('cash_quarter', 'Q2 FY 2026', 'take_rate', 20.200), ('cash_quarter', 'Q1 FY 2027', 'take_rate', 20.774),
    ('cash_quarter', 'Q2 FY 2027', 'take_rate', 20.398), ('cash_quarter', 'Q3 FY 2027', 'share', 0.302)])
def test_spec_section3_values(run, seg, q, field, want):
    _, _, res, _ = run
    assert res['calib'][seg][q][field] == pytest.approx(want, abs=6e-4)


def test_commodity_calibration_is_one_off(run):
    _, _, res, _ = run
    c = res['calib']['comm']
    assert c['quarter'] == 'Q3 FY 2026' and c['take_rate'] == pytest.approx(24.204, abs=6e-4)
    assert c['share'] == pytest.approx(c['share0'] * 1.05)                          # typed 5% growth, kept
    rates = {r['rev_mn'] / r['orders_mn'] for r in res['daily']['comm'].values()}
    assert len(rates) == 1 or max(rates) - min(rates) < 1e-9                        # one fixed take rate, every day


# ── Angel's calibration is reused, not re-implemented ──
def test_groww_reads_angels_calibration(run):
    I, _, res, _ = run
    angel = daily.run(I)
    d = '2026-05-14'
    assert res['daily']['fo'][d]['cpo'] == angel['calib']['fo_month'][fy_month_of(d)]['cpo']
    assert res['daily']['cash'][d]['tpo'] == angel['calib']['cash_quarter'][q_of(d)]['tpo']
    assert res['daily']['comm'][d]['cpo'] == angel['calib']['comm_month'][fy_month_of(d)]['cpo']
    # a change in Angel's inputs moves Groww (the coupling the spec calls out)
    I2 = load_snapshot(PG.ANGEL_SNAPSHOT)
    I2.cell[('Working sheet - Angel One', 'K', 7)] *= 1.1                  # Angel Q4 FY26 cash orders
    G2 = groww.GrowwInputs(json.load(open(PG.GROWW_SNAPSHOT)))
    res2 = groww.run(I2, G2)
    assert res2['daily']['cash']['2026-01-20']['tpo'] != res['daily']['cash']['2026-01-20']['tpo']


def test_groww_run_leaves_angel_untouched():
    I = load_snapshot(PG.ANGEL_SNAPSHOT)
    before = daily.run(I)['daily']['fo']['2026-05-14']['rev_mn']
    groww.run(I, groww.GrowwInputs(json.load(open(PG.GROWW_SNAPSHOT))))
    assert daily.run(I)['daily']['fo']['2026-05-14']['rev_mn'] == before


# ── SUMMARY - Groww ──
def test_all_262_summary_cells_match(run, fixtures):
    _, _, _, cells = run
    rows = [r for r in PG.compare_summary(cells, fixtures) if 'value' in r and r['expected'] != '-']
    assert len(rows) == 262
    bad = [r for r in rows if not r['ok']]
    assert not bad, bad[:5]


def test_dash_cells_are_division_by_zero(run, fixtures):
    _, _, _, cells = run
    assert [d['cell'] for d in fixtures['summary_dash']] == ['O39', 'E65']
    assert all(cells[d['cell']][2] is None for d in fixtures['summary_dash'])


def test_summary_headline_values(run):
    _, _, _, cells = run
    # spec section 1 table. Its F&O / Cash quarter and month figures (8.364, 10.540, 4.565 ...) are not in the panels
    # at those cells (the F&O and Cash panels show stale labels): only the cells that exist are checked here.
    want = {'M35': 11.4745, 'C61': 4.1344, 'M61': 1.1677, 'M8': 16.7766, 'C35': 2.2867, 'C7': 19.0633,
            'M36': 8.4453, 'C62': 2.6939, 'M62': 0.9157, 'M9': 12.0549, 'C36': 0.9852, 'C8': 13.0401,
            'M12': 14.5088, 'C39': 2.8977, 'C11': 17.4065, 'M13': 15.9675, 'C40': 2.4824, 'C12': 18.4499,
            'M65': 1.5795, 'M66': 1.2798, 'M71': 1.4783, 'M18': 16.2716, 'C45': 2.5988, 'C17': 18.8703}
    for cell, v in want.items():
        assert cells[cell][2] == pytest.approx(v, abs=6e-5), cell


def test_stale_labels_and_partial_period_are_kept():
    L = summary.GROWW_LABELS
    assert L['F&O']['q'] == ['Q1 FY 2027', 'Q4 FY 2026', 'Q4 FY 2025'] and L['F&O']['m'][0] == 'FY 2026 February'
    assert L['Cash']['q'][2] == 'Q1 FY 2026'
    assert L['default']['q'][0] == 'Q3 FY 2027' and L['default']['m'][0] == 'FY 2027 October'


def test_angel_summary_unchanged_by_the_generalisation():
    I = load_snapshot(PG.ANGEL_SNAPSHOT)
    res = daily.run(I)
    a, _ = summary.build(res['daily'])
    b, _ = summary.build(res['daily'], 'ANGELONE')
    assert a == b and 'N8' in a and 'M8' not in a                   # Angel keeps its M:U panels


# ── inputs: shape, units, sources ──
def test_groww_snapshot_shape():
    snap = json.load(open(PG.GROWW_SNAPSHOT))
    assert len(snap['facts']) == 41
    assert all(f['broker_id'] == 'GROWW' and f['source_ref'].startswith('excel:') for f in snap['facts'])
    assert all(a['broker_id'] == 'GROWW' for a in snap['assumptions']) and all(p['broker_id'] == 'GROWW' for p in snap['pins'])
    byref = {f['source_ref']: f for f in snap['facts']}
    assert byref['excel:Working sheet - Groww!H7']['value'] == 0.57                    # fractions, not 57
    assert byref['excel:MTF data!J58']['value'] == 0.0288
    a = {x['key']: x for x in snap['assumptions']}
    assert a['mtf_yield']['value'] == 0.1495 and a['mtf_day_basis']['value'] == 246
    assert a['share_growth_fo']['value'] == 0.05 and a['share_growth_comm']['value'] == 0.05
    assert (a['first_live_date_fo']['value_text'], a['first_live_date_comm']['value_text']) == ('2025-07-01', '2025-10-01')
    unread = [f['source_ref'] for f in snap['facts'] if not f['read_by_model']]
    assert len(unread) == 8                                                            # present in the sheet, not read


def test_unread_facts_do_not_move_the_result(run):
    """L7 (Q1 FY27 F&O mix 52%), L55 (share 22%), L9, J9 are in the sheet but not read: parity keeps ignoring them."""
    I, G, res, _ = run
    snap = json.load(open(PG.GROWW_SNAPSHOT))
    for f in snap['facts']:
        if not f['read_by_model']:
            f['value'] = f['value'] * 3
    res2 = groww.run(I, groww.GrowwInputs(snap))
    assert res2['daily']['fo'] == res['daily']['fo'] and res2['daily']['comm'] == res['daily']['comm']
    assert res2['daily']['cash'] == res['daily']['cash']


def test_missing_parameters_raise_in_parity_helpers(run):
    I, G, res, _ = run
    snap = json.load(open(PG.GROWW_SNAPSHOT))
    snap['facts'] = [f for f in snap['facts'] if not (f['metric'] == 'share_fo_adto_q' and f['period_key'] == 'Q3 FY 2026')]
    with pytest.raises(KeyError):
        groww.run(I, groww.GrowwInputs(snap))


def test_shared_angel_inputs_equal_the_workbook_inventory():
    """Series Groww borrows from Angel (workbook_inputs.json scope angel_shared) are in the Angel snapshot with the
    same values. Skipped when the inventory file is not present."""
    path = os.path.join(os.path.dirname(__file__), '..', 'out', 'groww', 'workbook_inputs.json')
    if not os.path.exists(path):
        pytest.skip('out/groww/workbook_inputs.json not present')
    I = load_snapshot(PG.ANGEL_SNAPSHOT)
    rows = [r for r in json.load(open(path)) if r['scope'] == 'angel_shared' and isinstance(r['value'], (int, float))]
    checked = mism = 0
    for r in rows:
        key = (r['sheet'], ''.join(c for c in r['cell'] if c.isalpha()), int(''.join(c for c in r['cell'] if c.isdigit())))
        if key in I.cell:
            checked += 1
            mism += abs(I.cell[key] - r['value']) > 1e-9
        elif r['sheet'].strip() == 'F&O market':                      # the Angel snapshot keys these by metric and month
            v = I.fact[(r['metric'], 'F&O market')].get(r['period_key'])
            checked += 1
            mism += v is None or abs(v - r['value']) > 1e-9
    assert checked > 0 and mism == 0, (checked, mism)
