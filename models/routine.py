from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class RoutineStep(BaseModel):
    gesture_id: str  # must exist in /vision/gestures/samples.py
    prompt: str
    hint: str


class Routine(BaseModel):
    id: str
    name: str
    description: str
    scenario_tag: str  # "daily" | "mealtime" | "safety" | "home" | "custom" ...
    steps: list[RoutineStep] = Field(default_factory=list)
    created_by: str | None = None  # profile_id of creator, None for seed routines
    is_custom: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def length(self) -> int:
        return len(self.steps)
