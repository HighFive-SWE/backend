from fastapi import APIRouter, Query

from controllers.progress_controller import progress_controller
from views.progress_view import (
    ProgressCreateRequest,
    ProgressCreateResponse,
    ProgressResponse,
)

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("", response_model=ProgressCreateResponse)
def create_progress(payload: ProgressCreateRequest) -> ProgressCreateResponse:
    return progress_controller.record(payload)


@router.get("/{profile_id}", response_model=ProgressResponse)
def get_progress(profile_id: str, limit: int = Query(25, ge=1, le=200)) -> ProgressResponse:
    return progress_controller.get_for(profile_id, limit=limit)
