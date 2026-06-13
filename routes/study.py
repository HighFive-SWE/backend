from fastapi import APIRouter, Path

from controllers.study_controller import study_controller
from views.study_view import (
    StudySessionRequest,
    StudySessionResponse,
    StudyStatsResponse,
)

router = APIRouter(prefix="/study", tags=["study"])


@router.post("/sessions", response_model=StudySessionResponse)
def record_session(payload: StudySessionRequest) -> StudySessionResponse:
    return study_controller.record(payload)


@router.get("/{profile_id}", response_model=StudyStatsResponse)
def get_stats(profile_id: str = Path(max_length=64)) -> StudyStatsResponse:
    return study_controller.stats_for(profile_id)
