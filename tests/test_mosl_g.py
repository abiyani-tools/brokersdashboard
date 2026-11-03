"""MOSL switch m-g: FY24 quarters (docs/MOSL_LIVE_SPEC.md, "Proposed switch m-g"; approved by AB on 3 Nov 2026, live default).

The 116 FY24 facts are read as reviewed (snapshot/mosl_facts_fy24_candidates_2026-11-03.json: AB's approval of 3 Nov 2026; the
database gets them from out/mosl/fy24_facts.sql). Market data from 1 Jun 2023 comes from the m-g fixtures (snapshot/db_snapshot_2026-11-03.json,
snapshot/mosl_lake_2026-11-03.json, built by seed/build_mosl_g_fixtures.py from ExchangesDash's public JSON).
Run: python -m pytest tests/test_mosl_g.py -q"""
import copy
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.engine import mosl, mosl_bridge as B, mosl_switches as MS, parity_mosl as PM
from src.engine import summary_periods as SP
from src.engine.inputs import q_of, quarter_seq

ROOT = os.path.join(os.path.dirname(__file__), '..')
SH_G, LK_G = MS.SHARED_FIXTURE_G, MS.LAKE_FIXTURE_G
_cache = {}


def run_g(sw, shared=SH_G, lake=LK_G):
    """(M, res) on the m-g fixtures (market data from 1 Jun 2023), cached."""
    if (sw, shared, lake) not in _cache:
        _cache[(sw, shared, lake)] = B.run_switches(tuple(sw), shared, PM.MOSL_SNAPSHOT, lake_path=lake)
    return _cache[(sw, shared, lake)]


def fy24_rows():
    return MS.load_reviewed(MS.FY24_REVIEWED)


def fy24_facts():
    return {(f['metric'], f['period_key']): f for f in fy24_rows()}


# ── fixtures and the switch itself ──
def test_fixture_is_the_116_fy24_facts_marked_reviewed_per_abs_approval():
    rows = fy24_rows()
    fx = json.load(open(MS.FY24_REVIEWED))
    cand = json.load(open(MS.FY24_CANDIDATES))['sb_disclosure_facts']
    assert len(rows) == len(cand) == 116 and {r['status'] for r in rows} == {'reviewed'}
    assert sorted(r['fact_id'] for r in rows) == list(range(20291, 20407))
    assert "AB's approval of 3 Nov 2026" in fx['_meta'] and 'not the database' in fx['_meta']
    assert {r['period_key'] for r in rows} == set(quarter_seq('Q1 FY 2024', 'Q4 FY 2024'))
    assert all(r['broker_id'] == 'MOSL' and r['doc_id'] and r['reviewed_at'].startswith('2026-11-03') for r in rows)
    assert fx == MS.build_fy24_fixture()                                        # reproducible from the candidates
    assert not {(r['metric'], r['period_key']) for r in rows} & {(r['metric'], r['period_key']) for r in MS.load_reviewed()}
    # the combined file the live run reads in file mode: 290 + 116, all reviewed
    allf = json.load(open(MS.REVIEWED_ALL))
    assert allf == MS.build_reviewed_all_fixture() and "AB's approval of 3 Nov 2026" in allf['_about']
    assert [r['fact_id'] for r in allf['facts']] == list(range(20001, 20407)) and {r['status'] for r in allf['facts']} == {'reviewed'}


def test_g_is_an_extra_switch_that_needs_a_and_b_and_is_on_by_default_since_abs_approval():
    assert MS.ORDER == 'abcdef' and MS.EXTRA == 'g' and MS.ALL == 'abcdefg'
    assert MS.cumulative('g') == (frozenset('abcdef'), frozenset('abcdefg'))
    from src.live import mosl_run
    assert mosl_run.SWITCHES == 'abcdefg'                                        # AB approved m-g on 3 Nov 2026
    with pytest.raises(MS.SwitchError, match='needs m-ab'):
        MS.check('g')
    with pytest.raises(MS.SwitchError, match='needs m-ab'):
        MS.check('acdefg')
    assert MS.check('abg') == frozenset('abg')
    assert len(MS.fy24_inputs()) == 30 and MS.FY24_QUARTERS == ['Q2 FY 2024', 'Q3 FY 2024', 'Q4 FY 2024']


