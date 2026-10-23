"""E6 — readers. Both expose `table(name, **eq_filters) -> list[dict]`.

SnapshotReader reads snapshot/db_snapshot_*.json ({"tables": {name: [rows]}} or {name: [rows]}).
SupabaseReader reads PostgREST with the service key from the environment. The key is never
accepted as an argument, never stored on the instance in printable form, and never logged.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable

DEFAULT_URL = "https://everjfpbnlbcpuarnhob.supabase.co"
KEY_ENV = "SUPABASE_SERVICE_KEY"
URL_ENV = "SUPABASE_URL"
PAGE = 1000


class MissingCredentials(RuntimeError):
    pass


class SnapshotReader:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        data = json.loads(self.path.read_text())
        self._tables = data.get("tables", data)

    def table(self, name: str, **eq) -> list[dict]:
        if name not in self._tables:
            raise KeyError(f"{name} not in snapshot {self.path.name}")
        rows = self._tables[name]
        return [r for r in rows if all(str(r.get(k)) == str(v) for k, v in eq.items())]


class SupabaseReader:
    def __init__(self, url: str | None = None, session=None, page_size: int = PAGE):
        key = os.environ.get(KEY_ENV)
        if not key:
            raise MissingCredentials(f"{KEY_ENV} is not set; the live DB reader needs the service key")
        self.url = (url or os.environ.get(URL_ENV) or DEFAULT_URL).rstrip("/")
        self.page_size = page_size
        if session is None:
            import requests
            session = requests.Session()
        self._session = session
        self._headers: Callable[[], dict] = lambda: {
            "apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json"}

    def __repr__(self) -> str:
        return f"SupabaseReader(url={self.url!r})"

    def table(self, name: str, **eq) -> list[dict]:
        params = {"select": "*"}
        params.update({k: f"eq.{v}" for k, v in eq.items()})
        rows: list[dict] = []
        start = 0
        while True:
            headers = self._headers()
            headers["Range-Unit"] = "items"
            headers["Range"] = f"{start}-{start + self.page_size - 1}"
            resp = self._session.get(f"{self.url}/rest/v1/{name}", params=params, headers=headers, timeout=60)
            if resp.status_code not in (200, 206):
                # Body only; headers carry the key and are never echoed.
                raise RuntimeError(f"GET {name} failed: HTTP {resp.status_code} {resp.text[:200]}")
            page = resp.json()
            rows.extend(page)
            if len(page) < self.page_size:
                return rows
            start += self.page_size


def reader_from_env(snapshot: str | Path | None = None):
    """Snapshot if a path is given (tests, local runs), else the DB (CI / daily job)."""
    return SnapshotReader(snapshot) if snapshot else SupabaseReader()
