from datetime import date, datetime, timezone

import pytest

from models.lesson import Lesson
from models.progress import Achievement, DailyGoal, ProgressRecord, ProgressSummary
from models.routine import Routine, RoutineStep


def make_step(gesture_id="hello"):
    return RoutineStep(gesture_id=gesture_id, prompt="Sign it", hint="Like this")


# ── Routine.length ────────────────────────────────────────────────────────────

def test_routine_length_empty_steps():
    r = Routine(id="r1", name="r", description="d", scenario_tag="daily", steps=[])
    assert r.length == 0


def test_routine_length_with_two_steps():
    r = Routine(id="r1", name="r", description="d", scenario_tag="daily",
                steps=[make_step("hello"), make_step("water")])
    assert r.length == 2


def test_routine_length_with_one_step():
    r = Routine(id="r1", name="r", description="d", scenario_tag="daily",
                steps=[make_step()])
    assert r.length == 1


def test_routine_is_custom_default_is_false():
    r = Routine(id="r1", name="r", description="d", scenario_tag="daily")
    assert r.is_custom is False


def test_routine_created_by_default_is_none():
    r = Routine(id="r1", name="r", description="d", scenario_tag="daily")
    assert r.created_by is None


# ── DailyGoal.met ─────────────────────────────────────────────────────────────

def test_daily_goal_met_when_progress_equals_target():
    g = DailyGoal(target=3, progress=3, date=date.today())
    assert g.met is True


def test_daily_goal_met_when_progress_exceeds_target():
    g = DailyGoal(target=3, progress=10, date=date.today())
    assert g.met is True


def test_daily_goal_not_met_when_progress_below_target():
    g = DailyGoal(target=3, progress=2, date=date.today())
    assert g.met is False


def test_daily_goal_not_met_at_zero_progress():
    g = DailyGoal(target=3, progress=0, date=date.today())
    assert g.met is False


def test_daily_goal_met_with_target_1():
    g = DailyGoal(target=1, progress=1, date=date.today())
    assert g.met is True


# ── ProgressRecord ────────────────────────────────────────────────────────────

def _make_record(**kwargs):
    base = dict(
        profile_id="p", routine_id="r", gesture_id="g",
        accuracy=0.7, band="correct", attempts=1, succeeded=True,
    )
    return ProgressRecord(**{**base, **kwargs})


def test_progress_record_incorrect_points_defaults_empty():
    r = _make_record()
    assert r.incorrect_points == []


def test_progress_record_created_at_is_recent():
    r = _make_record()
    delta = abs((datetime.now(timezone.utc) - r.created_at).total_seconds())
    assert delta < 5


def test_progress_record_created_at_is_timezone_aware():
    r = _make_record()
    assert r.created_at.tzinfo is not None


def test_progress_record_accepts_incorrect_points():
    r = _make_record(incorrect_points=[5, 9, 13])
    assert r.incorrect_points == [5, 9, 13]


# ── ProgressSummary defaults ──────────────────────────────────────────────────

def test_progress_summary_default_streak_is_0():
    s = ProgressSummary(profile_id="p", total_attempts=0, successes=0,
                        avg_accuracy=0.0, best_accuracy=0.0, routines_completed=[])
    assert s.current_streak == 0
    assert s.longest_streak == 0


def test_progress_summary_default_xp_is_0():
    s = ProgressSummary(profile_id="p", total_attempts=0, successes=0,
                        avg_accuracy=0.0, best_accuracy=0.0, routines_completed=[])
    assert s.total_xp == 0
    assert s.level == 0


def test_progress_summary_achievements_default_empty():
    s = ProgressSummary(profile_id="p", total_attempts=0, successes=0,
                        avg_accuracy=0.0, best_accuracy=0.0, routines_completed=[])
    assert s.achievements == []


# ── Lesson defaults ───────────────────────────────────────────────────────────

def test_lesson_difficulty_defaults_to_starter():
    l = Lesson(id="l1", title="L", description="D")
    assert l.difficulty == "starter"


def test_lesson_tags_default_empty():
    l = Lesson(id="l1", title="L", description="D")
    assert l.tags == []


def test_lesson_gesture_ids_default_empty():
    l = Lesson(id="l1", title="L", description="D")
    assert l.gesture_ids == []


def test_lesson_scenario_tag_default_none():
    l = Lesson(id="l1", title="L", description="D")
    assert l.scenario_tag is None
