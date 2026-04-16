import os
from dataclasses import dataclass, field


def _parse_origins(raw: str | None) -> list[str]:
    if not raw:
        return ["http://localhost:3000"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    env: str = os.getenv("HIGHFIVE_ENV", "dev")
    cors_origins: list[str] = field(
        default_factory=lambda: _parse_origins(os.getenv("HIGHFIVE_CORS_ORIGINS"))
    )


settings = Settings()
