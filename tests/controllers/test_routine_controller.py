from unittest.mock import ANY, MagicMock, patch
import pytest
from fastapi import HTTPException, status

from controllers.routine_controller import RoutineController
from models.routine import Routine, RoutineStep
from views.routine_view import (
    RoutineCreateRequest,
    RoutineListResponse,
    RoutineResponse,
    RoutineStepInput,
    RoutineUpdateRequest,
)


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def controller(mock_service):
    return RoutineController(service=mock_service)


def make_routine(**overrides):
    defaults = dict(
        id="routine-1",
        name="Test Routine",
        description="A test",
        scenario_tag="daily",
        steps=[],
        created_by="profile-1",
        is_custom=True,
    )
    return Routine(**{**defaults, **overrides})


def make_create_request(**overrides):
    defaults = dict(
        name="Morning Routine",
        description="A daily morning routine",
        steps=[
            RoutineStepInput(gesture_id="wave", prompt="Wave hello", hint="Palm out"),
            RoutineStepInput(gesture_id="point", prompt="Point forward", hint="Index finger"),
        ],
        created_by="profile-1",
    )
    return RoutineCreateRequest(**{**defaults, **overrides})


def make_update_request(**overrides):
    return RoutineUpdateRequest(**overrides)


# --- list_routines ---

def test_list_routines_returns_response(controller, mock_service):
    mock_service.list_routines.return_value = []

    result = controller.list_routines()

    assert isinstance(result, RoutineListResponse)


def test_list_routines_forwards_service_results(controller, mock_service):
    fake_routines = [make_routine(id="r-1"), make_routine(id="r-2")]
    mock_service.list_routines.return_value = fake_routines

    result = controller.list_routines()

    assert result.routines == fake_routines


def test_list_routines_calls_service_once(controller, mock_service):
    mock_service.list_routines.return_value = []

    controller.list_routines()

    mock_service.list_routines.assert_called_once()


def test_list_routines_returns_empty_list(controller, mock_service):
    mock_service.list_routines.return_value = []

    result = controller.list_routines()

    assert result.routines == []


# --- get ---

def test_get_returns_routine_response(controller, mock_service):
    fake_routine = make_routine()
    mock_service.get.return_value = fake_routine

    result = controller.get("routine-1")

    assert isinstance(result, RoutineResponse)
    assert result.routine == fake_routine


def test_get_raises_404_on_key_error(controller, mock_service):
    mock_service.get.side_effect = KeyError("routine not found")

    with pytest.raises(HTTPException) as exc_info:
        controller.get("nonexistent")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_get_calls_service_with_correct_id(controller, mock_service):
    mock_service.get.return_value = make_routine()

    controller.get("routine-xyz")

    mock_service.get.assert_called_once_with("routine-xyz")


# --- create ---

