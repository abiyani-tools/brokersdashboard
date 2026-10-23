"""E5 — integrity checks before every live run.

Two layers:
  check_selected  the series the engine will use (after source selection). Issues here are
                  'error' (blocks publishing) unless the input's rule says 'warning'.
  audit_sources   every source on its own. Always 'info': it keeps lake gaps visible even when
                  the other source covers the day, so they can be fixed upstream.

Checks: missing trading day, non-ok status, zero on a trading day, frozen series
(≥ FROZEN_RUN equal non-zero values in a row), jump (above JUMP_UP × the trailing max or below
JUMP_DOWN × the trailing min of the last JUMP_WINDOW non-zero values). The trailing max/min,
not the median, is used because expiry days run 15–20× a normal day.
A value on a day sb_calendar marks closed for the series is reported as 'closed' (info) and left out of
the jump test.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Iterable

from .guards import Insufficient, is_insufficient
from .loader import ADR_MARKET_KEYS, Facts, Inputs, Volume
from .periods import Calendar

FROZEN_RUN = 3
JUMP_UP, JUMP_DOWN = 5.0, 0.2
JUMP_WINDOW, JUMP_MIN_HISTORY = 20, 10
TAKE_RATE_RANGE = (5.0, 60.0)   # Rs per order


@dataclass(frozen=True)
class Rule:
    days: str = "equity"          # which calendar days the series must cover: 'equity' or 'mcx'
    tail_lag: int = 0             # trading days at the end of the window allowed to be missing
    missing: str = "error"        # severity of a missing day


RULES: dict[str, Rule] = {
    "mcx:contracts": Rule(days="mcx"),
    # NSE publishes the industry MTF book with a lag and skips some days (e.g. 8 Apr 2026);
    # the quarterly industry average is taken over the days reported, so a gap is a warning.
    "mtf_industry:book_cr": Rule(tail_lag=3, missing="warning"),
}

# Reviewed exceptions: (check, key, date) -> reason. A matching issue is reported as 'info' with the reason,
# never dropped. Add an entry only after the day has been looked at; say what is and is not known.
KNOWN_ISSUES = {
    ("jump", "mcx:contracts", "2025-01-01"):
        "406,749 contracts against a trailing 20-day minimum of 2,205,346: New Year's Day, MCX traded the "
        "morning session only (evening session from 5 pm closed; Zerodha bulletin 31 Dec 2024). Genuine thin "
        "day, not a data error; not marked special in sb_calendar, so it stays in the commodity averages",
}


@dataclass(frozen=True)
class Issue:
    check: str
    key: str
    severity: str                 # 'error' | 'warning' | 'info'
    dates: tuple[dt.date, ...]
    detail: str
    source: str = ""

    def __str__(self) -> str:
        if not self.dates:
            span = "-"
        elif len(self.dates) == 1:
            span = self.dates[0].isoformat()
        else:
            span = f"{self.dates[0].isoformat()}..{self.dates[-1].isoformat()} ({len(self.dates)} days)"
        src = f" [{self.source}]" if self.source else ""
        return f"{self.severity.upper():7} {self.check:8} {self.key}{src} {span}: {self.detail}"


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def blocking(self) -> bool:
        return bool(self.errors)

    def find(self, check: str | None = None, key: str | None = None, severity: str | None = None,
             source: str | None = None) -> list[Issue]:
        return [i for i in self.issues
                if (check is None or i.check == check) and (key is None or i.key == key)
                and (severity is None or i.severity == severity) and (source is None or i.source == source)]

    def summary(self) -> str:
        head = f"E5: {len(self.errors)} blocking, {len(self.find(severity='warning'))} warning, " \
               f"{len(self.find(severity='info'))} info"
        return "\n".join([head] + [str(i) for i in self.issues])

    def raise_if_blocking(self) -> None:
        if self.blocking:
            raise IntegrityError(self)


class IntegrityError(RuntimeError):
    def __init__(self, report: Report):
        self.report = report
        super().__init__(report.summary())


def series_issues(key: str, series: list[Volume], calendar: Calendar, as_of: dt.date,
                  severity: str, source: str = "") -> list[Issue]:
    """Issues for one series. Special sessions (sb_calendar.special_session) are thin by design and are
    not tested for jumps, nor used as the jump baseline."""
    rule = RULES.get(key, Rule())
    out: list[Issue] = []
    by_date = {v.date: v for v in series}

    # missing trading days
    expected = [d.date for d in calendar.trading_days(rule.days, until=as_of)]
    if expected and series:
        first = min(by_date)
        expected = [d for d in expected if d >= first]       # series history starts at its first row
    cutoff = len(expected) - rule.tail_lag
    missing = [d for i, d in enumerate(expected) if d not in by_date and i < cutoff]
    if missing:
        sev = severity if severity == "info" else rule.missing
        out.append(Issue("missing", key, sev, tuple(missing), "no value on a trading day", source))

    ordered = [v for v in sorted(series, key=lambda v: v.date) if v.date <= as_of]

    nonok = [v.date for v in ordered if v.status != "ok"]
    if nonok:
        statuses = sorted({v.status for v in ordered if v.status != "ok"})
        out.append(Issue("status", key, severity, tuple(nonok), "status " + "/".join(statuses), source))

    zeros = [v.date for v in ordered if v.value == 0]
    if zeros:
        out.append(Issue("zero", key, severity, tuple(zeros), "zero on a trading day", source))

    # frozen: runs of equal non-zero values
    run: list[Volume] = []
    for v in ordered + [None]:
        if v is not None and run and v.value == run[-1].value and v.value != 0:
            run.append(v)
            continue
        if len(run) >= FROZEN_RUN:
            out.append(Issue("frozen", key, severity, tuple(x.date for x in run),
                             f"{run[0].value:,.0f} repeated {len(run)} days", source))
        run = [v] if v is not None else []

    # values on days the calendar marks closed for this series (e.g. MCX on 1 Jan 2024): the engine does
    # not average them, so they are reported as info and kept out of the jump test and its baseline
    open_days = {d.date for d in calendar.trading_days(rule.days)}
    closed = [v.date for v in ordered if v.date in calendar and v.date not in open_days]
    if closed:
        out.append(Issue("closed", key, "info", tuple(closed),
                         f"value on a day sb_calendar marks closed for {rule.days}", source))

    # jumps against the trailing non-zero range
    hist: list[float] = []
    jumps = []
    special = {d.date for d in calendar.days if d.special}
    skip = special | set(closed)
    for v in ordered:
        if v.value == 0 or v.date in skip:
            continue
        window = hist[-JUMP_WINDOW:]
        if len(window) >= JUMP_MIN_HISTORY:
            hi, lo = max(window), min(window)
            if v.value > JUMP_UP * hi or v.value < JUMP_DOWN * lo:
                jumps.append((v.date, v.value, lo, hi))
        hist.append(v.value)
    for d, val, lo, hi in jumps:
        out.append(Issue("jump", key, severity, (d,),
                         f"{val:,.0f} outside {JUMP_DOWN}×{lo:,.0f} .. {JUMP_UP}×{hi:,.0f}", source))
    return out


def check_selected(inputs: Inputs) -> list[Issue]:
    """Blocking checks on the series the engine reads; a series with no rows at all is an error."""
    out = []
    for key in ADR_MARKET_KEYS:
        series = inputs.volumes.get(key, [])
        if not series:
            out.append(Issue("missing", key, "error", (), "no rows at all for an input the engine reads"))
            continue
        out += series_issues(key, series, inputs.calendar, inputs.as_of, "error")
    return [_known(i) for i in out]


def _known(issue: Issue) -> Issue:
    if len(issue.dates) == 1:
        why = KNOWN_ISSUES.get((issue.check, issue.key, issue.dates[0].isoformat()))
        if why:
            return Issue(issue.check, issue.key, "info", issue.dates, f"{issue.detail} — known: {why}", issue.source)
    return issue


def audit_sources(inputs: Inputs) -> list[Issue]:
    by_src: dict[tuple[str, str], list[Volume]] = {}
    for v in inputs.raw_volumes:
        if v.key in inputs.volumes:
            by_src.setdefault((v.key, v.source), []).append(v)
    out = []
    for (key, source), series in sorted(by_src.items()):
        out += series_issues(key, series, inputs.calendar, inputs.as_of, "info", source)
    return out


def check_facts(facts: Facts) -> list[Issue]:
    out = []
    for metric, period, segment in facts.unresolved_conflicts():
        f = facts.fact(metric, period, segment)
        out.append(Issue("conflict", f"{metric} {period}", "warning", (),
                         f"seed values disagree; using fact {f.fact_id} ({f.source_ref}) by rule"))
    return out


def check_take_rates(rates: dict[tuple[str, str], float | Insufficient]) -> list[Issue]:
    """rates: {(segment, period_key): Rs per order}. Out-of-range or insufficient → error."""
    lo, hi = TAKE_RATE_RANGE
    out = []
    for (segment, period), r in sorted(rates.items()):
        if is_insufficient(r):
            out.append(Issue("unit", f"take_rate {segment} {period}", "error", (), str(r)))
        elif not lo <= r <= hi:
            out.append(Issue("unit", f"take_rate {segment} {period}", "error", (),
                             f"{r:.4f} Rs/order outside {lo}..{hi} (unit error?)"))
    return out


def run_checks(inputs: Inputs, take_rates: dict | None = None) -> Report:
    issues = check_selected(inputs) + check_facts(inputs.facts) + audit_sources(inputs)
    if take_rates:
        issues += check_take_rates(take_rates)
    return Report(issues)
