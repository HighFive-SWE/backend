from unittest.mock import MagicMock, patch

import pytest

from models.cv_result import CVResult
from services.cv_service import CVService


def make_vision_result(accuracy=0.9, band="correct", incorrect_points=None):
    m = MagicMock()
    m.accuracy = accuracy
    m.band = band
    m.incorrect_points = incorrect_points if incorrect_points is not None else []
    return m


def make_landmarks(n=21):
    return [[0.05 * i, 0.1 * i, 0.0] for i in range(n)]


@pytest.fixture
def svc():
    return CVService()


# ── evaluate ─────────────────────────────────────────────────────────────────

def test_evaluate_returns_cv_result(svc):
    mock_result = make_vision_result()
    with patch("services.cv_service.get_reference"), \
         patch("services.cv_service.compare_gesture", return_value=mock_result):
        result = svc.evaluate("hello", make_landmarks())
    assert isinstance(result, CVResult)


def test_evaluate_maps_accuracy(svc):
    mock_result = make_vision_result(accuracy=0.85)
    with patch("services.cv_service.get_reference"), \
         patch("services.cv_service.compare_gesture", return_value=mock_result):
        result = svc.evaluate("hello", make_landmarks())
    assert result.accuracy == 0.85


def test_evaluate_maps_band(svc):
    mock_result = make_vision_result(band="partial")
    with patch("services.cv_service.get_reference"), \
         patch("services.cv_service.compare_gesture", return_value=mock_result):
        result = svc.evaluate("hello", make_landmarks())
    assert result.band == "partial"


def test_evaluate_maps_incorrect_points(svc):
    mock_result = make_vision_result(incorrect_points=[5, 9])
    with patch("services.cv_service.get_reference"), \
         patch("services.cv_service.compare_gesture", return_value=mock_result):
        result = svc.evaluate("hello", make_landmarks())
    assert result.incorrect_points == [5, 9]


def test_evaluate_stores_user_id(svc):
    mock_result = make_vision_result()
    with patch("services.cv_service.get_reference"), \
         patch("services.cv_service.compare_gesture", return_value=mock_result):
        result = svc.evaluate("hello", make_landmarks(), user_id="user-42")
    assert result.user_id == "user-42"


def test_evaluate_stores_gesture_id(svc):
    mock_result = make_vision_result()
    with patch("services.cv_service.get_reference"), \
         patch("services.cv_service.compare_gesture", return_value=mock_result):
        result = svc.evaluate("water", make_landmarks())
    assert result.gesture_id == "water"


def test_evaluate_appends_to_log(svc):
    mock_result = make_vision_result()
    with patch("services.cv_service.get_reference"), \
         patch("services.cv_service.compare_gesture", return_value=mock_result):
        svc.evaluate("hello", make_landmarks())
    assert len(svc.recent()) == 1


def test_evaluate_calls_get_reference_with_correct_id(svc):
    mock_result = make_vision_result()
    with patch("services.cv_service.get_reference") as mock_ref, \
         patch("services.cv_service.compare_gesture", return_value=mock_result):
        svc.evaluate("water", make_landmarks())
    mock_ref.assert_called_once_with("water")


def test_evaluate_passes_landmarks_to_compare(svc):
    mock_result = make_vision_result()
    lm = make_landmarks()
    with patch("services.cv_service.get_reference"), \
         patch("services.cv_service.compare_gesture", return_value=mock_result) as mock_compare:
        svc.evaluate("hello", lm)
    called_lm = mock_compare.call_args.args[0]
    assert called_lm == lm


# ── recent ────────────────────────────────────────────────────────────────────

def test_recent_empty_initially(svc):
    assert svc.recent() == []


def test_recent_returns_most_recent_first(svc):
    mock_result = make_vision_result()
    with patch("services.cv_service.get_reference"), \
         patch("services.cv_service.compare_gesture", return_value=mock_result):
        svc.evaluate("hello", make_landmarks())
        svc.evaluate("water", make_landmarks())
    results = svc.recent(limit=2)
    assert results[0].gesture_id == "water"


def test_recent_respects_limit(svc):
    mock_result = make_vision_result()
    with patch("services.cv_service.get_reference"), \
         patch("services.cv_service.compare_gesture", return_value=mock_result):
        for _ in range(5):
            svc.evaluate("hello", make_landmarks())
    assert len(svc.recent(limit=3)) == 3


def test_recent_limit_zero_returns_empty(svc):
    mock_result = make_vision_result()
    with patch("services.cv_service.get_reference"), \
         patch("services.cv_service.compare_gesture", return_value=mock_result):
        svc.evaluate("hello", make_landmarks())
    assert svc.recent(limit=0) == []


def test_log_capacity_evicts_oldest():
    svc = CVService(log_capacity=3)
    mock_result = make_vision_result()
    with patch("services.cv_service.get_reference"), \
         patch("services.cv_service.compare_gesture", return_value=mock_result):
        for i in range(5):
            svc.evaluate(f"g{i}", make_landmarks())
    all_results = svc.recent(limit=100)
    assert len(all_results) == 3
    assert all_results[0].gesture_id == "g4"


# ── suggestion_for ────────────────────────────────────────────────────────────

def test_suggestion_for_correct_is_nonempty(svc):
    assert svc.suggestion_for("correct")


def test_suggestion_for_partial_is_nonempty(svc):
    assert svc.suggestion_for("partial")


def test_suggestion_for_incorrect_is_nonempty(svc):
    assert svc.suggestion_for("incorrect")


def test_suggestion_for_unknown_returns_partial_fallback(svc):
    assert svc.suggestion_for("unknown-band") == svc.suggestion_for("partial")


def test_suggestion_bands_differ(svc):
    assert svc.suggestion_for("correct") != svc.suggestion_for("incorrect")
