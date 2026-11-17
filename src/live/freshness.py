"""Freshness check (06:15 IST): is every broker's latest published run as of the last trading day?

Target: AB wants day D's ADR published by 06:00 IST on D+1. The target day is the last date in ExchangesDash's NSE file
(the file only has trading days, so holidays and weekends need no list). Each broker's latest 'success' live run in
sb_runs is compared with it. When a broker is behind, the cause is named:
  - upstream: an input series in the lake ends before the target (e.g. MCX contracts, filled a day late), or
  - pipeline: the lake has every series through the target but no run published it (run late, crashed or blocked).
If the NSE file itself ends before the previous weekday, that is reported too (a holiday, or NSE data not in yet).
Read only: sb_runs (brokers-dashboard) and the public ExchangesDash JSON. Exit 1 when any broker is behind.

    python -m src.live.freshness            # needs SUPABASE_URL / SUPABASE_SERVICE_KEY
"""
from __future__ import annotations

import datetime as dt
import os
import sys

from .loader import ADR_MARKET_KEYS, MOSL_MARKET_KEYS

# The series each run's as-of date waits on (loader.py); the industry MTF book is published with a lag and left out,
# as in snapshot.complete_through / complete_through_mosl. Groww uses Angel One's inputs.
_LAGGED = "mtf_industry:book_cr"
ANGEL_KEYS = [k for k in ADR_MARKET_KEYS if k != _LAGGED]
MOSL_KEYS = [k for k in MOSL_MARKET_KEYS if k != _LAGGED]
BROKERS = {"ANGELONE": ANGEL_KEYS, "GROWW": ANGEL_KEYS, "MOSL": MOSL_KEYS}
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def lake_ends(rows: list[dict]) -> dict[str, str]:
    """Last 'ok', non-zero date per dataset:metric in sb_market_daily-shaped rows."""
    ends: dict[str, str] = {}
    for r in rows:
        if r.get("status", "ok") == "ok" and r["value"]:
            k = f"{r['dataset']}:{r['metric']}"
            ends[k] = max(ends.get(k, ""), r["trade_date"])
    return ends


def previous_weekday(today: dt.date) -> dt.date:
    d = today - dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d


def assess(runs: list[dict], ends: dict[str, str], nse_dates: list[str], today: dt.date) -> dict:
    """runs: sb_runs rows; ends: lake_ends(); nse_dates: dates in the NSE file; today: IST date of the check."""
    target = max(d for d in nse_dates if d < today.isoformat())
    prev = previous_weekday(today).isoformat()
    out = {"target": target, "nse_note": None, "brokers": {}}
    if target < prev:
        out["nse_note"] = f"NSE file ends {target}, before {prev}: a holiday, or NSE data for {prev} is not in yet"
    for broker, keys in BROKERS.items():
        ok = [r for r in runs if r["broker_id"] == broker and r.get("status") == "success"
              and r.get("mode", "live") == "live"]
        as_of = max((str(r["as_of_date"])[:10] for r in ok), default=None)
        late = sorted(f"{k} through {ends.get(k, 'none')}" for k in keys if ends.get(k, "") < target)
        if as_of and as_of >= target:
            status, cause = "ok", None
        elif late:
            status, cause = "behind", "upstream: " + "; ".join(late)
        else:
            status, cause = "behind", f"pipeline: the lake has every input through {target} but no run published it"
        out["brokers"][broker] = dict(as_of=as_of, status=status, cause=cause)
    return out


def report_md(a: dict, now: str) -> str:
    lines = [f"## Freshness check, {now} IST: target day {a['target']}", "",
             "| Broker | Published as of | Status | Cause |", "|---|---|---|---|"]
    for b, r in a["brokers"].items():
        lines.append(f"| {b} | {r['as_of'] or 'none'} | {r['status']} | {r['cause'] or ''} |")
    if a["nse_note"]:
        lines += ["", a["nse_note"]]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    from .db import SupabaseReader
    from .refresh_market import fetch, lake_rows, _rows
    now = dt.datetime.now(IST)
    data, shas = fetch()
    rows = lake_rows(data, shas, now.isoformat())
    special = {r["date"] for r in data["nse"].get("special_sessions", [])} if isinstance(data["nse"], dict) else set()
    nse_dates = [r["date"] for r in _rows(data["nse"]) if r["date"] not in special]   # Muhurat etc. not targeted
    runs = SupabaseReader().table("sb_runs")
    a = assess(runs, lake_ends(rows), nse_dates, now.date())
    md = report_md(a, now.strftime("%Y-%m-%d %H:%M"))
    print(md)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as fh:
            fh.write(md)
    behind = {b: r for b, r in a["brokers"].items() if r["status"] != "ok"}
    for b, r in behind.items():
        print(f"::error title={b} not published for {a['target']}::as of {r['as_of']}; {r['cause']}")
    if a["nse_note"]:
        print(f"::warning title=NSE file behind::{a['nse_note']}")
    return 1 if behind else 0


if __name__ == "__main__":
    sys.exit(main())
