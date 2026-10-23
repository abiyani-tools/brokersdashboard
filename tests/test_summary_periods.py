"""E3: the Summary for every FY / quarter / month (LIVE_SPEC §3, decision D1)."""
import os
import sys
from statistics import mean

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.engine.inputs import load_snapshot, fy_month_of, q_of
from src.engine import daily, summary, publish
from src.engine import summary_periods as SP

SNAP = os.environ.get('SB_SNAPSHOT', os.path.join(os.path.dirname(__file__), '..', 'snapshot', 'db_snapshot_2026-10-23.json'))


@pytest.fixture(scope='module')
def run():
    I = load_snapshot(SNAP)
    return I, daily.run(I)


@pytest.fixture(scope='module')
def live_rows(run):
    I, res = run
    return SP.period_rows(SP.make_segments(res['daily'], guarded=True, calendar=I.cal))


def _row(rows, panel, ptype, pkey, label):
    hits = [r for r in rows if (r['panel'], r['period_type'], r['period_key'], r['row_label']) == (panel, ptype, pkey, label)]
    assert len(hits) == 1, (panel, ptype, pkey, label, len(hits))
    return hits[0]


@pytest.mark.parametrize('m, k, want', [('FY 2027 April', -1, 'FY 2026 March'), ('FY 2027 September', -12, 'FY 2026 September'),
                                        ('FY 2026 March', 1, 'FY 2027 April'), ('FY 2027 January', -6, 'FY 2027 July')])
def test_month_arithmetic(m, k, want):
    assert SP.month_shift(m, k) == want


def test_label_arithmetic():
    assert SP.prev_q('Q1 FY 2027') == 'Q4 FY 2026' and SP.q_last_year('Q2 FY 2027') == 'Q2 FY 2026'
    assert SP.prev_fy('FY 2027') == 'FY 2026'
    assert [SP.period_start(x) for x in ('FY 2027', 'Q4 FY 2027', 'FY 2027 January', 'FY 2027 April')] == \
        ['2026-04-01', '2027-01-01', '2027-01-01', '2026-04-01']
    assert SP.six_months('FY 2027 September') == ['FY 2027 April', 'FY 2027 May', 'FY 2027 June', 'FY 2027 July',
                                                  'FY 2027 August', 'FY 2027 September']


@pytest.mark.parametrize('name', ['default', 'Cash'])
def test_parity_labels_are_the_general_rule_at_two_selections(name):
    lab = SP.labels_for(*SP.PARITY_SELECTIONS[name])
    assert {k: lab[k] for k in summary.PARITY_LABELS[name]} == summary.PARITY_LABELS[name]


def test_general_rule_reproduces_the_264_excel_cells(run):
    """E3 exit test: built from labels_for at the parity selections, the grid equals the workbook's own values."""
    I, res = run
    cells = summary._to_cells(SP.parity_stats(SP.make_segments(res['daily'])), None)
    expected = {e['excel_ref'].split('!')[1]: e['value'] for e in I.snap['parity_expected'] if e['kind'] == 'summary'}
    assert len(expected) == 264
    bad = {k: (cells[k][2], v) for k, v in expected.items()
           if cells[k][2] is None or abs(cells[k][2] - v) > max(1e-9, 1e-9 * abs(v))}
    assert not bad


def test_every_period_has_rows_with_a_unique_key(live_rows, run):
    _, res = run
    keys = [(r['panel'], r['period_type'], r['period_key'], r['table_name'], r['row_label']) for r in live_rows]
    assert len(keys) == len(set(keys))
    months = {fy_month_of(d) for d in res['daily']['fo']}
    assert {r['period_key'] for r in live_rows if r['period_type'] == 'M'} >= months
    assert {r['period_key'] for r in live_rows if r['period_type'] == 'asof'} == {'2026-10-21'}


