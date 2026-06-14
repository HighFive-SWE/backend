from __future__ import annotations

import pytest
from sqlalchemy import inspect

from db import models
from db.base import Base, dump_schema_sql, init_db, make_engine, session_scope


@pytest.fixture()
def empty_engine(tmp_path):
    eng = make_engine(f"sqlite:///{tmp_path / 'schema.db'}")
    init_db(eng)
    yield eng
    eng.dispose()


def test_all_tables_created(empty_engine):
    tables = set(inspect(empty_engine).get_table_names())
    expected = {
        "users",
        "profiles",
        "lessons",
        "routines",
        "routine_steps",
        "progress_logs",
        "cv_results",
        "study_sessions",
        "achievements",
        "progress_state",
        "educator_groups",
        "educator_group_members",
    }
    assert expected <= tables


def test_profile_user_roundtrip(empty_engine):
    with session_scope(empty_engine) as s:
        s.add(models.User(id="u1", name="home", role="parent"))
        s.add(models.Profile(id="p1", user_id="u1", display_name="kid", avatar="mint"))

    with session_scope(empty_engine) as s:
        profile = s.get(models.Profile, "p1")
        assert profile is not None
        assert profile.user.name == "home"


def test_routine_steps_cascade(empty_engine):
    with session_scope(empty_engine) as s:
        r = models.Routine(id="r1", name="n", description="d", scenario_tag="daily")
        r.steps.append(models.RoutineStep(position=0, gesture_id="hello", prompt="p", hint="h"))
        s.add(r)

    with session_scope(empty_engine) as s:
        r = s.get(models.Routine, "r1")
        assert [step.gesture_id for step in r.steps] == ["hello"]
        s.delete(r)

    with session_scope(empty_engine) as s:
        assert s.query(models.RoutineStep).count() == 0


def test_dump_schema_sql_covers_every_table():
    ddl = dump_schema_sql()
    for table in Base.metadata.tables:
        assert f"CREATE TABLE {table}" in ddl
