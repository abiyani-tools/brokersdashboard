"""Live run — writes out/live/<as_of>/; publishes to the DB only with --publish.

    python3 run_live.py [snapshot] [reviewed_facts]   # from snapshot files (default: snapshot/*_2026-10-23.json)
    python3 run_live.py --db                          # from the DB (needs SUPABASE_SERVICE_KEY in the environment)
    python3 run_live.py --db --publish                # ... and write the run to sb_runs / sb_calibration /
                                                      #     sb_daily_revenue / sb_summary_cells (refused if E5 blocks)

    --broker ANGELONE (default) | GROWW | all
        Groww borrows Angel One's calibration, so every broker choice runs the Angel One live run first and builds
        Groww from it (same snapshot, same as-of date). Groww's report goes to out/live/<as_of>/groww/.
        --broker all publishes Angel One, then Groww, each as its own sb_runs row. A Groww run is refused (a warning
        under `all`, Angel One still publishes) unless every fact it reads is 'reviewed' in the database.
    --groww-snapshot PATH --groww-facts PATH          # Groww's inputs for a run from files
                                                      # (default: snapshot/groww_snapshot_2026-10-23.json,
                                                      #  snapshot/groww_facts_reviewed_2026-10-31.json)

From the DB the run is as of the last day on which every input the engine reads is complete; the series that
limits it is named in the report and in sb_runs.notes.
"""
import sys

from src.live.cli import main

if __name__ == '__main__':
    sys.exit(main())
