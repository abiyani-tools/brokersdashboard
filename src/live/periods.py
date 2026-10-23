"""E1 — period ranges derived from sb_calendar.

Labels follow sb_calendar: fy "FY 2027", q_fy "Q1 FY 2027", fy_month "FY 2027 April".
A calendar day whose period has no calibration raises MissingCalibration; it is never dropped.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Iterable, Mapping

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
KINDS = ("FY", "Q", "M")


class MissingCalibration(Exception):
    """A period has trading days up to as_of but no calibration inputs."""

    def __init__(self, periods: list[str]):
        self.periods = periods
        super().__init__("no calibration for period(s) with trading days: " + ", ".join(periods))


def fy_labels(d: dt.date) -> dict[str, str]:
    """Indian financial year labels (April–March), in sb_calendar's format."""
    fy = d.year + 1 if d.month >= 4 else d.year
    q = (d.month - 4) % 12 // 3 + 1
    return {"FY": f"FY {fy}", "Q": f"Q{q} FY {fy}", "M": f"FY {fy} {MONTHS[d.month - 1]}"}


@dataclass(frozen=True)
class Day:
    date: dt.date
    equity: bool
    mcx: bool
    special: str | None = None   # 'muhurat', 'dr_test' or None
    labels: Mapping[str, str] = field(default_factory=dict)

    def label(self, kind: str) -> str:
        return self.labels[kind]


@dataclass(frozen=True)
class Period:
    kind: str
    key: str
    start: dt.date
    end: dt.date
    days: tuple[Day, ...]

    @property
    def equity_days(self) -> list[Day]:
        return [d for d in self.days if d.equity]

    @property
    def mcx_days(self) -> list[Day]:
        return [d for d in self.days if d.mcx]


class Calendar:
    def __init__(self, days: Iterable[Day]):
        self.days = sorted(days, key=lambda d: d.date)
        seen = set()
        for d in self.days:
            if d.date in seen:
                raise ValueError(f"duplicate calendar date {d.date}")
            seen.add(d.date)
        self._by_date = {d.date: d for d in self.days}

    @classmethod
    def from_rows(cls, rows: Iterable[Mapping]) -> "Calendar":
        """Rows as in sb_calendar. Labels in the rows must agree with the April–March rule."""
        days = []
        for r in rows:
            date = r["trade_date"]
            if isinstance(date, str):
                date = dt.date.fromisoformat(date)
            expected = fy_labels(date)
            given = {"FY": r.get("fy"), "Q": r.get("q_fy"), "M": r.get("fy_month")}
            for kind, value in given.items():
                if value is not None and value != expected[kind]:
                    raise ValueError(f"sb_calendar {date}: {kind} label {value!r}, expected {expected[kind]!r}")
            days.append(Day(date, bool(r["is_equity_day"]), bool(r["is_mcx_day"]),
                            r.get("special_session") or None, expected))
        return cls(days)

    def __contains__(self, date: dt.date) -> bool:
        return date in self._by_date

    def day(self, date: dt.date) -> Day:
        return self._by_date[date]

    def trading_days(self, kind: str = "equity", until: dt.date | None = None) -> list[Day]:
        attr = {"equity": "equity", "mcx": "mcx"}[kind]
        return [d for d in self.days if getattr(d, attr) and (until is None or d.date <= until)]

    def periods(self, kind: str, until: dt.date | None = None) -> dict[str, Period]:
        """All periods of one kind ('FY', 'Q', 'M') that have calendar days, in date order."""
        if kind not in KINDS:
            raise ValueError(f"kind must be one of {KINDS}")
        groups: dict[str, list[Day]] = {}
        for d in self.days:
            if until is not None and d.date > until:
                continue
            groups.setdefault(d.label(kind), []).append(d)
        return {k: Period(kind, k, v[0].date, v[-1].date, tuple(v)) for k, v in groups.items()}

    def period_of(self, date: dt.date, kind: str) -> str:
        return self.day(date).label(kind)


def require_calibration(calendar: Calendar, calibrated: Iterable[tuple[str, str]], as_of: dt.date,
                        kinds: Iterable[str] = ("Q", "M")) -> None:
    """Raise MissingCalibration for every period with a trading day up to as_of that is not calibrated.

    `calibrated` holds (kind, period_key) pairs the engine has inputs for, actual or projected.
    """
    have = set(calibrated)
    missing = [key for kind in kinds for key, p in calendar.periods(kind, until=as_of).items()
               if (p.equity_days or p.mcx_days) and (kind, key) not in have]
    if missing:
        raise MissingCalibration(missing)