def test_create_raises_404_when_profile_not_found(controller, mock_service):
    with patch("controllers.routine_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            controller.create(make_create_request())

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "profile not found"
    mock_service.create.assert_not_called()


def test_create_returns_routine_response(controller, mock_service):
    fake_routine = make_routine()
    mock_service.create.return_value = fake_routine

    with patch("controllers.routine_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        result = controller.create(make_create_request())

    assert isinstance(result, RoutineResponse)
    assert result.routine == fake_routine


def test_create_raises_422_on_value_error(controller, mock_service):
    mock_service.create.side_effect = ValueError("invalid steps")

    with patch("controllers.routine_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True

        with pytest.raises(HTTPException) as exc_info:
            controller.create(make_create_request())

    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_builds_routine_steps_correctly(controller, mock_service):
    mock_service.create.return_value = make_routine()

    with patch("controllers.routine_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        controller.create(make_create_request())

    _, call_kwargs = mock_service.create.call_args
    steps = call_kwargs["steps"]
    assert len(steps) == 2
    assert all(isinstance(s, RoutineStep) for s in steps)
    assert steps[0].gesture_id == "wave"
    assert steps[1].gesture_id == "point"


def test_create_passes_fields_to_service(controller, mock_service):
    mock_service.create.return_value = make_routine()

    with patch("controllers.routine_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        controller.create(make_create_request(name="Custom", description="Desc"))

    mock_service.create.assert_called_once_with(
        name="Custom",
        description="Desc",
        steps=ANY,
        created_by="profile-1",
    )


def test_create_checks_correct_profile_id(controller, mock_service):
    with patch("controllers.routine_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = False

        with pytest.raises(HTTPException):
            controller.create(make_create_request(created_by="profile-999"))

        mock_profile.exists.assert_called_once_with("profile-999")


# --- update ---
# update and delete check ownership first: the controller loads the routine
# and compares the caller's created_by claim against the stored one, so
# every test primes mock_service.get and passes a matching claim.

def test_update_returns_routine_response(controller, mock_service):
    fake_routine = make_routine()
    mock_service.get.return_value = fake_routine
    mock_service.update.return_value = fake_routine

    result = controller.update(
        "routine-1", make_update_request(name="New Name", created_by="profile-1")
    )

    assert isinstance(result, RoutineResponse)
    assert result.routine == fake_routine


def test_update_raises_404_on_key_error(controller, mock_service):
    mock_service.get.side_effect = KeyError("not found")

    with pytest.raises(HTTPException) as exc_info:
        controller.update("routine-1", make_update_request(name="X"))

    assert exc_info.value.status_code == 404


def test_update_raises_422_on_value_error(controller, mock_service):
    mock_service.get.return_value = make_routine()
    mock_service.update.side_effect = ValueError("invalid")

    with pytest.raises(HTTPException) as exc_info:
        controller.update(
            "routine-1", make_update_request(name="X", created_by="profile-1")
        )

    assert exc_info.value.status_code == 422


def test_update_rejects_wrong_owner(controller, mock_service):
    mock_service.get.return_value = make_routine(created_by="profile-1")

    with pytest.raises(HTTPException) as exc_info:
        controller.update(
            "routine-1", make_update_request(name="X", created_by="profile-2")
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    mock_service.update.assert_not_called()


def test_update_requires_ownership_claim(controller, mock_service):
    mock_service.get.return_value = make_routine(created_by="profile-1")

    with pytest.raises(HTTPException) as exc_info:
        controller.update("routine-1", make_update_request(name="X"))

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


def test_update_skips_ownership_for_non_custom(controller, mock_service):
    # seed routines are guarded by the service's own ValueError, not by the
    # ownership check — the controller must not 403 them.
    mock_service.get.return_value = make_routine(is_custom=False, created_by=None)
    mock_service.update.return_value = make_routine()

    controller.update("routine-1", make_update_request(name="X"))

    mock_service.update.assert_called_once()


def test_update_passes_none_steps_when_not_provided(controller, mock_service):
    mock_service.get.return_value = make_routine()
    mock_service.update.return_value = make_routine()

    controller.update("routine-1", make_update_request(name="New", created_by="profile-1"))

    _, call_kwargs = mock_service.update.call_args
    assert call_kwargs["steps"] is None


def test_update_builds_steps_when_provided(controller, mock_service):
    mock_service.get.return_value = make_routine()
    mock_service.update.return_value = make_routine()
    payload = RoutineUpdateRequest(created_by="profile-1", steps=[
        RoutineStepInput(gesture_id="wave", prompt="Wave", hint="hint"),
        RoutineStepInput(gesture_id="point", prompt="Point", hint="hint2"),
    ])

    controller.update("routine-1", payload)

    _, call_kwargs = mock_service.update.call_args
    steps = call_kwargs["steps"]
    assert steps is not None
    assert len(steps) == 2
    assert all(isinstance(s, RoutineStep) for s in steps)


def test_update_calls_service_with_correct_id(controller, mock_service):
    mock_service.get.return_value = make_routine()
    mock_service.update.return_value = make_routine()

    controller.update("routine-abc", make_update_request(name="X", created_by="profile-1"))

    args, _ = mock_service.update.call_args
    assert args[0] == "routine-abc"


# --- delete ---

def test_delete_returns_ok(controller, mock_service):
    mock_service.get.return_value = make_routine()

    result = controller.delete("routine-1", created_by="profile-1")

    assert result == {"ok": True}


def test_delete_calls_service_with_correct_id(controller, mock_service):
    mock_service.get.return_value = make_routine()

    controller.delete("routine-abc", created_by="profile-1")

    mock_service.delete.assert_called_once_with("routine-abc")


def test_delete_rejects_wrong_owner(controller, mock_service):
    mock_service.get.return_value = make_routine(created_by="profile-1")

    with pytest.raises(HTTPException) as exc_info:
        controller.delete("routine-1", created_by="profile-2")

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    mock_service.delete.assert_not_called()


def test_delete_requires_ownership_claim(controller, mock_service):
    mock_service.get.return_value = make_routine(created_by="profile-1")

    with pytest.raises(HTTPException) as exc_info:
        controller.delete("routine-1")

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


def test_delete_raises_404_on_key_error(controller, mock_service):
    mock_service.get.side_effect = KeyError("not found")

    with pytest.raises(HTTPException) as exc_info:
        controller.delete("routine-1")

    assert exc_info.value.status_code == 404


def test_delete_raises_422_on_value_error(controller, mock_service):
    mock_service.get.return_value = make_routine()
    mock_service.delete.side_effect = ValueError("cannot delete")

    with pytest.raises(HTTPException) as exc_info:
        controller.delete("routine-1", created_by="profile-1")

    assert exc_info.value.status_code == 422
