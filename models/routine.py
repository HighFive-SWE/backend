from __future__ import annotations

from pydantic import BaseModel, Field


class RoutineStep(BaseModel):
    gesture_id: str  # must exist in /vision/gestures/samples.py
    prompt: str
    hint: str


class Routine(BaseModel):
    id: str
    name: str  # e.g. "i need water"
    description: str
    scenario_tag: str  # "daily" | "mealtime" | "emergency" ...
    steps: list[RoutineStep] = Field(default_factory=list)

    @property
    def length(self) -> int:
        return len(self.steps)
