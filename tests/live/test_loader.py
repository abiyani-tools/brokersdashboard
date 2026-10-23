import datetime as dt
import random

import pytest

from conftest import AS_OF, fact_rows
from src.live.loader import Facts, MissingInput, convert, load_inputs, select_volumes, volume_policy

D = dt.date


@pytest.fixture(scope="module")
def facts():
    return Facts.from_rows(fact_rows())


def test_q2_fy27_inputs(facts):
    """E2 exit test: the live loader returns the Q2 FY27 inputs from reviewed facts."""
    q = "Q2 FY 2027"
    got = {m: facts.get(m, q) for m in ("orders_fo", "orders_cash", "orders_comm", "total_income",
                                        "revmix_fo", "revmix_cash", "revmix_comm", "avg_funding_book",
                                        "share_fo_q", "share_cash_q", "share_comm_q", "trading_days_q")}
    assert got == {"orders_fo": 256, "orders_cash": 66, "orders_comm": 45, "total_income": 14315,
                   "revmix_fo": 0.387, "revmix_cash": 0.087, "revmix_comm": 0.071,
                   "avg_funding_book": 74530, "share_fo_q": pytest.approx(0.221),
                   "share_cash_q": 0.168, "share_comm_q": 0.44, "trading_days_q": 65}
    assert all(facts.fact(m, q).status == "reviewed" for m in got)
    assert facts.get("avg_funding_book", q, unit="Rs Cr") == pytest.approx(7453.0)
    # Q2 FY27 take rates, LIVE_SPEC §4: F&O 21.6403, commodity 22.5859
    assert facts.get("total_income", q) * facts.get("revmix_fo", q) / facts.get("orders_fo", q) == pytest.approx(21.6403, abs=1e-4)
    assert facts.get("total_income", q) * facts.get("revmix_comm", q) / facts.get("orders_comm", q) == pytest.approx(22.5859, abs=1e-4)


def test_reviewed_beats_seed(facts):
    assert facts.fact("orders_comm", "Q3 FY 2026").fact_id == 596          # 35, not seed 36 (J8)
    assert facts.get("avg_funding_book", "Q4 FY 2026") == 58490            # not seed 58000


def test_seed_conflicts_use_fo_market_sheet(facts):
    """Decision Q1: seed-vs-seed monthly total_orders → the F&O-market value."""
    assert facts.get("total_orders", "FY 2025 November") == 130.96
    assert facts.get("total_orders", "FY 2025 January") == 125.96
    assert facts.get("total_orders", "FY 2026 January") == 146.7
    assert [k[1] for k in facts.unresolved_conflicts()] == ["FY 2025 January", "FY 2025 November", "FY 2026 January"]
    assert ("orders_comm", "Q3 FY 2026", "") in facts.conflicts          # conflict, but decided by review
    assert ("orders_comm", "Q3 FY 2026", "") not in facts.unresolved_conflicts()


def test_seed_rule_does_not_depend_on_fact_id_order():
    rows = fact_rows()
    for r in rows:                         # give the Working-sheet rows the higher ids
        if r["source_ref"].startswith("excel:Working sheet") and r["metric"] == "total_orders":
            r["fact_id"] += 1000
    random.Random(1).shuffle(rows)
    assert Facts.from_rows(rows).get("total_orders", "FY 2025 November") == 130.96


def test_later_reviewed_fact_wins_and_rejected_is_ignored():
    rows = fact_rows()
    rows.append(dict(rows[-1], fact_id=900, value=0.02, created_at="2026-11-01T00:00:00"))   # revmix_other
    rows.append(dict(rows[-1], fact_id=901, value=0.5, status="rejected", created_at="2026-12-01T00:00:00"))
    assert Facts.from_rows(rows).fact("revmix_other", "Q2 FY 2027").fact_id == 900


def test_units(facts):
    assert convert(74530, "Rs Mn", "Rs Cr") == pytest.approx(7453)
    assert convert(79, "Rs Bn", "Rs Cr") == pytest.approx(7900)
    with pytest.raises(ValueError):
        convert(1, "Mn", "Rs Cr")
    bad = fact_rows()
    bad.append(dict(bad[-1], fact_id=999, metric="share_x", value=17.4, created_at="2026-11-01"))
    with pytest.raises(ValueError, match="outside"):
        Facts.from_rows(bad)
    with pytest.raises(MissingInput):
        facts.get("orders_fo", "Q3 FY 2027")


def test_volume_policy_per_switch(reader):
    assert volume_policy(()) == "excel_first" and volume_policy({"c", "a"}) == "best_ok"
    raw = reader.table("sb_market_daily")
    ex, best = select_volumes(raw, "excel_first"), select_volumes(raw, "best_ok")

    def at(sel, key, date):
        return next(v for v in sel[key] if v.date == date)

    # BSE F&O 1 Oct: Excel carried value (imputed) without switch c; the lake's real value with it.
    assert (at(ex, "bse_fo:contracts", D(2026, 10, 1)).value, at(ex, "bse_fo:contracts", D(2026, 10, 1)).status) == (18962859, "imputed")
    assert at(best, "bse_fo:contracts", D(2026, 10, 1)).value == 512976127
    # NSE IO 12 Oct: lake is 0/suspect, Excel ok → both policies use Excel.
    assert at(ex, "nse_fo:io_contracts", D(2026, 10, 12)).value == 181714772
    assert at(best, "nse_fo:io_contracts", D(2026, 10, 12)).value == 181714772
    # 16 Oct: no lake row at all → Excel.
    assert at(best, "nse_fo:io_contracts", D(2026, 10, 16)).source == "excel_seed"
    # Every selected series has one value per date.
    for sel in (ex, best):
        for key, series in sel.items():
            assert len({v.date for v in series}) == len(series)


def test_load_inputs_respects_as_of(reader):
    inputs = load_inputs(reader, "ANGELONE", D(2026, 9, 30), switches={"c"})
    assert max(d.date for d in inputs.calendar.days) == D(2026, 9, 30)
    assert all(v.date <= D(2026, 9, 30) for s in inputs.volumes.values() for v in s)
    assert inputs.volume_policy() == "best_ok"
