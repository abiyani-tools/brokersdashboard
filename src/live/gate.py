"""Gate for the daily job's night runs: go on only when a new day is complete.

The night runs (workflow 'daily', 03:45 and 04:45 IST, dispatched on time by pg_cron in the brokers-dashboard
project: migrations/20261110_night_run_trigger.sql) are there to publish trading day D before 06:00 IST on D+1,
once ExchangesDash has D's MCX contract count. They run after the market refresh and go on only if the last
day on which every engine input is complete (snapshot.complete_through, the same date the live run takes) is
later than Angel One's latest successful live run. Otherwise the job stops there: nothing is published, so a
night with nothing new adds no sb_runs rows. Angel One's date is the test because MCX contracts (the input that
arrives last) set Angel One's, Groww's and MOSL's dates alike. The evening run (19:47 IST) is not gated: it
also refreshes share prices and archives Groww's IR page.

    python -m src.live.gate     # prints the decision; writes go=true|false to $GITHUB_OUTPUT when set
"""
from __future__ import annotations

import os
import sys

BROKER = 'ANGELONE'


def latest_published(runs, broker=BROKER):
    """The as-of date of the broker's latest successful live run in sb_runs rows, or None."""
    dates = [str(r['as_of_date'])[:10] for r in runs
             if r.get('broker_id') == broker and r.get('mode') == 'live' and r.get('status') == 'success'
             and r.get('as_of_date')]
    return max(dates, default=None)


def decide(snap, runs, broker=BROKER):
    """(go, message): go when the snapshot is complete through a later day than the latest published run."""
    from .snapshot import complete_through
    as_of, limiting = complete_through(snap)
    published = latest_published(runs, broker)
    if published is None:
        return True, f'complete through {as_of}; no live run of {broker} published yet: go'
    if as_of > published:
        return True, f'complete through {as_of} (limited by {limiting}), published {published}: new day, go'
    return False, (f'complete through {as_of} (limited by {limiting}), already published {published}: '
                   'nothing new, the night run stops here')


def main(reader_factory=None):
    from .db import CachingReader, SupabaseReader
    from .snapshot import build_snapshot
    reader = CachingReader((reader_factory or SupabaseReader)())
    snap, _ = build_snapshot(reader)
    go, msg = decide(snap, reader.table('sb_runs', broker_id=BROKER, mode='live', status='success'))
    print(msg)
    out = os.environ.get('GITHUB_OUTPUT')
    if out:
        with open(out, 'a') as fh:
            fh.write(f"go={'true' if go else 'false'}\n")
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a') as fh:
            fh.write(f"### Night run gate: {'GO' if go else 'nothing new'}\n{msg}\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
