from fastapi import APIRouter, Path, Query

from controllers.progress_controller import progress_controller
from views.progress_view import (
    DailyGoalUpdateRequest,
    DailyGoalUpdateResponse,
    ProgressCreateRequest,
    ProgressCreateResponse,
    ProgressResponse,
)

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("", response_model=ProgressCreateResponse)
def create_progress(payload: ProgressCreateRequest) -> ProgressCreateResponse:
    return progress_controller.record(payload)


@router.get("/{profile_id}", response_model=ProgressResponse)
def get_progress(
    profile_id: str = Path(max_length=64),
    limit: int = Query(25, ge=1, le=200),
) -> ProgressResponse:
    return progress_controller.get_for(profile_id, limit=limit)


@router.put("/{profile_id}/goal", response_model=DailyGoalUpdateResponse)
def set_daily_goal(
    payload: DailyGoalUpdateRequest,
    profile_id: str = Path(max_length=64),
) -> DailyGoalUpdateResponse:
    return progress_controller.set_daily_goal(profile_id, payload)
