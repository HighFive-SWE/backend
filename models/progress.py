from __future__ import annotations

from datetime import date, datetime, timezone

from pydantic import BaseModel, Field


class ProgressRecord(BaseModel):
    profile_id: str
    routine_id: str
    gesture_id: str
    accuracy: float
    band: str  # "correct" | "partial" | "incorrect"
    attempts: int
    succeeded: bool
    # landmark indices that drifted past the comparator's joint threshold on
    # the best sample of this attempt. phase 6 analytics uses it for the
    # finger heatmap. defaults to [] so older clients stay compatible.
    incorrect_points: list[int] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Achievement(BaseModel):
    code: str
    title: str
    description: str
    unlocked_at: datetime


class DailyGoal(BaseModel):
    target: int
    progress: int
    date: date

    @property
    def met(self) -> bool:
        return self.progress >= self.target


class ProgressSummary(BaseModel):
    profile_id: str
    total_attempts: int
    successes: int
    avg_accuracy: float
    best_accuracy: float
    routines_completed: list[str]

    # gamification additions (phase 4)
    current_streak: int = 0
    longest_streak: int = 0
    last_active_date: date | None = None
    total_xp: int = 0
    level: int = 0
    xp_into_level: int = 0
    xp_to_next_level: int = 50
    achievements: list[Achievement] = Field(default_factory=list)
    daily_goal: DailyGoal | None = None

    # kept for backward compatibility with any pre-phase-4 clients.
    streak_days: int = 0
