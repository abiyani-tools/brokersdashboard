"""Daily refresh of the exchange volumes in sb_market_daily from ExchangesDash's public JSON (read only).

    python3 -m src.live.refresh_market            # dry run: what would be written, nothing sent
    python3 -m src.live.refresh_market --write    # upsert into sb_market_daily (needs SUPABASE_SERVICE_KEY)

Reads the files in FILES from the owner's GitHub repo, each at the latest commit that changed it, and maps them
as seed/build_fixtures.py did for the 23 Oct import. Rows go under the stable source 'exchangesdash_json'
(commit in source_ref), which the loader prefers over the one-off 'exchangesdash_json@b2049b5' and
'octo_mcx@2026-10-22' rows, so each run replaces the whole series and the owner's corrections to past days
come through. A zero on a trading day is stored as 'suspect' for E5 to block on.

Three series are not public yet; the owner was asked to publish them under these names
(docs/Prompt_for_ExchangesDash_owner.md) and they are read as soon as they appear:
  1. NSE cash trades     `cash_trades` in nse_dashboard_data.json rows
  2. MCX contracts       `total_contracts` in mcx_dashboard_data.json rows, or mcx_contracts_daily.json
  3. industry MTF book   nse_mtf_daily.json rows {date, book_cr}
The two new files are optional: a file the repo doesn't have is skipped. The owner's answer (2 Nov 2026): NSE cash
trades and MCX total_contracts arrive in those files with their PR #33; the industry MTF book stays in their
Supabase view `codex_public_nse_mtf_daily`, read with their read-only key (env NSE_LAKE_ANON_KEY; skipped if unset).

sb_calendar is extended the same way: each day after its last date on which NSE or MCX traded (a row in
the NSE or MCX file) is added, equity / MCX flags from which file has it. A day in a file's
special_sessions is added with special_session 'special' and a note for AB to classify (muhurat, dr_test,
budget, ...). Existing calendar days are never changed.
"""
from __future__ import annotations

import datetime as dt
import sys

from .periods import fy_labels

REPO = "sucaanalytics-max/ExchangesDash"
FILES = {
    "nse": "dashboard/data/nse_dashboard_data.json",
    "bse": "dashboard/data/bse_dashboard_data.json",
    "mcx": "dashboard/data/mcx_dashboard_data.json",
    "mcx_contracts": "dashboard/data/mcx_contracts_daily.json",     # optional
    "mtf": "dashboard/data/nse_mtf_daily.json",                     # optional
}
REQUIRED = ("nse", "bse", "mcx")
SOURCE = "exchangesdash_json"
START = "2023-09-29"
PK = ("trade_date", "dataset", "metric", "source")


def _rows(d):
    """Daily rows of a dashboard file ({daily_all, special_sessions}) or of a plain list of rows."""
    if isinstance(d, list):
        return d
    return (d.get("daily_all") or d.get("daily") or []) + d.get("special_sessions", [])


