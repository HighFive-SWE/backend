from unittest.mock import ANY, MagicMock
import pytest
from fastapi import HTTPException, status

from controllers.cv_controller import CVController
from models.cv_result import CVResult
from views.cv_view import EvaluateRequest, EvaluateResponse, LandmarkPoint, RecentResultsResponse


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def controller(mock_service):
    return CVController(service=mock_service)


def make_landmarks(n=21):
    return [LandmarkPoint(x=0.1, y=0.2, z=0.3) for _ in range(n)]


def make_payload(**overrides):
    defaults = dict(
        gesture_id="gesture-1",
        user_id="user-123",
        landmarks=make_landmarks(),
    )
    return EvaluateRequest(**{**defaults, **overrides})


def make_cv_result(**overrides):
    defaults = dict(gesture_id="gesture-1", accuracy=0.9, band="correct")
    return CVResult(**{**defaults, **overrides})


# --- evaluate ---

def test_evaluate_returns_response(controller, mock_service):
    record = MagicMock(accuracy=0.95, band="A", incorrect_points=[])
    mock_service.evaluate.return_value = record
    mock_service.suggestion_for.return_value = "Great job!"

    result = controller.evaluate(make_payload())

    assert isinstance(result, EvaluateResponse)
    assert result.accuracy == 0.95
    assert result.band == "A"
    assert result.incorrect_points == []
    assert result.suggestion == "Great job!"


def test_evaluate_maps_landmarks_correctly(controller, mock_service):
    mock_service.evaluate.return_value = MagicMock(
        accuracy=0.8, band="B", incorrect_points=[]
    )
    mock_service.suggestion_for.return_value = ""
    landmarks = (
        [LandmarkPoint(x=0.1, y=0.2, z=0.3), LandmarkPoint(x=0.4, y=0.5, z=0.6)]
        + make_landmarks(19)
    )

    controller.evaluate(make_payload(landmarks=landmarks))

    _, called_landmarks, *_ = mock_service.evaluate.call_args.args
    assert called_landmarks[0] == [0.1, 0.2, 0.3]
    assert called_landmarks[1] == [0.4, 0.5, 0.6]


def test_evaluate_passes_gesture_and_user_id(controller, mock_service):
    mock_service.evaluate.return_value = MagicMock(
        accuracy=0.9, band="A", incorrect_points=[]
    )
    mock_service.suggestion_for.return_value = ""

    controller.evaluate(make_payload(gesture_id="wave", user_id="user-42"))

    mock_service.evaluate.assert_called_once_with(
        "wave", ANY, user_id="user-42"
    )


def test_evaluate_raises_404_on_key_error(controller, mock_service):
    mock_service.evaluate.side_effect = KeyError("gesture not found")

    with pytest.raises(HTTPException) as exc_info:
        controller.evaluate(make_payload())

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "gesture not found" in exc_info.value.detail


def test_evaluate_raises_422_on_value_error(controller, mock_service):
    mock_service.evaluate.side_effect = ValueError("invalid landmark count")

    with pytest.raises(HTTPException) as exc_info:
        controller.evaluate(make_payload())

    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "invalid landmark count" in exc_info.value.detail


def test_evaluate_suggestion_uses_record_band(controller, mock_service):
    record = MagicMock(accuracy=0.7, band="C", incorrect_points=[])
    mock_service.evaluate.return_value = record
    mock_service.suggestion_for.return_value = "Keep practicing"

    result = controller.evaluate(make_payload())

    mock_service.suggestion_for.assert_called_once_with("C")
    assert result.suggestion == "Keep practicing"


# --- recent ---

def test_recent_returns_response(controller, mock_service):
    mock_service.recent.return_value = [make_cv_result(), make_cv_result()]

    result = controller.recent()

    assert isinstance(result, RecentResultsResponse)
    assert len(result.results) == 2


def test_recent_passes_default_limit(controller, mock_service):
    mock_service.recent.return_value = []

    controller.recent()

    mock_service.recent.assert_called_once_with(limit=25, user_id=None)


def test_recent_passes_custom_limit(controller, mock_service):
    mock_service.recent.return_value = []

    controller.recent(limit=10)

    mock_service.recent.assert_called_once_with(limit=10, user_id=None)


def test_recent_passes_user_filter(controller, mock_service):
    mock_service.recent.return_value = []

    controller.recent(limit=5, user_id="user-7")

    mock_service.recent.assert_called_once_with(limit=5, user_id="user-7")
