from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from models.progress import Achievement, ProgressRecord, ProgressSummary


# phase 9: tightened validators. band is a closed set on the comparator side
# — reject anything that isn't one of the three values instead of storing
# whatever the client shipped. id fields are bounded so a malformed client
# can't flood memory with megabyte-long strings. incorrect_points is bounded
# to the mediapipe landmark count (0..20) and capped at 21 entries.
Band = Literal["correct", "partial", "incorrect"]


class ProgressCreateRequest(BaseModel):
    profile_id: str = Field(min_length=1, max_length=64)
    routine_id: str = Field(min_length=1, max_length=64)
    gesture_id: str = Field(min_length=1, max_length=64)
    accuracy: float = Field(ge=0.0, le=1.0)
    band: Band
    attempts: int = Field(ge=1, le=1000)
    succeeded: bool
    completed_routine: bool = False
    incorrect_points: list[int] = Field(default_factory=list, max_length=21)
    # upg-7: client-supplied dedupe token. when present, a replay of the same
    # token within the cache's ttl returns the original response instead of
    # double-recording the attempt. optional so older clients keep working.
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=64)

    @field_validator("incorrect_points")
    @classmethod
    def _bounded_indices(cls, v: list[int]) -> list[int]:
        for idx in v:
            if idx < 0 or idx > 20:
                raise ValueError("incorrect_points entries must be landmark indices 0..20")
        return v


class ProgressCreateResponse(BaseModel):
    record: ProgressRecord
    summary: ProgressSummary
    xp_gained: int = 0
    new_achievements: list[Achievement] = Field(default_factory=list)
    leveled_up: bool = False


class ProgressResponse(BaseModel):
    summary: ProgressSummary
    recent: list[ProgressRecord]
