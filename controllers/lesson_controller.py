from services.lesson_service import LessonService, lesson_service
from views.lesson_view import LessonsResponse


class LessonController:
    def __init__(self, service: LessonService = lesson_service) -> None:
        self._service = service

    def list_lessons(self) -> LessonsResponse:
        return LessonsResponse(lessons=self._service.list_lessons())


lesson_controller = LessonController()
