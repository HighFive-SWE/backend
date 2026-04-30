import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp

from core.config import settings
from core.request_id import RequestIdLogFilter, RequestIdMiddleware, current_request_id
from routes import analytics, cv, health, lessons, profiles, progress, routines


def _configure_logging() -> None:
    # idempotent: re-importing main shouldn't stack handlers (uvicorn --reload).
    root = logging.getLogger()
    if any(getattr(h, "_highfive", False) for h in root.handlers):
        return
    handler = logging.StreamHandler()
    handler._highfive = True  # type: ignore[attr-defined]
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s [rid=%(request_id)s] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    handler.addFilter(RequestIdLogFilter())
    root.addHandler(handler)
    if root.level > logging.INFO or root.level == logging.NOTSET:
        root.setLevel(logging.INFO)


_configure_logging()
_log = logging.getLogger("highfive.api")


def create_app() -> FastAPI:
    app = FastAPI(
        title="HighFive API",
        version="0.1.0",
        description="foundation api for the HighFive sign language platform.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["x-request-id"],
    )

    # phase 9: never crash on bad input — pydantic already returns 422 on
    # validation failures, but anything else (a service-layer bug, a vision
    # import error, an unexpected KeyError) would otherwise leak a traceback
    # to the client. log it server-side, ship a stable JSON shape to the ui.
    # upg-1: include the active request id in both the log line and the
    # response body so a user-reported error is one grep away from the trace.
    @app.exception_handler(Exception)
    async def _on_unhandled(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
        rid = current_request_id() or "-"
        _log.exception("unhandled error in %s %s", request.method, request.url.path)
        # the response header is added by RequestIdMiddleware on the way out;
        # echoing the id in the body is what makes a user-reported error
        # joinable with the log line above.
        return JSONResponse(
            status_code=500,
            content={
                "detail": "internal error — please try again.",
                "request_id": rid,
            },
        )

    app.include_router(health.router)
    app.include_router(lessons.router)
    app.include_router(routines.router)
    app.include_router(cv.router)
    app.include_router(profiles.router)
    app.include_router(progress.router)
    app.include_router(analytics.router)

    return app


# wrap the fastapi app at the pure-asgi layer rather than via add_middleware:
# fastapi attaches its `Exception` handler to the outermost ServerErrorMiddleware,
# so a user middleware (which lives inside ServerErrorMiddleware) wouldn't have
# its contextvars visible to the handler. wrapping at the asgi layer puts the
# request id in scope before fastapi's stack is even entered.
fastapi_app: ASGIApp = create_app()
app: ASGIApp = RequestIdMiddleware(fastapi_app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
