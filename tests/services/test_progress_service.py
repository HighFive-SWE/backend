from datetime import date, datetime, timedelta, timezone

import pytest

from models.progress import ProgressRecord
from services.progress_service import (
    ProgressService,
    XP_PER_STEP,
    XP_PER_ROUTINE,
    XP_PERFECT_BONUS,
    PERFECT_ACCURACY_THRESHOLD,
    level_for,
    xp_for_level,
)


def make_record(profile_id="p1", gesture_id="hello", routine_id="r1",
                accuracy=0.7, band="correct", succeeded=True, **kwargs):
    return ProgressRecord(
        profile_id=profile_id,
        gesture_id=gesture_id,
        routine_id=routine_id,
        accuracy=accuracy,
        band=band,
        attempts=1,
        succeeded=succeeded,
        **kwargs,
    )


# ── level_for / xp_for_level ─────────────────────────────────────────────────

def test_level_for_zero_xp_is_level_0():
    assert level_for(0) == 0


def test_level_for_negative_xp_is_level_0():
    assert level_for(-100) == 0


def test_level_for_50_xp_is_level_1():
    assert level_for(50) == 1


def test_xp_for_level_0_is_0():
    assert xp_for_level(0) == 0


def test_xp_for_level_1_is_50():
    assert xp_for_level(1) == 50


def test_xp_for_level_2_is_200():
    assert xp_for_level(2) == 200


def test_level_for_and_xp_for_level_are_inverse():
    for level in range(1, 6):
        assert level_for(xp_for_level(level)) == level


# ── XP awarding ──────────────────────────────────────────────────────────────

def test_succeeded_step_awards_xp():
    svc = ProgressService()
    svc.record(make_record(accuracy=0.5))
    assert svc.summary("p1").total_xp == XP_PER_STEP


def test_perfect_step_awards_extra_xp():
    svc = ProgressService()
    svc.record(make_record(accuracy=PERFECT_ACCURACY_THRESHOLD))
    assert svc.summary("p1").total_xp == XP_PER_STEP + XP_PERFECT_BONUS


def test_completed_routine_awards_routine_xp():
    svc = ProgressService()
    svc.record(make_record(), completed_routine=True)
    assert svc.summary("p1").total_xp >= XP_PER_ROUTINE


def test_failed_step_awards_no_xp():
    svc = ProgressService()
    svc.record(make_record(succeeded=False, accuracy=0.9))
    assert svc.summary("p1").total_xp == 0


# ── streak logic ─────────────────────────────────────────────────────────────

def _record_on(day_offset: int, **kwargs) -> ProgressRecord:
    ts = datetime.now(timezone.utc) - timedelta(days=day_offset)
    return make_record(created_at=ts, **kwargs)


def test_first_record_starts_streak_at_1():
    svc = ProgressService()
    svc.record(_record_on(0))
    assert svc.summary("p1").current_streak == 1


def test_consecutive_days_builds_streak():
    svc = ProgressService()
    svc.record(_record_on(2))
    svc.record(_record_on(1))
    svc.record(_record_on(0))
    assert svc.summary("p1").current_streak == 3


def test_gap_in_days_resets_streak():
    svc = ProgressService()
    svc.record(_record_on(5))
    svc.record(_record_on(0))
    assert svc.summary("p1").current_streak == 1


def test_same_day_two_records_streak_stays_at_1():
    svc = ProgressService()
    svc.record(_record_on(0))
    svc.record(_record_on(0))
    assert svc.summary("p1").current_streak == 1


def test_longest_streak_tracks_maximum():
    svc = ProgressService()
    svc.record(_record_on(3))
    svc.record(_record_on(2))
    svc.record(_record_on(1))
    svc.record(_record_on(0))
    summary = svc.summary("p1")
    assert summary.longest_streak >= 4


# ── daily goal ───────────────────────────────────────────────────────────────

def test_daily_goal_progress_increments_on_success():
    svc = ProgressService()
    svc.record(make_record(succeeded=True))
    assert svc.summary("p1").daily_goal.progress == 1


def test_daily_goal_not_incremented_on_failure():
    svc = ProgressService()
    svc.record(make_record(succeeded=False))
    assert svc.summary("p1").daily_goal.progress == 0


def test_daily_goal_met_after_three_successes():
    svc = ProgressService()
    for _ in range(3):
        svc.record(make_record(succeeded=True))
    assert svc.summary("p1").daily_goal.met is True


# ── achievements ─────────────────────────────────────────────────────────────

def test_first_step_achievement_unlocked_on_first_success():
    svc = ProgressService()
    svc.record(make_record(succeeded=True))
    codes = {a.code for a in svc.summary("p1").achievements}
    assert "first_step" in codes


def test_first_routine_achievement_unlocked_on_completion():
    svc = ProgressService()
    svc.record(make_record(succeeded=True), completed_routine=True)
    codes = {a.code for a in svc.summary("p1").achievements}
    assert "first_routine" in codes


def test_three_day_streak_achievement():
    svc = ProgressService()
    for day in range(2, -1, -1):
        svc.record(_record_on(day))
    codes = {a.code for a in svc.summary("p1").achievements}
    assert "three_day_streak" in codes


def test_ten_perfect_steps_achievement():
    svc = ProgressService()
    for _ in range(10):
        svc.record(make_record(accuracy=PERFECT_ACCURACY_THRESHOLD, succeeded=True))
    codes = {a.code for a in svc.summary("p1").achievements}
    assert "ten_perfect_steps" in codes


# ── read-path isolation ───────────────────────────────────────────────────────

def test_separate_profiles_are_isolated():
    svc = ProgressService()
    svc.record(make_record(profile_id="alice"))
    svc.record(make_record(profile_id="bob"))
    assert len(svc.list_for("alice")) == 1
    assert len(svc.list_for("bob")) == 1


def test_list_for_empty_profile_returns_empty():
    svc = ProgressService()
    assert svc.list_for("nobody") == []
