from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from models.cv_result import CVResult


class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float = 0.0


class EvaluateRequest(BaseModel):
    gesture_id: str
    landmarks: list[LandmarkPoint]
    user_id: str | None = None

    @field_validator("landmarks")
    @classmethod
    def _check_length(cls, v: list[LandmarkPoint]) -> list[LandmarkPoint]:
        if len(v) != 21:
            raise ValueError("mediapipe hand tracking returns exactly 21 landmarks")
        return v


class EvaluateResponse(BaseModel):
    accuracy: float
    band: str
    incorrect_points: list[int] = Field(default_factory=list)
    suggestion: str | None = None


class RecentResultsResponse(BaseModel):
    results: list[CVResult]
