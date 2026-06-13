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
    the ring buffer is enough to power the dashboard strip on /mirror. results
    are also bucketed per user so one learner's reads never mix in another's
    attempts.
    """

    def __init__(self, log_capacity: int = 200, max_tracked_users: int = 256) -> None:
        self._log_capacity = log_capacity
        self._max_tracked_users = max_tracked_users
        self._log: Deque[CVResult] = deque(maxlen=log_capacity)
        self._per_user: dict[str, Deque[CVResult]] = {}

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
        if user_id:
            self._user_log(user_id).append(record)
        return record

    def suggestion_for(self, band: str) -> str:
        return _SUGGESTIONS.get(band, _SUGGESTIONS["partial"])

    def recent(self, limit: int = 25, user_id: str | None = None) -> list[CVResult]:
        if limit <= 0:
            return []
        source = self._per_user.get(user_id, ()) if user_id else self._log
        items = list(source)[-limit:]
        items.reverse()
        return items

    def _user_log(self, user_id: str) -> Deque[CVResult]:
        log = self._per_user.get(user_id)
        if log is None:
            # bounded — evict the longest-untouched user so anonymous churn
            # can't grow memory without limit.
            if len(self._per_user) >= self._max_tracked_users:
                self._per_user.pop(next(iter(self._per_user)))
            log = deque(maxlen=self._log_capacity)
            self._per_user[user_id] = log
        else:
            # re-insert so dict order tracks recency, not first-seen.
            self._per_user[user_id] = self._per_user.pop(user_id)
        return log


cv_service = CVService()
