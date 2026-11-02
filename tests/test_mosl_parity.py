"""MOSL parity gate: the engine must reproduce the workbook's four feeder columns and SUMMARY - Motilal Oswal.

Fixtures come from seed/build_mosl.py (cached workbook values). Run: python -m pytest tests/test_mosl_parity.py -q
"""
import copy
import json
import os
import sys
from collections import Counter

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.engine import mosl, parity_mosl as PM, summary
from src.engine.inputs import q_of

TOL = 1e-9


@pytest.fixture(scope='module')
def fixtures():
    return json.load(open(PM.MOSL_FIXTURES))


@pytest.fixture(scope='module')
def run():
    return PM.run_all()


# ── daily rows of the four feeder columns ──
@pytest.mark.parametrize('col, days', [('backtesting F&O!AG', 757), ('backtesting cash!AB', 509),
                                       ('Commodities!O', 653), ('MTF data (2)!X', 495)])
def test_feeder_column_matches_workbook(run, fixtures, col, days, capsys):
    _, res, _ = run
    r = PM.compare_daily(res, fixtures)[col]
    assert r['days'] == days
    assert not r['mismatches'], r['mismatches'][:5]
    assert r['max_abs_diff'] <= TOL
    with capsys.disabled():
        print(f'\n  {col}: {days} days, max abs diff {r["max_abs_diff"]:.3g}')


@pytest.mark.parametrize('col, days', [('backtesting F&O!AF', 633), ('backtesting cash!AA', 509),
                                       ('Commodities!L', 646), ('MTF data (2)!W', 495)])
def test_gross_column_matches_workbook(run, fixtures, col, days, capsys):
    _, res, _ = run
    r = PM.compare_gross(res, fixtures)[col]
    assert r['days'] == days
    assert not r['mismatches'], r['mismatches'][:5]
    assert r['max_abs_diff'] <= TOL
    with capsys.disabled():
        print(f'\n  {col}: {days} numeric days, max relative diff {r["max_abs_diff"]:.3g}')


def test_error_and_blank_rows_follow_the_workbook(run):
    _, res, _ = run
    fo, cash, comm, mtf = (res['daily'][s] for s in ('fo', 'cash', 'comm', 'mtf'))
    assert fo['2023-10-03']['err'] == '#N/A' and fo['2024-03-28']['err'] == '#N/A'              # Q3, Q4 FY24: no table row
    assert fo['2024-05-31']['err'] == '#VALUE!'                                                # P169 is text
    assert fo['2024-04-01']['rev_mn'] == 0.0 and fo['2024-09-30']['rev_mn'] == 0.0             # Q1, Q2 FY25: blank rate
    assert fo['2024-10-01']['rev_mn'] > 0 and fo['2026-10-21']['rev_mn'] > 0                   # Q3 FY27 is F&O only
    assert min(cash) == '2024-10-01'                                                           # AB blank before
    assert cash['2026-10-21']['err'] == '#N/A' and cash['2026-10-21']['gross_cr'] > 15         # AA inflated x5, hidden
    assert comm['2026-10-12']['err'] == '#N/A' and '2026-10-13' not in comm                    # formula not extended
    assert max(mtf) == '2026-09-30'                                                            # no MTF row in October


# ── quarterly parameters ──
def test_quarterly_parameters_match_workbook(run, fixtures):
    _, res, _ = run
    rows = PM.compare_calibration(res, fixtures)
    assert len(rows) == 175
    assert not [r for r in rows if not r[3]]


def test_calibrated_quarters_tie_to_reported_gross(run):
    """sum(AF) = 10 x gross F&O; sum(L) = 10 x gross commodities; sum(AA) = gross cash, except Q1 FY27 (J52 = J51)."""
    M, res, _ = run
    d = res['daily']
    for q in mosl.Q_ALL[2:9]:
        fo = sum(r['gross_mn'] for x, r in d['fo'].items() if q_of(x) == q and r['gross_mn'] is not None)
        assert fo == pytest.approx(10 * M.fact('gross_fo_cr', q), rel=1e-12)
        cash = sum(r['gross_cr'] for x, r in d['cash'].items() if q_of(x) == q)
        if q == 'Q1 FY 2027':
            assert cash == pytest.approx(224.97587, abs=2e-5)         # not the typed 228
        else:
            assert cash == pytest.approx(M.fact('gross_cash_cr', q), rel=1e-12)
    for q in mosl.Q_ALL[:9]:
        cm = sum(r['gross_mn'] for x, r in d['comm'].items() if q_of(x) == q and r['gross_mn'] is not None)
        assert cm == pytest.approx(10 * M.fact('gross_comm_cr', q), rel=1e-12)


