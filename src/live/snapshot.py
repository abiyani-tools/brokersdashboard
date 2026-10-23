"""Build the engine's snapshot (src/engine/inputs.py shape) from the sb_* tables, through an E6 reader.

The daily job reads the DB with SupabaseReader and runs the engine on what this returns; tests and local
runs use a snapshot file. Volumes: one row per date and series, the workbook's copy first and the lake where
the workbook has no row (new days); lake rows are also kept separately for switch (c).
"""
from __future__ import annotations

import datetime as dt

from .loader import ADR_MARKET_KEYS, is_lake, select_volumes

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
    lake = [dict(trade_date=str(r['trade_date'])[:10], dataset=r['dataset'], metric=r['metric'],
                 value=r['value'], source=r['source'])
            for r in raw if is_lake(r['source']) and f"{r['dataset']}:{r['metric']}" in ADR_MARKET_KEYS
            and r.get('status', 'ok') == 'ok']
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
    workbook's copy or in the lake (switch c takes the lake's value on imputed days).

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
    key = min(last, key=last.get)
    cal_last = max(r['trade_date'] for r in snap['calendar'])
    return min(last[key], cal_last), key


def trim(snap, as_of):
    """Copy of the snapshot without calendar days or volumes after as_of."""
    out = dict(snap)
    out['calendar'] = [r for r in snap['calendar'] if r['trade_date'] <= as_of]
    out['market_daily'] = [r for r in snap['market_daily'] if r['trade_date'] <= as_of]
    out['market_daily_lake'] = [r for r in snap['market_daily_lake'] if r['trade_date'] <= as_of]
    return out
