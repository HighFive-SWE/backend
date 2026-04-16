from __future__ import annotations

from pydantic import BaseModel, Field

from models.progress import Achievement, ProgressRecord, ProgressSummary


class ProgressCreateRequest(BaseModel):
    profile_id: str
    routine_id: str
    gesture_id: str
    accuracy: float = Field(ge=0.0, le=1.0)
    band: str
    attempts: int = Field(ge=1)
    succeeded: bool
    completed_routine: bool = False


class ProgressCreateResponse(BaseModel):
    record: ProgressRecord
    summary: ProgressSummary
    xp_gained: int = 0
    new_achievements: list[Achievement] = Field(default_factory=list)
    leveled_up: bool = False


class ProgressResponse(BaseModel):
    summary: ProgressSummary
    recent: list[ProgressRecord]
