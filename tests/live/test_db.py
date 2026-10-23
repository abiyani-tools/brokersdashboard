import json
import os

import pytest

from live.db import KEY_ENV, MissingCredentials, SnapshotReader, SupabaseReader, reader_from_env

SECRET = "sb_secret_TEST_ONLY_not_a_real_key"


class FakeResponse:
    def __init__(self, rows, status=200):
        self._rows, self.status_code, self.text = rows, status, json.dumps(rows)[:50]

    def json(self):
        return self._rows


class FakeSession:
    def __init__(self, rows, status=200):
        self.rows, self.status, self.calls = rows, status, []

    def get(self, url, params, headers, timeout):
        self.calls.append((url, dict(params), dict(headers)))
        lo, hi = map(int, headers["Range"].split("-"))
        return FakeResponse(self.rows[lo:hi + 1], self.status)


def test_snapshot_reader(tmp_path):
    p = tmp_path / "db_snapshot_test.json"
    p.write_text(json.dumps({"tables": {"sb_runs": [{"run_id": "a", "mode": "parity"}, {"run_id": "b", "mode": "live"}]}}))
    r = SnapshotReader(p)
    assert [x["run_id"] for x in r.table("sb_runs", mode="live")] == ["b"]
    with pytest.raises(KeyError):
        r.table("sb_missing")
    assert isinstance(reader_from_env(p), SnapshotReader)


def test_db_reader_needs_the_key_from_the_environment(monkeypatch):
    monkeypatch.delenv(KEY_ENV, raising=False)
    with pytest.raises(MissingCredentials):
        SupabaseReader(session=FakeSession([]))


def test_db_reader_paginates_and_never_exposes_the_key(monkeypatch):
    monkeypatch.setenv(KEY_ENV, SECRET)
    rows = [{"i": i} for i in range(5)]
    s = FakeSession(rows)
    r = SupabaseReader(session=s, page_size=2)
    assert r.table("sb_calendar", is_equity_day="true") == rows
    assert len(s.calls) == 3
    url, params, headers = s.calls[0]
    assert url.endswith("/rest/v1/sb_calendar") and params["is_equity_day"] == "eq.true"
    assert headers["apikey"] == SECRET
    assert SECRET not in repr(r) and SECRET not in str(vars(r))


def test_db_reader_error_does_not_echo_headers(monkeypatch):
    monkeypatch.setenv(KEY_ENV, SECRET)
    r = SupabaseReader(session=FakeSession([{"message": "permission denied"}], status=401))
    with pytest.raises(RuntimeError) as e:
        r.table("sb_market_daily")
    assert "401" in str(e.value) and SECRET not in str(e.value)


@pytest.mark.skipif(not (os.environ.get(KEY_ENV) and os.environ.get("BROKERS_SNAPSHOT")),
                    reason="needs SUPABASE_SERVICE_KEY and BROKERS_SNAPSHOT (a snapshot taken the same minute)")
def test_db_equals_snapshot():
    """E6 exit test (CI): a DB read equals the snapshot taken the same minute."""
    db, snap = SupabaseReader(), SnapshotReader(os.environ["BROKERS_SNAPSHOT"])
    for name in ("sb_calendar", "sb_disclosure_facts", "sb_market_daily", "sb_assumptions"):
        key = lambda r: json.dumps(r, sort_keys=True, default=str)
        assert sorted(map(key, db.table(name))) == sorted(map(key, snap.table(name))), name
