from __future__ import annotations

import time
from collections import OrderedDict
from typing import Generic, TypeVar

T = TypeVar("T")


class IdempotencyCache(Generic[T]):
    """
    bounded ttl cache keyed by a client-supplied idempotency token. used to
    dedupe POST replays — when the offline progress queue (or an httpJson
    retry) re-sends a payload that the server already committed, the second
    call must return the original response instead of running the side
    effect twice.

    not thread-safe by design. fastapi serves requests on the asyncio loop
    and the controller methods that use this are sync, so concurrent
    mutation isn't possible until the api moves to a worker pool. when that
    happens, wrap the two read-modify-write paths (`get` and `set`) in a
    lock — the rest of the surface stays the same.
    """

    def __init__(self, *, ttl_seconds: int, max_entries: int = 5000) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        if max_entries <= 0:
            raise ValueError("max_entries must be positive")
        self._ttl = ttl_seconds
        self._max = max_entries
        # ordered so eviction is "oldest insertion / least-recently touched
        # first" without a separate lru list.
        self._store: "OrderedDict[str, tuple[float, T]]" = OrderedDict()

    def get(self, key: str) -> T | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if expires_at <= time.monotonic():
            del self._store[key]
            return None
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: T) -> None:
        now = time.monotonic()
        # cheap amortised prune — drop anything that's already expired so the
        # store doesn't grow toward `max` faster than necessary.
        expired = [k for k, (exp, _) in self._store.items() if exp <= now]
        for k in expired:
            del self._store[k]
        self._store[key] = (now + self._ttl, value)
        self._store.move_to_end(key)
        # hard cap: oldest-first eviction once we're over budget. this is the
        # safety net; the ttl prune above is the usual reaper.
        while len(self._store) > self._max:
            self._store.popitem(last=False)

    def __len__(self) -> int:
        return len(self._store)
