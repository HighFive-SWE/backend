import time

import pytest

from core.idempotency import IdempotencyCache


@pytest.fixture
def cache():
    return IdempotencyCache(ttl_seconds=60, max_entries=100)


# ── constructor validation ────────────────────────────────────────────────────

def test_negative_ttl_raises():
    with pytest.raises(ValueError):
        IdempotencyCache(ttl_seconds=-1)


def test_zero_ttl_raises():
    with pytest.raises(ValueError):
        IdempotencyCache(ttl_seconds=0)


def test_zero_max_entries_raises():
    with pytest.raises(ValueError):
        IdempotencyCache(ttl_seconds=10, max_entries=0)


# ── basic get / set ───────────────────────────────────────────────────────────

def test_get_missing_key_returns_none(cache):
    assert cache.get("missing") is None


def test_set_and_get_round_trip(cache):
    cache.set("k", "value")
    assert cache.get("k") == "value"


def test_set_overwrites_existing(cache):
    cache.set("k", "first")
    cache.set("k", "second")
    assert cache.get("k") == "second"


def test_len_reflects_stored_entries(cache):
    cache.set("a", 1)
    cache.set("b", 2)
    assert len(cache) == 2


# ── TTL expiry ────────────────────────────────────────────────────────────────

def test_expired_entry_returns_none():
    c = IdempotencyCache(ttl_seconds=1)
    c.set("k", "val")
    time.sleep(1.05)
    assert c.get("k") is None


def test_expired_entry_removed_from_store():
    c = IdempotencyCache(ttl_seconds=1)
    c.set("k", "val")
    time.sleep(1.05)
    c.get("k")
    assert len(c) == 0


# ── max_entries eviction ──────────────────────────────────────────────────────

def test_max_entries_evicts_oldest():
    c = IdempotencyCache(ttl_seconds=60, max_entries=3)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    c.set("d", 4)
    assert len(c) == 3
    assert c.get("a") is None


def test_max_entries_keeps_newest():
    c = IdempotencyCache(ttl_seconds=60, max_entries=3)
    for i in range(5):
        c.set(str(i), i)
    assert c.get("4") == 4


def test_max_entries_exactly_at_limit_no_eviction():
    c = IdempotencyCache(ttl_seconds=60, max_entries=3)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    assert len(c) == 3
    assert c.get("a") is not None
