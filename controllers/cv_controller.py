from __future__ import annotations

from fastapi import HTTPException, status

from core.server_timing import segment
from services.cv_service import CVService, cv_service
from views.cv_view import (
    EvaluateRequest,
    EvaluateResponse,
    RecentResultsResponse,
)


class CVController:
    def __init__(self, service: CVService = cv_service) -> None:
        self._service = service

    def evaluate(self, payload: EvaluateRequest) -> EvaluateResponse:
        landmarks = [[p.x, p.y, p.z] for p in payload.landmarks]
        try:
            # surfaces in the Server-Timing header next to `app`, so the
            # network tab shows comparator time vs framework overhead.
            with segment("comparator"):
                record = self._service.evaluate(
                    payload.gesture_id, landmarks, user_id=payload.user_id
                )
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        return EvaluateResponse(
            accuracy=record.accuracy,
            band=record.band,
            incorrect_points=record.incorrect_points,
            suggestion=self._service.suggestion_for(record.band),
        )

    def recent(self, limit: int = 25, user_id: str | None = None) -> RecentResultsResponse:
        return RecentResultsResponse(results=self._service.recent(limit=limit, user_id=user_id))


cv_controller = CVController()
