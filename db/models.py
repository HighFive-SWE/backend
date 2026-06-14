from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# --- accounts + profiles ----------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(16))  # parent | child | educator
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    profiles: Mapped[list["Profile"]] = relationship(back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    avatar: Mapped[str] = mapped_column(String(32))  # palette key
    age_group: Mapped[str] = mapped_column(String(16), default="middle")
    role: Mapped[str] = mapped_column(String(16), default="child")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    user: Mapped[User] = relationship(back_populates="profiles")


# --- content (lessons + routines) -------------------------------------------

class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(500))
    difficulty: Mapped[str] = mapped_column(String(16), default="starter")
    scenario_tag: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    gesture_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class Routine(Base):
    __tablename__ = "routines"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(500))
    scenario_tag: Mapped[str] = mapped_column(String(32))
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    steps: Mapped[list["RoutineStep"]] = relationship(
        back_populates="routine",
        order_by="RoutineStep.position",
        cascade="all, delete-orphan",
    )


class RoutineStep(Base):
    __tablename__ = "routine_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    routine_id: Mapped[str] = mapped_column(ForeignKey("routines.id"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    gesture_id: Mapped[str] = mapped_column(String(64))
    prompt: Mapped[str] = mapped_column(String(200))
    hint: Mapped[str] = mapped_column(String(300))

    routine: Mapped[Routine] = relationship(back_populates="steps")


# --- activity (progress, cv, study) -----------------------------------------

class ProgressLog(Base):
    __tablename__ = "progress_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id"), index=True)
    routine_id: Mapped[str] = mapped_column(String(64))
    gesture_id: Mapped[str] = mapped_column(String(64))
    accuracy: Mapped[float] = mapped_column(Float)
    band: Mapped[str] = mapped_column(String(16))  # correct | partial | incorrect
    attempts: Mapped[int] = mapped_column(Integer, default=1)
    succeeded: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_routine: Mapped[bool] = mapped_column(Boolean, default=False)
    incorrect_points: Mapped[list[int]] = mapped_column(JSON, default=list)
    tz_offset_minutes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class CVResult(Base):
    __tablename__ = "cv_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    gesture_id: Mapped[str] = mapped_column(String(64))
    accuracy: Mapped[float] = mapped_column(Float)
    band: Mapped[str] = mapped_column(String(16))
    incorrect_points: Mapped[list[int]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class StudySession(Base):
    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id"), index=True)
    deck: Mapped[str] = mapped_column(String(32))
    mode: Mapped[str] = mapped_column(String(16))  # browse | quiz
    cards_seen: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


# --- gamification rollups ----------------------------------------------------

class Achievement(Base):
    __tablename__ = "achievements"
    __table_args__ = (UniqueConstraint("profile_id", "code", name="uq_achievement_profile_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id"), index=True)
    code: Mapped[str] = mapped_column(String(48))
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(300))
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class ProgressState(Base):
    """per-profile gamification aggregate — mirrors the in-memory ProfileState
    so a restart no longer wipes streaks, xp, or the daily goal."""

    __tablename__ = "progress_state"

    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id"), primary_key=True)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    perfect_steps: Mapped[int] = mapped_column(Integer, default=0)
    daily_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    daily_progress: Mapped[int] = mapped_column(Integer, default=0)
    daily_target: Mapped[int] = mapped_column(Integer, default=3)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    successes: Mapped[int] = mapped_column(Integer, default=0)
    accuracy_sum: Mapped[float] = mapped_column(Float, default=0.0)
    best_accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    tz_offset_minutes: Mapped[int] = mapped_column(Integer, default=0)
    routines_completed: Mapped[list[str]] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)


# --- educator groups (the §7 multi-user surface) ----------------------------

class EducatorGroup(Base):
    __tablename__ = "educator_groups"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    members: Mapped[list["EducatorGroupMember"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )


class EducatorGroupMember(Base):
    __tablename__ = "educator_group_members"
    __table_args__ = (UniqueConstraint("group_id", "profile_id", name="uq_group_member"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[str] = mapped_column(ForeignKey("educator_groups.id"), index=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id"), index=True)

    group: Mapped[EducatorGroup] = relationship(back_populates="members")
