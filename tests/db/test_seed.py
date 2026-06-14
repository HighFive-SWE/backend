from __future__ import annotations

import pytest

from db import models
from db.base import make_engine, session_scope
from db.seed import seed
from services.lesson_service import _SEED as LESSON_SEED
from services.routine_service import _SEED as ROUTINE_SEED
from vision.gestures.samples import GESTURES


@pytest.fixture(scope="module")
def seeded_engine(tmp_path_factory):
    path = tmp_path_factory.mktemp("seed") / "highfive.db"
    eng = make_engine(f"sqlite:///{path}")
    seed(eng)
    yield eng
    eng.dispose()


def test_content_counts_match_seed_lists(seeded_engine):
    with session_scope(seeded_engine) as s:
        assert s.query(models.Lesson).count() == len(LESSON_SEED)
        assert s.query(models.Routine).count() == len(ROUTINE_SEED)
        assert s.query(models.RoutineStep).count() == sum(len(r.steps) for r in ROUTINE_SEED)


def test_every_persisted_gesture_is_in_catalog(seeded_engine):
    known = set(GESTURES.keys())
    with session_scope(seeded_engine) as s:
        for table in (models.RoutineStep, models.ProgressLog, models.CVResult):
            ids = {row.gesture_id for row in s.query(table).all()}
            assert ids <= known, f"{table.__tablename__} references unknown gestures: {ids - known}"


def test_progress_state_matches_logs(seeded_engine):
    with session_scope(seeded_engine) as s:
        for state in s.query(models.ProgressState).all():
            logged = s.query(models.ProgressLog).filter_by(profile_id=state.profile_id).count()
            assert state.total_attempts == logged
            assert 0 <= state.successes <= state.total_attempts
            assert state.longest_streak >= state.current_streak >= 1


def test_seed_is_deterministic_and_resettable(seeded_engine):
    # re-seeding the same engine drops and rebuilds — counts stay identical.
    before = seed(seeded_engine)
    after = seed(seeded_engine)
    assert before == after


def test_educator_group_links_child_profiles(seeded_engine):
    with session_scope(seeded_engine) as s:
        group = s.query(models.EducatorGroup).one()
        member_ids = {m.profile_id for m in group.members}
        child_ids = {p.id for p in s.query(models.Profile).filter_by(role="child").all()}
        assert member_ids == child_ids
