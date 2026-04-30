from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar
from typing import Awaitable, Callable

from starlette.types import ASGIApp, Message, Receive, Scope, Send


# header used both inbound (honour an upstream id) and outbound (echo back).
HEADER_NAME = "x-request-id"

# upper bound on accepted inbound ids — defangs a hostile client trying to push
# a multi-megabyte token into our log lines and response headers.
_MAX_INBOUND_LENGTH = 128

# contextvar so the log filter and exception handler can read the active id
# without threading it through every call site.
_request_id_var: ContextVar[str | None] = ContextVar("highfive_request_id", default=None)


def current_request_id() -> str | None:
    """return the id for the request currently being served on this task."""
    return _request_id_var.get()


def _coerce_inbound(raw: str | None) -> str | None:
    if not raw:
        return None
    candidate = raw.strip()
    if not candidate or len(candidate) > _MAX_INBOUND_LENGTH:
        return None
    # printable-ascii only — keeps log lines and response headers safe.
    if any(ord(c) < 0x20 or ord(c) > 0x7E for c in candidate):
        return None
    return candidate


def _fresh_id() -> str:
    return uuid.uuid4().hex


class RequestIdMiddleware:
    """
    pure-asgi middleware so it sits outside fastapi's exception handling and
    still tags every response — including the ones produced by the global
    `Exception` handler in main.py.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        inbound = _read_header(scope.get("headers") or (), HEADER_NAME)
        request_id = _coerce_inbound(inbound) or _fresh_id()
        token = _request_id_var.set(request_id)

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers") or [])
                headers.append((HEADER_NAME.encode("latin-1"), request_id.encode("latin-1")))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_with_header)
        finally:
            _request_id_var.reset(token)


def _read_header(headers: list[tuple[bytes, bytes]] | tuple, name: str) -> str | None:
    target = name.lower().encode("latin-1")
    for key, value in headers:
        if key.lower() == target:
            try:
                return value.decode("latin-1")
            except UnicodeDecodeError:
                return None
    return None


class RequestIdLogFilter(logging.Filter):
    """attaches the active request id (or '-') to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_var.get() or "-"
        return True
