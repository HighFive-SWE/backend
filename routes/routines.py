from fastapi import APIRouter

from controllers.routine_controller import routine_controller
from views.routine_view import RoutineListResponse, RoutineResponse

router = APIRouter(prefix="/routines", tags=["routines"])


@router.get("", response_model=RoutineListResponse)
def list_routines() -> RoutineListResponse:
    return routine_controller.list_routines()


@router.get("/{routine_id}", response_model=RoutineResponse)
def get_routine(routine_id: str) -> RoutineResponse:
    return routine_controller.get(routine_id)
