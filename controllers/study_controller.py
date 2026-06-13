from fastapi import HTTPException

from services.profile_service import profile_service
from services.study_service import StudyService, study_service
from views.study_view import (
    StudySessionRequest,
    StudySessionResponse,
    StudyStatsResponse,
)


class StudyController:
    def __init__(self, service: StudyService = study_service) -> None:
        self._service = service

    def record(self, payload: StudySessionRequest) -> StudySessionResponse:
        # same rule as progress: sessions cannot be tied to an unknown learner.
        if not profile_service.exists(payload.profile_id):
            raise HTTPException(status_code=404, detail="profile not found")
        stats = self._service.record_session(
            profile_id=payload.profile_id,
            deck=payload.deck,
            mode=payload.mode,
            cards_seen=payload.cards_seen,
            correct=payload.correct,
        )
        return StudySessionResponse(stats=stats)

    def stats_for(self, profile_id: str) -> StudyStatsResponse:
        if not profile_service.exists(profile_id):
            raise HTTPException(status_code=404, detail="profile not found")
        return StudyStatsResponse(stats=self._service.stats(profile_id))


study_controller = StudyController()
