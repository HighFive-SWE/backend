from unittest.mock import MagicMock
import pytest

from controllers.lesson_controller import LessonController
from models.lesson import Lesson
from views.lesson_view import LessonsResponse


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def controller(mock_service):
    return LessonController(service=mock_service)


def make_lesson(**overrides):
    defaults = dict(id="lesson-1", title="Lesson 1", description="A lesson")
    return Lesson(**{**defaults, **overrides})


# --- list_lessons ---

def test_list_lessons_returns_response(controller, mock_service):
    mock_service.list_lessons.return_value = [make_lesson(id="l-1"), make_lesson(id="l-2")]

    result = controller.list_lessons()

    assert isinstance(result, LessonsResponse)


def test_list_lessons_forwards_service_results(controller, mock_service):
    fake_lessons = [make_lesson(id="l-1"), make_lesson(id="l-2")]
    mock_service.list_lessons.return_value = fake_lessons

    result = controller.list_lessons()

    assert result.lessons == fake_lessons


def test_list_lessons_calls_service_once(controller, mock_service):
    mock_service.list_lessons.return_value = []

    controller.list_lessons()

    mock_service.list_lessons.assert_called_once()


def test_list_lessons_returns_empty_list(controller, mock_service):
    mock_service.list_lessons.return_value = []

    result = controller.list_lessons()

    assert result.lessons == []
