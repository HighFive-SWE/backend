from fastapi import APIRouter, Query

from controllers.analytics_controller import analytics_controller
from views.analytics_view import AnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/{profile_id}", response_model=AnalyticsResponse)
def get_analytics(
    profile_id: str,
    weak_limit: int = Query(5, ge=1, le=15),
    trend_window: int = Query(10, ge=1, le=50),
) -> AnalyticsResponse:
    return analytics_controller.get_for(
        profile_id,
        weak_limit=weak_limit,
        trend_window=trend_window,
    )
