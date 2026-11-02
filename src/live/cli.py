"""The live run's command line (run_live.py): Angel One, Groww, MOSL, or all three.

Angel One is run first whenever Angel One or Groww is wanted: Groww borrows its calibration, so a Groww run is built from
the same Angel live run (same snapshot, same as-of date). With `--broker all` the order is: Angel run -> Groww run (from
it) -> MOSL run -> publish Angel -> publish Groww -> publish MOSL, each as its own sb_runs row. A Groww or MOSL run that
is refused (its facts are not reviewed, or its workbook inputs are not in the database) never stops Angel One from
publishing: under `all` it is a warning (exit 0); with `--broker GROWW` / `--broker MOSL` alone it is a failure (exit 2).

MOSL needs no Angel One calibration: it runs on the same snapshot (calendar, MCX contracts, industry MTF book) with its own
inputs and its own as-of date, the last day on which its inputs are complete (NSE index-option contracts, BSE contracts,
NSE / BSE cash turnover, MCX contracts). That date can be earlier than Angel One's and Groww's: a MOSL run whose E5 checks
block (a zero or a non-ok row in one of its series) is not published, warns, and fails the job after the others published.
"""
from __future__ import annotations

import json
import os
import sys
import traceback

from .groww_run import GrowwRefused
from .mosl_run import MoslRefused

ANGEL, GROWW, MOSL = 'ANGELONE', 'GROWW', 'MOSL'
BROKERS = {'ANGELONE': ANGEL, 'ANGEL': ANGEL, 'GROWW': GROWW, 'MOSL': MOSL, 'ALL': 'ALL'}
DEFAULT_SNAPSHOT = 'snapshot/db_snapshot_2026-10-23.json'
DEFAULT_REVIEWED = 'snapshot/facts_reviewed_2026-10-23.json'
DEFAULT_GROWW_SNAPSHOT = 'snapshot/groww_snapshot_2026-10-23.json'
DEFAULT_GROWW_FACTS = 'snapshot/groww_facts_reviewed_2026-10-31.json'
DEFAULT_GROWW_IR = 'snapshot/groww_ir_2026-10-31.json'
DEFAULT_GROWW_EXCHANGE = 'snapshot/groww_exchange_2026-10-31.json'
DEFAULT_MOSL_SNAPSHOT = 'snapshot/mosl_snapshot_2026-10-23.json'
DEFAULT_MOSL_FACTS = 'snapshot/mosl_facts_reviewed_2026-11-02.json'
DEFAULT_MOSL_LAKE = 'snapshot/mosl_lake_2026-11-02.json'
EXTRA_ENV = 'GROWW_EXTRA'          # same as --groww-extra; the flag wins
SIGNED_OFF_EXTRA = 'i'             # optional Groww IR switches AB signed off (31 Oct 2026: g-i on, g-h off); published
REFUSED_EXIT = 2


