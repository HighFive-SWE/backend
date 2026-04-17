from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routes import analytics, cv, health, lessons, profiles, progress, routines


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
