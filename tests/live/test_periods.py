import datetime as dt

import pytest

from conftest import AS_OF
from live.loader import Facts, load_inputs
from live.periods import Calendar, MissingCalibration, fy_labels, require_calibration

D = dt.date


@pytest.mark.parametrize("date, fy, q, m", [
    (D(2026, 3, 31), "FY 2026", "Q4 FY 2026", "FY 2026 March"),
    (D(2026, 4, 1), "FY 2027", "Q1 FY 2027", "FY 2027 April"),
    (D(2026, 10, 21), "FY 2027", "Q3 FY 2027", "FY 2027 October"),   # as in sb_calendar
    (D(2025, 10, 21), "FY 2026", "Q3 FY 2026", "FY 2026 October"),
    (D(2027, 1, 4), "FY 2027", "Q4 FY 2027", "FY 2027 January"),
])
def test_labels_match_sb_calendar(date, fy, q, m):
    assert fy_labels(date) == {"FY": fy, "Q": q, "M": m}


def test_calendar_rejects_wrong_label_and_duplicates():
    row = {"trade_date": "2026-04-01", "is_equity_day": True, "is_mcx_day": True}
    with pytest.raises(ValueError, match="expected 'Q1 FY 2027'"):
        Calendar.from_rows([dict(row, q_fy="Q4 FY 2026")])
    with pytest.raises(ValueError, match="duplicate"):
        Calendar.from_rows([row, row])


def test_quarter_ranges_and_trading_days_agree_with_disclosures(reader):
    inputs = load_inputs(reader, "ANGELONE", AS_OF)
    q = inputs.calendar.periods("Q")
    assert (q["Q2 FY 2027"].start, q["Q2 FY 2027"].end) == (D(2026, 7, 1), D(2026, 9, 30))
    # Angel One's own count of trading days for Q2 FY27 (fact 563) equals the calendar's equity days.
    assert len(q["Q2 FY 2027"].equity_days) == inputs.facts.get("trading_days_q", "Q2 FY 2027") == 65
    m = inputs.calendar.periods("M")
    assert list(m)[-1] == "FY 2027 October"
    assert m["FY 2027 October"].end == AS_OF
    assert len(m["FY 2027 October"].mcx_days) == len(m["FY 2027 October"].equity_days) + 1  # 20 Oct MCX only


def _calibrated(cal: Calendar):
    return {(k, key) for k in ("Q", "M") for key in cal.periods(k)}


def test_new_month_without_calibration_fails_loudly(reader):
    """E1 exit test: November exists in the calendar, no inputs for it → the run fails, naming it."""
    rows = reader.table("sb_calendar") + [
        {"trade_date": "2026-11-02", "is_equity_day": True, "is_mcx_day": True, "special_session": None}]
    cal = Calendar.from_rows(rows)
    calibrated = _calibrated(Calendar.from_rows(reader.table("sb_calendar")))   # up to October only
    as_of = D(2026, 11, 2)
    with pytest.raises(MissingCalibration) as e:
        require_calibration(cal, calibrated, as_of)
    assert e.value.periods == ["FY 2027 November"]          # Q3 FY27 is calibrated; the month is not
    require_calibration(cal, calibrated | {("M", "FY 2027 November")}, as_of)
    require_calibration(cal, calibrated, AS_OF)              # before November: nothing missing
