import datetime as dt

from src.live.freshness import ANGEL_KEYS, MOSL_KEYS, assess, lake_ends


def _rows(through, mcx_through):
    out = []
    for k in set(ANGEL_KEYS) | set(MOSL_KEYS):
        ds, m = k.split(":")
        out.append(dict(trade_date=mcx_through if k == "mcx:contracts" else through, dataset=ds, metric=m,
                        value=1.0, status="ok"))
    return out


def _runs(as_of):
    return [dict(broker_id=b, status="success", mode="live", as_of_date=as_of) for b in ("ANGELONE", "GROWW", "MOSL")]


NSE = ["2026-11-05", "2026-11-06", "2026-11-09"]
TUE = dt.date(2026, 11, 10)


def test_ok_when_published_through_target():
    a = assess(_runs("2026-11-09"), lake_ends(_rows("2026-11-09", "2026-11-09")), NSE, TUE)
    assert a["target"] == "2026-11-09" and all(r["status"] == "ok" for r in a["brokers"].values())


def test_upstream_mcx_lag_is_named():
    a = assess(_runs("2026-11-06"), lake_ends(_rows("2026-11-09", "2026-11-06")), NSE, TUE)
    assert a["brokers"]["ANGELONE"]["cause"] == "upstream: mcx:contracts through 2026-11-06"


def test_pipeline_fault_when_lake_complete():
    a = assess(_runs("2026-11-06"), lake_ends(_rows("2026-11-09", "2026-11-09")), NSE, TUE)
    assert a["brokers"]["MOSL"]["cause"].startswith("pipeline:")


def test_failed_runs_and_zeros_do_not_count():
    runs = _runs("2026-11-06") + [dict(broker_id="GROWW", status="failed", mode="live", as_of_date="2026-11-09")]
    rows = _rows("2026-11-09", "2026-11-09") + [dict(trade_date="2026-11-10", dataset="mcx", metric="contracts",
                                                     value=0.0, status="ok")]
    a = assess(runs, lake_ends(rows), NSE, TUE)
    assert a["brokers"]["GROWW"]["status"] == "behind"
    assert lake_ends(rows)["mcx:contracts"] == "2026-11-09"


def test_monday_targets_friday_and_flags_missing_nse():
    a = assess(_runs("2026-11-06"), lake_ends(_rows("2026-11-06", "2026-11-06")), NSE[:2], TUE)
    assert a["target"] == "2026-11-06" and a["nse_note"]          # 9 Nov missing: holiday or late
    assert assess(_runs("2026-11-06"), {}, NSE, dt.date(2026, 11, 9))["nse_note"] is None
