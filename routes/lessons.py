from fastapi import APIRouter

from controllers.lesson_controller import lesson_controller
from views.lesson_view import LessonsResponse

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("", response_model=LessonsResponse)
def list_lessons() -> LessonsResponse:
    return lesson_controller.list_lessons()
