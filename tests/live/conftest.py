import datetime as dt
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

FIX = Path(__file__).parent / "fixtures"
MARKET = FIX / "market_2026-04-01_2026-10-21.json"
FACTS = FIX / "facts_subset.json"
AS_OF = dt.date(2026, 10, 21)


def _entries(s: str, year: int = 2026):
    for tok in s.split():
        mmdd, val = tok.split("=")
        d = dt.date(year, int(mmdd[:2]), int(mmdd[2:]))
        if val == "-":
            yield d, None, None
            continue
        value, _, status = val.partition("!")
        yield d, float(value), status or "ok"


def calendar_rows(spec: str):
    rows = []
    for tok in spec.split():
        d = dt.date(int(tok[:4]), int(tok[4:6]), int(tok[6:8]))
        flags, _, special = tok[8:].partition("/")
        rows.append({"trade_date": d.isoformat(), "is_equity_day": "E" in flags,
                     "is_mcx_day": "M" in flags, "special_session": special or None})
    return rows


def market_rows(data: dict):
    rows = []
    for key, s in data["series"].items():
        dataset, metric = key.split(":")
        base = {d: (v, st) for d, v, st in _entries(s["base"])}
        for source in s["sources"]:
            vals = dict(base)
            for d, v, st in _entries(s["overrides"].get(source, "")):
                if v is None:
                    vals.pop(d, None)
                else:
                    vals[d] = (v, st)
            for d, (v, st) in vals.items():
                rows.append({"trade_date": d.isoformat(), "dataset": dataset, "metric": metric,
                             "source": source, "value": v, "status": st})
    return rows


def fact_rows():
    data = json.loads(FACTS.read_text())
    cols = data["columns"]
    return [dict(zip(cols, r), broker_id="ANGELONE") for r in data["rows"]]


class FixtureReader:
    """Same interface as live.db readers, built from the fixture files."""

    def __init__(self):
        self.market = json.loads(MARKET.read_text())
        self.tables = {
            "sb_calendar": calendar_rows(self.market["calendar"]),
            "sb_market_daily": market_rows(self.market),
            "sb_disclosure_facts": fact_rows(),
        }

    def table(self, name, **eq):
        return [r for r in self.tables[name] if all(str(r.get(k)) == str(v) for k, v in eq.items())]


@pytest.fixture(scope="session")
def reader():
    return FixtureReader()