def lake_rows(data: dict, shas: dict, loaded_at: str) -> list[dict]:
    """sb_market_daily rows (one per date × dataset × metric).

    data: {file key: parsed JSON} for the files that exist; shas: {file key: commit} they were read at."""
    out: dict[tuple, dict] = {}

    def push(key, date, ds, metric, value, field, unit, zero_is_suspect=False):
        if value is None or date < START:
            return
        bad = zero_is_suspect and value == 0
        out[(date, ds, metric)] = dict(
            trade_date=date, dataset=ds, metric=metric, source=SOURCE, value=float(value), unit=unit,
            status="suspect" if bad else "ok", note="zero on a trading day" if bad else None,
            source_ref=f"{REPO}@{shas[key][:7]}:{FILES[key]}[{date}].{field}", loaded_at=loaded_at)

    for r in _rows(data.get("nse", {})):
        d = r["date"]
        push("nse", d, "nse_fo", "contracts", r.get("total_contracts"), "total_contracts", "count", True)
        push("nse", d, "nse_fo", "io_contracts", r.get("io_contracts"), "io_contracts", "count", True)
        push("nse", d, "nse_fo", "so_contracts", r.get("so_contracts"), "so_contracts", "count", True)
        push("nse", d, "nse_fo", "io_premium_cr", r.get("io_premium"), "io_premium", "Rs Cr")
        push("nse", d, "nse_fo", "so_premium_cr", r.get("so_premium"), "so_premium", "Rs Cr")
        if r.get("if_turnover") is not None and r.get("sf_turnover") is not None:
            push("nse", d, "nse_fo", "fut_turnover_cr", r["if_turnover"] + r["sf_turnover"],
                 "if_turnover+sf_turnover", "Rs Cr")
        push("nse", d, "nse_cash", "turnover_cr", r.get("cash_traded_value"), "cash_traded_value", "Rs Cr")
        push("nse", d, "nse_cash", "trades", r.get("cash_trades"), "cash_trades", "count", True)
    for r in _rows(data.get("bse", {})):
        d = r["date"]
        push("bse", d, "bse_fo", "contracts", r.get("total_contracts"), "total_contracts", "count", True)
        push("bse", d, "bse_fo", "opt_premium_cr", r.get("options_premium_turnover"), "options_premium_turnover",
             "Rs Cr")
        push("bse", d, "bse_fo", "fut_turnover_cr", r.get("futures_turnover"), "futures_turnover", "Rs Cr")
        push("bse", d, "bse_cash", "trades", r.get("cash_trades"), "cash_trades", "count", True)
        push("bse", d, "bse_cash", "turnover_cr", r.get("cash_traded_value"), "cash_traded_value", "Rs Cr")
    # MCX contracts: the dashboard file's field, or the separate file (which wins on a date both have)
    for key in ("mcx", "mcx_contracts"):
        for r in _rows(data.get(key, {})):
            push(key, r["date"], "mcx", "contracts", r.get("total_contracts"), "total_contracts", "count", True)
    for r in _rows(data.get("mtf", {})):
        push("mtf", r["date"], "mtf_industry", "book_cr", r.get("book_cr"), "book_cr", "Rs Cr", True)
    return sorted(out.values(), key=lambda x: (x["trade_date"], x["dataset"], x["metric"]))


def calendar_rows(data: dict, after: str) -> list[dict]:
    """sb_calendar rows for the days after `after` on which NSE or MCX traded, per the dashboard files."""
    def dates(key):
        d = data.get(key, {})
        return {r["date"] for r in _rows(d)}, {r["date"] for r in d.get("special_sessions", [])}
    eq, eq_special = dates("nse")
    mcx, mcx_special = dates("mcx")
    out = []
    for day in sorted(d for d in eq | mcx if d > after):
        date = dt.date.fromisoformat(day)
        labels = fy_labels(date)
        special = day in eq_special | mcx_special
        out.append(dict(trade_date=day, fy=labels["FY"], q_fy=labels["Q"], fy_month=labels["M"],
                        weekday=date.strftime("%A"), is_equity_day=day in eq, is_mcx_day=day in mcx,
                        special_session="special" if special else None,
                        note=("in ExchangesDash special_sessions; type to classify (muhurat, dr_test, budget, ...)"
                              if special else None)))
    return out


def fetch(session=None):
    """(data, shas): each file at the latest commit that changed it; optional files missing from the repo are
    left out."""
    if session is None:
        import requests
        session = requests.Session()
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "brokersdashboard-refresh"}
    data, shas = {}, {}
    for k, path in FILES.items():
        resp = session.get(f"https://api.github.com/repos/{REPO}/commits", params={"path": path, "per_page": 1},
                           headers=headers, timeout=60)
        resp.raise_for_status()
        commits = resp.json()
        if not commits:
            if k in REQUIRED:
                raise RuntimeError(f"{REPO}: no commits for {path}")
            continue
        shas[k] = commits[0]["sha"]
        r = session.get(f"https://raw.githubusercontent.com/{REPO}/{shas[k]}/{path}", timeout=120)
        r.raise_for_status()
        data[k] = r.json()
    return data, shas


def summary(rows: list[dict]) -> str:
    last: dict[str, str] = {}
    suspect: dict[str, int] = {}
    for r in rows:
        k = f"{r['dataset']}:{r['metric']}"
        last[k] = max(last.get(k, ""), r["trade_date"])
        suspect[k] = suspect.get(k, 0) + (r["status"] == "suspect")
    return "\n".join(f"  {k:24} last {v}  suspect {suspect[k]}" for k, v in sorted(last.items()))