def test_g_off_the_data_extension_changes_no_a_f_row():
    """a-f on the extended snapshot (calendar and MCX from Jun 2023) with the 2 Nov lake equals a-f on the 23 Oct snapshot,
    row for row."""
    old = B.run_switches(tuple('abcdef'))[1]['daily']
    new = run_g('abcdef', SH_G, MS.LAKE_FIXTURE)[1]['daily']
    for seg in old:
        assert new[seg] == old[seg], seg


def test_g_off_the_fy24_facts_being_present_changes_nothing():
    """The database holds the 116 FY24 facts before the code reads them: m-abcdef with them present as reviewed gives the
    same daily rows, calibration and summary rows as without them."""
    def go(extra):
        M = mosl.MoslInputs(json.load(open(PM.MOSL_SNAPSHOT)), json.load(open(SH_G)), tuple('abcdef'),
                            MS.load_reviewed() + extra, mosl.load_lake(LK_G), '2026-10-21')
        res = mosl.run(M)
        return res, B.live_period_rows(M, res), B.adr(M, res)
    without, with_ = go([]), go(fy24_rows())
    assert with_[0] == without[0]                                                # daily rows and calibration
    assert with_[1] == without[1] and with_[2] == without[2]                     # summary rows and the ADR table
    assert min(with_[0]['daily']['fo']) == '2024-04-01'


def test_g_quarters_start_at_q2_fy24_with_actual_regime():
    M, res = run_g('abcdefg')
    Mf, rf = run_g('abcdef')
    assert M.qs[0] == 'Q2 FY 2024' and M.pin('fo_table_first_quarter') == M.pin('cash_table_first_quarter') == 'Q2 FY 2024'
    assert Mf.qs[0] == 'Q1 FY 2025' and M.qs[-1] == Mf.qs[-1]
    for seg in ('fo', 'cash', 'comm'):
        rows = res['daily'][seg]
        assert min(rows) == '2023-07-03'
        assert all(r['regime'] == 'actual' for d, r in rows.items() if d < '2024-04-01')
    assert res['calib']['last_actual'] == rf['calib']['last_actual']             # last_actual unchanged


def test_g_no_revenue_row_before_q2_fy24_and_never_a_zero():
    M, res = run_g('abcdefg')
    june = [d for d in M.cal if d < '2023-07-01']
    assert len(june) == 21 and june[0] == '2023-06-01'                           # the calendar has the June days ...
    for seg, field in (('fo', 'rev_mn'), ('cash', 'rev_cr'), ('comm', 'rev_mn'), ('mtf', 'nii_cr')):
        rows = res['daily'][seg]
        assert not [d for d in rows if d < '2023-07-01'], seg                    # ... and none has a revenue row
        assert all(r.get('err') is None for r in rows.values())
        assert all(isinstance(r[field], float) and r[field] > 0 for r in rows.values()), seg     # no zero-fill
    assert min(res['daily']['mtf']) == '2024-10-01'                              # MTF unchanged: starts Q3 FY25
    assert res['daily']['mtf'] == run_g('abcdef')[1]['daily']['mtf']


def test_g_independent_recompute_from_the_raw_series_and_the_facts():
    """Each FY24 day's net is the quarter's reported net brokerage spread by that day's share of the quarter's key (shares
    and ADTO cancel). Uses the lake / MCX series and the fact rows directly, not the engine's tables."""
    M, res = run_g('abcdefg')
    F = fy24_facts()
    lake = mosl.load_lake(LK_G)
    shared = json.load(open(SH_G))
    mcx = {r['trade_date']: r['value'] for r in shared['market_daily'] if r['dataset'] == 'mcx'}
    for q in MS.FY24_QUARTERS:
        days = [d for d in lake['nse_fo/io_contracts'] if q_of(d) == q]
        fo = {d: lake['nse_fo/io_contracts'][d][0] + lake['bse_fo/contracts'][d][0] for d in days}
        cash = {d: lake['nse_cash/turnover_cr'][d][0] + lake['bse_cash/turnover_cr'][d][0] for d in days}
        com = {d: v for d, v in mcx.items() if q_of(d) == q}
        for seg, key, field, scale in (('fo', fo, 'rev_mn', 10.0), ('cash', cash, 'rev_cr', 1.0), ('comm', com, 'rev_mn', 10.0)):
            gross_cr = F[(f'gross_brokerage_{seg}', q)]['value'] / 10
            ng = F[(f'net_brokerage_{seg}', q)]['value'] / F[(f'gross_brokerage_{seg}', q)]['value']
            tot = sum(key.values())
            rows = res['daily'][seg]
            assert sorted(d for d in rows if q_of(d) == q) == sorted(key), seg
            for d, k in key.items():
                assert rows[d][field] == pytest.approx(ng * gross_cr * k / tot * scale, rel=1e-9), (seg, d)
            assert sum(rows[d][field] for d in key) / scale == pytest.approx(F[(f'net_brokerage_{seg}', q)]['value'] / 10, rel=1e-9)


