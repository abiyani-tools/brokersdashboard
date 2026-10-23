"""Live dry run — writes out/live/<as_of>/ and never writes to the database.

    python3 run_live.py [snapshot] [reviewed_facts]   # from snapshot files (default: snapshot/*_2026-10-23.json)
    python3 run_live.py --db                          # from the DB (needs SUPABASE_SERVICE_KEY in the environment)
"""
import json
import os
import sys

from src.live.run import live_run, live_run_snapshot, report_md, write

if '--db' in sys.argv:
    from src.live.db import SupabaseReader
    from src.live.snapshot import build_snapshot
    snap, reviewed = build_snapshot(SupabaseReader())
    run = live_run_snapshot(snap, reviewed)
    out = write(run, f"out/live/{run['as_of']}")
    with open(os.path.join(out, 'snapshot.json'), 'w') as fh:      # git-ignored; the inputs of this run
        json.dump({'snapshot': snap, 'reviewed': reviewed}, fh, default=str)
else:
    snap = sys.argv[1] if len(sys.argv) > 1 else 'snapshot/db_snapshot_2026-10-23.json'
    reviewed = sys.argv[2] if len(sys.argv) > 2 else 'snapshot/facts_reviewed_2026-10-23.json'
    run = live_run(snap, reviewed)
    out = write(run, f"out/live/{run['as_of']}")
print(report_md(run))
print('written', out)
sys.exit(1 if run['report'].blocking else 0)
