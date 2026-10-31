"""Groww IR switches g-h (and g-i): optional, off in the published chain. Run: python -m pytest tests/test_groww_ir_switches.py -q"""
import json
import os
import sys
from collections import defaultdict

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.engine import groww, groww_bridge as B, groww_ir as IR, groww_ir_backtest as BT, groww_switches as GS
from src.engine import parity_groww as PG
from src.engine.inputs import q_of

ROOT = os.path.join(os.path.dirname(__file__), '..')
_cache = {}


def run(sw):
    if sw not in _cache:
        _cache[sw] = B.run_switches(tuple(sw))
    return _cache[sw]


def ir_rows():
    return json.load(open(GS.IR_FIXTURE))['rows']


# ── wiring ──
def test_published_chain_is_unchanged_and_extras_are_separate():
    assert GS.ORDER == 'abcdefg' and GS.EXTRA == 'hi' and GS.ALL == 'abcdefghi'
    from src.live.groww_run import SWITCHES
    assert SWITCHES == 'abcdefg'
    assert GS.cumulative('h') == (frozenset('abcdefg'), frozenset('abcdefgh'))


def test_h_needs_d_and_e():
    with pytest.raises(GS.SwitchError, match='needs g-d, g-e'):
        GS.check('abch')
    GS.check('abcdefgh')


def test_h_without_ir_or_exchange_data_raises():
    snap = json.load(open(PG.GROWW_SNAPSHOT))
    with pytest.raises(GS.SwitchError, match='IR rows and the exchange'):
        groww.GrowwInputs(snap, tuple('abcdefgh'), GS.load_reviewed())
    with pytest.raises(GS.SwitchError, match='IR rows and the exchange'):
        groww.GrowwInputs(snap, tuple('abcdefgh'), GS.load_reviewed(), ir=IR.IR(ir_rows()))


# ── g-h changes only the first unreported quarter's F&O and cash share ──
def test_h_moves_only_q3_fy27_fo_and_cash_share():
    I0, G0, r0 = run('abcdefg')
    I1, G1, r1 = run('abcdefgh')
    moved = B.moved(B.params(G0, r0), B.params(G1, r1))
    assert [(seg, what, q) for (seg, what, q), _, _ in moved] == [
        ('Cash', 'share (ADTO, legacy basis)', 'Q3 FY 2027'), ('F&O', 'share (ADTO, legacy basis)', 'Q3 FY 2027')]
    for seg in ('fo', 'cash', 'comm', 'mtf'):
        for d, row in r0['daily'][seg].items():
            if not (seg in ('fo', 'cash') and q_of(d) == 'Q3 FY 2027'):
                assert r1['daily'][seg][d] == row, (seg, d)                  # every other day is bit-identical
    for seg in ('fo', 'cash'):
        for q, p in r0['calib'][f'{seg}_quarter'].items():
            if q != 'Q3 FY 2027':
                assert r1['calib'][f'{seg}_quarter'][q] == p
            else:
                assert r1['calib'][f'{seg}_quarter'][q]['take_rate'] == p['take_rate']        # take rate unchanged


def test_h_ratio_recomputed_independently_from_the_raw_fixtures():
    """Raw JSON only: no engine helper, no IR class."""
    ir = {(r['metric'], r['period_key']): r for r in ir_rows()}
    ex = json.load(open(GS.EXCHANGE_FIXTURE))['rows']

    def tot(keys, a, b):
        return sum(r[k] for r in ex if a <= r['trade_date'] <= b for k in keys)
    cash_k, fo_k = ('nse_cash', 'bse_cash'), ('nse_io', 'nse_so', 'bse_opt')
    exp = {}
    for seg, metric, keys in (('cash', 'ir_stocks_turnover', cash_k), ('fo', 'ir_equity_derivs_premium', fo_k)):
        s2 = ir[(metric, 'Q2 FY 2027')]['value'] / 10 / tot(keys, '2026-07-01', '2026-09-30')
        s3 = ir[(metric, 'Q3 FY 2027')]['value'] / 10 / tot(keys, '2026-10-01', '2026-10-30')
        exp[seg] = s3 / s2
    assert exp['cash'] == pytest.approx(0.98089, abs=2e-5) and exp['fo'] == pytest.approx(1.00193, abs=2e-5)
    I0, G0, r0 = run('abcdefg')
    I1, G1, r1 = run('abcdefgh')
    for seg, table in (('cash', 'cash_quarter'), ('fo', 'fo_quarter')):
        base = r0['calib'][table]['Q2 FY 2027']['share']
        assert r1['calib'][table]['Q3 FY 2027']['share'] == pytest.approx(base * exp[seg], rel=1e-12)
        assert r0['calib'][table]['Q3 FY 2027']['share'] == base                     # g-e: carried
    # revenue of a Q3 day moves by exactly the ratio (same orders, same take rate)
    d = '2026-10-15'
    assert r1['daily']['fo'][d]['rev_mn'] / r0['daily']['fo'][d]['rev_mn'] == pytest.approx(exp['fo'], rel=1e-12)
    assert r1['daily']['cash'][d]['rev_mn'] / r0['daily']['cash'][d]['rev_mn'] == pytest.approx(exp['cash'], rel=1e-12)


def test_h_exchange_definition_matches_the_database_sums():
    """SELECT sums by quarter from sb_market_daily on 31 Oct 2026 (source exchangesdash_json), Rs Cr."""
    tv = IR.Turnover.from_fixture(GS.EXCHANGE_FIXTURE)
    db = {'Q2 FY 2027': (7694481 + 682133, 2651704 + 466788 + 1464494),
          'Q1 FY 2027': (8156924 + 586731, 3385997 + 475110 + 1777020),
          'Q3 FY 2027': (2280706 + 205917, 1264548 + 145975 + 709629)}
    for q, (cash, deriv) in db.items():
        a, b = IR.quarter_bounds(q)
        b = min(b, '2026-10-30')
        assert tv.total('cash', a, b)[0] == pytest.approx(cash, abs=3) and tv.total('deriv', a, b)[0] == \
            pytest.approx(deriv, abs=3)


