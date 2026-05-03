from __future__ import annotations

from fastapi import HTTPException

from core.idempotency import IdempotencyCache
from models.progress import ProgressRecord
from services.profile_service import profile_service
from services.progress_service import ProgressService, progress_service
from views.progress_view import (
    ProgressCreateRequest,
    ProgressCreateResponse,
    ProgressResponse,
)


# upg-7: 24h is comfortably longer than the offline queue's realistic
# replay window — a tab that's been offline for a day is the worst case
# we want to dedupe. anything older falls out and re-records, which is
# the right tradeoff (we don't pin response state in memory forever).
_IDEMPOTENCY_TTL_SECONDS = 24 * 60 * 60


class ProgressController:
    def __init__(self, service: ProgressService = progress_service) -> None:
        self._service = service
        self._idempotency: IdempotencyCache[ProgressCreateResponse] = IdempotencyCache(
            ttl_seconds=_IDEMPOTENCY_TTL_SECONDS,
        )

    def record(self, payload: ProgressCreateRequest) -> ProgressCreateResponse:
        # upg-7: short-circuit a replay before any side effects run. we
        # namespace the cache by profile_id so a leaked or guessed token
        # from one learner can't surface another learner's response.
        cache_key = self._cache_key(payload)
        if cache_key is not None:
            cached = self._idempotency.get(cache_key)
            if cached is not None:
                return cached

        # validate against the profile store — progress cannot be tied to an
        # unknown learner. ui should always post a real seeded/created profile.
        if not profile_service.exists(payload.profile_id):
            raise HTTPException(status_code=404, detail="profile not found")

        # capture achievements that exist before this attempt so the response
        # can tell the client which badges were newly unlocked.
        before_summary = self._service.summary(payload.profile_id)
        before_codes = {a.code for a in before_summary.achievements}

        record = self._service.record(
            ProgressRecord(
                profile_id=payload.profile_id,
                routine_id=payload.routine_id,
                gesture_id=payload.gesture_id,
                accuracy=payload.accuracy,
                band=payload.band,
                attempts=payload.attempts,
                succeeded=payload.succeeded,
                incorrect_points=payload.incorrect_points,
            ),
            completed_routine=payload.completed_routine,
        )

        summary = self._service.summary(payload.profile_id)
        new_codes = [a for a in summary.achievements if a.code not in before_codes]

        xp_gained = summary.total_xp - before_summary.total_xp
        response = ProgressCreateResponse(
            record=record,
            summary=summary,
            xp_gained=xp_gained,
            new_achievements=new_codes,
            leveled_up=summary.level > before_summary.level,
        )
        if cache_key is not None:
            self._idempotency.set(cache_key, response)
        return response

    @staticmethod
    def _cache_key(payload: ProgressCreateRequest) -> str | None:
        if not payload.idempotency_key:
            return None
        return f"{payload.profile_id}:{payload.idempotency_key}"

    def get_for(self, profile_id: str, limit: int = 25) -> ProgressResponse:
        summary = self._service.summary(profile_id)
        recent = self._service.list_for(profile_id, limit=limit)
        return ProgressResponse(summary=summary, recent=recent)


progress_controller = ProgressController()
