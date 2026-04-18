from fastapi import APIRouter, Path

from controllers.routine_controller import routine_controller
from views.routine_view import (
    RoutineCreateRequest,
    RoutineListResponse,
    RoutineResponse,
    RoutineUpdateRequest,
)

router = APIRouter(prefix="/routines", tags=["routines"])


@router.get("", response_model=RoutineListResponse)
def list_routines() -> RoutineListResponse:
    return routine_controller.list_routines()


@router.get("/{routine_id}", response_model=RoutineResponse)
def get_routine(routine_id: str = Path(max_length=64)) -> RoutineResponse:
    return routine_controller.get(routine_id)


@router.post("", response_model=RoutineResponse, status_code=201)
def create_routine(payload: RoutineCreateRequest) -> RoutineResponse:
    return routine_controller.create(payload)


@router.put("/{routine_id}", response_model=RoutineResponse)
def update_routine(
    payload: RoutineUpdateRequest,
    routine_id: str = Path(max_length=64),
) -> RoutineResponse:
    return routine_controller.update(routine_id, payload)


@router.delete("/{routine_id}")
def delete_routine(routine_id: str = Path(max_length=64)) -> dict:
    return routine_controller.delete(routine_id)
