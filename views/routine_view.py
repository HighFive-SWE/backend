from __future__ import annotations

from pydantic import BaseModel

from models.routine import Routine


class RoutineListResponse(BaseModel):
    routines: list[Routine]


class RoutineResponse(BaseModel):
    routine: Routine
