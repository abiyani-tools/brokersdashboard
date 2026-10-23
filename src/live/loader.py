"""E2 — live loader: disclosure facts by metric × period, exchange volumes by date.

Facts precedence (same as the sb_facts_current view, plus decision Q1 of LIVE_SPEC §7):
  drop 'rejected' → 'reviewed' first → seed rule (SEED_PREFERENCE) → latest created_at → highest fact_id.

Volumes: one value per (date, dataset:metric).
  policy 'excel_first' (parity inputs; live without switch c): the excel_seed row, else the lake row.
  policy 'best_ok'     (switch c): an 'ok' lake row, else an 'ok' excel_seed row, else whatever exists.
A non-ok selected value is kept, with its status, for E5 to block on; it is never replaced by 0.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Iterable, Mapping

from .periods import Calendar

# Decision Q1 (AB, 23 Oct 2026): for seed-vs-seed conflicts on monthly total_orders, use the
# F&O-market sheet until filing-extractor stages the disclosed value (which is 'reviewed' and wins).
SEED_PREFERENCE = {"total_orders": "F&O market"}

# Exchange series the ADR engine reads (E5 blocks on these) ...
ADR_MARKET_KEYS = (
    "nse_fo:contracts", "bse_fo:contracts", "nse_cash:trades", "bse_cash:trades", "mcx:contracts",
    "mtf_industry:book_cr",
)
# ... and series E5 only audits (the engine uses total NSE F&O contracts, not the index / stock option split)
AUDIT_ONLY_KEYS = ("nse_fo:io_contracts", "nse_fo:so_contracts")

MONEY = {"Rs Mn": 1e6, "Rs Bn": 1e9, "Rs Cr": 1e7}
FRACTION_UNITS = {"fraction"}
KNOWN_UNITS = set(MONEY) | FRACTION_UNITS | {"Mn", "days", "'000", "count", "p.a."}


class MissingInput(KeyError):
    pass


def convert(value: float, unit: str, to: str) -> float:
    if unit == to:
        return value
    if unit in MONEY and to in MONEY:
        return value * MONEY[unit] / MONEY[to]
    raise ValueError(f"cannot convert {unit!r} to {to!r}")


def is_lake(source: str) -> bool:
    return not source.startswith("excel_seed")


# ---------------------------------------------------------------- facts

@dataclass(frozen=True)
class Fact:
    fact_id: int
    period_type: str
    period_key: str
    metric: str
    segment: str
    value: float
    unit: str
    status: str
    source_ref: str
    created_at: str


def _fact(row: Mapping) -> Fact:
    return Fact(int(row["fact_id"]), row["period_type"], row["period_key"], row["metric"],
                row.get("segment") or "", float(row["value"]), row["unit"], row["status"],
                row.get("source_ref") or "", str(row.get("created_at") or ""))


def _rank(f: Fact) -> tuple:
    pref = SEED_PREFERENCE.get(f.metric)
    seed_pref = f.status != "reviewed" and pref is not None and pref in f.source_ref
    # sorted ascending: smaller tuple wins
    return (f.status != "reviewed", not seed_pref, _neg(f.created_at), -f.fact_id)


def _neg(ts: str) -> tuple:
    return tuple(-ord(c) for c in ts)


def select_current(rows: Iterable[Mapping]) -> dict[tuple[str, str, str], Fact]:
    groups: dict[tuple[str, str, str], list[Fact]] = {}
    for r in rows:
        f = _fact(r)
        if f.status == "rejected":
            continue
        groups.setdefault((f.metric, f.period_key, f.segment), []).append(f)
    return {k: min(v, key=_rank) for k, v in groups.items()}


@dataclass
class Facts:
    current: dict[tuple[str, str, str], Fact]
    conflicts: list[tuple[str, str, str]] = field(default_factory=list)

    @classmethod
    def from_rows(cls, rows: Iterable[Mapping]) -> "Facts":
        rows = list(rows)
        current = select_current(rows)
        values: dict[tuple, set] = {}
        for r in rows:
            if r["status"] != "rejected":
                values.setdefault((r["metric"], r["period_key"], r.get("segment") or ""), set()).add(float(r["value"]))
        conflicts = sorted(k for k, v in values.items() if len(v) > 1)
        facts = cls(current, conflicts)
        facts.check_units()
        return facts

    def fact(self, metric: str, period_key: str, segment: str = "") -> Fact:
        try:
            return self.current[(metric, period_key, segment)]
        except KeyError:
            raise MissingInput(f"no fact {metric} for {period_key}" + (f" [{segment}]" if segment else "")) from None

    def get(self, metric: str, period_key: str, unit: str | None = None, segment: str = "") -> float:
        f = self.fact(metric, period_key, segment)
        return f.value if unit is None else convert(f.value, f.unit, unit)

    def has(self, metric: str, period_key: str, segment: str = "") -> bool:
        return (metric, period_key, segment) in self.current

    def periods(self, metric: str) -> list[str]:
        return sorted({k[1] for k in self.current if k[0] == metric})

    def unresolved_conflicts(self) -> list[tuple[str, str, str]]:
        """Conflicting keys where no reviewed fact decides (value chosen by rule, not by review)."""
        return [k for k in self.conflicts if self.current[k].status != "reviewed"]

    def check_units(self) -> None:
        for f in self.current.values():
            if f.unit not in KNOWN_UNITS:
                raise ValueError(f"fact {f.fact_id} {f.metric}: unknown unit {f.unit!r}")
            if f.unit in FRACTION_UNITS and not 0 <= f.value <= 1:
                raise ValueError(f"fact {f.fact_id} {f.metric} {f.period_key}: fraction {f.value} outside [0, 1]")


# ---------------------------------------------------------------- volumes

@dataclass(frozen=True)
class Volume:
    date: dt.date
    key: str
    value: float
    status: str
    source: str

    @property
    def ok(self) -> bool:
        return self.status == "ok"


def _volume(row: Mapping) -> Volume:
    d = row["trade_date"]
    if isinstance(d, str):
        d = dt.date.fromisoformat(d)
    return Volume(d, f'{row["dataset"]}:{row["metric"]}', float(row["value"]), row["status"], row["source"])


def select_volumes(rows: Iterable[Mapping], policy: str, keys: Iterable[str] = ADR_MARKET_KEYS + AUDIT_ONLY_KEYS
                   ) -> dict[str, list[Volume]]:
    if policy not in ("excel_first", "best_ok"):
        raise ValueError(f"unknown volume policy {policy!r}")
    keys = set(keys)
    cands: dict[tuple[str, dt.date], list[Volume]] = {}
    for r in rows:
        v = r if isinstance(r, Volume) else _volume(r)
        if v.key in keys:
            cands.setdefault((v.key, v.date), []).append(v)

    def excel_first(v: Volume) -> tuple:
        return (is_lake(v.source), v.source)

    def best_ok(v: Volume) -> tuple:
        return (not v.ok, not is_lake(v.source), v.source)

    rank = excel_first if policy == "excel_first" else best_ok
    out: dict[str, list[Volume]] = {k: [] for k in keys}
    for (key, _), vs in cands.items():
        out[key].append(min(vs, key=rank))
    for k in out:
        out[k].sort(key=lambda v: v.date)
    return out


# ---------------------------------------------------------------- everything

@dataclass
class Inputs:
    calendar: Calendar
    facts: Facts
    volumes: dict[str, list[Volume]]
    raw_volumes: list[Volume]
    as_of: dt.date
    switches: frozenset[str]

    def volume_policy(self) -> str:
        return volume_policy(self.switches)


def volume_policy(switches: Iterable[str]) -> str:
    return "best_ok" if "c" in set(switches) else "excel_first"


def load_inputs(reader, broker: str, as_of: dt.date, switches: Iterable[str] = ()) -> Inputs:
    switches = frozenset(switches)
    calendar = Calendar.from_rows(r for r in reader.table("sb_calendar")
                                  if _date(r["trade_date"]) <= as_of)
    facts = Facts.from_rows(reader.table("sb_disclosure_facts", broker_id=broker))
    raw = [_volume(r) for r in reader.table("sb_market_daily") if _date(r["trade_date"]) <= as_of]
    volumes = select_volumes(raw, volume_policy(switches))
    return Inputs(calendar, facts, volumes, raw, as_of, switches)


def _date(d) -> dt.date:
    return d if isinstance(d, dt.date) else dt.date.fromisoformat(str(d)[:10])
