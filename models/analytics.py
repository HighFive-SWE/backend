from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class WeakGesture(BaseModel):
    gesture_id: str
    attempts: int
    successes: int
    success_rate: float  # 0..1
    avg_accuracy: float


class TrendPoint(BaseModel):
    gesture_id: str
    accuracy: float
    succeeded: bool
    at: datetime


class FingerHeat(BaseModel):
    finger: str  # "thumb" | "index" | "middle" | "ring" | "pinky"
    misses: int
    share: float  # portion of total misses, 0..1


class AnalyticsSnapshot(BaseModel):
    profile_id: str
    sample_size: int
    avg_accuracy: float
    success_rate: float
    weak_gestures: list[WeakGesture]
    trend: list[TrendPoint]
    finger_heat: list[FingerHeat]
    weakest_gesture_id: str | None
