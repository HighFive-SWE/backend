import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from routes import analytics, cv, health, lessons, profiles, progress, routines

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
    )

    # phase 9: never crash on bad input — pydantic already returns 422 on
    # validation failures, but anything else (a service-layer bug, a vision
    # import error, an unexpected KeyError) would otherwise leak a traceback
    # to the client. log it server-side, ship a stable JSON shape to the ui.
    @app.exception_handler(Exception)
    async def _on_unhandled(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
        _log.exception("unhandled error in %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "internal error — please try again."},
        )

    app.include_router(health.router)
    app.include_router(lessons.router)
    app.include_router(routines.router)
    app.include_router(cv.router)
    app.include_router(profiles.router)
    app.include_router(progress.router)
    app.include_router(analytics.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