def test_g_quarter_adr_and_arithmetic():
    M, res = run_g('abcdefg')
    det = B.g_detail(M, res)
    F = fy24_facts()
    for q in MS.FY24_QUARTERS:
        for name in ('F&O', 'Cash', 'Commodities'):
            x = det[(name, q)]
            s = x['seg']
            assert x['adr'] == pytest.approx(x['adr_engine'], rel=1e-12)
            assert x['revenue'] == pytest.approx(F[(f'net_brokerage_{s}', q)]['value'] / 10, rel=1e-9)
            assert x['ng'] == pytest.approx(F[(f'net_brokerage_{s}', q)]['value'] / F[(f'gross_brokerage_{s}', q)]['value'])
            assert x['gross'] == pytest.approx(F[(f'gross_brokerage_{s}', q)]['value'] / 10)
        assert det[('Broking', q)]['adr'] == pytest.approx(sum(det[(n, q)]['adr'] for n in ('F&O', 'Cash', 'Commodities')))
    assert [round(det[('Broking', q)]['adr'], 4) for q in MS.FY24_QUARTERS] == [4.2723, 4.4566, 5.5458]


def test_g_is_refused_when_the_key_series_start_after_the_first_day_of_q2_fy24():
    """The old fixtures start on 2023-09-29: Q2 FY24 would be calibrated on part of its key, so the engine raises."""
    with pytest.raises(MS.SwitchError, match='key series must start by 2023-07-03'):
        B.run_switches(tuple('abcdefg'))                                         # 23 Oct snapshot, 2 Nov lake
    with pytest.raises(MS.SwitchError, match='key series must start by 2023-07-03'):
        B.run_switches(tuple('abcdefg'), SH_G, PM.MOSL_SNAPSHOT, lake_path=MS.LAKE_FIXTURE)


def test_g_changes_no_fy25_plus_value_and_keeps_fy24_periods_insufficient():
    Ma, ra = run_g('abcdef')
    Mb, rb = run_g('abcdefg')
    eff = B.fy24_effect(Ma, ra, Mb, rb)
    assert eff['violations'] == []                                               # no FY25+ value or comparison changed
    for seg in ra['daily']:                                                      # the daily rows from 1 Apr 2024 are identical
        assert {d: r for d, r in rb['daily'][seg].items() if d >= '2024-04-01'} == ra['daily'][seg]
    changed = {(k[0], k[2], k[4], f) for k, f, x, y in eff['fy25_changed']}
    assert eff['fy25_changed'] and all(x is None and y is not None for _, _, x, y in eff['fy25_changed'])
    for panel in ('Broking', 'F&O', 'Cash', 'Commodities'):
        for q in ('Q2 FY 2025', 'Q3 FY 2025', 'Q4 FY 2025'):
            assert (panel, q, f'{q} | YoY', 'comp_value') in changed, (panel, q)
        for m in ('FY 2025 July', 'FY 2025 December', 'FY 2025 March'):
            assert (panel, m, f'{m} | YoY', 'comp_value') in changed, (panel, m)
        assert (panel, 'Q1 FY 2025', 'Q1 FY 2025', 'comp_value') in changed      # QoQ: Q4 FY24 is now a base
    assert not [c for c in changed if c[0] in ('Consolidated', 'MTF')]           # no MTF in FY24: Consolidated stays insufficient
    assert not [c for c in changed if c[1] == 'FY 2025']                         # FY 2025 YoY needs Q1 FY24
    assert not [c for c in changed if c[1] in ('FY 2025 April', 'FY 2025 May', 'FY 2025 June') and c[2].endswith('| YoY')]
    rows = {(r['panel'], r['period_type'], r['period_key'], r['row_label']): r for r in eff['fy24_rows']}
    for panel in SP.PANELS:
        fy = rows[(panel, 'FY', 'FY 2024', 'FY 2024')]
        assert fy['value'] is None and fy['note'].startswith('insufficient data')
        q1 = rows[(panel, 'Q', 'Q2 FY 2024', 'Q1 FY 2024')]
        assert q1['value'] is None and q1['note'].startswith('insufficient data')
        for q in MS.FY24_QUARTERS:
            r = rows[(panel, 'Q', q, q)]
            if panel in ('Consolidated', 'MTF'):
                assert r['value'] is None and r['note'].startswith('insufficient data') and 'MTF' in r['note']
            else:
                assert r['value'] > 0                                            # the value; its QoQ / YoY bases (Q1 FY24, FY23) are not
                assert r['note'] is None or ('Q1 FY 2024' in r['note'] or 'FY 2023' in r['note'])
    live = {(r['panel'], r['period_key'], r['row_label']): r for r in B.live_period_rows(Mb, rb)}
    for panel in ('Broking', 'F&O', 'Cash', 'Commodities'):                      # FY 2025 YoY stays insufficient
        r = live[(panel, 'FY 2025', 'FY 2025')]
        assert r['comp_value'] is None and 'FY 2024' in r['note']


