"""Daily refresh of the exchange volumes in sb_market_daily from ExchangesDash's public JSON (read only).

    python3 -m src.live.refresh_market            # dry run: what would be written, nothing sent
    python3 -m src.live.refresh_market --write    # upsert into sb_market_daily (needs SUPABASE_SERVICE_KEY)

Reads dashboard/data/{nse,bse}_dashboard_data.json (daily_all + special_sessions) from the owner's GitHub repo,
each at the latest commit that changed it, and maps them as seed/build_fixtures.py did for the 23 Oct
import. Rows go under the stable source 'exchangesdash_json' (commit in source_ref), which the loader prefers
over the one-off 'exchangesdash_json@b2049b5' rows, so each run replaces the whole series and the owner's
corrections to past days come through. A zero on a trading day is stored as 'suspect' for E5 to block on.

NSE cash trades are not in the JSON yet (docs/Prompt_for_ExchangesDash_owner.md, item 1); they are picked up
when a `cash_trades` field appears. MCX contracts come from Octo-MCX and are not refreshed here.
"""
from __future__ import annotations

import datetime as dt
import json
import sys

REPO = "sucaanalytics-max/ExchangesDash"
FILES = {"nse": "dashboard/data/nse_dashboard_data.json", "bse": "dashboard/data/bse_dashboard_data.json"}
SOURCE = "exchangesdash_json"
START = "2023-09-29"
PK = ("trade_date", "dataset", "metric", "source")


def _rows(d):
    return d["daily_all"] + d.get("special_sessions", [])


def lake_rows(nse: dict, bse: dict, shas: dict, loaded_at: str) -> list[dict]:
    """sb_market_daily rows from the two dashboard JSON files (one row per date × dataset × metric).

    shas: {'nse': commit, 'bse': commit} the files were read at."""
    out: dict[tuple, dict] = {}

    def push(date, ds, metric, value, ref, unit, zero_is_suspect=False):
        sha = shas[ds[:3]]
        if value is None:
            return
        bad = zero_is_suspect and value == 0
        out[(date, ds, metric)] = dict(
            trade_date=date, dataset=ds, metric=metric, source=SOURCE, value=float(value), unit=unit,
            status="suspect" if bad else "ok", note="zero on a trading day" if bad else None,
            source_ref=f"{REPO}@{sha[:7]}:{ref}", loaded_at=loaded_at)

    for r in _rows(nse):
        d = r["date"]
        if d < START:
            continue
        ref = f"{FILES['nse']}[{d}]"
        push(d, "nse_fo", "contracts", r.get("total_contracts"), ref + ".total_contracts", "count", True)
        push(d, "nse_fo", "io_contracts", r.get("io_contracts"), ref + ".io_contracts", "count", True)
        push(d, "nse_fo", "so_contracts", r.get("so_contracts"), ref + ".so_contracts", "count", True)
        push(d, "nse_fo", "io_premium_cr", r.get("io_premium"), ref + ".io_premium", "Rs Cr")
        push(d, "nse_fo", "so_premium_cr", r.get("so_premium"), ref + ".so_premium", "Rs Cr")
        if r.get("if_turnover") is not None and r.get("sf_turnover") is not None:
            push(d, "nse_fo", "fut_turnover_cr", r["if_turnover"] + r["sf_turnover"],
                 ref + ".if_turnover+sf_turnover", "Rs Cr")
        push(d, "nse_cash", "turnover_cr", r.get("cash_traded_value"), ref + ".cash_traded_value", "Rs Cr")
        push(d, "nse_cash", "trades", r.get("cash_trades"), ref + ".cash_trades", "count", True)
    for r in _rows(bse):
        d = r["date"]
        if d < START:
            continue
        ref = f"{FILES['bse']}[{d}]"
        push(d, "bse_fo", "contracts", r.get("total_contracts"), ref + ".total_contracts", "count", True)
        push(d, "bse_fo", "opt_premium_cr", r.get("options_premium_turnover"), ref + ".options_premium_turnover",
             "Rs Cr")
        push(d, "bse_fo", "fut_turnover_cr", r.get("futures_turnover"), ref + ".futures_turnover", "Rs Cr")
        push(d, "bse_cash", "trades", r.get("cash_trades"), ref + ".cash_trades", "count", True)
        push(d, "bse_cash", "turnover_cr", r.get("cash_traded_value"), ref + ".cash_traded_value", "Rs Cr")
    return sorted(out.values(), key=lambda x: (x["trade_date"], x["dataset"], x["metric"]))


def fetch(session=None):
    """(nse, bse, shas): each file at the latest commit that changed it."""
    if session is None:
        import requests
        session = requests.Session()
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "brokersdashboard-refresh"}
    data, shas = {}, {}
    for k, path in FILES.items():
        resp = session.get(f"https://api.github.com/repos/{REPO}/commits", params={"path": path, "per_page": 1},
                           headers=headers, timeout=60)
        resp.raise_for_status()
        shas[k] = resp.json()[0]["sha"]
        r = session.get(f"https://raw.githubusercontent.com/{REPO}/{shas[k]}/{path}", timeout=120)
        r.raise_for_status()
        data[k] = r.json()
    return data["nse"], data["bse"], shas


def summary(rows: list[dict]) -> str:
    last: dict[str, str] = {}
    suspect: dict[str, int] = {}
    for r in rows:
        k = f"{r['dataset']}:{r['metric']}"
        last[k] = max(last.get(k, ""), r["trade_date"])
        suspect[k] = suspect.get(k, 0) + (r["status"] == "suspect")
    return "\n".join(f"  {k:24} last {v}  suspect {suspect[k]}" for k, v in sorted(last.items()))


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    nse, bse, shas = fetch()
    rows = lake_rows(nse, bse, shas, dt.datetime.now(dt.timezone.utc).isoformat())
    print(f"{REPO} nse@{shas['nse'][:7]} bse@{shas['bse'][:7]}: {len(rows)} rows from {START}")
    print(summary(rows))
    if "--write" not in argv:
        print("dry run: nothing written (pass --write to upsert into sb_market_daily)")
        return 0
    from .db import SupabaseWriter
    n = SupabaseWriter().upsert("sb_market_daily", rows, PK)
    print(f"upserted {n} rows into sb_market_daily (source {SOURCE})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
