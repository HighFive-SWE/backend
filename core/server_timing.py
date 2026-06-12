from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator

from starlette.types import ASGIApp, Message, Receive, Scope, Send

# stamps a `Server-Timing` header on every http response so the browser's
# network tab shows where time went without any client code or tooling.
# the middleware always reports `app` (total time inside the asgi stack);
# finer segments are opt-in via the `segment` context manager below.
#
# upg-10 from todos.md. headers are inert to every existing consumer —
# unmount the middleware and nothing changes.

_segments_var: ContextVar[list[tuple[str, float]] | None] = ContextVar(
    "highfive_server_timing_segments", default=None
)


@contextmanager
def segment(name: str) -> Iterator[None]:
    """time a named block, e.g. `with segment("comparator"): ...` — the
    duration lands in the response's Server-Timing header alongside `app`."""
    start = time.perf_counter()
    try:
        yield
    finally:
        bucket = _segments_var.get()
        if bucket is not None:
            bucket.append((name, (time.perf_counter() - start) * 1000.0))


class ServerTimingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        token = _segments_var.set([])

        async def send_with_timing(message: Message) -> None:
            if message["type"] == "http.response.start":
                total = (time.perf_counter() - start) * 1000.0
                parts = [f"app;dur={total:.1f}"]
                for name, dur in _segments_var.get() or []:
                    parts.append(f"{_safe_name(name)};dur={dur:.1f}")
                headers = list(message.get("headers") or [])
                headers.append((b"server-timing", ", ".join(parts).encode("latin-1")))
                # lets cross-origin js (the frontend on another port) read the
                # values via the performance api, not just see them in devtools.
                headers.append((b"timing-allow-origin", b"*"))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_with_timing)
        finally:
            _segments_var.reset(token)


def _safe_name(name: str) -> str:
    # server-timing metric names are header tokens — keep them boring.
    cleaned = "".join(c if c.isalnum() or c in "-_" else "-" for c in name)
    return cleaned or "segment"
