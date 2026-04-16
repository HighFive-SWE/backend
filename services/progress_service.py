from __future__ import annotations

import math
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Deque

from models.progress import Achievement, DailyGoal, ProgressRecord, ProgressSummary


# --- xp / level ------------------------------------------------------------

XP_PER_STEP = 10
XP_PER_ROUTINE = 50
XP_PERFECT_BONUS = 20
PERFECT_ACCURACY_THRESHOLD = 0.95

# level = floor(sqrt(xp / 50)) — rising gap between levels keeps milestones feeling earned.
def level_for(xp: int) -> int:
    return int(math.floor(math.sqrt(max(xp, 0) / 50)))


def xp_for_level(level: int) -> int:
    return (level * level) * 50


# --- daily goal ------------------------------------------------------------

DEFAULT_DAILY_TARGET = 3


# --- achievements ----------------------------------------------------------

@dataclass(frozen=True)
class AchievementDef:
    code: str
    title: str
    description: str


ACHIEVEMENT_CATALOG: dict[str, AchievementDef] = {
    "first_step": AchievementDef(
        code="first_step",
        title="first step",
        description="completed your first sign.",
    ),
    "first_routine": AchievementDef(
        code="first_routine",
        title="first scenario",
        description="finished a whole routine end-to-end.",
    ),
    "three_day_streak": AchievementDef(
        code="three_day_streak",
        title="three-day streak",
        description="showed up three days in a row.",
    ),
    "ten_perfect_steps": AchievementDef(
        code="ten_perfect_steps",
        title="ten clean signs",
        description="ten steps at 95%+ accuracy.",
    ),
}


# --- per-profile state -----------------------------------------------------

@dataclass
class ProfileState:
    current_streak: int = 0
    longest_streak: int = 0
    last_active_date: date | None = None
    total_xp: int = 0
    perfect_steps: int = 0
    daily_date: date | None = None
    daily_progress: int = 0
    daily_target: int = DEFAULT_DAILY_TARGET
    achievements: dict[str, Achievement] = field(default_factory=dict)


# --- service ---------------------------------------------------------------

class ProgressService:
    """
    in-memory per-profile progress log with phase 4 gamification layer
    (streaks, xp, levels, daily goal, achievements). phase 5 keyed all
    storage by profile_id so each learner has isolated progress.
    """

    def __init__(self, per_profile_capacity: int = 500) -> None:
        self._per_profile_capacity = per_profile_capacity
        self._logs: dict[str, Deque[ProgressRecord]] = defaultdict(
            lambda: deque(maxlen=per_profile_capacity)
        )
        self._completed_routines: dict[str, set[str]] = defaultdict(set)
        self._state: dict[str, ProfileState] = defaultdict(ProfileState)

    # --- write path -------------------------------------------------------

    def record(
        self,
        record: ProgressRecord,
        *,
        completed_routine: bool = False,
    ) -> ProgressRecord:
        self._logs[record.profile_id].append(record)

        state = self._state[record.profile_id]
        today = record.created_at.astimezone(timezone.utc).date()
        self._bump_streak(state, today)

        if record.succeeded:
            self._award_xp_for_step(state, record)
            self._bump_daily_goal(state, today)
            if record.accuracy >= PERFECT_ACCURACY_THRESHOLD:
                state.perfect_steps += 1

        if completed_routine:
            self._completed_routines[record.profile_id].add(record.routine_id)
            state.total_xp += XP_PER_ROUTINE

        self._check_achievements(state, record, completed_routine)
        return record

    def mark_routine_complete(self, profile_id: str, routine_id: str) -> None:
        self._completed_routines[profile_id].add(routine_id)

    # --- read path --------------------------------------------------------

    def list_for(self, profile_id: str, limit: int = 100) -> list[ProgressRecord]:
        if limit <= 0:
            return []
        records = list(self._logs.get(profile_id, ()))[-limit:]
        records.reverse()
        return records

    def summary(self, profile_id: str) -> ProgressSummary:
        records = list(self._logs.get(profile_id, ()))
        state = self._state.get(profile_id, ProfileState())
        total = len(records)

        if total == 0:
            avg_accuracy = 0.0
            best = 0.0
            successes = 0
        else:
            successes = sum(1 for r in records if r.succeeded)
            avg_accuracy = round(sum(r.accuracy for r in records) / total, 4)
            best = round(max(r.accuracy for r in records), 4)

        level = level_for(state.total_xp)
        floor_xp = xp_for_level(level)
        next_level_xp = xp_for_level(level + 1)
        xp_into_level = max(state.total_xp - floor_xp, 0)
        xp_to_next = max(next_level_xp - floor_xp, 1)

        # daily goal resets lazily — if today's different from stored date, reset counter.
        today = datetime.now(timezone.utc).date()
        if state.daily_date != today:
            daily_progress = 0
        else:
            daily_progress = state.daily_progress

        return ProgressSummary(
            profile_id=profile_id,
            total_attempts=total,
            successes=successes,
            avg_accuracy=avg_accuracy,
            best_accuracy=best,
            routines_completed=sorted(self._completed_routines.get(profile_id, set())),
            current_streak=state.current_streak,
            longest_streak=state.longest_streak,
            last_active_date=state.last_active_date,
            total_xp=state.total_xp,
            level=level,
            xp_into_level=xp_into_level,
            xp_to_next_level=xp_to_next,
            achievements=sorted(
                state.achievements.values(),
                key=lambda a: a.unlocked_at,
            ),
            daily_goal=DailyGoal(
                target=state.daily_target,
                progress=daily_progress,
                date=today,
            ),
            streak_days=state.current_streak,
        )

    # --- helpers ----------------------------------------------------------

    def _bump_streak(self, state: ProfileState, today: date) -> None:
        last = state.last_active_date
        if last is None:
            state.current_streak = 1
        elif last == today:
            pass  # same-day activity doesn't move the streak.
        elif last == today - timedelta(days=1):
            state.current_streak += 1
        else:
            state.current_streak = 1
        state.longest_streak = max(state.longest_streak, state.current_streak)
        state.last_active_date = today

    def _award_xp_for_step(self, state: ProfileState, record: ProgressRecord) -> None:
        state.total_xp += XP_PER_STEP
        if record.accuracy >= PERFECT_ACCURACY_THRESHOLD:
            state.total_xp += XP_PERFECT_BONUS

    def _bump_daily_goal(self, state: ProfileState, today: date) -> None:
        if state.daily_date != today:
            state.daily_date = today
            state.daily_progress = 0
        state.daily_progress += 1

    def _check_achievements(
        self,
        state: ProfileState,
        record: ProgressRecord,
        completed_routine: bool,
    ) -> None:
        def unlock(code: str) -> None:
            if code in state.achievements:
                return
            definition = ACHIEVEMENT_CATALOG[code]
            state.achievements[code] = Achievement(
                code=definition.code,
                title=definition.title,
                description=definition.description,
                unlocked_at=datetime.now(timezone.utc),
            )

        if record.succeeded:
            unlock("first_step")
        if completed_routine:
            unlock("first_routine")
        if state.current_streak >= 3:
            unlock("three_day_streak")
        if state.perfect_steps >= 10:
            unlock("ten_perfect_steps")


progress_service = ProgressService()
