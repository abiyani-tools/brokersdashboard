"""Live run — writes out/live/<as_of>/; publishes to the DB only with --publish.

    python3 run_live.py [snapshot] [reviewed_facts]   # from snapshot files (default: snapshot/*_2026-10-23.json)
    python3 run_live.py --db                          # from the DB (needs SUPABASE_SERVICE_KEY in the environment)
    python3 run_live.py --db --publish                # ... and write the run to sb_runs / sb_calibration /
                                                      #     sb_daily_revenue / sb_summary_cells (refused if E5 blocks)

From the DB the run is as of the last day on which every input the engine reads is complete; the series that
limits it is named in the report and in sb_runs.notes.
"""
import json
import os
import sys

from src.live.run import live_run, live_run_snapshot, report_md, write

note = ''
if '--db' in sys.argv:
    from src.live.db import SupabaseReader
    from src.live.snapshot import build_snapshot, complete_through, trim
    snap, reviewed = build_snapshot(SupabaseReader())
    as_of, limiting = complete_through(snap)
    note = f'complete through {as_of} (limited by {limiting})'
    snap = trim(snap, as_of)
    run = live_run_snapshot(snap, reviewed)
    out = write(run, f"out/live/{run['as_of']}")
    with open(os.path.join(out, 'snapshot.json'), 'w') as fh:      # git-ignored; the inputs of this run
        json.dump({'snapshot': snap, 'reviewed': reviewed}, fh, default=str)
else:
    if '--publish' in sys.argv:
        sys.exit('--publish needs --db (a run from snapshot files is not published)')
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    snap = args[0] if args else 'snapshot/db_snapshot_2026-10-23.json'
    reviewed = args[1] if len(args) > 1 else 'snapshot/facts_reviewed_2026-10-23.json'
    run = live_run(snap, reviewed)
    out = write(run, f"out/live/{run['as_of']}")
print(report_md(run))
if note:
    print(note)
print('written', out)
if run['report'].blocking:
    sys.exit(1)
if '--publish' in sys.argv:
    from src.live.db import SupabaseWriter
    from src.live.publish import publish
    run_id, counts = publish(run, SupabaseWriter(), notes_extra=note)
    print(f'published run {run_id}: {counts}')
