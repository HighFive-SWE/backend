from unittest.mock import patch
import pytest

from controllers.health_controller import HealthController
from views.lesson_view import HealthResponse


@pytest.fixture
def controller():
    return HealthController()


def test_check_returns_health_response(controller):
    result = controller.check()

    assert isinstance(result, HealthResponse)


def test_check_status_is_ok(controller):
    result = controller.check()

    assert result.status == "ok"


def test_check_returns_env_from_settings(controller):
    with patch("controllers.health_controller.settings") as mock_settings:
        mock_settings.env = "production"
        result = controller.check()

    assert result.env == "production"


def test_check_env_is_string(controller):
    result = controller.check()

    assert isinstance(result.env, str)
