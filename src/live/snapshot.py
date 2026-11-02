"""Build the engine's snapshot (src/engine/inputs.py shape) from the sb_* tables, through an E6 reader.

The daily job reads the DB with SupabaseReader and runs the engine on what this returns; tests and local
runs use a snapshot file. Volumes: one row per date and series, the workbook's copy first and the lake where
the workbook has no row (new days); lake rows are also kept separately for switch (c).
"""
from __future__ import annotations

import datetime as dt

from .loader import ADR_MARKET_KEYS, MOSL_LAKE_KEYS, is_lake, select_volumes

BROKER = 'ANGELONE'


def _le(d, as_of):
    return as_of is None or str(d)[:10] <= as_of


def build_snapshot(reader, broker=BROKER, as_of=None):
    """(snapshot dict, reviewed facts). as_of: ISO date or None (everything)."""
    facts = [f for f in reader.table('sb_disclosure_facts', broker_id=broker) if f['status'] != 'rejected']
    raw = [r for r in reader.table('sb_market_daily') if _le(r['trade_date'], as_of)]
    selected = select_volumes(raw, 'excel_first', ADR_MARKET_KEYS)
    market = [dict(trade_date=v.date.isoformat(), dataset=v.key.split(':')[0], metric=v.key.split(':')[1],
                   value=v.value, status=v.status, source=v.source)
              for series in selected.values() for v in series]
    # one lake row per day and series; with several lake sources the loader's tie-break applies (lowest
    # source name, so the daily refresh 'exchangesdash_json' wins over the one-off '...@b2049b5' import)
    lake_by = {}
    for r in raw:
        if is_lake(r['source']) and f"{r['dataset']}:{r['metric']}" in ADR_MARKET_KEYS \
                and r.get('status', 'ok') == 'ok':
            k = (str(r['trade_date'])[:10], r['dataset'], r['metric'])
            if k not in lake_by or r['source'] < lake_by[k]['source']:
                lake_by[k] = dict(trade_date=k[0], dataset=r['dataset'], metric=r['metric'], value=r['value'],
                                  source=r['source'])
    lake = list(lake_by.values())
    snap = {
        'calendar': sorted((dict(r, trade_date=str(r['trade_date'])[:10]) for r in reader.table('sb_calendar')
                            if _le(r['trade_date'], as_of)), key=lambda r: r['trade_date']),
        'facts': [f for f in facts if f['status'] != 'reviewed'],
        'monthly': reader.table('sb_market_monthly'),
        'pins': reader.table('sb_parity_pins', broker_id=broker),
        'assumptions': [a for a in reader.table('sb_assumptions') if a.get('broker_id') in ('*', broker)],
        'market_daily': sorted(market, key=lambda r: (r['dataset'], r['metric'], r['trade_date'])),
        'market_daily_lake': sorted(lake, key=lambda r: (r['dataset'], r['metric'], r['trade_date'])),
        '_built': dict(at=dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), as_of=as_of,
                       source=repr(reader)),
    }
    reviewed = [f for f in facts if f['status'] == 'reviewed']
    return snap, reviewed


def complete_through(snap, keys=None):
    """(date, limiting series): the last calendar day on which every engine input has an 'ok' value, in the
    workbook's copy or in the lake (switch c takes the lake's value on imputed days). Series that end on the
    same day are all named, comma-separated; 'sb_calendar' when the calendar ends first.

    The industry MTF book is published with a lag and is left out (coverage allows its last 3 trading days).
    """
    keys = keys or [k for k in ADR_MARKET_KEYS if k != 'mtf_industry:book_cr']
    last = {}
    for r in list(snap['market_daily']) + list(snap.get('market_daily_lake', [])):
        k = f"{r['dataset']}:{r['metric']}"
        if k in keys and r.get('status', 'ok') == 'ok':
            last[k] = max(last.get(k, ''), r['trade_date'])
    missing = [k for k in keys if k not in last]
    if missing:
        raise ValueError(f'no rows for {missing}')
    first_end = min(last.values())
    limiting = ', '.join(sorted(k for k, d in last.items() if d == first_end))
    cal_last = max(r['trade_date'] for r in snap['calendar'])
    if cal_last < first_end:
        return cal_last, 'sb_calendar'
    return first_end, limiting


def trim(snap, as_of):
    """Copy of the snapshot without calendar days or volumes after as_of."""
    out = dict(snap)
    out['calendar'] = [r for r in snap['calendar'] if r['trade_date'] <= as_of]
    out['market_daily'] = [r for r in snap['market_daily'] if r['trade_date'] <= as_of]
    out['market_daily_lake'] = [r for r in snap['market_daily_lake'] if r['trade_date'] <= as_of]
    return out


# ── MOSL: its own inputs (docs/MOSL_LIVE_SPEC.md) ──
def mosl_lake_rows(rows, as_of=None):
    """sb_market_daily rows of MOSL's four lake series (source other than the workbook's `excel_seed`), up to as_of."""
    keys = {k.replace(':', '/') for k in MOSL_LAKE_KEYS}
    return [dict(r) for r in rows if is_lake(r['source']) and f"{r['dataset']}/{r['metric']}" in keys and _le(r['trade_date'], as_of)]


def mosl_lake_series(rows):
    """{'dataset/metric': {date: (value, status)}} from lake rows: one per date, an 'ok' row before a suspect one, then the
    lowest source name (the daily refresh 'exchangesdash_json' before the one-off '...@b2049b5' import)."""
    best = {}
    for r in rows:
        k, d = f"{r['dataset']}/{r['metric']}", str(r['trade_date'])[:10]
        rank = (r.get('status', 'ok') != 'ok', r['source'])
        if (k, d) not in best or rank < best[(k, d)][0]:
            best[(k, d)] = (rank, (float(r['value']), r.get('status', 'ok')))
    out = {k.replace(':', '/'): {} for k in MOSL_LAKE_KEYS}
    for (k, d), (_, vs) in best.items():
        out.setdefault(k, {})[d] = vs
    return out


def complete_through_mosl(snap, lake):
    """(date, limiting series): the last calendar day on which every input of a MOSL run has an 'ok', non-zero value:
    its four lake series (zero on a trading day is suspect) and MCX contracts; the industry MTF book is left out (published
    with a lag, coverage allows its last 3 trading days). Like complete_through, with MOSL's own series: the NSE
    index-option contracts end on the last 'ok' day, so until the lake has them again MOSL's date is earlier than Angel One's."""
    mcx_end, mcx_lim = complete_through(snap, keys=['mcx:contracts'])
    ends = {mcx_lim if mcx_lim == 'sb_calendar' else 'mcx:contracts': mcx_end}
    for key in MOSL_LAKE_KEYS:
        ok = [d for d, (v, st) in lake.get(key.replace(':', '/'), {}).items() if st == 'ok' and v > 0]
        if not ok:
            raise ValueError(f'no rows for {key}')
        ends[key] = max(ok)
    first_end = min(ends.values())
    return first_end, ', '.join(sorted(k for k, d in ends.items() if d == first_end))
