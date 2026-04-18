from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from models.cv_result import CVResult


# phase 9: accept normalized mediapipe coords but reject wildly out-of-range
# values. mediapipe reports x/y in [0, 1] (with small overshoot allowed for
# off-frame hands) and z typically in [-1, 1]. anything far outside that is
# a bad client, not a legitimate frame.
class LandmarkPoint(BaseModel):
    x: float = Field(ge=-2.0, le=2.0)
    y: float = Field(ge=-2.0, le=2.0)
    z: float = Field(default=0.0, ge=-5.0, le=5.0)


class EvaluateRequest(BaseModel):
    gesture_id: str = Field(min_length=1, max_length=64)
    landmarks: list[LandmarkPoint]
    user_id: str | None = Field(default=None, max_length=64)

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
