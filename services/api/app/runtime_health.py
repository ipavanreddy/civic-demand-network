"""Last-call outcome per integration, so the demo badge reflects what actually happened at runtime
(a configured key that is failing shows as "fallback", not "real")."""
from __future__ import annotations

from datetime import UTC, datetime
from threading import Lock

_lock = Lock()
_last: dict[str, dict] = {}


def record(name: str, ok: bool, error: object | None = None) -> None:
    with _lock:
        _last[name] = {"ok": ok, "at": datetime.now(UTC).isoformat(timespec="seconds"),
                       "error": None if ok else str(error)[:200]}


def last(name: str) -> dict | None:
    with _lock:
        return _last.get(name)


def reset() -> None:
    with _lock:
        _last.clear()
