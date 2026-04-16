from core.config import settings
from views.lesson_view import HealthResponse


class HealthController:
    def check(self) -> HealthResponse:
        return HealthResponse(status="ok", env=settings.env)


health_controller = HealthController()
