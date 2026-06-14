"""builds the schema and fills it with mock data.

run as a module to (re)create the configured database from scratch and write
the canonical schema file:

    python -m db.seed

it drops every table first, so re-running gives a deterministic, stable db.
mock activity is generated through the real ProgressService, so the streaks,
xp, levels, and achievements stored here match exactly what the gamification
engine would compute at runtime — no hand-faked numbers that drift from logic.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from db.base import Base, dump_schema_sql, engine as default_engine, init_db
from db import models
from models.profile import Profile as ProfileModel
from services.lesson_service import _SEED as LESSON_SEED
from services.profile_service import ProfileService
from services.progress_service import ProgressService
from models.progress import ProgressRecord
from services.routine_service import _SEED as ROUTINE_SEED

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

# fixed seed → the same mock db every time, so screenshots and tests are stable.
_RNG_SEED = 20260614


def _band_for(accuracy: float) -> str:
    if accuracy >= 0.85:
        return "correct"
    if accuracy >= 0.65:
        return "partial"
    return "incorrect"


def _gesture_pool() -> list[str]:
    # only gestures that already drive a seed routine — guaranteed catalog-valid.
    ids: list[str] = []
    for routine in ROUTINE_SEED:
        for step in routine.steps:
            if step.gesture_id not in ids:
                ids.append(step.gesture_id)
    return ids


def _seed_accounts(session: Session) -> list[ProfileModel]:
    ps = ProfileService()  # reuse the canonical seeded users + profiles
    profiles = ps.list_profiles()
    for user in ps._users.values():  # noqa: SLF001 — seed-time read of the source of truth
        session.add(models.User(id=user.id, name=user.name, role=user.role.value, created_at=user.created_at))
    for p in profiles:
        session.add(
            models.Profile(
                id=p.id,
                user_id=p.user_id,
                display_name=p.display_name,
                avatar=p.avatar,
                age_group=p.age_group.value,
                role=p.role.value,
                created_at=p.created_at,
            )
        )
    return profiles


def _seed_content(session: Session) -> None:
    for lesson in LESSON_SEED:
        session.add(
            models.Lesson(
                id=lesson.id,
                title=lesson.title,
                description=lesson.description,
                difficulty=lesson.difficulty,
                scenario_tag=lesson.scenario_tag,
                tags=list(lesson.tags),
                gesture_ids=list(lesson.gesture_ids),
            )
        )
    for routine in ROUTINE_SEED:
        row = models.Routine(
            id=routine.id,
            name=routine.name,
            description=routine.description,
            scenario_tag=routine.scenario_tag,
            created_by=routine.created_by,
            is_custom=routine.is_custom,
            created_at=routine.created_at,
        )
        for i, step in enumerate(routine.steps):
            row.steps.append(
                models.RoutineStep(
                    position=i,
                    gesture_id=step.gesture_id,
                    prompt=step.prompt,
                    hint=step.hint,
                )
            )
        session.add(row)


def _mock_progress(profile_id: str, rng: random.Random, days: int) -> list[tuple[ProgressRecord, bool]]:
    routines = [r for r in ROUTINE_SEED if len(r.steps) >= 2]
    out: list[tuple[ProgressRecord, bool]] = []
    now = datetime.now(timezone.utc)
    # oldest -> today, one consecutive run of days so the streak engine climbs.
    for day_offset in range(days, -1, -1):
        when = now - timedelta(days=day_offset, hours=rng.randint(0, 6))
        for _ in range(rng.randint(1, 3)):
            routine = rng.choice(routines)
            last = len(routine.steps) - 1
            for i, step in enumerate(routine.steps):
                accuracy = round(rng.uniform(0.55, 0.99), 4)
                succeeded = accuracy >= 0.65
                incorrect = [] if accuracy >= 0.9 else sorted(rng.sample(range(1, 21), rng.randint(1, 3)))
                rec = ProgressRecord(
                    profile_id=profile_id,
                    routine_id=routine.id,
                    gesture_id=step.gesture_id,
                    accuracy=accuracy,
                    band=_band_for(accuracy),
                    attempts=rng.randint(1, 3),
                    succeeded=succeeded,
                    incorrect_points=incorrect,
                    tz_offset_minutes=0,
                    created_at=when,
                )
                out.append((rec, i == last and succeeded))
    return out


def _seed_activity(session: Session, profiles: list[ProfileModel]) -> None:
    rng = random.Random(_RNG_SEED)
    pool = _gesture_pool()
    learners = [p for p in profiles if p.role.value == "child"]

    for idx, profile in enumerate(learners):
        engine_state = ProgressService()
        records = _mock_progress(profile.id, rng, days=6 + idx * 2)

        for rec, completed in records:
            engine_state.record(rec, completed_routine=completed)
            session.add(
                models.ProgressLog(
                    profile_id=rec.profile_id,
                    routine_id=rec.routine_id,
                    gesture_id=rec.gesture_id,
                    accuracy=rec.accuracy,
                    band=rec.band,
                    attempts=rec.attempts,
                    succeeded=rec.succeeded,
                    completed_routine=completed,
                    incorrect_points=list(rec.incorrect_points),
                    tz_offset_minutes=rec.tz_offset_minutes,
                    created_at=rec.created_at,
                )
            )

        st = engine_state._state[profile.id]  # noqa: SLF001 — computed by the real engine
        session.add(
            models.ProgressState(
                profile_id=profile.id,
                current_streak=st.current_streak,
                longest_streak=st.longest_streak,
                last_active_date=st.last_active_date,
                total_xp=st.total_xp,
                perfect_steps=st.perfect_steps,
                daily_date=st.daily_date,
                daily_progress=st.daily_progress,
                daily_target=st.daily_target,
                total_attempts=st.total_attempts,
                successes=st.successes,
                accuracy_sum=round(st.accuracy_sum, 6),
                best_accuracy=round(st.best_accuracy, 6),
                tz_offset_minutes=st.tz_offset_minutes,
                routines_completed=sorted(engine_state._completed_routines[profile.id]),  # noqa: SLF001
            )
        )
        for ach in st.achievements.values():
            session.add(
                models.Achievement(
                    profile_id=profile.id,
                    code=ach.code,
                    title=ach.title,
                    description=ach.description,
                    unlocked_at=ach.unlocked_at,
                )
            )

        # a handful of camera-free study sessions and raw cv reads per learner.
        for deck, mode in (("greetings", "browse"), ("manners", "quiz"), ("feelings", "quiz")):
            seen = rng.randint(6, 16)
            session.add(
                models.StudySession(
                    profile_id=profile.id,
                    deck=deck,
                    mode=mode,
                    cards_seen=seen,
                    correct=rng.randint(seen // 2, seen) if mode == "quiz" else 0,
                    created_at=datetime.now(timezone.utc) - timedelta(days=rng.randint(0, 4)),
                )
            )
        for _ in range(rng.randint(12, 20)):
            accuracy = round(rng.uniform(0.5, 0.99), 4)
            session.add(
                models.CVResult(
                    user_id=profile.id,
                    gesture_id=rng.choice(pool),
                    accuracy=accuracy,
                    band=_band_for(accuracy),
                    incorrect_points=[] if accuracy >= 0.9 else sorted(rng.sample(range(1, 21), rng.randint(1, 3))),
                    created_at=datetime.now(timezone.utc) - timedelta(hours=rng.randint(0, 72)),
                )
            )


def _seed_educator(session: Session, profiles: list[ProfileModel]) -> None:
    educator = models.User(id="user-educator-1", name="ms. rivera", role="educator")
    session.add(educator)
    group = models.EducatorGroup(id="group-room-a", name="room a", owner_user_id=educator.id)
    session.add(group)
    for p in profiles:
        if p.role.value == "child":
            group.members.append(models.EducatorGroupMember(profile_id=p.id))


def seed(eng: Engine = default_engine, *, reset: bool = True) -> dict[str, int]:
    """create the schema and fill it with mock data. returns row counts."""
    if reset:
        Base.metadata.drop_all(eng)
    init_db(eng)

    from db.base import session_scope

    with session_scope(eng) as session:
        profiles = _seed_accounts(session)
        _seed_content(session)
        _seed_activity(session, profiles)
        _seed_educator(session, profiles)

    counts: dict[str, int] = {}
    with session_scope(eng) as session:
        for model in (
            models.User,
            models.Profile,
            models.Lesson,
            models.Routine,
            models.RoutineStep,
            models.ProgressLog,
            models.ProgressState,
            models.Achievement,
            models.StudySession,
            models.CVResult,
            models.EducatorGroup,
            models.EducatorGroupMember,
        ):
            counts[model.__tablename__] = session.query(model).count()
    return counts


def main() -> None:
    SCHEMA_PATH.write_text(dump_schema_sql())
    counts = seed()
    print(f"schema written to {SCHEMA_PATH}")
    print("seeded:")
    for table, n in counts.items():
        print(f"  {table:<24} {n}")


if __name__ == "__main__":
    main()
