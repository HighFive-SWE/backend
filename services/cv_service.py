from __future__ import annotations

from collections import deque
from typing import Deque

from core import vision_path  # noqa: F401  — adds /vision to sys.path
from vision import compare_gesture, get_reference  # type: ignore[import-not-found]

from models.cv_result import CVResult


_SUGGESTIONS = {
    "correct": "nailed it — hold that shape.",
    "partial": "almost there, steady your hand.",
    "incorrect": "let's reset — watch the loop and try again.",
}


class CVService:
    """
    evaluates user landmarks against a reference gesture and keeps a short
    rolling log of results in memory. phase 2 doesn't need a persistent store —
    the ring buffer is enough to power the dashboard strip on /mirror.
    """

    def __init__(self, log_capacity: int = 200) -> None:
        self._log: Deque[CVResult] = deque(maxlen=log_capacity)

    def evaluate(
        self,
        gesture_id: str,
        landmarks: list[list[float]],
        user_id: str | None = None,
    ) -> CVResult:
        reference = get_reference(gesture_id)
        result = compare_gesture(landmarks, reference)

        record = CVResult(
            gesture_id=gesture_id,
            accuracy=result.accuracy,
            band=result.band,
            incorrect_points=result.incorrect_points,
            user_id=user_id,
        )
        self._log.append(record)
        return record

    def suggestion_for(self, band: str) -> str:
        return _SUGGESTIONS.get(band, _SUGGESTIONS["partial"])

    def recent(self, limit: int = 25) -> list[CVResult]:
        if limit <= 0:
            return []
        items = list(self._log)[-limit:]
        items.reverse()
        return items


cv_service = CVService()
