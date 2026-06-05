from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException

from controllers.profile_controller import ProfileController
from models.profile import AgeGroup, Profile, Role
from views.profile_view import ProfileCreateRequest, ProfileListResponse, ProfileResponse


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def controller(mock_service):
    return ProfileController(service=mock_service)


def make_profile(**overrides):
    defaults = dict(
        id="profile-1",
        user_id="user-1",
        display_name="Alice",
        avatar="peach",
        age_group=AgeGroup.middle,
        role=Role.child,
    )
    return Profile(**{**defaults, **overrides})


def make_create_request(**overrides):
    defaults = dict(
        display_name="Alice",
        avatar="peach",
        age_group=AgeGroup.middle,
        role=Role.child,
        user_id="user-1",
    )
    return ProfileCreateRequest(**{**defaults, **overrides})


# --- list ---

def test_list_returns_profile_list_response(controller, mock_service):
    mock_service.list_profiles.return_value = []

    result = controller.list()

    assert isinstance(result, ProfileListResponse)


def test_list_forwards_service_results(controller, mock_service):
    fake_profiles = [make_profile(id="p-1"), make_profile(id="p-2")]
    mock_service.list_profiles.return_value = fake_profiles

    result = controller.list()

    assert result.profiles == fake_profiles


def test_list_passes_user_id_filter(controller, mock_service):
    mock_service.list_profiles.return_value = []

    controller.list(user_id="user-42")

    mock_service.list_profiles.assert_called_once_with("user-42")


def test_list_passes_none_user_id_by_default(controller, mock_service):
    mock_service.list_profiles.return_value = []

    controller.list()

    mock_service.list_profiles.assert_called_once_with(None)


def test_list_returns_empty_when_no_profiles(controller, mock_service):
    mock_service.list_profiles.return_value = []

    result = controller.list()

    assert result.profiles == []


# --- get ---

def test_get_returns_profile_response(controller, mock_service):
    fake_profile = make_profile()
    mock_service.get_profile.return_value = fake_profile

    result = controller.get("profile-1")

    assert isinstance(result, ProfileResponse)
    assert result.profile == fake_profile


def test_get_raises_404_when_not_found(controller, mock_service):
    mock_service.get_profile.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.get("nonexistent")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "profile not found"


def test_get_calls_service_with_correct_id(controller, mock_service):
    mock_service.get_profile.return_value = make_profile()

    controller.get("profile-xyz")

    mock_service.get_profile.assert_called_once_with("profile-xyz")


def test_get_does_not_raise_when_profile_exists(controller, mock_service):
    mock_service.get_profile.return_value = make_profile()

    result = controller.get("profile-1")

    assert result is not None


# --- create ---

def test_create_returns_profile_response(controller, mock_service):
    fake_profile = make_profile()
    mock_service.create_profile.return_value = fake_profile

    result = controller.create(make_create_request())

    assert isinstance(result, ProfileResponse)
    assert result.profile == fake_profile


def test_create_passes_all_fields_to_service(controller, mock_service):
    mock_service.create_profile.return_value = make_profile()
    payload = make_create_request(
        display_name="Bob",
        avatar="mint",
        age_group=AgeGroup.teen,
        role=Role.parent,
        user_id="user-99",
    )

    controller.create(payload)

    mock_service.create_profile.assert_called_once_with(
        user_id="user-99",
        display_name="Bob",
        avatar="mint",
        age_group=AgeGroup.teen,
        role=Role.parent,
    )


def test_create_calls_service_once(controller, mock_service):
    mock_service.create_profile.return_value = make_profile()

    controller.create(make_create_request())

    mock_service.create_profile.assert_called_once()
