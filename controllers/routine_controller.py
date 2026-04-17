from __future__ import annotations

from fastapi import HTTPException, status

from models.routine import RoutineStep
from services.profile_service import profile_service
from services.routine_service import RoutineService, routine_service
from views.routine_view import (
    RoutineCreateRequest,
    RoutineListResponse,
    RoutineResponse,
    RoutineUpdateRequest,
)


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

    def create(self, payload: RoutineCreateRequest) -> RoutineResponse:
        if not profile_service.exists(payload.created_by):
            raise HTTPException(status_code=404, detail="profile not found")
        steps = [
            RoutineStep(gesture_id=s.gesture_id, prompt=s.prompt, hint=s.hint)
            for s in payload.steps
        ]
        try:
            routine = self._service.create(
                name=payload.name,
                description=payload.description,
                steps=steps,
                created_by=payload.created_by,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
            ) from exc
        return RoutineResponse(routine=routine)

    def update(self, routine_id: str, payload: RoutineUpdateRequest) -> RoutineResponse:
        steps = (
            [RoutineStep(gesture_id=s.gesture_id, prompt=s.prompt, hint=s.hint) for s in payload.steps]
            if payload.steps is not None
            else None
        )
        try:
            routine = self._service.update(
                routine_id,
                name=payload.name,
                description=payload.description,
                steps=steps,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return RoutineResponse(routine=routine)

    def delete(self, routine_id: str) -> dict:
        try:
            self._service.delete(routine_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {"ok": True}


routine_controller = RoutineController()
