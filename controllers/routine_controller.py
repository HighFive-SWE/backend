from __future__ import annotations

from fastapi import HTTPException, status

from services.routine_service import RoutineService, routine_service
from views.routine_view import RoutineListResponse, RoutineResponse


class RoutineController:
    def __init__(self, service: RoutineService = routine_service) -> None:
        self._service = service

    def list_routines(self) -> RoutineListResponse:
        return RoutineListResponse(routines=self._service.list_routines())

    def get(self, routine_id: str) -> RoutineResponse:
        try:
            return RoutineResponse(routine=self._service.get(routine_id))
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc


routine_controller = RoutineController()