def test_selected_quarter_comparisons(live_rows, run):
    _, res = run
    fo = {d: r['rev_mn'] / 10 for d, r in res['daily']['fo'].items()}
    q = lambda lab: mean(v for d, v in fo.items() if q_of(d) == lab)
    row = _row(live_rows, 'F&O', 'Q', 'Q2 FY 2027', 'Q2 FY 2027')
    assert row['value'] == pytest.approx(q('Q2 FY 2027'), rel=1e-12)
    assert row['comp_value'] == pytest.approx(q('Q2 FY 2027') / q('Q1 FY 2027') - 1, rel=1e-12)
    yoy = _row(live_rows, 'F&O', 'Q', 'Q2 FY 2027', 'Q2 FY 2027 | YoY')
    assert yoy['comp_value'] == pytest.approx(q('Q2 FY 2027') / q('Q2 FY 2026') - 1, rel=1e-12)


def test_live_six_months_is_the_calendar_six_months(live_rows, run):
    """Decision Q2: 6M = average over the six calendar months ending at the month (not two quarter averages)."""
    _, res = run
    cash = {d: r['rev_mn'] / 10 for d, r in res['daily']['cash'].items()}
    months = SP.six_months('FY 2027 September')
    six = mean(v for d, v in cash.items() if fy_month_of(d) in months)
    row = _row(live_rows, 'Cash', 'M', 'FY 2027 September', 'Avg of last 6 months')
    assert row['value'] == pytest.approx(six, rel=1e-12)
    two_q = (mean(v for d, v in cash.items() if q_of(d) == 'Q1 FY 2027') + mean(v for d, v in cash.items() if q_of(d) == 'Q2 FY 2027')) / 2
    assert row['value'] != pytest.approx(two_q, rel=1e-9)        # the parity rule gives a different number


def test_broking_and_consolidated_are_sums(live_rows):
    get = lambda p: _row(live_rows, p, 'M', 'FY 2027 September', 'FY 2027 September')['value']
    assert get('Broking') == pytest.approx(get('F&O') + get('Cash') + get('Commodities'), rel=1e-12)
    assert get('Consolidated') == pytest.approx(get('Broking') + get('MTF'), rel=1e-12)


def test_partial_history_is_insufficient_not_a_short_average(live_rows):
    """F&O, cash and MTF series start 1 Oct 2024: FY 2025 is partial, Q3 FY 2025 is complete."""
    fy25 = _row(live_rows, 'F&O', 'FY', 'FY 2025', 'FY 2025')
    assert fy25['value'] is None and 'series starts 2024-10-01' in fy25['note']
    q3 = _row(live_rows, 'F&O', 'Q', 'Q3 FY 2025', 'Q3 FY 2025')
    assert q3['value'] is not None
    assert q3['comp_value'] is None and 'Q2 FY 2025' in q3['note']          # QoQ base is partial
    # one insufficient segment makes the sum insufficient
    assert _row(live_rows, 'Broking', 'FY', 'FY 2025', 'FY 2025')['value'] is None
    # commodities start 1 Apr 2024, so its FY 2025 is complete
    assert _row(live_rows, 'Commodities', 'FY', 'FY 2025', 'FY 2025')['value'] is not None


def test_parity_publish_rows_carry_the_selection(run):
    I, res = run
    _, stats = summary.build(res['daily'])
    rows = publish.summary_rows('run', stats, '2026-10-21')
    assert len(rows) == 210
    sel = {(r['panel'], r['period_type'], r['period_key']) for r in rows}
    assert ('Cash', 'Q', 'Q4 FY 2026') in sel and ('F&O', 'Q', 'Q2 FY 2027') in sel
    assert ('Cash', 'M', 'FY 2026 February') in sel and ('MTF', 'asof', '2026-10-21') in sel
    keys = [(r['panel'], r['period_type'], r['period_key'], r['table_name'], r['row_label']) for r in rows]
    assert len(keys) == len(set(keys))
