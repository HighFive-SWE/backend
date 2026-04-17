from __future__ import annotations

from pydantic import BaseModel, Field

from models.routine import Routine, RoutineStep


class RoutineListResponse(BaseModel):
    routines: list[Routine]


class RoutineResponse(BaseModel):
    routine: Routine


class RoutineStepInput(BaseModel):
    gesture_id: str
    prompt: str
    hint: str


class RoutineCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(max_length=400)
    steps: list[RoutineStepInput] = Field(min_length=2, max_length=6)
    created_by: str


class RoutineUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=400)
    steps: list[RoutineStepInput] | None = Field(default=None, min_length=2, max_length=6)
