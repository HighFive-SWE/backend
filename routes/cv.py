from fastapi import APIRouter, Query

from controllers.cv_controller import cv_controller
from views.cv_view import EvaluateRequest, EvaluateResponse, RecentResultsResponse

router = APIRouter(prefix="/cv", tags=["cv"])


@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate_gesture(payload: EvaluateRequest) -> EvaluateResponse:
    return cv_controller.evaluate(payload)


@router.get("/results", response_model=RecentResultsResponse)
def recent_results(limit: int = Query(25, ge=1, le=200)) -> RecentResultsResponse:
    return cv_controller.recent(limit=limit)
