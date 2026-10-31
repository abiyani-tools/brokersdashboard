"""The live run's command line (run_live.py): Angel One, Groww, or both.

Angel One is always run first: Groww borrows its calibration, so a Groww run is built from the same Angel live run
(same snapshot, same as-of date). With `--broker all` the order is: Angel run -> Groww run (from it) -> publish Angel
-> publish Groww, each as its own sb_runs row. A Groww run that is refused (its facts are not reviewed, or its
workbook inputs are not in the database) never stops Angel One from publishing: under `all` it is a warning
(exit 0); with `--broker GROWW` alone it is a failure (exit 2).
"""
from __future__ import annotations

import json
import os
import sys
import traceback

from .groww_run import GrowwRefused

ANGEL, GROWW = 'ANGELONE', 'GROWW'
BROKERS = {'ANGELONE': ANGEL, 'ANGEL': ANGEL, 'GROWW': GROWW, 'ALL': 'ALL'}
DEFAULT_SNAPSHOT = 'snapshot/db_snapshot_2026-10-23.json'
DEFAULT_REVIEWED = 'snapshot/facts_reviewed_2026-10-23.json'
DEFAULT_GROWW_SNAPSHOT = 'snapshot/groww_snapshot_2026-10-23.json'
DEFAULT_GROWW_FACTS = 'snapshot/groww_facts_reviewed_2026-10-31.json'
REFUSED_EXIT = 2


def parse(argv):
    """-> dict(db, publish, broker, snapshot, reviewed, groww_snapshot, groww_facts). Positional: snapshot, facts."""
    opts = dict(db=False, publish=False, broker=ANGEL, groww_snapshot=DEFAULT_GROWW_SNAPSHOT,
                groww_facts=DEFAULT_GROWW_FACTS)
    args, i = [], 0
    while i < len(argv):
        a = argv[i]
        if a in ('--db', '--publish'):
            opts[a[2:]] = True
        elif a.startswith('--broker') or a in ('--groww-snapshot', '--groww-facts'):
            key, eq, val = a.partition('=')
            if not eq:
                i += 1
                if i >= len(argv):
                    sys.exit(f'{key} needs a value')
                val = argv[i]
            if key == '--broker':
                if val.upper() not in BROKERS:
                    sys.exit(f'--broker {val}: expected ANGELONE, GROWW or all')
                opts['broker'] = BROKERS[val.upper()]
            else:
                opts[key[2:].replace('-', '_')] = val
        elif a.startswith('--'):
            sys.exit(f'unknown option {a}')
        else:
            args.append(a)
        i += 1
    opts['snapshot'] = args[0] if args else DEFAULT_SNAPSHOT
    opts['reviewed'] = args[1] if len(args) > 1 else DEFAULT_REVIEWED
    return opts


def _warn(title, text):
    """A GitHub Actions annotation in the job, plain text elsewhere."""
    if os.environ.get('GITHUB_ACTIONS'):
        print(f'::warning title={title}::{text.replace(chr(10), " ")}')
    print(f'WARNING {title}: {text}')


def main(argv=None, reader_factory=None, writer_factory=None):
    from .run import live_run, live_run_snapshot, report_md, write

    argv = sys.argv[1:] if argv is None else argv
    o = parse(argv)
    broker, publish_on = o['broker'], o['publish']
    if publish_on and not o['db']:
        sys.exit('--publish needs --db (a run from snapshot files is not published)')
    want_angel, want_groww = broker in (ANGEL, 'ALL'), broker in (GROWW, 'ALL')
    pending = 'Not published yet: the run is published after this report if E5 does not block.' if publish_on else None

    # ── Angel One run (Groww's calibration comes from it, so it is always computed) ──
    note, reader = '', None
    if o['db']:
        from .db import CachingReader, SupabaseReader
        from .snapshot import build_snapshot, complete_through, trim
        reader = CachingReader((reader_factory or SupabaseReader)())
        snap, reviewed = build_snapshot(reader)
        as_of, limiting = complete_through(snap)
        note = f'complete through {as_of} (limited by {limiting})'
        snap = trim(snap, as_of)
        angel = live_run_snapshot(snap, reviewed)
        out = f"out/live/{angel['as_of']}"
        if want_angel:
            write(angel, out, pending)
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, 'snapshot.json'), 'w') as fh:      # git-ignored; the inputs of this run
            json.dump({'snapshot': snap, 'reviewed': reviewed}, fh, default=str)
    else:
        angel = live_run(o['snapshot'], o['reviewed'])
        out = f"out/live/{angel['as_of']}"
        if want_angel:
            write(angel, out)
    if want_angel:
        print(report_md(angel, pending))
    else:
        print(f"Angel One live run (calibration source for Groww, not published by this call): as of "
              f"{angel['as_of']}, E5 {'BLOCKING' if angel['report'].blocking else 'pass'}")
    if note:
        print(note)
    if want_angel:
        print('written', out)
    if angel['report'].blocking:
        if not want_angel:
            print(angel['report'].summary())
        if want_groww:
            print('Groww not run: it borrows the Angel One calibration, and the Angel One run is blocked by E5.')
        return 1

    # ── Groww run, from the Angel run ──
    rc, groww, gout, refused = 0, None, os.path.join(out, 'groww'), None
    if want_groww:
        try:
            from .groww_run import groww_inputs, live_run_groww
            if o['db']:
                gsnap, facts = groww_inputs(reader)
            else:
                from ..engine import groww_switches as GS
                gsnap = json.load(open(o['groww_snapshot']))
                facts = GS.load_reviewed(o['groww_facts'])
            groww = live_run_groww(angel, gsnap, facts)
        except GrowwRefused as e:
            refused = e
        except Exception:
            traceback.print_exc()
            print('Groww run failed (an error, not a refusal).')
            rc = 1
        if refused:
            os.makedirs(gout, exist_ok=True)
            with open(os.path.join(gout, 'report.md'), 'w') as fh:
                fh.write('# Live run · GROWW — refused\n\n' + '\n'.join(f'- {r}' for r in refused.reasons) + '\n')
            _warn('Groww not published', '; '.join(refused.reasons))
            if not want_angel:
                rc = REFUSED_EXIT
        if groww is not None:
            write(groww, gout, pending)
            print(report_md(groww, pending))
            print('written', gout)
            if groww['report'].blocking:
                rc = 1

    # ── publish: Angel first, then Groww ──
    if publish_on:
        from .db import SupabaseWriter
        from .publish import publish
        writer = None
        angel_id = None
        if want_angel:
            writer = (writer_factory or SupabaseWriter)()
            angel_id, counts = publish(angel, writer, notes_extra=note)
            print(f'published run {angel_id}: {counts}')
            write(angel, out, f'Published to the database as run {angel_id}: {counts}.')
        if groww is not None and not groww['report'].blocking:
            writer = writer or (writer_factory or SupabaseWriter)()
            src = (f'Angel One calibration from run {angel_id}' if angel_id
                   else 'Angel One calibration from the same snapshot (the Angel run is not published by this call)')
            gid, counts = publish(groww, writer, notes_extra='; '.join(x for x in (note, src) if x))
            print(f'published GROWW run {gid}: {counts}')
            write(groww, gout, f'Published to the database as run {gid}: {counts}.')
    return rc