def test_estimate_quarter_rules(run):
    """Section 6: carries and trailing averages in Q2 FY27 (the headline quarter is a pure estimate)."""
    M, res, _ = run
    c = res['calib']
    assert c['fo']['rate']['Q2 FY 2027'] == c['fo']['rate']['Q1 FY 2027'] == c['fo']['rate']['Q3 FY 2027']
    assert c['fo']['rate']['Q1 FY 2027'] / 10 == pytest.approx(1.428, abs=1e-3)
    assert c['cash']['table']['Q1 FY 2027']['J'] == c['cash']['table']['Q4 FY 2026']['J']       # J52 = J51
    assert c['cash']['table']['Q2 FY 2027']['H'] == pytest.approx(2.7846, abs=1e-4)
    assert c['comm']['share']['Q2 FY 2027'] == pytest.approx(0.0870, abs=1e-4)
    assert c['comm']['take']['Q2 FY 2027'] == pytest.approx(7.3265, abs=1e-4)
    assert c['ratio']['Q2 FY 2027']['fo'] == pytest.approx(0.5740, abs=1e-4)
    assert c['ratio']['Q3 FY 2027']['fo'] == c['ratio']['Q2 FY 2027']['fo']
    assert c['ratio']['Q3 FY 2027']['cash'] is None and c['ratio']['Q3 FY 2027']['comm'] is None
    assert c['mtf']['share']['Q2 FY 2027'] == c['mtf']['share']['Q1 FY 2027']


# ── the Summary ──
def test_all_264_summary_cells_match(run, fixtures, capsys):
    _, _, cells = run
    rows = PM.compare_summary(cells, fixtures)
    assert len(rows) == 264
    assert Counter(r['panel'] for r in rows) == {p: 44 for p in
                                                 ('Consolidated', 'Broking', 'MTF', 'F&O', 'Commodities', 'Cash')}
    bad = [r for r in rows if not r['ok']]
    assert not bad, bad[:5]
    with capsys.disabled():
        print(f'\n  summary: 264/264 cells, max abs diff {max(abs(r["got"] - r["expected"]) for r in rows):.3g}')


def test_the_layout_is_the_sheets_not_angels(run, fixtures):
    """Broking sits on the Consolidated rows, band 3 is swapped (Commodities left, Cash right and one row lower)."""
    _, _, cells = run
    assert {c for c, v in cells.items() if v[0] == 'Broking' and not v[1].endswith(('cmp1', 'cmp2'))} >= {'M7', 'M8', 'M22'}
    where = {e['cell']: e['panel'] for e in fixtures['summary']}
    assert where['C63'] == 'Commodities' and where['M64'] == 'Cash' and where['C35'] == 'MTF' and where['M35'] == 'F&O'
    assert where['M7'] == 'Broking' and where['C7'] == 'Consolidated'
    assert set(where) == {c for c, v in cells.items() if c in where}
    assert all(cells[c][0] == p for c, p in where.items())


def test_workbook_quirks_in_the_summary(run):
    _, _, cells = run
    v = lambda c: cells[c][2]
    # FY27 YTD: AVERAGEIFS over the #N/A days -> error -> IFERROR 0 for cash and commodities
    assert v('M64') == 0 and v('C63') == 0
    assert v('M7') == pytest.approx(v('M35'), abs=1e-12) == pytest.approx(1.8054, abs=1e-4)          # F&O only
    assert v('C7') == pytest.approx(v('M7') + v('C35'), abs=1e-12)
    assert v('N64') == -1 and v('D63') == -1                                                       # -100%
    # 'YoY' compares Q2 FY27 with the typed Q4 FY26 row; Broking = sum of the segment ADRs
    assert v('M13') == pytest.approx(1.9453 + 1.6998 + 0.7949, abs=1e-3)
    assert v('M11') == pytest.approx(v('M39') + v('M68') + v('C67'), abs=1e-12)
    assert v('O11') == pytest.approx(v('M11') / v('M13') - 1, abs=1e-12)
    assert v('C11') == pytest.approx(v('M11') + v('C39'), abs=1e-12)
    # 'Avg of last 6 months' is the mean of the two quarter ADRs; windows follow each segment's own dates
    assert v('M46') == pytest.approx((v('M40') + v('M39')) / 2, abs=1e-12)
    assert v('M22') == pytest.approx(v('M50') + v('M79') + v('C78'), abs=1e-12)


