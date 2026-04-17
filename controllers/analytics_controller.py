from __future__ import annotations

from fastapi import HTTPException

from services.analytics_service import AnalyticsService, analytics_service
from services.profile_service import profile_service
from views.analytics_view import AnalyticsResponse


class AnalyticsController:
    def __init__(self, service: AnalyticsService = analytics_service) -> None:
        self._service = service

    def get_for(
        self,
        profile_id: str,
        *,
        weak_limit: int = 5,
        trend_window: int = 10,
    ) -> AnalyticsResponse:
        if not profile_service.exists(profile_id):
            raise HTTPException(status_code=404, detail="profile not found")
        snapshot = self._service.snapshot(
            profile_id,
            weak_limit=weak_limit,
            trend_window=trend_window,
        )
        return AnalyticsResponse(analytics=snapshot)


analytics_controller = AnalyticsController()
