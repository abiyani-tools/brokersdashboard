"""Publish a live run to sb_runs / sb_calibration / sb_daily_revenue / sb_summary_cells (PLAN 4.1).

Order: the sb_runs row ('running') → calibration → daily revenue → Summary cells → sb_runs 'success'.
Any failure marks the run 'failed' with the error and re-raises; a run whose E5 report blocks, or with a
non-finite value, is refused before anything is written. AB approved publishing on 23 Oct 2026.
"""
from __future__ import annotations

import datetime as dt
import math
import os
import subprocess
import uuid

BROKER = 'ANGELONE'


class PublishRefused(RuntimeError):
    pass


def code_version():
    sha = os.environ.get('GITHUB_SHA')
    if not sha:
        try:
            sha = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
        except Exception:
            sha = 'unknown'
    return f'broker_db engine live ({sha[:12]})'


def rows_for(run, run_id):
    from ..engine import publish as P
    return {
        'sb_calibration': P.calibration_rows(run_id, run['calib']),
        'sb_daily_revenue': P.daily_rows(run_id, run['daily']),
        'sb_summary_cells': P.period_summary_rows(run_id, run['rows']),
    }


def _check_finite(tables):
    for name, rows in tables.items():
        for r in rows:
            for k, v in r.items():
                if isinstance(v, float) and not math.isfinite(v):
                    raise PublishRefused(f'{name}: non-finite {k} in {r}')


def publish(run, writer, notes_extra=''):
    rep = run['report']
    if rep.blocking:
        raise PublishRefused('E5 blocks this run; nothing written:\n' + rep.summary())
    run_id = str(uuid.uuid4())
    tables = rows_for(run, run_id)
    _check_finite(tables)
    now = lambda: dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    notes = (f"live run, switches {run['switches']}; E5 {len(rep.errors)} blocking / "
             f"{len(rep.find(severity='warning'))} warnings / {len(rep.find(severity='info'))} info"
             + (f'; {notes_extra}' if notes_extra else ''))
    writer.insert('sb_runs', [dict(run_id=run_id, broker_id=BROKER, mode='live', as_of_date=run['as_of'],
                                   started_at=now(), status='running', parity_pass=None,
                                   code_version=code_version(), notes=notes)])
    try:
        counts = {name: writer.insert(name, rows) for name, rows in tables.items()}
    except Exception as e:
        writer.update('sb_runs', dict(status='failed', finished_at=now(), notes=f'{notes}; FAILED: {e}'[:2000]),
                      run_id=run_id)
        raise
    writer.update('sb_runs', dict(status='success', finished_at=now()), run_id=run_id)
    return run_id, counts
