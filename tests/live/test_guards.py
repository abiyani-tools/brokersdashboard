import datetime as dt

import pytest

from live.guards import Insufficient, is_insufficient, mean, mean_last, ratio_change, safe_div, weekday_mean


def test_division_by_zero_is_insufficient_not_zero():
    r = safe_div(10.0, 0.0, "cash ADR")
    assert is_insufficient(r) and not r and "denominator is 0" in str(r)
    assert safe_div(10.0, 4.0, "x") == 2.5
    assert safe_div(Insufficient("a"), 4.0, "x") == Insufficient("a")
    assert safe_div(1.0, Insufficient("b"), "x") == Insufficient("b")


def test_insufficient_cannot_leak_into_arithmetic():
    with pytest.raises(TypeError):
        Insufficient("x") + 1.0


@pytest.mark.parametrize("n_values, n, ok", [(0, 45, False), (1, 45, False), (44, 45, False), (45, 45, True)])
def test_last_n_needs_the_full_window(n_values, n, ok):
    r = mean_last([1.0] * n_values, n, "last 45 days")
    assert (r == 1.0) if ok else is_insufficient(r)


def test_mean_of_nothing_and_missing_values():
    assert is_insufficient(mean([], "weekday"))
    with pytest.raises(ValueError, match="missing value"):
        mean([1.0, None], "x")
    with pytest.raises(ValueError, match="NaN"):
        mean([1.0, float("nan")], "x")


def test_weekday_mean():
    s = [(dt.date(2026, 10, 19), 10.0), (dt.date(2026, 10, 20), 99.0), (dt.date(2026, 10, 12), 20.0)]
    assert weekday_mean(s, 0, "fo") == 15.0              # Mondays
    r = weekday_mean(s, 5, "fo")                         # no Saturdays
    assert is_insufficient(r) and "Saturday" in str(r)
    assert is_insufficient(weekday_mean(s, 0, "fo", min_n=3))


def test_comparison_cells():
    assert ratio_change(110.0, 100.0, "YoY") == pytest.approx(0.10)
    assert is_insufficient(ratio_change(110.0, 0.0, "YoY"))
    assert is_insufficient(ratio_change(Insufficient("no prior year"), 100.0, "YoY"))
