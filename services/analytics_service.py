from __future__ import annotations

from collections import Counter, defaultdict

from models.analytics import AnalyticsSnapshot, FingerHeat, TrendPoint, WeakGesture
from services.progress_service import ProgressService, progress_service

# mediapipe landmark indices bucketed by finger. matches the grouping used in
# frontend/modules/learning/feedback.ts so copy + heatmap speak the same language.
_FINGER_POINTS: dict[str, tuple[int, ...]] = {
    "thumb":  (1, 2, 3, 4),
    "index":  (5, 6, 7, 8),
    "middle": (9, 10, 11, 12),
    "ring":   (13, 14, 15, 16),
    "pinky":  (17, 18, 19, 20),
}
_FINGER_ORDER = ("thumb", "index", "middle", "ring", "pinky")


def _finger_for(landmark: int) -> str | None:
    for name, ids in _FINGER_POINTS.items():
        if landmark in ids:
            return name
    return None


class AnalyticsService:
    """
    derives weak-gesture + trend + finger-heat views from the per-profile
    progress log. no extra state — progress_service is the single source of truth.
    """

    def __init__(self, progress: ProgressService = progress_service) -> None:
        self._progress = progress

    def snapshot(
        self,
        profile_id: str,
        *,
        weak_limit: int = 5,
        trend_window: int = 10,
    ) -> AnalyticsSnapshot:
        records = self._progress.all_records(profile_id)
        total = len(records)

        if total == 0:
            return AnalyticsSnapshot(
                profile_id=profile_id,
                sample_size=0,
                avg_accuracy=0.0,
                success_rate=0.0,
                weak_gestures=[],
                trend=[],
                finger_heat=[],
                weakest_gesture_id=None,
            )

        avg_accuracy = round(sum(r.accuracy for r in records) / total, 4)
        successes = sum(1 for r in records if r.succeeded)
        success_rate = round(successes / total, 4)

        weak = self._weak_gestures(records, weak_limit)
        trend = self._trend(records, trend_window)
        finger_heat = self._finger_heat(records)

        return AnalyticsSnapshot(
            profile_id=profile_id,
            sample_size=total,
            avg_accuracy=avg_accuracy,
            success_rate=success_rate,
            weak_gestures=weak,
            trend=trend,
            finger_heat=finger_heat,
            weakest_gesture_id=weak[0].gesture_id if weak else None,
        )

    def _weak_gestures(self, records, limit: int) -> list[WeakGesture]:
        by_gesture: dict[str, list] = defaultdict(list)
        for r in records:
            by_gesture[r.gesture_id].append(r)

        rows: list[WeakGesture] = []
        for gesture_id, items in by_gesture.items():
            attempts = len(items)
            successes = sum(1 for r in items if r.succeeded)
            avg = round(sum(r.accuracy for r in items) / attempts, 4)
            rows.append(
                WeakGesture(
                    gesture_id=gesture_id,
                    attempts=attempts,
                    successes=successes,
                    success_rate=round(successes / attempts, 4),
                    avg_accuracy=avg,
                )
            )

        # lowest success rate first, then lowest avg accuracy as a tiebreaker.
        rows.sort(key=lambda w: (w.success_rate, w.avg_accuracy))
        return rows[:limit]

    def _trend(self, records, window: int) -> list[TrendPoint]:
        tail = records[-window:] if window > 0 else records
        return [
            TrendPoint(
                gesture_id=r.gesture_id,
                accuracy=round(r.accuracy, 4),
                succeeded=r.succeeded,
                at=r.created_at,
            )
            for r in tail
        ]

    def _finger_heat(self, records) -> list[FingerHeat]:
        counter: Counter[str] = Counter()
        for r in records:
            for landmark in r.incorrect_points:
                finger = _finger_for(landmark)
                if finger is not None:
                    counter[finger] += 1

        total_misses = sum(counter.values())
        if total_misses == 0:
            return [FingerHeat(finger=name, misses=0, share=0.0) for name in _FINGER_ORDER]

        return [
            FingerHeat(
                finger=name,
                misses=counter.get(name, 0),
                share=round(counter.get(name, 0) / total_misses, 4),
            )
            for name in _FINGER_ORDER
        ]


analytics_service = AnalyticsService()