def test_h_needs_ir_for_the_quarter_after_the_last_reported_one():
    ir = IR.IR([r for r in ir_rows() if r['period_key'] != 'Q3 FY 2027'])   # IR page without the QTD point
    G = _g('abcdefgh', ir=ir)
    with pytest.raises(GS.SwitchError, match='no ir_equity_derivs_premium for Q3 FY 2027'):
        groww.run(run('abcdefgh')[0], G)


def test_h_refuses_a_qtd_it_cannot_pin_to_a_day():
    rows = [dict(r, covers_through=None, value=r['value'] * 3 if r['metric'] == 'ir_stocks_turnover' and r['is_qtd']
                 else r['value']) for r in ir_rows()]
    G = _g('abcdefgh', ir=IR.IR(rows))
    with pytest.raises(GS.SwitchError, match='cannot pin'):
        groww.run(run('abcdefgh')[0], G)


def test_h_derives_the_day_when_the_archive_did_not_store_it():
    rows = [dict(r, covers_through=None) for r in ir_rows()]
    I, G, res = run('abcdefgh')
    G2 = _g('abcdefgh', ir=IR.IR(rows))
    res2 = groww.run(run('abcdefgh')[0], G2)
    assert res2['calib']['cash_quarter']['Q3 FY 2027']['qtd_ratio']['through_how'] == 'inferred'
    assert res2['daily'] == res['daily']                                     # the same day, so the same numbers


def _g(sw, ir=None):
    snap = json.load(open(PG.GROWW_SNAPSHOT))
    return groww.GrowwInputs(snap, tuple(sw), GS.load_reviewed(), ir, IR.Turnover.from_fixture(GS.EXCHANGE_FIXTURE))


def test_h_bridge_shows_the_arithmetic_and_consolidated_numbers():
    b = B.bridge('h')
    txt = B.markdown(b)
    assert b['before'] == list('abcdefg') and b['after'] == list('abcdefgh')
    assert 'g-h arithmetic' in txt and 'Q3 FY 2027 (to 2026-10-30)' in txt and 'FY 2027 October' in txt
    cons = {r['period']: r for r in b['rows'] if r['panel'] == 'Consolidated'}
    assert cons['Q2 FY 2027']['after'] == cons['Q2 FY 2027']['before'] and cons['FY 2026']['after'] == cons['FY 2026']['before']
    assert cons['FY 2027 October']['after'] < cons['FY 2027 October']['before']          # cash share down 1.9%


# ── backtest ──
def test_h_backtest_numbers_and_the_plain_conclusion():
    rows = BT.backtest_h()
    assert len(rows) == 8 and {r['quarter'] for r in rows} == set(BT.H_QUARTERS)
    s = BT.summary_h(rows)
    # carry vs g-h: cash better with g-h, F&O worse; overall not a clear win
    assert s['Cash']['share']['h']['mae'] < s['Cash']['share']['carry']['mae']
    assert s['F&O']['share']['h']['mae'] > s['F&O']['share']['carry']['mae']
    assert abs(s['All']['rev']['h']['mae'] - s['All']['rev']['carry']['mae']) < 0.01
    # the carry share of a quarter is the previous quarter's disclosed share
    byq = {(r['segment'], r['quarter']): r for r in rows}
    assert byq[('Cash', 'Q4 FY 2026')]['carry_share'] == byq[('Cash', 'Q3 FY 2026')]['disclosed_share']


# ── live CLI ──
def test_cli_extras_are_off_by_default_and_never_published(monkeypatch):
    from src.live import cli
    assert cli.parse([])['groww_extra'] == ''
    assert cli.parse(['--groww-extra', 'ih'])['groww_extra'] == 'hi'
    assert cli.parse(['--groww-extra=h'])['groww_extra'] == 'h'
    monkeypatch.setenv('GROWW_EXTRA', 'h')
    assert cli.parse([])['groww_extra'] == 'h' and cli.parse(['--groww-extra', 'i'])['groww_extra'] == 'i'
    with pytest.raises(SystemExit):
        cli.parse(['--groww-extra', 'x'])
    with pytest.raises(SystemExit, match='not signed off'):
        cli.main(['--db', '--publish', '--broker', 'GROWW', '--groww-extra', 'h'])


def test_cli_dry_run_with_h_changes_only_groww_q3(tmp_path, monkeypatch, capsys):
    from src.live import cli
    monkeypatch.chdir(ROOT)
    for k in ('GROWW_EXTRA', 'GITHUB_ACTIONS'):
        monkeypatch.delenv(k, raising=False)
    assert cli.main(['--broker', 'GROWW']) == 0
    base = json.load(open(os.path.join(ROOT, 'out', 'live', '2026-10-21', 'groww', 'summary_rows.json')))
    assert cli.main(['--broker', 'GROWW', '--groww-extra', 'h']) == 0
    out = capsys.readouterr().out
    assert 'Groww optional IR switches ON: g-h' in out
    new = json.load(open(os.path.join(ROOT, 'out', 'live', '2026-10-21', 'groww', 'summary_rows.json')))
    assert new != base
    assert cli.main(['--broker', 'GROWW']) == 0                               # leave the default output in place
    assert json.load(open(os.path.join(ROOT, 'out', 'live', '2026-10-21', 'groww', 'summary_rows.json'))) == base
