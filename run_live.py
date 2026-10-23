"""Live dry run: python3 run_live.py [snapshot] [reviewed_facts] — writes out/live/<as_of>/ (no DB writes)."""
import sys

from src.live.run import live_run, report_md, write

snap = sys.argv[1] if len(sys.argv) > 1 else 'snapshot/db_snapshot_2026-10-23.json'
reviewed = sys.argv[2] if len(sys.argv) > 2 else 'snapshot/facts_reviewed_2026-10-23.json'
run = live_run(snap, reviewed)
print(report_md(run))
print('written', write(run, f"out/live/{run['as_of']}"))
sys.exit(1 if run['report'].blocking else 0)