# ── facts: unreviewed or missing FY24 fact ──
def _make(rows24):
    return mosl.MoslInputs(json.load(open(PM.MOSL_SNAPSHOT)), json.load(open(SH_G)), tuple('abcdefg'),
                           MS.load_reviewed() + rows24, mosl.load_lake(LK_G), '2026-10-21')


def test_g_unreviewed_missing_or_wrong_unit_fy24_fact_raises():
    f24 = fy24_rows()
    _make(f24)
    staged = copy.deepcopy(f24)
    for r in staged:
        if (r['metric'], r['period_key']) == ('gross_brokerage_fo', 'Q3 FY 2024'):
            r['status'] = 'staged'
    with pytest.raises(MS.SwitchError, match='gross_brokerage_fo Q3 FY 2024 is staged, not reviewed'):
        _make(staged)
    with pytest.raises(MS.SwitchError, match='no reviewed fact share_cash Q4 FY 2024'):
        _make([r for r in f24 if (r['metric'], r['period_key']) != ('share_cash', 'Q4 FY 2024')])
    unit = copy.deepcopy(f24)
    for r in unit:
        if (r['metric'], r['period_key']) == ('adto_cash', 'Q2 FY 2024'):
            r['unit'] = 'Rs Cr/day'
    with pytest.raises(MS.SwitchError, match='adto_cash Q2 FY 2024'):
        _make(unit)


def test_fy24_facts_sql_is_insert_only_idempotent_and_current():
    sys.path.insert(0, os.path.join(ROOT, 'seed'))
    import build_mosl_fy24_facts_sql as S
    docs, facts = S.rows()
    text = S.sql(docs, facts)
    assert text == open(os.path.join(ROOT, 'out', 'mosl', 'fy24_facts.sql')).read()
    assert len(docs) == 1 and len(facts) == 116 and all(f['broker_id'] == 'MOSL' for f in facts)
    assert docs == S.rows()[0]                                                   # the doc_id is deterministic (uuid5 of the sha256)
    assert "'reviewed'" in text and 'NOT applied' in text
    body = '\n'.join(line for line in text.splitlines() if not line.startswith('--'))
    assert body.count('where not exists') == 2 and 'on conflict' not in body
    for bad in ('update ', 'delete ', 'drop ', 'truncate '):
        assert bad not in body.lower(), bad
    assert {(f['metric'], f['period_key']) for f in facts} == {(f['metric'], f['period_key']) for f in fy24_rows()}


def test_g_bridge_file_is_reproducible():
    text = open(os.path.join(ROOT, 'out', 'bridges', 'mosl_g.md')).read()
    assert B.markdown(B.bridge('g')) == text
    assert '## m-g: FY24 quarters' in text and '| Q2 FY 2024 |' in text
