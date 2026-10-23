import datetime as dt

import pytest

from conftest import AS_OF
from src.live.guards import Insufficient
from src.live.integrity import IntegrityError, check_take_rates, run_checks, series_issues
from src.live.loader import Volume, load_inputs
from src.live.periods import Calendar

D = dt.date


@pytest.fixture(scope="module")
def without_c(reader):
    return run_checks(load_inputs(reader, "ANGELONE", AS_OF))


@pytest.fixture(scope="module")
def with_c(reader):
    return run_checks(load_inputs(reader, "ANGELONE", AS_OF, switches={"c"}))


def _dates(issue):
    return (issue.dates[0], issue.dates[-1], len(issue.dates))


def test_frozen_bse_blocks_without_switch_c(without_c):
    assert without_c.blocking
    keys = {(i.check, i.key) for i in without_c.errors}
    assert keys == {("frozen", "bse_fo:contracts"), ("status", "bse_fo:contracts")}
    frozen = without_c.find("frozen", "bse_fo:contracts", "error")[0]
    assert _dates(frozen) == (D(2026, 9, 28), D(2026, 10, 21), 16)
    with pytest.raises(IntegrityError):
        without_c.raise_if_blocking()


def test_with_switch_c_nothing_blocks(with_c):
    assert not with_c.blocking, with_c.summary()


@pytest.mark.parametrize("check, key, source, first, last, n", [
    ("zero", "bse_cash:trades", "exchangesdash_json@b2049b5", D(2026, 6, 15), D(2026, 6, 15), 1),
    ("zero", "nse_fo:io_contracts", "exchangesdash_json@b2049b5", D(2026, 10, 12), D(2026, 10, 15), 4),
    ("zero", "nse_fo:so_contracts", "exchangesdash_json@b2049b5", D(2026, 10, 12), D(2026, 10, 15), 4),
    ("zero", "mcx:contracts", "octo_mcx@2026-10-22", D(2026, 5, 27), D(2026, 5, 28), 2),
    ("frozen", "bse_fo:contracts", "excel_seed", D(2026, 9, 28), D(2026, 10, 21), 16),
    ("missing", "nse_fo:io_contracts", "exchangesdash_json@b2049b5", D(2026, 10, 16), D(2026, 10, 21), 3),
])
def test_known_lake_gaps_are_caught(with_c, without_c, check, key, source, first, last, n):
    """E5 exit test: the known gaps (LIVE_SPEC §3) are reported, with or without switch c."""
    for report in (with_c, without_c):
        hits = report.find(check, key, "info", source)
        assert hits and _dates(hits[0]) == (first, last, n)


def test_no_false_jumps_on_six_months_of_real_data(with_c, without_c):
    assert not with_c.find("jump") and not without_c.find("jump")


def test_mtf_gap_is_a_warning_and_tail_lag_is_allowed(with_c):
    w = with_c.find("missing", "mtf_industry:book_cr", "warning")
    assert len(w) == 1 and w[0].dates == (D(2026, 4, 8),)          # 20, 21 Oct inside the lag


def test_seed_conflicts_are_warnings(with_c):
    assert len(with_c.find("conflict", severity="warning")) == 3


# ---- synthetic series

def _cal(n=30):
    start = D(2026, 6, 1)
    days = [start + dt.timedelta(i) for i in range(60) if (start + dt.timedelta(i)).weekday() < 5][:n]
    return Calendar.from_rows({"trade_date": d.isoformat(), "is_equity_day": True, "is_mcx_day": True}
                              for d in days), days


def _series(days, values, key="nse_cash:trades"):
    return [Volume(d, key, float(v), "ok", "x") for d, v in zip(days, values)]


def _checks(series, cal, days):
    return {i.check for i in series_issues("nse_cash:trades", series, cal, days[-1], "error")}


def test_unit_error_jumps_are_caught():
    cal, days = _cal()
    base = [100 + (i % 7) for i in range(30)]
    assert _checks(_series(days, base), cal, days) == set()
    up = base[:25] + [base[25] * 100] + base[26:]
    down = base[:25] + [base[25] / 1000] + base[26:]
    assert "jump" in _checks(_series(days, up), cal, days)
    assert "jump" in _checks(_series(days, down), cal, days)


def test_frozen_needs_three_equal_days():
    cal, days = _cal()
    base = [100 + (i % 7) for i in range(30)]
    two = base[:10] + [500, 500] + base[12:]
    three = base[:10] + [100, 100, 100] + base[13:]
    assert "frozen" not in _checks(_series(days, two), cal, days)
    assert "frozen" in _checks(_series(days, three), cal, days)


def test_missing_day_blocks():
    cal, days = _cal()
    s = _series(days, [100 + (i % 7) for i in range(30)])
    del s[12]
    issues = series_issues("nse_cash:trades", s, cal, days[-1], "error")
    assert [(i.check, i.severity, i.dates) for i in issues] == [("missing", "error", (days[12],))]


def test_take_rate_unit_sanity():
    issues = check_take_rates({("fo", "Q2 FY 2027"): 21.6403, ("fo", "Q3 FY 2027"): 2164.03,
                               ("cash", "Q3 FY 2027"): Insufficient("no orders")})
    assert {i.key for i in issues} == {"take_rate fo Q3 FY 2027", "take_rate cash Q3 FY 2027"}
    assert all(i.severity == "error" for i in issues)
