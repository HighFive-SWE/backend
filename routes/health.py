from fastapi import APIRouter

from controllers.health_controller import health_controller
from views.lesson_view import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    return health_controller.check()
