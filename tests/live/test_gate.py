"""The night-run gate (src/live/gate.py): go on only when a later day than the published one is complete."""
import json
import os

from src.live.gate import decide, latest_published, main

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SNAP = os.path.join(ROOT, 'snapshot', 'db_snapshot_2026-10-23.json')   # complete through 2026-10-21


def run(as_of, broker='ANGELONE', mode='live', status='success'):
    return dict(broker_id=broker, mode=mode, status=status, as_of_date=as_of)


def test_latest_published_counts_only_successful_live_runs_of_the_broker():
    runs = [run('2026-10-16'), run('2026-10-20', status='failed'), run('2026-10-21', mode='parity'),
            run('2026-10-22', broker='GROWW'), run('2026-10-17T00:00:00')]
    assert latest_published(runs) == '2026-10-17'
    assert latest_published([]) is None


def test_go_when_a_new_day_is_complete():
    go, msg = decide(json.load(open(SNAP)), [run('2026-10-20')])
    assert go and 'complete through 2026-10-21' in msg and 'published 2026-10-20' in msg


def test_stop_when_the_complete_day_is_already_published():
    go, msg = decide(json.load(open(SNAP)), [run('2026-10-21')])
    assert not go and 'nothing new' in msg


def test_go_when_nothing_is_published_yet():
    assert decide(json.load(open(SNAP)), [])[0]


def test_stop_when_mcx_contracts_lag():
    # the case of 10 Nov 2026: NSE and BSE have the new day, MCX contracts do not
    snap = json.load(open(SNAP))
    snap['market_daily'] = [r for r in snap['market_daily']
                            if not (r['dataset'] == 'mcx' and r['trade_date'] > '2026-10-20')]
    snap['market_daily_lake'] = [r for r in snap['market_daily_lake']
                                 if not (r['dataset'] == 'mcx' and r['trade_date'] > '2026-10-20')]
    go, msg = decide(snap, [run('2026-10-20')])
    assert not go and 'mcx:contracts' in msg


class FakeReader:
    def __init__(self, snap, runs):
        self.snap, self.runs = snap, runs

    def table(self, name, **eq):
        if name == 'sb_runs':
            return [r for r in self.runs if all(r.get(k) == v for k, v in eq.items())]
        return []


def test_main_writes_the_decision_for_the_workflow(tmp_path, monkeypatch):
    out = tmp_path / 'out.txt'
    monkeypatch.setenv('GITHUB_OUTPUT', str(out))
    monkeypatch.delenv('GITHUB_STEP_SUMMARY', raising=False)
    snap = json.load(open(SNAP))
    monkeypatch.setattr('src.live.snapshot.build_snapshot', lambda reader: (snap, []))
    assert main(lambda: FakeReader(snap, [run('2026-10-21')])) == 0
    assert out.read_text() == 'go=false\n'
