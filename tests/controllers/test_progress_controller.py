from unittest.mock import patch
from datetime import datetime, timezone
import pytest
from fastapi import HTTPException

from controllers.progress_controller import ProgressController
from models.progress import Achievement, ProgressRecord, ProgressSummary
from views.progress_view import (
    ProgressCreateRequest,
    ProgressCreateResponse,
    ProgressResponse,
)


@pytest.fixture
def mock_service():
    from unittest.mock import MagicMock
    return MagicMock()


@pytest.fixture
def controller(mock_service):
    return ProgressController(service=mock_service)


def make_request(**overrides):
    defaults = dict(
        profile_id="profile-1",
        routine_id="routine-1",
        gesture_id="gesture-1",
        accuracy=0.9,
        band="correct",
        attempts=1,
        succeeded=True,
    )
    return ProgressCreateRequest(**{**defaults, **overrides})


def make_summary(**overrides):
    defaults = dict(
        profile_id="profile-1",
        total_attempts=1,
        successes=1,
        avg_accuracy=0.9,
        best_accuracy=0.9,
        routines_completed=[],
        total_xp=0,
        level=1,
        achievements=[],
    )
    return ProgressSummary(**{**defaults, **overrides})


def make_record(**overrides):
    defaults = dict(
        profile_id="profile-1",
        routine_id="routine-1",
        gesture_id="gesture-1",
        accuracy=0.9,
        band="correct",
        attempts=1,
        succeeded=True,
    )
    return ProgressRecord(**{**defaults, **overrides})


# --- record ---

