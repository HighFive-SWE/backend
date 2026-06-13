from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class StudySessionRequest(BaseModel):
    profile_id: str = Field(max_length=64)
    deck: str = Field(max_length=32)
    mode: Literal["browse", "quiz"]
    cards_seen: int = Field(ge=1, le=500)
    correct: int = Field(0, ge=0, le=500)

    @model_validator(mode="after")
    def _correct_within_seen(self) -> "StudySessionRequest":
        if self.correct > self.cards_seen:
            raise ValueError("correct cannot exceed cards_seen")
        return self


class StudyDeckStats(BaseModel):
    sessions: int
    cards_seen: int


class StudyStats(BaseModel):
    profile_id: str
    total_sessions: int
    cards_seen: int
    quiz_seen: int
    quiz_correct: int
    decks: dict[str, StudyDeckStats]
    last_studied_at: datetime | None


class StudySessionResponse(BaseModel):
    stats: StudyStats


class StudyStatsResponse(BaseModel):
    stats: StudyStats
