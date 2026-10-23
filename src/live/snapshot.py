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
