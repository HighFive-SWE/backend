from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException

from controllers.analytics_controller import AnalyticsController
from models.analytics import AnalyticsSnapshot
from views.analytics_view import AnalyticsResponse


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def controller(mock_service):
    return AnalyticsController(service=mock_service)


def make_snapshot(**overrides):
    defaults = dict(
        profile_id="user-123",
        sample_size=10,
        avg_accuracy=0.85,
        success_rate=0.7,
        weak_gestures=[],
        trend=[],
        finger_heat=[],
        weakest_gesture_id=None,
    )
    return AnalyticsSnapshot(**{**defaults, **overrides})


# --- get_for ---

def test_get_for_raises_404_when_profile_not_found(controller, mock_service):
    with patch("controllers.analytics_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            controller.get_for("nonexistent-id")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "profile not found"
        mock_service.snapshot.assert_not_called()


def test_get_for_returns_analytics_response(controller, mock_service):
    fake_snapshot = make_snapshot()

    with patch("controllers.analytics_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        mock_service.snapshot.return_value = fake_snapshot

        result = controller.get_for("user-123")

        assert isinstance(result, AnalyticsResponse)
        assert result.analytics == fake_snapshot


def test_get_for_passes_default_params_to_snapshot(controller, mock_service):
    with patch("controllers.analytics_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        mock_service.snapshot.return_value = make_snapshot()

        controller.get_for("user-123")

        mock_service.snapshot.assert_called_once_with(
            "user-123",
            weak_limit=5,
            trend_window=10,
        )


def test_get_for_passes_custom_params_to_snapshot(controller, mock_service):
    with patch("controllers.analytics_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        mock_service.snapshot.return_value = make_snapshot()

        controller.get_for("user-123", weak_limit=3, trend_window=20)

        mock_service.snapshot.assert_called_once_with(
            "user-123",
            weak_limit=3,
            trend_window=20,
        )


def test_get_for_checks_correct_profile_id(controller, mock_service):
    with patch("controllers.analytics_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = False

        with pytest.raises(HTTPException):
            controller.get_for("specific-id-999")

        mock_profile.exists.assert_called_once_with("specific-id-999")
