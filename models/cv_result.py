from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class CVResult(BaseModel):
    gesture_id: str
    accuracy: float
    band: str  # "correct" | "partial" | "incorrect"
    incorrect_points: list[int] = Field(default_factory=list)
    user_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