def test_record_raises_404_when_profile_not_found(controller, mock_service):
    with patch("controllers.progress_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            controller.record(make_request())

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "profile not found"
    mock_service.record.assert_not_called()


def test_record_returns_progress_create_response(controller, mock_service):
    before = make_summary(total_xp=0, level=1)
    after = make_summary(total_xp=10, level=1)
    fake_record = make_record()
    mock_service.summary.side_effect = [before, after]
    mock_service.record.return_value = fake_record

    with patch("controllers.progress_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        result = controller.record(make_request())

    assert isinstance(result, ProgressCreateResponse)
    assert result.record == fake_record
    assert result.summary == after


def test_record_calculates_xp_gained(controller, mock_service):
    before = make_summary(total_xp=20, level=1)
    after = make_summary(total_xp=45, level=1)
    mock_service.summary.side_effect = [before, after]
    mock_service.record.return_value = make_record()

    with patch("controllers.progress_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        result = controller.record(make_request())

    assert result.xp_gained == 25


def test_record_detects_level_up(controller, mock_service):
    before = make_summary(total_xp=0, level=1)
    after = make_summary(total_xp=50, level=2)
    mock_service.summary.side_effect = [before, after]
    mock_service.record.return_value = make_record()

    with patch("controllers.progress_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        result = controller.record(make_request())

    assert result.leveled_up is True


def test_record_no_level_up_when_same_level(controller, mock_service):
    before = make_summary(total_xp=0, level=1)
    after = make_summary(total_xp=10, level=1)
    mock_service.summary.side_effect = [before, after]
    mock_service.record.return_value = make_record()

    with patch("controllers.progress_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        result = controller.record(make_request())

    assert result.leveled_up is False


def test_record_detects_new_achievements(controller, mock_service):
    now = datetime.now(timezone.utc)
    old = Achievement(code="first_step", title="First Step", description="First", unlocked_at=now)
    new = Achievement(code="perfect_10", title="Perfect 10", description="Ten", unlocked_at=now)
    before = make_summary(achievements=[old])
    after = make_summary(achievements=[old, new])
    mock_service.summary.side_effect = [before, after]
    mock_service.record.return_value = make_record()

    with patch("controllers.progress_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        result = controller.record(make_request())

    assert len(result.new_achievements) == 1
    assert result.new_achievements[0].code == "perfect_10"


def test_record_no_new_achievements_when_none_unlocked(controller, mock_service):
    now = datetime.now(timezone.utc)
    existing = Achievement(code="first_step", title="First Step", description="First", unlocked_at=now)
    before = make_summary(achievements=[existing])
    after = make_summary(achievements=[existing])
    mock_service.summary.side_effect = [before, after]
    mock_service.record.return_value = make_record()

    with patch("controllers.progress_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        result = controller.record(make_request())

    assert result.new_achievements == []


def test_record_returns_cached_response_on_replay(controller, mock_service):
    before = make_summary(total_xp=0)
    after = make_summary(total_xp=10)
    mock_service.summary.side_effect = [before, after]
    mock_service.record.return_value = make_record()
    request = make_request(idempotency_key="idem-key-12345678")

    with patch("controllers.progress_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        first = controller.record(request)
        second = controller.record(request)

    assert first is second
    assert mock_service.record.call_count == 1


def test_record_does_not_cache_when_no_idempotency_key(controller, mock_service):
    mock_service.summary.side_effect = [
        make_summary(total_xp=0),
        make_summary(total_xp=10),
        make_summary(total_xp=10),
        make_summary(total_xp=20),
    ]
    mock_service.record.return_value = make_record()

    with patch("controllers.progress_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        controller.record(make_request())
        controller.record(make_request())

    assert mock_service.record.call_count == 2


def test_record_builds_progress_record_with_correct_fields(controller, mock_service):
    mock_service.summary.side_effect = [make_summary(), make_summary()]
    mock_service.record.return_value = make_record()

    with patch("controllers.progress_controller.profile_service") as mock_profile:
        mock_profile.exists.return_value = True
        controller.record(make_request(
            profile_id="p-1",
            routine_id="r-1",
            gesture_id="g-1",
            accuracy=0.85,
            band="partial",
            attempts=3,
            succeeded=False,
            completed_routine=True,
        ))

    call_args = mock_service.record.call_args
    passed_record = call_args.args[0]
    assert passed_record.profile_id == "p-1"
    assert passed_record.routine_id == "r-1"
    assert passed_record.gesture_id == "g-1"
    assert passed_record.accuracy == 0.85
    assert passed_record.band == "partial"
    assert passed_record.attempts == 3
    assert passed_record.succeeded is False
    assert call_args.kwargs["completed_routine"] is True


# --- get_for ---

def test_get_for_returns_progress_response(controller, mock_service):
    fake_summary = make_summary()
    fake_recent = [make_record(), make_record()]
    mock_service.summary.return_value = fake_summary
    mock_service.list_for.return_value = fake_recent

    result = controller.get_for("profile-1")

    assert isinstance(result, ProgressResponse)
    assert result.summary == fake_summary
    assert result.recent == fake_recent


def test_get_for_passes_correct_profile_id(controller, mock_service):
    mock_service.summary.return_value = make_summary()
    mock_service.list_for.return_value = []

    controller.get_for("profile-abc")

    mock_service.summary.assert_called_once_with("profile-abc")
    mock_service.list_for.assert_called_once_with("profile-abc", limit=25)


def test_get_for_passes_custom_limit(controller, mock_service):
    mock_service.summary.return_value = make_summary()
    mock_service.list_for.return_value = []

    controller.get_for("profile-1", limit=10)

    mock_service.list_for.assert_called_once_with("profile-1", limit=10)


def test_get_for_default_limit_is_25(controller, mock_service):
    mock_service.summary.return_value = make_summary()
    mock_service.list_for.return_value = []

    controller.get_for("profile-1")

    mock_service.list_for.assert_called_once_with("profile-1", limit=25)


# --- _cache_key ---

def test_cache_key_returns_none_when_no_idempotency_key():
    assert ProgressController._cache_key(make_request()) is None


def test_cache_key_returns_namespaced_key():
    request = make_request(idempotency_key="test-key-12345678")
    assert ProgressController._cache_key(request) == "profile-1:test-key-12345678"
