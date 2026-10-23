"""Parity gate: the engine must reproduce the workbook. Run: python -m pytest tests/ -q (from broker_db/)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.engine.inputs import load_snapshot
from src.engine import daily, summary, parity

SNAP = os.environ.get('SB_SNAPSHOT', os.path.join(os.path.dirname(__file__), '..', 'snapshot', 'db_snapshot_2026-10-23.json'))


def _run():
    I = load_snapshot(SNAP)
    res = daily.run(I)
    cells, _ = summary.build(res['daily'])
    return parity.compare(res, cells, I.snap['parity_expected'])


def test_every_expected_value_matches_or_is_documented_out_of_scope():
    rows = _run()
    unexplained = [r for r in rows if not r['ok'] and not r['out_of_scope']]
    assert not unexplained, unexplained[:10]


def test_all_summary_cells_match():
    rows = [r for r in _run() if r['kind'] == 'summary']
    assert len(rows) == 264 and all(r['ok'] for r in rows)


def test_out_of_scope_is_small_and_known():
    rows = _run()
    assert sum(1 for r in rows if r['out_of_scope']) == 23