def parse(argv):
    """-> dict(db, publish, broker, snapshot, reviewed, groww_snapshot, groww_facts, groww_extra, groww_ir,
    groww_exchange, mosl_snapshot, mosl_facts, mosl_lake). Positional: snapshot, facts.

    groww_extra: the optional Groww IR switches ('h', 'i', 'hi'); default SIGNED_OFF_EXTRA (env GROWW_EXTRA overrides,
    'none' turns them all off)."""
    opts = dict(db=False, publish=False, broker=ANGEL, groww_snapshot=DEFAULT_GROWW_SNAPSHOT,
                groww_facts=DEFAULT_GROWW_FACTS, groww_extra=os.environ.get(EXTRA_ENV, SIGNED_OFF_EXTRA),
                groww_ir=DEFAULT_GROWW_IR, groww_exchange=DEFAULT_GROWW_EXCHANGE, mosl_snapshot=DEFAULT_MOSL_SNAPSHOT,
                mosl_facts=DEFAULT_MOSL_FACTS, mosl_lake=DEFAULT_MOSL_LAKE)
    args, i = [], 0
    while i < len(argv):
        a = argv[i]
        if a in ('--db', '--publish'):
            opts[a[2:]] = True
        elif a.startswith('--broker') or a.split('=')[0] in ('--groww-snapshot', '--groww-facts', '--groww-extra',
                                                              '--groww-ir', '--groww-exchange', '--mosl-snapshot',
                                                              '--mosl-facts', '--mosl-lake'):
            key, eq, val = a.partition('=')
            if not eq:
                i += 1
                if i >= len(argv):
                    sys.exit(f'{key} needs a value')
                val = argv[i]
            if key == '--broker':
                if val.upper() not in BROKERS:
                    sys.exit(f'--broker {val}: expected ANGELONE, GROWW, MOSL or all')
                opts['broker'] = BROKERS[val.upper()]
            else:
                opts[key[2:].replace('-', '_')] = val
        elif a.startswith('--'):
            sys.exit(f'unknown option {a}')
        else:
            args.append(a)
        i += 1
    raw = opts['groww_extra'].lower().replace(',', '')
    extra = '' if raw in ('', 'none', 'off') else ''.join(sorted(set(raw)))
    if set(extra) - {'h', 'i'}:
        sys.exit(f"--groww-extra {opts['groww_extra']!r}: expected h, i or hi")
    opts['groww_extra'] = extra
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
    unsigned = ''.join(sorted(set(o['groww_extra']) - set(SIGNED_OFF_EXTRA)))
    if publish_on and unsigned and broker in (GROWW, 'ALL'):
        sys.exit(f"--publish with Groww switches g-{unsigned}: not signed off by AB, nothing is published "
                 f"(use --groww-extra {SIGNED_OFF_EXTRA or 'none'} for a published run)")
    want_angel, want_groww, want_mosl = broker in (ANGEL, 'ALL'), broker in (GROWW, 'ALL'), broker in (MOSL, 'ALL')
    need_angel = want_angel or want_groww                # MOSL alone needs no Angel One run
    pending = 'Not published yet: the run is published after this report if E5 does not block.' if publish_on else None

    # ── Angel One run (Groww's calibration comes from it, so it is computed whenever Groww is wanted) ──
    note, reader, snap_full, angel, out, angel_blocked = '', None, None, None, None, False
    if o['db']:
        from .db import CachingReader, SupabaseReader
        from .snapshot import build_snapshot, complete_through, trim
        reader = CachingReader((reader_factory or SupabaseReader)())
        snap, reviewed = build_snapshot(reader)
        snap_full = snap                                  # untrimmed: MOSL takes its own as-of date from it
        if need_angel:
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
    elif need_angel:
        angel = live_run(o['snapshot'], o['reviewed'])
        out = f"out/live/{angel['as_of']}"
        snap_full = angel['snapshot']
        if want_angel:
            write(angel, out)
    else:
        snap_full = json.load(open(o['snapshot']))
    if need_angel:
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
            if not want_mosl:
                return 1
            angel_blocked = True                          # MOSL does not depend on it: its own run goes on

    # ── Groww run, from the Angel run ──
    rc, groww, gout, refused, ir_note = (1 if angel_blocked else 0), None, os.path.join(out or '', 'groww'), None, ''
    if want_groww and not angel_blocked:
        try:
            from .groww_run import SWITCHES, groww_inputs, ir_inputs, live_run_groww
            from ..engine import groww_ir as IR
            extra, ir, turnover = o['groww_extra'], None, None
            if o['db']:
                gsnap, facts = groww_inputs(reader)
            else:
                from ..engine import groww_switches as GS
                gsnap = json.load(open(o['groww_snapshot']))
                facts = GS.load_reviewed(o['groww_facts'])
            if extra:                      # IR switches: SIGNED_OFF_EXTRA by default, others only when asked for
                try:
                    if o['db']:
                        ir, turnover = ir_inputs(reader)
                    else:
                        ir = IR.IR(json.load(open(o['groww_ir']))['rows'])
                        turnover = IR.Turnover.from_fixture(o['groww_exchange'])
                except (IR.IRError, OSError) as e:     # no archive in the DB, or no IR file for a dry run
                    if set(extra) - set(SIGNED_OFF_EXTRA):
                        raise GrowwRefused([f'Groww IR switches g-{extra}: {e}'])
                    # signed-off switches without IR data: publish the base chain and say so, rather than no Groww
                    ir_note = f'g-{extra} skipped: {e}'
                    _warn('Groww IR switches skipped', ir_note)
                    extra, ir, turnover = '', None, None
                if extra:
                    print(f"Groww IR switches ON: g-{extra} (IR snapshot {ir.snapshot_date}); "
                          f"signed off: g-{SIGNED_OFF_EXTRA or '(none)'}")
            groww = live_run_groww(angel, gsnap, facts, SWITCHES + extra, ir, turnover)
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

    # ── MOSL run: the same snapshot, its own inputs and as-of date; nothing from the Angel One calibration ──
    mosl, mrefused, mnote, mout = None, None, '', None
    if want_mosl:
        base = angel['as_of'] if angel else max(r['trade_date'] for r in snap_full['calendar'])
        mout = f'out/live/{base}/mosl'
        try:
            from .mosl_run import SWITCHES as MOSL_SWITCHES, live_run_mosl, mosl_inputs
            from .snapshot import mosl_lake_rows
            if o['db']:
                msnap, mfacts = mosl_inputs(reader)
                lake_rows = mosl_lake_rows(reader.table('sb_market_daily'))
            else:
                from ..engine import mosl_switches as MS
                msnap = json.load(open(o['mosl_snapshot']))
                mfacts = MS.load_reviewed(o['mosl_facts'])
                lake_rows = [dict(trade_date=d, dataset=k.split('/')[0], metric=k.split('/')[1], value=v, status=st,
                                  source='exchangesdash_json')
                             for k, rows in json.load(open(o['mosl_lake']))['series'].items() for d, v, st in rows]
            mosl = live_run_mosl(snap_full, msnap, mfacts, lake_rows, MOSL_SWITCHES)
            mout = f"out/live/{mosl['as_of']}/mosl"
            mnote = f"MOSL complete through {mosl['as_of']}" + (f" (limited by {mosl['limiting']})" if mosl['limiting'] else '')
        except MoslRefused as e:
            mrefused = e
        except Exception:
            traceback.print_exc()
            print('MOSL run failed (an error, not a refusal).')
            rc = 1
        if mrefused:
            os.makedirs(mout, exist_ok=True)
            with open(os.path.join(mout, 'report.md'), 'w') as fh:
                fh.write('# Live run · MOSL — refused\n\n' + '\n'.join(f'- {r}' for r in mrefused.reasons) + '\n')
            _warn('MOSL not published', '; '.join(mrefused.reasons))
            if not want_angel and not want_groww:
                rc = REFUSED_EXIT
        if mosl is not None:
            write(mosl, mout, pending)
            print(report_md(mosl, pending))
            print(mnote)
            print('written', mout)
            if mosl['report'].blocking:
                _warn('MOSL not published', f"E5 blocks the MOSL run as of {mosl['as_of']}: "
                      + '; '.join(str(i) for i in mosl['report'].errors[:3]))
                rc = 1

    # ── publish: Angel first, then Groww, then MOSL ──
    if publish_on:
        from .db import SupabaseWriter
        from .publish import publish
        writer = None
        angel_id = None
        if want_angel and not angel_blocked:
            writer = (writer_factory or SupabaseWriter)()
            angel_id, counts = publish(angel, writer, notes_extra=note)
            print(f'published run {angel_id}: {counts}')
            write(angel, out, f'Published to the database as run {angel_id}: {counts}.')
        if groww is not None and not groww['report'].blocking:
            writer = writer or (writer_factory or SupabaseWriter)()
            src = (f'Angel One calibration from run {angel_id}' if angel_id
                   else 'Angel One calibration from the same snapshot (the Angel run is not published by this call)')
            gid, counts = publish(groww, writer, notes_extra='; '.join(x for x in (note, src, ir_note) if x))
            print(f'published GROWW run {gid}: {counts}')
            write(groww, gout, f'Published to the database as run {gid}: {counts}.')
        if mosl is not None and not mosl['report'].blocking:
            writer = writer or (writer_factory or SupabaseWriter)()
            mid, counts = publish(mosl, writer, notes_extra=mnote)
            print(f'published MOSL run {mid}: {counts}')
            write(mosl, mout, f'Published to the database as run {mid}: {counts}.')
    return rc