MTF_LAKE_URL_ENV, MTF_LAKE_KEY_ENV = "NSE_LAKE_URL", "NSE_LAKE_ANON_KEY"
MTF_LAKE_DEFAULT_URL = "https://vuswwmczfrlzjoxfvkzu.supabase.co"
MTF_VIEW = "codex_public_nse_mtf_daily"   # the owner's public view: reporting_date, closing_outstanding_cr
MTF_SOURCE = "codex_nse_mtf"


def mtf_rows(view_rows: list, loaded_at: str) -> list[dict]:
    """sb_market_daily rows (mtf_industry / book_cr, Rs Cr) from the owner's daily industry MTF book view."""
    out = []
    for r in view_rows:
        d, v = str(r["reporting_date"])[:10], r.get("closing_outstanding_cr")
        if v is None or d < START:
            continue
        bad = v == 0
        out.append(dict(trade_date=d, dataset="mtf_industry", metric="book_cr", source=MTF_SOURCE, value=float(v),
                        unit="Rs Cr", status="suspect" if bad else "ok", note="zero on a trading day" if bad else None,
                        source_ref=f"{MTF_VIEW}[{d}].closing_outstanding_cr", loaded_at=loaded_at))
    return out


def fetch_mtf_book(session=None, page: int = 1000):
    """(view rows, message). Reads the owner's view with their read-only key from the environment; without the key
    nothing is read and the message says so (the run goes on with the rows already in sb_market_daily)."""
    import os
    key = os.environ.get(MTF_LAKE_KEY_ENV)
    if not key:
        return [], f"industry MTF book: skipped ({MTF_LAKE_KEY_ENV} not set)"
    if session is None:
        import requests
        session = requests.Session()
    url = f"{os.environ.get(MTF_LAKE_URL_ENV) or MTF_LAKE_DEFAULT_URL}/rest/v1/{MTF_VIEW}"
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json"}
    rows, offset = [], 0
    while True:
        r = session.get(url, params={"select": "reporting_date,closing_outstanding_cr", "order": "reporting_date",
                                     "reporting_date": f"gte.{START}", "limit": page, "offset": offset},
                        headers=headers, timeout=60)
        r.raise_for_status()
        part = r.json()
        rows += part
        if len(part) < page:
            break
        offset += page
    last = max((str(x["reporting_date"])[:10] for x in rows), default="none")
    return rows, f"industry MTF book: {len(rows)} days from {MTF_VIEW}, last {last}"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    data, shas = fetch()
    loaded_at = dt.datetime.now(dt.timezone.utc).isoformat()
    rows = lake_rows(data, shas, loaded_at)
    read = " ".join(f"{k}@{v[:7]}" for k, v in shas.items())
    print(f"{REPO} {read}: {len(rows)} rows from {START}")
    print(f"  not in the repo yet: {', '.join(k for k in FILES if k not in shas) or 'none'}")
    view, msg = fetch_mtf_book()
    rows += mtf_rows(view, loaded_at)
    print(f"  {msg}")
    print(summary(rows))
    if "--write" not in argv:
        print("dry run: nothing written (pass --write to upsert into sb_market_daily and extend sb_calendar)")
        return 0
    from .db import SupabaseReader, SupabaseWriter
    writer = SupabaseWriter()
    n = writer.upsert("sb_market_daily", rows, PK)
    print(f"upserted {n} rows into sb_market_daily (sources {SOURCE}, {MTF_SOURCE})")
    cal_last = max(str(r["trade_date"])[:10] for r in SupabaseReader().table("sb_calendar"))
    new_days = calendar_rows(data, cal_last)
    if new_days:
        writer.insert("sb_calendar", new_days)
    special = [r["trade_date"] for r in new_days if r["special_session"]]
    print(f"sb_calendar: last day was {cal_last}; added {len(new_days)} days"
          + (f" through {new_days[-1]['trade_date']}" if new_days else "")
          + (f"; special sessions to classify: {', '.join(special)}" if special else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
