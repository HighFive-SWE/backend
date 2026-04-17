from __future__ import annotations

from fastapi import HTTPException

from models.progress import ProgressRecord
from services.profile_service import profile_service
from services.progress_service import ProgressService, progress_service
from views.progress_view import (
    ProgressCreateRequest,
    ProgressCreateResponse,
    ProgressResponse,
)


class ProgressController:
    def __init__(self, service: ProgressService = progress_service) -> None:
        self._service = service

    def record(self, payload: ProgressCreateRequest) -> ProgressCreateResponse:
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
        return ProgressCreateResponse(
            record=record,
            summary=summary,
            xp_gained=xp_gained,
            new_achievements=new_codes,
            leveled_up=summary.level > before_summary.level,
        )

    def get_for(self, profile_id: str, limit: int = 25) -> ProgressResponse:
        summary = self._service.summary(profile_id)
        recent = self._service.list_for(profile_id, limit=limit)
        return ProgressResponse(summary=summary, recent=recent)


progress_controller = ProgressController()
