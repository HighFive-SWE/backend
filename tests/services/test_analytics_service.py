from datetime import datetime, timezone

import pytest

from models.progress import ProgressRecord
from services.analytics_service import AnalyticsService
from services.progress_service import ProgressService


def make_record(profile_id="p1", gesture_id="hello", routine_id="r1",
                accuracy=0.8, band="correct", succeeded=True,
                incorrect_points=None):
    return ProgressRecord(
        profile_id=profile_id,
        gesture_id=gesture_id,
        routine_id=routine_id,
        accuracy=accuracy,
        band=band,
        attempts=1,
        succeeded=succeeded,
        incorrect_points=incorrect_points or [],
    )


@pytest.fixture
def empty_svc():
    ps = ProgressService()
    return AnalyticsService(progress=ps)


@pytest.fixture
def loaded_svc():
    ps = ProgressService()
    ps.record(make_record(gesture_id="hello", accuracy=0.9, succeeded=True))
    ps.record(make_record(gesture_id="hello", accuracy=0.5, succeeded=False))
    ps.record(make_record(gesture_id="water", accuracy=0.3, succeeded=False))
    ps.record(make_record(gesture_id="water", accuracy=0.4, succeeded=False))
    return AnalyticsService(progress=ps)


# ── empty profile ─────────────────────────────────────────────────────────────

def test_empty_snapshot_sample_size_zero(empty_svc):
    snap = empty_svc.snapshot("p1")
    assert snap.sample_size == 0


def test_empty_snapshot_avg_accuracy_zero(empty_svc):
    snap = empty_svc.snapshot("p1")
    assert snap.avg_accuracy == 0.0


def test_empty_snapshot_success_rate_zero(empty_svc):
    snap = empty_svc.snapshot("p1")
    assert snap.success_rate == 0.0


def test_empty_snapshot_weak_gestures_empty(empty_svc):
    snap = empty_svc.snapshot("p1")
    assert snap.weak_gestures == []


def test_empty_snapshot_trend_empty(empty_svc):
    snap = empty_svc.snapshot("p1")
    assert snap.trend == []


def test_empty_snapshot_finger_heat_empty(empty_svc):
    snap = empty_svc.snapshot("p1")
    assert snap.finger_heat == []


# ── avg_accuracy ──────────────────────────────────────────────────────────────

def test_avg_accuracy_is_mean_of_records(loaded_svc):
    snap = loaded_svc.snapshot("p1")
    expected = round((0.9 + 0.5 + 0.3 + 0.4) / 4, 4)
    assert snap.avg_accuracy == expected


# ── success_rate ──────────────────────────────────────────────────────────────

def test_success_rate_one_of_four(loaded_svc):
    snap = loaded_svc.snapshot("p1")
    assert snap.success_rate == round(1 / 4, 4)


# ── weak_gestures ─────────────────────────────────────────────────────────────

def test_weak_gestures_sorted_ascending_by_success_rate(loaded_svc):
    snap = loaded_svc.snapshot("p1")
    rates = [w.success_rate for w in snap.weak_gestures]
    assert rates == sorted(rates)


def test_weak_gestures_water_is_weakest(loaded_svc):
    snap = loaded_svc.snapshot("p1")
    assert snap.weakest_gesture_id == "water"


# ── trend window ─────────────────────────────────────────────────────────────

def test_trend_window_limits_results():
    ps = ProgressService()
    for i in range(15):
        ps.record(make_record(gesture_id=f"g{i}"))
    svc = AnalyticsService(progress=ps)
    snap = svc.snapshot("p1", trend_window=5)
    assert len(snap.trend) == 5


# ── finger heat ──────────────────────────────────────────────────────────────

def test_finger_heat_has_all_five_fingers():
    ps = ProgressService()
    ps.record(make_record(incorrect_points=[4, 8, 12, 16, 20]))
    svc = AnalyticsService(progress=ps)
    snap = svc.snapshot("p1")
    finger_names = {f.finger for f in snap.finger_heat}
    assert finger_names == {"thumb", "index", "middle", "ring", "pinky"}


def test_finger_heat_wrist_landmark_ignored():
    ps = ProgressService()
    ps.record(make_record(incorrect_points=[0]))
    svc = AnalyticsService(progress=ps)
    snap = svc.snapshot("p1")
    total_misses = sum(f.misses for f in snap.finger_heat)
    assert total_misses == 0
