"""MOSL switch m-g in the live run: the refusal unless every FY24 fact it reads is 'reviewed', the default switches, and
the run itself on the m-g fixtures (market data from 1 Jun 2023; the FY24 candidates stand in for reviewed facts)."""
import json

import pytest

from src.engine import mosl_switches as MS
from src.live import mosl_run
from src.live.mosl_run import MoslRefused, live_run_mosl, refusal_reasons
from tests.live.test_mosl_live import MSNAP, lake_rows


@pytest.fixture(scope='module')
def shared():
    return json.load(open(MS.SHARED_FIXTURE_G))


@pytest.fixture(scope='module')
def msnap():
    return json.load(open(MSNAP))


@pytest.fixture(scope='module')
def facts290():
    return MS.load_reviewed()


@pytest.fixture(scope='module')
def facts24():
    return MS.load_reviewed(MS.FY24_REVIEWED)


def test_default_switches_stay_abcdef():
    assert mosl_run.SWITCHES == 'abcdef'


def test_refused_unless_every_fy24_fact_is_reviewed(msnap, facts290, facts24):
    assert refusal_reasons('abcdefg', msnap, facts290 + facts24) == []
    absent = refusal_reasons('abcdefg', msnap, facts290)
    assert len(absent) == 1 and 'switch m-g: 30 of the 30 FY24 facts it reads are not reviewed (30 absent' in absent[0]
    staged = refusal_reasons('abcdefg', msnap, facts290 + [dict(f, status='staged') for f in facts24])
    assert len(staged) == 1 and '(0 absent, 30 not reviewed)' in staged[0] and 'staged' in staged[0]
    one = [dict(f, status='staged') if (f['metric'], f['period_key']) == ('net_brokerage_comm', 'Q4 FY 2024') else f
           for f in facts24]
    r = refusal_reasons('abcdefg', msnap, facts290 + one)
    assert len(r) == 1 and '1 of the 30' in r[0] and 'net_brokerage_comm Q4 FY 2024' in r[0]
    # facts the switch does not read (Q1 FY24, other metrics) do not matter
    unread = [dict(f, status='staged') if f['period_key'] == 'Q1 FY 2024' or f['metric'] == 'wm_nii' else f for f in facts24]
    assert refusal_reasons('abcdefg', msnap, facts290 + unread) == []
    # a rejected fact is not a fact
    rej = [dict(f, status='rejected') if (f['metric'], f['period_key']) == ('share_fo_premium', 'Q2 FY 2024') else f
           for f in facts24]
    assert 'share_fo_premium Q2 FY 2024 (absent)' in refusal_reasons('abcdefg', msnap, facts290 + rej)[0]
    # an FY24 fact that is not reviewed does not stop the published chain
    assert refusal_reasons('abcdef', msnap, facts290 + [dict(f, status='staged') for f in facts24]) == []


def test_the_run_is_refused_with_fy24_facts_staged_or_absent(shared, msnap, facts290, facts24):
    lr = lake_rows(MS.LAKE_FIXTURE_G)
    with pytest.raises(MoslRefused, match='switch m-g'):
        live_run_mosl(shared, msnap, facts290, lr, 'abcdefg', as_of='2026-10-21')
    with pytest.raises(MoslRefused, match='not reviewed'):
        live_run_mosl(shared, msnap, facts290 + [dict(f, status='staged') for f in facts24], lr, 'abcdefg', as_of='2026-10-21')


def test_the_run_with_g_on_the_m_g_fixtures(shared, msnap, facts290, facts24):
    lr = lake_rows(MS.LAKE_FIXTURE_G)
    run = live_run_mosl(shared, msnap, facts290 + facts24, lr, 'abcdefg', as_of='2026-10-21')
    base = live_run_mosl(shared, msnap, facts290 + facts24, lr, 'abcdef', as_of='2026-10-21')
    assert run['switches'] == 'abcdefg' and not run['report'].blocking, run['report'].summary()
    assert run['coverage'] == 'pass' and 'm-g' in run['note'] and 'm-g' not in base['note']
    assert len(run['fact_ids']) > len(base['fact_ids'])                         # the FY24 facts are read
    get = lambda r: {(x['panel'], x['row_label']): (x['value'], x['note']) for x in r['rows'] if x['period_type'] in ('FY', 'Q', 'M')}
    g, a = get(run), get(base)
    assert a[('Broking', 'Q2 FY 2024')][0] is None and g[('Broking', 'Q2 FY 2024')][0] == pytest.approx(4.272250, abs=5e-7)
    assert g[('Broking', 'Q4 FY 2024')][0] == pytest.approx(5.545791, abs=5e-7)
    assert g[('Consolidated', 'Q2 FY 2024')][0] is None and g[('Consolidated', 'Q2 FY 2024')][1].startswith('insufficient data')
    assert g[('Broking', 'FY 2024')][0] is None and g[('Consolidated', 'FY 2024')][0] is None
    for k, (v, _) in a.items():                                                  # no value that a-f gives changes
        if v is not None:
            assert g[k][0] == v, k
    # the daily rows: none before Q2 FY24
    assert min(run['daily']['fo']) == '2023-07-03' and min(base['daily']['fo']) == '2024-04-01'