def test_summary_aggregation_on_error_rows():
    """An error row poisons FY / quarter / month averages (IFERROR 0) and is dropped by the last-N and weekday windows."""
    series = {f'2026-09-{d:02d}': float(d) for d in range(1, 29)}
    seg = summary.Seg(series, 1, errors=['2025-10-01', '2026-10-01'])
    assert seg.m('FY 2027 September') == pytest.approx(14.5) and seg.m('FY 2027 October') == 0.0
    assert seg.fy('FY 2027') == 0.0 and seg.fy('FY 2026') == 0.0       # an error row in each FY
    assert summary.Seg(series, 1, errors=['2025-10-01']).fy('FY 2027') == pytest.approx(14.5)
    seg = summary.Seg(series, 1, errors=['2026-09-30'])
    assert seg.fy('FY 2027') == 0.0 and seg.q('Q2 FY 2027') == 0.0
    assert seg.lastn(5) == pytest.approx(26.0)                       # the error row is not a number: dropped


# ── the inputs ──
def test_snapshot_rows_are_mosl_only_and_cite_cells():
    snap = json.load(open(PM.MOSL_SNAPSHOT))
    assert snap['broker_id'] == 'MOSL'
    rows = snap['facts'] + snap['assumptions'] + snap['pins']
    assert rows and all(r['broker_id'] == 'MOSL' for r in rows)
    sheets = {r['source_ref'].split('!')[0] for r in snap['facts']}
    assert sheets == {'excel:Motilal Oswal assumptions', 'excel:Working Sheet - MOSL'}          # no Angel or Groww cell
    assert all(r['status'] == 'staged' and r['source_ref'].startswith('excel:') for r in snap['facts'])
    nii = [r for r in snap['facts'] if r['metric'] == 'mtf_nii_yield']
    assert len(nii) == 9 and all('SOURCE NEEDED' in r['note'] for r in nii)


def test_exchange_series_added_without_touching_the_shared_snapshot():
    snap, shared = json.load(open(PM.MOSL_SNAPSHOT)), json.load(open(PM.SHARED_SNAPSHOT))
    mine = {(m['dataset'], m['metric']) for m in snap['market_daily']}
    theirs = {(m['dataset'], m['metric']) for m in shared['market_daily']}
    assert mine == {('nse_fo', 'index_opt_contracts'), ('bse_fo', 'opt_contracts_live'), ('nse_fo', 'index_opt_adto'),
                    ('bse_fo', 'opt_adto'), ('nse_cash', 'turnover_cr_xl'), ('bse_cash', 'turnover_cr_xl')}
    assert not mine & theirs
    live = {m['trade_date']: m['value'] for m in snap['market_daily'] if m['metric'] == 'opt_contracts_live'}
    frozen = {m['trade_date']: m['value'] for m in shared['market_daily']
              if (m['dataset'], m['metric']) == ('bse_fo', 'contracts')}
    assert live['2026-10-21'] != frozen['2026-10-21']                # R is live; the shared copy is frozen 29 Sep-21 Oct


def test_mosl_reads_only_mcx_and_mtf_from_the_shared_snapshot(run, fixtures):
    """No Angel or Groww input: the run is unchanged when the shared snapshot keeps only MCX contracts and the book."""
    _, res, _ = run
    shared = json.load(open(PM.SHARED_SNAPSHOT))
    slim = {'market_daily': [m for m in shared['market_daily']
                             if (m['dataset'], m['metric']) in mosl.SHARED.values()]}
    M = mosl.MoslInputs(json.load(open(PM.MOSL_SNAPSHOT)), slim)
    again = mosl.run(M)
    assert again['daily'] == res['daily']


def test_missing_fact_raises():
    snap = json.load(open(PM.MOSL_SNAPSHOT))
    snap = copy.deepcopy(snap)
    snap['facts'] = [f for f in snap['facts'] if not (f['metric'] == 'adto_cash_mosl' and f['period_key'] == 'Q4 FY 2026')]
    M = mosl.MoslInputs(snap, json.load(open(PM.SHARED_SNAPSHOT)))
    with pytest.raises(KeyError):
        mosl.run(M)


# ── Angel One and Groww are untouched ──
def test_default_summary_spec_is_still_angels():
    from src.engine import daily
    from src.engine.inputs import load_snapshot
    I = load_snapshot(PM.SHARED_SNAPSHOT)
    res = daily.run(I)
    a, _ = summary.build(res['daily'])
    b, _ = summary.build(res['daily'], 'ANGELONE')
    assert a == b and len(a) >= 264
    assert summary.SPECS['ANGELONE']['labels'] is summary.PARITY_LABELS
    assert 'layout' not in summary.SPECS['ANGELONE'] and 'layout' not in summary.SPECS['GROWW']
