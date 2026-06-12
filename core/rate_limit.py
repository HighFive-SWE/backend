from __future__ import annotations

import json
import logging
import os
import time

from starlette.types import ASGIApp, Receive, Scope, Send

from core.config import settings

_log = logging.getLogger("highfive.rate_limit")

# token-bucket rate limit for the open POST endpoints. enabled only when
# HIGHFIVE_RATE_LIMIT is set, e.g. "240/60" = 240 requests per 60 seconds per
# client ip per path. unset (the dev default) the middleware is a transparent
# pass-through — behaviour is byte-identical to not mounting it at all.

LIMITED_PATHS = frozenset({"/cv/evaluate", "/progress"})

# safety valve so the bucket map can't grow without bound on a long-lived
# process being scanned by random clients.
_MAX_BUCKETS = 4096


def parse_limit(raw: str | None) -> tuple[int, float] | None:
    """parse "<requests>/<window-seconds>" → (count, window). None disables."""
    if not raw or not raw.strip():
        return None
    try:
        count_part, window_part = raw.split("/", 1)
        count = int(count_part)
        window = float(window_part)
    except ValueError:
        return None
    if count <= 0 or window <= 0:
        return None
    return count, window


class _Bucket:
    __slots__ = ("tokens", "updated", "limited")

    def __init__(self, tokens: float, updated: float) -> None:
        self.tokens = tokens
        self.updated = updated
        # tracks the limited episode so we log once when a client crosses
        # the line, not once per rejected request.
        self.limited = False


class RateLimitMiddleware:
    """
    pure-asgi so it sits in front of the whole fastapi stack and a limited
    request costs nothing past this point. only POSTs to LIMITED_PATHS are
    metered; every other request flows through untouched.
    """

    def __init__(self, app: ASGIApp, raw_limit: str | None = None) -> None:
        self.app = app
        if raw_limit is None:
            raw_limit = os.getenv("HIGHFIVE_RATE_LIMIT")
        self.limit = parse_limit(raw_limit)
        self._buckets: dict[str, _Bucket] = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            self.limit is None
            or scope["type"] != "http"
            or scope.get("method") != "POST"
            or scope.get("path") not in LIMITED_PATHS
        ):
            await self.app(scope, receive, send)
            return

        retry_after = self._take(self._key(scope))
        if retry_after is not None:
            await _send_429(scope, send, retry_after)
            return
        await self.app(scope, receive, send)

    def _key(self, scope: Scope) -> str:
        # the direct peer address, deliberately not x-forwarded-for — an
        # unauthenticated client could spoof that header to dodge the limit.
        client = scope.get("client")
        ip = client[0] if client else "unknown"
        return f"{ip}:{scope['path']}"

    def _take(self, key: str) -> float | None:
        """consume one token. returns None on success, else seconds to wait."""
        assert self.limit is not None
        count, window = self.limit
        rate = count / window
        now = time.monotonic()

        bucket = self._buckets.get(key)
        if bucket is None:
            if len(self._buckets) >= _MAX_BUCKETS:
                self._prune(now, window)
            bucket = _Bucket(tokens=float(count), updated=now)
            self._buckets[key] = bucket
        else:
            bucket.tokens = min(float(count), bucket.tokens + (now - bucket.updated) * rate)
            bucket.updated = now

        if bucket.tokens >= 1.0:
            bucket.tokens -= 1.0
            bucket.limited = False
            return None
        if not bucket.limited:
            bucket.limited = True
            _log.warning("rate limit engaged for %s (limit %d/%gs)", key, count, window)
        return (1.0 - bucket.tokens) / rate

    def _prune(self, now: float, window: float) -> None:
        idle = [k for k, b in self._buckets.items() if now - b.updated > window]
        for k in idle:
            del self._buckets[k]
        # pathological case: everything is active. drop the stalest entries
        # rather than letting the map grow forever.
        if len(self._buckets) >= _MAX_BUCKETS:
            stalest = sorted(self._buckets, key=lambda k: self._buckets[k].updated)
            for k in stalest[: _MAX_BUCKETS // 4]:
                del self._buckets[k]


async def _send_429(scope: Scope, send: Send, retry_after: float) -> None:
    wait = max(1, int(retry_after + 0.999))
    body = json.dumps(
        {"detail": "too many requests — slow down and try again.", "retry_after": wait}
    ).encode("utf-8")
    headers = [
        (b"content-type", b"application/json"),
        (b"content-length", str(len(body)).encode("latin-1")),
        (b"retry-after", str(wait).encode("latin-1")),
    ]
    # this response short-circuits before fastapi's cors middleware runs, so
    # echo the allowed origin ourselves or the browser hides the 429 from js.
    origin = _read_header(scope.get("headers") or (), b"origin")
    if origin and origin.decode("latin-1") in settings.cors_origins:
        headers.append((b"access-control-allow-origin", origin))
        headers.append((b"vary", b"origin"))
    await send({"type": "http.response.start", "status": 429, "headers": headers})
    await send({"type": "http.response.body", "body": body})


def _read_header(headers: list[tuple[bytes, bytes]] | tuple, name: bytes) -> bytes | None:
    for key, value in headers:
        if key.lower() == name:
            return value
    return None
