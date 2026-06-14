import os
from dataclasses import dataclass, field
from pathlib import Path


def _parse_origins(raw: str | None) -> list[str]:
    if not raw:
        return ["http://localhost:3000"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _default_database_url() -> str:
    # a local sqlite file is the zero-setup default: it survives restarts
    # (unlike the in-memory services) without needing a running postgres.
    # set DATABASE_URL to a postgres dsn in prod, e.g.
    # postgresql+psycopg://user:pass@host:5432/highfive.
    db_path = Path(__file__).resolve().parent.parent / "db" / "highfive.db"
    return f"sqlite:///{db_path}"


@dataclass(frozen=True)
class Settings:
    env: str = os.getenv("HIGHFIVE_ENV", "dev")
    cors_origins: list[str] = field(
        default_factory=lambda: _parse_origins(os.getenv("HIGHFIVE_CORS_ORIGINS"))
    )
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL") or _default_database_url()
    )


settings = Settings()
