"""E4 — guards for short history and zero denominators.

A guarded computation returns either a float or an Insufficient value carrying the reason.
Insufficient is falsy and not a number, so arithmetic on it fails loudly instead of yielding 0.
"""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass
from typing import Iterable, Sequence, Union


@dataclass(frozen=True)
class Insufficient:
    reason: str

    def __bool__(self) -> bool:
        return False

    def __str__(self) -> str:
        return f"insufficient data: {self.reason}"


Result = Union[float, Insufficient]


def is_insufficient(x) -> bool:
    return isinstance(x, Insufficient)


def _clean(values: Iterable[float | None], what: str) -> list[float]:
    out = []
    for v in values:
        if v is None or is_insufficient(v):
            raise ValueError(f"{what}: missing value in input; resolve it before averaging")
        if isinstance(v, float) and math.isnan(v):
            raise ValueError(f"{what}: NaN in input")
        out.append(float(v))
    return out


def safe_div(num: float | Insufficient, den: float | Insufficient, what: str) -> Result:
    if is_insufficient(num):
        return num
    if is_insufficient(den):
        return den
    if den == 0:
        return Insufficient(f"{what}: denominator is 0")
    return num / den


def mean(values: Sequence[float], what: str, min_n: int = 1) -> Result:
    vals = _clean(values, what)
    if len(vals) < max(min_n, 1):
        return Insufficient(f"{what}: {len(vals)} value(s), need {max(min_n, 1)}")
    return sum(vals) / len(vals)


def mean_last(values: Sequence[float], n: int, what: str) -> Result:
    """Mean of the last n values; Insufficient if fewer than n exist (no shortened window)."""
    if n <= 0:
        raise ValueError("n must be positive")
    vals = _clean(values, what)
    if len(vals) < n:
        return Insufficient(f"{what}: last-{n} needs {n} values, have {len(vals)}")
    return sum(vals[-n:]) / n


def weekday_mean(series: Sequence[tuple[dt.date, float]], weekday: int, what: str,
                 min_n: int = 1) -> Result:
    """Mean over dates falling on `weekday` (Monday=0)."""
    vals = [v for d, v in series if d.weekday() == weekday]
    return mean(vals, f"{what} ({dt.date(2024, 1, 1 + weekday):%A})", min_n=min_n)


def ratio_change(new: Result, old: Result, what: str) -> Result:
    """new / old − 1, guarded (comparison cells: YoY, QoQ, MoM, vs last-N)."""
    r = safe_div(new, old, what)
    return r if is_insufficient(r) else r - 1.0
