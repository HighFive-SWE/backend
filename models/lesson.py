from typing import Literal

from pydantic import BaseModel, Field

Difficulty = Literal["starter", "growing", "fluent"]


class Lesson(BaseModel):
    id: str
    title: str
    description: str
    difficulty: Difficulty = "starter"
    tags: list[str] = Field(default_factory=list)
    # ids referenced from the shared /vision/gestures catalog.
    gesture_ids: list[str] = Field(default_factory=list)
    scenario_tag: str | None = None
